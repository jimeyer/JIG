---
delta_type: plan
created: 2025-11-22
branch: merge-validate-status
status: test-recovery
updated: 2025-11-22
---

# PLAN: Merge `jigy validate` into `jigy status`

- **SCOPE:** docs/wip/S029_PROPOSAL_merge_validate_into_status.md
- **Start:** 2025-11-22
- **Owner:** Jim Meyer
- **Status:** Test Recovery (WU2.1-2.6 in progress)
- **Subsystem:** cli

> **NOTE:** WU2 implementation broke 85 tests. Test recovery work units (WU2.1-2.6) added following taskTestRepair.md protocol. See docs/wip/S032_RETROSPECTIVE_wu2_test_failures.md for analysis.

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
- [x] WU1: Extract validation core logic — tests ✓ / docs ✓ / reflect ☐
- [x] WU2: Merge validation into status command — tests ✓ / docs ✓ / reflect ☐
- [x] **WU2.1: Stop Bleeding - Fix critical blockers** — tests ✓ / docs n/a / reflect ✓
- [x] **WU2.2: SPEC Audit - Classify all failures** — tests n/a / docs ✓ / reflect ✓
- [x] **WU2.3: Create Missing SPECs (if needed)** — tests n/a / docs n/a / reflect n/a (skipped - no SPECs needed)
- [x] **WU2.4: Root Cause Grouping** — tests n/a / docs ✓ / reflect ✓
- [ ] **WU2.5: Execute Repairs (batch fixes)** — tests 🔄 (24/85 - 28%) / docs ✓ / reflect ✓ (IN PROGRESS - Phase 0 ✓, Phase 1 partial)
- [ ] **WU2.6: Validation & Integration** — tests ☐ / docs ☐ / reflect ☐
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

## TEST RECOVERY WORK UNITS (Following taskTestRepair.md)

**Context:** WU2 implementation broke 85 tests (23% failure rate). Following SPEC-driven test recovery protocol to restore test suite health before proceeding to WU3.

**See:** docs/wip/S032_RETROSPECTIVE_wu2_test_failures.md for detailed analysis.

**Protocol:** agents/taskTestRepair.md (5-bucket classification, 5-phase recovery)

---

### Work Unit 2.1: Stop Bleeding - Fix Critical Blockers

**Goal:** Get clean failure counts by fixing obvious blockers that cascade into many test failures.

**Planned Effort:** 30-45 minutes

**Acceptance Criteria:**
- All import errors resolved (e.g., missing modules, moved functions)
- Obvious constructor signature changes fixed (mechanical changes only)
- Full test suite runs without crashes
- Clean baseline established: X tests failing out of Y total
- Failure categories documented

**Implementation Notes:**
- Run `pytest tests/unit/ -v` to get initial failure count
- Fix critical import errors first (these block many tests)
- Fix obvious constructor signature mismatches (e.g., missing required params)
- **Do NOT fix logic errors yet** - only blockers that prevent tests from running
- Document baseline in this work unit's Reflect section

**Failure Categories (from S032_RETROSPECTIVE):**
1. Graph Index Format Errors (~30 failures) - Tests expect YAML, now JSON
2. Status Logic Tests (~7 failures) - Tests create minimal fixtures, validation expects complete graph
3. Validator Tests (~6 failures) - Tests call validate_graph() without proper index
4. Subsystem Path Validation (~20+ failures) - Tests create nodes with subsystem="core" but no subsystem defined

**Test Plan:**
```bash
# Initial baseline
pytest tests/unit/ -v --tb=no -q | tee test-baseline-before.txt

# After fixing blockers
pytest tests/unit/ -v --tb=no -q | tee test-baseline-after.txt

# Document counts
grep -c FAILED test-baseline-before.txt
grep -c FAILED test-baseline-after.txt
```

**Docs to Update:**
- Add baseline metrics to S032_RETROSPECTIVE (if needed)
- Document any discoveries about failure root causes

**Reflect:**
- Baseline before: 365 tests total, 85 failed (23.3%), 280 passed (76.7%)
- Baseline after: Same (no blockers to fix - test suite runs clean)
- Critical blockers fixed: **NONE** - No import errors or constructor mismatches found
- Remaining failures: 85 tests, all due to graph-index.json format migration
  - Graph commands: 24 failures (missing graph-index.json in fixtures)
  - Graph traversal: 11 failures (missing graph-index.json in fixtures)
  - Graph queries: 10 failures (missing graph-index.json in fixtures)
  - Graph index loading: 8 failures (tests expect YAML, code uses JSON)
  - Annotation validation: 8 failures (validation expects complete graph structure)
  - Validator tests: 7 failures (missing graph-index.json in fixtures)
  - Status logic: 7 failures (calculate_status now runs comprehensive validation)
  - Nested subsystems: 7 failures (missing graph-index.json + subsystem definitions)
  - Other: 3 failures (edge validation, node registry, decompose metrics)

**Discovery:** All 85 failures are logic errors (missing graph-index.json or stricter validation), NOT import/constructor blockers. Test suite runs without crashes. Ready for WU2.2 classification.

---

### Work Unit 2.2: SPEC Audit - Classify All Failures

**Goal:** Classify every failing test into one of 5 buckets (A/B/C/D/E) per taskTestRepair.md protocol.

**Planned Effort:** 2-3 hours

**Acceptance Criteria:**
- All failing tests classified into buckets:
  - **Bucket A:** SPEC valid, test needs alignment (FIX or REWRITE)
  - **Bucket B:** SPEC missing, requirement real (create SPEC first)
  - **Bucket C:** SPEC obsolete or redundant (DELETE test)
  - **Bucket D:** O-S-T aligned, CODE missing (SKIP - TDD scenario)
  - **Bucket E:** CODE bug detected (DEBUG workflow)
- Audit table created with test name, file:line, SPEC, bucket, notes
- For each test, documented: What SPEC does this verify? Is SPEC still valid?
- Initial strategy assigned (FIX/REWRITE/DELETE/SKIP/DEBUG)

**Implementation Notes:**
- Create audit spreadsheet/table in this PLAN document or separate file
- For each failing test:
  1. Read test function and docstring
  2. Determine: What requirement does this verify?
  3. Search for SPEC in jig/specifications/ or test annotations
  4. Classify using decision tree from taskTestRepair.md
  5. Document bucket and rationale

