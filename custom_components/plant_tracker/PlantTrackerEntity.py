"""Platform for sensor integration."""

from __future__ import annotations

import unicodedata
from typing import Any

from homeassistant.components.sensor import SensorEntity
from datetime import datetime


def remove_accents(input_str: str) -> str:
    """Remove accents from a string."""
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


class PlantTrackerEntity(SensorEntity):
    """Representation of a plant tracker sensor."""

    def __init__(self, plant_id: str, data: dict[str, Any], config_entry) -> None:
        """Initialize the sensor."""
        self._plant_id = plant_id
        self._config_entry = config_entry
        self._name = f"plant_tracker_{plant_id}"
        self._unique_id = self._name

        # Load data
        self._plant_name = data.get("plant_name", plant_id)
        self._last_watered = data.get("last_watered", "Unknown")
        self._last_fertilized = data.get("last_fertilized", "Unknown")
        self._watering_interval = data.get("watering_interval", 14)
        self._watering_postponed = data.get("watering_postponed", 0)
        self._days_since_watered = data.get("days_since_watered", 0)
        self._inside = data.get("inside", True)
        image_name = remove_accents(plant_id).lower().replace(" ", "_")
        self._image = f"plant_tracker.{image_name}"
        self._state = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "plant_name": self._plant_name,
            "last_watered": self._last_watered,
            "last_fertilized": self._last_fertilized,
            "watering_interval": self._watering_interval,
            "watering_postponed": self._watering_postponed,
            "days_since_watered": self._days_since_watered,
            "inside": self._inside,
            "image": self._image,
        }

    async def async_update(self) -> None:
        """Update the sensor data."""
        await self.async_update_days_since_last_watered()

    async def async_update_days_since_last_watered(self):
        """Calculate and update days since last watered."""
        if self._last_watered:
            try:
                last_watered_date = datetime.strptime(
                    self._last_watered, "%Y-%m-%d"
                ).date()
                self._days_since_watered = (
                    datetime.today().date() - last_watered_date
                ).days
            except ValueError:
                self._days_since_watered = 0
        else:
            self._days_since_watered = 0

        if self._days_since_watered == 0:
            self._state = 3
        elif self._days_since_watered <= int(self._watering_interval) + int(
            self._watering_postponed
        ):
            self._state = 2
        else:
            self._state = 0
