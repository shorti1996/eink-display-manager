"""Sensor entities for E-Ink Display Manager."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory

from .const import CONF_HEIGHT, CONF_WIDTH, DOMAIN

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import ProfileCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor entities for all profile subentries."""
    coordinators = hass.data[DOMAIN]["coordinators"]
    for sub_id, coordinator in coordinators.items():
        subentry = entry.subentries[sub_id]
        async_add_entities(
            [
                LastUpdateSensor(coordinator, entry, subentry),
                StatusSensor(coordinator, entry, subentry),
            ],
            config_subentry_id=sub_id,
        )


def _device_info(entry: ConfigEntry, subentry: Any) -> DeviceInfo:
    """Shared device info — one device per profile subentry."""
    data = subentry.data
    w = data.get(CONF_WIDTH, 296)
    h = data.get(CONF_HEIGHT, 128)
    return DeviceInfo(
        identifiers={(DOMAIN, subentry.subentry_id)},
        name=subentry.title,
        manufacturer="E-Ink Display Manager",
        model=f"{w}\u00d7{h}",
        entry_type="service",
    )


def _unique_id(subentry: Any, suffix: str) -> str:
    """Build unique_id, using legacy prefix for migrated subentries."""
    prefix = subentry.data.get("_legacy_uid_prefix", subentry.subentry_id)
    return f"{prefix}_{suffix}"


class LastUpdateSensor(SensorEntity):
    """Timestamp of last successful display update."""

    _attr_has_entity_name = True
    _attr_name = "Last Update"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: ProfileCoordinator, entry: ConfigEntry, subentry: Any) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = _unique_id(subentry, "last_update")
        self._attr_device_info = _device_info(entry, subentry)
        self._attr_config_entry_id = entry.entry_id
        self._attr_config_subentry_id = subentry.subentry_id

    @property
    def native_value(self) -> datetime | None:
        return self._coordinator.last_update

    @property
    def available(self) -> bool:
        return True


class StatusSensor(SensorEntity):
    """Current status of the display profile."""

    _attr_has_entity_name = True
    _attr_name = "Status"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["idle", "updating", "retrying", "error"]
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: ProfileCoordinator, entry: ConfigEntry, subentry: Any) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = _unique_id(subentry, "status")
        self._attr_device_info = _device_info(entry, subentry)
        self._attr_config_entry_id = entry.entry_id
        self._attr_config_subentry_id = subentry.subentry_id

    @property
    def native_value(self) -> str:
        return self._coordinator.status

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self._coordinator.last_error:
            return {"last_error": self._coordinator.last_error}
        return None

    @property
    def available(self) -> bool:
        return True
