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


# @jig C-NESTED-001 implements:S-NESTED-001 subsystem:core interface:internal
@dataclass
class Subsystem:
    """Represents a subsystem grouping of nodes.

    Attributes:
        name: Subsystem name (local, not fully-qualified)
        nodes: List of node IDs in this subsystem (leaf only)
        subsystems: Dictionary of child subsystems (optional)
        description: Human-readable description (optional)
        parent_path: Fully-qualified parent path (e.g., "crdt")
    """

    name: str
    nodes: list[str] = field(default_factory=list)
    subsystems: dict[str, "Subsystem"] = field(default_factory=dict)
    description: str = ""
    parent_path: str = ""

    @property
    def full_path(self) -> str:
        """Return fully-qualified subsystem path."""
        if self.parent_path:
            return f"{self.parent_path}.{self.name}"
        return self.name

    def is_leaf(self) -> bool:
        """Return True if this subsystem has no children."""
        return len(self.subsystems) == 0

    def get_all_nodes(self, recursive: bool = False) -> list[str]:
        """Return all nodes in this subsystem.

        Args:
            recursive: If True, include nodes from child subsystems

        Returns:
            List of node IDs
        """
        if not recursive:
            return self.nodes

        all_nodes = list(self.nodes)
        for child in self.subsystems.values():
            all_nodes.extend(child.get_all_nodes(recursive=True))
        return all_nodes

    def find_subsystem(self, path: str) -> "Subsystem | None":
        """Find subsystem by path (e.g., 'ser' or 'crdt.ser').

        Args:
            path: Subsystem path (dot notation)

        Returns:
            Subsystem object or None if not found
        """
        parts = path.split(".", 1)
        if parts[0] != self.name:
            return None

        if len(parts) == 1:
            return self

        # Recurse into children
        child_path = parts[1]
        for child in self.subsystems.values():
            result = child.find_subsystem(child_path)
            if result:
                return result

        return None


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
        1. All O/S/X markdown nodes from outcomes/, specifications/, constraints/
        2. Edges and subsystems from graph-index.yaml
        
        Note: T/C nodes will be discovered via @jig annotations (future feature)

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

        # Load only markdown-based nodes (O/S/X in OSTCX model)
        # T/C nodes discovered via @jig annotations (future feature)
        node_dirs = ["outcomes", "specifications", "constraints"]
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

                # Load subsystems (supports nested hierarchy)
                subsystems_data = index_data.get("subsystems", {})

                def parse_subsystem(name: str, data: dict[str, Any], parent_path: str = "") -> Subsystem:
                    """Recursively parse subsystem and its children."""
                    subsystem = Subsystem(
                        name=name,
                        nodes=data.get("nodes", []),
                        description=data.get("description", ""),
                        parent_path=parent_path,
                    )

                    # Parse child subsystems
                    child_subsystems = data.get("subsystems", {})
                    for child_name, child_data in child_subsystems.items():
                        child = parse_subsystem(child_name, child_data, subsystem.full_path)
                        subsystem.subsystems[child_name] = child

                    return subsystem

                for subsystem_name, subsystem_dict in subsystems_data.items():
                    subsystem = parse_subsystem(subsystem_name, subsystem_dict)
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

    def get_dependencies(self, node_id: str) -> list[str]:
        """Return nodes that this node depends on (incoming edges).

        For 'implements' edges: S-001 implements O-001 → O-001 is dependency of S-001
        For 'verifies' edges: T-001 verifies S-001 → S-001 is dependency of T-001

        Args:
            node_id: Node ID to get dependencies for

        Returns:
            List of node IDs that this node depends on (sorted)
            Returns empty list if node has no dependencies or doesn't exist

        Example:
            >>> graph.get_dependencies("S-JIG-001")
            ["O-JIG-001"]
        """
        dependencies = []
        for edge in self.edges:
            if edge.from_node == node_id:
                dependencies.append(edge.to_node)
        return sorted(dependencies)

    def get_dependents(self, node_id: str) -> list[str]:
        """Return nodes that depend on this node (outgoing edges).

        For 'implements' edges: S-001 implements O-001 → S-001 is dependent of O-001

        Args:
            node_id: Node ID to get dependents for

        Returns:
            List of node IDs that depend on this node (sorted)
            Returns empty list if node has no dependents or doesn't exist

        Example:
            >>> graph.get_dependents("O-JIG-001")
            ["S-JIG-001", "S-JIG-002"]
        """
        dependents = []
        for edge in self.edges:
            if edge.to_node == node_id:
                dependents.append(edge.from_node)
        return sorted(dependents)

    def find_path(self, start: str, end: str) -> list[str] | None:
        """Find shortest path between two nodes using BFS.

        Traverses edges in both directions (treats graph as undirected for path finding).

        Args:
            start: Starting node ID
            end: Ending node ID

        Returns:
            List of node IDs representing the shortest path from start to end,
            or None if no path exists or nodes don't exist

        Example:
            >>> graph.find_path("S-JIG-001", "O-JIG-001")
            ["S-JIG-001", "O-JIG-001"]
        """
        if start not in self.nodes or end not in self.nodes:
            return None

        # BFS implementation
        from collections import deque

        queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()
            if current == end:
                return path

            # Explore neighbors (both directions since we traverse undirected)
            neighbors = self.get_dependencies(current) + self.get_dependents(current)
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None  # No path found

    def filter_by_type(self, node_type: str) -> list[OSTCNode]:
        """Return all nodes of given type (case-insensitive).

        Args:
            node_type: Node type to filter by (e.g., "outcome", "specification")

        Returns:
            List of nodes matching the type, sorted by ID

        Example:
            >>> outcomes = graph.filter_by_type("outcome")
            >>> [node.id for node in outcomes]
            ["O-JIG-001", "O-JIG-002"]
        """
        node_type_lower = node_type.lower()
        filtered = [
            node for node in self.nodes.values()
            if node.type.lower() == node_type_lower
        ]
        return sorted(filtered, key=lambda n: n.id)

    def filter_by_subsystem(self, subsystem: str) -> list[OSTCNode]:
        """Return all nodes in given subsystem (case-insensitive).

        Args:
            subsystem: Subsystem name to filter by (e.g., "core", "cli")

        Returns:
            List of nodes in the subsystem, sorted by ID
            Returns empty list if no nodes found in subsystem

        Example:
            >>> core_nodes = graph.filter_by_subsystem("core")
            >>> [node.id for node in core_nodes]
            ["O-JIG-001", "S-JIG-001"]
        """
        subsystem_lower = subsystem.lower()
        filtered = [
            node for node in self.nodes.values()
            if node.subsystem and node.subsystem.lower() == subsystem_lower
        ]
        return sorted(filtered, key=lambda n: n.id)

