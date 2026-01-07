"""Integration tests for CLI output modes (WU8 Validation).

This module provides comprehensive integration tests verifying that:
1. All commands accept -j, -m, -v flags
2. JSON output is single-line and parseable
3. Markdown output has headers and structure
4. Verbose adds detail to any format
5. -j -m produces clear error (mutual exclusivity)
6. Old standalone commands no longer exist

These tests verify the SCOPE problem is solved at the system boundary.
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
specifies: [S-001]
---

# Test Outcome
"""
    )

    # Create Charter.md with goals (using proper ### G-001: format)
    (root / "jig" / "Charter.md").write_text(
        """---
id: Charter
type: charter
defines_goals:
  - G-001
---

# Project Charter

### G-001: Test Goal

Test goal description.
"""
    )

    # Create architecture document (using valid status: active)
    (root / "jig" / "architecture" / "A-001_Test_Architecture.md").write_text(
        """---
id: A-001
title: Test Architecture
type: architecture
status: active
supports_goals:
  - G-001
---

# Test Architecture

Architecture description.
"""
    )

    # Create bricks.yaml with multiple towers
    (root / "jig" / "bricks.yaml").write_text(
        """bricks:
  - id: B-backend
    name: Backend Brick
    layer: 0
    tower: backend
    units:
      - M-backend

  - id: B-frontend
    name: Frontend Brick
    layer: 0
    tower: frontend
    units:
      - M-frontend

  - id: B-core
    name: Core Brick
    layer: 1
    units:
      - M-core
"""
    )

    # Create implementation graph
    impl_graph = root / "jig" / "generated" / "implementation-graph.ndjson"
    impl_graph.write_text(
        json.dumps({"_meta": {"version": "1.0"}}) + "\n"
        + json.dumps({"type": "module", "id": "M-backend", "file": "src/backend.py"}) + "\n"
        + json.dumps({"type": "module", "id": "M-frontend", "file": "src/frontend.py"}) + "\n"
        + json.dumps({"type": "module", "id": "M-core", "file": "src/core.py"}) + "\n"
        + json.dumps({"type": "function", "id": "F-backend.func", "file": "src/backend.py", "line": 5}) + "\n"
    )

    # Create intent graph
    intent_graph = root / "jig" / "generated" / "intent-graph.ndjson"
    intent_graph.write_text(
        json.dumps({"_meta": {"version": "1.0"}}) + "\n"
        + json.dumps({"type": "specification", "id": "S-001", "file": "jig/specifications/S-001_Test_Specification.md"}) + "\n"
    )

    # Create verification graph
    verify_graph = root / "jig" / "generated" / "verification-graph.ndjson"
    verify_graph.write_text(
        json.dumps({"_meta": {"version": "1.0"}}) + "\n"
        + json.dumps({"type": "test", "id": "T-test.test_func", "file": "tests/test_example.py", "line": 5}) + "\n"
    )

    # Create src directory
    (root / "src").mkdir()
    (root / "src" / "backend.py").write_text(
        '''"""Backend module."""

import jig


@jig.implements("S-001")
def backend_func():
    """Backend function."""
    pass
'''
    )
    (root / "src" / "frontend.py").write_text('"""Frontend module."""\n')
    (root / "src" / "core.py").write_text('"""Core module."""\n')

    # Create tests directory
    (root / "tests").mkdir()
    (root / "tests" / "test_example.py").write_text(
        '''"""Example tests."""

import jig


@jig.verifies("S-001")
def test_example():
    """Example test."""
    pass
'''
    )


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
    # align command
    (["align"], "align"),
    # show commands
    (["show"], "show"),
    (["show", "layers"], "show layers"),
    (["show", "bricks"], "show bricks"),
    (["show", "charter"], "show charter"),
    (["show", "goals"], "show goals"),
    (["show", "architecture"], "show architecture"),
    (["show", "towers"], "show towers"),
    (["show", "matrix"], "show matrix"),
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
    (["--no-rebuild", "show", "-j"], "show -j"),
    (["--no-rebuild", "show", "layers", "-j"], "show layers -j"),
    (["--no-rebuild", "show", "bricks", "-j"], "show bricks -j"),
    (["--no-rebuild", "show", "towers", "-j"], "show towers -j"),
    (["--no-rebuild", "show", "matrix", "-j"], "show matrix -j"),
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
    (["--no-rebuild", "show", "-m"], "show -m"),
    (["--no-rebuild", "show", "layers", "-m"], "show layers -m"),
    (["--no-rebuild", "show", "bricks", "-m"], "show bricks -m"),
    (["--no-rebuild", "show", "towers", "-m"], "show towers -m"),
    (["--no-rebuild", "show", "matrix", "-m"], "show matrix -m"),
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
    (["--no-rebuild", "show", "-v"], "show -v"),
    (["--no-rebuild", "show", "layers", "-v"], "show layers -v"),
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
    (["towers"], "jigy towers"),
    (["matrix"], "jigy matrix"),
    (["layers"], "jigy layers"),
    (["impl"], "jigy impl"),
    (["intent"], "jigy intent"),
    (["verify"], "jigy verify"),
]


