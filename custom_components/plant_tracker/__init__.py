"""Plant Tracker component for Home Assistant."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Plant Tracker component."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)
    await component.async_setup(config)
    return True
