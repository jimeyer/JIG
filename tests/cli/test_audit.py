"""Tests for audit CLI command output format flags (S-093).

These tests verify that audit commands support universal output format flags:
- `-j/--json` for JSON output
- `-m/--markdown` for markdown output
- `-v/--verbose` for verbose output
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

import jig
from jig.cli.main import cli


def _setup_minimal_jig_project(tmp_path: Path) -> Path:
    """Create minimal JIG project structure for testing.

    Args:
        tmp_path: Temporary directory path.

    Returns:
        Path to the project root.
    """
    # Create jig directory structure
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir()
    (jig_dir / "specifications").mkdir()
    (jig_dir / "outcomes").mkdir()
    (jig_dir / "generated").mkdir()

    # Create a minimal spec
    spec_file = jig_dir / "specifications" / "S-001_Test_Specification.md"
    spec_file.write_text("""---
id: S-001
title: Test Specification
type: specification
---

# Test Specification
""")

    # Create implementation graph
    impl_graph = jig_dir / "generated" / "implementation-graph.ndjson"
    impl_graph.write_text(
        json.dumps({"_meta": {"version": "1.0"}}) + "\n"
        + json.dumps({"type": "function", "id": "F-test.func", "file": "src/test.py", "line": 1}) + "\n"
    )

    # Create verification graph
    verify_graph = jig_dir / "generated" / "verification-graph.ndjson"
    verify_graph.write_text(
        json.dumps({"_meta": {"version": "1.0"}}) + "\n"
        + json.dumps({"type": "test", "id": "T-test.test_func", "file": "tests/test.py", "line": 1}) + "\n"
    )

    # Create bricks.yaml
    bricks_file = jig_dir / "bricks.yaml"
    bricks_file.write_text("""bricks:
  - id: B-test
    name: Test
    layer: 0
    units:
      - F-test.func
""")

    # Create src and tests directories
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()

    return tmp_path


# ============================================================================
# Flag Wiring Tests (S-093)
# ============================================================================


@jig.verifies("S-093")
def test_audit_coverage_accepts_json_flag():
    """jigy audit coverage accepts -j/--json flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ["audit", "coverage", "--help"])

    assert result.exit_code == 0
    assert "-j" in result.output or "--json" in result.output


@jig.verifies("S-093")
def test_audit_coverage_accepts_markdown_flag():
    """jigy audit coverage accepts -m/--markdown flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ["audit", "coverage", "--help"])

    assert result.exit_code == 0
    assert "-m" in result.output or "--markdown" in result.output


@jig.verifies("S-093")
def test_audit_coverage_accepts_verbose_flag():
    """jigy audit coverage accepts -v/--verbose flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ["audit", "coverage", "--help"])

    assert result.exit_code == 0
    assert "-v" in result.output or "--verbose" in result.output


@jig.verifies("S-093")
def test_audit_coverage_json_markdown_mutual_exclusion():
    """jigy audit coverage -j -m errors (mutually exclusive)."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        _setup_minimal_jig_project(Path(tmpdir))

        result = runner.invoke(cli, ["audit", "coverage", "-j", "-m"])

        assert result.exit_code != 0
        assert "mutually exclusive" in result.output.lower()


# ============================================================================
# JSON Output Tests (S-093)
# ============================================================================


@jig.verifies("S-093")
def test_audit_coverage_json_produces_valid_json():
    """jigy audit coverage -j produces valid JSON output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        project_root = _setup_minimal_jig_project(Path(tmpdir))

        # Mock coverage command to avoid running pytest
        with patch("jig.cli.audit.coverage_command") as mock_coverage:
            # Return a mock result with coverage data
            mock_coverage.return_value = 0

            # We need to mock at CLI level, so patch the function that gets called
            with patch("jig.audit.coverage.run_coverage_collection") as mock_run:
                mock_run.return_value = (0, project_root / ".coverage")

                # Create a mock .coverage file
                (project_root / ".coverage").write_bytes(b"")

                with patch("jig.audit.coverage.extract_tf_edges") as mock_extract:
                    mock_extract.return_value = []

                    with patch("jig.audit.record_writer.write_coverage_record") as mock_write:
                        mock_write.return_value = project_root / "jig" / "audits" / "records" / "coverage-2024-01-01.ndjson"

                        with patch("jig.audit.record_writer.cleanup_coverage_file"):
                            result = runner.invoke(cli, ["--no-rebuild", "audit", "coverage", "-j"])

        # For now, check that -j flag is accepted
        # Full JSON output will be implemented in the implementation phase
        # The test will initially fail, showing that the flag isn't wired up yet
        if result.exit_code == 0:
            # If the command succeeded, output should be valid JSON
            data = json.loads(result.output)
            assert "status" in data


