---
id: S-JIGY-013
type: specification
title: Index rebuild exports subsystems to graph-index.yaml
subsystem: jigy-tool
implements:
  - O-JIGY-002
created: 2025-11-21
source_scope: docs/wip/S021_SCOPE_validate_consistency.md
---

# Specification: Subsystem Export in Index Rebuild

## Purpose

Enable subsystem-based queries and metrics by persisting subsystem structure to `graph-index.yaml`.

## Requirements

### 1. Infer Subsystems from Node Metadata

Build subsystem structure from `subsystem:` field on nodes:

```python
def build_subsystems_from_nodes(nodes: list[dict]) -> dict:
    """Group nodes by subsystem, handle nested paths."""
    subsystems = {}
    for node in nodes:
        subsystem_path = node.get("subsystem")
        if not subsystem_path:
            continue

        # Handle nested (e.g., "crdt.ser")
        if "." in subsystem_path:
            parts = subsystem_path.split(".")
            parent = parts[0]
            child = parts[1]

            if parent not in subsystems:
                subsystems[parent] = {"subsystems": {}}
            if child not in subsystems[parent]["subsystems"]:
                subsystems[parent]["subsystems"][child] = {"nodes": []}

            subsystems[parent]["subsystems"][child]["nodes"].append(node["id"])
        else:
            # Top-level subsystem
            if subsystem_path not in subsystems:
                subsystems[subsystem_path] = {"nodes": []}
            subsystems[subsystem_path]["nodes"].append(node["id"])

    return subsystems
```

### 2. Write Subsystems Section

Add `subsystems:` to graph-index.yaml:

```yaml
version: '1.0'
nodes:
  - id: C-AUTH-001
    subsystem: auth
    ...

subsystems:  # ← ADD THIS
  auth:
    nodes: [C-AUTH-001, C-AUTH-002, T-AUTH-001]
  core:
    nodes: [C-GRAPH-001, C-NESTED-001, T-STATUS-001]
  crdt:
    subsystems:
      ser:
        nodes: [C-SER-001, C-SER-002]
      merge:
        nodes: [C-MERGE-001]
```

### 3. Handle Nested Subsystems

Support dot-notation paths (e.g., `crdt.ser`):
- Parse path into parent and child
- Create parent subsystem if doesn't exist
- Add child subsystem under parent
- Assign nodes to leaf subsystems only

### 4. Preserve Subsystems on Load

Ensure `Graph.load_from_dir()` loads subsystems correctly:
- Parse `subsystems:` section
- Recreate subsystem hierarchy
- Verify nodes assigned correctly

## Current Behavior (Broken)

```yaml
# graph-index.yaml
version: '1.0'
nodes:
  - id: C-AUTH-001
    subsystem: auth  # ← Metadata on node
    ...
# Missing: subsystems section
```

**Result:**
- `jigy status` reports "0 subsystems"
- Subsystem queries fail
- Metrics can't be calculated

## Correct Behavior

```yaml
# graph-index.yaml
version: '1.0'
nodes:
  - id: C-AUTH-001
    subsystem: auth
    ...

subsystems:
  auth:
    nodes: [C-AUTH-001, C-AUTH-002]
  core:
    nodes: [C-GRAPH-001, C-NESTED-001]
```

**Result:**
- `jigy status` reports correct subsystem count
- Subsystem queries work
- Metrics calculable by subsystem

## Implementation Location

- File: `src/jig/cli/index.py`
- Function: `rebuild()` command
- Add: `build_subsystems_from_nodes()` helper
- Modify: Write subsystems to graph-index.yaml

## Test Coverage

- Unit test: build_subsystems_from_nodes() with flat and nested subsystems
- Integration test: Rebuild index, verify subsystems section exists
- Integration test: Status command shows correct subsystem count

## References

- SCOPE: docs/wip/S021_SCOPE_validate_consistency.md (Issue 2)
- Related: S-NESTED-001 (subsystem data structure)
- Implements: O-JIGY-002 (subsystem navigation)
