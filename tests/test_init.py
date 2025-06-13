"""Tests for Plant Tracker integration."""

import pytest
from custom_components.plant_tracker import config_flow
from unittest import mock

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
