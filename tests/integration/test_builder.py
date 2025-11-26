"""Integration tests for GraphBuilder.

Tests verify that the graph builder correctly discovers files, analyzes them,
and generates complete graphs.

Verifies S-001, S-002, S-003, S-006: End-to-end graph generation.
"""

import json
from pathlib import Path

import pytest

import jig
from jig.impl_graph import Graph
from jig.impl_graph.builder import GraphBuilder, build_graph

# Get path to test fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "python"


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Create a temporary project root with source files."""
    project_root = tmp_path / "test_project"
    src_dir = project_root / "src"
    src_dir.mkdir(parents=True)

    # Create a simple Python module
    (src_dir / "module1.py").write_text(
        """
import jig

@jig.implements("S-001")
def hello():
    pass

@jig.implements("S-002")
class Greeter:
    def greet(self):
        pass
"""
    )

    # Create another module
    (src_dir / "module2.py").write_text(
        """
def world():
    pass
"""
    )

    return project_root


@jig.verifies("S-001", "S-006")
def test_builder_discovers_files(project_root: Path) -> None:
    """Test that builder discovers Python files."""
    builder = GraphBuilder(project_root)
    files = builder._discover_files([])

    # Should find 2 Python files
    assert len(files) == 2
    assert any("module1.py" in str(f) for f in files)
    assert any("module2.py" in str(f) for f in files)


@jig.verifies("S-001", "S-006")
def test_builder_excludes_patterns(project_root: Path) -> None:
    """Test that builder excludes files matching patterns."""
    # Add a test file
    (project_root / "src" / "test_module.py").write_text("def test(): pass")

    builder = GraphBuilder(project_root)
    files = builder._discover_files(["**/test_*.py"])

    # Should exclude test_module.py
    assert not any("test_module.py" in str(f) for f in files)
    assert len(files) == 2  # Only module1.py and module2.py


@jig.verifies("S-001", "S-002", "S-006")
def test_builder_builds_graph(project_root: Path) -> None:
    """Test that builder builds a complete graph."""
    builder = GraphBuilder(project_root)
    graph = builder.build()

    # Should have nodes and edges
    assert graph.node_count() > 0
    assert graph.edge_count() > 0

    # Check for expected nodes
    nodes = graph.get_nodes()
    node_ids = [n["id"] for n in nodes]

    # Should have modules
    assert any("module1" in nid for nid in node_ids)
    assert any("module2" in nid for nid in node_ids)

    # Should have functions
    assert any("hello" in nid for nid in node_ids)
    assert any("world" in nid for nid in node_ids)

    # Should have class
    assert any("Greeter" in nid for nid in node_ids)


@jig.verifies("S-002")
def test_builder_extracts_decorators(project_root: Path) -> None:
    """Test that builder extracts @jig.implements decorators."""
    builder = GraphBuilder(project_root)
    graph = builder.build()

    # Find nodes with implements field
    nodes_with_implements = [n for n in graph.get_nodes() if "implements" in n]

    # Should have at least 2 (hello function and Greeter class)
    assert len(nodes_with_implements) >= 2


@jig.verifies("S-002")
def test_builder_creates_implementation_edges(project_root: Path) -> None:
    """Test that builder creates implementation edges."""
    builder = GraphBuilder(project_root)
    graph = builder.build()

    # Find implementation edges
    impl_edges = [e for e in graph.get_edges() if e["type"] == "implements"]

    # Should have at least 2 implementation edges
    assert len(impl_edges) >= 2


@jig.verifies("S-003")
def test_builder_writes_ndjson(project_root: Path, tmp_path: Path) -> None:
    """Test that builder writes valid NDJSON."""
    builder = GraphBuilder(project_root)
    builder.build()

    output_path = tmp_path / "graph.ndjson"
    builder.write(output_path, include_timestamp=False)

    # File should exist
    assert output_path.exists()

    # Should be valid NDJSON
    lines = output_path.read_text().strip().split("\n")
    for line in lines:
        json.loads(line)  # Should not raise


@jig.verifies("S-006")
def test_builder_strict_mode_fails_on_parse_error(tmp_path: Path) -> None:
    """Test that strict mode fails on parse errors."""
    # Create a project with invalid Python
    project_root = tmp_path / "bad_project"
    src_dir = project_root / "src"
    src_dir.mkdir(parents=True)

    (src_dir / "bad.py").write_text("def bad(:\n    pass")  # Invalid syntax

    builder = GraphBuilder(project_root)

    # Should raise ParseError in strict mode
    from jig.impl_graph.analyzers.python import ParseError

    with pytest.raises(ParseError):
        builder.build(strict=True)


@jig.verifies("S-006")
def test_builder_lenient_mode_skips_parse_errors(tmp_path: Path) -> None:
    """Test that lenient mode skips files with parse errors."""
    # Create a project with one good and one bad file
    project_root = tmp_path / "mixed_project"
    src_dir = project_root / "src"
    src_dir.mkdir(parents=True)

    (src_dir / "good.py").write_text("def good(): pass")
    (src_dir / "bad.py").write_text("def bad(:\n    pass")  # Invalid syntax

    builder = GraphBuilder(project_root)

    # Should not raise in lenient mode
    graph = builder.build(strict=False)

    # Should still have nodes from good.py
    assert graph.node_count() > 0


@jig.verifies("S-001", "S-003")
def test_build_graph_convenience_function(project_root: Path, tmp_path: Path) -> None:
    """Test the build_graph convenience function."""
    output_path = tmp_path / "graph.ndjson"

    graph = build_graph(
        project_root=project_root,
        output_path=output_path,
        verbose=False,
        strict=True,
        include_timestamp=False,
    )

    # Should return a graph
    assert isinstance(graph, Graph)
    assert graph.node_count() > 0

    # Should write output file
    assert output_path.exists()


@jig.verifies("S-001")
def test_builder_deterministic_file_ordering(project_root: Path) -> None:
    """Test that file discovery is deterministic."""
    builder1 = GraphBuilder(project_root)
    builder2 = GraphBuilder(project_root)

    files1 = builder1._discover_files([])
    files2 = builder2._discover_files([])

    # Should discover files in same order
    assert files1 == files2


@jig.verifies("S-001", "S-002", "S-003")
def test_builder_on_real_fixtures() -> None:
    """Test builder on actual test fixtures."""
    # Use the fixtures directory as source
    project_root = FIXTURES_DIR.parent.parent
    source_dir = FIXTURES_DIR

    builder = GraphBuilder(project_root, source_dir=source_dir)
    graph = builder.build()

    # Should have many nodes (all the fixture files)
    assert graph.node_count() > 20

    # Should have various node types
    nodes = graph.get_nodes()
    node_types = {n["type"] for n in nodes}
    assert "module" in node_types
    assert "class" in node_types
    assert "function" in node_types

    # Should have various edge types
    edges = graph.get_edges()
    edge_types = {e["type"] for e in edges}
    assert "contains" in edge_types
    assert "implements" in edge_types  # From decorator fixtures


@jig.verifies("S-001", "S-003")
def test_builder_empty_source_directory(tmp_path: Path) -> None:
    """Test builder with empty source directory."""
    project_root = tmp_path / "empty_project"
    src_dir = project_root / "src"
    src_dir.mkdir(parents=True)

    builder = GraphBuilder(project_root)
    graph = builder.build()

    # Should have empty graph
    assert graph.node_count() == 0
    assert graph.edge_count() == 0


@jig.verifies("S-003")
def test_builder_uses_relative_paths(tmp_path: Path) -> None:
    """Test that file paths are relative to project root, not absolute."""
    project_root = tmp_path / "test_project"
    src_dir = project_root / "src"
    src_dir.mkdir(parents=True)

    # Create a simple Python file
    (src_dir / "example.py").write_text("def hello(): pass")

    builder = GraphBuilder(project_root)
    graph = builder.build()

    # Get all nodes with file paths
    nodes = graph.get_nodes()
    file_paths = [n["file"] for n in nodes if "file" in n]

    # All paths should be relative (not start with /)
    for path in file_paths:
        assert not path.startswith("/"), f"Path should be relative: {path}"
        assert path.startswith("src/"), f"Path should start with src/: {path}"
