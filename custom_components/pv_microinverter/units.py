from typing import Self

# SI prefix multipliers
SI_PREFIXES = {
    "Y": 1e24,
    "Z": 1e21,
    "E": 1e18,
    "P": 1e15,
    "T": 1e12,
    "G": 1e9,
    "M": 1e6,
    "k": 1e3,
    "h": 1e2,
    "da": 1e1,
    "d": 1e-1,
    "c": 1e-2,
    "m": 1e-3,
    "µ": 1e-6,
    "u": 1e-6,
    "n": 1e-9,
    "p": 1e-12,
    "f": 1e-15,
    "a": 1e-18,
    "z": 1e-21,
    "y": 1e-24,
}


def _get_unit_symbol(unit_val: str) -> str:
    """Extract the unit symbol from a unit value string."""
    # Assuming the unit value is in the format "value unit"
    return unit_val.strip().split(" ")[-1]


class SIUnit:
    """SI Units with automatic unit conversion."""

    def __init__(self, name: str, quantity: str, symbol: str, factor: float):
        self.name = name
        self.quantity = quantity
        self.symbol = symbol
        self.factor = factor

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    def __repr__(self):
        return f"SIUnit(name={self.name}, symbol={self.symbol}, factor={self.factor})"

    @classmethod
    def parse(cls, unit_str: str) -> Self:
        """
        Return an SIUnit by parsing the given unit string, supporting SI prefixes.
        """
        # If the unit is registered directly, return it.
        if unit_str in BASE_UNITS:
            return BASE_UNITS[unit_str]
        # Otherwise, check for a valid prefix.
        for prefix in sorted(SI_PREFIXES, key=len, reverse=True):
            if unit_str.startswith(prefix):
                base_symbol = unit_str[len(prefix) :]
                if base_symbol in BASE_UNITS:
                    base_unit = BASE_UNITS[base_symbol]
                    multiplier = SI_PREFIXES[prefix]
                    return SIUnit(
                        f"{prefix}{base_unit.name}",
                        base_unit.quantity,
                        f"{prefix}{base_unit.symbol}",
                        base_unit.factor * multiplier,
                    )
        raise ValueError(f"Unknown unit: {unit_str}")


class Dimension:
    """Class to represent a dimension with a unit."""

    def __init__(self, value: float, unit: SIUnit):
        self.value = value
        self.unit = unit

    def __str__(self):
        return f"{self.value} {self.unit.symbol}"

    def to_base_unit(self) -> float:
        """Convert the dimension value to its base unit."""
        return float(self.value) * self.unit.factor

    def __repr__(self):
        return f"Dimension(value={self.value}, unit={self.unit})"

    @classmethod
    def parse(cls, unit_val: str) -> Self:
        """
        Parse a unit value string into a Dimension object, supporting SI unit prefixes.
        Expects the format "value unit", e.g. "3.5 kW" or "10 Wh".
        """
        parts = unit_val.strip().split()
        if len(parts) != 2:
            raise ValueError(f"Invalid unit value format: {unit_val}")
        value, unit_str = parts
        unit = SIUnit.parse(unit_str)
        return cls(float(value), unit)


# Define SI units
WATT = SIUnit("Watt", "Power", "W", 1)
WATT_HOUR = SIUnit("Watt-hour", "Energy", "Wh", 1)


# Mapping of base unit symbols to registered SIUnit objects
BASE_UNITS = {
    "W": WATT,
    "Wh": WATT_HOUR,
}
