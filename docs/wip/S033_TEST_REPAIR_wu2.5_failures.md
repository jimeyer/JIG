# S033: Test Repair Report - WU2.5 Test Suite Recovery

**Created:** 2025-11-22
**Type:** Test Repair Analysis
**Branch:** dev
**Methodology:** taskTestRepair.md v2.0.0 (5-Bucket Model)

---

## Executive Summary

**Baseline State:**
- Total tests: 455
- Passing: 399 (87.7%)
- Failing: 56 (12.3%)
- Test run time: 2.46s

**Root Cause:** Integration tests are failing because CLI commands now validate project initialization (exit code 3) when intent directory doesn't exist. The tests mock `load_config()` but don't create the actual directories that `Graph.load_from_dir()` expects.

**Classification:** All 56 failures fall into **Bucket A** (Align - SPEC valid, test needs fixing).

**Strategy:** **FIX** - Mechanical change to ensure test fixtures create required directories before running CLI commands.

---

## Phase 0: Baseline Analysis

### Test Execution Summary
```bash
source .venv/bin/activate && python -m pytest --tb=no -q
# Result: 56 failed, 399 passed in 2.46s
```

### Failure Breakdown by Test File

| Test File | Failed | Total | Failure Rate |
|-----------|--------|-------|--------------|
| test_command_consistency.py | 1 | 3 | 33% |
| test_decompose_commands.py | 8 | 8 | 100% |
| test_graph_deps.py | 8 | 8 | 100% |
| test_graph_path_list.py | 13 | 13 | 100% |
| test_graph_show.py | 5 | 6 | 83% |
| test_nested_status.py | 7 | 7 | 100% |
| test_status_command.py | 5 | 7 | 71% |
| test_validate_command.py | 9 | 14 | 64% |

### Common Error Pattern
```
assert result.exit_code == 0
E   assert 3 == 0
E    +  where 3 = <Result SystemExit(3)>.exit_code
```

Exit code 3 = "Intent directory not found" (project not initialized)

---

## Phase 1: SPEC Audit

### Bucket Classification

#### Bucket A: Existing SPEC - Align Test (56 tests)
All 56 failing tests verify valid SPECs but need alignment with new initialization check.

| Test Category | Count | Verifies SPEC | Root Cause |
|--------------|-------|---------------|------------|
| decompose commands | 8 | S-NESTED-004 | Missing intent directory in temp fixture |
| graph deps/impact | 8 | S-GRAPH-003 | Missing intent directory in temp fixture |
| graph path/list | 13 | S-GRAPH-003 | Missing intent directory in temp fixture |
| graph show | 5 | S-GRAPH-003 | Missing intent directory in temp fixture |
| nested status | 7 | S-NESTED-001, S-NESTED-002 | Missing intent directory in temp fixture |
| status command | 5 | S-CLI-001 | Missing intent directory in temp fixture |
| validate command | 9 | S-JIG-003 | Missing intent directory in temp fixture |
| command consistency | 1 | S-CLI-001 | Different issue: subsystem hierarchy validation changed |

**Total Bucket A:** 56 tests

#### Bucket B: Missing SPEC (0 tests)
No tests found that verify missing SPECs.

#### Bucket C: Obsolete SPEC - Delete Test (0 tests)
No obsolete tests found. All tests verify current, valid SPECs.

#### Bucket D: CODE Missing - TDD Scenario (0 tests)
No tests skipped due to missing CODE implementation.

#### Bucket E: CODE Bug Detected (0 tests)
No CODE bugs detected during test audit.

---

## Phase 2: Create Missing SPECs

**Status:** SKIPPED - No Bucket B tests identified.

All failing tests already have valid SPEC coverage:
- S-GRAPH-003: Graph query and navigation commands
- S-NESTED-001: Nested subsystem hierarchy
- S-NESTED-002: Flat subsystem view
- S-NESTED-004: Decompose metrics for nested subsystems
- S-CLI-001: CLI command behavior
- S-JIG-003: Validation rules

---

## Phase 3: Root Cause Grouping

### Group 1: Missing Intent Directory (55 tests) - FIX

**Root Cause:** CLI commands now check if `config.intent_dir` exists via `Graph.load_from_dir()`, raising `FileNotFoundError` and returning exit code 3 if not found.

