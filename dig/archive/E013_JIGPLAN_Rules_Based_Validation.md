---
title: "JIGPLAN: Rules-Based Validation"
type: jigplan
status: implemented
decision: completed
created: 1737244800
created_human: "2026-01-18 19:00 CST"
parent: "[[E012_SCOPE_Rules_Based_Validation]]"
children: []
---

# JIGPLAN: Rules-Based Validation

**SCOPE:** dig/wip/E012_SCOPE_Rules_Based_Validation.md
**Date:** 2026-01-18
**Status:** Draft
**Author:** Claude (agent)

---

## Summary

Migrate JIG validation from procedural functions to a rules-based architecture. Creates 2 new bricks (B-rules, B-mend), modifies 2 existing bricks (B-validation, B-cli), adds 6 new specifications for mend command and rule engine, and requires major rewrite of A-004 architecture document. Core validation logic specs (S-018 through S-095) are REUSED unchanged - they define WHAT rules check, the rules engine defines HOW.

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | O-004 | Early Error Detection in Artifact Validation | Existing outcome covers validation CLI |
| REUSE | O-005 | Actionable Error Messages | Existing outcome covers error quality |
| REUSE | O-013 | Layer Architecture Enforcement | Existing outcome covers layer rules |
| REUSE | O-015 | Completeness Validation for Intent Graph | Existing outcome covers bidirectional links |
| CREATE | O-029 | Automated Validation Repair | NEW: mend command and fix templates |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | S-018 | Specification File Validation | Defines what to validate - rules implement this |
| REUSE | S-019 | Outcome File Validation | Defines what to validate - rules implement this |
| REUSE | S-020 | Decorator Reference Validation | Defines what to validate - rules implement this |
| REUSE | S-021 | Brick Definition Validation | Defines what to validate - rules implement this |
| REUSE | S-022 | Brick Partition Validation | Defines what to validate - rules implement this |
| REUSE | S-035 | Brick ID Format Validation | Defines what to validate - rules implement this |
| REUSE | S-036 | Layer Field Presence Validation | Defines what to validate - rules implement this |
| REUSE | S-037 | Layer Value Validation | Defines what to validate - rules implement this |
| REUSE | S-038 | Layer Constraint Validation | Defines what to validate - rules implement this |
| REUSE | S-039 | Circular Dependency Detection | Defines what to validate - rules implement this |
| REUSE | S-042 | Outcomes Must Specify Specifications | Defines what to validate - rules implement this |
| REUSE | S-043 | Specifications Must Have Outcome Coverage | Defines what to validate - rules implement this |
| REUSE | S-089 | Tower Isolation Validation | Defines what to validate - rules implement this |
| REUSE | S-087 | Tower Value Format | Defines what to validate - rules implement this |
| REUSE | S-088 | Cross Tower Isolation | Defines what to validate - rules implement this |
| REUSE | S-095 | Bidirectional Reference Consistency | Defines what to validate - rules implement this |
| REUSE | S-023 | Intent Validation CLI Command | Existing CLI - gains -j output via S-104 |
| REUSE | S-024 | Brick Validation CLI Command | Existing CLI - gains -j output via S-104 |
| REUSE | S-025 | Full Validation CLI Command | Existing CLI - gains -j output via S-104 |
| CREATE | S-104 | Validation Fix Template Output | NEW: JSON output with fix templates |
| CREATE | S-105 | Mend Command Auto Mode | NEW: `jigy mend --auto` |
| CREATE | S-106 | Mend Command Apply Mode | NEW: `jigy mend --apply` |
| CREATE | S-107 | Mend Fixed Point Iteration | NEW: iterate until stable |
| CREATE | S-108 | Validation Error ID Stability | NEW: deterministic error IDs |
| CREATE | S-109 | Rule Spec Traceability | NEW: rules reference specs |

---

## O/S Node Details

### Nodes to CREATE

#### O-029: Automated Validation Repair (NEW)

**File:** `jig/outcomes/O-029_Automated_Validation_Repair.md` (created)
**Supports Goals:** G-003 (Enforcing Constraints), G-004 (Intent Alignment)
**Summary:** Validation errors include machine-readable repair instructions enabling automated or agent-assisted fixing.

#### S-104: Validation Fix Template Output (NEW)

**File:** `jig/specifications/S-104_Validation_Fix_Template_Output.md` (created)
**Implements:** O-029, O-005
**Summary:** `jigy validate -j` outputs errors with `fix` field containing structured repair instructions.

#### S-105: Mend Command Auto Mode (NEW)

