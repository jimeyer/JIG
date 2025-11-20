# @jig C-STATUS-001 implements:S-GRAPH-001 subsystem:core interface:public
"""Status command for JIG graph health monitoring."""

import sys
from dataclasses import dataclass, field
from pathlib import Path

import click

from jig.core.config import load_config
from jig.core.graph import Graph


@dataclass
class StatusData:
    """Status data for graph health metrics.

    Attributes:
        total_nodes: Total number of nodes in the graph
        node_counts: Dictionary mapping node type to count
        subsystems: Dictionary mapping subsystem name to list of node IDs
        orphaned_nodes: List of node IDs without edges
        validation_errors: List of validation error messages
    """

    total_nodes: int
    node_counts: dict[str, int]
    subsystems: dict[str, list[str]]
    orphaned_nodes: list[str]
    validation_errors: list[str] = field(default_factory=list)


def calculate_status(intent_dir: Path) -> StatusData:
    """Calculate graph health metrics.

    Args:
        intent_dir: Path to jig/ directory containing OSTC nodes

    Returns:
        StatusData with calculated metrics

    Raises:
        FileNotFoundError: If intent_dir doesn't exist
        ValueError: If graph cannot be loaded

    Example:
        >>> status = calculate_status(Path("jig/"))
        >>> print(status.total_nodes)
        15
    """
    # Load graph from directory
    try:
        graph = Graph.load_from_dir(intent_dir)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Intent directory not found: {intent_dir}\n"
            f"Have you run 'jigy init' to initialize this project?"
        )
    except ValueError as e:
        # Graph loading failed due to parse errors
        # Return status with validation errors
        return StatusData(
            total_nodes=0,
            node_counts={},
            subsystems={},
            orphaned_nodes=[],
            validation_errors=[str(e)],
        )

    # Calculate metrics
    total_nodes = len(graph.nodes)
    node_counts = graph.get_node_counts_by_type()
    subsystems = graph.get_nodes_by_subsystem()
    orphaned_nodes = graph.find_orphaned_nodes()

    # Check for missing graph-index.yaml
    validation_errors = []
    graph_index_path = intent_dir / "graph-index.yaml"
    if not graph_index_path.exists() and total_nodes > 0:
        validation_errors.append(
            f"Warning: {graph_index_path} not found. "
            "Run 'jigy validate' to generate it."
        )

    return StatusData(
        total_nodes=total_nodes,
        node_counts=node_counts,
        subsystems=subsystems,
        orphaned_nodes=orphaned_nodes,
        validation_errors=validation_errors,
    )


@click.command()
@click.option("--verbose", is_flag=True, help="Show detailed statistics")
def status(verbose: bool) -> None:
    """Show JIG graph status and health.

    Displays:
    - Total node count
    - Node counts by type (outcome, specification, test, constraint)
    - Subsystem breakdown
    - Orphaned nodes (nodes without relationships)
    - Validation warnings

    Exit codes:
    - 0: Success
    - 3: Directory not initialized (jig/ doesn't exist)
    """
    config = load_config()

    try:
        status_data = calculate_status(config.intent_dir)
    except FileNotFoundError as e:
        click.echo(click.style("✗ Error: ", fg="red") + str(e))
        sys.exit(3)

    # Display status (formatting will be implemented in WU3)
    # For now, just show basic output
    click.echo(click.style("JIG Graph Status", bold=True))
    click.echo("")
    click.echo(f"Total nodes: {status_data.total_nodes}")

    if status_data.node_counts:
        click.echo("")
        click.echo(click.style("Node counts by type:", bold=True))
        for node_type, count in sorted(status_data.node_counts.items()):
            click.echo(f"  {node_type}: {count}")

    if status_data.subsystems:
        click.echo("")
        click.echo(click.style("Subsystems:", bold=True))
        for subsystem_name, nodes in sorted(status_data.subsystems.items()):
            click.echo(f"  {subsystem_name}: {len(nodes)} nodes")
            if verbose:
                for node_id in sorted(nodes):
                    click.echo(f"    - {node_id}")

    if status_data.orphaned_nodes:
        click.echo("")
        click.echo(click.style("⚠ Orphaned nodes:", fg="yellow"))
        for node_id in status_data.orphaned_nodes:
            click.echo(f"  - {node_id}")

    if status_data.validation_errors:
        click.echo("")
        for error in status_data.validation_errors:
            click.echo(click.style("⚠ ", fg="yellow") + error)
