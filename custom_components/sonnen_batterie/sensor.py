"""  Sonnen Batterie sensor platform """
import logging
from datetime import timedelta
from typing import Callable, Optional

import sonnen_api_v2
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_IP_ADDRESS,
    CONF_SCAN_INTERVAL
)

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import HomeAssistantType, ConfigType, DiscoveryInfoType

from sonnen_api_v2 import Sonnen
from . import DOMAIN

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_SCAN_INTERVAL): cv.positive_int
    }
)

SCAN_INTERVAL = timedelta(seconds=5)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistantType,
        config: ConfigType,
        async_add_entities: Callable,
        discovery_info: Optional[DiscoveryInfoType] = None) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    data = Sonnen(config.get(CONF_IP_ADDRESS),
                  config.get(CONF_IP_ADDRESS),
                  logger=_LOGGER)
    await data.update()
    sensors = []

    async_add_entities(sensors, update_before_add=True)