**File:** `jig/specifications/S-105_Mend_Command_Auto_Mode.md` (created)
**Implements:** O-029
**Summary:** `jigy mend --auto` applies all fixes where `auto: true`.

#### S-106: Mend Command Apply Mode (NEW)

**File:** `jig/specifications/S-106_Mend_Command_Apply_Mode.md` (created)
**Implements:** O-029
**Summary:** `jigy mend --apply fixes.json` applies explicit fixes from a JSON file.

#### S-107: Mend Fixed Point Iteration (NEW)

**File:** `jig/specifications/S-107_Mend_Fixed_Point_Iteration.md` (created)
**Implements:** O-029
**Summary:** Mend iterates (max 3) until no new auto-fixable errors appear.

#### S-108: Validation Error ID Stability (NEW)

**File:** `jig/specifications/S-108_Validation_Error_ID_Stability.md` (created)
**Implements:** O-029, O-005
**Summary:** Validation errors have stable IDs computed from rule code, artifact ID, and context.

#### S-109: Rule Spec Traceability (NEW)

**File:** `jig/specifications/S-109_Rule_Spec_Traceability.md` (created)
**Implements:** O-029, O-005
**Summary:** Each rule references the spec it enforces, enabling error-to-requirement traceability.

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| CREATE | B-rules | 0 | Rule types, registry, protocols |
| CREATE | B-mend | 0 | Mend engine, fix actions, YAML editor |
| MODIFY | B-validation | 0 | Rewrite to use rule engine |
| MODIFY | B-cli | 1 | Add mend.py command |
| FORBIDDEN | B-decorators | 0 | Core decorators unchanged |
| FORBIDDEN | B-impl-graph | 0 | Graph building unchanged |
| FORBIDDEN | B-intent-graph | 0 | Graph building unchanged |
| FORBIDDEN | B-config | 0 | Config loading unchanged |
| FORBIDDEN | B-hashing | 0 | Hashing unchanged |
| FORBIDDEN | B-languages | 0 | Language analyzers unchanged |
| FORBIDDEN | B-verification-graph | 1 | Verification graph unchanged |
| FORBIDDEN | B-audit | 1 | Audit system unchanged |
| FORBIDDEN | B-staleness | 0 | Staleness detection unchanged |
| FORBIDDEN | B-templates | 0 | Templates unchanged |
| FORBIDDEN | B-init | 0 | Init unchanged |

---

### Brick Details

#### B-rules (NEW)

- **Layer:** 0
- **Purpose:** Rule type classes, rule registry, validation/mend protocols
- **Units:**
  - M-jig.rules.base (Rule protocol, Violation, Fix dataclasses)
  - M-jig.rules.context (ValidationContext, MendContext)
  - M-jig.rules.registry (RULES list, RULES_BY_CODE, RULES_BY_SPEC)
  - M-jig.rules.types.required_field
  - M-jig.rules.types.id_format
  - M-jig.rules.types.uniqueness
  - M-jig.rules.types.filename_sync
  - M-jig.rules.types.header_sync
  - M-jig.rules.types.excluded_field
  - M-jig.rules.types.field_type
  - M-jig.rules.types.field_value
  - M-jig.rules.types.reference_validity
  - M-jig.rules.types.bidirectional_link
  - M-jig.rules.types.coverage
  - M-jig.rules.types.partition
  - M-jig.rules.types.dag
  - M-jig.rules.types.layer_constraint
  - M-jig.rules.types.isolation
- **Dependencies:** None (foundation brick)

#### B-mend (NEW)

- **Layer:** 0
- **Purpose:** Mend execution engine, fix action implementations, YAML-preserving editor
- **Units:**
  - M-jig.mend.engine (apply fixes, iterate to fixed point)
  - M-jig.mend.actions (set_field, add_field_value, rename_file, etc.)
  - M-jig.mend.yaml_editor (YAML-preserving frontmatter modification)
- **Dependencies:** B-rules (uses Fix dataclass)
- **Layer 0 dependency note:** Per A-001 §Layer 0 special rules, layer 0 bricks MAY depend on other layer 0 bricks. Horizontal dependencies within layer 0 are permitted.

#### B-validation Modifications

- **Current units:** M-jig.validation.intent, M-jig.validation.bricks, M-jig.validation.models, M-jig.validation.reporting
- **Changes:**
  - M-jig.validation.intent → DELETE (replaced by rules)
  - M-jig.validation.bricks → DELETE (replaced by rules)
  - M-jig.validation.models → KEEP (ValidationError, ValidationResult)
  - M-jig.validation.reporting → KEEP (output formatting)
  - M-jig.validation.engine → ADD (runs rules, produces results)
