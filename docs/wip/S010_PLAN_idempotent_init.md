---
delta_type: plan
branch: feat/idempotent-init
---

# PLAN: Idempotent `jigy init` Command

- **SCOPE:** Make `jigy init` idempotent - allow re-running to verify/repair JIG structure instead of erroring
- **Start:** 2025-11-21
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** cli

## Known Intent (Created Before Coding)

**Outcomes Created:**
- O-CLI-001: "Users can safely run jigy init multiple times" (jig/outcomes/O-CLI-001.md)
- O-CLI-002: "Missing JIG structure components are automatically repaired" (jig/outcomes/O-CLI-002.md)

**Specifications Created:**
- S-CLI-003: "jigy init verifies and repairs missing directories" (jig/specifications/S-CLI-003.md)
- S-CLI-004: "jigy init verifies and repairs missing config files" (jig/specifications/S-CLI-004.md)
- S-CLI-005: "jigy init reports created vs repaired components" (jig/specifications/S-CLI-005.md)

**Rationale:** These constraints are clear from the current issue - users expect init to be idempotent (standard CLI practice). This enables O→S→TDD flow.

## Work Unit Checklist
- [x] WU0: Create known Intent nodes (O/S) — done ✅
- [x] WU1: Refactor init.py for idempotent directory creation — tests ✅ / docs ✅ / reflect ✅
- [x] WU2: Implement idempotent file creation/verification — tests ✅ / docs ✅ / reflect ✅ (combined with WU1)
- [x] WU3: Update user feedback messages — tests ✅ / docs ✅ / reflect ✅ (combined with WU1)
- [x] WU4: Add integration tests for idempotent behavior — tests ✅ / docs ☐ / reflect ☐
- [ ] WU5: Update documentation — tests ☐ / docs ☐ / reflect ☐

## Work Units

### Work Unit 0: Create Known Intent

**Goal:** Capture all known Outcomes and Specifications before coding.

**Acceptance Criteria:**
- All known "why" statements → Outcome nodes in jig/outcomes/
- All known "what" requirements → Specification nodes in jig/specifications/
- All nodes have proper YAML frontmatter and markdown content
- `jigy validate` passes

**Created Nodes:**
- O-CLI-001.md: User can safely re-run init
- O-CLI-002.md: Automatic repair of missing components
- S-CLI-003.md: Directory verification and repair
- S-CLI-004.md: Config file verification and repair
- S-CLI-005.md: User feedback on created vs repaired

**Reflect:**
- What was clear from SCOPE: User expectation for idempotency is standard CLI practice (git init, npm init) [design]
- What was ambiguous: Whether to preserve existing config files vs merge/update them [design]
  #DECISION "Never overwrite existing jig.toml"
  **Choice:** Preserve all existing files, only create missing ones
  **Rationale:** User may have customized config, overwrites would be destructive
  **Tradeoffs:** Can't auto-update config format (acceptable - migrations are separate concern)
- Discovered during node creation: [tooling]
  #DISCOVERY "graph-index.yaml maintenance is manual - could be auto-generated from directory scan"

---

### Work Unit 1: Refactor init.py for idempotent directory creation

**Goal:** Remove error-on-exists logic and implement check-and-repair for directories
**Planned Effort:** 45-60m

**Acceptance Criteria:**
- Remove lines 30-35 that exit with error if jig/ exists
- Track which directories already existed vs newly created
- Separate created/repaired lists for user feedback
- All four directories verified: outcomes, specifications, tests, constraints
- Code passes existing tests

**Implementation Notes**
- Remove early exit at line 31-35
- Replace with check: `already_initialized = jig_dir.exists()`
- Track creations in `created` and `repaired` lists
- Files: `src/jig/cli/init.py:16-91`

**Test Plan**
- Unit: Test with existing jig/ directory doesn't error
- Integration: Run init twice, second run should report "verified"
- Test files: `tests/integration/test_init_command.py`

