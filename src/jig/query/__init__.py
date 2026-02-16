# ABOUTME: Public API for the jig.query package.
# ABOUTME: Exports node resolution, graph traversal, formatting, and convenience wrappers.

"""Query layer for JIG graph exploration.

Public API:
- query_node(): One-call resolve + traverse + format
- config_to_graphs(): Map JigConfig to graph file paths
- resolve_identifier(): Parse and resolve identifiers to graph nodes
- traverse_graph(): Navigate ancestors and descendants with budget control
- format_response(): Format traversal results into structured response
- IdentifierError: Raised when identifier cannot be resolved
"""

from jig.query.node import (
    IdentifierError,
    config_to_graphs,
    format_response,
    query_node,
    resolve_identifier,
    traverse_graph,
)

__all__ = [
    "IdentifierError",
    "config_to_graphs",
    "format_response",
    "query_node",
    "resolve_identifier",
    "traverse_graph",
]