**Expected Distribution (based on S032_RETROSPECTIVE):**
- **Bucket A (Align):** ~70-80 tests - Tests need to adapt to stricter validation
- **Bucket B (Create SPEC):** ~0-5 tests - Most tests likely have implicit SPECs
- **Bucket C (Delete):** ~0-2 tests - Minimal obsolete tests expected
- **Bucket D (Skip - TDD):** ~0 tests - CODE exists, just stricter
- **Bucket E (Debug):** ~0-2 tests - May discover actual bugs

**Audit Template:**
```markdown
## SPEC Audit Results

### Bucket A: Existing SPEC (align test) - N tests
| Test | File:Line | Verifies SPEC | Strategy | Root Cause |
|------|-----------|---------------|----------|------------|
| test_graph_traversal_basic | test_graph_traversal.py:42 | S-CORE-001 | FIX | Needs graph-index.json fixture |

### Bucket B: Missing SPEC - N tests
| Test | File:Line | Needs SPEC | Subsystem | Rationale |
|------|-----------|------------|-----------|-----------|
| (Expected: 0-5 tests) |

### Bucket C: Obsolete SPEC - N tests
| Test | File:Line | Obsolete Feature | Decision |
|------|-----------|------------------|----------|
| (Expected: 0-2 tests) |

### Bucket D: CODE Missing (TDD) - N tests
| Test | File:Line | Verifies SPEC | CODE Status | SCOPE Doc |
|------|-----------|---------------|-------------|-----------|
| (Expected: 0 tests) |

### Bucket E: CODE Bug Detected - N tests
| Test | File:Line | Verifies SPEC | Bug Description | DEBUG Delta |
|------|-----------|---------------|-----------------|-------------|
| (Expected: 0-2 tests) |
```

**JIG Markers:**
```markdown
#DISCOVERY "Found N tests with no traceable SPEC (Bucket B)"
(Document any SPEC gaps discovered)

#DISCOVERY "Found N tests where stricter validation breaks minimal fixtures (Bucket A)"
Tests assumed lenient validation, now validation is comprehensive.

#DECISION "Classify tests by SPEC validity before fixing"
**Rationale:** SPEC-first approach ensures fixes are durable
**Tradeoffs:** More upfront analysis, but prevents re-breakage
```

**Test Plan:**
- No code changes in this phase
- Pure audit and classification
- Verify every test has a bucket assignment

**Docs to Update:**
- Add audit results to this PLAN document (create section after WU2.6)
- Update S032_RETROSPECTIVE with classification insights

**Reflect:**
- Bucket distribution:
  - **Bucket A (Align):** 85 tests (100%)
  - **Bucket B (Missing SPEC):** 0 tests
  - **Bucket C (Obsolete):** 0 tests
  - **Bucket D (TDD - CODE missing):** 0 tests
  - **Bucket E (CODE bug):** 0 tests
- Surprises: **ZERO tests in buckets B/C/D/E!** All 85 failures have same root cause (missing graph-index.json). All SPECs are valid and active.
- Strategy clarity: **Crystal clear** - 100% FIX strategy. All tests verify valid SPECs, just need proper fixtures.

## SPEC Audit Results (WU2.2)

**Summary:** All 85 failing tests classified into **Bucket A** (SPEC valid, test needs alignment). Zero tests in other buckets.

**Root Cause:** Graph.load_from_dir() now requires graph-index.json (WU4 format migration). Test fixtures create markdown nodes but don't create graph-index.json.

**Strategy:** **FIX** (mechanical) - Create test fixture helpers to generate graph-index.json for all tests.

### Bucket A: Existing SPEC (align test) - 85 tests

**Group 1: Graph Commands (24 tests)** - `tests/unit/test_graph_commands.py`
| Test | Verifies SPEC | Root Cause | Strategy |
|------|---------------|------------|----------|
| test_graph_show_displays_node_details | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_show_displays_dependencies | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_show_displays_dependents | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_show_node_not_found | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_show_displays_body_content | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_list_all_nodes | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_list_filter_by_type | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_list_filter_by_subsystem | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_list_compact_format | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_list_yaml_format | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_deps_shows_dependency_tree | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_deps_node_not_found | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_impact_shows_impact_tree | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_impact_node_not_found | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_path_finds_shortest_path | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_path_no_path_exists | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_path_start_node_not_found | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_path_end_node_not_found | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_show_with_multiple_dependencies | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_commands_performance | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_list_empty_result | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_show_node_with_no_dependencies | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_commands_with_code_and_test_nodes | S-JIGY-005 | Missing graph-index.json | FIX |
| test_graph_list_combined_filters | S-JIGY-005 | Missing graph-index.json | FIX |

**Group 2: Graph Traversal (11 tests)** - `tests/unit/test_graph_traversal.py`
| Test | Verifies SPEC | Root Cause | Strategy |
|------|---------------|------------|----------|
| test_get_dependencies | S-GRAPH-003 | Missing graph-index.json | FIX |
| test_get_dependents | S-GRAPH-003 | Missing graph-index.json | FIX |
| test_find_path_exists | S-GRAPH-003 | Missing graph-index.json | FIX |
| test_find_path_no_path | S-GRAPH-003 | Missing graph-index.json | FIX |
| test_find_path_same_node | S-GRAPH-003 | Missing graph-index.json | FIX |
| test_find_path_missing_nodes | S-GRAPH-003 | Missing graph-index.json | FIX |
| test_get_dependencies_multiple | S-GRAPH-003 | Missing graph-index.json | FIX |
| test_get_dependencies_missing_node | S-GRAPH-003 | Missing graph-index.json | FIX |
| test_get_dependents_missing_node | S-GRAPH-003 | Missing graph-index.json | FIX |
| test_traversal_performance | S-GRAPH-003 | Missing graph-index.json | FIX |
| test_find_path_shortest | S-GRAPH-003 | Missing graph-index.json | FIX |

