# Zendure Local Integration - Development Instructions

This document provides specific coding guidelines for the Zendure Local Home Assistant custom integration.

- use context7
- use `home-assistant/.github/copilot-instructions.md`

## Integration Overview

**Domain**: `zendure_local`
**Type**: Custom Integration for Zendure devices (SolarFlow, etc.)
**Purpose**: Local polling integration to fetch device data from Zendure devices on the local network

## Project Structure

```
custom_components/zendure_local/
├── __init__.py          # Entry point and setup
├── manifest.json        # Integration metadata
├── const.py            # Constants and configuration
├── config_flow.py      # UI configuration flow
├── sensor.py           # Sensor platform implementation
├── strings.json        # English translations (source of truth)
└── translations/
    └── nl.json         # Dutch translations
```

## Development Guidelines

### Code Standards

- **Python**: 3.11+ compatibility
- **Async**: All I/O operations must be async
- **Type Hints**: Use comprehensive type hints
- **Formatting**: Follow Black/Ruff standards
- **Imports**: Use absolute imports, group properly

### Integration-Specific Patterns

#### Data Fetching
```python
# Use aiohttp for HTTP requests
async with aiohttp.ClientSession() as session:
    async with session.get(resource_url) as response:
        data = await response.json()
```

#### Sensor Creation
```python
# Use translation keys for entity names
class ZendureSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "battery_level"  # Defined in strings.json
```

#### Device Information
```python
# Provide comprehensive device info
_attr_device_info = DeviceInfo(
    identifiers={(DOMAIN, device_id)},
    name=device_name,
    manufacturer="Zendure",
    model="SolarFlow",  # Or detected model
)
```

### Configuration Flow Best Practices

1. **Validate URLs**: Always test connectivity to the provided resource URL
2. **Unique ID Management**: Use device MAC or serial number when available
3. **Error Handling**: Provide clear, actionable error messages
4. **Duplicate Prevention**: Check for existing config entries

```python
# Example validation
try:
    async with aiohttp.ClientSession() as session:
        async with session.get(user_input[CONF_RESOURCE], timeout=10) as response:
            if response.status != 200:
                errors["resource"] = "cannot_connect"
except (aiohttp.ClientError, asyncio.TimeoutError):
    errors["base"] = "cannot_connect"
```

### Translation Guidelines

#### strings.json Structure
```json
{
    "config": {
        "step": {
            "user": {
                "title": "Add Zendure Local Integration",
                "description": "Configure connection to your Zendure device",
                "data": {
                    "name": "Name",
                    "resource": "Resource URL"
                }
            }
        }
    },
    "entity": {
        "sensor": {
            "battery_level": {
                "name": "Battery Level"
            }
        }
    }
}
```

#### Translation Keys
- Use descriptive, consistent naming
- Follow Home Assistant conventions
- Keep entity names short but clear
- Include state translations for enum-like values

### Sensor Implementation

#### Key Patterns
```python
# State mapping for enum values
STATE_MAP = {
    0: "off",
    1: "on",
    2: "standby"
}

# Value transformation
@property
def native_value(self) -> int | None:
    if raw_value := self.coordinator.data.get(self._attr_key):
        return int(raw_value)
    return None

# State attribute for enum sensors
@property
def native_value(self) -> str:
    raw_value = self.coordinator.data.get(self._attr_key)
    return STATE_MAP.get(raw_value, "unknown")
```

#### Entity Categories
- Use `EntityCategory.DIAGNOSTIC` for technical/debug sensors
- Leave category `None` for primary user-facing sensors
- Use `_attr_entity_registry_enabled_default = False` for noisy sensors

### Error Handling

#### Coordinator Pattern
```python
async def _async_update_data(self) -> dict[str, Any]:
    try:
        async with self.session.get(self.resource_url, timeout=30) as response:
            response.raise_for_status()
            return await response.json()
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        raise UpdateFailed(f"Error communicating with device: {err}") from err
```

#### Config Flow Error Handling
```python
# Use specific error types in config flow
except aiohttp.ClientTimeout:
    errors["base"] = "timeout"
except aiohttp.ClientConnectorError:
    errors["base"] = "cannot_connect"
except Exception:  # Broad exception allowed in config flow
    errors["base"] = "unknown"
```

### Testing Guidelines

#### File Structure
```
tests/
├── __init__.py
├── conftest.py          # Test fixtures
├── test_config_flow.py  # Config flow tests
├── test_init.py         # Integration setup tests
└── test_sensor.py       # Sensor platform tests
```

#### Mock Patterns
```python
@pytest.fixture
def mock_zendure_api():
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"battery": 85, "state": 1}
        mock_get.return_value.__aenter__.return_value = mock_response
        yield mock_get
```

### Common Device Types

#### SolarFlow Devices
- Battery level, state, power values
- Temperature sensors
- AC/DC status indicators
- Grid connection state

#### Expected Data Format
```json
{
    "electricLevel": 85,
    "outputPackPower": 500,
    "solarInputPower": 800,
    "remainOutTime": 300,
    "packState": 2
}
```

### Performance Considerations

1. **Update Intervals**:
   - Default: 30 seconds for local devices
   - Adjustable based on device capabilities
   - Never user-configurable

2. **Parallel Updates**:
   - Set `PARALLEL_UPDATES = 1` to serialize updates
   - Prevents overwhelming single device

3. **Session Reuse**:
   - Store aiohttp session in coordinator
   - Reuse across all sensor updates

### Maintenance Notes

#### Version Compatibility
- Maintain backward compatibility with existing config entries
- Use config entry version migrations when needed
- Document breaking changes clearly

#### Device Support
- Support multiple Zendure device types
- Auto-detect device capabilities when possible
- Gracefully handle missing data fields

### Development Workflow

1. **Before Changes**: Run existing tests
2. **After Changes**:
   - Run `pytest tests/` to verify tests pass
   - Run `ruff check .` for linting
   - Test in Home Assistant UI
3. **Pull Requests**: Include test coverage for new features

### Common Issues & Solutions

#### "Integration could not be loaded"
- Check `manifest.json` syntax
- Verify all required files exist
- Check Python syntax errors

#### "Config flow could not be loaded"
- Verify `strings.json` format
- Check config flow class inheritance
- Ensure proper imports

#### Entities not appearing
- Verify `unique_id` is set
- Check `_attr_has_entity_name = True`
- Ensure coordinator data contains expected keys

#### Translation not working
- Verify `translation_key` matches `strings.json`
- Check file encoding (UTF-8)
- Restart Home Assistant after translation changes

## Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale/)
- [Config Flow Documentation](https://developers.home-assistant.io/docs/config_entries_config_flow_handler/)
- [Entity Documentation](https://developers.home-assistant.io/docs/core/entity/)
