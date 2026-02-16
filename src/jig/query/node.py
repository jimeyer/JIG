# ABOUTME: Query layer for node resolution, graph traversal, and response formatting.
# ABOUTME: Provides config_to_graphs() and query_node() as the primary public API.

"""Query layer for graph neighborhood exploration (S-111, S-112, S-113).

This module provides:
- resolve_identifier(): Parse identifiers and resolve to graph nodes
- traverse_graph(): Navigate ancestors and descendants with budget control
- format_response(): Format traversal results into structured response
- config_to_graphs(): Map JigConfig to graph file paths
- query_node(): Convenience wrapper composing resolve -> traverse -> format
"""

from __future__ import annotations

import json
import re
from collections import deque
from pathlib import Path
from typing import Any

import jig

# Identifier patterns per S-111
PATTERNS = {
    "specification": re.compile(r"^S-(\d+)$"),
    "outcome": re.compile(r"^O-(\d+)$"),
    "goal": re.compile(r"^G-(\d+)$"),
    "architecture": re.compile(r"^A-(\d+)$"),
    "brick": re.compile(r"^B-([\w-]+)$"),
    "function": re.compile(r"^F-(.+)$"),
    "test": re.compile(r"^T-(.+)$"),
    "charter": re.compile(r"^Charter$"),
}

# Valid pattern examples for error messages
VALID_PATTERNS = [
    "S-### (specification)",
    "O-### (outcome)",
    "G-### (goal)",
    "A-### (architecture)",
    "B-* (brick)",
    "F-* (function)",
    "T-* (test)",
    "Charter",
    "file path (e.g., src/jig/cli/main.py)",
]


class IdentifierError(Exception):
    """Raised when identifier cannot be resolved."""

    pass


def _load_graph(path: Path) -> tuple[dict[str, dict], list[dict]]:
    """Load NDJSON graph file, returning (nodes_by_id, edges)."""
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    if not path.exists():
        return nodes, edges

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "_meta" in obj:
                continue  # Skip metadata line
            if "source" in obj and "target" in obj:
                edges.append(obj)
            elif "id" in obj:
                nodes[obj["id"]] = obj

    return nodes, edges


def _load_all_graphs(
    graphs: dict[str, Path],
) -> tuple[dict[str, dict], list[dict]]:
    """Load all three graphs and merge into unified index."""
    all_nodes: dict[str, dict] = {}
    all_edges: list[dict] = []

    for graph_path in [graphs["intent"], graphs["impl"], graphs["verify"]]:
        nodes, edges = _load_graph(graph_path)
        all_nodes.update(nodes)
        all_edges.extend(edges)

    return all_nodes, all_edges


def _match_pattern(identifier: str) -> tuple[str | None, str]:
    """Match identifier against known patterns.

    Returns (node_type, matched_id) or (None, identifier) if no match.
    """
    for node_type, pattern in PATTERNS.items():
        match = pattern.match(identifier)
        if match:
            return node_type, identifier
    return None, identifier


@jig.implements("S-111")
def resolve_identifier(
    identifier: str, graphs: dict[str, Path]
) -> dict | list[dict]:
    """Resolve an identifier to graph node(s).

    Args:
        identifier: Pattern-based ID (S-###, O-###, etc.) or file path
        graphs: Dict with 'intent', 'impl', 'verify' keys pointing to graph paths

    Returns:
        Single node dict for ID patterns, list of nodes for file paths

    Raises:
        IdentifierError: If identifier cannot be resolved
    """
    all_nodes, _ = _load_all_graphs(graphs)

    # Try pattern matching first
    node_type, matched_id = _match_pattern(identifier)

    if node_type is not None:
        # Pattern matched - look up by ID
        if matched_id in all_nodes:
            return all_nodes[matched_id]
        raise IdentifierError(
            f"Identifier '{matched_id}' not found in graphs. "
            f"No {node_type} node with this ID exists."
        )

    # Check if it's a file path
    project_root = graphs.get("project_root", Path.cwd())
    file_path = Path(identifier)

    # Try as relative path from project root
    if not file_path.is_absolute():
        full_path = project_root / file_path
    else:
        full_path = file_path

    # Check if file exists OR if we have nodes with this file field
    # (for testing with synthetic graphs that don't have real files)
    matching_nodes = [
        node for node in all_nodes.values() if node.get("file") == identifier
    ]

    if matching_nodes:
        return matching_nodes

    if full_path.exists():
        # File exists but no nodes - return empty list
        return []

    # Not a valid pattern or existing file
    patterns_list = "\n  ".join(VALID_PATTERNS)
    raise IdentifierError(
        f"Cannot resolve '{identifier}'. Not a valid identifier pattern or existing file.\n"
        f"Valid patterns:\n  {patterns_list}"
    )


