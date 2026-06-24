"""Tests for Plant Diary integration."""

import pathlib
import types
from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.loader import Integration
from homeassistant.setup import async_setup_component

from custom_components.plant_diary import (
    async_reload_entry,
    config_flow,
)

DEFAULT_NAME = "My Plant Diary"


@pytest.mark.asyncio
async def test_flow_user_init() -> None:
    """Test the initialization of the config flow without Home Assistant fixture."""

    flow = config_flow.PlantDiaryConfigFlow()

    # Provide a minimal hass with no existing config entries
    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_entries = MagicMock(return_value=[])
    flow.hass = hass

    result = await flow.async_step_user()

    # Since no data is required, a create_entry result is expected
    assert result["type"] == "create_entry"
    assert result["title"] == "Plant Diary"
    assert result["data"] == {}


@pytest.mark.asyncio
async def test_async_reload_entry():
    hass = MagicMock(spec=HomeAssistant)
    entry = MagicMock(spec=ConfigEntry)

    with (
        patch(
            "custom_components.plant_diary.async_unload_entry",
            new_callable=AsyncMock,
        ) as mock_unload,
        patch(
            "custom_components.plant_diary.async_setup_entry",
            new_callable=AsyncMock,
        ) as mock_setup,
    ):
        await async_reload_entry(hass, entry)

        mock_unload.assert_awaited_once_with(hass, entry)
        mock_setup.assert_awaited_once_with(hass, entry)
