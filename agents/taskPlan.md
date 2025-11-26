# Task: Execute Work Plan with Intent-First Development

**Version:** 2.0.0 (JIG v8 aligned)
**Audience:** AI coding agents + Human developers
**Status:** Active

## Objective

Execute planned work using Test-Driven Development while maintaining alignment between intent (specifications), implementation (code), and verification (tests) as measured by the JIG Alignment Graph.

## Context

### What is JIG?

JIG (Just-In-Graph) is an alignment measurement system that makes the relationship between intent, implementation, and verification explicit and measurable through a graph of nodes and edges:

- **S nodes (Specifications)**: What we intend to build
- **F nodes (Functions)**: What we actually built
- **T nodes (Tests)**: What we actually verify
- **Edges**: implements (F→S), verifies (T→S), covers (T→F)

### The Five JIG Artifacts

1. **Specification Files**: `jig/specifications/S-001.md` (intent, human-authored)
2. **Outcome Files**: `jig/outcomes/O-001.md` (optional, high-level goals)
3. **Brick Definitions**: `jig/bricks.yaml` (architectural partitions)
4. **@jig Decorators**: In source code (`@jig.implements("S-001")`, `@jig.verifies("S-001")`)
5. **Graph Files**: `jig/generated/*.ndjson` (machine-generated)

### Core Workflow: O→S→TDD

1. **O (Outcomes)**: WHY we build this (business value)
2. **S (Specifications)**: WHAT we build (concrete requirements)
3. **T (Tests)**: Verify specifications (write first, TDD red phase)
4. **F (Functions)**: Implement specifications (TDD green phase)

**Philosophy**: Development is constraint satisfaction. Start with known constraints (Intent), write tests that verify them, then implement.

## Inputs

When starting work, you receive:

1. **SCOPE Document**: Describes the feature/problem to solve
   - May reference existing O/S nodes (e.g., "Implements: O-001, S-003")
   - May describe new intent to be created as O/S nodes

2. **Existing JIG Artifacts**: Review before starting
   - `jig/outcomes/*.md` - existing outcomes
   - `jig/specifications/*.md` - existing specifications
   - `jig/bricks.yaml` - architectural partitions

3. **Codebase Context**: Relevant code, tests, documentation

## Process

### Step 1: Create PLAN Document (Work Tracker)

Create a markdown file to track your work. This is NOT a JIG artifact, just your working notes.

**Location**: `docs/plans/PLAN-<feature-name>.md` (or similar location outside `jig/`)

**Template**:
```markdown
# PLAN: <Feature Name>

- **SCOPE**: <link to scope document>
- **Start**: <YYYY-MM-DD>
- **Status**: Draft | In-Progress | Complete
- **Branch**: <git-branch-name>

## Known Intent (Created Before Coding)

**Outcomes**:
- O-001: <description> (jig/outcomes/O-001.md)

**Specifications**:
- S-001: <description> (jig/specifications/S-001.md)
- S-002: <description> (jig/specifications/S-002.md)

**Bricks Affected**:
- B-001: <brick name>

## Work Unit Checklist
- [ ] WU0: Create Intent nodes (O/S)
- [ ] WU1: <title> — tests ☐ / code ☐ / docs ☐
- [ ] WU2: <title> — tests ☐ / code ☐ / docs ☐

## Work Units

### Work Unit 0: Create Known Intent

**Goal**: Capture all known Outcomes and Specifications from SCOPE before writing any code.

**Acceptance Criteria**:
- [ ] All known "why" statements → Outcome files in `jig/outcomes/`
- [ ] All known "what" requirements → Specification files in `jig/specifications/`
- [ ] All files have proper YAML frontmatter
- [ ] `jigy validate` passes

**Created Nodes**:
- (List will be filled during execution)

**Reflect**:
- What was clear from SCOPE: <clarity wins>
- What was ambiguous: <will discover during implementation>

---

### Work Unit N: <Title>

**Goal**: <Single, testable goal>

**Planned Effort**: 60-90 minutes

**Acceptance Criteria**:
- [ ] Specification S-NNN is implemented by function(s)
- [ ] Specification S-NNN is verified by test(s)
- [ ] Tests execute implementation (coverage confirms)
- [ ] `jigy status` shows alignment

**Implementation Notes**:
- Approach: <steps>
- Files: `path/to/file.py`
- Decorators added: `@jig.implements("S-NNN")`

**Test Plan**:
- Unit tests: <describe>
- Test file: `tests/path/test_feature.py`
- Decorators added: `@jig.verifies("S-NNN")`

**Docs Updated**:
- README / ADR / API docs

**Reflect** (≤5 bullets):
- What worked well: <concise notes>
- What could be better: <process improvements>
- Surprises/discoveries: <non-obvious learnings>
- Risks identified: <watch items>

**Links**:
- Commit: <hash>
- PR: <url if applicable>
```

