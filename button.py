"""Button entity for E-Ink Display Manager."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.button import ButtonEntity

from .const import DOMAIN
from .sensor import _device_info, _unique_id

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import ProfileCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up button entity for all profile subentries."""
    coordinators = hass.data[DOMAIN]["coordinators"]
    for sub_id, coordinator in coordinators.items():
        subentry = entry.subentries[sub_id]
        async_add_entities(
            [
                RefreshButton(coordinator, entry, subentry),
                StopButton(coordinator, entry, subentry),
            ],
            config_subentry_id=sub_id,
        )


class RefreshButton(ButtonEntity):
    """Manual refresh button for a display profile."""

    _attr_has_entity_name = True
    _attr_name = "Refresh"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: ProfileCoordinator, entry: ConfigEntry, subentry: Any) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = _unique_id(subentry, "refresh")
        self._attr_device_info = _device_info(entry, subentry)
        self._attr_config_entry_id = entry.entry_id
        self._attr_config_subentry_id = subentry.subentry_id

    async def async_press(self) -> None:
        """Handle button press."""
        await self._coordinator.async_trigger_update("manual", force=True)


class StopButton(ButtonEntity):
    """Cancel pending retries and debounced updates for a display profile."""

    _attr_has_entity_name = True
    _attr_name = "Stop"
    _attr_icon = "mdi:stop"

    def __init__(self, coordinator: ProfileCoordinator, entry: ConfigEntry, subentry: Any) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = _unique_id(subentry, "stop")
        self._attr_device_info = _device_info(entry, subentry)
        self._attr_config_entry_id = entry.entry_id
        self._attr_config_subentry_id = subentry.subentry_id

    async def async_press(self) -> None:
        """Cancel pending updates and retries."""
        self._coordinator.cancel_pending()