**Group 3: Graph Queries (10 tests)** - `tests/unit/test_graph_queries.py`
| Test | Verifies SPEC | Root Cause | Strategy |
|------|---------------|------------|----------|
| test_filter_by_type_outcome | S-GRAPH-002 | Missing graph-index.json | FIX |
| test_filter_by_type_case_insensitive | S-GRAPH-002 | Missing graph-index.json | FIX |
| test_filter_by_type_specification | S-GRAPH-002 | Missing graph-index.json | FIX |
| test_filter_by_type_empty | S-GRAPH-002 | Missing graph-index.json | FIX |
| test_filter_by_subsystem | S-GRAPH-002 | Missing graph-index.json | FIX |
| test_filter_by_subsystem_case_insensitive | S-GRAPH-002 | Missing graph-index.json | FIX |
| test_filter_by_subsystem_empty | S-GRAPH-002 | Missing graph-index.json | FIX |
| test_filter_by_subsystem_handles_none | S-GRAPH-002 | Missing graph-index.json | FIX |
| test_filter_returns_sorted | S-GRAPH-002 | Missing graph-index.json | FIX |
| test_filter_combined_operations | S-GRAPH-002 | Missing graph-index.json | FIX |

**Group 4: Graph Index Loading (8 tests)** - `tests/unit/test_graph_index_loading.py`
| Test | Verifies SPEC | Root Cause | Strategy |
|------|---------------|------------|----------|
| test_load_graph_index_with_ct_nodes | S-INDEX-002 | Tests expect YAML format | FIX |
| test_load_node_centric_relationships | S-INDEX-002 | Tests expect YAML format | FIX |
| test_load_edge_centric_format | S-INDEX-002 | Tests expect YAML format | FIX |
| test_merge_markdown_and_graph_index | S-INDEX-002 | Tests expect YAML format | FIX |
| test_markdown_takes_precedence_for_os_nodes | S-INDEX-002 | Tests expect YAML format | FIX |
| test_graph_index_without_nodes_section | S-INDEX-002 | Tests expect YAML format | FIX |
| test_ct_nodes_with_file_and_line | S-INDEX-002 | Tests expect YAML format | FIX |
| test_invalid_nodes_format_raises_error | S-INDEX-002 | Tests expect YAML format | FIX |

**Group 5: Annotation Validation (8 tests)** - `tests/unit/test_annotation_validation.py`
| Test | Verifies SPEC | Root Cause | Strategy |
|------|---------------|------------|----------|
| test_validate_all_valid_annotations | S-ANNO-002 | Validation expects complete graph | FIX |
| test_allow_same_id_if_same_file_and_line | S-ANNO-002 | Validation expects complete graph | FIX |
| test_detect_spec_without_implementation | S-ANNO-002 | Validation expects complete graph | FIX |
| test_detect_spec_without_tests | S-ANNO-002 | Validation expects complete graph | FIX |
| test_valid_code_node_id | S-ANNO-002 | Validation expects complete graph | FIX |
| test_validate_annotations_function | S-ANNO-002 | Validation expects complete graph | FIX |
| test_calculate_implementation_coverage | S-ANNO-002 | Validation expects complete graph | FIX |
| test_validate_intent_only_no_annotations | S-ANNO-002 | Validation expects complete graph | FIX |

**Group 6: Validator Tests (7 tests)** - `tests/unit/test_validator.py`
| Test | Verifies SPEC | Root Cause | Strategy |
|------|---------------|------------|----------|
| test_validate_graph_duplicate_ids | S-VAL-001 | Missing graph-index.json | FIX |
| test_validate_graph_empty_directory | S-VAL-001 | Missing graph-index.json | FIX |
| test_validate_graph_with_valid_nodes | S-VAL-001 | Missing graph-index.json | FIX |
| test_validate_graph_with_invalid_node | S-VAL-001 | Missing graph-index.json | FIX |
| test_validate_graph_index_nonexistent_node | S-VAL-001 | Missing graph-index.json | FIX |
| test_validate_graph_orphaned_nodes_warning | S-VAL-001 | Missing graph-index.json | FIX |
| test_validate_graph_with_ct_nodes | S-VAL-001 | Missing graph-index.json | FIX |

**Group 7: Status Logic (7 tests)** - `tests/unit/test_status_logic.py`
| Test | Verifies SPEC | Root Cause | Strategy |
|------|---------------|------------|----------|
| test_calculate_status_with_valid_graph | S-CLI-022 | Missing graph-index.json + validation | FIX |
| test_calculate_status_identifies_orphans | S-CLI-022 | Missing graph-index.json + validation | FIX |
| test_calculate_status_handles_missing_graph_index | S-CLI-022 | Missing graph-index.json + validation | FIX |
| test_calculate_status_empty_directory | S-CLI-022 | Missing graph-index.json + validation | FIX |
| test_calculate_status_multiple_subsystems | S-CLI-022 | Missing graph-index.json + validation | FIX |
| test_calculate_status_all_node_types | S-CLI-022 | Missing graph-index.json + validation | FIX |
| test_calculate_status_no_orphans_when_connected | S-CLI-022 | Missing graph-index.json + validation | FIX |

**Group 8: Nested Subsystems (7 tests)** - `tests/unit/test_nested_subsystems.py`
| Test | Verifies SPEC | Root Cause | Strategy |
|------|---------------|------------|----------|
| test_nested_subsystem_loading | S-SUBSYS-001 | Missing graph-index.json + subsystem defs | FIX |
| test_subsystem_path_resolution | S-SUBSYS-001 | Missing graph-index.json + subsystem defs | FIX |
| test_recursive_node_collection | S-SUBSYS-001 | Missing graph-index.json + subsystem defs | FIX |
| test_parent_with_nodes_validation | S-SUBSYS-001 | Missing graph-index.json + subsystem defs | FIX |
| test_backward_compatibility_flat | S-SUBSYS-001 | Missing graph-index.json + subsystem defs | FIX |
| test_get_all_subsystem_paths | S-SUBSYS-001 | Missing graph-index.json + subsystem defs | FIX |
| test_invalid_node_subsystem_path | S-SUBSYS-001 | Missing graph-index.json + subsystem defs | FIX |

**Group 9: Other Tests (3 tests)**
| Test | File | Verifies SPEC | Root Cause | Strategy |
|------|------|---------------|------------|----------|
| test_validate_edges_integration | test_edge_validation.py | S-VAL-003 | Missing graph-index.json | FIX |
| test_node_registry_integration | test_node_registry.py | S-GRAPH-001 | Missing graph-index.json | FIX |
| test_modularity_calculation_known_graph | test_decompose_metrics.py | S-METRICS-001 | Missing graph-index.json | FIX |

