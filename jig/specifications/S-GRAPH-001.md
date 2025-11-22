---
id: S-GRAPH-001
type: specification
title: Status calculation logic for Intent Graph health
subsystem: core
status: active
created: 2025-11-21
---

# Specification: Status Calculation Logic

## Purpose

Calculate and display the health status of the Intent Graph, identifying orphaned nodes, missing relationships, and subsystem coverage.

## Requirements

### 1. Status Metrics

Calculate the following metrics:

**Node counts:**
- Total nodes by type (O, S, C, T)
- Nodes with relationships
- Orphaned nodes (no incoming/outgoing edges)

**Subsystem coverage:**
- Subsystems defined
- Nodes per subsystem
- Nodes without subsystem assignment

**Relationship health:**
- Total edges
- Specification coverage (S nodes with tests)
- Implementation coverage (S nodes with code)
- Orphaned specifications

### 2. Orphan Detection

**Orphaned node definition:**
- No incoming edges AND no outgoing edges
- Isolated from Intent Graph
- Likely incomplete or obsolete

**Detection algorithm:**
```python
def find_orphaned_nodes(graph: Graph) -> list[str]:
    """Find nodes with degree = 0."""
    orphans = []
    for node_id in graph.nodes:
        if graph.in_degree(node_id) == 0 and graph.out_degree(node_id) == 0:
            orphans.append(node_id)
    return orphans
```

### 3. Coverage Calculations

**Specification test coverage:**
```
tested_specs = count(S nodes with incoming T edges)
total_specs = count(S nodes)
coverage = tested_specs / total_specs * 100
```

**Specification implementation coverage:**
```
implemented_specs = count(S nodes with incoming C edges)
total_specs = count(S nodes)
coverage = implemented_specs / total_specs * 100
```

### 4. Status Command Output

**jigy status:**
```
Intent Graph Status

Nodes: 197 total
  14 Outcomes (O)
  24 Specifications (S)
  37 Code (C)
  122 Tests (T)

Relationships: ~394 edges

Coverage:
  Specifications with tests: 18/24 (75%)
  Specifications with code: 22/24 (92%)

Issues:
  ⚠ 3 orphaned nodes: S-OLD-001, O-DEPRECATED-002, C-UNUSED-003

Subsystems: 5
  core (89 nodes)
  cli (42 nodes)
  decompose (31 nodes)
  jigy-tool (18 nodes)
  utils (17 nodes)
```

### 5. Error Handling

**Missing directories:**
- Warn if `jig/outcomes/` or `jig/specifications/` missing
- Suggest running `jigy init`
- Continue with available data

**Empty graph:**
- Display "No nodes found"
- Suggest creating first outcome
- Exit code 0 (not an error)

### 6. Performance Target

- Status calculation: <500ms for 1000 nodes
- Single graph traversal
- Cached degree calculations

## Implementation Notes

**Location:** `src/jig/cli/status.py:1` (C-STATUS-001)

**Dependencies:**
- Graph loading (`src/jig/core/graph.py`)
- NetworkX for degree calculations
- Rich for formatted output

**Data Flow:**
1. Load graph from `jig/graph-index.yaml`
2. Calculate node counts by type
3. Find orphaned nodes (degree = 0)
4. Calculate coverage metrics
5. Group nodes by subsystem
6. Render formatted output

## Test Coverage

- T-STATUS-001: Basic status calculation with mock data
- T-STATUS-002: Orphan detection
- T-STATUS-003: Graceful handling of missing directories
- T-STATUS-004: Full integration test with real data

## References

- Implementation: `src/jig/cli/status.py:1`
- Tests: `tests/unit/test_status_logic.py`, `tests/integration/test_status_command.py`
- Related: S-GRAPH-002 (graph data structures), S-NESTED-003 (display)
