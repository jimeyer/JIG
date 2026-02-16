# ABOUTME: Project overview building and formatting, extracted from cli/overview.py.
# ABOUTME: Builds unified context combining charter, goals, specs, bricks, etc.

"""Query layer for project overview (S-114).

Provides:
- build_overview(): Build unified project overview data structure
- format_overview_human(): Format for terminal output
- format_overview_json(): Format as JSON
- format_overview_markdown(): Format as markdown for LLM consumption
"""

import json as json_module
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

import jig


def _load_yaml_frontmatter(file_path: Path) -> dict:
    """Load YAML frontmatter from a markdown file."""
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


def _load_bricks(bricks_file: Path) -> list | None:
    """Load bricks from bricks.yaml file."""
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


def _load_graph(graph_path: Path) -> tuple[dict[str, dict], list[dict]]:
    """Load NDJSON graph into nodes and edges."""
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    if not graph_path.exists():
        return nodes, edges

    try:
        with graph_path.open() as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json_module.loads(line)
                if "source" in obj and "target" in obj:
                    edges.append(obj)
                elif "id" in obj:
                    nodes[obj["id"]] = obj
    except Exception:
        pass

    return nodes, edges


@jig.implements("S-114")
def build_overview(config: Any) -> dict[str, Any]:
    """Build unified project overview data structure.

    Args:
        config: JIG configuration with resolved paths (duck-typed).

    Returns:
        Dictionary with all overview sections per S-114.
    """
    result: dict[str, Any] = {}

    # 1. Charter
    charter_path = config.paths.charter
    if charter_path.exists():
        content = charter_path.read_text()
        # Extract name from H1 heading
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        charter_name = h1_match.group(1) if h1_match else "Untitled"
        result["charter"] = {"name": charter_name, "file": str(charter_path)}
    else:
        result["charter"] = None

    # 2. Goals (from Charter frontmatter + content)
    goals = []
    if charter_path.exists():
        content = charter_path.read_text()
        fm = _load_yaml_frontmatter(charter_path)
        goal_ids = fm.get("goals", [])
        for goal_id in goal_ids:
            pattern = rf"^#{{2,3}}\s+{goal_id}:\s*(.+)$"
            match = re.search(pattern, content, re.MULTILINE)
            title = match.group(1) if match else "(untitled)"
            goals.append({"id": goal_id, "title": title})
    result["goals"] = goals

    # 3. Architecture documents
    arch_dir = config.paths.architecture
    architectures = []
    if arch_dir.exists():
        for f in sorted(arch_dir.glob("A-*.md")):
            fm = _load_yaml_frontmatter(f)
            architectures.append({
                "id": fm.get("id", "?"),
                "title": fm.get("title", f.stem),
                "file": str(f),
            })
    result["architecture"] = architectures

    # 4. Outcomes
    outcomes_dir = config.paths.outcomes
    outcomes = []
    if outcomes_dir.exists():
        for f in sorted(outcomes_dir.glob("O-*.md")):
            fm = _load_yaml_frontmatter(f)
            outcomes.append({
                "id": fm.get("id", "?"),
                "title": fm.get("title", f.stem),
                "goals": fm.get("goals", []),
            })
    result["outcomes"] = outcomes

    # 5. Specifications count
    specs_dir = config.paths.specifications
    impl_graph_path = config.paths.generated / "implementation-graph.ndjson"
    verify_graph_path = config.paths.generated / "verification-graph.ndjson"

    spec_ids = set()
    if specs_dir.exists():
        for f in specs_dir.glob("S-*.md"):
            fm = _load_yaml_frontmatter(f)
            spec_id = fm.get("id")
            if spec_id:
                spec_ids.add(spec_id)

    # Count implemented specs
    _, impl_edges = _load_graph(impl_graph_path)
    implemented_specs = set()
    for edge in impl_edges:
        if edge.get("type") == "implements":
            target = edge.get("target")
            if target and target.startswith("S-"):
                implemented_specs.add(target)

    # Count verified specs
    _, verify_edges = _load_graph(verify_graph_path)
    verified_specs = set()
    for edge in verify_edges:
        if edge.get("type") == "verifies":
            target = edge.get("target")
            if target and target.startswith("S-"):
                verified_specs.add(target)

    result["specs"] = {
        "total": len(spec_ids),
        "implemented": len(implemented_specs & spec_ids),
        "verified": len(verified_specs & spec_ids),
    }

    # 6. Bricks by layer
    bricks = _load_bricks(config.paths.bricks)
    bricks_by_layer: dict[int, list[str]] = defaultdict(list)
    if bricks:
        for brick in bricks:
            layer = brick.get("layer", 0)
            brick_id = brick.get("id")
            if brick_id:
                bricks_by_layer[layer].append(brick_id)

    # Convert to sorted dict
    result["bricks_by_layer"] = {
        str(layer): sorted(brick_ids)
        for layer, brick_ids in sorted(bricks_by_layer.items())
    }

    # 7. Towers (only if multi-tower)
    towers_set: set[str] = set()
    if bricks:
        for brick in bricks:
            tower = brick.get("tower")
            if tower:
                towers_set.add(tower)

    if towers_set:
        result["towers"] = sorted(towers_set)
    else:
        result["towers"] = None

    # 8. Traversal keys
    traversal_keys: list[str] = []

    # Spec IDs
    traversal_keys.extend(sorted(spec_ids))

    # Outcome IDs
    traversal_keys.extend(o["id"] for o in outcomes if o["id"] != "?")

    # Goal IDs
    traversal_keys.extend(g["id"] for g in goals)

    # Architecture IDs
    traversal_keys.extend(a["id"] for a in architectures if a["id"] != "?")

    # Brick IDs
    if bricks:
        traversal_keys.extend(sorted(b.get("id") for b in bricks if b.get("id")))

    # Charter
    if result["charter"]:
        traversal_keys.append("Charter")

    result["traversal_keys"] = traversal_keys

    return result