**Why This Changed:**
- Previous implementation: `load_config()` returned default config, commands proceeded without checking if directories exist
- Current implementation: Commands call `Graph.load_from_dir(config.intent_dir)` which validates directory existence
- Exit code 3 convention added for "project not initialized" (per S005_PLAN_phase_1_intent_graph.md)

**Test Issue:** Tests mock `load_config()` to return a config pointing to temp directories, but don't actually create those directories before invoking CLI commands.

**Strategy:** **FIX** (mechanical change)
- Add `config.intent_dir.mkdir(parents=True, exist_ok=True)` after mocking config
- Optionally create subdirectories: outcomes/, specifications/, constraints/
- Result: Tests will pass with no semantic changes

**Affected Test Files:**
- tests/integration/test_decompose_commands.py (8 tests)
- tests/integration/test_graph_deps.py (8 tests)
- tests/integration/test_graph_path_list.py (13 tests)
- tests/integration/test_graph_show.py (5 tests)
- tests/integration/test_nested_status.py (7 tests)
- tests/integration/test_status_command.py (5 tests)
- tests/integration/test_validate_command.py (9 tests)

**Example Fix:**
```python
# BEFORE (broken)
def test_graph_show_displays_node() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_test_node(tmp_path, "O-TEST-001", "outcome", "Test Outcome", "core")
        create_test_graph_index(tmp_path, [], {})

        # Mock config
        jig.cli.graph.load_config = lambda: mock_config(tmp_path)

        runner = CliRunner()
        result = runner.invoke(graph, ["show", "O-TEST-001"])
        assert result.exit_code == 0  # FAILS: exit_code is 3

# AFTER (fixed)
def test_graph_show_displays_node() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create intent directory structure (FIX)
        (tmp_path / "outcomes").mkdir(parents=True, exist_ok=True)
        (tmp_path / "specifications").mkdir(parents=True, exist_ok=True)
        (tmp_path / "constraints").mkdir(parents=True, exist_ok=True)

        create_test_node(tmp_path, "O-TEST-001", "outcome", "Test Outcome", "core")
        create_test_graph_index(tmp_path, [], {})

        # Mock config
        jig.cli.graph.load_config = lambda: mock_config(tmp_path)

        runner = CliRunner()
        result = runner.invoke(graph, ["show", "O-TEST-001"])
        assert result.exit_code == 0  # PASSES
```

### Group 2: Subsystem Hierarchy Validation Change (1 test) - REWRITE or UPDATE SPEC

**Root Cause:** test_validate_status_index_consistency expects that a parent subsystem CAN have both child subsystems and direct nodes, but validation now rejects this as an error.

**Test:** tests/integration/test_command_consistency.py::test_validate_status_index_consistency

**Current Behavior:**
```
Errors:
  ✗ Parent subsystem 'core' has both children and direct nodes

✗ Graph is INVALID
```

**Test Expectation:** exit_code == 0 (validation should pass)

**Decision Required:**
1. **Option A - SPEC Changed:** If S-NESTED-001 or S-CLI-001 now prohibits parent subsystems from having both children and direct nodes, then:
   - Strategy: **REWRITE** test to verify the new validation rule
   - Update test fixture to use valid hierarchy (no mixed parent/leaf subsystems)

2. **Option B - CODE Bug:** If the SPEC allows mixed parent/leaf subsystems, then:
   - Strategy: **Bucket E** (DEBUG) - this is a CODE bug in validation
   - The test is correctly verifying SPEC, CODE is wrong
   - Create DEBUG delta to fix validation logic

**Recommendation:** Need to check S-NESTED-001 specification to determine if this is a SPEC change or CODE bug.

**Temporary Classification:** Marking as Bucket A (align) assuming SPEC changed. Will verify during Phase 4.

---

## Phase 4: Execution Plan (Not Yet Executed)

### Strategy Summary

| Group | Strategy | Tests | Estimated Time |
|-------|----------|-------|----------------|
| Group 1 | FIX | 55 | 2-3 hours |
| Group 2 | REWRITE or DEBUG | 1 | 30 min - 1 hour |
| **Total** | | **56** | **2.5-4 hours** |

### Execution Steps

#### Step 1: Fix Group 1 (Intent Directory Missing)

**Approach:** Create helper function to set up test fixture with directories.

