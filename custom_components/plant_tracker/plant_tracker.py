"""Platform for sensor integration."""

from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.restore_state import RestoreEntity
import unicodedata

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

    async_add_entities([PlantTrackerEntity(config["name"])])


class PlantTrackerEntity(RestoreEntity):
    """Representation of a Ping Binary sensor."""

    def __init__(self, name: str) -> None:
        """Initialize."""
        self._name = remove_accents(name).lower()
        self._state = 0
        self._last_watered = "2023-10-02"
        self._last_fertilized = "2023-10-02"

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
        }

    async def async_update(self) -> None:
        """Get the latest data."""

    async def async_added_to_hass(self):
        """Restore previous state on restart to avoid blocking startup."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._state = last_state.state
            self._last_watered = last_state.attributes["last_watered"]
            self._last_fertilized = last_state.attributes["last_fertilized"]
