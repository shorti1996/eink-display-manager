"""E-Ink Display Manager — scheduled updates for passive e-ink displays.

v2: singleton config entry + profile subentries.
"""

from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING, Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, callback
from homeassistant.helpers import (
    device_registry as dr,
    entity_registry as er,
)
from homeassistant.helpers.event import async_call_later

from .const import (
    CONF_BACKGROUND,
    CONF_COMPRESS,
    CONF_DEBOUNCE,
    CONF_DITHER,
    CONF_ENTITY_ID,
    CONF_HEIGHT,
    CONF_MIRROR,
    CONF_NAME,
    CONF_PAYLOAD_JSON,
    CONF_RETRY_COUNT,
    CONF_RETRY_DELAY,
    CONF_ROTATE,
    CONF_SERVICE,
    CONF_TRIGGER_ENTITIES,
    CONF_UPDATE_INTERVAL,
    CONF_WIDTH,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import ProfileCoordinator
from .frontend import JSModuleRegistration

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall

_LOGGER = logging.getLogger(__name__)

_STARTUP_RENDER_DELAY = 10     # seconds after HA started before first render
_STARTUP_RENDER_STAGGER = 10   # seconds between successive profile renders


# ─── Active‑profile persistence (file‑based) ──────────────────────────


def _active_profiles_path(hass: HomeAssistant) -> str:
    """Return path to the active‑profiles JSON file."""
    return hass.config.path(".storage", DOMAIN, "_active_profiles.json")


def _load_active_profiles_sync(hass: HomeAssistant) -> dict[str, str]:
    """Load {entity_id: subentry_id} map from file. Returns {} if missing."""
    path = _active_profiles_path(hass)
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        pass
    return {}


def _save_active_profiles_sync(hass: HomeAssistant, mapping: dict[str, str]) -> None:
    """Write {entity_id: subentry_id} map to file."""
    path = _active_profiles_path(hass)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(mapping, f, ensure_ascii=False)


async def async_load_active_profiles(hass: HomeAssistant) -> dict[str, str]:
    """Load active profiles map in executor."""
    return await hass.async_add_executor_job(_load_active_profiles_sync, hass)


async def async_save_active_profiles(hass: HomeAssistant, mapping: dict[str, str]) -> None:
    """Save active profiles map in executor."""
    await hass.async_add_executor_job(_save_active_profiles_sync, hass, mapping)


def is_profile_active(
    active_map: dict[str, str], entity_id: str, subentry_id: str
) -> bool:
    """Return True if *subentry_id* is the active profile for *entity_id*.

    If no entry exists yet for the display, the profile is considered active
    (backward‑compat: first profile wins).
    """
    return active_map.get(entity_id, subentry_id) == subentry_id


# ─── Integration setup (migration runs here, before entries) ─────────


async def async_setup(hass: HomeAssistant, config: Any) -> bool:
    """Set up integration — migrate, register frontend/WS/services once."""
    await _async_migrate_integration(hass)

    hass.data.setdefault(DOMAIN, {})

    # Register WS commands and services once (async_setup runs exactly once)
    _register_websocket_commands(hass)
    _register_services(hass)

    # Register frontend (static paths + Lovelace resource)
    async def _register_frontend(_event: Any = None) -> None:
        registrar = JSModuleRegistration(hass)
        await registrar.async_register()
        hass.data[DOMAIN]["frontend_registrar"] = registrar

    if hass.state is CoreState.running:
        await _register_frontend()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _register_frontend)

    return True


