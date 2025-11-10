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


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
