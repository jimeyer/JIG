# JIGPLAN: Extended Intent Hierarchy and Slices

**SCOPE:** docs/wip/C003_SCOPE_Extended-Intent-Hierarchy-and-Slices.md
**Date:** 2025-12-29
**Status:** Draft
**Author:** Claude + Jim

---

## Summary

This JIGPLAN defines the architectural evolution of JIG from a 4-level hierarchy (Outcome → Specification → Code/Tests) to a 7-level hierarchy (Charter → Goals → Architecture/Outcomes → Specifications → Code/Tests) with vertical partitioning (Slices).

**Key changes:**
- **1 new root document**: Charter.md (replaces Constitution.md)
- **1 new architecture document**: A-001.md (merges C001 Core Artifacts Contract + C002 Slices)
- **18 outcome updates**: Add `supports_goals` to all existing outcomes
- **11 brick updates**: Add `slice: jig` to all bricks
- **20 new specifications**: S-072 through S-091
- **4 new outcomes**: O-023 through O-026

**Validation strategy:** Mandatory immediately (breaking change)

---

## Proposed Charter Goals

Derived from Constitution.md's four stated purposes:

| Goal ID | Title | Description |
|---------|-------|-------------|
| G-1 | Grounding in Reality | AI agents query verified truth from implementation/intent graphs, not hallucinate |
| G-2 | Continuity Across Sessions | Persistent, machine-readable context survives session boundaries |
| G-3 | Enforcing Constraints | Architectural boundaries validated automatically before code commits |
| G-4 | Intent Alignment | WHY (specs, outcomes) is explicit and required before modifying HOW (code) |
| G-5 | Full Traceability | Every function traces to specs, specs to outcomes, outcomes to goals, goals to Charter |

**Note:** Goals are defined in Charter markdown body with `### G-{number}:` headers. The `defines_goals` frontmatter array lists them.

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| UPDATE | O-001 | Implementation structure is discoverable | Add supports_goals: [G-1, G-2] |
| UPDATE | O-002 | Code-to-specification traceability | Add supports_goals: [G-4, G-1] |
| UPDATE | O-003 | Multi-language support | Add supports_goals: [G-1] |
| UPDATE | O-004 | Early error detection | Add supports_goals: [G-3] |
| UPDATE | O-005 | Clear actionable error messages | Add supports_goals: [G-2, G-3] |
| UPDATE | O-006 | Fast project validation | Add supports_goals: [G-3] |
| UPDATE | O-009 | Intent graph generation | Add supports_goals: [G-4, G-2] |
| UPDATE | O-012 | Brick A001 compliance | Add supports_goals: [G-3] |
| UPDATE | O-013 | Layer architecture enforcement | Add supports_goals: [G-3] |
| UPDATE | O-014 | Layer visibility | Add supports_goals: [G-4, G-2] |
| UPDATE | O-015 | Completeness validation | Add supports_goals: [G-4, G-3] |
| UPDATE | O-016 | CI/Tooling integration | Add supports_goals: [G-3] |
| UPDATE | O-017 | Artifact change detection | Add supports_goals: [G-2, G-1] |
| UPDATE | O-018 | Test-to-spec traceability | Add supports_goals: [G-1, G-4] |
| UPDATE | O-019 | Intuitive CLI | Add supports_goals: [G-2] |
| UPDATE | O-020 | Configurable project structure | Add supports_goals: [G-1] |
| UPDATE | O-021 | Verifiable test coverage | Add supports_goals: [G-1, G-4] |
| UPDATE | O-022 | Commands operate on current data | Add supports_goals: [G-2, G-1] |
| CREATE | O-023 | Charter establishes project goals | supports_goals: [G-5, G-4] |
| CREATE | O-024 | Architecture constrains specifications | supports_goals: [G-3, G-5] |
| CREATE | O-025 | Intent graph captures full hierarchy | supports_goals: [G-5, G-2] |
| CREATE | O-026 | Slices enforce component isolation | supports_goals: [G-3] |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | S-001 through S-071 | [existing specs] | No changes to existing specs |
| CREATE | S-072 | Charter file structure | Charter MUST be single file at jig/Charter.md |
| CREATE | S-073 | Charter defines_goals field | Charter MUST have defines_goals array in frontmatter |
| CREATE | S-074 | Goal header format | Goals MUST have `### G-{number}:` headers in Charter body |
| CREATE | S-075 | Goal ID format | Goal IDs MUST match `G-{number}` pattern (not zero-padded) |
| CREATE | S-076 | Architecture file location | Architecture files MUST be in jig/architecture/A-*.md |
| CREATE | S-077 | Architecture ID format | Architecture IDs MUST match `A-{NNN}` (zero-padded to 3 digits) |
| CREATE | S-078 | Architecture supports_goals required | Architecture MUST have non-empty supports_goals array |
| CREATE | S-079 | Architecture constrains references | constrains field MUST reference existing spec IDs |
| CREATE | S-080 | Charter node in intent graph | Intent graph MUST include Charter node with defines_goals |
| CREATE | S-081 | Goal nodes in intent graph | Intent graph MUST include Goal nodes extracted from Charter |
| CREATE | S-082 | Architecture nodes in intent graph | Intent graph MUST include Architecture nodes |
| CREATE | S-083 | defines_goal edges | Intent graph MUST include Charter→Goal edges |
| CREATE | S-084 | supports_goal edges | Intent graph MUST include A→Goal and O→Goal edges |
| CREATE | S-085 | constrains edges | Intent graph MUST include A→S edges for constrains relationships |
| CREATE | S-086 | Brick slice field required | Bricks MUST have slice field in bricks.yaml |
| CREATE | S-087 | Slice value validation | slice MUST be a valid slice ID defined for the project |
| CREATE | S-088 | Cross-slice isolation | Cross-slice dependencies are forbidden |
| CREATE | S-089 | Slice isolation validation | jigy validate MUST check for cross-slice dependencies |
| CREATE | S-090 | jigy slices command | CLI MUST provide command to list slices and their bricks |
| CREATE | S-091 | jigy matrix command | CLI MUST provide layer×slice matrix visualization |

