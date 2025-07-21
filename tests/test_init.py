"""Test the Zendure Local integration setup."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_RESOURCE
from homeassistant.core import HomeAssistant

from custom_components.zendure_local import async_setup, async_setup_entry, async_unload_entry
from custom_components.zendure_local.const import DOMAIN


async def test_async_setup(hass: HomeAssistant):
    """Test the async_setup function."""
    config = {}
    result = await async_setup(hass, config)
    assert result is True


async def test_async_setup_entry_success(hass: HomeAssistant, mock_config_entry):
    """Test successful setup of config entry."""
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
        new_callable=AsyncMock,
    ) as mock_forward:
        result = await async_setup_entry(hass, mock_config_entry)
        
        assert result is True
        mock_forward.assert_called_once_with(mock_config_entry, ["sensor"])


async def test_async_unload_entry_success(hass: HomeAssistant, mock_config_entry):
    """Test successful unload of config entry."""
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_unload",
        new_callable=AsyncMock,
        return_value=True,
    ) as mock_unload:
        result = await async_unload_entry(hass, mock_config_entry)
        
        assert result is True
        mock_unload.assert_called_once_with(mock_config_entry, "sensor")


async def test_async_unload_entry_failure(hass: HomeAssistant, mock_config_entry):
    """Test failed unload of config entry."""
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_unload",
        new_callable=AsyncMock,
        return_value=False,
    ) as mock_unload:
        result = await async_unload_entry(hass, mock_config_entry)
        
        assert result is False
        mock_unload.assert_called_once_with(mock_config_entry, "sensor")
