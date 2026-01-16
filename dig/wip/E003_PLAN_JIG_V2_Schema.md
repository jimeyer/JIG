---
type: plan
title: "PLAN: JIG V2 Schema Migration"
status: active
created: 1768596160
created_human: "2026-01-16 10:42 PST"
parent: "[[E002_JIGPLAN_JIG_V2_Schema]]"
children: []
---

# PLAN: JIG V2 Schema Migration

- **SCOPE**: dig/wip/E001_SCOPE_JIG_V2_Schema.md
- **JIGPLAN**: dig/wip/E002_JIGPLAN_JIG_V2_Schema.md
- **Start**: 2026-01-16
- **Status**: Draft
- **Branch**: dev

---

## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- B-impl-graph (layer 0) — implementation graph uses code AST, not intent frontmatter
- B-verification-graph (layer 1) — verification graph uses test AST, not intent frontmatter

**Layer Constraints:**
- B-validation at layer 0
- B-intent-graph at layer 0
- B-cli at layer 1
- No upward dependencies

**Clean Break:**
- Old field names become validation errors immediately
- No backwards compatibility shims
- Atomic migration (code + content + specs together)

---

## Key Existing Code References

(Populated during Fresh Agent Review)

| Concern | Location | Notes |
|---------|----------|-------|
| Charter validation | `src/jig/validation/intent.py:788` | `validate_charter_file()` |
| Architecture validation | `src/jig/validation/intent.py:1051` | `validate_architecture_files()` |
| Outcome validation | `src/jig/validation/intent.py:306` | `validate_outcome_files()` |
| Specification validation | `src/jig/validation/intent.py:177` | `validate_specification_files()` |
| Charter node loading | `src/jig/intent_graph/generator.py:135` | `_load_charter_node()` |
| Architecture node loading | `src/jig/intent_graph/generator.py:210` | `_load_architecture_nodes()` |
| Outcome node loading | `src/jig/intent_graph/generator.py:301` | `_load_outcome_nodes()` |
| Defines goal edges | `src/jig/intent_graph/generator.py:432` | `_create_defines_goal_edges()` |
| Supports goal edges | `src/jig/intent_graph/generator.py:455` | `_create_supports_goal_edges()` |
| Constrains edges | `src/jig/intent_graph/generator.py:492` | `_create_constrains_edges()` |
| Specifies edges | `src/jig/intent_graph/generator.py:514` | `_create_specifies_edges()` |
| V1 field usage (CLI) | `src/jig/cli/validate.py`, `src/jig/cli/show.py` | May need updates |

---

## Execution Order

```
WU1 (Validation Code) ──┬── WU3 (Bidirectional)
                        │
WU2 (Intent Graph) ─────┤
                        │
WU4 (Migration Script) ─┴── WU5 (Content Migration) ── WU6 (Test Files) ─┐
                                                                          │
WU7 (Spec Files) ────────────────────────────────────────────────────────┤
                                                                          │
                                                        WU8 (Validation) ─┴── WU9 (Context)
```

**Parallelizable:** WU1, WU2 can run in parallel. WU4 depends on WU1+WU2.
**Sequential:** WU5→WU6→WU7 must be sequential (content before tests before specs).
**Gate:** WU8 (Validation) must pass before WU9 (Finalize).

---

## Test Strategy

**New tests:**
- `tests/validation/test_intent.py` — bidirectional consistency tests
- `tests/integration/test_v2_schema.py` — V2 schema integration test

**Existing tests to update:**
- `tests/validation/test_intent.py` — field name assertions
- `tests/jig/intent_graph/test_generator.py` — node/edge field assertions
- `tests/cli/test_validate_integration.py` — validation output assertions
- `tests/cli/test_show.py` — show output assertions
- `tests/cli/test_rebuild.py` — rebuild output assertions
- `tests/cli/test_output_modes.py` — output format assertions
- `tests/cli/test_align.py` — align command assertions
- `tests/integration/test_intent_completeness.py` — completeness checks

**Deleted tests:** None (all tests updated, not deleted)

