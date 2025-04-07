"""Config flow for PV Microinverter integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PVMicroinverterApiClient
from .const import (
    CONF_STATION_ID,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_STATION_ID): str,
    vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect to the API.

    Args:
        hass: The Home Assistant instance
        data: The user input

    Returns:
        Dict[str, Any]: The validated data

    Raises:
        CannotConnect: If the API connection cannot be established
        InvalidAuth: If the API key is invalid
    """
    session = async_get_clientsession(hass)

    api_client = PVMicroinverterApiClient(
        session=session,
        station_id=data[CONF_STATION_ID],
    )

    # Test connection and authentication
    connection_successful = await api_client.async_check_connection()

    if not connection_successful:
        raise CannotConnect

    # Return validated data
    return {
        CONF_STATION_ID: data[CONF_STATION_ID],
        CONF_UPDATE_INTERVAL: data[CONF_UPDATE_INTERVAL],
    }


class PVMicroinverterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PV Microinverter."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                # Check if we already have an entry for this system_id
                await self.async_set_unique_id(user_input[CONF_STATION_ID])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"PV Microinverter {user_input[CONF_STATION_ID]}",
                    data=info,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(self, user_input: dict[str, Any] = None) -> FlowResult:
        """Handle re-authentication."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                # Get existing entry
                existing_entry = await self.async_set_unique_id(
                    user_input[CONF_STATION_ID]
                )

                if existing_entry:
                    self.hass.config_entries.async_update_entry(
                        existing_entry, data=info
                    )
                    await self.hass.config_entries.async_reload(existing_entry.entry_id)
                    return self.async_abort(reason="reauth_successful")

                return self.async_abort(reason="reauth_failed_existing_entry_not_found")
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reauth", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