### Bucket B: Missing SPEC - 0 tests
**Result:** All tests have valid, traceable SPECs. No SPEC creation needed.

### Bucket C: Obsolete SPEC - 0 tests
**Result:** All SPECs are active and relevant. No test deletion needed.

### Bucket D: CODE Missing (TDD) - 0 tests
**Result:** All CODE exists. Tests fail due to stricter validation, not missing functionality.

### Bucket E: CODE Bug Detected - 0 tests
**Result:** No CODE bugs detected. All failures are fixture-related (mechanical fixes).

## Classification Insights

**#DISCOVERY "100% Bucket A classification - unprecedented test repair clarity"**
All 85 failures stem from a single architectural change (graph-index format migration). Every test verifies a valid, active SPEC. Zero tests need deletion, SPEC creation, or CODE debugging. This is a textbook example of clean architectural evolution requiring systematic fixture updates.

**#DISCOVERY "Graph-index.json requirement is pervasive"**
Graph.load_from_dir() now requires graph-index.json (enforced in WU4). This touches every test that creates graph fixtures. The format migration (YAML→JSON) was intentionally a clean break, with zero fallback to YAML. This forced all tests to adapt to the new format.

**#LEARNED "Clean breaks create clean failure patterns"**
By removing YAML support completely (no fallback, no migration path), the failure pattern is crystal clear: missing graph-index.json. If we had kept YAML fallback, we'd have inconsistent failures and harder classification. Clean architectural decisions enable clean test repairs.

**#DECISION "FIX all 85 tests with fixture helpers (no REWRITE)"**
**Choice:** Mechanical FIX strategy for all tests
**Rationale:** SPECs unchanged, test intent unchanged, only fixture format changed
**Implementation:** Create `tests/helpers/graph_fixtures.py` with `create_test_graph()` helper
**Tradeoffs:** More helper code, but maintainable and reusable across all tests

---

### Work Unit 2.3: Create Missing SPECs (If Needed)

**Goal:** For every Bucket B test, create the missing Specification before fixing the test.

**Planned Effort:** 0-2 hours (depends on Bucket B count from WU2.2)

**Acceptance Criteria:**
- All Bucket B tests have corresponding SPECs created
- SPECs have proper YAML frontmatter (id, type, title, subsystem, implements)
- SPECs describe "what", not "how"
- SPECs link to at least one Outcome (business value)
- `jigy validate` passes on new SPECs
- SPECs committed before test fixes

**Implementation Notes:**
- **If Bucket B is empty:** Skip this work unit entirely (likely scenario)
- **If Bucket B has tests:**
  1. For each Bucket B test, extract the requirement (the "what")
  2. Determine which Outcome this supports (or create new Outcome)
  3. Create `jig/specifications/S-<SUBSYSTEM>-NNN.md`
  4. Run `jigy validate` to check format
  5. Commit SPECs before proceeding to WU2.4

**SPEC Template:**
```yaml
---
id: S-XXX-NNN
type: specification
title: "[Clear, testable requirement]"
subsystem: [subsystem]
created: 2025-11-22
implements: O-XXX-NNN
---

# Specification: [Title]

[Clear statement of requirement]

## Rationale
[Why this requirement exists]

## Acceptance Criteria
- [Testable criterion 1]
- [Testable criterion 2]

## Related
- implements: O-XXX-NNN
- tested_by: T-XXX-NNN
- code: C-XXX-NNN
```

**Expected Outcome:**
- Based on S032_RETROSPECTIVE analysis, expect 0-5 missing SPECs
- Most tests verify existing SPECs, just need fixture updates

**Test Plan:**
```bash
# Validate new SPECs
jigy validate

# Verify SPECs in graph
jigy status | grep "specifications"
```

**Docs to Update:**
- Document any new SPECs created in Reflect section

**Reflect:**
- SPECs created: (count and IDs)
- Rationale: (why these were missing)
- Or: "Bucket B empty, no SPECs needed" (likely)

---

### Work Unit 2.4: Root Cause Grouping

**Goal:** Group Bucket A tests by root cause and assign repair strategy (FIX vs REWRITE).

**Planned Effort:** 1 hour

**Acceptance Criteria:**
- All Bucket A tests grouped by common root cause
- Each group assigned strategy: FIX or REWRITE
- Strategy rationale documented for each group
- Bucket C (delete) and D/E handled separately
- Batch repair plan created (one commit per group)

**Implementation Notes:**
- Analyze failure messages to identify common patterns
- Group tests by (root cause, strategy) tuple
- Assign strategy using decision matrix:
  - **FIX:** Change is mechanical, result is "as good as new"
  - **REWRITE:** Architecture changed, SPEC semantics evolved

**Expected Groups (from S032_RETROSPECTIVE):**

**Group 1: Graph Index Fixture (FIX) - ~30 tests**
- **Root Cause:** Tests create markdown nodes but no graph-index.json
- **Strategy:** FIX (create test fixture helper that generates index)
- **Files:** tests/unit/test_graph_*.py, test_nested_subsystems.py
- **Action:** Create `tests/helpers/graph_fixtures.py` with builder functions

**Group 2: Status Logic Fixtures (FIX) - ~7 tests**
- **Root Cause:** Tests create temp dirs but validation expects complete graph structure
- **Strategy:** FIX (update fixtures to create valid graph structures)
- **Files:** tests/unit/test_status_logic.py
- **Action:** Use fixture helpers from Group 1

**Group 3: Validator Fixtures (FIX) - ~6 tests**
- **Root Cause:** Tests call validate_graph() without proper index
- **Strategy:** FIX (create graph-index.json in test setup)
- **Files:** tests/unit/test_validator.py
- **Action:** Use fixture helpers from Group 1

**Group 4: Subsystem Path Validation (FIX) - ~20+ tests**
- **Root Cause:** Tests create nodes with subsystem="core" but no subsystem definition
- **Strategy:** FIX (create subsystem nodes in test fixtures)
- **Files:** Multiple test files
- **Action:** Update fixtures to create subsystem hierarchy

