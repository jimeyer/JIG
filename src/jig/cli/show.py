"""Show CLI commands for displaying JIG structure."""

import json
from collections import defaultdict
from pathlib import Path

import click
import yaml

import jig
from jig.cli.discovery import find_project_root


@jig.implements("S-060")
def show_overview_command(project_root: Path) -> int:
    """Display bricks + layers overview.

    Args:
        project_root: Root directory of the project.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    bricks_file = project_root / "jig" / "bricks.yaml"
    impl_graph = project_root / "jig" / "generated" / "implementation-graph.ndjson"

    if not bricks_file.exists():
        click.echo("No bricks.yaml found.")
        return 0

    # Load bricks
    try:
        with bricks_file.open() as f:
            bricks_data = yaml.safe_load(f)
            if isinstance(bricks_data, dict) and "bricks" in bricks_data:
                bricks = bricks_data["bricks"]
            elif isinstance(bricks_data, list):
                bricks = bricks_data
            else:
                bricks = []
    except Exception as e:
        click.echo(f"Error loading bricks: {e}", err=True)
        return 1

    # Group by layer
    layers_dict = defaultdict(list)
    for brick in bricks:
        layer = brick.get("layer", 0)
        layers_dict[layer].append(brick)

    # Display overview
    click.echo("JIG Structure Overview")
    click.echo("=" * 40)
    click.echo()

    # Bricks summary
    click.echo(f"Bricks: {len(bricks)} total")
    for layer in sorted(layers_dict.keys()):
        layer_bricks = layers_dict[layer]
        brick_names = [b.get("id", "?") for b in layer_bricks]
        click.echo(f"  Layer {layer}: {', '.join(brick_names)}")

    click.echo()

    # Layers summary
    click.echo(f"Layers: {len(layers_dict)} total")
    for layer in sorted(layers_dict.keys()):
        layer_name = _get_layer_name(layer)
        count = len(layers_dict[layer])
        click.echo(f"  {layer}: {layer_name} ({count} bricks)")

    return 0


@jig.implements("S-060")
def show_layers_command(project_root: Path) -> int:
    """Display layer hierarchy.

    Args:
        project_root: Root directory of the project.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    bricks_file = project_root / "jig" / "bricks.yaml"
    impl_graph = project_root / "jig" / "generated" / "implementation-graph.ndjson"

    if not bricks_file.exists():
        click.echo("No bricks.yaml found.")
        return 0

    # Load bricks
    try:
        with bricks_file.open() as f:
            bricks_data = yaml.safe_load(f)
            if isinstance(bricks_data, dict) and "bricks" in bricks_data:
                bricks = bricks_data["bricks"]
            elif isinstance(bricks_data, list):
                bricks = bricks_data
            else:
                bricks = []
    except Exception as e:
        click.echo(f"Error loading bricks: {e}", err=True)
        return 1

    # Load impl graph for dependency info
    brick_dependencies = defaultdict(set)
    if impl_graph.exists():
        try:
            # Build unit to brick mapping
            unit_to_brick = {}
            for brick in bricks:
                brick_id = brick.get("id")
                for unit_id in brick.get("units", []):
                    unit_to_brick[unit_id] = brick_id

            # Read edges
            with impl_graph.open() as f:
                for line in f:
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    if obj.get("type") in ["calls", "imports", "inherits"]:
                        source = obj.get("source")
                        target = obj.get("target")
                        if source and target:
                            source_brick = unit_to_brick.get(source)
                            target_brick = unit_to_brick.get(target)
                            if source_brick and target_brick and source_brick != target_brick:
                                brick_dependencies[source_brick].add(target_brick)
        except Exception:
            pass  # Continue without dependency info

    # Group by layer
    layers_dict = defaultdict(list)
    for brick in bricks:
        layer = brick.get("layer", 0)
        layers_dict[layer].append(brick)

    # Display layer hierarchy
    click.echo("Layer Hierarchy")
    click.echo("=" * 40)
    click.echo()

    for layer in sorted(layers_dict.keys(), reverse=True):
        layer_name = _get_layer_name(layer)
        layer_bricks = layers_dict[layer]

        click.echo(f"Layer {layer}: {layer_name}")
        click.echo("-" * 40)

        for brick in layer_bricks:
            brick_id = brick.get("id")
            brick_name = brick.get("name", brick_id)
            click.echo(f"  {brick_id}: {brick_name}")

            # Show dependencies (downward arrows)
            deps = sorted(brick_dependencies.get(brick_id, []))
            if deps:
                click.echo(f"    ↓ {', '.join(deps)}")

        click.echo()

    return 0


@jig.implements("S-060")
def show_bricks_command(project_root: Path) -> int:
    """Display brick details.

    Args:
        project_root: Root directory of the project.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    bricks_file = project_root / "jig" / "bricks.yaml"
    impl_graph = project_root / "jig" / "generated" / "implementation-graph.ndjson"

    if not bricks_file.exists():
        click.echo("No bricks.yaml found.")
        return 0

    # Load bricks
    try:
        with bricks_file.open() as f:
            bricks_data = yaml.safe_load(f)
            if isinstance(bricks_data, dict) and "bricks" in bricks_data:
                bricks = bricks_data["bricks"]
            elif isinstance(bricks_data, list):
                bricks = bricks_data
            else:
                bricks = []
    except Exception as e:
        click.echo(f"Error loading bricks: {e}", err=True)
        return 1

    # Load impl graph for unit counts
    nodes = {}
    if impl_graph.exists():
        try:
            with impl_graph.open() as f:
                for line in f:
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    if obj.get("type") in ["function", "class", "module"]:
                        nodes[obj["id"]] = obj
        except Exception:
            pass

    # Display brick details
    click.echo("Brick Details")
    click.echo("=" * 40)
    click.echo()

    for brick in bricks:
        brick_id = brick.get("id")
        brick_name = brick.get("name", brick_id)
        layer = brick.get("layer", "?")
        units = brick.get("units", [])

        click.echo(f"{brick_id}")
        click.echo(f"  Name: {brick_name}")
        click.echo(f"  Layer: {layer}")

        # Count unit types
        module_count = sum(1 for u in units if u.startswith("M-"))
        class_count = sum(1 for u in units if u.startswith("C-"))
        function_count = sum(1 for u in units if u.startswith("F-"))

        click.echo(f"  Units: {len(units)} ({module_count} modules, {class_count} classes, {function_count} functions)")

        # Show first few units
        if units:
            shown = units[:3]
            click.echo(f"    - " + "\n    - ".join(shown))
            if len(units) > 3:
                click.echo(f"    ... and {len(units) - 3} more")

        click.echo()

    return 0


def _get_layer_name(layer: int) -> str:
    """Get descriptive name for layer."""
    if layer == 0:
        return "Foundation"
    elif layer == 1:
        return "Core Logic"
    elif layer == 2:
        return "Interface"
    else:
        return f"Layer {layer}"