---

## Work Unit Checklist

- [x] WU1: Update Validation Code — tests ☑ / code ☑
- [x] WU2: Update Intent Graph Generator — tests ☑ / code ☑
- [x] WU3: Add Bidirectional Consistency Validation — tests ☑ / code ☑ / spec ☑
- [x] WU4: Create Migration Script — script ☑
- [ ] WU5: Execute Content Migration — charter ☐ / arch ☐ / outcomes ☐ / specs ☐
- [ ] WU6: Update Test Files — fixtures ☐ / assertions ☐
- [ ] WU7: Update Spec Files — field names ☐ / back-refs ☐
- [ ] WU8: Validation — SCOPE verified ☐
- [ ] WU9: Finalize Context — context updated ☐

---

## Work Units

### Work Unit 1: Update Validation Code

**Goal**: Update field names in validation logic to support V2 schema.

**Specs Addressed**: S-018, S-019, S-073, S-078, S-079, S-082

**Acceptance Criteria**:
- [ ] Charter validation: `defines_goals` → `goals`
- [ ] Architecture validation: `supports_goals` → `goals`, `constrains` → `specifications`
- [ ] Architecture validation: `status` field no longer required/validated
- [ ] Outcome validation: `supports_goals` → `goals`, `specifies` → `specifications`
- [ ] Specification validation: `outcomes` required (non-empty array)
- [ ] Specification validation: `architecture` required (non-empty array)
- [ ] Error messages reference new field names
- [ ] Code with @jig.implements decorators updated

**Success Gates** (all must pass):
- [ ] Unit tests updated and passing: `pytest tests/validation/test_intent.py -v`
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors: `ruff check src/jig/validation/`

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- FORBIDDEN brick modification needed
- Unclear which validation functions need changes

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| Charter validation function | `validate_charter_file()` | intent.py:788 |
| Architecture validation function | `validate_architecture_files()` | intent.py:1051 |
| Outcome validation function | `validate_outcome_files()` | intent.py:306 |
| Spec validation function | `validate_specification_files()` | intent.py:177 |
| V1 field patterns to find | `defines_goals`, `supports_goals`, `specifies`, `constrains`, `status` | grep confirmed |

**Implementation Notes**:
- File: `src/jig/validation/intent.py` (~1269 LOC)
- Key functions: `validate_charter_file()`, `validate_architecture_files()`, `validate_outcome_files()`, `validate_specification_files()`
- Search for: `defines_goals`, `supports_goals`, `specifies`, `constrains`, `status`
- Remove all `status` validation from architecture

**Human Verification**:
```bash
pytest tests/validation/test_intent.py -v
ruff check src/jig/validation/
```

---

### Work Unit 2: Update Intent Graph Generator

**Goal**: Update field names in graph generation to produce V2 schema nodes and edges.

**Specs Addressed**: S-028, S-084, S-085

**Acceptance Criteria**:
- [ ] Charter nodes: `defines_goals` → `goals`
- [ ] Architecture nodes: `supports_goals` → `goals`, `constrains` → `specifications`, no `status`
- [ ] Outcome nodes: `supports_goals` → `goals`, `specifies` → `specifications`
- [ ] Edge type: `constrains` → `specifications`
- [ ] Edge type `supports_goal` unchanged (describes relationship)
- [ ] Code with @jig.implements decorators updated

**Success Gates** (all must pass):
- [ ] Unit tests updated and passing: `pytest tests/jig/intent_graph/test_generator.py -v`
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors: `ruff check src/jig/intent_graph/`

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Edge type rename has unexpected downstream effects
- NDJSON format changes break other tools

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| Charter node loader | `_load_charter_node()` | generator.py:135 |
| Architecture node loader | `_load_architecture_nodes()` | generator.py:210 |
| Outcome node loader | `_load_outcome_nodes()` | generator.py:301 |
| Edge creators to update | `_create_defines_goal_edges()`, `_create_supports_goal_edges()`, `_create_constrains_edges()`, `_create_specifies_edges()` | generator.py:432-514 |