**Implementation:**
1. Create `setup_test_jig_project(tmp_path: Path)` helper in each test file or in a shared conftest.py
2. Helper creates: `tmp_path/outcomes/`, `tmp_path/specifications/`, `tmp_path/constraints/`
3. Call helper at start of each test before creating nodes
4. Run tests to verify fix

**Commit Strategy:**
- One commit per test file (8 commits total for Group 1)
- OR: One commit for all Group 1 fixes if using shared helper

**Example Commit Message:**
```
test(integration): fix intent directory existence check (Group 1)

Fixed 8 decompose command tests to create intent directory
before invoking CLI commands.

Root Cause: Graph.load_from_dir() now validates intent_dir exists
Strategy: FIX (mechanical change, added directory creation)
Result: Tests verify S-NESTED-004 correctly

Tests Fixed:
- test_decompose_metrics_overall
- test_decompose_metrics_specific_subsystem
- test_decompose_metrics_hierarchical_coupling
- test_decompose_metrics_excludes_constraint_edges
- test_decompose_report_generates_markdown
- test_decompose_report_outputs_to_file
- test_decompose_metrics_nonexistent_subsystem
- test_decompose_metrics_yaml_output

Unit: Test Repair Phase 4.1
See: docs/wip/S033_TEST_REPAIR_wu2.5_failures.md
```

#### Step 2: Resolve Group 2 (Subsystem Hierarchy Validation)

**Investigation Required:**
1. Read S-NESTED-001 specification
2. Check git history: When was "parent with both children and direct nodes" made invalid?
3. Determine: SPEC change or CODE bug?

**If SPEC Changed (most likely):**
- Update test fixture to use valid hierarchy
- Update test to verify that invalid hierarchy is rejected (exit_code == 1 with error message)