**Docs to Update**
- Inline docstring for init() command

**Reflect (≤5 bullets; keep crisp)**

- What worked well: [implementation]
  - Separating created/repaired lists was straightforward with conditional list selection
  - Using list comprehension made tracking clean: `target_list = repaired if already_initialized else created`
  #LEARNED "Track state changes with dual lists (created/repaired) for clear user feedback"

- Implementation insight: [design]
  - Combined WU1 (directories), WU2 (files), and WU3 (messages) into single refactor
  - All three needed to work together for functional code
  #DECISION "Implement WU1-3 together vs incrementally"
  **Choice:** Implement together in WU1
  **Rationale:** Partial implementation would break existing functionality
  **Tradeoffs:** Larger WU than planned, but code stays functional throughout

- Testing discovery: [tests]
  - Existing test expected failure on second run (assert exit_code == 1)
  - Updated to expect success (exit_code == 0) with verification message
  - Added repair test to verify missing components are restored

- User experience win: [ux]
  - Three clear scenarios: "Initialized" / "Verified" / "Repaired"
  - Messages are concise and actionable
  - No error-like messaging for normal operations

**Links**
- MR/PR: (to be filled)
- Commit(s): d4b054e

**Human Validation**
- Commands: `jigy init` (first run), `jigy init` (second run - should verify/repair)
- Look for: No error on second run, appropriate "verified" or "repaired" messages
- ✅ Validated: All scenarios tested manually and via integration tests

---

### Work Unit 2: Implement idempotent file creation/verification

**Goal:** Verify and repair graph-index.yaml, subsystems.yaml, jig.toml if missing
**Planned Effort:** 45-60m
**Status:** ✅ COMPLETE (implemented with WU1)

