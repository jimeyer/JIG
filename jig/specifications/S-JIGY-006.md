---
id: S-JIGY-006
type: specification
title: Path finding and graph traversal with depth limits
subsystem: jigy-tool
status: active
created: 2025-11-21
implements:
  - O-JIGY-002
---

# Specification: Graph Traversal

## Purpose

Enable graph traversal operations to trace relationships, find paths between nodes, and explore dependencies. Support depth-limited traversal to prevent overwhelming output.

## Requirements

### 1. Trace Command

**Command:** `jigy trace <node-id> [--depth N] [--direction forward|backward|both]`

**Purpose:** Traverse graph from a starting node, showing tree structure

**Default:** depth=2, direction=forward (follow outgoing edges)

```bash
$ jigy trace O-AIR-001 --depth 3

O-AIR-001: Track bike states across multiple devices
├─ implements → S-AIR-001: BikeState messages use operation_type
│  ├─ implements → C-AIR-003: BikeState class
│  │  └─ depends_on → C-PROTOCOL-001: ProtocolStack
│  ├─ verifies → T-AIR-005: test_bike_state_operation_type
│  └─ verifies → T-AIR-007: test_bike_state_propagation
└─ implements → S-AIR-002: BikeState includes device_id
   ├─ implements → C-AIR-003: BikeState class (seen above)
   └─ verifies → T-AIR-006: test_bike_state_device_id

Legend:
  (seen above) = node already displayed (cycle detection)
```

**Backward trace** (find what depends on this node):
```bash
$ jigy trace C-AIR-003 --direction backward --depth 2

C-AIR-003: BikeState class
├─ implements ← S-AIR-001: BikeState messages use operation_type
│  └─ implements ← O-AIR-001: Track bike states
└─ implements ← S-AIR-002: BikeState includes device_id
   └─ implements ← O-AIR-001: Track bike states (seen above)
```

**Performance:** <500ms for depth-3 traversal on 1000-node graph

### 2. Path Finding Command

**Command:** `jigy path <from-id> <to-id> [--max-depth N]`

**Purpose:** Find shortest path between two nodes

```bash
$ jigy path O-PS-001 C-PS-005

Path from O-PS-001 to C-PS-005 (length: 2):
  O-PS-001 
    --implements--> S-PS-003
    --implements--> C-PS-005

$ jigy path O-AUTH-001 C-GATEWAY-042

Path from O-AUTH-001 to C-GATEWAY-042 (length: 4):
  O-AUTH-001
    --implements--> S-AUTH-001
    --depends_on--> S-GATEWAY-001
    --implements--> C-GATEWAY-042

$ jigy path O-PS-001 O-AUTH-001

No path found from O-PS-001 to O-AUTH-001
(Nodes in different connected components)
```

**Algorithm:** Breadth-first search (BFS) for shortest path

**Performance:** <300ms for path finding on 1000-node graph

### 3. Dependencies Command

**Command:** `jigy deps <node-id> [--reverse] [--transitive]`

**Purpose:** Show direct dependencies (or dependents if --reverse)

```bash
$ jigy deps S-AIR-001

Direct dependencies of S-AIR-001:
  → O-AIR-001 (implements)
  → O-AIR-002 (implements)

$ jigy deps S-AIR-001 --reverse

Nodes depending on S-AIR-001:
  ← C-AIR-003 (implements)
  ← T-AIR-005 (verifies)
  ← T-AIR-007 (verifies)

$ jigy deps S-AIR-001 --reverse --transitive

All transitive dependents of S-AIR-001 (depth-first):
  ← C-AIR-003 (implements)
    ← [any nodes depending on C-AIR-003]
  ← T-AIR-005 (verifies)
  ← T-AIR-007 (verifies)
```

**Performance:** <200ms for direct deps, <1s for transitive

### 4. Cycle Detection

Detect and handle cycles gracefully:

```bash
$ jigy trace S-CYCLE-001

S-CYCLE-001: Node in cycle
├─ depends_on → S-CYCLE-002: Second node
│  └─ depends_on → S-CYCLE-001: Node in cycle [CYCLE DETECTED]
└─ implements → O-CYCLE-001: Outcome
```

Mark already-visited nodes to prevent infinite loops.

### 5. Output Formatting

**Tree format** (default for trace):
- Unicode box-drawing characters: `├─`, `└─`, `│`
- Indentation shows depth
- Edge type shown: `--implements-->`, `--verifies-->`

**Path format** (for path command):
- Linear list with edge types
- Node IDs with titles
- Total path length

**JSON format** (for scripting):
```bash
$ jigy trace O-AIR-001 --format json
{
  "root": "O-AIR-001",
  "depth": 2,
  "nodes": [
    {
      "id": "O-AIR-001",
      "children": [
        {"id": "S-AIR-001", "edge_type": "implements", "children": [...]}
      ]
    }
  ]
}
```

## Implementation Notes

**Location:** `jigy/cli/traversal_commands.py`

**Algorithm Libraries:**
- NetworkX for graph algorithms (BFS, DFS, shortest_path)
- Or custom implementation for more control

**Data Structures:**
```python
# @jig C-JIGY-006 implements:S-JIGY-006 subsystem:jigy-tool interface:public
def trace_graph(registry, start_id, depth=2, direction="forward"):
    """Traverse graph from starting node"""
    visited = set()
    
    def traverse(node_id, current_depth):
        if current_depth > depth or node_id in visited:
            return
        
        visited.add(node_id)
        node = registry.get_node(node_id)
        
        if direction in ["forward", "both"]:
            edges = registry.get_edges_from(node_id)
            for edge in edges:
                yield (node_id, edge, current_depth)
                yield from traverse(edge.target, current_depth + 1)
        
        if direction in ["backward", "both"]:
            edges = registry.get_edges_to(node_id)
            for edge in edges:
                yield (node_id, edge, current_depth)
                yield from traverse(edge.source, current_depth + 1)
    
    yield from traverse(start_id, 0)
```

**Performance Optimization:**
- Depth limit prevents exponential explosion
- Visited set prevents infinite loops
- Lazy evaluation (generators) for large graphs

## Test Cases

```python
# @jig T-JIGY-015 verifies:S-JIGY-006 subsystem:jigy-tool
def test_trace_command():
    """Test graph traversal with depth limit"""
    result = run_cli(["trace", "O-AIR-001", "--depth", "2"])
    assert result.exit_code == 0
    assert "O-AIR-001" in result.output
    assert "S-AIR-001" in result.output  # Depth 1
    assert "C-AIR-003" in result.output  # Depth 2

# @jig T-JIGY-016 verifies:S-JIGY-006 subsystem:jigy-tool
def test_path_finding():
    """Test shortest path between nodes"""
    result = run_cli(["path", "O-PS-001", "C-PS-005"])
    assert result.exit_code == 0
    assert "Path" in result.output
    assert "length:" in result.output

# @jig T-JIGY-017 verifies:S-JIGY-006 subsystem:jigy-tool
def test_cycle_detection():
    """Test cycle detection in traversal"""
    # Create graph with cycle
    registry = create_graph_with_cycle()
    result = trace_graph(registry, "S-CYCLE-001", depth=5)
    # Should not infinite loop
    nodes = list(result)
    assert len(nodes) < 100  # Bounded by visited set
```

## References

- O-JIGY-002: Developers can navigate Intent graph efficiently
- S-JIGY-003: Unified node registry (provides graph data)
- S017 Analysis: Part 3.2.2 (Path finding & traversal)
- JIG v6.1 Spec: §7.4 (Validate alignment workflows)