**If CODE Bug:**
- Create DEBUG delta
- Fix validation logic to allow mixed parent/leaf subsystems
- Keep test as-is (it's correctly verifying SPEC)

---

## Phase 5: JIG Integration & Validation (Not Yet Executed)

**Checklist:**
- [ ] All tests have `@jig T-XXX verifies:S-YYY` annotations (already present)
- [ ] Full test suite passes: `pytest -v` (0 failures)
- [ ] Test count healthy: 455 tests (maintained)
- [ ] No commented-out tests in codebase
- [ ] No `# TODO: fix this test` comments
- [ ] Graph index alignment: `jigy validate --check-all` (separate from test suite)

---

## JIG Markers

### #DISCOVERY "Exit code 3 initialization check now enforced across CLI"

Found that CLI commands added `Graph.load_from_dir()` call which validates intent directory existence and returns exit code 3 if not found. This is correct behavior per S005_PLAN_phase_1_intent_graph.md design, but integration tests weren't updated to create the expected directories.

This reveals a pattern: when adding new validation/initialization checks, all integration tests need to be audited for fixture completeness.

### #DISCOVERY "55 of 56 failures have same root cause"

Excellent signal-to-noise: 98% of failures are the same mechanical issue (missing directory creation in test fixtures). Only 1 test has a different root cause (subsystem hierarchy validation change).

This clustering validates the root cause grouping approach - batch fixes will be highly efficient.

### #DECISION "FIX vs REWRITE for Group 1 tests"

**Choice:** FIX (add directory creation, don't rewrite tests)

**Rationale:**
- Tests are verifying correct SPECs (S-GRAPH-003, S-NESTED-004, etc.)
- Test logic is sound - only missing prerequisite directory setup
- Adding `mkdir()` calls is mechanical and preserves test intent
- Result will be "as good as new" - tests verify same behavior

**Tradeoffs:**
- Slightly more boilerplate in test fixtures
- Alternative (rewriting) would waste time and introduce risk

### #DECISION "Investigation required for Group 2 before repair"

**Choice:** Do NOT fix Group 2 until SPEC is verified

**Rationale:**
- Unclear if subsystem hierarchy validation change was intentional
- Fixing test without understanding SPEC could mask a CODE bug (Bucket E)
- Better to spend 15 minutes reading SPEC than commit wrong fix

**Tradeoffs:**
- Delays completion of Group 2 repair
- Acceptable: Group 2 is only 1 test (1.8% of failures)

### #LEARNED "Exit code conventions enable clear test failures"

Exit code 3 for "not initialized" makes failures immediately recognizable:
- Exit code 0: success
- Exit code 1: operational error (node not found, validation failed)
- Exit code 2: file system error
- Exit code 3: project not initialized

This convention (from S005_PLAN) makes test failures self-documenting. The error message "Have you run 'jigy init'?" is also helpful.

**Actionable:** When adding new error cases, consider introducing new exit codes with consistent semantics.

### #LEARNED "Mock load_config() is insufficient when commands use config.intent_dir"

**Pattern:**
- Test mocks `load_config()` to return custom JigConfig
- Test expects this is sufficient to redirect command to temp directory
- Reality: Command calls `Graph.load_from_dir(config.intent_dir)`, which validates directory existence

**Lesson:** Mocking config is only half the job. Test must also ensure:
1. Directories referenced by config exist
2. Required files (graph-index.yaml, node markdown files) exist
3. File contents are valid for the test scenario

**Actionable:** Create `setup_test_jig_project(tmp_path)` helper that:
- Creates directory structure
- Creates minimal valid graph-index.yaml
- Returns JigConfig pointing to temp structure

This makes test fixtures more robust and self-contained.

---

## Recommended Next Steps

### Immediate Actions
1. **Execute Phase 4.1:** Fix Group 1 tests (55 tests, 2-3 hours)
   - Create shared `setup_test_jig_project()` helper
   - Update all affected test files to call helper
   - Run `pytest tests/integration/` to verify fixes

2. **Investigate Group 2:** Read S-NESTED-001 specification (15 min)
   - Determine if "parent subsystem with children and direct nodes" is now invalid
   - If SPEC changed: update test fixture and expectations
   - If CODE bug: create DEBUG delta

3. **Execute Phase 4.2:** Resolve Group 2 test (1 test, 30 min - 1 hour)
   - Apply REWRITE or DEBUG strategy based on investigation

4. **Execute Phase 5:** Validation (30 min)
   - Run full test suite: `pytest -v` (expect 0 failures)
   - Check for anti-patterns (commented tests, TODOs)
   - Update this document with completion metrics

### Harvest Preparation
**Markers Captured:** 5 (#DISCOVERY: 2, #DECISION: 2, #LEARNED: 2)

**Recommended OSTC Updates:**
- [ ] Consider creating S-TEST-001: "Integration tests must create required directory structure"
- [ ] Consider updating S-CLI-001 or S-GRAPH-003 to document exit code 3 convention
- [ ] Update test helper library with `setup_test_jig_project()` utility

---

## Appendix A: Detailed Failure List

### test_decompose_commands.py (8 failures)
```
FAILED test_decompose_metrics_overall - assert 3 == 0
FAILED test_decompose_metrics_specific_subsystem - assert 3 == 0
FAILED test_decompose_metrics_hierarchical_coupling - assert 3 == 0
FAILED test_decompose_metrics_excludes_constraint_edges - assert 3 == 0
FAILED test_decompose_report_generates_markdown - assert 3 == 0
FAILED test_decompose_report_outputs_to_file - assert 3 == 0
FAILED test_decompose_metrics_nonexistent_subsystem - assert 3 == 0
FAILED test_decompose_metrics_yaml_output - assert 3 == 0
```

### test_graph_deps.py (8 failures)
```
FAILED test_graph_deps_shows_tree - assert 3 == 0
FAILED test_graph_deps_handles_cycles - assert 3 == 0
FAILED test_graph_impact_shows_dependents - assert 3 == 0
FAILED test_graph_deps_performance - assert 3 == 0
FAILED test_graph_deps_no_dependencies - assert 3 == 0
FAILED test_graph_impact_no_dependents - assert 3 == 0
FAILED test_graph_deps_node_not_found - assert 3 == 0
FAILED test_graph_impact_node_not_found - assert 3 == 0
```

### test_graph_path_list.py (13 failures)
```
FAILED test_graph_path_finds_route - assert 3 == 0
FAILED test_graph_path_no_route - assert 3 == 0
FAILED test_graph_list_all_nodes - assert 3 == 0
FAILED test_graph_list_filter_by_type - assert 3 == 0
FAILED test_graph_list_filter_by_subsystem - assert 3 == 0
FAILED test_graph_list_yaml_output - assert 3 == 0
FAILED test_graph_path_same_node - assert 3 == 0
FAILED test_graph_path_node_not_found - assert 3 == 0
FAILED test_graph_list_empty_result - assert 3 == 0
FAILED test_graph_list_combined_filters - assert 3 == 0
FAILED test_graph_list_compact_format - assert 3 == 0
FAILED test_graph_list_compact_with_subsystem_filter - assert 3 == 0
FAILED test_graph_list_default_format_is_table - assert 3 == 0
```

### test_graph_show.py (5 failures)
```
FAILED test_graph_show_displays_node - assert 3 == 0
FAILED test_graph_show_displays_relationships - assert 3 == 0
FAILED test_graph_show_node_not_found - assert 3 == 0
FAILED test_graph_show_truncates_long_body - assert 3 == 0
FAILED test_graph_show_colorized_output - assert 3 == 0
```

### test_nested_status.py (7 failures)
```
FAILED test_status_hierarchical_view - assert 3 == 0
FAILED test_status_flat_view - assert 3 == 0
FAILED test_graph_list_recursive - assert 3 == 0
FAILED test_graph_list_leaf_subsystem - assert 3 == 0
FAILED test_constraint_scope_nested_subsystems - assert 3 == 0
FAILED test_graph_list_subsystem_with_table_format - assert 3 == 0
FAILED test_graph_list_nonexistent_subsystem - assert 3 == 0
```

### test_status_command.py (5 failures)
```
FAILED test_status_performance - FileNotFoundError [Errno 2] No such file or directory
FAILED test_status_command_cli_output - assert 3 == 0
FAILED test_status_command_verbose_output - assert 3 == 0
FAILED test_status_command_empty_graph - assert 3 == 0
FAILED test_status_command_healthy_graph - assert 3 == 0
```

### test_validate_command.py (9 failures)
```
FAILED test_jigy_validate_all_valid - assert 3 == 0
FAILED test_jigy_validate_detects_errors - assert 3 == 0
FAILED test_jigy_validate_verbose - assert 3 == 0
FAILED test_jigy_validate_shows_warnings - assert 3 == 0
FAILED test_jigy_validate_duplicate_ids - assert 3 == 0
FAILED test_jigy_validate_graph_index_nonexistent_node - assert 3 == 0
FAILED test_jigy_validate_performance - assert 3 == 0
FAILED test_jigy_validate_empty_graph - assert 3 == 0
FAILED test_jigy_validate_exit_codes - assert 3 == 0
```

### test_command_consistency.py (1 failure)
```
FAILED test_validate_status_index_consistency - AssertionError: status failed
  Errors: ✗ Parent subsystem 'core' has both children and direct nodes
  assert 1 == 0
```

---

## Appendix B: Code References

### Exit Code 3 Implementation Locations
- src/jig/cli/status.py:410
- src/jig/cli/node.py:87, 96
- src/jig/cli/validate.py:102, 115
- src/jig/cli/graph.py:107, 180, 211, 243, 301
- src/jig/cli/decompose.py:52, 247

### Test Files Requiring Fixes
- tests/integration/test_decompose_commands.py (8 tests)
- tests/integration/test_graph_deps.py (8 tests)
- tests/integration/test_graph_path_list.py (13 tests)
- tests/integration/test_graph_show.py (5 tests)
- tests/integration/test_nested_status.py (7 tests)
- tests/integration/test_status_command.py (5 tests)
- tests/integration/test_validate_command.py (9 tests)
- tests/integration/test_command_consistency.py (1 test - different root cause)

---

## Appendix C: Quick Reference Decision Matrix

```
For each failing test:
  ├─ Exit code 3 (intent directory not found)?
  │  └─ YES → Bucket A, Strategy: FIX (add mkdir to fixture) [55 tests]
  │
  └─ Subsystem hierarchy validation error?
     └─ YES → Investigate SPEC → Bucket A or E [1 test]
        ├─ SPEC allows mixed parent/leaf → Bucket E (DEBUG)
        └─ SPEC prohibits mixed parent/leaf → Bucket A (REWRITE test)
```

---

## Status: Analysis Complete, Awaiting Execution

**Next:** Execute Phase 4 repairs per plan above.

**Time Estimate:** 2.5-4 hours total
- Group 1 (FIX): 2-3 hours
- Group 2 (REWRITE or DEBUG): 30 min - 1 hour
- Phase 5 (Validation): 30 min

**Confidence:** HIGH
- Root cause clearly identified (98% same issue)
- Fix strategy is mechanical (low risk)
- All tests have valid SPEC coverage (no Bucket B or C)
- No CODE bugs detected in audit (no Bucket E, except possibly 1 test)