---

## O/S Node Details

### Nodes to UPDATE

#### All Existing Outcomes (O-001 through O-022)

**Current format:**
```yaml
---
id: O-001
type: outcome
title: Implementation structure is discoverable from source code
specifies: [S-001, S-003, S-005, S-006]
---
```

**Updated format:**
```yaml
---
id: O-001
type: outcome
title: Implementation structure is discoverable from source code
supports_goals: [G-1, G-2]
specifies: [S-001, S-003, S-005, S-006]
---
```

**Goal Assignments:**

| Outcome | supports_goals | Rationale |
|---------|----------------|-----------|
| O-001 | [G-1, G-2] | Grounding + Continuity |
| O-002 | [G-4, G-1] | Intent Alignment + Grounding |
| O-003 | [G-1] | Grounding (polyglot) |
| O-004 | [G-3] | Enforcing Constraints |
| O-005 | [G-2, G-3] | Continuity + Constraints |
| O-006 | [G-3] | Enforcing Constraints |
| O-009 | [G-4, G-2] | Intent Alignment + Continuity |
| O-012 | [G-3] | Enforcing Constraints |
| O-013 | [G-3] | Enforcing Constraints |
| O-014 | [G-4, G-2] | Intent Alignment + Continuity |
| O-015 | [G-4, G-3] | Intent Alignment + Constraints |
| O-016 | [G-3] | Enforcing Constraints |
| O-017 | [G-2, G-1] | Continuity + Grounding |
| O-018 | [G-1, G-4] | Grounding + Intent Alignment |
| O-019 | [G-2] | Continuity |
| O-020 | [G-1] | Grounding |
| O-021 | [G-1, G-4] | Grounding + Intent Alignment |
| O-022 | [G-2, G-1] | Continuity + Grounding |

---

### Nodes to CREATE

#### Charter.md (ROOT DOCUMENT)

