# Task: SPEC-Driven Test Recovery (5-Bucket Model)

**Version:** 3.0.0 (Updated: 2025-11-30)

## Objective

Recover failing test suites by re-aligning tests with Specifications using a 5-bucket classification system, ensuring every test traces to a specification and eliminating broken tests through regeneration rather than shimming.

## Context

This task exists because test suites break during refactoring, and traditional approaches (shimming old behavior, commenting out tests) create technical debt. JIG v8 provides a better way: SPECs are the source of truth, tests are reproducible code that can be regenerated from SPECs.

**Philosophy:** Tests verify Specifications, not implementations. When tests break, first ask: "What SPEC does this verify?" If the SPEC is valid, the test must align. If the SPEC is obsolete, the test must die. No shims, no adapters, no backwards compatibility.

**Core Insight:** SPECs are timeless. Tests are code. Code is cheap (especially for AI agents). Don't preserve broken tests—regenerate correct tests from SPECs.

---

## JIG v8 Foundation: The S-F-T Triangle

In JIG v8, the Alignment Graph has three core node types:

```
         S (Spec)
        ╱   ╲
       ╱     ╲
implements  verifies
     ╱         ╲
    ╱           ╲
   ▼             ▼
  F ── covers ──> T
(Function)      (Test)
```

**Key Relationships:**
- **F → S:** Functions implement Specifications (via `@jig.implements("S-001")`)
- **T → S:** Tests verify Specifications (via `@jig.verifies("S-001")`)
- **T → F:** Tests cover Functions (via coverage analysis)

**Test Annotation Pattern:**
```python
@jig.verifies("S-001")
def test_token_expiration():
    """Verify tokens expire after 15 minutes of inactivity."""
    token = authenticate("user", "pass")
    token.last_activity = datetime.now() - timedelta(minutes=15, seconds=1)
    assert is_expired(token)
```

**Critical Rule:** Every test MUST trace to a Specification. If you can't name the SPEC, the test shouldn't exist.

---

## Core Principles

### 1. SPEC-Centric Recovery
- **SPECs are source of truth** - Tests serve SPECs, not vice versa
- **Tests are reproducible** - If you have a clear SPEC, you can regenerate the test
- **Old tests aren't sacred** - Delete broken tests confidently if you have the SPEC
- **No SPEC = No test** - Unspecified behavior is undefined behavior

### 2. Five-Bucket Classification
Every failing test falls into exactly one bucket:

| Bucket | Name | Condition | Action | Example |
|--------|------|-----------|--------|---------|
| **A** | **Align** | SPEC valid, test needs fixing | FIX/REWRITE/ANNOTATE test | Constructor signature changed |
| **B** | **Create SPEC** | SPEC missing, requirement real | Create SPEC → align test | Implicit security requirement |
| **C** | **Delete** | SPEC obsolete or redundant | DELETE test entirely | Feature removed, or duplicate test |
| **D** | **Skip (TDD)** | S-F-T aligned, function missing | @pytest.mark.skip → document scope | Test written before implementation |
| **E** | **Debug** | Function bug detected | Redirect to DEBUG workflow | Test reveals function violates SPEC |

**Key Insight:** Buckets A/B/C handle SPEC lifecycle. Bucket D handles TDD scenarios. Bucket E detects bugs (redirect to DEBUG workflow).

### 3. Decision Matrix (No Shims)

**For Buckets A and B** (test needs alignment), choose ONE strategy:

| Strategy | When to Use | What to Do | Never Do |
|----------|-------------|------------|----------|
| **FIX** | Change is mechanical, result is "as good as new" | Fix the test (add param, fix import) | Add compatibility layers |
| **REWRITE** | Architecture changed, SPEC semantics evolved | Delete old test, write new test per SPEC | Try to salvage old test logic |

**For Bucket C** (SPEC obsolete):

| Strategy | Action |
|----------|--------|
| **DELETE** | Remove test entirely, regenerate graphs |

**For Bucket D** (Function missing - TDD scenario):

| Strategy | Action |
|----------|--------|
| **SKIP** | Add `@pytest.mark.skip`, document missing implementation |

**For Bucket E** (Function bug detected):

| Strategy | Action |
|----------|--------|
| **DEBUG** | Document bug, do NOT "fix" test to match buggy function |

**NEVER:**
- Add shims or adapters to make old tests pass
- Preserve backwards compatibility for obsolete SPECs
- Use feature flags to toggle test behavior
- Comment out tests "temporarily"
- "Fix" a test to match buggy function (Bucket E → DEBUG instead)

---

## The 5-Phase Recovery Workflow

### Phase 0: Stop Bleeding (30 minutes)

**Goal:** Get clean failure counts by fixing obvious blockers.

**Actions:**
1. Fix critical import errors (e.g., missing module imports)
2. Fix obvious constructor signature changes
3. Run full test suite to get accurate failure count
4. Document baseline: X tests failing out of Y total

**Output:**
```markdown
## Phase 0: Baseline
- Total tests: 1,528
- Failing: 118
- Blocked by imports: 77 (fixed)
- Clean failures: 41
- Run: `pytest -v > test-baseline.txt`
```

### Phase 1: SPEC Audit (2-3 hours)

**Goal:** Classify every failing test into Buckets A, B, C, D, or E.

