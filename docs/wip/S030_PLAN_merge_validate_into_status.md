---
delta_type: plan
created: 2025-11-22
branch: merge-validate-status
status: draft
---

# PLAN: Merge `jigy validate` into `jigy status`

- **SCOPE:** docs/wip/S029_PROPOSAL_merge_validate_into_status.md
- **Start:** 2025-11-22
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** cli

## Overview

Simplify JIG's command interface by consolidating validation functionality into the status command. This reduces cognitive overhead, prepares for auto-rebuild, and provides a clearer user mental model: `jigy index rebuild` (build artifact) → `jigy status` (check artifact health + validate semantics).

**Clean Break:** This removes `jigy validate` completely (no deprecation period). JIG is a reference implementation - clean architecture > backward compatibility.

### Before vs After

| Before (3 commands) | After (2 commands) |
|---------------------|---------------------|
| `jigy index rebuild` | `jigy index rebuild` |
| `jigy status` (metrics only) | `jigy status` (metrics + validation) |
| `jigy validate` (validation only) | ~~deleted~~ |

**Migration:**
```bash
# Old CI pipeline
- run: jigy validate

# New CI pipeline
- run: jigy status
```

**Files Deleted:**
- `src/jig/cli/validate.py` (complete deletion)
- `tests/unit/test_validate.py` (complete deletion)
- `tests/integration/test_validate.py` (complete deletion)

**Protocol:** Following `agents/taskCleanBreak.md` - no feature flags, no deprecation warnings, no backward compatibility code.

## Known Intent (Created Before Coding)

### Outcomes Created

- **O-CLI-006:** "Developers understand graph health with single command"
  - Rationale: Status should be the one-stop command for "is my graph ready to commit?"
  - Success: Users run `jigy status` and know immediately if they can commit

- **O-CLI-007:** "CI pipelines use consistent validation strategy"
  - Rationale: One command for CI reduces configuration complexity
  - Success: All CI examples use `jigy status` without confusion

### Specifications Created

- **S-CLI-022:** "Status command validates graph semantics and shows health metrics"
  - Validates edge type rules (O→S, S→S, etc.)
  - Checks subsystem hierarchy (no cycles)
  - Detects self-loops
  - Reports quality warnings (orphans, unassigned)
  - Exits 1 on semantic errors, 0 on success

- **S-CLI-023:** "Status exit codes configurable via flags"
  - `--warn-only`: Always exit 0 (preview mode)
  - `--strict`: Exit 1 on errors OR warnings
  - `--quiet`: Suppress metrics, show only validation
  - Default: Exit 1 on errors, 0 on warnings

- **S-CLI-024:** "Validate command removed completely"
  - `validate.py` deleted entirely
  - `validate` subcommand removed from CLI
  - Clear error message if old docs reference validate
  - Migration: Use `jigy status` instead

- **S-CLI-025:** "Validation distinguishes structural vs semantic errors"
  - Index rebuild validates: parseability, ID format, required fields, reference existence
  - Status validates: edge semantics, subsystem cycles, self-loops, quality metrics
  - Clear separation of concerns documented

**Rationale:** These constraints are known from SCOPE and analysis. Creating them upfront enables O→S→TDD flow.

## Work Unit Checklist

- [x] WU0: Create known Intent nodes (O/S) — done ✓
- [ ] WU1: Extract validation core logic — tests ☐ / docs ☐ / reflect ☐
- [ ] WU2: Merge validation into status command — tests ☐ / docs ☐ / reflect ☐
- [ ] WU3: Add CLI flags for exit code control — tests ☐ / docs ☐ / reflect ☐
- [ ] WU4: Remove validate command completely — tests ☐ / docs ☐ / reflect ☐
- [ ] WU5: Update documentation — tests ☐ / docs ☐ / reflect ☐
- [ ] WU6: Add integration tests — tests ☐ / docs ☐ / reflect ☐

## Work Units

### Work Unit 0: Create Known Intent

**Goal:** Capture all known Outcomes and Specifications from SCOPE as Intent nodes before coding.

