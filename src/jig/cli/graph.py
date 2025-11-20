# @jig C-GRAPH-004 implements:S-GRAPH-003 subsystem:core interface:public
"""Graph commands for querying and navigating the Intent Graph."""

import sys

import click

from jig.core.config import load_config
from jig.core.graph import Graph


def format_dependency_tree(
    node_id: str, graph: Graph, visited: set[str], prefix: str = ""
) -> list[str]:
    """Recursively format dependency tree (what this node depends on).

    Args:
        node_id: Current node ID to format
        graph: Graph instance
        visited: Set of visited node IDs for cycle detection
        prefix: Current indentation prefix

    Returns:
        List of formatted tree lines
    """
    if node_id in visited:
        return [f"{prefix}↻ {node_id} (cycle)"]

    visited.add(node_id)
    lines = [f"{prefix}{node_id}"]

    deps = graph.get_dependencies(node_id)
    for i, dep in enumerate(deps):
        is_last = i == len(deps) - 1
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "
        subtree = format_dependency_tree(dep, graph, visited.copy(), prefix + extension)
        # Replace the prefix on the first line with the connector
        subtree[0] = prefix + connector + subtree[0][len(prefix + extension) :]
        lines.extend(subtree)

    return lines


def format_impact_tree(
    node_id: str, graph: Graph, visited: set[str], prefix: str = ""
) -> list[str]:
    """Recursively format impact tree (what depends on this node).

    Args:
        node_id: Current node ID to format
        graph: Graph instance
        visited: Set of visited node IDs for cycle detection
        prefix: Current indentation prefix

    Returns:
        List of formatted tree lines
    """
    if node_id in visited:
        return [f"{prefix}↻ {node_id} (cycle)"]

    visited.add(node_id)
    lines = [f"{prefix}{node_id}"]

    dependents = graph.get_dependents(node_id)
    for i, dependent in enumerate(dependents):
        is_last = i == len(dependents) - 1
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "
        subtree = format_impact_tree(
            dependent, graph, visited.copy(), prefix + extension
        )
        # Replace the prefix on the first line with the connector
        subtree[0] = prefix + connector + subtree[0][len(prefix + extension) :]
        lines.extend(subtree)

    return lines


@click.group()
def graph() -> None:
    """Query and navigate the Intent Graph."""
    pass


@graph.command()
@click.argument("node_id")
def show(node_id: str) -> None:
    """Show node details and relationships.

    Display full information about a node including its metadata,
    body content (first 10 lines), dependencies, and dependents.

    Examples:
        jigy graph show O-JIG-001
        jigy graph show S-GRAPH-001
    """
    config = load_config()

    try:
        g = Graph.load_from_dir(config.intent_dir)
    except FileNotFoundError:
        click.echo(click.style("Error: Intent directory not found", fg="red"))
        click.echo("Have you run 'jigy init' to initialize this project?")
        sys.exit(3)

    if node_id not in g.nodes:
        click.echo(click.style(f"Error: Node {node_id} not found", fg="red"))
        sys.exit(1)

    node = g.nodes[node_id]

    # Display node metadata
    click.echo(click.style(f"{node.id}", bold=True))
    click.echo(f"Type: {node.type}")
    click.echo(f"Title: {node.title}")
    if node.subsystem:
        click.echo(f"Subsystem: {node.subsystem}")
    if node.status:
        click.echo(f"Status: {node.status}")

    # Display body (first 10 lines)
    click.echo("")
    lines = node.body.split("\n")
    display_lines = lines[:10]
    click.echo("\n".join(display_lines))
    if len(lines) > 10:
        click.echo(click.style("... (use 'cat' to see full content)", fg="cyan"))

    # Display dependencies
    click.echo("")
    click.echo(click.style("Dependencies:", fg="cyan"))
    deps = g.get_dependencies(node_id)
    if deps:
        for dep in deps:
            click.echo(f"  → {dep}")
    else:
        click.echo("  (none)")

    # Display dependents
    click.echo("")
    click.echo(click.style("Dependents:", fg="cyan"))
    dependents = g.get_dependents(node_id)
    if dependents:
        for dependent in dependents:
            click.echo(f"  ← {dependent}")
    else:
        click.echo("  (none)")


@graph.command()
@click.argument("node_id")
def deps(node_id: str) -> None:
    """Show dependency tree for a node.

    Display all nodes that this node depends on, recursively.
    Shows transitive dependencies in tree format with proper indentation.

    Examples:
        jigy graph deps S-JIG-001
        jigy graph deps T-GRAPH-001
    """
    config = load_config()

    try:
        g = Graph.load_from_dir(config.intent_dir)
    except FileNotFoundError:
        click.echo(click.style("Error: Intent directory not found", fg="red"))
        click.echo("Have you run 'jigy init' to initialize this project?")
        sys.exit(3)

    if node_id not in g.nodes:
        click.echo(click.style(f"Error: Node {node_id} not found", fg="red"))
        sys.exit(1)

    click.echo(click.style(f"Dependency tree for {node_id}:", bold=True))
    click.echo("")
    tree = format_dependency_tree(node_id, g, set())
    click.echo("\n".join(tree))


@graph.command()
@click.argument("node_id")
def impact(node_id: str) -> None:
    """Show impact analysis (what depends on this node).

    Display all nodes that depend on this node, recursively.
    Shows transitive dependents in tree format with proper indentation.

    Examples:
        jigy graph impact O-JIG-001
        jigy graph impact S-GRAPH-001
    """
    config = load_config()

    try:
        g = Graph.load_from_dir(config.intent_dir)
    except FileNotFoundError:
        click.echo(click.style("Error: Intent directory not found", fg="red"))
        click.echo("Have you run 'jigy init' to initialize this project?")
        sys.exit(3)

    if node_id not in g.nodes:
        click.echo(click.style(f"Error: Node {node_id} not found", fg="red"))
        sys.exit(1)

    click.echo(click.style(f"Impact analysis for {node_id}:", bold=True))
    click.echo("")
    tree = format_impact_tree(node_id, g, set())
    click.echo("\n".join(tree))
