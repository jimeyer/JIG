"""Main CLI entry point for JIG."""

import logging
import sys
from pathlib import Path

import click

from jig.cli.layers import layers_command, suggest_layers_command
from jig.cli.validate import (
    auto_validate_decorators,
    validate_bricks_command,
    validate_full_command,
    validate_intent_command,
)
from jig.cli.verify import verify_rebuild_command
from jig.impl_graph.builder import build_graph
from jig.intent_graph.generator import generate_intent_graph


@click.group()
@click.version_option()
def cli():
    """JIG - JIG Intent Graph for Software Alignment."""
    pass


@cli.group()
def impl():
    """Implementation graph commands."""
    pass


@cli.group()
def intent():
    """Intent graph commands."""
    pass


@cli.group()
def verify():
    """Verification graph commands."""
    pass


@cli.command()
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Root directory of the project (default: current directory)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def rebuild(project_root: Path, verbose: bool) -> None:
    """Run complete JIG rebuild workflow.

    Executes all standard JIG commands in sequence:
    1. Rebuild implementation graph
    2. Rebuild verification graph
    3. Validate artifacts
    4. Rebuild intent graph
    5. Display layer structure

    Example:
        jigy rebuild
        jigy rebuild --verbose
    """
    # Configure logging if verbose
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Step 1: Rebuild implementation graph
    click.echo("=" * 60)
    click.echo("Step 1/5: Rebuilding implementation graph...")
    click.echo("=" * 60)
    try:
        impl_output = project_root / "jig" / "generated" / "implementation-graph.ndjson"
        graph = build_graph(
            project_root=project_root,
            source_dir=None,  # Uses default
            output_path=impl_output,
            exclude_patterns=None,
            verbose=verbose,
            strict=True,
            include_timestamp=True,
        )
        click.echo(f"\n✓ Implementation graph generated successfully:")
        click.echo(f"  - Nodes: {graph.node_count()}")
        click.echo(f"  - Edges: {graph.edge_count()}")
        click.echo(f"  - Output: {impl_output}")
    except Exception as e:
        click.echo(f"\n✗ Implementation rebuild failed: {e}", err=True)
        sys.exit(1)

    # Step 2: Rebuild verification graph
    click.echo("\n" + "=" * 60)
    click.echo("Step 2/5: Rebuilding verification graph...")
    click.echo("=" * 60)
    try:
        from jig.verification_graph.builder import build_verification_graph

        verify_output = project_root / "jig" / "generated" / "verification-graph.ndjson"
        verify_graph = build_verification_graph(
            project_root=project_root,
            test_dir=None,  # Uses default
            output_path=verify_output,
            include_timestamp=True,
        )
        click.echo(f"\n✓ Verification graph generated successfully:")
        click.echo(f"  - Nodes: {verify_graph.node_count()}")
        click.echo(f"  - Edges: {verify_graph.edge_count()}")
        click.echo(f"  - Output: {verify_output}")
    except Exception as e:
        click.echo(f"\n✗ Verification rebuild failed: {e}", err=True)
        sys.exit(1)

    # Step 3: Validate artifacts
    click.echo("\n" + "=" * 60)
    click.echo("Step 3/5: Validating JIG artifacts...")
    click.echo("=" * 60)
    exit_code = validate_full_command(project_root, "human")
    if exit_code != 0:
        click.echo("\n✗ Validation failed. Stopping rebuild.", err=True)
        sys.exit(exit_code)

    # Step 4: Rebuild intent graph
    click.echo("\n" + "=" * 60)
    click.echo("Step 4/5: Rebuilding intent graph...")
    click.echo("=" * 60)
    try:
        output_path, node_count, edge_count = generate_intent_graph(
            project_root=project_root,
            output_path=None,  # Uses default
            include_timestamp=True,
        )
        click.echo(f"\n✓ Intent graph generated successfully:")
        click.echo(f"  - Nodes: {node_count}")
        click.echo(f"  - Edges: {edge_count}")
        click.echo(f"  - Output: {output_path}")
    except Exception as e:
        click.echo(f"\n✗ Intent rebuild failed: {e}", err=True)
        sys.exit(1)

    # Step 5: Display layers
    click.echo("\n" + "=" * 60)
    click.echo("Step 5/5: Displaying layer structure...")
    click.echo("=" * 60)
    exit_code = layers_command(project_root, summary=False, verbose=verbose)
    if exit_code != 0:
        click.echo("\n✗ Layer display failed.", err=True)
        sys.exit(exit_code)

    # Success summary
    click.echo("\n" + "=" * 60)
    click.echo("✓ Complete! All JIG artifacts rebuilt successfully.")
    click.echo("=" * 60)


