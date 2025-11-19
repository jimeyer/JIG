# Task: DEBUG Workflow (JIG Edition)

**Version:** 1.1.0 (Agent-Optimized)
**Owner:** Jim Meyer
**Audience:** AI coding agents (primary) + Human developers
**Updated:** 2025-11-19

## Objective

Execute systematic debugging that maps broken behavior to violated OSTC constraints, fixes the root cause, and harvests learnings to strengthen the Intent Graph.

---

## Quick Start for AI Agents

When assigned a DEBUG task, you will:

1. **Create** a DEBUG delta in `jig/deltas/active/debug-[issue-id]/`
2. **Investigate** to find which Intent Graph constraints are violated
3. **Fix** the violation (update Code/Tests OR update Intent)
4. **Harvest** learnings into OSTC before closing
5. **Archive** the DEBUG delta after merge

**Success = Bug fixed + Regression test added + Intent aligned + Learnings harvested**

---

## Context: Why DEBUG is Different in JIG

**Traditional debugging:** Find bug → Fix code → Done

**JIG debugging:** Find bug → Identify violated constraint → Fix violation → Update Intent Graph → Harvest learnings

**Key insight:** Every bug reveals a gap in our constraint model. Bugs are opportunities to strengthen Intent.

**Two types of violations:**
1. **Implementation violated Intent** - Code/Tests don't satisfy existing O/S constraints
2. **Intent was incomplete/wrong** - O/S constraints don't capture reality

---

## When to Use DEBUG (vs PLAN)

| Scenario | Use DEBUG |
|----------|-----------|
| Production bug reported | ✅ |
| Test failing in CI | ✅ |
| Unexpected behavior found | ✅ |
| Performance regression | ✅ |
| Known feature request | ❌ (use PLAN) |
| Planned refactor | ❌ (use PLAN) |

**Rule:** If work starts with "something is broken", use DEBUG. If it starts with "we want to build X", use PLAN.

---

## Inputs Required

Before starting DEBUG, you need:

- **Symptom Report** - Bug ticket, user report, failing test, stack trace
- **Reproduction Steps** - How to observe the broken behavior
- **Expected vs Actual** - What should happen vs what does happen
- **Access to Intent Graph** - `jig/outcomes/` and `jig/specifications/` directories

---

## Outputs You Will Create

- **DEBUG Delta** - `jig/deltas/active/debug-[issue-id]/DEBUG_[title].md`
- **Fix Commit(s)** - Code/test changes with `@jig` annotations
- **Updated Intent** - New or modified O/S nodes (if needed)
- **Harvest Report** - Extracted learnings for `jig ai-synthesize`

---

## DEBUG Workflow (Step-by-Step)

### Phase 1: Triage & Setup (15-30 min)

**Objective:** Create DEBUG delta and map symptoms to Intent Graph

**Steps:**

1. **Create branch and delta**
   ```bash
   git checkout -b debug-issue-[N]
   jig delta new --type debug --issue [N]
   # Creates: jig/deltas/active/debug-issue-[N]/DEBUG_[title].md
   ```

2. **Fill Symptoms section** (use template below)
   - Clear "what's broken" description
   - Specific reproduction steps (must be actionable!)
   - Expected vs actual behavior
   - Impact assessment (users, data, security, workarounds)

3. **Map to Intent Graph**
   - Search `jig/outcomes/` for relevant Outcomes
   - Search `jig/specifications/` for relevant Specifications
   - Identify which O/S nodes should govern this behavior
   - Check which Tests should have caught this
   - Form hypothesis: Is Intent wrong or is Reality wrong?

4. **Commit initial DEBUG**
   ```bash
   git add jig/deltas/
   git commit -m "debug: start investigation for issue #[N]

   Symptom: [one-line summary]
   Affected subsystem: [name]
   See: jig/deltas/active/debug-issue-[N]/DEBUG_[title].md"
   ```

**Success Criteria:**
- [ ] DEBUG delta exists with complete Symptoms section
- [ ] Constraint Mapping section lists relevant O/S nodes
- [ ] Initial hypothesis documented
- [ ] Branch created and initial commit made

---

### Phase 2: Investigation (variable time)

**Objective:** Find root cause and identify violated constraints

**Steps:**

1. **Reproduce the bug**
   - Follow reproduction steps exactly
   - Capture logs, stack traces, data
   - Document observations in Investigation Log

