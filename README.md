# Zendure Local Integration

This custom integration allows Home Assistant to monitor your Zendure SolarFlow device locally via REST API.

## Features

- Sensors for battery, inverter temperature, charge/discharge times, and more
- Local polling (no cloud)
- Configurable via Home Assistant UI
- HACS compatible
- ONLY READ/QUERY is supported in this initial release

## Installation via HACS

1. **Add this repository to HACS:**
   - [![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=TimSoethout&repository=home-assistant-zendure_local&category=integration)
   - Or go to **HACS > Integrations > Custom repositories**.
   - Enter the URL of this repository:  
     `https://github.com/TimSoethout/home-assistant-zendure_local`
   - Set category to **Integration** and click **Add**.

2. **Install the Integration:**
   - Find **Zendure Local Integration** in HACS > Integrations.
   - Click **Install**.

3. **Restart Home Assistant** after installation.

4. **Add the Integration:**
   - Go to **Settings > Devices & Services > Add Integration**.
   - Search for **Zendure Local** and follow the prompts to configure.

## Manual Installation

1. Copy the `zendure_local` folder to your `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration via the UI as above.

## Configuration

All configuration is done via the Home Assistant UI (Config Flow).

## Support

For issues or feature requests, open an issue on [GitHub](https://github.com/TimSoethout/home-assistant-zendure_local/issues).