# ABOUTME: Tests verifying old commands have been removed.
# ABOUTME: Ensures the clean break from old CLI structure is complete.
"""Tests verifying old commands have been removed.

These tests ensure the clean break from old CLI structure is complete.
No @jig decorators since we're testing removal, not behavior.
"""

from click.testing import CliRunner

from jig.cli.main import cli


def test_impl_command_removed():
    """jigy impl fails with 'No such command'."""
    runner = CliRunner()
    result = runner.invoke(cli, ["impl"])

    assert result.exit_code == 2
    assert "No such command" in result.output or "Error" in result.output


def test_impl_rebuild_command_removed():
    """jigy impl rebuild fails with 'No such command'."""
    runner = CliRunner()
    result = runner.invoke(cli, ["impl", "rebuild"])

    assert result.exit_code == 2
    assert "No such command" in result.output or "Error" in result.output


def test_intent_command_removed():
    """jigy intent fails with 'No such command'."""
    runner = CliRunner()
    result = runner.invoke(cli, ["intent"])

    assert result.exit_code == 2
    assert "No such command" in result.output or "Error" in result.output


def test_intent_rebuild_command_removed():
    """jigy intent rebuild fails with 'No such command'."""
    runner = CliRunner()
    result = runner.invoke(cli, ["intent", "rebuild"])

    assert result.exit_code == 2
    assert "No such command" in result.output or "Error" in result.output


def test_verify_command_removed():
    """jigy verify fails with 'No such command'."""
    runner = CliRunner()
    result = runner.invoke(cli, ["verify"])

    assert result.exit_code == 2
    assert "No such command" in result.output or "Error" in result.output


def test_verify_rebuild_command_removed():
    """jigy verify rebuild fails with 'No such command'."""
    runner = CliRunner()
    result = runner.invoke(cli, ["verify", "rebuild"])

    assert result.exit_code == 2
    assert "No such command" in result.output or "Error" in result.output


def test_old_rebuild_command_removed():
    """jigy rebuild-old fails with 'No such command'."""
    runner = CliRunner()
    result = runner.invoke(cli, ["rebuild-old"])

    assert result.exit_code == 2
    assert "No such command" in result.output or "Error" in result.output


def test_align_command_removed():
    """jigy align fails with 'No such command' (consolidated into context)."""
    runner = CliRunner()
    result = runner.invoke(cli, ["align"])

    assert result.exit_code == 2
    assert "No such command" in result.output or "Error" in result.output


def test_core_commands_still_work():
    """Core commands are still available."""
    runner = CliRunner()

    # Just check --help works for each core command
    for cmd in ["rebuild", "validate", "context", "mend"]:
        result = runner.invoke(cli, [cmd, "--help"])
        assert result.exit_code == 0, f"{cmd} --help should work"
        assert "Usage:" in result.output


def test_alias_commands_work():
    """Alias commands are available and show (alias) in help."""
    runner = CliRunner()

    aliases = ["graph", "list", "show", "bricks", "layers", "towers", "fix"]
    for alias in aliases:
        result = runner.invoke(cli, [alias, "--help"])
        assert result.exit_code == 0, f"{alias} --help should work"
        assert "alias" in result.output.lower(), f"{alias} should show (alias)"