**Planned Effort:** 30-45 minutes

**Acceptance Criteria:**
- All known "why" statements → Outcome nodes in jig/outcomes/
- All known "what" requirements → Specification nodes in jig/specifications/
- All nodes have proper YAML frontmatter and markdown content
- `jigy status` shows new nodes (after index rebuild)

**Created Nodes:**
- O-CLI-006: Single command for graph health understanding
- O-CLI-007: Consistent CI validation strategy
- S-CLI-022: Status validates semantics and shows metrics
- S-CLI-023: Configurable exit codes via flags
- S-CLI-024: Validate command removed completely (clean break)
- S-CLI-025: Structural vs semantic validation separation

**Reflect:**
- What was clear from SCOPE: Command consolidation rationale, separation of structural/semantic validation
- What was ambiguous: Exact flag names (chose --warn-only, --strict, --quiet based on clarity)
- Decision made: Three flags instead of single --mode flag for better composability

**#DECISION "Clean break over gradual deprecation"**
- **Choice:** Complete deletion of validate command (no deprecation period)
- **Rationale:** JIG is a reference implementation demonstrating clean architecture principles. Technical debt from deprecation periods obscures the architectural clarity. Pre-1.0 software should prioritize pristine code over backward compatibility.
- **Tradeoffs:** Breaking change for existing users vs. cleaner codebase and simpler mental model
- **Migration path:** One-line change in scripts: `jigy validate` → `jigy status`

---

### Work Unit 1: Extract Validation Core Logic

**Goal:** Create reusable validation module that both status and validate can use, eliminating code duplication.

**Planned Effort:** 90-120 minutes

**Acceptance Criteria:**
- New module `src/jig/core/validation.py` created
- `ValidationResult` dataclass with errors, warnings, and check results
- `validate_graph_comprehensive()` function performs all semantic checks
- Helper functions: `validate_node_schema()`, `validate_edges()`, `validate_subsystem_hierarchy()`
- All validation logic extracted from existing `validate.py`
- Unit tests pass for validation functions
- Validation module is optimized for status command (no legacy CLI concerns)

**Implementation Notes:**
- Create `src/jig/core/validation.py`
- Define `ValidationResult` dataclass:
  ```python
  @dataclass
  class ValidationResult:
      errors: list[ValidationError]
      warnings: list[ValidationWarning]
      node_count: int
      edge_count: int
      checks_passed: dict[str, bool]
  ```
- Extract validation logic from `src/jig/cli/validate.py`:
  - Node schema validation (ID format, required fields, type validity)
  - Edge validation (target existence, type rules, no self-loops)
  - Subsystem hierarchy validation (no cycles)
  - Quality checks (orphans, unassigned nodes)
- Keep validation.py focused on pure validation logic (no CLI concerns)
- Files modified:
  - `src/jig/core/validation.py` (new)
  - `src/jig/cli/validate.py` (refactor to use validation.py)

**Test Plan:**
- Unit tests in `tests/unit/test_validation_core.py`:
  - `test_validate_node_schema_valid()` - Valid node passes
  - `test_validate_node_schema_invalid_id()` - Invalid ID format caught
  - `test_validate_node_schema_missing_field()` - Missing required field caught
  - `test_validate_edges_valid()` - Valid edges pass
  - `test_validate_edges_invalid_type()` - Invalid edge type caught (O→O)
  - `test_validate_edges_self_loop()` - Self-loop detected
  - `test_validate_subsystem_hierarchy_cycle()` - Cycle detected
  - `test_validation_result_aggregation()` - Errors and warnings collected correctly
- Integration test: Ensure `jigy validate` still works identically

**Docs to Update:**
- Add docstrings to all validation functions
- Document ValidationResult structure

**Reflect:**
- (To be filled after implementation)

---

### Work Unit 2: Merge Validation into Status Command

**Goal:** Integrate validation logic into status command so it shows metrics AND validates semantics.

**Planned Effort:** 60-90 minutes

