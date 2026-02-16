# ABOUTME: Public API for the jig.query package.
# ABOUTME: Exports node resolution, graph traversal, formatting, overview, validation, and search.

"""Query layer for JIG graph exploration.

Public API:
- query_node(): One-call resolve + traverse + format
- config_to_graphs(): Map JigConfig to graph file paths
- resolve_identifier(): Parse and resolve identifiers to graph nodes
- traverse_graph(): Navigate ancestors and descendants with budget control
- format_response(): Format traversal results into structured response
- IdentifierError: Raised when identifier cannot be resolved
- build_overview() / format_overview_*(): Project overview building and formatting
- query_validate() / filter_errors_by_specs(): Scoped validation queries
- search_docs(): Text search across JIG documents
"""

from jig.query.node import (
    IdentifierError,
    config_to_graphs,
    format_response,
    query_node,
    resolve_identifier,
    traverse_graph,
)
from jig.query.overview import (
    build_overview,
    format_overview_human,
    format_overview_json,
    format_overview_markdown,
)
from jig.query.search import search_docs
from jig.query.validate import (
    BRICK_SPECS,
    INTENT_SPECS,
    filter_errors_by_specs,
    query_validate,
)

__all__ = [
    "BRICK_SPECS",
    "INTENT_SPECS",
    "IdentifierError",
    "build_overview",
    "config_to_graphs",
    "filter_errors_by_specs",
    "format_overview_human",
    "format_overview_json",
    "format_overview_markdown",
    "format_response",
    "query_node",
    "query_validate",
    "resolve_identifier",
    "search_docs",
    "traverse_graph",
]
