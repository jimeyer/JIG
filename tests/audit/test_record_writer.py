"""Tests for record writer functionality.

These tests verify S-067: Coverage Record Format.
"""

import json
from datetime import date
from pathlib import Path

import jig

from jig.audit.coverage import TFEdge
from jig.audit.record_writer import (
    _build_edge_record,
    _load_function_hashes,
    _load_test_hashes,
    cleanup_coverage_file,
    write_coverage_record,
)


def _create_mock_impl_graph(path: Path, functions: list[dict]) -> None:
    """Create a mock implementation graph file."""
    with open(path, "w") as f:
        f.write(json.dumps({"_meta": {"version": "1.0"}}) + "\n")
        for func in functions:
            node = {"type": "function", **func}
            f.write(json.dumps(node) + "\n")


def _create_mock_verify_graph(path: Path, tests: list[dict]) -> None:
    """Create a mock verification graph file."""
    with open(path, "w") as f:
        f.write(json.dumps({"_meta": {"version": "1.0"}}) + "\n")
        for test in tests:
            node = {"type": "test", **test}
            f.write(json.dumps(node) + "\n")


@jig.verifies("S-067")
def test_load_function_hashes(tmp_path):
    """_load_function_hashes extracts id->jig_hash mapping."""
    impl_graph = tmp_path / "impl-graph.ndjson"
    _create_mock_impl_graph(
        impl_graph,
        [
            {"id": "F-module.func_a", "jig_hash": "abc123"},
            {"id": "F-module.func_b", "jig_hash": "def456"},
        ],
    )

    hashes = _load_function_hashes(impl_graph)

    assert hashes == {
        "F-module.func_a": "abc123",
        "F-module.func_b": "def456",
    }


@jig.verifies("S-067")
def test_load_function_hashes_ignores_non_functions(tmp_path):
    """_load_function_hashes ignores non-function nodes."""
    impl_graph = tmp_path / "impl-graph.ndjson"
    with open(impl_graph, "w") as f:
        f.write(json.dumps({"_meta": {"version": "1.0"}}) + "\n")
        f.write(
            json.dumps(
                {"type": "function", "id": "F-module.func", "jig_hash": "abc123"}
            )
            + "\n"
        )
        f.write(
            json.dumps({"type": "class", "id": "C-module.Class", "jig_hash": "xyz789"})
            + "\n"
        )

    hashes = _load_function_hashes(impl_graph)

    assert hashes == {"F-module.func": "abc123"}
    assert "C-module.Class" not in hashes


@jig.verifies("S-067")
def test_load_test_hashes(tmp_path):
    """_load_test_hashes extracts id->jig_hash mapping."""
    verify_graph = tmp_path / "verify-graph.ndjson"
    _create_mock_verify_graph(
        verify_graph,
        [
            {"id": "T-test_module.test_a", "jig_hash": "test123"},
            {"id": "T-test_module.test_b", "jig_hash": "test456"},
        ],
    )

    hashes = _load_test_hashes(verify_graph)

    assert hashes == {
        "T-test_module.test_a": "test123",
        "T-test_module.test_b": "test456",
    }


@jig.verifies("S-067")
def test_build_edge_record():
    """_build_edge_record creates correct record structure."""
    edge = TFEdge(test_id="T-test_foo.test_bar", function_id="F-module.func")
    function_hashes = {"F-module.func": "func_hash"}
    test_hashes = {"T-test_foo.test_bar": "test_hash"}

    record = _build_edge_record(edge, function_hashes, test_hashes)

    assert record == {
        "edge": "T->F",
        "from": {"id": "T-test_foo.test_bar", "jig_hash": "test_hash"},
        "to": {"id": "F-module.func", "jig_hash": "func_hash"},
        "result": "covered",
    }


@jig.verifies("S-067")
def test_build_edge_record_missing_hash():
    """_build_edge_record handles missing hashes gracefully."""
    edge = TFEdge(test_id="T-unknown.test", function_id="F-unknown.func")
    function_hashes = {}
    test_hashes = {}

    record = _build_edge_record(edge, function_hashes, test_hashes)

    assert record["from"]["jig_hash"] == ""
    assert record["to"]["jig_hash"] == ""


