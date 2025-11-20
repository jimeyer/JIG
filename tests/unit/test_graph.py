# @jig T-GRAPH-001 verifies:S-GRAPH-002 subsystem:core
"""Unit tests for graph data structures and operations."""

import tempfile
from pathlib import Path

import pytest

from jig.core.graph import Edge, Graph, Subsystem
from jig.utils.yaml_utils import dump_yaml


def create_test_node(tmp_path: Path, node_id: str, node_type: str, title: str, subsystem: str = "core") -> Path:
    """Helper to create a test OSTC node file.

    Args:
        tmp_path: Temporary directory
        node_id: Node ID (e.g., O-TEST-001)
        node_type: Node type (outcome, specification, etc.)
        title: Node title
        subsystem: Subsystem name

    Returns:
        Path to created node file
    """
    # Determine directory based on type
    type_to_dir = {
        "outcome": "outcomes",
        "specification": "specifications",
        "constraint": "constraints",
        "test": "tests",
    }
    node_dir = tmp_path / type_to_dir.get(node_type, "outcomes")
    node_dir.mkdir(parents=True, exist_ok=True)

    # Create node file with YAML frontmatter
    node_file = node_dir / f"{node_id}.md"
    # Use triple-quoted string with explicit line breaks to avoid YAML parsing issues
    lines = [
        "---",
        f"id: {node_id}",
        f"type: {node_type}",
        f'title: "{title}"',  # Always quote title to avoid YAML issues
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
    """Helper to create a test graph-index.yaml file.

    Args:
        tmp_path: Temporary directory
        edges: List of edge dictionaries with from, to, type
        subsystems: Dictionary of subsystems with nodes lists

    Returns:
        Path to created graph-index.yaml
    """
    graph_index_path = tmp_path / "graph-index.yaml"
    data = {
        "version": "1.0.0",
        "edges": edges,
        "subsystems": subsystems,
    }
    dump_yaml(data, graph_index_path)
    return graph_index_path


# @jig T-GRAPH-001 verifies:S-GRAPH-002 subsystem:core
def test_load_from_dir_success():
    """Verify Graph loads from jig/ directory with valid nodes."""
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

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Verify nodes loaded
        assert len(graph.nodes) == 3
        assert "O-TEST-001" in graph.nodes
        assert "O-TEST-002" in graph.nodes
        assert "S-TEST-001" in graph.nodes

        # Verify edges loaded
        assert len(graph.edges) == 1
        assert graph.edges[0].from_node == "S-TEST-001"
        assert graph.edges[0].to_node == "O-TEST-001"
        assert graph.edges[0].type == "implements"

        # Verify subsystems loaded
        assert len(graph.subsystems) == 1
        assert "core" in graph.subsystems
        assert graph.subsystems["core"].nodes == ["O-TEST-001", "O-TEST-002", "S-TEST-001"]


# @jig T-GRAPH-002 verifies:S-GRAPH-002 subsystem:core
def test_get_node_counts_by_type():
    """Verify node counting by type."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes of different types
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Outcome 2")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1")
        create_test_node(tmp_path, "S-TEST-002", "specification", "Spec 2")
        create_test_node(tmp_path, "S-TEST-003", "specification", "Spec 3")

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Get counts
        counts = graph.get_node_counts_by_type()

        # Verify counts
        assert counts["outcome"] == 2
        assert counts["specification"] == 3


# @jig T-GRAPH-003 verifies:S-GRAPH-002 subsystem:core
def test_find_orphaned_nodes():
    """Verify orphaned node detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Connected outcome")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Orphaned outcome")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Connected spec")

        # Create edges - O-TEST-002 is not in any edge
        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
        ]
        create_test_graph_index(tmp_path, edges, {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Find orphaned nodes
        orphaned = graph.find_orphaned_nodes()

        # Verify orphaned nodes
        assert len(orphaned) == 1
        assert "O-TEST-002" in orphaned


def test_load_from_dir_missing_directory():
    """Verify error when intent directory doesn't exist."""
    with pytest.raises(FileNotFoundError, match="Intent directory not found"):
        Graph.load_from_dir(Path("/nonexistent/path"))


def test_load_from_dir_without_graph_index():
    """Verify graph loads even without graph-index.yaml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes but no graph-index.yaml
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Test outcome")

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Verify nodes loaded, no edges/subsystems
        assert len(graph.nodes) == 1
        assert len(graph.edges) == 0
        assert len(graph.subsystems) == 0


def test_get_nodes_by_subsystem():
    """Verify nodes grouped by subsystem."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes in different subsystems
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core outcome", "core")
        create_test_node(tmp_path, "O-CORE-002", "outcome", "Core outcome 2", "core")
        create_test_node(tmp_path, "O-CLI-001", "outcome", "CLI outcome", "cli")

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Get nodes by subsystem
        subsystem_nodes = graph.get_nodes_by_subsystem()

        # Verify grouping
        assert len(subsystem_nodes) == 2
        assert "core" in subsystem_nodes
        assert "cli" in subsystem_nodes
        assert len(subsystem_nodes["core"]) == 2
        assert len(subsystem_nodes["cli"]) == 1
        assert "O-CORE-001" in subsystem_nodes["core"]
        assert "O-CLI-001" in subsystem_nodes["cli"]


def test_to_networkx():
    """Verify conversion to NetworkX graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1")

        # Create edges
        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
        ]
        create_test_graph_index(tmp_path, edges, {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Convert to NetworkX
        nx_graph = graph.to_networkx()

        # Verify nodes
        assert nx_graph.number_of_nodes() == 2
        assert "O-TEST-001" in nx_graph.nodes
        assert "S-TEST-001" in nx_graph.nodes

        # Verify edges
        assert nx_graph.number_of_edges() == 1
        assert nx_graph.has_edge("S-TEST-001", "O-TEST-001")

        # Verify node attributes
        assert nx_graph.nodes["O-TEST-001"]["type"] == "outcome"
        assert nx_graph.nodes["S-TEST-001"]["type"] == "specification"


def test_edge_dataclass():
    """Verify Edge dataclass works correctly."""
    edge = Edge(from_node="S-001", to_node="O-001", type="implements")
    assert edge.from_node == "S-001"
    assert edge.to_node == "O-001"
    assert edge.type == "implements"


def test_subsystem_dataclass():
    """Verify Subsystem dataclass works correctly."""
    subsystem = Subsystem(name="core", nodes=["O-001", "S-001"])
    assert subsystem.name == "core"
    assert subsystem.nodes == ["O-001", "S-001"]


def test_graph_dataclass_defaults():
    """Verify Graph dataclass has proper defaults."""
    graph = Graph()
    assert graph.nodes == {}
    assert graph.edges == []
    assert graph.subsystems == {}


def test_load_from_dir_with_multiple_node_types():
    """Verify loading nodes from all supported markdown directories (O/S/C)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes in different directories
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec")
        create_test_node(tmp_path, "C-TEST-001", "constraint", "Constraint")
        # Test nodes (T) are NOT loaded from markdown files (annotation-based)
        create_test_node(tmp_path, "T-TEST-001", "test", "Test")

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Verify only O/S/C types loaded (3 nodes, not 4)
        assert len(graph.nodes) == 3
        assert "O-TEST-001" in graph.nodes
        assert "S-TEST-001" in graph.nodes
        assert "C-TEST-001" in graph.nodes
        assert "T-TEST-001" not in graph.nodes  # Test nodes not loaded from markdown


def test_find_orphaned_nodes_all_connected():
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

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Find orphaned nodes
        orphaned = graph.find_orphaned_nodes()

        # Verify no orphaned nodes
        assert len(orphaned) == 0


def test_get_node_counts_empty_graph():
    """Verify node counts for empty graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Load empty graph
        graph = Graph.load_from_dir(tmp_path)

        # Get counts
        counts = graph.get_node_counts_by_type()

        # Verify empty
        assert counts == {}
