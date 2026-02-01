"""Show CLI commands for displaying JIG structure."""

import json as json_module
import re
from collections import defaultdict
from pathlib import Path

import click
import yaml

import jig
from jig.cli.discovery import find_project_root
from jig.cli.output import OutputFormat
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


def _load_bricks(bricks_file: Path) -> list | None:
    """Load bricks from bricks.yaml file.

    Args:
        bricks_file: Path to bricks.yaml

    Returns:
        List of brick dictionaries, or None if file doesn't exist or has error.
    """
    if not bricks_file.exists():
        return None

    try:
        with bricks_file.open() as f:
            bricks_data = yaml.safe_load(f)
            if isinstance(bricks_data, dict) and "bricks" in bricks_data:
                return bricks_data["bricks"]
            elif isinstance(bricks_data, list):
                return bricks_data
            else:
                return []
    except Exception:
        return None


@jig.implements("S-060", "S-065", "S-070", "S-093")
def show_overview_command(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
    skip_rebuild: bool = False,
) -> int:
    """Display bricks + layers overview.

    Args:
        config: JIG configuration with resolved paths.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional detail.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    # Auto-rebuild all stale graphs before showing (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current

    ensure_graphs_current(
        ["impl", "verify", "intent"], config, skip_rebuild=skip_rebuild
    )
    bricks_file = config.paths.bricks

    bricks = _load_bricks(bricks_file)
    if bricks is None:
        if output_format == OutputFormat.JSON:
            click.echo(json_module.dumps({"error": "No bricks.yaml found"}))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo("# JIG Structure Overview\n\nNo bricks.yaml found.")
        else:
            click.echo("No bricks.yaml found.")
        return 0

    # Group by layer
    layers_dict = defaultdict(list)
    for brick in bricks:
        layer = brick.get("layer", 0)
        layers_dict[layer].append(brick)

    if output_format == OutputFormat.JSON:
        # JSON output
        result = {
            "bricks": [
                {
                    "id": b.get("id"),
                    "name": b.get("name", b.get("id")),
                    "layer": b.get("layer", 0),
                    "units": b.get("units", []) if verbose else len(b.get("units", [])),
                }
                for b in bricks
            ],
            "layers": [
                {
                    "layer": layer,
                    "name": _get_layer_name(layer),
                    "brick_count": len(layers_dict[layer]),
                    "brick_ids": [b.get("id") for b in layers_dict[layer]],
                }
                for layer in sorted(layers_dict.keys())
            ],
            "summary": {
                "total_bricks": len(bricks),
                "total_layers": len(layers_dict),
            },
        }
        click.echo(json_module.dumps(result))
    elif output_format == OutputFormat.MARKDOWN:
        # Markdown output
        lines = ["# JIG Structure Overview", ""]
        lines.append(f"**Bricks:** {len(bricks)} total")
        lines.append(f"**Layers:** {len(layers_dict)} total")
        lines.append("")
        lines.append("## Bricks by Layer")
        lines.append("")
        for layer in sorted(layers_dict.keys()):
            layer_bricks = layers_dict[layer]
            brick_names = [b.get("id", "?") for b in layer_bricks]
            lines.append(f"- **Layer {layer}:** {', '.join(brick_names)}")
            if verbose:
                for b in layer_bricks:
                    units = b.get("units", [])
                    lines.append(f"  - {b.get('id')}: {len(units)} units")
        lines.append("")
        lines.append("## Layers")
        lines.append("")
        for layer in sorted(layers_dict.keys()):
            layer_name = _get_layer_name(layer)
            count = len(layers_dict[layer])
            lines.append(f"- **{layer}:** {layer_name} ({count} bricks)")
        click.echo("\n".join(lines))
    else:
        # Human-readable output
        click.echo("JIG Structure Overview")
        click.echo("=" * 40)
        click.echo()

        # Bricks summary
        click.echo(f"Bricks: {len(bricks)} total")
        for layer in sorted(layers_dict.keys()):
            layer_bricks = layers_dict[layer]
            brick_names = [b.get("id", "?") for b in layer_bricks]
            click.echo(f"  Layer {layer}: {', '.join(brick_names)}")
            if verbose:
                for b in layer_bricks:
                    units = b.get("units", [])
                    for u in units[:5]:
                        click.echo(f"    - {u}")
                    if len(units) > 5:
                        click.echo(f"    ... and {len(units) - 5} more")

        click.echo()

        # Layers summary
        click.echo(f"Layers: {len(layers_dict)} total")
        for layer in sorted(layers_dict.keys()):
            layer_name = _get_layer_name(layer)
            count = len(layers_dict[layer])
            click.echo(f"  {layer}: {layer_name} ({count} bricks)")

    return 0


@jig.implements("S-060", "S-065", "S-070", "S-093")
def show_layers_command(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
    skip_rebuild: bool = False,
) -> int:
    """Display layer hierarchy.

    Args:
        config: JIG configuration with resolved paths.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional detail.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    # Auto-rebuild stale impl + intent graphs before showing (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current

    ensure_graphs_current(["impl", "intent"], config, skip_rebuild=skip_rebuild)
    bricks_file = config.paths.bricks
    impl_graph = config.paths.generated / "implementation-graph.ndjson"

    bricks = _load_bricks(bricks_file)
    if bricks is None:
        if output_format == OutputFormat.JSON:
            click.echo(json_module.dumps({"error": "No bricks.yaml found"}))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo("# Layer Hierarchy\n\nNo bricks.yaml found.")
        else:
            click.echo("No bricks.yaml found.")
        return 0

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
                    obj = json_module.loads(line)
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

    if output_format == OutputFormat.JSON:
        result = {
            "layers": [
                {
                    "layer": layer,
                    "name": _get_layer_name(layer),
                    "bricks": [
                        {
                            "id": b.get("id"),
                            "name": b.get("name", b.get("id")),
                            "dependencies": sorted(brick_dependencies.get(b.get("id"), [])),
                            "units": b.get("units", []) if verbose else None,
                        }
                        for b in layers_dict[layer]
                    ],
                }
                for layer in sorted(layers_dict.keys(), reverse=True)
            ]
        }
        click.echo(json_module.dumps(result))
    elif output_format == OutputFormat.MARKDOWN:
        lines = ["# Layer Hierarchy", ""]
        for layer in sorted(layers_dict.keys(), reverse=True):
            layer_name = _get_layer_name(layer)
            layer_bricks = layers_dict[layer]
            lines.append(f"## Layer {layer}: {layer_name}")
            lines.append("")
            for brick in layer_bricks:
                brick_id = brick.get("id")
                brick_name = brick.get("name", brick_id)
                lines.append(f"- **{brick_id}**: {brick_name}")
                deps = sorted(brick_dependencies.get(brick_id, []))
                if deps:
                    lines.append(f"  - Dependencies: {', '.join(deps)}")
                if verbose:
                    units = brick.get("units", [])
                    lines.append(f"  - Units: {len(units)}")
            lines.append("")
        click.echo("\n".join(lines))
    else:
        # Human-readable output
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
                    click.echo(f"    -> {', '.join(deps)}")

                if verbose:
                    units = brick.get("units", [])
                    for u in units[:3]:
                        click.echo(f"    - {u}")
                    if len(units) > 3:
                        click.echo(f"    ... and {len(units) - 3} more")

            click.echo()

    return 0