async def _async_migrate_integration(hass: HomeAssistant) -> None:
    """Consolidate v1 per-profile config entries into one v2 singleton + subentries.

    Follows the OpenAI pattern: first v1 entry becomes the parent (reused),
    subsequent v1 entries are absorbed into it and then removed.
    """
    from types import MappingProxyType

    entries = hass.config_entries.async_entries(DOMAIN)
    if not any(entry.version == 1 for entry in entries):
        return

    _LOGGER.info("Migrating E-Ink Display Manager from v1 to v2")
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    parent_entry: ConfigEntry | None = None

    for entry in list(entries):  # copy list since we may remove entries
        if entry.version != 1:
            continue

        old_entry_id = entry.entry_id
        data = {**entry.data, **entry.options}

        # Build subentry from old profile data (cold config only)
        subentry = ConfigSubentry(
            data=MappingProxyType({
                CONF_ENTITY_ID: data.get(CONF_ENTITY_ID, ""),
                CONF_SERVICE: data.get(CONF_SERVICE, ""),
                CONF_WIDTH: int(data.get(CONF_WIDTH, 296)),
                CONF_HEIGHT: int(data.get(CONF_HEIGHT, 128)),
                CONF_BACKGROUND: data.get(CONF_BACKGROUND, "white"),
                CONF_ROTATE: int(data.get(CONF_ROTATE, 0)),
                CONF_DITHER: data.get(CONF_DITHER, "floyd-steinberg"),
                CONF_UPDATE_INTERVAL: int(data.get(CONF_UPDATE_INTERVAL, 30)),
                CONF_TRIGGER_ENTITIES: list(data.get(CONF_TRIGGER_ENTITIES, [])),
                CONF_DEBOUNCE: int(data.get(CONF_DEBOUNCE, 60)),
            }),
            subentry_type="profile",
            title=data.get(CONF_NAME, entry.title),
            unique_id=None,
        )

        use_existing = parent_entry is None
        if use_existing:
            parent_entry = entry

        hass.config_entries.async_add_subentry(parent_entry, subentry)

        # Migrate payload to .storage file (hot data) — must run in executor
        payload_raw = data.get(CONF_PAYLOAD_JSON, "[]")
        store_dir = hass.config.path(".storage", DOMAIN)
        payload_path = os.path.join(store_dir, f"{subentry.subentry_id}.json")
        try:
            payload_str = payload_raw if isinstance(payload_raw, str) else json.dumps(payload_raw)
            await hass.async_add_executor_job(_write_payload_file, store_dir, payload_path, payload_str)
        except OSError:
            _LOGGER.warning("Could not write payload file for %s", subentry.title)

        # Migrate entities: update unique_id and link to parent + subentry
        for ent in er.async_entries_for_config_entry(entity_registry, old_entry_id):
            # unique_id is like "{old_entry_id}_status" → "{subentry_id}_status"
            suffix = ent.unique_id.removeprefix(f"{old_entry_id}_")
            if suffix == ent.unique_id:
                suffix = ent.unique_id  # didn't have expected prefix
            new_uid = f"{subentry.subentry_id}_{suffix}"
            try:
                entity_registry.async_update_entity(
                    ent.entity_id,
                    config_entry_id=parent_entry.entry_id,
                    config_subentry_id=subentry.subentry_id,
                    new_unique_id=new_uid,
                )
            except Exception:  # noqa: BLE001
                _LOGGER.debug("Could not migrate entity %s", ent.entity_id)

        # Migrate device: relink to subentry
        device = device_registry.async_get_device(
            identifiers={(DOMAIN, old_entry_id)}
        )
        if device is not None:
            if parent_entry.entry_id != old_entry_id:
                # Subsequent entry: move device to parent + subentry, remove old link
                device_registry.async_update_device(
                    device.id,
                    new_identifiers={(DOMAIN, subentry.subentry_id)},
                    add_config_subentry_id=subentry.subentry_id,
                    add_config_entry_id=parent_entry.entry_id,
                    remove_config_entry_id=old_entry_id,
                )
            else:
                # First entry (becomes parent): add subentry link, remove bare entry link
                # Must include add_config_entry_id even though it's the same entry,
                # because HA requires it when add_config_subentry_id is set.
                device_registry.async_update_device(
                    device.id,
                    new_identifiers={(DOMAIN, subentry.subentry_id)},
                    add_config_entry_id=parent_entry.entry_id,
                    add_config_subentry_id=subentry.subentry_id,
                    remove_config_entry_id=old_entry_id,
                    remove_config_subentry_id=None,
                )

        if not use_existing:
            # Remove the old entry (it's been absorbed into parent)
            await hass.config_entries.async_remove(old_entry_id)
        else:
            # Convert the first entry into the v2 singleton
            hass.config_entries.async_update_entry(
                entry,
                title="E-Ink Display Manager",
                data={},
                options={},
                version=2,
                minor_version=1,
            )

    _LOGGER.info(
        "Migration complete: %d profile(s) migrated",
        len(parent_entry.subentries) if parent_entry else 0,
    )


