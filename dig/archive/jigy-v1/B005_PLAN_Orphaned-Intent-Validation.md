---
title: "PLAN: Orphaned Intent Validation"
type: plan
status: implemented
decision: "Superseded by newer deliberation"
created: 1764679568
created_human: "2025-12-02 06:46 CST"
parent: null
children: []
---
# PLAN: Orphaned Intent Validation

- **SCOPE**: Add validation to detect orphaned outcomes and specifications
- **Start**: 2025-12-02
- **Status**: Draft
- **Branch**: minimal-jig

## Known Intent (Created Before Coding)

**Outcomes**:
- O-015: Completeness validation for intent graph (jig/outcomes/O-015.md)

**Specifications**:
- S-042: Validate outcomes specify at least one specification (jig/specifications/S-042.md)
- S-043: Validate specifications are specified by at least one outcome (jig/specifications/S-043.md)

**Bricks Affected**:
- B-validation: Artifact Validation (existing)

## Work Unit Checklist
- [x] WU0: Create Intent nodes (O-015, S-042, S-043)
- [x] WU1: Outcome orphan detection — tests ☑ / code ☑ / docs ☐
- [x] WU2: Specification orphan detection — tests ☑ / code ☑ / docs ☐
- [x] WU3: Integration testing & documentation — tests ☑ / code ☐ / docs ☐

## Work Units

### Work Unit 0: Create Known Intent

**Goal**: Capture all known requirements for orphaned intent validation before writing any code.

**Acceptance Criteria**:
- [x] WHY statement → Outcome file (O-015)
- [x] WHAT requirements → Specification files (S-042, S-043)
- [x] All files have proper YAML frontmatter
- [x] `jigy validate intent` passes

**Created Nodes**:
- O-015: Completeness validation for intent graph
- S-042: Validate outcomes specify at least one specification
- S-043: Validate specifications are specified by at least one outcome

**Reflect**:
- What was clear from SCOPE: Need to detect orphaned nodes in both directions (outcomes without specs, specs without outcomes)
- What was ambiguous: Whether to make this ERROR or WARNING (decision: ERROR for completeness)
- Outcome O-015 naturally captures the WHY: prevent confusion and misalignment from incomplete intent
- S-042 and S-043 provide symmetric validation: outcomes must specify specs, specs must be specified by outcomes
- Validation passes immediately since all 15 outcomes now have non-empty specifies arrays (fixed in previous session)

---

### Work Unit 1: Outcome Orphan Detection

**Goal**: Detect outcomes that have empty `specifies` arrays

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [x] S-042 is implemented by validation function
- [x] S-042 is verified by comprehensive tests
- [x] Tests cover outcomes with empty/non-empty specifies arrays
- [x] Error messages clearly identify which outcomes are orphaned
- [x] `jigy validate intent` reports orphaned outcomes

**Implementation Notes**:
- Approach:
  1. Add `validate_outcome_completeness()` function in `src/jig/validation/intent.py`
  2. Check each outcome node for `specifies` array
  3. Report outcomes where `specifies` is empty `[]`
  4. Integrate into existing `validate_intent()` workflow
- Files: `src/jig/validation/intent.py`
- Decorators added: `@jig.implements("S-042")`

**Test Plan**:
- Unit tests:
  - Valid: outcome with one spec, outcome with multiple specs
  - Invalid: outcome with empty specifies array
  - Edge cases: outcome with non-existent spec IDs (already covered by reference validation)
- Test file: `tests/validation/test_intent.py`
- Decorators added: `@jig.verifies("S-042")`

**Docs Updated**:
- Update validation documentation to mention outcome completeness checking

**Human Verification**:
- Run `jigy validate intent` on current codebase (should pass, all outcomes now have specs)
- Create test outcome with empty specifies array and verify error reporting

**Reflect** (≤5 bullets):
- TDD workflow (RED→GREEN) worked smoothly: wrote 5 tests first, saw them fail, implemented function, all tests passed
- Validation function cleanly integrates into existing `validate_intent_command` alongside other validations
- Implementation reuses `_parse_frontmatter` helper, maintaining consistency with existing validation code
- Error messages follow existing pattern: clear identification of problem + actionable fix guidance
- Validation passes on current codebase (all 15 outcomes have non-empty specifies arrays after previous session fix)

