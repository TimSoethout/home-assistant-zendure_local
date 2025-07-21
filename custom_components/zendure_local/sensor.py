"""Zendure Local sensor platform for Home Assistant."""

import logging
import re

import aiohttp
import requests

from homeassistant.components.button import ButtonEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import CONF_NAME, CONF_RESOURCE, UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DEFAULT_RESOURCE, DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


def camel_to_snake(camel_str: str) -> str:
    """Convert camelCase to snake_case."""
    # Handle special cases first
    if camel_str == "IOTState":
        return "iot_state"
    if camel_str == "BatVolt":
        return "bat_volt"

    # Convert camelCase to snake_case
    snake_str = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_str).lower()


# Translation key mapping for camelCase to snake_case
TRANSLATION_KEY_MAP = {
    "messageId": "message_id",
    "smartMode": "smart_mode",
    "remainOutTime": "remain_out_time",
    "hyperTmp": "hyper_tmp",
    "maxTemp": "max_temp",
    "electricLevel": "electric_level",
    "minSoc": "min_soc",
    "socSet": "soc_set",
    "acMode": "ac_mode",
    "socStatus": "soc_status",
    "outputLimit": "output_limit",
    "inputLimit": "input_limit",
    "packInputPower": "pack_input_power",
    "outputPackPower": "output_pack_power",
    "solarInputPower": "solar_input_power",
    "solarPower1": "solar_power1",
    "solarPower2": "solar_power2",
    "gridInputPower": "grid_input_power",
    "outputHomePower": "output_home_power",
    "packState": "pack_state",
    "heatState": "heat_state",
    "dcStatus": "dc_status",
    "pvStatus": "pv_status",
    "acStatus": "ac_status",
    "gridState": "grid_state",
    "BatVolt": "bat_volt",
    "IOTState": "iot_state",
    "gridStandard": "grid_standard",
    "inverseMaxPower": "inverse_max_power",
    "chargeMaxLimit": "charge_max_limit",
}


