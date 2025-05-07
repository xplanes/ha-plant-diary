"""Plant Tracker component for Home Assistant."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    entity_registry = async_get_entity_registry(hass)

    # Filtrar entidades con dominio plant_tracker
    plant_entities = [
        entry.original_name
        for entry in entity_registry.entities.values()
        if entry.domain == DOMAIN
    ]

    # Si no hay entidades, no se configura el componente
    if not plant_entities:
        _LOGGER.warning("No plant entities found in the entity registry.")
        return False

    # Configurar el componente con las entidades encontradas
    config[DOMAIN] = [
        {"platform": DOMAIN, "name": plant_name} for plant_name in plant_entities
    ]

    """Set up the Plant Tracker component."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)
    await component.async_setup(config)

    # Initialize the DOMAIN in hass.data
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    return True