**Process:**
```bash
# 1. List all failing tests
pytest --tb=no -q | grep FAILED > failing-tests.txt

# 2. For each failing test, trace to SPEC
# Create audit spreadsheet or markdown table

# 3. Classify into buckets
```

**Audit Template:**
```markdown
## SPEC Audit Results

### Bucket A: Existing SPEC (N tests)
| Test | File:Line | Verifies SPEC | Status | Notes |
|------|-----------|---------------|--------|-------|
| test_token_validation | test_auth.py:42 | S-001 | Missing @jig decorator | Add @jig.verifies("S-001") |
| test_token_expiry | test_auth.py:58 | S-001 | Needs update | Constructor changed |

### Bucket B: Missing SPEC (N tests)
| Test | File:Line | Needs SPEC | Brick | Rationale |
|------|-----------|------------|-------|-----------|
| test_constant_time_compare | test_crypto.py:120 | S-005 | B-003 | Security requirement, was implicit |
| test_device_id_uniqueness | test_auth.py:205 | S-004 | B-001 | Edge case not documented |

### Bucket C: Obsolete SPEC (N tests)
| Test | File:Line | Obsolete Feature | Decision |
|------|-----------|------------------|----------|
| test_flat_map_merge | test_crdt.py:88 | Flat-map removed | DELETE (replaced by OR-Map) |
| test_legacy_token_format | test_auth.py:310 | Pre-v2 tokens | DELETE (no migration needed) |

### Bucket D: Function Missing - TDD Scenario (N tests)
| Test | File:Line | Verifies SPEC | Function Status | Notes |
|------|-----------|---------------|-----------------|-------|
| test_mfa_token_validation | test_auth.py:505 | S-007 | Not implemented | Document missing function |
| test_device_enrollment | test_auth.py:520 | S-008 | Not implemented | Document missing function |

### Bucket E: Function Bug Detected (N tests)
| Test | File:Line | Verifies SPEC | Bug Description | Action |
|------|-----------|---------------|-----------------|--------|
| test_device_id_uniqueness | test_auth.py:205 | S-004 | Generates duplicate IDs | Document bug, fix function |
| test_token_expiry_timing | test_auth.py:175 | S-003 | Tokens expire 1hr early | Document bug, fix function |
```

**Notes:**
- Found 23 tests with no traceable SPEC (Bucket B) - tests were written against implementation, not requirements
- Found 8 tests where function not implemented yet (Bucket D - TDD) - tests exist, SPECs exist, but function missing
- Found 2 function bugs during test audit (Bucket E) - tests correctly verify SPECs, but function violates SPEC
- Strategy: Create missing SPECs before fixing tests (Bucket B) for durable alignment
- Strategy: Skip Bucket D tests to preserve TDD intent; function will be implemented later

### Phase 2: Create Missing SPECs (1-2 hours)

**Goal:** For every Bucket B test, create the missing Specification.

**Process:**
1. Read the failing test to understand what it verifies
2. Extract the requirement (the "what", not the "how")
3. Create SPEC file in `jig/specifications/`
4. Link SPEC to Outcome if relevant (optional)
5. Run `jigy validate` to check format

**Example:**
```markdown
# jig/specifications/S-005.md
---
id: S-005
type: specification
---

# Token Signature Validation

JWT signature validation MUST use constant-time comparison to prevent timing attacks.

## Rationale
Variable-time comparison leaks information about signature bytes through timing side-channels.

## Acceptance Criteria
- Signature comparison completes in constant time regardless of input
- No early-exit on first differing byte
- Use `hmac.compare_digest()` or equivalent

## Related
- Outcome: O-002 ("Secure authentication without passwords")
```

**Commit:**
```bash
git add jig/specifications/
jigy index  # Regenerate intent graph
git add jig/generated/intent-graph.ndjson
git commit -m "specs: create missing SPECs for authentication and crypto

Created 5 specifications for previously implicit requirements:
- S-005: Constant-time token signature validation
- S-004: Device ID uniqueness
- S-006: Token refresh timing <100ms
- S-010: WebSocket reconnection strategy
- S-012: Conflict-free OR-Set semantics

These requirements were implemented but not specified.
Discovered during test repair audit (Phase 1)."
```

### Phase 3: Root Cause Grouping (1 hour)

**Goal:** Group Bucket A and B tests by repair strategy (FIX, REWRITE). Handle Buckets C, D, E with specific actions.

