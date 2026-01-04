"""Tower CLI commands for displaying tower structure."""

import json
from collections import defaultdict
from pathlib import Path

import click
import yaml

import jig
from jig.config import JigConfig


@jig.implements("S-090")
def towers_command(
    config: JigConfig, tower_id: str | None = None, skip_rebuild: bool = False
) -> int:
    """Display tower structure with brick counts by layer.

    Args:
        config: JIG configuration with resolved paths.
        tower_id: Optional specific tower ID to show details for.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["impl", "intent"], config, skip_rebuild=skip_rebuild)

    bricks_file = config.paths.bricks

    if not bricks_file.exists():
        click.echo("No bricks.yaml found.")
        return 1

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

    # Group bricks by tower
    towers: dict[str | None, list] = defaultdict(list)
    for brick in bricks:
        tower = brick.get("tower")
        towers[tower].append(brick)

    # Check if single-tower project (no towers declared)
    declared_towers = [t for t in towers.keys() if t is not None]
    if not declared_towers:
        click.echo("Single-Tower Project")
        click.echo("=" * 40)
        click.echo()
        click.echo("No towers declared in bricks.yaml.")
        click.echo("All bricks operate in a single implicit tower.")
        click.echo()
        click.echo(f"Total Bricks: {len(bricks)}")

        # Show layer breakdown
        layers = defaultdict(int)
        for brick in bricks:
            layers[brick.get("layer", 0)] += 1
        if layers:
            click.echo("By Layer:")
            for layer in sorted(layers.keys()):
                click.echo(f"  Layer {layer}: {layers[layer]} bricks")

        return 0

    # Multi-tower project
    if tower_id:
        # Show specific tower
        if tower_id not in towers:
            click.echo(f"Tower '{tower_id}' not found.")
            click.echo(f"Available towers: {', '.join(sorted(declared_towers))}")
            return 1

        tower_bricks = towers[tower_id]
        click.echo(f"Tower: {tower_id}")
        click.echo("=" * 40)
        click.echo()
        click.echo(f"Bricks: {len(tower_bricks)}")
        click.echo()

        # Group by layer
        layers = defaultdict(list)
        for brick in tower_bricks:
            layers[brick.get("layer", 0)].append(brick)

        for layer in sorted(layers.keys(), reverse=True):
            layer_bricks = layers[layer]
            click.echo(f"Layer {layer}:")
            for brick in layer_bricks:
                brick_id = brick.get("id")
                brick_name = brick.get("name", brick_id)
                click.echo(f"  {brick_id}: {brick_name}")
            click.echo()

        return 0

    # List all towers
    click.echo("Towers")
    click.echo("=" * 40)
    click.echo()

    for tower_name in sorted(declared_towers):
        tower_bricks = towers[tower_name]
        layers = defaultdict(int)
        for brick in tower_bricks:
            layers[brick.get("layer", 0)] += 1

        layer_summary = ", ".join(
            f"L{l}:{c}" for l, c in sorted(layers.items())
        )
        click.echo(f"{tower_name}: {len(tower_bricks)} bricks ({layer_summary})")

    # Show unassigned bricks (None tower)
    unassigned = towers.get(None, [])
    if unassigned:
        click.echo()
        click.echo(f"Unassigned: {len(unassigned)} bricks")
        for brick in unassigned:
            click.echo(f"  {brick.get('id')}")

    return 0


@jig.implements("S-091")
def matrix_command(config: JigConfig, skip_rebuild: bool = False) -> int:
    """Display layer × tower grid.

    Args:
        config: JIG configuration with resolved paths.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["impl", "intent"], config, skip_rebuild=skip_rebuild)

    bricks_file = config.paths.bricks

    if not bricks_file.exists():
        click.echo("No bricks.yaml found.")
        return 1

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

    # Build tower/layer matrix
    towers: set[str | None] = set()
    layers: set[int] = set()
    matrix: dict[tuple[str | None, int], list[str]] = defaultdict(list)

    for brick in bricks:
        tower = brick.get("tower")
        layer = brick.get("layer", 0)
        brick_id = brick.get("id")

        towers.add(tower)
        layers.add(layer)
        matrix[(tower, layer)].append(brick_id)

    # Check if single-tower project
    declared_towers = [t for t in towers if t is not None]
    if not declared_towers:
        click.echo("Single-Tower Project")
        click.echo("=" * 40)
        click.echo()
        click.echo("No towers declared - matrix view not applicable.")
        click.echo("Use 'jigy show layers' to see layer structure.")
        return 0

    # Display matrix
    click.echo("Layer × Tower Matrix")
    click.echo("=" * 60)
    click.echo()

    # Column headers
    sorted_towers = sorted(declared_towers)
    header = "Layer".ljust(8)
    for tower in sorted_towers:
        header += tower[:12].ljust(14)
    click.echo(header)
    click.echo("-" * len(header))

    # Rows (layers, highest first)
    for layer in sorted(layers, reverse=True):
        row = f"L{layer}".ljust(8)
        for tower in sorted_towers:
            cell_bricks = matrix.get((tower, layer), [])
            if cell_bricks:
                cell = f"{len(cell_bricks)} bricks"
            else:
                cell = "-"
            row += cell.ljust(14)
        click.echo(row)

    # Show unassigned if any
    unassigned_layers = [(l, matrix.get((None, l), [])) for l in layers]
    unassigned_total = sum(len(b) for _, b in unassigned_layers)
    if unassigned_total > 0:
        click.echo()
        click.echo(f"Unassigned: {unassigned_total} bricks not in any tower")

    return 0

