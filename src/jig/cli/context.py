# ABOUTME: Context module for identifier resolution and graph traversal.
# ABOUTME: Resolves S-###, O-###, G-###, A-###, B-*, F-*, T-*, Charter, and file paths to graph nodes.

"""Context module for graph neighborhood exploration (S-111, S-112).

This module provides:
- resolve_identifier(): Parse identifiers and resolve to graph nodes
- traverse_graph(): Navigate ancestors and descendants with budget control
"""

from __future__ import annotations

import json
from pathlib import Path

import jig

# Re-exports from query layer for backwards compatibility
from jig.query.node import (  # noqa: F401
    EDGE_DIRECTIONS,
    EDGE_TO_PARENT,
    PATTERNS,
    VALID_PATTERNS,
    IdentifierError,
    _build_adjacency,
    _collect_ancestors,
    _collect_descendants_breadth_first,
    _compute_depths,
    _get_edge_type_for_node,
    _load_all_graphs,
    _load_graph,
    _match_pattern,
    config_to_graphs,
    format_human,
    format_markdown,
    format_response,
    resolve_identifier,
    traverse_graph,
)


@jig.implements("S-110")
def context_command(
    identifier: str | None,
    project_root: Path,
    max_nodes: int = 50,
    output_format: str = "human",
    verbose: bool = False,
    skip_rebuild: bool = False,
) -> tuple[int, str]:
    """Execute context command and return exit code and output.

    Supports three modes per S-110:
    - Bare mode: No identifier -> Project Overview (S-114)
    - Traversal mode: Valid identifier -> Graph neighborhood
    - Fallback mode: Invalid identifier -> Overview + "not found" note

    Args:
        identifier: Node identifier to explore, or None for overview
        project_root: Project root directory
        max_nodes: Maximum nodes in response (traversal mode only)
        output_format: Output format (human, json, markdown)
        verbose: Include additional detail
        skip_rebuild: Skip auto-rebuild before operation

    Returns:
        Tuple of (exit_code, output_string)
    """
    from jig.cli.auto_rebuild import ensure_graphs_current
    from jig.config.schema import load_config
    from jig.query.overview import (
        build_overview,
        format_overview_human,
        format_overview_json,
        format_overview_markdown,
    )

    # Load config for overview functions
    config = load_config(project_root)

    # Build graph paths for traversal
    graphs = config_to_graphs(config)

    # BARE MODE: No identifier -> return overview
    if not identifier:
        ensure_graphs_current(["impl", "verify", "intent"], config, skip_rebuild=skip_rebuild)
        overview = build_overview(config)
        if output_format == "json":
            return 0, format_overview_json(overview)
        elif output_format == "markdown":
            return 0, format_overview_markdown(overview, verbose=verbose)
        else:
            return 0, format_overview_human(overview, verbose=verbose)

    # TRAVERSAL MODE: Try to resolve and traverse
    try:
        ensure_graphs_current(["impl", "verify", "intent"], config, skip_rebuild=skip_rebuild)
        traversal_result = traverse_graph(identifier, graphs, max_nodes)
        _, all_edges = _load_all_graphs(graphs)
        response = format_response(traversal_result, all_edges)

        # Format output based on requested format
        if output_format == "json":
            output = json.dumps(response)
        elif output_format == "markdown":
            output = format_markdown(response)
        else:
            output = format_human(response)

        return 0, output

    except IdentifierError as e:
        # FALLBACK MODE: Return overview + note per S-111
        error_str = str(e)
        if "not found" in error_str.lower():
            note = f'"{identifier}" not found in project.'
        elif "not a valid" in error_str.lower():
            note = f'"{identifier}" is not a jig node.'
        else:
            note = f'"{identifier}" could not be resolved.'

        overview = build_overview(config)
        if output_format == "json":
            overview["note"] = note
            return 0, format_overview_json(overview)
        elif output_format == "markdown":
            output = f"> **Note:** {note}\n\n{format_overview_markdown(overview, verbose=verbose)}"
            return 0, output
        else:
            output = f"Note: {note}\n\n{format_overview_human(overview, verbose=verbose)}"
            return 0, output
