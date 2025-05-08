"""Plant Tracker component for Home Assistant."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.entity_registry as er

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Plant Tracker component.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        config (ConfigType): The configuration dictionary.

    Returns:
        bool: True if the setup was successful, False otherwise.
    """
    entity_registry = er.async_get(hass)

    # Filtrar entidades con dominio plant_tracker
    plant_entities = [
        entry.original_name
        for entry in entity_registry.entities.values()
        if entry.domain == DOMAIN
    ]

    # Si no hay entidades, no se configura el componente
    if not plant_entities:
        _LOGGER.warning("No plant entities found in the entity registry")
        return False

    # Configurar el componente con las entidades encontradas
    config[DOMAIN] = [
        {"platform": DOMAIN, "name": plant_name} for plant_name in plant_entities
    ]

    # Set up the Plant Tracker component.
    component = EntityComponent(_LOGGER, DOMAIN, hass)
    await component.async_setup(config)

    # Initialize the DOMAIN in hass.data
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    return True