**Process:**
```markdown
## Root Cause Groups

### Group 1: Constructor Signature (FIX) - 43 tests
**Root Cause:** `Replicator()` now requires `node_id` parameter
**Strategy:** FIX (mechanical change, tests still valid)
**Files:** tests/crdt/test_*.py
**Action:** Add `node_id="test-node"` to all constructor calls

### Group 2: OR-Map Semantics (REWRITE) - 35 tests
**Root Cause:** Flat-map removed, OR-Map has different semantics
**Strategy:** REWRITE (architecture changed, old tests verify wrong SPEC)
**Files:** tests/crdt/test_map.py, test_merge.py
**Action:** Delete old tests, write new tests per S-006 (OR-Map SPEC)

### Group 3: Legacy Token Format (DELETE) - 18 tests
**Root Cause:** Pre-v2 token support removed
**Strategy:** DELETE (SPEC obsolete, no replacement)
**Files:** tests/auth/test_legacy_tokens.py
**Action:** Delete file entirely, regenerate graphs

### Group 4: Missing @jig Decorators (FIX) - 22 tests
**Root Cause:** Tests pass but lack SPEC traceability
**Strategy:** FIX (add decorators only)
**Files:** tests/*/test_*.py (scattered)
**Action:** Add `@jig.verifies("S-XXX")` decorators

### Group 5: MFA Function Not Implemented (SKIP - Bucket D) - 8 tests
**Root Cause:** Tests and SPECs exist, but function not implemented yet (TDD)
**Strategy:** SKIP (S-F-T aligned, waiting for function)
**Files:** tests/auth/test_mfa.py
**Action:** Add `@pytest.mark.skip`, document missing implementation

### Group 6: Function Bugs Detected (DEBUG - Bucket E) - 2 tests
**Root Cause:** Tests correctly verify SPECs, but function violates SPEC
**Strategy:** DEBUG (redirect to debugging, not test repair)
**Files:** tests/auth/test_device_id.py, test_token_expiry.py
**Action:** Document bugs, do NOT "fix" tests to match buggy function
```

**Notes:**
- Decision: REWRITE OR-Map tests vs FIX - chose REWRITE because semantics fundamentally different (add-wins vs last-write-wins); more work now, but tests verify correct SPEC (S-006)
- Learning: Group by root cause before fixing individual tests - identified 4 groups covering 118 tests; batch fixes are 10x faster than one-off repairs

### Phase 4: Execute Repairs (4-6 hours)

**Goal:** Apply FIX/REWRITE/DELETE strategy to each group.

**Workflow per Group:**

#### Strategy: FIX (Mechanical Changes)

```python
# BEFORE (broken)
@jig.verifies("S-003")
def test_replicator_initialization():
    """Verify replicator initializes with empty state"""
    rep = Replicator()  # Missing node_id
    assert rep.state == {}

# AFTER (fixed)
@jig.verifies("S-003")
def test_replicator_initialization():
    """Verify replicator initializes with empty state"""
    rep = Replicator(node_id="test-node")  # Added required param
    assert rep.state == {}
```

**Commit per group:**
```bash
git add tests/crdt/
jigy verify rebuild --run-tests  # Regenerate verification graph
git add jig/generated/verification-graph.ndjson
git commit -m "test(crdt): fix constructor signatures (Group 1)

Fixed 43 tests to use new Replicator(node_id=...) signature.

Strategy: FIX (mechanical change, tests still verify S-003)
Root Cause: Constructor signature changed during refactor
Result: All tests pass, semantics unchanged"
```

#### Strategy: REWRITE (Architecture Changed)

```python
# BEFORE (obsolete flat-map test)
def test_flat_map_merge():
    """Verify flat-map merges use last-write-wins"""
    map1 = FlatMap()  # No longer exists
    map1.set("key", "value1")
    map2 = FlatMap()
    map2.set("key", "value2")
    merged = map1.merge(map2)
    assert merged.get("key") == "value2"  # LWW semantics

# AFTER (new OR-Map test per SPEC)
@jig.verifies("S-006")
def test_or_map_merge_preserves_all_values():
    """Verify OR-Map merge preserves all concurrent values (add-wins)"""
    map1 = ORMap(node_id="node-1")
    map1.set("key", "value1")

    map2 = ORMap(node_id="node-2")
    map2.set("key", "value2")

    merged = map1.merge(map2)

    # OR-Map keeps both values (add-wins, not LWW)
    assert set(merged.get("key")) == {"value1", "value2"}
```

**Delete old, commit new:**
```bash
# Delete obsolete tests
rm tests/crdt/test_flat_map.py

# Write new tests per SPEC
# (Create tests/crdt/test_or_map_semantics.py)

git add tests/crdt/
jigy verify rebuild --run-tests
git add jig/generated/verification-graph.ndjson
git commit -m "test(crdt): rewrite OR-Map tests per S-006 (Group 2)

Deleted 35 flat-map tests (obsolete).
Created 28 OR-Map tests verifying add-wins semantics.

Strategy: REWRITE (architecture change, not backwards compatible)
Root Cause: Flat-map removed, OR-Map has different conflict resolution
SPECs verified: S-006 (OR-Map add-wins), S-007 (merge semantics)

New tests written from scratch per SPEC.
No attempt to salvage old test logic (burn ships)."
```

#### Strategy: DELETE (Obsolete)

```bash
# Delete tests for removed features
rm tests/auth/test_legacy_tokens.py
rm tests/utils/test_deprecated_helpers.py

# Regenerate graphs (removes orphaned test nodes)
jigy verify rebuild --run-tests

git add tests/ jig/generated/
git commit -m "test: delete obsolete legacy token tests (Group 3)

Deleted 18 tests for pre-v2 token format (no longer supported).

Strategy: DELETE (SPEC obsolete, no replacement needed)
Root Cause: Legacy token support removed (burn ships)
Decision: No migration path, clean break"
```

#### Strategy: SKIP (Bucket D - Function Missing, TDD)

