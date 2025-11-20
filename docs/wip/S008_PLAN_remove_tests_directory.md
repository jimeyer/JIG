---
delta_type: plan
branch: remove-tests-directory
scope: docs/wip/S007_SCOPE_remove_tests_directory.md
---

# PLAN: Remove jig/tests/ Directory and Test Node Type

- **SCOPE:** docs/wip/S007_SCOPE_remove_tests_directory.md
- **Start:** 2025-11-20
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** core (parser, validator, graph loading)

## Known Intent (Created Before Coding)

**Rationale from SCOPE:**

The `jig/tests/` directory and `type: test` node type are redundant in the JIG v7 OSTCX architecture. The model explicitly separates:
- **O/S/X nodes**: Markdown files (timeless intent, system properties)
- **T/C nodes**: Annotations in code (executable reality)

Tests represent "Empirical truth (verify)" and should be discovered via `@jig` annotations in test code, not stored as markdown files. This PLAN implements that architectural principle.

**Outcomes (Already Exist):**
- O-JIG-002: "JIG v7 OSTCX model implemented" (jig/outcomes/O-JIG-002.md)
  - This work contributes to v7 architectural alignment

**Specifications (To Be Created or Referenced):**
- S-JIG-002: "OSTC node parsing" (exists, needs update for OSX markdown-only)
- S-JIG-005: "Test nodes discovered via annotations" (NEW - to be created in WU0)
- S-JIG-006: "Graph loads O/S/X markdown nodes only" (NEW - to be created in WU0)

**Constraints (Already Exist):**
- C-PERF-001: "Graph loading <1 second for 1k nodes" (jig/constraints/C-PERF-001.md)
  - Removing test directory scanning helps maintain this

## Work Unit Checklist
- [x] WU0: Create known Specification nodes (S-JIG-005, S-JIG-006) — tests ☑ / docs ☑ / reflect ☑
- [x] WU1: Remove test type from validator and parser — tests ☑ / docs ☑ / reflect ☑
- [ ] WU2: Remove test directory from graph loading — tests ☐ / docs ☐ / reflect ☐
- [ ] WU3: Remove test type from CLI node creation — tests ☐ / docs ☐ / reflect ☐
- [ ] WU4: Delete test template and directory — tests ☐ / docs ☐ / reflect ☐
- [ ] WU5: Update test suite (remove test node tests) — tests ☐ / docs ☐ / reflect ☐
- [ ] WU6: Update documentation (README, agents) — tests ☐ / docs ☐ / reflect ☐

---

## Work Units

### Work Unit 0: Create Known Specification Nodes

**Goal:** Capture the architectural constraints from SCOPE as Specification nodes before implementation.

**Planned Effort:** 30m

**Acceptance Criteria:**
- [x] S-JIG-005.md created in jig/specifications/
- [x] S-JIG-006.md created in jig/specifications/
- [x] Both specs reference O-JIG-002 (implements)
- [x] Both specs have proper YAML frontmatter
- [x] `jig validate` passes

**Implementation Notes:**

S-JIG-005: "Test nodes discovered via @jig annotations"
- Why: T nodes represent executable tests, not intent documents
- What: Test nodes (T-XXX) exist in graph but are discovered from `@jig T-XXX` annotations in test code
- Storage: Annotations with `verifies:` relations
- Rationale: Tests are code; source of truth is the implementation

S-JIG-006: "Graph loads O/S/X markdown nodes only"
- Why: OSTCX model separates markdown intent (O/S/X) from annotation-based reality (T/C)
- What: `Graph.load_from_dir()` scans only outcomes/, specifications/, constraints/ directories
- Storage: node_dirs = ["outcomes", "specifications", "constraints"]
- Rationale: T/C nodes discovered via future annotation scanning feature

**Reflect:**

- What was clear from SCOPE:
  - Architectural rationale (OSTCX model separation)
  - Specific files to modify
  - Zero risk (no existing usage of test markdown files)

- What was ambiguous:
  - Whether to update S-JIG-002 or create new specs (decided: create new, S-JIG-002 is about parsing, these are about discovery/loading)

**Completed 2025-11-20:**

