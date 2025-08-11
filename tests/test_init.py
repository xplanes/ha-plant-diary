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

from custom_components.plant_diary import (
    async_reload_entry,
    config_flow,
    async_unload_entry,
)

DEFAULT_NAME = "My Plant Diary"


@pytest.mark.asyncio
async def test_flow_user_init(hass) -> None:
    """Test the initialization of the form in the first step of the config flow."""

    # Registramos manualmente el flujo
    config_entries.HANDLERS[config_flow.DOMAIN] = config_flow.PlantDiaryConfigFlow

    mock_integration = Integration(
        hass=hass,
        pkg_path="custom_components.plant_diary",
        file_path=pathlib.Path("custom_components/plant_diary/__init__.py"),
        manifest={
            "domain": config_flow.DOMAIN,
            "name": "Plant Diary",
            "version": "1.0.0",
            "requirements": [],
            "dependencies": [],
            "after_dependencies": [],
            "is_built_in": False,
        },
        top_level_files={
            "custom_components/plant_diary/manifest.json",
            "custom_components/plant_diary/config_flow.py",
            "custom_components/plant_diary/const.py",
            "custom_components/plant_diary/PlantDiaryEntity.py",
            "custom_components/plant_diary/PlantDiaryManager.py ",
            "custom_components/plant_diary/services.yaml",
        },
    )

    mock_config_flow_module = types.SimpleNamespace()
    mock_config_flow_module.PlantDiaryConfigFlow = config_flow.PlantDiaryConfigFlow
    mock_integration.async_get_platform = mock.AsyncMock(
        return_value=mock_config_flow_module
    )

    with (
        mock.patch(
            "homeassistant.loader.async_get_integration",
            return_value=mock_integration,
        ),
        mock.patch(
            "homeassistant.loader.async_get_integrations",
            return_value={config_flow.DOMAIN: mock_integration},
        ),
    ):
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
        "title": "Plant Diary",
        "type": mock.ANY,
        "version": 1,
        "description_placeholders": None,
        "handler": "plant_diary",
    }
    assert expected == result

    await hass.config_entries.async_unload(result["result"].entry_id)


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