```python
# Test exists, SPEC exists, but function not implemented yet
@jig.verifies("S-007")
@pytest.mark.skip(reason="Function not implemented - S-007 pending")
def test_mfa_token_validation():
    """Verify MFA tokens validate correctly (S-007)"""
    token = create_mfa_token(user_id="user-123", device_id="device-456")
    assert validate_mfa_token(token) is True

@jig.verifies("S-008")
@pytest.mark.skip(reason="Function not implemented - S-008 pending")
def test_mfa_device_enrollment():
    """Verify MFA device enrollment generates unique device IDs (S-008)"""
    device1 = enroll_mfa_device(user_id="user-123")
    device2 = enroll_mfa_device(user_id="user-123")
    assert device1.id != device2.id
```

**Document missing implementations:**

```markdown
# Add to project documentation or issue tracker

## Missing Implementations (TDD Scenario)

| SPEC | Description | Tests Waiting |
|------|-------------|---------------|
| S-007 | MFA token validation | test_mfa_token_validation |
| S-008 | Device enrollment | test_mfa_device_enrollment |
| S-009 | Backup code generation | test_mfa_backup_codes |

All SPECs exist, tests exist and are skipped, implementations pending.
```

**Commit:**
```bash
git add tests/auth/
jigy verify rebuild --run-tests
git add jig/generated/verification-graph.ndjson
git commit -m "test(auth): skip MFA tests pending function implementation (Group 5)

Skipped 8 tests for MFA feature (TDD scenario).

Strategy: SKIP (S-F-T aligned, function not implemented yet)
Root Cause: Tests written before implementation (Bucket D - TDD)

Tests have correct @jig.verifies() decorators and verify valid SPECs.
Will implement functions in future work."
```

#### Strategy: DEBUG (Bucket E - Function Bug Detected)

```markdown
# DO NOT "fix" tests to match buggy functions
# These are actual bugs discovered by tests

## Bucket E: Function Bugs Detected During Test Repair

During test audit, discovered 2 tests that correctly verify SPECs,
but functions violate SPECs (actual bugs, not test issues).

### Bug 1: Device ID Collision
- **Test:** test_device_id_uniqueness (tests/auth/test_device_id.py:205)
- **Verifies:** S-004 ("Device IDs must be globally unique")
- **Issue:** Function generates duplicate IDs (~1% collision rate)
- **Status:** Marked for debugging

### Bug 2: Token Expiry Timing
- **Test:** test_token_expiry_timing (tests/auth/test_token_expiry.py:175)
- **Verifies:** S-003 ("Tokens expire after 24 hours")
- **Issue:** Tokens expire at 23 hours (timezone calculation bug)
- **Status:** Marked for debugging

**Do NOT "fix" these tests - they are correct!**
The functions are buggy. Fix the functions, not the tests.
```

**Document and track:**
```bash
# Create issues or document bugs for future fixes
# Tests remain as-is (they're working correctly)

git commit -m "docs: identify function bugs during test repair (Group 6 - Bucket E)

Found 2 tests that correctly verify SPECs but reveal function bugs:
- test_device_id_uniqueness: Device ID collision bug (violates S-004)
- test_token_expiry_timing: Token expiry timing bug (violates S-003)

Strategy: DEBUG (fix functions, not tests)
These are NOT test failures - these are function bugs.
Tests are working as intended (catching bugs).

Will fix function bugs in separate commits."
```

### Phase 5: JIG Integration & Validation (1-2 hours)

**Goal:** Ensure all tests have `@jig.verifies()` decorators and graph alignment is correct.

**Actions:**
1. Add missing `@jig.verifies()` decorators to passing tests (Bucket A tests that were fixed)
2. Regenerate all graphs: `jigy index`, `jigy impl rebuild`, `jigy verify rebuild --run-tests`
3. Validate alignment: `jigy status`
4. Run full test suite: `pytest -v`
5. Check coverage: ensure test count is healthy (e.g., >1450 tests)

**Validation Checklist:**
```markdown
## Phase 5: Validation Results

- [ ] All tests have `@jig.verifies("S-XXX")` decorators
- [ ] `jigy status` shows correct alignment
- [ ] Full test suite passes: `pytest -v` (0 failures)
- [ ] Test count healthy: 1,482 tests (expected: >1,450)
- [ ] Coverage >80% on all bricks
- [ ] No commented-out tests in codebase
- [ ] No `# TODO: fix this test` comments
- [ ] All graphs regenerated and committed
```

**Final Commit:**
```bash
git add tests/ jig/generated/
git commit -m "test: complete SPEC-driven test recovery

Test Suite Recovery Summary:
- Baseline: 118 failing tests (out of 1,528)
- Repaired: 1,482 tests passing (97% healthy)

Strategy Breakdown:
- FIX: 65 tests (mechanical changes, SPECs unchanged)
- REWRITE: 35 tests (deleted old, wrote new per SPEC)
- DELETE: 18 tests (obsolete features, no replacement)
- SKIP: 8 tests (function not implemented, TDD scenario)
- DEBUG: 2 function bugs identified (fix functions, not tests)

JIG v8 Alignment:
- All tests annotated with @jig.verifies('S-XXX')
- Created 5 missing SPECs (Bucket B)
- All graphs regenerated (intent, implementation, verification)
- jigy status shows 100% alignment

