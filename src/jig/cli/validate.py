# @jig C-CLI-004 implements:S-JIG-002 subsystem:core interface:public
# @jig C-CLI-011 implements:S-CLI-008 subsystem:cli interface:public
"""Validate OSTC nodes and graph consistency."""

import re
import sys
from pathlib import Path

import click

from jig.cli.formatting import (
    format_node_summary,
    format_warning,
    format_suggestion,
)
from jig.core.config import load_config
from jig.core.validator import validate_graph


def _parse_and_aggregate_warnings(warnings: list[str]) -> dict:
    """Parse and aggregate validation warnings for consistent formatting.

    Args:
        warnings: List of warning strings from validator

    Returns:
        Dictionary with aggregated warnings:
        {
            'unassigned_nodes': [node_ids],
            'missing_created_date': [node_ids],
            'orphaned_nodes': [node_ids],
            'other': [other_warnings]
        }
    """
    aggregated = {
        'unassigned_nodes': [],
        'missing_created_date': [],
        'orphaned_nodes': [],
        'other': []
    }

    for warning in warnings:
        # Parse "Node X-YYY-NNN: subsystem not specified"
        match = re.match(r'Node ([A-Z]+-[A-Z]+-\d+): subsystem not specified', warning)
        if match:
            aggregated['unassigned_nodes'].append(match.group(1))
            continue

        # Parse "Node X-YYY-NNN: created date not specified"
        match = re.match(r'Node ([A-Z]+-[A-Z]+-\d+): created date not specified', warning)
        if match:
            aggregated['missing_created_date'].append(match.group(1))
            continue

        # Parse "Nodes not referenced in graph index: ..."
        if warning.startswith("Nodes not referenced in graph index:"):
            # Extract comma-separated list of node IDs
            node_list_str = warning.split(":", 1)[1].strip()
            aggregated['orphaned_nodes'] = [n.strip() for n in node_list_str.split(",")]
            continue

        # Other warnings pass through
        aggregated['other'].append(warning)

    return aggregated


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

    # Print node summary (consistent with status command)
    if total_nodes > 0:
        click.echo()
        # Convert directory counts to type counts (outcomes -> outcome, etc.)
        type_counts = {
            k.rstrip('s'): v for k, v in node_counts.items() if v > 0
        }
        node_summary = format_node_summary(type_counts)
        # Apply styling to first line (header)
        lines = node_summary.split("\n")
        lines[0] = click.style(lines[0], bold=True)
        for line in lines:
            click.echo(line)

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

    # Parse and aggregate warnings for consistent formatting
    if result.warnings:
        aggregated = _parse_and_aggregate_warnings(result.warnings)
        formatted_warnings = []

        # Unassigned nodes (nodes missing subsystem)
        if aggregated['unassigned_nodes']:
            warning = format_warning("Unassigned nodes", aggregated['unassigned_nodes'])
            formatted_warnings.append(click.style(warning, fg="yellow"))

        # Orphaned nodes (nodes not referenced in graph index)
        if aggregated['orphaned_nodes']:
            warning = format_warning("Orphaned nodes", aggregated['orphaned_nodes'])
            formatted_warnings.append(click.style(warning, fg="yellow"))

        # Missing created date (less critical)
        if aggregated['missing_created_date']:
            warning = format_warning("Nodes missing created date", aggregated['missing_created_date'])
            formatted_warnings.append(click.style(warning, fg="yellow"))

        # Other warnings pass through
        for warning in aggregated['other']:
            formatted_warnings.append(click.style("⚠ ", fg="yellow") + warning)

        # Print warnings section
        if formatted_warnings:
            click.echo()
            click.echo(click.style("Warnings:", fg="yellow", bold=True))
            for warning in formatted_warnings:
                click.echo(f"  {warning}")

    # Print suggestions section
    suggestions = []

    # Suggest running status for detailed metrics
    if result.warnings or result.errors:
        suggestions.append(format_suggestion("Run 'jigy status' for detailed graph health metrics"))

    # Suggest fixing unassigned nodes
    if result.warnings:
        aggregated = _parse_and_aggregate_warnings(result.warnings)
        if aggregated['unassigned_nodes']:
            suggestions.append(
                format_suggestion(
                    f"Add 'subsystem: <name>' to frontmatter for {len(aggregated['unassigned_nodes'])} unassigned nodes"
                )
            )

    if suggestions:
        click.echo()
        click.echo(click.style("Suggestions:", fg="cyan", bold=True))
        for suggestion in suggestions:
            click.echo(f"  {suggestion}")

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
