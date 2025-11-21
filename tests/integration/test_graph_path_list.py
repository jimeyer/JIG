# @jig T-GRAPH-020 verifies:S-GRAPH-003 subsystem:core
"""Integration tests for graph path and list commands."""

import tempfile
from pathlib import Path

import yaml
from click.testing import CliRunner

from jig.cli.graph import graph
from jig.utils.yaml_utils import dump_yaml


def create_test_node(
    tmp_path: Path, node_id: str, node_type: str, title: str, subsystem: str = "core"
) -> Path:
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
        "",
    ]
    content = "\n".join(lines)
    node_file.write_text(content)
    return node_file


def create_test_graph_index(
    tmp_path: Path,
    edges: list[dict[str, str]],
    subsystems: dict[str, dict[str, list[str]]],
) -> Path:
    """Helper to create a test graph-index.yaml file."""
    graph_index_path = tmp_path / "graph-index.yaml"
    data = {
        "version": "1.0.0",
        "edges": edges,
        "subsystems": subsystems,
    }
    dump_yaml(data, graph_index_path)
    return graph_index_path


# @jig T-GRAPH-020 verifies:S-GRAPH-003 subsystem:core
def test_graph_path_finds_route() -> None:
    """Verify path command finds route between nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a chain: C-001 -> S-001 -> O-001 (using O/S/C nodes)
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1", "core")
        create_test_node(tmp_path, "C-TEST-001", "constraint", "Constraint 1", "core")

        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
            {"from": "C-TEST-001", "to": "S-TEST-001", "type": "constrains"},
        ]
        create_test_graph_index(tmp_path, edges, {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph path command
            runner = CliRunner()
            result = runner.invoke(graph, ["path", "C-TEST-001", "O-TEST-001"])

            # Verify output
            assert result.exit_code == 0
            assert "Path from C-TEST-001 to O-TEST-001:" in result.output
            assert "C-TEST-001 → S-TEST-001 → O-TEST-001" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-GRAPH-021 verifies:S-GRAPH-003 subsystem:core
def test_graph_path_no_route() -> None:
    """Verify message when no path exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create disconnected nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Outcome 2", "core")

        # No edges - nodes are disconnected
        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph path command
            runner = CliRunner()
            result = runner.invoke(graph, ["path", "O-TEST-001", "O-TEST-002"])

            # Verify output
            assert result.exit_code == 0
            assert "No path found from O-TEST-001 to O-TEST-002" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-GRAPH-022 verifies:S-GRAPH-003 subsystem:core