- What worked well:
  - Template format was easy to follow from S-JIG-001 example
  - Both specs created with clear requirements and rationale
  - Validation passed on first try (16 nodes total)
  - Specs clearly capture architectural constraints before implementation

- Discoveries:
  - CLI command is `jigy` (via .venv/bin/jigy), confirmed in pyproject.toml
  - Validation shows warnings but passes (5 warnings for 16 nodes)

---

### Work Unit 1: Remove Test Type from Validator and Parser

**Goal:** Remove `type: test` from VALID_TYPES and update related validation logic to reflect markdown-only node types (O/S/X).

**Planned Effort:** 45m

**Acceptance Criteria:**
- [x] `VALID_TYPES` in validator.py contains only {"outcome", "specification", "constraint"}
- [x] `TYPE_PREFIX_MAP` updated (test type removed)
- [x] Validation error messages reference OSTCX model
- [x] OSTCNode docstring updated to clarify O/S/X markdown nodes
- [x] Unit tests pass: test_validator.py
- [x] No test type validation tests remain

**Implementation Notes:**

Files to modify:
- `src/jig/core/validator.py` (Lines 29, 32-36)
  - Remove "test" from VALID_TYPES
  - Remove "test": "T" from TYPE_PREFIX_MAP
  - Update error messages: "Valid types for markdown nodes: outcome, specification, constraint"
  
- `src/jig/core/parser.py` (Line 18)
  - Update OSTCNode docstring: "Parses O/S/X markdown nodes (T/C are annotation-based)"
  - Keep name `OSTCNode` per SCOPE decision (reflects broader OSTCX model)

**Test Plan:**

Unit tests to update:
- `tests/unit/test_validator.py`
  - Remove tests validating `type: test` frontmatter
  - Add test: validate rejects test type with helpful error
  - Verify error message mentions OSTCX model and annotations

Expected test changes:
- Remove: ~3-5 tests for test node validation
- Add: 1 test for helpful error message

**Docs to Update:**
- Code comments explaining OSTCX model split

**Reflect (≤5 bullets; keep crisp)**

**Completed 2025-11-20:**

- What worked well:
  - Clean removal of test type from VALID_TYPES and TYPE_PREFIX_MAP
  - Helpful error message guides users to annotations and JIG-Concept-v7.md
  - All 186 tests pass (25 validator tests, 0 failures)
  - Updated test validates helpful error message correctly

- Discoveries:
  - Existing T-UNIT-001.md now correctly rejected by validation (expected until WU4)
  - Error message format is clear: "Invalid type: 'test'. Valid types for markdown nodes: constraint, outcome, specification. Test nodes (T) must use @jig annotations in test code."

**Links:**
- Commit(s): 70720fd

**Human Validation:**
- Commands: `pytest tests/unit/test_validator.py -v`, `jigy validate`
- Look for: All tests pass, error message is clear and helpful

---

### Work Unit 2: Remove Test Directory from Graph Loading

**Goal:** Remove "tests" from node_dirs in Graph.load_from_dir() so graph only loads O/S/X markdown nodes.

**Planned Effort:** 30m

**Acceptance Criteria:**
- [ ] `node_dirs` in graph.py contains only ["outcomes", "specifications", "constraints"]
- [ ] Comment explains OSTCX model: "T/C nodes discovered via annotations (future)"
- [ ] Graph loading no longer attempts to scan jig/tests/
- [ ] Unit tests pass: test_graph.py
- [ ] Integration tests pass: test_graph_*.py

**Implementation Notes:**

Files to modify:
- `src/jig/core/graph.py` (Line 89)
  ```python
  # Before:
  node_dirs = ["outcomes", "specifications", "constraints", "tests"]
  
  # After:
  # Load only markdown-based nodes (O/S/X in OSTCX model)
  # T/C nodes discovered via @jig annotations (future feature)
  node_dirs = ["outcomes", "specifications", "constraints"]
  ```

**Test Plan:**