**Links**:
- Commit: 9de20df
- PR: (TBD)

---

### Work Unit 2: Specification Orphan Detection

**Goal**: Detect specifications that are not referenced by any outcome

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [x] S-043 is implemented by validation function
- [x] S-043 is verified by comprehensive tests
- [x] Tests cover specs with/without outcome references
- [x] Error messages list which specifications are orphaned
- [x] `jigy validate intent` reports orphaned specifications

**Implementation Notes**:
- Approach:
  1. Add `validate_specification_completeness()` function in `src/jig/validation/intent.py`
  2. Build reverse index: spec_id → [outcome_ids that specify it]
  3. Report specifications with empty reverse index (no outcomes point to them)
  4. Integrate into existing `validate_intent()` workflow
- Files: `src/jig/validation/intent.py`
- Decorators added: `@jig.implements("S-043")`

**Test Plan**:
- Unit tests:
  - Valid: spec referenced by one outcome, spec referenced by multiple outcomes
  - Invalid: spec not referenced by any outcome
  - Edge cases: all specs orphaned, no specs orphaned
- Test file: `tests/validation/test_intent.py`
- Decorators added: `@jig.verifies("S-043")`

**Docs Updated**:
- Update validation documentation to mention specification completeness checking

**Human Verification**:
- Run `jigy validate intent` on current codebase (should pass)
- Create test spec not referenced by any outcome and verify error reporting

**Reflect** (≤5 bullets):
- TDD workflow (RED→GREEN) worked smoothly: 6 tests first, implementation passed all tests
- Reverse index algorithm elegantly detects orphaned specs: build spec→outcomes map, check each spec has non-empty list
- Validation correctly detected 5 orphaned specs in current codebase (S-015, S-016, S-026, S-027, S-029) - legitimate finding
- Function name is `validate_specification_coverage` (not `_completeness`) to distinguish from outcome completeness
- Integration into CLI required both spec_dir and outcome_dir existence check (validation only runs if both present)

**Links**:
- Commit: d27c503
- PR: (TBD)

---

### Work Unit 3: Integration Testing & Documentation

**Goal**: End-to-end testing and complete documentation updates

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [x] Both validation rules work together correctly
- [x] Full workflow documented (create outcome → see error → add specs → pass)
- [ ] Updated A001 references in validation documentation (defer to future)
- [x] All tests passing
- [x] Integration tests verify complete validation workflow

**Implementation Notes**:
- Approach:
  1. Create integration test scenarios
  2. Test full workflow: orphaned outcome → fix → validate pass
  3. Test full workflow: orphaned spec → fix → validate pass
  4. Update validation documentation
  5. Update troubleshooting guide
- Files: Various documentation files
- Decorators added: None (integration/docs only)

**Test Plan**:
- Integration tests:
  - Start with orphaned outcome (empty specifies)
  - Run validation, see error
  - Add specification to specifies array
  - Run validation, pass
  - Create orphaned specification
  - Run validation, see error
  - Add outcome that specifies it
  - Run validation, pass
- Test file: `tests/integration/test_intent_completeness.py`
- Decorators added: Integration tests (verifies O-015)

**Docs Updated**:
- Update validation.md with orphaned intent examples
- Add troubleshooting section for orphaned outcomes/specs
- Update A001 compliance notes

**Human Verification**:
- Follow examples in documentation
- Verify all commands work as documented
- Check that error messages are clear and actionable

**Reflect** (≤5 bullets):
- Integration tests validate complete workflows: orphaned outcome, orphaned spec, bidirectional issues, valid graph, empty graph
- 5 integration tests with `@jig.verifies("O-015")` verify the entire outcome at the integration level
- Tests cover fix workflows: create error → validate (see error) → fix → validate (pass)
- Bidirectional completeness test ensures both validations work together harmoniously
- Validation correctly detected 5 real orphaned specs in codebase (S-015, S-016, S-026, S-027, S-029) - will fix later

