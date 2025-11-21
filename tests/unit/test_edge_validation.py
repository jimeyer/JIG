# @jig T-JIGY-009 verifies:S-JIGY-004 subsystem:jigy-tool
"""Unit tests for edge validation and orphan detection (WU4)."""

from pathlib import Path

import pytest

from jig.core.graph import Graph, Edge
from jig.core.parser import OSTCNode
from jig.core.validator import ValidationResult, validate_edges


# @jig T-JIGY-010 verifies:S-JIGY-004 subsystem:jigy-tool
def test_validate_edge_target_exists() -> None:
    """Test validation detects edges to non-existent nodes."""
    graph = Graph()
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    
    # Valid edge
    graph.edges.append(Edge("S-001", "O-001", "implements"))
    
    # Invalid edge - target doesn't exist
    graph.edges.append(Edge("S-001", "O-999", "implements"))
    
    result = validate_edges(graph)
    
    assert not result.valid
    assert len(result.errors) == 1
    assert "O-999" in result.errors[0]
    assert "does not exist" in result.errors[0].lower()


def test_validate_edge_source_exists() -> None:
    """Test validation detects edges from non-existent nodes."""
    graph = Graph()
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    
    # Invalid edge - source doesn't exist
    graph.edges.append(Edge("S-999", "O-001", "implements"))
    
    result = validate_edges(graph)
    
    assert not result.valid
    assert len(result.errors) == 1
    assert "S-999" in result.errors[0]
    assert "does not exist" in result.errors[0].lower()


def test_validate_edge_type_implements_s_to_o() -> None:
    """Test 'implements' edge from S to O is valid."""
    graph = Graph()
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    graph.edges.append(Edge("S-001", "O-001", "implements"))
    
    result = validate_edges(graph)
    
    assert result.valid
    assert len(result.errors) == 0


def test_validate_edge_type_implements_c_to_s() -> None:
    """Test 'implements' edge from C to S is valid."""
    graph = Graph()
    graph.nodes["C-001"] = OSTCNode(id="C-001", type="code", title="Code 1")
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.edges.append(Edge("C-001", "S-001", "implements"))
    
    result = validate_edges(graph)
    
    assert result.valid
    assert len(result.errors) == 0


def test_validate_edge_type_implements_invalid() -> None:
    """Test 'implements' edge with invalid source/target types."""
    graph = Graph()
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    graph.nodes["O-002"] = OSTCNode(id="O-002", type="outcome", title="Outcome 2")
    
    # O->O is not valid for 'implements'
    graph.edges.append(Edge("O-001", "O-002", "implements"))
    
    result = validate_edges(graph)
    
    assert not result.valid
    assert len(result.errors) == 1
    assert "implements" in result.errors[0].lower()
    assert "outcome" in result.errors[0].lower()


def test_validate_edge_type_verifies_t_to_s() -> None:
    """Test 'verifies' edge from T to S is valid."""
    graph = Graph()
    graph.nodes["T-001"] = OSTCNode(id="T-001", type="test", title="Test 1")
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.edges.append(Edge("T-001", "S-001", "verifies"))
    
    result = validate_edges(graph)
    
    assert result.valid
    assert len(result.errors) == 0


def test_validate_edge_type_verifies_t_to_o() -> None:
    """Test 'verifies' edge from T to O is valid."""
    graph = Graph()
    graph.nodes["T-001"] = OSTCNode(id="T-001", type="test", title="Test 1")
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    graph.edges.append(Edge("T-001", "O-001", "verifies"))
    
    result = validate_edges(graph)
    
    assert result.valid
    assert len(result.errors) == 0


def test_validate_edge_type_verifies_invalid() -> None:
    """Test 'verifies' edge with invalid source type."""
    graph = Graph()
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    
    # S->O with 'verifies' is invalid (should be T->S or T->O)
    graph.edges.append(Edge("S-001", "O-001", "verifies"))
    
    result = validate_edges(graph)
    
    assert not result.valid
    assert len(result.errors) == 1
    assert "verifies" in result.errors[0].lower()


def test_validate_edge_type_satisfies_s_to_o() -> None:
    """Test 'satisfies' edge from S to O is valid."""
    graph = Graph()
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    graph.edges.append(Edge("S-001", "O-001", "satisfies"))
    
    result = validate_edges(graph)
    
    assert result.valid
    assert len(result.errors) == 0


def test_validate_edge_type_depends_on_any_to_any() -> None:
    """Test 'depends_on' edge allows any node types."""
    graph = Graph()
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    graph.nodes["O-002"] = OSTCNode(id="O-002", type="outcome", title="Outcome 2")
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.nodes["C-001"] = OSTCNode(id="C-001", type="code", title="Code 1")
    
    # depends_on allows any combinations
    graph.edges.append(Edge("O-001", "O-002", "depends_on"))
    graph.edges.append(Edge("S-001", "O-001", "depends_on"))
    graph.edges.append(Edge("C-001", "S-001", "depends_on"))
    
    result = validate_edges(graph)
    
    assert result.valid
    assert len(result.errors) == 0


def test_validate_no_self_loops() -> None:
    """Test validation detects self-loops."""
    graph = Graph()
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    
    # Self-loop
    graph.edges.append(Edge("S-001", "S-001", "depends_on"))
    
    result = validate_edges(graph)
    
    assert not result.valid
    assert len(result.errors) == 1
    assert "self-loop" in result.errors[0].lower()
    assert "S-001" in result.errors[0]


