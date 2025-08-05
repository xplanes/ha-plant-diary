# Test cases for the async_setup_entry function in the Plant Diary custom component for Home Assistant
from typing import Iterable
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from config.custom_components.plant_diary.const import DOMAIN, PLANT_DIARY_MANAGER
from config.custom_components.plant_diary.sensor import async_setup_entry


@pytest.mark.asyncio
async def test_async_setup_entry_calls_restore(caplog):
    """Test that async_setup_entry calls restore_and_add_entities."""
    hass = MagicMock(spec=HomeAssistant)
    entry = MagicMock(spec=ConfigEntry)

    # Prepare mock manager and inject it into hass.data
    mock_manager = MagicMock()
    mock_manager.restore_and_add_entities = AsyncMock()

    hass.data = {DOMAIN: {PLANT_DIARY_MANAGER: mock_manager}}

    # Define a dummy async_add_entities callback
    def add_entities(
        entities: Iterable[Entity], update_before_add: bool = False
    ) -> None:
        pass  # optional: assert entities, etc.

    hass.async_add_entities = add_entities

    await async_setup_entry(hass, entry, hass.async_add_entities)

    mock_manager.restore_and_add_entities.assert_awaited_once_with(add_entities)

    hass.data[DOMAIN].pop(PLANT_DIARY_MANAGER)
    caplog.clear()
    await async_setup_entry(hass, entry, hass.async_add_entities)
    assert "PlantDiaryManager not found in hass.data" in caplog.text
