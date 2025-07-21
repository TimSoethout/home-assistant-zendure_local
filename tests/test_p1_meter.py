"""Test the Zendure Local P1 meter functionality."""
import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory

from custom_components.zendure_local.const import DOMAIN
from custom_components.zendure_local.p1_meter import (
    P1_SENSOR_TYPES,
    P1MeterCoordinator,
    P1MeterSensor,
    async_setup_entry,
)


def load_fixture(filename):
    """Load fixture data."""
    path = Path(__file__).parent / "fixtures" / filename
    with path.open(encoding="utf-8") as file:
        return json.loads(file.read())


async def test_p1_meter_coordinator_successful_update(hass: HomeAssistant):
    """Test P1 meter coordinator successful update."""
    mock_response_data = {
        "timestamp": 1752063327,
        "messageId": 1,
        "deviceId": "KNIP",
        "a_aprt_power": -286,
        "b_aprt_power": 1293,
        "c_aprt_power": 1486,
        "total_power": 2494,
        "meterType": 3,
        "protocolType": 51,
    }
    
    with patch(
        "requests.get",
        return_value=MagicMock(
            status_code=200,
            json=MagicMock(return_value=mock_response_data),
        ),
    ):
        coordinator = P1MeterCoordinator(hass, "http://example.com/api")
        data = await coordinator._async_update_data()
        
        assert data == mock_response_data
        assert data["total_power"] == 2494
        assert data["deviceId"] == "KNIP"


async def test_p1_meter_coordinator_failed_update(hass: HomeAssistant):
    """Test P1 meter coordinator failed update."""
    with patch(
        "requests.get",
        side_effect=Exception("Connection error"),
    ):
        coordinator = P1MeterCoordinator(hass, "http://example.com/api")
        data = await coordinator._async_update_data()
        assert data == {}


async def test_p1_meter_setup_entry_no_resource(hass: HomeAssistant):
    """Test P1 meter setup with no resource configured."""
    entry = MagicMock()
    entry.data = {}  # No p1_meter_resource
    
    add_entities_mock = Mock()
    await async_setup_entry(hass, entry, add_entities_mock)
    
    # Should not add any entities if no resource is configured
    assert not add_entities_mock.called


async def test_p1_meter_sensor_initialization(hass: HomeAssistant):
    """Test P1MeterSensor initialization."""
    coordinator = MagicMock()
    coordinator.data = {
        "total_power": 2494,
        "a_aprt_power": -286,
        "deviceId": "KNIP",
        "protocolType": 51,
    }
    
    description = SensorEntityDescription(
        key="total_power",
        name="Total Power",
    )
    
    sensor = P1MeterSensor(coordinator, description, "Test P1 Meter")
    
    assert sensor.entity_description.key == "total_power"
    assert sensor.unique_id == "Test P1 Meter_total_power"
    assert sensor.device_info is not None
    assert sensor.device_info["identifiers"] == {(DOMAIN, "zendure_p1_meter")}
    assert sensor.device_info["manufacturer"] == "Zendure"
    assert sensor.device_info["model"] == "P1 Smart Meter"


async def test_p1_meter_sensor_values(hass: HomeAssistant):
    """Test P1MeterSensor value retrieval."""
    coordinator = MagicMock()
    coordinator.data = {
        "total_power": 2494,
        "a_aprt_power": -286,
        "b_aprt_power": 1293,
        "c_aprt_power": 1486,
        "deviceId": "KNIP",
        "protocolType": 51,
    }
    
    # Test total power sensor
    total_power_sensor = P1MeterSensor(
        coordinator, 
        SensorEntityDescription(key="total_power", name="Total Power"),
        "Test P1 Meter"
    )
    assert total_power_sensor.native_value == 2494
    
    # Test phase A power sensor
    phase_a_sensor = P1MeterSensor(
        coordinator,
        SensorEntityDescription(key="a_aprt_power", name="A Phase Power"),
        "Test P1 Meter"
    )
    assert phase_a_sensor.native_value == -286
    
    # Test device ID sensor
    device_id_sensor = P1MeterSensor(
        coordinator,
        SensorEntityDescription(key="deviceId", name="Device ID"),
        "Test P1 Meter"
    )
    assert device_id_sensor.native_value == "KNIP"


async def test_p1_meter_sensor_no_data(hass: HomeAssistant):
    """Test P1MeterSensor with no coordinator data."""
    coordinator = MagicMock()
    coordinator.data = {}
    
    description = SensorEntityDescription(
        key="total_power",
        name="Total Power",
    )
    
    sensor = P1MeterSensor(coordinator, description, "Test P1 Meter")
    assert sensor.native_value is None


async def test_p1_sensor_types_configuration():
    """Test that P1_SENSOR_TYPES is properly configured."""
    assert isinstance(P1_SENSOR_TYPES, dict)
    assert len(P1_SENSOR_TYPES) > 0
    
    # Check expected sensor types exist
    expected_sensors = [
        "a_aprt_power", "b_aprt_power", "c_aprt_power", 
        "total_power", "deviceId", "protocolType"
    ]
    
    for sensor_key in expected_sensors:
        assert sensor_key in P1_SENSOR_TYPES
        config = P1_SENSOR_TYPES[sensor_key]
        assert "name" in config
        assert "unit" in config
        
        # Check diagnostic entities have entity_category set
        if sensor_key in ["deviceId", "protocolType"]:
            assert "entity_category" in config
            assert config["entity_category"] == EntityCategory.DIAGNOSTIC
