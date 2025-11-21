---
id: O-JIGY-002
type: outcome
title: Developers can navigate Intent graph efficiently
subsystem: jigy-tool
status: active
created: 2025-11-21
---

# Outcome: Efficient Graph Navigation

## Value Proposition

Understanding a large codebase requires following Intent chains: "This Outcome is satisfied by these Specifications, implemented by this Code, verified by these Tests." Developers need to navigate these relationships quickly to understand system structure, find related work, and make informed changes.

**User Impact:**
- Find all implementations of an Outcome in <1 second
- Trace dependency paths between nodes instantly
- Explore subsystem boundaries and cross-cutting concerns
- Answer "what depends on this?" without manual searching

## Current Problem

jigy v0.1.0 has navigation commands (`jigy graph`, `jigy node`) but they don't work without edges. Can't trace relationships, can't find paths, can't explore the Intent structure. Developers fall back to manual grep, losing the benefit of structured Intent.

## Success Criteria

1. **Node Queries** (<100ms response)
   - Show node details with all relationships
   - Display incoming and outgoing edges
   - List related nodes (implementations, verifications, dependencies)

2. **Graph Traversal** (<500ms response)
   - Trace from node with depth limit (default depth=2)
   - Find shortest path between two nodes
   - Show dependency tree (all transitive dependencies)

3. **Subsystem Navigation** (<200ms response)
   - List all nodes in a subsystem
   - Show internal edges (within subsystem)
   - Show external edges (cross-subsystem dependencies)
   - Calculate coupling metrics (internal/external ratio)

4. **Multiple Output Formats**
   - Human-readable text (default, for terminal use)
   - JSON (for scripting and tools)
   - YAML (for config and integration)
   - DOT format (for visualization tools)

## Use Cases

**UC1: Understanding an Outcome**
```bash
jigy node O-AUTH-001
# Shows: Title, subsystem, all specifications that implement it,
# all tests that verify it, related outcomes
```

**UC2: Finding Implementation Chain**
```bash
jigy trace O-AUTH-001 --depth 3
# Shows: O-AUTH-001 → S-AUTH-001, S-AUTH-002 → C-AUTH-001, C-AUTH-002 
#        → T-AUTH-001, T-AUTH-003
```

**UC3: Analyzing Subsystem Coupling**
```bash
jigy subsystem auth --edges
# Shows: Node counts, internal edges, external edges to other subsystems
```

**UC4: Finding Dependency Path**
```bash
jigy path O-PS-001 C-PS-005
# Shows: Shortest path from outcome to code implementation
```

## Acceptance Tests

```bash
# Query performance
time jigy node S-AIR-001
# Should complete in <100ms

# Traversal performance
time jigy trace O-PS-001 --depth 3
# Should complete in <500ms

# Subsystem query
time jigy subsystem airspace
# Should complete in <200ms

# Output formats
jigy node S-AIR-001 --json | jq .
jigy list specification --yaml
```

## Related Specifications

- S-JIGY-003: Unified node registry (enables fast lookups)
- S-JIGY-005: Graph query commands
- S-JIGY-006: Path finding and traversal
- S-JIGY-007: Subsystem queries

## Metrics

- **Query Speed:** <100ms for node queries on 1000-node graph
- **Traversal Speed:** <500ms for depth-3 trace on 1000-node graph
- **Subsystem Speed:** <200ms for subsystem analysis on 1000-node graph
- **Usability:** Developers can answer "what implements X?" in one command