@pytest.mark.parametrize("cmd_args,cmd_name", OLD_COMMANDS)
@jig.verifies("S-060", "S-090", "S-091")
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
# Test: New Commands Work Under Show Group
# ============================================================================


@jig.verifies("S-060", "S-090")
def test_show_towers_works():
    """jigy show towers works as replacement for jigy towers."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["show", "towers"])

        assert result.exit_code == 0, "show towers should succeed"
        # Should show tower info
        assert "backend" in result.output.lower() or "frontend" in result.output.lower() or "tower" in result.output.lower()


@jig.verifies("S-060", "S-091")
def test_show_matrix_works():
    """jigy show matrix works as replacement for jigy matrix."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["show", "matrix"])

        assert result.exit_code == 0, "show matrix should succeed"


@jig.verifies("S-060", "S-090")
def test_show_towers_specific_tower():
    """jigy show towers <id> shows specific tower."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["show", "towers", "backend"])

        assert result.exit_code == 0, "show towers backend should succeed"
        assert "backend" in result.output.lower()


# ============================================================================
# Test: Complete Command Matrix
# ============================================================================


# All commands x all flags matrix
COMPLETE_COMMAND_FLAG_MATRIX = []
for cmd_args, cmd_name in COMMANDS_WITH_OUTPUT_FLAGS:
    for flags, flag_name in [
        ([], "no flags"),
        (["-j"], "-j"),
        (["-m"], "-m"),
        (["-v"], "-v"),
        (["-j", "-v"], "-j -v"),
        (["-m", "-v"], "-m -v"),
    ]:
        COMPLETE_COMMAND_FLAG_MATRIX.append(
            (cmd_args, cmd_name, flags, flag_name)
        )


@pytest.mark.parametrize("cmd_args,cmd_name,flags,flag_name", COMPLETE_COMMAND_FLAG_MATRIX)
@jig.verifies("S-093")
def test_command_flag_combination_accepted(cmd_args, cmd_name, flags, flag_name):
    """All command x flag combinations are accepted (no 'no such option' error)."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["--no-rebuild"] + cmd_args + flags)

        # Should not have "no such option" error
        assert "no such option" not in result.output.lower(), \
            f"{cmd_name} {flag_name} should be accepted"


# ============================================================================
# Test: Rebuild Commands (require actual rebuild)
# ============================================================================


@jig.verifies("S-093")
def test_rebuild_json_output():
    """jigy rebuild -j produces valid JSON with graph info."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "-j"])

        assert result.exit_code == 0, f"rebuild -j failed: {result.output}"
        data = json.loads(result.output)
        assert data["status"] == "success"
        assert "graphs" in data
        assert "duration_ms" in data


@jig.verifies("S-093")
def test_rebuild_markdown_output():
    """jigy rebuild -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["rebuild", "-m"])

        assert result.exit_code == 0, f"rebuild -m failed: {result.output}"
        assert "#" in result.output or "**" in result.output


@jig.verifies("S-093")
def test_align_json_output():
    """jigy align -j produces combined JSON output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["align", "-j"])

        assert result.exit_code == 0, f"align -j failed: {result.output}"
        data = json.loads(result.output)
        # Should have status and sections
        assert "status" in data


@jig.verifies("S-093")
def test_align_markdown_output():
    """jigy align -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem() as tmpdir:
        root = Path(tmpdir)
        create_full_jig_project(root)

        result = runner.invoke(cli, ["align", "-m"])

        assert result.exit_code == 0, f"align -m failed: {result.output}"
        assert "#" in result.output or "**" in result.output
