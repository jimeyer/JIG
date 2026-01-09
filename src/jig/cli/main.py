"""Main CLI entry point for JIG."""

import sys
from pathlib import Path
from typing import Optional

import click

import jig
from jig.config import ConfigError, JigConfig, load_config


class OrderedGroup(click.Group):
    """A Click group with explicit command ordering."""

    COMMAND_ORDER = ["align", "validate", "show", "audit", "rebuild"]

    def list_commands(self, ctx):
        # Return commands in explicit order, then any others
        ordered = [c for c in self.COMMAND_ORDER if c in self.commands]
        others = [c for c in self.commands if c not in self.COMMAND_ORDER]
        return ordered + others


from jig.cli.discovery import ProjectNotFoundError, find_project_root


def get_config(ctx: click.Context) -> JigConfig:
    """Get JigConfig from Click context, loading if needed."""
    if "config" not in ctx.obj:
        try:
            project_root = find_project_root()
        except ProjectNotFoundError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        ctx.obj["config"] = load_config(project_root)
    return ctx.obj["config"]


@jig.implements("S-071")
def get_no_rebuild(ctx: click.Context) -> bool:
    """Get --no-rebuild flag from Click context.

    Args:
        ctx: Click context.

    Returns:
        True if --no-rebuild was passed, False otherwise.
    """
    return ctx.obj.get("no_rebuild", False)


from jig.cli.audit import coverage_command
from jig.cli.output import add_output_options, resolve_format
from jig.cli.rebuild import (
    align_command,
    rebuild_all_command,
    rebuild_impl_command,
    rebuild_intent_command,
    rebuild_verify_command,
)
from jig.cli.show import (
    show_architecture_command,
    show_bricks_command,
    show_charter_command,
    show_goals_command,
    show_layers_command,
    show_matrix_command,
    show_overview_command,
    show_towers_command,
)
from jig.cli.validate import (
    validate_bricks_command,
    validate_full_command,
    validate_intent_command,
)


