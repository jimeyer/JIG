"""Tests for output format infrastructure (S-093).

These tests verify the universal output format flags:
- OutputFormat enum with HUMAN, JSON, MARKDOWN values
- add_output_options decorator adds -j/-m/-v flags
- resolve_format() validates mutual exclusivity and returns correct format
"""

import click
import pytest
from click.testing import CliRunner

import jig


@jig.verifies("S-093")
def test_output_format_enum_has_required_values():
    """OutputFormat enum has HUMAN, JSON, MARKDOWN values."""
    from jig.cli.output import OutputFormat

    assert hasattr(OutputFormat, "HUMAN")
    assert hasattr(OutputFormat, "JSON")
    assert hasattr(OutputFormat, "MARKDOWN")


@jig.verifies("S-093")
def test_output_format_enum_values_are_distinct():
    """OutputFormat enum values are distinct from each other."""
    from jig.cli.output import OutputFormat

    assert OutputFormat.HUMAN != OutputFormat.JSON
    assert OutputFormat.HUMAN != OutputFormat.MARKDOWN
    assert OutputFormat.JSON != OutputFormat.MARKDOWN


@jig.verifies("S-093")
def test_add_output_options_adds_json_flag():
    """@add_output_options adds -j/--json flag to commands."""
    from jig.cli.output import add_output_options

    @click.command()
    @add_output_options
    def test_cmd(json, markdown, verbose):
        click.echo(f"json={json}")

    runner = CliRunner()

    # Test short flag
    result = runner.invoke(test_cmd, ["-j"])
    assert result.exit_code == 0
    assert "json=True" in result.output

    # Test long flag
    result = runner.invoke(test_cmd, ["--json"])
    assert result.exit_code == 0
    assert "json=True" in result.output


@jig.verifies("S-093")
def test_add_output_options_adds_markdown_flag():
    """@add_output_options adds -m/--markdown flag to commands."""
    from jig.cli.output import add_output_options

    @click.command()
    @add_output_options
    def test_cmd(json, markdown, verbose):
        click.echo(f"markdown={markdown}")

    runner = CliRunner()

    # Test short flag
    result = runner.invoke(test_cmd, ["-m"])
    assert result.exit_code == 0
    assert "markdown=True" in result.output

    # Test long flag
    result = runner.invoke(test_cmd, ["--markdown"])
    assert result.exit_code == 0
    assert "markdown=True" in result.output


@jig.verifies("S-093")
def test_add_output_options_adds_verbose_flag():
    """@add_output_options adds -v/--verbose flag to commands."""
    from jig.cli.output import add_output_options

    @click.command()
    @add_output_options
    def test_cmd(json, markdown, verbose):
        click.echo(f"verbose={verbose}")

    runner = CliRunner()

    # Test short flag
    result = runner.invoke(test_cmd, ["-v"])
    assert result.exit_code == 0
    assert "verbose=True" in result.output

    # Test long flag
    result = runner.invoke(test_cmd, ["--verbose"])
    assert result.exit_code == 0
    assert "verbose=True" in result.output


@jig.verifies("S-093")
def test_add_output_options_defaults_all_false():
    """Without flags, all options default to False."""
    from jig.cli.output import add_output_options

    @click.command()
    @add_output_options
    def test_cmd(json, markdown, verbose):
        click.echo(f"json={json} markdown={markdown} verbose={verbose}")

    runner = CliRunner()
    result = runner.invoke(test_cmd, [])
    assert result.exit_code == 0
    assert "json=False" in result.output
    assert "markdown=False" in result.output
    assert "verbose=False" in result.output


@jig.verifies("S-093")
def test_resolve_format_default_returns_human():
    """resolve_format() returns HUMAN when no flags set."""
    from jig.cli.output import OutputFormat, resolve_format

    result = resolve_format(json=False, markdown=False)
    assert result == OutputFormat.HUMAN


@jig.verifies("S-093")
def test_resolve_format_json_flag_returns_json():
    """resolve_format() returns JSON when json=True."""
    from jig.cli.output import OutputFormat, resolve_format

    result = resolve_format(json=True, markdown=False)
    assert result == OutputFormat.JSON


@jig.verifies("S-093")
def test_resolve_format_markdown_flag_returns_markdown():
    """resolve_format() returns MARKDOWN when markdown=True."""
    from jig.cli.output import OutputFormat, resolve_format

    result = resolve_format(json=False, markdown=True)
    assert result == OutputFormat.MARKDOWN


@jig.verifies("S-093")
def test_resolve_format_mutual_exclusivity_error():
    """resolve_format() raises error when both json and markdown are True."""
    from jig.cli.output import resolve_format

    with pytest.raises(click.UsageError) as exc_info:
        resolve_format(json=True, markdown=True)

    # Error message should be clear about mutual exclusivity
    assert "mutually exclusive" in str(exc_info.value).lower() or \
           "-j" in str(exc_info.value) or \
           "--json" in str(exc_info.value)


@jig.verifies("S-093")
def test_verbose_can_combine_with_json():
    """Verbose flag can be combined with JSON format (-j -v)."""
    from jig.cli.output import add_output_options

    @click.command()
    @add_output_options
    def test_cmd(json, markdown, verbose):
        click.echo(f"json={json} verbose={verbose}")

    runner = CliRunner()
    result = runner.invoke(test_cmd, ["-j", "-v"])
    assert result.exit_code == 0
    assert "json=True" in result.output
    assert "verbose=True" in result.output


@jig.verifies("S-093")
def test_verbose_can_combine_with_markdown():
    """Verbose flag can be combined with markdown format (-m -v)."""
    from jig.cli.output import add_output_options

    @click.command()
    @add_output_options
    def test_cmd(json, markdown, verbose):
        click.echo(f"markdown={markdown} verbose={verbose}")

    runner = CliRunner()
    result = runner.invoke(test_cmd, ["-m", "-v"])
    assert result.exit_code == 0
    assert "markdown=True" in result.output
    assert "verbose=True" in result.output


@jig.verifies("S-093")
def test_verbose_alone_is_valid():
    """Verbose flag alone is valid (-v without -j or -m)."""
    from jig.cli.output import add_output_options

    @click.command()
    @add_output_options
    def test_cmd(json, markdown, verbose):
        click.echo(f"verbose={verbose}")

    runner = CliRunner()
    result = runner.invoke(test_cmd, ["-v"])
    assert result.exit_code == 0
    assert "verbose=True" in result.output


@jig.verifies("S-093")
def test_flags_appear_in_help():
    """All output flags appear in command help with descriptions."""
    from jig.cli.output import add_output_options

    @click.command()
    @add_output_options
    def test_cmd(json, markdown, verbose):
        pass

    runner = CliRunner()
    result = runner.invoke(test_cmd, ["--help"])
    assert result.exit_code == 0

    # All flags should appear in help
    assert "-j" in result.output or "--json" in result.output
    assert "-m" in result.output or "--markdown" in result.output
    assert "-v" in result.output or "--verbose" in result.output


@jig.verifies("S-093")
def test_decorator_preserves_command_function():
    """@add_output_options preserves the original command function."""
    from jig.cli.output import add_output_options

    @click.command()
    @add_output_options
    def my_test_command(json, markdown, verbose):
        """My custom help text."""
        click.echo("executed")

    runner = CliRunner()

    # Check help shows original docstring
    result = runner.invoke(my_test_command, ["--help"])
    assert "My custom help text" in result.output

    # Check command executes
    result = runner.invoke(my_test_command, [])
    assert "executed" in result.output
