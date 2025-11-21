# @jig T-JIGY-004 verifies:S-JIGY-002 subsystem:jigy-tool
"""Unit tests for graph-index.yaml loading (WU2)."""

from pathlib import Path

import pytest

from jig.core.graph import Graph


# @jig T-JIGY-005 verifies:S-JIGY-002 subsystem:jigy-tool
def test_load_graph_index_with_ct_nodes(tmp_path: Path) -> None:
    """Test loading C/T nodes from graph-index.yaml."""
    # Create minimal jig directory structure
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    
    # Create one O node in markdown
    outcomes_dir = jig_dir / "outcomes"
    outcomes_dir.mkdir()
    outcome_file = outcomes_dir / "O-TEST-001.md"
    outcome_file.write_text("""---
id: O-TEST-001
type: outcome
title: Test outcome
---
# Outcome
""")
    
    # Create graph-index.yaml with C/T nodes
    graph_index = jig_dir / "graph-index.yaml"
    graph_index.write_text("""
version: '1.0'
nodes:
  - id: C-TEST-001
    type: code
    title: Test code implementation
    subsystem: test
    file: src/test.py
    line: 42
  - id: T-TEST-001
    type: test
    title: Test case
    subsystem: test
    file: tests/test_test.py
    line: 10
""")
    
    graph = Graph.load_from_dir(jig_dir)
    
    # Should have O node from markdown + C/T nodes from graph-index
    assert len(graph.nodes) == 3
    assert "O-TEST-001" in graph.nodes
    assert "C-TEST-001" in graph.nodes
    assert "T-TEST-001" in graph.nodes
    
    # Check C node details
    c_node = graph.nodes["C-TEST-001"]
    assert c_node.type == "code"
    assert c_node.title == "Test code implementation"
    assert c_node.subsystem == "test"
    
    # Check T node details
    t_node = graph.nodes["T-TEST-001"]
    assert t_node.type == "test"
    assert t_node.title == "Test case"


# @jig T-JIGY-006 verifies:S-JIGY-002 subsystem:jigy-tool
def test_load_node_centric_relationships(tmp_path: Path) -> None:
    """Test extracting relationships from node-centric format in graph-index.yaml."""
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    
    # Create O node in markdown (no relationships)
    outcomes_dir = jig_dir / "outcomes"
    outcomes_dir.mkdir()
    outcome_file = outcomes_dir / "O-TEST-001.md"
    outcome_file.write_text("""---
id: O-TEST-001
type: outcome
title: Test outcome
---
""")
    
    # Create graph-index.yaml with node-centric relationships
    graph_index = jig_dir / "graph-index.yaml"
    graph_index.write_text("""
version: '1.0'
nodes:
  - id: S-TEST-001
    type: specification
    title: Test spec
    subsystem: test
    implements:
      - O-TEST-001
  - id: C-TEST-001
    type: code
    title: Test implementation
    subsystem: test
    implements:
      - S-TEST-001
""")
    
    graph = Graph.load_from_dir(jig_dir)
    
    # Should have edges from node-centric relationships
    assert len(graph.edges) >= 2
    
    # Check S-TEST-001 implements O-TEST-001
    s_edges = [e for e in graph.edges if e.from_node == "S-TEST-001"]
    assert len(s_edges) == 1
    assert s_edges[0].to_node == "O-TEST-001"
    assert s_edges[0].type == "implements"
    
    # Check C-TEST-001 implements S-TEST-001
    c_edges = [e for e in graph.edges if e.from_node == "C-TEST-001"]
    assert len(c_edges) == 1
    assert c_edges[0].to_node == "S-TEST-001"
    assert c_edges[0].type == "implements"


def test_load_edge_centric_format(tmp_path: Path) -> None:
    """Test loading edges from edge-centric format (existing functionality)."""
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    
    # Create nodes in markdown
    outcomes_dir = jig_dir / "outcomes"
    outcomes_dir.mkdir()
    o_file = outcomes_dir / "O-TEST-001.md"
    o_file.write_text("""---
id: O-TEST-001
type: outcome
title: Test outcome
---
""")
    
    specs_dir = jig_dir / "specifications"
    specs_dir.mkdir()
    s_file = specs_dir / "S-TEST-001.md"
    s_file.write_text("""---
id: S-TEST-001
type: specification
title: Test spec
---
""")
    
    # Create graph-index.yaml with edge-centric format
    graph_index = jig_dir / "graph-index.yaml"
    graph_index.write_text("""
version: '1.0'
edges:
  - from: S-TEST-001
    to: O-TEST-001
    type: implements
""")
    
    graph = Graph.load_from_dir(jig_dir)
    
    # Should load edge from edges section
    assert len(graph.edges) == 1
    assert graph.edges[0].from_node == "S-TEST-001"
    assert graph.edges[0].to_node == "O-TEST-001"
    assert graph.edges[0].type == "implements"


