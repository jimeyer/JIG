# @jig C-DECOMP-001 implements:S-DECOMP-001,S-DECOMP-003 subsystem:decompose interface:internal
"""Metrics calculation for decomposability analysis.

This module implements Newman modularity and coupling ratio calculations
for analyzing subsystem boundaries and dependencies.
"""

from dataclasses import dataclass

import networkx as nx  # type: ignore[import-untyped]
from networkx.algorithms import community  # type: ignore[import-untyped]

from jig.core.graph import Graph


@dataclass
class SubsystemMetrics:
    """Metrics for a single subsystem.

    Attributes:
        name: Subsystem name (fully-qualified path for nested subsystems)
        node_count: Number of nodes in this subsystem
        internal_edges: Edges where both endpoints are in this subsystem
        external_edges: Edges where one endpoint is outside this subsystem
        coupling_ratio: Ratio of internal to external edges (higher is better)
    """

    name: str
    node_count: int
    internal_edges: int
    external_edges: int
    coupling_ratio: float


@dataclass
class DecomposabilityMetrics:
    """Overall decomposability metrics for the graph.

    Attributes:
        modularity: Newman modularity score (range: -0.5 to 1.0, higher is better)
        subsystem_count: Number of subsystems in the graph
        avg_coupling_ratio: Average coupling ratio across all subsystems
        subsystems: Dictionary mapping subsystem name to its metrics
        boundary_violations: List of boundary violation descriptions
    """

    modularity: float
    subsystem_count: int
    avg_coupling_ratio: float
    subsystems: dict[str, SubsystemMetrics]
    boundary_violations: list[str]


def calculate_modularity(graph: Graph) -> float:
    """Calculate Newman modularity score.

    The modularity measures the strength of division of a network into modules
    (communities). Networks with high modularity have dense connections between
    nodes within modules but sparse connections between nodes in different modules.

    Formula: Q = (1/2m) Σ[A_ij - (k_i * k_j)/2m] * δ(c_i, c_j)
    where:
    - m = total edges
    - A_ij = adjacency matrix
    - k_i = degree of node i
    - δ(c_i, c_j) = 1 if nodes in same community, 0 otherwise

    Args:
        graph: Graph to analyze

    Returns:
        Modularity score between -0.5 and 1.0. Higher values indicate
        better-defined subsystem boundaries.
        - Score > 0.3: Good modular structure
        - Score 0.2-0.3: Moderate modular structure
        - Score < 0.2: Weak or no modular structure

    Example:
        >>> modularity = calculate_modularity(graph)
        >>> print(f"Modularity: {modularity:.3f}")
        Modularity: 0.457
    """
    if not graph.subsystems:
        # No subsystems defined - modularity is 0
        return 0.0

    # Convert to NetworkX graph
    G = graph.to_networkx()

    if G.number_of_edges() == 0:
        # No edges - modularity is undefined, return 0
        return 0.0

    # Convert subsystems to communities (list of sets of node IDs)
    communities_list = []
    for subsystem in graph.subsystems.values():
        # Get all nodes in this subsystem (including nested)
        nodes = subsystem.get_all_nodes(recursive=True)
        if nodes:
            communities_list.append(set(nodes))

    if not communities_list:
        return 0.0

    # Use NetworkX modularity calculation
    # Note: This only considers nodes that are in the graph
    # Filter communities to only include nodes that exist in G
    filtered_communities = []
    for comm in communities_list:
        filtered_comm = {node for node in comm if node in G.nodes()}
        if filtered_comm:
            filtered_communities.append(filtered_comm)

    if not filtered_communities:
        return 0.0

    return community.modularity(G, filtered_communities)


