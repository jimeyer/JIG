"""Tests for root CLI command (WU6).

These tests verify S-061: Minimal Global Options.
"""

import jig
from click.testing import CliRunner

from jig.cli.main import cli


@jig.verifies("S-061")
def test_bare_command_shows_help_exits_zero():
    """jigy (bare) shows help and exits 0."""
    runner = CliRunner()
    result = runner.invoke(cli, [])

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Commands:" in result.output


@jig.verifies("S-061")
def test_version_option_works():
    """jigy --version shows version and exits 0."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "version" in result.output.lower()


@jig.verifies("S-061")
def test_help_option_works():
    """jigy --help shows help and exits 0."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "--help" in result.output
    assert "--version" in result.output


@jig.verifies("S-061")
def test_unknown_option_fails():
    """Unknown flag produces error with exit code 2."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--unknown-flag"])

    assert result.exit_code == 2
    assert "No such option" in result.output or "Error" in result.output


@jig.verifies("S-061")
def test_help_shows_expected_commands():
    """Help displays the expected command groups."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    # New verb-first commands (S-058, S-059, S-060)
    assert "align" in result.output
    assert "rebuild" in result.output
    assert "validate" in result.output
    assert "show" in result.output


@jig.verifies("S-061")
def test_only_help_and_version_global_options():
    """Only --help and --version appear as global options."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    # These should NOT appear
    assert "--project-root" not in result.output
    assert "--verbose" not in result.output
    assert "--format" not in result.output
    # These SHOULD appear
    assert "--help" in result.output
    assert "--version" in result.output


@jig.verifies("S-061")
def test_cli_docstring_is_concise():
    """CLI docstring matches A002 spec."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    # Verify the new concise docstring is shown
    assert "Keep specs, code, and tests aligned" in result.output
