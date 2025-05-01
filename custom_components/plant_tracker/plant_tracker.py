"""Platform for sensor integration."""

from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers import config_validation as cv
import unicodedata
import voluptuous as vol
from .const import DOMAIN
from typing import Any


def remove_accents(input_str: str) -> str:
    """Remove accents from a string."""
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


# This is the sensor platform for the Plant Tracker integration
async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    entity = PlantTrackerEntity(config["name"])
    async_add_entities([entity])

    # Add the entity to hass.data with the correct entity_id
    hass.data[DOMAIN][entity.entity_id] = entity

    async def handle_update_service(call):
        """Handle the service call to update the entity's attributes."""
        entity_id = call.data["entity_id"]
        entity = hass.states.get(entity_id)
        if entity is None:
            return

        # Get the entity object
        entity_obj = hass.data[DOMAIN].get(entity_id)
        if entity_obj is None:
            return

        # Update the attributes
        if "last_watered" in call.data:
            entity_obj._last_watered = call.data["last_watered"]
        if "last_fertilized" in call.data:
            entity_obj._last_fertilized = call.data["last_fertilized"]
        if "watering_interval" in call.data:
            entity_obj._watering_interval = call.data["watering_interval"]
        if "watering_postponed" in call.data:
            entity_obj._watering_postponed = call.data["watering_postponed"]

        # Schedule an update
        entity_obj.async_schedule_update_ha_state(True)

    # Register the service
    hass.services.async_register(DOMAIN, "update_plant", handle_update_service)


class PlantTrackerEntity(RestoreEntity):
    """Representation of a Ping Binary sensor."""

    def __init__(self, name: str) -> None:
        """Initialize."""
        self._name = name
        self._friendly_name = remove_accents(name).lower()
        self._unique_id = f"plant_tracker_{self._friendly_name}"
        self._state = 0
        self._last_watered = "Unknown"
        self._last_fertilized = "Unknown"
        self._watering_interval = 14
        self._watering_postponed = 0
        self._days_since_watered = 0
        self._interior = True
        self._image = f"plant_tracker.{self._friendly_name.replace(' ', '_')}"

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the ICMP checo request."""
        return {
            "last_watered": self._last_watered,
            "last_fertilized": self._last_fertilized,
            "watering_interval": self._watering_interval,
            "watering_postponed": self._watering_postponed,
            "days_since_watered": self._days_since_watered,
            "interior": self._interior,
            "image": self._image,
        }

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the entity."""
        return self._unique_id

    async def async_update(self) -> None:
        """Get the latest data."""

    async def async_added_to_hass(self):
        """Restore previous state on restart to avoid blocking startup."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._state = last_state.state
            self._last_watered = last_state.attributes.get(
                "last_watered", self._last_watered
            )
            self._last_fertilized = last_state.attributes.get(
                "last_fertilized", self._last_fertilized
            )
            self._watering_interval = last_state.attributes.get(
                "watering_interval", self._watering_interval
            )
            self._watering_postponed = last_state.attributes.get(
                "watering_postponed", self._watering_postponed
            )
            self._days_since_watered = last_state.attributes.get(
                "days_since_watered", self._days_since_watered
            )
            self._interior = last_state.attributes.get("interior", self._interior)
            self._image = last_state.attributes.get("image", self._image)
