import asyncio
from custom_components.plant_tracker.PlantTrackerEntity import PlantTrackerEntity
from datetime import date
from datetime import timedelta


def test_planttrackerentity_initialization() -> None:
    """Test the initialization of the entity."""
    entity = PlantTrackerEntity(
        "test_plant",
        {
            "plant_name": "Test Plant",
            "last_watered": "2023-10-01",
            "last_fertilized": "2023-09-15",
            "watering_interval": 14,
            "watering_postponed": 0,
            "days_since_watered": 1,
            "inside": True,
        },
    )
    assert entity._plant_id == "test_plant"
    assert entity._name == "plant_tracker_test_plant"
    assert entity._unique_id == "plant_tracker_test_plant"
    assert entity._plant_name == "Test Plant"
    assert entity._last_watered == "2023-10-01"
    assert entity._last_fertilized == "2023-09-15"
    assert entity._watering_interval == 14
    assert entity._watering_postponed == 0
    assert entity._days_since_watered == 1
    assert entity._inside is True
    assert entity._image == "test_plant"


def test_planttrackerentity_name() -> None:
    """Test the name property of the entity."""
    entity = PlantTrackerEntity(
        "test_plant",
        {
            "plant_name": "Test Plant",
            "last_watered": "2023-10-01",
            "last_fertilized": "2023-09-15",
            "watering_interval": 14,
            "watering_postponed": 0,
            "days_since_watered": 1,
            "inside": True,
        },
    )
    assert entity.name == "plant_tracker_test_plant"


def test_planttrackerentity_unique_id() -> None:
    """Test the unique ID property of the entity."""
    entity = PlantTrackerEntity(
        "test_plant",
        {
            "plant_name": "Test Plant",
            "last_watered": "2023-10-01",
            "last_fertilized": "2023-09-15",
            "watering_interval": 14,
            "watering_postponed": 0,
            "days_since_watered": 1,
            "inside": True,
        },
    )
    assert entity.unique_id == "plant_tracker_test_plant"


def test_planttrackerentity_state() -> None:
    """Test the state property of the entity."""
    entity = PlantTrackerEntity(
        "test_plant",
        {
            "plant_name": "Test Plant",
            "last_watered": "2023-10-01",
            "last_fertilized": "2023-09-15",
            "watering_interval": 14,
            "watering_postponed": 0,
            "days_since_watered": 1,
            "inside": True,
        },
    )
    assert entity.state == 0


def test_planttrackerentity_icon() -> None:
    """Test the icon property of the entity."""
    entity = PlantTrackerEntity(
        "test_plant",
        {
            "plant_name": "Test Plant",
            "last_watered": "2023-10-01",
            "last_fertilized": "2023-09-15",
            "watering_interval": 14,
            "watering_postponed": 0,
            "days_since_watered": 1,
            "inside": True,
        },
    )
    assert entity.icon == "mdi:flower"


def test_planttrackerentity_attributes() -> None:
    """Test the extra state attributes of the entity."""
    entity = PlantTrackerEntity(
        "test_plant",
        {
            "plant_name": "Test Plant",
            "last_watered": "2023-10-01",
            "last_fertilized": "2023-09-15",
            "watering_interval": 14,
            "watering_postponed": 0,
            "days_since_watered": 1,
            "inside": True,
        },
    )
    attributes = entity.extra_state_attributes
    assert attributes["plant_name"] == "Test Plant"
    assert attributes["last_watered"] == "2023-10-01"
    assert attributes["last_fertilized"] == "2023-09-15"
    assert attributes["watering_interval"] == 14
    assert attributes["watering_postponed"] == 0
    assert attributes["days_since_watered"] == 1
    assert attributes["inside"] is True
    assert attributes["image"] == "test_plant"


def test_planttrackerentity_update() -> None:
    """Test the async_update method of the entity."""
    entity = PlantTrackerEntity(
        "test_plant",
        {
            "plant_name": "Test Plant",
            "last_watered": "2023-10-01",
            "last_fertilized": "2023-09-15",
            "watering_interval": 14,
            "watering_postponed": 0,
            "days_since_watered": 1,
            "inside": True,
        },
    )
    # Simulate an update
    asyncio.run(entity.async_update())
    # Check if the state is still 0 after update
    assert entity.state == 0


def test_planttrackerentity_update_days_since_watered() -> None:
    """Test the async_update_days_since_last_watered method of the entity."""
    today_str = date.today().strftime("%Y-%m-%d")
    entity = PlantTrackerEntity(
        "test_plant",
        {
            "plant_name": "Test Plant",
            "last_watered": today_str,
            "last_fertilized": "2023-09-15",
            "watering_interval": 14,
            "watering_postponed": 0,
            "days_since_watered": 1,
            "inside": True,
        },
    )
    # Simulate an update of days since last watered
    asyncio.run(entity.async_update_days_since_last_watered())
    # Check if the state is still 0 after update
    assert entity.state == 3

    # Simulate a date 13 days ago
    date_13_days_ago = (date.today() - timedelta(days=13)).strftime("%Y-%m-%d")
    entity._last_watered = date_13_days_ago
    asyncio.run(entity.async_update_days_since_last_watered())
    assert entity.state == 2

    # Simulate a date 15 days ago
    date_15_days_ago = (date.today() - timedelta(days=15)).strftime("%Y-%m-%d")
    entity._last_watered = date_15_days_ago
    asyncio.run(entity.async_update_days_since_last_watered())
    assert entity.state == 0

    # Simulate a date 15 days ago + postponed watering
    entity._watering_postponed = 2
    entity._last_watered = date_15_days_ago
    asyncio.run(entity.async_update_days_since_last_watered())
    assert entity.state == 1

    # Simulate a date error
    entity._last_watered = "invalid-date"
    asyncio.run(entity.async_update_days_since_last_watered())
    assert entity.state == 0
