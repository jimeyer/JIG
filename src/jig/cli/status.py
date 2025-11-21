# @jig C-STATUS-001 implements:S-GRAPH-001 subsystem:core interface:public
# @jig C-CLI-010 implements:S-CLI-007 subsystem:cli interface:public
"""Status command for JIG graph health monitoring."""

import sys
from dataclasses import dataclass, field
from pathlib import Path

import click

from jig.cli.formatting import (
    format_node_list,
    format_node_summary,
    format_warning,
    format_suggestion,
)
from jig.core.config import load_config
from jig.core.graph import Graph, Subsystem


# @jig C-NESTED-004 implements:S-NESTED-003 subsystem:core interface:public
def format_subsystem_tree(subsystem: Subsystem, graph: Graph, indent: str = "") -> list[str]:
    """Format subsystem hierarchy as tree.

    Args:
        subsystem: Root subsystem to format
        graph: Graph for constraint lookup
        indent: Current indentation level

    Returns:
        List of formatted lines
    """
    lines = []
    node_count = len(subsystem.get_all_nodes(recursive=True))
    lines.append(f"{indent}{subsystem.name} ({node_count} nodes)")

    # Show constraints for this subsystem
    constraints = graph.get_constraints_for_subsystem(subsystem.full_path)
    if constraints:
        lines.append(f"{indent}  └── Constraints: {', '.join(constraints)}")

    # Show child subsystems
    children = list(subsystem.subsystems.values())
    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "

        child_lines = format_subsystem_tree(child, graph, indent + extension)
        child_lines[0] = indent + connector + child_lines[0].lstrip()
        lines.extend(child_lines)

    return lines


@dataclass
class StatusData:
    """Status data for graph health metrics.

    Attributes:
        total_nodes: Total number of nodes in the graph
        total_edges: Total number of edges in the graph
        subsystem_count: Number of subsystems defined
        node_counts: Dictionary mapping node type to count
        subsystems: Dictionary mapping subsystem name to list of node IDs
        orphaned_nodes: List of node IDs without edges
        unassigned_nodes: List of node IDs without subsystem assignment
        validation_errors: List of validation error messages
    """

    total_nodes: int
    total_edges: int
    subsystem_count: int
    node_counts: dict[str, int]
    subsystems: dict[str, list[str]]
    orphaned_nodes: list[str]
    unassigned_nodes: list[str]
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
            total_edges=0,
            subsystem_count=0,
            node_counts={},
            subsystems={},
            orphaned_nodes=[],
            unassigned_nodes=[],
            validation_errors=[str(e)],
        )

    # Calculate metrics
    total_nodes = len(graph.nodes)
    total_edges = len(graph.edges)
    subsystem_count = len(graph.subsystems)
    node_counts = graph.get_node_counts_by_type()
    subsystems = graph.get_nodes_by_subsystem()
    orphaned_nodes = graph.find_orphaned_nodes()

    # Find nodes without subsystem assignment
    nodes_with_subsystem = set()
    for node_list in subsystems.values():
        nodes_with_subsystem.update(node_list)
    unassigned_nodes = [
        node_id for node_id in graph.nodes.keys()
        if node_id not in nodes_with_subsystem
    ]

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
        total_edges=total_edges,
        subsystem_count=subsystem_count,
        node_counts=node_counts,
        subsystems=subsystems,
        orphaned_nodes=orphaned_nodes,
        unassigned_nodes=unassigned_nodes,
        validation_errors=validation_errors,
    )