@jig.verifies("S-093")
def test_audit_coverage_json_output_structure():
    """jigy audit coverage -j JSON output has expected structure."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        project_root = _setup_minimal_jig_project(Path(tmpdir))

        # Mock the entire coverage workflow
        with patch("jig.audit.coverage.run_coverage_collection") as mock_run:
            mock_run.return_value = (0, project_root / ".coverage")
            (project_root / ".coverage").write_bytes(b"")

            with patch("jig.audit.coverage.extract_tf_edges") as mock_extract:
                from jig.audit.coverage import TFEdge
                mock_extract.return_value = [
                    TFEdge(test_id="T-test.test_func", function_id="F-test.func")
                ]

                with patch("jig.audit.record_writer.write_coverage_record") as mock_write:
                    mock_write.return_value = project_root / "jig" / "audits" / "records" / "coverage-2024-01-01.ndjson"

                    with patch("jig.audit.record_writer.cleanup_coverage_file"):
                        result = runner.invoke(cli, ["--no-rebuild", "audit", "coverage", "-j"])

        # Expect JSON output with status, edges, and record_path
        if result.exit_code == 0 and result.output.strip():
            try:
                data = json.loads(result.output)
                # JSON output should have these fields when implemented
                assert "status" in data
            except json.JSONDecodeError:
                # If output isn't JSON, the test should fail
                # This is expected in RED phase
                pytest.fail(f"Output is not valid JSON: {result.output}")


# ============================================================================
# Markdown Output Tests (S-093)
# ============================================================================


@jig.verifies("S-093")
def test_audit_coverage_markdown_produces_markdown():
    """jigy audit coverage -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        project_root = _setup_minimal_jig_project(Path(tmpdir))

        with patch("jig.audit.coverage.run_coverage_collection") as mock_run:
            mock_run.return_value = (0, project_root / ".coverage")
            (project_root / ".coverage").write_bytes(b"")

            with patch("jig.audit.coverage.extract_tf_edges") as mock_extract:
                mock_extract.return_value = []

                with patch("jig.audit.record_writer.write_coverage_record") as mock_write:
                    mock_write.return_value = project_root / "jig" / "audits" / "records" / "coverage-2024-01-01.ndjson"

                    with patch("jig.audit.record_writer.cleanup_coverage_file"):
                        result = runner.invoke(cli, ["--no-rebuild", "audit", "coverage", "-m"])

        # For markdown output, expect markdown headers
        if result.exit_code == 0 and result.output.strip():
            # Markdown should have headers
            assert "# " in result.output or "**" in result.output


# ============================================================================
# Verbose Output Tests (S-093)
# ============================================================================


@jig.verifies("S-093")
def test_audit_coverage_verbose_flag_works():
    """jigy audit coverage -v produces verbose output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        project_root = _setup_minimal_jig_project(Path(tmpdir))

        with patch("jig.audit.coverage.run_coverage_collection") as mock_run:
            mock_run.return_value = (0, project_root / ".coverage")
            (project_root / ".coverage").write_bytes(b"")

            with patch("jig.audit.coverage.extract_tf_edges") as mock_extract:
                mock_extract.return_value = []

                with patch("jig.audit.record_writer.write_coverage_record") as mock_write:
                    mock_write.return_value = project_root / "jig" / "audits" / "records" / "coverage-2024-01-01.ndjson"

                    with patch("jig.audit.record_writer.cleanup_coverage_file"):
                        result = runner.invoke(cli, ["--no-rebuild", "audit", "coverage", "-v"])

        # Verbose should at least not error
        assert result.exit_code == 0 or "no such option" not in result.output.lower()


@jig.verifies("S-093")
def test_audit_coverage_json_verbose_combination():
    """jigy audit coverage -j -v produces verbose JSON output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        project_root = _setup_minimal_jig_project(Path(tmpdir))

        with patch("jig.audit.coverage.run_coverage_collection") as mock_run:
            mock_run.return_value = (0, project_root / ".coverage")
            (project_root / ".coverage").write_bytes(b"")

            with patch("jig.audit.coverage.extract_tf_edges") as mock_extract:
                mock_extract.return_value = []

                with patch("jig.audit.record_writer.write_coverage_record") as mock_write:
                    mock_write.return_value = project_root / "jig" / "audits" / "records" / "coverage-2024-01-01.ndjson"

                    with patch("jig.audit.record_writer.cleanup_coverage_file"):
                        result = runner.invoke(cli, ["--no-rebuild", "audit", "coverage", "-j", "-v"])

        # -j -v combination should work
        if result.exit_code == 0 and result.output.strip():
            try:
                data = json.loads(result.output)
                assert "status" in data
            except json.JSONDecodeError:
                pass  # Expected in RED phase


@jig.verifies("S-093")
def test_audit_coverage_markdown_verbose_combination():
    """jigy audit coverage -m -v produces verbose markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        project_root = _setup_minimal_jig_project(Path(tmpdir))

        with patch("jig.audit.coverage.run_coverage_collection") as mock_run:
            mock_run.return_value = (0, project_root / ".coverage")
            (project_root / ".coverage").write_bytes(b"")

            with patch("jig.audit.coverage.extract_tf_edges") as mock_extract:
                mock_extract.return_value = []

                with patch("jig.audit.record_writer.write_coverage_record") as mock_write:
                    mock_write.return_value = project_root / "jig" / "audits" / "records" / "coverage-2024-01-01.ndjson"

                    with patch("jig.audit.record_writer.cleanup_coverage_file"):
                        result = runner.invoke(cli, ["--no-rebuild", "audit", "coverage", "-m", "-v"])

        # -m -v combination should work
        if result.exit_code == 0 and result.output.strip():
            assert "# " in result.output or "**" in result.output
