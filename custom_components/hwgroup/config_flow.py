"""Config flow for HW Group integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_DEVICE_TYPE,
    DEVICE_TYPES,
    DEVICE_TYPE_POSEIDON_3268,
    DOMAIN,
    CONF_DEVICE_NAME,
    CONF_INVERT_BINARY_SENSORS,
)
from .hwgroup import HWGroupAPI, HWGroupAuthError, HWGroupConnectionError

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    api = HWGroupAPI(
        data[CONF_HOST],
        session,
        data.get(CONF_USERNAME),
        data.get(CONF_PASSWORD),
    )

    if not await api.async_test_connection():
        raise CannotConnect

    device_data = await api.async_get_data()
    device_info = device_data.get("device_info", {})

    return {
        "title": device_info.get("name", data[CONF_HOST]),
        "model": device_info.get("model", "Unknown"),
        "serial": device_info.get("serial", "Unknown"),
        "device_type": device_info.get("device_type", DEVICE_TYPE_POSEIDON_3268),
    }


class HWGroupConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HW Group."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow for this handler."""
        return HWGroupOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except HWGroupAuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Determine configured name (user can override device name)
                configured_name = user_input.get(CONF_DEVICE_NAME) or info["title"]
                
                # Use host + serial as unique_id to allow multiple devices
                # If serial is "Unknown", use only host
                if info["serial"] != "Unknown":
                    unique_id = f"{user_input[CONF_HOST]}_{info['serial']}"
                else:
                    unique_id = user_input[CONF_HOST]
                
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                entry_data = dict(user_input)
                entry_data[CONF_DEVICE_NAME] = configured_name
                # Use auto-detected device type
                entry_data[CONF_DEVICE_TYPE] = info["device_type"]
                
                _LOGGER.info(
                    "Auto-detected device type: %s (Model: %s)",
                    info["device_type"],
                    info["model"]
                )

                return self.async_create_entry(title=configured_name, data=entry_data)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_USERNAME): str,
                vol.Optional(CONF_PASSWORD): str,
                vol.Optional(CONF_DEVICE_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors,
            description_placeholders={
                "note": "Device type will be automatically detected"
            }
        )


class HWGroupOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for HW Group integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        return await self.async_step_basic()

    async def async_step_basic(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle basic settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate connection with new settings
            try:
                session = async_get_clientsession(self.hass)
                api = HWGroupAPI(
                    user_input[CONF_HOST],
                    session,
                    user_input.get(CONF_USERNAME),
                    user_input.get(CONF_PASSWORD),
                )
                if not await api.async_test_connection():
                    raise CannotConnect
                
                # Get device info for auto-detection
                device_data = await api.async_get_data()
                device_info = device_data.get("device_info", {})
                detected_type = device_info.get("device_type", DEVICE_TYPE_POSEIDON_3268)
                
                # Add detected device type to user input
                user_input[CONF_DEVICE_TYPE] = detected_type
                
                _LOGGER.info(
                    "Auto-detected device type: %s (Model: %s)",
                    detected_type,
                    device_info.get("model", "Unknown")
                )
                
                # Store in temporary data and move to binary sensor config
                self.basic_config = user_input
                return await self.async_step_binary_sensors()
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except HWGroupAuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Get current values from config entry
        current_host = self.config_entry.data.get(CONF_HOST, "")
        current_username = self.config_entry.data.get(CONF_USERNAME, "")
        current_password = self.config_entry.data.get(CONF_PASSWORD, "")
        current_device_name = self.config_entry.data.get(CONF_DEVICE_NAME, "")
        current_device_type = self.config_entry.data.get(CONF_DEVICE_TYPE, "")

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current_host): str,
                vol.Optional(CONF_USERNAME, default=current_username): str,
                vol.Optional(CONF_PASSWORD, default=current_password): str,
                vol.Optional(CONF_DEVICE_NAME, default=current_device_name): str,
            }
        )

        # Show current device type in description
        device_type_display = current_device_type.replace("_", " ").title() if current_device_type else "Unknown"

        return self.async_show_form(
            step_id="basic",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "device_name": self.config_entry.title,
                "current_type": device_type_display,
            },
        )

    async def async_step_binary_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure binary sensor inversion."""
        if user_input is not None:
            # Merge basic config with binary sensor config
            final_config = {**self.basic_config, **user_input}
            
            # Update config entry with new data
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=final_config,
                title=final_config.get(CONF_DEVICE_NAME, self.config_entry.title),
            )
            
            _LOGGER.info("Binary sensor inversion updated, reloading integration...")
            
            # Reload the integration to apply changes without restart
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            
            _LOGGER.info("Integration reloaded successfully")
            
            return self.async_create_entry(title="", data={})

        # Get coordinator to fetch current binary sensors
        coordinator = self.hass.data[DOMAIN][self.config_entry.entry_id]["coordinator"]
        binary_sensors = coordinator.data.get("binary_sensors", [])
        
        if not binary_sensors:
            # No binary sensors available, skip this step
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=self.basic_config,
                title=self.basic_config.get(CONF_DEVICE_NAME, self.config_entry.title),
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})
        
        # Get currently inverted sensors
        current_inverted = self.config_entry.data.get(CONF_INVERT_BINARY_SENSORS, [])
        
        # Build schema with multi-select for binary sensors
        binary_sensor_options = {
            sensor["id"]: sensor["name"] for sensor in binary_sensors
        }
        
        # Import selector for multi-select
        from homeassistant.helpers import selector
        
        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_INVERT_BINARY_SENSORS,
                    default=current_inverted,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=sid, label=name)
                            for sid, name in binary_sensor_options.items()
                        ],
                        multiple=True,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="binary_sensors",
            data_schema=data_schema,
            errors={},
            description_placeholders={
                "sensors": "\n".join([f"- {name} ({sid})" for sid, name in binary_sensor_options.items()]),
            },
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