class ZendureCoordinator(DataUpdateCoordinator):
    """Data coordinator for Zendure Local sensors."""

    def __init__(self, hass: HomeAssistant, resource: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.resource = resource

    async def _async_update_data(self) -> dict:
        """Fetch data from Zendure device."""
        try:
            _LOGGER.debug("Fetching data from %s", self.resource)
            response = await self.hass.async_add_executor_job(
                lambda: requests.get(self.resource, timeout=10)
            )
            # Example response:
            # {"timestamp":1750179973,"messageId":142,"sn":"REDACTED","version":2,"product":"solarFlow800","properties":{"heatState":0,"packInputPower":676,"outputPackPower":0,"outputHomePower":799,"remainOutTime":324,"packState":2,"electricLevel":97,"gridInputPower":0,"solarInputPower":123,"solarPower1":64,"solarPower2":59,"pass":0,"reverseState":0,"socStatus":0,"hyperTmp":3211,"dcStatus":2,"pvStatus":1,"acStatus":1,"dataReady":1,"gridState":1,"BatVolt":4923,"socLimit":0,"writeRsp":0,"acMode":2,"inputLimit":400,"outputLimit":800,"socSet":1000,"minSoc":50,"gridStandard":4,"gridReverse":1,"inverseMaxPower":800,"lampSwitch":1,"IOTState":2,"factoryModeState":0,"OTAState":0,"LCNState":0,"oldMode":0,"VoltWakeup":0,"ts":1750179970,"bindstate":0,"tsZone":14,"chargeMaxLimit":800,"smartMode":1,"packNum":2,"rssi":-82,"is_error":0},"packData":[{"sn":"REDACTED","packType":70,"socLevel":97,"state":2,"power":742,"maxTemp":3091,"totalVol":4980,"batcur":65387,"maxVol":332,"minVol":331,"softVersion":4113,"heatState":0},{"sn":"REDACTED","packType":70,"socLevel":97,"state":2,"power":139,"maxTemp":3051,"totalVol":4970,"batcur":65508,"maxVol":332,"minVol":331,"softVersion":4113,"heatState":0}]}a

            if response.status_code == 200:
                data = response.json()
                _LOGGER.debug("Successfully fetched data: %s", data)
                return data

            _LOGGER.warning(
                "HTTP error %s when fetching data", response.status_code
            )
            return {}

        except requests.exceptions.RequestException as ex:
            _LOGGER.error("Error fetching Zendure data: %s", ex)
            return {}
        except (ValueError, KeyError) as ex:
            _LOGGER.error("Error parsing Zendure data: %s", ex)
            return {}


SENSOR_TYPES = {
    "messageId": {
        "native_unit_of_measurement": None,
        "icon": "mdi:api",
        "state_class": SensorStateClass.MEASUREMENT,
        "value_func": lambda data: data["messageId"],
    },
    "smartMode": {
        "native_unit_of_measurement": None,
        "icon": "mdi:floppy",
        "value_func": lambda data: {1: "ram", 0: "flash"}.get(
            int(data["properties"]["smartMode"]), "unknown"
        ),
    },
    "remainOutTime": {
        "native_unit_of_measurement": None,
        "icon": "mdi:clock-time-eight-outline",
        "value_func": lambda data: (
            "Unknown"
            if int(data["properties"]["remainOutTime"] // 60) == 999
            and int(data["properties"]["remainOutTime"] % 60) == 0
            else f"{int(data['properties']['remainOutTime'] // 60)} h {int(data['properties']['remainOutTime'] % 60)} m"
        ),
    },
    "hyperTmp": {
        "native_unit_of_measurement": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:thermometer",
        "value_func": lambda data: (int(data["properties"]["hyperTmp"]) - 2731) / 10.0,
    },
    "maxTemp": {
        "native_unit_of_measurement": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:thermometer",
        "value_func": lambda data: (int(data["packData"][0]["maxTemp"]) - 2731) / 10.0,
    },
    "electricLevel": {
        "native_unit_of_measurement": "%",
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "value_func": lambda data: data["properties"]["electricLevel"],
    },
    "minSoc": {
        "native_unit_of_measurement": "%",
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-high",
        "value_func": lambda data: int(int(data["properties"]["minSoc"]) / 10),
    },
    "socSet": {
        "native_unit_of_measurement": "%",
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-high",
        "value_func": lambda data: int(int(data["properties"]["socSet"]) / 10),
    },
    "acMode": {
        "native_unit_of_measurement": None,
        "icon": "mdi:battery-charging-wireless",
        "value_func": lambda data: {1: "charging", 2: "discharging"}.get(
            int(data["properties"]["acMode"]), "unknown"
        ),
    },
    "is_error": {
        "native_unit_of_measurement": None,
        "icon": "mdi:battery-alert",
        "value_func": lambda data: {0: "no_errors", 1: "check_app"}.get(
            int(data["properties"]["is_error"]), "unknown"
        ),
    },
    "socStatus": {
        "native_unit_of_measurement": None,
        "icon": "mdi:battery-heart-variant",
        "value_func": lambda data: {0: "good", 1: "calibrating"}.get(
            int(data["properties"]["socStatus"]), "unknown"
        ),
    },
    "outputLimit": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "value_func": lambda data: data["properties"]["outputLimit"],
    },
    "inputLimit": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "value_func": lambda data: data["properties"]["inputLimit"],
    },
    "packInputPower": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "value_func": lambda data: -int(data["properties"]["packInputPower"]),
    },
    "outputPackPower": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "value_func": lambda data: data["properties"]["outputPackPower"],
    },
    "combined_power": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "value_func": lambda data: (
            data["properties"]["outputPackPower"]
            if int(data["properties"]["outputPackPower"]) != 0
            else -int(data["properties"]["packInputPower"])
        ),
    },
    # Solar Power Sensors
    "solarInputPower": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-power",
        "value_func": lambda data: data["properties"]["solarInputPower"],
    },
    "solarPower1": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-panel",
        "value_func": lambda data: data["properties"]["solarPower1"],
    },
    "solarPower2": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-panel",
        "value_func": lambda data: data["properties"]["solarPower2"],
    },
    # Grid Power Sensors
    "gridInputPower": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:transmission-tower",
        "value_func": lambda data: data["properties"]["gridInputPower"],
    },
    "outputHomePower": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:home-lightning-bolt",
        "value_func": lambda data: data["properties"]["outputHomePower"],
    },
    # Status Sensors
    "packState": {
        "native_unit_of_measurement": None,
        "icon": "mdi:battery-sync",
        "value_func": lambda data: {
            0: "standby",
            1: "charging",
            2: "discharging",
            3: "bypass",
        }.get(int(data["properties"]["packState"]), "unknown"),
    },
    "heatState": {
        "native_unit_of_measurement": None,
        "icon": "mdi:thermometer-alert",
        "value_func": lambda data: {0: "normal", 1: "heating"}.get(
            int(data["properties"]["heatState"]), "unknown"
        ),
    },
    "dcStatus": {
        "native_unit_of_measurement": None,
        "icon": "mdi:current-dc",
        "value_func": lambda data: {0: "off", 1: "on", 2: "ready"}.get(
            int(data["properties"]["dcStatus"]), "unknown"
        ),
    },
    "pvStatus": {
        "native_unit_of_measurement": None,
        "icon": "mdi:solar-panel-large",
        "value_func": lambda data: {0: "off", 1: "on"}.get(
            int(data["properties"]["pvStatus"]), "unknown"
        ),
    },
    "acStatus": {
        "native_unit_of_measurement": None,
        "icon": "mdi:current-ac",
        "value_func": lambda data: {0: "off", 1: "on"}.get(
            int(data["properties"]["acStatus"]), "unknown"
        ),
    },
    "gridState": {
        "native_unit_of_measurement": None,
        "icon": "mdi:transmission-tower-export",
        "value_func": lambda data: {0: "disconnected", 1: "connected"}.get(
            int(data["properties"]["gridState"]), "unknown"
        ),
    },
    # Voltage Sensors
    "BatVolt": {
        "native_unit_of_measurement": "mV",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:flash",
        "value_func": lambda data: data["properties"]["BatVolt"],
    },
    # Network & System
    "rssi": {
        "native_unit_of_measurement": "dBm",
        "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:wifi-strength-2",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "value_func": lambda data: data["properties"]["rssi"],
    },
    "IOTState": {
        "native_unit_of_measurement": None,
        "icon": "mdi:cloud-check",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "value_func": lambda data: {
            0: "disconnected",
            1: "connecting",
            2: "connected",
        }.get(int(data["properties"]["IOTState"]), "unknown"),
    },
    # Configuration Sensors
    "gridStandard": {
        "native_unit_of_measurement": None,
        "icon": "mdi:cog",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "value_func": lambda data: data["properties"]["gridStandard"],
    },
    "inverseMaxPower": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "icon": "mdi:lightning-bolt-circle",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "value_func": lambda data: data["properties"]["inverseMaxPower"],
    },
    "chargeMaxLimit": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "icon": "mdi:battery-charging-high",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "value_func": lambda data: data["properties"]["chargeMaxLimit"],
    },
}

