"""Tests for verify CLI commands.

TDD tests for S-056: CLI Verify Rebuild Command.
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

import jig
from jig.cli.main import cli


@jig.verifies("S-056")
def test_cli_verify_rebuild_creates_file(tmp_path: Path) -> None:
    """jigy verify rebuild creates verification-graph.ndjson."""
    # Create test file structure
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    (test_dir / "test_example.py").write_text("""\
def test_simple():
    assert True
""")

    # Create jig directory structure
    (tmp_path / "jig" / "generated").mkdir(parents=True)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["verify", "rebuild", "--project-root", str(tmp_path), "--no-timestamp"],
    )

    assert result.exit_code == 0, f"Failed: {result.output}"
    output_path = tmp_path / "jig" / "generated" / "verification-graph.ndjson"
    assert output_path.exists()


@jig.verifies("S-056")
def test_cli_verify_rebuild_custom_test_dir(tmp_path: Path) -> None:
    """jigy verify rebuild --test-dir works."""
    # Create custom test directory
    custom_tests = tmp_path / "custom_tests"
    custom_tests.mkdir()
    (custom_tests / "test_custom.py").write_text("""\
def test_in_custom():
    assert True
""")

    # Create jig directory
    (tmp_path / "jig" / "generated").mkdir(parents=True)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "verify",
            "rebuild",
            "--project-root",
            str(tmp_path),
            "--test-dir",
            str(custom_tests),
            "--no-timestamp",
        ],
    )

    assert result.exit_code == 0, f"Failed: {result.output}"
    # Verify the test was found
    output_path = tmp_path / "jig" / "generated" / "verification-graph.ndjson"
    content = output_path.read_text()
    assert "T-test_custom.test_in_custom" in content


@jig.verifies("S-056")
def test_cli_verify_rebuild_no_timestamp(tmp_path: Path) -> None:
    """jigy verify rebuild --no-timestamp produces deterministic output."""
    # Create test file
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    (test_dir / "test_example.py").write_text("""\
def test_simple():
    assert True
""")

    # Create jig directory
    (tmp_path / "jig" / "generated").mkdir(parents=True)

    runner = CliRunner()

    # Run twice with --no-timestamp
    result1 = runner.invoke(
        cli,
        ["verify", "rebuild", "--project-root", str(tmp_path), "--no-timestamp"],
    )
    output_path = tmp_path / "jig" / "generated" / "verification-graph.ndjson"
    content1 = output_path.read_text()

    result2 = runner.invoke(
        cli,
        ["verify", "rebuild", "--project-root", str(tmp_path), "--no-timestamp"],
    )
    content2 = output_path.read_text()

    assert result1.exit_code == 0
    assert result2.exit_code == 0
    assert content1 == content2

    # Verify no timestamp in metadata
    first_line = content1.split("\n")[0]
    metadata = json.loads(first_line)
    assert "generated" not in metadata["_meta"]


@jig.verifies("S-056")
def test_cli_verify_rebuild_shows_progress(tmp_path: Path) -> None:
    """jigy verify rebuild prints progress output."""
    # Create test files with verifies
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    (test_dir / "test_example.py").write_text("""\
import jig

@jig.verifies("S-001")
def test_one():
    assert True

def test_two():
    assert True
""")

    # Create jig directory
    (tmp_path / "jig" / "generated").mkdir(parents=True)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["verify", "rebuild", "--project-root", str(tmp_path), "--no-timestamp"],
    )

    assert result.exit_code == 0
    # Should show progress messages
    assert "Discovering" in result.output or "test" in result.output.lower()
    assert "verification" in result.output.lower() or "graph" in result.output.lower()


@jig.verifies("S-056")
def test_cli_verify_rebuild_returns_zero_on_success(tmp_path: Path) -> None:
    """jigy verify rebuild returns exit code 0 on success."""
    # Create test file
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    (test_dir / "test_example.py").write_text("""\
def test_simple():
    assert True
""")

    # Create jig directory
    (tmp_path / "jig" / "generated").mkdir(parents=True)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["verify", "rebuild", "--project-root", str(tmp_path), "--no-timestamp"],
    )

    assert result.exit_code == 0


@jig.verifies("S-056")
def test_cli_verify_rebuild_help() -> None:
    """jigy verify rebuild --help shows options."""
    runner = CliRunner()
    result = runner.invoke(cli, ["verify", "rebuild", "--help"])

    assert result.exit_code == 0
    assert "--test-dir" in result.output
    assert "--no-timestamp" in result.output


@jig.verifies("S-056")
def test_cli_verify_rebuild_empty_tests(tmp_path: Path) -> None:
    """jigy verify rebuild handles empty test directory."""
    # Create empty test directory
    test_dir = tmp_path / "tests"
    test_dir.mkdir()

    # Create jig directory
    (tmp_path / "jig" / "generated").mkdir(parents=True)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["verify", "rebuild", "--project-root", str(tmp_path), "--no-timestamp"],
    )

    assert result.exit_code == 0
    output_path = tmp_path / "jig" / "generated" / "verification-graph.ndjson"
    assert output_path.exists()

    # Check metadata shows 0 nodes
    first_line = output_path.read_text().split("\n")[0]
    metadata = json.loads(first_line)
    assert metadata["_meta"]["node_count"] == 0


@jig.verifies("S-056")
def test_cli_verify_group_exists() -> None:
    """verify subcommand group is registered."""
    runner = CliRunner()
    result = runner.invoke(cli, ["verify", "--help"])

    assert result.exit_code == 0
    assert "rebuild" in result.output