**Group 5: Bucket C - Obsolete Tests (DELETE) - ~0-2 tests**
- **Root Cause:** Test verifies obsolete SPEC or duplicate coverage
- **Strategy:** DELETE
- **Files:** TBD from audit
- **Action:** Delete file, update graph index

**Decision Criteria:**
- FIX: Would you write the same test today? (Yes → FIX)
- REWRITE: Does the SPEC match old test intent? (No → REWRITE)
- DELETE: Should this SPEC exist? (No → DELETE)

**JIG Markers:**
```markdown
#DECISION "FIX test fixtures vs REWRITE tests from scratch"
**Choice:** FIX (create test fixture helpers)
**Rationale:** SPECs unchanged, tests just need stricter fixtures
**Tradeoffs:** Helper functions add code, but make tests maintainable

#LEARNED "Stricter validation requires stricter test fixtures"
Validation now comprehensive - tests need complete graph structures.
Cannot use minimal fixtures anymore (subsystems required, index required).
```

**Test Plan:**
- No code changes yet (planning only)
- Verify all tests assigned to a group
- Verify each group has clear strategy

**Docs to Update:**
- Document grouping results in this PLAN

**Reflect:**
- Groups identified: **5 consolidated groups** (from 9 initial groups in WU2.2)
- FIX vs REWRITE ratio: **100% FIX** (0% REWRITE, 0% DELETE)
- Surprises: All groups use same helper function strategy - single foundational fix enables all repairs

## Root Cause Grouping Results (WU2.4)

**Summary:** Consolidated 9 test groups from WU2.2 into 5 repair groups based on common root causes and repair actions. All groups use **FIX** strategy (mechanical changes).

**Consolidation Rationale:** Multiple test groups share the same root cause (missing graph-index.json) and can be fixed with the same helper function. Consolidating reduces duplication and enables batch fixes.

### Repair Group 1: Graph Index Fixtures - 55 tests (FIX)

**Root Cause:** Tests create markdown nodes but no graph-index.json

**Source Groups:**
- Group 1: Graph Commands (24 tests)
- Group 2: Graph Traversal (11 tests)
- Group 3: Graph Queries (10 tests)
- Group 6: Validator Tests (7 tests)
- Group 9: Other Tests (3 tests)

**Files Affected:**
- `tests/unit/test_graph_commands.py` (24 tests)
- `tests/unit/test_graph_traversal.py` (11 tests)
- `tests/unit/test_graph_queries.py` (10 tests)
- `tests/unit/test_validator.py` (7 tests)
- `tests/unit/test_edge_validation.py` (1 test)
- `tests/unit/test_node_registry.py` (1 test)
- `tests/unit/test_decompose_metrics.py` (1 test)

**Strategy:** FIX (mechanical)

**Repair Actions:**
1. Create `tests/helpers/graph_fixtures.py` with foundational helper
2. Implement `create_test_graph(tmp_path, nodes, subsystems=None, edges=None)` function
3. Update all 55 tests to use helper instead of manual fixture creation
4. Helper generates both markdown files AND graph-index.json
5. Verify tests pass after update

**Decision Criteria (FIX vs REWRITE):**
- Would you write the same test today? **YES** - Test intent unchanged
- Test just needs proper fixtures with graph-index.json

**Batch Commit Message:**
```
test(core): fix graph index fixtures (Repair Group 1 - 55 tests)

Created tests/helpers/graph_fixtures.py with create_test_graph() helper.
Updated 55 tests to use helper for generating complete graph fixtures.

Tests now create:
- Markdown node files (outcomes, specs, etc.)
- graph-index.json with proper structure
- Subsystem definitions (when needed)

Files updated:
- tests/unit/test_graph_commands.py (24 tests)
- tests/unit/test_graph_traversal.py (11 tests)
- tests/unit/test_graph_queries.py (10 tests)
- tests/unit/test_validator.py (7 tests)
- tests/unit/test_edge_validation.py (1 test)
- tests/unit/test_node_registry.py (1 test)
- tests/unit/test_decompose_metrics.py (1 test)

Strategy: FIX (mechanical change, SPECs unchanged)
Root Cause: Graph.load_from_dir() now requires graph-index.json
Result: All 55 tests pass

Unit: Test Repair WU2.5.1 (taskTestRepair Phase 4)
See: docs/wip/S030_PLAN → WU2.4 → Repair Group 1
```

### Repair Group 2: Graph Index Format Migration - 8 tests (FIX)

**Root Cause:** Tests expect YAML format, code now uses JSON format

**Source Groups:**
- Group 4: Graph Index Loading (8 tests)

**Files Affected:**
- `tests/unit/test_graph_index_loading.py` (8 tests)

**Strategy:** FIX (mechanical)

**Repair Actions:**
1. Update tests to create graph-index.json instead of graph-index.yaml
2. Convert YAML test data to JSON format
3. Update assertions to expect JSON structure
4. Use `json.dumps()` instead of `yaml.dump()`
5. Verify JSON format validation works correctly

**Decision Criteria (FIX vs REWRITE):**
- Would you write the same test today? **YES** - Format changed, not requirements
- Tests verify index loading, just need JSON instead of YAML

**Batch Commit Message:**
```
test(core): migrate graph index tests to JSON format (Repair Group 2 - 8 tests)

Updated all graph index loading tests from YAML to JSON format.
Tests now create graph-index.json (not graph-index.yaml).

Changes:
- Convert test fixtures from YAML to JSON
- Update assertions for JSON structure
- Use json.dumps() instead of yaml.dump()
- Verify JSON parsing and validation

Files updated:
- tests/unit/test_graph_index_loading.py (8 tests)

Strategy: FIX (mechanical format migration)
Root Cause: Clean break from YAML to JSON (WU4 format migration)
Result: All 8 tests pass

Unit: Test Repair WU2.5.2 (taskTestRepair Phase 4)
See: docs/wip/S030_PLAN → WU2.4 → Repair Group 2
```

### Repair Group 3: Annotation Validation Fixtures - 8 tests (FIX)

**Root Cause:** Validation now expects complete graph structure (stricter validation from WU2)

**Source Groups:**
- Group 5: Annotation Validation (8 tests)

