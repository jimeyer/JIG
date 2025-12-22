"""Main CLI entry point for JIG."""

import sys
from pathlib import Path
from typing import Optional

import click

import jig
from jig.config import ConfigError, JigConfig, load_config


class OrderedGroup(click.Group):
    """A Click group that preserves command order."""

    def list_commands(self, ctx):
        return list(self.commands.keys())


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
from jig.cli.rebuild import (
    align_command,
    rebuild_all_command,
    rebuild_impl_command,
    rebuild_intent_command,
    rebuild_verify_command,
)
from jig.cli.show import (
    show_bricks_command,
    show_layers_command,
    show_overview_command,
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
@click.pass_context
@jig.implements("S-058", "S-065")
def rebuild_group(ctx) -> None:
    """Rebuild JIG graphs.

    Rebuilds implementation, verification, and/or intent graphs.

    Example:
        jigy rebuild           # Rebuild all graphs
        jigy rebuild impl      # Rebuild implementation graph only
        jigy rebuild intent    # Rebuild intent graph only
        jigy rebuild verify    # Rebuild verification graph only
    """
    if ctx.invoked_subcommand is None:
        # No subcommand = rebuild all
        config = get_config(ctx)
        exit_code = rebuild_all_command(config)
        sys.exit(exit_code)


@rebuild_group.command(name="impl")
@click.pass_context
@jig.implements("S-058", "S-065")
def rebuild_impl_cli(ctx) -> None:
    """Rebuild implementation graph."""
    config = get_config(ctx)
    exit_code = rebuild_impl_command(config)
    sys.exit(exit_code)


@rebuild_group.command(name="intent")
@click.pass_context
@jig.implements("S-058", "S-065")
def rebuild_intent_cli(ctx) -> None:
    """Rebuild intent graph."""
    config = get_config(ctx)
    exit_code = rebuild_intent_command(config)
    sys.exit(exit_code)


@rebuild_group.command(name="verify")
@click.pass_context
@jig.implements("S-058", "S-065")
def rebuild_verify_cli(ctx) -> None:
    """Rebuild verification graph."""
    config = get_config(ctx)
    exit_code = rebuild_verify_command(config)
    sys.exit(exit_code)


@cli.command()
@click.pass_context
@jig.implements("S-059", "S-065")
def align(ctx) -> None:
    """Run full alignment workflow.

    Rebuilds all graphs, validates artifacts, and displays summary.
    This is the "do everything" command for keeping JIG in sync.

    Example:
        jigy align
    """
    config = get_config(ctx)
    exit_code = align_command(config)
    sys.exit(exit_code)


@cli.group(invoke_without_command=True)
@click.pass_context
@jig.implements("S-061", "S-065", "S-071")
def validate(ctx):
    """Validate JIG artifacts.

    Validates specifications, outcomes, decorators, and bricks.

    Example:
        jigy validate           # Run full validation
        jigy validate intent    # Validate intent only
        jigy validate bricks    # Validate bricks only
        jigy validate full      # Run full validation (explicit)
    """
    # If no subcommand, run full validation
    if ctx.invoked_subcommand is None:
        config = get_config(ctx)
        skip_rebuild = get_no_rebuild(ctx)
        exit_code = validate_full_command(config, "human", skip_rebuild=skip_rebuild)
        sys.exit(exit_code)


@validate.command(name="intent")
@click.pass_context
@jig.implements("S-061", "S-065", "S-071")
def validate_intent_cli(ctx) -> None:
    """Validate intent artifacts (specifications, outcomes, decorators).

    Validates human-authored artifacts before any graph generation.
    Can run without graphs existing.

    Example:
        jigy validate intent
    """
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = validate_intent_command(config, "human", skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


@validate.command(name="bricks")
@click.pass_context
@jig.implements("S-061", "S-065", "S-071")
def validate_bricks_cli(ctx) -> None:
    """Validate brick definitions and partition constraints.

    Validates brick definitions against implementation graph.
    Requires implementation graph to exist.

    Example:
        jigy validate bricks
    """
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = validate_bricks_command(config, "human", skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


@validate.command()
@click.pass_context
@jig.implements("S-061", "S-065", "S-071")
def full(ctx) -> None:
    """Run full validation (intent + bricks if graph exists).

    Validates all artifacts. Runs intent validation always,
    and brick validation if implementation graph exists.

    Example:
        jigy validate full
    """
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = validate_full_command(config, "human", skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


# Show command group (S-060)
@cli.group(name="show", invoke_without_command=True)
@click.pass_context
@jig.implements("S-060", "S-065", "S-071")
def show_group(ctx) -> None:
    """Display JIG structure information.

    Shows bricks, layers, and other structural details.

    Example:
        jigy show           # Show overview
        jigy show layers    # Show layer hierarchy
        jigy show bricks    # Show brick details
    """
    if ctx.invoked_subcommand is None:
        # No subcommand = show overview
        config = get_config(ctx)
        skip_rebuild = get_no_rebuild(ctx)
        exit_code = show_overview_command(config, skip_rebuild=skip_rebuild)
        sys.exit(exit_code)


@show_group.command(name="layers")
@click.pass_context
@jig.implements("S-060", "S-065", "S-071")
def show_layers_cli(ctx) -> None:
    """Display layer hierarchy."""
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = show_layers_command(config, skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


@show_group.command(name="bricks")
@click.pass_context
@jig.implements("S-060", "S-065", "S-071")
def show_bricks_cli(ctx) -> None:
    """Display brick details."""
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = show_bricks_command(config, skip_rebuild=skip_rebuild)
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
@click.pass_context
@jig.implements("S-066", "S-067", "S-071")
def audit_coverage_cli(ctx) -> None:
    """Run full coverage audit pipeline.

    Runs tests with coverage, extracts T→F edges, and writes
    results to jig/audits/records/coverage-YYYY-MM-DD.ndjson.

    Example:
        jigy audit coverage
    """
    config = get_config(ctx)
    skip_rebuild = get_no_rebuild(ctx)
    exit_code = coverage_command(config, skip_rebuild=skip_rebuild)
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
