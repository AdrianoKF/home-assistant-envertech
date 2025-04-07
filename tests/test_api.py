"""Tests for the PV Microinverter API client."""

import json
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from aiohttp import ClientResponseError, ClientSession
from custom_components.pv_microinverter.api import (
    PVMicroinverterApiClient,
    PVMicroinverterApiClientError,
)


@pytest.fixture
def mock_session():
    """Return a mocked aiohttp client session."""
    session = MagicMock(spec=ClientSession)
    session.get = AsyncMock()
    return session


@pytest.fixture
def api_client(mock_session):
    """Return a new API client with a mocked session."""
    return PVMicroinverterApiClient(
        session=mock_session,
        station_id="test_station_id",
        base_url="https://api.example.com/v1",
    )


@pytest.fixture
def mock_response():
    """Return a mocked API response."""
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json = AsyncMock(
        return_value={
            "current_power": 500.5,
            "today_energy": 3.75,
            "lifetime_energy": 1250.25,
            "last_updated": "2023-04-01T12:00:00Z",
        }
    )
    return mock


@pytest.mark.asyncio
async def test_async_get_data_success(api_client, mock_session, mock_response):
    """Test successful data retrieval."""
    # Setup the mock response
    mock_session.get.return_value = mock_response

    # Call the method
    data = await api_client.async_get_data()

    # Verify the API call
    mock_session.get.assert_called_once_with(
        "https://api.example.com/v1/systems/test_system_id/stats",
        headers={
            "Authorization": "Bearer test_api_key",
            "Content-Type": "application/json",
        },
    )

    # Verify the response processing
    assert data.current_power == 500.5
    assert data.today_energy == 3.75
    assert data.lifetime_energy == 1250.25
    assert data.last_updated == "2023-04-01T12:00:00Z"


@pytest.mark.asyncio
async def test_async_get_data_http_error(api_client, mock_session):
    """Test handling of HTTP errors."""
    # Setup the mock to raise an error
    error_response = MagicMock()
    error_response.raise_for_status.side_effect = ClientResponseError(
        request_info=MagicMock(),
        history=None,
        status=401,
        message="Unauthorized",
        headers=None,
    )
    mock_session.get.return_value = error_response

    # Call the method and expect an exception
    with pytest.raises(PVMicroinverterApiClientError) as excinfo:
        await api_client.async_get_data()

    # Verify the error message
    assert "Error fetching data from API" in str(excinfo.value)


@pytest.mark.asyncio
async def test_async_get_data_connection_error(api_client, mock_session):
    """Test handling of connection errors."""
    # Setup the mock to raise a connection error
    mock_session.get.side_effect = aiohttp.ClientConnectionError("Connection refused")

    # Call the method and expect an exception
    with pytest.raises(PVMicroinverterApiClientError) as excinfo:
        await api_client.async_get_data()

    # Verify the error message
    assert "Error fetching data from API" in str(excinfo.value)


@pytest.mark.asyncio
async def test_async_get_data_invalid_json(api_client, mock_session, mock_response):
    """Test handling of invalid JSON responses."""
    # Setup the mock to return invalid JSON
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_session.get.return_value = mock_response

    # Call the method and expect an exception
    with pytest.raises(PVMicroinverterApiClientError) as excinfo:
        await api_client.async_get_data()

    # Verify the error message
    assert "Unexpected error occurred" in str(excinfo.value)


@pytest.mark.asyncio
async def test_async_get_data_missing_fields(api_client, mock_session, mock_response):
    """Test handling of responses with missing fields."""
    # Setup the mock to return a response with missing fields
    mock_response.json.return_value = {"some_other_field": "value"}
    mock_session.get.return_value = mock_response

    # Call the method - it should handle missing fields gracefully
    data = await api_client.async_get_data()

    # Verify default values are used
    assert data.current_power == 0
    assert data.today_energy == 0
    assert data.lifetime_energy == 0
    assert data.last_updated is not None  # Should default to current time


@pytest.mark.asyncio
async def test_async_check_connection_success(api_client, mock_session):
    """Test successful connection check."""
    # Setup the mock response
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_session.get.return_value = mock_response

    # Call the method
    result = await api_client.async_check_connection()

    # Verify the API call
    mock_session.post.assert_called_once_with(
        f"{api_client._base_url}/GetStationInfo",
        headers={
            "Authorization": "Bearer test_api_key",
            "Content-Type": "application/json",
        },
    )

    # Verify the result
    assert result is True


@pytest.mark.asyncio
async def test_async_check_connection_failure(api_client, mock_session):
    """Test failed connection check."""
    # Setup the mock to raise an error
    mock_session.get.side_effect = aiohttp.ClientError("Connection error")

    # Call the method
    result = await api_client.async_check_connection()

    # Verify the result
    assert result is False


@pytest.mark.asyncio
async def test_process_data_with_various_types(api_client):
    """Test data processing with various data types."""
    # Test with string values that should be converted to float
    data_with_strings = {
        "current_power": "450.75",
        "today_energy": "2.5",
        "lifetime_energy": "1000",
        "last_updated": "2023-04-01T14:30:00Z",
    }
    result = api_client._process_data(data_with_strings)
    assert result.current_power == 450.75
    assert result.today_energy == 2.5
    assert result.lifetime_energy == 1000.0
    assert result.last_updated == "2023-04-01T14:30:00Z"

    # Test with mixed types
    data_mixed = {
        "current_power": 300,
        "today_energy": 1.5,
        "lifetime_energy": "750.5",
        "last_updated": "2023-04-01T14:30:00Z",
    }
    result = api_client._process_data(data_mixed)
    assert result.current_power == 300.0
    assert result.today_energy == 1.5
    assert result.lifetime_energy == 750.5
    assert result.last_updated == "2023-04-01T14:30:00Z"