PACK_SENSOR_TYPES = {
    "soc": {
        "native_unit_of_measurement": "%",
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-outline",
    },
    "power": {
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-charging",
    },
    "temp": {
        "native_unit_of_measurement": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:thermometer",
    },
    "voltage": {
        "native_unit_of_measurement": "mV",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:flash",
    },
    "state": {
        "native_unit_of_measurement": None,
        "icon": "mdi:battery-sync",
    },
}

ZENDURE_ACTIONS = [
    {
        "key": "snel_laden",
        "name": "Snel Laden",
        "service": "rest_command.zendure_snel_laden",
    },
    {
        "key": "stop_met_laden",
        "name": "Stop met Laden",
        "service": "rest_command.zendure_stop_met_laden",
    },
    {
        "key": "snel_ontladen",
        "name": "Snel Ontladen",
        "service": "rest_command.zendure_snel_ontladen",
    },
    {
        "key": "stop_met_ontladen",
        "name": "Stop met Ontladen",
        "service": "rest_command.zendure_stop_met_ontladen",
    },
    {
        "key": "stop_met_alles",
        "name": "Stop met Alles",
        "service": "rest_command.zendure_stop_met_alles",
    },
]


class ZendureActionButton(ButtonEntity):
    """Button entity for Zendure action."""

    def __init__(self, hass, action, device_info):
        """Initialize ZendureActionButton."""
        self._hass = hass
        self._action = action
        self._attr_name = f"Zendure {action['name']}"
        self._attr_unique_id = f"zendure_{action['key']}_button"
        self._attr_device_info = device_info

    async def async_press(self) -> None:
        """Handle button press by making the actual POST call to the Zendure device."""
        serial = "!secret solarflow800_serial"  # Replace with actual serial retrieval if needed
        url = "http://SolarFlow800.lan/properties/write"
        payloads = {
            "snel_laden": {
                "sn": serial,
                "properties": {"acMode": 1, "inputLimit": 2400},
            },
            "stop_met_laden": {
                "sn": serial,
                "properties": {"acMode": 1, "inputLimit": 0},
            },
            "snel_ontladen": {
                "sn": serial,
                "properties": {"acMode": 2, "outputLimit": 2400},
            },
            "stop_met_ontladen": {
                "sn": serial,
                "properties": {"acMode": 2, "outputLimit": 0},
            },
            "stop_met_alles": {
                "sn": serial,
                "properties": {"outputLimit": 0, "inputLimit": 0},
            },
        }
        payload = payloads.get(self._action["key"])
        if payload is None:
            _LOGGER.error("No payload defined for action %s", self._action["key"])
            return
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            resp = await session.post(url, json=payload)
            if resp.status != 200:
                _LOGGER.error(
                    "Failed to POST to Zendure: %s %s", resp.status, await resp.text()
                )
            else:
                _LOGGER.debug("POST to Zendure succeeded for %s", self._action["key"])


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    """Set up Zendure Local sensors from a config entry."""
    resource = entry.data.get(CONF_RESOURCE, DEFAULT_RESOURCE)
    name = entry.data.get(CONF_NAME, "Solarflow 800")

    _LOGGER.debug(
        "Setting up ZendureLocal integration with resource: %s and name: %s",
        resource,
        name,
    )

    coordinator = ZendureCoordinator(hass, resource)
    await coordinator.async_config_entry_first_refresh()

    if coordinator.data is None:
        _LOGGER.warning(
            "Zendure coordinator did not fetch data on first refresh; entities will be added with unknown state"
        )
    else:
        _LOGGER.debug("Coordinator initial data: %s", coordinator.data)

    entities = []

    # Create main inverter device sensors
    main_sensors = [key for key in SENSOR_TYPES if not key.startswith("pack")]
    for sensor_key in main_sensors:
        sensor_config = SENSOR_TYPES[sensor_key]
        # Use translation key mapping to convert camelCase to snake_case
        translation_key = TRANSLATION_KEY_MAP.get(sensor_key, sensor_key)
        description = SensorEntityDescription(
            key=sensor_key,
            translation_key=translation_key,
            name=None,  # Use translation system for entity name
            native_unit_of_measurement=sensor_config.get("native_unit_of_measurement"),
            device_class=sensor_config.get("device_class"),
            state_class=sensor_config.get("state_class"),
            icon=sensor_config.get("icon"),
            entity_category=sensor_config.get("entity_category"),
        )
        entities.append(ZendureLocalSensor(coordinator, description, name))

    # Dynamically create battery pack device sensors based on available pack data
    pack_count = 0
    if coordinator.data and "packData" in coordinator.data:
        pack_count = len(coordinator.data["packData"])
        _LOGGER.debug("Found %d battery pack(s) in coordinator data", pack_count)
    else:
        _LOGGER.debug(
            "No pack data available initially, sensors will be created when data becomes available"
        )

    for pack_index in range(pack_count):
        pack_number = pack_index + 1  # Human-readable pack numbers start at 1
        for sensor_key, sensor_config in PACK_SENSOR_TYPES.items():
            # Handle special case for pack state to avoid duplicate with main pack_state
            translation_key = f"pack_{sensor_key}"
            if sensor_key == "state":
                translation_key = "pack_battery_state"

            description = SensorEntityDescription(
                key=f"pack_{sensor_key}",
                translation_key=translation_key,
                name=None,  # Use translation system for entity name
                native_unit_of_measurement=sensor_config.get(
                    "native_unit_of_measurement"
                ),
                device_class=sensor_config.get("device_class"),
                state_class=sensor_config.get("state_class"),
                icon=sensor_config.get("icon"),
                entity_category=sensor_config.get("entity_category"),
            )
            entities.append(
                ZendureLocalBatterySensor(
                    coordinator,
                    description,
                    f"{name} Battery {pack_number}",
                    pack_index,
                )
            )

    # # Add Zendure action buttons
    # device_info = DeviceInfo(
    #     identifiers={(DOMAIN, "zendure_solarflow")},
    #     name="Solarflow 800",
    #     manufacturer="Zendure",
    #     model="Solarflow Hub",
    # )
    # buttons = [
    #     ZendureActionButton(hass, action, device_info) for action in ZENDURE_ACTIONS
    # ]
    # async_add_entities(buttons, update_before_add=False)

    async_add_entities(entities)
    _LOGGER.debug("Added %d ZendureLocalSensor entities", len(entities))


