"""Intent graph generator.

Generates intent-graph.ndjson from specifications, outcomes, and bricks.yaml
per A001 §6.1.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

import jig
from jig.hashing import hash_brick, hash_intent_artifact


@jig.implements("S-028", "S-050")
def generate_intent_graph(
    project_root: Path,
    output_path: Optional[Path] = None,
    include_timestamp: bool = True,
) -> tuple[Path, int, int]:
    """Generate intent-graph.ndjson from intent artifacts.

    Args:
        project_root: Root directory of the project.
        output_path: Path to write the intent graph. Defaults to
            <project_root>/jig/generated/intent-graph.ndjson.
        include_timestamp: Whether to include generated timestamp in metadata.
            Defaults to True.

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
    spec_dir = project_root / "jig" / "specifications"
    outcome_dir = project_root / "jig" / "outcomes"
    bricks_file = project_root / "jig" / "bricks.yaml"

    # Load spec nodes
    spec_nodes = _load_specification_nodes(spec_dir)

    # Load outcome nodes (optional)
    outcome_nodes = _load_outcome_nodes(outcome_dir)

    # Load brick nodes
    brick_nodes = _load_brick_nodes(bricks_file)

    # Create edges from outcome.specifies relationships
    edges = _create_specifies_edges(outcome_nodes)

    # Calculate counts
    node_count = len(spec_nodes) + len(outcome_nodes) + len(brick_nodes)
    edge_count = len(edges)

    # Generate metadata
    metadata = _generate_metadata(
        spec_count=len(spec_nodes),
        outcome_count=len(outcome_nodes),
        brick_count=len(brick_nodes),
        include_timestamp=include_timestamp,
    )

    # Write NDJSON file
    _write_intent_graph(
        output_path=output_path,
        metadata=metadata,
        spec_nodes=spec_nodes,
        outcome_nodes=outcome_nodes,
        brick_nodes=brick_nodes,
        edges=edges,
    )

    return output_path, node_count, edge_count


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

        outcome_nodes.append(outcome_node)

    return outcome_nodes


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

    brick_nodes = []
    for brick in bricks:
        brick_id = brick.get("id")
        brick_name = brick.get("name")
        brick_units = brick.get("units", [])

        if not brick_id or not brick_name:
            continue

        brick_node = {
            "id": brick_id,
            "type": "brick",
            "name": brick_name,
            "file": "jig/bricks.yaml",
            "jig_hash": hash_brick(brick),
            "units": brick_units,
        }

        brick_nodes.append(brick_node)

    return brick_nodes


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


def _generate_metadata(
    spec_count: int,
    outcome_count: int,
    brick_count: int,
    include_timestamp: bool,
) -> Dict[str, Any]:
    """Generate metadata for intent graph.

    Args:
        spec_count: Number of specification nodes.
        outcome_count: Number of outcome nodes.
        brick_count: Number of brick nodes.
        include_timestamp: Whether to include generated timestamp.

    Returns:
        Metadata dictionary with _meta key.
    """
    metadata: Dict[str, Any] = {
        "_meta": {
            "version": "1.0",
            "spec_count": spec_count,
            "outcome_count": outcome_count,
            "brick_count": brick_count,
        }
    }

    if include_timestamp:
        metadata["_meta"]["generated"] = datetime.now(timezone.utc).isoformat()

    return metadata


def _write_intent_graph(
    output_path: Path,
    metadata: Dict[str, Any],
    spec_nodes: List[Dict[str, Any]],
    outcome_nodes: List[Dict[str, Any]],
    brick_nodes: List[Dict[str, Any]],
    edges: List[Dict[str, str]],
) -> None:
    """Write intent graph to NDJSON file.

    Args:
        output_path: Path to write the NDJSON file.
        metadata: Metadata dictionary.
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
