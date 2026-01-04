"""Show CLI commands for displaying JIG structure."""

import json
import re
from collections import defaultdict
from pathlib import Path

import click
import yaml

import jig
from jig.cli.discovery import find_project_root
from jig.config import JigConfig


def _load_yaml_frontmatter(file_path: Path) -> dict:
    """Load YAML frontmatter from a markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Dictionary of frontmatter fields, or empty dict if not found.
    """
    try:
        content = file_path.read_text()
        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx != -1:
                frontmatter = content[3:end_idx].strip()
                return yaml.safe_load(frontmatter) or {}
    except Exception:
        pass
    return {}


def _extract_goal_headers(content: str) -> list[str]:
    """Extract goal IDs from markdown headers.

    Looks for headers like ## G-001: Goal Title or ### G-001: Goal Title

    Args:
        content: Full markdown content.

    Returns:
        List of goal IDs found.
    """
    pattern = r"^#{2,3}\s+(G-\d{3}):"
    return re.findall(pattern, content, re.MULTILINE)


@jig.implements("S-060", "S-065", "S-070")
def show_overview_command(config: JigConfig, skip_rebuild: bool = False) -> int:
    """Display bricks + layers overview.

    Args:
        config: JIG configuration with resolved paths.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    # Auto-rebuild all stale graphs before showing (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["impl", "verify", "intent"], config, skip_rebuild=skip_rebuild)
    bricks_file = config.paths.bricks
    impl_graph = config.paths.generated / "implementation-graph.ndjson"

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


@jig.implements("S-060", "S-065", "S-070")
def show_layers_command(config: JigConfig, skip_rebuild: bool = False) -> int:
    """Display layer hierarchy.

    Args:
        config: JIG configuration with resolved paths.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    # Auto-rebuild stale impl + intent graphs before showing (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["impl", "intent"], config, skip_rebuild=skip_rebuild)
    bricks_file = config.paths.bricks
    impl_graph = config.paths.generated / "implementation-graph.ndjson"

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


@jig.implements("S-060", "S-065", "S-070")
def show_bricks_command(config: JigConfig, skip_rebuild: bool = False) -> int:
    """Display brick details.

    Args:
        config: JIG configuration with resolved paths.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    # Auto-rebuild stale impl + intent graphs before showing (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["impl", "intent"], config, skip_rebuild=skip_rebuild)
    bricks_file = config.paths.bricks
    impl_graph = config.paths.generated / "implementation-graph.ndjson"

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


@jig.implements("S-072")
def show_charter_command(config: JigConfig, skip_rebuild: bool = False) -> int:
    """Display Charter.md content and goals.

    Args:
        config: JIG configuration with resolved paths.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    charter_path = config.paths.charter

    if not charter_path.exists():
        click.echo("No Charter.md found.")
        click.echo(f"  Expected location: {charter_path}")
        return 1

    # Load and display charter
    try:
        content = charter_path.read_text()
        frontmatter = _load_yaml_frontmatter(charter_path)
        goals = frontmatter.get("defines_goals", [])

        click.echo("Project Charter")
        click.echo("=" * 50)
        click.echo()

        # Display defined goals
        if goals:
            click.echo(f"Defined Goals: {len(goals)}")
            for goal_id in goals:
                click.echo(f"  • {goal_id}")
            click.echo()

        # Extract and display goal sections
        goal_headers = _extract_goal_headers(content)
        if goal_headers:
            click.echo("Goal Sections:")
            for goal_id in goal_headers:
                # Find the goal title (supports ## or ### headers)
                pattern = rf"^#{{2,3}}\s+{goal_id}:\s*(.+)$"
                match = re.search(pattern, content, re.MULTILINE)
                title = match.group(1) if match else "(untitled)"
                click.echo(f"  {goal_id}: {title}")
            click.echo()

        click.echo(f"Source: {charter_path}")

    except Exception as e:
        click.echo(f"Error reading Charter: {e}", err=True)
        return 1

    return 0


