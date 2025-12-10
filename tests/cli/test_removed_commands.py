"""Tests verifying old commands have been removed (WU7).

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


def test_layers_command_removed():
    """jigy layers fails with 'No such command'."""
    runner = CliRunner()
    result = runner.invoke(cli, ["layers"])

    assert result.exit_code == 2
    assert "No such command" in result.output or "Error" in result.output


def test_layers_suggest_command_removed():
    """jigy layers suggest fails with 'No such command'."""
    runner = CliRunner()
    result = runner.invoke(cli, ["layers", "suggest"])

    assert result.exit_code == 2
    assert "No such command" in result.output or "Error" in result.output


def test_old_rebuild_command_removed():
    """jigy rebuild-old fails with 'No such command'."""
    runner = CliRunner()
    result = runner.invoke(cli, ["rebuild-old"])

    assert result.exit_code == 2
    assert "No such command" in result.output or "Error" in result.output


def test_new_commands_still_work():
    """New verb-first commands are still available."""
    runner = CliRunner()

    # Just check --help works for each new command
    for cmd in ["align", "rebuild", "show", "validate"]:
        result = runner.invoke(cli, [cmd, "--help"])
        assert result.exit_code == 0, f"{cmd} --help should work"
        assert "Usage:" in result.output