**Acceptance Criteria:**
- ✅ Check existence of each file before creating
- ✅ Create with default content if missing (repair case)
- ✅ Skip if exists (don't overwrite user data)
- ✅ Track repairs separately from initial creation
- ✅ Special handling: jig.toml never overwritten once created

**Implementation Notes**
- Check each file: `if not file_path.exists():`
- Create with standard defaults if missing
- Add to appropriate list (created vs repaired)
- Files: `src/jig/cli/init.py:44-75`

**Test Plan**
- ✅ Unit: Test file creation skips existing files
- ✅ Integration: Delete graph-index.yaml, run init, verify it's recreated
- ✅ Integration: Delete constraints/ dir, run init, verify repair
- ✅ Test files: `tests/integration/test_init_command.py::test_init_repairs_missing_components`

**Docs to Update**
- None (internal logic)

**Reflect (≤5 bullets; keep crisp)**
- Implemented together with WU1 - see WU1 reflect for details
- File verification follows same pattern as directory verification
- Preserving existing jig.toml is critical for user data safety

**Links**
- MR/PR: (to be filled)
- Commit(s): (to be filled)

**Human Validation**
- Commands: 
  1. `jigy init` (first time)
  2. `rm jig/graph-index.yaml jig/constraints`
  3. `jigy init` (repair run)
  4. `jigy validate` (should clear warnings)
- Look for: Missing components recreated, warnings cleared

---

### Work Unit 3: Update user feedback messages

**Goal:** Provide clear, helpful feedback distinguishing init vs verify vs repair
**Planned Effort:** 30-45m
**Status:** ✅ COMPLETE (implemented with WU1)

**Acceptance Criteria:**
- ✅ First run (new init): "✓ Initialized JIG in <path>" with created list
- ✅ Subsequent run (all exists): "✓ JIG structure verified - all components present"
- ✅ Repair run (some missing): "✓ Repaired JIG structure" with repaired list
- ✅ Messages are clear and actionable
- ✅ No confusing "Error: already initialized" message

**Implementation Notes**
- Three message paths based on state:
  1. `not already_initialized` → "Initialized" + created list
  2. `already_initialized and repaired` → "Repaired" + repaired list
  3. `already_initialized and not repaired` → "verified - all present"
- Files: `src/jig/cli/init.py:77-92`

**Test Plan**
- ✅ Integration: Verify each message appears in appropriate scenario
- ✅ Test files: `tests/integration/test_init_command.py` (multiple tests verify messages)

**Docs to Update**
- None (user-facing messages are self-documenting)

**Reflect (≤5 bullets; keep crisp)**
- Implemented together with WU1 - see WU1 reflect for details
- Three-way conditional (if/elif/else) makes message logic clear
- Manual testing confirmed all three scenarios produce expected output

**Links**
- MR/PR: (to be filled)
- Commit(s): (to be filled)

**Human Validation**
- Commands: Test all three scenarios manually
- Look for: Clear, helpful messages in each case

---

### Work Unit 4: Add integration tests for idempotent behavior

**Goal:** Ensure idempotent behavior is properly tested and won't regress
**Planned Effort:** 60-75m
**Status:** ✅ COMPLETE

**Acceptance Criteria:**
- ✅ Test: init twice in same directory succeeds both times
- ✅ Test: init after deleting directories repairs them
- ✅ Test: init after deleting files repairs them
- ✅ Test: verify appropriate messages in each scenario
- ✅ All tests pass with good coverage

**Implementation Notes**
- Updated existing test_init_command.py
- Test cases implemented:
  1. ✅ `test_init_idempotent` - updated to expect success on second run
  2. ✅ `test_init_repairs_missing_components` - new test for repair scenario
- Files: `tests/integration/test_init_command.py`

**Test Plan**
- ✅ Run full test suite: `pytest tests/integration/test_init_command.py -v` - 9 passed in 0.18s
- ✅ Manual testing verified all three scenarios (init/verify/repair)

**Docs to Update**
- None (test code)

**Reflect (≤5 bullets; keep crisp)**

- Testing insight: [tests]
  - Existing test had opposite expectation (expected failure, now expects success)
  - Test naming stayed accurate: "idempotent" now truly tests idempotency
  #DISCOVERY "Legacy test encoded old non-idempotent behavior as expectation"

- Test coverage: [quality]
  - Added repair test using shutil.rmtree and Path.unlink to simulate deletion
  - Tests verify both behavior (exit code 0) and user feedback (message content)
  
- Performance: [perf]
  - All 9 tests pass in 0.18s (well under performance budget)
  - Idempotent operations don't add measurable overhead

**Links**
- MR/PR: (to be filled)
- Commit(s): (to be filled)

**Human Validation**
- Commands: `pytest tests/integration/test_init_command.py -v`
- Look for: All tests pass, good coverage of edge cases

---

### Work Unit 5: Update documentation

**Goal:** Document the idempotent behavior in relevant places
**Planned Effort:** 30m

**Acceptance Criteria:**
- Update init command docstring with idempotent behavior
- Add note in README about safe re-running
- Update any tutorials that mention init
- Clear communication of verify/repair functionality

**Implementation Notes**
- Files to update:
  - `src/jig/cli/init.py` docstring (lines 17-24)
  - `README.md` - Quick Start section
  - Check `docs/tutorials/` for any init references

**Test Plan**
- Manual review of documentation
- Verify examples are accurate

**Docs to Update**
- README.md: Quick Start section
- src/jig/cli/init.py: Command docstring
- Any tutorials mentioning init

**Reflect (≤5 bullets; keep crisp)**
- (To be filled after implementation)

**Links**
- MR/PR: (to be filled)
- Commit(s): (to be filled)

**Human Validation**
- Commands: Read through updated docs
- Look for: Clear explanation of idempotent behavior

---

## Summary
(To be filled on completion)

## Metrics
(To be filled on completion)

## Reflection Roll-up
(To be filled on completion)

## Harvest Preparation (JIG)
(To be filled on completion)

