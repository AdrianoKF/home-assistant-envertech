"""API client for PV Microinverter."""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

import aiohttp

from .const import PVMicroinverterData
from .units import WATT, Dimension

_LOGGER = logging.getLogger(__name__)


class ApiEndpoints(StrEnum):
    GET_STATION_INFO = "GetStationInfo"


@dataclass
class StationInfoData:
    UnitCapacity: str
    UnitEToday: str
    UnitEMonth: str
    UnitEYear: str
    UnitETotal: str
    Power: float
    PowerStr: str
    Capacity: float
    LoadPower: str
    GridPower: str
    StrCO2: str
    StrTrees: str
    StrIncome: str
    PwImg: str
    StationName: str
    InvModel1: str
    InvModel2: str | None
    Lat: str
    Lng: str
    TimeZone: str
    StrPeakPower: str
    Installer: str | None
    CreateTime: datetime
    CreateYear: int
    CreateMonth: int
    Etoday: float
    InvTotal: int


@dataclass
class StationInfoResponse:
    Status: int
    Result: Any
    Data: StationInfoData


class PVMicroinverterApiClientError(Exception):
    """Exception to indicate an error with the API client."""


class PVMicroinverterApiClient:
    """API client for PV Microinverter."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        station_id: str,
        base_url: str = "https://www.envertecportal.com/ApiStations",
    ) -> None:
        """Initialize the Envertech API client.

        Args:
            session: The aiohttp client session
            station_id: The station identifier
            base_url: The base URL for the API
        """
        self._session = session
        self._station_id = station_id
        self._base_url = base_url

    async def async_get_data(self) -> PVMicroinverterData:
        """Get data from the API.

        Returns:
            PVMicroinverterData: The data from the API

        Raises:
            PVMicroinverterApiClientError: If the API request fails
        """
        try:
            # Make the request to the API
            response = await self._session.post(
                f"{self._base_url}/{ApiEndpoints.GET_STATION_INFO}",
                json={"stationId": self._station_id},
                headers={
                    "Content-Type": "application/json",
                },
            )

            response.raise_for_status()
            data = await response.json()

            # Process the response
            return self._process_data(data)

        except aiohttp.ClientError as error:
            _LOGGER.error("Error fetching data: %s", error)
            raise PVMicroinverterApiClientError(
                "Error fetching data from API"
            ) from error
        except Exception as error:
            _LOGGER.exception("Unexpected error: %s", error)
            raise PVMicroinverterApiClientError("Unexpected error occurred") from error

    def _process_data(self, data: dict[str, Any]) -> PVMicroinverterData:
        """Process the API response data.

        Args:
            data: The data from the API

        Returns:
            PVMicroinverterData: The processed data
        """

        station_data = StationInfoData(**data.get("Data", {}))
        station_info = StationInfoResponse(
            Status=data.get("Status"),
            Result=data.get("Result"),
            Data=station_data,
        )

        if station_info.Status != "0":
            raise PVMicroinverterApiClientError(f"API error: {station_info.Result}")

        return PVMicroinverterData(
            current_power=Dimension(station_data.Power, WATT).value,
            today_energy=Dimension.parse(station_data.UnitEToday).value,
            lifetime_energy=Dimension.parse(station_data.UnitETotal).value,
            last_updated=datetime.now().isoformat(),
        )

    async def async_check_connection(self) -> bool:
        """Test the API connection to verify credentials.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            response = await self._session.post(
                f"{self._base_url}/{ApiEndpoints.GET_STATION_INFO}",
                headers={
                    "Content-Type": "application/json",
                },
                json={"stationId": self._station_id},
            )
            response.raise_for_status()
            return True
        except Exception as error:
            _LOGGER.error("Connection test failed: %s", error)
            return False
