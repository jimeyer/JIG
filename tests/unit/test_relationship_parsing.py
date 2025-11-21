# @jig T-JIGY-001 verifies:S-JIGY-001 subsystem:jigy-tool
"""Unit tests for frontmatter relationship parsing (WU1)."""

from pathlib import Path

import pytest

from jig.core.parser import OSTCNode, parse_ostc_node
from jig.core.graph import Edge
from jig.core.relationships import extract_relationships_from_node, build_edges_from_relationships


# @jig T-JIGY-002 verifies:S-JIGY-001 subsystem:jigy-tool
def test_parse_frontmatter_single_implements(tmp_path: Path) -> None:
    """Test parsing single implements value."""
    node_file = tmp_path / "S-TEST-001.md"
    content = """---
id: S-TEST-001
type: specification
title: "Test spec"
implements: O-TEST-001
---

# Specification
"""
    node_file.write_text(content)
    
    node = parse_ostc_node(node_file)
    
    # Check metadata contains the relationship
    assert "implements" in node.metadata
    # Single value should be kept as-is (or normalized to list by relationship extractor)
    assert node.metadata["implements"] == "O-TEST-001" or node.metadata["implements"] == ["O-TEST-001"]


# @jig T-JIGY-003 verifies:S-JIGY-001 subsystem:jigy-tool
def test_parse_frontmatter_list_implements(tmp_path: Path) -> None:
    """Test parsing list of implements values."""
    node_file = tmp_path / "S-TEST-002.md"
    content = """---
id: S-TEST-002
type: specification
title: "Test spec"
implements:
  - O-TEST-001
  - O-TEST-002
---

# Specification
"""
    node_file.write_text(content)
    
    node = parse_ostc_node(node_file)
    
    assert "implements" in node.metadata
    assert node.metadata["implements"] == ["O-TEST-001", "O-TEST-002"]


def test_extract_relationships_single_value() -> None:
    """Test extracting relationship from node with single value."""
    node = OSTCNode(
        id="S-TEST-001",
        type="specification",
        title="Test",
        metadata={"implements": "O-TEST-001"}
    )
    
    relationships = extract_relationships_from_node(node)
    
    assert "implements" in relationships
    assert relationships["implements"] == ["O-TEST-001"]  # Normalized to list


def test_extract_relationships_list_values() -> None:
    """Test extracting relationships from node with list values."""
    node = OSTCNode(
        id="S-TEST-002",
        type="specification",
        title="Test",
        metadata={"implements": ["O-TEST-001", "O-TEST-002"]}
    )
    
    relationships = extract_relationships_from_node(node)
    
    assert "implements" in relationships
    assert relationships["implements"] == ["O-TEST-001", "O-TEST-002"]


def test_extract_multiple_relationship_types() -> None:
    """Test extracting multiple relationship types from one node."""
    node = OSTCNode(
        id="S-TEST-003",
        type="specification",
        title="Test",
        metadata={
            "implements": ["O-TEST-001", "O-TEST-002"],
            "depends_on": "S-TEST-001",
            "satisfies": "O-TEST-003"
        }
    )
    
    relationships = extract_relationships_from_node(node)
    
    assert relationships["implements"] == ["O-TEST-001", "O-TEST-002"]
    assert relationships["depends_on"] == ["S-TEST-001"]
    assert relationships["satisfies"] == ["O-TEST-003"]


def test_extract_relationships_no_relationships() -> None:
    """Test extracting from node with no relationships."""
    node = OSTCNode(
        id="O-TEST-001",
        type="outcome",
        title="Test",
        metadata={}
    )
    
    relationships = extract_relationships_from_node(node)
    
    assert relationships == {}


def test_extract_relationships_verifies() -> None:
    """Test extracting verifies relationship (for tests)."""
    node = OSTCNode(
        id="T-TEST-001",
        type="test",
        title="Test",
        metadata={"verifies": ["S-TEST-001", "S-TEST-002"]}
    )
    
    relationships = extract_relationships_from_node(node)
    
    assert relationships["verifies"] == ["S-TEST-001", "S-TEST-002"]


def test_build_edges_from_relationships() -> None:
    """Test building edge list from extracted relationships."""
    node_id = "S-TEST-001"
    relationships = {
        "implements": ["O-TEST-001", "O-TEST-002"],
        "depends_on": ["S-OTHER-001"]
    }
    
    edges = build_edges_from_relationships(node_id, relationships)
    
    assert len(edges) == 3
    
    # Check implements edges
    implements_edges = [e for e in edges if e.type == "implements"]
    assert len(implements_edges) == 2
    assert Edge("S-TEST-001", "O-TEST-001", "implements") in implements_edges
    assert Edge("S-TEST-001", "O-TEST-002", "implements") in implements_edges
    
    # Check depends_on edge
    depends_edges = [e for e in edges if e.type == "depends_on"]
    assert len(depends_edges) == 1
    assert Edge("S-TEST-001", "S-OTHER-001", "depends_on") in depends_edges


def test_build_edges_from_empty_relationships() -> None:
    """Test building edges from empty relationships dict."""
    edges = build_edges_from_relationships("S-TEST-001", {})
    
    assert edges == []


def test_parse_inline_list_format(tmp_path: Path) -> None:
    """Test parsing inline list format."""
    node_file = tmp_path / "S-TEST-003.md"
    content = """---
id: S-TEST-003
type: specification
title: "Test spec"
implements: [O-TEST-001, O-TEST-002]
---

# Specification
"""
    node_file.write_text(content)
    
    node = parse_ostc_node(node_file)
    
    assert "implements" in node.metadata
    assert node.metadata["implements"] == ["O-TEST-001", "O-TEST-002"]


def test_extract_all_relationship_types(tmp_path: Path) -> None:
    """Test that all supported relationship types are extracted."""
    node_file = tmp_path / "S-TEST-004.md"
    content = """---
id: S-TEST-004
type: specification
title: "Test with all relationships"
implements: O-TEST-001
satisfies: O-TEST-002
depends_on: S-OTHER-001
verifies: O-TEST-003
---

# Specification
"""
    node_file.write_text(content)
    
    node = parse_ostc_node(node_file)
    relationships = extract_relationships_from_node(node)
    
    # All four relationship types should be extracted
    assert "implements" in relationships
    assert "satisfies" in relationships
    assert "depends_on" in relationships
    assert "verifies" in relationships


def test_build_edges_preserves_edge_type() -> None:
    """Test that edge type is correctly preserved from relationship type."""
    relationships = {
        "implements": ["O-001"],
        "satisfies": ["O-002"],
        "verifies": ["S-001"],
        "depends_on": ["S-002"]
    }
    
    edges = build_edges_from_relationships("S-TEST-001", relationships)
    
    # Check each edge has correct type
    implements_edge = next(e for e in edges if e.to_node == "O-001")
    assert implements_edge.type == "implements"
    
    satisfies_edge = next(e for e in edges if e.to_node == "O-002")
    assert satisfies_edge.type == "satisfies"
    
    verifies_edge = next(e for e in edges if e.to_node == "S-001")
    assert verifies_edge.type == "verifies"
    
    depends_edge = next(e for e in edges if e.to_node == "S-002")
    assert depends_edge.type == "depends_on"

