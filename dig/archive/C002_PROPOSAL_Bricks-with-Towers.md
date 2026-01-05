---
title: "Proposal: Bricks with Towers"
type: exploration
status: implemented
decision: "Towers added to brick model in A-001"
created: 1767412904
created_human: "2026-01-02 22:01 CST"
parent: null
children: ['[[C003_SCOPE_Extended-Intent-Hierarchy-and-Towers]]']
---
# Proposal: Bricks with Towers

**Status:** Draft
**Author:** Claude + Jim
**Date:** 2025-12-29
**Related:** [contextBricks.md](contextBricks.md), [A-002: Four-Component Separation](../../jig/architecture/A-002_Four_Component_Separation.md)

---

## Problem Statement

The current brick/layer model provides **one axis** of organization:

- **Layers** (horizontal) — dependency depth, layer N depends only on layers < N

But ASE's architecture (A-002) requires a **second axis**:

- **Components** (vertical) — SERVER, HARNESS, DEVICE LOGIC as isolated code partitions

Currently, there's no way to:
1. Declare which component a brick belongs to
2. Enforce complete isolation between components
3. Query "show me all bricks in the HARNESS component"

---

## Solution: Introduce Towers

A **Tower** is a vertical partition of the codebase. Towers are **completely independent** — no code imports cross tower boundaries.

```
              │  server  │  harness  │  device-logic  │  ← Towers
  ────────────┼──────────┼───────────┼────────────────┤
  Layer 2     │   B-s2   │   B-h2    │                │
  Layer 1     │   B-s1   │   B-h1    │     B-d1       │
  Layer 0     │   B-s0   │   B-h0    │     B-d0       │
              │          │           │                │
                               Layers ↓
```

- **Layers** = horizontal rows (dependency depth within a tower)
- **Towers** = vertical columns (complete isolation)
- **Bricks** = cells in the Layer × Tower matrix

### Key Principle: Towers Are Independent

**No cross-tower code dependencies.** Ever.

How do towers communicate? Through **INTENT** — the shared specifications, contracts, and test vectors that all towers implement against. INTENT is not code; it's the shared understanding that enables independent implementation.

```
         ┌─────────────────────────────────────────────┐
         │                   INTENT                     │
         │  (Charter, Specs, Contracts, Test Vectors)   │
         │             NOT CODE — NO TOWER             │
         └──────────┬──────────┬──────────┬────────────┘
                    │          │          │
           implements      implements    implements
                    │          │          │
                    ▼          ▼          ▼
              ┌─────────┐ ┌─────────┐ ┌───────────────┐
              │ server  │ │ harness │ │ device-logic  │
              │ (tower) │ │ (tower) │ │   (tower)     │
              └─────────┘ └─────────┘ └───────────────┘
                    │          │          │
                  ISOLATED   ISOLATED   ISOLATED
```

---

## Tower Definitions

Towers are **project-defined**. Each project declares its own towers based on its architectural needs. Towers are **implicit** — they're inferred from usage in bricks, not declared separately.

### Example: ASE's Three Towers

ASE (the reference project) uses three towers based on A-002:

| Tower ID | A-002 Component | Contains | Language |
|----------|-----------------|----------|----------|
| `server` | #2 SERVER | Planes, Enforcer, Monitors, Routing | Python forever |
| `harness` | #3 HARNESS | Transport, Timers, GUI, Effect Executor | Python forever |
| `device-logic` | #4 DEVICE LOGIC | CRDT, Protocol, Operations, IGP | Python → Rust/Swift/Kotlin |

### Single-Tower Projects

Projects that don't need vertical partitioning simply omit the `tower` field. All bricks belong to an implicit default tower, and cross-tower validation is skipped.

### What About INTENT?