def test_merge_markdown_and_graph_index(tmp_path: Path) -> None:
    """Test merging nodes from markdown and graph-index.yaml."""
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    
    # Create O/S nodes in markdown with relationships
    outcomes_dir = jig_dir / "outcomes"
    outcomes_dir.mkdir()
    o_file = outcomes_dir / "O-TEST-001.md"
    o_file.write_text("""---
id: O-TEST-001
type: outcome
title: Outcome from markdown
subsystem: test
---
""")
    
    specs_dir = jig_dir / "specifications"
    specs_dir.mkdir()
    s_file = specs_dir / "S-TEST-001.md"
    s_file.write_text("""---
id: S-TEST-001
type: specification
title: Spec from markdown
subsystem: test
implements:
  - O-TEST-001
---
""")
    
    # Create graph-index.yaml with C/T nodes and their relationships
    graph_index = jig_dir / "graph-index.yaml"
    graph_index.write_text("""
version: '1.0'
nodes:
  - id: C-TEST-001
    type: code
    title: Code from graph-index
    subsystem: test
    implements:
      - S-TEST-001
  - id: T-TEST-001
    type: test
    title: Test from graph-index
    subsystem: test
    verifies:
      - S-TEST-001
""")
    
    graph = Graph.load_from_dir(jig_dir)
    
    # Should have all 4 nodes
    assert len(graph.nodes) == 4
    assert "O-TEST-001" in graph.nodes
    assert "S-TEST-001" in graph.nodes
    assert "C-TEST-001" in graph.nodes
    assert "T-TEST-001" in graph.nodes
    
    # Should have edges from both sources
    assert len(graph.edges) >= 3
    
    # Edge from markdown frontmatter
    s_edges = [e for e in graph.edges if e.from_node == "S-TEST-001"]
    assert len(s_edges) == 1
    
    # Edges from graph-index
    c_edges = [e for e in graph.edges if e.from_node == "C-TEST-001"]
    t_edges = [e for e in graph.edges if e.from_node == "T-TEST-001"]
    assert len(c_edges) == 1
    assert len(t_edges) == 1


def test_markdown_takes_precedence_for_os_nodes(tmp_path: Path) -> None:
    """Test that markdown content takes precedence over graph-index for O/S nodes."""
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    
    # Create S node in markdown with specific content
    specs_dir = jig_dir / "specifications"
    specs_dir.mkdir()
    s_file = specs_dir / "S-TEST-001.md"
    s_file.write_text("""---
id: S-TEST-001
type: specification
title: Title from markdown
subsystem: markdown-subsystem
---
# Body from markdown
""")
    
    # Create graph-index.yaml with conflicting S node data
    graph_index = jig_dir / "graph-index.yaml"
    graph_index.write_text("""
version: '1.0'
nodes:
  - id: S-TEST-001
    type: specification
    title: Title from graph-index (should be ignored)
    subsystem: graph-index-subsystem
""")
    
    graph = Graph.load_from_dir(jig_dir)
    
    # Markdown should take precedence
    s_node = graph.nodes["S-TEST-001"]
    assert s_node.title == "Title from markdown"
    assert s_node.subsystem == "markdown-subsystem"
    assert "Body from markdown" in s_node.body


def test_graph_index_without_nodes_section(tmp_path: Path) -> None:
    """Test graph-index.yaml with only edges section (no nodes)."""
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    
    outcomes_dir = jig_dir / "outcomes"
    outcomes_dir.mkdir()
    o_file = outcomes_dir / "O-TEST-001.md"
    o_file.write_text("""---
id: O-TEST-001
type: outcome
title: Test
---
""")
    
    # graph-index with no nodes section
    graph_index = jig_dir / "graph-index.yaml"
    graph_index.write_text("""
version: '1.0'
edges:
  - from: S-TEST-001
    to: O-TEST-001
    type: implements
""")
    
    graph = Graph.load_from_dir(jig_dir)
    
    # Should load successfully with just markdown nodes
    assert len(graph.nodes) == 1
    assert "O-TEST-001" in graph.nodes


def test_ct_nodes_with_file_and_line(tmp_path: Path) -> None:
    """Test C/T nodes preserve file path and line number metadata."""
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    
    graph_index = jig_dir / "graph-index.yaml"
    graph_index.write_text("""
version: '1.0'
nodes:
  - id: C-TEST-001
    type: code
    title: Code implementation
    file: src/impl.py
    line: 123
  - id: T-TEST-001
    type: test
    title: Test case
    file: tests/test_impl.py
    line: 456
""")
    
    graph = Graph.load_from_dir(jig_dir)
    
    c_node = graph.nodes["C-TEST-001"]
    assert c_node.metadata is not None
    assert c_node.metadata.get("file") == "src/impl.py"
    assert c_node.metadata.get("line") == 123
    
    t_node = graph.nodes["T-TEST-001"]
    assert t_node.metadata is not None
    assert t_node.metadata.get("file") == "tests/test_impl.py"
    assert t_node.metadata.get("line") == 456


def test_dict_mapping_format(tmp_path: Path) -> None:
    """Test loading nodes from dict/mapping format (legacy format)."""
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    
    # Create graph-index.yaml with dict/mapping format
    graph_index = jig_dir / "graph-index.yaml"
    graph_index.write_text("""
version: '1.0'
nodes:
  C-TEST-001:
    type: code
    title: Code from dict format
    subsystem: test
    file: src/code.py
    line: 10
  T-TEST-001:
    type: test
    title: Test from dict format
    subsystem: test
    file: tests/test_code.py
    line: 20
""")
    
    graph = Graph.load_from_dir(jig_dir)
    
    # Should load both nodes
    assert len(graph.nodes) == 2
    assert "C-TEST-001" in graph.nodes
    assert "T-TEST-001" in graph.nodes
    
    # Check node details
    c_node = graph.nodes["C-TEST-001"]
    assert c_node.type == "code"
    assert c_node.title == "Code from dict format"
    assert c_node.metadata.get("file") == "src/code.py"
    
    t_node = graph.nodes["T-TEST-001"]
    assert t_node.type == "test"
    assert t_node.title == "Test from dict format"