@jig.implements("S-060", "S-065", "S-070", "S-093")
def show_bricks_command(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
    skip_rebuild: bool = False,
) -> int:
    """Display brick details.

    Args:
        config: JIG configuration with resolved paths.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional detail.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    # Auto-rebuild stale impl + intent graphs before showing (S-070)
    from jig.cli.auto_rebuild import ensure_graphs_current

    ensure_graphs_current(["impl", "intent"], config, skip_rebuild=skip_rebuild)
    bricks_file = config.paths.bricks

    bricks = _load_bricks(bricks_file)
    if bricks is None:
        if output_format == OutputFormat.JSON:
            click.echo(json_module.dumps({"error": "No bricks.yaml found"}))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo("# Brick Details\n\nNo bricks.yaml found.")
        else:
            click.echo("No bricks.yaml found.")
        return 0

    if output_format == OutputFormat.JSON:
        result = {
            "bricks": [
                {
                    "id": b.get("id"),
                    "name": b.get("name", b.get("id")),
                    "layer": b.get("layer", 0),
                    "units": b.get("units", []),
                    "unit_counts": {
                        "modules": sum(1 for u in b.get("units", []) if u.startswith("M-")),
                        "classes": sum(1 for u in b.get("units", []) if u.startswith("C-")),
                        "functions": sum(1 for u in b.get("units", []) if u.startswith("F-")),
                    },
                }
                for b in bricks
            ]
        }
        click.echo(json_module.dumps(result))
    elif output_format == OutputFormat.MARKDOWN:
        lines = ["# Brick Details", ""]
        for brick in bricks:
            brick_id = brick.get("id")
            brick_name = brick.get("name", brick_id)
            layer = brick.get("layer", "?")
            units = brick.get("units", [])

            module_count = sum(1 for u in units if u.startswith("M-"))
            class_count = sum(1 for u in units if u.startswith("C-"))
            function_count = sum(1 for u in units if u.startswith("F-"))

            lines.append(f"## {brick_id}")
            lines.append("")
            lines.append(f"- **Name:** {brick_name}")
            lines.append(f"- **Layer:** {layer}")
            lines.append(f"- **Units:** {len(units)} ({module_count} modules, {class_count} classes, {function_count} functions)")
            if verbose and units:
                lines.append("")
                lines.append("### Units")
                lines.append("")
                for u in units:
                    lines.append(f"- `{u}`")
            lines.append("")
        click.echo("\n".join(lines))
    else:
        # Human-readable output
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

            click.echo(
                f"  Units: {len(units)} ({module_count} modules, {class_count} classes, {function_count} functions)"
            )

            # Show first few units (or all if verbose)
            if units:
                shown = units if verbose else units[:3]
                click.echo(f"    - " + "\n    - ".join(shown))
                if not verbose and len(units) > 3:
                    click.echo(f"    ... and {len(units) - 3} more")

            click.echo()

    return 0


@jig.implements("S-072", "S-093")
def show_charter_command(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
    skip_rebuild: bool = False,
) -> int:
    """Display Charter.md content and goals.

    Args:
        config: JIG configuration with resolved paths.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional detail.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    charter_path = config.paths.charter

    if not charter_path.exists():
        if output_format == OutputFormat.JSON:
            click.echo(json_module.dumps({"error": "No charter file found", "expected_path": str(charter_path)}))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo(f"# Project Charter\n\nNo charter file found.\n\nExpected location: `{charter_path}`")
        else:
            click.echo("No charter file found.")
            click.echo(f"  Expected location: {charter_path}")
        return 1

    # Load and display charter
    try:
        content = charter_path.read_text()
        frontmatter = _load_yaml_frontmatter(charter_path)
        goals = frontmatter.get("defines_goals", [])

        # Extract goal sections with titles
        goal_headers = _extract_goal_headers(content)
        goal_titles = {}
        for goal_id in goal_headers:
            pattern = rf"^#{{2,3}}\s+{goal_id}:\s*(.+)$"
            match = re.search(pattern, content, re.MULTILINE)
            goal_titles[goal_id] = match.group(1) if match else "(untitled)"

        if output_format == OutputFormat.JSON:
            result = {
                "source": str(charter_path),
                "goals": [
                    {"id": g, "title": goal_titles.get(g, "(untitled)")}
                    for g in goals
                ],
            }
            if verbose:
                result["frontmatter"] = frontmatter
            click.echo(json_module.dumps(result))
        elif output_format == OutputFormat.MARKDOWN:
            lines = ["# Project Charter", ""]
            if goals:
                lines.append(f"**Defined Goals:** {len(goals)}")
                lines.append("")
                for goal_id in goals:
                    title = goal_titles.get(goal_id, "(untitled)")
                    lines.append(f"- **{goal_id}:** {title}")
                lines.append("")
            lines.append(f"*Source: `{charter_path}`*")
            if verbose:
                lines.append("")
                lines.append("---")
                lines.append("")
                lines.append("## Full Content")
                lines.append("")
                lines.append(content)
            click.echo("\n".join(lines))
        else:
            # Human-readable output
            click.echo("Project Charter")
            click.echo("=" * 50)
            click.echo()

            # Display defined goals
            if goals:
                click.echo(f"Defined Goals: {len(goals)}")
                for goal_id in goals:
                    click.echo(f"  * {goal_id}")
                click.echo()

            # Extract and display goal sections
            if goal_headers:
                click.echo("Goal Sections:")
                for goal_id in goal_headers:
                    title = goal_titles.get(goal_id, "(untitled)")
                    click.echo(f"  {goal_id}: {title}")
                click.echo()

            click.echo(f"Source: {charter_path}")

    except Exception as e:
        click.echo(f"Error reading Charter: {e}", err=True)
        return 1

    return 0


