---
id: S-JIGY-014
type: specification
title: Commands report consistent node and edge counts
subsystem: jigy-tool
implements:
  - O-JIGY-001
created: 2025-11-21
source_scope: docs/wip/S021_SCOPE_validate_consistency.md
---

# Specification: Consistent Count Reporting

## Purpose

Ensure all commands (validate, status, index rebuild) report the same node and edge counts for the same graph state.

## Requirements

### 1. Unified Counting Logic

All commands MUST use the same counting logic:

```python
# Count nodes by type
def count_nodes_by_type(graph: Graph) -> dict[str, int]:
    counts = {}
    for node in graph.nodes.values():
        node_type = node.type
        counts[node_type] = counts.get(node_type, 0) + 1
    return counts

# Count edges (deduplicated)
def count_edges(graph: Graph) -> int:
    unique_edges = {(e.from_node, e.to_node, e.type) for e in graph.edges}
    return len(unique_edges)
```

### 2. Edge Deduplication

Edges MUST be deduplicated before counting:
- Key: `(from_node, to_node, type)` tuple
- Same edge from multiple sources (frontmatter, annotations, edges section) = 1 edge
- Report deduplicated count consistently

### 3. Scan All Markdown Files

Index rebuild MUST scan all node directories:

```python
node_dirs = ["outcomes", "specifications", "constraints"]
for node_dir in node_dirs:
    dir_path = intent_dir / node_dir
    if not dir_path.exists():
        continue  # OK if directory doesn't exist yet

    for md_file in dir_path.glob("*.md"):
        # Parse and count
```

### 4. Handle Parsing Errors

Don't silently skip files:
- Log parsing errors
- Include in error count
- Report which files failed

### 5. Verbose Output

Index rebuild SHOULD show breakdown:

```
Scanning sources:
  ✓ jig/outcomes/*.md (16 nodes)
  ✓ jig/specifications/*.md (39 nodes)
  ✓ jig/constraints/*.md (1 node)
  ✓ src/ for @jig annotations (37 code nodes)
  ✓ tests/ for @jig annotations (122 test nodes)

Total nodes: 215 (16 O, 39 S, 1 X, 37 C, 122 T)
Total edges: 183 (after deduplication)
```

## Current Behavior (Broken)

- `index rebuild` says: 211 nodes, ~422 edges
- `status` says: 215 nodes, 183 edges
- `validate` says: 56 nodes (O/S/X only)
- Mismatch: 4 nodes missing, edge count unclear

## Correct Behavior

All commands report:
- 215 nodes (16 O, 39 S, 1 X, 37 C, 122 T)
- 183 edges (deduplicated)
- 7 subsystems (after S-JIGY-013)

## Implementation Locations

- `src/jig/cli/index.py` (rebuild command)
- `src/jig/cli/status.py` (status command)
- `src/jig/core/validator.py` (validate command)

## Test Coverage

- Integration test: Run all 3 commands, verify counts match
- Unit test: Edge deduplication logic
- Unit test: Node counting by type

## References

- SCOPE: docs/wip/S021_SCOPE_validate_consistency.md (Issues 3 & 4)
- Related: S-JIGY-012 (unified graph loading)
- Implements: O-JIGY-001 (accurate graph representation)
