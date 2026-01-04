# JIGPLAN: Extended Intent Hierarchy and Towers

**SCOPE:** docs/wip/C003_SCOPE_Extended-Intent-Hierarchy-and-Towers.md
**Date:** 2025-12-29
**Updated:** 2026-01-04
**Status:** Ready for Approval
**Author:** Claude + Jim

---

## Summary

This JIGPLAN defines the architectural evolution of JIG from a 4-level hierarchy (Outcome → Specification → Code/Tests) to a 7-level hierarchy (Charter → Goals → Architecture/Outcomes → Specifications → Code/Tests) with vertical partitioning (Towers).

**Current state:**
- 18 outcomes exist (O-001 through O-022, with gaps at O-007, O-008, O-010, O-011)
- 54 specs exist (S-001 through S-071, with gaps)
- 11 bricks across 2 layers
- Constitution.md exists (will become Charter.md)
- No architecture/ directory yet

**Key changes:**
- **1 new root document**: Charter.md (replaces Constitution.md)
- **1 new architecture document**: A-001_JIG_Core_Architecture.md (merges C001 Core Artifacts Contract + C002 Towers)
- **18 outcome updates**: Add `supports_goals` to all existing outcomes
- **4 brick modifications**: B-cli, B-validation, B-intent-graph, B-config (7 bricks unaffected)
- **20 new specifications**: S-072 through S-091
- **4 new outcomes**: O-023 through O-026

**Validation strategy:** Mandatory immediately (breaking change)

---

## Proposed Charter Goals

Derived from Constitution.md's four stated purposes:

| Goal ID | Title | Description |
|---------|-------|-------------|
| G-001 | Grounding in Reality | AI agents query verified truth from implementation/intent graphs, not hallucinate |
| G-002 | Continuity Across Sessions | Persistent, machine-readable context survives session boundaries |
| G-003 | Enforcing Constraints | Architectural boundaries validated automatically before code commits |
| G-004 | Intent Alignment | WHY (specs, outcomes) is explicit and required before modifying HOW (code) |
| G-005 | Full Traceability | Every function traces to specs, specs to outcomes, outcomes to goals, goals to Charter |

**Note:** Goals are defined in Charter markdown body with `### G-{number}:` headers. The `defines_goals` frontmatter array lists them.

---

## O/S Node Reconciliation

### Outcomes

**Note:** 18 outcomes exist (O-001 through O-022). IDs O-007, O-008, O-010, O-011 were never created.

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| UPDATE | O-001 | Implementation structure is discoverable | Add supports_goals: [G-001, G-002] |
| UPDATE | O-002 | Code-to-specification traceability | Add supports_goals: [G-004, G-001] |
| UPDATE | O-003 | Multi-language support | Add supports_goals: [G-001] |
| UPDATE | O-004 | Early error detection | Add supports_goals: [G-003] |
| UPDATE | O-005 | Clear actionable error messages | Add supports_goals: [G-002, G-003] |
| UPDATE | O-006 | Fast project validation | Add supports_goals: [G-003] |
| UPDATE | O-009 | Intent graph generation | Add supports_goals: [G-004, G-002] |
| UPDATE | O-012 | Brick A001 compliance | Add supports_goals: [G-003] |
| UPDATE | O-013 | Layer architecture enforcement | Add supports_goals: [G-003] |
| UPDATE | O-014 | Layer visibility | Add supports_goals: [G-004, G-002] |
| UPDATE | O-015 | Completeness validation | Add supports_goals: [G-004, G-003] |
| UPDATE | O-016 | CI/Tooling integration | Add supports_goals: [G-003] |
| UPDATE | O-017 | Artifact change detection | Add supports_goals: [G-002, G-001] |
| UPDATE | O-018 | Test-to-spec traceability | Add supports_goals: [G-001, G-004] |
| UPDATE | O-019 | Intuitive CLI | Add supports_goals: [G-002] |
| UPDATE | O-020 | Configurable project structure | Add supports_goals: [G-001] |
| UPDATE | O-021 | Verifiable test coverage | Add supports_goals: [G-001, G-004] |
| UPDATE | O-022 | Commands operate on current data | Add supports_goals: [G-002, G-001] |
| CREATE | O-023 | Charter establishes project goals | supports_goals: [G-005, G-004] |
| CREATE | O-024 | Architecture constrains specifications | supports_goals: [G-003, G-005] |
| CREATE | O-025 | Intent graph captures full hierarchy | supports_goals: [G-005, G-002] |
| CREATE | O-026 | Towers enforce component isolation | supports_goals: [G-003] |

