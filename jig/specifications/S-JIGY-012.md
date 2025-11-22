---
id: S-JIGY-012
type: specification
title: Validator uses unified graph loading for all node types
subsystem: jigy-tool
implements:
  - O-JIGY-001
created: 2025-11-21
source_scope: docs/wip/S021_SCOPE_validate_consistency.md
---

# Specification: Unified Validator Graph Loading

## Purpose

Ensure `jigy validate` understands all node types (O/S/X/C/T) by using the same graph loading logic as `status` and other commands.

## Requirements

### 1. Use Graph.load_from_dir()

The validator MUST use `Graph.load_from_dir(intent_dir)` to load the complete graph:
- Loads markdown files (O/S/X nodes)
- Loads graph-index.yaml (C/T nodes)
- Returns complete node set

### 2. Validate Markdown Nodes Explicitly

After loading graph, validate O/S/X nodes:
- Parse each markdown file
- Check YAML frontmatter validity
- Verify ID format, type consistency
- Report parsing errors

### 3. Validate Annotation Nodes Indirectly

C/T nodes validated through successful loading:
- If `Graph.load_from_dir()` succeeds, C/T nodes are valid
- If loading fails, report error with context
- Don't re-parse annotation files

### 4. Check for Duplicates Across All Types

Use complete node set to detect duplicates:
- Count occurrences of each node ID
- Report duplicates across all types (O/S/X/C/T)
- Fail validation if duplicates found

## Current Behavior (Broken)

```python
# Validator only scans markdown
for node_dir in ["outcomes", "specifications", "constraints"]:
    for node_file in node_dir.glob("*.md"):
        node_ids[node.id] = node_file  # Only O/S/X

# Then validates against graph-index (ALL nodes)
indexed_ids = {n["id"] for n in graph_data["nodes"]}  # O/S/X/C/T
for indexed_id in indexed_ids:
    if indexed_id not in node_ids:  # C/T missing!
        errors.append(f"Non-existent node: {indexed_id}")  # FALSE ERROR
```

**Result:** 159 false errors for all C/T nodes

## Correct Behavior

```python
# Load complete graph (like status does)
from jig.core.graph import Graph
graph = Graph.load_from_dir(intent_dir)
all_node_ids = set(graph.nodes.keys())  # All 215 nodes

# Validate markdown nodes explicitly
for node_dir in ["outcomes", "specifications", "constraints"]:
    for node_file in (intent_dir / node_dir).glob("*.md"):
        try:
            node = parse_ostc_node(node_file)
            result = validate_node(node)
            errors.extend(result.errors)
        except Exception as e:
            errors.append(f"Failed to parse {node_file}: {e}")

# C/T nodes validated through successful graph load
# Check duplicates across all types
node_id_counts = {}
for node_id in all_node_ids:
    node_id_counts[node_id] = node_id_counts.get(node_id, 0) + 1
for node_id, count in node_id_counts.items():
    if count > 1:
        errors.append(f"Duplicate node ID: {node_id}")
```

**Result:** 0 false errors, all node types validated

## Implementation Location

- File: `src/jig/core/validator.py`
- Function: `validate_graph(intent_dir: Path) -> ValidationResult`
- Lines: ~130-188 (refactor needed)

## Test Coverage

- Unit test: Validate graph with all node types (O/S/X/C/T)
- Integration test: Run validate on real codebase, expect 0 false errors
- Regression test: Ensure C/T nodes don't cause "non-existent" errors

## References

- SCOPE: docs/wip/S021_SCOPE_validate_consistency.md (Issue 1)
- Related: S-JIGY-002 (graph loading), S-CLI-008 (validate output)
- Implements: O-JIGY-001 (accurate graph representation)