INTENT (#1 from A-002) is **not a tower**. Towers partition executable code. INTENT contains:
- Markdown documents (Charter, Architecture)
- YAML/JSON specifications
- Test vectors

INTENT is managed separately — it's the **bridge** that enables tower independence.

### Tower ID Format

Tower IDs use **kebab-case** for language-agnostic compatibility:

- `server` ✓
- `harness` ✓
- `device-logic` ✓

This format works across Python, Rust, Swift, Kotlin, TypeScript, etc.

---

## Updated Brick Definition

### Current Format

```yaml
bricks:
  - id: B-crdt-core
    name: CRDT Core Primitives
    layer: 1
    units:
      - M-ase.device_logic.crdt.core
```

### Proposed Format (Multi-Tower Project)

```yaml
bricks:
  - id: B-crdt-core
    name: CRDT Core Primitives
    layer: 1
    tower: device-logic              # NEW: optional field
    units:
      - M-ase.device_logic.crdt.core
```

### Proposed Format (Single-Tower Project)

```yaml
bricks:
  - id: B-decorators
    name: JIG Core Decorators
    layer: 0
    # tower omitted — single-tower project
    units:
      - M-jig.__init__
```

### Tower Field Rules

1. **Optional** — omit for single-tower projects
2. **Implicit** — towers are inferred from usage, not declared separately
3. **Kebab-case** — tower IDs use kebab-case for cross-language compatibility
4. **Consistent** — if any brick has a tower, cross-tower validation is enabled

---

## Dependency Rules

### The Core Rule

**Layer rules apply within a tower. Cross-tower dependencies are forbidden.**

```
WITHIN tower:    Layer N may depend on layers 0..(N-1)
ACROSS towers:   FORBIDDEN — no exceptions
```

### Validation Logic

```
is_valid_dependency(from_brick, to_brick):
    if from_brick.tower != to_brick.tower:
        return FALSE  # Cross-tower = always invalid

    if from_brick.layer <= to_brick.layer:
        return FALSE  # Must depend on lower layer

    return TRUE
```

### Why No Exceptions?

A-002 shows a dependency matrix with some allowed cross-tower imports. We simplify:

| A-002 Says | We Say | Why |
|------------|--------|-----|
| SERVER may import DEVICE LOGIC types | No | SERVER uses INTENT specs to understand message formats |
| HARNESS may import DEVICE LOGIC interface | No | HARNESS uses INTENT specs for the DeviceLogic contract |
| HARNESS may import SERVER connection | No | Both implement INTENT transport specs independently |

The pattern: **Don't share code. Share specifications.**

---

## Language-Agnostic Unit References

For multi-language support, unit references should be language-tagged:

```yaml
# Python units (current)
units:
  - py:M-ase.device_logic.crdt.core
  - py:C-ase.device_logic.crdt.LWWRegister
  - py:F-ase.device_logic.crdt.merge

# Rust units (future)
units:
  - rs:M-device_logic::crdt::core
  - rs:S-device_logic::crdt::LWWRegister    # S = struct
  - rs:F-device_logic::crdt::merge

# Swift units (future)
units:
  - swift:M-DeviceLogic.CRDT.Core
  - swift:C-DeviceLogic.CRDT.LWWRegister
  - swift:F-DeviceLogic.CRDT.merge
```

**Unit prefix format:** `{lang}:{type}-{path}`

| Prefix | Meaning |
|--------|---------|
| `M-` | Module (all functions) |
| `C-` | Class (all methods) |
| `S-` | Struct (all methods) — Rust/Swift |
| `F-` | Single function |

**Migration:** Existing Python-only units remain valid. Language prefix defaults to `py:` if omitted.

---

## CLI Commands

### Existing Commands (Enhanced)

```bash
jigy validate        # Now validates tower isolation
jigy layers          # Show layer structure (within each tower)
```

### New Commands

```bash
jigy towers                    # List all towers with brick counts
jigy towers <tower_id>         # Show all bricks in a tower
jigy matrix                    # Show 2D Layer × Tower grid
```

### Example Output: `jigy towers`

```
Towers (3):

server (5 bricks)
  Layer 0: B-server-transport
  Layer 1: B-planes-core, B-enforcer
  Layer 2: B-simops

harness (4 bricks)
  Layer 0: B-harness-transport
  Layer 1: B-effect-executor, B-timers
  Layer 2: B-gui

device-logic (6 bricks)
  Layer 0: B-protocol-codecs, B-elc
  Layer 1: B-crdt-core, B-operations
  Layer 2: B-igp, B-replicator
```

### Example Output: `jigy matrix`

```
              │  server  │  harness  │  device-logic  │
──────────────┼──────────┼───────────┼────────────────┤
Layer 2       │  B-sim   │  B-gui    │  B-igp,B-rep   │
Layer 1       │  B-pln   │  B-eff    │  B-crdt,B-ops  │
Layer 0       │  B-trn   │  B-trn    │  B-codec,B-elc │
```

---

## Validation Errors

### Possible Typo Warning

```
WARNING: Tower 'devic-logic' has only 1 brick
  Brick: B-crdt-core
  Hint: Did you mean 'device-logic'? (3 bricks)

  To suppress: This is a warning, not an error. Ignore if intentional.
```

### Cross-Tower Violation

```
ERROR: Cross-tower dependency forbidden
  Brick: B-crdt-core (tower=device-logic)
  Depends on: B-planes-core (tower=server)
  Rule: Towers are completely independent. No cross-tower imports.
  Fix: Use INTENT specifications instead of direct code imports.
```

### Layer Violation (Within Tower)

```
ERROR: Layer dependency violation
  Brick: B-igp (layer=2, tower=device-logic)
  Depends on: B-replicator (layer=2, tower=device-logic)
  Rule: Layer 2 may only depend on layers 0-1
```

---

## Migration Path

### Phase 1: Add Tower Field

1. Add optional `tower` field to brick schema
2. Assign bricks to towers (or omit for single-tower projects)
3. Towers inferred from usage — no separate declaration needed

### Phase 2: Enforce Isolation

1. Validate no cross-tower dependencies
2. Fix violations by extracting shared code to INTENT specs
3. Add `jigy towers` command

### Phase 3: Multi-Language Support

1. Add language-prefixed unit format
2. Support Rust/Swift/Kotlin unit references
3. Validate cross-language tower consistency

---

## Schema Update

### bricks.yaml JSON Schema

```json
{
  "properties": {
    "tower": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9-]*$",
      "description": "The architectural tower this brick belongs to (optional, kebab-case)"
    }
  },
  "required": ["id", "layer", "units"]
}
```

**Note:** Tower is optional. If omitted, the project is treated as single-tower. Valid towers are inferred from usage across all bricks.

---

## Summary

| Concept | Definition |
|---------|------------|
| **Layer** | Horizontal stratification (dependency depth) |
| **Tower** | Vertical partition (complete isolation) |
| **Brick** | Cell in Layer × Tower matrix |
| **INTENT** | Not a tower — specifications that bridge towers |
| **Layer Rule** | Within tower: layer N depends only on layers < N |
| **Tower Rule** | Across towers: **FORBIDDEN** |

### The Simplification

A-002 defines a complex dependency matrix. We simplify to one rule:

> **Towers don't import from each other. Period.**

How do they interoperate? Through INTENT — shared specifications, contracts, and test vectors. This enables:
- True independence (each tower is a standalone codebase)
- Multi-language freedom (device-logic can be Rust without affecting server)
- Parallel development (teams work on towers independently)
- Clean testing (each tower tests against INTENT, not other towers)
