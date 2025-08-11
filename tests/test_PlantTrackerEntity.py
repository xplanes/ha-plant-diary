# Test cases for PlantDiaryEntity class in the Plant Diary custom component for Home Assistant
from datetime import date, timedelta

import pytest

from custom_components.plant_diary.PlantDiaryEntity import PlantDiaryEntity


@pytest.mark.asyncio
async def test_plantdiaryentity_initialization() -> None:
    """Test the initialization of the entity."""
    date_1_days_ago = (date.today() - timedelta(days=1)).isoformat()

    entity = PlantDiaryEntity(
        "test_plant",
        {
            "plant_name": "Test Plant",
            "last_watered": date_1_days_ago,
            "last_fertilized": date_1_days_ago,
            "watering_interval": 14,
            "watering_postponed": 0,
            "days_since_watered": 1,
            "inside": True,
        },
    )
    await entity.async_update()  # Simulate async update
    assert entity._plant_id == "test_plant"
    assert entity._name == "plant_diary_test_plant"
    assert entity._unique_id == "plant_diary_test_plant"
    assert entity._plant_name == "Test Plant"
    assert (
        entity._last_watered is not None
        and entity._last_watered.isoformat() == date_1_days_ago
    )
    assert (
        entity._last_fertilized is not None
        and entity._last_fertilized.isoformat() == date_1_days_ago
    )
    assert entity._watering_interval == 14
    assert entity._watering_postponed == 0
    assert entity._days_since_watered == 1
    assert entity._inside is True
    assert entity._image == ""


def test_plantdiaryentity_name() -> None:
    """Test the name property of the entity."""
    entity = PlantDiaryEntity(
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
    assert entity.name == "plant_diary_test_plant"


def test_plantdiaryentity_unique_id() -> None:
    """Test the unique ID property of the entity."""
    entity = PlantDiaryEntity(
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
    assert entity.unique_id == "plant_diary_test_plant"


def test_plantdiaryentity_state() -> None:
    """Test the state property of the entity."""
    entity = PlantDiaryEntity(
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
    assert entity.native_value == 0


def test_plantdiaryentity_icon() -> None:
    """Test the icon property of the entity."""
    entity = PlantDiaryEntity(
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


@pytest.mark.asyncio
async def test_plantdiaryentity_attributes() -> None:
    """Test the extra state attributes of the entity."""
    date_1_days_ago = (date.today() - timedelta(days=1)).isoformat()
    entity = PlantDiaryEntity(
        "test_plant",
        {
            "plant_name": "Test Plant",
            "last_watered": date_1_days_ago,
            "last_fertilized": date_1_days_ago,
            "watering_interval": 14,
            "watering_postponed": 0,
            "days_since_watered": 1,
            "inside": True,
        },
    )
    await entity.async_update()
    attributes = entity.extra_state_attributes
    assert attributes["plant_name"] == "Test Plant"
    assert attributes["last_watered"] == date_1_days_ago
    assert attributes["last_fertilized"] == date_1_days_ago
    assert attributes["watering_interval"] == 14
    assert attributes["watering_postponed"] == 0
    assert attributes["days_since_watered"] == 1
    assert attributes["inside"] is True
    assert attributes["image"] == ""


@pytest.mark.asyncio
async def test_plantdiaryentity_update() -> None:
    """Test the async_update method of the entity."""
    entity = PlantDiaryEntity(
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
    await entity.async_update()
    # Check if the state is still 0 after update
    assert entity.native_value == 0


@pytest.mark.asyncio
async def test_plantdiaryentity_update_days_since_watered() -> None:
    """Test the update_days_since_last_watered method of the entity."""
    today_str = date.today().strftime("%Y-%m-%d")
    entity = PlantDiaryEntity(
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
    entity.update_days_since_last_watered()
    # Check if the state is still 0 after update
    assert entity.native_value == 3

    # Simulate a date 13 days ago
    date_13_days_ago = date.today() - timedelta(days=13)
    entity._last_watered = date_13_days_ago
    entity.update_days_since_last_watered()
    assert entity.native_value == 2

    # Simulate a date 15 days ago
    date_15_days_ago = date.today() - timedelta(days=15)
    entity._last_watered = date_15_days_ago
    entity.update_days_since_last_watered()
    assert entity.native_value == 0

    # Simulate a date 15 days ago + postponed watering
    entity._watering_postponed = 2
    entity._last_watered = date_15_days_ago
    entity.update_days_since_last_watered()
    assert entity.native_value == 1

    # Simulate a date error
    entity._last_watered = None
    entity.update_days_since_last_watered()
    assert entity.native_value == 0


def test_plantdiaryentity_parse_date() -> None:
    """Test the _parse_date method of the entity."""
    entity = PlantDiaryEntity(
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
    assert entity._parse_date("2023-10-01") == date(2023, 10, 1)
    assert entity._parse_date("invalid-date") is None
    assert entity._parse_date(None) is None
    assert entity._parse_date(12345) is None  # Non-string input should return None


def test_plantdiaryentity_clear_cache() -> None:
    """Test that the extra_state_attributes cache is cleared."""
    entity = PlantDiaryEntity(
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
    # Access extra_state_attributes to populate the cache
    _ = entity.extra_state_attributes
    # Clear the cache
    entity.__dict__.pop("extra_state_attributes", None)
    # Check if the cache is cleared
    assert "extra_state_attributes" not in entity.__dict__


def test_plantdiaryentity_parse_int() -> None:
    """Test the _parse_int method of the entity."""
    entity = PlantDiaryEntity(
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
    assert entity._parse_int("42") == 42
    assert entity._parse_int("invalid") == 0
    assert entity._parse_int(None) == 0
    assert entity._parse_int(100) == 100  # Integer input should return itself
    assert entity._parse_int(3.14) == 3  # Float input should return truncated integer
    assert entity._parse_int(True) == 1  # Boolean input should return 1
    assert entity._parse_int(False) == 0  # Boolean input should return 0
    assert entity._parse_int([]) == 0  # List input should return 0
    assert entity._parse_int({}) == 0  # Dict input should return 0
