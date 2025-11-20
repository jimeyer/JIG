# @jig C-CLI-003 implements:S-JIG-002 subsystem:core interface:public
"""Create OSTC nodes from templates."""

import re
import sys
from datetime import datetime
from pathlib import Path

import click
import yaml

from jig.core.config import load_config
from jig.utils.io import ensure_dir, write_file


@click.group()
def node() -> None:
    """Manage OSTC nodes (create, update, delete)."""
    pass


@node.command()
@click.option(
    "--type",
    "node_type",
    required=True,
    type=click.Choice(["outcome", "specification", "constraint"]),
    help="Node type (O/S/X only; T/C use @jig annotations)",
)
@click.option(
    "--id",
    "node_id",
    required=True,
    help="Node ID (e.g., O-JIG-001, S-TEST-002)",
)
@click.option(
    "--title",
    required=True,
    help="Human-readable title for the node",
)
@click.option(
    "--subsystem",
    default=None,
    help="Subsystem name (optional)",
)
def create(node_type: str, node_id: str, title: str, subsystem: str | None) -> None:
    """Create a new OSTC node from template.

    Creates a new node file from the appropriate template, substituting
    placeholders with provided values. Updates the graph index to include
    the new node.

    Examples:
        jigy node create --type outcome --id O-PROJ-001 --title "Fast operations"
        jigy node create --type specification --id S-API-001 --title "REST API spec" --subsystem api
    """
    # Validate ID format
    if not _validate_id_format(node_id):
        click.echo(
            f"Error: Invalid ID format '{node_id}'",
            err=True,
        )
        click.echo(
            "ID must match pattern: [OSC]-[A-Z0-9]+-[0-9]{3}",
            err=True,
        )
        click.echo("Examples: O-JIG-001, S-TEST-002, C-PERF-001", err=True)
        sys.exit(1)

    # Validate ID prefix matches type
    if not _validate_id_prefix(node_id, node_type):
        prefix = node_id.split("-")[0]
        expected = _get_type_prefix(node_type)
        click.echo(
            f"Error: ID prefix '{prefix}' doesn't match type '{node_type}'",
            err=True,
        )
        click.echo(f"Expected ID to start with '{expected}-' for type '{node_type}'", err=True)
        sys.exit(1)

    # Load config
    try:
        config = load_config()
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        click.echo("Have you run 'jigy init' yet?", err=True)
        sys.exit(3)

    # Check if JIG initialized
    if not config.intent_dir.exists():
        click.echo(
            f"Error: JIG not initialized (directory {config.intent_dir} not found)",
            err=True,
        )
        click.echo("Run 'jigy init' first to initialize JIG structure", err=True)
        sys.exit(3)

    # Determine output directory and file path
    node_dir = config.intent_dir / f"{node_type}s"
    node_file = node_dir / f"{node_id}.md"

    # Check if node already exists
    if node_file.exists():
        click.echo(f"Error: Node {node_id} already exists at {node_file}", err=True)
        sys.exit(2)

    # Load template - try config location first, then package location
    template_file = config.templates_dir / f"{node_type}_template.md"

    if not template_file.exists():
        # Try finding templates relative to package (for development/installation)
        import jig
        package_dir = Path(jig.__file__).parent.parent.parent
        template_file = package_dir / "templates" / f"{node_type}_template.md"

    if not template_file.exists():
        click.echo(f"Error: Template not found: {node_type}_template.md", err=True)
        click.echo("Searched in:", err=True)
        click.echo(f"  - {config.templates_dir / f'{node_type}_template.md'}", err=True)
        click.echo(f"  - {template_file}", err=True)
        sys.exit(1)

    try:
        template_content = template_file.read_text()
    except Exception as e:
        click.echo(f"Error reading template: {e}", err=True)
        sys.exit(1)

    # Substitute placeholders
    node_content = _substitute_placeholders(
        template_content,
        node_id=node_id,
        title=title,
        subsystem=subsystem or "null",
        date=datetime.now().strftime("%Y-%m-%d"),
    )

    # Create node file
    try:
        ensure_dir(node_dir)
        write_file(node_file, node_content)
    except Exception as e:
        click.echo(f"Error writing node file: {e}", err=True)
        sys.exit(1)

    # Update graph-index.yaml
    try:
        _update_graph_index(config.graph_index_file, node_id, node_type)
    except Exception as e:
        click.echo(f"Warning: Failed to update graph index: {e}", err=True)
        click.echo(f"Node file created at {node_file}, but graph index not updated", err=True)

    # Success message
    click.echo(f"✓ Created {node_type} node: {node_id}")
    click.echo(f"  File: {node_file}")
    click.echo(f"  Title: {title}")
    if subsystem and subsystem != "null":
        click.echo(f"  Subsystem: {subsystem}")
    click.echo("\nNext steps:")
    click.echo(f"  1. Edit the node: {node_file}")
    click.echo("  2. Validate: jigy validate")

    sys.exit(0)


def _validate_id_format(node_id: str) -> bool:
    """Validate node ID matches required format.

    Args:
        node_id: Node ID to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r"^[OSC]-[A-Z0-9]+-\d{3}$"
    return re.match(pattern, node_id) is not None


def _validate_id_prefix(node_id: str, node_type: str) -> bool:
    """Validate node ID prefix matches node type.

    Args:
        node_id: Node ID to validate
        node_type: Type of node (outcome, specification, constraint)

    Returns:
        True if prefix matches type, False otherwise
    """
    prefix = node_id.split("-")[0]
    expected_prefix = _get_type_prefix(node_type)
    return prefix == expected_prefix


def _get_type_prefix(node_type: str) -> str:
    """Get expected ID prefix for node type.

    Args:
        node_type: Type of node

    Returns:
        Single-letter prefix (O, S, or C)
    """
    prefix_map = {
        "outcome": "O",
        "specification": "S",
        "constraint": "C",
    }
    return prefix_map[node_type]


def _substitute_placeholders(
    content: str,
    node_id: str,
    title: str,
    subsystem: str,
    date: str,
) -> str:
    """Substitute template placeholders with actual values.

    Args:
        content: Template content with placeholders
        node_id: Node ID
        title: Node title
        subsystem: Subsystem name
        date: Creation date (ISO format)

    Returns:
        Content with placeholders substituted
    """
    return (
        content.replace("{id}", node_id)
        .replace("{title}", title)
        .replace("{subsystem}", subsystem)
        .replace("{date}", date)
    )


def _update_graph_index(graph_file: Path, node_id: str, node_type: str) -> None:
    """Update graph-index.yaml with new node entry.

    Args:
        graph_file: Path to graph-index.yaml
        node_id: ID of new node
        node_type: Type of new node
    """
    # Load existing graph index
    if graph_file.exists():
        graph_data = yaml.safe_load(graph_file.read_text())
    else:
        graph_data = {"version": "1.0", "nodes": []}

    # Add new node entry
    if "nodes" not in graph_data:
        graph_data["nodes"] = []

    graph_data["nodes"].append({"id": node_id, "type": node_type})

    # Write updated graph index
    write_file(graph_file, yaml.dump(graph_data, sort_keys=False))
