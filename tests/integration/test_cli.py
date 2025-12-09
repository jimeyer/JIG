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
    assert "generated successfully" in result.output

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

    # Should have verbose output (Generating message is always shown)
    assert "Generating" in result.output
    assert "generated successfully" in result.output


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
    assert "generated successfully" in result.output


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


@pytest.fixture
def full_project(tmp_path: Path) -> Path:
    """Create a complete test project with all JIG artifacts."""
    project_root = tmp_path / "full_project"
    src_dir = project_root / "src"
    jig_dir = project_root / "jig"
    specs_dir = jig_dir / "specifications"
    outcomes_dir = jig_dir / "outcomes"

    # Create directories
    src_dir.mkdir(parents=True)
    specs_dir.mkdir(parents=True)
    outcomes_dir.mkdir(parents=True)

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

    # Create specification
    (specs_dir / "S-001.md").write_text(
        """---
id: S-001
type: specification
---

# Example Specification

Example spec for testing.
"""
    )

    # Create outcome
    (outcomes_dir / "O-001.md").write_text(
        """---
id: O-001
type: outcome
specifies:
  - S-001
---

# Example Outcome

Example outcome for testing.
"""
    )

    # Create bricks.yaml
    (jig_dir / "bricks.yaml").write_text(
        """bricks:
  - id: B-example
    name: Example Brick
    layer: 0
    units:
      - M-example
"""
    )

    return project_root


def test_cli_rebuild_success(runner: CliRunner, full_project: Path) -> None:
    """Test that rebuild runs all five steps successfully."""
    result = runner.invoke(
        cli,
        [
            "rebuild",
            "--project-root",
            str(full_project),
        ],
    )

    # Should succeed
    assert result.exit_code == 0, f"Command failed with output:\n{result.output}"

    # Should show all five steps
    assert "Step 1/5: Validating JIG artifacts" in result.output
    assert "Step 2/5: Rebuilding implementation graph" in result.output
    assert "Step 3/5: Rebuilding intent graph" in result.output
    assert "Step 4/5: Rebuilding verification graph" in result.output
    assert "Step 5/5: Displaying layer structure" in result.output

    # Should show success message
    assert "Complete! All JIG artifacts rebuilt successfully" in result.output

    # Should create all graph files
    impl_graph = full_project / "jig" / "generated" / "implementation-graph.ndjson"
    intent_graph = full_project / "jig" / "generated" / "intent-graph.ndjson"
    verify_graph = full_project / "jig" / "generated" / "verification-graph.ndjson"
    assert impl_graph.exists(), "Implementation graph not created"
    assert intent_graph.exists(), "Intent graph not created"
    assert verify_graph.exists(), "Verification graph not created"


def test_cli_rebuild_with_verbose(runner: CliRunner, full_project: Path) -> None:
    """Test rebuild with verbose flag."""
    result = runner.invoke(
        cli,
        [
            "rebuild",
            "--project-root",
            str(full_project),
            "--verbose",
        ],
    )

    # Should succeed
    assert result.exit_code == 0

    # Should show all steps
    assert "Step 1/5" in result.output
    assert "Step 2/5" in result.output
    assert "Step 3/5" in result.output
    assert "Step 4/5" in result.output
    assert "Step 5/5" in result.output


def test_cli_rebuild_stops_on_validation_error(runner: CliRunner, tmp_path: Path) -> None:
    """Test that rebuild stops when validation fails."""
    project_root = tmp_path / "bad_project"
    jig_dir = project_root / "jig"
    specs_dir = jig_dir / "specifications"
    specs_dir.mkdir(parents=True)

    # Create invalid specification (missing type field)
    (specs_dir / "S-001.md").write_text(
        """---
id: S-001
---

# Bad Spec
"""
    )

    result = runner.invoke(
        cli,
        [
            "rebuild",
            "--project-root",
            str(project_root),
        ],
    )

    # Should fail
    assert result.exit_code != 0

    # Should show step 1
    assert "Step 1/5: Validating" in result.output

    # Should show validation failure
    assert "Validation failed" in result.output or "Error" in result.output

    # Should NOT continue to step 2
    assert "Step 2/5" not in result.output


def test_cli_rebuild_help(runner: CliRunner) -> None:
    """Test that rebuild command has helpful documentation."""
    result = runner.invoke(cli, ["rebuild", "--help"])

    assert result.exit_code == 0
    assert "rebuild" in result.output.lower()
    assert "workflow" in result.output.lower()
    assert "validate" in result.output.lower() or "Validate" in result.output
