## Running Tests

Here are several ways to run the tests for your Zendure Local integration, following pytest and Home Assistant best practices:

### Option 1: Using pytest with virtual environment (Recommended)

1. **Set up virtual environment:**
   ```bash
   cd /Users/tim/workspace/home-assistant/config/zendure_local
   python3 -m venv venv
   source venv/bin/activate.fish  # For fish shell
   # or source venv/bin/activate   # For bash/zsh
   ```

2. **Install dependencies:**
   ```bash
   pip install -r tests/requirements.txt
   ```

3. **Run basic functionality tests (Recommended):**
   ```bash
   # Run working unit tests that validate core functionality
   pytest tests/test_basic.py -v
   
   # Run with coverage report
   pytest tests/test_basic.py --cov=custom_components.zendure_local --cov-report=term-missing -v
   
   # Alternative: Run directly with Python (if pytest has issues)
   PYTHONPATH=. python tests/test_basic.py
   ```

4. **Run specific test files:**
   ```bash
   pytest tests/test_basic.py -v           # Basic functionality tests (reliable)
   pytest tests/test_sensor.py -v          # Sensor platform tests (may need HA fixtures)
   pytest tests/test_config_flow.py -v     # Config flow tests (may need HA fixtures)
   pytest tests/test_init.py -v            # Integration setup tests (may need HA fixtures)
   ```

5. **Run specific test functions:**
   ```bash
   # Run individual test functions
   pytest tests/test_basic.py::test_sensor_types_configuration -v
   pytest tests/test_basic.py::test_sensor_value_functions -v
   ```

### Option 2: Home Assistant Development Environment

If you have a full Home Assistant development environment set up:

```bash
# Run tests for your specific integration with coverage
pytest ./tests/components/zendure_local/ --cov=homeassistant.components.zendure_local --cov-report term-missing -vv

# Run tests with Home Assistant's full test infrastructure
pytest tests/ --timeout=10 --durations=10
```

### Option 3: Quick Development Testing

For rapid iteration during development:

```bash
# Run only basic tests (fastest, most reliable)
pytest tests/test_basic.py

# Run with keyword filtering
pytest tests/ -k "sensor_types or fixture_loading" -v

# Stop after first failure for quick debugging
pytest tests/test_basic.py -x

# Run tests matching specific patterns
pytest tests/ -k "coordinator" -v
```

### Test Options and Flags

Following pytest best practices, here are useful command-line options:

```bash
# Essential options
pytest tests/test_basic.py -v                    # Verbose output
pytest tests/test_basic.py -x                    # Stop on first failure  
pytest tests/test_basic.py -s                    # Show print statements
pytest tests/test_basic.py --tb=short            # Shorter traceback format

# Coverage and reporting
pytest tests/test_basic.py --cov=custom_components.zendure_local --cov-report=html
pytest tests/test_basic.py --durations=10        # Show 10 slowest tests

# Test selection
pytest tests/ -k "sensor"                        # Run tests matching "sensor"
pytest tests/ -m "not slow"                      # Skip tests marked as slow
pytest tests/test_basic.py::test_sensor_types_configuration  # Run specific test

# Debugging options  
pytest tests/test_basic.py --pdb                 # Drop into debugger on failure
pytest tests/test_basic.py --timeout=5           # Fail tests after 5 seconds
```

### Examples:

```bash
# Quick validation of core functionality
pytest tests/test_basic.py -v

# Comprehensive test with coverage report
pytest tests/test_basic.py --cov=custom_components.zendure_local --cov-report=html -v

# Debug failing test with detailed output
pytest tests/test_basic.py::test_sensor_value_functions -vvv --tb=long

# Performance analysis
pytest tests/test_basic.py --durations=0 -v
```

### Troubleshooting

If you encounter import errors:
1. Ensure you're in the virtual environment: `source venv/bin/activate`
2. Verify the `pythonpath = .` is set in `pytest.ini`
3. Run with explicit Python path: `PYTHONPATH=. pytest tests/test_basic.py -v`

If you see Home Assistant fixture errors:
- **Root cause**: The `pytest-homeassistant-custom-component` plugin conflicts with basic tests
- **Solution**: We've disabled the conflicting `conftest.py` file for basic testing
- **Quick fix**: `PYTHONPATH=. python tests/test_basic.py` always works
- **Best practice**: Use `pytest tests/test_basic.py -v` for the working configuration

**Debugging the test environment:**
```bash
# If pytest still has issues, run the setup commands:
pip uninstall pytest-homeassistant-custom-component -y
mv tests/conftest.py tests/conftest.py.disabled

# Then pytest should work normally:
pytest tests/test_basic.py -v
```

Common pytest patterns:
```bash
# Re-run only failed tests from last run
pytest --lf tests/test_basic.py

# Run tests that failed in last session first, then all others  
pytest --ff tests/test_basic.py

# Disable warnings for cleaner output
pytest tests/test_basic.py --disable-warnings

# Get help on available options
pytest --help
```

### Continuous Integration

The repository includes a comprehensive GitHub Actions workflow (`.github/workflows/tests.yml`) that:

- **Runs tests** on Python 3.11 and 3.12
- **Generates coverage reports** and uploads to Codecov
- **Performs code linting** with ruff, black, isort, and mypy  
- **Validates integration** with Home Assistant's hassfest tool
- **Runs daily** to catch dependency issues

The workflow is automatically triggered on:
- Push to main/master branches
- Pull requests
- Daily schedule (6 AM UTC)

**Local development tip**: Before pushing, run the same checks locally:

```bash
# Run tests like CI does
pytest tests/test_basic.py --cov=custom_components.zendure_local --cov-report=xml -v

# Run linting like CI does
ruff check custom_components/
black --check custom_components/
isort --check-only custom_components/

# Fix linting issues automatically
black custom_components/
isort custom_components/
ruff check --fix custom_components/
```

### Integration Quality

Following Home Assistant integration quality standards:

```bash
# Test coverage check (aim for >90% on core functionality)
pytest tests/test_basic.py --cov=custom_components.zendure_local --cov-report=term-missing

# Validate integration follows HA patterns
# Check entity unique IDs, device info, etc. in test output

# Performance testing  
pytest tests/test_basic.py --durations=10
```
