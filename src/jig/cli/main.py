"""Main CLI entry point for JIG."""

import logging
import sys
from pathlib import Path

import click

from jig.impl_graph.builder import build_graph


@click.group()
@click.version_option()
def cli():
    """JIG - Just-In-time Graph for alignment tracking."""
    pass


@cli.group()
def impl():
    """Implementation graph commands."""
    pass


@impl.command()
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Root directory of the project (default: current directory)",
)
@click.option(
    "--source-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Source directory to scan (default: <project-root>/src)",
)
@click.option(
    "--exclude",
    multiple=True,
    help="Glob patterns to exclude (can be specified multiple times)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file path (default: <project-root>/jig/generated/implementation-graph.ndjson)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--strict/--lenient",
    default=True,
    help="Fail on parse errors (default: strict)",
)
@click.option(
    "--no-timestamp",
    is_flag=True,
    help="Exclude timestamp from metadata (for deterministic output)",
)
def rebuild(
    project_root: Path,
    source_dir: Path | None,
    exclude: tuple[str, ...],
    output: Path | None,
    verbose: bool,
    strict: bool,
    no_timestamp: bool,
) -> None:
    """Rebuild the implementation graph from source code.

    Scans Python source files, extracts structure and decorators,
    and generates an NDJSON implementation graph.

    Example:
        jig impl rebuild --project-root ~/my-project --verbose
    """
    # Configure logging
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
    else:
        logging.basicConfig(level=logging.WARNING, format="%(message)s")

    # Determine output path
    if output is None:
        output = project_root / "jig" / "generated" / "implementation-graph.ndjson"

    # Convert exclude tuple to list
    exclude_patterns = list(exclude) if exclude else None

    try:
        # Build the graph
        click.echo(f"Building implementation graph for {project_root}")

        graph = build_graph(
            project_root=project_root,
            source_dir=source_dir,
            output_path=output,
            exclude_patterns=exclude_patterns,
            verbose=verbose,
            strict=strict,
            include_timestamp=not no_timestamp,
        )

        # Report results
        click.echo(f"\n✓ Graph generated successfully:")
        click.echo(f"  - Nodes: {graph.node_count()}")
        click.echo(f"  - Edges: {graph.edge_count()}")
        click.echo(f"  - Output: {output}")

    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
