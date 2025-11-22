# @jig T-GRAPH-016 verifies:S-GRAPH-003 subsystem:core
"""Integration tests for graph deps and impact commands."""

import tempfile
import time
from pathlib import Path

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


def test_graph_deps_shows_tree() -> None:
    """Verify deps shows dependency tree."""
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
            # Run graph deps command
            runner = CliRunner()
            result = runner.invoke(graph, ["deps", "C-TEST-001"])

            # Verify output
            assert result.exit_code == 0
            assert "Dependency tree for C-TEST-001:" in result.output
            assert "C-TEST-001" in result.output
            assert "S-TEST-001" in result.output
            assert "O-TEST-001" in result.output
            # Verify tree structure with connectors
            assert "└──" in result.output or "├──" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-GRAPH-017 verifies:S-GRAPH-003 subsystem:core
def test_graph_deps_handles_cycles() -> None:
    """Verify cycle detection in dependency tree."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a cycle: S-001 -> O-001 -> S-001
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1", "core")

        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
            {"from": "O-TEST-001", "to": "S-TEST-001", "type": "depends_on"},
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
            # Run graph deps command
            runner = CliRunner()
            result = runner.invoke(graph, ["deps", "S-TEST-001"])

            # Verify cycle is detected
            assert result.exit_code == 0
            assert "(cycle)" in result.output
            assert "↻" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-GRAPH-018 verifies:S-GRAPH-003 subsystem:core
def test_graph_impact_shows_dependents() -> None:
    """Verify impact shows what depends on node."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create: O-001 <- S-001 <- T-001
        #                 <- S-002
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Outcome 1", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Spec 1", "core")
        create_test_node(tmp_path, "S-TEST-002", "specification", "Spec 2", "core")
        create_test_node(tmp_path, "T-TEST-001", "test", "Test 1", "core")

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
            # Run graph impact command on O-TEST-001
            runner = CliRunner()
            result = runner.invoke(graph, ["impact", "O-TEST-001"])

            # Verify output
            assert result.exit_code == 0
            assert "Impact analysis for O-TEST-001:" in result.output
            assert "O-TEST-001" in result.output
            assert "S-TEST-001" in result.output
            assert "S-TEST-002" in result.output
            assert "T-TEST-001" in result.output
            # Verify tree structure
            assert "└──" in result.output or "├──" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


# @jig T-GRAPH-019 verifies:S-GRAPH-003 subsystem:core
def test_graph_deps_performance() -> None:
    """Verify deps completes in <200ms for 100 nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a chain of 100 nodes
        edges = []
        for i in range(50):
            # Create outcome
            outcome_id = f"O-PERF-{i:03d}"
            create_test_node(tmp_path, outcome_id, "outcome", f"Outcome {i}", "core")

            # Create specification that implements the outcome
            spec_id = f"S-PERF-{i:03d}"
            create_test_node(
                tmp_path, spec_id, "specification", f"Spec {i}", "core"
            )

            # Add edge
            edges.append({"from": spec_id, "to": outcome_id, "type": "implements"})

            # Chain specifications together
            if i > 0:
                prev_spec_id = f"S-PERF-{i-1:03d}"
                edges.append(
                    {"from": spec_id, "to": prev_spec_id, "type": "depends_on"}
                )

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
            # Run graph deps command and measure time
            runner = CliRunner()
            start_time = time.time()
            result = runner.invoke(graph, ["deps", "S-PERF-049"])
            elapsed_ms = (time.time() - start_time) * 1000

            # Verify performance: <200ms for 100 nodes
            assert result.exit_code == 0
            assert (
                elapsed_ms < 200
            ), f"deps took {elapsed_ms:.2f}ms, expected <200ms"
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_deps_no_dependencies() -> None:
    """Verify deps handles nodes with no dependencies."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a node with no dependencies
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
            # Run graph deps command
            runner = CliRunner()
            result = runner.invoke(graph, ["deps", "O-TEST-001"])

            # Verify output shows just the node itself
            assert result.exit_code == 0
            assert "O-TEST-001" in result.output
            # Should not have any tree connectors since no deps
            lines = result.output.strip().split("\n")
            # Should only have header and the node itself
            assert len([line for line in lines if "O-TEST-001" in line]) >= 1
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_impact_no_dependents() -> None:
    """Verify impact handles nodes with no dependents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a node with no dependents (using O/S/C nodes)
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
            # Run graph impact command
            runner = CliRunner()
            result = runner.invoke(graph, ["impact", "C-TEST-001"])

            # Verify output shows just the node itself
            assert result.exit_code == 0
            assert "C-TEST-001" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_deps_node_not_found() -> None:
    """Verify error when node not found."""
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
            # Run graph deps with invalid node
            runner = CliRunner()
            result = runner.invoke(graph, ["deps", "INVALID-001"])

            # Verify error
            assert result.exit_code == 1
            assert "Error:" in result.output
            assert "INVALID-001 not found" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]


def test_graph_impact_node_not_found() -> None:
    """Verify error when node not found."""
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
            # Run graph impact with invalid node
            runner = CliRunner()
            result = runner.invoke(graph, ["impact", "INVALID-001"])

            # Verify error
            assert result.exit_code == 1
            assert "Error:" in result.output
            assert "INVALID-001 not found" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config  # type: ignore[attr-defined]
