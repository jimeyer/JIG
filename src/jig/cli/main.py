"""Main CLI entry point for JIG."""

import sys
from pathlib import Path
from typing import Optional

import click

import jig
from jig.config import ConfigError, JigConfig, load_config


class OrderedGroup(click.Group):
    """A Click group with explicit command ordering and commands-first help."""

    COMMAND_ORDER = ["init", "validate", "mend", "context", "audit", "rebuild"]

    def list_commands(self, ctx):
        # Return commands in explicit order, then any others
        ordered = [c for c in self.COMMAND_ORDER if c in self.commands]
        others = [c for c in self.commands if c not in self.COMMAND_ORDER]
        return ordered + others

    def format_help(self, ctx, formatter):
        """Format help to show commands before options."""
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        # Commands first
        self.format_commands(ctx, formatter)
        # Then options
        self.format_options(ctx, formatter)

    def format_options(self, ctx, formatter):
        """Format options in specific order: -j, -m, -v, -h, --version, --no-rebuild."""
        # Collect all options with their names
        opts_by_name = {}
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                # Use first option name as key
                name = param.opts[0] if param.opts else param.name
                opts_by_name[name] = rv

        # Define desired order
        order = ["-j", "-m", "-v", "-h", "--version", "--no-rebuild"]
        ordered_opts = []
        for key in order:
            if key in opts_by_name:
                ordered_opts.append(opts_by_name[key])
        # Add any remaining options not in our order
        for key, rv in opts_by_name.items():
            if key not in order:
                ordered_opts.append(rv)

        if ordered_opts:
            with formatter.section("Options"):
                formatter.write_dl(ordered_opts)


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
from jig.cli.init import init_command
from jig.cli.mend import mend_command
from jig.cli.output import add_output_options, resolve_format
from jig.cli.rebuild import (
    rebuild_all_command,
    rebuild_impl_command,
    rebuild_intent_command,
    rebuild_verify_command,
)
from jig.cli.validate import (
    validate_bricks_command,
    validate_full_command,
    validate_intent_command,
)
from jig.cli.context import context_command


@click.group(
    cls=OrderedGroup,
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "--no-rebuild",
    is_flag=True,
    default=False,
    help="Skip automatic graph rebuild before commands",
)
@click.version_option(None, "--version", message="jigy version %(version)s", help="Show version number and exit")
@click.option("-v", "--verbose", is_flag=True, help="Show detailed progress")
@click.option("-m", "--markdown", is_flag=True, help="Output LLM-optimized markdown")
@click.option("-j", "--json", is_flag=True, help="Output single-line JSON")
@click.pass_context
@jig.implements("S-061", "S-065", "S-071", "S-093")
def cli(ctx, no_rebuild: bool, json: bool, markdown: bool, verbose: bool):
    """JIG (Jig Intent Graph) — Keep specs, code, and tests aligned."""
    ctx.ensure_object(dict)
    ctx.obj["no_rebuild"] = no_rebuild
    # Store output options in context for subcommands that want to inherit them
    ctx.obj["json"] = json
    ctx.obj["markdown"] = markdown
    ctx.obj["verbose"] = verbose
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Init command (S-103)
@cli.command(name="init")
@click.option(
    "-p",
    "--project",
    "project_name",
    default=None,
    help="Project name for Charter filename (default: directory name)",
)
@click.option(
    "--no-skills",
    is_flag=True,
    default=False,
    help="Skip skill installation",
)
@click.option(
    "--skills-only",
    is_flag=True,
    default=False,
    help="Only install skills, skip jig/ structure",
)
@click.option(
    "--global-skills",
    is_flag=True,
    default=False,
    help="Install skills to ~/.agent/skills/ instead of .agent/skills/",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite existing jig.toml (does not overwrite Charter or bricks.yaml)",
)
@add_output_options
@jig.implements("S-103")
def init_cli(
    project_name: str | None,
    no_skills: bool,
    skills_only: bool,
    global_skills: bool,
    force: bool,
    json: bool,
    markdown: bool,
    verbose: bool,
) -> None:
    """Initialize a new JIG project.

    Creates the JIG directory structure and configuration files:
    - jig.toml configuration file
    - jig/ directory with Charter, specifications, outcomes, architecture
    - .agent/skills/jig/ with AI agent skill files

    Examples:
        jigy init                    # Initialize with defaults
        jigy init -p myproject       # Set project name
        jigy init --no-skills        # Skip skill installation
        jigy init --skills-only      # Only install skills
        jigy init --global-skills    # Install skills globally
        jigy init -f                 # Force overwrite jig.toml
        jigy init -j                 # JSON output
    """
    # Check mutual exclusivity
    if no_skills and skills_only:
        raise click.UsageError("--no-skills and --skills-only are mutually exclusive")

    output_format = resolve_format(json, markdown)
    exit_code = init_command(
        project_name=project_name,
        no_skills=no_skills,
        skills_only=skills_only,
        global_skills=global_skills,
        force=force,
        output_format=output_format,
        verbose=verbose,
    )
    sys.exit(exit_code)


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


