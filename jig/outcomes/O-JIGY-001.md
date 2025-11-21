---
id: O-JIGY-001
type: outcome
title: JIG graph accurately reflects all OSTC relationships
subsystem: jigy-tool
status: active
created: 2025-11-21
---

# Outcome: JIG Graph Accuracy

## Value Proposition

Developers using JIG need to trust that the graph representation matches the actual Intent structure in their codebase. When `jigy status` reports node and edge counts, those numbers must be accurate. When validation runs, it must catch real issues.

**User Impact:** 
- Developers see complete Intent alignment, not partial or incorrect views
- No missing edges means no hidden dependencies
- Validation catches drift between code and Intent immediately
- Team can make architectural decisions based on accurate metrics

## Current Problem

jigy v0.1.0 reports "0 edges" despite relationship data existing in frontmatter. This makes the tool useless for understanding system structure. Developers can't see what implements what, can't trace dependencies, can't validate alignment.

## Success Criteria

1. **Accurate Node Counts**
   - All OSTC node types discovered (O, S, T, C)
   - Count matches actual files and annotations
   - No phantom nodes, no missing nodes

2. **Accurate Edge Counts**
   - All relationships parsed from frontmatter (implements, satisfies, verifies, depends_on)
   - All relationships loaded from graph-index.yaml
   - Count matches expected relationships (~113 edges for ASE-A)

3. **Complete Graph Representation**
   - Every node reachable through queries
   - Every edge traversable
   - No disconnected subgraphs that should be connected

4. **Validation Detects Issues**
   - Broken references (edge to non-existent node)
   - Orphaned nodes (no incoming or outgoing edges)
   - Invalid edge types (e.g., O→S when should be S→O)

## Acceptance Tests

```bash
# Against ASE-A project
cd ~/Code/ASE-A
jigy status
# Should report: 126 nodes (18 O, 47 S, 24 C, 37 T), ~113 edges, 7 subsystems

jigy validate --check-all
# Should detect any broken references or orphans

jigy edges S-AIR-001
# Should show all edges connected to this node
```

## Related Specifications

- S-JIGY-001: Parse frontmatter relationships
- S-JIGY-002: Load graph-index.yaml
- S-JIGY-004: Edge validation with type-aware rules

## Metrics

- **Accuracy:** 100% of nodes discovered, 100% of edges counted
- **Validation:** 0% false negatives (catches all real issues)
- **Performance:** <1 second to build complete graph on 1000-node project

