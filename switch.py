"""Switch entity for E-Ink Display Manager."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN
from .sensor import _device_info, _unique_id

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import ProfileCoordinator

_LOGGER = logging.getLogger(__name__)


async def _async_save_active_profile(
    hass: HomeAssistant, entity_id: str, subentry_id: str
) -> None:
    """Persist which profile is active for a display entity."""
    from . import async_save_active_profiles

    active_map = hass.data.get(DOMAIN, {}).get("active_profiles", {})
    active_map[entity_id] = subentry_id
    hass.data[DOMAIN]["active_profiles"] = active_map
    await async_save_active_profiles(hass, active_map)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up switch entity for all profile subentries."""
    coordinators = hass.data[DOMAIN]["coordinators"]
    switches: dict[str, ProfileEnabledSwitch] = hass.data[DOMAIN].setdefault("switches", {})
    for sub_id, coordinator in coordinators.items():
        subentry = entry.subentries[sub_id]
        switch = ProfileEnabledSwitch(coordinator, entry, subentry)
        switches[sub_id] = switch
        async_add_entities(
            [switch],
            config_subentry_id=sub_id,
        )


class ProfileEnabledSwitch(SwitchEntity):
    """Toggle to pause/resume a display profile."""

    _attr_has_entity_name = True
    _attr_name = "Enabled"
    _attr_icon = "mdi:play-pause"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: ProfileCoordinator, entry: ConfigEntry, subentry: Any) -> None:
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = _unique_id(subentry, "enabled")
        self._attr_device_info = _device_info(entry, subentry)
        self._attr_config_entry_id = entry.entry_id
        self._attr_config_subentry_id = subentry.subentry_id

    @property
    def is_on(self) -> bool:
        return self._coordinator.enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        coordinators = self.hass.data[DOMAIN]["coordinators"]
        switches = self.hass.data[DOMAIN].get("switches", {})
        my_entity_id = self._coordinator.entity_id

        # Disable all other profiles targeting the same display
        for sub_id, coord in coordinators.items():
            if sub_id == self._coordinator.subentry_id:
                continue
            if coord.entity_id != my_entity_id:
                continue
            if not coord.enabled:
                continue
            await coord.async_stop()
            coord.enabled = False
            sibling = switches.get(sub_id)
            if sibling:
                sibling.async_write_ha_state()

        # Enable self
        self._coordinator.enabled = True
        await self._coordinator.async_start()
        self.async_write_ha_state()

        # Persist
        await _async_save_active_profile(
            self.hass, my_entity_id, self._coordinator.subentry_id
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._coordinator.async_stop()
        self._coordinator.enabled = False
        self.async_write_ha_state()
        # Note: turning off doesn't set another profile as active —
        # the display just has no active profile until one is turned on.
