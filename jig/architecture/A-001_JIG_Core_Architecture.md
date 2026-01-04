---
id: A-001
type: architecture
title: JIG Core Architecture
status: active
supports_goals: [G-001, G-003, G-004, G-005]
constrains: [S-072, S-073, S-074, S-075, S-076, S-077, S-078, S-079, S-086, S-087, S-088]
---

# A-001: JIG Core Architecture

## Overview

This architecture document defines the G-A-O-S-C-T pyramid (the intent hierarchy) and the Layer×Tower partitioning model that governs JIG's structure.

JIG measures alignment between **intent** (specifications), **implementation** (code), and **verification** (tests). This architecture establishes the structural constraints that enable complete traceability from any code artifact back to the project's foundational goals.

---

## The Intent Hierarchy

JIG establishes a seven-level pyramid that connects human intent to machine execution:

```
                      CHARTER
                    (defines G-#)
                    /          \
                   /            \
          ARCHITECTURE         OUTCOMES
               A-###              O-###
           supports_goals     supports_goals
           constrains ──┐    ┌── specifies
                        │    │
                        ▼    ▼
                    SPECIFICATIONS
                         S-###
                       /      \
                      /        \
                 verifies   implements
                    /            \
                   /              \
               TESTS              CODE
                T-###              C-###
```

Six relationships define alignment:

| Relationship | Direction | Meaning |
|--------------|-----------|---------|
| Charter `defines_goals` | Parent → Child | Charter defines which goals exist |
| Architecture `supports_goals` | Child → Parent | Which goals this architecture supports |
| Architecture `constrains` | Parent → Child | Which specs this architecture constrains |
| Outcome `supports_goals` | Child → Parent | Which goals this outcome supports |
| Outcome `specifies` | Parent → Child | Which specs this outcome decomposes into |
| Code `implements` | Child → Parent | Which specs this code implements |
| Test `verifies` | Child → Parent | Which specs this test verifies |

---

## Artifact Types

The system consists of exactly **seven** core artifact types:

| # | Artifact | Format | Count | Authored By |
|---|----------|--------|-------|-------------|
| 1 | Charter | `.md` with YAML frontmatter | Single | Human |
| 2 | Architecture | `.md` with YAML frontmatter | Multiple | Human |
| 3 | Outcome | `.md` with YAML frontmatter | Multiple | Human |
| 4 | Specification | `.md` with YAML frontmatter | Multiple | Human |
| 5 | Brick definitions | `bricks.yaml` | Single | Human |
| 6 | @jig annotations | In source code | Multiple | Human |
| 7 | Graph files | `.ndjson` | Multiple | Machine |

### ID Format Contract

| Type | Format | Example | Notes |
|------|--------|---------|-------|
| Charter | `Charter` | `Charter` | Singleton |
| Goal | `G-{number}` | `G-001`, `G-005` | Defined in Charter body |
| Architecture | `A-{number}` | `A-001`, `A-007` | Zero-padded to 3 digits |
| Outcome | `O-{number}` | `O-001`, `O-045` | Zero-padded to 3 digits |
| Specification | `S-{number}` | `S-001`, `S-169` | Zero-padded to 3 digits |
| Brick | `B-{kebab-case}` | `B-crdt`, `B-cli` | Semantic kebab-case |
| Code | `C-{path}` | `C-jig.cli.main` | Fully-qualified path |
| Test | `T-{path}` | `T-test_cli.test_main` | Test path |

---

## Brick Partitioning

Bricks partition the codebase into architectural units. Every function belongs to exactly **one** brick (partition constraint).

### Brick Structure

```yaml
bricks:
  - id: B-cli
    name: CLI Commands
    layer: 1
    units:
      - M-jig.cli.main
      - M-jig.cli.show
```

### Field Contract

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | YES | Format: `B-{kebab-case}` |
| `name` | string | YES | Human-readable name |
| `layer` | integer | YES | Non-negative integer (0, 1, 2, ...) |
| `tower` | string | NO | Optional tower assignment (kebab-case) |
| `units` | array[string] | YES | Implementation graph node IDs |