class ZendureLocalSensor(CoordinatorEntity[ZendureCoordinator], SensorEntity):
    """Representation of a Zendure Local Sensor (main/inverter)."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ZendureCoordinator,
        description: SensorEntityDescription,
        prefix: str,
    ) -> None:
        """Initialize a ZendureLocalSensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{prefix}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "zendure_solarflow")},
            name=prefix,
            manufacturer="Zendure",
            model="Solarflow Hub",
        )
        self._attr_native_value = None
        self._update_native_value()
        _LOGGER.debug("Initialized sensor: %s", description.key)

    def _handle_coordinator_update(self) -> None:
        self._update_native_value()
        super()._handle_coordinator_update()

    def _update_native_value(self) -> None:
        if not self.coordinator.data:
            self._attr_native_value = None
            return
        sensor_key = self.entity_description.key
        data = self.coordinator.data
        value_func = SENSOR_TYPES.get(sensor_key, {}).get("value_func")
        if value_func:
            try:
                value = value_func(data)
                _LOGGER.debug("Processed value for sensor %s: %s", sensor_key, value)
                self._attr_native_value = value
            except (KeyError, ValueError, TypeError) as e:
                _LOGGER.warning(
                    "Failed to process value for sensor %s: %s", sensor_key, e
                )
                self._attr_native_value = None
        else:
            _LOGGER.warning("No value function defined for sensor %s", sensor_key)
            self._attr_native_value = None


