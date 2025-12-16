"""Tests for coverage collection functionality.

These tests verify S-066: T→F Edge Collection via Coverage.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import jig
from click.testing import CliRunner

from jig.audit.coverage import ensure_audits_directory, run_coverage_collection
from jig.cli.main import cli
from jig.config import JigConfig, PathsConfig


def _make_test_config(tmp_path: Path) -> JigConfig:
    """Create a test JigConfig pointing to a temporary directory."""
    jig_root = tmp_path / "jig"
    jig_root.mkdir(parents=True, exist_ok=True)

    paths = PathsConfig(
        source=tmp_path / "src",
        tests=tmp_path / "tests",
        jig_root=jig_root,
        specifications=jig_root / "specifications",
        outcomes=jig_root / "outcomes",
        bricks=jig_root / "bricks.yaml",
        generated=jig_root / "generated",
    )

    return JigConfig(
        paths=paths,
        project_root=tmp_path,
        config_file_path=None,
        has_config_file=False,
    )


@jig.verifies("S-066")
def test_audit_command_group_exists():
    """jigy audit command group exists and shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["audit", "--help"])

    assert result.exit_code == 0
    assert "coverage" in result.output
    assert "audit" in result.output.lower()


@jig.verifies("S-066")
def test_audit_coverage_command_exists():
    """jigy audit coverage command exists and shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["audit", "coverage", "--help"])

    assert result.exit_code == 0
    assert "coverage" in result.output.lower()
    assert "T→F" in result.output or "test" in result.output.lower()


@jig.verifies("S-066")
def test_audit_bare_shows_help():
    """jigy audit (bare) shows help with available subcommands."""
    runner = CliRunner()
    result = runner.invoke(cli, ["audit"])

    assert result.exit_code == 0
    assert "coverage" in result.output


@jig.verifies("S-066")
def test_ensure_audits_directory_creates_path(tmp_path):
    """ensure_audits_directory creates jig/audits/records/ if missing."""
    config = _make_test_config(tmp_path)

    # Ensure directory doesn't exist yet
    audits_dir = config.paths.jig_root / "audits" / "records"
    assert not audits_dir.exists()

    # Call function
    result_path = ensure_audits_directory(config)

    # Verify directory was created
    assert result_path.exists()
    assert result_path.is_dir()
    assert result_path == audits_dir


@jig.verifies("S-066")
def test_ensure_audits_directory_idempotent(tmp_path):
    """ensure_audits_directory is idempotent (can be called multiple times)."""
    config = _make_test_config(tmp_path)

    # Create directory twice
    path1 = ensure_audits_directory(config)
    path2 = ensure_audits_directory(config)

    # Both should succeed and return same path
    assert path1 == path2
    assert path1.exists()


@jig.verifies("S-066")
def test_run_coverage_collection_builds_correct_command(tmp_path):
    """run_coverage_collection builds pytest command with coverage flags."""
    config = _make_test_config(tmp_path)

    # Create minimal test directory
    config.paths.tests.mkdir(parents=True, exist_ok=True)
    (config.paths.tests / "test_dummy.py").write_text("def test_pass(): pass")

    # Mock subprocess.run to capture the command
    with patch("jig.audit.coverage.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        run_coverage_collection(config)

        # Verify subprocess.run was called
        assert mock_run.called
        call_args = mock_run.call_args

        # Check command contains expected flags
        cmd = call_args[0][0]  # First positional arg is the command list
        cmd_str = " ".join(cmd)

        assert "pytest" in cmd_str
        assert "--cov=" in cmd_str
        assert "--cov-context=test" in cmd_str


@jig.verifies("S-066")
def test_run_coverage_collection_returns_coverage_path(tmp_path):
    """run_coverage_collection returns path to .coverage file."""
    config = _make_test_config(tmp_path)

    # Create minimal test directory
    config.paths.tests.mkdir(parents=True, exist_ok=True)

    with patch("jig.audit.coverage.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        exit_code, coverage_path = run_coverage_collection(config)

        assert coverage_path == config.project_root / ".coverage"
        assert exit_code == 0


@jig.verifies("S-066")
def test_run_coverage_collection_captures_test_failures(tmp_path):
    """run_coverage_collection returns non-zero exit code on test failures."""
    config = _make_test_config(tmp_path)

    # Create minimal test directory
    config.paths.tests.mkdir(parents=True, exist_ok=True)

    with patch("jig.audit.coverage.subprocess.run") as mock_run:
        # Simulate test failure
        mock_run.return_value = MagicMock(returncode=1)

        exit_code, coverage_path = run_coverage_collection(config)

        # Exit code should be non-zero but coverage path still returned
        assert exit_code == 1
        assert coverage_path is not None


@jig.verifies("S-066")
def test_help_shows_audit_command():
    """Main CLI help shows audit command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "audit" in result.output