@jig.verifies("S-067")
def test_write_coverage_record_creates_file(tmp_path):
    """write_coverage_record creates NDJSON file."""
    output_dir = tmp_path / "records"
    impl_graph = tmp_path / "impl-graph.ndjson"
    verify_graph = tmp_path / "verify-graph.ndjson"

    _create_mock_impl_graph(impl_graph, [{"id": "F-module.func", "jig_hash": "fh123"}])
    _create_mock_verify_graph(
        verify_graph, [{"id": "T-test_mod.test_x", "jig_hash": "th456"}]
    )

    edges = [TFEdge(test_id="T-test_mod.test_x", function_id="F-module.func")]

    result_path = write_coverage_record(
        edges,
        output_dir,
        impl_graph,
        verify_graph,
        record_date=date(2025, 12, 16),
    )

    assert result_path.exists()
    assert result_path.name == "coverage-2025-12-16.ndjson"


@jig.verifies("S-067")
def test_write_coverage_record_valid_json(tmp_path):
    """write_coverage_record produces valid JSON on each line."""
    output_dir = tmp_path / "records"
    impl_graph = tmp_path / "impl-graph.ndjson"
    verify_graph = tmp_path / "verify-graph.ndjson"

    _create_mock_impl_graph(impl_graph, [{"id": "F-module.func", "jig_hash": "fh123"}])
    _create_mock_verify_graph(
        verify_graph, [{"id": "T-test_mod.test_x", "jig_hash": "th456"}]
    )

    edges = [TFEdge(test_id="T-test_mod.test_x", function_id="F-module.func")]

    result_path = write_coverage_record(
        edges,
        output_dir,
        impl_graph,
        verify_graph,
        record_date=date(2025, 12, 16),
    )

    # Read and parse each line
    with open(result_path) as f:
        lines = f.readlines()

    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["edge"] == "T->F"
    assert record["from"]["id"] == "T-test_mod.test_x"
    assert record["to"]["id"] == "F-module.func"


@jig.verifies("S-067")
def test_write_coverage_record_sorted(tmp_path):
    """write_coverage_record sorts by from.id then to.id."""
    output_dir = tmp_path / "records"
    impl_graph = tmp_path / "impl-graph.ndjson"
    verify_graph = tmp_path / "verify-graph.ndjson"

    _create_mock_impl_graph(
        impl_graph,
        [
            {"id": "F-module.func_a", "jig_hash": "ha"},
            {"id": "F-module.func_b", "jig_hash": "hb"},
        ],
    )
    _create_mock_verify_graph(
        verify_graph,
        [
            {"id": "T-test_z.test_last", "jig_hash": "hz"},
            {"id": "T-test_a.test_first", "jig_hash": "ha"},
        ],
    )

    # Create edges in unsorted order
    edges = [
        TFEdge(test_id="T-test_z.test_last", function_id="F-module.func_b"),
        TFEdge(test_id="T-test_a.test_first", function_id="F-module.func_b"),
        TFEdge(test_id="T-test_z.test_last", function_id="F-module.func_a"),
        TFEdge(test_id="T-test_a.test_first", function_id="F-module.func_a"),
    ]

    result_path = write_coverage_record(
        edges,
        output_dir,
        impl_graph,
        verify_graph,
        record_date=date(2025, 12, 16),
    )

    # Read records
    with open(result_path) as f:
        records = [json.loads(line) for line in f]

    # Verify sorted order
    assert len(records) == 4

    # Should be sorted by from.id first, then to.id
    expected_order = [
        ("T-test_a.test_first", "F-module.func_a"),
        ("T-test_a.test_first", "F-module.func_b"),
        ("T-test_z.test_last", "F-module.func_a"),
        ("T-test_z.test_last", "F-module.func_b"),
    ]

    for i, (from_id, to_id) in enumerate(expected_order):
        assert records[i]["from"]["id"] == from_id
        assert records[i]["to"]["id"] == to_id


@jig.verifies("S-067")
def test_write_coverage_record_includes_jig_hash(tmp_path):
    """write_coverage_record includes jig_hash for both from and to."""
    output_dir = tmp_path / "records"
    impl_graph = tmp_path / "impl-graph.ndjson"
    verify_graph = tmp_path / "verify-graph.ndjson"

    _create_mock_impl_graph(
        impl_graph, [{"id": "F-module.func", "jig_hash": "func_hash_123"}]
    )
    _create_mock_verify_graph(
        verify_graph, [{"id": "T-test_mod.test_x", "jig_hash": "test_hash_456"}]
    )

    edges = [TFEdge(test_id="T-test_mod.test_x", function_id="F-module.func")]

    result_path = write_coverage_record(
        edges,
        output_dir,
        impl_graph,
        verify_graph,
        record_date=date(2025, 12, 16),
    )

    with open(result_path) as f:
        record = json.loads(f.readline())

    assert record["from"]["jig_hash"] == "test_hash_456"
    assert record["to"]["jig_hash"] == "func_hash_123"


