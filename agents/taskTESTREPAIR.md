# taskTESTREPAIR: SPEC-Driven Test Recovery

**Purpose:** Recover failing test suites by re-aligning tests with Specifications. Tests are reproducible artifacts—SPECs are the source of truth.

**Philosophy:** Tests verify Specifications, not implementations. When tests break, first ask: "What SPEC does this verify?" If the SPEC is valid, the test must align. If the SPEC is obsolete, the test must die. No shims, no adapters, no backwards compatibility.

**Core Insight:** SPECs are timeless. Tests are code. Code is cheap (especially for AI agents). Don't preserve broken tests—regenerate correct tests from SPECs.

---

## 0) JIG Foundation: The OSTC Model for Tests

In JIG, **Tests (T)** are empirical truth that verify **Specifications (S)**:

```
Outcome (O) ──implements──> Specification (S) ──verifies──> Test (T)
                                    │
                                    └──implements──> Code (C)
```

**Key Relationships:**
- **O → S:** Specifications implement Outcomes (business value)
- **S → T:** Tests verify Specifications (empirical proof)
- **S → C:** Code implements Specifications (operational reality)

**Test Annotation Pattern:**
```python
# @jig T-AUTH-001 verifies:S-AUTH-001 subsystem:auth
def test_jwt_token_validation():
    """Verify JWT tokens validate correctly with device ID"""
    # Test implementation
```

**Critical Rule:** Every test MUST trace to a Specification. If you can't name the SPEC, the test shouldn't exist.

---

## 1) Core Principles

### 1. SPEC-Centric Recovery
- **SPECs are source of truth** - Tests serve SPECs, not vice versa
- **Tests are reproducible** - If you have a clear SPEC, you can regenerate the test
- **Old tests aren't sacred** - Delete broken tests confidently if you have the SPEC
- **No SPEC = No test** - Unspecified behavior is undefined behavior

### 2. Three-Bucket Classification
Every failing test falls into exactly one bucket:

| Bucket | SPEC Status | Action | Example |
|--------|-------------|--------|---------|
| **A** | Existing SPEC (valid) | Add `@jig` annotation, ensure alignment | Test for JWT validation, SPEC exists |
| **B** | Missing SPEC (needed) | Create SPEC first, then align/rewrite test | Test for edge case not in SPEC |
| **C** | Obsolete SPEC | Delete test entirely | Test for removed flat-map feature |

### 3. Decision Matrix (No Shims)

For tests in Buckets A and B, choose ONE strategy:

| Strategy | When to Use | What to Do | Never Do |
|----------|-------------|------------|----------|
| **FIX** | Change is mechanical, result is "as good as new" | Fix the test (add param, fix import) | Add compatibility layers |
| **REWRITE** | Architecture changed, SPEC semantics evolved | Delete old test, write new test per SPEC | Try to salvage old test logic |
| **DELETE** | SPEC is obsolete, no replacement needed | Remove test, update graph index | Comment out "just in case" |

**NEVER:**
- Add shims or adapters to make old tests pass
- Preserve backwards compatibility for obsolete SPECs
- Use feature flags to toggle test behavior
- Comment out tests "temporarily"

---

## 2) The 5-Phase Recovery Workflow

### Phase 0: Stop Bleeding (30 minutes)

**Goal:** Get clean failure counts by fixing obvious blockers.

**Actions:**
1. Fix critical import errors (e.g., missing replicator module)
2. Fix obvious constructor signature changes
3. Run full test suite to get accurate failure count
4. Document baseline: X tests failing out of Y total

**Output:**
```markdown
# In jig/deltas/active/<branch>/NOTES.md or PLAN.md

## Phase 0: Baseline
- Total tests: 1,528
- Failing: 118
- Blocked by imports: 77 (fixed)
- Clean failures: 41
- Run: `pytest -v > test-baseline.txt`
```

### Phase 1: SPEC Audit (2-3 hours)

**Goal:** Classify every failing test into Buckets A, B, or C.

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
| test_jwt_validation | test_auth.py:42 | S-AUTH-001 | Missing @jig | Add annotation |
| test_token_expiry | test_auth.py:58 | S-AUTH-001 | Needs update | Constructor changed |

### Bucket B: Missing SPEC (N tests)
| Test | File:Line | Needs SPEC | Subsystem | Rationale |
|------|-----------|------------|-----------|-----------|
| test_constant_time_compare | test_crypto.py:120 | S-CRYPTO-005 | crypto | Security requirement, was implicit |
| test_device_id_uniqueness | test_auth.py:205 | S-AUTH-004 | auth | Edge case not documented |

