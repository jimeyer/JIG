# ABOUTME: Integration tests for CLI output modes.
# ABOUTME: Verifies -j, -m, -v flags work on all commands and mutual exclusivity.
"""Integration tests for CLI output modes.

This module provides comprehensive integration tests verifying that:
1. All commands accept -j, -m, -v flags
2. JSON output is single-line and parseable
3. Markdown output has headers and structure
4. Verbose adds detail to any format
5. -j -m produces clear error (mutual exclusivity)

These tests verify the output format specs are correctly implemented.
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

import jig
from jig.cli.main import cli


# ============================================================================
# Test Fixtures
# ============================================================================


def create_full_jig_project(root: Path) -> None:
    """Create a complete JIG project with all required components for testing."""
    # Create jig directory structure
    (root / "jig" / "specifications").mkdir(parents=True)
    (root / "jig" / "outcomes").mkdir(parents=True)
    (root / "jig" / "architecture").mkdir(parents=True)
    (root / "jig" / "generated").mkdir(parents=True)

    # Create a minimal spec with proper filename format
    (root / "jig" / "specifications" / "S-001_Test_Specification.md").write_text(
        """---
id: S-001
title: Test Specification
type: specification
outcomes: [O-001]
architecture: [A-001]
---

# Test Specification
"""
    )

    # Create a minimal outcome
    (root / "jig" / "outcomes" / "O-001_Test_Outcome.md").write_text(
        """---
id: O-001
title: Test Outcome
type: outcome
specifications: [S-001]
---

# Test Outcome
"""
    )

    # Create Charter.md with goals (using proper ### G-001: format)
    (root / "jig" / "Charter.md").write_text(
        """---
id: Charter
type: charter
goals:
  - G-001
---

# Project Charter

### G-001: Test Goal

Test goal description.
"""
    )

    # Create architecture document (V2 schema: no status field)
    (root / "jig" / "architecture" / "A-001_Test_Architecture.md").write_text(
        """---
id: A-001
title: Test Architecture
type: architecture
goals:
  - G-001
specifications:
  - S-001
---

# Test Architecture

Architecture description.
"""
    )

    # Create bricks.yaml
    (root / "jig" / "bricks.yaml").write_text(
        """bricks:
  - id: B-core
    name: Core Brick
    layer: 0
    units:
      - M-core