SPECs are source of truth. Tests are reproducible.
No shims, no adapters, no backwards compatibility."
```

---

## Documentation & Learnings

### Document Key Findings

As you work through test repair, document important discoveries and decisions:

**Discoveries** - Gaps in test coverage or SPEC alignment:
- "23 tests had no traceable SPEC" - tests were written against implementation details, not requirements
- "OR-Map tests verified wrong semantics" - tests expected last-write-wins, but OR-Map uses add-wins

**Decisions** - Strategy choices (FIX vs REWRITE vs DELETE):
- "REWRITE OR-Map tests vs FIX for backwards compatibility"
  - Choice: REWRITE (delete old, write new)
  - Rationale: Architecture fundamentally changed (LWW → add-wins)
  - Tradeoffs: More work now, but tests verify correct SPEC

- "DELETE legacy token tests vs update for v2 format"
  - Choice: DELETE (no migration)
  - Rationale: Burn ships—v1 tokens unsupported, clean break
  - Tradeoffs: No rollback path, acceptable for reference implementation

**Learnings** - Reusable patterns from test repair:
- "Group by root cause before fixing tests" - identified 4 groups covering 118 tests; batch fixes 10x faster
- "SPECs make tests reproducible" - deleted 35 broken tests, regenerated 28 new tests from SPEC; code is cheap when requirements are clear
- "Missing decorators hide alignment drift" - 22 tests passed but had no SPEC link; drift invisible until audit

---

**LEARNED** - Reusable patterns from test repair:
```markdown
#LEARNED "Group by root cause before fixing tests"
Identified 4 groups covering 118 tests. Batch fixes 10x faster.

#LEARNED "SPECs make tests reproducible"
Deleted 35 broken tests, regenerated 28 new tests from SPEC.
Code is cheap when requirements are clear.

#LEARNED "Missing @jig annotations hide alignment drift"
22 tests passed but had no SPEC link. Drift invisible until audit.
Always annotate tests at creation time.
```

---

## 4) AI Agent Prompts

### Phase 1: SPEC Audit

> Audit all failing tests and classify into buckets.
>
> **For each failing test:**
> 1. Read the test function and docstring
> 2. Determine: What requirement does this test verify?
> 3. Search `jig/specifications/` for matching SPEC
> 4. Classify using decision tree:
>    - **Bucket A:** SPEC exists, test needs alignment
>    - **Bucket B:** SPEC missing but needed (note what SPEC should say)
>    - **Bucket C:** SPEC obsolete (note why it's no longer relevant)
>    - **Bucket D:** SPEC exists, test correct, but function missing (TDD scenario)
>    - **Bucket E:** SPEC exists, test correct, but function violates SPEC (bug detected)
>
> **Decision tree for Buckets D and E:**
> - If SPEC exists and test looks correct:
>   - Does the function for this feature exist?
>     - No → **Bucket D** (TDD: test written before function)
>     - Yes → Does function pass the test when run?
>       - No, and test is correct → **Bucket E** (function bug)
>       - No, and test is wrong → **Bucket A** (align test)
>
> **Output:** Markdown table per bucket (see Phase 1 template)
>
> **Focus:** Be ruthless about Bucket C. If you can't justify why a test should exist (business value, safety requirement), it's obsolete. For Bucket E, DO NOT "fix" the test—the test is doing its job (catching bugs).

### Phase 2: Create Missing SPECs

> For each Bucket B test, create the missing Specification.
>
> **Process:**
> 1. Read the failing test to extract the requirement (the "what")
> 2. Determine which Outcome this supports (optional)
> 3. Create `jig/specifications/S-NNN.md`:
>    - YAML frontmatter with id, type (minimal)
>    - Markdown body with rationale, acceptance criteria, related info
> 4. Run `jigy validate` to check format
> 5. Run `jigy index` to regenerate intent graph
>
> **Quality bar:**
> - SPEC describes "what", not "how"
> - Rationale explains why this requirement exists
> - Acceptance criteria are testable
> - Optionally links to Outcome (business value)

### Phase 3: Root Cause Grouping

> Group Bucket A and B tests by repair strategy.
>
> **Process:**
> 1. Analyze failure messages for common root causes
> 2. For each root cause, determine strategy:
>    - **FIX:** If change is mechanical (add param, fix import) and result is "as good as new"
>    - **REWRITE:** If architecture changed (semantics evolved, SPEC different)
>    - **DELETE:** If SPEC obsolete (Bucket C only)
> 3. Group tests by (root cause, strategy) tuple
>
> **Decision criteria:**
> - FIX: Would you write the same test today? (Yes → FIX)
> - REWRITE: Does the SPEC match old test intent? (No → REWRITE)
> - DELETE: Should this SPEC exist? (No → DELETE)
>
> **Output:** Markdown grouping with strategy justification (see Phase 3 template)

### Phase 4: Execute Repairs

> Execute repair strategy for each group, one commit per group.
>
> **For FIX groups:**
> 1. Apply mechanical changes (add param, fix import, etc.)
> 2. Ensure `@jig.verifies("S-XXX")` decorator exists
> 3. Run tests to verify they pass
> 4. Run `jigy verify rebuild --run-tests` to update verification graph
> 5. Commit with message: `test(<brick>): fix <root-cause> (Group N)`
>
> **For REWRITE groups:**
> 1. Delete old test file entirely (burn ships)
> 2. Read the SPEC that these tests should verify
> 3. Write new tests from scratch per SPEC acceptance criteria
> 4. Add `@jig.verifies("S-XXX")` decorators
> 5. Run tests to verify they pass
> 6. Run `jigy verify rebuild --run-tests`
> 7. Commit with message: `test(<brick>): rewrite per <SPEC> (Group N)`
>
> **For DELETE groups:**
> 1. Delete test files entirely
> 2. Run `jigy verify rebuild --run-tests` to update verification graph
> 3. Commit with message: `test: delete obsolete <feature> tests (Group N)`
>
> **Quality bar:**
> - No shims, no adapters, no feature flags
> - REWRITE tests are "as good as new" (not salvaged old logic)
> - Every test has `@jig.verifies()` decorator
> - Commit message explains strategy and rationale

### Phase 5: Validation

> Validate that test suite is healthy and JIG-aligned.
>
> **Checklist:**
> 1. Add `@jig.verifies()` decorators to any tests missing them
> 2. Regenerate all graphs:
>    - `jigy index` (intent graph)
>    - `jigy impl rebuild` (implementation graph)
>    - `jigy verify rebuild --run-tests` (verification graph)
> 3. Validate alignment: `jigy status` (check for missing edges)
> 4. Run full test suite: `pytest -v` (must pass)
> 5. Check test count (should be close to baseline, accounting for deletes)
> 6. Check coverage: `pytest --cov` (should be >80% on all bricks)
> 7. Search for anti-patterns:
>    - Commented-out tests: `grep -r "# def test_" tests/`
>    - TODO comments: `grep -r "# TODO.*test" tests/`
>    - Missing decorators: `grep -L "@jig.verifies" tests/**/*test*.py`
>
> **Output:** Document validation results and final metrics

---

## 5) Anti-Patterns vs Good Patterns

### ❌ Anti-Pattern: Shim the Old Behavior

```python
# BAD: Adding compatibility layer to make old test pass
@jig.verifies("S-003")
def test_replicator_initialization():
    """Verify replicator initializes with empty state"""
    # Shim to support old constructor (NO!)
    rep = Replicator() if hasattr(Replicator, '_allow_no_node_id') else Replicator(node_id="test-node")
    assert rep.state == {}