class ZendureLocalBatterySensor(CoordinatorEntity[ZendureCoordinator], SensorEntity):
    """Representation of a Zendure Local Battery Pack Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ZendureCoordinator,
        description: SensorEntityDescription,
        prefix: str,
        pack_index: int,
    ) -> None:
        """Initialize a ZendureLocalBatterySensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._pack_index = pack_index
        self._attr_unique_id = f"{prefix}_{description.key}"
        pack_number = pack_index + 1
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"zendure_pack{pack_number}")},
            name=prefix,
            manufacturer="Zendure",
            model="Battery Pack",
            via_device=(DOMAIN, "zendure_solarflow"),
        )
        self._attr_native_value = None
        self._update_native_value()
        _LOGGER.debug("Initialized battery sensor: %s", description.key)

    def _handle_coordinator_update(self) -> None:
        self._update_native_value()
        super()._handle_coordinator_update()

    def _update_native_value(self) -> None:
        data = self.coordinator.data
        if not data:
            self._attr_native_value = None
            return
        sensor_key = self.entity_description.key
        pack_data = data.get("packData", [])
        if self._pack_index is None or len(pack_data) <= self._pack_index:
            self._attr_native_value = None
            return
        pack_info = pack_data[self._pack_index]
        try:
            if sensor_key.endswith("_soc"):
                self._attr_native_value = pack_info.get("socLevel")
            elif sensor_key.endswith("_power"):
                self._attr_native_value = pack_info.get("power")
            elif sensor_key.endswith("_temp"):
                max_temp = pack_info.get("maxTemp")
                if max_temp is not None:
                    self._attr_native_value = (int(max_temp) - 2731) / 10.0
                else:
                    self._attr_native_value = None
            elif sensor_key.endswith("_voltage"):
                self._attr_native_value = pack_info.get("totalVol")
            elif sensor_key.endswith("_state"):
                state_value = pack_info.get("state")
                if state_value is not None:
                    state_map = {0: "standby", 1: "charging", 2: "discharging"}
                    self._attr_native_value = state_map.get(int(state_value), "unknown")
                else:
                    self._attr_native_value = None
            else:
                _LOGGER.warning("Unknown pack sensor type: %s", sensor_key)
                self._attr_native_value = None
        except (KeyError, ValueError, TypeError) as e:
            _LOGGER.warning("Failed to process pack sensor %s: %s", sensor_key, e)
            self._attr_native_value = None