@jig.verifies("S-067")
def test_write_coverage_record_grepable(tmp_path):
    """write_coverage_record output is grep-able for test and function IDs."""
    output_dir = tmp_path / "records"
    impl_graph = tmp_path / "impl-graph.ndjson"
    verify_graph = tmp_path / "verify-graph.ndjson"

    _create_mock_impl_graph(
        impl_graph,
        [
            {"id": "F-module.func_a", "jig_hash": "ha"},
            {"id": "F-module.func_b", "jig_hash": "hb"},
        ],
    )
    _create_mock_verify_graph(
        verify_graph,
        [
            {"id": "T-test_mod.test_x", "jig_hash": "hx"},
            {"id": "T-test_mod.test_y", "jig_hash": "hy"},
        ],
    )

    edges = [
        TFEdge(test_id="T-test_mod.test_x", function_id="F-module.func_a"),
        TFEdge(test_id="T-test_mod.test_x", function_id="F-module.func_b"),
        TFEdge(test_id="T-test_mod.test_y", function_id="F-module.func_a"),
    ]

    result_path = write_coverage_record(
        edges, output_dir, impl_graph, verify_graph, record_date=date(2025, 12, 16)
    )

    # Read file content
    content = result_path.read_text()

    # Grep for test ID should find relevant lines
    test_x_lines = [line for line in content.splitlines() if "T-test_mod.test_x" in line]
    assert len(test_x_lines) == 2

    # Grep for function ID should find relevant lines
    func_a_lines = [line for line in content.splitlines() if "F-module.func_a" in line]
    assert len(func_a_lines) == 2


@jig.verifies("S-067")
def test_cleanup_coverage_file_deletes(tmp_path):
    """cleanup_coverage_file deletes existing .coverage file."""
    coverage_file = tmp_path / ".coverage"
    coverage_file.write_text("mock coverage data")

    assert coverage_file.exists()

    result = cleanup_coverage_file(coverage_file)

    assert result is True
    assert not coverage_file.exists()


@jig.verifies("S-067")
def test_cleanup_coverage_file_nonexistent(tmp_path):
    """cleanup_coverage_file handles non-existent file gracefully."""
    coverage_file = tmp_path / ".coverage"

    assert not coverage_file.exists()

    result = cleanup_coverage_file(coverage_file)

    assert result is False


@jig.verifies("S-067")
def test_write_coverage_record_creates_directory(tmp_path):
    """write_coverage_record creates output directory if missing."""
    output_dir = tmp_path / "deeply" / "nested" / "records"
    impl_graph = tmp_path / "impl-graph.ndjson"
    verify_graph = tmp_path / "verify-graph.ndjson"

    _create_mock_impl_graph(impl_graph, [{"id": "F-module.func", "jig_hash": "fh"}])
    _create_mock_verify_graph(verify_graph, [{"id": "T-test.test_x", "jig_hash": "th"}])

    edges = [TFEdge(test_id="T-test.test_x", function_id="F-module.func")]

    assert not output_dir.exists()

    result_path = write_coverage_record(
        edges, output_dir, impl_graph, verify_graph, record_date=date(2025, 12, 16)
    )

    assert output_dir.exists()
    assert result_path.exists()


@jig.verifies("S-067")
def test_write_coverage_record_uses_today_by_default(tmp_path):
    """write_coverage_record uses today's date when not specified."""
    output_dir = tmp_path / "records"
    impl_graph = tmp_path / "impl-graph.ndjson"
    verify_graph = tmp_path / "verify-graph.ndjson"

    _create_mock_impl_graph(impl_graph, [{"id": "F-module.func", "jig_hash": "fh"}])
    _create_mock_verify_graph(verify_graph, [{"id": "T-test.test_x", "jig_hash": "th"}])

    edges = [TFEdge(test_id="T-test.test_x", function_id="F-module.func")]

    result_path = write_coverage_record(edges, output_dir, impl_graph, verify_graph)

    # Should use today's date
    today = date.today()
    expected_name = f"coverage-{today.isoformat()}.ndjson"
    assert result_path.name == expected_name
