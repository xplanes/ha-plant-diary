"""Module for managing the Plant Tracker component."""

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from functools import partial
from .PlantTrackerEntity import PlantTrackerEntity
from .const import DOMAIN


class PlantTrackerManager:
    """Manager class to handle multiple PlantTrackerEntity instances."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.entities = {}
        self._async_add_entities = None
        self._listeners = {}

    async def async_init(self):
        await self.async_register_services()

    async def restore_and_add_entities(self, async_add_entities: AddEntitiesCallback):
        self._async_add_entities = async_add_entities
        plants_data = self.entry.data.get("plants", {})

        entities = {}
        for plant_id, plant_data in plants_data.items():
            entity = PlantTrackerEntity(plant_id, plant_data, self.entry)
            entities[plant_id] = entity

            remove_listener = async_track_time_change(
                self.hass,
                partial(self._update_entity_midnight, entity),
                hour=0,
                minute=0,
                second=0,
            )
            self._listeners[plant_id] = remove_listener

        self.entities = entities
        async_add_entities(list(entities.values()))

    async def async_register_services(self):
        hass = self.hass

        async def handle_create_plant(call: ServiceCall):
            await self.create_plant(call.data)

        async def handle_update_plant(call: ServiceCall):
            await self.update_plant(call.data)

        async def handle_delete_plant(call: ServiceCall):
            await self.delete_plant(call.data["plant_id"])

        async def handle_update_days_since_last_watered(call: ServiceCall):
            plant_id = call.data["plant_id"]
            entity = self.entities.get(plant_id)
            if entity:
                await entity.async_update_days_since_last_watered()

        hass.services.async_register(DOMAIN, "create_plant", handle_create_plant)
        hass.services.async_register(DOMAIN, "update_plant", handle_update_plant)
        hass.services.async_register(DOMAIN, "delete_plant", handle_delete_plant)
        hass.services.async_register(
            DOMAIN, "update_days_since_watered", handle_update_days_since_last_watered
        )

    async def create_plant(self, data: dict):
        """Create a new PlantTrackerEntity and add it."""
        plant_id = data["plant_name"]
        plant_data = {
            "plant_name": data.get("plant_name", plant_id),
            "last_watered": data.get("last_watered", "Unknown"),
            "last_fertilized": data.get("last_fertilized", "Unknown"),
            "watering_interval": data.get("watering_interval", 14),
            "watering_postponed": data.get("watering_postponed", 0),
            "inside": data.get("inside", True),
            "image": data.get("image", f"plant_tracker.{plant_id}"),
        }

        entity = PlantTrackerEntity(plant_id, plant_data, self.entry)
        self.entities[plant_id] = entity

        if self._async_add_entities:
            self._async_add_entities([entity])

        # Registrar actualización diaria
        async def midnight_callback(now):
            await entity.async_update_days_since_last_watered()

        async_track_time_change(
            self.hass, midnight_callback, hour=0, minute=0, second=0
        )

        # Update the days since last watered
        await entity.async_update()

        # Guardar en la entrada de configuración
        self.update_all_plants(plant_id, entity.extra_state_attributes)

        # Force update the entity state
        entity.async_schedule_update_ha_state(True)

    async def update_plant(self, data: dict):
        """Update an existing plant."""
        plant_id = data["plant_id"]
        entity = self.entities.get(plant_id)
        if not entity:
            return

        if "last_watered" in data:
            entity._last_watered = data["last_watered"]
        if "last_fertilized" in data:
            entity._last_fertilized = data["last_fertilized"]
        if "watering_interval" in data:
            entity._watering_interval = data["watering_interval"]
        if "watering_postponed" in data:
            entity._watering_postponed = data["watering_postponed"]
        if "inside" in data:
            entity._inside = data["inside"]
        if "plant_name" in data:
            entity._plant_name = data["plant_name"]
        if "image" in data:
            entity._image = data["image"]

        # Update the days since last watered
        await entity.async_update()

        # Guardar en la entrada de configuración
        self.update_all_plants(plant_id, entity.extra_state_attributes)

        # Force update the entity state
        entity.async_schedule_update_ha_state(True)

    async def delete_plant(self, plant_id: str):
        """Delete a plant tracker entity."""
        entity = self.entities.get(plant_id)
        if not entity:
            return

        # Remove from config entry
        self.update_all_plants(plant_id, None)

        # Stop listener if exists
        remove_listener = self._listeners.pop(plant_id, None)
        if remove_listener:
            remove_listener()

        # Remove the entity from Home Assistant
        await entity.async_remove()

        # Remove from the entities dictionary
        del self.entities[plant_id]

    def update_all_plants(self, plant_id: str, plant_data: dict):
        """Update all plants in the config entry."""
        raw_plants = dict(self.entry.data.get("plants", {}))
        if isinstance(raw_plants, dict):
            all_plants = dict(raw_plants)
        else:
            all_plants = {}

        if plant_data is None:
            del all_plants[plant_id]
        else:
            all_plants[plant_id] = plant_data

        self.hass.config_entries.async_update_entry(
            self.entry, data={"plants": all_plants}
        )

    async def _update_entity_midnight(self, entity: PlantTrackerEntity, now):
        await entity.async_update()
