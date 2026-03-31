"""Config flow for E-Ink Display Manager (v2 — singleton + subentries)."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigEntryState,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import selector

from .const import (
    CONF_BACKGROUND,
    CONF_DEBOUNCE,
    CONF_DITHER,
    CONF_ENTITY_ID,
    CONF_HEIGHT,
    CONF_RETRY_COUNT,
    CONF_RETRY_DELAY,
    CONF_ROTATE,
    CONF_SERVICE,
    CONF_TRIGGER_ENTITIES,
    CONF_UPDATE_INTERVAL,
    CONF_WIDTH,
    DOMAIN,
)


# ─── Helper functions ────────────────────────────────────────────────


def _derive_service(hass: HomeAssistant, entity_id: str) -> str:
    """Derive the drawcustom service from an image entity's platform."""
    ent_reg = er.async_get(hass)
    entry = ent_reg.async_get(entity_id)
    if entry and entry.platform:
        return f"{entry.platform}.drawcustom"
    # Fallback: discover any *.drawcustom service
    services = hass.services.async_services()
    for dom, svcs in services.items():
        if "drawcustom" in svcs:
            return f"{dom}.drawcustom"
    return "wolink_esl.drawcustom"


def _detect_dimensions(hass: HomeAssistant, entity_id: str) -> tuple[int, int]:
    """Read display_width/display_height from image entity state attributes."""
    state = hass.states.get(entity_id)
    if state:
        w = state.attributes.get("display_width")
        h = state.attributes.get("display_height")
        if w is not None and h is not None:
            return (int(w), int(h))
    return (296, 128)


def _derive_title(hass: HomeAssistant, entity_id: str) -> str:
    """Generate a human-readable profile title from the entity."""
    state = hass.states.get(entity_id)
    if state and state.attributes.get("friendly_name"):
        return state.attributes["friendly_name"]
    return entity_id.replace("image.", "").replace("_", " ").title()


def _reconfigure_schema(data: dict) -> vol.Schema:
    """Schema for editing schedule + rendering settings of an existing profile."""
    return vol.Schema(
        {
            vol.Required(
                CONF_BACKGROUND, default=data.get(CONF_BACKGROUND, "white")
            ): selector(
                {"select": {"options": ["white", "black", "red", "yellow"]}}
            ),
            vol.Required(
                CONF_ROTATE, default=str(data.get(CONF_ROTATE, 0))
            ): selector(
                {
                    "select": {
                        "options": [
                            {"value": "0", "label": "0°"},
                            {"value": "90", "label": "90°"},
                            {"value": "180", "label": "180°"},
                            {"value": "270", "label": "270°"},
                        ]
                    }
                }
            ),
            vol.Required(
                CONF_DITHER, default=data.get(CONF_DITHER, "none")
            ): selector(
                {
                    "select": {
                        "options": [
                            "floyd-steinberg",
                            "atkinson",
                            "stucki",
                            "none",
                        ]
                    }
                }
            ),
            vol.Required(
                CONF_UPDATE_INTERVAL,
                default=int(data.get(CONF_UPDATE_INTERVAL, 30)),
            ): selector({"number": {"min": 0, "max": 1440, "mode": "box"}}),
            vol.Optional(
                CONF_TRIGGER_ENTITIES,
                default=data.get(CONF_TRIGGER_ENTITIES, []),
            ): selector({"entity": {"multiple": True}}),
            vol.Required(
                CONF_DEBOUNCE, default=int(data.get(CONF_DEBOUNCE, 60))
            ): selector({"number": {"min": 0, "max": 600, "mode": "box"}}),
            vol.Required(
                CONF_RETRY_DELAY, default=int(data.get(CONF_RETRY_DELAY, 5))
            ): selector({"number": {"min": 1, "max": 60, "mode": "box", "unit_of_measurement": "min"}}),
            vol.Required(
                CONF_RETRY_COUNT, default=int(data.get(CONF_RETRY_COUNT, 3))
            ): selector({"number": {"min": 0, "max": 10, "mode": "box"}}),
        }
    )


# ─── Singleton config flow ───────────────────────────────────────────


