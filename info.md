# Zendure Local Integration

This integration provides sensors for Zendure SolarFlow devices via local REST API.

- Add to your `custom_components` folder
- Configure in `configuration.yaml`:

```yaml
sensor:
  - platform: zendure_local
    resource: "http://SolarFlow800.lan/properties/report"
    name: "Solarflow 800"
```
