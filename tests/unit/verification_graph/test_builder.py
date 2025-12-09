"""Tests for verification graph builder.

TDD tests for S-055: Verification Graph Generation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

import jig
from jig.impl_graph.graph import Graph


@jig.verifies("S-055")
def test_build_verification_graph_creates_ndjson(tmp_path: Path) -> None:
    """Builder creates verification-graph.ndjson file."""
    from jig.verification_graph.builder import build_verification_graph

    # Create a minimal test file
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "test_example.py"
    test_file.write_text("""\
def test_simple():
    assert True
""")

    output_path = tmp_path / "jig" / "generated" / "verification-graph.ndjson"

    build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        output_path=output_path,
        include_timestamp=False,
    )

    assert output_path.exists()


@jig.verifies("S-055")
def test_build_verification_graph_has_metadata(tmp_path: Path) -> None:
    """First line is metadata with node_count, edge_count."""
    from jig.verification_graph.builder import build_verification_graph

    # Create test files with verifies decorators
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "test_example.py"
    test_file.write_text("""\
import jig

@jig.verifies("S-001")
def test_one():
    assert True

def test_two():
    assert True
""")

    output_path = tmp_path / "verification-graph.ndjson"

    build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        output_path=output_path,
        include_timestamp=False,
    )

    # Read first line and parse metadata
    with output_path.open("r") as f:
        first_line = f.readline()
    metadata = json.loads(first_line)

    assert "_meta" in metadata
    assert "node_count" in metadata["_meta"]
    assert "edge_count" in metadata["_meta"]
    assert metadata["_meta"]["node_count"] == 2  # Two tests
    assert metadata["_meta"]["edge_count"] == 1  # One verifies edge


@jig.verifies("S-055")
def test_build_verification_graph_nodes_sorted(tmp_path: Path) -> None:
    """Nodes are sorted alphabetically by ID."""
    from jig.verification_graph.builder import build_verification_graph

    # Create test file with tests in non-alphabetical order
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "test_example.py"
    test_file.write_text("""\
def test_zebra():
    assert True

def test_alpha():
    assert True

def test_middle():
    assert True
""")

    output_path = tmp_path / "verification-graph.ndjson"

    build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        output_path=output_path,
        include_timestamp=False,
    )

    # Parse all lines and extract node IDs
    with output_path.open("r") as f:
        lines = f.readlines()

    nodes = [json.loads(line) for line in lines if "type" in json.loads(line) and json.loads(line).get("type") == "test"]
    node_ids = [n["id"] for n in nodes]

    # Should be sorted alphabetically
    assert node_ids == sorted(node_ids)
    assert "T-test_example.test_alpha" in node_ids
    assert "T-test_example.test_middle" in node_ids
    assert "T-test_example.test_zebra" in node_ids


@jig.verifies("S-055")
def test_build_verification_graph_edges_sorted(tmp_path: Path) -> None:
    """Edges are sorted by (source, target, type)."""
    from jig.verification_graph.builder import build_verification_graph

    # Create test file with multiple verifies in non-alphabetical order
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "test_example.py"
    test_file.write_text("""\
import jig

@jig.verifies("S-003")
def test_zebra():
    assert True

@jig.verifies("S-001")
def test_alpha():
    assert True

@jig.verifies("S-002")
def test_middle():
    assert True
""")

    output_path = tmp_path / "verification-graph.ndjson"

    build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        output_path=output_path,
        include_timestamp=False,
    )

    # Parse all lines and extract edges
    with output_path.open("r") as f:
        lines = f.readlines()

    edges = [json.loads(line) for line in lines if "source" in json.loads(line)]
    edge_tuples = [(e["source"], e["target"], e["type"]) for e in edges]

    # Should be sorted by (source, target, type)
    assert edge_tuples == sorted(edge_tuples)


@jig.verifies("S-055")
def test_build_verification_graph_deterministic(tmp_path: Path) -> None:
    """Same input produces identical output."""
    from jig.verification_graph.builder import build_verification_graph

    # Create test files
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "test_example.py"
    test_file.write_text("""\
import jig

@jig.verifies("S-001")
def test_one():
    assert True

@jig.verifies("S-002", "S-003")
def test_two():
    assert True
""")

    output_path1 = tmp_path / "output1.ndjson"
    output_path2 = tmp_path / "output2.ndjson"

    # Build twice
    build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        output_path=output_path1,
        include_timestamp=False,
    )
    build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        output_path=output_path2,
        include_timestamp=False,
    )

    # Should be identical
    content1 = output_path1.read_text()
    content2 = output_path2.read_text()
    assert content1 == content2


@jig.verifies("S-055")
def test_build_verification_graph_returns_graph(tmp_path: Path) -> None:
    """Builder returns existing Graph class from impl_graph."""
    from jig.verification_graph.builder import build_verification_graph

    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "test_example.py"
    test_file.write_text("""\
