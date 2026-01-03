# Proposal: Bricks with Slices

**Status:** Draft
**Author:** Claude + Jim
**Date:** 2025-12-29
**Related:** [contextBricks.md](contextBricks.md), [A-002: Four-Component Separation](../../jig/architecture/A-002.md)

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

## Solution: Introduce Slices

A **Slice** is a vertical partition of the codebase. Slices are **completely independent** — no code imports cross slice boundaries.

```
              │  server  │  harness  │  device-logic  │  ← Slices
  ────────────┼──────────┼───────────┼────────────────┤
  Layer 2     │   B-s2   │   B-h2    │                │
  Layer 1     │   B-s1   │   B-h1    │     B-d1       │
  Layer 0     │   B-s0   │   B-h0    │     B-d0       │
              │          │           │                │
                               Layers ↓
```

- **Layers** = horizontal rows (dependency depth within a slice)
- **Slices** = vertical columns (complete isolation)
- **Bricks** = cells in the Layer × Slice matrix

### Key Principle: Slices Are Independent

**No cross-slice code dependencies.** Ever.

How do slices communicate? Through **INTENT** — the shared specifications, contracts, and test vectors that all slices implement against. INTENT is not code; it's the shared understanding that enables independent implementation.

```
         ┌─────────────────────────────────────────────┐
         │                   INTENT                     │
         │  (Charter, Specs, Contracts, Test Vectors)   │
         │              NOT CODE — NO SLICE             │
         └──────────┬──────────┬──────────┬────────────┘
                    │          │          │
           implements      implements    implements
                    │          │          │
                    ▼          ▼          ▼
              ┌─────────┐ ┌─────────┐ ┌───────────────┐
              │ server  │ │ harness │ │ device-logic  │
              │ (slice) │ │ (slice) │ │   (slice)     │
              └─────────┘ └─────────┘ └───────────────┘
                    │          │          │
                  ISOLATED   ISOLATED   ISOLATED
```

---

## Slice Definitions

Three slices partition the executable codebase:

| Slice ID | A-002 Component | Contains | Language |
|----------|-----------------|----------|----------|
| `server` | #2 SERVER | Planes, Enforcer, Monitors, Routing | Python forever |
| `harness` | #3 HARNESS | Transport, Timers, GUI, Effect Executor | Python forever |
| `device-logic` | #4 DEVICE LOGIC | CRDT, Protocol, Operations, IGP | Python → Rust/Swift/Kotlin |

### What About INTENT?

INTENT (#1 from A-002) is **not a slice**. Slices partition executable code. INTENT contains:
- Markdown documents (Charter, Architecture)
- YAML/JSON specifications
- Test vectors

INTENT is managed separately — it's the **bridge** that enables slice independence.

### Slice ID Format

Slice IDs use **kebab-case** for language-agnostic compatibility:

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

### Proposed Format

```yaml
bricks:
  - id: B-crdt-core
    name: CRDT Core Primitives
    layer: 1
    slice: device-logic              # NEW: required field
    units:
      - M-ase.device_logic.crdt.core
```

### Slice Field Rules

1. **Required** — every brick must declare its slice
2. **Enum** — must be one of: `server`, `harness`, `device-logic`
3. **Immutable** — the three slices are architectural constants, not extensible

---

## Dependency Rules

### The Core Rule

**Layer rules apply within a slice. Cross-slice dependencies are forbidden.**

```
WITHIN slice:    Layer N may depend on layers 0..(N-1)
ACROSS slices:   FORBIDDEN — no exceptions
```

### Validation Logic

```
is_valid_dependency(from_brick, to_brick):
    if from_brick.slice != to_brick.slice:
        return FALSE  # Cross-slice = always invalid

    if from_brick.layer <= to_brick.layer:
        return FALSE  # Must depend on lower layer

    return TRUE
```

### Why No Exceptions?

A-002 shows a dependency matrix with some allowed cross-slice imports. We simplify:

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
jigy validate        # Now validates slice isolation
jigy layers          # Show layer structure (within each slice)
```

### New Commands

```bash
jigy slices                    # List all slices with brick counts
jigy slices <slice_id>         # Show all bricks in a slice
jigy matrix                    # Show 2D Layer × Slice grid
```

### Example Output: `jigy slices`

```
Slices (3):

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

### Cross-Slice Violation

```
ERROR: Cross-slice dependency forbidden
  Brick: B-crdt-core (slice=device-logic)
  Depends on: B-planes-core (slice=server)
  Rule: Slices are completely independent. No cross-slice imports.
  Fix: Use INTENT specifications instead of direct code imports.
```

### Layer Violation (Within Slice)

```
ERROR: Layer dependency violation
  Brick: B-igp (layer=2, slice=device-logic)
  Depends on: B-replicator (layer=2, slice=device-logic)
  Rule: Layer 2 may only depend on layers 0-1
```

---

## Migration Path

### Phase 1: Add Slice Field

1. Add required `slice` field to brick schema
2. Assign all existing bricks to appropriate slice
3. Validate slice values are in enum

### Phase 2: Enforce Isolation

1. Validate no cross-slice dependencies
2. Fix violations by extracting shared code to INTENT specs
3. Add `jigy slices` command

### Phase 3: Multi-Language Support

1. Add language-prefixed unit format
2. Support Rust/Swift/Kotlin unit references
3. Validate cross-language slice consistency

---

## Schema Update

### bricks.yaml JSON Schema

```json
{
  "properties": {
    "slice": {
      "type": "string",
      "enum": ["server", "harness", "device-logic"],
      "description": "The architectural slice this brick belongs to"
    }
  },
  "required": ["id", "layer", "slice", "units"]
}
```

---

## Summary

| Concept | Definition |
|---------|------------|
| **Layer** | Horizontal stratification (dependency depth) |
| **Slice** | Vertical partition (complete isolation) |
| **Brick** | Cell in Layer × Slice matrix |
| **INTENT** | Not a slice — specifications that bridge slices |
| **Layer Rule** | Within slice: layer N depends only on layers < N |
| **Slice Rule** | Across slices: **FORBIDDEN** |

### The Simplification

A-002 defines a complex dependency matrix. We simplify to one rule:

> **Slices don't import from each other. Period.**

How do they interoperate? Through INTENT — shared specifications, contracts, and test vectors. This enables:
- True independence (each slice is a standalone codebase)
- Multi-language freedom (device-logic can be Rust without affecting server)
- Parallel development (teams work on slices independently)
- Clean testing (each slice tests against INTENT, not other slices)