# Edge direction table per S-112
# For each edge type, which end is the "parent" (toward Charter)?
# source_is_parent=True means traversing source->target goes DOWN
# source_is_parent=False means traversing source->target goes UP
EDGE_DIRECTIONS = {
    "defines_goal": {"source_is_parent": True},  # Charter -> Goal
    "supports_goal": {"source_is_parent": False},  # O/A -> Goal (Goal is parent)
    "specifications": {"source_is_parent": True},  # A -> S
    "specifies": {"source_is_parent": True},  # O -> S
    "implements": {"source_is_parent": False},  # F -> S (S is parent)
    "verifies": {"source_is_parent": False},  # T -> S (S is parent)
}


def _build_adjacency(
    edges: list[dict],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Build parent and child adjacency lists from edges.

    Returns (parents_of, children_of) dicts.
    """
    parents_of: dict[str, list[str]] = {}
    children_of: dict[str, list[str]] = {}

    for edge in edges:
        edge_type = edge.get("type", "")
        source = edge.get("source", "")
        target = edge.get("target", "")

        if not source or not target:
            continue

        direction = EDGE_DIRECTIONS.get(edge_type, {"source_is_parent": True})

        if direction["source_is_parent"]:
            # source is parent of target
            parents_of.setdefault(target, []).append(source)
            children_of.setdefault(source, []).append(target)
        else:
            # target is parent of source
            parents_of.setdefault(source, []).append(target)
            children_of.setdefault(target, []).append(source)

    return parents_of, children_of


def _collect_ancestors(
    node_id: str, parents_of: dict[str, list[str]], all_nodes: dict[str, dict]
) -> list[dict]:
    """Collect all ancestors by following parent edges.

    Uses BFS to get all ancestors. Graph is bounded upward (~5 hops max).
    """
    ancestors = []
    visited = {node_id}
    queue = deque(parents_of.get(node_id, []))

    while queue:
        parent_id = queue.popleft()
        if parent_id in visited:
            continue
        visited.add(parent_id)

        if parent_id in all_nodes:
            ancestors.append(all_nodes[parent_id])

        # Add grandparents
        for grandparent in parents_of.get(parent_id, []):
            if grandparent not in visited:
                queue.append(grandparent)

    return ancestors


def _collect_descendants_breadth_first(
    node_id: str,
    children_of: dict[str, list[str]],
    all_nodes: dict[str, dict],
    budget: int,
) -> tuple[list[dict], list[dict], int]:
    """Collect descendants breadth-first up to budget.

    Returns (immediate_children, deeper_descendants, more_count).
    """
    immediate_children = []
    deeper_descendants = []
    visited = {node_id}

    # First, get immediate children (always included)
    child_ids = children_of.get(node_id, [])
    for child_id in child_ids:
        if child_id not in visited and child_id in all_nodes:
            visited.add(child_id)
            immediate_children.append(all_nodes[child_id])

    # Track remaining budget after children
    used = len(immediate_children)

    # BFS for deeper descendants
    queue = deque()  # (node_id, depth)
    for child_id in child_ids:
        for grandchild in children_of.get(child_id, []):
            if grandchild not in visited:
                queue.append((grandchild, 2))

    # Collect deeper descendants up to budget
    while queue and used < budget:
        desc_id, depth = queue.popleft()
        if desc_id in visited:
            continue
        visited.add(desc_id)

        if desc_id in all_nodes:
            deeper_descendants.append(all_nodes[desc_id])
            used += 1

        # Add next level
        for next_child in children_of.get(desc_id, []):
            if next_child not in visited:
                queue.append((next_child, depth + 1))

    # Count remaining (not visited yet)
    more_count = 0
    remaining_queue = deque(queue)
    remaining_visited = set(visited)
    while remaining_queue:
        desc_id, _ = remaining_queue.popleft()
        if desc_id in remaining_visited:
            continue
        remaining_visited.add(desc_id)
        if desc_id in all_nodes:
            more_count += 1
        for next_child in children_of.get(desc_id, []):
            if next_child not in remaining_visited:
                remaining_queue.append((next_child, 0))

    return immediate_children, deeper_descendants, more_count


@jig.implements("S-112")
def traverse_graph(
    identifier: str, graphs: dict[str, Path], max_nodes: int = 50
) -> dict[str, Any]:
    """Traverse graph from a node, collecting ancestors and descendants.

    Args:
        identifier: Starting node identifier
        graphs: Dict with graph paths
        max_nodes: Maximum total nodes in response

    Returns:
        Dict with root, ancestors, children, descendants, and more count
    """
    all_nodes, all_edges = _load_all_graphs(graphs)

    # Resolve the root node
    resolved = resolve_identifier(identifier, graphs)
    if isinstance(resolved, list):
        if not resolved:
            raise IdentifierError(f"No nodes found for '{identifier}'")
        # For file paths, use first node as root
        root_node = resolved[0]
    else:
        root_node = resolved

    root_id = root_node["id"]

    # Build adjacency
    parents_of, children_of = _build_adjacency(all_edges)

    # Collect ancestors (always all of them per S-112)
    ancestors = _collect_ancestors(root_id, parents_of, all_nodes)

    # Calculate remaining budget after root + ancestors
    # Budget: root (1) + ancestors + children + descendants <= max_nodes
    ancestor_count = len(ancestors)
    remaining_budget = max_nodes - 1 - ancestor_count

    # Collect descendants with remaining budget
    if remaining_budget > 0:
        children, descendants, more = _collect_descendants_breadth_first(
            root_id, children_of, all_nodes, remaining_budget
        )
    else:
        children = []
        descendants = []
        # Count all potential descendants as 'more'
        _, _, more = _collect_descendants_breadth_first(
            root_id, children_of, all_nodes, 0
        )

    return {
        "root": root_node,
        "ancestors": ancestors,
        "children": children,
        "descendants": descendants,
        "more": more,
    }


# Edge type to parent edge name mapping
# These are the edge names used in the JSON output
EDGE_TO_PARENT = {
    "defines_goal": "parent",  # Charter defines goal -> goal's parent edge
    "supports_goal": "parent",  # O/A supports goal -> O/A's parent edge
    "specifies": "parent",  # O specifies S -> S's parent edge
    "specifications": "parent",  # A has specifications -> S's parent edge
    "implements": "implements",  # F implements S -> F's edge is "implements"
    "verifies": "verifies",  # T verifies S -> T's edge is "verifies"
}


def _compute_depths(
    root_id: str,
    parents_of: dict[str, list[str]],
    children_of: dict[str, list[str]],
    all_nodes: dict[str, dict],
) -> dict[str, int]:
    """Compute depth from root for all reachable nodes.

    Negative depths are ancestors, positive are descendants.
    """
    depths: dict[str, int] = {root_id: 0}

    # BFS for ancestors (negative depths)
    visited_up = {root_id}
    queue = deque([(p, -1) for p in parents_of.get(root_id, [])])
    while queue:
        node_id, depth = queue.popleft()
        if node_id in visited_up:
            continue
        visited_up.add(node_id)
        depths[node_id] = depth
        for parent in parents_of.get(node_id, []):
            if parent not in visited_up:
                queue.append((parent, depth - 1))

    # BFS for descendants (positive depths)
    visited_down = {root_id}
    queue = deque([(c, 1) for c in children_of.get(root_id, [])])
    while queue:
        node_id, depth = queue.popleft()
        if node_id in visited_down:
            continue
        visited_down.add(node_id)
        depths[node_id] = depth
        for child in children_of.get(node_id, []):
            if child not in visited_down:
                queue.append((child, depth + 1))

    return depths


def _get_edge_type_for_node(
    node_id: str,
    root_id: str,
    depth: int,
    all_edges: list[dict],
) -> str:
    """Determine the edge type connecting this node toward root.

    For ancestors (depth < 0), find the edge where node is the parent.
    For descendants (depth > 0), find the edge where node is the child.
    """
    if depth < 0:
        # Ancestor - find edge where this node connects to its child (toward root)
        for edge in all_edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            edge_type = edge.get("type", "")

            direction = EDGE_DIRECTIONS.get(edge_type, {"source_is_parent": True})
            if direction["source_is_parent"]:
                # source is parent, target is child
                if source == node_id:
                    return "parent"
            else:
                # target is parent, source is child
                if target == node_id:
                    return "parent"
        return "parent"  # Default for ancestors

    else:
        # Descendant - find edge where this node connects to its parent (toward root)
        for edge in all_edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            edge_type = edge.get("type", "")

            direction = EDGE_DIRECTIONS.get(edge_type, {"source_is_parent": True})
            if direction["source_is_parent"]:
                # source is parent, target is child
                if target == node_id:
                    return edge_type
            else:
                # target is parent, source is child
                if source == node_id:
                    return edge_type
        return "child"  # Default for descendants


@jig.implements("S-113")
def format_response(
    traversal_result: dict[str, Any],
    all_edges: list[dict],
) -> dict[str, Any]:
    """Format traversal result into S-113 response schema.

    Args:
        traversal_result: Output from traverse_graph()
        all_edges: All edges from graphs (for edge type lookup)

    Returns:
        Dict matching S-113 schema with root, nodes, more fields
    """
    root_node = traversal_result["root"]
    root_id = root_node["id"]

    # Build adjacency for depth computation
    parents_of, children_of = _build_adjacency(all_edges)

    # Compute depths
    all_nodes_map = {root_id: root_node}
    for node in traversal_result.get("ancestors", []):
        all_nodes_map[node["id"]] = node
    for node in traversal_result.get("children", []):
        all_nodes_map[node["id"]] = node
    for node in traversal_result.get("descendants", []):
        all_nodes_map[node["id"]] = node

    depths = _compute_depths(root_id, parents_of, children_of, all_nodes_map)

    # Build flat node list
    nodes = []
    for node in (
        traversal_result.get("ancestors", [])
        + traversal_result.get("children", [])
        + traversal_result.get("descendants", [])
    ):
        node_id = node["id"]
        depth = depths.get(node_id, 0)
        edge_type = _get_edge_type_for_node(node_id, root_id, depth, all_edges)

        nodes.append(
            {
                "id": node_id,
                "type": node.get("type", "unknown"),
                "file": node.get("file", ""),
                "edge": edge_type,
                "depth": depth,
            }
        )

    # Sort by depth (ancestors first), then by ID
    nodes.sort(key=lambda n: (n["depth"], n["id"]))

    return {
        "root": root_id,
        "nodes": nodes,
        "more": traversal_result.get("more", 0),
    }


def format_human(response: dict[str, Any]) -> str:
    """Format response for human-readable terminal output."""
    lines = []
    root = response["root"]
    lines.append(f"Context for: {root}")
    lines.append("")

    # Group by depth
    ancestors = [n for n in response["nodes"] if n["depth"] < 0]
    descendants = [n for n in response["nodes"] if n["depth"] > 0]

    if ancestors:
        lines.append("Ancestors:")
        for node in ancestors:
            indent = "  " * abs(node["depth"])
            lines.append(f"{indent}{node['id']} ({node['type']})")
        lines.append("")

    if descendants:
        lines.append("Descendants:")
        for node in descendants:
            indent = "  " * node["depth"]
            edge_info = f" [{node['edge']}]" if node["edge"] != "child" else ""
            lines.append(f"{indent}{node['id']} ({node['type']}){edge_info}")
        lines.append("")

    more = response.get("more", 0)
    if more > 0:
        lines.append(f"... and {more} more descendants (use --max to increase)")

    return "\n".join(lines)


def format_markdown(response: dict[str, Any]) -> str:
    """Format response for LLM-optimized markdown output."""
    lines = []
    root = response["root"]
    lines.append(f"# Context: {root}")
    lines.append("")

    ancestors = [n for n in response["nodes"] if n["depth"] < 0]
    descendants = [n for n in response["nodes"] if n["depth"] > 0]

    if ancestors:
        lines.append("## Ancestors")
        lines.append("")
        lines.append("| ID | Type | File | Depth |")
        lines.append("|---|---|---|---|")
        for node in ancestors:
            lines.append(
                f"| {node['id']} | {node['type']} | {node['file']} | {node['depth']} |"
            )
        lines.append("")

    if descendants:
        lines.append("## Descendants")
        lines.append("")
        lines.append("| ID | Type | File | Edge | Depth |")
        lines.append("|---|---|---|---|---|")
        for node in descendants:
            lines.append(
                f"| {node['id']} | {node['type']} | {node['file']} | {node['edge']} | {node['depth']} |"
            )
        lines.append("")

    more = response.get("more", 0)
    if more > 0:
        lines.append(f"*{more} more descendants not shown*")

    return "\n".join(lines)


def config_to_graphs(config: Any) -> dict[str, Path]:
    """Build graphs dict from JigConfig.

    Maps config.paths.generated to the three graph file paths
    and includes project_root for file path resolution.

    Args:
        config: JigConfig instance (or any object with paths.generated and project_root)

    Returns:
        Dict with 'intent', 'impl', 'verify', 'project_root' keys
    """
    return {
        "intent": config.paths.generated / "intent-graph.ndjson",
        "impl": config.paths.generated / "implementation-graph.ndjson",
        "verify": config.paths.generated / "verification-graph.ndjson",
        "project_root": config.project_root,
    }


def query_node(identifier: str, config: Any) -> dict[str, Any]:
    """Resolve, traverse, and format a node's neighborhood in one call.

    Convenience wrapper that composes config_to_graphs -> traverse_graph ->
    format_response. Returns {} on any IdentifierError (not found, invalid pattern).

    Args:
        identifier: Node identifier (S-###, O-###, file path, etc.)
        config: JigConfig instance

    Returns:
        Formatted response dict with root/nodes/more, or {} if not found
    """
    graphs = config_to_graphs(config)
    try:
        traversal = traverse_graph(identifier, graphs)
    except IdentifierError:
        return {}
    _, all_edges = _load_all_graphs(graphs)
    return format_response(traversal, all_edges)
