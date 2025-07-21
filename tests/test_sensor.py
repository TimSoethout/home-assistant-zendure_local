"""Tests for the Zendure Local sensor platform."""
import json
import os
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import CONF_NAME, CONF_RESOURCE
from homeassistant.core import HomeAssistant

from custom_components.zendure_local.const import DOMAIN
from custom_components.zendure_local.sensor import (
    SENSOR_TYPES,
    ZendureCoordinator,
    ZendureLocalSensor,
    ZendureLocalBatterySensor,
    async_setup_entry,
)


def load_fixture(filename):
    """Load fixture data."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as file:
        return json.loads(file.read())


@pytest.fixture
def mock_successful_response():
    """Return a successful response with sample data."""
    return load_fixture("sample_response.json")


@pytest.fixture
def mock_coordinator(hass, mock_successful_response):
    """Create a mock coordinator with sample data."""
    coordinator = ZendureCoordinator(hass, "http://example.com/api")
    coordinator.data = mock_successful_response
    coordinator.last_update_success = True
    return coordinator


async def test_coordinator_successful_update(hass: HomeAssistant, mock_successful_response):
    """Test coordinator update method with successful response."""
    with patch(
        "requests.get",
        return_value=MagicMock(
            status_code=200,
            json=MagicMock(return_value=mock_successful_response),
        ),
    ):
        coordinator = ZendureCoordinator(hass, "http://example.com/api")
        data = await coordinator._async_update_data()
        
        assert data == mock_successful_response
        assert "properties" in data
        assert "packData" in data
        assert data["properties"]["electricLevel"] == 97


async def test_coordinator_failed_update(hass: HomeAssistant):
    """Test coordinator update method with failed response."""
    with patch(
        "requests.get",
        side_effect=Exception("Connection error"),
    ):
        coordinator = ZendureCoordinator(hass, "http://example.com/api")
        data = await coordinator._async_update_data()
        assert data == {}


async def test_coordinator_http_error(hass: HomeAssistant):
    """Test coordinator update method with HTTP error."""
    with patch(
        "requests.get",
        return_value=MagicMock(status_code=404),
    ):
        coordinator = ZendureCoordinator(hass, "http://example.com/api")
        data = await coordinator._async_update_data()
        assert data == {}


async def test_sensor_setup_entry(hass: HomeAssistant, mock_successful_response, mock_config_entry):
    """Test sensor setup from config entry."""
    with patch(
        "custom_components.zendure_local.sensor.ZendureCoordinator._async_update_data",
        return_value=mock_successful_response,
    ), patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_config_entry_first_refresh",
        new_callable=AsyncMock,
    ):
        add_entities_mock = Mock()
        await async_setup_entry(hass, mock_config_entry, add_entities_mock)
        
        # Verify entities were added
        assert add_entities_mock.called
        entities = add_entities_mock.call_args[0][0]
        assert len(entities) > 0
        
        # Check we have both main sensors and battery sensors
        main_sensors = [e for e in entities if isinstance(e, ZendureLocalSensor)]
        battery_sensors = [e for e in entities if isinstance(e, ZendureLocalBatterySensor)]
        
        assert len(main_sensors) > 0
        assert len(battery_sensors) > 0


async def test_zendure_local_sensor_initialization(hass: HomeAssistant, mock_coordinator):
    """Test ZendureLocalSensor initialization."""
    description = SensorEntityDescription(
        key="electricLevel",
        name="Battery Level",
    )
    
    sensor = ZendureLocalSensor(mock_coordinator, description, "Test Zendure")
    
    assert sensor.entity_description.key == "electricLevel"
    assert sensor.unique_id == "Test Zendure_electricLevel"
    assert sensor.device_info is not None
    assert sensor.device_info["identifiers"] == {(DOMAIN, "zendure_solarflow")}
    assert sensor.device_info["manufacturer"] == "Zendure"
    assert sensor.device_info["model"] == "Solarflow Hub"


async def test_zendure_local_sensor_value(hass: HomeAssistant, mock_coordinator):
    """Test ZendureLocalSensor value retrieval."""
    description = SensorEntityDescription(
        key="electricLevel",
        name="Battery Level",
    )
    
    sensor = ZendureLocalSensor(mock_coordinator, description, "Test Zendure")
    
    # Test that sensor gets value from coordinator data
    assert sensor.native_value == 97  # From fixture data


async def test_zendure_local_sensor_no_data(hass: HomeAssistant):
    """Test ZendureLocalSensor with no coordinator data."""
    coordinator = ZendureCoordinator(hass, "http://example.com/api")
    coordinator.data = None
    
    description = SensorEntityDescription(
        key="electricLevel",
        name="Battery Level",
    )
    
    sensor = ZendureLocalSensor(coordinator, description, "Test Zendure")
    assert sensor.native_value is None


async def test_zendure_local_sensor_invalid_key(hass: HomeAssistant, mock_coordinator):
    """Test ZendureLocalSensor with invalid sensor key."""
    description = SensorEntityDescription(
        key="nonexistent_key",
        name="Non-existent Sensor",
    )
    
    sensor = ZendureLocalSensor(mock_coordinator, description, "Test Zendure")
    assert sensor.native_value is None


async def test_zendure_battery_sensor_initialization(hass: HomeAssistant, mock_coordinator):
    """Test ZendureLocalBatterySensor initialization."""
    description = SensorEntityDescription(
        key="pack_soc",
        name="Battery SOC",
    )
    
    battery_sensor = ZendureLocalBatterySensor(
        mock_coordinator, description, "Test Battery 1", 0
    )
    
    assert battery_sensor.entity_description.key == "pack_soc"
    assert battery_sensor.unique_id == "Test Battery 1_pack_soc"
    assert battery_sensor.device_info is not None
    assert battery_sensor.device_info["identifiers"] == {(DOMAIN, "zendure_pack1")}
    assert battery_sensor.device_info["manufacturer"] == "Zendure"
    assert battery_sensor.device_info["model"] == "Battery Pack"


async def test_zendure_battery_sensor_values(hass: HomeAssistant, mock_coordinator):
    """Test ZendureLocalBatterySensor value retrieval for different sensor types."""
    # Test SOC sensor
    soc_description = SensorEntityDescription(key="pack_soc", name="Battery SOC")
    soc_sensor = ZendureLocalBatterySensor(mock_coordinator, soc_description, "Test Battery 1", 0)
    assert soc_sensor.native_value == 97  # From fixture data

    # Test power sensor
    power_description = SensorEntityDescription(key="pack_power", name="Battery Power")
    power_sensor = ZendureLocalBatterySensor(mock_coordinator, power_description, "Test Battery 1", 0)
    assert power_sensor.native_value == 742  # From fixture data

    # Test temperature sensor
    temp_description = SensorEntityDescription(key="pack_temp", name="Battery Temperature")
    temp_sensor = ZendureLocalBatterySensor(mock_coordinator, temp_description, "Test Battery 1", 0)
    assert temp_sensor.native_value == 36.0  # (3091 - 2731) / 10.0

    # Test voltage sensor
    voltage_description = SensorEntityDescription(key="pack_voltage", name="Battery Voltage")
    voltage_sensor = ZendureLocalBatterySensor(mock_coordinator, voltage_description, "Test Battery 1", 0)
    assert voltage_sensor.native_value == 4980  # From fixture data

    # Test state sensor
    state_description = SensorEntityDescription(key="pack_state", name="Battery State")
    state_sensor = ZendureLocalBatterySensor(mock_coordinator, state_description, "Test Battery 1", 0)
    assert state_sensor.native_value == "discharging"  # state 2 maps to discharging


async def test_zendure_battery_sensor_no_pack_data(hass: HomeAssistant):
    """Test ZendureLocalBatterySensor with no pack data."""
    coordinator = ZendureCoordinator(hass, "http://example.com/api")
    coordinator.data = {"properties": {}}  # No packData
    
    description = SensorEntityDescription(key="pack_soc", name="Battery SOC")
    battery_sensor = ZendureLocalBatterySensor(coordinator, description, "Test Battery 1", 0)
    
    assert battery_sensor.native_value is None


async def test_zendure_battery_sensor_invalid_pack_index(hass: HomeAssistant, mock_coordinator):
    """Test ZendureLocalBatterySensor with invalid pack index."""
    description = SensorEntityDescription(key="pack_soc", name="Battery SOC")
    
    # Use pack index 5 when only 2 packs exist in fixture
    battery_sensor = ZendureLocalBatterySensor(mock_coordinator, description, "Test Battery 6", 5)
    assert battery_sensor.native_value is None


async def test_sensor_coordinator_update(hass: HomeAssistant, mock_coordinator, mock_successful_response):
    """Test sensor updates when coordinator data changes."""
    description = SensorEntityDescription(key="electricLevel", name="Battery Level")
    sensor = ZendureLocalSensor(mock_coordinator, description, "Test Zendure")
    
    initial_value = sensor.native_value
    assert initial_value == 97
    
    # Update coordinator data
    new_data = mock_successful_response.copy()
    new_data["properties"]["electricLevel"] = 85
    mock_coordinator.data = new_data
    
    # Trigger update
    sensor._handle_coordinator_update()
    
    assert sensor.native_value == 85
    assert sensor.native_value != initial_value


async def test_sensor_types_configuration():
    """Test that SENSOR_TYPES is properly configured."""
    assert isinstance(SENSOR_TYPES, dict)
    assert len(SENSOR_TYPES) > 0
    
    # Check a few key sensors exist
    assert "electricLevel" in SENSOR_TYPES
    assert "packInputPower" in SENSOR_TYPES
    assert "solarInputPower" in SENSOR_TYPES
    
    # Check sensor configurations have required fields
    for key, config in SENSOR_TYPES.items():
        assert "value_func" in config
        assert callable(config["value_func"])
        assert "icon" in config or "device_class" in config  # Should have at least one