import jig

@jig.verifies("S-001")
def test_one():
    assert True
""")

    output_path = tmp_path / "verification-graph.ndjson"

    result = build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        output_path=output_path,
        include_timestamp=False,
    )

    # Should return a Graph instance
    assert isinstance(result, Graph)
    assert result.node_count() == 1
    assert result.edge_count() == 1


@jig.verifies("S-055")
def test_build_verification_graph_includes_tests_without_verifies(tmp_path: Path) -> None:
    """Includes all discovered tests, even those without @jig.verifies."""
    from jig.verification_graph.builder import build_verification_graph

    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "test_example.py"
    test_file.write_text("""\
import jig

@jig.verifies("S-001")
def test_with_verifies():
    assert True

def test_without_verifies():
    assert True
""")

    output_path = tmp_path / "verification-graph.ndjson"

    result = build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        output_path=output_path,
        include_timestamp=False,
    )

    # Should have 2 nodes (both tests)
    assert result.node_count() == 2
    # Should have 1 edge (only the verifies)
    assert result.edge_count() == 1

    # Verify file content has both nodes
    with output_path.open("r") as f:
        content = f.read()

    assert "T-test_example.test_with_verifies" in content
    assert "T-test_example.test_without_verifies" in content


@jig.verifies("S-055")
def test_build_verification_graph_creates_verifies_edges(tmp_path: Path) -> None:
    """Creates T→S edges with type 'verifies'."""
    from jig.verification_graph.builder import build_verification_graph

    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "test_example.py"
    test_file.write_text("""\
import jig

@jig.verifies("S-001", "S-002")
def test_multiple():
    assert True
""")

    output_path = tmp_path / "verification-graph.ndjson"

    build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        output_path=output_path,
        include_timestamp=False,
    )

    # Parse edges from output
    with output_path.open("r") as f:
        lines = f.readlines()

    edges = [json.loads(line) for line in lines if "source" in json.loads(line)]

    # Should have 2 edges (T→S-001 and T→S-002)
    assert len(edges) == 2

    # All edges should be type "verifies"
    for edge in edges:
        assert edge["type"] == "verifies"
        assert edge["source"] == "T-test_example.test_multiple"
        assert edge["target"] in ["S-001", "S-002"]


@jig.verifies("S-055")
def test_build_verification_graph_default_output_path(tmp_path: Path) -> None:
    """Uses default output path if not specified."""
    from jig.verification_graph.builder import build_verification_graph

    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "test_example.py"
    test_file.write_text("""\
def test_simple():
    assert True
""")

    # Build without specifying output_path
    build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        include_timestamp=False,
    )

    # Should create default path
    default_path = tmp_path / "jig" / "generated" / "verification-graph.ndjson"
    assert default_path.exists()


@jig.verifies("S-055")
def test_build_verification_graph_empty_test_dir(tmp_path: Path) -> None:
    """Handles empty test directory gracefully."""
    from jig.verification_graph.builder import build_verification_graph

    test_dir = tmp_path / "tests"
    test_dir.mkdir()  # Empty directory

    output_path = tmp_path / "verification-graph.ndjson"

    result = build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        output_path=output_path,
        include_timestamp=False,
    )

    assert result.node_count() == 0
    assert result.edge_count() == 0
    assert output_path.exists()

    # Metadata should have zero counts
    with output_path.open("r") as f:
        first_line = f.readline()
    metadata = json.loads(first_line)
    assert metadata["_meta"]["node_count"] == 0
    assert metadata["_meta"]["edge_count"] == 0


@jig.verifies("S-055")
def test_build_verification_graph_multiple_files(tmp_path: Path) -> None:
    """Handles multiple test files."""
    from jig.verification_graph.builder import build_verification_graph

    test_dir = tmp_path / "tests"
    test_dir.mkdir()

    # Create multiple test files
    (test_dir / "test_alpha.py").write_text("""\
import jig

@jig.verifies("S-001")
def test_alpha():
    assert True
""")
    (test_dir / "test_beta.py").write_text("""\
import jig

@jig.verifies("S-002")
def test_beta():
    assert True
""")

    output_path = tmp_path / "verification-graph.ndjson"

    result = build_verification_graph(
        project_root=tmp_path,
        test_dir=test_dir,
        output_path=output_path,
        include_timestamp=False,
    )

    assert result.node_count() == 2
    assert result.edge_count() == 2

    # Verify content
    with output_path.open("r") as f:
        content = f.read()
    assert "T-test_alpha.test_alpha" in content
    assert "T-test_beta.test_beta" in content
