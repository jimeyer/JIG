"""Output format infrastructure for JIG CLI (S-093).

Provides universal output format flags for all CLI commands:
- OutputFormat enum: HUMAN, JSON, MARKDOWN
- add_output_options decorator: adds -j/-m/-v flags to commands
- resolve_format(): validates flags and returns appropriate format
"""

from enum import Enum
from functools import wraps
from typing import Callable, TypeVar

import click

import jig

F = TypeVar("F", bound=Callable)


@jig.implements("S-093")
class OutputFormat(Enum):
    """Output format for CLI commands.

    Values:
        HUMAN: Human-readable terminal output (default)
        JSON: Machine-parseable JSON output
        MARKDOWN: LLM-optimized markdown output
    """

    HUMAN = "human"
    JSON = "json"
    MARKDOWN = "markdown"


@jig.implements("S-093")
def add_output_options(func: F) -> F:
    """Decorator that adds universal output format options to a Click command.

    Adds the following flags:
        -j/--json: Machine-parseable JSON output
        -m/--markdown: LLM-optimized markdown output
        -v/--verbose: Additional detail in any format

    Usage:
        @click.command()
        @add_output_options
        def my_command(json, markdown, verbose):
            format = resolve_format(json, markdown)
            ...

    Args:
        func: The Click command function to decorate

    Returns:
        Decorated function with output options added
    """

    @click.option(
        "-j",
        "--json",
        is_flag=True,
        default=False,
        help="Machine-parseable JSON output.",
    )
    @click.option(
        "-m",
        "--markdown",
        is_flag=True,
        default=False,
        help="LLM-optimized markdown output.",
    )
    @click.option(
        "-v",
        "--verbose",
        is_flag=True,
        default=False,
        help="Additional detail in any format.",
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


@jig.implements("S-093")
def resolve_format(json: bool, markdown: bool) -> OutputFormat:
    """Resolve output format from CLI flags.

    Validates that -j and -m are mutually exclusive and returns
    the appropriate OutputFormat.

    Args:
        json: True if -j/--json flag was passed
        markdown: True if -m/--markdown flag was passed

    Returns:
        OutputFormat enum value based on flags

    Raises:
        click.UsageError: If both json and markdown are True (mutually exclusive)
    """
    if json and markdown:
        raise click.UsageError(
            "Options -j/--json and -m/--markdown are mutually exclusive. "
            "Choose one output format."
        )

    if json:
        return OutputFormat.JSON
    if markdown:
        return OutputFormat.MARKDOWN
    return OutputFormat.HUMAN


__all__ = ["OutputFormat", "add_output_options", "resolve_format"]
