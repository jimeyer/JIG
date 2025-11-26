"""Integration tests for CLI commands.

Tests verify that the CLI commands work correctly end-to-end.

Verifies S-001, S-003, S-006: CLI integration.
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

import jig
from jig.cli.main import cli


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Create a temporary project root with source files."""
    project_root = tmp_path / "test_project"
    src_dir = project_root / "src"
    src_dir.mkdir(parents=True)

    # Create a simple Python module
    (src_dir / "example.py").write_text(
        """
import jig

@jig.implements("S-001")
def example_function():
    '''Example function.'''
    pass
"""
    )

    return project_root


@jig.verifies("S-001", "S-003")
def test_cli_impl_rebuild_basic(runner: CliRunner, project_root: Path) -> None:
    """Test basic jig impl rebuild command."""
    result = runner.invoke(
        cli,
        [
            "impl",
            "rebuild",
            "--project-root",
            str(project_root),
            "--no-timestamp",
        ],
    )

    # Should succeed
    assert result.exit_code == 0
    assert "Graph generated successfully" in result.output

    # Should create output file
    output_path = project_root / "jig" / "generated" / "implementation-graph.ndjson"
    assert output_path.exists()


@jig.verifies("S-003")
def test_cli_impl_rebuild_custom_output(runner: CliRunner, project_root: Path, tmp_path: Path) -> None:
    """Test jig impl rebuild with custom output path."""
    output_path = tmp_path / "custom-graph.ndjson"

    result = runner.invoke(
        cli,
        [
            "impl",
            "rebuild",
            "--project-root",
            str(project_root),
            "--output",
            str(output_path),
            "--no-timestamp",
        ],
    )

    # Should succeed
    assert result.exit_code == 0

    # Should create file at custom location
    assert output_path.exists()


@jig.verifies("S-001")
def test_cli_impl_rebuild_with_exclude(runner: CliRunner, tmp_path: Path) -> None:
    """Test jig impl rebuild with exclude patterns."""
    project_root = tmp_path / "test_project"
    src_dir = project_root / "src"
    src_dir.mkdir(parents=True)

    # Create files
    (src_dir / "include.py").write_text("def include(): pass")
    (src_dir / "test_exclude.py").write_text("def test(): pass")

    result = runner.invoke(
        cli,
        [
            "impl",
            "rebuild",
            "--project-root",
            str(project_root),
            "--exclude",
            "**/test_*.py",
            "--no-timestamp",
        ],
    )

    # Should succeed
    assert result.exit_code == 0

    # Read output to verify test file was excluded
    output_path = project_root / "jig" / "generated" / "implementation-graph.ndjson"
    content = output_path.read_text()

    # Should have include.py but not test_exclude.py
    assert "include.py" in content
    assert "test_exclude" not in content


@jig.verifies("S-001")
def test_cli_impl_rebuild_verbose(runner: CliRunner, project_root: Path) -> None:
    """Test jig impl rebuild with verbose output."""
    result = runner.invoke(
        cli,
        [
            "impl",
            "rebuild",
            "--project-root",
            str(project_root),
            "--verbose",
            "--no-timestamp",
        ],
    )

    # Should succeed
    assert result.exit_code == 0

    # Should have verbose output (Building message is always shown)
    assert "Building" in result.output
    assert "Graph generated successfully" in result.output


@jig.verifies("S-006")
def test_cli_impl_rebuild_parse_error_strict(runner: CliRunner, tmp_path: Path) -> None:
    """Test that parse errors fail in strict mode."""
    project_root = tmp_path / "bad_project"
    src_dir = project_root / "src"
    src_dir.mkdir(parents=True)

    (src_dir / "bad.py").write_text("def bad(:\n    pass")  # Invalid syntax

    result = runner.invoke(
        cli,
        [
            "impl",
            "rebuild",
            "--project-root",
            str(project_root),
            "--strict",
        ],
    )

    # Should fail
    assert result.exit_code == 1
    assert "Error" in result.output


@jig.verifies("S-006")
def test_cli_impl_rebuild_parse_error_lenient(runner: CliRunner, tmp_path: Path) -> None:
    """Test that parse errors are skipped in lenient mode."""
    project_root = tmp_path / "mixed_project"
    src_dir = project_root / "src"
    src_dir.mkdir(parents=True)

    (src_dir / "good.py").write_text("def good(): pass")
    (src_dir / "bad.py").write_text("def bad(:\n    pass")  # Invalid syntax

    result = runner.invoke(
        cli,
        [
            "impl",
            "rebuild",
            "--project-root",
            str(project_root),
            "--lenient",
            "--no-timestamp",
        ],
    )

    # Should succeed (skipping bad file)
    assert result.exit_code == 0
    assert "Graph generated successfully" in result.output


@jig.verifies("S-003")
def test_cli_impl_rebuild_output_format(runner: CliRunner, project_root: Path) -> None:
    """Test that output is valid NDJSON."""
    result = runner.invoke(
        cli,
        [
            "impl",
            "rebuild",
            "--project-root",
            str(project_root),
            "--no-timestamp",
        ],
    )

    # Should succeed
    assert result.exit_code == 0

    # Read and validate NDJSON
    output_path = project_root / "jig" / "generated" / "implementation-graph.ndjson"
    lines = output_path.read_text().strip().split("\n")

    # Each line should be valid JSON
    for line in lines:
        obj = json.loads(line)
        assert isinstance(obj, dict)

    # First line should be metadata
    metadata = json.loads(lines[0])
    assert "_meta" in metadata


@jig.verifies("S-001")
def test_cli_reports_node_edge_counts(runner: CliRunner, project_root: Path) -> None:
    """Test that CLI reports node and edge counts."""
    result = runner.invoke(
        cli,
        [
            "impl",
            "rebuild",
            "--project-root",
            str(project_root),
            "--no-timestamp",
        ],
    )

    # Should report counts
    assert "Nodes:" in result.output
    assert "Edges:" in result.output
    assert "Output:" in result.output


@jig.verifies("S-001", "S-003")
def test_cli_help_messages() -> None:
    """Test that CLI provides helpful help messages."""
    runner = CliRunner()

    # Test main help
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "JIG" in result.output or "jig" in result.output.lower()

    # Test impl help
    result = runner.invoke(cli, ["impl", "--help"])
    assert result.exit_code == 0
    assert "Implementation graph" in result.output or "impl" in result.output

    # Test rebuild help
    result = runner.invoke(cli, ["impl", "rebuild", "--help"])
    assert result.exit_code == 0
    assert "project-root" in result.output
    assert "source-dir" in result.output or "output" in result.output