### Bucket C: Obsolete SPEC (N tests)
| Test | File:Line | Obsolete Feature | Decision |
|------|-----------|------------------|----------|
| test_flat_map_merge | test_crdt.py:88 | Flat-map removed | DELETE (replaced by OR-Map) |
| test_legacy_token_format | test_auth.py:310 | Pre-v2 tokens | DELETE (no migration needed) |
```

**JIG Markers:**
```markdown
#DISCOVERY "Found 23 tests with no traceable SPEC"
Tests were written against implementation, not requirements.

#DECISION "Create missing SPECs before fixing tests (Bucket B)"
**Choice:** SPEC-first approach
**Rationale:** Tests without SPECs will break again on next refactor
**Tradeoffs:** More upfront work, but durable alignment
```

### Phase 2: Create Missing SPECs (1-2 hours)

**Goal:** For every Bucket B test, create the missing Specification.

**Process:**
1. Read the failing test to understand what it verifies
2. Extract the requirement (the "what", not the "how")
3. Create SPEC file in `jig/specifications/`
4. Link SPEC to Outcome (or create new Outcome if needed)
5. Run `jig validate` to check format

**Example:**
```yaml
# jig/specifications/S-CRYPTO-005.md
---
id: S-CRYPTO-005
type: specification
title: "JWT signature validation uses constant-time comparison"
subsystem: crypto
created: 2025-11-18
implements: O-AUTH-002
---

# Specification: Constant-time JWT validation

JWT signature validation MUST use constant-time comparison to prevent timing attacks.

## Rationale
Variable-time comparison leaks information about signature bytes through timing side-channels.

## Acceptance Criteria
- Signature comparison completes in constant time regardless of input
- No early-exit on first differing byte
- Use `hmac.compare_digest()` or equivalent

## Related
- implements: O-AUTH-002 ("Zero authentication bypass incidents")
- tested_by: T-CRYPTO-005
- code: C-CRYPTO-003
```

**Commit:**
```bash
git add jig/specifications/
git commit -m "specs: create missing SPECs for crypto tests

Created 5 specifications for previously implicit requirements:
- S-CRYPTO-005: Constant-time JWT validation
- S-AUTH-004: Device ID uniqueness
- S-AUTH-005: Token refresh timing <100ms
- S-IPC-002: WebSocket reconnection strategy
- S-CRDT-008: Conflict-free OR-Set semantics

These requirements were implemented but not specified.
Discovered during test repair audit (Phase 1).

See: jig/deltas/active/<branch>/PLAN.md → Phase 2"
```

### Phase 3: Root Cause Grouping (1 hour)

**Goal:** Group Bucket A and B tests by repair strategy (FIX, REWRITE, DELETE).

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
**Action:** Delete old tests, write new tests per S-CRDT-006 (OR-Map SPEC)

### Group 3: Legacy Token Format (DELETE) - 18 tests
**Root Cause:** Pre-v2 token support removed
**Strategy:** DELETE (SPEC obsolete, no replacement)
**Files:** tests/auth/test_legacy_tokens.py
**Action:** Delete file entirely, remove from graph index

### Group 4: Missing @jig Annotations (FIX) - 22 tests
**Root Cause:** Tests pass but lack SPEC traceability
**Strategy:** FIX (add annotations only)
**Files:** tests/*/test_*.py (scattered)
**Action:** Add `@jig T-XXX-NNN verifies:S-YYY-NNN` annotations
```

**JIG Markers:**
```markdown
#DECISION "REWRITE OR-Map tests vs FIX flat-map tests"
**Choice:** REWRITE (delete old, write new)
**Rationale:** OR-Map semantics fundamentally different (add-wins vs last-write-wins)
**Tradeoffs:** More work now, but tests verify correct SPEC (S-CRDT-006)

#LEARNED "Group by root cause before fixing individual tests"
Identified 4 groups covering 118 tests. Each group has one strategy.
Batch fixes are 10x faster than one-off repairs.
```

### Phase 4: Execute Repairs (4-6 hours)

**Goal:** Apply FIX/REWRITE/DELETE strategy to each group.

**Workflow per Group:**

#### Strategy: FIX (Mechanical Changes)

