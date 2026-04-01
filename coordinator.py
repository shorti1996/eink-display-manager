"""Profile coordinator — trigger engine and service dispatcher."""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import logging
import os
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import callback
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_template_result,
    async_track_time_interval,
    TrackTemplate,
)
from homeassistant.helpers.template import Template

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant
    from homeassistant.helpers.event import TrackTemplateResult

from .const import (
    CONF_BACKGROUND,
    CONF_COMPRESS,
    CONF_DEBOUNCE,
    CONF_DEBOUNCE_CONFIG,
    CONF_DITHER,
    CONF_MIRROR,
    CONF_ENTITY_ID,
    CONF_RETRY_COUNT,
    CONF_RETRY_DELAY,
    CONF_ROTATE,
    CONF_SERVICE,
    CONF_TRIGGER_ENTITIES,
    CONF_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def _is_template(value: str) -> bool:
    """Check if a string contains Jinja2 template syntax."""
    return "{{" in value or "{%" in value


def _extract_template_strings(payload: list[dict]) -> list[str]:
    """Walk payload recursively, collecting unique strings with Jinja2 syntax."""
    templates: list[str] = []

    def _walk(value: Any) -> None:
        if isinstance(value, str) and _is_template(value):
            templates.append(value)
        elif isinstance(value, dict):
            for v in value.values():
                _walk(v)
        elif isinstance(value, list):
            for item in value:
                _walk(item)

    for el in payload:
        _walk(el)
    return list(dict.fromkeys(templates))


class BoundedDebouncer:
    """Debouncer with max_wait to prevent starvation from rapid updates.

    Normal case: entity settles within cooldown -> fires on trailing edge.
    Starvation case: entity keeps updating past max_wait -> force fire, reset cycle.
    """

    def __init__(
        self, hass, logger, *, cooldown: float, max_wait: float | None = None,
        function=None,
    ):
        self.hass = hass
        self._max_wait = max_wait if max_wait is not None else cooldown * 3
        self._first_trigger: float | None = None
        self._max_wait_handle: asyncio.TimerHandle | None = None
        self._function = function
        self._inner = Debouncer(
            hass, logger, cooldown=cooldown, immediate=False,
            function=self._on_inner_fire,
        )

    async def _on_inner_fire(self):
        """Inner debouncer fired normally -- clean up max_wait timer and call target."""
        if self._first_trigger is None:
            return
        if self._max_wait_handle:
            self._max_wait_handle.cancel()
            self._max_wait_handle = None
        self._first_trigger = None
        if self._function:
            await self._function()

    @callback
    def async_schedule_call(self):
        if self._first_trigger is None:
            self._first_trigger = self.hass.loop.time()
            self._max_wait_handle = self.hass.loop.call_later(
                self._max_wait, self._force_fire,
            )
        self._inner.async_schedule_call()

    @callback
    def _force_fire(self):
        """max_wait exceeded -- force fire and reset cycle."""
        self._inner.async_cancel()
        self._first_trigger = None
        self._max_wait_handle = None
        if self._function:
            self.hass.async_create_task(self._function())

    @callback
    def async_cancel(self):
        self._inner.async_cancel()
        self._first_trigger = None
        if self._max_wait_handle:
            self._max_wait_handle.cancel()
            self._max_wait_handle = None


_DEBOUNCE_DEFAULTS = {"default": 60, "global": 5, "entities": {}, "ignored": []}


class ProfileCoordinator:
    """Manages trigger lifecycle and dispatches updates for one display profile."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, subentry: Any,
        *, enabled: bool = True,
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.subentry = subentry
        self.subentry_id: str = subentry.subentry_id

        # Cold config from subentry.data
        data = subentry.data
        self.service: str = data.get(CONF_SERVICE, "")
        self.entity_id: str = data.get(CONF_ENTITY_ID, "")
        self.background: str = data.get(CONF_BACKGROUND, "white")
        self.rotate: int = int(data.get(CONF_ROTATE, 0))
        self.dither: str = data.get(CONF_DITHER, "none")
        self.update_interval: int = int(data.get(CONF_UPDATE_INTERVAL, 0))
        self.trigger_entities: list[str] = list(data.get(CONF_TRIGGER_ENTITIES, []))

        # Two-tier debounce config
        debounce_config = data.get(CONF_DEBOUNCE_CONFIG)
        if debounce_config is None:
            old_debounce = int(data.get(CONF_DEBOUNCE, 60))
            debounce_config = {**_DEBOUNCE_DEFAULTS, "default": old_debounce}
        else:
            debounce_config = {**_DEBOUNCE_DEFAULTS, **debounce_config}
        self._debounce_config: dict = debounce_config
        self.retry_delay: int = int(data.get(CONF_RETRY_DELAY, 5))
        self.retry_count: int = int(data.get(CONF_RETRY_COUNT, 3))
        self.compress: bool = bool(data.get(CONF_COMPRESS, True))
        self.mirror: str = data.get(CONF_MIRROR, "none")

        # Hot data — payload loaded later via async_load_payload()
        self.payload_template: list[dict] = []

        # Runtime state
        self.last_hash: str | None = None
        self.last_update: datetime | None = None
        self.last_error: str | None = None
        self.status: str = "idle"
        self.enabled: bool = enabled

        # Subscriptions
        self._unsub_interval: CALLBACK_TYPE | None = None
        self._unsub_template_track: CALLBACK_TYPE | None = None
        self._unsub_entities: list[CALLBACK_TYPE] = []
        self._entity_debouncers: dict[str, BoundedDebouncer] = {}
        self._global_debouncer: Debouncer | None = None
        self._template_track_info = None
        self._template_init_done: bool = False
        self._update_lock = asyncio.Lock()
        self._send_task: asyncio.Task | None = None
        self._retry_attempt: int = 0
        self._retry_unsub: CALLBACK_TYPE | None = None

    @property
    def title(self) -> str:
        """Human-readable label for logging."""
        return getattr(self.subentry, "title", self.subentry_id)

    def _payload_file_path(self) -> str:
        """Return the path to the payload JSON file for this profile."""
        return self.hass.config.path(".storage", DOMAIN, f"{self.subentry_id}.json")

    def _load_payload_from_file_sync(self) -> list[dict]:
        """Load payload from the .storage file (blocking). Returns [] if missing."""
        path = self._payload_file_path()
        try:
            with open(path) as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            pass
        return []

    async def async_load_payload(self) -> None:
        """Load payload from file in executor."""
        self.payload_template = await self.hass.async_add_executor_job(
            self._load_payload_from_file_sync
        )

    def save_payload_to_file(self, elements: list[dict]) -> None:
        """Write payload to the .storage file."""
        path = self._payload_file_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(elements, f, ensure_ascii=False)

    async def update_payload(self, elements: list[dict]) -> None:
        """Hot-update payload without entry reload. Called by WS handler."""
        self.payload_template = elements
        await self.hass.async_add_executor_job(self.save_payload_to_file, elements)
        # Re-register template tracking for new payload
        await self.async_stop()
        self.last_hash = None  # Force re-render with new payload
        await self.async_start()

    async def async_start(self) -> None:
        """Register all triggers. Idempotent — stops existing listeners first."""
        await self.async_stop()
        if not self.enabled:
            return

        # Global gate: leading-edge debouncer
        self._global_debouncer = Debouncer(
            self.hass, _LOGGER,
            cooldown=self._debounce_config.get("global", 5),
            immediate=True,
            function=self._async_execute_update,
        )

        if self.update_interval and self.update_interval > 0:
            self._unsub_interval = async_track_time_interval(
                self.hass,
                self._on_interval,
                timedelta(minutes=self.update_interval),
            )

        # Auto-track entities referenced in payload templates
        template_strings = _extract_template_strings(self.payload_template)
        if template_strings:
            track_templates = [
                TrackTemplate(Template(s, self.hass), None)
                for s in template_strings
            ]
            self._template_init_done = False
            info = async_track_template_result(
                self.hass,
                track_templates,
                self._on_template_change,
            )
            self._unsub_template_track = info.async_remove
            self._template_track_info = info
            info.async_refresh()

        # Additional manual trigger entities (for entities not in templates)
        if self.trigger_entities:
            self._unsub_entities.append(
                async_track_state_change_event(
                    self.hass,
                    self.trigger_entities,
                    self._on_entity_change,
                )
            )

    async def async_stop(self) -> None:
        """Unregister all triggers and cancel pending work."""
        if self._unsub_interval:
            self._unsub_interval()
            self._unsub_interval = None
        if self._unsub_template_track:
            self._unsub_template_track()
            self._unsub_template_track = None
        self._template_track_info = None
        for unsub in self._unsub_entities:
            unsub()
        self._unsub_entities.clear()
        for debouncer in self._entity_debouncers.values():
            debouncer.async_cancel()
        self._entity_debouncers.clear()
        if self._global_debouncer:
            self._global_debouncer.async_cancel()
            self._global_debouncer = None
        if self._retry_unsub:
            self._retry_unsub()
            self._retry_unsub = None
        self._retry_attempt = 0

    async def _on_interval(self, _now: datetime) -> None:
        """Handle periodic interval trigger."""
        await self.async_trigger_update("interval")

    @callback
    def _on_template_change(
        self, event: Event | None, updates: list[TrackTemplateResult]
    ) -> None:
        """Handle template dependency change detected by HA's tracker."""
        if not self._template_init_done:
            self._template_init_done = True
            return
        if all(u.last_result == u.result for u in updates):
            _LOGGER.debug("Profile %s: template deps fired but outputs unchanged", self.title)
            return

        if event is None:
            # Initial render -- bypass debounce
            self.hass.async_create_task(self._async_execute_update())
            return

        entity_id = event.data.get("entity_id")
        if not entity_id:
            return
        if entity_id in self._debounce_config.get("ignored", []):
            _LOGGER.debug("Profile %s: ignoring change from %s", self.title, entity_id)
            return

        debouncer = self._get_or_create_entity_debouncer(entity_id)
        debouncer.async_schedule_call()

    @callback
    def _on_entity_change(self, event: Event) -> None:
        """Handle entity state change — route through per-entity debouncer."""
        entity_id = event.data.get("entity_id")
        if not entity_id:
            return
        if entity_id in self._debounce_config.get("ignored", []):
            _LOGGER.debug("Profile %s: ignoring change from %s", self.title, entity_id)
            return
        debouncer = self._get_or_create_entity_debouncer(entity_id)
        debouncer.async_schedule_call()

    def _get_or_create_entity_debouncer(self, entity_id: str) -> BoundedDebouncer:
        if entity_id in self._entity_debouncers:
            return self._entity_debouncers[entity_id]

        entity_cfg = self._debounce_config.get("entities", {}).get(entity_id)
        if isinstance(entity_cfg, dict):
            cooldown = entity_cfg.get("cooldown", self._debounce_config.get("default", 5))
            max_wait = entity_cfg.get("max_wait")
        elif isinstance(entity_cfg, (int, float)):
            cooldown = entity_cfg
            max_wait = None
        else:
            cooldown = self._debounce_config.get("default", 5)
            max_wait = None

        debouncer = BoundedDebouncer(
            self.hass, _LOGGER,
            cooldown=cooldown,
            max_wait=max_wait,
            function=self._async_request_global_refresh,
        )
        self._entity_debouncers[entity_id] = debouncer
        return debouncer

    async def _async_request_global_refresh(self):
        """Per-entity debouncer fires here -- route through global gate."""
        if self._global_debouncer:
            await self._global_debouncer.async_call()

    async def _async_execute_update(self):
        """Global debouncer fires here -- the only place expensive work happens."""
        await self.async_trigger_update("debounced")

    def get_tracked_entities(self) -> set[str]:
        """Return entity IDs this profile depends on (templates + manual triggers)."""
        entities: set[str] = set()
        if self._template_track_info:
            listeners = self._template_track_info.listeners
            entities.update(listeners.get("entities", set()))
        entities.update(self.trigger_entities)
        return entities

    def update_debounce_config(self, config: dict) -> None:
        """Hot-update debounce config -- cancel all pending, recreate global debouncer."""
        self._debounce_config = {**_DEBOUNCE_DEFAULTS, **config}
        for debouncer in self._entity_debouncers.values():
            debouncer.async_cancel()
        self._entity_debouncers.clear()
        if self._global_debouncer:
            self._global_debouncer.async_cancel()
        self._global_debouncer = Debouncer(
            self.hass, _LOGGER,
            cooldown=self._debounce_config.get("global", 5),
            immediate=True,
            function=self._async_execute_update,
        )

    def cancel_pending(self) -> None:
        """Cancel pending retries, debounced updates, and in-progress sends."""
        if self._retry_unsub:
            self._retry_unsub()
            self._retry_unsub = None
        self._retry_attempt = 0
        for debouncer in self._entity_debouncers.values():
            debouncer.async_cancel()
        self._entity_debouncers.clear()
        if self._global_debouncer:
            self._global_debouncer.async_cancel()
        if self._send_task and not self._send_task.done():
            self._send_task.cancel()
            self._send_task = None
        if self.status in ("retrying", "updating"):
            self.status = "idle"

    async def _on_retry(self, _now: Any) -> None:
        """Handle scheduled retry callback."""
        self._retry_unsub = None
        await self.async_trigger_update("retry")

    async def async_trigger_update(self, reason: str, *, force: bool = False) -> None:
        """Resolve templates, check hash, dispatch service call."""
        if not self.enabled:
            return

        if self._update_lock.locked():
            _LOGGER.debug("Profile %s: update already in progress, skipping (%s)", self.title, reason)
            return

        # A new intentional trigger supersedes any pending retry chain
        if reason != "retry":
            self._retry_attempt = 0
            if self._retry_unsub:
                self._retry_unsub()
                self._retry_unsub = None

        async with self._update_lock:
            self.status = "updating"
            try:
                resolved = _resolve_templates(self.hass, copy.deepcopy(self.payload_template))

                hash_input = json.dumps(
                    {"payload": resolved, "bg": self.background, "r": self.rotate,
                     "d": self.dither, "c": self.compress, "m": self.mirror},
                    sort_keys=True,
                    ensure_ascii=False,
                )
                payload_hash = hashlib.sha256(hash_input.encode()).hexdigest()

                if payload_hash == self.last_hash and not force:
                    _LOGGER.debug("Profile %s: no change, skipping (%s)", self.title, reason)
                    self.status = "idle"
                    return

                domain, service = self.service.split(".", 1)
                self._send_task = self.hass.async_create_task(
                    self.hass.services.async_call(
                        domain,
                        service,
                        {
                            "entity_id": self.entity_id,
                            "payload": resolved,
                            "background": self.background,
                            "rotate": self.rotate,
                            "dither": self.dither,
                            "compress": self.compress,
                            **({"mirror": self.mirror} if self.mirror and self.mirror != "none" else {}),
                            "dry_run": False,
                        },
                        blocking=True,
                    )
                )
                try:
                    async with asyncio.timeout(300):
                        await self._send_task
                finally:
                    self._send_task = None

                self.last_hash = payload_hash
                self.last_update = datetime.now(UTC)
                self.last_error = None
                self.status = "idle"
                self._retry_attempt = 0
                _LOGGER.info("Profile %s: updated (%s)", self.title, reason)

            except asyncio.CancelledError:
                self.status = "idle"
                _LOGGER.info("Profile %s: update cancelled (%s)", self.title, reason)

            except Exception as err:  # noqa: BLE001
                self.last_error = str(err)
                if self.retry_count > 0 and self._retry_attempt < self.retry_count:
                    self._retry_attempt += 1
                    self.status = "retrying"
                    delay = self.retry_delay * 60
                    self._retry_unsub = async_call_later(
                        self.hass, delay, self._on_retry
                    )
                    _LOGGER.info(
                        "Profile %s: update failed (%s): %s — retry %d/%d in %d min",
                        self.title, reason, err,
                        self._retry_attempt, self.retry_count, self.retry_delay,
                    )
                else:
                    self.status = "error"
                    _LOGGER.warning("Profile %s: update failed (%s): %s", self.title, reason, err)


def _resolve_templates(hass: HomeAssistant, payload: list[dict]) -> list[dict]:
    """Walk payload recursively, rendering Jinja2 templates in string values."""

    def _resolve(value: Any) -> Any:
        if isinstance(value, str) and _is_template(value):
            try:
                tpl = Template(value, hass)
                return tpl.async_render()
            except Exception:  # noqa: BLE001
                return value
        if isinstance(value, dict):
            return {k: _resolve(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_resolve(item) for item in value]
        return value

    return [_resolve(el) for el in payload]
