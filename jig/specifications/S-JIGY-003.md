---
id: S-JIGY-003
type: specification
title: Unified node registry with O(1) lookup performance
subsystem: jigy-tool
status: active
created: 2025-11-21
implements:
  - O-JIGY-002
---

# Specification: Unified Node Registry

## Purpose

Provide a single data structure for fast node lookups, edge queries, and subsystem operations across all OSTC node types. Enable <100ms query performance on 1000-node graphs.

## Requirements

### 1. Node Registry Data Structure

```python
class NodeRegistry:
    """Unified registry for all OSTC nodes with fast lookup"""
    
    # Primary storage
    _nodes: Dict[str, Node]  # ID → Node (O(1) lookup)
    _edges: List[Edge]       # All edges
    
    # Indices for fast queries
    _edges_from: Dict[str, List[Edge]]  # source ID → edges
    _edges_to: Dict[str, List[Edge]]    # target ID → edges
    _nodes_by_type: Dict[str, List[Node]]  # type → nodes
    _nodes_by_subsystem: Dict[str, List[Node]]  # subsystem → nodes
    
    # Subsystem metadata
    _subsystems: Dict[str, Subsystem]  # name → subsystem
```

### 2. Node Object Structure

```python
@dataclass
class Node:
    id: str                    # "S-AIR-001"
    type: str                  # "outcome", "specification", "code", "test"
    title: str                 # "BikeState messages use operation_type"
    subsystem: str             # "airspace"
    status: str                # "active", "deprecated", "archived"
    file: Optional[str]        # "jig/specifications/S-AIR-001.md"
    line: Optional[int]        # 42 (for C/T nodes)
    metadata: Dict[str, Any]   # Additional fields from frontmatter
```

### 3. Edge Object Structure

```python
@dataclass
class Edge:
    source: str       # Source node ID
    target: str       # Target node ID
    type: str         # "implements", "satisfies", "verifies", "depends_on"
    metadata: Dict[str, Any]  # Optional additional fields
```

### 4. Core Operations (Performance Targets)

| Operation | Target | Method |
|-----------|--------|--------|
| Get node by ID | O(1) | Hash map lookup |
| Get edges from node | O(k) | Indexed by source |
| Get edges to node | O(k) | Indexed by target |
| Get nodes by type | O(n) | Pre-built list |
| Get nodes by subsystem | O(n) | Pre-built list |
| Add node | O(1) | Hash map insert |
| Add edge | O(1) | List append + index update |

Where k = number of edges for node, n = number of nodes of type/subsystem

### 5. Registry Building Sequence

```python
def build_registry():
    """Build complete node registry from all sources"""
    registry = NodeRegistry()
    
    # 1. Load subsystems
    subsystems = load_subsystems_yaml()
    registry.add_subsystems(subsystems)
    
    # 2. Discover O/S nodes from markdown
    for file in discover_markdown_files():
        node = parse_markdown_node(file)
        registry.add_node(node)
        
        # Extract relationships from frontmatter
        edges = extract_relationships(node)
        for edge in edges:
            registry.add_edge(edge)
    
    # 3. Load graph-index.yaml (adds C/T nodes)
    graph_index = load_graph_index_yaml()
    for node in graph_index.nodes:
        registry.add_node(node, merge=True)
    for edge in graph_index.edges:
        registry.add_edge(edge)
    
    # 4. Build indices
    registry.build_indices()
    
    return registry
```

### 6. Query API

```python
# Node queries
node = registry.get_node("S-AIR-001")
nodes = registry.get_nodes_by_type("specification")
nodes = registry.get_nodes_by_subsystem("airspace")
exists = registry.has_node("S-AIR-001")

# Edge queries
edges = registry.get_edges_from("S-AIR-001")  # Outgoing
edges = registry.get_edges_to("S-AIR-001")    # Incoming
edges = registry.get_all_edges()

# Subsystem queries
subsystem = registry.get_subsystem("airspace")
subsystems = registry.get_all_subsystems()

# Statistics
stats = registry.get_stats()  # Node counts, edge counts, etc.
```

## Implementation Notes

**Location:** `jigy/core/registry.py`

**Dependencies:**
- dataclasses for Node/Edge structures
- typing for type hints

**Memory Considerations:**
- 1000-node graph ≈ 1MB memory (acceptable)
- Indices add ~50% overhead (worth it for speed)
- No need for disk caching at this scale

**Thread Safety:**
- Read operations: Thread-safe (no mutation)
- Write operations: Not thread-safe (single-threaded build assumed)
- If needed later: Add read-write locks

## Performance Validation

```python
# @jig T-JIGY-007 verifies:S-JIGY-003 subsystem:jigy-tool
def test_node_lookup_performance():
    """Verify O(1) node lookup performance"""
    registry = build_large_registry(n_nodes=1000)
    
    start = time.time()
    for i in range(1000):
        node = registry.get_node(f"S-TEST-{i:03d}")
    elapsed = time.time() - start
    
    # 1000 lookups in <10ms (O(1) confirmed)
    assert elapsed < 0.010

# @jig T-JIGY-008 verifies:S-JIGY-003 subsystem:jigy-tool
def test_edge_query_performance():
    """Verify fast edge queries with indices"""
    registry = build_large_registry(n_nodes=1000, edges_per_node=5)
    
    start = time.time()
    edges = registry.get_edges_from("S-TEST-500")
    elapsed = time.time() - start
    
    # Query in <1ms with index
    assert elapsed < 0.001
```

## References

- O-JIGY-002: Developers can navigate Intent graph efficiently
- S017 Analysis: Part 3.1.3 (Unified node registry)
- JIG v6.1 Spec: §8.2 (Graph index data model)

