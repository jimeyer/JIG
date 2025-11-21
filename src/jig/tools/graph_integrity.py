# @jig C-INTEGRITY-001 implements:S-JIG-012 subsystem:jig-graph interface:public
"""Graph integrity detection for orphaned nodes.

This module provides deterministic detection of three types of graph integrity issues:
1. Dangling references: Node A references Node B, but B doesn't exist
2. Unreferenced nodes: Node exists but is never referenced
3. Malformed structures: Invalid or null relationship fields
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jig.utils.yaml_utils import load_yaml


# Relationship fields to check for references
RELATIONSHIP_FIELDS = ["implements", "specifies", "contributes_to", "depends_on"]


def check_graph_integrity(
    graph_path: Path,
    subsystems_path: Path,
    include_node_context: bool = True,
) -> dict[str, Any]:
    """Analyze graph integrity and return structured findings.

    Args:
        graph_path: Path to graph-index.yaml
        subsystems_path: Path to subsystems.yaml
        include_node_context: Include node descriptions in output

    Returns:
        Dictionary with findings, statistics, and metadata:
        {
            "timestamp": "2025-11-21T10:30:00Z",
            "graph_file": "jig/graph-index.yaml",
            "total_nodes": 42,
            "findings": {
                "dangling_references": [...],
                "unreferenced_nodes": [...],
                "malformed_structures": [...]
            },
            "statistics": {...}
        }

    Raises:
        FileNotFoundError: If graph files don't exist
        ValueError: If YAML files have invalid syntax
    """
    # Load graph data
    if not graph_path.exists():
        raise FileNotFoundError(f"Graph file not found: {graph_path}")

    if not subsystems_path.exists():
        raise FileNotFoundError(f"Subsystems file not found: {subsystems_path}")

    try:
        graph_data = load_yaml(graph_path)
        subsystems_data = load_yaml(subsystems_path)
    except Exception as e:
        raise ValueError(f"Failed to parse YAML: {e}") from e

    # Build node registry
    nodes = graph_data.get("nodes", {})
    if not nodes:
        # Empty graph
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "graph_file": str(graph_path),
            "total_nodes": 0,
            "findings": {
                "dangling_references": [],
                "unreferenced_nodes": [],
                "malformed_structures": [],
            },
            "statistics": {
                "total_relationships": 0,
                "relationship_density": 0.0,
                "node_type_distribution": {},
            },
            "message": "No nodes to analyze (empty graph)",
        }

    node_registry = set(nodes.keys())

    # Find dangling references
    dangling_references = _find_dangling_references(
        nodes, node_registry, include_node_context
    )

    # Find unreferenced nodes
    unreferenced_nodes = _find_unreferenced_nodes(
        nodes, node_registry, include_node_context
    )

    # Find malformed structures
    malformed_structures = _find_malformed_structures(nodes)

    # Calculate statistics
    statistics = _calculate_statistics(nodes)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "graph_file": str(graph_path),
        "total_nodes": len(nodes),
        "findings": {
            "dangling_references": dangling_references,
            "unreferenced_nodes": unreferenced_nodes,
            "malformed_structures": malformed_structures,
        },
        "statistics": statistics,
    }


def _find_dangling_references(
    nodes: dict[str, Any], node_registry: set[str], include_context: bool
) -> list[dict[str, Any]]:
    """Find references to non-existent nodes."""
    dangling = []

    for node_id, node_data in nodes.items():
        for field in RELATIONSHIP_FIELDS:
            if field not in node_data:
                continue

            # Handle both string and list formats
            field_value = node_data[field]
            if field_value is None:
                continue  # Handled by malformed check

            refs = field_value if isinstance(field_value, list) else [field_value]

            for ref in refs:
                if not isinstance(ref, str):
                    continue  # Handled by malformed check

                if ref not in node_registry:
                    issue = {
                        "node_id": node_id,
                        "node_type": node_data.get("type", "unknown"),
                        "field": field,
                        "missing_reference": ref,
                    }

                    if include_context:
                        issue["node_context"] = {
                            "title": node_data.get("title", ""),
                            "subsystem": node_data.get("subsystem", ""),
                        }

                    dangling.append(issue)

    return dangling


def _find_unreferenced_nodes(
    nodes: dict[str, Any], node_registry: set[str], include_context: bool
) -> list[dict[str, Any]]:
    """Find nodes that are never referenced by any other node."""
    # Build set of all referenced node IDs
    referenced_ids = set()

    for node_data in nodes.values():
        for field in RELATIONSHIP_FIELDS:
            if field not in node_data:
                continue

            field_value = node_data[field]
            if field_value is None:
                continue

            # Handle both string and list formats
            refs = field_value if isinstance(field_value, list) else [field_value]

            for ref in refs:
                if isinstance(ref, str):
                    referenced_ids.add(ref)

    # Find unreferenced nodes
    unreferenced_ids = node_registry - referenced_ids
    unreferenced = []

    for node_id in unreferenced_ids:
        node_data = nodes[node_id]
        issue = {
            "node_id": node_id,
            "node_type": node_data.get("type", "unknown"),
            "potential_reason": "isolated",
        }

        if include_context:
            issue["node_data"] = {
                "title": node_data.get("title", ""),
                "subsystem": node_data.get("subsystem", ""),
                "file": node_data.get("file", ""),
            }

            # Add hint if this looks like a root-level node
            if node_data.get("type") == "outcome":
                issue["potential_reason"] = "possibly_intentional_root"

        unreferenced.append(issue)

    return unreferenced


def _find_malformed_structures(nodes: dict[str, Any]) -> list[dict[str, Any]]:
    """Find relationship fields with null or invalid values."""
    malformed = []

    for node_id, node_data in nodes.items():
        for field in RELATIONSHIP_FIELDS:
            if field not in node_data:
                continue

            field_value = node_data[field]

            # Check for null
            if field_value is None:
                malformed.append({
                    "node_id": node_id,
                    "issue": "relationship_field_null",
                    "field": field,
                    "value": None,
                })
                continue

            # Check for empty list
            if isinstance(field_value, list) and len(field_value) == 0:
                malformed.append({
                    "node_id": node_id,
                    "issue": "relationship_field_empty_list",
                    "field": field,
                    "value": [],
                })
                continue

            # Check for invalid type (not string or list)
            if not isinstance(field_value, (str, list)):
                malformed.append({
                    "node_id": node_id,
                    "issue": "relationship_field_invalid_type",
                    "field": field,
                    "value": field_value,
                    "value_type": type(field_value).__name__,
                })
                continue

            # If it's a list, check each element is a string
            if isinstance(field_value, list):
                for idx, item in enumerate(field_value):
                    if not isinstance(item, str):
                        malformed.append({
                            "node_id": node_id,
                            "issue": "relationship_list_item_invalid_type",
                            "field": field,
                            "list_index": idx,
                            "value": item,
                            "value_type": type(item).__name__,
                        })

    return malformed


def _calculate_statistics(nodes: dict[str, Any]) -> dict[str, Any]:
    """Calculate graph statistics."""
    total_relationships = 0
    node_type_counts: dict[str, int] = {}

    for node_data in nodes.values():
        # Count relationships
        for field in RELATIONSHIP_FIELDS:
            if field in node_data and node_data[field] is not None:
                field_value = node_data[field]
                if isinstance(field_value, list):
                    total_relationships += len(field_value)
                else:
                    total_relationships += 1

        # Count node types
        node_type = node_data.get("type", "unknown")
        node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1

    # Calculate relationship density (avg relationships per node)
    relationship_density = (
        total_relationships / len(nodes) if len(nodes) > 0 else 0.0
    )

    return {
        "total_relationships": total_relationships,
        "relationship_density": round(relationship_density, 2),
        "node_type_distribution": node_type_counts,
    }
