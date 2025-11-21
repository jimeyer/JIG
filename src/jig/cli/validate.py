# @jig C-CLI-004 implements:S-JIG-002 subsystem:core interface:public
"""Validate OSTC nodes and graph consistency."""

import sys
from pathlib import Path

import click

from jig.core.config import load_config
from jig.core.validator import validate_graph


@click.command()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed validation information",
)
def validate(verbose: bool) -> None:
    """Validate OSTC nodes and graph consistency.

    Checks all nodes in the JIG intent graph for:
    - Required fields (id, type, title)
    - Valid ID format and type values
    - ID prefix matches type
    - No duplicate node IDs
    - Valid graph index references

    Exit codes:
        0: All nodes valid (no errors)
        1: Validation errors found
        3: JIG not initialized

    Examples:
        jigy validate              # Validate with standard output
        jigy validate --verbose    # Show detailed information
    """
    # Load config
    try:
        config = load_config()
    except Exception as e:
        click.echo(click.style("✗ Error loading config:", fg="red", bold=True), err=True)
        click.echo(f"  {e}", err=True)
        click.echo("\nHave you run 'jigy init' yet?", err=True)
        sys.exit(3)

    # Check if JIG initialized
    if not config.intent_dir.exists():
        click.echo(
            click.style(
                f"✗ JIG not initialized (directory {config.intent_dir} not found)",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        click.echo("Run 'jigy init' first to initialize JIG structure", err=True)
        sys.exit(3)

    # Print header
    click.echo(click.style("Validating JIG graph...", bold=True))

    # Validate graph
    result = validate_graph(config.intent_dir)

    # Count nodes by directory
    node_counts = _count_nodes(config.intent_dir)
    total_nodes = sum(node_counts.values())

    # Print summary immediately after header
    if result.valid:
        click.echo(
            click.style("✓ ", fg="green", bold=True)
            + click.style(f"All {total_nodes} nodes valid", bold=True)
        )
    else:
        error_count = len(result.errors)
        click.echo(
            click.style("✗ ", fg="red", bold=True)
            + click.style(
                f"Validation failed: {error_count} error{'s' if error_count != 1 else ''}",
                fg="red",
                bold=True,
            )
        )

    # Print per-file validation results if verbose
    if verbose:
        click.echo()
        _print_verbose_results(config.intent_dir, result)

    # Print errors
    if result.errors:
        click.echo()
        click.echo(click.style("Errors found:", fg="red", bold=True))
        for error in result.errors:
            click.echo(click.style("  ✗ ", fg="red") + error)

    # Always print warnings if there are any
    if result.warnings:
        click.echo()
        click.echo(click.style("Warnings:", fg="yellow", bold=True))
        for warning in result.warnings:
            click.echo(click.style("  ⚠ ", fg="yellow") + warning)

    # Exit with appropriate code
    sys.exit(0 if result.valid else 1)


def _count_nodes(intent_dir: Path) -> dict[str, int]:
    """Count nodes in each directory.

    Args:
        intent_dir: Path to intent directory

    Returns:
        Dictionary mapping directory name to node count
    """
    counts = {}
    for node_type in ["outcomes", "specifications", "tests", "constraints"]:
        type_dir = intent_dir / node_type
        if type_dir.exists():
            counts[node_type] = len(list(type_dir.glob("*.md")))
        else:
            counts[node_type] = 0
    return counts


def _print_verbose_results(intent_dir: Path, result: object) -> None:
    """Print verbose per-file validation results.

    Args:
        intent_dir: Path to intent directory
        result: ValidationResult (not typed to avoid circular import)
    """
    # Import here to avoid issues
    from jig.core.validator import validate_node_file

    click.echo(click.style("Node files:", bold=True))

    for node_type in ["outcomes", "specifications", "tests", "constraints"]:
        type_dir = intent_dir / node_type
        if not type_dir.exists():
            continue

        node_files = sorted(type_dir.glob("*.md"))
        if not node_files:
            continue

        click.echo(f"\n  {node_type}:")
        for node_file in node_files:
            node_result = validate_node_file(node_file)
            if node_result.valid:
                click.echo(
                    "    "
                    + click.style("✓ ", fg="green")
                    + str(node_file.relative_to(intent_dir.parent))
                )
            else:
                click.echo(
                    "    "
                    + click.style("✗ ", fg="red")
                    + str(node_file.relative_to(intent_dir.parent))
                )
                for error in node_result.errors:
                    click.echo(f"      - {error}")
