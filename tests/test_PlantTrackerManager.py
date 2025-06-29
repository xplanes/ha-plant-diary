# Test for PlantTrackerManager
import pytest
from unittest.mock import MagicMock, patch, ANY, AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from custom_components.plant_tracker.PlantTrackerManager import PlantTrackerManager
from custom_components.plant_tracker.const import DOMAIN
from typing import Iterable
from homeassistant.helpers.entity import Entity
from homeassistant.core import ServiceCall


def create_test_hass():
    """Create a reusable Home Assistant instance with minimal mocks."""
    hass = MagicMock(spec=HomeAssistant)
    hass.async_create_task = AsyncMock()
    hass._added_entities = []

    # Dictionary to store registered service handlers
    registered_services = {}

    def async_register(domain, service, handler, *args, **kwargs):
        if domain not in registered_services:
            registered_services[domain] = {}
        registered_services[domain][service] = handler

    async def async_call(domain, service, data, blocking=False, context=None):
        handler = registered_services[domain][service]
        await handler(ServiceCall(hass, domain, service, data, context))

    # Set up mock services object
    hass.services = MagicMock()
    hass.services.async_register = async_register
    hass.services.async_call = async_call
    hass.services.has_service = lambda d, s: s in registered_services.get(d, {})

    def add_entities(
        entities: Iterable[Entity], update_before_add: bool = False
    ) -> None:
        """Mock synchronous add_entities (follows the protocol)."""
        for entity in entities:
            entity.hass = hass
            hass._added_entities.append(entity)
            # async_added_to_hass must be scheduled manually
            if hasattr(entity, "async_added_to_hass"):
                hass.async_create_task(entity.async_added_to_hass())

    hass.async_add_entities = add_entities

    return hass


def test_planttrackermanager_initialization() -> None:
    """Test the initialization of the manager."""
    hass = MagicMock(spec=HomeAssistant)
    entry = MagicMock(spec=ConfigEntry)
    manager = PlantTrackerManager(hass, entry)
    assert manager is not None
    assert manager.hass == hass
    assert manager.entry == entry
    assert manager.entities == {}
    assert manager._async_add_entities is None
    assert manager._midnight_listener is None


@pytest.mark.asyncio
@patch("custom_components.plant_tracker.PlantTrackerManager.async_track_time_change")
async def test_planttrackermanager_async_init(mock_async_track_time_change) -> None:
    """Test the async initialization of the manager."""
    hass = MagicMock(spec=HomeAssistant)

    # Add mock for hass.services.async_register
    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    entry = MagicMock(spec=ConfigEntry)

    manager = PlantTrackerManager(hass, entry)
    await manager.async_init()
    # Check if the method runs without errors
    assert manager is not None
    # Verify that the service was registered
    hass.services.async_register.assert_any_call(
        DOMAIN,
        "create_plant",
        ANY,
    )
    hass.services.async_register.assert_any_call(
        DOMAIN,
        "update_plant",
        ANY,
    )
    hass.services.async_register.assert_any_call(
        DOMAIN,
        "delete_plant",
        ANY,
    )
    hass.services.async_register.assert_any_call(
        DOMAIN,
        "update_days_since_watered",
        ANY,
    )
    assert manager._midnight_listener is not None
    mock_async_track_time_change.assert_called_once_with(
        hass,
        manager._update_all_days_since_last_watered,
        hour=0,
        minute=0,
        second=0,
    )

    assert manager._midnight_listener == mock_async_track_time_change.return_value


@pytest.mark.asyncio
@patch("custom_components.plant_tracker.PlantTrackerManager.async_track_time_change")
async def test_service_handlers_register_and_call(mock_async_track_time_change):
    hass = create_test_hass()
    manager = PlantTrackerManager(hass, MagicMock())

    # Patch the methods that the services would call
    manager.create_plant = AsyncMock()
    manager.update_plant = AsyncMock()
    manager.delete_plant = AsyncMock()
    manager._update_all_days_since_last_watered = AsyncMock()

    # Patch async_track_time_change to avoid lingering timers
    with patch("homeassistant.helpers.event.async_track_time_change"):
        await manager.async_register_services()

    # Simulate service calls
    await hass.services.async_call(
        DOMAIN,
        "create_plant",
        {"plant_id": "test_plant"},
        blocking=True,
    )
    manager.create_plant.assert_called_once()

    await hass.services.async_call(
        DOMAIN,
        "update_plant",
        {"plant_id": "test_plant", "new_name": "Updated"},
        blocking=True,
    )
    manager.update_plant.assert_called_once()

    await hass.services.async_call(
        DOMAIN,
        "delete_plant",
        {"plant_id": "test_plant"},
        blocking=True,
    )
    manager.delete_plant.assert_called_once()

    await hass.services.async_call(
        DOMAIN,
        "update_days_since_watered",
        {},
        blocking=True,
    )
    manager._update_all_days_since_last_watered.assert_called_once()


@pytest.mark.asyncio
async def test_planttrackermanager_restore_and_add_entities() -> None:
    """Test restoring and adding entities."""
    hass = create_test_hass()
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        "plants": {
            "test_plant": {
                "plant_name": "Test Plant",
                "last_watered": "2023-10-01",
                "last_fertilized": "2023-09-15",
                "watering_interval": 14,
                "watering_postponed": 0,
                "days_since_watered": 1,
                "inside": True,
            }
        }
    }
    manager = PlantTrackerManager(hass, entry)
    await manager.restore_and_add_entities(hass.async_add_entities)

    assert manager._async_add_entities is not None
    assert len(manager.entities) == 1
    assert "test_plant" in manager.entities


