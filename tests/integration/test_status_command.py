# @jig T-STATUS-004 verifies:S-GRAPH-001 subsystem:core
"""Integration tests for status command."""

import tempfile
import time
from pathlib import Path

import yaml
from jig.cli.status import calculate_status
from jig.utils.io import write_file
import json



def setup_test_jig_structure(tmp_path: Path) -> None:
    """Create standard JIG directory structure for tests."""
    (tmp_path / "outcomes").mkdir(parents=True, exist_ok=True)
    (tmp_path / "specifications").mkdir(parents=True, exist_ok=True)
    (tmp_path / "constraints").mkdir(parents=True, exist_ok=True)


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


def create_test_graph_index(tmp_path: Path, edges: list[dict], subsystems: dict) -> Path:
    """Helper to create a test graph-index.json file."""
    graph_index_path = tmp_path / "graph-index.json"
    data = {
        "version": "1.0.0",
        "nodes": [],
        "edges": edges,
        "subsystems": subsystems,
    }
    write_file(graph_index_path, json.dumps(data, indent=2))
    return graph_index_path


def create_test_subsystems_file(tmp_path: Path, subsystem_names: list[str]) -> Path:
    """Helper to create a test subsystems.yaml file."""
    import yaml
    subsystems_path = tmp_path / "subsystems.yaml"
    data = {
        "version": "1.0.0",
        "subsystems": {}
    }
    for name in subsystem_names:
        data["subsystems"][name] = {
            "name": name,
            "description": f"Test subsystem {name}",
            "max_exports": 5,
            "allowed_dependencies": [],
            "status": "active"
        }
    write_file(subsystems_path, yaml.dump(data, sort_keys=False))
    return subsystems_path


def test_status_performance():
    """Verify status completes in <100ms for 100 nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create 100 nodes (mix of outcomes and specifications)
        edges = []
        node_ids = []

        for i in range(50):
            # Create outcome
            outcome_id = f"O-PERF-{i:03d}"
            create_test_node(tmp_path, outcome_id, "outcome", f"Outcome {i}", "core")
            node_ids.append(outcome_id)

            # Create specification that implements the outcome
            spec_id = f"S-PERF-{i:03d}"
            create_test_node(tmp_path, spec_id, "specification", f"Spec {i}", "core")
            node_ids.append(spec_id)

            # Add edge
            edges.append({
                "from": spec_id,
                "to": outcome_id,
                "type": "implements"
            })

        # Create graph-index.yaml
        subsystems = {
            "core": {"nodes": node_ids}
        }
        create_test_graph_index(tmp_path, edges, subsystems)

        # Time the status calculation
        start_time = time.time()
        status = calculate_status(tmp_path)
        elapsed_ms = (time.time() - start_time) * 1000

        # Verify results
        assert status.total_nodes == 100
        assert status.node_counts["outcome"] == 50
        assert status.node_counts["specification"] == 50
        assert len(status.orphaned_nodes) == 0

        # Verify performance: <100ms for 100 nodes
        assert elapsed_ms < 100, f"Status took {elapsed_ms:.2f}ms, expected <100ms"


def test_status_on_real_jig_graph():
    """Verify status works on JIG's own graph."""
    # This test runs against the actual JIG graph in the repository
    jig_intent_dir = Path("jig")

    if not jig_intent_dir.exists():
        # Skip if not in JIG repository
        return

    # Calculate status for JIG's own graph
    start_time = time.time()
    status = calculate_status(jig_intent_dir)
    elapsed_ms = (time.time() - start_time) * 1000

    # Verify basic properties
    assert status.total_nodes > 0
    assert len(status.node_counts) > 0

    # Verify performance on JIG's own graph (should be <100ms)
    assert elapsed_ms < 100, f"Status took {elapsed_ms:.2f}ms, expected <100ms"


def test_status_command_cli_output():
    """Verify status command CLI output."""
    from click.testing import CliRunner
    from jig.cli.status import status

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Test outcome", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Test spec", "core")
        create_test_node(tmp_path, "O-TEST-002", "outcome", "Orphaned outcome", "api")

        # Create edges - O-TEST-002 is orphaned
        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
        ]
        subsystems = {
            "core": {"nodes": ["O-TEST-001", "S-TEST-001"]},
            "api": {"nodes": ["O-TEST-002"]}
        }
        create_test_graph_index(tmp_path, edges, subsystems)
        create_test_subsystems_file(tmp_path, ["core", "api"])

        # Mock config to point to tmp_path
        import jig.cli.status
        original_load_config = jig.cli.status.load_config

        def mock_load_config():
            from jig.core.config import JigConfig
            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.json",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.status.load_config = mock_load_config

        try:
            # Run status command
            runner = CliRunner()
            result = runner.invoke(status, [])

            # Verify output
            assert result.exit_code == 0
            assert "JIG Graph Status" in result.output
            # New format: "✓ 3 nodes, X edges, Y subsystems"
            assert "3 nodes" in result.output
            assert "edges" in result.output
            # New format: "• Outcomes: 2" and "• Specifications: 1"
            assert "• Outcomes: 2" in result.output
            assert "• Specifications: 1" in result.output
            # Warnings section (new)
            assert "Warnings:" in result.output
            assert "Orphaned nodes" in result.output
            assert "O-TEST-002" in result.output

            # Verify suggestions section
            assert "Suggestions:" in result.output
            assert "Add relationships" in result.output
            assert "jigy validate" in result.output
        finally:
            # Restore original
            jig.cli.status.load_config = original_load_config


