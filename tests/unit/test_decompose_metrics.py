# @jig T-DECOMP-001 verifies:S-DECOMP-001 subsystem:decompose
"""Unit tests for decompose metrics calculation."""

from pathlib import Path
from textwrap import dedent

import pytest

from jig.core.graph import Edge, Graph, Subsystem
from jig.decompose.metrics import (
    DecomposabilityMetrics,
    SubsystemMetrics,
    calculate_all_metrics,
    calculate_coupling_ratio,
    calculate_modularity,
)


def test_modularity_calculation_known_graph(tmp_path: Path) -> None:
    """Verify modularity score for known graph structure."""
    from tests.helpers.graph_fixtures import create_test_graph

    # Create a graph with clear subsystem structure
    # Two subsystems with strong internal connections, weak cross connections
    nodes = []

    # Create nodes for subsystem_a
    for i in range(4):
        nodes.append({
            "id": f"O-A-{i:03d}",
            "type": "outcome",
            "title": f"Node A{i}",
            "subsystem": "subsystem_a",
            "depends_on": [f"O-A-{i+1:03d}"] if i < 3 else ["O-B-000"],  # Chain within, cross at end
        })

    # Create nodes for subsystem_b
    for i in range(4):
        depends_on = [f"O-B-{i+1:03d}"] if i < 3 else []
        nodes.append({
            "id": f"O-B-{i:03d}",
            "type": "outcome",
            "title": f"Node B{i}",
            "subsystem": "subsystem_b",
            "depends_on": depends_on if depends_on else None,
        })

    # Create graph with subsystems
    jig_dir = create_test_graph(tmp_path, nodes, subsystems={
        "subsystem_a": {"id": "subsystem_a"},
        "subsystem_b": {"id": "subsystem_b"},
    })

    # Load graph and calculate modularity
    graph = Graph.load_from_dir(jig_dir)
    modularity = calculate_modularity(graph)

    # With strong internal connections and one weak cross connection,
    # modularity should be positive and relatively high
    assert modularity > 0.2, f"Expected modularity > 0.2, got {modularity:.3f}"
    assert modularity < 1.0, f"Modularity should be < 1.0, got {modularity:.3f}"


# @jig T-DECOMP-002 verifies:S-DECOMP-003 subsystem:decompose
def test_coupling_ratio_calculation() -> None:
    """Verify coupling ratio for subsystem with known edges."""
    # Create a simple graph manually
    graph = Graph()

    # Create subsystem with 4 nodes
    subsystem = Subsystem(name="core", nodes=["N1", "N2", "N3", "N4"])
    graph.subsystems["core"] = subsystem

    # Add edges: 10 internal, 2 external
    # Internal edges (both endpoints in subsystem)
    for i in range(10):
        graph.edges.append(Edge(from_node="N1", to_node="N2", type="depends_on"))

    # External edges (one endpoint outside)
    graph.edges.append(Edge(from_node="N1", to_node="N5", type="depends_on"))
    graph.edges.append(Edge(from_node="N6", to_node="N2", type="depends_on"))

    # Calculate coupling ratio
    metrics = calculate_coupling_ratio("core", graph)

    # Verify results
    assert metrics.name == "core"
    assert metrics.node_count == 4
    assert metrics.internal_edges == 10
    assert metrics.external_edges == 2
    assert metrics.coupling_ratio == 5.0  # 10 / 2 = 5.0


# @jig T-DECOMP-003 verifies:S-DECOMP-001 subsystem:decompose
def test_modularity_single_subsystem() -> None:
    """Verify modularity = 0 for single subsystem (no structure)."""
    graph = Graph()

    # Single subsystem with all nodes
    subsystem = Subsystem(name="all", nodes=["N1", "N2", "N3"])
    graph.subsystems["all"] = subsystem

    # Add some edges
    graph.edges.append(Edge(from_node="N1", to_node="N2", type="depends_on"))
    graph.edges.append(Edge(from_node="N2", to_node="N3", type="depends_on"))

    # Calculate modularity
    modularity = calculate_modularity(graph)

    # Single subsystem means no community structure, modularity should be 0
    assert modularity == 0.0


# @jig T-DECOMP-004 verifies:S-DECOMP-003 subsystem:decompose
def test_coupling_ratio_no_external_edges() -> None:
    """Verify ratio = inf when subsystem has no external edges."""
    graph = Graph()

    # Perfectly isolated subsystem
    subsystem = Subsystem(name="isolated", nodes=["N1", "N2"])
    graph.subsystems["isolated"] = subsystem

    # Only internal edges
    graph.edges.append(Edge(from_node="N1", to_node="N2", type="depends_on"))
    graph.edges.append(Edge(from_node="N2", to_node="N1", type="depends_on"))

    # Calculate coupling ratio
    metrics = calculate_coupling_ratio("isolated", graph)

    # No external edges means perfect isolation, ratio = infinity
    assert metrics.coupling_ratio == float("inf")
    assert metrics.internal_edges == 2
    assert metrics.external_edges == 0


