# ABOUTME: Tests for jig.query.node module — config_to_graphs and query_node wrappers.
# ABOUTME: Verifies identifier resolution and graph traversal via the query layer public API.

"""Tests for query.node module.

Tests config_to_graphs path mapping and query_node convenience wrapper
that composes resolve -> traverse -> format into a single call.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

import jig


@dataclass
class _FakePaths:
    """Minimal PathsConfig stand-in for tests."""

    generated: Path
    source: Path = Path("src")
    tests: Path = Path("tests")
    jig_root: Path = Path("jig")
    specifications: Path = Path("jig/specifications")
    outcomes: Path = Path("jig/outcomes")
    bricks: Path = Path("jig/bricks.yaml")
    charter: Path = Path("jig/Charter.md")
    architecture: Path = Path("jig/architecture")


@dataclass
class _FakeConfig:
    """Minimal JigConfig stand-in for tests."""

    paths: _FakePaths
    project_root: Path
    config_file_path: Path | None = None
    has_config_file: bool = False


def _write_ndjson(path: Path, items: list[dict]) -> None:
    """Write a list of dicts as NDJSON."""
    with open(path, "w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")


@pytest.fixture
def graph_dir(tmp_path):
    """Create synthetic graph files and return (generated_dir, config)."""
    generated = tmp_path / "jig" / "generated"
    generated.mkdir(parents=True)

    # Intent graph: Charter -> G-001 -> O-001 -> S-001
    intent_items = [
        {"_meta": {"version": "2.0"}},
        {"id": "Charter", "type": "charter", "file": "jig/Charter.md"},
        {"id": "G-001", "type": "goal", "title": "Goal 1"},
        {"id": "O-001", "type": "outcome", "title": "Outcome 1"},
        {"id": "S-001", "type": "specification", "title": "Spec 1"},
        {"source": "Charter", "target": "G-001", "type": "defines_goal"},
        {"source": "O-001", "target": "G-001", "type": "supports_goal"},
        {"source": "O-001", "target": "S-001", "type": "specifies"},
    ]
    _write_ndjson(generated / "intent-graph.ndjson", intent_items)

    # Impl graph: F-foo implements S-001
    impl_items = [
        {"_meta": {"version": "1.0"}},
        {"id": "F-foo", "type": "function", "file": "src/foo.py", "implements": ["S-001"]},
        {"source": "F-foo", "target": "S-001", "type": "implements"},
    ]
    _write_ndjson(generated / "implementation-graph.ndjson", impl_items)

    # Verify graph: T-bar verifies S-001
    verify_items = [
        {"_meta": {"version": "1.0"}},
        {"id": "T-bar", "type": "test", "file": "tests/test_bar.py", "verifies": ["S-001"]},
        {"source": "T-bar", "target": "S-001", "type": "verifies"},
    ]
    _write_ndjson(generated / "verification-graph.ndjson", verify_items)

    config = _FakeConfig(
        paths=_FakePaths(generated=generated),
        project_root=tmp_path,
    )
    return config


class TestConfigToGraphs:
    """Tests for config_to_graphs path mapping."""

    @jig.verifies("S-111", "S-112")
    def test_returns_correct_paths(self, tmp_path):
        """config_to_graphs maps config.paths.generated to the three graph files + project_root."""
        from jig.query.node import config_to_graphs

        generated = tmp_path / "jig" / "generated"
        config = _FakeConfig(
            paths=_FakePaths(generated=generated),
            project_root=tmp_path,
        )

        result = config_to_graphs(config)

        assert result["intent"] == generated / "intent-graph.ndjson"
        assert result["impl"] == generated / "implementation-graph.ndjson"
        assert result["verify"] == generated / "verification-graph.ndjson"
        assert result["project_root"] == tmp_path

    @jig.verifies("S-111", "S-112")
    def test_returns_dict_with_four_keys(self, tmp_path):
        """config_to_graphs returns exactly four keys."""
        from jig.query.node import config_to_graphs

        config = _FakeConfig(
            paths=_FakePaths(generated=tmp_path),
            project_root=tmp_path,
        )

        result = config_to_graphs(config)
        assert set(result.keys()) == {"intent", "impl", "verify", "project_root"}


class TestQueryNode:
    """Tests for query_node convenience wrapper."""

    @jig.verifies("S-111", "S-112", "S-113")
    def test_valid_identifier_returns_formatted_response(self, graph_dir):
        """query_node with valid ID returns dict with root, nodes, more."""
        from jig.query.node import query_node

        result = query_node("S-001", graph_dir)

        assert result != {}
        assert "root" in result
        assert result["root"] == "S-001"
        assert "nodes" in result
        assert "more" in result

    @jig.verifies("S-111", "S-112", "S-113")
    def test_valid_identifier_includes_ancestors(self, graph_dir):
        """query_node result includes ancestor nodes with negative depth."""
        from jig.query.node import query_node

        result = query_node("S-001", graph_dir)

        ancestor_ids = {n["id"] for n in result["nodes"] if n["depth"] < 0}
        assert "O-001" in ancestor_ids

    @jig.verifies("S-111", "S-112", "S-113")
    def test_valid_identifier_includes_descendants(self, graph_dir):
        """query_node result includes descendant nodes with positive depth."""
        from jig.query.node import query_node

        result = query_node("S-001", graph_dir)

        descendant_ids = {n["id"] for n in result["nodes"] if n["depth"] > 0}
        # F-foo and T-bar are children of S-001
        assert "F-foo" in descendant_ids
        assert "T-bar" in descendant_ids

    @jig.verifies("S-111")
    def test_invalid_identifier_returns_empty_dict(self, graph_dir):
        """query_node with invalid identifier (not a pattern, not a file) returns {}."""
        from jig.query.node import query_node

        result = query_node("not-a-valid-thing", graph_dir)
        assert result == {}

    @jig.verifies("S-111")
    def test_nonexistent_id_returns_empty_dict(self, graph_dir):
        """query_node with valid pattern but nonexistent node returns {}."""
        from jig.query.node import query_node

        result = query_node("S-999", graph_dir)
        assert result == {}

    @jig.verifies("S-111", "S-112", "S-113")
    def test_matches_format_response_of_traverse_graph(self, graph_dir):
        """query_node produces same output as manual traverse_graph + format_response."""
        from jig.query.node import (
            _load_all_graphs,
            config_to_graphs,
            format_response,
            query_node,
            traverse_graph,
        )

        graphs = config_to_graphs(graph_dir)
        traversal = traverse_graph("S-001", graphs)
        _, all_edges = _load_all_graphs(graphs)
        expected = format_response(traversal, all_edges)

        result = query_node("S-001", graph_dir)

        assert result == expected


class TestPublicExports:
    """Verify jig.query.__init__ exports the public API."""

    def test_query_node_importable(self):
        from jig.query import query_node  # noqa: F401

    def test_config_to_graphs_importable(self):
        from jig.query import config_to_graphs  # noqa: F401

    def test_resolve_identifier_importable(self):
        from jig.query import resolve_identifier  # noqa: F401

    def test_traverse_graph_importable(self):
        from jig.query import traverse_graph  # noqa: F401

    def test_format_response_importable(self):
        from jig.query import format_response  # noqa: F401

    def test_identifier_error_importable(self):
        from jig.query import IdentifierError  # noqa: F401
