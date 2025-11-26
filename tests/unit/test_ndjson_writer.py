"""Unit tests for NDJSON writer.

Tests verify that the NDJSON writer produces deterministic, git-friendly
output with correct formatting and ordering.

Verifies S-003: NDJSON output is deterministic and git-friendly.
"""

import json
from pathlib import Path

import pytest

import jig
from jig.impl_graph import Graph, NDJSONWriter, write_ndjson


@pytest.fixture
def sample_graph() -> Graph:
    """Create a sample graph for testing."""
    graph = Graph()

    # Add nodes (intentionally not in alphabetical order)
    graph.add_node(
        {
            "id": "M-mymodule",
            "type": "module",
            "language": "python",
            "file": "mymodule.py",
        }
    )
    graph.add_node(
        {
            "id": "C-mymodule.MyClass",
            "type": "class",
            "language": "python",
            "line": 10,
        }
    )
    graph.add_node(
        {
            "id": "F-mymodule.my_function",
            "type": "function",
            "language": "python",
            "line": 5,
            "implements": ["S-001"],
        }
    )

    # Add edges (intentionally not in sorted order)
    graph.add_edge(
        {"source": "M-mymodule", "target": "C-mymodule.MyClass", "type": "contains"}
    )
    graph.add_edge(
        {"source": "F-mymodule.my_function", "target": "S-001", "type": "implements"}
    )
    graph.add_edge(
        {"source": "M-mymodule", "target": "F-mymodule.my_function", "type": "contains"}
    )

    return graph


@pytest.fixture
def temp_output(tmp_path: Path) -> Path:
    """Create a temporary output file path."""
    return tmp_path / "test-graph.ndjson"


@jig.verifies("S-003")
def test_ndjson_format(sample_graph: Graph, temp_output: Path) -> None:
    """Test that output is valid NDJSON format.

    Verifies S-003: One JSON object per line, no pretty-printing.
    """
    writer = NDJSONWriter(sample_graph)
    writer.write(temp_output, include_timestamp=False)

    # Read the file
    lines = temp_output.read_text().strip().split("\n")

    # Each line should be valid JSON
    for i, line in enumerate(lines):
        try:
            obj = json.loads(line)
            assert isinstance(obj, dict), f"Line {i+1} is not a dict"
        except json.JSONDecodeError as e:
            pytest.fail(f"Line {i+1} is not valid JSON: {e}")

    # Should have metadata + nodes + edges
    expected_lines = 1 + sample_graph.node_count() + sample_graph.edge_count()
    assert len(lines) == expected_lines


@jig.verifies("S-003")
def test_metadata_first(sample_graph: Graph, temp_output: Path) -> None:
    """Test that metadata is on line 1.

    Verifies S-003: Metadata line first.
    """
    writer = NDJSONWriter(sample_graph)
    writer.write(temp_output, include_timestamp=False)

    # Read first line
    first_line = temp_output.read_text().split("\n")[0]
    metadata = json.loads(first_line)

    # Should have _meta key
    assert "_meta" in metadata
    assert "version" in metadata["_meta"]
    assert "node_count" in metadata["_meta"]
    assert "edge_count" in metadata["_meta"]

    # Check counts
    assert metadata["_meta"]["node_count"] == 3
    assert metadata["_meta"]["edge_count"] == 3
    assert metadata["_meta"]["version"] == "1.0"


@jig.verifies("S-003")
def test_nodes_sorted_by_id(sample_graph: Graph, temp_output: Path) -> None:
    """Test that nodes are sorted by ID.

    Verifies S-003: Nodes sorted by ID (stable diffs).
    """
    writer = NDJSONWriter(sample_graph)
    writer.write(temp_output, include_timestamp=False)

    lines = temp_output.read_text().strip().split("\n")

    # Skip metadata line, get nodes (next 3 lines)
    node_lines = lines[1:4]
    node_ids = [json.loads(line)["id"] for line in node_lines]

    # Should be sorted alphabetically
    expected_order = ["C-mymodule.MyClass", "F-mymodule.my_function", "M-mymodule"]
    assert node_ids == expected_order


@jig.verifies("S-003")
def test_edges_after_nodes(sample_graph: Graph, temp_output: Path) -> None:
    """Test that edges come after all nodes.

    Verifies S-003: Edges after all nodes.
    """
    writer = NDJSONWriter(sample_graph)
    writer.write(temp_output, include_timestamp=False)

    lines = temp_output.read_text().strip().split("\n")

    # Metadata is line 0
    # Nodes should be lines 1-3
    # Edges should be lines 4-6

    # Check that lines 1-3 are nodes
    for i in range(1, 4):
        obj = json.loads(lines[i])
        assert "type" in obj
        assert obj["type"] in ["module", "class", "function"]

    # Check that lines 4-6 are edges
    for i in range(4, 7):
        obj = json.loads(lines[i])
        assert "source" in obj
        assert "target" in obj
        assert "type" in obj


@jig.verifies("S-003")
def test_deterministic_output(sample_graph: Graph, tmp_path: Path) -> None:
    """Test that same input produces identical output.

    Verifies S-003: Same input → identical output (deterministic).
    """
    output1 = tmp_path / "graph1.ndjson"
    output2 = tmp_path / "graph2.ndjson"

    # Write same graph twice
    writer = NDJSONWriter(sample_graph)
    writer.write(output1, include_timestamp=False)
    writer.write(output2, include_timestamp=False)

    # Files should be byte-for-byte identical
    content1 = output1.read_bytes()
    content2 = output2.read_bytes()

    assert content1 == content2, "Output is not deterministic"