**Files Affected:**
- `tests/unit/test_annotation_validation.py` (8 tests)

**Strategy:** FIX (mechanical)

**Repair Actions:**
1. Use `create_test_graph()` helper from Repair Group 1
2. Create complete graph structures with graph-index.json
3. Add subsystem definitions where needed
4. Ensure all referenced nodes exist in fixtures
5. Verify comprehensive validation passes

**Decision Criteria (FIX vs REWRITE):**
- Would you write the same test today? **YES** - Validation stricter, not different
- Tests verify annotation validation, just need complete fixtures

**Batch Commit Message:**
```
test(core): fix annotation validation fixtures (Repair Group 3 - 8 tests)

Updated annotation validation tests to create complete graph structures.
Validation now comprehensive (from WU2), tests need proper fixtures.

Changes:
- Use create_test_graph() helper for complete fixtures
- Add graph-index.json to all test setups
- Create subsystem definitions where referenced
- Ensure all node references are valid

Files updated:
- tests/unit/test_annotation_validation.py (8 tests)

Strategy: FIX (mechanical change, SPECs unchanged)
Root Cause: Comprehensive validation expects complete graph
Result: All 8 tests pass

Unit: Test Repair WU2.5.3 (taskTestRepair Phase 4)
See: docs/wip/S030_PLAN → WU2.4 → Repair Group 3
```

### Repair Group 4: Status Logic Fixtures - 7 tests (FIX)

**Root Cause:** calculate_status() now runs comprehensive validation (from WU2), expects complete graph + graph-index.json

**Source Groups:**
- Group 7: Status Logic (7 tests)

**Files Affected:**
- `tests/unit/test_status_logic.py` (7 tests)

**Strategy:** FIX (mechanical)

**Repair Actions:**
1. Use `create_test_graph()` helper from Repair Group 1
2. Create graph-index.json in all test fixtures
3. Add subsystem definitions
4. Handle validation results in status output
5. Update assertions for validation section in status

**Decision Criteria (FIX vs REWRITE):**
- Would you write the same test today? **YES** - Status now includes validation (expected)
- Tests verify status logic, just need to handle new validation output

**Batch Commit Message:**
```
test(cli): fix status logic fixtures (Repair Group 4 - 7 tests)

Updated status tests to create complete graph structures with validation.
Status command now runs comprehensive validation (WU2 integration).

Changes:
- Use create_test_graph() helper for complete fixtures
- Create graph-index.json in all test setups
- Add subsystem definitions
- Update assertions for validation in status output
- Handle validation errors/warnings in test expectations

Files updated:
- tests/unit/test_status_logic.py (7 tests)

Strategy: FIX (mechanical change, SPECs unchanged)
Root Cause: calculate_status() now includes comprehensive validation
Result: All 7 tests pass

Unit: Test Repair WU2.5.4 (taskTestRepair Phase 4)
See: docs/wip/S030_PLAN → WU2.4 → Repair Group 4
```

### Repair Group 5: Nested Subsystems Fixtures - 7 tests (FIX)

**Root Cause:** Tests create nodes with subsystem references but no subsystem definitions + missing graph-index.json

**Source Groups:**
- Group 8: Nested Subsystems (7 tests)

**Files Affected:**
- `tests/unit/test_nested_subsystems.py` (7 tests)

**Strategy:** FIX (mechanical)

**Repair Actions:**
1. Use `create_test_graph()` helper with subsystems parameter
2. Create subsystem hierarchy definitions
3. Create graph-index.json with subsystems section
4. Ensure all node subsystem paths are valid
5. Verify nested subsystem validation works

**Decision Criteria (FIX vs REWRITE):**
- Would you write the same test today? **YES** - Subsystem validation unchanged
- Tests verify nested subsystems, just need proper subsystem definitions

**Batch Commit Message:**
```
test(core): fix nested subsystem fixtures (Repair Group 5 - 7 tests)

Updated nested subsystem tests to create complete subsystem hierarchies.
Tests now create subsystem definitions + graph-index.json.

Changes:
- Use create_test_graph() with subsystems parameter
- Create subsystem hierarchy in fixtures
- Add subsystems section to graph-index.json
- Ensure all node subsystem paths are valid
- Verify nested validation works correctly

Files updated:
- tests/unit/test_nested_subsystems.py (7 tests)

Strategy: FIX (mechanical change, SPECs unchanged)
Root Cause: Validation requires complete subsystem definitions
Result: All 7 tests pass

Unit: Test Repair WU2.5.5 (taskTestRepair Phase 4)
See: docs/wip/S030_PLAN → WU2.4 → Repair Group 5
```

## Grouping Summary

**Total Groups:** 5 (consolidated from 9)

| Group | Tests | Strategy | Root Cause | Repair Action |
|-------|-------|----------|------------|---------------|
| 1: Graph Index Fixtures | 55 | FIX | Missing graph-index.json | Create helper, update tests |
| 2: Format Migration | 8 | FIX | YAML→JSON migration | Convert format in tests |
| 3: Annotation Validation | 8 | FIX | Stricter validation | Use helper for complete fixtures |
| 4: Status Logic | 7 | FIX | Status includes validation | Use helper + update assertions |
| 5: Nested Subsystems | 7 | FIX | Missing subsystem defs | Use helper with subsystems |
| **TOTAL** | **85** | **100% FIX** | | |

## Batch Repair Plan

**Execution Order:**
1. **Phase 0 (Foundational):** Create `tests/helpers/graph_fixtures.py` helper
2. **Phase 1:** Repair Group 1 (55 tests) - enables other groups
3. **Phase 2:** Repair Group 2 (8 tests) - format migration
4. **Phase 3:** Repair Group 3 (8 tests) - uses helper from Phase 1
5. **Phase 4:** Repair Group 4 (7 tests) - uses helper from Phase 1
6. **Phase 5:** Repair Group 5 (7 tests) - uses helper from Phase 1

**One commit per group** (6 commits total: 1 helper + 5 groups)

**Quality Standards:**
- No shims, no feature flags, no backwards compatibility code
- Every test uses `create_test_graph()` helper (consistency)
- All tests pass after each group repair
- Commit messages follow JIG format with strategy and root cause

## Decision Rationale

