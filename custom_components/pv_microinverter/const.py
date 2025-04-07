"""Constants for the PV Microinverter integration."""

from dataclasses import dataclass
from typing import Final

DOMAIN: Final = "pv_microinverter"
MANUFACTURER: Final = "Envertech"

# Config flow
CONF_STATION_ID: Final = "station_id"
CONF_UPDATE_INTERVAL: Final = "update_interval"

# Default values
DEFAULT_UPDATE_INTERVAL: Final = 60  # 1 minute

# Entity attributes
ATTR_LAST_UPDATED: Final = "last_updated"

# Sensors
SENSOR_TYPES: Final = {
    "current_power": {
        "name": "Current Power",
        "icon": "mdi:solar-power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "today_energy": {
        "name": "Today's Energy",
        "icon": "mdi:solar-power",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "lifetime_energy": {
        "name": "Lifetime Energy",
        "icon": "mdi:solar-power",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
}


@dataclass
class PVMicroinverterData:
    """Class to hold PV microinverter data."""

    current_power: float
    today_energy: float
    lifetime_energy: float
    last_updated: str