**Implementation Notes**:
- File: `src/jig/intent_graph/generator.py` (~676 LOC)
- Key functions: `_load_charter_node()`, `_load_architecture_nodes()`, `_load_outcome_nodes()`, `_create_*_edges()`
- Search for same field names as WU1
- Update NDJSON output format

**Human Verification**:
```bash
pytest tests/jig/intent_graph/test_generator.py -v
ruff check src/jig/intent_graph/
```

---

### Work Unit 3: Add Bidirectional Consistency Validation

**Goal**: Implement validation that spec back-refs match forward-refs from outcomes/architecture.

**Specs Addressed**: S-095 (NEW)

**Acceptance Criteria**:
- [ ] If O-001.specifications contains S-042, then S-042.outcomes must contain O-001
- [ ] If A-001.specifications contains S-072, then S-072.architecture must contain A-001
- [ ] Missing back-ref detected and reported as error
- [ ] Missing forward-ref detected and reported as error
- [ ] Error messages identify both sides of inconsistency
- [ ] @jig.implements("S-095") decorator on validation function
- [ ] @jig.verifies("S-095") decorator on tests

**Success Gates** (all must pass):
- [ ] New tests pass: `pytest tests/validation/test_intent.py -k bidirectional -v`
- [ ] jigy validate reports inconsistencies correctly
- [ ] No modifications to FORBIDDEN bricks

**Escalation Triggers** (stop and ask human if):
- Unclear how to handle partial consistency (one direction exists)
- Performance concerns with cross-referencing all specs

**Implementation Notes**:
- File: `src/jig/validation/intent.py` — add `validate_bidirectional_consistency()`
- Create spec file: `jig/specifications/S-095_Bidirectional_Reference_Consistency.md`
- Algorithm: Build forward index from O/A, build back index from S, compare

**Human Verification**:
```bash
pytest tests/validation/test_intent.py -k bidirectional -v
```

---

### Work Unit 4: Create Migration Script

**Goal**: Create script to transform all content files from V1 to V2 schema.

**Specs Addressed**: (tooling, no spec)

**Acceptance Criteria**:
- [ ] Script reads all Charter, Architecture, Outcome, Specification files
- [ ] Renames fields in frontmatter per V2 schema
- [ ] Removes `status` from Architecture frontmatter
- [ ] Computes back-refs for Specifications from forward-refs in Outcomes/Architecture
- [ ] Dry-run mode shows what would change without modifying files
- [ ] Script is idempotent (safe to run multiple times)

**Success Gates** (all must pass):
- [ ] Dry-run completes without error
- [ ] Script handles edge cases (missing fields, empty arrays)
- [ ] No data loss (all content preserved)

**Escalation Triggers** (stop and ask human if):
- Ambiguous forward-refs (spec referenced by outcome AND architecture with conflicts)
- Files with unexpected frontmatter structure
- YAML parsing errors

**Implementation Notes**:
- File: `scripts/migrate_v2_schema.py` (new)
- Use PyYAML for frontmatter parsing
- Preserve file content outside frontmatter exactly
- Log all changes for audit trail

**Human Verification**:
```bash
python scripts/migrate_v2_schema.py --dry-run
```

---

### Work Unit 5: Execute Content Migration

**Goal**: Run migration script on all 105 content files.

**Specs Addressed**: (migration, no spec)

**Acceptance Criteria**:
- [ ] Charter.md: `defines_goals` → `goals`
- [ ] 4 Architecture files: field renames, `status` removed
- [ ] 23 Outcome files: field renames
- [ ] 77 Specification files: `outcomes` and `architecture` back-refs added
- [ ] All files valid YAML after migration
- [ ] No content outside frontmatter modified

**Success Gates** (all must pass):
- [ ] Migration script completes without error
- [ ] Git diff shows only expected changes
- [ ] No frontmatter parsing errors

**Escalation Triggers** (stop and ask human if):
- Migration script fails on any file
- Unexpected changes to file content
- Back-ref computation produces empty arrays (orphaned specs)

