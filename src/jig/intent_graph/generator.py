"""Intent graph generator.

Generates intent-graph.ndjson from specifications, outcomes, and bricks.yaml
per A001 §6.1.

Version 2.0 adds Charter, Goal, and Architecture nodes.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

import jig
from jig.hashing import git_blob_hash, hash_brick, hash_intent_artifact


@jig.implements("S-028", "S-050", "S-068", "S-080", "S-081", "S-082", "S-083", "S-084", "S-085", "S-086")
def generate_intent_graph(
    project_root: Path,
    output_path: Optional[Path] = None,
    include_timestamp: bool = True,
    git_metadata: Optional[Dict[str, Any]] = None,
) -> tuple[Path, int, int]:
    """Generate intent-graph.ndjson from intent artifacts.

    Args:
        project_root: Root directory of the project.
        output_path: Path to write the intent graph. Defaults to
            <project_root>/jig/generated/intent-graph.ndjson.
        include_timestamp: Whether to include generated timestamp in metadata.
            Defaults to True.
        git_metadata: Optional git state metadata for staleness detection.

    Returns:
        Tuple of (output_path, node_count, edge_count).

    Raises:
        FileNotFoundError: If required directories don't exist.
        ValueError: If YAML parsing fails or data is invalid.
    """
    # Set default output path
    if output_path is None:
        output_path = project_root / "jig" / "generated" / "intent-graph.ndjson"

    # Define paths to intent artifacts
    charter_file = project_root / "jig" / "Charter.md"
    architecture_dir = project_root / "jig" / "architecture"
    spec_dir = project_root / "jig" / "specifications"
    outcome_dir = project_root / "jig" / "outcomes"
    bricks_file = project_root / "jig" / "bricks.yaml"

    # Load charter node (S-080)
    charter_node = _load_charter_node(charter_file)

    # Load goal nodes from charter (S-081)
    goal_nodes = _load_goal_nodes(charter_file)

    # Load architecture nodes (S-082)
    architecture_nodes = _load_architecture_nodes(architecture_dir)

    # Load spec nodes
    spec_nodes = _load_specification_nodes(spec_dir)

    # Load outcome nodes (optional)
    outcome_nodes = _load_outcome_nodes(outcome_dir)

    # Load brick nodes
    brick_nodes = _load_brick_nodes(bricks_file)

    # Create all edges
    edges: List[Dict[str, str]] = []

    # Charter→Goal defines_goal edges (S-083)
    edges.extend(_create_defines_goal_edges(charter_node))

    # Architecture/Outcome→Goal supports_goal edges (S-084)
    edges.extend(_create_supports_goal_edges(architecture_nodes, outcome_nodes))

    # Architecture→Spec constrains edges (S-085)
    edges.extend(_create_constrains_edges(architecture_nodes))

    # Outcome→Spec specifies edges
    edges.extend(_create_specifies_edges(outcome_nodes))

    # Calculate counts
    charter_count = 1 if charter_node else 0
    goal_count = len(goal_nodes)
    arch_count = len(architecture_nodes)
    tower_count = _count_towers(brick_nodes)

    node_count = (
        charter_count
        + goal_count
        + arch_count
        + len(spec_nodes)
        + len(outcome_nodes)
        + len(brick_nodes)
    )
    edge_count = len(edges)

    # Generate metadata (version 2.0)
    metadata = _generate_metadata(
        spec_count=len(spec_nodes),
        outcome_count=len(outcome_nodes),
        brick_count=len(brick_nodes),
        include_timestamp=include_timestamp,
        git_metadata=git_metadata,
        charter_exists=charter_node is not None,
        goal_count=goal_count,
        architecture_count=arch_count,
        tower_count=tower_count,
    )

    # Write NDJSON file
    _write_intent_graph(
        output_path=output_path,
        metadata=metadata,
        charter_node=charter_node,
        goal_nodes=goal_nodes,
        architecture_nodes=architecture_nodes,
        spec_nodes=spec_nodes,
        outcome_nodes=outcome_nodes,
        brick_nodes=brick_nodes,
        edges=edges,
    )

    return output_path, node_count, edge_count


@jig.implements("S-080")
def _load_charter_node(charter_file: Path) -> Optional[Dict[str, Any]]:
    """Load Charter node from Charter.md.

    Args:
        charter_file: Path to Charter.md.

    Returns:
        Charter node dictionary, or None if file doesn't exist.
    """
    if not charter_file.exists():
        return None

    frontmatter = _parse_frontmatter(charter_file)
    if frontmatter is None:
        return None

    charter_node = {
        "id": "Charter",
        "type": "charter",
        "defines_goals": frontmatter.get("defines_goals", []),
        "file": "jig/Charter.md",
        "jig_hash": hash_intent_artifact(charter_file),
    }

    # Add optional git_blob for tiered rebuild optimization (S-049)
    git_blob = git_blob_hash(charter_file)
    if git_blob:
        charter_node["git_blob"] = git_blob

    return charter_node


@jig.implements("S-081")
def _load_goal_nodes(charter_file: Path) -> List[Dict[str, Any]]:
    """Load Goal nodes extracted from Charter.md body.

    Args:
        charter_file: Path to Charter.md.

    Returns:
        List of goal node dictionaries.
    """
    if not charter_file.exists():
        return []

    goal_nodes = []
    goal_header_pattern = re.compile(r"^###\s+(G-\d+):\s*(.*)$", re.MULTILINE)

    try:
        content = charter_file.read_text()
        # Skip frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]

        for match in goal_header_pattern.finditer(content):
            goal_id = match.group(1)
            title = match.group(2).strip()

            goal_node = {
                "id": goal_id,
                "type": "goal",
                "title": title,
                "file": "jig/Charter.md",
            }
            goal_nodes.append(goal_node)

    except Exception:
        pass

    return goal_nodes


@jig.implements("S-082")
def _load_architecture_nodes(architecture_dir: Path) -> List[Dict[str, Any]]:
    """Load Architecture nodes from jig/architecture/*.md.

    Args:
        architecture_dir: Directory containing A-*.md files.

    Returns:
        List of architecture node dictionaries.
    """
    if not architecture_dir.exists():
        return []

    arch_nodes = []
    for arch_file in sorted(architecture_dir.glob("A-*.md")):
        frontmatter = _parse_frontmatter(arch_file)
        if frontmatter is None:
            continue

        arch_id = frontmatter.get("id")
        if not arch_id:
            continue

        relative_path = f"jig/architecture/{arch_file.name}"

        arch_node: Dict[str, Any] = {
            "id": arch_id,
            "type": "architecture",
            "title": frontmatter.get("title", ""),
            "status": frontmatter.get("status", ""),
            "supports_goals": frontmatter.get("supports_goals", []),
            "file": relative_path,
            "jig_hash": hash_intent_artifact(arch_file),
        }

        # Add constrains field if present
        constrains = frontmatter.get("constrains")
        if constrains:
            arch_node["constrains"] = constrains

        # Add optional git_blob for tiered rebuild optimization (S-049)
        git_blob = git_blob_hash(arch_file)
        if git_blob:
            arch_node["git_blob"] = git_blob

        arch_nodes.append(arch_node)

    return arch_nodes


def _load_specification_nodes(spec_dir: Path) -> List[Dict[str, Any]]:
    """Load specification nodes from spec files.

    Args:
        spec_dir: Directory containing S-*.md files.

    Returns:
        List of specification node dictionaries.
    """
    if not spec_dir.exists():
        return []

    spec_nodes = []
    for spec_file in sorted(spec_dir.glob("S-*.md")):
        frontmatter = _parse_frontmatter(spec_file)
        if frontmatter is None:
            continue

        spec_id = frontmatter.get("id")
        if not spec_id:
            continue

        # Relative path from project root (assumes spec_dir is <project>/jig/specifications)
        relative_path = f"jig/specifications/{spec_file.name}"

        spec_node = {
            "id": spec_id,
            "type": "specification",
            "file": relative_path,
            "jig_hash": hash_intent_artifact(spec_file),
        }

        # Add optional git_blob for tiered rebuild optimization (S-049)
        git_blob = git_blob_hash(spec_file)
        if git_blob:
            spec_node["git_blob"] = git_blob

        spec_nodes.append(spec_node)

    return spec_nodes


def _load_outcome_nodes(outcome_dir: Path) -> List[Dict[str, Any]]:
    """Load outcome nodes from outcome files.

    Args:
        outcome_dir: Directory containing O-*.md files.

    Returns:
        List of outcome node dictionaries. Empty list if directory doesn't exist.
    """
    if not outcome_dir.exists():
        return []

    outcome_nodes = []
    for outcome_file in sorted(outcome_dir.glob("O-*.md")):
        frontmatter = _parse_frontmatter(outcome_file)
        if frontmatter is None:
            continue

        outcome_id = frontmatter.get("id")
        if not outcome_id:
            continue

        # Relative path from project root
        relative_path = f"jig/outcomes/{outcome_file.name}"

        outcome_node: Dict[str, Any] = {
            "id": outcome_id,
            "type": "outcome",
            "file": relative_path,
            "jig_hash": hash_intent_artifact(outcome_file),
            "specifies": frontmatter.get("specifies", []),
        }

        # Add supports_goals if present (S-084)
        supports_goals = frontmatter.get("supports_goals")
        if supports_goals:
            outcome_node["supports_goals"] = supports_goals

        # Add optional git_blob for tiered rebuild optimization (S-049)
        git_blob = git_blob_hash(outcome_file)
        if git_blob:
            outcome_node["git_blob"] = git_blob

        outcome_nodes.append(outcome_node)

    return outcome_nodes


@jig.implements("S-086")
def _load_brick_nodes(bricks_file: Path) -> List[Dict[str, Any]]:
    """Load brick nodes from bricks.yaml.

    Args:
        bricks_file: Path to bricks.yaml.

    Returns:
        List of brick node dictionaries.

    Raises:
        FileNotFoundError: If bricks.yaml doesn't exist.
        ValueError: If bricks.yaml is invalid.
    """
    if not bricks_file.exists():
        raise FileNotFoundError(f"Bricks file not found: {bricks_file}")

    try:
        bricks_data = yaml.safe_load(bricks_file.read_text())
    except Exception as e:
        raise ValueError(f"Failed to parse bricks.yaml: {e}")

    # Handle both formats: {"bricks": [...]} or direct [...]
    if isinstance(bricks_data, dict) and "bricks" in bricks_data:
        bricks = bricks_data["bricks"]
    elif isinstance(bricks_data, list):
        bricks = bricks_data
    else:
        raise ValueError(
            f"Invalid bricks.yaml format: expected dict with 'bricks' key or list, got {type(bricks_data)}"
        )

    # Compute git_blob once for the bricks file (S-049)
    bricks_git_blob = git_blob_hash(bricks_file)

    brick_nodes = []
    for brick in bricks:
        brick_id = brick.get("id")
        brick_name = brick.get("name")
        brick_units = brick.get("units", [])
        brick_layer = brick.get("layer")

        if not brick_id or not brick_name:
            continue

        brick_node: Dict[str, Any] = {
            "id": brick_id,
            "type": "brick",
            "name": brick_name,
            "layer": brick_layer,
            "file": "jig/bricks.yaml",
            "jig_hash": hash_brick(brick),
            "units": brick_units,
        }

        # Add optional tower field if present (S-086)
        tower = brick.get("tower")
        if tower:
            brick_node["tower"] = tower

        # Add optional git_blob for tiered rebuild optimization (S-049)
        if bricks_git_blob:
            brick_node["git_blob"] = bricks_git_blob

        brick_nodes.append(brick_node)

    return brick_nodes


def _count_towers(brick_nodes: List[Dict[str, Any]]) -> int:
    """Count unique towers in brick nodes.

    Returns 0 for single-tower projects (no tower fields).
    """
    towers = set()
    for brick in brick_nodes:
        tower = brick.get("tower")
        if tower:
            towers.add(tower)
    return len(towers)


@jig.implements("S-083")
def _create_defines_goal_edges(charter_node: Optional[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Create Charter→Goal defines_goal edges.

    Args:
        charter_node: Charter node dictionary with defines_goals field.

    Returns:
        List of edge dictionaries with source, target, type.
    """
    if charter_node is None:
        return []

    edges = []
    goal_ids = charter_node.get("defines_goals", [])

    for goal_id in goal_ids:
        edge = {"source": "Charter", "target": goal_id, "type": "defines_goal"}
        edges.append(edge)

    return edges


@jig.implements("S-084")
def _create_supports_goal_edges(
    architecture_nodes: List[Dict[str, Any]],
    outcome_nodes: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Create A→Goal and O→Goal supports_goal edges.

    Args:
        architecture_nodes: List of architecture node dictionaries.
        outcome_nodes: List of outcome node dictionaries.

    Returns:
        List of edge dictionaries with source, target, type.
    """
    edges = []

    # Architecture→Goal edges
    for arch in architecture_nodes:
        arch_id = arch["id"]
        supports_goals = arch.get("supports_goals", [])

        for goal_id in supports_goals:
            edge = {"source": arch_id, "target": goal_id, "type": "supports_goal"}
            edges.append(edge)

    # Outcome→Goal edges
    for outcome in outcome_nodes:
        outcome_id = outcome["id"]
        supports_goals = outcome.get("supports_goals", [])

        for goal_id in supports_goals:
            edge = {"source": outcome_id, "target": goal_id, "type": "supports_goal"}
            edges.append(edge)

    return edges


@jig.implements("S-085")
def _create_constrains_edges(architecture_nodes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Create A→S constrains edges.

    Args:
        architecture_nodes: List of architecture node dictionaries.

    Returns:
        List of edge dictionaries with source, target, type.
    """
    edges = []

    for arch in architecture_nodes:
        arch_id = arch["id"]
        constrains = arch.get("constrains", [])

        for spec_id in constrains:
            edge = {"source": arch_id, "target": spec_id, "type": "constrains"}
            edges.append(edge)

    return edges


def _create_specifies_edges(outcome_nodes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Create O→S specifies edges from outcome nodes.

    Args:
        outcome_nodes: List of outcome node dictionaries.

    Returns:
        List of edge dictionaries with source, target, type.
    """
    edges = []
    for outcome in outcome_nodes:
        outcome_id = outcome["id"]
        spec_ids = outcome.get("specifies", [])

        for spec_id in spec_ids:
            edge = {"source": outcome_id, "target": spec_id, "type": "specifies"}
            edges.append(edge)

    return edges


@jig.implements("S-068")
def _generate_metadata(
    spec_count: int,
    outcome_count: int,
    brick_count: int,
    include_timestamp: bool,
    git_metadata: Optional[Dict[str, Any]] = None,
    charter_exists: bool = False,
    goal_count: int = 0,
    architecture_count: int = 0,
    tower_count: int = 0,
) -> Dict[str, Any]:
    """Generate metadata for intent graph.

    Args:
        spec_count: Number of specification nodes.
        outcome_count: Number of outcome nodes.
        brick_count: Number of brick nodes.
        include_timestamp: Whether to include generated timestamp.
        git_metadata: Optional git state metadata for staleness detection.
        charter_exists: Whether Charter.md exists.
        goal_count: Number of goal nodes.
        architecture_count: Number of architecture nodes.
        tower_count: Number of unique towers (0 for single-tower projects).

    Returns:
        Metadata dictionary with _meta key.
    """
    metadata: Dict[str, Any] = {
        "_meta": {
            "version": "2.0",
            "charter": charter_exists,
            "goal_count": goal_count,
            "architecture_count": architecture_count,
            "spec_count": spec_count,
            "outcome_count": outcome_count,
            "brick_count": brick_count,
            "tower_count": tower_count,
        }
    }

    if include_timestamp:
        metadata["_meta"]["generated"] = datetime.now(timezone.utc).isoformat()

    # Add git metadata for staleness detection (S-068)
    if git_metadata:
        metadata["_meta"]["git_head"] = git_metadata.get("git_head")
        metadata["_meta"]["git_tree_hashes"] = git_metadata.get("git_tree_hashes", {})
        metadata["_meta"]["git_dirty_files"] = git_metadata.get("git_dirty_files", [])

    return metadata


def _write_intent_graph(
    output_path: Path,
    metadata: Dict[str, Any],
    charter_node: Optional[Dict[str, Any]],
    goal_nodes: List[Dict[str, Any]],
    architecture_nodes: List[Dict[str, Any]],
    spec_nodes: List[Dict[str, Any]],
    outcome_nodes: List[Dict[str, Any]],
    brick_nodes: List[Dict[str, Any]],
    edges: List[Dict[str, str]],
) -> None:
    """Write intent graph to NDJSON file.

    Args:
        output_path: Path to write the NDJSON file.
        metadata: Metadata dictionary.
        charter_node: Charter node (may be None).
        goal_nodes: List of goal nodes.
        architecture_nodes: List of architecture nodes.
        spec_nodes: List of specification nodes.
        outcome_nodes: List of outcome nodes.
        brick_nodes: List of brick nodes.
        edges: List of edge dictionaries.
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        # Write metadata line
        f.write(json.dumps(metadata, sort_keys=True))
        f.write("\n")

        # Write charter node (if exists)
        if charter_node:
            f.write(json.dumps(charter_node, sort_keys=True))
            f.write("\n")

        # Write goal nodes (sorted by ID)
        for node in sorted(goal_nodes, key=lambda n: n["id"]):
            f.write(json.dumps(node, sort_keys=True))
            f.write("\n")

        # Write architecture nodes (sorted by ID)
        for node in sorted(architecture_nodes, key=lambda n: n["id"]):
            f.write(json.dumps(node, sort_keys=True))
            f.write("\n")

        # Write spec nodes (sorted by ID)
        for node in sorted(spec_nodes, key=lambda n: n["id"]):
            f.write(json.dumps(node, sort_keys=True))
            f.write("\n")

        # Write outcome nodes (sorted by ID)
        for node in sorted(outcome_nodes, key=lambda n: n["id"]):
            f.write(json.dumps(node, sort_keys=True))
            f.write("\n")

        # Write brick nodes (sorted by ID)
        for node in sorted(brick_nodes, key=lambda n: n["id"]):
            f.write(json.dumps(node, sort_keys=True))
            f.write("\n")

        # Write edges (sorted by source, target, type)
        for edge in sorted(edges, key=lambda e: (e["source"], e["target"], e["type"])):
            f.write(json.dumps(edge, sort_keys=True))
            f.write("\n")


def _parse_frontmatter(file_path: Path) -> Optional[dict]:
    """Parse YAML frontmatter from markdown file.

    Args:
        file_path: Path to markdown file.

    Returns:
        Frontmatter dictionary, or None if parsing fails.
    """
    try:
        content = file_path.read_text()
        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        return yaml.safe_load(parts[1])
    except Exception:
        return None