**Acceptance Criteria:**
- `status_command()` calls `validate_graph_comprehensive()` after calculating metrics
- Status output includes "Validation Results" section
- Default behavior: Exit 0 if no errors, exit 1 if errors present
- Warnings don't affect exit code (exit 0)
- Status command shows structured validation output with ✓/✗ symbols
- All existing status metrics still displayed correctly
- Performance: Status + validation completes in <2s for typical graphs

**Implementation Notes:**
- Modify `src/jig/cli/status.py`:
  - Import `validate_graph_comprehensive` from `jig.core.validation`
  - After calculating status metrics, run validation
  - Format validation results with color-coded output
  - Determine exit code based on validation errors
- Add helper function `format_validation_output(result: ValidationResult) -> str`
- Structure output:
  ```
  JIG Graph Status
  
  ✓ 215 nodes, 183 edges, 7 subsystems
  [existing status output]
  
  Validation Results:
  
  ✓ Schema Checks
    ✓ All node IDs valid (215 nodes)
    ✓ No duplicate IDs
  
  ✓ Graph Consistency
    ✓ All edge targets exist (183 edges)
    ✓ No self-loops
  
  Warnings:
    ⚠ Orphaned nodes (3): O-TEST-002, S-AUTH-007
  
  ✅ Graph is valid
  ```
- Files modified:
  - `src/jig/cli/status.py`
  - `src/jig/cli/formatting.py` (add validation formatting helpers)

**Test Plan:**
- Unit tests in `tests/unit/test_status_command.py`:
  - `test_status_with_valid_graph()` - Valid graph shows success, exit 0
  - `test_status_with_errors()` - Errors shown, exit 1
  - `test_status_with_warnings_only()` - Warnings shown, exit 0
  - `test_status_validation_output_format()` - Check output structure
- Manual test:
  ```bash
  jigy status  # Should show metrics + validation
  echo $?      # Should be 0 for valid graph, 1 for errors
  ```

**Docs to Update:**
- Update docstring for `status_command()`
- Add comments explaining validation integration

**Reflect:**
- (To be filled after implementation)

---

### Work Unit 3: Add CLI Flags for Exit Code Control

**Goal:** Add `--warn-only`, `--strict`, and `--quiet` flags to status command for flexible exit code behavior.

**Planned Effort:** 60-90 minutes

**Acceptance Criteria:**
- `jigy status --warn-only` always exits 0 (even with errors)
- `jigy status --strict` exits 1 on errors OR warnings
- `jigy status --quiet` suppresses metrics, shows only validation results
- Default (no flags): Exit 1 on errors, 0 on warnings
- Flags work independently and in combination
- Help text clearly explains flag behavior
- All flag combinations tested

**Implementation Notes:**
- Modify `src/jig/cli/status.py`:
  - Add flags to `status_command()` signature: `warn_only=False, strict=False, quiet=False`
  - Update Click decorator:
    ```python
    @click.option('--warn-only', is_flag=True, help='Always exit 0 (show warnings but don\'t fail)')
    @click.option('--strict', is_flag=True, help='Exit 1 on errors OR warnings')
    @click.option('--quiet', is_flag=True, help='Only show validation results (suppress metrics)')
    ```
  - Implement exit code logic:
    ```python
    if warn_only:
        return 0
    if strict and (validation_result.errors or validation_result.warnings):
        return 1
    if validation_result.errors:
        return 1
    return 0
    ```
  - Conditional metrics display:
    ```python
    if not quiet:
        print(format_status_output(status_data, verbose, flat))
    ```
- Update help text to explain use cases
- Files modified:
  - `src/jig/cli/status.py`
  - `src/jig/cli/main.py` (update command help)

**Test Plan:**
- Unit tests in `tests/unit/test_status_flags.py`:
  - `test_warn_only_always_exits_zero()` - Even with errors
  - `test_strict_fails_on_warnings()` - Warnings cause exit 1
  - `test_strict_fails_on_errors()` - Errors cause exit 1
  - `test_quiet_suppresses_metrics()` - Only validation shown
  - `test_quiet_with_strict()` - Flags compose correctly
  - `test_default_behavior()` - Errors fail, warnings don't