**#DECISION "Consolidate 9 groups into 5 repair groups"**
**Choice:** Merge groups with same root cause and repair action
**Rationale:** Reduces duplication, enables single helper to fix multiple groups
**Tradeoffs:** Larger commits per group, but clearer repair strategy

**#DECISION "Create single test fixture helper for all groups"**
**Choice:** `create_test_graph()` in `tests/helpers/graph_fixtures.py`
**Rationale:** All repairs need graph-index.json generation - single source of truth
**Tradeoffs:** Helper function complexity vs. duplicated fixture code
**Result:** Maintainable, reusable, consistent across all tests

**#LEARNED "Stricter validation requires stricter test fixtures"**
Validation now comprehensive (from WU2) - tests cannot use minimal fixtures anymore. Every test that loads a graph needs:
1. Markdown node files (outcomes, specs, etc.)
2. graph-index.json with complete structure
3. Subsystem definitions (if nodes reference subsystems)
4. Valid references (no dangling edges)

**#LEARNED "Clean breaks enable batch fixes"**
By removing YAML fallback (clean break), all failures follow same pattern. This enables systematic batch fixes with clear commit boundaries. Gradual migration would have created messy failure patterns.

---

### Work Unit 2.5: Execute Repairs (Batch Fixes)

**Goal:** Apply FIX/REWRITE/DELETE strategy to each group, one commit per group.

**Planned Effort:** 3-5 hours

**Acceptance Criteria:**
- All test groups repaired using assigned strategy
- Test fixture helpers created (if needed)
- All repaired tests have `@jig T-XXX verifies:S-YYY` annotations
- One commit per group with clear strategy in message
- No shims, no adapters, no backwards compatibility code
- All tests in each group pass after repair
- Running test count maintained (accounting for deletes)

**Implementation Notes:**

**Phase 1: Create Test Fixture Helpers (foundational)**
```python
# tests/helpers/graph_fixtures.py

def create_test_graph(tmp_path, nodes_spec, subsystems=None):
    """Create a complete valid graph structure for testing.

    Args:
        tmp_path: pytest tmp_path fixture
        nodes_spec: List of (id, type, title, subsystem, edges) tuples
        subsystems: List of subsystem names to create

    Returns:
        Path to graph root directory
    """
    # Create directory structure
    # Create subsystem nodes
    # Create intent nodes (outcomes, specs, etc)
    # Create graph-index.json
    # Return graph root path
```

**Phase 2: Fix Group 1 - Graph Index Fixtures (~30 tests)**
- Update all graph loading tests to use `create_test_graph()` helper
- Ensure graph-index.json exists in test fixtures
- Strategy: FIX (mechanical, add fixture helper calls)

**Commit:**
```bash
git commit -m "test(core): fix graph loading tests with proper fixtures (Group 1)

Fixed 30 tests to use create_test_graph() helper.
All tests now create graph-index.json in fixtures.

Strategy: FIX (mechanical change, SPECs unchanged)
Root Cause: Tests created minimal fixtures, validation now requires index
Result: All Group 1 tests pass

Unit: Test Repair WU2.5.1 (taskTestRepair Phase 4)
See: docs/wip/S030_PLAN → WU2.5"
```

**Phase 3: Fix Group 2 - Status Logic Tests (~7 tests)**
- Update test_status_logic.py to use `create_test_graph()` helper
- Ensure tests create complete graph structures (not minimal fixtures)
- Strategy: FIX

**Commit:**
```bash
git commit -m "test(cli): fix status logic tests with complete fixtures (Group 2)

Fixed 7 tests to use complete graph structures.
Updated fixtures to create subsystems, index, etc.

Strategy: FIX (mechanical change, SPECs unchanged)
Root Cause: calculate_status() now runs comprehensive validation
Result: All Group 2 tests pass

Unit: Test Repair WU2.5.2"
```

**Phase 4: Fix Group 3 - Validator Tests (~6 tests)**
- Update test_validator.py to create proper graph structures
- Strategy: FIX

**Commit:**
```bash
git commit -m "test(core): fix validator tests with proper graph fixtures (Group 3)

Fixed 6 tests to create graph-index.json in fixtures.
Updated to use create_test_graph() helper.

Strategy: FIX (mechanical change, SPECs unchanged)
Result: All Group 3 tests pass

Unit: Test Repair WU2.5.3"
```

**Phase 5: Fix Group 4 - Subsystem Path Validation (~20+ tests)**
- Update tests that create nodes with subsystem="core"
- Ensure test fixtures create matching subsystem nodes
- Strategy: FIX

**Commit:**
```bash
git commit -m "test(core): fix subsystem path validation tests (Group 4)

Fixed 20+ tests to create subsystem definitions in fixtures.
Tests creating nodes with subsystem='core' now create core subsystem.

Strategy: FIX (mechanical change, SPECs unchanged)
Root Cause: validate_nested_subsystems() now validates subsystem paths
Result: All Group 4 tests pass

Unit: Test Repair WU2.5.4"
```

**Phase 6: Delete Group 5 - Obsolete Tests (if any)**
- Delete any tests classified as Bucket C
- Strategy: DELETE

**Quality Standards:**
- No shims, no feature flags, no backwards compatibility
- Every test has `@jig T-XXX verifies:S-YYY subsystem:name` annotation
- Test fixture helpers are reusable and well-documented
- Commit messages explain strategy and root cause

**Test Plan:**
```bash
# After each group fix
pytest tests/unit/test_<group>.py -v

# After all groups
pytest tests/unit/ -v
# Should show 0 failures (or <5 if some skipped for WU3+)
```

**Docs to Update:**
- Add test fixture helpers documentation
- Update CONTRIBUTING.md with fixture usage examples (if needed)

**Reflect:**
- Groups fixed: **Phase 0 complete**, Phase 1 partial (24/55 tests - 1/7 files complete)
- Tests passing: 24/55 in Group 1 (44% - test_graph_commands.py ✓)
- Fixture helpers created: `tests/helpers/graph_fixtures.py::create_test_graph()`
- Challenges encountered:
  - Helper successfully fixed all 24 tests in test_graph_commands.py
  - Fixed subsystem filtering by generating proper subsystems dict with node lists
  - Remaining 6 files need different approach:
    * test_graph_traversal.py uses edge-centric format (edges list separate from nodes)
    * Other files (31 tests) need similar conversions
  - Estimated 2-3 hours remaining to complete Group 1