def test_find_orphaned_nodes_basic() -> None:
    """Test orphan detection for nodes with no edges."""
    graph = Graph()
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.nodes["S-002"] = OSTCNode(id="S-002", type="specification", title="Spec 2")
    
    # S-001 implements O-001
    graph.edges.append(Edge("S-001", "O-001", "implements"))
    
    # S-002 is orphaned (no edges)
    orphans = graph.find_orphaned_nodes()
    
    assert len(orphans) == 1
    assert "S-002" in orphans


def test_find_orphaned_nodes_all_connected() -> None:
    """Test orphan detection when all nodes are connected."""
    graph = Graph()
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.nodes["C-001"] = OSTCNode(id="C-001", type="code", title="Code 1")
    
    graph.edges.append(Edge("S-001", "O-001", "implements"))
    graph.edges.append(Edge("C-001", "S-001", "implements"))
    
    orphans = graph.find_orphaned_nodes()
    
    assert len(orphans) == 0


def test_find_orphaned_nodes_empty_graph() -> None:
    """Test orphan detection on empty graph."""
    graph = Graph()
    
    orphans = graph.find_orphaned_nodes()
    
    assert len(orphans) == 0


def test_validate_edges_multiple_errors() -> None:
    """Test validation reports multiple errors."""
    graph = Graph()
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    
    # Multiple invalid edges
    graph.edges.append(Edge("S-001", "O-999", "implements"))  # Missing target
    graph.edges.append(Edge("S-999", "O-001", "implements"))  # Missing source
    graph.edges.append(Edge("O-001", "S-001", "verifies"))    # Invalid type
    graph.edges.append(Edge("S-001", "S-001", "depends_on"))  # Self-loop
    
    result = validate_edges(graph)
    
    assert not result.valid
    assert len(result.errors) == 4


def test_validate_edges_with_warnings() -> None:
    """Test validation can return warnings for orphaned nodes."""
    graph = Graph()
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.nodes["S-002"] = OSTCNode(id="S-002", type="specification", title="Spec 2 (orphaned)")
    
    graph.edges.append(Edge("S-001", "O-001", "implements"))
    
    result = validate_edges(graph, check_orphans=True)
    
    assert result.valid  # No errors
    assert len(result.warnings) == 1
    assert "S-002" in result.warnings[0]
    assert "orphan" in result.warnings[0].lower()


def test_validate_edges_empty_graph() -> None:
    """Test validation on empty graph."""
    graph = Graph()
    
    result = validate_edges(graph)
    
    assert result.valid
    assert len(result.errors) == 0
    assert len(result.warnings) == 0


def test_validate_edge_type_unknown() -> None:
    """Test validation handles unknown edge types gracefully."""
    graph = Graph()
    graph.nodes["S-001"] = OSTCNode(id="S-001", type="specification", title="Spec 1")
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    
    # Unknown edge type
    graph.edges.append(Edge("S-001", "O-001", "unknown_type"))
    
    result = validate_edges(graph)
    
    # Should warn about unknown type but not error
    assert result.valid
    assert len(result.warnings) == 1
    assert "unknown_type" in result.warnings[0].lower()


def test_validate_edges_integration(tmp_path: Path) -> None:
    """Test edge validation with real graph loading."""
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    
    # Create outcomes
    outcomes_dir = jig_dir / "outcomes"
    outcomes_dir.mkdir()
    (outcomes_dir / "O-TEST-001.md").write_text("""---
id: O-TEST-001
type: outcome
title: Test outcome
---
""")
    
    # Create specifications with valid and invalid edges
    specs_dir = jig_dir / "specifications"
    specs_dir.mkdir()
    (specs_dir / "S-TEST-001.md").write_text("""---
id: S-TEST-001
type: specification
title: Valid spec
implements:
  - O-TEST-001
---
""")
    
    (specs_dir / "S-TEST-002.md").write_text("""---
id: S-TEST-002
type: specification
title: Spec with broken reference
implements:
  - O-MISSING-999
---
""")
    
    # Load graph
    graph = Graph.load_from_dir(jig_dir)
    
    # Validate edges
    result = validate_edges(graph)
    
    assert not result.valid
    assert len(result.errors) == 1
    assert "O-MISSING-999" in result.errors[0]


def test_validate_edge_type_c_to_o_invalid() -> None:
    """Test that C->O with 'implements' is invalid (should be C->S)."""
    graph = Graph()
    graph.nodes["C-001"] = OSTCNode(id="C-001", type="code", title="Code 1")
    graph.nodes["O-001"] = OSTCNode(id="O-001", type="outcome", title="Outcome 1")
    
    # C should implement S, not O directly
    graph.edges.append(Edge("C-001", "O-001", "implements"))
    
    result = validate_edges(graph)
    
    assert not result.valid
    assert len(result.errors) == 1
    assert "implements" in result.errors[0].lower()
    assert "code" in result.errors[0].lower()


def test_validate_edges_performance(tmp_path: Path) -> None:
    """Test validation performance on larger graph."""
    import time
    
    graph = Graph()
    
    # Create 1000 nodes
    for i in range(500):
        graph.nodes[f"O-TEST-{i:03d}"] = OSTCNode(
            id=f"O-TEST-{i:03d}",
            type="outcome",
            title=f"Outcome {i}"
        )
        graph.nodes[f"S-TEST-{i:03d}"] = OSTCNode(
            id=f"S-TEST-{i:03d}",
            type="specification",
            title=f"Spec {i}"
        )
    
    # Create 500 edges
    for i in range(500):
        graph.edges.append(Edge(f"S-TEST-{i:03d}", f"O-TEST-{i:03d}", "implements"))
    
    # Validate
    start = time.time()
    result = validate_edges(graph)
    elapsed = time.time() - start
    
    assert result.valid
    assert elapsed < 1.0  # Should complete in <1 second