- **Layer change:** None (stays at layer 0)
- **New dependencies:** B-rules

#### B-cli Modifications

- **Current units:** M-jig.cli.* (main, validate, discovery, rebuild, show, audit, auto_rebuild, output, init)
- **Add units:** M-jig.cli.mend
- **Layer change:** None (stays at layer 1)
- **New dependencies:** B-mend (for mend command)
- **Changes:** validate.py updated to use rule engine, mend.py added

#### FORBIDDEN Bricks

These bricks MUST NOT be modified by any work unit:

- **B-decorators** (layer 0): Core @jig.implements/@jig.verifies - no changes needed
- **B-impl-graph** (layer 0): Graph building - no changes needed
- **B-intent-graph** (layer 0): Intent graph generation - no changes needed
- **B-config** (layer 0): Configuration loading - no changes needed
- **B-hashing** (layer 0): Content hashing - no changes needed
- **B-languages** (layer 0): Python analyzer - no changes needed
- **B-verification-graph** (layer 1): Test verification - no changes needed
- **B-audit** (layer 1): Audit coverage - no changes needed
- **B-staleness** (layer 0): Staleness detection - no changes needed
- **B-templates** (layer 0): Template content - no changes needed
- **B-init** (layer 0): Project initialization - no changes needed

**Sub-agent constraint:** Any modification to FORBIDDEN bricks is an immediate escalation trigger.

---

## Layer/Dependency Analysis

### Layer Structure (Affected Bricks)

```
Layer 0: FOUNDATION
  B-rules (NEW)
    └─► depends on: nothing ✓
  B-mend (NEW)
    └─► depends on: B-rules ✓
  B-validation (MODIFY)
    └─► depends on: B-rules (NEW dependency) ✓

Layer 1: CLI
  B-cli (MODIFY)
    └─► depends on: B-validation, B-mend (NEW dependency) ✓
```

### Dependency Constraints

- B-rules (layer 0) MUST NOT depend on any other project bricks
- B-mend (layer 0) MAY depend on B-rules (layer 0)
- B-validation (layer 0) MAY depend on B-rules (layer 0)
- B-cli (layer 1) MAY depend on B-rules, B-mend, B-validation (all layer 0)
- No circular dependencies between affected bricks

### Validation Commands

After implementation, verify with:
```bash
jigy rebuild && jigy validate
jigy layers  # Confirm layer structure
```

---

## @jig Decorator Changes

### Decorators to ADD

| Type | Location | Spec |
|------|----------|------|
| implements | F-jig.rules.base.Rule | S-109 |
| implements | F-jig.rules.base.Violation | S-108 |
| implements | F-jig.rules.base.Fix | S-104 |
| implements | F-jig.rules.registry.RULES | S-109 |
| implements | F-jig.validation.engine.validate | S-104 |
| implements | F-jig.mend.engine.mend_auto | S-105, S-107 |
| implements | F-jig.mend.engine.mend_apply | S-106 |
| implements | F-jig.cli.mend.mend_command | S-105, S-106 |
| verifies | T-test_rules.* | S-104, S-108, S-109 |
| verifies | T-test_mend.* | S-105, S-106, S-107 |

### Decorators to REMOVE

| Type | Location | Spec | Reason |
|------|----------|------|--------|
| implements | F-jig.validation.intent.* | Various | Functions deleted, replaced by rules |
| implements | F-jig.validation.bricks.* | Various | Functions deleted, replaced by rules |
| verifies | T-test_validation.intent.* | Various | Tests rewritten for rule engine |
| verifies | T-test_validation.bricks.* | Various | Tests rewritten for rule engine |

### Decorators to KEEP

Existing decorators on functions in FORBIDDEN bricks remain unchanged.

---

## Architecture Document Updates

### A-004 (Validation Architecture) — Major Rewrite

A-004 currently documents procedural validation. Must be rewritten to describe rules-based architecture:

| Section | Change |
|---------|--------|
| Domain Overview table | Replace "Function" column with "Rule Type" column |
| Per-domain sections | Replace "Function" subsections with "Rule Instances" |
| Execution Model | Describe rule engine, flat rule list, cascading errors |
| New: Mend Architecture | Add section for mend command, fix actions, MendContext |
| New: Fix Action Primitives | Document frontmatter/file actions |
| Spec Traceability Matrix | Rewrite: A-004 Rule → Spec → Rule Instance |
| Validation Order | Update to reflect flat rule list |
| Frontmatter specifications | Add S-104, S-105, S-106, S-107, S-108, S-109 |

### A-002 (CLI Command Architecture) — Minor Update