- Status: **IN PROGRESS** - WU2.5.1 partial, requires continuation
- Progress: test_graph_commands.py (24/24 ✓), 6 files remaining (31 tests pending)

---

### Work Unit 2.6: Validation & Integration

**Goal:** Verify test suite is healthy, JIG-aligned, and ready for WU3.

**Planned Effort:** 30-60 minutes

**Acceptance Criteria:**
- Full test suite passes: `pytest tests/unit/ -v` shows 0 failures
- All tests have `@jig T-XXX verifies:S-YYY` annotations (or path to completion)
- `jigy index rebuild` succeeds
- `jigy status` passes (no validation errors)
- Test count healthy (within 5% of baseline, accounting for deletes)
- Coverage >80% on all subsystems (or documented plan to reach)
- No commented-out tests in codebase
- No anti-patterns (shims, TODOs, temporary fixes)

**Implementation Notes:**

**Validation Checklist:**
```markdown
## WU2.6 Validation Results

### Test Suite Health
- [ ] Full test suite passes: `pytest tests/unit/ -v`
- [ ] Test count: ____ tests (baseline: ~365, expected: ~360-365)
- [ ] Failure rate: 0% (target: 0%)

### JIG Alignment
- [ ] All tests have `@jig` annotations (or documented in TODO)
- [ ] `jigy index rebuild` succeeds
- [ ] `jigy status` shows healthy graph (0 errors)
- [ ] No orphaned test nodes in graph

### Code Quality
- [ ] No commented-out tests: `grep -r "# def test_" tests/` (should be empty)
- [ ] No TODO comments: `grep -r "# TODO.*test" tests/` (should be empty)
- [ ] No shims or adapters added
- [ ] Test fixture helpers documented

### Coverage (if measurable)
- [ ] Overall coverage: __% (target: >80%)
- [ ] Core module coverage: __% (target: >80%)
- [ ] CLI module coverage: __% (target: >80%)
```

**Anti-Pattern Search:**
```bash
# Search for commented-out tests
grep -r "# def test_" tests/

# Search for TODO markers
grep -r "# TODO" tests/ | grep -i test

# Search for temporary fixes
grep -r "FIXME\|HACK\|XXX" tests/

# All should return empty or have documented reasons
```

**Final Verification:**
```bash
# Full test suite
pytest tests/unit/ -v > test-final.txt
grep -E "(PASSED|FAILED|ERROR)" test-final.txt | tail -20

# JIG validation
jigy index rebuild
jigy status

# Coverage (optional, if pytest-cov installed)
pytest tests/unit/ --cov=jig --cov-report=term-missing
```

**Completion Summary Template:**
```markdown
## Test Repair Completion Summary (WU2.1-2.6)

### Baseline (from WU2.1)
- Total tests: 365
- Failing: 85 (23.3%)
- Passing: 280 (76.7%)

### Classification (from WU2.2)
- Bucket A (align): ___ tests
- Bucket B (create SPEC): ___ tests
- Bucket C (delete): ___ tests
- Bucket D (skip - TDD): ___ tests
- Bucket E (debug - CODE bug): ___ tests

### Strategy Execution (from WU2.5)
- FIX: ___ tests (mechanical changes)
- REWRITE: ___ tests (deleted old, wrote new per SPEC)
- DELETE: ___ tests (obsolete features)
- SKIP: ___ tests (CODE not implemented)
- DEBUG: ___ tests (redirected to DEBUG workflow)

### Test Fixture Helpers Created
- `tests/helpers/graph_fixtures.py::create_test_graph()` - Build valid graph for tests
- [Other helpers if created]

### Final State (from WU2.6)
- Total tests: ___ (expected: ~360-365)
- Passing: ___ (target: 100%)
- Failing: 0 (target: 0)
- SPEC coverage: ___% have @jig annotations
- JIG validation: PASS/FAIL

### Key Decisions
#DECISION "Fix test fixtures vs make validation opt-in"
**Choice:** Fix test fixtures (create helpers)
**Rationale:** Validation strictness is correct, tests need proper fixtures
**Tradeoffs:** More work now, but durable test suite

### Key Learnings
#LEARNED "Comprehensive validation requires comprehensive test fixtures"
Tests can't use minimal fixtures when validation is strict.
Created reusable helpers to build valid graph structures.

#LEARNED "Group by root cause for batch fixes"
Identified 4-5 groups covering ~85 tests. Batch strategy 10x faster.

### Time Investment
- WU2.1 (Stop Bleeding): ___ min
- WU2.2 (SPEC Audit): ___ hr
- WU2.3 (Create SPECs): ___ hr (or N/A)
- WU2.4 (Root Cause Grouping): ___ hr
- WU2.5 (Execute Repairs): ___ hr
- WU2.6 (Validation): ___ min
- **Total: ___ hours** (estimated: 3-4 hr)

### Markers Captured
- #DISCOVERY: ___ markers
- #DECISION: ___ markers
- #LEARNED: ___ markers

### Ready for WU3
- [x] All tests pass
- [x] No failing tests block WU3 work
- [x] Test fixtures support stricter validation
- [x] Can proceed with flag implementation
```

**Test Plan:**
- Run full test suite and verify 0 failures
- Run JIG validation and verify healthy graph
- Review code for anti-patterns

**Docs to Update:**
- Add completion summary to this PLAN document (after WU2.6)
- Update S032_RETROSPECTIVE with resolution notes

**Reflect:**
- Test suite health: (PASS/FAIL)
- Blockers for WU3: (any remaining issues)
- Confidence level: (ready to proceed?)

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
- Units: 12 total (excluding WU0)
  - Original: 6 units (WU1-WU6)
  - Test Recovery: 6 units (WU2.1-WU2.6)
- Estimated total effort: 10-13 hours
  - Original work: 6-9 hours
  - Test recovery: 4-6 hours (WU2.1-2.6)
- Median cycle time: (to be measured)
- Rework rate: (to be measured)
- Test coverage: (to be measured)
- Markers captured: (to be counted)
- Files deleted: 3+ (validate.py, test files)
- Tests repaired: ~85 tests (from WU2 test suite breakage)

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