2. **Add timestamped Investigation Log entries**
   ```markdown
   ### [YYYY-MM-DD HH:MM] - [milestone]

   **What I tried:** [action taken]
   **What I found:** [observation]
   **Next step:** [what to investigate next]
   ```

3. **Iterate until root cause found**
   - Try hypothesis → Document findings → Refine hypothesis
   - Update Constraint Mapping as understanding improves

4. **When root cause found, document:**
   ```markdown
   ### [YYYY-MM-DD HH:MM] - Root Cause Found

   **Root cause:** [clear statement of what's broken]
   **Why it happened:** [failure mechanism]
   **Constraint violated:**
   - Implementation violated: [S-XXX-NNN]
   - OR Intent was wrong: [S-XXX-NNN needs update]
   - OR Intent was missing: [need new S-XXX-NNN]

   **Evidence:**
   - Stack trace / logs / data
   - Code location: `src/path/file.py:123`
   - Test gap: `tests/path/file.py::missing_test`
   ```

**Success Criteria:**
- [ ] Bug reproduced successfully
- [ ] Root cause clearly stated with evidence
- [ ] Violated/missing constraint identified
- [ ] Code location(s) documented
- [ ] Investigation Log has timestamped entries

**DO NOT proceed to Phase 3 until root cause is confirmed**

---

### Phase 3: Fix Implementation (TDD when possible)

**Objective:** Fix violation, add regression test, update Intent if needed

**Steps:**

1. **Fill Fix Strategy section**
   - Approach: How will we fix this?
   - Changes required: Code, tests, intent, docs
   - Risk assessment: regression risk, scope, testing strategy
   - Rollback plan: How to undo if fix causes issues

2. **Write regression test FIRST** (unless P0 hotfix)
   ```python
   # @jig T-XXX-NNN verifies:S-YYY-NNN subsystem:name
   def test_regression_issue_[N]():
       """Regression test for issue #[N] - [one-line description]"""
       # This test should FAIL before the fix
       # This test should PASS after the fix
       [test implementation]
   ```

3. **Implement minimal fix**
   ```python
   # @jig C-XXX-NNN implements:S-YYY-NNN subsystem:name
   def fixed_function():
       # Fixed implementation
       [code]
   ```
   - Change only what's necessary
   - Add/update `@jig` annotations
   - Follow existing code style

4. **Update Intent if constraint was missing/wrong**
   - If missing: Create new O/S node in `jig/specifications/` or `jig/outcomes/`
   - If incomplete: Update existing O/S node
   - Document in "Intent Updates" section

5. **Fill Discoveries & Learnings section**
   - Focus on constraint model learnings
   - Add JIG markers:
     - `#DISCOVERY` - Constraint gaps revealed by bug
     - `#LEARNED` - Prevention patterns
     - `#DECISION` - Fix approach tradeoffs

6. **Validate the fix**
   ```bash
   # Reproduction steps should now work correctly
   pytest tests/path/test_file.py::test_regression_issue_[N] -v
   pytest tests/path/ -v  # Full test suite
   jig validate --check-all  # Intent alignment
   ```

7. **Commit the fix**
   ```bash
   git add src/ tests/ jig/
   git commit -m "fix(subsystem): resolve issue #[N]

   Root cause: [one-line explanation]
   Fix: [what changed]
   Implements: S-XXX-NNN
   Adds: T-XXX-NNN (regression test)

   Closes #[N]
   See: jig/deltas/active/debug-issue-[N]/DEBUG_[title].md"
   ```

**Success Criteria:**
- [ ] Regression test added and passing
- [ ] Fix implemented with @jig annotations
- [ ] Intent updated if needed (new/modified O/S nodes)
- [ ] Reproduction steps now work correctly
- [ ] Full test suite passes
- [ ] `jig validate --check-all` passes
- [ ] Fix committed with proper message

---

### Phase 4: RETRO & Harvest

**Objective:** Extract learnings and prepare for merge

**Steps:**

1. **Fill RETRO section**
   - Root cause category (missing spec, incomplete spec, violation, etc.)
   - Upstream failure point (where should this have been caught?)
   - What would have prevented this?
   - Process improvements proposed (with `#LEARNED` markers)

