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
    CONF_DEBOUNCE,
    CONF_DITHER,
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
        self.debounce_seconds: int = int(data.get(CONF_DEBOUNCE, 60))
        self.retry_delay: int = int(data.get(CONF_RETRY_DELAY, 5))
        self.retry_count: int = int(data.get(CONF_RETRY_COUNT, 3))

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
        self._debounce_task: asyncio.Task | None = None
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
        for unsub in self._unsub_entities:
            unsub()
        self._unsub_entities.clear()
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()
            self._debounce_task = None
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
        changed = [
            f"{u.template.template}: {u.last_result!r} -> {u.result!r}"
            for u in updates
            if u.last_result != u.result
        ]
        _LOGGER.debug(
            "Profile %s: %d template(s) changed: %s",
            self.title, len(changed), "; ".join(changed),
        )
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()
        self._debounce_task = self.hass.async_create_task(
            self._debounced_update("template_dep"),
        )

    async def _on_entity_change(self, event: Event) -> None:
        """Handle entity state change with debounce."""
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()
        entity_id = event.data.get("entity_id", "unknown")
        self._debounce_task = self.hass.async_create_task(
            self._debounced_update(f"entity:{entity_id}"),
        )

    async def _debounced_update(self, reason: str) -> None:
        """Wait for debounce period, then trigger update."""
        try:
            await asyncio.sleep(self.debounce_seconds)
            await self.async_trigger_update(reason)
        except asyncio.CancelledError:
            pass

    def cancel_pending(self) -> None:
        """Cancel pending retries, debounced updates, and in-progress sends."""
        if self._retry_unsub:
            self._retry_unsub()
            self._retry_unsub = None
        self._retry_attempt = 0
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()
            self._debounce_task = None
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
                    {"payload": resolved, "bg": self.background, "r": self.rotate, "d": self.dither},
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
