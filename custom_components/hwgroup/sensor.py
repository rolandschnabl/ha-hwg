"""Support for HW Group sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .const import CONF_DEVICE_NAME

_LOGGER = logging.getLogger(__name__)


@dataclass
class HWGroupSensorEntityDescription(SensorEntityDescription):
    """Describes HW Group sensor entity."""

    value_fn: Callable[[dict], any] | None = None


SENSOR_TYPES = {
    "temperature": HWGroupSensorEntityDescription(
        key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    "humidity": HWGroupSensorEntityDescription(
        key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    "voltage": HWGroupSensorEntityDescription(
        key="voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    "current": HWGroupSensorEntityDescription(
        key="current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    "generic": HWGroupSensorEntityDescription(
        key="generic",
        state_class=SensorStateClass.MEASUREMENT,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HW Group sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = []
    sensor_list = coordinator.data.get("sensors", [])
    _LOGGER.info("Setting up %d sensors for entry %s", len(sensor_list), entry.entry_id)
    
    for sensor_data in sensor_list:
        sensor_type = sensor_data.get("type", "generic")
        description = SENSOR_TYPES.get(sensor_type, SENSOR_TYPES["generic"])
        
        _LOGGER.debug("Creating sensor: %s (type: %s)", sensor_data.get("name"), sensor_type)
        sensors.append(
            HWGroupSensor(
                coordinator,
                entry,
                sensor_data,
                description,
            )
        )

    if sensors:
        _LOGGER.info("Adding %d sensor entities", len(sensors))
        async_add_entities(sensors)
    else:
        _LOGGER.warning("No sensors found in coordinator data")


class HWGroupSensor(CoordinatorEntity, SensorEntity):
    """Representation of a HW Group sensor."""

    entity_description: HWGroupSensorEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_data: dict,
        description: HWGroupSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._sensor_id = sensor_data["id"]
        self._attr_name = sensor_data["name"]
        self._attr_unique_id = f"{entry.entry_id}_{sensor_data['id']}"
        
        # Auto-detect icon from sensor name
        sensor_name_lower = sensor_data["name"].lower()
        sensor_type = sensor_data.get("type", "generic")
        
        if sensor_type == "temperature":
            if any(keyword in sensor_name_lower for keyword in ["server", "cpu", "processor"]):
                self._attr_icon = "mdi:cpu"
            elif any(keyword in sensor_name_lower for keyword in ["rack", "cabinet", "schrank"]):
                self._attr_icon = "mdi:server"
            elif any(keyword in sensor_name_lower for keyword in ["storage", "disk", "hdd", "ssd"]):
                self._attr_icon = "mdi:harddisk"
            elif any(keyword in sensor_name_lower for keyword in ["room", "raum", "zimmer"]):
                self._attr_icon = "mdi:home-thermometer"
            elif any(keyword in sensor_name_lower for keyword in ["outside", "outdoor", "aussen", "außen"]):
                self._attr_icon = "mdi:thermometer"
            elif any(keyword in sensor_name_lower for keyword in ["water", "wasser"]):
                self._attr_icon = "mdi:water-thermometer"
            else:
                self._attr_icon = "mdi:thermometer"
        
        elif sensor_type == "humidity":
            if any(keyword in sensor_name_lower for keyword in ["front", "vorne"]):
                self._attr_icon = "mdi:water-percent"
            elif any(keyword in sensor_name_lower for keyword in ["back", "rear", "hinten"]):
                self._attr_icon = "mdi:water-percent-alert"
            else:
                self._attr_icon = "mdi:water-percent"
        
        elif sensor_type == "voltage":
            if any(keyword in sensor_name_lower for keyword in ["battery", "batterie", "akku"]):
                self._attr_icon = "mdi:battery-charging"
            else:
                self._attr_icon = "mdi:lightning-bolt"
        
        elif sensor_type == "current":
            self._attr_icon = "mdi:current-ac"
        
        # SMS Gateway specific icons
        elif "signal" in sensor_name_lower:
            if "strength" in sensor_name_lower:
                self._attr_icon = "mdi:signal-cellular-3"
            elif "quality" in sensor_name_lower:
                self._attr_icon = "mdi:signal"
            else:
                self._attr_icon = "mdi:antenna"
        
        elif "network" in sensor_name_lower:
            if "operator" in sensor_name_lower:
                self._attr_icon = "mdi:cellphone"
            elif "status" in sensor_name_lower:
                self._attr_icon = "mdi:network"
            else:
                self._attr_icon = "mdi:network-outline"
        
        elif "sms" in sensor_name_lower:
            if "sent" in sensor_name_lower or "gesendet" in sensor_name_lower:
                self._attr_icon = "mdi:message-check"
            elif "error" in sensor_name_lower or "fehler" in sensor_name_lower:
                self._attr_icon = "mdi:message-alert"
            else:
                self._attr_icon = "mdi:message-text"
        
        else:
            # Use default icon from entity description if no specific match
            self._attr_icon = None
        
        if self._attr_icon:
            _LOGGER.debug(
                "Sensor '%s' (type: %s) assigned icon: %s",
                sensor_data["name"],
                sensor_type,
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
    def native_value(self) -> float | int | str | None:
        """Return the state of the sensor."""
        for sensor in self.coordinator.data.get("sensors", []):
            if sensor["id"] == self._sensor_id:
                return sensor.get("value")
        return None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        # First check if we have a custom unit from the device
        for sensor in self.coordinator.data.get("sensors", []):
            if sensor["id"] == self._sensor_id:
                device_unit = sensor.get("unit")
                if device_unit and self.entity_description.key == "generic":
                    return device_unit
        return self.entity_description.native_unit_of_measurement

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        for sensor in self.coordinator.data.get("sensors", []):
            if sensor["id"] == self._sensor_id:
                return {
                    "state": sensor.get("state", "ok"),
                    "sensor_id": self._sensor_id,
                }
        return {}