@pytest.mark.asyncio
async def test_planttrackermanager_create_plant() -> None:
    """Test creating a new plant."""
    hass = create_test_hass()
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {}
    manager = PlantTrackerManager(hass, entry)
    await manager.restore_and_add_entities(hass.async_add_entities)
    data = {
        "plant_name": "New Plant",
        "last_watered": "2023-10-01",
        "last_fertilized": "2023-09-15",
        "watering_interval": 14,
        "watering_postponed": 0,
        "inside": True,
    }
    await manager.create_plant(data)
    assert "New Plant" in manager.entities
    assert manager.entities["New Plant"]._plant_name == "New Plant"


@pytest.mark.asyncio
async def test_planttrackermanager_update_plant() -> None:
    """Test updating an existing plant."""
    hass = create_test_hass()
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        "plants": {
            "Existing Plant": {
                "plant_name": "Existing Plant",
                "last_watered": "2023-10-01",
                "last_fertilized": "2023-09-15",
                "watering_interval": 14,
                "watering_postponed": 0,
                "days_since_watered": 1,
                "inside": True,
            }
        }
    }
    manager = PlantTrackerManager(hass, entry)
    await manager.restore_and_add_entities(hass.async_add_entities)
    updated_data = {
        "plant_id": "Existing Plant",
        "last_watered": "2023-10-02",
        "last_fertilized": "2023-10-02",
        "watering_interval": 7,
        "watering_postponed": 0,
        "inside": False,
        "plant_name": "Updated Plant",
        "image": "Existing Plant",
    }
    await manager.update_plant(updated_data)
    updatedPlant = manager.entities["Existing Plant"]
    assert updatedPlant._last_watered.isoformat() == "2023-10-02"
    assert updatedPlant._last_fertilized.isoformat() == "2023-10-02"
    assert updatedPlant._watering_interval == 7
    assert updatedPlant._watering_postponed == 0
    assert updatedPlant._inside is False
    assert updatedPlant._plant_name == "Updated Plant"
    assert updatedPlant._image == "Existing Plant"

    # Test updating with a non-existing plant
    updated_data = {"plant_id": "Non-Existing Plant"}
    await manager.update_plant(updated_data)


@patch("homeassistant.helpers.entity_registry.async_get")
@pytest.mark.asyncio
async def test_planttrackermanager_delete_plant(mock_er_async_get) -> None:
    """Test deleting an existing plant."""
    hass = create_test_hass()
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        "plants": {
            "Plant to Delete": {
                "plant_name": "Plant to Delete",
                "last_watered": "2023-10-01",
                "last_fertilized": "2023-09-15",
                "watering_interval": 14,
                "watering_postponed": 0,
                "days_since_watered": 1,
                "inside": True,
            }
        }
    }
    manager = PlantTrackerManager(hass, entry)
    await manager.restore_and_add_entities(hass.async_add_entities)

    # Mock the entity to be deleted
    entity = manager.entities["Plant to Delete"]
    entity.async_remove = AsyncMock()

    # Mock the entity registry
    fake_registry = MagicMock()
    fake_entry = MagicMock()
    fake_entry.entity_id = "plant_tracker.plant_to_delete"

    fake_registry.async_get.return_value = fake_entry
    fake_registry.async_remove = MagicMock()
    mock_er_async_get.return_value = fake_registry

    # Call the delete method
    await manager.delete_plant("Plant to Delete")

    assert "Plant to Delete" not in manager.entities
    fake_registry.async_remove.assert_called_once_with("plant_tracker.plant_to_delete")

    # Call the delete method to a non-existing plant
    await manager.delete_plant("Plant to Delete")


@pytest.mark.asyncio
async def test_planttrackermanager_update_days_since_watered() -> None:
    """Test updating days since last watered for all plants."""
    hass = create_test_hass()
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        "plants": {
            "Plant to Update": {
                "plant_name": "Plant to Update",
                "last_watered": "2023-10-01",
                "last_fertilized": "2023-09-15",
                "watering_interval": 14,
                "watering_postponed": 0,
                "days_since_watered": 1,
                "inside": True,
            }
        }
    }
    manager = PlantTrackerManager(hass, entry)
    await manager.restore_and_add_entities(hass.async_add_entities)
    await manager._update_all_days_since_last_watered(None)
    assert manager.entities["Plant to Update"]._days_since_watered > 1


@patch("homeassistant.helpers.entity_registry.async_get")
@pytest.mark.asyncio
async def test_planttrackermanager_async_unload(mock_er_async_get) -> None:
    """Test unloading the manager."""
    hass = create_test_hass()
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        "plants": {
            "Plant to Delete": {
                "plant_name": "Plant to Delete",
                "last_watered": "2023-10-01",
                "last_fertilized": "2023-09-15",
                "watering_interval": 14,
                "watering_postponed": 0,
                "days_since_watered": 1,
                "inside": True,
            }
        }
    }
    manager = PlantTrackerManager(hass, entry)
    await manager.restore_and_add_entities(hass.async_add_entities)

    # Mock the entity to be deleted
    entity = manager.entities["Plant to Delete"]
    entity.async_remove = AsyncMock()

    # Mock the entity registry
    fake_registry = MagicMock()
    fake_entry = MagicMock()
    fake_entry.entity_id = "plant_tracker.plant_to_delete"

    fake_registry.async_get.return_value = fake_entry
    fake_registry.async_remove = MagicMock()
    mock_er_async_get.return_value = fake_registry

    # Mock the unload method
    await manager.async_unload()
    assert manager._midnight_listener is None
    assert manager._async_add_entities is None
    assert len(manager.entities) == 0
