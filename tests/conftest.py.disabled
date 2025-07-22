"""Simple fixtures for testing without full Home Assistant setup."""
import pytest
from unittest.mock import MagicMock
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_RESOURCE
from custom_components.zendure_local.const import DOMAIN


@pytest.fixture
def config_entry_data():
    """Create a config entry data fixture."""
    return {
        CONF_RESOURCE: "http://SolarFlow800.lan/properties/report",
        CONF_NAME: "Zendure SolarFlow",
    }


@pytest.fixture
def mock_config_entry(config_entry_data):
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.domain = DOMAIN
    entry.data = config_entry_data
    entry.entry_id = "test_entry_id"
    entry.unique_id = "test_unique_id"
    entry.title = "Test Zendure"
    return entry