def _make_subentry_data(
    hass: Any, entity_id: str
) -> tuple[str, dict[str, Any]]:
    """Build subentry title + data from an entity_id."""
    service = _derive_service(hass, entity_id)
    width, height = _detect_dimensions(hass, entity_id)
    title = _derive_title(hass, entity_id)
    data = {
        CONF_ENTITY_ID: entity_id,
        CONF_SERVICE: service,
        CONF_WIDTH: width,
        CONF_HEIGHT: height,
        CONF_BACKGROUND: "white",
        CONF_ROTATE: 0,
        CONF_DITHER: "none",
        CONF_UPDATE_INTERVAL: 30,
        CONF_TRIGGER_ENTITIES: [],
        CONF_DEBOUNCE: 60,
        CONF_RETRY_DELAY: 5,
        CONF_RETRY_COUNT: 3,
    }
    return title, data


class EinkDisplayManagerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow — creates singleton + first profile in one step."""

    VERSION = 2

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return EinkDisplayManagerOptionsFlow()

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Declare profile as a subentry type."""
        return {"profile": ProfileSubentryFlowHandler}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick a display entity → create singleton + first profile in one shot."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            title, subentry_data = _make_subentry_data(
                self.hass, user_input[CONF_ENTITY_ID]
            )
            return self.async_create_entry(
                title="E-Ink Display Manager",
                data={},
                subentries=[
                    {
                        "subentry_type": "profile",
                        "data": subentry_data,
                        "title": title,
                        "unique_id": None,
                    },
                ],
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ENTITY_ID): selector(
                        {"entity": {"filter": [{"domain": "image"}]}}
                    ),
                }
            ),
        )


# ─── Options flow (singleton has no options) ─────────────────────────


class EinkDisplayManagerOptionsFlow(OptionsFlow):
    """Empty options flow — singleton has no configurable options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return self.async_abort(reason="no_options")


# ─── Profile subentry flow ───────────────────────────────────────────


class ProfileSubentryFlowHandler(ConfigSubentryFlow):
    """Flow for adding / editing display profile subentries."""

    @property
    def _is_new(self) -> bool:
        return self.source == "user"

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Add a new profile — user picks an image entity."""
        if user_input is not None:
            title, data = _make_subentry_data(
                self.hass, user_input[CONF_ENTITY_ID]
            )
            # If a sibling profile already targets this display, ensure it's
            # recorded as active so the new profile starts inactive.
            entry = self._get_entry()
            entity_id = user_input[CONF_ENTITY_ID]
            for sub in entry.subentries.values():
                if sub.data.get(CONF_ENTITY_ID) == entity_id:
                    from . import async_load_active_profiles, async_save_active_profiles
                    active_map = await async_load_active_profiles(self.hass)
                    if entity_id not in active_map:
                        active_map[entity_id] = sub.subentry_id
                        self.hass.data.setdefault(DOMAIN, {})["active_profiles"] = active_map
                        await async_save_active_profiles(self.hass, active_map)
                    break
            return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ENTITY_ID): selector(
                        {"entity": {"filter": [{"domain": "image"}]}}
                    ),
                }
            ),
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Entry point for reconfigure — store current data, delegate."""
        self._options = dict(self._get_reconfigure_subentry().data)
        return await self.async_step_set_options()

    async def async_step_set_options(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Shared form for editing profile settings."""
        if self._get_entry().state != ConfigEntryState.LOADED:
            return self.async_abort(reason="entry_not_loaded")

        if user_input is None:
            return self.async_show_form(
                step_id="set_options",
                data_schema=_reconfigure_schema(self._options),
            )

        self._options.update(user_input)
        # Selector returns rotate as string; coerce back to int for storage
        self._options[CONF_ROTATE] = int(self._options[CONF_ROTATE])

        entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()

        # Hot-update coordinator with new settings
        coordinators = self.hass.data.get(DOMAIN, {}).get("coordinators", {})
        coord = coordinators.get(subentry.subentry_id)
        if coord:
            coord.background = self._options.get(CONF_BACKGROUND, coord.background)
            coord.rotate = int(self._options.get(CONF_ROTATE, coord.rotate))
            coord.dither = self._options.get(CONF_DITHER, coord.dither)
            coord.retry_delay = int(self._options.get(CONF_RETRY_DELAY, coord.retry_delay))
            coord.retry_count = int(self._options.get(CONF_RETRY_COUNT, coord.retry_count))

        return self.async_update_and_abort(
            entry,
            subentry,
            data=self._options,
        )