# ─── Entry setup / unload ────────────────────────────────────────────


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the singleton E-Ink Display Manager entry."""
    # Clean up payload files for deleted subentries
    await hass.async_add_executor_job(_cleanup_orphaned_payloads, hass, entry)

    # Load active-profile map from file
    active_map = await async_load_active_profiles(hass)

    # Create a coordinator for each profile subentry
    coordinators: dict[str, ProfileCoordinator] = {}
    hass.data.setdefault(DOMAIN, {})["coordinators"] = coordinators
    hass.data[DOMAIN]["active_profiles"] = active_map

    device_registry = dr.async_get(hass)
    for sub_id, subentry in entry.subentries.items():
        if subentry.subentry_type == "profile":
            # Explicitly register device linked to subentry
            data = subentry.data
            w = data.get(CONF_WIDTH, 296)
            h = data.get(CONF_HEIGHT, 128)
            device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                config_subentry_id=sub_id,
                identifiers={(DOMAIN, sub_id)},
                name=subentry.title,
                manufacturer="E-Ink Display Manager",
                model=f"{w}\u00d7{h}",
                entry_type=dr.DeviceEntryType.SERVICE,
            )

            entity_id = data.get(CONF_ENTITY_ID, "")
            enabled = is_profile_active(active_map, entity_id, sub_id)

            coord = ProfileCoordinator(hass, entry, subentry, enabled=enabled)
            coordinators[sub_id] = coord
            await coord.async_load_payload()

    # Defer trigger engine + startup renders until HA is fully started.
    # Template trackers fire as entities load during startup, which would
    # trigger BLE writes and keep the "starting…" toast visible for minutes.
    enabled_coords = [c for c in coordinators.values() if c.enabled]

    async def _activate_coordinators() -> None:
        """Start trigger engines, then schedule staggered startup renders."""
        for coord in enabled_coords:
            await coord.async_start()

        for idx, coord in enumerate(enabled_coords):
            delay = _STARTUP_RENDER_DELAY + idx * _STARTUP_RENDER_STAGGER

            async def _render(_now: Any, c: ProfileCoordinator = coord) -> None:
                await c.async_trigger_update("startup")

            entry.async_on_unload(async_call_later(hass, delay, _render))

    if hass.state is CoreState.running:
        # Runtime reload — HA already up, activate immediately
        await _activate_coordinators()
    elif enabled_coords:
        # Fresh boot — wait for HA to finish starting

        @callback
        def _on_ha_started(_event: Any) -> None:
            hass.async_create_task(_activate_coordinators())

        entry.async_on_unload(
            hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, _on_ha_started
            )
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Track subentry set — reload entry when profiles are added/removed
    hass.data[DOMAIN]["_subentry_ids"] = set(
        sid for sid, s in entry.subentries.items() if s.subentry_type == "profile"
    )

    async def _on_entry_update(
        hass: HomeAssistant, entry: ConfigEntry
    ) -> None:
        current = set(
            sid for sid, s in entry.subentries.items() if s.subentry_type == "profile"
        )
        previous = hass.data.get(DOMAIN, {}).get("_subentry_ids", set())
        if current != previous:
            await hass.config_entries.async_reload(entry.entry_id)

    entry.async_on_unload(entry.add_update_listener(_on_entry_update))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the singleton entry — stop all coordinators."""
    coordinators = hass.data.get(DOMAIN, {}).get("coordinators", {})
    for coordinator in coordinators.values():
        await coordinator.async_stop()
    hass.data.pop(DOMAIN, None)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def _cleanup_orphaned_payloads(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove payload files for subentries that no longer exist."""
    store_dir = hass.config.path(".storage", DOMAIN)
    if not os.path.isdir(store_dir):
        return
    live_ids = {
        sid for sid, s in entry.subentries.items()
        if s.subentry_type == "profile"
    }
    for fname in os.listdir(store_dir):
        if fname.startswith("_"):
            continue  # Skip internal files (_active_profiles.json, etc.)
        if fname.endswith(".json") and fname[:-5] not in live_ids:
            try:
                os.remove(os.path.join(store_dir, fname))
                _LOGGER.debug("Cleaned up orphaned payload file: %s", fname)
            except OSError:
                pass


# ─── Services ─────────────────────────────────────────────────────────


def _register_services(hass: HomeAssistant) -> None:
    """Register integration services."""

    async def _handle_refresh(call: ServiceCall) -> None:
        """Force refresh a specific profile via entity target."""
        entity_ids = call.data.get("entity_id", [])
        if isinstance(entity_ids, str):
            entity_ids = [entity_ids]

        ent_reg = er.async_get(hass)
        coordinators = hass.data.get(DOMAIN, {}).get("coordinators", {})
        for eid in entity_ids:
            entry = ent_reg.async_get(eid)
            if entry and entry.config_subentry_id:
                coordinator = coordinators.get(entry.config_subentry_id)
                if coordinator:
                    await coordinator.async_trigger_update("manual", force=True)

    async def _handle_refresh_all(call: ServiceCall) -> None:
        """Force refresh all enabled profiles."""
        coordinators = hass.data.get(DOMAIN, {}).get("coordinators", {})
        for coordinator in coordinators.values():
            if coordinator.enabled:
                await coordinator.async_trigger_update("refresh_all", force=True)

    hass.services.async_register(DOMAIN, "refresh", _handle_refresh)
    hass.services.async_register(DOMAIN, "refresh_all", _handle_refresh_all)


# ─── WebSocket API for editor card ────────────────────────────────────


_RECONFIGURE_KEYS = {
    CONF_BACKGROUND, CONF_ROTATE, CONF_DITHER, CONF_COMPRESS, CONF_MIRROR,
    CONF_UPDATE_INTERVAL, CONF_TRIGGER_ENTITIES, CONF_DEBOUNCE,
    CONF_RETRY_DELAY, CONF_RETRY_COUNT,
}


async def _async_persist_subentry_data(
    hass: HomeAssistant, entry: ConfigEntry, subentry: Any, new_data: dict
) -> None:
    """Persist updated subentry data via programmatic reconfigure flow.

    Handles coercion (rotate int→str) required by the form schema.
    Only passes keys accepted by _reconfigure_schema to avoid validation errors.
    """
    form_data = {k: v for k, v in new_data.items() if k in _RECONFIGURE_KEYS}
    # The reconfigure form schema expects rotate as a string (select selector)
    if CONF_ROTATE in form_data:
        form_data[CONF_ROTATE] = str(form_data[CONF_ROTATE])
    _LOGGER.debug("Persisting profile settings: %s", form_data)
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "profile"),
        context={"source": "reconfigure", "subentry_id": subentry.subentry_id},
    )
    _LOGGER.debug("Reconfigure init result type: %s", result.get("type"))
    if result.get("type") == "form":
        result2 = await hass.config_entries.subentries.async_configure(
            result["flow_id"], form_data
        )
        _LOGGER.debug("Reconfigure configure result type: %s", result2.get("type") if result2 else None)


def _resolve_subentry(hass: HomeAssistant, msg: dict) -> tuple[Any, Any]:
    """Find subentry by subentry_id or legacy config_entry_id."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        # New path: subentry_id
        if sid := msg.get("subentry_id"):
            if sid in entry.subentries:
                return entry, entry.subentries[sid]
        # Legacy path: config_entry_id (for migrated v1 entries)
        if cid := msg.get("config_entry_id"):
            for sub in entry.subentries.values():
                if sub.data.get("_legacy_uid_prefix") == cid:
                    return entry, sub
    return None, None


def _register_websocket_commands(hass: HomeAssistant) -> None:
    """Register WS commands for the WYSIWYG editor card."""

    @websocket_api.websocket_command({
        vol.Required("type"): "eink_display_manager/test_reconfigure",
    })
    @websocket_api.async_response
    async def ws_test_reconfigure(hass, connection, msg):
        """Debug: test subentry reconfigure flow directly."""
        import traceback
        try:
            entries = hass.config_entries.async_entries(DOMAIN)
            entry = entries[0]
            sub = list(entry.subentries.values())[0]
            _LOGGER.warning("TEST: entry=%s sub=%s", entry.entry_id, sub.subentry_id)

            result = await hass.config_entries.subentries.async_init(
                (entry.entry_id, "profile"),
                context={"source": "reconfigure", "subentry_id": sub.subentry_id},
            )
            _LOGGER.warning("TEST RESULT: %s", result)
            connection.send_result(msg["id"], {"result": str(result)})
        except Exception as ex:
            _LOGGER.error("TEST FAILED: %s\n%s", ex, traceback.format_exc())
            connection.send_error(msg["id"], "error", str(ex))

    websocket_api.async_register_command(hass, ws_test_reconfigure)

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "eink_display_manager/list_profiles",
        }
    )
    @websocket_api.async_response
    async def ws_list_profiles(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
    ) -> None:
        """Return all display profile subentries."""
        entries = hass.config_entries.async_entries(DOMAIN)
        device_registry = dr.async_get(hass)
        profiles = []
        for entry in entries:
            for sub_id, subentry in entry.subentries.items():
                if subentry.subentry_type == "profile":
                    data = subentry.data
                    # Prefer device name (user may have renamed it) over subentry title
                    title = subentry.title
                    device = device_registry.async_get_device(
                        identifiers={(DOMAIN, sub_id)}
                    )
                    if device and device.name_by_user:
                        title = device.name_by_user
                    elif device and device.name:
                        title = device.name
                    profiles.append(
                        {
                            "subentry_id": sub_id,
                            "entry_id": entry.entry_id,
                            "title": title,
                            "entity_id": data.get(CONF_ENTITY_ID, ""),
                            "service": data.get(CONF_SERVICE, ""),
                            "width": int(data.get(CONF_WIDTH, 296)),
                            "height": int(data.get(CONF_HEIGHT, 128)),
                            "background": data.get(CONF_BACKGROUND, "white"),
                            "enabled": is_profile_active(
                                hass.data.get(DOMAIN, {}).get("active_profiles", {}),
                                data.get(CONF_ENTITY_ID, ""),
                                sub_id,
                            ),
                        }
                    )
        connection.send_result(msg["id"], {"profiles": profiles})

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "eink_display_manager/get_payload",
            vol.Optional("subentry_id"): str,
            vol.Optional("config_entry_id"): str,
        }
    )
    @websocket_api.async_response
    async def ws_get_payload(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
    ) -> None:
        """Return the payload and settings for a profile subentry."""
        entry, subentry = _resolve_subentry(hass, msg)
        if entry is None or subentry is None:
            connection.send_error(msg["id"], "not_found", "Profile not found")
            return

        data = subentry.data
        # Load payload from file (hot data)
        coord = hass.data.get(DOMAIN, {}).get("coordinators", {}).get(
            subentry.subentry_id
        )
        payload = coord.payload_template if coord else []

        connection.send_result(
            msg["id"],
            {
                "payload": payload,
                "subentry_id": subentry.subentry_id,
                "entity_id": data.get(CONF_ENTITY_ID, ""),
                "service": data.get(CONF_SERVICE, ""),
                "width": int(data.get(CONF_WIDTH, 296)),
                "height": int(data.get(CONF_HEIGHT, 128)),
                "background": data.get(CONF_BACKGROUND, "white"),
                "rotate": int(data.get(CONF_ROTATE, 0)),
                "dither": data.get(CONF_DITHER, "none"),
                "update_interval_minutes": int(
                    data.get(CONF_UPDATE_INTERVAL, 30)
                ),
                "trigger_entities": list(
                    data.get(CONF_TRIGGER_ENTITIES, [])
                ),
                "trigger_debounce_seconds": int(
                    data.get(CONF_DEBOUNCE, 60)
                ),
                "compress": bool(data.get(CONF_COMPRESS, True)),
                "mirror": data.get(CONF_MIRROR, "none"),
            },
        )

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "eink_display_manager/update_payload",
            vol.Optional("subentry_id"): str,
            vol.Optional("config_entry_id"): str,
            vol.Required("payload"): list,
        }
    )
    @websocket_api.async_response
    async def ws_update_payload(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
    ) -> None:
        """Hot-update payload: write to file + poke coordinator. No entry reload."""
        entry, subentry = _resolve_subentry(hass, msg)
        if entry is None or subentry is None:
            connection.send_error(msg["id"], "not_found", "Profile not found")
            return

        coord = hass.data.get(DOMAIN, {}).get("coordinators", {}).get(
            subentry.subentry_id
        )
        if coord:
            await coord.update_payload(msg["payload"])
        else:
            # No coordinator running — just write the file
            store_dir = hass.config.path(".storage", DOMAIN)
            os.makedirs(store_dir, exist_ok=True)
            path = os.path.join(store_dir, f"{subentry.subentry_id}.json")
            await hass.async_add_executor_job(
                _write_json, path, msg["payload"]
            )

        connection.send_result(msg["id"], {"success": True})

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "eink_display_manager/create_profile",
            vol.Required("entity_id"): str,
        }
    )
    @websocket_api.async_response
    async def ws_create_profile(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
    ) -> None:
        """Auto-create a profile subentry from the card editor."""
        from types import MappingProxyType

        from .config_flow import _derive_service, _derive_title, _detect_dimensions

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            connection.send_error(
                msg["id"], "not_installed",
                "E-Ink Display Manager integration is not set up",
            )
            return

        entry = entries[0]  # singleton
        entity_id = msg["entity_id"]

        # Check if profile already exists for this entity
        for sub in entry.subentries.values():
            if sub.data.get(CONF_ENTITY_ID) == entity_id:
                connection.send_result(msg["id"], {
                    "subentry_id": sub.subentry_id,
                    "created": False,
                })
                return

        service = _derive_service(hass, entity_id)
        width, height = _detect_dimensions(hass, entity_id)
        title = _derive_title(hass, entity_id)

        subentry = ConfigSubentry(
            data=MappingProxyType({
                CONF_ENTITY_ID: entity_id,
                CONF_SERVICE: service,
                CONF_WIDTH: width,
                CONF_HEIGHT: height,
                CONF_BACKGROUND: "white",
                CONF_ROTATE: 0,
                CONF_DITHER: "none",
                CONF_COMPRESS: True,
                CONF_MIRROR: "none",
                CONF_UPDATE_INTERVAL: 30,
                CONF_TRIGGER_ENTITIES: [],
                CONF_DEBOUNCE: 60,
            }),
            subentry_type="profile",
            title=title,
            unique_id=None,
        )
        hass.config_entries.async_add_subentry(entry, subentry)

        connection.send_result(msg["id"], {
            "subentry_id": subentry.subentry_id,
            "created": True,
        })

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "eink_display_manager/resolve_templates",
            vol.Required("payload"): list,
        }
    )
    @websocket_api.async_response
    async def ws_resolve_templates(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
    ) -> None:
        """Resolve Jinja2 templates in a payload and return the result."""
        import copy

        from .coordinator import _resolve_templates

        resolved = _resolve_templates(hass, copy.deepcopy(msg["payload"]))
        connection.send_result(msg["id"], {"payload": resolved})

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "eink_display_manager/update_profile_settings",
            vol.Optional("subentry_id"): str,
            vol.Optional("config_entry_id"): str,
            vol.Optional("dither"): str,
            vol.Optional("background"): str,
            vol.Optional("rotate"): int,
            vol.Optional("compress"): bool,
            vol.Optional("mirror"): str,
        }
    )
    @websocket_api.async_response
    async def ws_update_profile_settings(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
    ) -> None:
        """Update profile display settings (cold config + coordinator)."""
        entry, subentry = _resolve_subentry(hass, msg)
        if entry is None or subentry is None:
            connection.send_error(msg["id"], "not_found", "Profile not found")
            return

        # Build updated data dict from current + overrides
        new_data = dict(subentry.data)
        changed = False
        for key in (CONF_DITHER, CONF_BACKGROUND, CONF_ROTATE, CONF_COMPRESS, CONF_MIRROR):
            if key in msg and msg[key] != new_data.get(key):
                new_data[key] = msg[key]
                changed = True

        if not changed:
            connection.send_result(msg["id"], {"success": True})
            return

        # Hot-update the coordinator immediately
        coord = hass.data.get(DOMAIN, {}).get("coordinators", {}).get(
            subentry.subentry_id
        )
        if coord:
            if CONF_DITHER in msg:
                coord.dither = msg[CONF_DITHER]
            if CONF_BACKGROUND in msg:
                coord.background = msg[CONF_BACKGROUND]
            if CONF_ROTATE in msg:
                coord.rotate = msg[CONF_ROTATE]
            if CONF_COMPRESS in msg:
                coord.compress = msg[CONF_COMPRESS]
            if CONF_MIRROR in msg:
                coord.mirror = msg[CONF_MIRROR]

        # Persist via programmatic reconfigure flow
        try:
            await _async_persist_subentry_data(hass, entry, subentry, new_data)
        except Exception as ex:
            _LOGGER.warning("Could not persist profile settings: %s", ex)

        connection.send_result(msg["id"], {"success": True})

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "eink_display_manager/activate_profile",
            vol.Required("subentry_id"): str,
        }
    )
    @websocket_api.async_response
    async def ws_activate_profile(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
    ) -> None:
        """Activate a profile and deactivate siblings for the same display."""
        entry, subentry = _resolve_subentry(hass, msg)
        if entry is None or subentry is None:
            connection.send_error(msg["id"], "not_found", "Profile not found")
            return

        coordinators = hass.data.get(DOMAIN, {}).get("coordinators", {})
        switches = hass.data.get(DOMAIN, {}).get("switches", {})
        target_entity_id = subentry.data.get(CONF_ENTITY_ID)

        # Disable siblings targeting the same display
        for sub_id, sub in entry.subentries.items():
            if sub_id == subentry.subentry_id:
                continue
            if sub.data.get(CONF_ENTITY_ID) != target_entity_id:
                continue
            coord = coordinators.get(sub_id)
            if coord and coord.enabled:
                await coord.async_stop()
                coord.enabled = False
                sibling_switch = switches.get(sub_id)
                if sibling_switch:
                    sibling_switch.async_write_ha_state()

        # Enable the target profile
        coord = coordinators.get(subentry.subentry_id)
        if coord:
            coord.enabled = True
            await coord.async_start()
            my_switch = switches.get(subentry.subentry_id)
            if my_switch:
                my_switch.async_write_ha_state()

        # Persist active profile to file
        active_map = hass.data.get(DOMAIN, {}).get("active_profiles", {})
        active_map[target_entity_id] = subentry.subentry_id
        hass.data[DOMAIN]["active_profiles"] = active_map
        await async_save_active_profiles(hass, active_map)

        connection.send_result(msg["id"], {"success": True})

    websocket_api.async_register_command(hass, ws_list_profiles)
    websocket_api.async_register_command(hass, ws_get_payload)
    websocket_api.async_register_command(hass, ws_update_payload)
    websocket_api.async_register_command(hass, ws_create_profile)
    websocket_api.async_register_command(hass, ws_resolve_templates)
    websocket_api.async_register_command(hass, ws_update_profile_settings)
    websocket_api.async_register_command(hass, ws_activate_profile)


def _write_json(path: str, data: Any) -> None:
    """Write JSON to a file (runs in executor)."""
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False)


def _write_payload_file(store_dir: str, path: str, content: str) -> None:
    """Write payload string to file, creating directory if needed (runs in executor)."""
    os.makedirs(store_dir, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
