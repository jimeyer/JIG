# @jig T-CLI-006 verifies:S-CLI-022,S-CLI-025 subsystem:cli
"""Unit tests for comprehensive semantic validation (WU1).

Tests the new validation.py module that provides semantic validation
for the status command, separate from structural validation in validator.py.
"""

import pytest

from jig.core.graph import Graph, Edge, Subsystem
from jig.core.parser import OSTCNode
from jig.core.validation import (
    ComprehensiveValidationResult,
    validate_graph_comprehensive,
)


def _create_test_graph_with_subsystems() -> Graph:
    """Helper to create a graph with proper subsystem structure."""
    graph = Graph()
    # Create core subsystem
    graph.subsystems["core"] = Subsystem(name="core")
    return graph


def test_validate_graph_comprehensive_valid_graph() -> None:
    """Test comprehensive validation on a valid graph."""
    graph = _create_test_graph_with_subsystems()
    graph.nodes["O-001"] = OSTCNode(
        id="O-001", type="outcome", title="Outcome 1", subsystem="core"
    )
    graph.nodes["S-001"] = OSTCNode(
        id="S-001", type="specification", title="Spec 1", subsystem="core"
    )
    graph.edges.append(Edge("S-001", "O-001", "implements"))

    result = validate_graph_comprehensive(graph)

    assert result.valid
    assert len(result.errors) == 0
    assert result.node_count == 2
    assert result.edge_count == 1
    assert result.checks_passed["edge_validation"]
    assert result.checks_passed["subsystem_hierarchy"]
    assert result.checks_passed["no_duplicate_ids"]


def test_validate_graph_comprehensive_with_edge_errors() -> None:
    """Test comprehensive validation detects edge validation errors."""
    graph = _create_test_graph_with_subsystems()
    graph.nodes["S-001"] = OSTCNode(
        id="S-001", type="specification", title="Spec 1", subsystem="core"
    )
    # Edge to non-existent node
    graph.edges.append(Edge("S-001", "O-999", "implements"))

    result = validate_graph_comprehensive(graph)

    assert not result.valid
    assert len(result.errors) > 0
    assert any("O-999" in error for error in result.errors)
    assert not result.checks_passed["edge_validation"]


def test_validate_graph_comprehensive_with_self_loop() -> None:
    """Test comprehensive validation detects self-loops."""
    graph = _create_test_graph_with_subsystems()
    graph.nodes["S-001"] = OSTCNode(
        id="S-001", type="specification", title="Spec 1", subsystem="core"
    )
    # Self-loop
    graph.edges.append(Edge("S-001", "S-001", "depends_on"))

    result = validate_graph_comprehensive(graph)

    assert not result.valid
    assert len(result.errors) > 0
    assert any("self-loop" in error.lower() for error in result.errors)


def test_validate_graph_comprehensive_with_warnings() -> None:
    """Test comprehensive validation generates warnings for quality issues."""
    graph = _create_test_graph_with_subsystems()
    # Node without subsystem assignment
    graph.nodes["O-001"] = OSTCNode(
        id="O-001", type="outcome", title="Outcome 1"
    )
    graph.nodes["S-001"] = OSTCNode(
        id="S-001", type="specification", title="Spec 1", subsystem="core"
    )
    graph.edges.append(Edge("S-001", "O-001", "implements"))

    result = validate_graph_comprehensive(graph)

    # Should be valid (warnings don't make it invalid)
    assert result.valid
    assert len(result.errors) == 0
    assert len(result.warnings) > 0
    assert any("subsystem" in warning.lower() for warning in result.warnings)


