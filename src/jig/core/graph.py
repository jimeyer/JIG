# @jig C-GRAPH-001 implements:S-GRAPH-002 subsystem:core interface:internal
"""Graph data structures and operations for the Intent Graph.

This module provides the core Graph class and related data structures for
loading, querying, and analyzing the Intent Graph.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import networkx as nx  # type: ignore[import-untyped]

from jig.core.parser import OSTCNode, parse_ostc_node
from jig.utils.yaml_utils import load_yaml


@dataclass
class Edge:
    """Represents a directed edge in the Intent Graph.

    Attributes:
        from_node: Source node ID
        to_node: Target node ID
        type: Edge type (implements, verifies, depends_on, etc.)
    """

    from_node: str
    to_node: str
    type: str


@dataclass
class Subsystem:
    """Represents a subsystem grouping of nodes.

    Attributes:
        name: Subsystem name (e.g., core, cli, graph)
        nodes: List of node IDs in this subsystem
    """

    name: str
    nodes: list[str] = field(default_factory=list)


@dataclass
class Graph:
    """Represents the complete Intent Graph.

    Attributes:
        nodes: Dictionary mapping node ID to OSTCNode
        edges: List of edges in the graph
        subsystems: Dictionary mapping subsystem name to Subsystem
    """

    nodes: dict[str, OSTCNode] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    subsystems: dict[str, Subsystem] = field(default_factory=dict)

    @staticmethod
    def load_from_dir(intent_dir: Path) -> "Graph":
        """Load entire graph from jig/ directory.

        This loads:
        1. All OSTC nodes from outcomes/, specifications/, constraints/, tests/
        2. Edges and subsystems from graph-index.yaml

        Args:
            intent_dir: Path to jig/ directory (e.g., /path/to/project/jig/)

        Returns:
            Graph object with all loaded nodes, edges, and subsystems

        Raises:
            FileNotFoundError: If intent_dir doesn't exist
            ValueError: If graph-index.yaml is malformed or nodes are invalid

        Example:
            >>> graph = Graph.load_from_dir(Path("jig/"))
            >>> print(len(graph.nodes))
            15
        """
        if not intent_dir.exists():
            raise FileNotFoundError(f"Intent directory not found: {intent_dir}")

        graph = Graph()

        # Load all OSTC node files
        node_dirs = ["outcomes", "specifications", "constraints", "tests"]
        for node_dir in node_dirs:
            dir_path = intent_dir / node_dir
            if not dir_path.exists():
                # Directory might not exist yet (e.g., tests/)
                continue

            # Load all .md files in this directory
            for md_file in dir_path.glob("*.md"):
                try:
                    node = parse_ostc_node(md_file)
                    graph.nodes[node.id] = node
                except (FileNotFoundError, ValueError) as e:
                    # Log warning but continue (could use logging in production)
                    # For now, we'll be strict and raise
                    raise ValueError(f"Failed to parse {md_file}: {e}") from e

        # Load graph-index.yaml if it exists
        graph_index_path = intent_dir / "graph-index.yaml"
        if graph_index_path.exists():
            try:
                index_data = load_yaml(graph_index_path)

                # Load edges
                edges_data = index_data.get("edges", [])
                for edge_dict in edges_data:
                    edge = Edge(
                        from_node=edge_dict["from"],
                        to_node=edge_dict["to"],
                        type=edge_dict["type"],
                    )
                    graph.edges.append(edge)

                # Load subsystems
                subsystems_data = index_data.get("subsystems", {})
                for subsystem_name, subsystem_dict in subsystems_data.items():
                    subsystem = Subsystem(
                        name=subsystem_name,
                        nodes=subsystem_dict.get("nodes", []),
                    )
                    graph.subsystems[subsystem_name] = subsystem

            except Exception as e:
                raise ValueError(f"Failed to load graph-index.yaml: {e}") from e

        return graph

    def get_node_counts_by_type(self) -> dict[str, int]:
        """Return counts of nodes grouped by type.

        Returns:
            Dictionary mapping node type to count
            Example: {"outcome": 5, "specification": 12, "test": 8}
        """
        counts: dict[str, int] = {}
        for node in self.nodes.values():
            node_type = node.type
            counts[node_type] = counts.get(node_type, 0) + 1
        return counts

    def get_nodes_by_subsystem(self) -> dict[str, list[str]]:
        """Return nodes grouped by subsystem.

        This uses the subsystem field from each node's metadata,
        NOT the subsystems defined in graph-index.yaml.

        Returns:
            Dictionary mapping subsystem name to list of node IDs
            Example: {"core": ["O-JIG-001", "S-JIG-002"], "cli": ["S-CLI-001"]}
        """
        subsystem_nodes: dict[str, list[str]] = {}
        for node_id, node in self.nodes.items():
            if node.subsystem:
                if node.subsystem not in subsystem_nodes:
                    subsystem_nodes[node.subsystem] = []
                subsystem_nodes[node.subsystem].append(node_id)
        return subsystem_nodes

    def find_orphaned_nodes(self) -> list[str]:
        """Find nodes not connected to any edges.

        A node is orphaned if it doesn't appear in any edge
        (neither as source nor target).

        Returns:
            List of orphaned node IDs, sorted alphabetically
        """
        # Collect all nodes that appear in edges
        connected_nodes = set()
        for edge in self.edges:
            connected_nodes.add(edge.from_node)
            connected_nodes.add(edge.to_node)

        # Find nodes that don't appear in any edge
        orphaned = [node_id for node_id in self.nodes.keys() if node_id not in connected_nodes]
        return sorted(orphaned)

    def to_networkx(self) -> nx.DiGraph:
        """Convert to NetworkX directed graph for algorithms.

        This is used for advanced graph algorithms like community detection
        and modularity calculation.

        Returns:
            NetworkX DiGraph with nodes and edges from this graph
        """
        G = nx.DiGraph()

        # Add all nodes
        for node_id, node in self.nodes.items():
            G.add_node(node_id, **{
                "type": node.type,
                "title": node.title,
                "subsystem": node.subsystem,
            })

        # Add all edges
        for edge in self.edges:
            G.add_edge(edge.from_node, edge.to_node, type=edge.type)

        return G