@click.group(cls=OrderedGroup, invoke_without_command=True)
@click.version_option()
@click.option(
    "--no-rebuild",
    is_flag=True,
    default=False,
    help="Skip automatic graph rebuild before commands.",
)
@click.pass_context
@jig.implements("S-061", "S-065", "S-071")
def cli(ctx, no_rebuild: bool):
    """JIG — Keep specs, code, and tests aligned."""
    ctx.ensure_object(dict)
    ctx.obj["no_rebuild"] = no_rebuild
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Verb-first rebuild command group (S-058)
@cli.group(name="rebuild", invoke_without_command=True)
@add_output_options
@click.pass_context
@jig.implements("S-058", "S-065", "S-093")
def rebuild_group(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Manual Rebuild of JIG graphs.

    Rebuilds implementation, verification, and/or intent graphs.

    Rebuild runs automatically before align and validate commands.

    Example:
        jigy rebuild           # Rebuild all graphs
        jigy rebuild impl      # Rebuild implementation graph only
        jigy rebuild intent    # Rebuild intent graph only
        jigy rebuild verify    # Rebuild verification graph only
        jigy rebuild -j        # JSON output
        jigy rebuild -m        # Markdown output
    """
    if ctx.invoked_subcommand is None:
        # No subcommand = rebuild all
        output_format = resolve_format(json, markdown)
        config = get_config(ctx)
        exit_code = rebuild_all_command(config, output_format, verbose)
        sys.exit(exit_code)


@rebuild_group.command(name="impl")
@add_output_options
@click.pass_context
@jig.implements("S-058", "S-065", "S-093")
def rebuild_impl_cli(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Rebuild implementation graph."""
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    exit_code = rebuild_impl_command(config, output_format, verbose)
    sys.exit(exit_code)


@rebuild_group.command(name="intent")
@add_output_options
@click.pass_context
@jig.implements("S-058", "S-065", "S-093")
def rebuild_intent_cli(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Rebuild intent graph."""
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    exit_code = rebuild_intent_command(config, output_format, verbose)
    sys.exit(exit_code)


@rebuild_group.command(name="verify")
@add_output_options
@click.pass_context
@jig.implements("S-058", "S-065", "S-093")
def rebuild_verify_cli(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Rebuild verification graph."""
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    exit_code = rebuild_verify_command(config, output_format, verbose)
    sys.exit(exit_code)


@cli.command()
@add_output_options
@click.pass_context
@jig.implements("S-059", "S-065", "S-093")
def align(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Run full alignment workflow.

    Rebuilds all graphs, validates artifacts, and displays summary.
    This is the "do everything" command for keeping JIG in sync.

    Example:
        jigy align
        jigy align -j    # JSON output
        jigy align -m    # Markdown output
    """
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    exit_code = align_command(config, output_format, verbose)
    sys.exit(exit_code)


@cli.group(invoke_without_command=True)
@add_output_options
@click.pass_context
@jig.implements("S-026", "S-061", "S-065", "S-071", "S-093")
def validate(ctx, json: bool, markdown: bool, verbose: bool):
    """Validate JIG artifacts.

    Validates specifications, outcomes, decorators, and bricks.

    Example:
        jigy validate           # Run full validation
        jigy validate intent    # Validate intent only
        jigy validate bricks    # Validate bricks only
        jigy validate full      # Run full validation (explicit)
        jigy validate -j        # JSON output
        jigy validate -m        # Markdown output
    """
    # If no subcommand, run full validation
    if ctx.invoked_subcommand is None:
        output_format = resolve_format(json, markdown)
        config = get_config(ctx)
        skip_rebuild = get_no_rebuild(ctx)
        exit_code = validate_full_command(config, output_format.value, skip_rebuild=skip_rebuild, verbose=verbose)
        sys.exit(exit_code)


@validate.command(name="intent")
@add_output_options
@click.pass_context
@jig.implements("S-026", "S-061", "S-065", "S-071", "S-093")
def validate_intent_cli(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Validate intent artifacts (specifications, outcomes, decorators).

    Validates human-authored artifacts before any graph generation.
    Can run without graphs existing.

    Example:
        jigy validate intent
        jigy validate intent -j    # JSON output
        jigy validate intent -m    # Markdown output
    """
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = validate_intent_command(config, output_format.value, skip_rebuild=skip_rebuild, verbose=verbose)
    sys.exit(exit_code)


@validate.command(name="bricks")
@add_output_options
@click.pass_context
@jig.implements("S-026", "S-061", "S-065", "S-071", "S-093")
def validate_bricks_cli(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Validate brick definitions and partition constraints.

    Validates brick definitions against implementation graph.
    Requires implementation graph to exist.

    Example:
        jigy validate bricks
        jigy validate bricks -j    # JSON output
        jigy validate bricks -m    # Markdown output
    """
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = validate_bricks_command(config, output_format.value, skip_rebuild=skip_rebuild, verbose=verbose)
    sys.exit(exit_code)


@validate.command()
@add_output_options
@click.pass_context
@jig.implements("S-026", "S-061", "S-065", "S-071", "S-093")
def full(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Run full validation (intent + bricks if graph exists).

    Validates all artifacts. Runs intent validation always,
    and brick validation if implementation graph exists.

    Example:
        jigy validate full
        jigy validate full -j    # JSON output
        jigy validate full -m    # Markdown output
    """
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = validate_full_command(config, output_format.value, skip_rebuild=skip_rebuild, verbose=verbose)
    sys.exit(exit_code)


# Show command group (S-060)
@cli.group(name="show", invoke_without_command=True)
@add_output_options
@click.pass_context
@jig.implements("S-060", "S-065", "S-071", "S-093")
def show_group(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Display JIG structure information.

    Shows bricks, layers, and other structural details.

    Example:
        jigy show           # Show overview
        jigy show layers    # Show layer hierarchy
        jigy show bricks    # Show brick details
        jigy show -j        # JSON output
        jigy show -m        # Markdown output
    """
    if ctx.invoked_subcommand is None:
        # No subcommand = show overview
        output_format = resolve_format(json, markdown)
        config = get_config(ctx)
        skip_rebuild = get_no_rebuild(ctx)
        exit_code = show_overview_command(config, output_format=output_format, verbose=verbose, skip_rebuild=skip_rebuild)
        sys.exit(exit_code)


@show_group.command(name="layers")
@add_output_options
@click.pass_context
@jig.implements("S-060", "S-065", "S-071", "S-093")
def show_layers_cli(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Display layer hierarchy."""
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = show_layers_command(config, output_format=output_format, verbose=verbose, skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


@show_group.command(name="bricks")
@add_output_options
@click.pass_context
@jig.implements("S-060", "S-065", "S-071", "S-093")
def show_bricks_cli(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Display brick details."""
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = show_bricks_command(config, output_format=output_format, verbose=verbose, skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


@show_group.command(name="charter")
@add_output_options
@click.pass_context
@jig.implements("S-072", "S-065", "S-071", "S-093")
def show_charter_cli(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Display Charter.md content and goals.

    Shows the project charter with defined goals.

    Example:
        jigy show charter
        jigy show charter -j    # JSON output
        jigy show charter -m    # Markdown output
    """
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = show_charter_command(config, output_format=output_format, verbose=verbose, skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


@show_group.command(name="goals")
@add_output_options
@click.pass_context
@jig.implements("S-075", "S-065", "S-071", "S-093")
def show_goals_cli(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Display all goals with supporting artifacts.

    Lists goals from Charter.md with their supporting
    Outcomes and Architecture documents.

    Example:
        jigy show goals
        jigy show goals -j    # JSON output
        jigy show goals -m    # Markdown output
    """
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = show_goals_command(config, output_format=output_format, verbose=verbose, skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


@show_group.command(name="architecture")
@click.argument("arch_id", required=False, default=None)
@add_output_options
@click.pass_context
@jig.implements("S-076", "S-065", "S-071", "S-093")
def show_architecture_cli(ctx, arch_id: str | None, json: bool, markdown: bool, verbose: bool) -> None:
    """Display architecture documents.

    Lists all architecture documents, or shows details
    for a specific one if ARCH_ID is provided.

    Example:
        jigy show architecture         # List all
        jigy show architecture A-001   # Show specific
        jigy show architecture -j      # JSON output
        jigy show architecture -m      # Markdown output
    """
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = show_architecture_command(config, arch_id=arch_id, output_format=output_format, verbose=verbose, skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


@show_group.command(name="towers")
@click.argument("tower_id", required=False, default=None)
@add_output_options
@click.pass_context
@jig.implements("S-060", "S-090", "S-065", "S-071", "S-093")
def show_towers_cli(ctx, tower_id: str | None, json: bool, markdown: bool, verbose: bool) -> None:
    """Display tower structure with brick counts.

    Lists all towers with brick counts by layer.
    For single-tower projects, shows appropriate message.

    Example:
        jigy show towers           # List all towers
        jigy show towers backend   # Show specific tower
        jigy show towers -j        # JSON output
        jigy show towers -m        # Markdown output
    """
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = show_towers_command(config, tower_id=tower_id, output_format=output_format, verbose=verbose, skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


@show_group.command(name="matrix")
@add_output_options
@click.pass_context
@jig.implements("S-060", "S-091", "S-065", "S-071", "S-093")
def show_matrix_cli(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Display layer x tower grid.

    Shows a matrix view of layers vs towers.
    For single-tower projects, shows appropriate message.

    Example:
        jigy show matrix        # Display matrix
        jigy show matrix -j     # JSON output
        jigy show matrix -m     # Markdown output
    """
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = show_matrix_command(config, output_format=output_format, verbose=verbose, skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


# Audit command group (S-066)
@cli.group(name="audit", invoke_without_command=True)
@click.pass_context
@jig.implements("S-066")
def audit_group(ctx) -> None:
    """Run audits to collect alignment evidence.

    Audits collect objective data about code relationships through
    execution-based analysis.

    Example:
        jigy audit coverage    # Run coverage audit for T→F edges
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@audit_group.command(name="coverage")
@add_output_options
@click.pass_context
@jig.implements("S-066", "S-067", "S-071", "S-093")
def audit_coverage_cli(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """Run full coverage audit pipeline.

    Runs tests with coverage, extracts T→F edges, and writes
    results to jig/audits/records/coverage-YYYY-MM-DD.ndjson.

    Example:
        jigy audit coverage
        jigy audit coverage -j    # JSON output
        jigy audit coverage -m    # Markdown output
    """
    output_format = resolve_format(json, markdown)
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = coverage_command(config, skip_rebuild=skip_rebuild, output_format=output_format, verbose=verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