2. **Fill Completion Summary**
   - Changes delivered (code, tests, intent, docs)
   - Constraint alignment achieved
   - Time metrics (time to reproduce, root cause, fix, total)
   - Harvest preparation:
     - Count markers by type (#DISCOVERY, #LEARNED, #DECISION)
     - Propose NEW or UPDATED OSTC nodes from discoveries
     - List subsystems touched

3. **Run harvest command**
   ```bash
   jig ai-distill --branch debug-issue-[N]
   # Extracts markers, proposes OSTC updates
   ```

4. **Review and commit harvest**
   ```bash
   git add jig/
   git commit -m "harvest: learnings from issue #[N] debug

   Distilled [X] markers into [Y] OSTC nodes:
   - S-XXX-042 (NEW): [description]
   - S-XXX-001 (UPDATE): [what changed]
   - T-XXX-043 (NEW): Regression test

   See: jig/harvest-reports/debug-issue-[N]-YYYY-MM-DD.yaml"
   ```

5. **Merge and archive**
   ```bash
   git checkout main
   git merge debug-issue-[N]
   jig delta archive --branch debug-issue-[N] --retention long-term
   # Archives to: jig/deltas/archive/debug-issue-[N]/
   ```

**Success Criteria:**
- [ ] RETRO section complete with root cause analysis
- [ ] Completion Summary filled with all metrics
- [ ] Harvest command executed
- [ ] OSTC updates committed
- [ ] Branch merged to main
- [ ] DEBUG delta archived

---

## DEBUG Template (Copy This)

```markdown
---
delta_type: debug
issue_id: [ticket/issue number]
branch: debug-issue-[N]
severity: [critical | high | medium | low]
---

# DEBUG: [Issue Title]

- **Issue ID:** [link to ticket]
- **Reported:** [YYYY-MM-DD]
- **Investigator:** [name]
- **Status:** [Investigating | Root Cause Found | Fixed | Closed]
- **Subsystem:** [affected subsystem]
- **Priority:** [P0 | P1 | P2 | P3]

## Symptoms

**What's broken:**
[Clear description of broken behavior]

**How to reproduce:**
1. Step 1
2. Step 2
3. Observe: [actual broken behavior]

**Expected behavior:**
[What should happen instead]

**First observed:**
- Environment: [prod | staging | dev]
- Version/Commit: [hash]
- Frequency: [always | intermittent | rare]

**Impact:**
- Users affected: [count or %]
- Data integrity: [yes | no]
- Security: [yes | no]
- Workaround available: [yes | no]

## Constraint Mapping (Intent Alignment)

**Which OSTC nodes should govern this behavior?**

**Outcomes potentially violated:**
- O-XXX-001: "Description" (jig/outcomes/O-XXX-001.md)
  - Violated? [yes | no | unclear]
  - How: [explanation]

**Specifications potentially violated:**
- S-XXX-001: "Description" (jig/specifications/S-XXX-001.md)
  - Violated? [yes | no | unclear]
  - How: [explanation]

**Tests that should have caught this:**
- T-XXX-001: `tests/path/to/test.py::test_function`
  - Exists? [yes | no]
  - Passing? [yes | no]
  - Adequate? [yes | no | needs expansion]

**Initial hypothesis:**
[Which constraint model is broken: Intent (O/S wrong) or Reality (C/T wrong)?]

## Investigation Log

### [YYYY-MM-DD HH:MM] - [milestone]

**What I tried:**
[Action taken]

**What I found:**
[Observation]

**Next step:**
[What to investigate next]

---

### [YYYY-MM-DD HH:MM] - Root Cause Found

**Root cause:**
[Clear statement of what's broken]

**Why it happened:**
[Explanation of failure mechanism]

**Constraint violated:**
- Implementation violated: [S-XXX-NNN]
- OR Intent was wrong: [S-XXX-NNN needs update]
- OR Intent was missing: [need new S-XXX-NNN]

**Evidence:**
- Stack trace / logs / data
- Code location: `src/path/file.py:123`
- Test gap: `tests/path/file.py::missing_test`

---

## Fix Strategy

**Approach:**
[How will we fix this?]

**Changes required:**
- [ ] Code changes in: `src/path/file.py`
- [ ] Test changes in: `tests/path/test_file.py`
- [ ] Intent updates: [O-XXX-NNN or S-XXX-NNN]
- [ ] Documentation updates: [paths]

**Risk assessment:**
- Regression risk: [low | medium | high]
- Scope of change: [isolated | localized | widespread]
- Testing strategy: [unit | integration | manual]

**Rollback plan:**
[How to undo if fix causes issues]

---

## Implementation

### Code Changes

**Files modified:**
- `src/path/file.py:123-145`
  ```python
  # @jig C-XXX-NNN implements:S-XXX-NNN subsystem:name
  def fixed_function():
      # Fixed implementation
  ```

**Root cause location:**
- File: `src/path/file.py`
- Line: 123
- Problem: [what was wrong]
- Fix: [what changed]

### Test Changes

**Tests added/modified:**
- `tests/path/test_file.py::test_regression_issue_[N]`
  ```python
  # @jig T-XXX-NNN verifies:S-XXX-NNN subsystem:name
  def test_regression_issue_[N]():
      """Regression test for issue #[N] - ensure X doesn't happen"""
      # Test that would have caught the bug
  ```

**Why this test didn't exist:**
[Gap in test strategy, edge case not considered, etc.]

### Intent Updates

**New OSTC nodes created:**
- S-XXX-042: "Description of new constraint discovered"
  - Why: [This constraint wasn't explicit before the bug]
  - Location: `jig/specifications/S-XXX-042.md`

**Existing OSTC nodes updated:**
- S-XXX-001: "Updated description"
  - What changed: [added constraint about edge case]
  - Why: [original spec was incomplete]

---

## Discoveries & Learnings

**What we learned about our constraints:**

#DISCOVERY "Edge case X was not covered in original specification S-XXX-001"
#DISCOVERY "Assumption Y was wrong - system behaves differently when Z"

**Why the bug escaped detection:**

#LEARNED "Test coverage was focused on happy path, missed error handling"
#LEARNED "Integration test needed - unit tests alone insufficient for this behavior"

**Decisions made during fix:**

#DECISION "Chose defensive validation over performance"
**Choice:** Add validation to every call site
**Rationale:** Performance cost <1ms, safety critical for data integrity
**Tradeoffs:** Slight overhead vs preventing data corruption

**Upstream gaps (prevention):**

#DISCOVERY "Need acceptance criteria for error cases in PLAN template"
#LEARNED "Specification S-XXX-001 should include failure modes, not just happy path"

**Constraint model improvements:**

#DISCOVERY "Need new specification S-XXX-042: Input validation requirements"
- What: All public APIs must validate inputs before processing
- Why: This entire class of bugs stems from missing input validation
- Subsystem: [name]

---

## RETRO (Why Did This Happen?)

**Root cause category:**
- [ ] Missing specification (constraint never documented)
- [ ] Incomplete specification (constraint documented but incomplete)
- [ ] Specification violation (constraint ignored/misunderstood)
- [ ] Missing test (constraint not verified)
- [ ] Environmental factor (works in dev, breaks in prod)
- [ ] Regression (worked before, broken by recent change)

**Upstream failure point:**
[Where in the development process should this have been caught?]

**What would have prevented this:**
1. [Specific practice, test, review step]
2. [Process improvement]
3. [Tool/automation]

**Process improvements proposed:**

#LEARNED "Always include error case acceptance criteria in PLAN Work Units"
#DECISION "Add input validation checklist to code review template"

**Intent Graph gaps identified:**

#DISCOVERY "Subsystem [name] lacks error handling specifications"
- Need: S-XXX-043: "Error handling strategy for subsystem [name]"
- Need: O-XXX-007: "System degrades gracefully under invalid input"

---

## Validation

**How to verify fix:**
1. Reproduction steps from "Symptoms" section should now work correctly
2. New regression test passes: `pytest tests/path/test_file.py::test_regression_issue_[N] -v`
3. Existing tests still pass: `pytest tests/path/ -v`
4. Intent alignment check: `jig validate --check-all`

**Manual testing:**
- [ ] Reproduction case: [result]
- [ ] Edge cases: [result]
- [ ] Performance: [result]
- [ ] Integration: [result]

**Rollout plan:**
- Staging: [YYYY-MM-DD]
- Production: [YYYY-MM-DD]
- Monitoring: [metrics to watch]

---

## Completion Summary

**Issue resolved:** [yes | no | partial]

**Changes delivered:**
- Code: [# files, # lines changed]
- Tests: [# tests added]
- Intent: [# O/S nodes created/updated]
- Documentation: [what updated]

**Constraint alignment:**
- Implementation now satisfies: [S-XXX-NNN, S-XXX-NNN]
- New constraints added: [S-XXX-NNN]
- Tests now verify: [S-XXX-NNN, S-XXX-NNN]

**Time metrics:**
- Time to reproduce: [duration]
- Time to root cause: [duration]
- Time to fix: [duration]
- Total time: [duration]

**Harvest Preparation (JIG):**

**Markers summary:**
- Discoveries: [count]
- Decisions: [count]
- Learned patterns: [count]

**Recommended OSTC Nodes (from DEBUG learnings):**
(Focus on DISCOVERIES - new constraints revealed by the bug)

- [ ] S-XXX-042: "Input validation required at all public APIs" (NEW - gap discovered)
- [ ] S-XXX-001: Add "must handle null input gracefully" (UPDATE - incomplete spec)
- [ ] O-XXX-007: "System degrades gracefully under invalid input" (NEW - outcome clarified)
- [ ] T-XXX-043: Add regression test for issue #[N] (NEW - test gap)

**Subsystems touched:** [primary], [secondary]

**Next step:** `jig ai-distill --branch debug-issue-[N]`
```

---

## Operating Rules

### Severity-Based Rules

- **P0/Critical:** Fix first, document after (but still create minimal DEBUG delta)
- **P1/High:** Full DEBUG workflow
- **P2/Medium:** Full DEBUG workflow
- **P3/Low:** Consider batching, full workflow when addressed

### Constraint Alignment Rules

- **ALWAYS map symptoms to Intent Graph** - which O/S nodes are violated/missing?
- **Update Intent when wrong** - if bug reveals wrong constraint, fix the constraint
- **Add Intent when missing** - if bug reveals missing constraint, create the constraint
- **Regression test required** - every bug fix needs a test that would have caught it
- **Harvest before close** - run `jig ai-distill` before archiving DEBUG delta

### Annotation Rules

- **Mark regression tests:** `# @jig T-XXX-NNN verifies:S-YYY-NNN subsystem:name`
- **Mark fixed code:** `# @jig C-XXX-NNN implements:S-YYY-NNN subsystem:name`
- **Link commits to DEBUG:** Use trailers `See: jig/deltas/active/debug-NNN/`

### RETRO Rules

- **RETRO required for P0/P1** - why did this escape? what process failed?
- **RETRO recommended for P2/P3** - capture learnings for prevention
- **RETRO feeds process improvement** - harvest RETRO discoveries into team practices

---

## JIG Marker Quick Reference

| Marker | When to Use | Example |
|--------|-------------|---------|
| `#DISCOVERY` | Constraint gap revealed | `#DISCOVERY "S-AUTH-001 missing: tokens must validate in constant time"` |
| `#DISCOVERY` | Missing specification | `#DISCOVERY "Need S-XXX-042: Input validation requirements"` |
| `#LEARNED` | Prevention pattern | `#LEARNED "Always validate nullable parameters at API boundaries"` |
| `#LEARNED` | Test strategy gap | `#LEARNED "Integration tests required for multi-step auth flows"` |
| `#DECISION` | Fix approach tradeoff | `#DECISION "Defensive validation vs performance"` |

**Aim for:** 3-7 high-value markers per DEBUG session

**Use markers for:**
- Constraint gaps revealed by the bug → `#DISCOVERY`
- Prevention patterns learned → `#LEARNED`
- Fix approach decisions with tradeoffs → `#DECISION`

**Don't marker:**
- Routine investigation steps
- Obvious findings
- Things already in Intent Graph

---

## Example: Minimal DEBUG Session

```markdown
---
delta_type: debug
issue_id: 42
branch: debug-issue-42
severity: high
---

# DEBUG: JWT validation fails for multi-device tokens

- **Issue ID:** #42
- **Reported:** 2025-11-18
- **Status:** Fixed
- **Subsystem:** auth

## Symptoms

**What's broken:**
Users report "Invalid token" error when switching between devices.

**How to reproduce:**
1. Login on device A (phone)
2. Login on device B (desktop) with same user
3. Make API call from device A
4. Observe: 403 "Invalid token"

**Expected:** Both tokens should be valid (per O-AUTH-001: multi-device support)

## Constraint Mapping

**Specifications violated:**
- S-AUTH-001: "JWT tokens with 24-hour expiration"
  - Violated? YES - tokens invalidating prematurely

**Tests missing:**
- T-AUTH-003 exists but only tests single device

## Investigation Log

### 2025-11-18 14:23 - Root Cause Found

**Root cause:** Token validation compares device_id without null check. Second login sets device_id, first login has null device_id, comparison throws exception, token rejected.

**Why:** Spec S-AUTH-001 didn't specify device_id as required field.

**Evidence:** `src/auth.py:156` - `if token.device_id == device_id:` fails when token.device_id is None

## Fix Strategy

- Add null check to device_id validation
- Make device_id required in token claims
- Add regression test for null device_id

## Implementation

```python
# @jig C-AUTH-012 implements:S-AUTH-001 subsystem:auth
def validate_token(token: str, device_id: str) -> bool:
    claims = decode_token(token)
    # FIX: Handle null device_id
    if claims.device_id is None or device_id is None:
        return False
    return claims.device_id == device_id
```

Regression test:
```python
# @jig T-AUTH-043 verifies:S-AUTH-001 subsystem:auth
def test_regression_null_device_id():
    """Regression test for issue #42 - null device_id"""
    token = create_token(device_id=None)
    assert not validate_token(token, "device-123")
```

## Discoveries & Learnings

#DISCOVERY "S-AUTH-001 incomplete: device_id optionality not specified"
#LEARNED "Always validate nullable fields at API boundaries"
#DECISION "Make device_id required vs optional" - chose required for security

## RETRO

**Upstream failure:** Specification S-AUTH-001 didn't define device_id as required field.

**Prevention:**
#LEARNED "All specifications should explicitly state field requirements (required/optional)"

## Completion Summary

**Constraint alignment:**
- Updated S-AUTH-001: Add "device_id is required field"
- Added T-AUTH-043: Regression test
- Fixed C-AUTH-012: Null check

**Harvest:** 3 discoveries, 2 learned patterns, 1 decision

**Next step:** `jig ai-distill --branch debug-issue-42`
```

---

## Constraints & Boundaries

### DO:
- ✅ Create DEBUG delta for all P1+ bugs
- ✅ Map every symptom to Intent Graph constraints
- ✅ Write regression test before fixing (when not hotfix)
- ✅ Add `@jig` annotations to all code/test changes
- ✅ Harvest learnings before merging
- ✅ Fill RETRO section for all P0/P1 bugs

### DO NOT:
- ❌ Skip constraint mapping ("just fix it quickly")
- ❌ Fix without regression test
- ❌ Close bug without harvesting learnings
- ❌ Ignore Intent Graph updates when constraint was wrong/missing
- ❌ Batch-commit multiple phases (commit after each phase)

### PREFER:
- 💡 TDD approach (test first, then fix)
- 💡 Minimal fixes (change only what's necessary)
- 💡 Defensive validation over performance
- 💡 Clear commit messages with traceability

---

## AI Agent Specific Guidance

### Phase Verification

**Before moving to next phase, verify:**

**Phase 1 → 2:**
- [ ] DEBUG delta file exists
- [ ] Symptoms section is specific and actionable
- [ ] Relevant O/S nodes identified
- [ ] Initial commit made

**Phase 2 → 3:**
- [ ] Bug reproduced successfully
- [ ] Root cause documented with evidence
- [ ] Violated constraint identified
- [ ] Code location documented

**Phase 3 → 4:**
- [ ] Regression test passes
- [ ] Full test suite passes
- [ ] `jig validate --check-all` passes
- [ ] Fix committed

**Phase 4 → Close:**
- [ ] RETRO complete
- [ ] Harvest command executed
- [ ] Changes merged
- [ ] Delta archived

### Common Failure Modes

**If you can't reproduce the bug:**
- Document in Investigation Log what you tried
- Check if symptom report has missing information
- Ask human for clarification before proceeding

**If root cause is unclear:**
- Continue Investigation Log entries
- Don't guess - document uncertainty
- Ask human to review findings before implementing fix

**If tests fail after fix:**
- Don't mark task complete
- Document failure in Investigation Log
- Investigate why tests are failing

**If `jig validate` fails:**
- Review `@jig` annotations
- Check O/S node references are correct
- Fix validation errors before marking complete

### Human Review Points

**Request human review at these points:**
1. After finding root cause (before implementing fix)
2. If constraint violation is ambiguous (Intent wrong vs Reality wrong)
3. If fix requires architectural changes
4. If P0/Critical bug requires immediate hotfix

---

## Testing Your DEBUG Completion

Before marking DEBUG complete, verify:

1. ✅ Can another developer understand the root cause from DEBUG delta alone?
2. ✅ Does regression test fail without fix and pass with fix?
3. ✅ Are all `@jig` annotations correct and traceable?
4. ✅ Has harvest command been run successfully?
5. ✅ Is RETRO section filled with actionable learnings?

---

**Status:** Ready for AI Agent use
**Version:** 1.1.0
**Changelog:**
- v1.1.0: Restructured for AI agent consumption following Task Crafting Guide
- v1.0.0: Initial JIG-integrated DEBUG workflow