```python
# BEFORE (broken)
# @jig T-CRDT-012 verifies:S-CRDT-003 subsystem:crdt
def test_replicator_initialization():
    """Verify replicator initializes with empty state"""
    rep = Replicator()  # Missing node_id
    assert rep.state == {}

# AFTER (fixed)
# @jig T-CRDT-012 verifies:S-CRDT-003 subsystem:crdt
def test_replicator_initialization():
    """Verify replicator initializes with empty state"""
    rep = Replicator(node_id="test-node")  # Added required param
    assert rep.state == {}
```

**Commit per group:**
```bash
git add tests/crdt/
git commit -m "test(crdt): fix constructor signatures (Group 1)

Fixed 43 tests to use new Replicator(node_id=...) signature.

Strategy: FIX (mechanical change, tests still verify S-CRDT-003)
Root Cause: Constructor signature changed in WU5 refactor
Result: All tests pass, semantics unchanged

Unit: Test Repair Phase 4.1
See: jig/deltas/active/<branch>/PLAN.md → Phase 4"
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
# @jig T-CRDT-015 verifies:S-CRDT-006 subsystem:crdt
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
git commit -m "test(crdt): rewrite OR-Map tests per S-CRDT-006 (Group 2)

Deleted 35 flat-map tests (obsolete).
Created 28 OR-Map tests verifying add-wins semantics.

Strategy: REWRITE (architecture change, not backwards compatible)
Root Cause: Flat-map removed, OR-Map has different conflict resolution
SPECs verified: S-CRDT-006 (OR-Map add-wins), S-CRDT-007 (merge semantics)

New tests written from scratch per SPEC.
No attempt to salvage old test logic (burn ships).

Unit: Test Repair Phase 4.2
See: jig/deltas/active/<branch>/PLAN.md → Phase 4"
```

#### Strategy: DELETE (Obsolete)

```bash
# Delete tests for removed features
rm tests/auth/test_legacy_tokens.py
rm tests/utils/test_deprecated_helpers.py

# Update graph index (remove orphaned T nodes)
jig index --rebuild

git add tests/ jig/
git commit -m "test: delete obsolete legacy token tests (Group 3)

Deleted 18 tests for pre-v2 token format (no longer supported).

Strategy: DELETE (SPEC obsolete, no replacement needed)
Root Cause: Legacy token support removed in WU6 (burn ships)
Decision: No migration path, clean break

Removed T-AUTH-050 through T-AUTH-067 from graph index.

Unit: Test Repair Phase 4.3
See: jig/deltas/active/<branch>/PLAN.md → Phase 4"
```

### Phase 5: JIG Integration & Validation (1-2 hours)

**Goal:** Ensure all tests have `@jig` annotations and graph alignment is correct.

**Actions:**
1. Add missing `@jig` annotations to passing tests (Bucket A tests that were fixed)
2. Rebuild graph index: `jig index --rebuild`
3. Validate alignment: `jig validate --check-all`
4. Run full test suite: `pytest -v`
5. Check coverage: ensure test count is healthy (e.g., >1450 tests)
6. Update PLAN reflection

**Validation Checklist:**
```markdown
## Phase 5: Validation Results

- [ ] All tests have `@jig T-XXX-NNN verifies:S-YYY-NNN` annotations
- [ ] `jig validate --check-all` passes (no orphaned nodes)
- [ ] Full test suite passes: `pytest -v` (0 failures)
- [ ] Test count healthy: 1,482 tests (expected: >1,450)
- [ ] Coverage >80% on all subsystems
- [ ] No commented-out tests in codebase
- [ ] No `# TODO: fix this test` comments
- [ ] Graph index rebuilt: `jig index --rebuild`
- [ ] Subsystem coupling ratios maintained (>10:1)
```

**Final Commit:**
```bash
git add tests/ jig/
git commit -m "test: complete SPEC-driven test recovery

Test Suite Recovery Summary:
- Baseline: 118 failing tests (out of 1,528)
- Repaired: 1,482 tests passing (97% healthy)

Strategy Breakdown:
- FIX: 65 tests (mechanical changes, SPECs unchanged)
- REWRITE: 35 tests (deleted old, wrote new per SPEC)
- DELETE: 18 tests (obsolete features, no replacement)

JIG Alignment:
- All tests annotated with @jig T-XXX verifies:S-YYY
- Created 5 missing SPECs (Bucket B)
- Validated: 0 orphaned nodes, 0 broken references

SPECs are source of truth. Tests are reproducible.
No shims, no adapters, no backwards compatibility.

