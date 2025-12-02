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


@jig.implements("S-041")
def suggest_layers_command(project_root: Path, apply: bool = False) -> int:
    """
    Suggest layer assignments based on dependency analysis.

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
                bricks = bricks_data["bricks"]
            elif isinstance(bricks_data, list):
                bricks = bricks_data
            else:
                click.echo(f"✗ Invalid bricks file format")
                return 1
    except Exception as e:
        click.echo(f"✗ Error loading bricks file: {e}")
        return 1

    # Load implementation graph
    try:
        edges = []
        with impl_graph.open() as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                if "type" in obj and obj["type"] in ["calls", "imports", "inherits"]:
                    edges.append(obj)
    except Exception as e:
        click.echo(f"✗ Error loading implementation graph: {e}")
        return 1

    # Build unit to brick mapping
    unit_to_brick = {}
    for brick in bricks:
        brick_id = brick.get("id")
        for unit_id in brick.get("units", []):
            unit_to_brick[unit_id] = brick_id

    # Calculate brick dependencies
    brick_dependencies = defaultdict(set)
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source and target:
            source_brick = unit_to_brick.get(source)
            target_brick = unit_to_brick.get(target)
            if source_brick and target_brick and source_brick != target_brick:
                brick_dependencies[source_brick].add(target_brick)

    # Check for cycles
    if _has_cycles_in_brick_graph(brick_dependencies):
        click.echo("✗ Cannot suggest layers: circular dependencies exist.")
        click.echo("Run 'jigy validate bricks' to see cycles.")
        return 1

    # Perform topological sort and assign layers
    try:
        suggested_layers = _assign_layers_topologically(bricks, brick_dependencies)
    except Exception as e:
        click.echo(f"✗ Error assigning layers: {e}")
        return 1

    # Display suggestions
    _display_suggestions(bricks, suggested_layers, brick_dependencies)

    # Apply if requested
    if apply:
        if click.confirm("\nApply suggested layers to bricks.yaml?"):
            try:
                _apply_suggested_layers(bricks_file, bricks, suggested_layers)
                click.echo(f"\n✓ Updated {bricks_file}")
                return 0
            except Exception as e:
                click.echo(f"\n✗ Error updating bricks.yaml: {e}")
                return 1
        else:
            click.echo("\nNo changes made.")
            return 0

    return 0


def _assign_layers_topologically(bricks, brick_dependencies):
    """Assign layers using topological sort."""
    # Build reverse mapping (brick → layer)
    brick_layers = {}

    # Get all brick IDs
    all_bricks = {brick.get("id") for brick in bricks}

    # Compute in-degree for each brick
    in_degree = {brick_id: 0 for brick_id in all_bricks}
    for brick_id in all_bricks:
        for dep in brick_dependencies.get(brick_id, []):
            if dep in in_degree:
                in_degree[dep] += 1

    # Kahn's algorithm with layer assignment
    queue = [brick_id for brick_id in all_bricks if in_degree[brick_id] == 0]

    # Assign layer 0 to bricks with no incoming edges (no one depends on them, they're at top)
    # Wait, that's backwards. Let me think about this...
    # Actually, brick_dependencies[A] = {B, C} means A depends on B and C
    # So in_degree[B] counts how many bricks depend on B
    # Bricks with in_degree 0 are leaves (no one depends on them) - these should be at TOP layer
    # But we want foundation at layer 0, so we need to reverse the dependency direction

    # Let me reconsider: brick_dependencies[source] = {targets} means source depends on targets
    # For layer assignment, we want: layer(source) = max(layer(target)) + 1 for all targets
    # So bricks with no dependencies should be layer 0

    # I need to compute layers differently - start from bricks with no dependencies

    # Initialize all layers to -1
    brick_layers = {brick_id: -1 for brick_id in all_bricks}

    # Find bricks with no dependencies (foundation layer)
    no_deps = [brick_id for brick_id in all_bricks if not brick_dependencies.get(brick_id)]
    for brick_id in no_deps:
        brick_layers[brick_id] = 0

    # Process remaining bricks in topological order
    # Use BFS/DFS to propagate layers
    changed = True
    max_iterations = len(all_bricks) + 1
    iteration = 0

    while changed and iteration < max_iterations:
        changed = False
        iteration += 1

        for brick_id in all_bricks:
            deps = brick_dependencies.get(brick_id, set())
            if deps:
                # Check if all dependencies have assigned layers
                dep_layers = [brick_layers[dep] for dep in deps if dep in brick_layers and brick_layers[dep] != -1]
                if len(dep_layers) == len(deps):
                    # All dependencies have layers assigned
                    new_layer = max(dep_layers) + 1
                    if brick_layers[brick_id] != new_layer:
                        brick_layers[brick_id] = new_layer
                        changed = True

    return brick_layers


def _display_suggestions(bricks, suggested_layers, brick_dependencies):
    """Display layer suggestions with comparison to current layers."""
    click.echo("Suggested layer assignments based on dependencies:")
    click.echo("━" * 60)
    click.echo()

    matches = 0
    mismatches = 0
    unset = 0

    for brick in bricks:
        brick_id = brick.get("id")
        brick_name = brick.get("name", brick_id)
        current_layer = brick.get("layer")
        suggested_layer = suggested_layers.get(brick_id, 0)

        click.echo(f"{brick_id}: {brick_name}")

        # Show current layer
        if current_layer is None:
            click.echo(f"  Current layer: (not set)")
            unset += 1
        else:
            click.echo(f"  Current layer: {current_layer}")

        # Show suggested layer with reason
        deps = brick_dependencies.get(brick_id, set())
        if not deps:
            reason = "(no dependencies)"
        else:
            dep_list = ", ".join(sorted(deps))
            reason = f"(depends on: {dep_list})"

        click.echo(f"  Suggested: {suggested_layer} {reason}", nl=False)

        # Show match/mismatch
        if current_layer is not None:
            if current_layer == suggested_layer:
                click.echo(" ✓ MATCHES")
                matches += 1
            else:
                click.echo(" ⚠ MISMATCH")
                mismatches += 1
        else:
            click.echo()

        click.echo()

    click.echo("━" * 60)
    summary_parts = []
    if matches > 0:
        summary_parts.append(f"{matches} brick{'s' if matches != 1 else ''} match{'es' if matches == 1 else ''}")
    if mismatches > 0:
        summary_parts.append(f"{mismatches} mismatch{'es' if mismatches != 1 else ''}")
    if unset > 0:
        summary_parts.append(f"{unset} unset")

    if summary_parts:
        click.echo(", ".join(summary_parts))


def _apply_suggested_layers(bricks_file: Path, bricks: list, suggested_layers: dict) -> None:
    """Apply suggested layers to bricks.yaml file."""
    # Update bricks with suggested layers
    for brick in bricks:
        brick_id = brick.get("id")
        if brick_id in suggested_layers:
            brick["layer"] = suggested_layers[brick_id]

    # Write back to file
    # Preserve the file format (check if original had {bricks: [...]} wrapper)
    with bricks_file.open() as f:
        original_data = yaml.safe_load(f)

    if isinstance(original_data, dict) and "bricks" in original_data:
        # Preserve wrapper format
        output_data = {"bricks": bricks}
    else:
        # Bare list format
        output_data = bricks

    with bricks_file.open("w") as f:
        yaml.dump(output_data, f, default_flow_style=False, sort_keys=False)
