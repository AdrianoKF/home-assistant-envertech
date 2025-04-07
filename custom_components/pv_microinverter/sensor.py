"""Sensor platform for PV Microinverter integration."""

from __future__ import annotations

import logging
from typing import Any, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_LAST_UPDATED, DOMAIN, SENSOR_TYPES
from .coordinator import PVMicroinverterDataUpdateCoordinator
from .entity import PVMicroinverterEntity

_LOGGER = logging.getLogger(__name__)

# Map to convert API units to HA units
UNIT_MAP: Final = {
    "W": UnitOfPower.WATT,
    "kWh": UnitOfEnergy.KILO_WATT_HOUR,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PV Microinverter sensors based on a config entry."""
    coordinator: PVMicroinverterDataUpdateCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]
    system_id = entry.data["system_id"]

    entities = []

    # Create a sensor entity for each sensor type
    for sensor_key, sensor_info in SENSOR_TYPES.items():
        entities.append(
            PVMicroinverterSensor(
                coordinator=coordinator,
                system_id=system_id,
                sensor_type=sensor_key,
                sensor_info=sensor_info,
            )
        )

    async_add_entities(entities, True)


class PVMicroinverterSensor(PVMicroinverterEntity, SensorEntity):
    """Representation of a PV Microinverter sensor."""

    def __init__(
        self,
        coordinator: PVMicroinverterDataUpdateCoordinator,
        system_id: dict[str, Any],
        sensor_type: str,
        sensor_info: dict[str, Any],
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: The data update coordinator
            system_id: The system identifier
            sensor_type: The sensor type
            sensor_info: The sensor information
        """
        super().__init__(coordinator, system_id["station_id"], sensor_type)

        self._attr_name = sensor_info["name"]
        self._attr_icon = sensor_info["icon"]

        # Convert API units to HA units
        unit = sensor_info["unit"]
        self._attr_native_unit_of_measurement = UNIT_MAP.get(unit, unit)

        # Set device class if available
        device_class = sensor_info.get("device_class")
        if device_class:
            if device_class == "power":
                self._attr_device_class = SensorDeviceClass.POWER
            elif device_class == "energy":
                self._attr_device_class = SensorDeviceClass.ENERGY

        # Set state class if available
        state_class = sensor_info.get("state_class")
        if state_class:
            if state_class == "measurement":
                self._attr_state_class = SensorStateClass.MEASUREMENT
            elif state_class == "total_increasing":
                self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data:
            return None

        if self._sensor_type == "current_power":
            return data.current_power
        elif self._sensor_type == "today_energy":
            return data.today_energy
        elif self._sensor_type == "lifetime_energy":
            return data.lifetime_energy
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""
        return {
            ATTR_LAST_UPDATED: self.coordinator.data.last_updated
            if self.coordinator.data
            else None,
        }
