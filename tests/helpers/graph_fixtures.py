"""Test fixture helpers for creating valid JIG graph structures.

This module provides utilities for tests to create complete, valid graph
fixtures with both markdown files and graph-index.json.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def create_test_graph(
    tmp_path: Path,
    nodes: list[dict[str, Any]],
    subsystems: dict[str, Any] | None = None,
) -> Path:
    """Create a complete valid graph structure for testing.

    Creates:
    - jig/ directory structure
    - Markdown node files for O/S/X nodes
    - graph-index.json with all nodes
    - Subsystem definitions (if provided)

    Args:
        tmp_path: pytest tmp_path fixture
        nodes: List of node specifications, each with:
            - id: Node ID (required)
            - type: Node type (required)
            - title: Node title (required)
            - subsystem: Subsystem name (required)
            - implements: List of node IDs (optional)
            - verifies: List of node IDs (optional)
            - satisfies: List of node IDs (optional)
            - depends_on: List of node IDs (optional)
            - status: Node status (default: "active")
            - file: Source file path for C/T nodes (optional)
            - line: Line number for C/T nodes (optional)
        subsystems: Dict of subsystem definitions (optional):
            {
                "subsystem-name": {
                    "id": "subsystem-id",
                    "children": {...}  # nested subsystems
                }
            }

    Returns:
        Path to jig directory

    Example:
        >>> jig_dir = create_test_graph(tmp_path, [
        ...     {
        ...         "id": "O-TEST-001",
        ...         "type": "outcome",
        ...         "title": "Test outcome",
        ...         "subsystem": "test",
        ...     },
        ...     {
        ...         "id": "S-TEST-001",
        ...         "type": "specification",
        ...         "title": "Test spec",
        ...         "subsystem": "test",
        ...         "implements": ["O-TEST-001"],
        ...     },
        ... ], subsystems={"test": {"id": "test"}})
    """
    # Create jig directory structure
    jig_dir = tmp_path / "jig"
    jig_dir.mkdir(exist_ok=True)

    # Create subdirectories for markdown nodes
    (jig_dir / "outcomes").mkdir(exist_ok=True)
    (jig_dir / "specifications").mkdir(exist_ok=True)
    (jig_dir / "constraints").mkdir(exist_ok=True)
    (jig_dir / "subsystems").mkdir(exist_ok=True)

    # Separate nodes by type
    markdown_nodes = []  # O, S, X nodes (go in markdown files)
    index_nodes = []  # All nodes (go in graph-index.json)

    for node in nodes:
        node_type = node["type"]

        # Create markdown file for O/S/X nodes
        if node_type in ["outcome", "specification", "constraint"]:
            markdown_nodes.append(node)
            _create_markdown_node(jig_dir, node)

        # Add all nodes to index
        index_nodes.append(_build_index_node(node))

    # Create graph-index.json
    graph_index = {
        "version": "1.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "nodes": index_nodes,
    }

    # Add subsystems if provided
    if subsystems:
        graph_index["subsystems"] = subsystems

    graph_index_path = jig_dir / "graph-index.json"
    graph_index_path.write_text(json.dumps(graph_index, indent=2))

    return jig_dir


def _create_markdown_node(jig_dir: Path, node: dict[str, Any]) -> None:
    """Create a markdown node file."""
    node_type = node["type"]
    node_id = node["id"]

    # Determine directory
    type_to_dir = {
        "outcome": "outcomes",
        "specification": "specifications",
        "constraint": "constraints",
    }
    node_dir = jig_dir / type_to_dir[node_type]

    # Build frontmatter
    frontmatter = {
        "id": node_id,
        "type": node_type,
        "title": node["title"],
        "subsystem": node["subsystem"],
    }

    # Add optional fields
    if "status" in node:
        frontmatter["status"] = node["status"]
    if "implements" in node and node["implements"]:
        frontmatter["implements"] = node["implements"]
    if "verifies" in node and node["verifies"]:
        frontmatter["verifies"] = node["verifies"]
    if "satisfies" in node and node["satisfies"]:
        frontmatter["satisfies"] = node["satisfies"]
    if "depends_on" in node and node["depends_on"]:
        frontmatter["depends_on"] = node["depends_on"]

    # Format frontmatter as YAML
    yaml_lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, list):
            yaml_lines.append(f"{key}:")
            for item in value:
                yaml_lines.append(f"  - {item}")
        else:
            yaml_lines.append(f"{key}: {value}")
    yaml_lines.append("---")

    # Create markdown content
    content = "\n".join(yaml_lines) + f"\n\n# {node['title']}\n\nTest node content.\n"

    # Write file
    node_file = node_dir / f"{node_id}.md"
    node_file.write_text(content)


def _build_index_node(node: dict[str, Any]) -> dict[str, Any]:
    """Build a node entry for graph-index.json."""
    index_node = {
        "id": node["id"],
        "type": node["type"],
        "title": node["title"],
        "subsystem": node["subsystem"],
        "status": node.get("status", "active"),
    }

    # Add file/line for C/T nodes
    if node["type"] in ["code", "test"]:
        index_node["file"] = node.get("file", "")
        index_node["line"] = node.get("line", 1)

    # Add relationships
    if "implements" in node and node["implements"]:
        index_node["implements"] = node["implements"]
    if "verifies" in node and node["verifies"]:
        index_node["verifies"] = node["verifies"]
    if "satisfies" in node and node["satisfies"]:
        index_node["satisfies"] = node["satisfies"]
    if "depends_on" in node and node["depends_on"]:
        index_node["depends_on"] = node["depends_on"]

    return index_node