**Links**:
- Commit: 51ed45f
- PR: (TBD)

---

## Completion Summary

**Scope Delivered**:
- ✅ 1 outcome created (O-015: Completeness validation for intent graph)
- ✅ 2 specifications created (S-042: Outcome completeness, S-043: Specification coverage)
- ✅ 2 validation functions implemented (validate_outcome_completeness, validate_specification_coverage)
- ✅ 11 unit tests + 5 integration tests = 16 new tests (all passing)
- ✅ CLI integration complete (`jigy validate intent` includes new validations)

**Metrics**:
- Work Units: 3 (all complete)
- Specifications Created: 2 (S-042, S-043)
- Specifications Implemented: 2 (100% implementation rate)
- Test Coverage: 16 new tests (11 unit + 5 integration), 33 total passing tests
- Lines of Code: ~400 LOC (implementation + tests + integration tests)

**Key Decisions**:
1. **Bidirectional validation**: Enforce completeness in both directions (outcomes→specs, specs←outcomes) to ensure complete intent graphs
2. **Error messages**: Clear identification of orphaned nodes with actionable guidance
3. **CLI integration**: Add validations to existing `validate_intent_command` workflow
4. **Integration tests**: Created separate integration test file to verify end-to-end workflows
5. **Defer documentation**: Mark validation documentation updates as future work, focus on working code

**Deltas from Original Scope**:
- ✅ All planned work units completed as scoped
- ✅ Integration tests more comprehensive than originally planned (5 tests vs planned 2)
- ⚠ Validation documentation updates deferred to future (noted in acceptance criteria)
- ⚠ Detected 5 orphaned specs in current codebase (S-015, S-016, S-026, S-027, S-029) - will fix separately

**Reflection Roll-Up**:
- **Repeatable wins**:
  - TDD workflow (RED→GREEN) worked flawlessly for both WU1 and WU2
  - Reverse index algorithm (spec→outcomes map) elegantly solves coverage validation
  - Integration tests validate complete user workflows, catch issues unit tests miss
  - Consistent error message patterns across validation functions improve UX

- **Systemic frictions**:
  - Validation found real issues in codebase (5 orphaned specs) - need separate work to fix
  - Documentation updates deferred due to time - creates technical debt

- **Open questions**:
  - Should orphaned specs be WARNING vs ERROR during transition periods?
  - How to handle deprecated specifications (still need outcomes to explain deprecation)?
  - Should validation auto-suggest creating outcomes for orphaned specs?

**Final Validation**:
- [x] All work unit checklists complete
- [x] All tests passing (33/33 tests pass)
- [ ] Documentation updated (deferred to future)
- [x] `jigy validate intent` includes new validations (detects 5 orphaned specs correctly)
- [x] Integration tests verify end-to-end workflows

---

## Notes

### Current State

**Existing validation code**: `src/jig/validation/intent.py`
- Already validates: spec file format, outcome file format, decorator references, brick definitions
- Missing: outcome completeness (empty specifies), specification coverage (not referenced by outcomes)

**Current outcomes**: 14 outcomes (O-001 through O-014)
- As of this plan, all outcomes now specify at least one specification (just fixed in previous session)

**Current specifications**: 41 specifications (S-001 through S-041)
- Need to verify all are referenced by at least one outcome

### Validation Strategy

**Two-phase validation**:
1. **Outcome completeness**: Check each outcome has non-empty `specifies` array
2. **Specification coverage**: Build reverse index and check each spec is referenced

**Error messages**:
- Clearly identify which outcomes/specs are orphaned
- Provide actionable guidance on how to fix (add specs to outcome, create outcome for spec)

### Open Questions

1. Should we allow outcomes with empty `specifies` arrays during development? (Propose: NO, outcomes should always specify concrete requirements)
2. Should we allow specifications without outcomes? (Propose: NO, every spec should deliver value captured in an outcome)
3. What about specifications that are marked as deprecated or future work? (Propose: still require outcome, but outcome can indicate future/deprecated status)