**File:** `jig/Charter.md`

**Action:** Create from Constitution.md content with new frontmatter format.

**Frontmatter:**
```yaml
---
id: Charter
type: charter
defines_goals: [G-1, G-2, G-3, G-4, G-5]
---
```

**Body structure:**
```markdown
# JIG Charter

## Purpose
[Adapted from Constitution.md Purpose section]

## Charter Goals

### G-1: Grounding in Reality
AI agents query verified truth from implementation and intent graphs, not hallucinate.
JIG grounds agent work in verifiable facts by automatically extracting actual code structure,
explicit specifications, and test relationships.

### G-2: Continuity Across Sessions
Persistent, machine-readable context survives session boundaries. The next agent (or the
same agent tomorrow) can read intent graphs, implementation graphs, and traceability links
that capture what exists and why.

### G-3: Enforcing Constraints
Architectural boundaries are validated automatically before code commits. Agents cannot
introduce circular dependencies, violate layering rules, or create coupling that violates
defined constraints.

### G-4: Intent Alignment
WHY (specifications, outcomes) is explicit and required before modifying HOW (code).
Agents must read specifications before implementing, outcomes before creating specifications.

### G-5: Full Traceability
Every function traces to specifications, specifications to outcomes, outcomes to goals,
goals to Charter. Breaks in this chain indicate misalignment between intent and reality.

## [Rest of content adapted from Constitution.md]
```

**Migration:** Constitution.md content is restructured, not deleted. Original archived to `jig/old/Constitution_v1.md`.

---

#### A-001.md (ARCHITECTURE DOCUMENT)

**File:** `jig/architecture/A-001.md`

**Purpose:** Merge C001 (Core Artifacts Contract) and C002 (Bricks with Slices) into single authoritative architecture document.

**Frontmatter:**
```yaml
---
id: A-001
type: architecture
title: JIG Core Architecture
status: active
supports_goals: [G-1, G-3, G-4, G-5]
constrains: [S-072, S-073, S-074, S-075, S-076, S-077, S-078, S-079, S-086, S-087, S-088]
---
```

**Body structure:**
```markdown
# A-001: JIG Core Architecture

## Overview
Defines the G-A-O-S-C-T pyramid and the Layer×Slice partitioning model.

## The Intent Hierarchy
[Content from C001 sections 1-4]

## Artifact Types
[Content from C001 sections on Charter, Architecture, Outcome, Specification]

## Brick Partitioning
[Content from C001 section 5 + C002 slice concept]

## Layer and Slice Model
[Content from C002 - layers are horizontal, slices are vertical]

## Validation Rules
[Content from C001 Validation Contract + C002 slice validation]
```

---

#### New Outcomes (O-023 through O-026)

**O-023: Charter establishes project goals**

```yaml
---
id: O-023
type: outcome
title: Charter establishes project goals
supports_goals: [G-5, G-4]
specifies: [S-072, S-073, S-074, S-075]
---

# Charter establishes project goals

A single Charter document defines all project goals, creating the root of the
intent hierarchy. All downstream artifacts (Architecture, Outcomes) reference
these goals, enabling complete top-down traceability.

## Value
- Goals provide context for WHY specifications exist
- Enables "which goals does this code support?" queries
- Single source of truth for project direction
```

**O-024: Architecture constrains specifications**

```yaml
---
id: O-024
type: outcome
title: Architecture constrains specifications
supports_goals: [G-3, G-5]
specifies: [S-076, S-077, S-078, S-079]
---

# Architecture constrains specifications

Architecture documents define structural boundaries that constrain how
specifications may be implemented. This enables separation of concerns
between "what we intend" (Outcomes/Specs) and "how we structure" (Architecture).

## Value
- Architectural decisions are explicit and traceable
- Specs can be constrained by multiple architectures
- Architecture changes trigger spec review
```

**O-025: Intent graph captures full hierarchy**

