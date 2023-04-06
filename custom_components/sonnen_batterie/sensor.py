"""  Sonnen Batterie sensor platform """
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Callable, Optional

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorDeviceClass
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_IP_ADDRESS,
    CONF_SCAN_INTERVAL,
    PERCENTAGE,
)

from homeassistant.util import Throttle

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import HomeAssistantType, ConfigType, DiscoveryInfoType, StateType

from sonnen_api_v2 import Sonnen

# Import constants here
from .const import DOMAIN, BATTERY_STATUS, SOC

DEFAULT_SENSORS = {
    BATTERY_STATUS: ['Battery status', '', 'mdi:battery-check', ''],
    SOC: ['SOC', PERCENTAGE, 'mdi:mdi:battery-charging-60', SensorDeviceClass.BATTERY]

}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_SCAN_INTERVAL): cv.positive_int,
    }
)

SCAN_INTERVAL = timedelta(seconds=5)
NAME = 'Sonnen'

_LOGGER = logging.getLogger(__name__)


@Throttle(SCAN_INTERVAL)
async def update_data(sonnen: Sonnen):
    await sonnen.async_update()
    _LOGGER.info(f'{DOMAIN}: sensor data updated')


async def async_setup_platform(
        hass: HomeAssistantType,
        config: ConfigType,
        async_add_entities: Callable,
        discovery_info: Optional[DiscoveryInfoType] = None) -> None:
    """Set up the sensor platform."""

    data = Sonnen(config.get(CONF_IP_ADDRESS),
                  config.get(CONF_IP_ADDRESS),
                  logger=_LOGGER)
    await data.async_update()
    sensors = [SonnenSensor(data, sensor_key, values) for sensor_key, values in DEFAULT_SENSORS]

    async_add_entities(sensors, update_before_add=True)


class SonnenSensor(Entity):

    def __init__(self, data: Sonnen, sensor_key: str, sensor_details: list):
        super().__init__()
        self._sensor_key = sensor_key
        self._name = f'{NAME} {sensor_details[0]}'
        self._unit = sensor_details[1]
        self._icon = sensor_details[2]
        self._device_class = sensor_details[3]
        self._data = data

        self._state = None
        self._last_updated = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def unit_of_measurement(self) -> str | None:
        return self._unit

    @property
    def icon(self) -> str | None:
        return self._icon

    @property
    def device_class(self) -> str | None:
        return self._device_class

    @property
    def sensor(self) -> str | None:
        return self._sensor_key

    @property
    def state(self) -> StateType:
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    async def async_update(self):
        await update_data(self._data)
        if self._sensor_key == SOC:
            self.state = self._data.u_soc()
        if self._sensor_key == BATTERY_STATUS:
            self.state = self._data.system_status()

        _LOGGER.info(f'Sensor {self._sensor_key} state: {self.state}')