---

## Layer and Tower Model

### Layers (Horizontal)

Layers stratify bricks by dependency depth:

- **Layer 0**: Foundation bricks; may depend on external libraries only
- **Layer N**: Bricks that depend only on layers 0..(N-1)

**The Layer Rule:** A brick at layer N may depend ONLY on bricks at layers < N. Upward dependencies are forbidden. Violations are errors.

### Towers (Vertical)

Towers partition the codebase into completely independent components:

```
              │  server  │  harness  │  device-logic  │  ← Towers
  ────────────┼──────────┼───────────┼────────────────┤
  Layer 2     │   B-s2   │   B-h2    │                │
  Layer 1     │   B-s1   │   B-h1    │     B-d1       │
  Layer 0     │   B-s0   │   B-h0    │     B-d0       │
              │          │           │                │
                               Layers ↓
```

**The Tower Rule:** Cross-tower dependencies are **FORBIDDEN**. Towers communicate through INTENT (shared specifications), not through code imports.

### Single-Tower Projects

Projects that don't need vertical partitioning (like JIG itself) simply omit the `tower` field from all bricks. Cross-tower validation is skipped, and all bricks belong to an implicit default tower.

### Tower Field Rules

1. **Optional** — omit for single-tower projects
2. **Kebab-case** — tower IDs use kebab-case format
3. **Inferred** — towers are inferred from usage, not declared separately
4. **Activating** — if any brick has a tower field, cross-tower validation is enabled

---

## Validation Rules

### Charter Validation

1. Charter `id` SHALL be exactly `"Charter"`
2. Charter `defines_goals` SHALL be non-empty
3. All goal IDs SHALL match `G-{number}` format
4. All goal IDs SHALL have corresponding headers in body

### Architecture Validation

5. Architecture `id` SHALL match pattern `A-{NNN}`
6. Architecture `supports_goals` SHALL be non-empty
7. Architecture `supports_goals` SHALL reference goals defined in Charter
8. Architecture `constrains` (if present) SHALL reference existing specs

### Outcome Validation

9. Outcome `id` SHALL match pattern `O-{NNN}`
10. Outcome `supports_goals` SHALL be non-empty
11. Outcome `supports_goals` SHALL reference goals defined in Charter
12. Outcome `specifies` SHALL reference existing specs

### Specification Validation

13. Specification `id` SHALL match pattern `S-{NNN}`
14. Specification `status` SHALL be one of: `draft`, `proposed`, `active`, `deprecated`

### Brick Validation

15. Brick `id` SHALL match pattern `B-[a-z0-9-]+`
16. Brick `layer` SHALL be non-negative integer
17. Brick `units` SHALL reference nodes in implementation graph
18. Every function SHALL belong to exactly one brick (partition)
19. Brick dependencies SHALL respect layer hierarchy (DAG)

### Tower Validation

20. Tower values (if present) SHALL match kebab-case pattern
21. Cross-tower dependencies SHALL be detected and reported as errors
22. Single-tower projects (no tower fields) skip tower validation

---

## File Structure

```
project-root/
├── jig/
│   ├── Charter.md                              # Root document (singleton)
│   ├── architecture/                           # Architecture documents
│   │   └── A-001_JIG_Core_Architecture.md
│   ├── outcomes/                               # Outcome documents
│   │   ├── O-001.md
│   │   └── ...
│   ├── specifications/                         # Specification documents
│   │   ├── S-001.md
│   │   └── ...
│   ├── bricks.yaml                             # Brick definitions
│   └── generated/                              # Machine-generated graphs
│       ├── intent-graph.ndjson
│       ├── implementation-graph.ndjson
│       └── verification-graph.ndjson
├── src/
│   └── [source code with @jig annotations]
└── test/
    └── [test code with @jig annotations]
```

---

## Compliance

All future work SHALL comply with this architecture. Deviations require explicit architectural decision superseding this document.

Tools, automation, and analysis SHALL treat this architecture as normative.

