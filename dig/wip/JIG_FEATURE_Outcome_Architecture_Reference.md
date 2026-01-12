# JIG Feature Request: Outcome Architecture Reference

**Date:** 2026-01-12
**Origin:** ASE F083 JIG Reset (WU5.3 planning)

---

## Summary

Add an `architecture:` field to Outcome (O-###) frontmatter that references one or more Architecture documents (A-###). This establishes explicit ownership between Outcomes and the architectural concerns they value.

---

## Motivation

During ASE's JIG reset, we discovered that Outcomes naturally align with Architecture documents:

| Category | A-doc | Example Outcomes |
|----------|-------|------------------|
| ANK | A-030 | Convergence, Ordering, Serialization |
| HOST | A-031 | Pure Logic, State Observability, Persistence |
| HARNESS | A-032 | Testable Components, Responsive GUI |
| SERVER | A-034 | Plane Isolation, Reliability, Observability |

This relationship is currently implicit. Making it explicit enables:
1. **Validation:** Warn if an Outcome doesn't reference any A-doc
2. **Navigation:** Query "which outcomes belong to A-030?"
3. **Completeness checking:** "Does every A-doc have outcomes?"
4. **Reassignment:** Change ownership at graph level without renaming IDs

---

## Proposed Schema

```yaml
---
id: O-101
type: outcome
architecture: [A-030]           # NEW: list of A-doc IDs
supports_goals: [G-002]
specifies: [S-001, S-002]
---
```

### Field Definition

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `architecture` | `list[string]` | Optional | A-doc IDs this outcome relates to |

### Validation Rules

1. Each value in `architecture:` must be a valid A-doc ID (A-###)
2. Referenced A-docs must exist in `jig/architecture/`
3. Empty list or missing field is allowed (for Global outcomes)

### Graph Representation

Add edge type `O-### --values--> A-###` in intent graph:

```
O-101 --values--> A-030
O-101 --supports_goals--> G-002
O-101 --specifies--> S-001
```

---

## Examples

**ANK Outcome (single A-doc):**
```yaml
---
id: O-101
type: outcome
architecture: [A-030]
supports_goals: [G-002]
specifies: []
---

# Distributed State Convergence

All devices converge to identical BikeState regardless of network conditions.
```

**Cross-cutting Outcome (multiple A-docs):**
```yaml
---
id: O-107
type: outcome
architecture: [A-020, A-030]
supports_goals: [G-001]
specifies: []
---

# Four-Tier Data Separation

Data tiers (CRDT, telemetry, settings, config) have distinct sync semantics.
```

**Global Outcome (no specific A-doc):**
```yaml
---
id: O-120
type: outcome
architecture: []
supports_goals: [G-001]
specifies: []
---

# Component Independence

Components can be modified, tested, and deployed independently.
```

---

## Impact

### CLI Changes

`jigy validate` should:
- Parse `architecture:` field
- Validate referenced A-docs exist
- Optionally warn on empty `architecture:` (configurable)

### Graph Changes

`jig/generated/intent-graph.ndjson` gains new edge type:
```json
{"source": "O-101", "target": "A-030", "relation": "values"}
```

### Query Capabilities

Enable queries like:
- "Which outcomes value A-030?" → filter by architecture field
- "Which A-docs have no outcomes?" → coverage gap detection

---

## Migration

Existing O-### documents without `architecture:` field remain valid (field is optional). Projects can adopt incrementally.

---

## Alternatives Considered

### Architecture-prefixed IDs (O-030-01)

Rejected because:
- Renaming required if ownership changes
- ID becomes invalid if A-doc renumbered
- Couples ID to current organization

### Tower field instead of architecture

Rejected because:
- Towers are code organization, not intent organization
- Some outcomes span towers (HOST applies to device, gateway, cloud)
- Architecture alignment is the deeper relationship

---

## Decision

Adopt `architecture:` field as optional list in O-### frontmatter. Implement validation in `jigy validate`. Add to intent graph as `values` edges.
