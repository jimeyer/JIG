# @jig T-STATUS-001 verifies:S-GRAPH-001 subsystem:core
"""Unit tests for status calculation logic."""

import tempfile
from pathlib import Path

import pytest

from jig.cli.status import StatusData, calculate_status
from jig.utils.yaml_utils import dump_yaml


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
    """Helper to create a test graph-index.yaml file."""
    graph_index_path = tmp_path / "graph-index.yaml"
    data = {
        "version": "1.0.0",
        "edges": edges,
        "subsystems": subsystems,
    }
    dump_yaml(data, graph_index_path)
    return graph_index_path


# @jig T-STATUS-001 verifies:S-GRAPH-001 subsystem:core
def test_calculate_status_with_valid_graph():
    """Verify status calculation with valid graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Test outcome 1", "core")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Test outcome 2", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Test spec 1", "core")

        # Create graph-index.yaml
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
        assert len(status.validation_errors) == 0


# @jig T-STATUS-002 verifies:S-GRAPH-001 subsystem:core
def test_calculate_status_identifies_orphans():
    """Verify status identifies orphaned nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes - all orphaned (no edges)
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Orphaned outcome", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Orphaned spec", "core")

        # Create graph-index.yaml with no edges
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
    """Verify warning when graph-index.yaml is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes but no graph-index.yaml
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Test outcome", "core")

        # Calculate status
        status = calculate_status(tmp_path)

        # Verify warning about missing graph-index.yaml
        assert status.total_nodes == 1
        assert len(status.validation_errors) == 1
        assert "graph-index.yaml not found" in status.validation_errors[0]


def test_calculate_status_empty_directory():
    """Verify status for empty jig/ directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

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
    """Verify status counts all node types correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes of all types
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec")
        create_test_node(tmp_path, "C-TEST-001", "constraint", "Constraint")
        create_test_node(tmp_path, "T-TEST-001", "test", "Test")

        # Calculate status
        status = calculate_status(tmp_path)

        # Verify all types counted
        assert status.total_nodes == 4
        assert status.node_counts["outcome"] == 1
        assert status.node_counts["specification"] == 1
        assert status.node_counts["constraint"] == 1
        assert status.node_counts["test"] == 1


def test_status_data_dataclass():
    """Verify StatusData dataclass works correctly."""
    status = StatusData(
        total_nodes=10,
        node_counts={"outcome": 5, "specification": 5},
        subsystems={"core": ["O-001", "S-001"]},
        orphaned_nodes=["O-002"],
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
        node_counts={},
        subsystems={},
        orphaned_nodes=[],
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
