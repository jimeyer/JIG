# @jig T-GRAPH-004 verifies:S-GRAPH-003 subsystem:core
"""Unit tests for graph traversal methods."""

import tempfile
import time
from pathlib import Path

from jig.core.graph import Graph
from tests.helpers.graph_fixtures import create_test_graph


def test_get_dependencies():
    """Verify dependency detection for implements edges."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # S-001 implements O-001 → O-001 is dependency of S-001
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "test"},
            {"id": "S-TEST-001", "type": "specification", "title": "Spec 1", "subsystem": "test", "implements": ["O-TEST-001"]},
        ], subsystems={"test": {"id": "test"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

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

        # S-001 implements O-001 → S-001 is dependent of O-001
        # S-002 implements O-001 → S-002 is dependent of O-001
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "test"},
            {"id": "S-TEST-001", "type": "specification", "title": "Spec 1", "subsystem": "test", "implements": ["O-TEST-001"]},
            {"id": "S-TEST-002", "type": "specification", "title": "Spec 2", "subsystem": "test", "implements": ["O-TEST-001"]},
        ], subsystems={"test": {"id": "test"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

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
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "test"},
            {"id": "S-TEST-001", "type": "specification", "title": "Spec 1", "subsystem": "test", "implements": ["O-TEST-001"]},
            {"id": "C-TEST-001", "type": "constraint", "title": "Constraint 1", "subsystem": "test", "satisfies": ["S-TEST-001"]},
        ], subsystems={"test": {"id": "test"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

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

        # Create disconnected nodes (no edges between them)
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "test"},
            {"id": "O-TEST-002", "type": "outcome", "title": "Outcome 2", "subsystem": "test"},
        ], subsystems={"test": {"id": "test"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # No path exists
        path = graph.find_path("O-TEST-001", "O-TEST-002")
        assert path is None


def test_find_path_same_node():
    """Verify path from node to itself."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create single node
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "test"},
        ], subsystems={"test": {"id": "test"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Path from node to itself
        path = graph.find_path("O-TEST-001", "O-TEST-001")
        assert path == ["O-TEST-001"]


def test_find_path_missing_nodes():
    """Verify returns None for missing nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create single node
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "test"},
        ], subsystems={"test": {"id": "test"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

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

        # S-001 implements both outcomes
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "test"},
            {"id": "O-TEST-002", "type": "outcome", "title": "Outcome 2", "subsystem": "test"},
            {"id": "S-TEST-001", "type": "specification", "title": "Spec 1", "subsystem": "test", "implements": ["O-TEST-001", "O-TEST-002"]},
        ], subsystems={"test": {"id": "test"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Verify dependencies are sorted
        deps = graph.get_dependencies("S-TEST-001")
        assert deps == ["O-TEST-001", "O-TEST-002"]


def test_get_dependencies_missing_node():
    """Verify empty list for missing node."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create single node
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "test"},
        ], subsystems={"test": {"id": "test"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Missing node returns empty list
        deps = graph.get_dependencies("INVALID-001")
        assert deps == []


def test_get_dependents_missing_node():
    """Verify empty list for missing node."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create single node
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "test"},
        ], subsystems={"test": {"id": "test"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Missing node returns empty list
        dependents = graph.get_dependents("INVALID-001")
        assert dependents == []


# @jig T-GRAPH-008 verifies:S-GRAPH-003 subsystem:core
def test_traversal_performance():
    """Verify traversal completes in <100ms for 100 nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create 100 nodes in a chain (50 outcomes + 50 specs)
        nodes = []
        for i in range(50):
            # Create outcome
            nodes.append({
                "id": f"O-PERF-{i:03d}",
                "type": "outcome",
                "title": f"Outcome {i}",
                "subsystem": "test"
            })
            # Create specification that implements the outcome
            nodes.append({
                "id": f"S-PERF-{i:03d}",
                "type": "specification",
                "title": f"Spec {i}",
                "subsystem": "test",
                "implements": [f"O-PERF-{i:03d}"]
            })

        jig_dir = create_test_graph(tmp_path, nodes, subsystems={"test": {"id": "test"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

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

        # Create a graph with multiple paths:
        # O-001 <- S-001 <- C-001 (short path)
        # O-001 <- S-002 <- S-003 <- C-001 (longer path)
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "test"},
            # Short path
            {"id": "S-TEST-001", "type": "specification", "title": "Spec 1", "subsystem": "test", "implements": ["O-TEST-001"]},
            # Longer path
            {"id": "S-TEST-002", "type": "specification", "title": "Spec 2", "subsystem": "test", "implements": ["O-TEST-001"]},
            {"id": "S-TEST-003", "type": "specification", "title": "Spec 3", "subsystem": "test", "depends_on": ["S-TEST-002"]},
            # Constraint connects to both paths
            {"id": "C-TEST-001", "type": "constraint", "title": "Constraint 1", "subsystem": "test", "satisfies": ["S-TEST-001", "S-TEST-003"]},
        ], subsystems={"test": {"id": "test"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Find path - should return shortest
        path = graph.find_path("C-TEST-001", "O-TEST-001")
        assert len(path) == 3  # Shortest path has 3 nodes
        assert path == ["C-TEST-001", "S-TEST-001", "O-TEST-001"]
