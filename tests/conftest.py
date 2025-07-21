"""Common fixtures for the Zendure Local tests."""
import pytest
from unittest.mock import MagicMock

from homeassistant.const import CONF_NAME, CONF_RESOURCE
from homeassistant.config_entries import ConfigEntry

from custom_components.zendure_local.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test directory."""
    yield


@pytest.fixture
def config_entry_data():
    """Create a config entry data fixture."""
    return {
        CONF_RESOURCE: "http://SolarFlow800.lan/properties/report",
        CONF_NAME: "Zendure SolarFlow",
    }


@pytest.fixture
def mock_config_entry(hass, config_entry_data):
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.domain = DOMAIN
    entry.data = config_entry_data
    entry.entry_id = "test_entry_id"
    entry.unique_id = "test_unique_id"
    entry.title = "Test Zendure"
    return entry
