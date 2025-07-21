"""Unit tests for sensor component logic without Home Assistant dependencies."""
import json
import sys
from pathlib import Path

# Add the parent directory to sys.path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from custom_components.zendure_local.sensor import SENSOR_TYPES


def load_fixture(filename):
    """Load fixture data."""
    path = Path(__file__).parent / "fixtures" / filename
    with path.open(encoding="utf-8") as file:
        return json.loads(file.read())


def test_sensor_types_structure():
    """Test that all sensor types have the required structure."""
    required_keys = {"value_func"}
    optional_keys = {
        "icon", "unit", "device_class", "state_class", "entity_category",
        "native_unit_of_measurement", "entity_registry_enabled_default"
    }

    for sensor_key, sensor_config in SENSOR_TYPES.items():
        # Check sensor key is a string
        assert isinstance(sensor_key, str)
        assert sensor_key  # Not empty

        # Check required keys exist
        for key in required_keys:
            assert key in sensor_config, f"Sensor {sensor_key} missing required key: {key}"

        # Check all keys are valid
        for key in sensor_config:
            assert key in required_keys | optional_keys, f"Sensor {sensor_key} has invalid key: {key}"

        # Check value_func is callable
        assert callable(sensor_config["value_func"])


def test_electric_level_sensor():
    """Test the electric level sensor value function."""
    sample_data = load_fixture("sample_response.json")
    value_func = SENSOR_TYPES["electricLevel"]["value_func"]

    result = value_func(sample_data)
    assert result == 97
    assert isinstance(result, int)


def test_pack_input_power_sensor():
    """Test the pack input power sensor value function."""
    sample_data = load_fixture("sample_response.json")
    value_func = SENSOR_TYPES["packInputPower"]["value_func"]

    result = value_func(sample_data)
    assert result == -676  # Should be inverted
    assert isinstance(result, int)


def test_solar_input_power_sensor():
    """Test the solar input power sensor value function."""
    sample_data = load_fixture("sample_response.json")
    value_func = SENSOR_TYPES["solarInputPower"]["value_func"]

    result = value_func(sample_data)
    assert result == 123
    assert isinstance(result, int)


def test_sensor_value_functions_with_missing_data():
    """Test sensor value functions with missing data."""
    # Test with empty data
    empty_data = {}

    for sensor_config in SENSOR_TYPES.values():
        value_func = sensor_config["value_func"]
        try:
            result = value_func(empty_data)
            # If function doesn't raise exception, result should be None or a valid value
            assert result is None or isinstance(result, (int, float, str))
        except (KeyError, AttributeError):
            # Expected for functions that require specific data structure
            pass


def test_sensor_value_functions_with_partial_data():
    """Test sensor value functions with partial data."""
    partial_data = {
        "properties": {"electricLevel": 50},
        "packData": []
    }

    # Test functions that should work with partial data
    electric_level_func = SENSOR_TYPES["electricLevel"]["value_func"]
    result = electric_level_func(partial_data)
    assert result == 50


def test_battery_sensor_value_functions():
    """Test battery-specific sensor value functions."""
    sample_data = load_fixture("sample_response.json")

    # Test battery pack sensors
    battery_sensors = [key for key in SENSOR_TYPES if "battery" in key.lower()]

    for sensor_key in battery_sensors:
        value_func = SENSOR_TYPES[sensor_key]["value_func"]
        # These might require pack index, so we'll test with mock data
        try:
            result = value_func(sample_data)
            # If successful, should be a valid value
            if result is not None:
                assert isinstance(result, (int, float, str))
        except (KeyError, IndexError, TypeError):
            # Expected for battery sensors that need specific pack structure
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