Unit tests to update:
- `tests/unit/test_graph.py`
  - Update test_load_from_dir to expect 3 directories, not 4
  - Verify no tests/ directory scanning occurs
  - Ensure graceful handling if jig/tests/ exists (ignore, don't error)

Integration tests to verify:
- `tests/integration/test_graph_*.py`
  - All graph operations work without test directory
  - No regression in graph loading performance

**Docs to Update:**
- Inline comments in graph.py

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

- Risk watchlist:

**Links:**
- Commit(s):

**Human Validation:**
- Commands: `pytest tests/unit/test_graph.py tests/integration/test_graph*.py -v`
- Look for: All tests pass, graph loads in <1 sec

---

### Work Unit 3: Remove Test Type from CLI Node Creation

**Goal:** Remove "test" from `jigy node create` command choices and provide helpful error message.

**Planned Effort:** 30m

**Acceptance Criteria:**
- [ ] `click.Choice` in cli/node.py contains only ["outcome", "specification", "constraint"]
- [ ] Help text clarifies only O/S/X nodes can be created via CLI
- [ ] Attempting `--type test` produces clear error referencing OSTCX model
- [ ] Integration tests pass: test_node_create.py

**Implementation Notes:**

Files to modify:
- `src/jig/cli/node.py` (Line 27)
  - Remove "test" from click.Choice options
  - Update help text: "Node type (O/S/X only; T/C use @jig annotations)"
  - Error message: "Test nodes (T) must use @jig annotations in test code, not markdown files. In the OSTCX model, only O/S/X nodes use markdown. See: docs/jig-concept/JIG-Concept-v7.md§1.3"

**Test Plan:**

Integration tests to update:
- `tests/integration/test_node_create.py`
  - Remove tests creating test nodes via CLI
  - Add test: verify helpful error if user somehow passes --type test
  - Verify successful creation of O/S/X nodes still works

**Docs to Update:**
- CLI help text (inline)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

- Risk watchlist:

**Links:**
- Commit(s):

**Human Validation:**
- Commands: `jigy node create --help`, `jigy node create --type outcome --id O-TEST-001 --title "Test"`
- Look for: Help text is clear, O/S/X creation works, test type rejected with helpful message

---

### Work Unit 4: Delete Test Template and Directory

**Goal:** Remove test_template.md, T-UNIT-001.md, and jig/tests/ directory from repository.

**Planned Effort:** 15m

**Acceptance Criteria:**
- [ ] `templates/test_template.md` deleted
- [ ] `jig/tests/T-UNIT-001.md` deleted
- [ ] `jig/tests/` directory deleted (if empty)
- [ ] All tests still pass (no dependencies on these files)
- [ ] Git history preserved (normal git rm, not force)

**Implementation Notes:**

Files to delete:
- `templates/test_template.md`
- `jig/tests/T-UNIT-001.md`
- `jig/tests/` (directory, if empty after file removal)

Commands:
```bash
git rm templates/test_template.md
git rm jig/tests/T-UNIT-001.md
rmdir jig/tests  # Only if empty
```

**Test Plan:**

Tests to update:
- `tests/unit/test_templates.py`
  - Remove test_template.md validation test
  - Verify other templates (outcome, specification, constraint) still work

Verify:
- All existing tests pass without these files
- No hardcoded paths reference deleted files

**Docs to Update:**
- None (files are just deleted)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

- Risk watchlist:

**Links:**
- Commit(s):

**Human Validation:**
- Commands: `pytest tests/unit/test_templates.py -v`, `ls jig/tests` (should not exist)
- Look for: Tests pass, directory gone, no broken references

---

### Work Unit 5: Update Test Suite

**Goal:** Remove or update all tests that validate test node markdown functionality.

**Planned Effort:** 60m

**Acceptance Criteria:**
- [ ] All tests referencing test node markdown files removed or updated
- [ ] Tests validating test type in frontmatter removed
- [ ] Tests creating test nodes via CLI removed
- [ ] All remaining tests pass
- [ ] Test coverage remains >80%

**Implementation Notes:**

Files to update (per SCOPE):
- `tests/unit/test_graph.py` - Update test verifying directory scanning (expect 3 dirs, not 4)
- `tests/unit/test_templates.py` - Remove test for test_template.md
- `tests/unit/test_validator.py` - Remove tests validating `type: test`
- `tests/integration/test_node_create.py` - Remove tests creating test nodes

Strategy:
1. Run `pytest -v` to identify failing tests
2. For each failing test, decide: delete (test node specific) or update (general test affected)
3. Ensure no test depends on jig/tests/ directory existing
4. Verify graph loading tests work with 3 directories

**Test Plan:**

Verification steps:
- Run full test suite: `pytest tests/ -v`
- Check coverage: `pytest tests/ --cov=src/jig --cov-report=term-missing`
- Verify no skipped tests remain for removed features
- Ensure all integration tests pass

Expected changes:
- Remove: ~5-10 tests specific to test node markdown
- Update: ~3-5 tests that reference 4 directories → 3 directories
- Coverage should remain similar (removed feature-specific tests)

**Docs to Update:**
- None (test code only)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

- Risk watchlist:

**Links:**
- Commit(s):

**Human Validation:**
- Commands: `pytest tests/ -v --cov=src/jig`, `make test`
- Look for: All tests pass, coverage >80%, no warnings about missing fixtures

---

### Work Unit 6: Update Documentation

**Goal:** Update README, agents, and concept docs to reflect OSTCX model with markdown (O/S/X) vs annotation (T/C) split.

**Planned Effort:** 45m

**Acceptance Criteria:**
- [ ] README.md updated with OSTCX model explanation
- [ ] agents/ instructions updated (if needed)
- [ ] JIG-Concept-v7.md confirmed as reference (already correct)
- [ ] Documentation consistently uses OSTCX terminology
- [ ] No references to creating test nodes via markdown remain

**Implementation Notes:**

Files to update:

1. **README.md**
   - Update OSTC → OSTCX model description
   - Clarify: "O/S/X nodes are markdown files in jig/"
   - Clarify: "T/C nodes are @jig annotations in test/source code"
   - Add example of test annotation
   - Remove any instructions for creating test markdown files

2. **agents/jig-agent-instructions.md** (if exists)
   - Verify alignment with v7 OSTCX model
   - Update any references to test node creation
   - Ensure examples use annotations for T nodes

3. **Verify JIG-Concept-v7.md**
   - Already correct per SCOPE
   - Reference it as authoritative source
   - No changes needed

**Test Plan:**

Verification:
- Grep for outdated references: `grep -r "jig/tests" docs/ README.md`
- Grep for test node creation: `grep -r "type: test" docs/ README.md`
- Verify all OSTCX references are consistent
- Check that examples match v7 model

Manual review:
- Read updated README for clarity
- Verify no contradictions between docs and implementation

**Docs to Update:**
- README.md (primary)
- agents/ files (verify/update)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Discoveries:

- Risk watchlist:

**Links:**
- Commit(s):

**Human Validation:**
- Commands: `grep -r "jig/tests" docs/ README.md`, `grep -r "type: test" docs/`
- Look for: No outdated references, clear OSTCX explanation, consistent terminology

---

## Summary

- **Scope delivered:** Remove jig/tests/ directory and test node type from JIG codebase, aligning with v7 OSTCX architecture principle that T/C nodes use annotations, not markdown files.

- **Key decisions:**
  - Keep `OSTCNode` name (reflects broader OSTCX model, not just markdown types)
  - Remove test type validation entirely (no future markdown use planned)
  - Create S-JIG-005 and S-JIG-006 to document architectural constraints

- **Deltas from SCOPE:**
  - (To be filled during execution)

---

## Metrics

- Units: 7 (including WU0)
- Median cycle time: (TBD)
- Rework rate: (TBD)
- Flaky test events: (TBD)
- Docs lag: (TBD)
- Markers captured: (TBD)

---

## Reflection Roll-up

(To be filled at completion)

- **Repeatable wins:**
- **Systemic frictions (top 3):**
- **Process changes adopted:**
- **Open questions for next plan:**

---

## Harvest Preparation (JIG)

**Markers Summary:**
- Discoveries: (TBD)
- Decisions: (TBD)
- Learned patterns: (TBD)

**Recommended OSTC Nodes (from DISCOVERIES only):**
(To be filled based on discoveries during implementation - these are NEW constraints learned, not known upfront)

**Subsystems Touched:** core (primary: graph, validator, parser, cli)

**Next Step:** `jig ai-distill --branch remove-tests-directory`

---

**Status:** Draft - Ready for WU0 execution
**Next:** Execute Work Unit 0 (Create Specification nodes S-JIG-005, S-JIG-006)


