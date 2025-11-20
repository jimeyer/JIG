# @jig C-CORE-002 implements:S-JIG-002 subsystem:core interface:internal
"""OSTC node parsing - YAML frontmatter + Markdown body."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import frontmatter  # type: ignore[import-untyped]


@dataclass
class OSTCNode:
    """Represents a parsed OSTC node (Outcome, Specification, or Constraint).

    In the OSTCX model, O/S/X nodes are markdown files (timeless intent).
    T/C nodes are discovered via @jig annotations in code (executable reality).

    Attributes:
        id: Unique identifier (e.g., O-JIG-001, S-JIG-002, C-PERF-001)
        type: Node type (outcome, specification, constraint)
        title: Human-readable title
        subsystem: Optional subsystem name (e.g., core, cli, graph)
        status: Optional status (e.g., active, deprecated, draft)
        created: Optional creation date
        updated: Optional last update date
        body: Markdown content (everything after YAML frontmatter)
        metadata: Raw frontmatter dictionary for additional fields
    """

    id: str
    type: str
    title: str
    subsystem: str | None = None
    status: str | None = None
    created: date | None = None
    updated: date | None = None
    body: str = ""
    metadata: dict[str, Any] | None = None


def parse_ostc_node(path: Path) -> OSTCNode:
    """Parse OSTC node file with YAML frontmatter + Markdown body.

    Args:
        path: Path to OSTC node file (.md file)

    Returns:
        OSTCNode object with parsed data

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required fields (id, type, title) are missing
        yaml.YAMLError: If YAML frontmatter is malformed

    Example:
        >>> node = parse_ostc_node(Path("jig/outcomes/O-JIG-001.md"))
        >>> print(node.id, node.type, node.title)
        O-JIG-001 outcome JIG tools run in <1 second for most operations
    """
    if not path.exists():
        raise FileNotFoundError(f"OSTC node file not found: {path}")

    try:
        post = frontmatter.load(path)
    except Exception as e:
        raise ValueError(f"Failed to parse frontmatter in {path}: {e}") from e

    # Extract required fields
    node_id = post.metadata.get("id")
    node_type = post.metadata.get("type")
    node_title = post.metadata.get("title")

    # Validate required fields
    if not node_id:
        raise ValueError(f"Missing required field 'id' in {path}")
    if not node_type:
        raise ValueError(f"Missing required field 'type' in {path}")
    if not node_title:
        raise ValueError(f"Missing required field 'title' in {path}")

    # Extract optional fields
    subsystem = post.metadata.get("subsystem")
    status = post.metadata.get("status")

    # Parse dates if present
    created = _parse_date(post.metadata.get("created"))
    updated = _parse_date(post.metadata.get("updated"))

    # Body is the markdown content
    body = post.content

    return OSTCNode(
        id=node_id,
        type=node_type,
        title=node_title,
        subsystem=subsystem,
        status=status,
        created=created,
        updated=updated,
        body=body,
        metadata=post.metadata,
    )


def _parse_date(value: Any) -> date | None:
    """Parse date from various formats.

    Args:
        value: Date value (can be date, str, or None)

    Returns:
        date object or None if value is None or invalid
    """
    if value is None:
        return None

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            # Try parsing ISO format: YYYY-MM-DD
            return date.fromisoformat(value)
        except ValueError:
            # If parsing fails, return None (could log warning in production)
            return None

    return None
