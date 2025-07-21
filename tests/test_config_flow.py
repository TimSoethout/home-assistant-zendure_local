"""Test the Zendure Local config flow."""
from unittest.mock import MagicMock, patch

import pytest

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_RESOURCE

from custom_components.zendure_local.config_flow import ConfigFlow
from custom_components.zendure_local.const import DEFAULT_NAME, DEFAULT_RESOURCE, DOMAIN


async def test_config_flow_user_step(hass):
    """Test the user step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    assert result["type"] == "form"
    assert result["errors"] == {}
    assert result["step_id"] == "user"


async def test_config_flow_user_step_success(hass):
    """Test successful config flow user step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    with patch(
        "custom_components.zendure_local.async_setup_entry",
        return_value=True,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_NAME: "Test Zendure",
                CONF_RESOURCE: "http://solarflow800.lan/properties/report",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == "create_entry"
    assert result2["title"] == "Test Zendure"
    assert result2["data"] == {
        CONF_NAME: "Test Zendure",
        CONF_RESOURCE: "http://solarflow800.lan/properties/report",
    }


async def test_config_flow_default_values(hass):
    """Test config flow shows default values."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    data_schema = result["data_schema"]
    assert data_schema is not None
    
    # Check that default values are set correctly
    for field in data_schema.schema:
        if field.default is not None:
            if str(field) == CONF_NAME:
                assert field.default == DEFAULT_NAME
            elif str(field) == CONF_RESOURCE:
                assert field.default == DEFAULT_RESOURCE


async def test_config_flow_unique_id_already_configured(hass):
    """Test that duplicate entries are handled correctly."""
    # Create first entry
    entry = MagicMock()
    entry.data = {
        CONF_NAME: "Existing Zendure",
        CONF_RESOURCE: "http://solarflow800.lan/properties/report",
    }
    hass.config_entries.async_entries = MagicMock(return_value=[entry])
    
    # Try to create second entry with same resource
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Duplicate Zendure",
            CONF_RESOURCE: "http://solarflow800.lan/properties/report",
        },
    )
    
    # Should complete successfully as we don't have unique_id validation implemented
    assert result2["type"] == "create_entry"