See: jig/deltas/active/<branch>/PLAN.md → Test Repair Completion Summary"
```

---

## 3) JIG Markers for Test Repair

### Use These Markers in Your Delta (PLAN or NOTES)

**DISCOVERY** - Gaps in test coverage or SPEC alignment:
```markdown
#DISCOVERY "23 tests had no traceable SPEC"
Tests written against implementation details, not requirements.
Created SPECs: S-CRYPTO-005, S-AUTH-004, S-AUTH-005.

#DISCOVERY "OR-Map tests verified wrong semantics"
Tests expected last-write-wins, but OR-Map uses add-wins.
Rewrote per S-CRDT-006.
```

**DECISION** - Strategy choices (FIX vs REWRITE vs DELETE):
```markdown
#DECISION "REWRITE OR-Map tests vs FIX for backwards compatibility"
**Choice:** REWRITE (delete old, write new)
**Rationale:** Architecture fundamentally changed (LWW → add-wins)
**Tradeoffs:** More work now, but tests verify correct SPEC

#DECISION "DELETE legacy token tests vs update for v2 format"
**Choice:** DELETE (no migration)
**Rationale:** Burn ships—v1 tokens unsupported, clean break
**Tradeoffs:** No rollback path, acceptable for reference implementation
```

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
> 4. Classify:
>    - **Bucket A:** SPEC exists (note the SPEC ID)
>    - **Bucket B:** SPEC missing but needed (note what SPEC should say)
>    - **Bucket C:** SPEC obsolete (note why it's no longer relevant)
>
> **Output:** Markdown table per bucket (see Phase 1 template)
>
> **Focus:** Be ruthless about Bucket C. If you can't justify why a test should exist (business value, safety requirement), it's obsolete.

### Phase 2: Create Missing SPECs

> For each Bucket B test, create the missing Specification.
>
> **Process:**
> 1. Read the failing test to extract the requirement (the "what")
> 2. Determine which Outcome this supports (or create new Outcome)
> 3. Create `jig/specifications/S-<SUBSYSTEM>-NNN.md`:
>    - YAML frontmatter with id, type, title, subsystem, implements
>    - Markdown body with rationale, acceptance criteria, related nodes
> 4. Run `jig validate` to check format
>
> **Quality bar:**
> - SPEC describes "what", not "how"
> - Rationale explains why this requirement exists
> - Acceptance criteria are testable
> - Links to at least one Outcome (business value)

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
> 2. Ensure `@jig T-XXX verifies:S-YYY` annotation exists
> 3. Run tests to verify they pass
> 4. Commit with message: `test(<subsystem>): fix <root-cause> (Group N)`
>
> **For REWRITE groups:**
> 1. Delete old test file entirely (burn ships)
> 2. Read the SPEC that these tests should verify
> 3. Write new tests from scratch per SPEC acceptance criteria
> 4. Add `@jig T-XXX verifies:S-YYY subsystem:name` annotations
> 5. Run tests to verify they pass
> 6. Commit with message: `test(<subsystem>): rewrite per <SPEC> (Group N)`
>
> **For DELETE groups:**
> 1. Delete test files entirely
> 2. Run `jig index --rebuild` to remove orphaned T nodes
> 3. Commit with message: `test: delete obsolete <feature> tests (Group N)`
>
> **Quality bar:**
> - No shims, no adapters, no feature flags
> - REWRITE tests are "as good as new" (not salvaged old logic)
> - Every test has `@jig` annotation
> - Commit message explains strategy and rationale

### Phase 5: Validation

> Validate that test suite is healthy and JIG-aligned.
>
> **Checklist:**
> 1. Add `@jig` annotations to any tests missing them
> 2. Run `jig index --rebuild` to regenerate graph index
> 3. Run `jig validate --check-all` (must pass)
> 4. Run full test suite: `pytest -v` (must pass)
> 5. Check test count (should be close to baseline, accounting for deletes)
> 6. Check coverage: `pytest --cov` (should be >80% on all subsystems)
> 7. Search for anti-patterns:
>    - Commented-out tests: `grep -r "# def test_" tests/`
>    - TODO comments: `grep -r "# TODO.*test" tests/`
>    - Missing annotations: `grep -L "@jig T-" tests/**/*test*.py`
>
> **Output:** Update PLAN with validation results and final metrics

---

## 5) Anti-Patterns vs Good Patterns

### ❌ Anti-Pattern: Shim the Old Behavior

```python
# BAD: Adding compatibility layer to make old test pass
# @jig T-CRDT-012 verifies:S-CRDT-003 subsystem:crdt
def test_replicator_initialization():
    """Verify replicator initializes with empty state"""
    # Shim to support old constructor (NO!)
    rep = Replicator() if hasattr(Replicator, '_allow_no_node_id') else Replicator(node_id="test-node")
    assert rep.state == {}