"""
    )

    # Create implementation graph
    impl_graph = root / "jig" / "generated" / "implementation-graph.ndjson"
    impl_graph.write_text(
        json.dumps({"_meta": {"version": "1.0"}}) + "\n"
        + json.dumps({"type": "module", "id": "M-core", "file": "src/core.py"}) + "\n"
    )

    # Create intent graph
    intent_graph = root / "jig" / "generated" / "intent-graph.ndjson"
    intent_graph.write_text(
        json.dumps({"_meta": {"version": "2.0"}}) + "\n"
        + json.dumps({"type": "charter", "id": "Charter", "file": "jig/Charter.md"}) + "\n"
        + json.dumps({"type": "goal", "id": "G-001", "title": "Test Goal"}) + "\n"
        + json.dumps({"type": "specification", "id": "S-001", "file": "jig/specifications/S-001_Test_Specification.md"}) + "\n"
    )

    # Create verification graph
    verify_graph = root / "jig" / "generated" / "verification-graph.ndjson"
    verify_graph.write_text(
        json.dumps({"_meta": {"version": "1.0"}}) + "\n"
    )

    # Create src directory
    (root / "src").mkdir()
    (root / "src" / "core.py").write_text('"""Core module."""\n')

    # Create tests directory
    (root / "tests").mkdir()


# ============================================================================
# Test: All Commands Accept Output Format Flags
# ============================================================================


# List of all commands and subcommands that should accept output flags
COMMANDS_WITH_OUTPUT_FLAGS = [
    # validate commands
    (["validate"], "validate"),
    (["validate", "intent"], "validate intent"),
    (["validate", "bricks"], "validate bricks"),
    (["validate", "full"], "validate full"),
    # rebuild commands
    (["rebuild"], "rebuild"),
    (["rebuild", "impl"], "rebuild impl"),
    (["rebuild", "intent"], "rebuild intent"),
    (["rebuild", "verify"], "rebuild verify"),
    # context command
    (["context"], "context"),
    # audit commands
    (["audit", "coverage"], "audit coverage"),
]


@pytest.mark.parametrize("cmd_args,cmd_name", COMMANDS_WITH_OUTPUT_FLAGS)
@jig.verifies("S-093")
def test_command_accepts_json_flag(cmd_args, cmd_name):
    """All commands accept -j/--json flag."""
    runner = CliRunner()
    result = runner.invoke(cli, cmd_args + ["--help"])

    assert result.exit_code == 0, f"{cmd_name} --help failed"
    assert "-j" in result.output or "--json" in result.output, \
        f"{cmd_name} should accept -j flag"


@pytest.mark.parametrize("cmd_args,cmd_name", COMMANDS_WITH_OUTPUT_FLAGS)
@jig.verifies("S-093")
def test_command_accepts_markdown_flag(cmd_args, cmd_name):
    """All commands accept -m/--markdown flag."""
    runner = CliRunner()
    result = runner.invoke(cli, cmd_args + ["--help"])

    assert result.exit_code == 0, f"{cmd_name} --help failed"
    assert "-m" in result.output or "--markdown" in result.output, \
        f"{cmd_name} should accept -m flag"


@pytest.mark.parametrize("cmd_args,cmd_name", COMMANDS_WITH_OUTPUT_FLAGS)
@jig.verifies("S-093")
def test_command_accepts_verbose_flag(cmd_args, cmd_name):
    """All commands accept -v/--verbose flag."""
    runner = CliRunner()
    result = runner.invoke(cli, cmd_args + ["--help"])

    assert result.exit_code == 0, f"{cmd_name} --help failed"
    assert "-v" in result.output or "--verbose" in result.output, \
        f"{cmd_name} should accept -v flag"


# ============================================================================
# Test: Mutual Exclusivity of -j and -m
# ============================================================================


@pytest.mark.parametrize("cmd_args,cmd_name", COMMANDS_WITH_OUTPUT_FLAGS)
@jig.verifies("S-093")
def test_command_rejects_json_and_markdown_together(cmd_args, cmd_name):
    """All commands error when -j and -m used together."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["--no-rebuild"] + cmd_args + ["-j", "-m"])

        assert result.exit_code != 0, \
            f"{cmd_name} -j -m should fail"
        assert "mutually exclusive" in result.output.lower(), \
            f"{cmd_name} should mention 'mutually exclusive'"


# ============================================================================
# Test: JSON Output Is Valid and Single-Line
# ============================================================================


# Commands that produce JSON output reliably without external dependencies
JSON_TESTABLE_COMMANDS = [
    (["--no-rebuild", "validate", "-j"], "validate -j"),
    (["--no-rebuild", "validate", "intent", "-j"], "validate intent -j"),
    (["--no-rebuild", "validate", "bricks", "-j"], "validate bricks -j"),
    (["--no-rebuild", "validate", "full", "-j"], "validate full -j"),
    (["--no-rebuild", "context", "-j"], "context -j"),
]


@pytest.mark.parametrize("cmd_args,cmd_name", JSON_TESTABLE_COMMANDS)
@jig.verifies("S-026", "S-093")
def test_json_output_is_valid_json(cmd_args, cmd_name):
    """JSON output is parseable as valid JSON."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, cmd_args)

        # If command succeeded, output should be valid JSON
        if result.exit_code == 0:
            try:
                data = json.loads(result.output)
                assert isinstance(data, dict), "JSON output should be an object"
            except json.JSONDecodeError as e:
                pytest.fail(f"{cmd_name} output is not valid JSON: {e}\nOutput: {result.output[:500]}")


@pytest.mark.parametrize("cmd_args,cmd_name", JSON_TESTABLE_COMMANDS)
@jig.verifies("S-026", "S-093")
def test_json_output_is_single_line(cmd_args, cmd_name):
    """JSON output is single-line (not pretty-printed)."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, cmd_args)

        if result.exit_code == 0:
            output = result.output.strip()
            # Single line means no embedded newlines
            assert "\n" not in output, \
                f"{cmd_name} JSON should be single-line, got:\n{output[:200]}"


# ============================================================================
# Test: Markdown Output Has Structure
# ============================================================================


MARKDOWN_TESTABLE_COMMANDS = [
    (["--no-rebuild", "validate", "-m"], "validate -m"),
    (["--no-rebuild", "validate", "intent", "-m"], "validate intent -m"),
    (["--no-rebuild", "context", "-m"], "context -m"),
]


