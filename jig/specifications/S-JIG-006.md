---
id: S-JIG-006
type: specification
title: "Graph loads O/S/X markdown nodes only"
subsystem: core
created: 2025-11-20
---

# Specification: Graph loads O/S/X markdown nodes only

The `Graph.load_from_dir()` function scans only the outcomes/, specifications/, and constraints/ directories for markdown nodes. Test (T) and code (C) nodes are discovered via annotation scanning, not directory scanning.

## Requirements

### Functional Requirements
- `node_dirs` in Graph.load_from_dir() contains: ["outcomes", "specifications", "constraints"]
- Graph loading does NOT scan jig/tests/ directory
- T/C nodes will be added to graph via future annotation discovery feature
- Existing graph operations (deps, show, status) work with O/S/X nodes only

### Non-Functional Requirements
- Performance: Reduced directory scanning improves load time
- Simplicity: Clear separation between markdown (O/S/X) and annotation (T/C) nodes
- Maintainability: No markdown file maintenance for test nodes

### Implementation Approach
- Update `node_dirs` list in src/jig/core/graph.py (Line 89)
- Add comment explaining OSTCX model split
- Remove "tests" from directory list
- Future feature: Separate annotation scanner adds T/C nodes after markdown load

## Rationale

The OSTCX model explicitly separates:
- **O/S/X nodes**: Markdown files representing timeless intent and system properties
- **T/C nodes**: Annotations in code representing executable reality

Graph loading should only scan directories containing markdown nodes. This:
- Reduces scanning overhead (one fewer directory)
- Prevents confusion about where to create test nodes
- Aligns with architectural principle: tests are code, not documentation
- Prepares for future annotation discovery feature

This change supports C-PERF-001 (graph loading <1s for 1k nodes) by reducing filesystem operations.

## Acceptance Criteria

- `node_dirs` contains exactly 3 entries: outcomes, specifications, constraints
- Graph loading completes successfully without jig/tests/ directory
- All existing graph commands (deps, show, status, validate) work correctly
- Unit tests verify 3 directories scanned, not 4
- Graph loading performance maintained (<1 second for 1k nodes)

## Related

- implements: O-JIG-002 (JIG v7 OSTCX model implemented)
- supports: C-PERF-001 (Graph loading <1 second for 1k nodes)
- subsystem: core

## History

- 2025-11-20: Created during WU0 (S008 PLAN, remove-tests-directory branch)

