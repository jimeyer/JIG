---
id: S-DECOMP-003
type: specification
title: Coupling ratio calculation for subsystem boundary quality
subsystem: decompose
status: active
created: 2025-11-21
---

# Specification: Coupling Ratio Calculation

## Purpose

Calculate the coupling ratio for each subsystem to measure boundary quality, quantifying the balance between internal cohesion and external coupling.

## Requirements

### 1. Coupling Ratio Definition

**Formula:**
```
coupling_ratio = internal_edges / external_edges

where:
  internal_edges = edges with both endpoints in subsystem
  external_edges = edges with one endpoint outside subsystem
```

**Interpretation:**
- Higher ratio = better (more cohesive, less coupled)
- Target: ≥ 10:1 (10x more internal than external edges)
- Warning: < 10:1
- Critical: < 5:1

### 2. Edge Classification

**Internal edge:** Both endpoints belong to subsystem
```python
# Example: Both nodes in 'auth' subsystem
edge = Edge(from_node="C-AUTH-001", to_node="C-AUTH-002", ...)
# → internal to 'auth'
```

**External edge:** One or both endpoints outside subsystem
```python
# Example: Crosses subsystem boundary
edge = Edge(from_node="C-AUTH-001", to_node="C-CRYPTO-001", ...)
# → external to 'auth' (depends on 'crypto')
```

### 3. SubsystemMetrics Data Structure

```python
@dataclass
class SubsystemMetrics:
    """Metrics for a single subsystem."""
    name: str                  # Fully-qualified path (e.g., "crdt.ser")
    node_count: int            # Number of nodes in subsystem
    internal_edges: int        # Both endpoints in subsystem
    external_edges: int        # One endpoint outside
    coupling_ratio: float      # internal / external (or inf)
```

### 4. Algorithm

```python
def calculate_coupling_ratio(subsystem_name: str, graph: Graph) -> SubsystemMetrics:
    """Calculate coupling metrics for a subsystem."""

    # 1. Get subsystem and collect all nodes
    subsystem = graph.get_subsystem(subsystem_name)
    nodes = subsystem.get_all_nodes(recursive=True)
    node_set = set(nodes)

    # 2. Classify edges
    internal = 0
    external = 0

    for edge in graph.edges:
        from_in = edge.from_node in node_set
        to_in = edge.to_node in node_set

        if from_in and to_in:
            internal += 1
        elif from_in or to_in:
            external += 1
        # else: neither endpoint in subsystem (ignore)

    # 3. Calculate ratio
    if external == 0:
        ratio = float('inf')  # Perfectly isolated
    else:
        ratio = internal / external

    return SubsystemMetrics(
        name=subsystem_name,
        node_count=len(nodes),
        internal_edges=internal,
        external_edges=external,
        coupling_ratio=ratio,
    )
```

### 5. Special Cases

**No external edges:**
- Ratio = ∞ (perfectly isolated subsystem)
- Display as "∞" or "isolated"
- Excellent decomposability

**No internal edges:**
- Ratio = 0 (no cohesion)
- Warning: subsystem may be too small or poorly defined

**Nested subsystems:**
- Use `recursive=True` to include child nodes
- Parent metrics aggregate all descendants

### 6. Constraint Edge Exclusion

**Important:** Edges from Constraint nodes (X-*) are excluded from coupling metrics.

**Rationale:**
- Constraints are architectural rules, not implementation dependencies
- Including constraint edges would inflate external edge counts
- Coupling measures implementation coupling, not rule enforcement

**Implementation:**
```python
# Skip edges from constraint nodes
if edge.from_node.startswith("X-"):
    continue
```

## Implementation Notes

**Location:** `src/jig/decompose/metrics.py:1` (function in module)

**Dependencies:**
- S-NESTED-002 (recursive node collection)
- S-GRAPH-002 (edge iteration)

**Performance:**
- Single pass over edges
- Target: <100ms for 1000 edges
- Amortized O(e) where e = number of edges

## Test Coverage

- T-DECOMP-002: Coupling ratio for known edge counts
- T-DECOMP-004: Ratio = ∞ for isolated subsystem (no external edges)

## References

- Implementation: `src/jig/decompose/metrics.py`
- Related: S-DECOMP-001 (modularity), S-NESTED-004 (nested metrics)
- Theoretical basis: Simon's "Nearly Decomposable Systems", Ousterhout's "Deep Modules"