def test_status_command_verbose_output():
    """Verify status command --verbose shows node lists."""
    from click.testing import CliRunner
    from jig.cli.status import status

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core outcome", "core")
        create_test_node(tmp_path, "O-CORE-002", "outcome", "Core outcome 2", "core")

        # Create graph index and subsystems
        subsystems = {
            "core": {"nodes": ["O-CORE-001", "O-CORE-002"]}
        }
        create_test_graph_index(tmp_path, [], subsystems)
        create_test_subsystems_file(tmp_path, ["core"])

        # Mock config
        import jig.cli.status
        original_load_config = jig.cli.status.load_config

        def mock_load_config():
            from jig.core.config import JigConfig
            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.json",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.status.load_config = mock_load_config

        try:
            # Run status command with --verbose
            runner = CliRunner()
            result = runner.invoke(status, ["--verbose"])

            # Verify verbose output includes node IDs
            assert result.exit_code == 0
            assert "O-CORE-001" in result.output
            assert "O-CORE-002" in result.output
        finally:
            jig.cli.status.load_config = original_load_config


def test_status_command_not_initialized():
    """Verify status command handles missing jig/ directory."""
    from click.testing import CliRunner
    from jig.cli.status import status

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "nonexistent"

        # Mock config to point to nonexistent directory
        import jig.cli.status
        original_load_config = jig.cli.status.load_config

        def mock_load_config():
            from jig.core.config import JigConfig
            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.json",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.status.load_config = mock_load_config

        try:
            # Run status command
            runner = CliRunner()
            result = runner.invoke(status, [])

            # Verify exit code 3 and error message
            assert result.exit_code == 3
            assert "Error:" in result.output
            assert "Intent directory not found" in result.output
        finally:
            jig.cli.status.load_config = original_load_config


def test_status_command_empty_graph():
    """Verify status command handles empty graph."""
    from click.testing import CliRunner
    from jig.cli.status import status

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create empty graph index and subsystems
        create_test_graph_index(tmp_path, [], {})
        create_test_subsystems_file(tmp_path, [])

        # Mock config to point to empty directory
        import jig.cli.status
        original_load_config = jig.cli.status.load_config

        def mock_load_config():
            from jig.core.config import JigConfig
            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.json",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.status.load_config = mock_load_config

        try:
            # Run status command
            runner = CliRunner()
            result = runner.invoke(status, [])

            # Verify output for empty graph
            assert result.exit_code == 0
            assert "No nodes found" in result.output
            assert "jigy init" in result.output or "jigy node create" in result.output
        finally:
            jig.cli.status.load_config = original_load_config


def test_status_command_healthy_graph():
    """Verify status command shows healthy message when no issues."""
    from click.testing import CliRunner
    from jig.cli.status import status

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create well-connected nodes - all have relationships and subsystems
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Test outcome", "core")
        create_test_node(tmp_path, "S-TEST-001", "specification", "Test spec", "core")

        # Create edges connecting all nodes
        edges = [
            {"from": "S-TEST-001", "to": "O-TEST-001", "type": "implements"},
        ]
        subsystems = {
            "core": {"nodes": ["O-TEST-001", "S-TEST-001"]}
        }
        create_test_graph_index(tmp_path, edges, subsystems)

        # Mock config
        import jig.cli.status
        original_load_config = jig.cli.status.load_config

        def mock_load_config():
            from jig.core.config import JigConfig
            return JigConfig(
                project_name="test",
                intent_dir=tmp_path,
                delta_dir=tmp_path / "deltas",
                templates_dir=tmp_path / "templates",
                graph_index_file=tmp_path / "graph-index.json",
                subsystems_file=tmp_path / "subsystems.yaml",
            )

        jig.cli.status.load_config = mock_load_config

        try:
            # Run status command
            runner = CliRunner()
            result = runner.invoke(status, [])

            # Verify healthy output
            assert result.exit_code == 0
            # New format: "✓ 2 nodes, X edges, Y subsystems"
            assert "2 nodes" in result.output
            assert "edges" in result.output
            # Healthy graph shows validation passed
            assert "Graph is valid" in result.output or "All" in result.output and "valid" in result.output
        finally:
            jig.cli.status.load_config = original_load_config
