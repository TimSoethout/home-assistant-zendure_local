"""Tests for config flow logic without Home Assistant test framework."""
import sys
from pathlib import Path
from unittest.mock import patch

# Add the parent directory to sys.path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from custom_components.zendure_local.config_flow import ConfigFlow
from custom_components.zendure_local.const import DEFAULT_NAME, DEFAULT_RESOURCE, DOMAIN


def test_config_flow_init():
    """Test that ConfigFlow can be instantiated."""
    flow = ConfigFlow()
    assert flow is not None
    assert hasattr(flow, 'VERSION')
    assert hasattr(flow, 'MINOR_VERSION')


def test_config_flow_constants():
    """Test that constants are properly defined."""
    assert DOMAIN == "zendure_local"
    assert DEFAULT_NAME is not None
    assert DEFAULT_RESOURCE is not None
    assert isinstance(DEFAULT_NAME, str)
    assert isinstance(DEFAULT_RESOURCE, str)


def test_config_flow_schema_structure():
    """Test that ConfigFlow has proper schema attributes."""
    flow = ConfigFlow()

    # Check that the flow has the necessary attributes for HA integration
    assert hasattr(flow, 'VERSION')
    assert hasattr(flow, 'MINOR_VERSION')

    # Verify version numbers are integers
    assert isinstance(flow.VERSION, int)
    assert isinstance(flow.MINOR_VERSION, int)


@patch('custom_components.zendure_local.config_flow.vol')
def test_config_flow_uses_voluptuous(mock_vol):
    """Test that config flow uses voluptuous for validation."""
    # Import should succeed and voluptuous should be available
    import custom_components.zendure_local.config_flow as config_flow
    assert hasattr(config_flow, 'vol')


def test_config_flow_basic_structure():
    """Test that config flow has basic required structure."""
    flow = ConfigFlow()

    # Test that basic attributes exist
    assert hasattr(flow, 'VERSION')
    assert hasattr(flow, 'MINOR_VERSION')

    # Test that version is reasonable
    assert flow.VERSION >= 1
    assert flow.MINOR_VERSION >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
