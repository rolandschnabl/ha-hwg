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
from .const import CONF_INVERT_BINARY_SENSORS

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
    inverted_sensors = entry.data.get(CONF_INVERT_BINARY_SENSORS, [])
    
    _LOGGER.info(
        "Setting up %d binary sensors for entry %s, inverted sensors: %s", 
        len(binary_list), 
        entry.entry_id,
        inverted_sensors
    )
    
    for binary_data in binary_list:
        _LOGGER.debug("Creating binary sensor: %s (ID: %s)", binary_data.get("name"), binary_data.get("id"))
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
        self._entry_id = entry.entry_id
        
        # Determine device class and icon based on name and type
        sensor_name_lower = binary_data["name"].lower()
        sensor_type = binary_data.get("type", "contact")
        
        # Auto-detect device class and icon from name
        if any(keyword in sensor_name_lower for keyword in ["door", "tür", "türe", "tur"]):
            self._attr_device_class = BinarySensorDeviceClass.DOOR
            self._attr_icon = "mdi:door"
        elif any(keyword in sensor_name_lower for keyword in ["window", "fenster"]):
            self._attr_device_class = BinarySensorDeviceClass.WINDOW
            self._attr_icon = "mdi:window-closed"
        elif any(keyword in sensor_name_lower for keyword in ["motion", "bewegung", "pir"]):
            self._attr_device_class = BinarySensorDeviceClass.MOTION
            self._attr_icon = "mdi:motion-sensor"
        elif any(keyword in sensor_name_lower for keyword in ["smoke", "rauch", "fire", "feuer"]):
            self._attr_device_class = BinarySensorDeviceClass.SMOKE
            self._attr_icon = "mdi:smoke-detector"
        elif any(keyword in sensor_name_lower for keyword in ["water", "wasser", "leak", "leck"]):
            self._attr_device_class = BinarySensorDeviceClass.MOISTURE
            self._attr_icon = "mdi:water-alert"
        elif any(keyword in sensor_name_lower for keyword in ["hum", "humidity", "feucht", "moisture"]):
            self._attr_device_class = BinarySensorDeviceClass.MOISTURE
            self._attr_icon = "mdi:water-percent"
        elif any(keyword in sensor_name_lower for keyword in ["temp", "temperature", "heat", "cold"]):
            self._attr_device_class = BinarySensorDeviceClass.HEAT
            self._attr_icon = "mdi:thermometer-alert"
        elif any(keyword in sensor_name_lower for keyword in ["vibration", "vibr", "shock"]):
            self._attr_device_class = BinarySensorDeviceClass.VIBRATION
            self._attr_icon = "mdi:vibrate"
        elif any(keyword in sensor_name_lower for keyword in ["sound", "noise", "geräusch", "laut"]):
            self._attr_device_class = BinarySensorDeviceClass.SOUND
            self._attr_icon = "mdi:volume-high"
        elif any(keyword in sensor_name_lower for keyword in ["power", "strom", "electricity"]):
            self._attr_device_class = BinarySensorDeviceClass.POWER
            self._attr_icon = "mdi:power-plug"
        elif any(keyword in sensor_name_lower for keyword in ["gas"]):
            self._attr_device_class = BinarySensorDeviceClass.GAS
            self._attr_icon = "mdi:gas-cylinder"
        elif any(keyword in sensor_name_lower for keyword in ["light", "licht", "brightness"]):
            self._attr_device_class = BinarySensorDeviceClass.LIGHT
            self._attr_icon = "mdi:lightbulb"
        elif any(keyword in sensor_name_lower for keyword in ["presence", "anwesenheit", "occupancy"]):
            self._attr_device_class = BinarySensorDeviceClass.OCCUPANCY
            self._attr_icon = "mdi:home-account"
        elif any(keyword in sensor_name_lower for keyword in ["comm", "connection", "verbindung", "network"]):
            self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
            self._attr_icon = "mdi:network"
        elif any(keyword in sensor_name_lower for keyword in ["alarm", "alert"]):
            self._attr_device_class = BinarySensorDeviceClass.PROBLEM
            self._attr_icon = "mdi:bell-alert"
        elif any(keyword in sensor_name_lower for keyword in ["battery", "batterie", "akku"]):
            self._attr_device_class = BinarySensorDeviceClass.BATTERY
            self._attr_icon = "mdi:battery-alert"
        elif sensor_type == "alarm":
            self._attr_device_class = BinarySensorDeviceClass.PROBLEM
            self._attr_icon = "mdi:alert-circle"
        else:
            # Default fallback
            self._attr_device_class = BinarySensorDeviceClass.OPENING
            self._attr_icon = "mdi:electric-switch"
        
        _LOGGER.debug(
            "Binary sensor '%s' detected as %s with icon %s",
            binary_data["name"],
            self._attr_device_class,
            self._attr_icon
        )
        
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
                state = binary.get("state", False)
                
                # Get current entry data dynamically to support live updates
                entry = self.hass.config_entries.async_get_entry(self._entry_id)
                if entry:
                    inverted_sensors = entry.data.get(CONF_INVERT_BINARY_SENSORS, [])
                    if self._binary_id in inverted_sensors:
                        _LOGGER.debug(
                            "Inverting binary sensor %s (ID: %s): %s -> %s",
                            self._attr_name,
                            self._binary_id,
                            state,
                            not state
                        )
                        state = not state
                    
                return state
        return None

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        # Get current entry data dynamically to support live updates
        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        inverted_sensors = entry.data.get(CONF_INVERT_BINARY_SENSORS, []) if entry else []
        is_inverted = self._binary_id in inverted_sensors
        
        return {
            "binary_sensor_id": self._binary_id,
            "inverted": is_inverted,
        }
