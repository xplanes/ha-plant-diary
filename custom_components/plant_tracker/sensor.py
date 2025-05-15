import logging
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLANT_TRACKER_MANAGER
from .PlantTrackerManager import PlantTrackerManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Plant Tracker sensor platform from a config entry."""
    _LOGGER.debug("Setting up Plant Tracker sensor platform")

    # Recuperar el manager desde hass.data
    manager: PlantTrackerManager = hass.data[DOMAIN].get(PLANT_TRACKER_MANAGER)

    if manager:
        await manager.restore_and_add_entities(async_add_entities)
    else:
        _LOGGER.error("PlantTrackerManager not found in hass.data")
