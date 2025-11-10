"""Support for HW Group binary sensors."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .const import CONF_DEVICE_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HW Group binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    binary_sensors = []
    binary_list = coordinator.data.get("binary_sensors", [])
    _LOGGER.info("Setting up %d binary sensors for entry %s", len(binary_list), entry.entry_id)
    
    for binary_data in binary_list:
        _LOGGER.debug("Creating binary sensor: %s", binary_data.get("name"))
        binary_sensors.append(
            HWGroupBinarySensor(
                coordinator,
                entry,
                binary_data,
            )
        )

    if binary_sensors:
        _LOGGER.info("Adding %d binary sensor entities", len(binary_sensors))
        async_add_entities(binary_sensors)
    else:
        _LOGGER.warning("No binary sensors found in coordinator data")


class HWGroupBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a HW Group binary sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        binary_data: dict,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._binary_id = binary_data["id"]
        self._attr_name = binary_data["name"]
        self._attr_unique_id = f"{entry.entry_id}_binary_{binary_data['id']}"
        
        # Determine device class based on type
        sensor_type = binary_data.get("type", "contact")
        if sensor_type == "alarm":
            self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        else:
            self._attr_device_class = BinarySensorDeviceClass.OPENING
        
        # Set device info
        device_info = coordinator.data.get("device_info", {})
        device_name = entry.data.get(CONF_DEVICE_NAME) or device_info.get("name", "HW Group Device")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "HW Group",
            "model": device_info.get("model", "Unknown"),
            "sw_version": device_info.get("version", "Unknown"),
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        for binary in self.coordinator.data.get("binary_sensors", []):
            if binary["id"] == self._binary_id:
                return binary.get("state", False)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        return {
            "binary_sensor_id": self._binary_id,
        }
