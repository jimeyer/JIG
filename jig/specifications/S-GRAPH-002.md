---
id: S-GRAPH-002
type: specification
title: Core graph data structures and operations
subsystem: core
status: active
created: 2025-11-21
---

# Specification: Graph Data Structures

## Purpose

Define core data structures for representing the Intent Graph, including nodes, edges, subsystems, and basic graph operations.

## Requirements

### 1. Node Structure

```python
@dataclass
class OSTCNode:
    """Represents a node in the Intent Graph."""
    id: str                    # Node ID (e.g., "S-AUTH-001")
    type: str                  # Node type: "outcome", "specification", "code", "test"
    title: str                 # Human-readable title
    subsystem: str             # Subsystem assignment
    file: str                  # Source file path
    line: int | None           # Line number (for C/T nodes)
    metadata: dict[str, Any]   # Additional frontmatter fields
```

### 2. Edge Structure

```python
@dataclass
class Edge:
    """Represents a directed edge in the Intent Graph."""
    from_node: str             # Source node ID
    to_node: str               # Target node ID
    type: str                  # Edge type: "implements", "verifies", "depends_on"
```

### 3. Graph Class

```python
class Graph:
    """Intent Graph with nodes, edges, and query methods."""

    def __init__(self):
        self.nodes: dict[str, OSTCNode] = {}
        self.edges: list[Edge] = []
        self._nx_graph: nx.DiGraph = nx.DiGraph()

    def add_node(self, node: OSTCNode) -> None:
        """Add node to graph."""

    def add_edge(self, edge: Edge) -> None:
        """Add edge to graph."""

    def get_node(self, node_id: str) -> OSTCNode | None:
        """Retrieve node by ID."""

    def get_edges(self, from_node: str | None = None,
                  to_node: str | None = None) -> list[Edge]:
        """Query edges by source or target."""

    def get_node_counts_by_type(self) -> dict[str, int]:
        """Count nodes by type (O/S/C/T)."""

    def find_orphaned_nodes(self) -> list[str]:
        """Find nodes with no edges."""
```

### 4. Graph Loading

Load graph from multiple sources:

**YAML files (O/S nodes):**
```python
def load_from_yaml_files(outcomes_dir: Path, specs_dir: Path) -> Graph:
    """Parse O/S nodes from jig/outcomes/, jig/specifications/."""
```

**Annotations (C/T nodes):**
```python
def load_from_annotations(src_dir: Path, test_dir: Path) -> Graph:
    """Scan for @jig annotations in source/test files."""
```

**Graph index:**
```python
def load_from_index(index_path: Path) -> Graph:
    """Load prebuilt graph from jig/graph-index.yaml."""
```

### 5. Internal Representation

Use NetworkX for graph operations:
- Node storage: `self._nx_graph.nodes[node_id] = node_data`
- Edge storage: `self._nx_graph.add_edge(from_node, to_node, type=edge_type)`
- Degree calculations: `self._nx_graph.in_degree(node_id)`
- Traversal: BFS/DFS using NetworkX algorithms

**Benefits:**
- Mature graph algorithms (shortest path, cycles, centrality)
- Performance optimizations
- Standard graph operations

### 6. Node Type Enumeration

Valid node types:
- `outcome` (O-*)
- `specification` (S-*)
- `code` (C-*)
- `test` (T-*)

**Validation:**
- Node ID must match type prefix (e.g., `S-AUTH-001` → type: "specification")
- Type field required in all nodes
- Invalid types rejected during load

## Implementation Notes

**Location:** `src/jig/core/graph.py:1` (C-GRAPH-001)

**Dependencies:**
- NetworkX (`pip install networkx`)
- dataclasses (Python 3.7+)
- YAML parsing (`src/jig/utils/yaml_utils.py`)

**Performance:**
- Graph construction: O(n + e) for n nodes, e edges
- Node lookup: O(1) via dictionary
- Edge query: O(e) worst case
- Target: <100ms to load 1000 nodes

## Test Coverage

- T-GRAPH-001: Basic graph construction and node addition
- T-GRAPH-002: Node counting by type
- T-GRAPH-003: Orphan detection

## References

- Implementation: `src/jig/core/graph.py:1`
- Tests: `tests/unit/test_graph.py`
- Related: S-NESTED-001 (subsystem structure), S-GRAPH-003 (traversal)