### Specifications

**Note:** 54 specs exist (S-001 through S-071). Gaps at S-007–S-017 and S-029–S-034.

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | S-001 to S-071 (54 files) | [existing specs] | No changes to existing specs |
| CREATE | S-072 | Charter file structure | Charter MUST be single file at jig/Charter.md |
| CREATE | S-073 | Charter defines_goals field | Charter MUST have defines_goals array in frontmatter |
| CREATE | S-074 | Goal header format | Goals MUST have `### G-{number}:` headers in Charter body |
| CREATE | S-075 | Goal ID format | Goal IDs MUST match `G-{number}` pattern (not zero-padded) |
| CREATE | S-076 | Architecture file location | Architecture files MUST be in jig/architecture/A-{NNN}_{Title}.md |
| CREATE | S-077 | Architecture ID format | Architecture IDs MUST match `A-{NNN}` (zero-padded to 3 digits) |
| CREATE | S-078 | Architecture supports_goals required | Architecture MUST have non-empty supports_goals array |
| CREATE | S-079 | Architecture constrains references | constrains field MUST reference existing spec IDs |
| CREATE | S-080 | Charter node in intent graph | Intent graph MUST include Charter node with defines_goals |
| CREATE | S-081 | Goal nodes in intent graph | Intent graph MUST include Goal nodes extracted from Charter |
| CREATE | S-082 | Architecture nodes in intent graph | Intent graph MUST include Architecture nodes |
| CREATE | S-083 | defines_goal edges | Intent graph MUST include Charter→Goal edges |
| CREATE | S-084 | supports_goal edges | Intent graph MUST include A→Goal and O→Goal edges |
| CREATE | S-085 | constrains edges | Intent graph MUST include A→S edges for constrains relationships |
| CREATE | S-086 | Brick tower field optional | Bricks MAY have optional tower field in bricks.yaml |
| CREATE | S-087 | Tower value format | tower MUST be kebab-case if present |
| CREATE | S-088 | Cross-tower isolation | Cross-tower dependencies are forbidden |
| CREATE | S-089 | Tower isolation validation | jigy validate MUST check for cross-tower dependencies |
| CREATE | S-090 | jigy towers command | CLI MUST provide command to list towers and their bricks |
| CREATE | S-091 | jigy matrix command | CLI MUST provide layer×tower matrix visualization |

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
supports_goals: [G-001, G-002]
specifies: [S-001, S-003, S-005, S-006]
---
```

**Goal Assignments:**

| Outcome | supports_goals | Rationale |
|---------|----------------|-----------|
| O-001 | [G-001, G-002] | Grounding + Continuity |
| O-002 | [G-004, G-001] | Intent Alignment + Grounding |
| O-003 | [G-001] | Grounding (polyglot) |
| O-004 | [G-003] | Enforcing Constraints |
| O-005 | [G-002, G-003] | Continuity + Constraints |
| O-006 | [G-003] | Enforcing Constraints |
| O-009 | [G-004, G-002] | Intent Alignment + Continuity |
| O-012 | [G-003] | Enforcing Constraints |
| O-013 | [G-003] | Enforcing Constraints |
| O-014 | [G-004, G-002] | Intent Alignment + Continuity |
| O-015 | [G-004, G-003] | Intent Alignment + Constraints |
| O-016 | [G-003] | Enforcing Constraints |
| O-017 | [G-002, G-001] | Continuity + Grounding |
| O-018 | [G-001, G-004] | Grounding + Intent Alignment |
| O-019 | [G-002] | Continuity |
| O-020 | [G-001] | Grounding |
| O-021 | [G-001, G-004] | Grounding + Intent Alignment |
| O-022 | [G-002, G-001] | Continuity + Grounding |

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
defines_goals: [G-001, G-002, G-003, G-004, G-005]
---
```

