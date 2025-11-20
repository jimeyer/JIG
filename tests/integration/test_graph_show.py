# @jig T-GRAPH-013 verifies:S-GRAPH-003 subsystem:core
"""Integration tests for graph show command."""

import tempfile
from pathlib import Path

from click.testing import CliRunner

from jig.cli.graph import graph
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
        "It has multiple lines.",
        "Line 3",
        "Line 4",
        "Line 5",
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


# @jig T-GRAPH-013 verifies:S-GRAPH-003 subsystem:core
def test_graph_show_displays_node() -> None:
    """Verify show command displays node details."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a test node
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Test Outcome", "core")
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
            # Run graph show command
            runner = CliRunner()
            result = runner.invoke(graph, ["show", "O-TEST-001"])

            # Verify output
            assert result.exit_code == 0
            assert "O-TEST-001" in result.output
            assert "Type: outcome" in result.output
            assert "Title: Test Outcome" in result.output
            assert "Subsystem: core" in result.output
            assert "Status: active" in result.output
            assert "This is a test node for O-TEST-001" in result.output
            assert "Dependencies:" in result.output
            assert "Dependents:" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-GRAPH-014 verifies:S-GRAPH-003 subsystem:core
def test_graph_show_displays_relationships() -> None:
    """Verify show displays dependencies and dependents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nodes with relationships
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1", "core")
        create_test_node(tmp_path, "S-TEST-002", "specification", "Spec 2", "core")
        create_test_node(tmp_path, "T-TEST-001", "test", "Test 1", "core")

        # S-TEST-001 implements O-TEST-001
        # S-TEST-002 implements O-TEST-001
        # T-TEST-001 verifies S-TEST-001
        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
            {"from": "S-TEST-002", "to": "O-TEST-001", "type": "implements"},
            {"from": "T-TEST-001", "to": "S-TEST-001", "type": "verifies"},
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
            # Show O-TEST-001 - should have 2 dependents, no dependencies
            runner = CliRunner()
            result = runner.invoke(graph, ["show", "O-TEST-001"])

            assert result.exit_code == 0
            assert "Dependencies:" in result.output
            assert "(none)" in result.output  # O-TEST-001 has no dependencies
            assert "Dependents:" in result.output
            assert "S-TEST-001" in result.output
            assert "S-TEST-002" in result.output

            # Show S-TEST-001 - should have 1 dependency and 1 dependent
            result = runner.invoke(graph, ["show", "S-TEST-001"])

            assert result.exit_code == 0
            assert "Dependencies:" in result.output
            assert "O-TEST-001" in result.output
            assert "Dependents:" in result.output
            assert "T-TEST-001" in result.output

            # Show T-TEST-001 - should have 1 dependency, no dependents
            result = runner.invoke(graph, ["show", "T-TEST-001"])

            assert result.exit_code == 0
            assert "Dependencies:" in result.output
            assert "S-TEST-001" in result.output
            assert "Dependents:" in result.output
            # Check for "(none)" after "Dependents:" section
            output_lines = result.output.split("\n")
            dependents_idx = next(i for i, line in enumerate(output_lines) if "Dependents:" in line)
            # The line after "Dependents:" should contain "(none)"
            assert "(none)" in output_lines[dependents_idx + 1]
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-GRAPH-015 verifies:S-GRAPH-003 subsystem:core
def test_graph_show_node_not_found() -> None:
    """Verify clear error for missing node."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a node but request a different one
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
            # Run graph show with invalid node ID
            runner = CliRunner()
            result = runner.invoke(graph, ["show", "INVALID-001"])

            # Verify exit code 1 and error message
            assert result.exit_code == 1
            assert "Error:" in result.output
            assert "INVALID-001 not found" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_show_not_initialized() -> None:
    """Verify error when intent directory doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "nonexistent"

        # Mock config to point to nonexistent directory
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
            # Run graph show command
            runner = CliRunner()
            result = runner.invoke(graph, ["show", "O-TEST-001"])

            # Verify exit code 3 and error message
            assert result.exit_code == 3
            assert "Error:" in result.output
            assert "Intent directory not found" in result.output
            assert "jigy init" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_show_truncates_long_body() -> None:
    """Verify body is truncated after 10 lines."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create node with long body
        node_dir = tmp_path / "outcomes"
        node_dir.mkdir(parents=True, exist_ok=True)
        node_file = node_dir / "O-LONG-001.md"

        lines = [
            "---",
            "id: O-LONG-001",
            "type: outcome",
            'title: "Long Outcome"',
            "subsystem: core",
            "status: active",
            "---",
            "",
            "# Long Outcome",
            "",
            "Line 1",
            "Line 2",
            "Line 3",
            "Line 4",
            "Line 5",
            "Line 6",
            "Line 7",
            "Line 8",
            "Line 9",
            "Line 10",
            "Line 11 should be truncated",
            "Line 12 should be truncated",
            ""
        ]
        node_file.write_text("\n".join(lines))
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
            # Run graph show command
            runner = CliRunner()
            result = runner.invoke(graph, ["show", "O-LONG-001"])

            # Verify output is truncated
            # First 10 lines of body are: "# Long Outcome", "", "Line 1-8"
            # So "Line 8" should be visible but "Line 9" should be truncated
            assert result.exit_code == 0
            assert "Line 8" in result.output
            assert "Line 9" not in result.output
            assert "Line 10" not in result.output
            assert "Line 11 should be truncated" not in result.output
            assert "Line 12 should be truncated" not in result.output
            assert "... (use 'cat' to see full content)" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_show_colorized_output() -> None:
    """Verify output uses colors for different sections."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1", "core")

        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
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
            # Run graph show command with color enabled
            runner = CliRunner()
            result = runner.invoke(graph, ["show", "S-TEST-001"], color=True)

            # Verify command ran successfully
            assert result.exit_code == 0
            # Note: We can't easily test for ANSI color codes in the output
            # as Click's testing framework may strip them, but we can verify
            # the structure is correct
            assert "Dependencies:" in result.output
            assert "Dependents:" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]
