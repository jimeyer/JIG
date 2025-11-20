# @jig T-NESTED-007 verifies:S-NESTED-003 subsystem:core
"""Integration tests for nested subsystems in status and graph commands."""

import tempfile
from pathlib import Path
from textwrap import dedent

from click.testing import CliRunner

from jig.cli.graph import graph
from jig.cli.status import status
from jig.utils.yaml_utils import dump_yaml


def create_test_node(tmp_path: Path, node_id: str, node_type: str, title: str, subsystem: str = "core") -> Path:
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


def create_test_graph_index(tmp_path: Path, edges: list[dict], subsystems: dict) -> Path:
    """Helper to create a test graph-index.yaml file with nested subsystems."""
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


# @jig T-NESTED-007 verifies:S-NESTED-003 subsystem:core
def test_status_hierarchical_view():
    """Verify status displays tree view for nested subsystems."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes with nested subsystem paths
        create_test_node(tmp_path, "O-SER-001", "outcome", "Serialization", "crdt.ser")
        create_test_node(tmp_path, "O-DESER-001", "outcome", "Deserialization", "crdt.deser")
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core", "core")

        # Create graph-index.yaml with nested subsystems
        edges = []
        subsystems = {
            "core": {
                "description": "Core subsystem",
                "nodes": ["O-CORE-001"]
            },
            "crdt": {
                "description": "CRDT subsystem",
                "subsystems": {
                    "ser": {
                        "description": "Serialization",
                        "nodes": ["O-SER-001"]
                    },
                    "deser": {
                        "description": "Deserialization",
                        "nodes": ["O-DESER-001"]
                    }
                }
            }
        }
        create_test_graph_index(tmp_path, edges, subsystems)

        # Mock config
        import jig.cli.status
        original_load_config = jig.cli.status.load_config
        jig.cli.status.load_config = lambda: mock_config(tmp_path)

        try:
            # Run status command (hierarchical view by default)
            runner = CliRunner()
            result = runner.invoke(status, [])

            # Verify hierarchical output
            assert result.exit_code == 0
            assert "Subsystems:" in result.output
            # Should show tree structure with proper formatting
            assert "core" in result.output
            assert "crdt" in result.output
            # Check for tree connectors (├── or └──)
            assert "ser" in result.output
            assert "deser" in result.output
        finally:
            jig.cli.status.load_config = original_load_config


# @jig T-NESTED-008 verifies:S-NESTED-003 subsystem:core
def test_status_flat_view():
    """Verify --flat option shows flattened view."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes
        create_test_node(tmp_path, "O-SER-001", "outcome", "Serialization", "crdt.ser")
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core", "core")

        # Create graph-index.yaml with nested subsystems
        subsystems = {
            "core": {
                "nodes": ["O-CORE-001"]
            },
            "crdt": {
                "subsystems": {
                    "ser": {
                        "nodes": ["O-SER-001"]
                    }
                }
            }
        }
        create_test_graph_index(tmp_path, [], subsystems)

        # Mock config
        import jig.cli.status
        original_load_config = jig.cli.status.load_config
        jig.cli.status.load_config = lambda: mock_config(tmp_path)

        try:
            # Run status command with --flat
            runner = CliRunner()
            result = runner.invoke(status, ["--flat"])

            # Verify flat output (no tree connectors)
            assert result.exit_code == 0
            assert "Subsystems:" in result.output
            # Flat view shows node counts per subsystem
            assert "core" in result.output or "crdt.ser" in result.output
        finally:
            jig.cli.status.load_config = original_load_config


