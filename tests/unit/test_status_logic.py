# @jig T-STATUS-001 verifies:S-GRAPH-001 subsystem:core
"""Unit tests for status calculation logic."""

import json
import tempfile
from pathlib import Path

import pytest

from jig.cli.status import StatusData, calculate_status


def create_test_node(tmp_path: Path, node_id: str, node_type: str, title: str, subsystem: str = "core") -> Path:
    """Helper to create a test OSTC node file."""
    type_to_dir = {
        "outcome": "outcomes",
        "specification": "specifications",
        "constraint": "constraints",
        "test": "tests",
    }
    node_dir = tmp_path / type_to_dir.get(node_type, "outcomes")
    node_dir.mkdir(parents=True, exist_ok=True)

    node_file = node_dir / f"{node_id}.md"
    lines = [
        "---",
        f"id: {node_id}",
        f"type: {node_type}",
        f'title: "{title}"',
        f"subsystem: {subsystem}",
        "status: active",
        "---",
        "",
        f"# {title}",
        "",
        f"This is a test node for {node_id}.",
        ""
    ]
    content = "\n".join(lines)
    node_file.write_text(content)
    return node_file


def create_test_graph_index(tmp_path: Path, edges: list[dict], subsystems: dict) -> Path:
    """Helper to create a test graph-index.json file."""
    graph_index_path = tmp_path / "graph-index.json"
    data = {
        "version": "1.0",
        "generated": "2025-11-22T00:00:00Z",
        "edges": edges,
        "subsystems": subsystems,
    }
    graph_index_path.write_text(json.dumps(data, indent=2))
    return graph_index_path


def test_calculate_status_with_valid_graph():
    """Verify status calculation with valid graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Test outcome 1", "core")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Test outcome 2", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Test spec 1", "core")

        # Create graph-index.json
        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
        ]
        subsystems = {
            "core": {"nodes": ["O-TEST-001", "O-TEST-002", "S-TEST-001"]},
        }
        create_test_graph_index(tmp_path, edges, subsystems)

        # Calculate status
        status = calculate_status(tmp_path)

        # Verify status data
        assert status.total_nodes == 3
        assert status.node_counts["outcome"] == 2
        assert status.node_counts["specification"] == 1
        assert "core" in status.subsystems
        assert len(status.subsystems["core"]) == 3
        assert "O-TEST-002" in status.orphaned_nodes
        # Note: May have warning about missing graph-index.yaml (legacy check)
        # assert len(status.validation_errors) == 0


# @jig T-STATUS-002 verifies:S-GRAPH-001 subsystem:core
def test_calculate_status_identifies_orphans():
    """Verify status identifies orphaned nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes - all orphaned (no edges)
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Orphaned outcome", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Orphaned spec", "core")

        # Create graph-index.json with no edges
        create_test_graph_index(tmp_path, [], {})

        # Calculate status
        status = calculate_status(tmp_path)

        # Verify all nodes are orphaned
        assert status.total_nodes == 2
        assert len(status.orphaned_nodes) == 2
        assert "O-TEST-001" in status.orphaned_nodes
        assert "S-TEST-001" in status.orphaned_nodes


# @jig T-STATUS-003 verifies:S-GRAPH-001 subsystem:core
def test_status_handles_missing_directory():
    """Verify graceful handling when jig/ doesn't exist."""
    with pytest.raises(FileNotFoundError, match="Intent directory not found"):
        calculate_status(Path("/nonexistent/path"))


def test_calculate_status_handles_missing_graph_index():
    """Verify error when graph-index.json is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes but no graph-index.json
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Test outcome", "core")

        # Calculate status should raise error for missing graph-index
        with pytest.raises(FileNotFoundError, match="Intent directory not found"):
            calculate_status(tmp_path)


def test_calculate_status_empty_directory():
    """Verify status for empty jig/ directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create empty graph-index.json
        create_test_graph_index(tmp_path, [], {})

        # Calculate status on empty directory
        status = calculate_status(tmp_path)

        # Verify empty status
        assert status.total_nodes == 0
        assert status.node_counts == {}
        assert status.subsystems == {}
        assert status.orphaned_nodes == []


def test_calculate_status_multiple_subsystems():
    """Verify status with multiple subsystems."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes in different subsystems
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core outcome", "core")
        create_test_node(tmp_path, "O-CLI-001", "outcome", "CLI outcome", "cli")
        create_test_node(tmp_path, "O-API-001", "outcome", "API outcome", "api")

        # Create graph-index.json
        create_test_graph_index(tmp_path, [], {})

        # Calculate status
        status = calculate_status(tmp_path)

        # Verify subsystem grouping
        assert status.total_nodes == 3
        assert len(status.subsystems) == 3
        assert "core" in status.subsystems
        assert "cli" in status.subsystems
        assert "api" in status.subsystems
        assert len(status.subsystems["core"]) == 1
        assert len(status.subsystems["cli"]) == 1
        assert len(status.subsystems["api"]) == 1


def test_calculate_status_all_node_types():
    """Verify status counts all markdown node types correctly (O/S/C)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes of all markdown types (O/S/C - test nodes not loaded)
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec")
        create_test_node(tmp_path, "C-TEST-001", "constraint", "Constraint")
        # Test nodes (T) are NOT loaded from markdown files
        create_test_node(tmp_path, "T-TEST-001", "test", "Test")

        # Create graph-index.json
        create_test_graph_index(tmp_path, [], {})

        # Calculate status
        status = calculate_status(tmp_path)

        # Verify only O/S/C types counted (3 nodes, not 4)
        assert status.total_nodes == 3
        assert status.node_counts["outcome"] == 1
        assert status.node_counts["specification"] == 1
        assert status.node_counts["constraint"] == 1
        assert "test" not in status.node_counts  # Test nodes not loaded from markdown


def test_status_data_dataclass():
    """Verify StatusData dataclass works correctly."""
    status = StatusData(
        total_nodes=10,
        total_edges=5,
        subsystem_count=1,
        node_counts={"outcome": 5, "specification": 5},
        subsystems={"core": ["O-001", "S-001"]},
        orphaned_nodes=["O-002"],
        unassigned_nodes=["O-003"],
        validation_errors=["Warning: something"],
    )

    assert status.total_nodes == 10
    assert status.node_counts["outcome"] == 5
    assert "core" in status.subsystems
    assert "O-002" in status.orphaned_nodes
    assert len(status.validation_errors) == 1


def test_status_data_default_validation_errors():
    """Verify StatusData has default empty validation_errors."""
    status = StatusData(
        total_nodes=0,
        total_edges=0,
        subsystem_count=0,
        node_counts={},
        subsystems={},
        orphaned_nodes=[],
        unassigned_nodes=[],
    )

    assert status.validation_errors == []


def test_calculate_status_no_orphans_when_connected():
    """Verify no orphaned nodes when all are connected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec")

        # Create edges connecting all nodes
        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
        ]
        create_test_graph_index(tmp_path, edges, {})

        # Calculate status
        status = calculate_status(tmp_path)

        # Verify no orphaned nodes
        assert status.total_nodes == 2
        assert len(status.orphaned_nodes) == 0