# @jig C-NESTED-002 implements:S-NESTED-002 subsystem:core interface:internal
    def get_subsystem_by_path(self, path: str) -> Subsystem | None:
        """Get subsystem by fully-qualified path.

        Args:
            path: Subsystem path (e.g., 'core', 'crdt.ser')

        Returns:
            Subsystem object or None if not found

        Example:
            >>> graph.get_subsystem_by_path("core")
            Subsystem(name="core", ...)
            >>> graph.get_subsystem_by_path("crdt.ser")
            Subsystem(name="ser", parent_path="crdt", ...)
        """
        parts = path.split(".")
        root_name = parts[0]

        if root_name not in self.subsystems:
            return None

        subsystem = self.subsystems[root_name]

        # Navigate down the hierarchy
        for part in parts[1:]:
            if part not in subsystem.subsystems:
                return None
            subsystem = subsystem.subsystems[part]

        return subsystem

    def get_all_subsystem_paths(self, flat: bool = False) -> list[str]:
        """Return all subsystem paths.

        Args:
            flat: If True, return only leaf subsystems

        Returns:
            List of fully-qualified subsystem paths, sorted

        Example:
            >>> graph.get_all_subsystem_paths()
            ['core', 'crdt', 'crdt.ser', 'cli']
            >>> graph.get_all_subsystem_paths(flat=True)
            ['core', 'crdt.ser', 'cli']
        """
        paths = []

        def collect_paths(subsystem: Subsystem, include_parents: bool) -> None:
            if include_parents or subsystem.is_leaf():
                paths.append(subsystem.full_path)

            for child in subsystem.subsystems.values():
                collect_paths(child, include_parents)

        for root in self.subsystems.values():
            collect_paths(root, not flat)

        return sorted(paths)

    def get_constraints_for_subsystem(self, path: str, recursive: bool = True) -> list[str]:
        """Return all constraints that apply to a subsystem (v7).

        Args:
            path: Subsystem path (e.g., 'core', 'crdt.ser')
            recursive: If True, include constraints from child subsystems

        Returns:
            List of constraint IDs (e.g., ['X-PERF-001']), sorted

        Example:
            >>> graph.get_constraints_for_subsystem("core")
            ['X-PERF-001', 'X-SIMPLE-001']
        """
        subsystem = self.get_subsystem_by_path(path)
        if not subsystem:
            return []

        constraints = set()

        # Get nodes in this subsystem
        nodes = subsystem.get_all_nodes(recursive=recursive)

        # Collect constraints from all nodes
        for node_id in nodes:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                if hasattr(node, 'constraints'):
                    constraints.update(node.constraints)

        return sorted(list(constraints))

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