# @jig T-DECOMP-004a verifies:S-DECOMP-003 subsystem:decompose
def test_coupling_ratio_excludes_constraint_edges() -> None:
    """Verify constraint edges (satisfies) not counted in coupling (v7)."""
    graph = Graph()

    # Create subsystem
    subsystem = Subsystem(name="core", nodes=["S-001", "X-001"])
    graph.subsystems["core"] = subsystem

    # Add structural edges (should be counted)
    graph.edges.append(Edge(from_node="S-001", to_node="O-001", type="implements"))

    # Add constraint edges (should NOT be counted)
    graph.edges.append(Edge(from_node="S-001", to_node="X-001", type="satisfies"))
    graph.edges.append(Edge(from_node="X-001", to_node="O-002", type="satisfies"))

    # Calculate coupling ratio
    metrics = calculate_coupling_ratio("core", graph)

    # Only the implements edge should be counted (external)
    assert metrics.internal_edges == 0
    assert metrics.external_edges == 1  # Only the implements edge
    assert metrics.coupling_ratio == 0.0  # 0 internal / 1 external


def test_calculate_all_metrics() -> None:
    """Test calculate_all_metrics aggregates subsystem metrics correctly."""
    graph = Graph()

    # Create two subsystems
    subsystem_a = Subsystem(name="subsystem_a", nodes=["A1", "A2"])
    subsystem_b = Subsystem(name="subsystem_b", nodes=["B1", "B2"])
    graph.subsystems["subsystem_a"] = subsystem_a
    graph.subsystems["subsystem_b"] = subsystem_b

    # Add edges
    # subsystem_a: 2 internal, 1 external → ratio = 2.0
    graph.edges.append(Edge(from_node="A1", to_node="A2", type="depends_on"))
    graph.edges.append(Edge(from_node="A2", to_node="A1", type="depends_on"))
    graph.edges.append(Edge(from_node="A1", to_node="B1", type="depends_on"))

    # subsystem_b: 1 internal, 1 external → ratio = 1.0
    graph.edges.append(Edge(from_node="B1", to_node="B2", type="depends_on"))

    # Calculate all metrics
    metrics = calculate_all_metrics(graph)

    # Verify aggregated metrics
    assert metrics.subsystem_count == 2
    assert "subsystem_a" in metrics.subsystems
    assert "subsystem_b" in metrics.subsystems
    assert metrics.subsystems["subsystem_a"].coupling_ratio == 2.0
    assert metrics.subsystems["subsystem_b"].coupling_ratio == 1.0
    # Average coupling ratio: (2.0 + 1.0) / 2 = 1.5
    assert metrics.avg_coupling_ratio == 1.5


def test_modularity_no_subsystems() -> None:
    """Test modularity returns 0 when no subsystems defined."""
    graph = Graph()
    # Add some edges but no subsystems
    graph.edges.append(Edge(from_node="N1", to_node="N2", type="depends_on"))

    modularity = calculate_modularity(graph)
    assert modularity == 0.0


def test_modularity_no_edges() -> None:
    """Test modularity returns 0 when no edges in graph."""
    graph = Graph()
    subsystem = Subsystem(name="empty", nodes=["N1", "N2"])
    graph.subsystems["empty"] = subsystem

    modularity = calculate_modularity(graph)
    assert modularity == 0.0


def test_coupling_ratio_subsystem_not_found() -> None:
    """Test coupling ratio raises error for nonexistent subsystem."""
    graph = Graph()

    with pytest.raises(ValueError, match="Subsystem .* not found"):
        calculate_coupling_ratio("nonexistent", graph)


def test_nested_subsystem_metrics() -> None:
    """Test metrics work with nested subsystems."""
    graph = Graph()

    # Create nested subsystem structure
    parent = Subsystem(name="parent", parent_path="")
    child1 = Subsystem(name="child1", nodes=["C1-1", "C1-2"], parent_path="parent")
    child2 = Subsystem(name="child2", nodes=["C2-1", "C2-2"], parent_path="parent")

    parent.subsystems["child1"] = child1
    parent.subsystems["child2"] = child2
    graph.subsystems["parent"] = parent

    # Add edges within child1
    graph.edges.append(Edge(from_node="C1-1", to_node="C1-2", type="depends_on"))
    # Add edge from child1 to child2 (external to child1, internal to parent)
    graph.edges.append(Edge(from_node="C1-2", to_node="C2-1", type="depends_on"))

    # Calculate metrics for child1
    metrics_child1 = calculate_coupling_ratio("parent.child1", graph)
    assert metrics_child1.node_count == 2
    assert metrics_child1.internal_edges == 1
    assert metrics_child1.external_edges == 1
    assert metrics_child1.coupling_ratio == 1.0

    # Calculate metrics for parent (should include all nodes)
    metrics_parent = calculate_coupling_ratio("parent", graph)
    assert metrics_parent.node_count == 4  # All child nodes
    assert metrics_parent.internal_edges == 2  # Both edges are internal to parent
    assert metrics_parent.external_edges == 0
    assert metrics_parent.coupling_ratio == float("inf")


def test_calculate_all_metrics_with_nested_subsystems() -> None:
    """Test calculate_all_metrics includes nested subsystems."""
    graph = Graph()

    # Create nested structure
    parent = Subsystem(name="parent", parent_path="")
    child = Subsystem(name="child", nodes=["N1", "N2"], parent_path="parent")
    parent.subsystems["child"] = child
    graph.subsystems["parent"] = parent

    # Add edge
    graph.edges.append(Edge(from_node="N1", to_node="N2", type="depends_on"))

    # Calculate all metrics
    metrics = calculate_all_metrics(graph)

    # Should include both parent and child
    assert metrics.subsystem_count == 2
    assert "parent" in metrics.subsystems
    assert "parent.child" in metrics.subsystems
