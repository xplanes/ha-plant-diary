"""Plant Tracker component for Home Assistant."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLANT_TRACKER_MANAGER
from .PlantTrackerManager import PlantTrackerManager


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration from configuration.yaml (not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from a config entry."""

    # Initialize the DOMAIN in hass.data if it doesn't exist
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Initialize the PlantTrackerManager and store it in hass.data
    # with the entry ID as the key
    manager = PlantTrackerManager(hass, entry)
    await manager.async_init()

    hass.data[DOMAIN][PLANT_TRACKER_MANAGER] = manager

    # Set up the sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload the plant tracker manager and its entities."""

    manager: PlantTrackerManager = hass.data[DOMAIN][PLANT_TRACKER_MANAGER]
    await manager.async_unload()

    return True
