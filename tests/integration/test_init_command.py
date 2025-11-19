# @jig T-CLI-001 verifies:S-JIG-002 subsystem:core
"""Integration tests for jigy init command."""

import time
from pathlib import Path

import yaml
from click.testing import CliRunner

from jig.cli.main import cli
from jig.core.config import load_config


def test_jigy_init_creates_structure(tmp_path: Path) -> None:
    """Verify jigy init creates correct directory structure."""
    runner = CliRunner()

    # Run jigy init
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])

    # Should succeed
    assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}. Output: {result.output}"
    assert "✓ Initialized JIG" in result.output

    # Verify directories created
    assert (tmp_path / "jig" / "outcomes").is_dir()
    assert (tmp_path / "jig" / "specifications").is_dir()
    assert (tmp_path / "jig" / "tests").is_dir()
    assert (tmp_path / "jig" / "constraints").is_dir()

    # Verify graph-index.yaml created and valid
    graph_index_file = tmp_path / "jig" / "graph-index.yaml"
    assert graph_index_file.exists()
    graph_data = yaml.safe_load(graph_index_file.read_text())
    assert graph_data["version"] == "1.0"
    assert graph_data["nodes"] == []

    # Verify subsystems.yaml created and valid
    subsystems_file = tmp_path / "jig" / "subsystems.yaml"
    assert subsystems_file.exists()
    subsystems_data = yaml.safe_load(subsystems_file.read_text())
    assert "subsystems" in subsystems_data
    assert len(subsystems_data["subsystems"]) > 0

    # Verify jig.toml created and valid
    config_file = tmp_path / "jig.toml"
    assert config_file.exists()
    config = load_config(config_file)
    assert config.project_name == tmp_path.name
    assert config.intent_dir == Path("jig")


# @jig T-CLI-002 verifies:S-JIG-002 subsystem:core
def test_jigy_init_idempotent(tmp_path: Path) -> None:
    """Verify jigy init fails gracefully if already initialized."""
    runner = CliRunner()

    # Run jigy init first time
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Run jigy init second time - should fail
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 1
    assert "Error: JIG already initialized" in result.output
    assert "Found existing directory" in result.output


# @jig T-CLI-003 verifies:S-JIG-001 subsystem:core
def test_jigy_init_performance(tmp_path: Path) -> None:
    """Verify jigy init completes in <500ms."""
    runner = CliRunner()

    # Measure execution time
    start_time = time.time()
    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    elapsed_time = time.time() - start_time

    assert result.exit_code == 0
    assert elapsed_time < 0.5, f"jigy init took {elapsed_time:.3f}s, expected <0.5s"


def test_jigy_init_help() -> None:
    """Verify jigy init --help displays usage information."""
    runner = CliRunner()

    result = runner.invoke(cli, ["init", "--help"])

    assert result.exit_code == 0
    assert "Initialize JIG structure" in result.output
    assert "--path" in result.output


def test_jigy_version() -> None:
    """Verify jigy --version displays version information."""
    runner = CliRunner()

    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_jigy_help() -> None:
    """Verify jigy --help displays main help."""
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "JIG (Jig Intent Graph)" in result.output
    assert "constraint-driven development" in result.output
    assert "init" in result.output


def test_jigy_init_creates_valid_yaml_files(tmp_path: Path) -> None:
    """Verify created YAML files are valid and well-formed."""
    runner = CliRunner()

    result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0

    # Verify graph-index.yaml is valid YAML
    graph_index_file = tmp_path / "jig" / "graph-index.yaml"
    graph_yaml = graph_index_file.read_text()
    assert "version:" in graph_yaml
    assert "nodes:" in graph_yaml
    # Should parse without errors
    graph_data = yaml.safe_load(graph_yaml)
    assert isinstance(graph_data, dict)

    # Verify subsystems.yaml is valid YAML
    subsystems_file = tmp_path / "jig" / "subsystems.yaml"
    subsystems_yaml = subsystems_file.read_text()
    assert "subsystems:" in subsystems_yaml
    # Should parse without errors
    subsystems_data = yaml.safe_load(subsystems_yaml)
    assert isinstance(subsystems_data, dict)


def test_jigy_init_current_directory() -> None:
    """Verify jigy init works in current directory (default)."""
    runner = CliRunner()

    # Use CliRunner's isolated filesystem feature
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert Path("jig").is_dir()
        assert Path("jig/outcomes").is_dir()
        assert Path("jig.toml").exists()
