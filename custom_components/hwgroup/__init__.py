"""The HW Group integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .hwgroup import HWGroupAPI, HWGroupError

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HW Group from a config entry."""
    host = entry.data[CONF_HOST]
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)

    session = async_get_clientsession(hass)
    api = HWGroupAPI(host, session, username, password)

    async def async_update_data():
        """Fetch data from API."""
        try:
            return await api.async_get_data()
        except HWGroupError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{host}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Register services for SMS Gateway
    async def handle_send_sms(call):
        """Handle the send_sms service call."""
        device_id = call.data.get("device_id")
        phone_number = call.data.get("phone_number")
        message = call.data.get("message")
        
        # Find the API instance for the specified device
        api_instance = None
        if device_id:
            # Use specific device
            for entry_id, data in hass.data[DOMAIN].items():
                if entry_id == device_id:
                    api_instance = data["api"]
                    break
        else:
            # Use first SMS Gateway found
            for data in hass.data[DOMAIN].values():
                if isinstance(data, dict) and "api" in data:
                    coordinator_data = data["coordinator"].data
                    if coordinator_data.get("device_info", {}).get("device_type") == "sms_gateway":
                        api_instance = data["api"]
                        break
        
        if api_instance:
            success = await api_instance.async_send_sms(phone_number, message)
            if not success:
                _LOGGER.error("Failed to send SMS to %s", phone_number)
        else:
            _LOGGER.error("No SMS Gateway device found")

    async def handle_call_number(call):
        """Handle the call_number service call."""
        device_id = call.data.get("device_id")
        phone_number = call.data.get("phone_number")
        
        # Find the API instance for the specified device
        api_instance = None
        if device_id:
            # Use specific device
            for entry_id, data in hass.data[DOMAIN].items():
                if entry_id == device_id:
                    api_instance = data["api"]
                    break
        else:
            # Use first SMS Gateway found
            for data in hass.data[DOMAIN].values():
                if isinstance(data, dict) and "api" in data:
                    coordinator_data = data["coordinator"].data
                    if coordinator_data.get("device_info", {}).get("device_type") == "sms_gateway":
                        api_instance = data["api"]
                        break
        
        if api_instance:
            success = await api_instance.async_call_number(phone_number)
            if not success:
                _LOGGER.error("Failed to call %s", phone_number)
        else:
            _LOGGER.error("No SMS Gateway device found")

    # Register services
    hass.services.async_register(DOMAIN, "send_sms", handle_send_sms)
    hass.services.async_register(DOMAIN, "call_number", handle_call_number)

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when it changes."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