@cli.group(invoke_without_command=True)
@click.pass_context
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Root directory of the project (default: current directory)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"], case_sensitive=False),
    default="human",
    help="Output format (default: human-readable)",
)
def validate(ctx, project_root: Path, output_format: str):
    """Validate JIG artifacts."""
    # If no subcommand, run full validation
    if ctx.invoked_subcommand is None:
        exit_code = validate_full_command(project_root, output_format)
        sys.exit(exit_code)


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
@click.option(
    "--skip-validation",
    is_flag=True,
    help="Skip decorator validation before building graph",
)
def rebuild(
    project_root: Path,
    source_dir: Path | None,
    exclude: tuple[str, ...],
    output: Path | None,
    verbose: bool,
    strict: bool,
    no_timestamp: bool,
    skip_validation: bool,
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

    # Auto-validate decorators (unless skipped)
    if not skip_validation:
        if not auto_validate_decorators(project_root):
            sys.exit(1)

    try:
        # Build the graph
        click.echo(f"Generating implementation graph for {project_root}")

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
        click.echo(f"\n✓ Implementation graph generated successfully:")
        click.echo(f"  - Nodes: {graph.node_count()}")
        click.echo(f"  - Edges: {graph.edge_count()}")
        click.echo(f"  - Output: {output}")

    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@intent.command()
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Root directory of the project (default: current directory)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file path (default: <project-root>/jig/generated/intent-graph.ndjson)",
)
@click.option(
    "--no-timestamp",
    is_flag=True,
    help="Exclude timestamp from metadata (for deterministic output)",
)
def rebuild(
    project_root: Path,
    output: Path | None,
    no_timestamp: bool,
) -> None:
    """Generate intent-graph.ndjson from specifications, outcomes, and bricks.

    Reads all specification and outcome files, loads bricks.yaml,
    and generates an NDJSON intent graph per A001 §6.1.

    Example:
        jigy intent rebuild
        jigy intent rebuild --project-root ~/my-project
        jigy intent rebuild --output custom-intent-graph.ndjson
    """
    try:
        click.echo(f"Generating intent graph for {project_root}")

        output_path, node_count, edge_count = generate_intent_graph(
            project_root=project_root,
            output_path=output,
            include_timestamp=not no_timestamp,
        )

        click.echo(f"\n✓ Intent graph generated successfully:")
        click.echo(f"  - Nodes: {node_count}")
        click.echo(f"  - Edges: {edge_count}")
        click.echo(f"  - Output: {output_path}")

    except FileNotFoundError as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n✗ Unexpected error: {e}", err=True)
        sys.exit(1)


@verify.command()
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Root directory of the project (default: current directory)",
)
@click.option(
    "--test-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Test directory to scan (default: <project-root>/tests)",
)
@click.option(
    "--no-timestamp",
    is_flag=True,
    help="Exclude timestamp from metadata (for deterministic output)",
)
def rebuild(
    project_root: Path,
    test_dir: Path | None,
    no_timestamp: bool,
) -> None:
    """Rebuild verification graph from test files.

    Scans test files for @jig.verifies decorators and generates
    an NDJSON verification graph.

    Example:
        jigy verify rebuild
        jigy verify rebuild --test-dir custom_tests/
        jigy verify rebuild --no-timestamp
    """
    try:
        exit_code = verify_rebuild_command(project_root, test_dir, no_timestamp)
        sys.exit(exit_code)
    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@validate.command(name="intent")
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Root directory of the project (default: current directory)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"], case_sensitive=False),
    default="human",
    help="Output format (default: human-readable)",
)
def validate_intent_cli(project_root: Path, output_format: str) -> None:
    """Validate intent artifacts (specifications, outcomes, decorators).

    Validates human-authored artifacts before any graph generation.
    Can run without graphs existing.

    Example:
        jig validate intent
        jig validate intent --format json
    """
    exit_code = validate_intent_command(project_root, output_format)
    sys.exit(exit_code)


@validate.command(name="bricks")
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Root directory of the project (default: current directory)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"], case_sensitive=False),
    default="human",
    help="Output format (default: human-readable)",
)
def validate_bricks_cli(project_root: Path, output_format: str) -> None:
    """Validate brick definitions and partition constraints.

    Validates brick definitions against implementation graph.
    Requires implementation graph to exist.

    Example:
        jig validate bricks
        jig validate bricks --format json
    """
    exit_code = validate_bricks_command(project_root, output_format)
    sys.exit(exit_code)


@validate.command()
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Root directory of the project (default: current directory)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"], case_sensitive=False),
    default="human",
    help="Output format (default: human-readable)",
)
def full(project_root: Path, output_format: str) -> None:
    """Run full validation (intent + bricks if graph exists).

    Validates all artifacts. Runs intent validation always,
    and brick validation if implementation graph exists.

    Example:
        jig validate full
        jig validate full --format json
    """
    exit_code = validate_full_command(project_root, output_format)
    sys.exit(exit_code)


@cli.group(invoke_without_command=True)
@click.pass_context
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Root directory of the project (default: current directory)",
)
@click.option(
    "--summary",
    is_flag=True,
    help="Show only layer counts (summary mode)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed function lists",
)
def layers(ctx, project_root: Path, summary: bool, verbose: bool) -> None:
    """Visualize and manage brick layer structure.

    Shows bricks grouped by layer with their dependencies and function counts.

    Example:
        jigy layers                    # Show layer structure
        jigy layers --summary          # Show counts only
        jigy layers suggest            # Suggest layer assignments
    """
    # If no subcommand, run visualization
    if ctx.invoked_subcommand is None:
        exit_code = layers_command(project_root, summary, verbose)
        sys.exit(exit_code)


@layers.command()
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Root directory of the project (default: current directory)",
)
@click.option(
    "--apply",
    is_flag=True,
    help="Apply suggested layers to bricks.yaml",
)
def suggest(project_root: Path, apply: bool) -> None:
    """Suggest layer assignments based on dependency analysis.

    Analyzes brick dependencies and suggests appropriate layer assignments
    using topological sort. Compares suggestions with current layers.

    Example:
        jigy layers suggest              # Show suggestions
        jigy layers suggest --apply      # Apply suggestions to bricks.yaml
    """
    exit_code = suggest_layers_command(project_root, apply)
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
