# @jig T-JIGY-007 verifies:S-JIGY-003 subsystem:jigy-tool
"""Unit tests for unified node registry (WU3)."""

from pathlib import Path

import pytest

from jig.core.graph import Graph, Edge
from jig.core.parser import OSTCNode


# @jig T-JIGY-008 verifies:S-JIGY-003 subsystem:jigy-tool
def test_node_lookup_o1_performance() -> None:
    """Verify O(1) node lookup performance with hash map."""
    graph = Graph()
    
    # Add 1000 nodes
    for i in range(1000):
        node = OSTCNode(
            id=f"S-TEST-{i:03d}",
            type="specification",
            title=f"Test spec {i}"
        )
        graph.nodes[node.id] = node
    
    # Lookup should be O(1) - test by doing many lookups
    import time
    start = time.time()
    for i in range(1000):
        node = graph.nodes.get(f"S-TEST-{i:03d}")
        assert node is not None
    elapsed = time.time() - start
    
    # 1000 lookups should be very fast (<10ms for O(1))
    assert elapsed < 0.010, f"Lookups took {elapsed*1000:.1f}ms, expected <10ms"


def test_get_nodes_by_type() -> None:
    """Test filtering nodes by type."""
    graph = Graph()
    
    # Add mixed node types
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    graph.nodes["O-002"] = OSTCNode(id="O-002", type="outcome", title="Outcome 2")
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.nodes["C-001"] = OSTCNode(id="C-001", type="code", title="Code 1")
    
    # Filter by type
    outcomes = graph.filter_by_type("outcome")
    assert len(outcomes) == 2
    assert all(n.type == "outcome" for n in outcomes)
    
    specs = graph.filter_by_type("specification")
    assert len(specs) == 1
    
    code = graph.filter_by_type("code")
    assert len(code) == 1


def test_get_nodes_by_subsystem() -> None:
    """Test filtering nodes by subsystem."""
    graph = Graph()
    
    # Add nodes with different subsystems
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="O1", subsystem="auth")
    graph.nodes["O-002"] = OSTCNode(id="O-002", type="outcome", title="O2", subsystem="auth")
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="S1", subsystem="core")
    graph.nodes["S-002"] = OSTCNode(id="S-002", type="specification", title="S2", subsystem=None)
    
    # Filter by subsystem
    auth_nodes = graph.filter_by_subsystem("auth")
    assert len(auth_nodes) == 2
    assert all(n.subsystem == "auth" for n in auth_nodes)
    
    core_nodes = graph.filter_by_subsystem("core")
    assert len(core_nodes) == 1


def test_get_edges_from_node() -> None:
    """Test getting outgoing edges from a node."""
    graph = Graph()
    
    # Add nodes
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="S1")
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="O1")
    graph.nodes["O-002"] = OSTCNode(id="O-002", type="outcome", title="O2")
    
    # Add edges
    graph.edges.append(Edge("S-001", "O-001", "implements"))
    graph.edges.append(Edge("S-001", "O-002", "implements"))
    graph.edges.append(Edge("O-001", "O-002", "depends_on"))
    
    # Get outgoing edges from S-001
    s_deps = graph.get_dependencies("S-001")
    assert len(s_deps) == 2
    assert "O-001" in s_deps
    assert "O-002" in s_deps
    
    # Get outgoing edges from O-001
    o_deps = graph.get_dependencies("O-001")
    assert len(o_deps) == 1
    assert "O-002" in o_deps


def test_get_edges_to_node() -> None:
    """Test getting incoming edges to a node."""
    graph = Graph()
    
    # Add nodes
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="O1")
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="S1")
    graph.nodes["S-002"] = OSTCNode(id="S-002", type="specification", title="S2")
    
    # Add edges
    graph.edges.append(Edge("S-001", "O-001", "implements"))
    graph.edges.append(Edge("S-002", "O-001", "implements"))
    
    # Get incoming edges to O-001
    dependents = graph.get_dependents("O-001")
    assert len(dependents) == 2
    assert "S-001" in dependents
    assert "S-002" in dependents


def test_get_all_edges() -> None:
    """Test getting all edges from graph."""
    graph = Graph()
    
    # Add edges
    graph.edges.append(Edge("S-001", "O-001", "implements"))
    graph.edges.append(Edge("S-002", "O-002", "implements"))
    graph.edges.append(Edge("C-001", "S-001", "implements"))
    
    # Get all edges
    all_edges = graph.edges
    assert len(all_edges) == 3


