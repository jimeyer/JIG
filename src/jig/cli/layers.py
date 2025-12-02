"""
Layers CLI commands for brick layer visualization and management.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import click
import yaml

import jig


@jig.implements("S-040")
def layers_command(project_root: Path, summary: bool = False, verbose: bool = False) -> int:
    """
    Visualize brick layer structure.

    Returns exit code: 0 (success), 1 (error).
    """
    bricks_file = project_root / "jig" / "bricks.yaml"
    impl_graph = project_root / "jig" / "generated" / "implementation-graph.ndjson"

    # Check if files exist
    if not impl_graph.exists():
        click.echo(f"✗ Implementation graph not found: {impl_graph}")
        click.echo("Run 'jigy impl rebuild' first to generate the implementation graph.")
        return 1

    if not bricks_file.exists():
        click.echo(f"✗ Bricks file not found: {bricks_file}")
        return 1

    # Load bricks
    try:
        with bricks_file.open() as f:
            bricks_data = yaml.safe_load(f)
            if not bricks_data:
                bricks = []
            elif isinstance(bricks_data, dict) and "bricks" in bricks_data:
                # Handle format: { bricks: [...] }
                bricks = bricks_data["bricks"]
            elif isinstance(bricks_data, list):
                # Handle format: [...]
                bricks = bricks_data
            else:
                click.echo(f"✗ Invalid bricks file format")
                return 1
    except Exception as e:
        click.echo(f"✗ Error loading bricks file: {e}")
        return 1

    # Load implementation graph
    try:
        nodes = {}
        edges = []
        with impl_graph.open() as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                if "type" in obj:
                    if obj["type"] in ["function", "class", "module"]:
                        nodes[obj["id"]] = obj
                    elif obj["type"] in ["calls", "imports", "inherits"]:
                        edges.append(obj)
    except Exception as e:
        click.echo(f"✗ Error loading implementation graph: {e}")
        return 1

    # Check if all bricks have layer field
    missing_layer_bricks = [b.get("id") for b in bricks if "layer" not in b or b.get("layer") is None]
    if missing_layer_bricks:
        click.echo(f"✗ Some bricks are missing the 'layer' field:")
        for brick_id in missing_layer_bricks[:5]:  # Show first 5
            click.echo(f"  - {brick_id}")
        if len(missing_layer_bricks) > 5:
            click.echo(f"  ... and {len(missing_layer_bricks) - 5} more")
        click.echo("\nRun 'jigy validate bricks' to see all validation errors.")
        return 1

    # Group bricks by layer
    layers_dict = defaultdict(list)
    for brick in bricks:
        layer = brick.get("layer", 0)
        layers_dict[layer].append(brick)

    # Build unit to brick mapping
    unit_to_brick = {}
    for brick in bricks:
        brick_id = brick.get("id")
        for unit_id in brick.get("units", []):
            unit_to_brick[unit_id] = brick_id

    # Calculate dependencies for each brick
    brick_dependencies = defaultdict(set)
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source and target:
            source_brick = unit_to_brick.get(source)
            target_brick = unit_to_brick.get(target)
            if source_brick and target_brick and source_brick != target_brick:
                brick_dependencies[source_brick].add(target_brick)

    # Count functions per brick
    brick_function_counts = {}
    for brick in bricks:
        brick_id = brick.get("id")
        function_count = sum(
            1 for unit_id in brick.get("units", [])
            if unit_id in nodes and nodes[unit_id].get("type") == "function"
        )
        brick_function_counts[brick_id] = function_count

    # Check for cycles
    has_cycles = _has_cycles_in_brick_graph(brick_dependencies)

    # Display output
    if summary:
        _display_summary(layers_dict, brick_function_counts, has_cycles, bricks)
    else:
        _display_full(layers_dict, brick_dependencies, brick_function_counts, has_cycles, bricks, verbose)

    return 0


def _has_cycles_in_brick_graph(dependencies: dict) -> bool:
    """Check if brick dependency graph has cycles using DFS."""
    visited = set()
    rec_stack = set()

    def has_cycle_from(node):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in dependencies.get(node, []):
            if neighbor not in visited:
                if has_cycle_from(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False

    for node in dependencies.keys():
        if node not in visited:
            if has_cycle_from(node):
                return True

    return False


def _display_summary(layers_dict, brick_function_counts, has_cycles, bricks):
    """Display summary output (--summary)."""
    click.echo("Layer Summary")
    click.echo("━" * 60)

    total_bricks = len(bricks)
    total_functions = sum(brick_function_counts.values())

    # Display each layer
    for layer in sorted(layers_dict.keys()):
        layer_bricks = layers_dict[layer]
        layer_brick_count = len(layer_bricks)
        layer_function_count = sum(
            brick_function_counts.get(brick.get("id"), 0)
            for brick in layer_bricks
        )
        click.echo(f"Layer {layer}: {layer_brick_count} bricks, {layer_function_count} functions")

    click.echo("━" * 60)
    click.echo(f"Total: {total_bricks} bricks, {len(layers_dict)} layers, {total_functions} functions")


def _display_full(layers_dict, brick_dependencies, brick_function_counts, has_cycles, bricks, verbose):
    """Display full output (default)."""
    click.echo("Brick Layer Structure")
    click.echo("━" * 60)
    click.echo()

    total_bricks = len(bricks)
    total_functions = sum(brick_function_counts.values())

    # Display each layer
    for layer in sorted(layers_dict.keys()):
        layer_bricks = layers_dict[layer]
        click.echo(f"Layer {layer}: {_get_layer_name(layer)} ({len(layer_bricks)} bricks)")
        click.echo("─" * 60)

        for brick in layer_bricks:
            brick_id = brick.get("id")
            brick_name = brick.get("name", brick_id)
            function_count = brick_function_counts.get(brick_id, 0)

            click.echo(f"  {brick_id}: {brick_name} ({function_count} functions)")

            # Show dependencies
            deps = sorted(brick_dependencies.get(brick_id, []))
            if deps:
                deps_str = ", ".join(deps)
                click.echo(f"    ↓ depends on: {deps_str}")

            if verbose:
                # Show function list
                units = brick.get("units", [])
                functions = [u for u in units if u.startswith("F-")]
                if functions:
                    click.echo(f"    Functions: {', '.join(functions[:5])}")
                    if len(functions) > 5:
                        click.echo(f"      ... and {len(functions) - 5} more")

        click.echo()

    click.echo("━" * 60)
    click.echo(f"Total: {total_bricks} bricks, {len(layers_dict)} layers, {total_functions} functions")

    # Show DAG status
    if has_cycles:
        click.echo("Dependency graph: ⚠ Cycles detected")
    else:
        click.echo("Dependency graph: DAG ✓ (no cycles)")


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
