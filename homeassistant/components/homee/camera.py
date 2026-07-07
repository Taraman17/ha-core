"""The homee camera platform."""

import json
from typing import override
from urllib.parse import unquote

from pyHomee.const import AttributeType, NodeProfile
from pyHomee.model import HomeeAttribute, HomeeNode

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import HomeeConfigEntry
from .entity import HomeeEntity
from .helpers import setup_homee_platform

PARALLEL_UPDATES = 0


async def add_camera_entities(
    config_entry: HomeeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
    nodes: list[HomeeNode],
) -> None:
    """Add homee camera entities."""
    async_add_entities(
        HomeeCamera(attribute, config_entry)
        for node in nodes
        if node.profile in [NodeProfile.CAMERA, NodeProfile.CAMERA_WITH_FLOODLIGHT]
        if (attribute := node.get_attribute_by_type(AttributeType.SURVEILLANCE_ON_OFF))
    )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HomeeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the homee camera platform."""

    await setup_homee_platform(add_camera_entities, async_add_entities, config_entry)


class HomeeCamera(HomeeEntity, Camera):
    """Representation of a homee camera entity."""

    def __init__(self, attribute: HomeeAttribute, entry: HomeeConfigEntry) -> None:
        """Initialize the homee camera entity."""
        super().__init__(attribute, entry)
        Camera.__init__(self)
        self._attr_supported_features = (
            CameraEntityFeature.ON_OFF | CameraEntityFeature.STREAM
        )
        self._attr_translation_key = "camera"

    @property
    @override
    def motion_detection_enabled(self) -> bool:
        """Return the camera motion detection status."""
        return self._attribute.current_value == 1.0

    @override
    async def stream_source(self) -> str | None:
        """Return the stream source URL for the camera."""
        attribute = self._attribute
        if attribute.type != AttributeType.SURVEILLANCE_ON_OFF:
            return None

        try:
            data = json.loads(attribute.data)
        except TypeError, ValueError:
            return None

        commands = data.get("commands") if isinstance(data, dict) else None
        video_path = commands.get("video") if isinstance(commands, dict) else None
        base_url = data.get("baseUrlLocal") or data.get("baseUrlOnline")
        if not isinstance(video_path, str) or not isinstance(base_url, str):
            return None

        return unquote(base_url) + video_path

    @override
    async def async_turn_on(self) -> None:
        """Turn on camera."""
        await self.async_set_homee_value(1)

    @override
    async def async_turn_off(self) -> None:
        """Turn off camera."""
        await self.async_set_homee_value(0)
