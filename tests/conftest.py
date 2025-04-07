"""Pytest fixtures for PV Microinverter tests."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from pv_microinverter.api import PVMicroinverterApiClient
from pv_microinverter.const import (
    CONF_STATION_ID,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    PVMicroinverterData,
)
from pv_microinverter.coordinator import (
    PVMicroinverterDataUpdateCoordinator,
)


@pytest.fixture
def mock_api_client():
    """Return a mocked PV Microinverter API client."""
    client = MagicMock(spec=PVMicroinverterApiClient)
    client.async_get_data = AsyncMock(
        return_value=PVMicroinverterData(
            current_power=500.0,
            today_energy=2.5,
            lifetime_energy=150.0,
            last_updated=datetime.now().isoformat(),
        )
    )
    client.async_check_connection = AsyncMock(return_value=True)
    return client


@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    return MagicMock(
        data={
            CONF_STATION_ID: "test_station_id",
            CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL,
        },
        entry_id="test_entry_id",
    )


@pytest.fixture
def mock_coordinator(mock_api_client):
    """Return a mock coordinator."""
    coordinator = MagicMock(spec=PVMicroinverterDataUpdateCoordinator)
    coordinator.api_client = mock_api_client
    coordinator.data = mock_api_client.async_get_data.return_value
    coordinator.last_update_success = True
    coordinator.async_config_entry_first_refresh = AsyncMock()
    return coordinator