@jig.implements("S-075", "S-093")
def show_goals_command(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
    skip_rebuild: bool = False,
) -> int:
    """Display all goals with supporting artifacts.

    Args:
        config: JIG configuration with resolved paths.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional detail.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    from jig.cli.auto_rebuild import ensure_graphs_current

    ensure_graphs_current(["intent"], config, skip_rebuild=skip_rebuild)

    charter_path = config.paths.charter
    intent_graph = config.paths.generated / "intent-graph.ndjson"

    if not charter_path.exists():
        if output_format == OutputFormat.JSON:
            click.echo(json_module.dumps({"error": "No charter file found - goals come from Charter"}))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo("# Project Goals\n\nNo charter file found - goals come from Charter.")
        else:
            click.echo("No charter file found - goals come from Charter.")
        return 1

    # Load charter for goals
    try:
        content = charter_path.read_text()
        frontmatter = _load_yaml_frontmatter(charter_path)
        defined_goals = frontmatter.get("defines_goals", [])
    except Exception as e:
        click.echo(f"Error reading Charter: {e}", err=True)
        return 1

    # Build goal -> supporters mapping from intent graph
    goal_supporters = defaultdict(list)
    if intent_graph.exists():
        try:
            with intent_graph.open() as f:
                for line in f:
                    if not line.strip():
                        continue
                    obj = json_module.loads(line)
                    if obj.get("type") == "supports_goal":
                        source = obj.get("source")
                        target = obj.get("target")
                        if source and target:
                            goal_supporters[target].append(source)
        except Exception:
            pass

    # Build goal titles
    goal_titles = {}
    for goal_id in defined_goals:
        pattern = rf"^#{{2,3}}\s+{goal_id}:\s*(.+)$"
        match = re.search(pattern, content, re.MULTILINE)
        goal_titles[goal_id] = match.group(1) if match else "(untitled)"

    if output_format == OutputFormat.JSON:
        result = {
            "goals": [
                {
                    "id": goal_id,
                    "title": goal_titles.get(goal_id, "(untitled)"),
                    "supporters": {
                        "outcomes": [s for s in sorted(goal_supporters.get(goal_id, [])) if s.startswith("O-")],
                        "architectures": [s for s in sorted(goal_supporters.get(goal_id, [])) if s.startswith("A-")],
                    },
                }
                for goal_id in defined_goals
            ]
        }
        click.echo(json_module.dumps(result))
    elif output_format == OutputFormat.MARKDOWN:
        lines = ["# Project Goals", ""]
        for goal_id in defined_goals:
            title = goal_titles.get(goal_id, "(untitled)")
            lines.append(f"## {goal_id}: {title}")
            lines.append("")
            supporters = sorted(goal_supporters.get(goal_id, []))
            if supporters:
                outcomes = [s for s in supporters if s.startswith("O-")]
                architectures = [s for s in supporters if s.startswith("A-")]
                if outcomes:
                    lines.append(f"**Outcomes:** {', '.join(outcomes)}")
                if architectures:
                    lines.append(f"**Architecture:** {', '.join(architectures)}")
            else:
                lines.append("*(no supporting artifacts)*")
            lines.append("")
        click.echo("\n".join(lines))
    else:
        # Human-readable output
        click.echo("Project Goals")
        click.echo("=" * 50)
        click.echo()

        for goal_id in defined_goals:
            title = goal_titles.get(goal_id, "(untitled)")
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


@jig.implements("S-060", "S-090", "S-093")
def show_towers_command(
    config: JigConfig,
    tower_id: str | None = None,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
    skip_rebuild: bool = False,
) -> int:
    """Display tower structure with brick counts by layer.

    Args:
        config: JIG configuration with resolved paths.
        tower_id: Optional specific tower ID to show details for.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional detail.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    from jig.cli.auto_rebuild import ensure_graphs_current

    ensure_graphs_current(["impl", "intent"], config, skip_rebuild=skip_rebuild)

    bricks_file = config.paths.bricks
    bricks = _load_bricks(bricks_file)

    if bricks is None:
        if output_format == OutputFormat.JSON:
            click.echo(json_module.dumps({"error": "No bricks.yaml found"}))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo("# Towers\n\nNo bricks.yaml found.")
        else:
            click.echo("No bricks.yaml found.")
        return 1

    # Group bricks by tower
    towers: dict[str | None, list] = defaultdict(list)
    for brick in bricks:
        tower = brick.get("tower")
        towers[tower].append(brick)

    # Check if single-tower project (no towers declared)
    declared_towers = [t for t in towers.keys() if t is not None]

    if not declared_towers:
        # Single-tower project
        if output_format == OutputFormat.JSON:
            layers = defaultdict(int)
            for brick in bricks:
                layers[brick.get("layer", 0)] += 1
            result = {
                "single_tower": True,
                "total_bricks": len(bricks),
                "by_layer": [{"layer": l, "count": c} for l, c in sorted(layers.items())],
            }
            click.echo(json_module.dumps(result))
        elif output_format == OutputFormat.MARKDOWN:
            lines = ["# Single-Tower Project", ""]
            lines.append("No towers declared in bricks.yaml.")
            lines.append("All bricks operate in a single implicit tower.")
            lines.append("")
            lines.append(f"**Total Bricks:** {len(bricks)}")
            lines.append("")
            layers = defaultdict(int)
            for brick in bricks:
                layers[brick.get("layer", 0)] += 1
            lines.append("## By Layer")
            lines.append("")
            for layer in sorted(layers.keys()):
                lines.append(f"- **Layer {layer}:** {layers[layer]} bricks")
            click.echo("\n".join(lines))
        else:
            click.echo("Single-Tower Project")
            click.echo("=" * 40)
            click.echo()
            click.echo("No towers declared in bricks.yaml.")
            click.echo("All bricks operate in a single implicit tower.")
            click.echo()
            click.echo(f"Total Bricks: {len(bricks)}")
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
            if output_format == OutputFormat.JSON:
                click.echo(json_module.dumps({
                    "error": f"Tower '{tower_id}' not found",
                    "available_towers": sorted(declared_towers),
                }))
            elif output_format == OutputFormat.MARKDOWN:
                click.echo(f"# Tower Not Found\n\nTower '{tower_id}' not found.\n\n")
                click.echo(f"**Available towers:** {', '.join(sorted(declared_towers))}")
            else:
                click.echo(f"Tower '{tower_id}' not found.")
                click.echo(f"Available towers: {', '.join(sorted(declared_towers))}")
            return 1

        tower_bricks = towers[tower_id]
        layers = defaultdict(list)
        for brick in tower_bricks:
            layers[brick.get("layer", 0)].append(brick)

        if output_format == OutputFormat.JSON:
            result = {
                "tower": tower_id,
                "brick_count": len(tower_bricks),
                "layers": [
                    {
                        "layer": layer,
                        "bricks": [
                            {
                                "id": b.get("id"),
                                "name": b.get("name", b.get("id")),
                                "units": b.get("units", []) if verbose else len(b.get("units", [])),
                            }
                            for b in layers[layer]
                        ],
                    }
                    for layer in sorted(layers.keys(), reverse=True)
                ],
            }
            click.echo(json_module.dumps(result))
        elif output_format == OutputFormat.MARKDOWN:
            lines = [f"# Tower: {tower_id}", ""]
            lines.append(f"**Bricks:** {len(tower_bricks)}")
            lines.append("")
            for layer in sorted(layers.keys(), reverse=True):
                layer_bricks = layers[layer]
                lines.append(f"## Layer {layer}")
                lines.append("")
                for brick in layer_bricks:
                    brick_id = brick.get("id")
                    brick_name = brick.get("name", brick_id)
                    lines.append(f"- **{brick_id}:** {brick_name}")
                    if verbose:
                        units = brick.get("units", [])
                        lines.append(f"  - Units: {len(units)}")
                lines.append("")
            click.echo("\n".join(lines))
        else:
            click.echo(f"Tower: {tower_id}")
            click.echo("=" * 40)
            click.echo()
            click.echo(f"Bricks: {len(tower_bricks)}")
            click.echo()
            for layer in sorted(layers.keys(), reverse=True):
                layer_bricks = layers[layer]
                click.echo(f"Layer {layer}:")
                for brick in layer_bricks:
                    brick_id = brick.get("id")
                    brick_name = brick.get("name", brick_id)
                    click.echo(f"  {brick_id}: {brick_name}")
                    if verbose:
                        units = brick.get("units", [])
                        for u in units[:5]:
                            click.echo(f"    - {u}")
                        if len(units) > 5:
                            click.echo(f"    ... and {len(units) - 5} more")
                click.echo()
        return 0

    # List all towers
    if output_format == OutputFormat.JSON:
        result = {
            "towers": [
                {
                    "name": tower_name,
                    "brick_count": len(towers[tower_name]),
                    "by_layer": [
                        {"layer": l, "count": sum(1 for b in towers[tower_name] if b.get("layer", 0) == l)}
                        for l in sorted(set(b.get("layer", 0) for b in towers[tower_name]))
                    ],
                }
                for tower_name in sorted(declared_towers)
            ],
        }
        unassigned = towers.get(None, [])
        if unassigned:
            result["unassigned"] = {
                "brick_count": len(unassigned),
                "brick_ids": [b.get("id") for b in unassigned],
            }
        click.echo(json_module.dumps(result))
    elif output_format == OutputFormat.MARKDOWN:
        lines = ["# Towers", ""]
        for tower_name in sorted(declared_towers):
            tower_bricks = towers[tower_name]
            layers = defaultdict(int)
            for brick in tower_bricks:
                layers[brick.get("layer", 0)] += 1
            layer_summary = ", ".join(f"L{l}:{c}" for l, c in sorted(layers.items()))
            lines.append(f"## {tower_name}")
            lines.append("")
            lines.append(f"**Bricks:** {len(tower_bricks)} ({layer_summary})")
            if verbose:
                lines.append("")
                for brick in tower_bricks:
                    lines.append(f"- {brick.get('id')}: {brick.get('name', brick.get('id'))}")
            lines.append("")
        unassigned = towers.get(None, [])
        if unassigned:
            lines.append("## Unassigned")
            lines.append("")
            lines.append(f"**{len(unassigned)} bricks** not assigned to any tower:")
            lines.append("")
            for brick in unassigned:
                lines.append(f"- {brick.get('id')}")
        click.echo("\n".join(lines))
    else:
        click.echo("Towers")
        click.echo("=" * 40)
        click.echo()
        for tower_name in sorted(declared_towers):
            tower_bricks = towers[tower_name]
            layers = defaultdict(int)
            for brick in tower_bricks:
                layers[brick.get("layer", 0)] += 1
            layer_summary = ", ".join(f"L{l}:{c}" for l, c in sorted(layers.items()))
            click.echo(f"{tower_name}: {len(tower_bricks)} bricks ({layer_summary})")
            if verbose:
                for brick in tower_bricks:
                    click.echo(f"  - {brick.get('id')}: {brick.get('name', brick.get('id'))}")
        unassigned = towers.get(None, [])
        if unassigned:
            click.echo()
            click.echo(f"Unassigned: {len(unassigned)} bricks")
            for brick in unassigned:
                click.echo(f"  {brick.get('id')}")

    return 0