```

### ✅ Good Pattern: Fix or Rewrite

```python
# GOOD: Simple fix (if SPEC unchanged)
@jig.verifies("S-003")
def test_replicator_initialization():
    """Verify replicator initializes with empty state"""
    rep = Replicator(node_id="test-node")  # Just add the param
    assert rep.state == {}
```

---

### ❌ Anti-Pattern: Comment Out "Temporarily"

```python
# BAD: Commenting out broken tests
# def test_flat_map_merge():
#     """TODO: fix this test after refactor"""
#     # Temporarily disabled - Jim 2025-11-18
#     map1 = FlatMap()  # doesn't exist anymore
#     ...
```

### ✅ Good Pattern: Delete or Rewrite

```python
# GOOD: Delete the file entirely (if obsolete)
# OR rewrite from scratch (if SPEC changed)

@jig.verifies("S-006")
def test_or_map_merge_preserves_all_values():
    """Verify OR-Map merge preserves concurrent values (add-wins semantics)"""
    # New test written per updated SPEC
    map1 = ORMap(node_id="node-1")
    map2 = ORMap(node_id="node-2")
    # ... test the new semantics
```

---

### ❌ Anti-Pattern: Test Without SPEC

```python
# BAD: Test has no traceable SPEC
def test_some_edge_case():
    """Verify edge case handling"""
    # What SPEC does this verify? Nobody knows.
    result = do_thing(weird_input)
    assert result is not None
```

### ✅ Good Pattern: SPEC-First Test

```python
# GOOD: Test explicitly verifies a SPEC
@jig.verifies("S-004")
def test_device_id_uniqueness():
    """Verify device IDs are globally unique (S-004)"""
    # Clear what requirement this verifies
    id1 = generate_device_id()
    id2 = generate_device_id()
    assert id1 != id2
```

---

## 6) Execution Checklist

When executing a test repair task:

### Phase 0: Stop Bleeding
- [ ] Fix critical import errors
- [ ] Fix obvious constructor signature changes
- [ ] Run full test suite to get baseline
- [ ] Document failure count and types

### Phase 1: SPEC Audit
- [ ] List all failing tests
- [ ] For each test, identify SPEC it verifies
- [ ] Classify into Buckets A, B, C, D, E
- [ ] Create audit table in Delta (PLAN or NOTES)
- [ ] Add `#DISCOVERY` markers for gaps found (including Bucket D and E discoveries)

### Phase 2: Create Missing SPECs
- [ ] For each Bucket B test, create SPEC file
- [ ] Link SPECs to Outcomes (or create new Outcomes)
- [ ] Run `jig validate` to check SPEC format
- [ ] Commit SPECs before fixing tests
- [ ] Add `#DECISION` marker explaining SPEC-first approach

### Phase 3: Root Cause Grouping
- [ ] Group tests by root cause
- [ ] Assign strategy to each group (FIX/REWRITE/DELETE/SKIP/DEBUG)
- [ ] Document strategy rationale in Delta
- [ ] Add `#LEARNED` marker about grouping benefits
- [ ] For Bucket D: Identify CODE needed, prepare SCOPE doc
- [ ] For Bucket E: Prepare DEBUG delta creation

