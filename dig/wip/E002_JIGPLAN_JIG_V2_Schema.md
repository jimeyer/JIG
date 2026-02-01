---
type: jigplan
title: "JIGPLAN: JIG V2 Schema Migration"
status: active
created: 1768595487
created_human: "2026-01-16 10:31 PST"
parent: "[[E001_SCOPE_JIG_V2_Schema]]"
children: ["[[E003_PLAN_JIG_V2_Schema]]"]
prompt: |
  now create the jigplan
  follow @agents/taskMakeJIGPLAN.md
  dig this as E002_JIGPLAN
---

# JIGPLAN: JIG V2 Schema Migration

**SCOPE:** dig/wip/E001_SCOPE_JIG_V2_Schema.md
**Date:** 2026-01-16
**Status:** Draft
**Author:** AI Agent

---

## Summary

Migrate JIG schema from V1 to V2: normalize 5 field names across Charter/Architecture/Outcome artifacts, add required bidirectional references on specifications, remove `status` from JIG's concern. Affects 12 specs, 105 content files, and ~2000 LOC in validation/graph-generation.

**Bootstrap constraint:** Spec files describe the NEW schema but cannot be updated until code supports V2. Migration is atomic—code, specs, and content change together.

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | O-004 | Early Error Detection in Artifact Validation | Validation behavior unchanged, field names change |
| REUSE | O-023 | Charter Establishes Project Goals | Goal semantics unchanged |
| REUSE | O-024 | Architecture Constrains Specifications | Relationship semantics unchanged |
| REUSE | O-025 | Intent Graph Captures Full Hierarchy | Graph structure unchanged |

No new outcomes needed—V2 is a schema normalization, not new functionality.

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| UPDATE | S-018 | Specification File Validation | Add required `outcomes`, `architecture` fields |
| UPDATE | S-019 | Outcome File Validation | `supports_goals`→`goals`, `specifies`→`specifications` |
| UPDATE | S-028 | CLI Command to Generate Intent Graph | Update node/edge field names in output |
| UPDATE | S-042 | Outcomes Must Specify Specifications | `specifies`→`specifications` |
| UPDATE | S-043 | Specifications Must Have Outcome Coverage | Reference new field name |
| UPDATE | S-073 | Charter Defines Goals Field | `defines_goals`→`goals`, rename spec |
| UPDATE | S-078 | Architecture Supports Goals Required | `supports_goals`→`goals`, rename spec |
| UPDATE | S-079 | Architecture Constrains References | `constrains`→`specifications`, rename spec |
| UPDATE | S-082 | Architecture Nodes In Intent Graph | Remove `status`, rename fields |
| UPDATE | S-084 | Supports Goal Edges | Update field references |
| UPDATE | S-085 | Constrains Edges | `constrains`→`specifications` edge type |
| CREATE | S-095 | Bidirectional Reference Consistency | Spec back-refs must match forward-refs |

---

## O/S Node Details

### Nodes to UPDATE

#### S-018: Specification File Validation

**Current required fields:** `id`, `type`, `title`

**Changes:**
- ADD: Required field `outcomes` — array of O-### IDs (non-empty)
- ADD: Required field `architecture` — array of A-### IDs (non-empty)
- ADD: Validation that referenced outcomes/architecture exist

#### S-019: Outcome File Validation

**Current validation:** Basic frontmatter (id, type, title) only. No validation of goal/spec references.