def test_graph_list_all_nodes() -> None:
    """Verify list shows all nodes in table format (O/S/C only)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create mixed nodes (O/S/C - test nodes not loaded from markdown)
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1", "core")
        create_test_node(tmp_path, "C-TEST-001", "constraint", "Constraint 1", "core")

        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph list command
            runner = CliRunner()
            result = runner.invoke(graph, ["list"])

            # Verify output
            assert result.exit_code == 0
            assert "ID" in result.output
            assert "Type" in result.output
            assert "Title" in result.output
            assert "O-TEST-001" in result.output
            assert "S-TEST-001" in result.output
            assert "C-TEST-001" in result.output
            assert "outcome" in result.output
            assert "specification" in result.output
            assert "constraint" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-GRAPH-023 verifies:S-GRAPH-003 subsystem:core
def test_graph_list_filter_by_type() -> None:
    """Verify list filters by type."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create mixed nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Outcome 2", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1", "core")

        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph list with --type filter
            runner = CliRunner()
            result = runner.invoke(graph, ["list", "--type", "outcome"])

            # Verify output
            assert result.exit_code == 0
            assert "O-TEST-001" in result.output
            assert "O-TEST-002" in result.output
            # Spec should not be in output
            assert "S-TEST-001" not in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_list_filter_by_subsystem() -> None:
    """Verify list filters by subsystem."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes in different subsystems
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core Outcome", "core")
        create_test_node(tmp_path, "O-CLI-001", "outcome", "CLI Outcome", "cli")

        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph list with --subsystem filter
            runner = CliRunner()
            result = runner.invoke(graph, ["list", "--subsystem", "core"])

            # Verify output
            assert result.exit_code == 0
            assert "O-CORE-001" in result.output
            # CLI node should not be in output
            assert "O-CLI-001" not in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-GRAPH-024 verifies:S-GRAPH-003 subsystem:core
def test_graph_list_yaml_output() -> None:
    """Verify list outputs valid YAML for piping."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1", "core")

        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph list with --format yaml
            runner = CliRunner()
            result = runner.invoke(graph, ["list", "--format", "yaml"])

            # Verify output is valid YAML
            assert result.exit_code == 0
            data = yaml.safe_load(result.output)
            assert isinstance(data, list)
            assert len(data) == 2

            # Check structure
            ids = [item["id"] for item in data]
            assert "O-TEST-001" in ids
            assert "S-TEST-001" in ids

            # Verify all required fields
            for item in data:
                assert "id" in item
                assert "type" in item
                assert "title" in item
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_path_same_node() -> None:
    """Verify path from node to itself."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph path command
            runner = CliRunner()
            result = runner.invoke(graph, ["path", "O-TEST-001", "O-TEST-001"])

            # Verify output - path to self should just be the node
            assert result.exit_code == 0
            assert "O-TEST-001" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_path_node_not_found() -> None:
    """Verify error when start or end node not found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph path with invalid start node
            runner = CliRunner()
            result = runner.invoke(graph, ["path", "INVALID-001", "O-TEST-001"])

            assert result.exit_code == 1
            assert "Error:" in result.output
            assert "INVALID-001 not found" in result.output

            # Run graph path with invalid end node
            result = runner.invoke(graph, ["path", "O-TEST-001", "INVALID-001"])

            assert result.exit_code == 1
            assert "Error:" in result.output
            assert "INVALID-001 not found" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_list_empty_result() -> None:
    """Verify list handles no matching nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create only outcomes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")

        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph list with --type constraint (no constraint nodes exist)
            runner = CliRunner()
            result = runner.invoke(graph, ["list", "--type", "constraint"])

            # Verify output
            assert result.exit_code == 0
            assert "No nodes found matching criteria" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_list_combined_filters() -> None:
    """Verify list handles combined type and subsystem filters."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create diverse nodes
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core Outcome", "core")
        create_test_node(tmp_path, "O-CLI-001", "outcome", "CLI Outcome", "cli")
        create_test_node(tmp_path, "S-CORE-001", "specification", "Core Spec", "core")

        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph list with both filters
            runner = CliRunner()
            result = runner.invoke(
                graph, ["list", "--type", "outcome", "--subsystem", "core"]
            )

            # Verify output - should only show O-CORE-001
            assert result.exit_code == 0
            assert "O-CORE-001" in result.output
            assert "O-CLI-001" not in result.output  # Wrong subsystem
            assert "S-CORE-001" not in result.output  # Wrong type
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-CLI-014 verifies:S-CLI-009 subsystem:cli
def test_graph_list_compact_format() -> None:
    """Verify list --format compact groups nodes by type."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create diverse nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Outcome 2", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1", "core")
        create_test_node(tmp_path, "C-TEST-001", "constraint", "Constraint 1", "core")

        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph list with --format compact
            runner = CliRunner()
            result = runner.invoke(graph, ["list", "--format", "compact"])

            # Verify output
            assert result.exit_code == 0
            # Header with total count
            assert "All nodes (4)" in result.output
            # Groups by type with bullet points and counts
            assert "• Constraints (1):" in result.output
            assert "• Outcomes (2):" in result.output
            assert "• Specifications (1):" in result.output
            # Comma-separated node IDs
            assert "O-TEST-001, O-TEST-002" in result.output
            assert "S-TEST-001" in result.output
            assert "C-TEST-001" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-CLI-015 verifies:S-CLI-009 subsystem:cli
def test_graph_list_compact_with_subsystem_filter() -> None:
    """Verify compact format shows subsystem name in header."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes in different subsystems
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core Outcome", "core")
        create_test_node(tmp_path, "O-CORE-002", "outcome", "Core Outcome 2", "core")
        create_test_node(tmp_path, "O-CLI-001", "outcome", "CLI Outcome", "cli")

        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph list with --subsystem and --format compact
            runner = CliRunner()
            result = runner.invoke(
                graph, ["list", "--subsystem", "core", "--format", "compact"]
            )

            # Verify output
            assert result.exit_code == 0
            # Header shows subsystem name
            assert "core (2 nodes)" in result.output
            # Shows only core nodes
            assert "O-CORE-001" in result.output
            assert "O-CORE-002" in result.output
            # CLI node should not be in output
            assert "O-CLI-001" not in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-CLI-016 verifies:S-CLI-009 subsystem:cli
def test_graph_list_default_format_is_table() -> None:
    """Verify default format is still table (backward compatibility)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test node
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")

        create_test_graph_index(tmp_path, [], {})

        # Mock config
        import jig.cli.graph

        original_load_config = jig.cli.graph.load_config  # type: ignore[attr-defined]

        def mock_load_config():  # type: ignore[no-untyped-def]
            from jig.core.config import JigConfig

            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.yaml",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.graph.load_config = mock_load_config  # type: ignore[attr-defined, assignment]

        try:
            # Run graph list without --format (should default to table)
            runner = CliRunner()
            result = runner.invoke(graph, ["list"])

            # Verify table format (has column headers)
            assert result.exit_code == 0
            assert "ID" in result.output
            assert "Type" in result.output
            assert "Title" in result.output
            # Should not have compact format markers
            assert "• Outcomes" not in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]
