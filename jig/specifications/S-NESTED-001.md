---
id: S-NESTED-001
type: specification
title: Nested subsystem data structure with hierarchical organization
subsystem: core
status: active
created: 2025-11-21
---

# Specification: Nested Subsystem Data Structure

## Purpose

Support hierarchical organization of subsystems using a recursive tree structure, enabling multi-level decomposition of system architecture (e.g., `crdt.ser`, `crdt.merge`).

## Requirements

### 1. Subsystem Data Structure

```python
@dataclass
class Subsystem:
    """Hierarchical subsystem node."""
    name: str                                    # Local name (e.g., "ser")
    nodes: list[str]                            # Node IDs (leaf only)
    subsystems: dict[str, "Subsystem"]          # Child subsystems
    description: str = ""
    parent_path: str = ""                       # Fully-qualified parent
```

### 2. Path Resolution

- **Local name:** `ser` (within parent context)
- **Fully-qualified path:** `crdt.ser` (global identifier)
- **Parent path:** `crdt` (parent subsystem)

Example hierarchy:
```
crdt/
├── crdt.ser (child)
├── crdt.merge (child)
└── crdt.conflict (child)
```

### 3. Node Assignment Rules

- **Leaf subsystems:** Can contain nodes
- **Parent subsystems:** Can contain child subsystems only (no direct nodes)
- **Node assignment:** Each node belongs to exactly one subsystem
- **Subsystem annotation:** Nodes use fully-qualified paths in `@jig` annotations

### 4. Core Methods

```python
def full_path(self) -> str:
    """Return fully-qualified path (e.g., 'crdt.ser')."""

def is_leaf(self) -> bool:
    """Return True if subsystem has no children."""

def get_all_nodes(self, recursive: bool = False) -> list[str]:
    """Return nodes in this subsystem (optionally recursive)."""

def find_subsystem(self, path: str) -> Subsystem | None:
    """Navigate hierarchy by path (e.g., 'crdt.ser')."""
```

### 5. Backward Compatibility

- Flat subsystems (no children) continue to work unchanged
- Path `auth` equivalent to single-level subsystem `auth`
- No breaking changes to existing annotations

## Implementation Notes

**Location:** `src/jig/core/graph.py:34-100`

**Data Loading:** Parse hierarchical YAML from `jig/graph-index.yaml`:

```yaml
subsystems:
  crdt:
    description: "CRDT implementation"
    subsystems:
      ser:
        nodes: [C-SER-001, C-SER-002]
      merge:
        nodes: [C-MERGE-001]
```

## Test Coverage

- T-NESTED-001: Parse nested subsystem structure from YAML
- T-NESTED-003: Recursive node collection
- T-NESTED-006: Backward compatibility with flat subsystems

## References

- Implementation: `src/jig/core/graph.py:34`
- Related: S-NESTED-002 (path resolution), S-NESTED-005 (validation)