**Changes:**
- ADD: Required `goals` array validation (non-empty, G-### format)
- ADD: Required `specifications` array validation (non-empty, S-### format)
- ADD: Optional `architecture` array validation (A-### format if present)
- ADD: Reference existence checking (goals/specs/arch must exist)

#### S-028: CLI Command to Generate Intent Graph

**Current node format:**
```json
{"id":"O-001","type":"outcome","specifies":["S-001"]}
```

**Changes:**
- Outcome nodes: `specifies` → `specifications`
- Architecture nodes: `supports_goals` → `goals`, `constrains` → `specifications`, remove `status`
- Charter nodes: `defines_goals` → `goals`
- Edge types: `constrains` → `specifications`

#### S-042: Outcomes Must Specify Specifications

**Changes:**
- All references to `specifies` → `specifications`
- Error messages updated

#### S-043: Specifications Must Have Outcome Coverage

**Changes:**
- Reference `specifications` field instead of `specifies`
- Can now also validate bidirectional consistency

#### S-073: Charter Defines Goals Field → Charter Goals Field

**Changes:**
- RENAME spec title to "Charter Goals Field"
- RENAME field: `defines_goals` → `goals`
- Update examples, validation rules, error messages

#### S-078: Architecture Supports Goals Required → Architecture Goals Required

**Changes:**
- RENAME spec title to "Architecture Goals Required"
- RENAME field: `supports_goals` → `goals`
- Remove `status` from example

#### S-079: Architecture Constrains References → Architecture Specifications References

**Changes:**
- RENAME spec title to "Architecture Specifications References"
- RENAME field: `constrains` → `specifications`
- Remove `status` from example

#### S-082: Architecture Nodes In Intent Graph

**Current required node fields:**
- status: from frontmatter
- supports_goals: array
- constrains: optional array

**Changes:**
- REMOVE: `status` field entirely
- RENAME: `supports_goals` → `goals`
- RENAME: `constrains` → `specifications`

#### S-084: Supports Goal Edges

**Changes:**
- Update references from `supports_goals` to `goals`
- Edge type remains `supports_goal` (describes relationship, not field)

#### S-085: Constrains Edges → Specifications Edges

**Changes:**
- RENAME spec title to "Specifications Edges"
- RENAME field reference: `constrains` → `specifications`
- RENAME edge type: `constrains` → `specifications`

---

### Nodes to CREATE

#### S-095: Bidirectional Reference Consistency (NEW)

**File:** `jig/specifications/S-095_Bidirectional_Reference_Consistency.md`
**Outcomes:** O-004, O-025

**Statement:**
Specification back-references must be consistent with forward-references from outcomes and architecture.

**Invariants:**
- If O-001.specifications contains S-042, then S-042.outcomes must contain O-001
- If A-001.specifications contains S-072, then S-072.architecture must contain A-001
- Validation reports both directions of inconsistency

**Verification:**
- [ ] Missing back-ref detected: O references S but S doesn't reference O
- [ ] Missing forward-ref detected: S references O but O doesn't reference S
- [ ] Bidirectional consistency passes when refs match

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| MODIFY | B-validation | 0 | Field name changes in validation logic |
| MODIFY | B-intent-graph | 0 | Field name changes in graph generation |
| MODIFY | B-cli | 1 | Output format changes |
| FORBIDDEN | B-impl-graph | 0 | Implementation graph unaffected |
| FORBIDDEN | B-verification-graph | 1 | Verification graph unaffected |
| UNAFFECTED | B-config | 0 | No schema changes in config |

---

### Brick Details

#### B-validation Modifications

**Affected files:**
- `src/jig/validation/intent.py` — field name changes throughout

**Changes:**
- `_validate_charter_frontmatter()`: `defines_goals` → `goals`
- `_validate_architecture_frontmatter()`: `supports_goals` → `goals`, `constrains` → `specifications`, remove `status`
- `_validate_outcome_frontmatter()`: `supports_goals` → `goals`, `specifies` → `specifications`
- `_validate_specification_frontmatter()`: add required `outcomes`, `architecture`
- ADD: `_validate_bidirectional_consistency()` for S-095

#### B-intent-graph Modifications

**Affected files:**
- `src/jig/intent_graph/generator.py` — field name changes in node/edge generation

**Changes:**
- `_load_charter_node()`: read `goals` instead of `defines_goals`
- `_load_architecture_nodes()`: read `goals`/`specifications`, omit `status`
- `_load_outcome_nodes()`: read `goals`/`specifications`
- `_create_*_edges()`: update edge type names

#### FORBIDDEN Bricks

- **B-impl-graph** (layer 0): Implementation graph uses code AST, not intent frontmatter
- **B-verification-graph** (layer 1): Verification graph uses test AST, not intent frontmatter

---

## Layer/Dependency Analysis

```
Layer 0: AFFECTED
  B-config ← no changes
  B-validation (MODIFY)
    └─► depends on: external libs only ✓
  B-intent-graph (MODIFY)
    └─► depends on: external libs only ✓

Layer 1: AFFECTED
  B-cli (MODIFY)
    └─► depends on: B-validation, B-intent-graph ✓
```

No layer violations introduced.

---

## @jig Decorator Changes

### Decorators to ADD

| Type | Location | Spec |
|------|----------|------|
| implements | F-validation.intent.validate_bidirectional_consistency | S-095 |
| verifies | T-test_intent.test_bidirectional_consistency_* | S-095 |

### Decorators to MODIFY

Existing decorators remain valid—specs retain their IDs. No decorator removals.

---

## Content Migration Plan

### Phase 1: Charter (1 file)

```yaml
# Before
defines_goals: [G-001, G-002, ...]

# After
goals: [G-001, G-002, ...]
```

### Phase 2: Architecture (4 files)

```yaml
# Before
supports_goals: [G-001, G-003]
constrains: [S-072, S-073]
status: active

# After
goals: [G-001, G-003]
specifications: [S-072, S-073]
# status removed
```

### Phase 3: Outcomes (23 files)

```yaml
# Before
supports_goals: [G-001, G-002]
specifies: [S-001, S-003]

# After
goals: [G-001, G-002]
specifications: [S-001, S-003]
```

### Phase 4: Specifications (77 files)

```yaml
# Before
id: S-042
title: Outcomes Must Specify Specifications
type: specification

# After
id: S-042
title: Outcomes Must Specify Specifications
type: specification
outcomes: [O-015]
architecture: [A-001]
```

**Note:** Back-references must be computed from current forward-refs in outcomes/architecture.

---

## Test Updates

### Fixtures requiring field renames

- `tests/fixtures/jig/Charter.md`
- `tests/fixtures/jig/outcomes/*.md`
- `tests/fixtures/jig/architecture/*.md`
- `tests/fixtures/jig/specifications/*.md`

### Test assertions requiring updates

- Any assertion checking for `supports_goals`, `specifies`, `constrains`, `defines_goals`, `status`
- Expected error messages containing old field names

---

## Clean Break Actions

This work follows clean break protocol:

- [x] Old field names become validation errors (not warnings)
- [x] No backwards compatibility shims
- [x] `status` field removed entirely, not deprecated
- [x] Atomic migration: all 105 files change in single commit

### Migration Script Required

A migration script will:
1. Update field names in all markdown files
2. Compute and add back-references to spec files
3. Remove `status` from architecture files

---

## Fresh Agent Review Summary

Review performed: 2026-01-16

### Review Findings

| Category | Type | Severity | Issue | Resolution |
|----------|------|----------|-------|------------|
| 3 | MECHANICAL | BLOCKER | Brick layers wrong: E002 said B-validation/B-intent-graph at layer 1, actual is layer 0 | Fixed layer assignments in Brick Scope and Layer/Dependency Analysis |
| 1 | MECHANICAL | WARNING | S-019 description said "rename fields" but S-019 doesn't currently validate those fields | Changed to "ADD validation" for goals/specifications fields |
| 3 | MECHANICAL | NOTE | Brick name B-verify-graph should be B-verification-graph per bricks.yaml | Fixed brick name in FORBIDDEN table |
| 5 | MECHANICAL | NOTE | S-095 file creation deferred due to bootstrap constraint | Documented in Bootstrap Constraint section |

### Bootstrap Constraint (S-095)

Per taskMakeJIGPLAN.md Step 5, new spec files should be written to disk. However, S-095 requires V2 frontmatter (`outcomes`, `architecture` fields) which the current validator would reject.

**Resolution:** S-095 creation is deferred to the atomic migration commit. The spec content is fully specified in this JIGPLAN. This is a valid exception to the "write files in Step 5" rule because the migration itself changes validation rules.

### Judgment Decisions

No JUDGMENT issues requiring Charter philosophy application.

---

## Approval Checklist

Before human approval:

- [x] All existing specs reviewed for REUSE opportunities
- [x] New specs follow evergreen guidelines (behavior, not implementation)
- [x] Brick layer constraints validated
- [x] FORBIDDEN bricks identified
- [x] @jig decorator plan complete
- [x] Clean break actions specified
- [x] **Fresh Agent Review completed (Step 9)**
- [x] All MECHANICAL issues resolved
- [x] All JUDGMENT issues resolved via Charter philosophy OR escalated (N/A - none found)
- [ ] Human approval pending

---

**Awaiting human approval before proceeding to PLAN.**
