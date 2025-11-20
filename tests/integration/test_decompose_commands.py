# @jig T-NESTED-011 verifies:S-NESTED-004 subsystem:decompose
"""Integration tests for decompose commands with nested subsystems."""

import tempfile
from pathlib import Path
from textwrap import dedent

from click.testing import CliRunner

from jig.cli.decompose import decompose
from jig.utils.yaml_utils import dump_yaml


def create_test_node(
    tmp_path: Path, node_id: str, node_type: str, title: str, subsystem: str = "core"
) -> Path:
    """Helper to create a test OSTC node file."""
    type_to_dir = {
        "outcome": "outcomes",
        "specification": "specifications",
        "constraint": "constraints",
    }
    node_dir = tmp_path / type_to_dir.get(node_type, "outcomes")
    node_dir.mkdir(parents=True, exist_ok=True)

    node_file = node_dir / f"{node_id}.md"
    content = dedent(f"""
    ---
    id: {node_id}
    type: {node_type}
    title: "{title}"
    subsystem: {subsystem}
    status: active
    ---

    # {title}

    This is a test node for {node_id}.
    """)
    node_file.write_text(content)
    return node_file


def create_test_graph_index(
    tmp_path: Path, edges: list[dict], subsystems: dict
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


def mock_config(tmp_path: Path):
    """Create a mock config for testing."""
    from jig.core.config import JigConfig

    return JigConfig(
        project_name="test",
        intent_dir=tmp_path,
        delta_dir=tmp_path / "deltas",
        templates_dir=tmp_path / "templates",
        graph_index_file=tmp_path / "graph-index.yaml",
        subsystems_file=tmp_path / "subsystems.yaml",
    )


# @jig T-NESTED-011 verifies:S-NESTED-004 subsystem:decompose
def test_decompose_metrics_overall() -> None:
    """Test decompose metrics command with overall graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes in two subsystems
        create_test_node(tmp_path, "O-A-001", "outcome", "A1", "subsystem_a")
        create_test_node(tmp_path, "O-A-002", "outcome", "A2", "subsystem_a")
        create_test_node(tmp_path, "O-B-001", "outcome", "B1", "subsystem_b")
        create_test_node(tmp_path, "O-B-002", "outcome", "B2", "subsystem_b")

        # Create edges: strong internal, weak cross
        edges = [
            {"from": "O-A-001", "to": "O-A-002", "type": "depends_on"},
            {"from": "O-B-001", "to": "O-B-002", "type": "depends_on"},
            {"from": "O-A-002", "to": "O-B-001", "type": "depends_on"},
        ]

        subsystems = {
            "subsystem_a": {"nodes": ["O-A-001", "O-A-002"]},
            "subsystem_b": {"nodes": ["O-B-001", "O-B-002"]},
        }
        create_test_graph_index(tmp_path, edges, subsystems)

        # Mock config
        import jig.cli.decompose

        original_load_config = jig.cli.decompose.load_config
        jig.cli.decompose.load_config = lambda: mock_config(tmp_path)

        try:
            runner = CliRunner()
            result = runner.invoke(decompose, ["metrics"])

            # Verify output
            assert result.exit_code == 0
            assert "Overall Metrics" in result.output
            assert "Modularity" in result.output
            assert "Per-Subsystem Metrics" in result.output
            assert "subsystem_a" in result.output
            assert "subsystem_b" in result.output
        finally:
            jig.cli.decompose.load_config = original_load_config


# @jig T-NESTED-012 verifies:S-NESTED-004 subsystem:decompose
def test_decompose_metrics_specific_subsystem() -> None:
    """Test decompose metrics with --subsystem option."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nested subsystem structure
        create_test_node(tmp_path, "O-SER-001", "outcome", "Serialization", "crdt.ser")
        create_test_node(tmp_path, "O-SER-002", "outcome", "Ser2", "crdt.ser")
        create_test_node(
            tmp_path, "O-DESER-001", "outcome", "Deserialization", "crdt.deser"
        )

        edges = [
            {"from": "O-SER-001", "to": "O-SER-002", "type": "depends_on"},
            {"from": "O-SER-002", "to": "O-DESER-001", "type": "depends_on"},
        ]

        subsystems = {
            "crdt": {
                "subsystems": {
                    "ser": {"nodes": ["O-SER-001", "O-SER-002"]},
                    "deser": {"nodes": ["O-DESER-001"]},
                }
            }
        }
        create_test_graph_index(tmp_path, edges, subsystems)

        # Mock config
        import jig.cli.decompose

        original_load_config = jig.cli.decompose.load_config
        jig.cli.decompose.load_config = lambda: mock_config(tmp_path)

        try:
            runner = CliRunner()
            result = runner.invoke(decompose, ["metrics", "--subsystem", "crdt.ser"])

            # Verify output
            assert result.exit_code == 0
            assert "Analyzing subsystem 'crdt.ser'" in result.output
            assert "Subsystem: crdt.ser" in result.output
            assert "Nodes: 2" in result.output
            assert "Coupling ratio" in result.output
        finally:
            jig.cli.decompose.load_config = original_load_config


# @jig T-NESTED-013 verifies:S-NESTED-004 subsystem:decompose
def test_decompose_metrics_hierarchical_coupling() -> None:
    """Test coupling ratio aggregates child metrics correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create parent with two children
        create_test_node(tmp_path, "O-C1-001", "outcome", "C1-1", "parent.child1")
        create_test_node(tmp_path, "O-C1-002", "outcome", "C1-2", "parent.child1")
        create_test_node(tmp_path, "O-C2-001", "outcome", "C2-1", "parent.child2")

        # Edges between children (internal to parent)
        edges = [
            {"from": "O-C1-001", "to": "O-C1-002", "type": "depends_on"},
            {"from": "O-C1-002", "to": "O-C2-001", "type": "depends_on"},
        ]

        subsystems = {
            "parent": {
                "subsystems": {
                    "child1": {"nodes": ["O-C1-001", "O-C1-002"]},
                    "child2": {"nodes": ["O-C2-001"]},
                }
            }
        }
        create_test_graph_index(tmp_path, edges, subsystems)

        # Mock config
        import jig.cli.decompose

        original_load_config = jig.cli.decompose.load_config
        jig.cli.decompose.load_config = lambda: mock_config(tmp_path)

        try:
            runner = CliRunner()

            # Test child1 (has 1 external edge)
            result = runner.invoke(
                decompose, ["metrics", "--subsystem", "parent.child1"]
            )
            assert result.exit_code == 0
            assert "Nodes: 2" in result.output

            # Test parent (all edges are internal)
            result = runner.invoke(decompose, ["metrics", "--subsystem", "parent"])
            assert result.exit_code == 0
            assert "Nodes: 3" in result.output
            assert "perfect isolation" in result.output or "∞" in result.output
        finally:
            jig.cli.decompose.load_config = original_load_config


# @jig T-NESTED-014 verifies:S-NESTED-004 subsystem:decompose
def test_decompose_metrics_excludes_constraint_edges() -> None:
    """Test that constraint edges are excluded from coupling metrics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        create_test_node(tmp_path, "S-001", "specification", "Spec", "core")
        create_test_node(tmp_path, "X-001", "constraint", "Constraint", "core")
        create_test_node(tmp_path, "O-001", "outcome", "Outcome", "other")

        edges = [
            # Structural edge (should be counted)
            {"from": "S-001", "to": "O-001", "type": "implements"},
            # Constraint edge (should NOT be counted)
            {"from": "S-001", "to": "X-001", "type": "satisfies"},
        ]

        subsystems = {
            "core": {"nodes": ["S-001", "X-001"]},
            "other": {"nodes": ["O-001"]},
        }
        create_test_graph_index(tmp_path, edges, subsystems)

        # Mock config
        import jig.cli.decompose

        original_load_config = jig.cli.decompose.load_config
        jig.cli.decompose.load_config = lambda: mock_config(tmp_path)

        try:
            runner = CliRunner()
            result = runner.invoke(decompose, ["metrics", "--subsystem", "core"])

            # Verify output
            assert result.exit_code == 0
            # Should have 0 internal edges (satisfies is excluded)
            # and 1 external edge (implements)
            assert "Internal edges: 0" in result.output
            assert "External edges: 1" in result.output
        finally:
            jig.cli.decompose.load_config = original_load_config


def test_decompose_report_generates_markdown() -> None:
    """Test decompose report command generates markdown."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create simple graph
        create_test_node(tmp_path, "O-001", "outcome", "Test", "core")

        subsystems = {"core": {"nodes": ["O-001"]}}
        create_test_graph_index(tmp_path, [], subsystems)

        # Mock config
        import jig.cli.decompose

        original_load_config = jig.cli.decompose.load_config
        jig.cli.decompose.load_config = lambda: mock_config(tmp_path)

        try:
            runner = CliRunner()
            result = runner.invoke(decompose, ["report"])

            # Verify output
            assert result.exit_code == 0
            assert "# Decomposability Analysis Report" in result.output
            assert "## Overall Metrics" in result.output
            assert "## Per-Subsystem Metrics" in result.output
            assert "## Recommendations" in result.output
        finally:
            jig.cli.decompose.load_config = original_load_config


def test_decompose_report_outputs_to_file() -> None:
    """Test decompose report writes to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        create_test_node(tmp_path, "O-001", "outcome", "Test", "core")
        subsystems = {"core": {"nodes": ["O-001"]}}
        create_test_graph_index(tmp_path, [], subsystems)

        # Mock config
        import jig.cli.decompose

        original_load_config = jig.cli.decompose.load_config
        jig.cli.decompose.load_config = lambda: mock_config(tmp_path)

        try:
            runner = CliRunner()
            output_file = tmp_path / "report.md"
            result = runner.invoke(decompose, ["report", "--output", str(output_file)])

            # Verify command succeeded
            assert result.exit_code == 0
            assert "Report written to" in result.output

            # Verify file was created
            assert output_file.exists()
            content = output_file.read_text()
            assert "# Decomposability Analysis Report" in content
        finally:
            jig.cli.decompose.load_config = original_load_config


def test_decompose_metrics_nonexistent_subsystem() -> None:
    """Test metrics command handles nonexistent subsystem."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        create_test_node(tmp_path, "O-001", "outcome", "Test", "core")
        subsystems = {"core": {"nodes": ["O-001"]}}
        create_test_graph_index(tmp_path, [], subsystems)

        # Mock config
        import jig.cli.decompose

        original_load_config = jig.cli.decompose.load_config
        jig.cli.decompose.load_config = lambda: mock_config(tmp_path)

        try:
            runner = CliRunner()
            result = runner.invoke(decompose, ["metrics", "--subsystem", "nonexistent"])

            # Should error gracefully
            assert result.exit_code == 1
            assert "not found" in result.output.lower()
        finally:
            jig.cli.decompose.load_config = original_load_config


def test_decompose_metrics_yaml_output() -> None:
    """Test metrics command with YAML output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        create_test_node(tmp_path, "O-001", "outcome", "Test", "core")
        create_test_node(tmp_path, "O-002", "outcome", "Test2", "core")

        edges = [{"from": "O-001", "to": "O-002", "type": "depends_on"}]
        subsystems = {"core": {"nodes": ["O-001", "O-002"]}}
        create_test_graph_index(tmp_path, edges, subsystems)

        # Mock config
        import jig.cli.decompose

        original_load_config = jig.cli.decompose.load_config
        jig.cli.decompose.load_config = lambda: mock_config(tmp_path)

        try:
            runner = CliRunner()
            result = runner.invoke(decompose, ["metrics", "--format", "yaml"])

            # Verify output
            assert result.exit_code == 0
            # Should be valid YAML
            import yaml

            data = yaml.safe_load(result.output)
            assert "modularity" in data
            assert "subsystem_count" in data
            assert "subsystems" in data
        finally:
            jig.cli.decompose.load_config = original_load_config
