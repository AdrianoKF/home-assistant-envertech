"""Data update coordinator for PV Microinverter integration."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import PVMicroinverterApiClient, PVMicroinverterApiClientError
from .const import DOMAIN, PVMicroinverterData

_LOGGER = logging.getLogger(__name__)


class PVMicroinverterDataUpdateCoordinator(DataUpdateCoordinator[PVMicroinverterData]):
    """Class to manage fetching PV Microinverter data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: PVMicroinverterApiClient,
        update_interval: int,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: The Home Assistant instance
            api_client: The API client
            update_interval: The update interval in seconds
        """
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )
        self.api_client = api_client

    async def _async_update_data(self) -> PVMicroinverterData:
        """Fetch data from the API.

        Returns:
            PVMicroinverterData: The fetched data

        Raises:
            UpdateFailed: If the update fails
        """
        try:
            return await self.api_client.async_get_data()
        except PVMicroinverterApiClientError as error:
            raise UpdateFailed(f"Error communicating with API: {error}") from error
