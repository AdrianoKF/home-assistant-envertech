import pytest

from pv_microinverter.units import Dimension, SIUnit


def test_siunit_parse_base_unit():
    unit = SIUnit.parse("W")
    # Check that parsing base unit returns the registered unit
    assert unit.name == "Watt"
    assert unit.symbol == "W"
    assert unit.factor == 1


def test_siunit_parse_prefixed_unit():
    unit = SIUnit.parse("kW")
    # The expected unit is created by prefix "k" and the base unit "Watt"
    assert unit.name == "kWatt"
    assert unit.symbol == "kW"
    assert unit.factor == 1000  # 1e3 multiplier


def test_dimension_parse_valid():
    # Parsing a valid dimension string should succeed
    dim = Dimension.parse("3.5 kW")
    assert dim.value == "3.5"
    # Check unit attributes from SIUnit.parse
    assert dim.unit.name == "kWatt"
    assert dim.unit.symbol == "kW"
    # Check conversion to base unit: 3.5 * 1000 = 3500.0
    assert dim.to_base_unit() == 3500.0


def test_dimension_parse_invalid_format():
    # Missing space between value and unit should raise a ValueError
    with pytest.raises(ValueError):
        Dimension.parse("3.5kW")


def test_siunit_parse_unknown_unit():
    # Attempting to parse an unknown unit should raise a ValueError
    with pytest.raises(ValueError):
        SIUnit.parse("invalid")
