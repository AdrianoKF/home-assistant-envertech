"""Tests for the PV Microinverter sensor platform."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfPower

from pv_microinverter.const import PVMicroinverterData
from pv_microinverter.coordinator import (
    PVMicroinverterDataUpdateCoordinator,
)
from pv_microinverter.sensor import PVMicroinverterSensor


@pytest.mark.asyncio
async def test_sensor_initialization():
    """Test sensor initialization."""
    # Mock data and coordinator
    mock_data = PVMicroinverterData(
        current_power=500.0,
        today_energy=2.5,
        lifetime_energy=150.0,
        last_updated=datetime.now().isoformat(),
    )

    mock_coordinator = MagicMock(spec=PVMicroinverterDataUpdateCoordinator)
    mock_coordinator.data = mock_data
    mock_coordinator.last_update_success = True

    # Test current power sensor
    current_power_sensor = PVMicroinverterSensor(
        coordinator=mock_coordinator,
        system_id="test_system",
        sensor_type="current_power",
        sensor_info={
            "name": "Current Power",
            "icon": "mdi:solar-power",
            "unit": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    )

    # Verify sensor properties
    assert current_power_sensor.name == "Current Power"
    assert current_power_sensor.native_unit_of_measurement == UnitOfPower.WATT
    assert current_power_sensor.device_class == SensorDeviceClass.POWER
    assert current_power_sensor.state_class == SensorStateClass.MEASUREMENT
    assert current_power_sensor.native_value == 500.0

    # Test today's energy sensor
    today_energy_sensor = PVMicroinverterSensor(
        coordinator=mock_coordinator,
        system_id="test_system",
        sensor_type="today_energy",
        sensor_info={
            "name": "Today's Energy",
            "icon": "mdi:solar-power",
            "unit": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    )

    # Verify sensor properties
    assert today_energy_sensor.name == "Today's Energy"
    assert today_energy_sensor.native_unit_of_measurement == UnitOfEnergy.KILO_WATT_HOUR
    assert today_energy_sensor.device_class == SensorDeviceClass.ENERGY
    assert today_energy_sensor.state_class == SensorStateClass.TOTAL_INCREASING
    assert today_energy_sensor.native_value == 2.5
