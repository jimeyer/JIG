# @jig T-GRAPH-004 verifies:S-GRAPH-003 subsystem:core
"""Unit tests for graph traversal methods."""

import tempfile
import time
from pathlib import Path

from jig.core.graph import Graph
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


# @jig T-GRAPH-004 verifies:S-GRAPH-003 subsystem:core
def test_get_dependencies():
    """Verify dependency detection for implements edges."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1")

        # S-001 implements O-001 → O-001 is dependency of S-001
        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
        ]
        create_test_graph_index(tmp_path, edges, {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Verify dependencies
        deps = graph.get_dependencies("S-TEST-001")
        assert deps == ["O-TEST-001"]

        # O-001 has no dependencies
        deps_o = graph.get_dependencies("O-TEST-001")
        assert deps_o == []


# @jig T-GRAPH-005 verifies:S-GRAPH-003 subsystem:core
def test_get_dependents():
    """Verify dependent detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1")
        create_test_node(tmp_path, "S-TEST-002", "specification", "Spec 2")

        # S-001 implements O-001 → S-001 is dependent of O-001
        # S-002 implements O-001 → S-002 is dependent of O-001
        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
            {"from": "S-TEST-002", "to": "O-TEST-001", "type": "implements"},
        ]
        create_test_graph_index(tmp_path, edges, {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Verify dependents
        dependents = graph.get_dependents("O-TEST-001")
        assert dependents == ["S-TEST-001", "S-TEST-002"]

        # S-001 has no dependents
        dependents_s = graph.get_dependents("S-TEST-001")
        assert dependents_s == []


# @jig T-GRAPH-006 verifies:S-GRAPH-003 subsystem:core
def test_find_path_exists():
    """Verify BFS finds shortest path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a chain: C-001 -> S-001 -> O-001 (using O/S/C nodes)
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1")
        create_test_node(tmp_path, "C-TEST-001", "constraint", "Constraint 1")

        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
            {"from": "C-TEST-001", "to": "S-TEST-001", "type": "constrains"},
        ]
        create_test_graph_index(tmp_path, edges, {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Find path from C-001 to O-001
        path = graph.find_path("C-TEST-001", "O-TEST-001")
        assert path == ["C-TEST-001", "S-TEST-001", "O-TEST-001"]

        # Path should work in reverse too (undirected traversal)
        path_reverse = graph.find_path("O-TEST-001", "C-TEST-001")
        assert path_reverse == ["O-TEST-001", "S-TEST-001", "C-TEST-001"]


# @jig T-GRAPH-007 verifies:S-GRAPH-003 subsystem:core
def test_find_path_no_path():
    """Verify returns None when no path exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create disconnected nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Outcome 2")

        # No edges between them
        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # No path exists
        path = graph.find_path("O-TEST-001", "O-TEST-002")
        assert path is None


def test_find_path_same_node():
    """Verify path from node to itself."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create single node
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Path from node to itself
        path = graph.find_path("O-TEST-001", "O-TEST-001")
        assert path == ["O-TEST-001"]


def test_find_path_missing_nodes():
    """Verify returns None for missing nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create single node
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Start node missing
        path = graph.find_path("INVALID-001", "O-TEST-001")
        assert path is None

        # End node missing
        path = graph.find_path("O-TEST-001", "INVALID-001")
        assert path is None

        # Both missing
        path = graph.find_path("INVALID-001", "INVALID-002")
        assert path is None


def test_get_dependencies_multiple():
    """Verify multiple dependencies are returned sorted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Outcome 2")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1")

        # S-001 implements both outcomes
        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-002", "type": "implements"},
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
        ]
        create_test_graph_index(tmp_path, edges, {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Verify dependencies are sorted
        deps = graph.get_dependencies("S-TEST-001")
        assert deps == ["O-TEST-001", "O-TEST-002"]


def test_get_dependencies_missing_node():
    """Verify empty list for missing node."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create single node
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Missing node returns empty list
        deps = graph.get_dependencies("INVALID-001")
        assert deps == []


def test_get_dependents_missing_node():
    """Verify empty list for missing node."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create single node
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Missing node returns empty list
        dependents = graph.get_dependents("INVALID-001")
        assert dependents == []


# @jig T-GRAPH-008 verifies:S-GRAPH-003 subsystem:core
def test_traversal_performance():
    """Verify traversal completes in <100ms for 100 nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create 100 nodes in a chain
        edges = []
        for i in range(50):
            # Create outcome
            outcome_id = f"O-PERF-{i:03d}"
            create_test_node(tmp_path, outcome_id, "outcome", f"Outcome {i}")

            # Create specification
            spec_id = f"S-PERF-{i:03d}"
            create_test_node(tmp_path, spec_id, "specification", f"Spec {i}")

            # Add edge: S implements O
            edges.append({
                "from": spec_id,
                "to": outcome_id,
                "type": "implements"
            })

        create_test_graph_index(tmp_path, edges, {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Test get_dependencies performance
        start = time.time()
        for i in range(50):
            graph.get_dependencies(f"S-PERF-{i:03d}")
        elapsed_deps = (time.time() - start) * 1000

        # Test get_dependents performance
        start = time.time()
        for i in range(50):
            graph.get_dependents(f"O-PERF-{i:03d}")
        elapsed_dependents = (time.time() - start) * 1000

        # Test find_path performance (worst case: no path)
        start = time.time()
        graph.find_path("O-PERF-000", "O-PERF-049")
        elapsed_path = (time.time() - start) * 1000

        # All operations should complete in <100ms
        assert elapsed_deps < 100, f"get_dependencies took {elapsed_deps:.2f}ms"
        assert elapsed_dependents < 100, f"get_dependents took {elapsed_dependents:.2f}ms"
        assert elapsed_path < 100, f"find_path took {elapsed_path:.2f}ms"


def test_find_path_shortest():
    """Verify BFS finds shortest path when multiple paths exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a graph with multiple paths (using O/S/C nodes):
        # O-001 <- S-001 <- C-001 (short path)
        # O-001 <- S-002 <- S-003 <- C-001 (longer path)
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1")
        create_test_node(tmp_path, "S-TEST-002", "specification", "Spec 2")
        create_test_node(tmp_path, "S-TEST-003", "specification", "Spec 3")
        create_test_node(tmp_path, "C-TEST-001", "constraint", "Constraint 1")

        edges = [
            # Short path
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
            {"from": "C-TEST-001", "to": "S-TEST-001", "type": "constrains"},
            # Longer path
            {"from": "S-TEST-002", "to": "O-TEST-001", "type": "implements"},
            {"from": "S-TEST-003", "to": "S-TEST-002", "type": "depends_on"},
            {"from": "C-TEST-001", "to": "S-TEST-003", "type": "constrains"},
        ]
        create_test_graph_index(tmp_path, edges, {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Find path - should return shortest
        path = graph.find_path("C-TEST-001", "O-TEST-001")
        assert len(path) == 3  # Shortest path has 3 nodes
        assert path == ["C-TEST-001", "S-TEST-001", "O-TEST-001"]