def format_status_output(status_data: StatusData, verbose: bool, flat: bool = False, graph: Graph | None = None) -> str:
    """Format status data for terminal output.

    Args:
        status_data: Status data to format
        verbose: Whether to show verbose output (node lists)
        flat: Whether to use flat subsystem display (backward compatible)
        graph: Graph instance (required for hierarchical view)

    Returns:
        Formatted string with colors and styling for terminal output
    """
    output = []

    # Header
    output.append(click.style("JIG Graph Status", bold=True))
    output.append("")

    # Overall health indicator
    if status_data.total_nodes == 0:
        output.append(click.style("✗ No nodes found", fg="yellow"))
        output.append("")
        output.append("Run 'jigy init' to initialize this project,")
        output.append("or 'jigy node create' to add your first node.")
        return "\n".join(output)

    # Summary line with nodes, edges, and subsystems
    health_color = "green" if len(status_data.orphaned_nodes) == 0 else "yellow"
    subsystem_text = "subsystem" if status_data.subsystem_count == 1 else "subsystems"
    summary = (
        f"✓ {status_data.total_nodes} nodes, "
        f"{status_data.total_edges} edges, "
        f"{status_data.subsystem_count} {subsystem_text}"
    )
    output.append(click.style(summary, fg=health_color))

    # Node summary
    if status_data.node_counts:
        output.append("")
        node_summary = format_node_summary(status_data.node_counts)
        # Apply styling to first line (header)
        lines = node_summary.split("\n")
        lines[0] = click.style(lines[0], bold=True)
        output.extend(lines)

    # Subsystems
    if status_data.subsystems or (graph and graph.subsystems):
        output.append("")
        output.append(click.style("Subsystems:", bold=True))

        if flat or not graph:
            # Flat view (backward compatible)
            for subsystem_name, nodes in sorted(status_data.subsystems.items()):
                output.append(f"  {subsystem_name}: {len(nodes)} nodes")
                if verbose:
                    for node_id in sorted(nodes):
                        output.append(f"    - {node_id}")
        else:
            # Hierarchical tree view
            for subsystem in sorted(graph.subsystems.values(), key=lambda s: s.name):
                tree_lines = format_subsystem_tree(subsystem, graph, "  ")
                output.extend(tree_lines)
                if verbose:
                    # Show individual nodes in verbose mode
                    all_nodes = subsystem.get_all_nodes(recursive=True)
                    for node_id in sorted(all_nodes):
                        if node_id in graph.nodes:
                            output.append(f"    - {node_id}")

    # Warnings section
    warnings = []

    # Orphaned nodes warning (nodes without edges)
    if status_data.orphaned_nodes:
        orphaned_warning = format_warning("Orphaned nodes", status_data.orphaned_nodes)
        warnings.append(click.style(orphaned_warning, fg="yellow"))

    # Unassigned nodes warning (nodes missing subsystem)
    if status_data.unassigned_nodes:
        unassigned_warning = format_warning("Unassigned nodes", status_data.unassigned_nodes)
        warnings.append(click.style(unassigned_warning, fg="yellow"))

    # Validation errors
    for error in status_data.validation_errors:
        warnings.append(click.style("⚠ ", fg="yellow") + error)

    if warnings:
        output.append("")
        output.append(click.style("Warnings:", fg="yellow", bold=True))
        for warning in warnings:
            output.append(f"  {warning}")

    # Suggestions section
    suggestions = []

    # Suggest adding relationships for orphaned nodes
    if status_data.orphaned_nodes:
        suggestion_text = (
            f"Add relationships to {len(status_data.orphaned_nodes)} orphaned nodes "
            "(use 'implements:', 'verifies:', or 'depends_on:')"
        )
        suggestions.append(format_suggestion(suggestion_text))

    # Suggest assigning subsystems if nodes lack them
    if status_data.unassigned_nodes:
        suggestion_text = (
            f"Assign {len(status_data.unassigned_nodes)} nodes to subsystems "
            "(add 'subsystem: <name>' to frontmatter)"
        )
        suggestions.append(format_suggestion(suggestion_text))

    # Suggest creating graph-index.yaml if missing
    if "graph-index.yaml not found" in str(status_data.validation_errors):
        suggestions.append(
            format_suggestion("Create graph-index.yaml to define relationships and subsystems")
        )

    # Suggest running validate
    if suggestions:
        suggestions.append(format_suggestion("Run 'jigy validate' to check graph consistency"))

    if suggestions:
        output.append("")
        output.append(click.style("Suggestions:", fg="cyan", bold=True))
        for suggestion in suggestions:
            output.append(f"  {suggestion}")
    else:
        # Graph is healthy - show success message
        output.append("")
        output.append(click.style("✓ Graph looks healthy!", fg="green"))

    return "\n".join(output)


@click.command()
@click.option("--verbose", is_flag=True, help="Show detailed statistics")
@click.option("--flat", is_flag=True, help="Show flat subsystem view (backward compatible)")
def status(verbose: bool, flat: bool) -> None:
    """Show JIG graph status and health.

    Displays:
    - Total node count
    - Node counts by type (outcome, specification, test, constraint)
    - Subsystem breakdown (hierarchical tree by default, --flat for legacy view)
    - Orphaned nodes (nodes without relationships)
    - Actionable suggestions for improving graph health

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

    # Load graph for hierarchical view (if not flat)
    graph = None
    if not flat:
        try:
            graph = Graph.load_from_dir(config.intent_dir)
        except (FileNotFoundError, ValueError):
            # Fall back to flat view if graph can't be loaded
            flat = True

    # Format and display status
    output = format_status_output(status_data, verbose, flat, graph)
    click.echo(output)
