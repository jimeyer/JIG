# @jig T-GRAPH-009 verifies:S-GRAPH-003 subsystem:core
"""Unit tests for graph query/filter methods."""

import tempfile
from pathlib import Path

from jig.core.graph import Graph
from jig.utils.yaml_utils import dump_yaml


def create_test_node(tmp_path: Path, node_id: str, node_type: str, title: str, subsystem: str = "core") -> Path:
    """Helper to create a test OSTC node file."""
    type_to_dir = {
        "outcome": "outcomes",
        "specification": "specifications",
        "constraint": "constraints",
        "test": "tests",
    }
    node_dir = tmp_path / type_to_dir.get(node_type, "outcomes")
    node_dir.mkdir(parents=True, exist_ok=True)

    node_file = node_dir / f"{node_id}.md"
    lines = [
        "---",
        f"id: {node_id}",
        f"type: {node_type}",
        f'title: "{title}"',
        f"subsystem: {subsystem}",
        "status: active",
        "---",
        "",
        f"# {title}",
        "",
        f"This is a test node for {node_id}.",
        ""
    ]
    content = "\n".join(lines)
    node_file.write_text(content)
    return node_file


def create_test_graph_index(tmp_path: Path, edges: list[dict[str, str]], subsystems: dict[str, dict[str, list[str]]]) -> Path:
    """Helper to create a test graph-index.yaml file."""
    graph_index_path = tmp_path / "graph-index.yaml"
    data = {
        "version": "1.0.0",
        "edges": edges,
        "subsystems": subsystems,
    }
    dump_yaml(data, graph_index_path)
    return graph_index_path


def test_filter_by_type_outcome() -> None:
    """Verify filtering by outcome type."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create mixed nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Outcome 2", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1", "core")
        create_test_node(tmp_path, "T-TEST-001", "test", "Test 1", "core")

        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

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
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Outcome 2", "core")

        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

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
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1", "core")
        create_test_node(tmp_path, "S-TEST-002", "specification", "Spec 2", "core")

        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Filter by specification
        specs = graph.filter_by_type("specification")
        assert len(specs) == 2
        assert all(node.type == "specification" for node in specs)


def test_filter_by_type_empty() -> None:
    """Verify empty list when no nodes match type."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create only outcomes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")

        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Filter by constraint (no constraints exist)
        constraints = graph.filter_by_type("constraint")
        assert constraints == []


# @jig T-GRAPH-011 verifies:S-GRAPH-003 subsystem:core
def test_filter_by_subsystem() -> None:
    """Verify filtering by subsystem."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes in different subsystems
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core Outcome", "core")
        create_test_node(tmp_path, "S-CORE-001", "specification", "Core Spec", "core")
        create_test_node(tmp_path, "O-CLI-001", "outcome", "CLI Outcome", "cli")
        create_test_node(tmp_path, "S-API-001", "specification", "API Spec", "api")

        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

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
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core Outcome", "core")
        create_test_node(tmp_path, "S-CORE-001", "specification", "Core Spec", "core")

        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

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
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core Outcome", "core")

        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Filter by nonexistent subsystem
        api_nodes = graph.filter_by_subsystem("api")
        assert api_nodes == []


def test_filter_by_subsystem_handles_none() -> None:
    """Verify filtering handles nodes without subsystem."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create node with subsystem
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core Outcome", "core")

        # Create node without subsystem (manually)
        node_dir = tmp_path / "outcomes"
        node_dir.mkdir(parents=True, exist_ok=True)
        node_file = node_dir / "O-NONE-001.md"
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

        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

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
        create_test_node(tmp_path, "O-TEST-003", "outcome", "Outcome 3", "core")
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Outcome 2", "core")

        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

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
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core Outcome", "core")
        create_test_node(tmp_path, "O-CORE-002", "outcome", "Core Outcome 2", "core")
        create_test_node(tmp_path, "S-CORE-001", "specification", "Core Spec", "core")
        create_test_node(tmp_path, "O-CLI-001", "outcome", "CLI Outcome", "cli")

        create_test_graph_index(tmp_path, [], {})

        # Load graph
        graph = Graph.load_from_dir(tmp_path)

        # Get all outcomes in core subsystem by combining filters
        all_outcomes = graph.filter_by_type("outcome")
        core_outcomes = [n for n in all_outcomes if n.subsystem == "core"]

        assert len(all_outcomes) == 3
        assert len(core_outcomes) == 2
        assert core_outcomes[0].id == "O-CORE-001"
        assert core_outcomes[1].id == "O-CORE-002"
