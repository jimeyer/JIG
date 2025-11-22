# @jig T-GRAPH-009 verifies:S-GRAPH-003 subsystem:core
"""Unit tests for graph query/filter methods."""

import tempfile
from pathlib import Path

from jig.core.graph import Graph
from tests.helpers.graph_fixtures import create_test_graph


def test_filter_by_type_outcome() -> None:
    """Verify filtering by outcome type."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create mixed nodes
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "core"},
            {"id": "O-TEST-002", "type": "outcome", "title": "Outcome 2", "subsystem": "core"},
            {"id": "S-TEST-001", "type": "specification", "title": "Spec 1", "subsystem": "core"},
            {"id": "T-TEST-001", "type": "test", "title": "Test 1", "subsystem": "core", "file": "test.py", "line": 1},
        ], subsystems={"core": {"id": "core"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Filter by outcome
        outcomes = graph.filter_by_type("outcome")
        assert len(outcomes) == 2
        assert outcomes[0].id == "O-TEST-001"
        assert outcomes[1].id == "O-TEST-002"
        assert all(node.type == "outcome" for node in outcomes)


# @jig T-GRAPH-010 verifies:S-GRAPH-003 subsystem:core
def test_filter_by_type_case_insensitive() -> None:
    """Verify case-insensitive type filtering."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "core"},
            {"id": "O-TEST-002", "type": "outcome", "title": "Outcome 2", "subsystem": "core"},
        ], subsystems={"core": {"id": "core"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Test different cases
        outcomes_lower = graph.filter_by_type("outcome")
        outcomes_upper = graph.filter_by_type("OUTCOME")
        outcomes_mixed = graph.filter_by_type("OuTcOmE")

        assert len(outcomes_lower) == 2
        assert len(outcomes_upper) == 2
        assert len(outcomes_mixed) == 2
        assert outcomes_lower == outcomes_upper == outcomes_mixed


def test_filter_by_type_specification() -> None:
    """Verify filtering by specification type."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create mixed nodes
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "core"},
            {"id": "S-TEST-001", "type": "specification", "title": "Spec 1", "subsystem": "core"},
            {"id": "S-TEST-002", "type": "specification", "title": "Spec 2", "subsystem": "core"},
        ], subsystems={"core": {"id": "core"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Filter by specification
        specs = graph.filter_by_type("specification")
        assert len(specs) == 2
        assert all(node.type == "specification" for node in specs)


def test_filter_by_type_empty() -> None:
    """Verify empty list when no nodes match type."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create only outcomes
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "core"},
        ], subsystems={"core": {"id": "core"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Filter by constraint (no constraints exist)
        constraints = graph.filter_by_type("constraint")
        assert constraints == []


# @jig T-GRAPH-011 verifies:S-GRAPH-003 subsystem:core
def test_filter_by_subsystem() -> None:
    """Verify filtering by subsystem."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes in different subsystems
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-CORE-001", "type": "outcome", "title": "Core Outcome", "subsystem": "core"},
            {"id": "S-CORE-001", "type": "specification", "title": "Core Spec", "subsystem": "core"},
            {"id": "O-CLI-001", "type": "outcome", "title": "CLI Outcome", "subsystem": "cli"},
            {"id": "S-API-001", "type": "specification", "title": "API Spec", "subsystem": "api"},
        ], subsystems={"core": {"id": "core"}, "cli": {"id": "cli"}, "api": {"id": "api"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Filter by core subsystem
        core_nodes = graph.filter_by_subsystem("core")
        assert len(core_nodes) == 2
        assert core_nodes[0].id == "O-CORE-001"
        assert core_nodes[1].id == "S-CORE-001"
        assert all(node.subsystem == "core" for node in core_nodes)

        # Filter by cli subsystem
        cli_nodes = graph.filter_by_subsystem("cli")
        assert len(cli_nodes) == 1
        assert cli_nodes[0].id == "O-CLI-001"


def test_filter_by_subsystem_case_insensitive() -> None:
    """Verify case-insensitive subsystem filtering."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-CORE-001", "type": "outcome", "title": "Core Outcome", "subsystem": "core"},
            {"id": "S-CORE-001", "type": "specification", "title": "Core Spec", "subsystem": "core"},
        ], subsystems={"core": {"id": "core"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Test different cases
        core_lower = graph.filter_by_subsystem("core")
        core_upper = graph.filter_by_subsystem("CORE")
        core_mixed = graph.filter_by_subsystem("CoRe")

        assert len(core_lower) == 2
        assert len(core_upper) == 2
        assert len(core_mixed) == 2
        assert core_lower == core_upper == core_mixed


def test_filter_by_subsystem_empty() -> None:
    """Verify empty list when no nodes in subsystem."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes in core subsystem
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-CORE-001", "type": "outcome", "title": "Core Outcome", "subsystem": "core"},
        ], subsystems={"core": {"id": "core"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Filter by nonexistent subsystem
        api_nodes = graph.filter_by_subsystem("api")
        assert api_nodes == []


def test_filter_by_subsystem_handles_none() -> None:
    """Verify filtering handles nodes without subsystem."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test graph with one node with subsystem
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-CORE-001", "type": "outcome", "title": "Core Outcome", "subsystem": "core"},
        ], subsystems={"core": {"id": "core"}})

        # Create node without subsystem (manually)
        node_file = jig_dir / "outcomes" / "O-NONE-001.md"
        content = """---
id: O-NONE-001
type: outcome
title: "No Subsystem"
status: active
---

# No Subsystem

This node has no subsystem field.
"""
        node_file.write_text(content)

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Filter by core - should only get node with subsystem
        core_nodes = graph.filter_by_subsystem("core")
        assert len(core_nodes) == 1
        assert core_nodes[0].id == "O-CORE-001"