### Step 2: Execute Work Unit 0 (Intent-First)

**DO THIS FIRST** - before writing any implementation code.

#### 2.1: Read SCOPE Carefully

Extract known constraints:
- **WHY statements** (business value, user needs) → Outcomes
- **WHAT statements** (technical requirements, constraints) → Specifications
- If unclear or ambiguous, note for later discovery (don't guess)

#### 2.2: Create Outcome Files

For each WHY statement:

**File**: `jig/outcomes/O-NNN.md` (sequential numbering: O-001, O-002, etc.)

```markdown
---
id: O-001
type: outcome
---

# <Human-Readable Title>

<Description of the business value, user need, or goal>

**Value**: <Why this matters>

**Acceptance Criteria**:
- <Observable outcome 1>
- <Observable outcome 2>
```

**Validation**: Run `jigy validate` to check format.

#### 2.3: Create Specification Files

For each WHAT statement:

**File**: `jig/specifications/S-NNN.md` (sequential numbering: S-001, S-002, etc.)

```markdown
---
id: S-001
type: specification
implements: [O-001]  # Links to outcome(s) this spec satisfies
---

# <Human-Readable Title>

<Concrete, testable requirement>

**Acceptance Criteria**:
- <Testable criterion 1>
- <Testable criterion 2>

**Rationale**: <Why this constraint exists>

**References**: <Links to external docs, RFCs, etc.>
```

**Validation**: Run `jigy validate` to check format.

#### 2.4: Commit Intent (Before Any Code)

```bash
git add jig/outcomes/ jig/specifications/
git commit -m "intent: define constraints for <feature>

Created Outcomes: O-001, O-002
Created Specifications: S-001, S-002, S-003

See: docs/plans/PLAN-<feature>.md → Work Unit 0"
```

### Step 3: Execute Work Units 1-N (TDD Loop)

For each work unit:

#### 3.1: Write Tests First (RED)

Write tests that verify the specifications:

```python
@jig.verifies("S-001")
def test_token_expiration():
    """Verify tokens expire after 15 minutes of inactivity."""
    token = create_token(user="test")
    token.last_activity = datetime.now() - timedelta(minutes=15, seconds=1)
    assert is_expired(token)
```

**Expected**: Tests FAIL (red) because implementation doesn't exist yet.

#### 3.2: Implement Code (GREEN)

Write minimal code to make tests pass:

```python
@jig.implements("S-001")
def is_expired(token: Token) -> bool:
    """Check if token has expired based on inactivity."""
    inactive_duration = datetime.now() - token.last_activity
    return inactive_duration > timedelta(minutes=15)
```

**Expected**: Tests PASS (green).

#### 3.3: Refactor (If Needed)

Improve code quality while keeping tests green.

#### 3.4: Update Documentation

Update relevant docs in the same commit:
- README if public API changed
- Architecture Decision Records (ADRs) if design choices made
- API documentation if interfaces changed

#### 3.5: Verify Alignment

```bash
# Regenerate graphs to include new code/tests
jigy index                          # Update intent graph
jigy impl rebuild                   # Update implementation graph
jigy verify rebuild --run-tests     # Update verification graph (runs tests with coverage)

# Check alignment
jigy status
```

**Expected output**:
```
S-001: Token Expiration
  ✓ Implemented by: F-auth.tokens.is_expired (B-001)
  ✓ Verified by: T-test_auth.test_token_expiration (B-001)
  ✓ Test covers implementation

  Alignment: PERFECT
```

#### 3.6: Update PLAN Reflect Block

Fill in the Reflect section for this work unit (≤5 bullets):
- **What worked well**: Concise wins (tools, techniques, approaches)
- **What could be better**: Process improvements, scope clarity issues
- **Surprises**: Non-obvious discoveries, edge cases found
- **Risks**: Items to watch, technical debt, potential issues

**Purpose**: PDCA learning (Plan-Do-Check-Act), not for harvest or synthesis. Focus on improving your development process.

#### 3.7: Commit

```bash
git add src/ tests/ docs/ jig/generated/
git commit -m "feat(<scope>): <brief description>

Implements: S-001, S-002
Tests: T-001, T-002
Alignment: verified with jigy status

See: docs/plans/PLAN-<feature>.md → Work Unit N"
```

**Commit Guidelines**:
- Type: `feat` (new feature), `fix` (bug fix), `refactor` (no behavior change)
- Reference S/T nodes for traceability
- Link to PLAN work unit for context

#### 3.8: Mark Checklist Complete

In your PLAN document, mark the work unit checklist items:
- [x] WUN: <title> — tests ✅ / code ✅ / docs ✅

### Step 4: Complete PLAN

When all work units are done:

#### 4.1: Add Completion Summary to PLAN

```markdown
## Completion Summary

**Scope Delivered**:
- <Summary of what was accomplished>

**Metrics**:
- Work Units: <count>
- Specifications Created: <count>
- Specifications Implemented: <count>
- Alignment: <percentage from jigy status>

**Key Decisions**:
- <Important choices made and rationale>

**Deltas from Original Scope**:
- <What changed and why>

**Reflection Roll-Up**:
- **Repeatable wins**: <Patterns that worked well>
- **Systemic frictions**: <Process issues to address>
- **Open questions**: <Items for future work>

**Final Validation**:
- [ ] All work unit checklists complete
- [ ] `jigy validate` passes
- [ ] `jigy status` shows expected alignment
- [ ] All tests passing
- [ ] Documentation updated
```

#### 4.2: Final Alignment Check

```bash
jigy validate              # Check artifact integrity
jigy status               # Check alignment status
pytest                    # Run all tests
```

#### 4.3: Mark PLAN Complete

Update PLAN header: `Status: Complete`

## Outputs

### Required Artifacts

1. **Intent Nodes**: `jig/outcomes/O-*.md`, `jig/specifications/S-*.md`
2. **Implementation**: Code with `@jig.implements("S-NNN")` decorators
3. **Verification**: Tests with `@jig.verifies("S-NNN")` decorators
4. **Updated Graphs**: `jig/generated/*.ndjson` (regenerated via jigy commands)
5. **PLAN Document**: Work tracker with reflections and completion summary
6. **Git Commits**: Clean history with traceability to S/T nodes

### Output Locations

```
jig/
├── outcomes/
│   ├── O-001.md              # Created in WU0
│   └── O-002.md
├── specifications/
│   ├── S-001.md              # Created in WU0
│   ├── S-002.md
│   └── S-003.md
├── bricks.yaml               # Updated if new bricks defined
└── generated/
    ├── intent-graph.ndjson   # Regenerated after O/S changes
    ├── implementation-graph.ndjson  # Regenerated after code changes
    └── verification-graph.ndjson    # Regenerated after test runs

src/
└── <modules>/
    └── *.py                  # Code with @jig.implements decorators

tests/
└── <modules>/
    └── test_*.py             # Tests with @jig.verifies decorators

docs/
└── plans/
    └── PLAN-<feature>.md     # Your work tracker
```

## Success Criteria

Your work is complete when:

- [ ] All O/S nodes from SCOPE are created in `jig/outcomes/` and `jig/specifications/`
- [ ] All specifications have `@jig.implements("S-NNN")` decorators in code
- [ ] All specifications have `@jig.verifies("S-NNN")` decorators in tests
- [ ] `jigy validate` passes with no errors
- [ ] `jigy status` shows expected alignment (typically 100% for new work)
- [ ] All tests pass (`pytest`)
- [ ] Documentation is updated
- [ ] PLAN document has completion summary
- [ ] Git commits reference S/T nodes for traceability

## Constraints

### DO NOT

- **Write code before creating Intent nodes** (WU0 must be first)
- **Write implementation before writing tests** (TDD: tests first)
- **Commit code without @jig decorators** (breaks alignment measurement)
- **Skip alignment validation** (`jigy status` is required)
- **Use domain prefixes in IDs** (use S-001, not S-AUTH-001; bricks provide organization)
- **Manually edit graph files** (`jig/generated/*.ndjson` are machine-generated)

### MUST

- **Follow O→S→TDD workflow** (Outcome → Spec → Test → Code)
- **Use sequential numbering** for O/S nodes (O-001, O-002, S-001, S-002)
- **Add decorators as you code** (@jig.implements in code, @jig.verifies in tests)
- **Regenerate graphs after changes** (jigy index, jigy impl rebuild, jigy verify rebuild)
- **Validate before completing** (jigy validate, jigy status)

### PREFER

- **Small work units** (60-90 minutes each)
- **One specification per file** (S-001.md, S-002.md)
- **Atomic commits** (one work unit per commit when possible)
- **Concise reflections** (≤5 bullets per work unit)

## Examples

### Example: Work Unit 0 Execution

**SCOPE excerpt**:
> Users must be able to authenticate securely using JWT tokens that expire after 15 minutes of inactivity.

**Extract intent**:
- **WHY**: Secure authentication (business value: reduce unauthorized access)
- **WHAT**: JWT tokens with 15-minute inactivity expiration (technical constraint)

**Create O-001.md**:
```markdown
---
id: O-001
type: outcome
---

# Secure User Authentication

Users can authenticate securely without password vulnerabilities.

**Value**: Reduces support burden from password resets and improves security posture.

**Acceptance Criteria**:
- Users successfully authenticate across multiple sessions
- No authentication bypasses in security audits
```

**Create S-001.md**:
```markdown
---
id: S-001
type: specification
implements: [O-001]
---

# JWT Token Inactivity Expiration

Authentication tokens MUST expire after 15 minutes of inactivity.

**Acceptance Criteria**:
- Token created with `expires_at = now() + 15 minutes`
- Any operation updates `last_activity` timestamp
- Token rejected if `now() > last_activity + 15 minutes`

**Rationale**: Limits exposure window if token is compromised.
```

**Commit**:
```bash
git add jig/outcomes/O-001.md jig/specifications/S-001.md
git commit -m "intent: define JWT authentication constraints

Created: O-001 (Secure Authentication), S-001 (Token Expiration)
See: docs/plans/PLAN-jwt-auth.md → WU0"
```

### Example: Work Unit 1 Execution (TDD)

**Goal**: Implement S-001 (JWT Token Inactivity Expiration)

**Step 1: Write Test First** (RED):
```python
# tests/auth/test_tokens.py
from datetime import datetime, timedelta
from auth.tokens import is_expired, Token

@jig.verifies("S-001")
def test_token_expires_after_15_minutes_inactivity():
    """Verify tokens expire after 15 minutes of inactivity."""
    token = Token(user="test", last_activity=datetime.now())

    # Token should NOT be expired at 14 minutes
    token.last_activity = datetime.now() - timedelta(minutes=14)
    assert not is_expired(token)

    # Token SHOULD be expired at 15 minutes + 1 second
    token.last_activity = datetime.now() - timedelta(minutes=15, seconds=1)
    assert is_expired(token)
```

Run test: `pytest tests/auth/test_tokens.py::test_token_expires_after_15_minutes_inactivity`
**Expected**: FAILS (function doesn't exist yet)

**Step 2: Implement** (GREEN):
```python
# src/auth/tokens.py
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class Token:
    user: str
    last_activity: datetime

@jig.implements("S-001")
def is_expired(token: Token) -> bool:
    """Check if token has expired due to inactivity."""
    inactive_duration = datetime.now() - token.last_activity
    return inactive_duration > timedelta(minutes=15)
```

Run test: `pytest tests/auth/test_tokens.py::test_token_expires_after_15_minutes_inactivity`
**Expected**: PASSES

**Step 3: Verify Alignment**:
```bash
jigy impl rebuild
jigy verify rebuild --run-tests
jigy status
```

**Output**:
```
S-001: JWT Token Inactivity Expiration
  ✓ Implemented by: F-auth.tokens.is_expired (B-001)
  ✓ Verified by: T-test_auth.test_token_expires_after_15_minutes_inactivity (B-001)
  ✓ Test covers implementation

  Alignment: PERFECT
```

**Step 4: Commit**:
```bash
git add src/auth/tokens.py tests/auth/test_tokens.py jig/generated/
git commit -m "feat(auth): implement JWT token expiration

Implements: S-001
Tests: T-test_auth.test_token_expires_after_15_minutes_inactivity
Alignment: verified (100%)

Tokens now expire after 15 minutes of inactivity as specified.

See: docs/plans/PLAN-jwt-auth.md → WU1"
```

## Common Pitfalls

### Pitfall 1: Writing Code Before Intent

**Wrong**:
```bash
# Starts coding immediately
vim src/auth/tokens.py  # Writing implementation first
```

**Right**:
```bash
# Creates intent first
vim jig/specifications/S-001.md  # Define what we're building
jigy validate                     # Validate format
git commit                        # Commit intent
vim tests/auth/test_tokens.py    # Then write test
vim src/auth/tokens.py           # Then implement
```

### Pitfall 2: Skipping @jig Decorators

**Wrong**:
```python
def is_expired(token: Token) -> bool:
    # No decorator - alignment cannot be measured!
    return datetime.now() - token.last_activity > timedelta(minutes=15)
```

**Right**:
```python
@jig.implements("S-001")
def is_expired(token: Token) -> bool:
    # Decorator makes alignment measurable
    return datetime.now() - token.last_activity > timedelta(minutes=15)
```

### Pitfall 3: Using Domain Prefixes in IDs

**Wrong**:
```markdown
---
id: S-AUTH-001  # Don't use domain prefixes!
---
```

**Right**:
```markdown
---
id: S-001       # Sequential numbering
type: specification
---
# JWT Token Expiration
# (Brick assignment provides organizational context)
```

### Pitfall 4: Forgetting to Regenerate Graphs

**Wrong**:
```bash
vim src/auth/tokens.py    # Add @jig.implements
git commit                # Commit immediately
jigy status              # Old graph - doesn't show new implementation!
```

**Right**:
```bash
vim src/auth/tokens.py    # Add @jig.implements
jigy impl rebuild         # Regenerate graph
jigy status              # Now shows new implementation
git add jig/generated/   # Include updated graphs in commit
git commit
```

## Quick Reference

### Essential Commands

```bash
# Validate artifact integrity
jigy validate

# Generate/update graphs
jigy index                         # Intent graph (O, S nodes)
jigy impl rebuild                  # Implementation graph (F nodes, F→S edges)
jigy verify rebuild --run-tests    # Verification graph (T nodes, T→S, T→F edges)

# Check alignment
jigy status                        # Overall alignment report
jigy status --spec S-001          # Alignment for specific spec

# Run tests
pytest                             # All tests
pytest -v                          # Verbose output
pytest --cov                       # With coverage
```

### Decorator Syntax

```python
# In implementation code
@jig.implements("S-001")
def my_function():
    pass

@jig.implements("S-001", "S-002")  # Multiple specs
def another_function():
    pass

# In test code
@jig.verifies("S-001")
def test_my_function():
    pass

@jig.verifies("S-001", "S-002")    # Multiple specs
def test_comprehensive():
    pass
```

### File Naming Conventions

```
jig/outcomes/O-001.md               # Sequential numbering
jig/outcomes/O-002.md
jig/specifications/S-001.md         # Sequential numbering
jig/specifications/S-002.md
```

### Commit Message Template

```
<type>(<scope>): <brief description>

Implements: S-001, S-002
Tests: T-001, T-002
Alignment: verified

<Optional detailed explanation>

See: docs/plans/PLAN-<feature>.md → Work Unit N
```

## Version History

- **2.0.0** (2025-11-26): Aligned with JIG v8
  - Removed: Deltas, harvest pipeline, markers, subsystems
  - Simplified: O→S→TDD workflow, sequential IDs, decorator syntax
  - Focused: Alignment measurement, five artifacts, bricks

- **1.0.0** (2024): Original version (JIG v7, included deltas/harvest)

---

**Next**: Apply this workflow to your first feature. Start with Work Unit 0 (Create Intent).