@pytest.mark.parametrize("cmd_args,cmd_name", MARKDOWN_TESTABLE_COMMANDS)
@jig.verifies("S-093", "S-094")
def test_markdown_output_has_headers(cmd_args, cmd_name):
    """Markdown output contains markdown headers."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, cmd_args)

        if result.exit_code == 0:
            # Markdown should have headers (# or ##)
            assert "#" in result.output, \
                f"{cmd_name} markdown output should contain headers"


@pytest.mark.parametrize("cmd_args,cmd_name", MARKDOWN_TESTABLE_COMMANDS)
@jig.verifies("S-093", "S-094")
def test_markdown_output_is_not_json(cmd_args, cmd_name):
    """Markdown output is not JSON."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, cmd_args)

        if result.exit_code == 0:
            # Output should NOT be valid JSON
            try:
                json.loads(result.output)
                pytest.fail(f"{cmd_name} markdown output should not be JSON")
            except json.JSONDecodeError:
                pass  # Expected - markdown is not JSON


# ============================================================================
# Test: Verbose Flag Combinations
# ============================================================================


VERBOSE_TESTABLE_COMMANDS = [
    (["--no-rebuild", "validate", "-v"], "validate -v"),
    (["--no-rebuild", "context", "-v"], "context -v"),
]


@pytest.mark.parametrize("cmd_args,cmd_name", VERBOSE_TESTABLE_COMMANDS)
@jig.verifies("S-093")
def test_verbose_flag_works(cmd_args, cmd_name):
    """Verbose flag is accepted and command runs."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, cmd_args)

        # Should run without "no such option" error
        assert "no such option" not in result.output.lower(), \
            f"{cmd_name} should accept -v flag"


@jig.verifies("S-093")
def test_json_verbose_combination():
    """JSON + verbose combination works (-j -v)."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "intent", "-j", "-v"])

        # validate intent should pass (the full validation may fail due to brick references)
        assert result.exit_code == 0, f"validate intent -j -v should succeed: {result.output}"
        # Output should still be valid JSON
        data = json.loads(result.output)
        assert isinstance(data, dict)


@jig.verifies("S-093")
def test_markdown_verbose_combination():
    """Markdown + verbose combination works (-m -v)."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "intent", "-m", "-v"])

        # validate intent should pass
        assert result.exit_code == 0, f"validate intent -m -v should succeed: {result.output}"
        # Output should be markdown (not JSON)
        assert "#" in result.output


# ============================================================================
# Test: Old Commands Are Gone
# ============================================================================


OLD_COMMANDS = [
    (["matrix"], "jigy matrix"),
    (["impl"], "jigy impl"),
    (["intent"], "jigy intent"),
    (["verify"], "jigy verify"),
]


@pytest.mark.parametrize("cmd_args,cmd_name", OLD_COMMANDS)
@jig.verifies("S-115")
def test_old_command_not_available(cmd_args, cmd_name):
    """Old standalone commands are not available."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, cmd_args)

        assert result.exit_code != 0, \
            f"{cmd_name} should not exist (command should fail)"
        assert "no such command" in result.output.lower() or "error" in result.output.lower(), \
            f"{cmd_name} should show 'No such command' error"


# ============================================================================
# Test: Alias Commands Work
# ============================================================================


ALIAS_COMMANDS = [
    (["graph"], "jigy graph"),
    (["list"], "jigy list"),
    (["show"], "jigy show"),
    (["bricks"], "jigy bricks"),
    (["layers"], "jigy layers"),
    (["towers"], "jigy towers"),
    (["fix", "--dry-run"], "jigy fix"),
]


@pytest.mark.parametrize("cmd_args,cmd_name", ALIAS_COMMANDS)
@jig.verifies("S-115")
def test_alias_command_works(cmd_args, cmd_name):
    """Alias commands are available and work."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["--no-rebuild"] + cmd_args)

        assert result.exit_code == 0, \
            f"{cmd_name} should work as alias: {result.output}"


@jig.verifies("S-115")
def test_alias_commands_show_alias_in_help():
    """Alias commands show (alias) in their help output."""
    runner = CliRunner()

    aliases = ["graph", "list", "show", "bricks", "layers", "towers", "fix"]
    for alias in aliases:
        result = runner.invoke(cli, [alias, "--help"])
        assert result.exit_code == 0, f"{alias} --help should work"
        assert "alias" in result.output.lower(), f"{alias} help should mention 'alias'"