# @jig T-GRAPH-012 verifies:S-GRAPH-003 subsystem:core
def test_filter_returns_sorted() -> None:
    """Verify filter results are sorted by ID."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes in non-alphabetical order
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-TEST-003", "type": "outcome", "title": "Outcome 3", "subsystem": "core"},
            {"id": "O-TEST-001", "type": "outcome", "title": "Outcome 1", "subsystem": "core"},
            {"id": "O-TEST-002", "type": "outcome", "title": "Outcome 2", "subsystem": "core"},
        ], subsystems={"core": {"id": "core"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Filter by outcome - should be sorted
        outcomes = graph.filter_by_type("outcome")
        assert len(outcomes) == 3
        assert outcomes[0].id == "O-TEST-001"
        assert outcomes[1].id == "O-TEST-002"
        assert outcomes[2].id == "O-TEST-003"

        # Test subsystem filtering too
        core_nodes = graph.filter_by_subsystem("core")
        assert len(core_nodes) == 3
        assert core_nodes[0].id == "O-TEST-001"
        assert core_nodes[1].id == "O-TEST-002"
        assert core_nodes[2].id == "O-TEST-003"


def test_filter_combined_operations() -> None:
    """Verify filters can be combined for complex queries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create diverse node set
        jig_dir = create_test_graph(tmp_path, [
            {"id": "O-CORE-001", "type": "outcome", "title": "Core Outcome", "subsystem": "core"},
            {"id": "O-CORE-002", "type": "outcome", "title": "Core Outcome 2", "subsystem": "core"},
            {"id": "S-CORE-001", "type": "specification", "title": "Core Spec", "subsystem": "core"},
            {"id": "O-CLI-001", "type": "outcome", "title": "CLI Outcome", "subsystem": "cli"},
        ], subsystems={"core": {"id": "core"}, "cli": {"id": "cli"}})

        # Load graph
        graph = Graph.load_from_dir(jig_dir)

        # Get all outcomes in core subsystem by combining filters
        all_outcomes = graph.filter_by_type("outcome")
        core_outcomes = [n for n in all_outcomes if n.subsystem == "core"]

        assert len(all_outcomes) == 3
        assert len(core_outcomes) == 2
        assert core_outcomes[0].id == "O-CORE-001"
        assert core_outcomes[1].id == "O-CORE-002"
