"""Basic unit tests for the Zendure Local integration."""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from custom_components.zendure_local.const import DOMAIN
from custom_components.zendure_local.sensor import SENSOR_TYPES


def load_fixture(filename):
    """Load fixture data."""
    path = Path(__file__).parent / "fixtures" / filename
    with path.open(encoding="utf-8") as file:
        return json.loads(file.read())


def test_sensor_types_configuration():
    """Test that SENSOR_TYPES is properly configured."""
    assert isinstance(SENSOR_TYPES, dict)
    assert len(SENSOR_TYPES) > 0
    
    # Check a few key sensors exist
    assert "electricLevel" in SENSOR_TYPES
    assert "packInputPower" in SENSOR_TYPES
    assert "solarInputPower" in SENSOR_TYPES
    
    # Check sensor configurations have required fields
    for config in SENSOR_TYPES.values():
        assert "value_func" in config
        assert callable(config["value_func"])


def test_domain_constant():
    """Test that the domain is properly defined."""
    assert DOMAIN == "zendure_local"


def test_fixture_loading():
    """Test that fixture data can be loaded."""
    data = load_fixture("sample_response.json")
    assert isinstance(data, dict)
    assert "properties" in data
    assert "packData" in data
    assert data["properties"]["electricLevel"] == 97


def test_sensor_value_functions():
    """Test that sensor value functions work with sample data."""
    sample_data = load_fixture("sample_response.json")
    
    # Test electricLevel sensor
    electric_level_func = SENSOR_TYPES["electricLevel"]["value_func"]
    assert electric_level_func(sample_data) == 97
    
    # Test packInputPower sensor  
    pack_input_power_func = SENSOR_TYPES["packInputPower"]["value_func"]
    assert pack_input_power_func(sample_data) == -676  # Negative because it's inverted
    
    # Test solarInputPower sensor
    solar_input_power_func = SENSOR_TYPES["solarInputPower"]["value_func"]
    assert solar_input_power_func(sample_data) == 123


if __name__ == "__main__":
    # Basic test runner
    import sys
    
    tests = [
        test_sensor_types_configuration,
        test_domain_constant,
        test_fixture_loading,
        test_sensor_value_functions,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
