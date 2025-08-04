"""Sensor platform for the Plant Diary custom component.

This module sets up the Plant Diary sensor platform and integrates it with Home Assistant.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PLANT_DIARY_MANAGER
from .PlantDiaryManager import PlantDiaryManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Plant Diary sensor platform from a config entry."""
    _LOGGER.debug("Setting up Plant Diary sensor platform")

    # Recuperar el manager desde hass.data
    manager: PlantDiaryManager = hass.data[DOMAIN].get(PLANT_DIARY_MANAGER)

    if manager:
        await manager.restore_and_add_entities(async_add_entities)
    else:
        _LOGGER.error("PlantDiaryManager not found in hass.data")