**Body structure:**
```markdown
# JIG Charter

## Purpose
[Adapted from Constitution.md Purpose section]

## Charter Goals

### G-001: Grounding in Reality
AI agents query verified truth from implementation and intent graphs, not hallucinate.
JIG grounds agent work in verifiable facts by automatically extracting actual code structure,
explicit specifications, and test relationships.

### G-002: Continuity Across Sessions
Persistent, machine-readable context survives session boundaries. The next agent (or the
same agent tomorrow) can read intent graphs, implementation graphs, and traceability links
that capture what exists and why.

### G-003: Enforcing Constraints
Architectural boundaries are validated automatically before code commits. Agents cannot
introduce circular dependencies, violate layering rules, or create coupling that violates
defined constraints.

### G-004: Intent Alignment
WHY (specifications, outcomes) is explicit and required before modifying HOW (code).
Agents must read specifications before implementing, outcomes before creating specifications.

### G-005: Full Traceability
Every function traces to specifications, specifications to outcomes, outcomes to goals,
goals to Charter. Breaks in this chain indicate misalignment between intent and reality.

## [Rest of content adapted from Constitution.md]
```

**Migration:** Constitution.md content is restructured, not deleted. Original archived to `jig/old/Constitution_v1.md`.

---

#### A-001.md (ARCHITECTURE DOCUMENT)

**File:** `jig/architecture/A-001_JIG_Core_Architecture.md`

**Purpose:** Merge C001 (Core Artifacts Contract) and C002 (Bricks with Towers) into single authoritative architecture document.

**Frontmatter:**
```yaml
---
id: A-001
type: architecture
title: JIG Core Architecture
status: active
supports_goals: [G-001, G-003, G-004, G-005]
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
[Content from C001 section 5 + C002 tower concept]

## Layer and Tower Model
[Content from C002 - layers are horizontal, towers are vertical]

## Validation Rules
[Content from C001 Validation Contract + C002 tower validation]
```

---

#### New Outcomes (O-023 through O-026)

**O-023: Charter establishes project goals**

```yaml
---
id: O-023
type: outcome
title: Charter establishes project goals
supports_goals: [G-005, G-004]
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
supports_goals: [G-003, G-005]
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
supports_goals: [G-005, G-002]
specifies: [S-080, S-081, S-082, S-083, S-084, S-085]
---

# Intent graph captures full hierarchy

The intent graph includes Charter, Goal, and Architecture nodes in addition
to Outcomes, Specifications, and Bricks. All six relationship types are
represented as edges.

## Value
- Complete traceability from functions to Charter
- Queries like "which code supports G-003?" become possible
- Architecture constraints visible in graph structure
```

**O-026: Towers enforce component isolation**

```yaml
---
id: O-026
type: outcome
title: Towers enforce component isolation
supports_goals: [G-003]
specifies: [S-086, S-087, S-088, S-089, S-090, S-091]
---

# Towers enforce component isolation

Bricks are assigned to towers (vertical partitions). Cross-tower dependencies
are forbidden, enforcing complete isolation between components.

## Value
- Components can be developed/deployed independently
- Multi-language freedom (tower can be rewritten in different language)
- Clean testing (each tower tests against INTENT, not other towers)

## Note on JIG's Single Tower

JIG currently uses a single tower (`jig`) since it is a cohesive tooling system.
This demonstrates that the tower model supports single-component projects.
Future JIG extensions (e.g., visualization tools) could introduce additional towers.
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
- S-076: Architecture files in jig/architecture/A-{NNN}_{Title}.md
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

**Tower specs (S-086 through S-091):**
- S-086: Brick tower field optional
- S-087: Tower value format (kebab-case)
- S-088: Cross-tower dependencies forbidden
- S-089: jigy validate checks tower isolation
- S-090: jigy towers command
- S-091: jigy matrix command

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| MODIFY | B-cli | 1 | Add new commands (show charter/goals/arch, towers, matrix) |
| MODIFY | B-validation | 0 | Add charter/architecture/goal/tower validation |
| MODIFY | B-intent-graph | 0 | Add Charter/Goal/Architecture nodes and edges |
| MODIFY | B-config | 0 | Add charter/architecture path configuration |
| UNAFFECTED | B-decorators | 0 | No code changes required |
| UNAFFECTED | B-impl-graph | 0 | No code changes required |
| UNAFFECTED | B-hashing | 0 | No code changes required |
| UNAFFECTED | B-languages | 0 | No code changes required |
| UNAFFECTED | B-verification-graph | 1 | No code changes required |
| UNAFFECTED | B-audit | 1 | No code changes required |
| UNAFFECTED | B-staleness | 0 | No code changes required |
| FORBIDDEN | (none) | - | No bricks are forbidden; all may be modified if needed |

**Summary:** 4 bricks require code changes; 7 bricks are unaffected.

---

### Brick Details

#### All Bricks: Tower Field Optional

**Format (unchanged for single-tower projects):**
```yaml
- id: B-decorators
  name: JIG Core Decorators
  layer: 0
  # tower field omitted — single-tower project
  units:
    - M-jig.__init__
