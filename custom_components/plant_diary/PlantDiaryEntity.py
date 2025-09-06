"""Plant Diary Entity."""

from datetime import date, datetime
from typing import Any

from propcache.api import cached_property

from homeassistant.components.sensor import SensorEntity
from homeassistant.util.dt import now

from .const import DOMAIN


class PlantDiaryEntity(SensorEntity):
    """Representation of a plant diary sensor."""

    def __init__(self, plant_id: str, data: dict[str, Any]) -> None:
        """Initialize the sensor."""
        self._plant_id: str = plant_id
        self._name: str = f"{DOMAIN}_{plant_id}"
        self._unique_id: str = self._name
        self._plant_name: str = data.get("plant_name", plant_id)
        self._last_watered: date | None = None
        self._last_fertilized: date | None = None
        self._watering_interval: int = 14
        self._watering_postponed: int = 0
        self._days_since_watered: int = 0
        self._inside: bool = True
        self._image: str = ""
        self._state: int = 0

        # Load data
        self.update_from_dict(data)

        # Calculate initial state
        self.update_days_since_last_watered()

    @cached_property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @cached_property
    def unique_id(self) -> str | None:
        """Return a unique ID for this entity."""
        return self._unique_id

    @property  # type: ignore[override]
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._state

    @cached_property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:flower"

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """Update entity attributes from a dictionary."""
        if "last_watered" in data:
            self._last_watered: date | None = self._parse_date(data["last_watered"])
        if "last_fertilized" in data:
            self._last_fertilized: date | None = self._parse_date(
                data["last_fertilized"]
            )
        if "watering_interval" in data:
            self._watering_interval: int = self._parse_int(data["watering_interval"])
        if "watering_postponed" in data:
            self._watering_postponed: int = self._parse_int(data["watering_postponed"])
        if "inside" in data:
            self._inside = bool(data["inside"])
        if "plant_name" in data:
            self._plant_name: str = data["plant_name"]
        if "image" in data:
            self._image: str = data["image"]

    @property  # type: ignore[override]
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "plant_name": self._plant_name,
            "last_watered": self._last_watered.isoformat()
            if self._last_watered
            else "Unknown",
            "last_fertilized": self._last_fertilized.isoformat()
            if self._last_fertilized
            else "Unknown",
            "watering_interval": self._watering_interval,
            "watering_postponed": self._watering_postponed,
            "days_since_watered": self._days_since_watered,
            "inside": self._inside,
            "image": self._image,
        }

    async def async_update(self) -> None:
        """Update the sensor data."""
        self.update_days_since_last_watered()

    def update_days_since_last_watered(self) -> None:
        """Calculate and update days since last watered."""
        if self._last_watered is None:
            self._days_since_watered = 0
            self._state = 0
        else:
            self._days_since_watered = (now().date() - self._last_watered).days

            if self._days_since_watered == 0:
                self._state = 3
            elif self._days_since_watered < self._watering_interval:
                self._state = 2
            elif (
                self._days_since_watered
                < self._watering_interval + self._watering_postponed
            ):
                self._state = 1
            else:
                self._state = 0

        # Clear cached native_value
        self.__dict__.pop("native_value", None)

    def _parse_date(self, value: Any) -> date | None:
        """Parse a date from various formats."""
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return None
        return None

    def _parse_int(self, value: Any, default: int = 0) -> int:
        """Parse an integer from various formats."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