```yaml
---
id: O-025
type: outcome
title: Intent graph captures full hierarchy
supports_goals: [G-5, G-2]
specifies: [S-080, S-081, S-082, S-083, S-084, S-085]
---

# Intent graph captures full hierarchy

The intent graph includes Charter, Goal, and Architecture nodes in addition
to Outcomes, Specifications, and Bricks. All six relationship types are
represented as edges.

## Value
- Complete traceability from functions to Charter
- Queries like "which code supports G-3?" become possible
- Architecture constraints visible in graph structure
```

**O-026: Slices enforce component isolation**

```yaml
---
id: O-026
type: outcome
title: Slices enforce component isolation
supports_goals: [G-3]
specifies: [S-086, S-087, S-088, S-089, S-090, S-091]
---

# Slices enforce component isolation

Bricks are assigned to slices (vertical partitions). Cross-slice dependencies
are forbidden, enforcing complete isolation between components.

## Value
- Components can be developed/deployed independently
- Multi-language freedom (slice can be rewritten in different language)
- Clean testing (each slice tests against INTENT, not other slices)

## Note on JIG's Single Slice

JIG currently uses a single slice (`jig`) since it is a cohesive tooling system.
This demonstrates that the slice model supports single-component projects.
Future JIG extensions (e.g., visualization tools) could introduce additional slices.
```

---

#### New Specifications (S-072 through S-091)

Specs will be created as individual files in `jig/specifications/`. Summary:

**Charter specs (S-072 through S-075):**
- S-072: Charter file at jig/Charter.md
- S-073: Charter defines_goals frontmatter array
- S-074: Goal headers match `### G-{number}:` format
- S-075: Goal IDs match `G-{number}` pattern

**Architecture specs (S-076 through S-079):**
- S-076: Architecture files in jig/architecture/A-*.md
- S-077: Architecture ID format A-{NNN}
- S-078: Architecture requires non-empty supports_goals
- S-079: Architecture constrains references valid specs

**Intent graph specs (S-080 through S-085):**
- S-080: Charter node in intent graph
- S-081: Goal nodes extracted from Charter
- S-082: Architecture nodes in intent graph
- S-083: Charter→Goal edges (defines_goal)
- S-084: A→Goal and O→Goal edges (supports_goal)
- S-085: A→S edges (constrains)

**Slice specs (S-086 through S-091):**
- S-086: Brick slice field required
- S-087: Slice value must be valid
- S-088: Cross-slice dependencies forbidden
- S-089: jigy validate checks slice isolation
- S-090: jigy slices command
- S-091: jigy matrix command

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| MODIFY | B-decorators | 0 | Add slice: jig |
| MODIFY | B-cli | 1 | Add slice: jig; add new commands (slices, matrix) |
| MODIFY | B-validation | 0 | Add slice: jig; add charter/arch/slice validation |
| MODIFY | B-impl-graph | 0 | Add slice: jig |
| MODIFY | B-intent-graph | 0 | Add slice: jig; add Charter/Goal/Architecture nodes |
| MODIFY | B-config | 0 | Add slice: jig; add charter/architecture paths |
| MODIFY | B-hashing | 0 | Add slice: jig |
| MODIFY | B-languages | 0 | Add slice: jig |
| MODIFY | B-verification-graph | 1 | Add slice: jig |
| MODIFY | B-audit | 1 | Add slice: jig |
| MODIFY | B-staleness | 0 | Add slice: jig |
| FORBIDDEN | (none) | - | All bricks need modification for slice field |

---

### Brick Details

#### All Bricks: Add Slice Field

**Current format:**
```yaml
- id: B-decorators
  name: JIG Core Decorators
  layer: 0
  units:
    - M-jig.__init__
```

**Updated format:**
```yaml
- id: B-decorators
  name: JIG Core Decorators
  layer: 0
  slice: jig
  units:
    - M-jig.__init__
```

**Slice rationale:** JIG is a single cohesive tool. All bricks belong to the `jig` slice. This demonstrates that the slice model works for single-component projects while establishing the infrastructure for future multi-slice evolution (e.g., a separate visualization tool).