@jig.verifies("S-003")
def test_sort_keys_in_json(sample_graph: Graph, temp_output: Path) -> None:
    """Test that JSON keys are sorted.

    Verifies S-003: Use sort_keys=True for stable field ordering.
    """
    writer = NDJSONWriter(sample_graph)
    writer.write(temp_output, include_timestamp=False)

    lines = temp_output.read_text().strip().split("\n")

    # Check first node (C-mymodule.MyClass)
    node_line = lines[1]

    # Keys should be in alphabetical order in the JSON string
    # This is enforced by sort_keys=True in json.dumps
    node = json.loads(node_line)

    # Serialize again to check key order
    reserialized = json.dumps(node, sort_keys=True)
    assert node_line == reserialized


@jig.verifies("S-003")
def test_empty_graph(temp_output: Path) -> None:
    """Test handling of empty graph."""
    graph = Graph()
    writer = NDJSONWriter(graph)
    writer.write(temp_output, include_timestamp=False)

    lines = temp_output.read_text().strip().split("\n")

    # Should only have metadata line
    assert len(lines) == 1

    metadata = json.loads(lines[0])
    assert metadata["_meta"]["node_count"] == 0
    assert metadata["_meta"]["edge_count"] == 0


@jig.verifies("S-003")
def test_timestamp_optional(sample_graph: Graph, tmp_path: Path) -> None:
    """Test that timestamp can be excluded for determinism."""
    output1 = tmp_path / "graph1.ndjson"
    output2 = tmp_path / "graph2.ndjson"

    # Write with timestamp
    writer = NDJSONWriter(sample_graph)
    writer.write(output1, include_timestamp=True)

    # Write without timestamp
    writer.write(output2, include_timestamp=False)

    # Read metadata
    meta1 = json.loads(output1.read_text().split("\n")[0])
    meta2 = json.loads(output2.read_text().split("\n")[0])

    # First should have timestamp, second should not
    assert "generated" in meta1["_meta"]
    assert "generated" not in meta2["_meta"]


@jig.verifies("S-003")
def test_output_directory_created(sample_graph: Graph, tmp_path: Path) -> None:
    """Test that output directory is created if it doesn't exist."""
    nested_output = tmp_path / "nested" / "dir" / "graph.ndjson"

    # Directory doesn't exist yet
    assert not nested_output.parent.exists()

    writer = NDJSONWriter(sample_graph)
    writer.write(nested_output, include_timestamp=False)

    # Directory should now exist
    assert nested_output.parent.exists()
    assert nested_output.exists()


@jig.verifies("S-003")
def test_write_ndjson_convenience_function(
    sample_graph: Graph, temp_output: Path
) -> None:
    """Test convenience function for writing NDJSON."""
    write_ndjson(sample_graph, temp_output, include_timestamp=False)

    # Should produce valid NDJSON
    lines = temp_output.read_text().strip().split("\n")
    assert len(lines) > 0

    # First line should be metadata
    metadata = json.loads(lines[0])
    assert "_meta" in metadata


@jig.verifies("S-003")
def test_edge_sorting_deterministic(temp_output: Path) -> None:
    """Test that edges are sorted deterministically."""
    graph = Graph()

    # Add edges in non-sorted order
    graph.add_edge({"source": "Z", "target": "A", "type": "calls"})
    graph.add_edge({"source": "A", "target": "Z", "type": "calls"})
    graph.add_edge({"source": "A", "target": "B", "type": "calls"})
    graph.add_edge({"source": "A", "target": "B", "type": "imports"})

    writer = NDJSONWriter(graph)
    writer.write(temp_output, include_timestamp=False)

    lines = temp_output.read_text().strip().split("\n")

    # Skip metadata, get edges
    edge_lines = lines[1:]
    edges = [json.loads(line) for line in edge_lines]

    # Check order: sorted by (source, target, type)
    expected_order = [
        {"source": "A", "target": "B", "type": "calls"},
        {"source": "A", "target": "B", "type": "imports"},
        {"source": "A", "target": "Z", "type": "calls"},
        {"source": "Z", "target": "A", "type": "calls"},
    ]

    assert edges == expected_order


@jig.verifies("S-003")
def test_round_trip_preserves_data(sample_graph: Graph, temp_output: Path) -> None:
    """Test that writing and reading preserves graph data."""
    # Write graph
    writer = NDJSONWriter(sample_graph)
    writer.write(temp_output, include_timestamp=False)

    # Read back
    lines = temp_output.read_text().strip().split("\n")

    # Skip metadata, parse nodes and edges
    parsed_lines = [json.loads(line) for line in lines[1:]]

    # Separate nodes and edges
    parsed_nodes = [obj for obj in parsed_lines if "source" not in obj]
    parsed_edges = [obj for obj in parsed_lines if "source" in obj]

    # Should have same count
    assert len(parsed_nodes) == sample_graph.node_count()
    assert len(parsed_edges) == sample_graph.edge_count()

    # Check that all original nodes are present (content matches)
    original_node_ids = {n["id"] for n in sample_graph.get_nodes()}
    parsed_node_ids = {n["id"] for n in parsed_nodes}
    assert original_node_ids == parsed_node_ids


@jig.verifies("S-003")
def test_no_extra_whitespace(sample_graph: Graph, temp_output: Path) -> None:
    """Test that there's no extra whitespace or indentation."""
    writer = NDJSONWriter(sample_graph)
    writer.write(temp_output, include_timestamp=False)

    content = temp_output.read_text()

    # No lines should have leading/trailing whitespace (except newline)
    for line in content.split("\n"):
        if line:  # Skip empty lines at end
            # Line should be pure JSON, no indentation
            assert line == line.strip()
            # Should not contain pretty-printed indentation
            assert "  " not in line  # No double spaces (indication of indent)