@jig.implements("S-075")
def show_goals_command(config: JigConfig, skip_rebuild: bool = False) -> int:
    """Display all goals with supporting artifacts.

    Args:
        config: JIG configuration with resolved paths.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["intent"], config, skip_rebuild=skip_rebuild)

    charter_path = config.paths.charter
    intent_graph = config.paths.generated / "intent-graph.ndjson"

    if not charter_path.exists():
        click.echo("No Charter.md found - goals come from Charter.")
        return 1

    # Load charter for goals
    try:
        content = charter_path.read_text()
        frontmatter = _load_yaml_frontmatter(charter_path)
        defined_goals = frontmatter.get("defines_goals", [])
    except Exception as e:
        click.echo(f"Error reading Charter: {e}", err=True)
        return 1

    # Build goal → supporters mapping from intent graph
    goal_supporters = defaultdict(list)
    if intent_graph.exists():
        try:
            with intent_graph.open() as f:
                for line in f:
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    if obj.get("type") == "supports_goal":
                        source = obj.get("source")
                        target = obj.get("target")
                        if source and target:
                            goal_supporters[target].append(source)
        except Exception:
            pass

    click.echo("Project Goals")
    click.echo("=" * 50)
    click.echo()

    for goal_id in defined_goals:
        # Find goal title from charter (supports ## or ### headers)
        pattern = rf"^#{{2,3}}\s+{goal_id}:\s*(.+)$"
        match = re.search(pattern, content, re.MULTILINE)
        title = match.group(1) if match else "(untitled)"

        click.echo(f"{goal_id}: {title}")

        # Show supporting artifacts
        supporters = sorted(goal_supporters.get(goal_id, []))
        if supporters:
            # Group by type
            outcomes = [s for s in supporters if s.startswith("O-")]
            architectures = [s for s in supporters if s.startswith("A-")]

            if outcomes:
                click.echo(f"  Outcomes: {', '.join(outcomes)}")
            if architectures:
                click.echo(f"  Architecture: {', '.join(architectures)}")
        else:
            click.echo("  (no supporting artifacts)")

        click.echo()

    return 0


@jig.implements("S-076")
def show_architecture_command(
    config: JigConfig, arch_id: str | None = None, skip_rebuild: bool = False
) -> int:
    """Display architecture documents.

    Args:
        config: JIG configuration with resolved paths.
        arch_id: Optional specific architecture ID (e.g., "A-001").
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    arch_dir = config.paths.architecture

    if not arch_dir.exists():
        click.echo("No architecture directory found.")
        click.echo(f"  Expected location: {arch_dir}")
        return 1

    # Find architecture files
    arch_files = sorted(arch_dir.glob("A-*.md"))
    if not arch_files:
        click.echo("No architecture documents found.")
        return 0

    # If specific ID requested, show that one
    if arch_id:
        target_file = None
        for f in arch_files:
            fm = _load_yaml_frontmatter(f)
            if fm.get("id") == arch_id:
                target_file = f
                break

        if not target_file:
            click.echo(f"Architecture document '{arch_id}' not found.")
            return 1

        # Show detailed view
        fm = _load_yaml_frontmatter(target_file)
        click.echo("Architecture Document")
        click.echo("=" * 50)
        click.echo()
        click.echo(f"ID: {fm.get('id', '?')}")
        click.echo(f"Title: {fm.get('title', '?')}")
        click.echo(f"Status: {fm.get('status', '?')}")
        click.echo()

        goals = fm.get("supports_goals", [])
        if goals:
            click.echo(f"Supports Goals: {', '.join(goals)}")

        constrains = fm.get("constrains", [])
        if constrains:
            click.echo(f"Constrains Specs: {len(constrains)}")
            # Show first few
            shown = constrains[:5]
            click.echo(f"  {', '.join(shown)}")
            if len(constrains) > 5:
                click.echo(f"  ... and {len(constrains) - 5} more")

        click.echo()
        click.echo(f"Source: {target_file}")
        return 0

    # List all architecture documents
    click.echo("Architecture Documents")
    click.echo("=" * 50)
    click.echo()

    for f in arch_files:
        fm = _load_yaml_frontmatter(f)
        arch_id = fm.get("id", "?")
        title = fm.get("title", f.stem)
        status = fm.get("status", "?")
        goals = fm.get("supports_goals", [])
        constrains = fm.get("constrains", [])

        click.echo(f"{arch_id}: {title}")
        click.echo(f"  Status: {status}")
        if goals:
            click.echo(f"  Goals: {', '.join(goals)}")
        if constrains:
            click.echo(f"  Constrains: {len(constrains)} specs")
        click.echo()

    return 0
