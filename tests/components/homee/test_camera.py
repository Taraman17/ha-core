"""Tests for the homee camera platform."""

from unittest.mock import MagicMock

from homeassistant.components.camera import async_get_stream_source
from homeassistant.core import HomeAssistant

from . import build_mock_node, setup_integration

from tests.common import MockConfigEntry


async def test_camera_stream_source(
    hass: HomeAssistant, mock_homee: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """Test that the Homee camera stream source is extracted from surveillance data."""
    mock_homee.nodes = [build_mock_node("camera.json")]
    mock_homee.get_node_by_id.return_value = mock_homee.nodes[0]

    await setup_integration(hass, mock_config_entry)

    camera_entity_ids = hass.states.async_entity_ids("camera")
    assert len(camera_entity_ids) == 1

    stream_source = await async_get_stream_source(hass, camera_entity_ids[0])

    assert stream_source == (
        "http://192.168.1.1/35370bc9f57d9c1e3edf1ea3f66889a9/live/index.m3u8"
    )