- Add `jigy mend` to Command Hierarchy section (lines 195-218)
- Add mend subcommands: `--auto`, `--apply`, `--dry-run`

**This update is part of Phase 5 (Cleanup) in Migration Strategy.**

---

## Clean Break Actions

This work follows clean break protocol:

- [x] Old code paths will be DELETED, not feature-flagged
- [x] Old tests will be DELETED and new tests written from scratch
- [x] No backwards compatibility shims
- [x] Unimplemented features will raise NotImplementedError
- [x] Deleted O/S nodes removed after final validation

### Code to Delete

- `src/jig/validation/intent.py` (entire module - replaced by rules)
- `src/jig/validation/bricks.py` (entire module - replaced by rules)
- `tests/unit/test_intent_validation.py` (rewrite as rule tests)
- `tests/unit/test_bricks_validation.py` (rewrite as rule tests)
- Any imports of deleted modules

### O/S Nodes to Delete

None. All existing validation specs are REUSED - they define WHAT rules check.

---

## Migration Strategy (from E012)

### Phase 1: Infrastructure (No Behavior Change)

1. Create `src/jig/rules/` module structure
2. Implement `ValidationContext` loader
3. Implement `MendContext` with YAML-preserving editor
4. Implement fix action primitives
5. Add `Fix` field to `ValidationError` model

**Deliverable:** Infrastructure ready, existing validation unchanged.

### Phase 2: Rule Types

1. Implement each rule type class (15 types)
2. Unit test each rule type in isolation
3. Create `RULES` registry with all current validations

**Deliverable:** All rule types implemented and tested.

### Phase 3: Validation Engine

1. Create `validation/engine.py` that runs rules
2. Wire `jigy validate` to use rule engine
3. Verify same errors detected (coverage parity test, not bit-identical output)
4. Add `-j` output with fix templates

**Deliverable:** `jigy validate` produces fix templates.

### Phase 4: Mend Command

1. Implement `mend/engine.py`
2. Implement `cli/mend.py` with `--auto` and `--apply`
3. Integration tests for validate → mend → validate cycle

**Deliverable:** Full validate/mend workflow operational.

### Phase 5: Cleanup

1. Remove old `validation/intent.py` functions (replaced by rules)
2. Remove old `validation/bricks.py` functions (replaced by rules)
3. Update A-004 architecture document
4. Update documentation

**Deliverable:** Clean codebase with single validation path.

---

## Fresh Agent Review Summary

### Review Findings

| Category | Type | Severity | Issue | Resolution |
|----------|------|----------|-------|------------|
| 1 | MECHANICAL | WARNING | S-087, S-088 missing from REUSE list | Added to spec reconciliation table |
| 1 | MECHANICAL | WARNING | A-004 frontmatter needs new specs | Added to A-004 update requirements |
| 2 | MECHANICAL | BLOCKER | S-108 had implementation code | Rewrote to describe observable properties |
| 2 | MECHANICAL | WARNING | S-109 had implementation details | Cleaned up to be more abstract |
| 3 | MECHANICAL | NOTE | Layer 0 dependency authorization unclear | Added citation to A-001 special rules |
| 4 | MECHANICAL | WARNING | Decorator plan incomplete for rule types | Acceptable - decorators assigned during impl |
| 5 | MECHANICAL | WARNING | S-105, S-106 referenced A-002 | Removed A-002 from architecture field |
| 5 | MECHANICAL | WARNING | A-002 needs `jigy mend` command | Added A-002 update to architecture section |
| 5 | MECHANICAL | NOTE | Regression test vs clean break | Clarified as "coverage parity" not bit-identical |

### Judgment Decisions

**Issue:** S-107 specifies "Maximum 3 iterations" - is this a spec or implementation choice?

**Options considered:**
1. Keep exact number (3) in spec - agents know the bound
2. Say "reasonable iterations" and let implementation choose

**Decision:** Keep as-is. The bound is observable behavior that agents and users may depend on. If mend takes more than 3 iterations, something is wrong with rule definitions. The number is a spec, not an implementation detail.

### Blockers Resolved

- S-108 implementation code removed - now describes observable ID properties
- Layer 0 dependency citation added - A-001 §Layer 0 special rules authorizes

### All MECHANICAL Issues Resolved

- Specs updated (S-108, S-109, S-105, S-106)
- JIGPLAN updated with missing specs, architecture update notes, and clarifications

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
- [x] All JUDGMENT issues resolved via Charter philosophy OR escalated
- [x] `jigy rebuild && jigy validate` passes

---

**Awaiting human approval before proceeding to PLAN.**