**Implementation Notes**:
- Run: `python scripts/migrate_v2_schema.py`
- Review git diff carefully before proceeding
- Specs without outcomes/architecture refs need manual review

**Human Verification**:
```bash
python scripts/migrate_v2_schema.py
git diff --stat
git diff jig/Charter.md
git diff jig/architecture/
```

---

### Work Unit 6: Update Test Files

**Goal**: Update test files to use V2 field names in fixtures and assertions.

**Specs Addressed**: (test maintenance, no spec)

**Acceptance Criteria**:
- [ ] All inline fixtures use V2 field names
- [ ] All assertions check V2 field names
- [ ] No references to `defines_goals`, `supports_goals`, `specifies`, `constrains`
- [ ] No assertions expecting `status` in architecture

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/ -v`
- [ ] No test file references V1 field names
- [ ] No new linting errors

**Escalation Triggers** (stop and ask human if):
- Tests fail for reasons unrelated to field names
- Unclear what the test was originally verifying

**Implementation Notes**:
- Files (9 total):
  - `tests/validation/test_intent.py`
  - `tests/jig/intent_graph/test_generator.py`
  - `tests/config/test_cli_integration.py`
  - `tests/cli/test_validate_integration.py`
  - `tests/cli/test_show.py`
  - `tests/cli/test_rebuild.py`
  - `tests/cli/test_output_modes.py`
  - `tests/cli/test_align.py`
  - `tests/integration/test_intent_completeness.py`
- Search and replace field names in test assertions

**Human Verification**:
```bash
pytest tests/ -v
grep -r "supports_goals\|specifies\|defines_goals\|constrains" tests/
```

---

### Work Unit 7: Update Spec Files

**Goal**: Update specification markdown files to reflect V2 schema and add back-refs.

**Specs Addressed**: S-018, S-019, S-028, S-042, S-043, S-073, S-078, S-079, S-082, S-084, S-085

**Acceptance Criteria**:
- [ ] S-073: Title → "Charter Goals Field", content references `goals`
- [ ] S-078: Title → "Architecture Goals Required", content references `goals`
- [ ] S-079: Title → "Architecture Specifications References", content references `specifications`
- [ ] S-085: Title → "Specifications Edges", content references `specifications`
- [ ] All 11 specs: Examples updated to V2 schema
- [ ] All 11 specs: Frontmatter includes `outcomes` and `architecture` back-refs
- [ ] S-082: Remove `status` from required fields

**Success Gates** (all must pass):
- [ ] jigy validate passes (after all migration complete)
- [ ] Spec filenames match updated titles
- [ ] H1 headings match frontmatter titles

**Escalation Triggers** (stop and ask human if):
- Filename rename would break external links
- Spec content changes beyond field names needed

**Implementation Notes**:
- Rename files for changed titles:
  - `S-073_Charter_Defines_Goals_Field.md` → `S-073_Charter_Goals_Field.md`
  - `S-078_Architecture_Supports_Goals_Required.md` → `S-078_Architecture_Goals_Required.md`
  - `S-079_Architecture_Constrains_References.md` → `S-079_Architecture_Specifications_References.md`
  - `S-085_Constrains_Edges.md` → `S-085_Specifications_Edges.md`
- Update content to reference new field names
- Add `outcomes: [O-xxx]` and `architecture: [A-xxx]` to frontmatter

**Human Verification**:
```bash
ls jig/specifications/S-07*.md jig/specifications/S-085*.md
head -10 jig/specifications/S-073*.md
```

---

### Work Unit 8: Validation

**Goal**: Verify SCOPE problem is solved at system boundary.

**SCOPE Reference**:
"Align JIG implementation with the V2 schema defined in agents/contextJIG-2.md"

**Validation Approach**: Integration Test

**Verification Steps**:
```bash
# Full validation suite
source .venv/bin/activate
jigy rebuild
jigy validate
pytest tests/ -v

# Verify V2 schema in generated graph
head -20 jig/generated/intent-graph.ndjson

