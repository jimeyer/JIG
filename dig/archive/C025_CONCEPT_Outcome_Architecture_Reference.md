---
type: concept
title: Outcome Architecture Reference
status: implemented
decision: completed
created: 1736726400
created_human: 2026-01-12 16:00 PST
parent: null
children: []
prompt: |
  Feature request from ASE F083 JIG Reset (WU5.3 planning).
  Add architecture: field to Outcome frontmatter to establish
  explicit ownership between Outcomes and Architecture documents.
---

# Outcome Architecture Reference

_Explicit alignment between Outcomes (O-###) and Architecture documents (A-###)_

---

## Core Insight

Outcomes naturally align with Architecture documents:

| Category | A-doc | Example Outcomes |
|----------|-------|------------------|
| ANK | A-030 | Convergence, Ordering, Serialization |
| HOST | A-031 | Pure Logic, State Observability, Persistence |
| HARNESS | A-032 | Testable Components, Responsive GUI |
| SERVER | A-034 | Plane Isolation, Reliability, Observability |

This relationship is currently implicit. Making it explicit via an `architecture:` field enables:

1. **Validation** - Warn if an Outcome doesn't reference any A-doc
2. **Navigation** - Query "which outcomes belong to A-030?"
3. **Completeness checking** - "Does every A-doc have outcomes?"
4. **Reassignment** - Change ownership at graph level without renaming IDs

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

---

## Graph Representation

Add edge type `O-### --values--> A-###` in intent graph:

```
O-101 --values--> A-030
O-101 --supports_goals--> G-002
O-101 --specifies--> S-001
```

New edge in `jig/generated/intent-graph.ndjson`:
```json
{"source": "O-101", "target": "A-030", "relation": "values"}
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

### Query Capabilities

- "Which outcomes value A-030?" - filter by architecture field
- "Which A-docs have no outcomes?" - coverage gap detection

---

## Alternatives Rejected

### Architecture-prefixed IDs (O-030-01)

- Renaming required if ownership changes
- ID becomes invalid if A-doc renumbered
- Couples ID to current organization

### Tower field instead of architecture

- Towers are code organization, not intent organization
- Some outcomes span towers (HOST applies to device, gateway, cloud)
- Architecture alignment is the deeper relationship

---

## Migration

Existing O-### documents without `architecture:` field remain valid (field is optional). Projects can adopt incrementally.

---

## Decision

Adopt `architecture:` field as optional list in O-### frontmatter. Implement validation in `jigy validate`. Add to intent graph as `values` edges.

---

## References

- [[jig-dev/dig/wip/JIG_FEATURE_Outcome_Architecture_Reference]] - Original feature request
