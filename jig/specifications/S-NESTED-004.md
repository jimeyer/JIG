---
id: S-NESTED-004
type: specification
title: Nested subsystem metrics and hierarchical coupling analysis
subsystem: decompose
status: active
created: 2025-11-21
---

# Specification: Nested Subsystem Decomposability Metrics

## Purpose

Calculate decomposability metrics (coupling ratio, modularity) for hierarchical subsystem structures, aggregating child metrics to parent levels.

## Requirements

### 1. Metric Calculation Scope

**Leaf subsystems:**
- Calculate metrics directly from node edges
- Internal edges: Edges between nodes within subsystem
- External edges: Edges crossing subsystem boundary
- Coupling ratio: `internal_edges / external_edges`

**Parent subsystems:**
- Aggregate metrics from all descendant subsystems
- Treat entire subtree as unit for coupling analysis
- Internal = edges within subtree, External = edges leaving subtree

### 2. Hierarchical Coupling Ratio

Calculate coupling at each level:

```python
def calculate_coupling_ratio(subsystem: Subsystem, graph: Graph) -> float:
    """Calculate coupling ratio for subsystem (recursive if parent)."""
    nodes = subsystem.get_all_nodes(recursive=True)
    internal = count_edges_within(nodes, graph)
    external = count_edges_crossing(nodes, graph)
    return internal / external if external > 0 else float('inf')
```

**Example:**
```
crdt (parent):
  internal: 12 (within crdt.*)
  external: 2 (to auth, network)
  ratio: 6.0

  crdt.ser (leaf):
    internal: 5
    external: 1
    ratio: 5.0
```

### 3. Edge Classification

**Internal edge:** Both endpoints in same subsystem (or descendants)
**External edge:** Endpoints in different top-level subsystems
**Cross-child edge:** Between sibling subsystems (counts as internal to parent)

**Constraint edge exclusion:**
- Edges from Constraint nodes (X-*) excluded from coupling metrics
- Constraints are architectural rules, not implementation dependencies
- See S-NESTED-004 test coverage (T-NESTED-014)

### 4. Metrics Display

**jigy decompose metrics:**
```
Overall: 75% (healthy)

Subsystems:
  crdt (6.0:1, 73%)
  ├── crdt.ser (5.0:1, 71%)
  ├── crdt.merge (8.0:1, 82%)
  └── crdt.conflict (4.0:1, 65%) ⚠
  auth (11.8:1, 92%)
```

**Display rules:**
- Show hierarchy with tree characters
- Parent shows aggregate ratio
- Children show individual ratios
- Warning indicator (⚠) for ratios < 10:1

### 5. Subsystem-Specific Metrics

**jigy decompose metrics --subsystem crdt.ser:**
- Show metrics for specific subsystem
- Include context (parent path)
- Display related subsystems

## Implementation Notes

**Location:** `src/jig/decompose/metrics.py:1` (C-DECOMP-001), `src/jig/cli/decompose.py:1` (C-NESTED-007)

**Algorithm:**
1. Traverse subsystem tree (depth-first)
2. Collect all nodes (recursive for parents)
3. Classify edges (internal/external)
4. Calculate ratios
5. Store in subsystem metadata
6. Render tree with metrics

**Performance:**
- Cache edge classification
- Single graph traversal per calculation
- Target: <500ms for 100 subsystems

## Test Coverage

- T-NESTED-011: Decompose metrics command with nested subsystems
- T-NESTED-012: Subsystem-specific metrics query
- T-NESTED-013: Hierarchical coupling aggregation
- T-NESTED-014: Constraint edge exclusion from metrics

## References

- Implementation: `src/jig/decompose/metrics.py:1`, `src/jig/cli/decompose.py:1`
- Related: S-DECOMP-001 (metrics calculation), S-NESTED-002 (path resolution)
