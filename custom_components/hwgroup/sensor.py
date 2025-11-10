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
    for sensor_data in coordinator.data.get("sensors", []):
        sensor_type = sensor_data.get("type", "generic")
        description = SENSOR_TYPES.get(sensor_type, SENSOR_TYPES["generic"])
        
        sensors.append(
            HWGroupSensor(
                coordinator,
                entry,
                sensor_data,
                description,
            )
        )

    async_add_entities(sensors)


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
