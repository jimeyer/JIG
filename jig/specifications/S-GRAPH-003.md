---
id: S-GRAPH-003
type: specification
title: Graph traversal, query, and path-finding operations
subsystem: core
status: active
created: 2025-11-21
---

# Specification: Graph Traversal Operations

## Purpose

Provide efficient graph traversal and query methods for dependency analysis, impact assessment, and path finding in the Intent Graph.

## Requirements

### 1. Dependency Traversal

Get all dependencies of a node (recursive):

```python
def get_dependencies(self, node_id: str, recursive: bool = True) -> list[str]:
    """Get all nodes this node depends on.

    Args:
        node_id: Starting node
        recursive: If True, follow dependencies transitively

    Returns:
        List of node IDs (breadth-first order)
    """
```

**Example:**
```
S-AUTH-001 depends on:
  Direct: O-AUTH-001
  Recursive: O-AUTH-001 → O-SECURITY-001
```

**Algorithm:** BFS traversal following outgoing edges

### 2. Dependent Traversal

Get all dependents of a node (reverse dependencies):

```python
def get_dependents(self, node_id: str, recursive: bool = True) -> list[str]:
    """Get all nodes that depend on this node (impact analysis).

    Args:
        node_id: Starting node
        recursive: If True, follow dependents transitively

    Returns:
        List of node IDs (breadth-first order)
    """
```

**Example:**
```
O-AUTH-001 is depended on by:
  Direct: S-AUTH-001, S-AUTH-002
  Recursive: S-AUTH-001 → C-AUTH-001 → T-AUTH-001
```

**Algorithm:** BFS traversal following incoming edges (reversed)

### 3. Path Finding

Find shortest path between two nodes:

```python
def find_path(self, from_node: str, to_node: str) -> list[str] | None:
    """Find shortest path from source to target.

    Returns:
        List of node IDs representing path, or None if no path exists
    """
```

**Example:**
```bash
jigy graph path O-AUTH-001 T-AUTH-001

Path: O-AUTH-001 → S-AUTH-001 → C-AUTH-001 → T-AUTH-001
Length: 3 hops
```

**Algorithm:** NetworkX `shortest_path()` (BFS-based)

### 4. Node Filtering

Filter nodes by type, subsystem, or metadata:

```python
def filter_nodes(self,
                 node_type: str | None = None,
                 subsystem: str | None = None,
                 metadata: dict[str, Any] | None = None) -> list[OSTCNode]:
    """Filter nodes by criteria."""
```

**Example:**
```python
# Get all specifications in 'auth' subsystem
specs = graph.filter_nodes(node_type="specification", subsystem="auth")
```

### 5. Cycle Detection

Detect cycles in dependency graph:

```python
def find_cycles(self) -> list[list[str]]:
    """Find all cycles in graph.

    Returns:
        List of cycles (each cycle is list of node IDs)
    """
```

**Example:**
```
⚠ Cycle detected: S-A-001 → S-B-001 → S-A-001
```

**Algorithm:** NetworkX `simple_cycles()`

### 6. Subgraph Extraction

Extract subgraph for visualization or analysis:

```python
def get_subgraph(self, node_ids: list[str], depth: int = 1) -> Graph:
    """Extract subgraph around specified nodes.

    Args:
        node_ids: Seed nodes
        depth: How many hops to include

    Returns:
        New Graph containing subgraph
    """
```

### 7. Performance Requirements

**Targets:**
- Dependency traversal: <50ms for 100-node subgraph
- Path finding: <100ms for 1000-node graph
- Cycle detection: <200ms for 1000-node graph

**Optimizations:**
- Use NetworkX built-in algorithms (C-optimized)
- Cache traversal results when appropriate
- Lazy evaluation for large result sets

## Implementation Notes

**Location:** `src/jig/cli/graph.py:1` (C-GRAPH-004)

**Dependencies:**
- S-GRAPH-002 (graph data structures)
- NetworkX algorithms (BFS, shortest_path, simple_cycles)

**CLI Integration:**
```bash
jigy graph deps S-AUTH-001          # Show dependencies
jigy graph impact O-AUTH-001        # Show dependents (impact)
jigy graph path O-AUTH-001 T-AUTH-001  # Find path
jigy graph show S-AUTH-001          # Show node + neighbors
jigy graph list --type spec         # Filter and list
```

## Test Coverage

- T-GRAPH-004: Basic dependency traversal
- T-GRAPH-005: Dependent detection (reverse deps)
- T-GRAPH-006: Path finding (exists)
- T-GRAPH-007: Path finding (no path)
- T-GRAPH-008: Traversal performance (<100ms)
- T-GRAPH-009 through T-GRAPH-024: Query and filter operations

## References

- Implementation: `src/jig/cli/graph.py:1`
- Tests: `tests/unit/test_graph_traversal.py`, `tests/unit/test_graph_queries.py`
- Integration: `tests/integration/test_graph_show.py`, `tests/integration/test_graph_deps.py`
- Related: S-GRAPH-002 (data structures), S-GRAPH-001 (status)
