"""Support for HW Group switches (relays)."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .hwgroup import HWGroupAPI
from .const import CONF_DEVICE_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HW Group switches from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    switches = []
    switch_list = coordinator.data.get("switches", [])
    _LOGGER.info("Setting up %d switches for entry %s", len(switch_list), entry.entry_id)
    
    for switch_data in switch_list:
        _LOGGER.debug("Creating switch: %s", switch_data.get("name"))
        switches.append(
            HWGroupSwitch(
                coordinator,
                api,
                entry,
                switch_data,
            )
        )

    if switches:
        _LOGGER.info("Adding %d switch entities", len(switches))
        async_add_entities(switches)
    else:
        _LOGGER.warning("No switches found in coordinator data")


class HWGroupSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a HW Group switch (relay)."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api: HWGroupAPI,
        entry: ConfigEntry,
        switch_data: dict,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._api = api
        self._switch_id = switch_data["id"]
        self._attr_name = switch_data["name"]
        self._attr_unique_id = f"{entry.entry_id}_switch_{switch_data['id']}"
        
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
        """Return true if the switch is on."""
        for switch in self.coordinator.data.get("switches", []):
            if switch["id"] == self._switch_id:
                return switch.get("state", False)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if await self._api.async_set_output(self._switch_id, True):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if await self._api.async_set_output(self._switch_id, False):
            await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        return {
            "output_id": self._switch_id,
        }