- Manual tests:
  ```bash
  # Valid graph
  jigy status && echo "PASS"           # Should print PASS
  jigy status --strict && echo "PASS"  # Should print PASS
  
  # Graph with warnings
  jigy status && echo "PASS"           # Should print PASS (warnings ok)
  jigy status --strict || echo "FAIL"  # Should print FAIL (strict mode)
  
  # Graph with errors
  jigy status || echo "FAIL"           # Should print FAIL
  jigy status --warn-only && echo "PASS"  # Should print PASS (override)
  
  # Quiet mode
  jigy status --quiet | grep "Node Summary"  # Should not match
  jigy status --quiet | grep "Validation"    # Should match
  ```

**Docs to Update:**
- Update `jigy status --help` text
- Add examples to help text

**Reflect:**
- (To be filled after implementation)

---

### Work Unit 4: Remove Validate Command Completely

**Goal:** Delete `jigy validate` completely. Clean break - no deprecation, no backward compatibility.

**Planned Effort:** 30-45 minutes

**Acceptance Criteria:**
- `src/jig/cli/validate.py` deleted entirely
- `validate` subcommand removed from `main.py`
- `tests/unit/test_validate.py` deleted entirely
- `tests/integration/test_validate.py` deleted entirely
- `jigy validate` produces clear error: "Unknown command 'validate'. Did you mean 'status'?"
- No validate references in core code
- `jigy --help` does not show validate command

**Implementation Notes:**
- **Delete files completely:**
  ```bash
  rm src/jig/cli/validate.py
  rm tests/unit/test_validate.py
  rm tests/integration/test_validate.py
  ```
- **Remove from main.py:**
  ```python
  # DELETE this entire block:
  # @cli.command()
  # def validate(...):
  #     ...
  ```
- **NO deprecation warnings** - Command simply doesn't exist
- **NO backward compatibility** - Users update their workflows
- **NO feature flags** - Clean deletion only

**#DECISION "Burn ships: Complete removal of validate command"**
- **Choice:** Delete validate.py entirely, no deprecation period
- **Rationale:** JIG is a reference implementation demonstrating clean architecture. Deprecation periods create technical debt and dual implementations that obscure the architectural clarity we're demonstrating.
- **Tradeoffs:** 
  - Breaking change for users with `jigy validate` in scripts
  - No gradual migration path
  - Users must update immediately
- **Why acceptable:**
  - JIG is pre-1.0 (breaking changes expected)
  - Migration is trivial: `validate` → `status`
  - Clean codebase demonstrates architectural principles better
  - Reference implementation should be pristine, not backward-compatible

**#LEARNED "Clean breaks reduce cognitive load"**
- Maintaining dual implementations adds ~40% code complexity
- Deprecation warnings pollute user output for months
- Clear break forces clean migration, then clean code

**Test Plan:**
- Manual verification:
  ```bash
  # Should fail with clear error
  jigy validate
  # Error: No such command 'validate'.
  # Did you mean 'status'? Try: jigy status
  
  # Verify validate not in help
  jigy --help | grep validate  # Should return nothing
  ```