# Context command (S-110)
@cli.command(name="context")
@click.argument("identifier", required=False, default=None)
@click.option(
    "--max",
    "max_nodes",
    type=int,
    default=50,
    help="Maximum total nodes in response (default: 50)",
)
@add_output_options
@click.pass_context
@jig.implements("S-110")
def context_cli(
    ctx, identifier: str | None, max_nodes: int, json: bool, markdown: bool, verbose: bool
) -> None:
    """Get project overview or graph neighborhood for an identifier.

    Without IDENTIFIER: Returns unified project overview (S-114).
    With IDENTIFIER: Returns ancestors and descendants of the node.
    With invalid IDENTIFIER: Returns overview + "not found" note.

    IDENTIFIER can be:
      S-### (specification), O-### (outcome), G-### (goal),
      A-### (architecture), B-* (brick), F-* (function),
      T-* (test), Charter, or a file path.

    Example:
        jigy context               # Project overview
        jigy context S-042         # Graph neighborhood
        jigy context S-042 -j      # JSON for agents
        jigy context S-042 --max 20  # Limit response size
        jigy context S-999         # Overview + "not found" note
    """
    output_format = resolve_format(json, markdown)
    skip_rebuild = get_no_rebuild(ctx)

    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code, output = context_command(
        identifier=identifier,
        project_root=project_root,
        max_nodes=max_nodes,
        output_format=output_format.value,
        verbose=verbose,
        skip_rebuild=skip_rebuild,
    )
    click.echo(output)
    sys.exit(exit_code)


# Alias commands (S-115)
# Full aliases: graph, list → context (with optional identifier)
@cli.command(name="graph")
@click.argument("identifier", required=False, default=None)
@click.option(
    "--max",
    "max_nodes",
    type=int,
    default=50,
    help="Maximum total nodes in response (default: 50)",
)
@add_output_options
@click.pass_context
@jig.implements("S-115")
def graph_alias(
    ctx, identifier: str | None, max_nodes: int, json: bool, markdown: bool, verbose: bool
) -> None:
    """(alias) Graph traversal → jigy context."""
    output_format = resolve_format(json, markdown)
    skip_rebuild = get_no_rebuild(ctx)

    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code, output = context_command(
        identifier=identifier,
        project_root=project_root,
        max_nodes=max_nodes,
        output_format=output_format.value,
        verbose=verbose,
        skip_rebuild=skip_rebuild,
    )
    click.echo(output)
    sys.exit(exit_code)


@cli.command(name="list")
@click.argument("identifier", required=False, default=None)
@click.option(
    "--max",
    "max_nodes",
    type=int,
    default=50,
    help="Maximum total nodes in response (default: 50)",
)
@add_output_options
@click.pass_context
@jig.implements("S-115")
def list_alias(
    ctx, identifier: str | None, max_nodes: int, json: bool, markdown: bool, verbose: bool
) -> None:
    """(alias) List artifacts → jigy context."""
    output_format = resolve_format(json, markdown)
    skip_rebuild = get_no_rebuild(ctx)

    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code, output = context_command(
        identifier=identifier,
        project_root=project_root,
        max_nodes=max_nodes,
        output_format=output_format.value,
        verbose=verbose,
        skip_rebuild=skip_rebuild,
    )
    click.echo(output)
    sys.exit(exit_code)


