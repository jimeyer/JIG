---
id: S-DECOMP-001
type: specification
title: Newman modularity calculation for subsystem boundary analysis
subsystem: decompose
status: active
created: 2025-11-21
---

# Specification: Modularity Calculation

## Purpose

Calculate Newman modularity score to measure the quality of subsystem decomposition, quantifying how well-defined subsystem boundaries are.

## Requirements

### 1. Modularity Definition

Newman modularity measures the strength of division of a network into communities (subsystems). It compares the actual number of intra-subsystem edges to the expected number in a random graph.

**Formula:**
```
Q = (1/2m) Σ[A_ij - (k_i * k_j)/2m] * δ(c_i, c_j)

where:
  m = total edges in graph
  A_ij = adjacency matrix (1 if edge exists, 0 otherwise)
  k_i = degree of node i
  δ(c_i, c_j) = 1 if nodes i,j in same subsystem, 0 otherwise
```

### 2. Score Interpretation

**Range:** -0.5 to 1.0

**Thresholds:**
- `Q > 0.3`: Good modular structure (well-defined subsystems)
- `0.2 ≤ Q ≤ 0.3`: Moderate modular structure
- `Q < 0.2`: Weak or no modular structure
- `Q = 0`: Random graph (no better than chance)
- `Q < 0`: Worse than random (anti-modular)

### 3. Algorithm

```python
def calculate_modularity(graph: Graph) -> float:
    """Calculate Newman modularity score."""

    # 1. Handle edge cases
    if not graph.subsystems:
        return 0.0  # No subsystems defined

    if graph.number_of_edges() == 0:
        return 0.0  # No edges

    # 2. Convert subsystems to communities (sets of node IDs)
    communities = []
    for subsystem in graph.subsystems.values():
        nodes = subsystem.get_all_nodes(recursive=True)
        if nodes:
            communities.append(set(nodes))

    # 3. Use NetworkX modularity calculation
    G = graph.to_networkx()
    return nx.community.modularity(G, communities)
```

### 4. Nested Subsystem Handling

For hierarchical subsystems (e.g., `crdt.ser`, `crdt.merge`):
- Use fully-qualified paths to identify communities
- Include all descendant nodes when calculating parent metrics
- Recursive node collection: `subsystem.get_all_nodes(recursive=True)`

**Example:**
```
crdt (parent subsystem)
├── crdt.ser (nodes: [C-SER-001, C-SER-002])
├── crdt.merge (nodes: [C-MERGE-001])
└── crdt.conflict (nodes: [C-CONF-001])

Communities for modularity:
  - {C-SER-001, C-SER-002, C-MERGE-001, C-CONF-001}  # crdt as whole
```

### 5. Performance Target

- Calculate modularity: <200ms for 1000 nodes
- Single pass over edges
- Use NetworkX optimized implementation

## Implementation Notes

**Location:** `src/jig/decompose/metrics.py:54-110`

**Dependencies:**
- NetworkX community module (`nx.community.modularity`)
- S-NESTED-002 (recursive node collection)
- S-GRAPH-002 (graph data structures)

**Edge Case Handling:**
- Empty graph → 0.0
- No subsystems → 0.0
- Single subsystem → 0.0 (no community structure)
- Isolated subsystems (no cross edges) → High modularity (good)

## Test Coverage

- T-DECOMP-001: Modularity for known graph structure
- T-DECOMP-003: Modularity = 0 for single subsystem

## References

- Implementation: `src/jig/decompose/metrics.py:54`
- Paper: Newman, M. E. J. (2006). "Modularity and community structure in networks"
- Related: S-DECOMP-003 (coupling ratio), S-NESTED-001 (subsystem structure)