- No unit tests needed (command doesn't exist)
- CLI help system provides "did you mean?" suggestion automatically (Click feature)

**Docs to Update:**
- Remove all validate documentation
- Update migration guide to explain the clean break
- Add note in README about breaking change

**Reflect:**
- (To be filled after implementation)

---

### Work Unit 5: Update Documentation

**Goal:** Update all documentation to reflect new command structure. Remove all validate references completely.

**Planned Effort:** 60-90 minutes

**Acceptance Criteria:**
- README.md updated with new workflow (rebuild → status)
- User guide updated with status flags and examples
- CI integration guide simplified to use `jigy status`
- Breaking change documented clearly
- All code examples updated
- Tutorial workflow updated
- ZERO references to `jigy validate` remain (except in git history)

**Implementation Notes:**
- Update `README.md`:
  - Quick start section: rebuild → status (two commands only)
  - Remove validate entirely from workflow
  - Add status flags to examples
  - Add note about breaking change if pre-existing users
- Create `docs/user-guide/BREAKING_CHANGES.md`:
  - Document the validate → status migration
  - Simple table: `jigy validate` → `jigy status`
  - No deprecation timeline (clean break)
  - Explain rationale (reference implementation, clean architecture)
- Update `docs/tutorials/basic-workflow.md`:
  - Two-command workflow: rebuild, status
  - Explain status validation
  - Show flag usage
- Create/update `docs/user-guide/commands.md`:
  - Full status command reference
  - Document all flags with examples
  - Explain exit code behavior
  - Show validation output format
- **Delete any existing validate documentation completely**
- Files modified:
  - `README.md`
  - `docs/user-guide/BREAKING_CHANGES.md` (new)
  - `docs/user-guide/commands.md` (new or update)
  - `docs/tutorials/basic-workflow.md`
  - `docs/tutorials/ci-integration.md` (if exists)
  - Delete: Any old validate-specific documentation

**Test Plan:**
- Manual review: Read all docs end-to-end
- Verify all examples are runnable
- Grep to ensure ZERO validate references remain:
  ```bash
  grep -r "jigy validate" docs/
  # Should return NOTHING (except maybe BREAKING_CHANGES.md showing migration)
  
  grep -r "validate command" docs/
  # Should only appear in breaking changes doc
  ```

**#DECISION "Document breaking change clearly, no apology"**
- JIG is a reference implementation (pre-1.0)
- Clean architecture demonstration > backward compatibility
- Users expect breaking changes in reference implementations
- Clear migration path: one-line change in scripts

**Docs to Update:**
- (This IS the docs work unit)

**Reflect:**
- (To be filled after implementation)

---

### Work Unit 6: Add Integration Tests

**Goal:** Add end-to-end integration tests that verify complete workflows with new unified command.

**Planned Effort:** 60-90 minutes

**Acceptance Criteria:**
- CI workflow test: rebuild → status → commit pipeline
- Error workflow test: Status fails on semantic errors
- Warning workflow test: Status succeeds with warnings
- Flag combination tests: All flag permutations tested
- Performance test: Status + validation <2s for real JIG graph
- All tests pass in CI
- NO backward compatibility tests (validate doesn't exist)

**Implementation Notes:**
- Create `tests/integration/test_status_validation_integration.py`:
  - `test_developer_workflow_happy_path()` - Full workflow succeeds
  - `test_developer_workflow_with_errors()` - Errors caught, workflow stops
  - `test_ci_pipeline_simulation()` - Simulates CI validation
  - `test_status_after_rebuild()` - Rebuild then status
  - `test_warn_only_for_ci_preview()` - CI preview mode
  - `test_strict_mode_for_quality_gate()` - High-quality enforcement
  - `test_quiet_mode_validation_only()` - Quiet mode for focused validation
  - `test_status_performance()` - Performance benchmark (<2s)
- **NO backward compatibility tests** - validate command doesn't exist
- Add performance benchmark:
  ```python
  def test_status_performance():
      """Status + validation must complete in <2s on real JIG graph."""
      start = time.time()
      result = runner.invoke(cli, ['status'])
      elapsed = time.time() - start
      assert elapsed < 2.0, f"Status took {elapsed}s (should be <2s)"
      assert result.exit_code == 0
  ```
- Files created:
  - `tests/integration/test_status_validation_integration.py` (new)
- Files deleted:
  - Any existing `test_validate*.py` files

**Test Plan:**
- Run all integration tests locally:
  ```bash
  pytest tests/integration/test_status_validation_integration.py -v
  ```
- Run in CI to ensure no environment-specific failures
- Verify tests catch regressions (intentionally break something, tests should fail)
- Verify old validate tests are gone:
  ```bash
  find tests/ -name "*validate*"  # Should return nothing
  ```

**#LEARNED "Test the new way, not backward compatibility"**
- Writing tests for dual implementations wastes time
- Test what actually runs, not what used to run
- If you need old behavior, check git history

**Docs to Update:**
- Add test documentation to CONTRIBUTING.md
- Document integration test patterns

**Reflect:**
- (To be filled after implementation)

---

## Completion Summary

### Summary
- (To be filled upon completion)

### Metrics
- Units: 6 (excluding WU0)
- Estimated total effort: 6-9 hours (reduced from 8-11h due to clean break)
- Median cycle time: (to be measured)
- Rework rate: (to be measured)
- Test coverage: (to be measured)
- Markers captured: (to be counted)
- Files deleted: 3+ (validate.py, test files)

### Reflection Roll-up
- Repeatable wins: (to be filled)
- Systemic frictions: (to be filled)
- Process changes adopted: (to be filled)

### Harvest Preparation (JIG)

**Markers Summary:**
- Discoveries: (to be counted)
- Decisions: (to be counted)
- Learned patterns: (to be counted)

**Recommended OSTC Nodes (from DISCOVERIES only):**
- (To be filled based on discoveries during implementation)
- Expected: Most constraints were known upfront (captured in WU0)
- Possible discoveries: Edge cases in validation, performance gotchas, UX insights

**Architectural Changes (Clean Break):**
- Burned ships: Removed `jigy validate` command entirely (no deprecation)
- Breaking change: Users must update scripts (`validate` → `status`)
- Files deleted: `src/jig/cli/validate.py`, all validate tests
- Rationale: Reference implementation prioritizes clean architecture over backward compatibility
- Migration: Zero-cost for users (one-line script change)

**Subsystems Touched:** cli (primary), core (validation module)

**Next Step:** `jig ai-distill --branch merge-validate-status`

---

## Risk Register

### High Priority Risks

**Risk 1: User scripts break immediately**
- **Impact:** Users with `jigy validate` in scripts get command errors
- **Mitigation:** 
  - Document breaking change prominently in README
  - Provide clear migration path (one-line fix)
  - JIG is pre-1.0 (breaking changes expected)
  - Migration is trivial: `validate` → `status`
- **Acceptance:** This is a feature, not a bug - forces clean migration

**Risk 2: CI pipelines break**
- **Impact:** CI jobs fail with "unknown command" error
- **Mitigation:**
  - Breaking change documented in BREAKING_CHANGES.md
  - Fix is one line: `jigy validate` → `jigy status`
  - Click provides helpful error: "Did you mean 'status'?"
  - Better to fail loudly than silently degrade

**Risk 3: Performance regression**
- **Impact:** Slow status command frustrates users
- **Mitigation:**
  - Benchmark before/after
  - Validation should add <100ms overhead
  - Graph already loaded for status, minimal extra cost
  - Add performance test in WU6 (<2s target)
  - Clean break allows optimization without legacy constraints

**Risk 4: Exit code confusion**
- **Impact:** Users don't understand when status fails
- **Mitigation:**
  - Clear documentation of exit code behavior
  - Verbose output explains why it failed
  - Examples in help text
  - Flags provide escape hatches (--warn-only, --strict)

### Medium Priority Risks

**Risk 5: Incomplete validation coverage**
- **Impact:** Some errors not caught by status
- **Mitigation:**
  - Extract ALL validation logic from validate.py in WU1
  - Comprehensive test coverage in WU6
  - Review S023 analysis for validation completeness
  - Clean break: No legacy edge cases to handle

**Risk 6: Flag naming confusion**
- **Impact:** Users don't understand flag purpose
- **Mitigation:**
  - Clear help text with use case examples
  - Document in user guide with scenarios
  - Choose intuitive names (--warn-only, --strict, --quiet)

### Benefits of Clean Break (Risk Mitigation)

**Why this is LESS risky than gradual deprecation:**
1. **No dual implementations** - One code path, simpler testing
2. **No deprecation noise** - Users don't see warnings for months
3. **Forces clean migration** - Users update scripts once, done
4. **Clearer mental model** - Two commands, not three (or 2.5 during transition)
5. **Faster iteration** - No compatibility constraints on future changes

---

## Dependencies

### External Dependencies
- None (pure refactoring of existing code)

### Internal Dependencies
- Requires working `jigy status` command (exists)
- Requires working `jigy validate` command (exists)
- Requires `Graph.load_from_dir()` (exists)

### Blocking Items
- None

---

## Testing Strategy

### Unit Test Coverage (per Work Unit)
- WU1: Validation core logic (100% coverage target)
- WU2: Status command integration (all paths tested)
- WU3: Flag behavior (all combinations)
- WU4: Complete removal of validate command (verification only)
- WU6: End-to-end workflows

### Integration Test Coverage
- Full developer workflow
- CI pipeline simulation
- Flag combinations and exit codes
- Performance benchmarks

### Manual Testing Checklist
- [ ] Run `jigy status` on valid graph → Exit 0, shows success
- [ ] Run `jigy status` on graph with errors → Exit 1, shows errors
- [ ] Run `jigy status` on graph with warnings → Exit 0, shows warnings
- [ ] Run `jigy status --strict` with warnings → Exit 1
- [ ] Run `jigy status --warn-only` with errors → Exit 0
- [ ] Run `jigy status --quiet` → Only validation output
- [ ] Run `jigy validate` → Command not found, suggests "status"
- [ ] Run `jigy --help` → validate not listed
- [ ] Run `jigy index rebuild` then `jigy status` → Full workflow
- [ ] Check performance: `time jigy status` → <2s

---

## Human Validation

After completing all work units, run these commands to verify the implementation:

```bash
# 1. Validate graph structure
jigy status
echo "Exit code: $?"

# 2. Test flags
jigy status --quiet
jigy status --warn-only
jigy status --strict

# 3. Verify validate is gone
jigy validate
# Should error: "No such command 'validate'. Did you mean 'status'?"

jigy --help | grep validate
# Should return nothing (command removed)

# 4. Full workflow
jigy index rebuild
jigy status
# Should show metrics + validation, exit 0 if valid

# 5. Run all tests
pytest tests/unit/test_validation_core.py -v
pytest tests/unit/test_status_command.py -v
pytest tests/unit/test_status_flags.py -v
pytest tests/integration/test_status_validation_integration.py -v

# 6. Check performance
time jigy status  # Should be <2s

# 7. Look for alignment violations
jigy status | grep "✗"  # Should be none on valid graph

# 8. Verify no validate tests remain
find tests/ -name "*validate*"  # Should return nothing

# 9. Verify no validate code remains
find src/ -name "*validate*"  # Should return nothing
```

---

## Clean Break Execution Checklist

Following taskCleanBreak.md protocol:

- [ ] Document decision in Delta with `#DECISION` marker (done in WU4)
- [ ] Delete `src/jig/cli/validate.py` completely (WU4)
- [ ] Delete all validate tests completely (WU4)
- [ ] Remove validate subcommand from `main.py` (WU4)
- [ ] Update `jig/graph-index.json` if validate had annotations (WU4)
- [ ] Run `jigy status` after deletion to verify no broken references (WU4)
- [ ] Update documentation with breaking change notice (WU5)
- [ ] NO feature flags, NO deprecation warnings, NO backward compat (all WUs)
- [ ] Commit with clear message: `refactor(cli): burn ships - remove validate command` (WU4)
- [ ] Update Harvest Preparation with `#LEARNED` about clean breaks (Completion)

---

**Document Status:** Draft  
**Ready for Execution:** After WU0 (Intent node creation)  
**Protocol:** Clean Break (per taskCleanBreak.md)  

**Next Steps:**
1. Create O-CLI-006, O-CLI-007, S-CLI-022, S-CLI-023, S-CLI-024, S-CLI-025
2. Commit Intent nodes
3. Begin WU1 (Extract validation core logic)
4. Execute WU4 with complete deletion (no deprecation)

**Related Documents:**
- docs/wip/S029_PROPOSAL_merge_validate_into_status.md (SCOPE)
- docs/wip/S023_EVALUATION_command_overlap_analysis.md (Analysis)
- docs/wip/S022_PLAN_validate_consistency.md (Related work)
- agents/taskCleanBreak.md (Protocol used)

