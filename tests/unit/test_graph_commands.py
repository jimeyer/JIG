# @jig T-JIGY-012 verifies:S-JIGY-005 subsystem:jigy-tool
"""Unit tests for graph query commands (WU5)."""

from pathlib import Path
from click.testing import CliRunner

import pytest

from jig.cli.graph import graph
from jig.core.graph import Graph
from tests.helpers.graph_fixtures import create_test_graph


@pytest.fixture
def setup_test_graph(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a test JIG directory with sample nodes."""
    jig_dir = create_test_graph(
        tmp_path,
        nodes=[
            {
                "id": "O-TEST-001",
                "type": "outcome",
                "title": "First outcome",
                "subsystem": "test",
            },
            {
                "id": "O-TEST-002",
                "type": "outcome",
                "title": "Second outcome",
                "subsystem": "test",
            },
            {
                "id": "O-TEST-003",
                "type": "outcome",
                "title": "Isolated outcome",
                "subsystem": "test",
            },
            {
                "id": "S-TEST-001",
                "type": "specification",
                "title": "First spec",
                "subsystem": "test",
                "implements": ["O-TEST-001"],
            },
            {
                "id": "S-TEST-002",
                "type": "specification",
                "title": "Second spec",
                "subsystem": "test",
                "implements": ["O-TEST-001", "O-TEST-002"],
            },
            {
                "id": "C-TEST-001",
                "type": "code",
                "title": "Test code",
                "subsystem": "test",
                "implements": ["S-TEST-001"],
            },
            {
                "id": "T-TEST-001",
                "type": "test",
                "title": "Test case",
                "subsystem": "test",
                "verifies": ["S-TEST-001"],
            },
        ],
        subsystems={"test": {"id": "test"}},
    )

    # Mock config to point to test directory
    from jig.core.config import JigConfig
    config = JigConfig(
        project_name="test",
        intent_dir=jig_dir,
        delta_dir=tmp_path / "deltas",
        templates_dir=tmp_path / "templates",
        graph_index_file=jig_dir / "graph-index.json",
        subsystems_file=jig_dir / "subsystems.yaml"
    )
    monkeypatch.setattr("jig.cli.graph.load_config", lambda: config)

    return jig_dir


# @jig T-JIGY-013 verifies:S-JIGY-005 subsystem:jigy-tool
def test_graph_show_displays_node_details(setup_test_graph: Path) -> None:
    """Test 'jigy graph show' displays node details."""
    runner = CliRunner()
    result = runner.invoke(graph, ["show", "O-TEST-001"])
    
    assert result.exit_code == 0
    assert "O-TEST-001" in result.output
    assert "Type: outcome" in result.output
    assert "Title: First outcome" in result.output
    assert "Subsystem: test" in result.output


def test_graph_show_displays_dependencies(setup_test_graph: Path) -> None:
    """Test 'jigy graph show' displays dependencies."""
    runner = CliRunner()
    result = runner.invoke(graph, ["show", "S-TEST-001"])
    
    assert result.exit_code == 0
    assert "Dependencies" in result.output
    assert "O-TEST-001" in result.output


def test_graph_show_displays_dependents(setup_test_graph: Path) -> None:
    """Test 'jigy graph show' displays dependents."""
    runner = CliRunner()
    result = runner.invoke(graph, ["show", "O-TEST-001"])
    
    assert result.exit_code == 0
    assert "Dependents" in result.output
    assert "S-TEST-001" in result.output
    assert "S-TEST-002" in result.output


def test_graph_show_node_not_found(setup_test_graph: Path) -> None:
    """Test 'jigy graph show' with non-existent node."""
    runner = CliRunner()
    result = runner.invoke(graph, ["show", "O-MISSING-999"])
    
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_graph_show_displays_body_content(setup_test_graph: Path) -> None:
    """Test 'jigy graph show' displays node body content."""
    runner = CliRunner()
    result = runner.invoke(graph, ["show", "O-TEST-001"])
    
    assert result.exit_code == 0
    assert "First Outcome" in result.output
    assert "first test outcome" in result.output


def test_graph_list_all_nodes(setup_test_graph: Path) -> None:
    """Test 'jigy graph list' displays all nodes."""
    runner = CliRunner()
    result = runner.invoke(graph, ["list"])
    
    assert result.exit_code == 0
    assert "O-TEST-001" in result.output
    assert "O-TEST-002" in result.output
    assert "S-TEST-001" in result.output
    assert "S-TEST-002" in result.output
    assert "C-TEST-001" in result.output
    assert "T-TEST-001" in result.output


def test_graph_list_filter_by_type(setup_test_graph: Path) -> None:
    """Test 'jigy graph list --type' filters nodes by type."""
    runner = CliRunner()
    result = runner.invoke(graph, ["list", "--type", "outcome"])
    
    assert result.exit_code == 0
    assert "O-TEST-001" in result.output
    assert "O-TEST-002" in result.output
    # Should not include specs
    assert "S-TEST-001" not in result.output
    assert "S-TEST-002" not in result.output


def test_graph_list_filter_by_subsystem(setup_test_graph: Path) -> None:
    """Test 'jigy graph list --subsystem' filters nodes by subsystem."""
    runner = CliRunner()
    result = runner.invoke(graph, ["list", "--subsystem", "test"])
    
    assert result.exit_code == 0
    assert "O-TEST-001" in result.output
    assert "S-TEST-001" in result.output


def test_graph_list_compact_format(setup_test_graph: Path) -> None:
    """Test 'jigy graph list --format compact' uses compact format."""
    runner = CliRunner()
    result = runner.invoke(graph, ["list", "--format", "compact"])
    
    assert result.exit_code == 0
    assert "Outcomes" in result.output or "Specifications" in result.output
    # Compact format groups by type


def test_graph_list_yaml_format(setup_test_graph: Path) -> None:
    """Test 'jigy graph list --format yaml' outputs YAML."""
    runner = CliRunner()
    result = runner.invoke(graph, ["list", "--format", "yaml"])
    
    assert result.exit_code == 0
    assert "id:" in result.output
    assert "type:" in result.output
    assert "title:" in result.output


def test_graph_deps_shows_dependency_tree(setup_test_graph: Path) -> None:
    """Test 'jigy graph deps' shows dependency tree."""
    runner = CliRunner()
    result = runner.invoke(graph, ["deps", "S-TEST-001"])
    
    assert result.exit_code == 0
    assert "Dependency tree" in result.output
    assert "S-TEST-001" in result.output
    assert "O-TEST-001" in result.output


def test_graph_deps_node_not_found(setup_test_graph: Path) -> None:
    """Test 'jigy graph deps' with non-existent node."""
    runner = CliRunner()
    result = runner.invoke(graph, ["deps", "O-MISSING-999"])
    
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_graph_impact_shows_impact_tree(setup_test_graph: Path) -> None:
    """Test 'jigy graph impact' shows impact analysis."""
    runner = CliRunner()
    result = runner.invoke(graph, ["impact", "O-TEST-001"])
    
    assert result.exit_code == 0
    assert "Impact analysis" in result.output
    assert "O-TEST-001" in result.output
    assert "S-TEST-001" in result.output
    assert "S-TEST-002" in result.output


def test_graph_impact_node_not_found(setup_test_graph: Path) -> None:
    """Test 'jigy graph impact' with non-existent node."""
    runner = CliRunner()
    result = runner.invoke(graph, ["impact", "O-MISSING-999"])
    
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_graph_path_finds_shortest_path(setup_test_graph: Path) -> None:
    """Test 'jigy graph path' finds shortest path between nodes."""
    runner = CliRunner()
    result = runner.invoke(graph, ["path", "S-TEST-001", "O-TEST-001"])
    
    assert result.exit_code == 0
    assert "Path from" in result.output
    assert "S-TEST-001" in result.output
    assert "O-TEST-001" in result.output
    assert "→" in result.output


def test_graph_path_no_path_exists(setup_test_graph: Path) -> None:
    """Test 'jigy graph path' when no path exists."""
    runner = CliRunner()
    # O-TEST-003 is isolated, no path to O-TEST-001
    result = runner.invoke(graph, ["path", "O-TEST-003", "O-TEST-001"])
    
    assert result.exit_code == 0
    assert "No path found" in result.output


def test_graph_path_start_node_not_found(setup_test_graph: Path) -> None:
    """Test 'jigy graph path' with non-existent start node."""
    runner = CliRunner()
    result = runner.invoke(graph, ["path", "O-MISSING-999", "O-TEST-001"])
    
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_graph_path_end_node_not_found(setup_test_graph: Path) -> None:
    """Test 'jigy graph path' with non-existent end node."""
    runner = CliRunner()
    result = runner.invoke(graph, ["path", "O-TEST-001", "O-MISSING-999"])
    
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_graph_show_with_multiple_dependencies(setup_test_graph: Path) -> None:
    """Test 'jigy graph show' correctly displays multiple dependencies."""
    runner = CliRunner()
    result = runner.invoke(graph, ["show", "S-TEST-002"])
    
    assert result.exit_code == 0
    assert "Dependencies" in result.output
    assert "O-TEST-001" in result.output
    assert "O-TEST-002" in result.output


def test_graph_commands_performance(setup_test_graph: Path) -> None:
    """Test graph commands complete in reasonable time."""
    import time
    
    runner = CliRunner()
    
    # Test show command
    start = time.time()
    result = runner.invoke(graph, ["show", "O-TEST-001"])
    elapsed = time.time() - start
    assert result.exit_code == 0
    assert elapsed < 0.1  # Should be <100ms
    
    # Test list command
    start = time.time()
    result = runner.invoke(graph, ["list"])
    elapsed = time.time() - start
    assert result.exit_code == 0
    assert elapsed < 0.1  # Should be <100ms


def test_graph_list_empty_result(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test 'jigy graph list' with filters that match no nodes."""
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    (jig_dir / "outcomes").mkdir()
    (jig_dir / "specifications").mkdir()
    
    from jig.core.config import JigConfig
    config = JigConfig(
        project_name="test",
        intent_dir=jig_dir,
        delta_dir=tmp_path / "deltas",
        templates_dir=tmp_path / "templates",
        graph_index_file=jig_dir / "graph-index.yaml",
        subsystems_file=jig_dir / "subsystems.yaml"
    )
    monkeypatch.setattr("jig.cli.graph.load_config", lambda: config)
    
    runner = CliRunner()
    result = runner.invoke(graph, ["list", "--type", "outcome"])
    
    assert result.exit_code == 0
    assert "No nodes found" in result.output


def test_graph_show_node_with_no_dependencies(setup_test_graph: Path) -> None:
    """Test 'jigy graph show' for node with no dependencies."""
    runner = CliRunner()
    result = runner.invoke(graph, ["show", "O-TEST-002"])
    
    assert result.exit_code == 0
    assert "Dependencies" in result.output
    assert "(none)" in result.output


def test_graph_commands_with_code_and_test_nodes(setup_test_graph: Path) -> None:
    """Test graph commands work with C and T nodes."""
    runner = CliRunner()
    
    # Test show on code node
    result = runner.invoke(graph, ["show", "C-TEST-001"])
    assert result.exit_code == 0
    assert "C-TEST-001" in result.output
    assert "Type: code" in result.output
    
    # Test show on test node
    result = runner.invoke(graph, ["show", "T-TEST-001"])
    assert result.exit_code == 0
    assert "T-TEST-001" in result.output
    assert "Type: test" in result.output


def test_graph_list_combined_filters(setup_test_graph: Path) -> None:
    """Test 'jigy graph list' with combined type and subsystem filters."""
    runner = CliRunner()
    result = runner.invoke(graph, ["list", "--type", "specification", "--subsystem", "test"])
    
    assert result.exit_code == 0
    assert "S-TEST-001" in result.output
    assert "S-TEST-002" in result.output
    # Should not include outcomes even though they're in same subsystem
    assert "O-TEST-001" not in result.output