### Phase 4: Execute Repairs
- [ ] For FIX groups: apply mechanical changes, ensure `@jig` annotations
- [ ] For REWRITE groups: delete old tests, write new tests per SPEC
- [ ] For DELETE groups: remove test files entirely
- [ ] For SKIP groups (Bucket D): add @pytest.mark.skip, create SCOPE doc
- [ ] For DEBUG groups (Bucket E): create DEBUG deltas, do NOT fix tests
- [ ] One commit per group with clear strategy in message
- [ ] No shims, no adapters, no backwards compatibility
- [ ] Run tests after each group to verify

### Phase 5: JIG Integration & Validation
- [ ] Add `@jig` annotations to all tests
- [ ] Rebuild graph index: `jig index --rebuild`
- [ ] Validate alignment: `jig validate --check-all` (must pass)
- [ ] Run full test suite: `pytest -v` (must pass)
- [ ] Check coverage: `pytest --cov` (target >80%)
- [ ] Search for anti-patterns (commented tests, TODOs)
- [ ] Update Delta with completion summary
- [ ] Final commit with recovery metrics

---

## 7) Metrics & Completion Summary

**Track these metrics during repair:**

| Metric | Target | Why |
|--------|--------|-----|
| Tests repaired | 100% of failures | Complete recovery |
| SPEC coverage | 100% of tests have `@jig T-XXX verifies:S-YYY` | Traceability |
| Missing SPECs created | All Bucket B tests | Durable alignment |
| Obsolete tests deleted | All Bucket C tests | Clean codebase |
| Alignment validation | `jig validate --check-all` passes | No drift |
| Test suite health | 0 failures, >baseline count | Functional recovery |

**Completion Summary Template:**
```markdown
## Test Repair Completion Summary

### Baseline
- Total tests: 1,528
- Failing: 118 (7.7%)
- Blocked by imports: 77

### Classification
- Bucket A (align - existing SPEC): 65 tests
- Bucket B (create SPEC - missing SPEC): 30 tests
- Bucket C (delete - obsolete): 18 tests
- Bucket D (skip - CODE missing, TDD): 8 tests
- Bucket E (debug - CODE bug detected): 2 tests

### Strategy Execution
- FIX: 65 tests (mechanical changes)
- REWRITE: 30 tests (deleted old, wrote new per SPEC)
- DELETE: 18 tests (obsolete features)
- SKIP: 8 tests (CODE not implemented, created SCOPE doc)
- DEBUG: 2 tests (redirected to DEBUG workflow)

### SPECs Created (Bucket B)
- S-CRYPTO-005: Constant-time JWT validation
- S-AUTH-004: Device ID uniqueness
- S-AUTH-005: Token refresh timing <100ms
- S-IPC-002: WebSocket reconnection strategy
- S-CRDT-008: OR-Set conflict-free semantics

### SCOPE Docs Created (Bucket D - TDD)
- SCOPE_AUTH_MFA.md: 8 tests skipped, waiting for MFA implementation
  - Tests: test_mfa_token_validation, test_mfa_device_enrollment, test_mfa_backup_codes
  - Next: Create PLAN for WU-AUTH-MFA

### DEBUG Deltas Created (Bucket E - CODE Bugs)
- debug-device-id-collision: Device ID uniqueness bug (violates S-AUTH-004)
- debug-token-expiry-timing: Token expires 1hr early (violates S-AUTH-003)
- Action: Following DEBUG workflow to fix CODE bugs

### Final State
- Total tests: 1,490 (100% passing + skipped)
- Passing: 1,482 (99.5%)
- Skipped: 8 (0.5% - Bucket D, TDD scenario)
- Failing: 0 (0%)
- SPEC coverage: 100% (all tests have @jig annotations)
- Alignment: `jig validate` passes (0 orphaned nodes)
- Coverage: 84.2% (above 80% target)
- CODE bugs found: 2 (redirected to DEBUG workflow)

### Key Decisions
#DECISION "REWRITE OR-Map tests vs backwards compatibility"
- Deleted 30 flat-map tests (obsolete)
- Wrote 30 OR-Map tests per S-CRDT-006 (add-wins semantics)
- No shims, clean break

### Key Learnings
#LEARNED "SPECs make tests reproducible"
- Deleted broken tests confidently when SPEC was clear
- Regenerated correct tests from SPEC in <2 hours

#LEARNED "Group by root cause for batch fixes"
- 4 groups covered 118 tests
- Batch strategy 10x faster than one-off repairs

### Time Investment
- Phase 0: 30 min (stop bleeding)
- Phase 1: 2.5 hr (SPEC audit)
- Phase 2: 1.5 hr (create missing SPECs)
- Phase 3: 1 hr (root cause grouping)
- Phase 4: 5 hr (execute repairs)
- Phase 5: 1 hr (validation)
- **Total: 11.5 hours**

### Harvest Preparation
**Markers captured:** 8 (#DISCOVERY: 3, #DECISION: 2, #LEARNED: 3)

**Recommended OSTC Updates:**
- [ ] Update S-CRDT-001: Add note about OR-Map replacing flat-map
- [ ] Create O-QUALITY-001: "Zero untraceable tests" (new quality outcome)
```

---

## 8) Rationale: Why SPEC-Driven Repair?

**For JIG specifically:**
- JIG is about aligning OSTC (Outcome, Spec, Test, Code)
- Tests (T) serve Specifications (S), not implementations
- SPECs are timeless, tests are code (reproducible)
- Broken tests are an opportunity to audit SPEC coverage