def calculate_coupling_ratio(subsystem_name: str, graph: Graph) -> SubsystemMetrics:
    """Calculate coupling ratio for a subsystem (supports hierarchical subsystems).

    Coupling ratio measures how well-isolated a subsystem is from others.
    A high ratio indicates good encapsulation.

    Internal edges: Both endpoints are in the subsystem (or its children)
    External edges: One endpoint is outside the subsystem
    Ratio: internal / external (higher is better)

    For hierarchical subsystems:
    - Parent subsystem metrics include ALL descendant nodes
    - Edges between child subsystems count as internal to the parent
    - This enables refactoring into hierarchies without degrading metrics

    Note: Constraint relationships (type='satisfies') are not counted as edges
    in v7, as they represent predicates over the graph rather than structural
    dependencies.

    Args:
        subsystem_name: Name or path of the subsystem to analyze (e.g., 'core' or 'crdt.ser')
        graph: Graph to analyze

    Returns:
        SubsystemMetrics with coupling information

    Raises:
        ValueError: If subsystem not found

    Example:
        >>> # Flat subsystem
        >>> metrics = calculate_coupling_ratio("core", graph)
        >>> print(f"Coupling ratio: {metrics.coupling_ratio:.2f}")
        Coupling ratio: 5.00

        >>> # Nested subsystem (includes all children)
        >>> metrics = calculate_coupling_ratio("crdt", graph)
        >>> # Edges between crdt.ser and crdt.deser count as internal
    """
    subsystem = graph.get_subsystem_by_path(subsystem_name)
    if not subsystem:
        raise ValueError(f"Subsystem {subsystem_name} not found")

    subsystem_nodes = set(subsystem.get_all_nodes(recursive=True))
    internal = 0
    external = 0

    for edge in graph.edges:
        # Skip constraint edges (v7) - they're predicates, not structural edges
        if edge.type == "satisfies":
            continue

        from_in = edge.from_node in subsystem_nodes
        to_in = edge.to_node in subsystem_nodes

        if from_in and to_in:
            internal += 1
        elif from_in or to_in:
            external += 1

    # Calculate ratio (infinity if no external edges)
    ratio = internal / external if external > 0 else float("inf")

    return SubsystemMetrics(
        name=subsystem_name,
        node_count=len(subsystem_nodes),
        internal_edges=internal,
        external_edges=external,
        coupling_ratio=ratio,
    )


def calculate_all_metrics(graph: Graph) -> DecomposabilityMetrics:
    """Calculate all decomposability metrics for the graph.

    This is the main entry point for decomposability analysis. It calculates:
    - Overall modularity score
    - Per-subsystem coupling ratios
    - Average coupling ratio

    Args:
        graph: Graph to analyze

    Returns:
        DecomposabilityMetrics with all calculated metrics

    Example:
        >>> metrics = calculate_all_metrics(graph)
        >>> print(f"Modularity: {metrics.modularity:.3f}")
        >>> print(f"Average coupling: {metrics.avg_coupling_ratio:.2f}")
        Modularity: 0.457
        Average coupling: 4.25
    """
    # Calculate overall modularity
    modularity = calculate_modularity(graph)

    # Calculate per-subsystem metrics
    subsystem_metrics = {}
    coupling_ratios = []

    # Get all subsystem paths (including nested)
    all_paths = graph.get_all_subsystem_paths(flat=False)

    for subsystem_path in all_paths:
        try:
            metrics = calculate_coupling_ratio(subsystem_path, graph)
            subsystem_metrics[subsystem_path] = metrics

            # Only include finite coupling ratios in average
            if metrics.coupling_ratio != float("inf"):
                coupling_ratios.append(metrics.coupling_ratio)
        except ValueError:
            # Subsystem not found or has no nodes - skip
            pass

    # Calculate average coupling ratio
    avg_coupling = (
        sum(coupling_ratios) / len(coupling_ratios) if coupling_ratios else 0.0
    )

    return DecomposabilityMetrics(
        modularity=modularity,
        subsystem_count=len(subsystem_metrics),
        avg_coupling_ratio=avg_coupling,
        subsystems=subsystem_metrics,
        boundary_violations=[],  # WU11 will populate this
    )