#### B-validation Modifications

**New functionality:**
- `validate_charter_file()` - Charter validation
- `validate_architecture_files()` - Architecture validation
- `validate_goal_references()` - Goal reference validation
- `validate_slice_isolation()` - Cross-slice dependency checking

**New dependencies:** None (layer 0)

#### B-intent-graph Modifications

**New functionality:**
- `_load_charter_node()` - Load Charter node
- `_load_goal_nodes()` - Extract Goal nodes from Charter
- `_load_architecture_nodes()` - Load Architecture nodes
- Charter→Goal, A→Goal, O→Goal, A→S edges

**New dependencies:** None (layer 0)

#### B-config Modifications

**New fields:**
- `charter` path (default: `Charter.md`)
- `architecture` path (default: `architecture`)

**New constant:**
- `VALID_SLICES` (project-specific, JIG uses `{"jig"}`)

#### B-cli Modifications

**New commands:**
- `jigy show charter` - Display Charter and goals
- `jigy show goals` - List goals with supporting artifacts
- `jigy show architecture` - List architecture documents
- `jigy slices` - List slices with brick counts
- `jigy matrix` - Display layer×slice grid

---

## Layer/Dependency Analysis

### Current Layer Structure

```
Layer 0: FOUNDATION (8 bricks)
  B-decorators
  B-validation
  B-impl-graph
  B-intent-graph
  B-config
  B-hashing
  B-languages
  B-staleness

Layer 1: SERVICES (3 bricks)
  B-cli
    └─► depends on: B-validation, B-impl-graph, B-intent-graph, B-config
  B-verification-graph
    └─► depends on: B-impl-graph
  B-audit
    └─► depends on: B-validation
```

### After Modifications

No layer changes. All modifications are additive to existing bricks.

### Slice Structure (New)

```
Slice: jig (11 bricks)
  Layer 0: B-decorators, B-validation, B-impl-graph, B-intent-graph,
           B-config, B-hashing, B-languages, B-staleness
  Layer 1: B-cli, B-verification-graph, B-audit
```

**Note:** Since JIG has only one slice, cross-slice validation will always pass. The infrastructure exists for future multi-slice projects or JIG extensions.

---

## @jig Decorator Changes

### Decorators to ADD

New validation functions:

| Type | Location | Spec |
|------|----------|------|
| implements | F-jig.validation.intent.validate_charter_file | S-072, S-073, S-074, S-075 |
| implements | F-jig.validation.intent.validate_architecture_files | S-076, S-077, S-078, S-079 |
| implements | F-jig.validation.intent.validate_goal_references | S-075 |
| implements | F-jig.validation.bricks.validate_slice_field | S-086, S-087 |
| implements | F-jig.validation.bricks.validate_slice_isolation | S-088, S-089 |

New intent graph functions:

| Type | Location | Spec |
|------|----------|------|
| implements | F-jig.intent_graph.generator._load_charter_node | S-080 |
| implements | F-jig.intent_graph.generator._load_goal_nodes | S-081 |
| implements | F-jig.intent_graph.generator._load_architecture_nodes | S-082 |
| implements | F-jig.intent_graph.generator._create_defines_goal_edges | S-083 |
| implements | F-jig.intent_graph.generator._create_supports_goal_edges | S-084 |
| implements | F-jig.intent_graph.generator._create_constrains_edges | S-085 |

New CLI commands:

| Type | Location | Spec |
|------|----------|------|
| implements | F-jig.cli.show.show_charter | S-072 |
| implements | F-jig.cli.show.show_goals | S-075 |
| implements | F-jig.cli.show.show_architecture | S-076 |
| implements | F-jig.cli.slices.slices_command | S-090 |
| implements | F-jig.cli.slices.matrix_command | S-091 |

### Decorators to REMOVE

None - no specs are being deleted.

### Decorators to MODIFY

None - existing spec IDs unchanged.

---

## Clean Break Actions

This work follows clean break protocol:

- [x] Old code paths will be DELETED, not feature-flagged
- [x] Old tests will be DELETED and new tests written from scratch
- [x] No backwards compatibility shims
- [x] Validation mandatory immediately (not opt-in)
- [x] Graph version bumps to 2.0 (not backward compatible)

### Files to Archive

| Current | Archive To | Reason |
|---------|------------|--------|
| jig/Constitution.md | jig/old/Constitution_v1.md | Replaced by Charter.md |
| jig/Constitution_v2.md | jig/old/Constitution_v2_draft.md | Draft superceded by Charter.md |

### New Directory Structure

```
jig/
├── Charter.md                    # NEW: Root document
├── architecture/                 # NEW: Directory
│   └── A-001.md                  # NEW: Core Architecture
├── outcomes/
│   └── O-001.md ... O-026.md     # UPDATED + NEW
├── specifications/
│   └── S-001.md ... S-091.md     # EXISTING + NEW
├── bricks.yaml                   # UPDATED: slice field
├── generated/                    # Intent graph version 2.0
│   ├── intent-graph.ndjson       # Charter, Goal, Architecture nodes
│   └── ...
└── old/                          # NEW: Archive
    ├── Constitution_v1.md
    └── Constitution_v2_draft.md
```

---

## Validation Sequence

After all changes, validation must pass:

```bash
# 1. Rebuild graphs with new schema
jigy rebuild

# 2. Validate all artifacts
jigy validate

# Expected output:
# ✓ Charter: 1 file, 5 goals defined
# ✓ Architecture: 1 file, valid supports_goals, valid constrains
# ✓ Outcomes: 22 files, all have supports_goals
# ✓ Specifications: 91 files, all valid
# ✓ Bricks: 11 bricks, all have slice field
# ✓ Slices: 1 slice (jig), no cross-slice violations
# ✓ Layer structure: valid (no upward dependencies)

# 3. Verify layer structure unchanged
jigy layers

# 4. Verify intent graph version 2.0
head -1 jig/generated/intent-graph.ndjson
# {"_meta":{"version":"2.0",...}}
```

---

## Risk Mitigation

### Breaking Change: Immediate Mandatory Validation

**Risk:** Existing projects using JIG will fail validation immediately.

**Mitigation:**
- JIG is the only project currently using JIG
- All changes are self-contained to this repository
- CI will verify full compliance before merge

### Graph Consumer Compatibility

**Risk:** Intent graph version 2.0 may break downstream consumers.

**Mitigation:**
- JIG is the only consumer of its own graphs
- No external API compatibility requirement
- Version field allows future consumers to detect schema

### Constitution → Charter Content Loss

**Risk:** Restructuring Constitution.md may lose important content.

**Mitigation:**
- Original archived to jig/old/Constitution_v1.md
- All outcome descriptions preserved
- Agent instructions section retained in Charter

---

## Approval Checklist

Before human approval:

- [x] All existing specs reviewed - 71 specs, no changes needed
- [x] All existing outcomes reviewed - 18 outcomes need supports_goals
- [x] Charter goals derived from Constitution's 4 purposes + traceability
- [x] Architecture document merges C001 + C002 proposals
- [x] Brick slice field planned (single slice: jig)
- [x] New specs follow evergreen guidelines
- [x] Layer constraints validated (no changes)
- [x] @jig decorator plan complete
- [x] Clean break actions specified
- [x] Validation mandatory immediately (confirmed)

---

## Questions for Approval

1. **Charter Goals**: Do G-1 through G-5 accurately capture JIG's purpose?
   - G-1: Grounding in Reality
   - G-2: Continuity Across Sessions
   - G-3: Enforcing Constraints
   - G-4: Intent Alignment
   - G-5: Full Traceability

2. **Slice Name**: Is `jig` the right slice name, or prefer `jig-tooling`?

3. **Archive Strategy**: Archive Constitution.md to `jig/old/` or delete entirely?

4. **Spec Count**: 20 new specs (S-072 to S-091) - is this granularity appropriate?

---

**Awaiting human approval before proceeding to implementation PLAN.**