**General benefits:**
- **Durable alignment:** Tests won't break on next refactor (they verify SPECs, not internals)
- **Fast recovery:** With clear SPECs, writing tests is mechanical (especially for AI agents)
- **Clean codebase:** No shims, no commented tests, no technical debt
- **Living documentation:** SPECs capture requirements, tests prove them
- **Onboarding:** New developers read SPECs to understand requirements, tests to see proof

**The alternative (shimming old tests) creates:**
- Technical debt (compatibility layers)
- Fragile tests (coupled to old implementation)
- Unclear requirements (tests verify "whatever makes them pass")
- Slow iteration (fear of breaking brittle tests)

---

## 9) Quick Reference: Decision Matrix (5 Buckets)

```
┌──────────────────────────────────────────────────────────────────────┐
│ For each failing test:                                               │
│                                                                       │
│ 1. What SPEC does this verify?                                       │
│    ├─ SPEC doesn't exist                                             │
│    │  ├─ Requirement is real → Bucket B (create SPEC)                │
│    │  └─ Requirement is obsolete → Bucket C (delete test)            │
│    │                                                                  │
│    └─ SPEC exists and is valid                                       │
│       ├─ Does CODE exist?                                            │
│       │  ├─ No → Bucket D (skip test, document SCOPE)                │
│       │  └─ Yes → Continue...                                        │
│       │                                                               │
│       ├─ Does CODE implement SPEC correctly?                         │
│       │  ├─ No → Bucket E (CODE bug → DEBUG workflow)                │
│       │  └─ Yes → Bucket A (align test)                              │
│       │                                                               │
│       └─ SPEC is obsolete → Bucket C (delete test)                   │
│                                                                       │
│ 2. Execute strategy per bucket:                                      │
│    ├─ Bucket A (Align): FIX or REWRITE test                          │
│    ├─ Bucket B (Create SPEC): Create SPEC → align test               │
│    ├─ Bucket C (Delete): Remove test, update graph                   │
│    ├─ Bucket D (Skip/TDD): @pytest.mark.skip + SCOPE doc             │
│    └─ Bucket E (Debug): Create DEBUG delta, don't fix test           │
│                                                                       │
│ NEVER: shims, adapters, backwards compatibility, "fix" test for bug  │
│ ALWAYS: @jig T-XXX verifies:S-YYY annotation                         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 10) Benefits of SPEC-Driven Test Repair

**For the Developer:**
- Clear decision framework (no guessing)
- SPECs provide "source of truth" for what tests should verify
- Confidence to delete broken tests (can regenerate from SPEC)
- Clean codebase (no technical debt from shims)

**For the AI Agent:**
- SPECs are unambiguous instructions for test generation
- Classification system (Buckets A/B/C) provides clear action
- Decision matrix (FIX/REWRITE/DELETE) removes ambiguity
- Batch repairs by root cause (efficient parallel work)

**For the Team:**
- Test suite becomes documentation of requirements
- Onboarding: read SPEC, see test, understand requirement
- SPECs stay current (repair process audits coverage)
- No "mystery tests" (every test traces to business value)

**For Future You:**
- SPECs explain why tests exist
- Delta markers explain repair decisions
- Graph index shows alignment (O→S→T→C)
- No archaeological digs through git history

---

**TL;DR:**

1. **Classify:** Every failing test is Bucket A (align), B (create SPEC), C (delete), D (skip - TDD), or E (debug - function bug)
2. **Create SPECs:** For Bucket B, create the SPEC before fixing the test
3. **Group:** Batch tests by root cause and strategy (FIX/REWRITE/DELETE/SKIP/DEBUG)
4. **Execute:** No shims, no adapters—fix, rewrite from SPEC, delete, skip, or redirect to DEBUG
5. **Validate:** All tests have `@jig.verifies()` decorators, `jigy status` shows alignment, test suite healthy

**Core principle:** SPECs are source of truth. Tests are reproducible. Code is cheap when requirements are clear.

**Key insight:** Bucket D (TDD) preserves S-F-T alignment when function is missing. Bucket E (Debug) prevents "fixing" tests to match buggy functions.

---

## Success Criteria

Test repair is complete when ALL of the following are true:

- [ ] **All failing tests classified** into Buckets A, B, C, D, or E
- [ ] **All Bucket B SPECs created** - every test without a SPEC now has one (or is deleted)
- [ ] **All tests aligned or resolved:**
  - Bucket A: Fixed or rewritten per SPEC
  - Bucket B: SPEC created, test aligned
  - Bucket C: Tests deleted
  - Bucket D: Tests skipped with `@pytest.mark.skip`, missing implementations documented
  - Bucket E: Function bugs documented (tests remain as-is)
- [ ] **All tests have decorators** - every test has `@jig.verifies("S-XXX")`
- [ ] **All graphs regenerated** - intent, implementation, verification graphs up to date
- [ ] **Alignment validated** - `jigy status` shows expected alignment
- [ ] **Test suite passes** - `pytest -v` shows 0 failures (skipped tests OK)
- [ ] **Coverage maintained** - test coverage >80% on all bricks
- [ ] **No anti-patterns** - no commented tests, no TODOs, no shims
- [ ] **Changes committed** - all work committed with clear messages

---

**Status:** Ready for use (v3.0 - JIG v8 compatible)
**Version:** 3.0.0 (2025-11-30)
**Compatibility:** JIG v8 (S-F-T triangle, Bricks, Decorators)
