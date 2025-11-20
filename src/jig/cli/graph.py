# @jig C-GRAPH-004 implements:S-GRAPH-003 subsystem:core interface:public
"""Graph commands for querying and navigating the Intent Graph."""

import sys

import click

from jig.core.config import load_config
from jig.core.graph import Graph


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
