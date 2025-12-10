"""Main CLI entry point for JIG."""

import sys

import click

import jig


class OrderedGroup(click.Group):
    """A Click group that preserves command order."""

    def list_commands(self, ctx):
        return list(self.commands.keys())


from jig.cli.discovery import ProjectNotFoundError, find_project_root
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
@click.pass_context
@jig.implements("S-061")
def cli(ctx):
    """JIG — Keep specs, code, and tests aligned."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Verb-first rebuild command group (S-058)
@cli.group(name="rebuild", invoke_without_command=True)
@click.pass_context
@jig.implements("S-058")
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
        try:
            project_root = find_project_root()
        except ProjectNotFoundError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        exit_code = rebuild_all_command(project_root)
        sys.exit(exit_code)


@rebuild_group.command(name="impl")
@jig.implements("S-058")
def rebuild_impl_cli() -> None:
    """Rebuild implementation graph."""
    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code = rebuild_impl_command(project_root)
    sys.exit(exit_code)


@rebuild_group.command(name="intent")
@jig.implements("S-058")
def rebuild_intent_cli() -> None:
    """Rebuild intent graph."""
    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code = rebuild_intent_command(project_root)
    sys.exit(exit_code)


@rebuild_group.command(name="verify")
@jig.implements("S-058")
def rebuild_verify_cli() -> None:
    """Rebuild verification graph."""
    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code = rebuild_verify_command(project_root)
    sys.exit(exit_code)


@cli.command()
@jig.implements("S-059")
def align() -> None:
    """Run full alignment workflow.

    Rebuilds all graphs, validates artifacts, and displays summary.
    This is the "do everything" command for keeping JIG in sync.

    Example:
        jigy align
    """
    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code = align_command(project_root)
    sys.exit(exit_code)


@cli.group(invoke_without_command=True)
@click.pass_context
@jig.implements("S-061")
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
        try:
            project_root = find_project_root()
        except ProjectNotFoundError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        exit_code = validate_full_command(project_root, "human")
        sys.exit(exit_code)


@validate.command(name="intent")
@jig.implements("S-061")
def validate_intent_cli() -> None:
    """Validate intent artifacts (specifications, outcomes, decorators).

    Validates human-authored artifacts before any graph generation.
    Can run without graphs existing.

    Example:
        jigy validate intent
    """
    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code = validate_intent_command(project_root, "human")
    sys.exit(exit_code)


@validate.command(name="bricks")
@jig.implements("S-061")
def validate_bricks_cli() -> None:
    """Validate brick definitions and partition constraints.

    Validates brick definitions against implementation graph.
    Requires implementation graph to exist.

    Example:
        jigy validate bricks
    """
    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code = validate_bricks_command(project_root, "human")
    sys.exit(exit_code)


@validate.command()
@jig.implements("S-061")
def full() -> None:
    """Run full validation (intent + bricks if graph exists).

    Validates all artifacts. Runs intent validation always,
    and brick validation if implementation graph exists.

    Example:
        jigy validate full
    """
    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code = validate_full_command(project_root, "human")
    sys.exit(exit_code)


# Show command group (S-060)
@cli.group(name="show", invoke_without_command=True)
@click.pass_context
@jig.implements("S-060")
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
        try:
            project_root = find_project_root()
        except ProjectNotFoundError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        exit_code = show_overview_command(project_root)
        sys.exit(exit_code)


@show_group.command(name="layers")
@jig.implements("S-060")
def show_layers_cli() -> None:
    """Display layer hierarchy."""
    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code = show_layers_command(project_root)
    sys.exit(exit_code)


@show_group.command(name="bricks")
@jig.implements("S-060")
def show_bricks_cli() -> None:
    """Display brick details."""
    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code = show_bricks_command(project_root)
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
