"""ABOUTME: Project Overview implementation for CLI consolidation.
ABOUTME: Builds unified context combining charter, goals, specs, bricks, etc."""

import click

import jig
from jig.cli.output import OutputFormat
from jig.config import JigConfig

# Re-exports from query layer for backwards compatibility
from jig.query.overview import (  # noqa: F401
    _load_bricks,
    _load_graph,
    _load_yaml_frontmatter,
    build_overview,
    format_overview_human,
    format_overview_json,
    format_overview_markdown,
)


@jig.implements("S-114")
def show_overview(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
    skip_rebuild: bool = False,
    note: str | None = None,
) -> int:
    """Display project overview.

    Args:
        config: JIG configuration.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: Include additional detail.
        skip_rebuild: Skip auto-rebuild.
        note: Optional note to prepend (e.g., "S-999 not found").

    Returns:
        Exit code (0 for success).
    """
    from jig.cli.auto_rebuild import ensure_graphs_current

    ensure_graphs_current(["impl", "verify", "intent"], config, skip_rebuild=skip_rebuild)

    overview = build_overview(config)

    if output_format == OutputFormat.JSON:
        if note:
            overview["note"] = note
        click.echo(format_overview_json(overview))
    elif output_format == OutputFormat.MARKDOWN:
        output = format_overview_markdown(overview, verbose=verbose)
        if note:
            output = f"> **Note:** {note}\n\n{output}"
        click.echo(output)
    else:
        output = format_overview_human(overview, verbose=verbose)
        if note:
            output = f"Note: {note}\n\n{output}"
        click.echo(output)

    return 0
