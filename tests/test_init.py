"""Tests for Plant Tracker integration."""

import pytest
from custom_components.plant_tracker import config_flow
from custom_components.plant_tracker import async_reload_entry
from unittest import mock
from unittest.mock import MagicMock, patch, ANY, AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DEFAULT_NAME = "My Plant Tracker"


@pytest.mark.asyncio
async def test_flow_user_init(hass) -> None:
    """Test the initialization of the form in the first step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    expected = {
        "context": {"source": "user"},
        "data": {},
        "description": None,
        "flow_id": mock.ANY,
        "minor_version": 1,
        "options": {},
        "result": mock.ANY,
        "subentries": (),
        "title": "Plant Tracker",
        "type": mock.ANY,
        "version": 1,
        "description_placeholders": None,
        "handler": "plant_tracker",
    }
    assert expected == result


@pytest.mark.asyncio
async def test_async_reload_entry():
    hass = MagicMock(spec=HomeAssistant)
    entry = MagicMock(spec=ConfigEntry)

    with (
        patch(
            "custom_components.plant_tracker.async_unload_entry", new_callable=AsyncMock
        ) as mock_unload,
        patch(
            "custom_components.plant_tracker.async_setup_entry", new_callable=AsyncMock
        ) as mock_setup,
    ):
        await async_reload_entry(hass, entry)

        mock_unload.assert_awaited_once_with(hass, entry)
        mock_setup.assert_awaited_once_with(hass, entry)