def test_node_registry_integration(tmp_path: Path) -> None:
    """Test complete node registry with real file loading."""
    from tests.helpers.graph_fixtures import create_test_graph

    # Create graph with O/S nodes and C/T nodes
    jig_dir = create_test_graph(tmp_path, [
        {"id": "O-TEST-001", "type": "outcome", "title": "Test outcome", "subsystem": "test"},
        {"id": "S-TEST-001", "type": "specification", "title": "Test spec", "subsystem": "test", "implements": ["O-TEST-001"]},
        {"id": "C-TEST-001", "type": "code", "title": "Test code", "subsystem": "test", "file": "test.py", "line": 1, "implements": ["S-TEST-001"]},
        {"id": "T-TEST-001", "type": "test", "title": "Test case", "subsystem": "test", "file": "test_test.py", "line": 5, "verifies": ["S-TEST-001"]},
    ], subsystems={"test": {"id": "test"}})

    # Load graph
    graph = Graph.load_from_dir(jig_dir)

    # Verify all nodes loaded
    assert len(graph.nodes) == 4
    assert "O-TEST-001" in graph.nodes
    assert "S-TEST-001" in graph.nodes
    assert "C-TEST-001" in graph.nodes
    assert "T-TEST-001" in graph.nodes

    # Verify node lookups work
    outcome = graph.nodes["O-TEST-001"]
    assert outcome.type == "outcome"
    assert outcome.subsystem == "test"

    # Verify type filtering
    outcomes = graph.filter_by_type("outcome")
    specs = graph.filter_by_type("specification")
    code = graph.filter_by_type("code")
    tests = graph.filter_by_type("test")
    assert len(outcomes) == 1
    assert len(specs) == 1
    assert len(code) == 1
    assert len(tests) == 1

    # Verify subsystem filtering
    test_nodes = graph.filter_by_subsystem("test")
    assert len(test_nodes) == 4

    # Verify edge queries
    assert len(graph.edges) == 3
    s_deps = graph.get_dependencies("S-TEST-001")
    assert "O-TEST-001" in s_deps

    o_dependents = graph.get_dependents("O-TEST-001")
    assert "S-TEST-001" in o_dependents


def test_node_counts_by_type() -> None:
    """Test getting node counts grouped by type."""
    graph = Graph()
    
    # Add various nodes
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="O1")
    graph.nodes["O-002"] = OSTCNode(id="O-002", type="outcome", title="O2")
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="S1")
    graph.nodes["S-002"] = OSTCNode(id="S-002", type="specification", title="S2")
    graph.nodes["S-003"] = OSTCNode(id="S-003", type="specification", title="S3")
    graph.nodes["C-001"] = OSTCNode(id="C-001", type="code", title="C1")
    
    counts = graph.get_node_counts_by_type()
    
    assert counts["outcome"] == 2
    assert counts["specification"] == 3
    assert counts["code"] == 1


def test_nodes_by_subsystem_grouping() -> None:
    """Test getting nodes grouped by subsystem."""
    graph = Graph()
    
    # Add nodes with various subsystems
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="O1", subsystem="auth")
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="S1", subsystem="auth")
    graph.nodes["O-002"] = OSTCNode(id="O-002", type="outcome", title="O2", subsystem="core")
    graph.nodes["S-002"] = OSTCNode(id="S-002", type="specification", title="S2", subsystem="core")
    graph.nodes["C-001"] = OSTCNode(id="C-001", type="code", title="C1", subsystem="core")
    
    grouped = graph.get_nodes_by_subsystem()
    
    assert len(grouped["auth"]) == 2
    assert len(grouped["core"]) == 3
    assert "O-001" in grouped["auth"]
    assert "S-001" in grouped["auth"]
    assert "O-002" in grouped["core"]


def test_empty_graph() -> None:
    """Test registry operations on empty graph."""
    graph = Graph()
    
    # Empty queries should work
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0
    assert graph.get_node_counts_by_type() == {}
    assert graph.get_nodes_by_subsystem() == {}
    assert graph.filter_by_type("outcome") == []
    assert graph.filter_by_subsystem("test") == []
    assert graph.get_dependencies("S-001") == []
    assert graph.get_dependents("O-001") == []