@jig.implements("S-060", "S-091", "S-093")
def show_matrix_command(
    config: JigConfig,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
    skip_rebuild: bool = False,
) -> int:
    """Display layer x tower grid.

    Args:
        config: JIG configuration with resolved paths.
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional detail.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    from jig.cli.auto_rebuild import ensure_graphs_current

    ensure_graphs_current(["impl", "intent"], config, skip_rebuild=skip_rebuild)

    bricks_file = config.paths.bricks
    bricks = _load_bricks(bricks_file)

    if bricks is None:
        if output_format == OutputFormat.JSON:
            click.echo(json_module.dumps({"error": "No bricks.yaml found"}))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo("# Layer x Tower Matrix\n\nNo bricks.yaml found.")
        else:
            click.echo("No bricks.yaml found.")
        return 1

    # Build tower/layer matrix
    towers_set: set[str | None] = set()
    layers_set: set[int] = set()
    matrix: dict[tuple[str | None, int], list[str]] = defaultdict(list)

    for brick in bricks:
        tower = brick.get("tower")
        layer = brick.get("layer", 0)
        brick_id = brick.get("id")

        towers_set.add(tower)
        layers_set.add(layer)
        matrix[(tower, layer)].append(brick_id)

    # Check if single-tower project
    declared_towers = [t for t in towers_set if t is not None]
    if not declared_towers:
        if output_format == OutputFormat.JSON:
            result = {
                "single_tower": True,
                "message": "No towers declared - matrix view not applicable",
            }
            click.echo(json_module.dumps(result))
        elif output_format == OutputFormat.MARKDOWN:
            lines = ["# Single-Tower Project", ""]
            lines.append("No towers declared - matrix view not applicable.")
            lines.append("")
            lines.append("Use `jigy show layers` to see layer structure.")
            click.echo("\n".join(lines))
        else:
            click.echo("Single-Tower Project")
            click.echo("=" * 40)
            click.echo()
            click.echo("No towers declared - matrix view not applicable.")
            click.echo("Use 'jigy show layers' to see layer structure.")
        return 0

    # Build matrix data
    sorted_towers = sorted(declared_towers)
    sorted_layers = sorted(layers_set, reverse=True)

    if output_format == OutputFormat.JSON:
        grid = []
        for layer in sorted_layers:
            row = {"layer": layer, "cells": {}}
            for tower in sorted_towers:
                cell_bricks = matrix.get((tower, layer), [])
                row["cells"][tower] = {
                    "count": len(cell_bricks),
                    "brick_ids": cell_bricks if verbose else None,
                }
            grid.append(row)

        result = {
            "towers": sorted_towers,
            "layers": sorted_layers,
            "grid": grid,
        }

        # Include unassigned if any
        unassigned_total = sum(len(matrix.get((None, l), [])) for l in sorted_layers)
        if unassigned_total > 0:
            result["unassigned"] = {
                "total": unassigned_total,
                "by_layer": [
                    {"layer": l, "count": len(matrix.get((None, l), []))}
                    for l in sorted_layers
                    if matrix.get((None, l))
                ],
            }

        click.echo(json_module.dumps(result))
    elif output_format == OutputFormat.MARKDOWN:
        lines = ["# Layer x Tower Matrix", ""]

        # Build markdown table
        header = "| Layer |"
        for tower in sorted_towers:
            header += f" {tower[:12]} |"
        lines.append(header)

        separator = "|-------|"
        for tower in sorted_towers:
            separator += "-" * (len(tower[:12]) + 2) + "|"
        lines.append(separator)

        for layer in sorted_layers:
            row = f"| L{layer}    |"
            for tower in sorted_towers:
                cell_bricks = matrix.get((tower, layer), [])
                if cell_bricks:
                    cell = f" {len(cell_bricks)} "
                else:
                    cell = " - "
                row += cell.center(len(tower[:12]) + 2) + "|"
            lines.append(row)

        lines.append("")

        # Unassigned
        unassigned_total = sum(len(matrix.get((None, l), [])) for l in sorted_layers)
        if unassigned_total > 0:
            lines.append(f"**Unassigned:** {unassigned_total} bricks not in any tower")

        click.echo("\n".join(lines))
    else:
        click.echo("Layer x Tower Matrix")
        click.echo("=" * 60)
        click.echo()

        # Column headers
        header = "Layer".ljust(8)
        for tower in sorted_towers:
            header += tower[:12].ljust(14)
        click.echo(header)
        click.echo("-" * len(header))

        # Rows (layers, highest first)
        for layer in sorted_layers:
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
        unassigned_total = sum(len(matrix.get((None, l), [])) for l in sorted_layers)
        if unassigned_total > 0:
            click.echo()
            click.echo(f"Unassigned: {unassigned_total} bricks not in any tower")

    return 0


@jig.implements("S-076", "S-093")
def show_architecture_command(
    config: JigConfig,
    arch_id: str | None = None,
    output_format: OutputFormat = OutputFormat.HUMAN,
    verbose: bool = False,
    skip_rebuild: bool = False,
) -> int:
    """Display architecture documents.

    Args:
        config: JIG configuration with resolved paths.
        arch_id: Optional specific architecture ID (e.g., "A-001").
        output_format: Output format (HUMAN, JSON, MARKDOWN).
        verbose: If True, include additional detail.
        skip_rebuild: If True, skip auto-rebuild.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    arch_dir = config.paths.architecture

    if not arch_dir.exists():
        if output_format == OutputFormat.JSON:
            click.echo(json_module.dumps({"error": "No architecture directory found", "expected_path": str(arch_dir)}))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo(f"# Architecture Documents\n\nNo architecture directory found.\n\nExpected location: `{arch_dir}`")
        else:
            click.echo("No architecture directory found.")
            click.echo(f"  Expected location: {arch_dir}")
        return 1

    # Find architecture files
    arch_files = sorted(arch_dir.glob("A-*.md"))
    if not arch_files:
        if output_format == OutputFormat.JSON:
            click.echo(json_module.dumps({"documents": []}))
        elif output_format == OutputFormat.MARKDOWN:
            click.echo("# Architecture Documents\n\nNo architecture documents found.")
        else:
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
            if output_format == OutputFormat.JSON:
                click.echo(json_module.dumps({"error": f"Architecture document '{arch_id}' not found"}))
            elif output_format == OutputFormat.MARKDOWN:
                click.echo(f"# Architecture Document\n\nDocument '{arch_id}' not found.")
            else:
                click.echo(f"Architecture document '{arch_id}' not found.")
            return 1

        # Show detailed view
        fm = _load_yaml_frontmatter(target_file)
        goals = fm.get("supports_goals", [])
        constrains = fm.get("constrains", [])

        if output_format == OutputFormat.JSON:
            result = {
                "id": fm.get("id", "?"),
                "title": fm.get("title", "?"),
                "status": fm.get("status", "?"),
                "supports_goals": goals,
                "constrains": constrains,
                "source": str(target_file),
            }
            if verbose:
                result["frontmatter"] = fm
            click.echo(json_module.dumps(result))
        elif output_format == OutputFormat.MARKDOWN:
            lines = [f"# {fm.get('title', 'Architecture Document')}", ""]
            lines.append(f"**ID:** {fm.get('id', '?')}")
            lines.append(f"**Status:** {fm.get('status', '?')}")
            lines.append("")
            if goals:
                lines.append(f"**Supports Goals:** {', '.join(goals)}")
            if constrains:
                lines.append(f"**Constrains:** {len(constrains)} specs")
                if verbose:
                    lines.append("")
                    for c in constrains:
                        lines.append(f"- {c}")
            lines.append("")
            lines.append(f"*Source: `{target_file}`*")
            click.echo("\n".join(lines))
        else:
            # Human-readable output
            click.echo("Architecture Document")
            click.echo("=" * 50)
            click.echo()
            click.echo(f"ID: {fm.get('id', '?')}")
            click.echo(f"Title: {fm.get('title', '?')}")
            click.echo(f"Status: {fm.get('status', '?')}")
            click.echo()

            if goals:
                click.echo(f"Supports Goals: {', '.join(goals)}")

            if constrains:
                click.echo(f"Constrains Specs: {len(constrains)}")
                # Show first few
                shown = constrains[:5] if not verbose else constrains
                click.echo(f"  {', '.join(shown)}")
                if not verbose and len(constrains) > 5:
                    click.echo(f"  ... and {len(constrains) - 5} more")

            click.echo()
            click.echo(f"Source: {target_file}")
        return 0

    # List all architecture documents
    docs = []
    for f in arch_files:
        fm = _load_yaml_frontmatter(f)
        docs.append({
            "id": fm.get("id", "?"),
            "title": fm.get("title", f.stem),
            "status": fm.get("status", "?"),
            "supports_goals": fm.get("supports_goals", []),
            "constrains": fm.get("constrains", []),
            "source": str(f),
        })

    if output_format == OutputFormat.JSON:
        click.echo(json_module.dumps({"documents": docs}))
    elif output_format == OutputFormat.MARKDOWN:
        lines = ["# Architecture Documents", ""]
        for doc in docs:
            lines.append(f"## {doc['id']}: {doc['title']}")
            lines.append("")
            lines.append(f"- **Status:** {doc['status']}")
            if doc["supports_goals"]:
                lines.append(f"- **Goals:** {', '.join(doc['supports_goals'])}")
            if doc["constrains"]:
                lines.append(f"- **Constrains:** {len(doc['constrains'])} specs")
            lines.append("")
        click.echo("\n".join(lines))
    else:
        # Human-readable output
        click.echo("Architecture Documents")
        click.echo("=" * 50)
        click.echo()

        for doc in docs:
            click.echo(f"{doc['id']}: {doc['title']}")
            click.echo(f"  Status: {doc['status']}")
            if doc["supports_goals"]:
                click.echo(f"  Goals: {', '.join(doc['supports_goals'])}")
            if doc["constrains"]:
                click.echo(f"  Constrains: {len(doc['constrains'])} specs")
            click.echo()

    return 0
