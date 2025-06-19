import pytest
from unittest.mock import AsyncMock, MagicMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from custom_components.plant_tracker.const import DOMAIN, PLANT_TRACKER_MANAGER
from custom_components.plant_tracker.sensor import async_setup_entry
from typing import Iterable
from homeassistant.helpers.entity import Entity


@pytest.mark.asyncio
async def test_async_setup_entry_calls_restore(caplog):
    hass = MagicMock(spec=HomeAssistant)
    entry = MagicMock(spec=ConfigEntry)

    # Prepare mock manager and inject it into hass.data
    mock_manager = MagicMock()
    mock_manager.restore_and_add_entities = AsyncMock()

    hass.data = {DOMAIN: {PLANT_TRACKER_MANAGER: mock_manager}}

    # Define a dummy async_add_entities callback
    def add_entities(
        entities: Iterable[Entity], update_before_add: bool = False
    ) -> None:
        pass  # optional: assert entities, etc.

    hass.async_add_entities = add_entities

    await async_setup_entry(hass, entry, hass.async_add_entities)

    mock_manager.restore_and_add_entities.assert_awaited_once_with(add_entities)

    hass.data[DOMAIN].pop(PLANT_TRACKER_MANAGER)
    caplog.clear()
    await async_setup_entry(hass, entry, hass.async_add_entities)
    assert "PlantTrackerManager not found in hass.data" in caplog.text