@jig.implements("S-114")
def format_overview_human(overview: dict[str, Any], verbose: bool = False) -> str:
    """Format overview for human terminal output."""
    lines = []

    # Charter
    if overview.get("charter"):
        lines.append(f"JIG: {overview['charter']['name']}")
        lines.append("")

    # Goals
    if overview.get("goals"):
        lines.append("Goals:")
        for g in overview["goals"]:
            lines.append(f"  {g['id']}: {g['title']}")
        lines.append("")

    # Bricks by layer
    if overview.get("bricks_by_layer"):
        lines.append("Bricks by Layer:")
        for layer, brick_ids in sorted(overview["bricks_by_layer"].items(), key=lambda x: int(x[0])):
            lines.append(f"  Layer {layer}: {', '.join(brick_ids)}")
        lines.append("")

    # Specs summary
    if overview.get("specs"):
        s = overview["specs"]
        lines.append(f"Specs: {s['total']} total ({s['implemented']} implemented, {s['verified']} verified)")
        lines.append("")

    # Towers (only if multi-tower)
    if overview.get("towers"):
        lines.append(f"Towers: {', '.join(overview['towers'])}")
        lines.append("")

    # Traversal keys summary
    if overview.get("traversal_keys") and verbose:
        keys = overview["traversal_keys"]
        lines.append(f"Traversal keys: {len(keys)} identifiers")
        # Show first few
        shown = keys[:10]
        lines.append(f"  {', '.join(shown)}" + (", ..." if len(keys) > 10 else ""))

    return "\n".join(lines)


@jig.implements("S-114")
def format_overview_json(overview: dict[str, Any]) -> str:
    """Format overview as JSON."""
    return json_module.dumps(overview)


@jig.implements("S-114")
def format_overview_markdown(overview: dict[str, Any], verbose: bool = False) -> str:
    """Format overview as markdown for LLM consumption."""
    lines = []

    # Charter
    if overview.get("charter"):
        lines.append(f"# {overview['charter']['name']}")
        lines.append("")

    # Goals
    if overview.get("goals"):
        lines.append("## Goals")
        lines.append("")
        for g in overview["goals"]:
            lines.append(f"- **{g['id']}:** {g['title']}")
        lines.append("")

    # Architecture
    if overview.get("architecture"):
        lines.append("## Architecture")
        lines.append("")
        for a in overview["architecture"]:
            lines.append(f"- **{a['id']}:** {a['title']}")
        lines.append("")

    # Outcomes
    if overview.get("outcomes") and verbose:
        lines.append("## Outcomes")
        lines.append("")
        for o in overview["outcomes"]:
            goals_str = f" (goals: {', '.join(o['goals'])})" if o.get("goals") else ""
            lines.append(f"- **{o['id']}:** {o['title']}{goals_str}")
        lines.append("")

    # Specs
    if overview.get("specs"):
        s = overview["specs"]
        lines.append("## Specifications")
        lines.append("")
        lines.append(f"- **Total:** {s['total']}")
        lines.append(f"- **Implemented:** {s['implemented']}")
        lines.append(f"- **Verified:** {s['verified']}")
        lines.append("")

    # Bricks
    if overview.get("bricks_by_layer"):
        lines.append("## Bricks by Layer")
        lines.append("")
        for layer, brick_ids in sorted(overview["bricks_by_layer"].items(), key=lambda x: int(x[0])):
            lines.append(f"- **Layer {layer}:** {', '.join(brick_ids)}")
        lines.append("")

    # Towers
    if overview.get("towers"):
        lines.append("## Towers")
        lines.append("")
        lines.append(f"{', '.join(overview['towers'])}")
        lines.append("")

    # Traversal keys
    if overview.get("traversal_keys"):
        lines.append("## Traversal Keys")
        lines.append("")
        lines.append("Valid identifiers for `context <id>`:")
        lines.append("")
        lines.append(f"`{', '.join(overview['traversal_keys'][:20])}`" +
                     (f" ... and {len(overview['traversal_keys']) - 20} more" if len(overview['traversal_keys']) > 20 else ""))
        lines.append("")

    return "\n".join(lines)
