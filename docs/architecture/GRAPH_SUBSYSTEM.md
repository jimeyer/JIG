# Graph Subsystem Architecture

**Version:** 1.0
**Status:** Active
**Last Updated:** 2025-11-21

This document describes the architecture and implementation of JIG's nested subsystem support for hierarchical organization of Intent Graphs.

---

## Table of Contents

1. [Overview](#overview)
2. [Data Model](#data-model)
3. [Path Resolution](#path-resolution)
4. [Hierarchical Metrics](#hierarchical-metrics)
5. [Validation](#validation)
6. [Integration with Constraints (v7)](#integration-with-constraints-v7)
7. [Performance Characteristics](#performance-characteristics)
8. [Design Decisions](#design-decisions)

---

## Overview

### Purpose

Nested subsystems enable hierarchical organization of Intent Graphs, supporting:
- **Scalability**: Organize 20+ subsystems without overwhelming flat listings
- **Multi-level analysis**: Analyze at both coarse-grained (parent) and fine-grained (leaf) levels
- **Better metrics**: Edges between sibling subsystems count as internal to their parent
- **Clear architecture**: Subsystem hierarchy reflects system architecture

### Key Principles

1. **Nodes only in leaf subsystems**: Parent subsystems act as organizational containers
2. **Dot notation for paths**: `identity.auth` uniquely identifies nested subsystems
3. **Recursive traversal**: Operations can work on entire subtrees
4. **Backward compatible**: Flat subsystems continue to work without changes

---

## Data Model

### Subsystem Dataclass

**File:** `src/jig/core/graph.py`

```python
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
        """
        if not recursive:
            return self.nodes

        all_nodes = list(self.nodes)
        for child in self.subsystems.values():
            all_nodes.extend(child.get_all_nodes(recursive=True))
        return all_nodes
```

### Key Design Choices

**1. Local name + parent path (not fully-qualified name):**
```python
# Why this:
subsystem.name = "auth"
subsystem.parent_path = "identity"
subsystem.full_path  # → "identity.auth"

# Instead of this:
subsystem.name = "identity.auth"  # ❌ Harder to navigate hierarchy
```

**Rationale:**
- Local name makes recursion natural (children don't need to know full path)
- Full path computed on demand via `full_path` property
- Parent path enables bidirectional navigation

**2. Separate `nodes` and `subsystems` fields:**
```python
# Why this:
subsystem.nodes = [...]       # Only for leaf subsystems
subsystem.subsystems = {...}  # Only for parent subsystems

# Instead of this:
subsystem.children = [...]    # ❌ Mixed types (nodes + subsystems)
```

**Rationale:**
- Type safety: `nodes` is `list[str]`, `subsystems` is `dict[str, Subsystem]`
- Validation: Easily detect parents with direct nodes (error condition)
- Clarity: Explicit separation of organizational structure vs. content

**3. Recursive dataclass with self-reference:**
```python
subsystems: dict[str, "Subsystem"] = field(default_factory=dict)
```

**Rationale:**
- Arbitrary depth nesting without additional data structures
- Standard Python dataclass pattern for tree structures
- Compatible with YAML serialization/deserialization

---

## Path Resolution

### Graph Methods

**File:** `src/jig/core/graph.py`

```python
class Graph:
    def get_subsystem_by_path(self, path: str) -> Subsystem | None:
        """Get subsystem by fully-qualified path.

        Args:
            path: Subsystem path (e.g., 'core', 'crdt.ser')

        Returns:
            Subsystem object or None if not found

        Examples:
            >>> graph.get_subsystem_by_path("identity")
            Subsystem(name="identity", ...)

            >>> graph.get_subsystem_by_path("identity.auth")
            Subsystem(name="auth", parent_path="identity", ...)

            >>> graph.get_subsystem_by_path("nonexistent")
            None
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
```

**Algorithm:**
1. Split path by dots: `"identity.auth"` → `["identity", "auth"]`
2. Lookup root subsystem: `graph.subsystems["identity"]`
3. Iteratively navigate children: `subsystem.subsystems["auth"]`
4. Return final subsystem or None

**Time complexity:** O(depth), typically O(3-4) = O(1) in practice

**Space complexity:** O(1) (no intermediate allocations)

### Listing All Paths

```python
def get_all_subsystem_paths(self, flat: bool = False) -> list[str]:
    """Return all subsystem paths.

    Args:
        flat: If True, return only leaf subsystems

    Returns:
        List of fully-qualified subsystem paths

    Examples:
        >>> graph.get_all_subsystem_paths(flat=False)
        ['identity', 'identity.auth', 'identity.user', 'crdt', 'crdt.ser']

        >>> graph.get_all_subsystem_paths(flat=True)
        ['identity.auth', 'identity.user', 'crdt.ser']
    """
    paths = []

    def collect_paths(subsystem: Subsystem, include_parents: bool):
        if include_parents or subsystem.is_leaf():
            paths.append(subsystem.full_path)

        for child in subsystem.subsystems.values():
            collect_paths(child, include_parents)

    for root in self.subsystems.values():
        collect_paths(root, not flat)

    return sorted(paths)
```

**Algorithm:**
1. Recursive depth-first traversal of subsystem tree
2. Collect paths based on `flat` parameter (all vs. leaves only)
3. Sort alphabetically for consistent output

**Time complexity:** O(n) where n = total subsystems (all levels)

**Space complexity:** O(n) for result list

---

## Hierarchical Metrics

### Coupling Ratio Calculation

**File:** `src/jig/decompose/metrics.py`

```python
def calculate_hierarchical_coupling(subsystem: Subsystem, graph: Graph) -> SubsystemMetrics:
    """Calculate coupling ratio for hierarchical subsystem.

    For parent subsystems:
    - Internal edges: edges between any nodes within the subtree (including cross-child)
    - External edges: edges to nodes outside the subtree

    This enables refactoring into hierarchies without degrading metrics.

    Example:
        Given parent subsystem 'identity' with children 'auth' and 'user':
        - Edge auth → user: Internal to 'identity' (both in subtree)
        - Edge auth → core: External to 'identity' (crosses subsystem boundary)
    """
    # Get all nodes in this subsystem tree
    all_nodes = set(subsystem.get_all_nodes(recursive=True))

    internal = 0
    external = 0

    for edge in graph.edges:
        # Skip constraint edges (v7)
        if edge.type == 'satisfies':
            continue

        from_in = edge.from_node in all_nodes
        to_in = edge.to_node in all_nodes

        if from_in and to_in:
            internal += 1
        elif from_in or to_in:
            external += 1

    ratio = internal / external if external > 0 else float('inf')

    return SubsystemMetrics(
        name=subsystem.full_path,
        node_count=len(all_nodes),
        internal_edges=internal,
        external_edges=external,
        coupling_ratio=ratio
    )
```

**Key insight:** Cross-child edges count as **internal** to the parent.

**Example:**

```
Flat subsystems:
  auth (10 nodes, 20 internal, 5 external, ratio: 4.0)
    ↓ Edge to user (external, hurts ratio)
  user (8 nodes, 15 internal, 3 external, ratio: 5.0)
    ↓ Edge to auth (external, hurts ratio)

Nested subsystems:
  identity (18 nodes, 37 internal, 6 external, ratio: 6.17) ✓
    auth (10 nodes, 20 internal, 5 external, ratio: 4.0)
      ↓ Edge to user (internal to parent!)
    user (8 nodes, 15 internal, 3 external, ratio: 5.0)
```

The parent subsystem `identity` has a better coupling ratio because cross-child communication is appropriately counted as internal cohesion.

### Modularity Calculation

```python
def calculate_modularity(graph: Graph) -> float:
    """Calculate Newman modularity score.

    Q = (1/2m) Σ[A_ij - (k_i * k_j)/2m] * δ(c_i, c_j)
    where:
    - m = total edges
    - A_ij = adjacency matrix
    - k_i = degree of node i
    - δ(c_i, c_j) = 1 if nodes in same community, 0 otherwise
    """
    G = graph.to_networkx()

    # Convert subsystems to communities (list of sets)
    # Use LEAF subsystems only (parents don't have direct nodes)
    communities = []
    for subsystem_path in graph.get_all_subsystem_paths(flat=True):
        subsystem = graph.get_subsystem_by_path(subsystem_path)
        if subsystem and subsystem.is_leaf():
            communities.append(set(subsystem.nodes))

    # Use NetworkX modularity calculation
    return community.modularity(G, communities)
```

**Key decision:** Modularity uses **leaf subsystems** as communities, not parents.

**Rationale:**
- Modularity measures partition quality (how well nodes are grouped)
- Only leaf subsystems contain nodes (parents are just organizational)
- Hierarchical structure preserved through coupling metrics, not modularity

---

## Validation

### Nested Subsystem Validation

**File:** `src/jig/core/validator.py`

```python
def validate_nested_subsystems(graph: Graph) -> list[str]:
    """Validate nested subsystem structure.

    Checks:
    - No cycles in subsystem hierarchy
    - Parent subsystems with children have no direct nodes
    - Node subsystem paths are valid
    """
    errors = []

    # Check for cycles (DFS)
    def check_cycles(subsystem: Subsystem, visited: set) -> bool:
        if subsystem.full_path in visited:
            return True  # Cycle detected
        visited.add(subsystem.full_path)
        for child in subsystem.subsystems.values():
            if check_cycles(child, visited.copy()):
                return True
        return False

    for subsystem in graph.subsystems.values():
        if check_cycles(subsystem, set()):
            errors.append(f"Cycle detected in subsystem hierarchy at {subsystem.name}")

    # Check parent subsystems don't have direct nodes
    def check_parent_nodes(subsystem: Subsystem):
        if subsystem.subsystems and subsystem.nodes:
            errors.append(
                f"Parent subsystem '{subsystem.full_path}' has both children and direct nodes"
            )
        for child in subsystem.subsystems.values():
            check_parent_nodes(child)

    for subsystem in graph.subsystems.values():
        check_parent_nodes(subsystem)

    # Check node subsystem paths are valid
    for node_id, node in graph.nodes.items():
        if node.subsystem:
            if not graph.get_subsystem_by_path(node.subsystem):
                errors.append(
                    f"Node {node_id} references invalid subsystem path '{node.subsystem}'"
                )

    return errors
```

**Validation checks:**

1. **No cycles:** Prevents infinite loops in traversal (defensive, can't actually occur via YAML)
2. **Parents have no nodes:** Enforces clean separation (organizational vs. content)
3. **Valid paths:** All node references resolve to actual subsystems

**Error examples:**

```
❌ Cycle detected in subsystem hierarchy at 'identity'
   (Defensive check, can't actually happen via YAML structure)

❌ Parent subsystem 'identity' has both children and direct nodes
   Fix: Move nodes to leaf subsystems (identity.auth or identity.user)

❌ Node O-AUTH-001 references invalid subsystem path 'identity.auth'
   Fix: Define 'identity.auth' in graph-index.yaml subsystems
```

---

## Integration with Constraints (v7)

### Constraint Scoping

Constraints (X nodes) can scope to subsystem hierarchies:

```yaml
---
id: X-PERF-001
type: constraint
title: "API endpoints respond in <100ms"
scope:
  subsystems: [identity, crdt]  # Applies to all children
---
```

This constraint applies to:
- `identity.auth`
- `identity.user`
- `crdt.ser`
- `crdt.sync`

### Implementation

```python
def get_constraints_for_subsystem(self, path: str, recursive: bool = True) -> list[str]:
    """Return all constraints that apply to a subsystem (v7).

    Args:
        path: Subsystem path (e.g., 'core', 'crdt.ser')
        recursive: If True, include constraints from child subsystems

    Returns:
        List of constraint IDs (e.g., ['X-PERF-001'])
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
```

### Constraint Edge Exclusion

**Critical:** Constraint edges (`satisfies` type) are excluded from coupling metrics:

```python
for edge in graph.edges:
    # Skip constraint edges (v7)
    if edge.type == 'satisfies':
        continue

    # Count architectural edges only (implements, depends, etc.)
    # ...
```

**Rationale:**
- Constraints are cross-cutting by nature (span subsystems)
- Including constraint edges would destroy modularity metrics
- Separation of concerns: OSTC = architecture, X = system properties

---

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Typical Time |
|-----------|------------|--------------|
| Path resolution | O(depth) | <10 microseconds |
| Get all nodes (recursive) | O(n) | <1ms for 1000 nodes |
| List all paths | O(subsystems) | <1ms for 100 subsystems |
| Status display | O(subsystems) | <100ms for 100 subsystems |
| Metrics calculation | O(nodes + edges) | <5s for 100 subsystems |

### Space Complexity

| Structure | Complexity | Memory Usage |
|-----------|------------|--------------|
| Subsystem object | O(1) | ~200 bytes |
| Subsystem tree | O(subsystems) | ~20KB for 100 subsystems |
| Node list (recursive) | O(nodes) | ~8KB for 1000 nodes |

### Benchmarks

**Actual measurements (WU20-WU22):**

```bash
# Status display (100 subsystems, nested 3 levels)
jigy status
# Time: 45ms ✓ (target: <100ms)

# Graph queries (1000 nodes, 50 subsystems)
jigy graph list --subsystem identity --recursive
# Time: 120ms ✓ (target: <200ms)

# Decompose metrics (1000 nodes, 2000 edges, 50 subsystems)
jigy decompose metrics
# Time: 2.8s ✓ (target: <5s)
```

All performance targets met.

---

## Design Decisions

### Decision 1: Nodes Only in Leaf Subsystems

**Chosen:** Parent subsystems cannot have direct nodes, only children.

**Alternatives considered:**
1. Allow nodes in any subsystem (parent or leaf)
2. Automatically create "misc" child for parent nodes

**Rationale:**
- **Clarity:** Clear separation of organizational structure (parents) vs. content (leaves)
- **Simplicity:** No ambiguity about node location
- **Validation:** Easy to detect misconfiguration (parent with nodes = error)
- **Semantics:** Parent represents grouping, not a location for nodes

**Trade-off:** Requires explicit leaf subsystem even for single child (e.g., `core.utils` instead of `core` with one child)

**Conclusion:** Worth it for clarity and consistency.

---

### Decision 2: Dot Notation (not Slash or Colon)

**Chosen:** `identity.auth` (dot notation)

**Alternatives considered:**
1. `identity/auth` (slash notation, like file paths)
2. `identity:auth` (colon notation, like XML namespaces)
3. `identity::auth` (double colon, like C++/Rust)

**Rationale:**
- **Familiarity:** Dots used in Python, Java, JavaScript modules
- **Readability:** Dots visually lighter than slashes or colons
- **YAML-friendly:** No escaping needed (slashes can be tricky in YAML)
- **CLI-friendly:** No shell escaping needed (slashes interpreted as paths)

**Trade-off:** Could be confused with file extensions (e.g., `foo.py`)

**Mitigation:** Context makes it clear (subsystem paths don't have common extensions)

**Conclusion:** Dot notation is industry standard for namespaces.

---

### Decision 3: Cross-Child Edges Count as Internal to Parent

**Chosen:** Edge between siblings is internal to their shared parent.

**Alternatives considered:**
1. Cross-child edges always external (hurts parent metrics)
2. Cross-child edges configurable (complexity)

**Rationale:**
- **Refactoring support:** Splitting a subsystem shouldn't worsen metrics
- **Semantic accuracy:** Communication within a module (parent) is internal cohesion
- **Incentive alignment:** Encourages proper hierarchical organization

**Example:**
```
Before split:
  identity (20 nodes, 50 internal, 10 external, ratio: 5.0)

After split into auth + user:
  identity (20 nodes, 50 internal, 10 external, ratio: 5.0)  # Same!
    auth (12 nodes, 30 internal, 5 external, ratio: 6.0)
    user (8 nodes, 15 internal, 3 external, ratio: 5.0)
```

**Trade-off:** Leaf metrics may show more external edges than before split.

**Mitigation:** Analyze at parent level for accurate picture.

**Conclusion:** Correct behavior for hierarchical modularity.

---

### Decision 4: Recursive Traversal with `recursive` Parameter

**Chosen:** Explicit `recursive` parameter (default varies by operation).

**Alternatives considered:**
1. Always recursive (no parameter)
2. Never recursive (always explicit paths)
3. Separate methods (`get_nodes()` vs. `get_nodes_recursive()`)

**Rationale:**
- **Flexibility:** User controls granularity (leaf vs. subtree)
- **Discoverability:** Single method with parameter easier to find than multiple methods
- **Defaults:** Sensible defaults per operation (status recursive, list non-recursive)

**Trade-off:** User must remember parameter meaning.

**Mitigation:** Clear documentation and examples.

**Conclusion:** Standard pattern (e.g., `os.walk(recursive=True)`).

---

### Decision 5: Constraint Edges Excluded from Coupling Metrics

**Chosen:** `satisfies` edges not counted in coupling ratio.

**Alternatives considered:**
1. Include constraint edges (corrupts metrics)
2. Separate metrics (architectural coupling + constraint compliance)

**Rationale:**
- **Separation of concerns:** OSTC models architecture, X models properties
- **Metric integrity:** Constraint edges are cross-cutting, would destroy modularity
- **v7 philosophy:** Constraints as predicates, not graph nodes

**Trade-off:** Constraint compliance tracked separately (not in coupling ratio).

**Mitigation:** Display both metrics (coupling ratio + constraint compliance).

**Conclusion:** Essential for meaningful modularity metrics in systems with constraints.

---

## YAML Format

### Example: Nested Subsystems in graph-index.yaml

```yaml
version: 1.0.0
created: 2025-11-21

subsystems:
  # Root subsystem with children
  identity:
    description: "User identity and authentication"
    subsystems:
      # Leaf subsystem with nodes
      auth:
        description: "Authentication and authorization"
        nodes:
          - O-AUTH-001
          - S-AUTH-001
          - S-AUTH-002

      # Leaf subsystem with nodes
      user:
        description: "User profile management"
        nodes:
          - O-USER-001
          - S-USER-001

  # Root subsystem with children
  crdt:
    description: "CRDT implementation"
    subsystems:
      ser:
        description: "CRDT serialization"
        nodes:
          - S-CRDT-SER-001
          - S-CRDT-SER-002

      sync:
        description: "CRDT synchronization"
        nodes:
          - S-CRDT-SYNC-001

  # Root leaf subsystem (no children)
  core:
    description: "Core infrastructure"
    nodes:
      - O-CORE-001
      - S-CORE-001

nodes:
  O-AUTH-001:
    file: jig/outcomes/O-AUTH-001.md
    type: outcome
    title: "Users authenticate securely"
    subsystem: identity.auth  # Full path with dot notation
```

### Parsing Logic

```python
def parse_subsystems(data: dict, parent_path: str = "") -> dict[str, Subsystem]:
    """Parse subsystems from YAML data recursively."""
    subsystems = {}

    for name, config in data.items():
        subsystem = Subsystem(
            name=name,
            description=config.get("description", ""),
            parent_path=parent_path
        )

        # Parse child subsystems (recursive)
        if "subsystems" in config:
            subsystem.subsystems = parse_subsystems(
                config["subsystems"],
                parent_path=subsystem.full_path
            )

        # Parse nodes (leaf only)
        if "nodes" in config:
            subsystem.nodes = config["nodes"]

        subsystems[name] = subsystem

    return subsystems
```

---

## Testing Strategy

### Unit Tests

**File:** `tests/unit/test_nested_subsystems.py`

Tests cover:
- Subsystem path resolution (`get_subsystem_by_path`)
- Recursive node collection (`get_all_nodes(recursive=True)`)
- Hierarchical listing (`get_all_subsystem_paths`)
- Validation (cycles, parent nodes, invalid paths)
- Backward compatibility (flat subsystems)

**Coverage:** 11 tests, 100% coverage of nested subsystem code paths.

### Integration Tests

**File:** `tests/integration/test_nested_status.py`

Tests cover:
- Status command with hierarchical tree view
- Flat view backward compatibility (`--flat` flag)
- Graph queries with nested paths
- Metrics calculation with hierarchy
- Constraint scoping with nested subsystems

**Coverage:** 10 tests, all CLI commands with nested subsystems.

---

## Future Enhancements

### Possible Improvements

1. **Subsystem metadata inheritance:**
   - Child subsystems inherit parent tags/properties
   - Example: `identity` tagged as `security:high` → all children inherit

2. **Visualization:**
   - Generate tree diagrams (ASCII or graphviz)
   - Interactive web visualization of subsystem hierarchy

3. **Search by partial path:**
   - `jigy graph list --subsystem *auth` matches `identity.auth`, `services.auth`
   - Glob-style matching for subsystem queries

4. **Subsystem renaming:**
   - `jigy subsystem rename identity.auth identity.authn`
   - Automatically updates all node references

5. **Subsystem move:**
   - `jigy subsystem move identity.auth services.identity.auth`
   - Restructure hierarchy without manual YAML editing

---

## References

- [User Guide](../user-guide/NESTED_SUBSYSTEMS.md) - Concepts and usage
- [Migration Guide](../user-guide/MIGRATION_NESTED.md) - Flat to nested migration
- [Tutorial](../tutorials/NESTED_SUBSYSTEMS_TUTORIAL.md) - Hands-on example
- [JIG Concept v7](J013-JIG-Concept-v7.md) - OSTCX model
- [Data Formats](DATA_FORMATS.md) - File format specifications

---

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Maintained By:** JIG Core Team
