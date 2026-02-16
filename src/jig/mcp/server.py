# ABOUTME: FastMCP server exposing JIG query layer as MCP tools.
# ABOUTME: Four read-only tools: lookup_node, search_docs, get_overview, validate_project.

"""MCP server for LLM agent access to JIG (S-117).

Provides four read-only tools over stdio transport:
- lookup_node: Resolve identifier to graph neighborhood
- search_docs: Text search across JIG corpus
- get_overview: Project overview
- validate_project: Run validation
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

import jig

mcp = FastMCP(name="jig")


def _get_config() -> Any:
    """Load JIG config from current working directory."""
    from jig.config import load_config

    return load_config()


@jig.implements("S-117")
def lookup_node(node_id: str) -> dict:
    """Look up a JIG node by identifier and return its graph neighborhood.

    Args:
        node_id: Identifier like S-042, O-001, B-cli, F-module.func, Charter

    Returns:
        Dict with root, nodes, more fields — or empty dict if not found.
    """
    from jig.query import query_node

    config = _get_config()
    return query_node(node_id, config)


@jig.implements("S-117")
def search_docs(query: str, limit: int = 20) -> list:
    """Search across JIG specifications, outcomes, and architecture docs.

    Args:
        query: Text to search for (case-insensitive substring match)
        limit: Maximum results to return (default 20)

    Returns:
        List of matching documents with id, title, path, and matching line.
    """
    from jig.query import search_docs as _search_docs

    config = _get_config()
    return _search_docs(query, config, limit=limit)


@jig.implements("S-117")
def get_overview() -> dict:
    """Get unified project overview including charter, goals, specs, bricks.

    Returns:
        Dict with charter, goals, architecture, outcomes, specs, bricks_by_layer, etc.
    """
    from jig.query import build_overview

    config = _get_config()
    return build_overview(config)


@jig.implements("S-117")
def validate_project(scope: str = "full") -> dict:
    """Run JIG validation and return results.

    Args:
        scope: "full" (default), "intent", or "bricks"

    Returns:
        Dict with errors list and summary.
    """
    from jig.query import query_validate

    config = _get_config()
    return query_validate(config, scope)


# Register functions as MCP tools.
# Done after definition so @jig.implements sees the raw function (preserving
# callability) and FastMCP sees the type annotations.
mcp.tool()(lookup_node)
mcp.tool()(search_docs)
mcp.tool()(get_overview)
mcp.tool()(validate_project)


def run_server() -> None:
    """Start the MCP server with stdio transport."""
    mcp.run()