```

### ✅ Good Pattern: Fix or Rewrite

```python
# GOOD: Simple fix (if SPEC unchanged)
# @jig T-CRDT-012 verifies:S-CRDT-003 subsystem:crdt
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

# @jig T-CRDT-015 verifies:S-CRDT-006 subsystem:crdt
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
# @jig T-AUTH-023 verifies:S-AUTH-004 subsystem:auth
def test_device_id_uniqueness():
    """Verify device IDs are globally unique (S-AUTH-004)"""
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
- [ ] Classify into Buckets A, B, C
- [ ] Create audit table in Delta (PLAN or NOTES)
- [ ] Add `#DISCOVERY` markers for gaps found

### Phase 2: Create Missing SPECs
- [ ] For each Bucket B test, create SPEC file
- [ ] Link SPECs to Outcomes (or create new Outcomes)
- [ ] Run `jig validate` to check SPEC format
- [ ] Commit SPECs before fixing tests
- [ ] Add `#DECISION` marker explaining SPEC-first approach

### Phase 3: Root Cause Grouping
- [ ] Group tests by root cause
- [ ] Assign strategy to each group (FIX/REWRITE/DELETE)
- [ ] Document strategy rationale in Delta
- [ ] Add `#LEARNED` marker about grouping benefits

### Phase 4: Execute Repairs
- [ ] For FIX groups: apply mechanical changes, ensure `@jig` annotations
- [ ] For REWRITE groups: delete old tests, write new tests per SPEC
- [ ] For DELETE groups: remove test files entirely
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
- Bucket A (existing SPEC): 65 tests
- Bucket B (missing SPEC): 30 tests
- Bucket C (obsolete): 23 tests

### Strategy Execution
- FIX: 65 tests (mechanical changes)
- REWRITE: 30 tests (deleted old, wrote new per SPEC)
- DELETE: 23 tests (obsolete features)

### SPECs Created (Bucket B)
- S-CRYPTO-005: Constant-time JWT validation
- S-AUTH-004: Device ID uniqueness
- S-AUTH-005: Token refresh timing <100ms
- S-IPC-002: WebSocket reconnection strategy
- S-CRDT-008: OR-Set conflict-free semantics

### Final State
- Total tests: 1,482 (97% healthy)
- Failing: 0 (0%)
- SPEC coverage: 100% (all tests have @jig annotations)
- Alignment: `jig validate` passes (0 orphaned nodes)
- Coverage: 84.2% (above 80% target)

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

## 9) Quick Reference: Decision Matrix

```
┌─────────────────────────────────────────────────────────────┐
│ For each failing test:                                      │
│                                                              │
│ 1. What SPEC does this verify?                              │
│    ├─ Existing SPEC → Bucket A                              │
│    ├─ Missing SPEC (needed) → Bucket B                      │
│    └─ Obsolete SPEC → Bucket C                              │
│                                                              │
│ 2. What's the root cause?                                   │
│    ├─ Mechanical change (constructor, import) → FIX         │
│    ├─ Architecture change (semantics evolved) → REWRITE     │
│    └─ Feature removed (obsolete) → DELETE                   │
│                                                              │
│ 3. Execute strategy:                                        │
│    ├─ FIX: Minimal change, verify SPEC still correct        │
│    ├─ REWRITE: Delete old, write new per SPEC               │
│    └─ DELETE: Remove test, update graph index               │
│                                                              │
│ NEVER: shims, adapters, backwards compatibility             │
│ ALWAYS: @jig T-XXX verifies:S-YYY annotation                │
└─────────────────────────────────────────────────────────────┘
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

1. **Classify:** Every failing test is Bucket A (existing SPEC), B (missing SPEC), or C (obsolete)
2. **Create SPECs:** For Bucket B, create the SPEC before fixing the test
3. **Group:** Batch tests by root cause and strategy (FIX/REWRITE/DELETE)
4. **Execute:** No shims, no adapters—fix, rewrite from SPEC, or delete
5. **Validate:** All tests have `@jig` annotations, `jig validate` passes, test suite healthy

**Core principle:** SPECs are source of truth. Tests are reproducible. Code is cheap when requirements are clear.

---

**Status:** Ready for use
**Next:** Apply to first broken test suite (bootstrap validation)
