"""The PV Microinverter integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PVMicroinverterApiClient
from .api import PVMicroinverterApiClientError as PVMicroinverterApiClientError
from .const import (
    CONF_STATION_ID,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .coordinator import PVMicroinverterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# List of platforms to support
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PV Microinverter from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Get configuration from the config entry
    station_id = entry.data[CONF_STATION_ID]
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

    # Create API client
    session = async_get_clientsession(hass)
    api_client = PVMicroinverterApiClient(
        session=session,
        station_id=station_id,
    )

    # Initialize coordinator
    coordinator = PVMicroinverterDataUpdateCoordinator(
        hass=hass,
        api_client=api_client,
        update_interval=update_interval,
    )

    # Fetch initial data
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady as error:
        raise ConfigEntryNotReady(f"Failed to load initial data: {error}") from error

    # Store coordinator in hass.data
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up all platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Add update listener for config entry changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)