# Verify no V1 field names remain
grep -r "defines_goals\|supports_goals\|specifies\|constrains" jig/ --include="*.md" | grep -v "contextJIG-2"
```

**Expected Result**:
- jigy validate: 0 errors, 0 warnings
- All tests pass
- Generated graph uses V2 field names (`goals`, `specifications`)
- No V1 field names in any jig/ markdown files

**Deliverable**:
- [ ] Integration test added: `tests/integration/test_v2_schema.py`
- [ ] Test verifies field names in generated graph
- [ ] Test verifies bidirectional consistency

**If Validation Fails**:
- Investigate which files still have V1 fields
- Check migration script coverage
- Fix and re-run validation

---

### Work Unit 9: Finalize Context

**Goal**: Update agent context file to V2 schema documentation.

**Specs Addressed**: (documentation, no spec)

**Acceptance Criteria**:
- [ ] `agents/contextJIG.md` contains V2 schema documentation
- [ ] `agents/contextJIG-2.md` deleted (content merged into contextJIG.md)
- [ ] No references to V1 field names in context

**Success Gates** (all must pass):
- [ ] agents/contextJIG.md matches V2 schema
- [ ] agents/contextJIG-2.md removed
- [ ] jigy validate still passes

**Escalation Triggers** (stop and ask human if):
- Other files reference contextJIG-2.md
- Context changes affect agent behavior unexpectedly

**Implementation Notes**:
- Copy content from contextJIG-2.md to contextJIG.md
- Delete contextJIG-2.md
- Verify no broken references

**Human Verification**:
```bash
ls agents/context*.md
head -50 agents/contextJIG.md
```

---

## Fresh Agent Review Summary

Review performed: 2026-01-16

### Review Findings

| Category | Type | Issue | Resolution |
|----------|------|-------|------------|
| 4 (Location) | (A) Resolvable | Layer constraints wrong in original (said layer 1, actual is layer 0) | Fixed: B-validation, B-intent-graph now layer 0; B-cli layer 1 |
| 4 (Location) | (A) Resolvable | FORBIDDEN brick name wrong (B-verify-graph vs B-verification-graph) | Fixed brick name |
| 2 (Location) | (A) Resolvable | Validation function locations not specified | Added Key Existing Code References with line numbers |
| 2 (Location) | (A) Resolvable | Intent graph function locations not specified | Added to Key Existing Code References |
| 6 (Missing) | (A) Resolvable | No Execution Order section | Added dependency graph |
| 6 (Missing) | (A) Resolvable | No Test Strategy section | Added test strategy |
| 6 (Missing) | (A) Resolvable | No Resolved Context in WUs | Added to WU1, WU2 |

### Category (B) Issues Requiring Human Input

None identified.

### Exit Criteria

- [x] All (A) issues resolved via codebase exploration
- [x] All resolved context documented in PLAN
- [x] Key Existing Code References populated
- [x] PLAN is self-contained (executor needs no external context)

---

## Execution Log

(Filled in by orchestrator)

---

## Completion Summary

**Scope Delivered:**
- (to be filled)

**JIG Summary:**
- (to be filled)

**Clean Break Actions:**
- [ ] V1 field names rejected by validation
- [ ] No backwards compatibility shims
- [ ] Final jigy rebuild && jigy validate passed

**Reflection Roll-Up:**
- Repeatable wins: (to be filled)
- Systemic frictions: (to be filled)
- Open questions: (to be filled)

---

## Plan Validation Checklist

Before human approval:

- [x] All specs from JIGPLAN have at least one WU
- [x] WUs are properly sequenced (dependencies respected)
- [x] Each WU has single testable goal
- [x] FORBIDDEN bricks listed in constraints
- [x] **Validation WU included** (WU8 verifies SCOPE is solved)
- [x] Validation WU comes before Cleanup WU (WU9 is documentation, not cleanup)
- [x] Checklist matches WU list
- [x] **Fresh Agent Review completed**
- [x] All resolved context documented in WUs
- [x] Key Existing Code References populated
- [ ] Human approval pending