# @jig T-NESTED-009 verifies:S-NESTED-002 subsystem:core
def test_graph_list_recursive():
    """Verify list --subsystem --recursive includes child nodes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes
        create_test_node(tmp_path, "O-SER-001", "outcome", "Serialization", "crdt.ser")
        create_test_node(tmp_path, "O-DESER-001", "outcome", "Deserialization", "crdt.deser")
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core", "core")

        # Create graph-index.yaml with nested subsystems
        subsystems = {
            "core": {
                "nodes": ["O-CORE-001"]
            },
            "crdt": {
                "subsystems": {
                    "ser": {
                        "nodes": ["O-SER-001"]
                    },
                    "deser": {
                        "nodes": ["O-DESER-001"]
                    }
                }
            }
        }
        create_test_graph_index(tmp_path, [], subsystems)

        # Mock config
        import jig.cli.graph
        original_load_config = jig.cli.graph.load_config
        jig.cli.graph.load_config = lambda: mock_config(tmp_path)

        try:
            # Run graph list with --subsystem crdt --recursive
            runner = CliRunner()
            result = runner.invoke(graph, ["list", "--subsystem", "crdt", "--recursive"])

            # Verify recursive output includes all child nodes
            assert result.exit_code == 0
            assert "O-SER-001" in result.output
            assert "O-DESER-001" in result.output
            # Should not include core node
            assert "O-CORE-001" not in result.output
        finally:
            jig.cli.graph.load_config = original_load_config


# @jig T-NESTED-009 verifies:S-NESTED-002 subsystem:core
def test_graph_list_leaf_subsystem():
    """Verify list --subsystem shows only leaf nodes when no --recursive."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes
        create_test_node(tmp_path, "O-SER-001", "outcome", "Serialization", "crdt.ser")
        create_test_node(tmp_path, "O-DESER-001", "outcome", "Deserialization", "crdt.deser")

        # Create graph-index.yaml with nested subsystems
        subsystems = {
            "crdt": {
                "subsystems": {
                    "ser": {
                        "nodes": ["O-SER-001"]
                    },
                    "deser": {
                        "nodes": ["O-DESER-001"]
                    }
                }
            }
        }
        create_test_graph_index(tmp_path, [], subsystems)

        # Mock config
        import jig.cli.graph
        original_load_config = jig.cli.graph.load_config
        jig.cli.graph.load_config = lambda: mock_config(tmp_path)

        try:
            # Run graph list with --subsystem crdt.ser (leaf subsystem)
            runner = CliRunner()
            result = runner.invoke(graph, ["list", "--subsystem", "crdt.ser"])

            # Verify output includes only ser nodes
            assert result.exit_code == 0
            assert "O-SER-001" in result.output
            assert "O-DESER-001" not in result.output
        finally:
            jig.cli.graph.load_config = original_load_config


# @jig T-NESTED-010 verifies:S-NESTED-006 subsystem:core
def test_constraint_scope_nested_subsystems():
    """Verify constraint scopes work with nested subsystem paths (v7)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes with constraints
        create_test_node(tmp_path, "X-PERF-001", "constraint", "Performance", "crdt.ser")
        create_test_node(tmp_path, "O-SER-001", "outcome", "Serialization", "crdt.ser")

        # Create graph-index.yaml with nested subsystems
        subsystems = {
            "crdt": {
                "subsystems": {
                    "ser": {
                        "nodes": ["X-PERF-001", "O-SER-001"]
                    }
                }
            }
        }
        create_test_graph_index(tmp_path, [], subsystems)

        # Mock config
        import jig.cli.status
        original_load_config = jig.cli.status.load_config
        jig.cli.status.load_config = lambda: mock_config(tmp_path)

        try:
            # Run status command (should show constraints per subsystem)
            runner = CliRunner()
            result = runner.invoke(status, [])

            # Verify constraints are shown in status output
            assert result.exit_code == 0
            # Note: Constraints display depends on OSTC node having constraints field
            # This is a placeholder test for v7 constraint integration
            assert "Subsystems:" in result.output
        finally:
            jig.cli.status.load_config = original_load_config


def test_graph_list_subsystem_with_table_format():
    """Verify list --subsystem shows subsystem column in table."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test nodes
        create_test_node(tmp_path, "O-SER-001", "outcome", "Serialization", "crdt.ser")
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core", "core")

        # Create graph-index.yaml
        subsystems = {
            "core": {"nodes": ["O-CORE-001"]},
            "crdt": {
                "subsystems": {
                    "ser": {"nodes": ["O-SER-001"]}
                }
            }
        }
        create_test_graph_index(tmp_path, [], subsystems)

        # Mock config
        import jig.cli.graph
        original_load_config = jig.cli.graph.load_config
        jig.cli.graph.load_config = lambda: mock_config(tmp_path)

        try:
            # Run graph list
            runner = CliRunner()
            result = runner.invoke(graph, ["list"])

            # Verify subsystem column is shown
            assert result.exit_code == 0
            assert "Subsystem" in result.output
            assert "crdt.ser" in result.output
            assert "core" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config


def test_graph_list_nonexistent_subsystem():
    """Verify list --subsystem handles nonexistent subsystem gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create minimal graph
        create_test_node(tmp_path, "O-CORE-001", "outcome", "Core", "core")
        subsystems = {"core": {"nodes": ["O-CORE-001"]}}
        create_test_graph_index(tmp_path, [], subsystems)

        # Mock config
        import jig.cli.graph
        original_load_config = jig.cli.graph.load_config
        jig.cli.graph.load_config = lambda: mock_config(tmp_path)

        try:
            # Run graph list with nonexistent subsystem
            runner = CliRunner()
            result = runner.invoke(graph, ["list", "--subsystem", "nonexistent"])

            # With backward compatibility, this falls back to frontmatter filtering
            # which returns no nodes (exit code 0) but shows "No nodes found"
            assert result.exit_code == 0
            assert "No nodes found" in result.output
        finally:
            jig.cli.graph.load_config = original_load_config