```

**Rationale:** JIG is a single cohesive tool. As a single-tower project, the `tower` field is omitted from all bricks. Cross-tower validation is skipped. This demonstrates that the tower model is opt-in — projects that don't need vertical partitioning simply don't use it.

#### B-validation Modifications

**New functionality:**
- `validate_charter_file()` - Charter validation
- `validate_architecture_files()` - Architecture validation
- `validate_goal_references()` - Goal reference validation
- `validate_tower_isolation()` - Cross-tower dependency checking

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

**Note:** Towers are implicit (inferred from brick usage), not configured. No `VALID_TOWERS` constant needed.

#### B-cli Modifications

**New commands:**
- `jigy show charter` - Display Charter and goals
- `jigy show goals` - List goals with supporting artifacts
- `jigy show architecture` - List architecture documents
- `jigy towers` - List towers with brick counts
- `jigy matrix` - Display layer×tower grid

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

### Tower Structure (Single-Tower)

```
(no towers declared — single-tower project)
  Layer 0: B-decorators, B-validation, B-impl-graph, B-intent-graph,
           B-config, B-hashing, B-languages, B-staleness
  Layer 1: B-cli, B-verification-graph, B-audit
```

**Note:** JIG is a single-tower project. The `tower` field is omitted from all bricks, and cross-tower validation is skipped. The tower infrastructure exists for multi-tower projects like ASE.

---

## @jig Decorator Changes

### Decorators to ADD

New validation functions:

| Type | Location | Spec |
|------|----------|------|
| implements | F-jig.validation.intent.validate_charter_file | S-072, S-073, S-074, S-075 |
| implements | F-jig.validation.intent.validate_architecture_files | S-076, S-077, S-078, S-079 |
| implements | F-jig.validation.intent.validate_goal_references | S-075 |
| implements | F-jig.validation.bricks.validate_tower_format | S-086, S-087 |
| implements | F-jig.validation.bricks.validate_tower_isolation | S-088, S-089 |

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
| implements | F-jig.cli.towers.towers_command | S-090 |
| implements | F-jig.cli.towers.matrix_command | S-091 |

### Decorators to REMOVE

None - no specs are being deleted.

### Decorators to MODIFY

None - existing spec IDs unchanged.

---

## Clean Break Actions

This work follows clean break protocol (per SCOPE, no backwards compatibility requested):

- [x] Old code paths will be DELETED, not feature-flagged
- [x] Old tests will be DELETED and new tests written from scratch
- [x] No backwards compatibility shims
- [x] Validation mandatory immediately (not opt-in)
- [x] Graph version bumps to 2.0 (not backward compatible)
- [x] Constitution.md archived (not deleted) to preserve history

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
│   └── A-001_JIG_Core_Architecture.md  # NEW: Core Architecture
├── outcomes/
│   └── O-{NNN}_{Title}.md        # UPDATED + NEW (26 files)
├── specifications/
│   └── S-{NNN}_{Title}.md        # EXISTING + NEW (91 files)
├── bricks.yaml                   # UPDATED: tower field
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
# ✓ Outcomes: 22 files (18 existing + 4 new), all have supports_goals
# ✓ Specifications: 74 files (54 existing + 20 new), all valid
# ✓ Bricks: 11 bricks (tower field optional, omitted)
# ✓ Towers: single-tower project, cross-tower validation skipped
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

- [x] All existing specs reviewed - 54 specs exist (S-001 to S-071 with gaps), no changes needed
- [x] All existing outcomes reviewed - 18 outcomes need supports_goals (O-001 to O-022 with gaps)
- [x] Charter goals derived from Constitution's 4 purposes + traceability (G-001 to G-005)
- [x] Architecture document merges C001 + C002 proposals (A-001_JIG_Core_Architecture.md)
- [x] Brick tower field optional (single-tower project, field omitted)
- [x] New specs follow evergreen guidelines (behavior, not implementation)
- [x] Layer constraints validated (no layer changes, 11 bricks stay at layers 0-1)
- [x] @jig decorator plan complete (15 new implementing functions, 5 new CLI commands)
- [x] Clean break actions specified (archive, don't delete Constitution)
- [x] Validation mandatory immediately (confirmed, breaking change)
- [x] Files to create explicitly listed (20 specs, 4 outcomes, Charter, A-001)

---

## Design Decisions

These decisions were made during JIGPLAN development:

### 1. Charter Goals (G-001 through G-005)

**Decision:** Goals derive directly from Constitution.md's four stated purposes, plus traceability.

| Goal | Source | Rationale |
|------|--------|-----------|
| G-001: Grounding in Reality | Constitution §1 | Core purpose: agents query truth, not hallucinate |
| G-002: Continuity Across Sessions | Constitution §2 | Core purpose: persistent context |
| G-003: Enforcing Constraints | Constitution §3 | Core purpose: automatic validation |
| G-004: Intent Alignment | Constitution §4 | Core purpose: WHY before HOW |
| G-005: Full Traceability | Constitution hierarchy | Implicit in design, made explicit |

### 2. Tower Field Handling

**Decision:** Omit tower field for JIG (single-tower project).

- Tower field is OPTIONAL per SCOPE C002
- Single-tower projects simply omit the field
- Cross-tower validation skipped when no towers declared
- This demonstrates the opt-in nature of towers

### 3. Archive Strategy

**Decision:** Archive Constitution.md to `jig/old/` (not delete).

- Preserves historical context for future reference
- Charter.md is the successor, not a replacement
- Archives retain provenance for decisions

### 4. Specification Granularity

**Decision:** 20 new specs (S-072 through S-091) is appropriate.

- 4 specs for Charter (structure, fields, headers, ID format)
- 4 specs for Architecture (location, ID format, required fields, reference integrity)
- 6 specs for Intent Graph (3 node types, 3 edge types)
- 6 specs for Towers (field, format, isolation, validation, 2 CLI commands)
- Granularity enables precise `@jig.implements` traceability

---

## Files to Create During JIGPLAN

Per taskMakeJIGPLAN Step 5, these O/S node files will be created:

### New Specifications (20 files)

```
jig/specifications/S-072_Charter_File_Structure.md
jig/specifications/S-073_Charter_Defines_Goals_Field.md
jig/specifications/S-074_Goal_Header_Format.md
jig/specifications/S-075_Goal_ID_Format.md
jig/specifications/S-076_Architecture_File_Location.md
jig/specifications/S-077_Architecture_ID_Format.md
jig/specifications/S-078_Architecture_Supports_Goals_Required.md
jig/specifications/S-079_Architecture_Constrains_References.md
jig/specifications/S-080_Charter_Node_In_Intent_Graph.md
jig/specifications/S-081_Goal_Nodes_In_Intent_Graph.md
jig/specifications/S-082_Architecture_Nodes_In_Intent_Graph.md
jig/specifications/S-083_Defines_Goal_Edges.md
jig/specifications/S-084_Supports_Goal_Edges.md
jig/specifications/S-085_Constrains_Edges.md
jig/specifications/S-086_Brick_Tower_Field_Optional.md
jig/specifications/S-087_Tower_Value_Format.md
jig/specifications/S-088_Cross_Tower_Isolation.md
jig/specifications/S-089_Tower_Isolation_Validation.md
jig/specifications/S-090_Jigy_Towers_Command.md
jig/specifications/S-091_Jigy_Matrix_Command.md
```

### New Outcomes (4 files)

```
jig/outcomes/O-023_Charter_Establishes_Project_Goals.md
jig/outcomes/O-024_Architecture_Constrains_Specifications.md
jig/outcomes/O-025_Intent_Graph_Captures_Full_Hierarchy.md
jig/outcomes/O-026_Towers_Enforce_Component_Isolation.md
```

### New Root Document

```
jig/Charter.md
```

### New Architecture Directory and Document

```
jig/architecture/A-001_JIG_Core_Architecture.md
```

---

**Awaiting human approval before proceeding to implementation PLAN.**