@cli.command(name="show")
@click.argument("identifier", required=False, default=None)
@click.option(
    "--max",
    "max_nodes",
    type=int,
    default=50,
    help="Maximum total nodes in response (default: 50)",
)
@add_output_options
@click.pass_context
@jig.implements("S-115")
def show_alias(
    ctx, identifier: str | None, max_nodes: int, json: bool, markdown: bool, verbose: bool
) -> None:
    """(alias) Show info → jigy context."""
    output_format = resolve_format(json, markdown)
    skip_rebuild = get_no_rebuild(ctx)

    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code, output = context_command(
        identifier=identifier,
        project_root=project_root,
        max_nodes=max_nodes,
        output_format=output_format.value,
        verbose=verbose,
        skip_rebuild=skip_rebuild,
    )
    click.echo(output)
    sys.exit(exit_code)


# Bare-only aliases: bricks, layers, towers → context (overview only)
@cli.command(name="bricks")
@add_output_options
@click.pass_context
@jig.implements("S-115")
def bricks_alias(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """(alias) Brick info → jigy context (overview)."""
    output_format = resolve_format(json, markdown)
    skip_rebuild = get_no_rebuild(ctx)

    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code, output = context_command(
        identifier=None,  # Bare only - always overview
        project_root=project_root,
        max_nodes=50,
        output_format=output_format.value,
        verbose=verbose,
        skip_rebuild=skip_rebuild,
    )
    click.echo(output)
    sys.exit(exit_code)


@cli.command(name="layers")
@add_output_options
@click.pass_context
@jig.implements("S-115")
def layers_alias(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """(alias) Layer info → jigy context (overview)."""
    output_format = resolve_format(json, markdown)
    skip_rebuild = get_no_rebuild(ctx)

    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code, output = context_command(
        identifier=None,  # Bare only - always overview
        project_root=project_root,
        max_nodes=50,
        output_format=output_format.value,
        verbose=verbose,
        skip_rebuild=skip_rebuild,
    )
    click.echo(output)
    sys.exit(exit_code)


@cli.command(name="towers")
@add_output_options
@click.pass_context
@jig.implements("S-115")
def towers_alias(ctx, json: bool, markdown: bool, verbose: bool) -> None:
    """(alias) Tower info → jigy context (overview)."""
    output_format = resolve_format(json, markdown)
    skip_rebuild = get_no_rebuild(ctx)

    try:
        project_root = find_project_root()
    except ProjectNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    exit_code, output = context_command(
        identifier=None,  # Bare only - always overview
        project_root=project_root,
        max_nodes=50,
        output_format=output_format.value,
        verbose=verbose,
        skip_rebuild=skip_rebuild,
    )
    click.echo(output)
    sys.exit(exit_code)


# Fix alias: fix → mend
@cli.command(name="fix")
@click.option(
    "--auto",
    "auto_mode",
    is_flag=True,
    default=False,
    help="Apply all auto-fixable validation errors",
)
@click.option(
    "--apply",
    "apply_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Apply explicit fixes from JSON file",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show changes without modifying files",
)
@click.option(
    "--no-iterate",
    is_flag=True,
    default=False,
    help="Disable fixed point iteration (single pass only)",
)
@click.option(
    "-j",
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Output results as JSON",
)
@jig.implements("S-115")
def fix_alias(
    auto_mode: bool,
    apply_path: Path | None,
    dry_run: bool,
    no_iterate: bool,
    json_output: bool,
) -> None:
    """(alias) Fix artifacts → jigy mend."""
    # Import here to avoid circular imports at module load
    from jig.mend.engine import mend_apply, mend_auto, mend_combined

    project_root = find_project_root()

    # Same logic as mend_command
    if auto_mode and apply_path:
        result = mend_combined(
            project_root=project_root,
            auto_json_path=apply_path,
            dry_run=dry_run,
            iterate=not no_iterate,
        )
    elif apply_path:
        result = mend_apply(
            project_root=project_root,
            apply_path=apply_path,
            dry_run=dry_run,
            iterate=not no_iterate,
        )
    elif auto_mode:
        result = mend_auto(
            project_root=project_root,
            dry_run=dry_run,
            iterate=not no_iterate,
        )
    else:
        # Default to auto mode
        result = mend_auto(
            project_root=project_root,
            dry_run=dry_run,
            iterate=not no_iterate,
        )

    if json_output:
        import json
        click.echo(json.dumps(result, indent=2))
    else:
        # Import format function from mend module
        from jig.cli.mend import _format_text_output
        click.echo(_format_text_output(result, dry_run))

    sys.exit(0 if result.get("success", True) else 1)


# Mend command (S-105, S-106, S-107)
cli.add_command(mend_command)


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
