"""In-memory graph representation for implementation graph.

This module provides a simple in-memory representation of the implementation
graph, collecting nodes and edges before serialization to NDJSON.
"""

from typing import Any, Dict, List

import jig


@jig.implements("S-003")
class Graph:
    """In-memory representation of an implementation graph.

    Collects nodes (modules, classes, functions) and edges (relationships)
    for eventual serialization to NDJSON format.
    """

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []

    def add_node(self, node: Dict[str, Any]) -> None:
        """Add a node to the graph.

        Args:
            node: Node dictionary with at least 'id', 'type', 'language' fields.
        """
        self.nodes.append(node)

    def add_edge(self, edge: Dict[str, Any]) -> None:
        """Add an edge to the graph.

        Args:
            edge: Edge dictionary with 'source', 'target', 'type' fields.
        """
        self.edges.append(edge)

    def add_nodes(self, nodes: List[Dict[str, Any]]) -> None:
        """Add multiple nodes to the graph.

        Args:
            nodes: List of node dictionaries.
        """
        self.nodes.extend(nodes)

    def add_edges(self, edges: List[Dict[str, Any]]) -> None:
        """Add multiple edges to the graph.

        Args:
            edges: List of edge dictionaries.
        """
        self.edges.extend(edges)

    def node_count(self) -> int:
        """Return the number of nodes in the graph.

        Returns:
            Number of nodes.
        """
        return len(self.nodes)

    def edge_count(self) -> int:
        """Return the number of edges in the graph.

        Returns:
            Number of edges.
        """
        return len(self.edges)

    def get_nodes(self) -> List[Dict[str, Any]]:
        """Return all nodes in the graph.

        Returns:
            List of all node dictionaries.
        """
        return self.nodes

    def get_edges(self) -> List[Dict[str, Any]]:
        """Return all edges in the graph.

        Returns:
            List of all edge dictionaries.
        """
        return self.edges

    def clear(self) -> None:
        """Clear all nodes and edges from the graph."""
        self.nodes.clear()
        self.edges.clear()
