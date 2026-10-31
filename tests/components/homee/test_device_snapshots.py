"""Test snapshots for Homee device nodes."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_homeassistant.common import MockConfigEntry
from syrupy.assertion import SnapshotAssertion

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import build_mock_node, setup_integration

DEVICE_FIXTURES = Path(__file__).parent / "fixtures" / "devices"


@pytest.mark.parametrize(
    "device_file",
    sorted(DEVICE_FIXTURES.glob("*.json")),
    ids=lambda device_file: device_file.stem,
)
async def test_device_snapshot(
    hass: HomeAssistant,
    mock_homee: MagicMock,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    device_file: Path,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Home Assistant entities created for each Homee device node."""
    fixture_file = str(device_file.relative_to(DEVICE_FIXTURES.parent))
    mock_homee.nodes = [build_mock_node(fixture_file)]
    mock_homee.get_node_by_id.return_value = mock_homee.nodes[0]
    mock_homee.homeegrams = []
    await setup_integration(hass, mock_config_entry)

    entity_snapshots = {}
    for entity_entry in er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    ):
        state = hass.states.get(entity_entry.entity_id)
        if entity_entry.disabled_by is not None:
            assert state is None
        else:
            assert state is not None
        entity_snapshots[entity_entry.entity_id] = {
            "registry_entry": entity_entry,
            "state": state,
        }

    assert entity_snapshots
    assert entity_snapshots == snapshot
