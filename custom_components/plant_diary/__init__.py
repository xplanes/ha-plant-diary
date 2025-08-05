"""Plant Diary component for Home Assistant."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLANT_DIARY_MANAGER
from .PlantDiaryManager import PlantDiaryManager

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration from configuration.yaml (not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from a config entry."""

    # Initialize the DOMAIN in hass.data if it doesn't exist
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Initialize the PlantDiaryManager and store it in hass.data
    # with the entry ID as the key
    manager = PlantDiaryManager(hass, entry)
    await manager.async_init()

    hass.data[DOMAIN][PLANT_DIARY_MANAGER] = manager

    # Set up the sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload the plant diary manager and its entities."""

    # Unload the platforms (e.g., sensor)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    if unload_ok:
        # Cleanup manager
        manager: PlantDiaryManager = hass.data[DOMAIN].pop(PLANT_DIARY_MANAGER, None)
        if manager:
            await manager.async_unload()

        # Optionally remove the domain if empty
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle reloads of the config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