def test_validate_graph_comprehensive_orphaned_nodes() -> None:
    """Test comprehensive validation detects orphaned nodes."""
    graph = _create_test_graph_with_subsystems()
    # Node with no edges
    graph.nodes["O-001"] = OSTCNode(
        id="O-001", type="outcome", title="Outcome 1", subsystem="core"
    )
    # Node with edges
    graph.nodes["S-001"] = OSTCNode(
        id="S-001", type="specification", title="Spec 1", subsystem="core"
    )
    graph.nodes["O-002"] = OSTCNode(
        id="O-002", type="outcome", title="Outcome 2", subsystem="core"
    )
    graph.edges.append(Edge("S-001", "O-002", "implements"))

    result = validate_graph_comprehensive(graph)

    # Should be valid (orphans are warnings)
    assert result.valid
    assert len(result.warnings) > 0
    assert any("orphan" in warning.lower() for warning in result.warnings)


def test_validate_graph_comprehensive_invalid_edge_type() -> None:
    """Test comprehensive validation detects invalid edge types."""
    graph = _create_test_graph_with_subsystems()
    graph.nodes["O-001"] = OSTCNode(
        id="O-001", type="outcome", title="Outcome 1", subsystem="core"
    )
    graph.nodes["O-002"] = OSTCNode(
        id="O-002", type="outcome", title="Outcome 2", subsystem="core"
    )
    # O->O with 'implements' is invalid
    graph.edges.append(Edge("O-001", "O-002", "implements"))

    result = validate_graph_comprehensive(graph)

    assert not result.valid
    assert len(result.errors) > 0
    assert any("invalid edge type" in error.lower() for error in result.errors)


def test_validate_graph_comprehensive_empty_graph() -> None:
    """Test comprehensive validation on empty graph."""
    graph = Graph()

    result = validate_graph_comprehensive(graph)

    assert result.valid
    assert len(result.errors) == 0
    assert result.node_count == 0
    assert result.edge_count == 0


def test_validate_graph_comprehensive_result_structure() -> None:
    """Test ComprehensiveValidationResult has expected structure."""
    graph = _create_test_graph_with_subsystems()
    graph.nodes["O-001"] = OSTCNode(
        id="O-001", type="outcome", title="Outcome 1", subsystem="core"
    )

    result = validate_graph_comprehensive(graph)

    # Check all expected fields exist
    assert hasattr(result, "valid")
    assert hasattr(result, "errors")
    assert hasattr(result, "warnings")
    assert hasattr(result, "node_count")
    assert hasattr(result, "edge_count")
    assert hasattr(result, "checks_passed")

    # Check types
    assert isinstance(result.valid, bool)
    assert isinstance(result.errors, list)
    assert isinstance(result.warnings, list)
    assert isinstance(result.node_count, int)
    assert isinstance(result.edge_count, int)
    assert isinstance(result.checks_passed, dict)


def test_validate_graph_comprehensive_multiple_errors() -> None:
    """Test comprehensive validation collects multiple errors."""
    graph = _create_test_graph_with_subsystems()
    graph.nodes["S-001"] = OSTCNode(
        id="S-001", type="specification", title="Spec 1", subsystem="core"
    )
    graph.nodes["O-001"] = OSTCNode(
        id="O-001", type="outcome", title="Outcome 1", subsystem="core"
    )

    # Error 1: Edge to non-existent node
    graph.edges.append(Edge("S-001", "O-999", "implements"))
    # Error 2: Self-loop
    graph.edges.append(Edge("O-001", "O-001", "depends_on"))
    # Error 3: Invalid edge type
    graph.edges.append(Edge("O-001", "S-001", "implements"))

    result = validate_graph_comprehensive(graph)

    assert not result.valid
    assert len(result.errors) >= 3


def test_validate_graph_comprehensive_checks_passed() -> None:
    """Test checks_passed dict contains expected check names."""
    graph = _create_test_graph_with_subsystems()
    graph.nodes["O-001"] = OSTCNode(
        id="O-001", type="outcome", title="Outcome 1", subsystem="core"
    )

    result = validate_graph_comprehensive(graph)

    # Expected check names
    assert "edge_validation" in result.checks_passed
    assert "subsystem_hierarchy" in result.checks_passed
    assert "no_duplicate_ids" in result.checks_passed

    # All checks should pass for valid simple graph
    assert all(result.checks_passed.values())
