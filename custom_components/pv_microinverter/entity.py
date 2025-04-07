"""Base entity for PV Microinverter integration."""

from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import PVMicroinverterDataUpdateCoordinator


class PVMicroinverterEntity(CoordinatorEntity[PVMicroinverterDataUpdateCoordinator]):
    """Base entity for PV Microinverter integration."""

    def __init__(
        self,
        coordinator: PVMicroinverterDataUpdateCoordinator,
        station_id: str,
        sensor_type: str,
    ) -> None:
        """Initialize the entity.

        Args:
            coordinator: The data update coordinator
            system_id: The system identifier
            sensor_type: The sensor type
        """
        super().__init__(coordinator)
        self._station_id = station_id
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{station_id}_{sensor_type}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, station_id)},
            name=f"PV Microinverter {station_id}",
            manufacturer=MANUFACTURER,
            model="Microinverter",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and super().available
