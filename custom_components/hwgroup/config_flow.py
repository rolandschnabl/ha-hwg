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

                return self.async_create_entry(title=configured_name, data=entry_data)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_USERNAME): str,
                vol.Optional(CONF_PASSWORD): str,
                vol.Optional(CONF_DEVICE_NAME): str,
                vol.Optional(
                    CONF_DEVICE_TYPE, default=DEVICE_TYPE_POSEIDON_3268
                ): vol.In(DEVICE_TYPES),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
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
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except HWGroupAuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Update config entry with new data
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=user_input,
                    title=user_input.get(CONF_DEVICE_NAME, self.config_entry.title),
                )
                # Reload the integration to apply changes without restart
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                return self.async_create_entry(title="", data={})

        # Get current values from config entry
        current_host = self.config_entry.data.get(CONF_HOST, "")
        current_username = self.config_entry.data.get(CONF_USERNAME, "")
        current_password = self.config_entry.data.get(CONF_PASSWORD, "")
        current_device_name = self.config_entry.data.get(CONF_DEVICE_NAME, "")
        current_device_type = self.config_entry.data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_POSEIDON_3268)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current_host): str,
                vol.Optional(CONF_USERNAME, default=current_username): str,
                vol.Optional(CONF_PASSWORD, default=current_password): str,
                vol.Optional(CONF_DEVICE_NAME, default=current_device_name): str,
                vol.Optional(CONF_DEVICE_TYPE, default=current_device_type): vol.In(DEVICE_TYPES),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "device_name": self.config_entry.title,
            },
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
