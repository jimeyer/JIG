---
title: "J016: JIG Concept v8"
type: exploration
status: superseded
created: 1764187522
created_human: "2025-11-26 14:05 CST"
parent: "[[J013_JIG-Concept-v7]]"
children: ['[[J017_JIG-Concept-v9]]']
superseded_by: "[[J017_JIG-Concept-v9]]"
---
# J016: JIG Concept v8

_The Alignment Graph - Simplified to Its Essence_

**Date:** 2025-11-26
**Status:** Concept
**Supersedes:** J013
**References:** AG002, AG019, AG020, A001

---

## The Problem

Software systems drift. Intent diverges from implementation. Implementation diverges from verification. Codebases become archaeological sites where the relationship between "what we meant to build," "what we actually built," and "what we actually tested" is lost to time.

This drift is invisible until it's catastrophic. We have tools that measure test coverage, but coverage alone doesn't tell us if we're testing the right things. We have documentation, but documentation drifts from reality. We have requirements, but requirements live in separate systems, disconnected from code.

**The fundamental problem: we cannot measure alignment between intent, implementation, and verification.**

Without measurement, we cannot detect drift. Without detecting drift, we cannot correct it. Without correcting drift, systems decay.

---

## The Core Idea: The Alignment Graph

**What if intent, implementation, and verification were nodes in a graph, and their relationships were edges we could traverse?**

This is the Alignment Graph: a unified representation that makes alignment explicit, measurable, and queryable.

Instead of:
- Requirements in Jira
- Code in repositories
- Tests in separate files
- No visible connection between them

We get:
- Intent declared in specifications (`S-001`, `S-002`)
- Implementation annotated with intent (`@jig.implements("S-001")`)
- Verification annotated with intent (`@jig.verifies("S-001")`)
- A graph connecting all three, making alignment visible

**The graph answers fundamental questions:**
- Which specifications are implemented? (F → S edges)
- Which specifications are verified? (T → S edges)
- Do tests actually execute the code they claim to verify? (T → F edges)

---

## The Irreducible Core: S-F-T Triangle

The Alignment Graph reduces to three node types and three edge types. Everything else is organizational scaffolding.

### Three Node Types

**S - Specifications**
What we intend to build. Concrete, testable requirements.
- Example: "Authentication tokens must expire after 15 minutes of inactivity"
- Stored as: `S-001`, `S-002`, `S-003`

**F - Functions**
What we actually built. The implementation.
- Example: `F-auth.session.authenticate`
- Discovered by parsing code (AST analysis)

**T - Tests**
What we actually verify. The validation.
- Example: `T-test_auth.test_token_expiration`
- Discovered by test discovery (pytest, unittest)

### Three Edge Types

**F → S (implements)**
Which functions implement which specifications.
- Declared by developer: `@jig.implements("S-001")`
- Makes intent explicit in code

**T → S (verifies)**
Which tests verify which specifications.
- Declared by developer: `@jig.verifies("S-001")`
- Makes verification intent explicit

**T → F (covers)**
Which tests execute which functions.
- Discovered automatically via coverage analysis
- Objective, machine-observed fact

### The Triangle

```
         S (Spec)
        ╱   ╲
       ╱     ╲
      ╱       ╲
     ╱       verifies  
implements      ╲
   ╱             ╲
  ╱               ╲
 ▼                 ▼
F ───── covers─────> T
 (Function)          (Test)
```

**Perfect alignment exists when all three edges are present:**
- Specification S is implemented by function F (F → S)
- Specification S is verified by test T (T → S)
- Test T executes function F (T → F)

**Alignment is measurable, objective, and queryable.**

---

## Bricks: Architectural Partitions

Real systems are not monoliths. They have structure, boundaries, modules. We need a way to organize the S-F-T triangle at scale.   We will take inspiration from Legos - good code is a collection of 'bricks' that snap together.

**A Brick is a partition of the function space F.**

Given all functions in a codebase, bricks divide them into named sets where:
1. Every function belongs to exactly one brick
2. Bricks are disjoint (no overlap)
3. Bricks cover all functions (no gaps)

**Brick B-001 might contain:**
```
F-auth.session.authenticate
F-auth.session.logout
F-auth.tokens.validate
F-auth.tokens.refresh
...
```

**Why this matters:**
- **Scoped queries:** "Is brick B-001 aligned?" (measure alignment for just these functions)
- **Architectural visibility:** See dependencies between bricks (B-001 calls B-003)
- **Boundary enforcement:** Detect violations (function in B-001 calls private function in B-002)
- **Work assignment:** "Implement specs for brick B-001"

**Bricks derive their properties:**
- **Specs assigned to brick:** Brick implements specs that its functions implement
- **Tests assigned to brick:** Brick's tests primarily cover its functions
- **Brick dependencies:** Brick B-001 depends on B-003 if any F in B-001 calls any F in B-003
- **Public API:** Functions called from outside the brick

Everything flows from the partition of F.

---

## Concrete Implementation: Five Artifacts

The Alignment Graph is built from five artifacts (defined normatively in A001):

### 1. Specification Files

**Format:** Markdown with minimal YAML frontmatter

**File:** `jig/specifications/S-001.md`
```markdown
---
id: S-001
type: specification
---

# Token Expiration

Authentication tokens MUST expire after 15 minutes of inactivity.

**Acceptance Criteria:**
- Token created with expires_at = now() + 15 minutes
- Any operation updates last_activity timestamp
- Token rejected if now() > last_activity + 15 minutes

**Rationale:** Limits exposure window if token is compromised.
```

**What it is:**
- Human-authored intent
- One spec per file
- Sequential numbering (S-001, S-002, S-003)
- No domain prefixes (removed for simplicity)

**What it's not:**
- Not connected to bricks (circular dependency)
- Not connected to code directly (only via decorators)
- Not machine-executed (documentation for humans and AI agents)

### 2. Outcome Files (Optional)

**Format:** Markdown with minimal YAML frontmatter

**File:** `jig/outcomes/O-001.md`
```markdown
---
id: O-001
type: outcome
specifies: [S-001, S-002, S-003]
---

# Secure Authentication Without Passwords

Users can authenticate securely without managing passwords or secrets.

**Value:** Reduces support burden (no password resets) and improves security.
```

**What it is:**
- High-level goals that decompose into specs
- Optional (can omit if specs are self-explanatory)
- Explains WHY specs exist

**Relationship:** Outcomes → Specifications (one outcome may specify multiple specs)

### 3. Brick Definitions

**Format:** Single YAML file

**File:** `jig/bricks.yaml`
```yaml
bricks:
  - id: B-001
    name: Authentication & Session Management
    units:
      - M-auth.session      # All functions in module
      - M-auth.tokens       # All functions in module

  - id: B-002
    name: Command Line Interface
    units:
      - M-cli.main
      - M-cli.commands

  - id: B-003
    name: Core Utilities
    units:
      - M-utils.io
      - M-utils.yaml_utils
```

**What it is:**
- Partition definition (assigns functions to bricks)
- Uses M-/C-/F- prefixes (Module/Class/Function)
- Direct references to implementation graph nodes
- Unambiguous and machine-verifiable

**Units expand:**
- `M-auth.session` → all `F-auth.session.*` functions
- `C-auth.tokens.TokenValidator` → all `F-auth.tokens.TokenValidator.*` methods
- `F-auth.utils.hash_password` → exactly this one function

**What it's not:**
- Not storing dependencies (computed from call graph)
- Not storing public API (computed from calls across bricks)
- Not storing specs (derived from functions' implementations)

### 4. @jig Decorators

**Format:**  Decorators in source code

**@jig.implements (declares F → S edge):**
```python
@jig.implements("S-001")
def authenticate(user: str, password: str) -> Token:
    """Authenticate user and return session token."""
    token = Token(
        user=user,
        expires_at=datetime.now() + timedelta(minutes=15)
    )
    return token
```

**@jig.verifies (declares T → S edge):**
```python
@jig.verifies("S-001")
def test_token_expiration():
    """Verify tokens expire after 15 minutes."""
    token = authenticate("user", "pass")
    token.last_activity = datetime.now() - timedelta(minutes=15, seconds=1)
    assert is_expired(token)
```

**What it is:**
- Lightweight annotations (one line)
- Lives with the code (git tracks together)
- Explicit intent (no guessing from comments)
- Machine-parseable (AST extraction)

**What it's not:**
- Not a separate mapping file (co-located with code)
- Not comments (structured, queryable)
- Not optional if you want alignment measurement

### 5. Graph Files

**Format:** NDJSON (Newline-Delimited JSON)

**Location:** `jig/generated/`

**Three files:**
```
jig/generated/intent-graph.ndjson           # S, O, B nodes
jig/generated/implementation-graph.ndjson   # F nodes, F→S edges
jig/generated/verification-graph.ndjson     # T nodes, T→S edges, T→F edges
```

**Why NDJSON:** One JSON object per line. Clean git diffs (only changed lines show).

**Example: implementation-graph.ndjson**
```json
{"id":"F-auth.session.authenticate","type":"function","file":"src/auth/session.py","implements":["S-001"],"calls":["F-auth.tokens.validate"]}
{"id":"F-auth.session.logout","type":"function","file":"src/auth/session.py","implements":[],"calls":[]}
{"id":"F-auth.tokens.validate","type":"function","file":"src/auth/tokens.py","implements":["S-001"],"calls":[]}
```

**What it is:**
- Machine-generated (never manually edited)
- Observable facts (structure, relationships)
- Fast to parse and query
- Git-committable (human-inspectable)

**What it's not:**
- Not storing derived data (metrics computed on demand)
- Not storing brick assignments (computed at query time)
- Not storing line numbers (brittle, computable when needed)

---

## The Workflow

### 1. Human Authors Intent

Write specifications:
```markdown
---
id: S-001
type: specification
---

# Token Expiration

Tokens must expire after 15 minutes of inactivity.
```

### 2. Human Defines Architecture

Define bricks:
```yaml
bricks:
  - id: B-001
    name: Authentication
    units:
      - M-auth.session
      - M-auth.tokens
```

### 3. Human Implements with Intent

Write code with decorators:
```python
@jig.implements("S-001")
def authenticate(user, password):
    token = create_token(user)
    token.expires_at = now() + timedelta(minutes=15)
    return token
```

### 4. Human Verifies with Intent

Write tests with decorators:
```python
@jig.verifies("S-001")
def test_token_expiration():
    token = authenticate("user", "pass")
    time.sleep(901)  # 15 min + 1 sec
    assert is_expired(token)
```

### 5. Machine Generates Graphs

```bash
jigy index         # Generate intent-graph.ndjson
jigy impl rebuild  # Generate implementation-graph.ndjson
jigy verify rebuild --run-tests  # Generate verification-graph.ndjson
```

### 6. Machine Measures Alignment

```bash
jigy status
```

Output:
```
S-001: Token Expiration
  ✓ Implemented by: F-auth.session.authenticate (B-001)
  ✓ Verified by: T-test_auth.test_token_expiration (B-001)
  ✓ Test covers implementation

  Alignment: PERFECT

Overall: 100% (1/1 specs perfectly aligned)
```

---

## Queries the System Enables

### Basic Alignment Queries

**Unimplemented specs:**
```
Find S where NOT EXISTS F: F → S
```

**Unverified specs:**
```
Find S where NOT EXISTS T: T → S
```

**Untested functions:**
```
Find F where NOT EXISTS T: T → F
```

**Orphan code:**
```
Find F where NOT EXISTS S: F → S
(Functions implementing no specification)
```

**Misaligned verification:**
```
Find (S, F, T) where:
  F → S (function implements spec)
  T → S (test verifies spec)
  BUT NOT T → F (test doesn't execute function)
```

### Architectural Queries

**Brick alignment:**
```
For brick B-001:
  - Which specs are assigned? (specs implemented by B-001's functions)
  - Are they all implemented? (all S have F → S)
  - Are they all verified? (all S have T → S)
  - Alignment percentage?
```

**Brick dependencies:**
```
Find all B₂ where:
  EXISTS F₁ ∈ B₁, F₂ ∈ B₂: F₁ calls F₂

Result: B₁ depends on B₂ (computed, not stored)
```

**Boundary violations:**
```
Find (F₁, F₂) where:
  F₁ ∈ B₁, F₂ ∈ B₂
  F₁ calls F₂
  B₁ does NOT depend on B₂

Result: Illegal cross-brick call
```

**Public API:**
```
Find F ∈ B where:
  EXISTS F_external ∉ B: F_external calls F

Result: F is part of B's public API (computed, not stored)
```

### Impact Analysis

**What breaks if I change this function?**
```
For F:
  - Direct callers: Find F₂ where F₂ calls F
  - Indirect callers: Transitive closure of calls
  - Affected tests: Find T where T covers F
  - Affected specs: Find S where F → S
```

**What do I need to update if this spec changes?**
```
For S:
  - Implementing functions: Find F where F → S
  - Verifying tests: Find T where T → S
  - Dependent specs: Find S₂ where S₂ depends on S (informal, in markdown)
```

---

## Design Decisions

### Why Three Separate Graph Files?

**Rationale:** Intent changes rarely (design decisions stable). Implementation changes frequently (code edited daily). Verification changes on test runs. Separating them minimizes git churn.

**Alternative considered:** One combined file. Rejected because every code change rewrites the entire file, polluting git history.

### Why NDJSON Instead of Pretty-Printed JSON?

**Rationale:** Git diffs. One node per line means only changed nodes show in diffs. Pretty-printed JSON shows entire object as changed.

**Trade-off:** Less human-readable. Acceptable because graphs are machine-generated and tools parse them, not humans.

### Why Sequential Number IDs (S-001) Not Domain Prefixes (S-AUTH-001)?

**Rationale:** Domain is an undefined concept (not brick, not subsystem, just noise). Sequential numbers are sufficient for uniqueness. Human-readable names belong in the `name` field, not the ID.

**Trade-off:** IDs don't indicate domain. Acceptable because brick assignment and `name` fields provide context.

### Why Bricks Use M-/C-/F- Prefixes?

**Rationale:** Direct reference to implementation graph nodes. Unambiguous (prefix indicates type). Verifiable (validate units exist in graph). Language-agnostic foundation (easy to add P- for packages, K- for crates).

**Alternative considered:** Plain strings (`auth.session`). Rejected as ambiguous (module? class? function?).

### Why No @jig.brick Decorator?

**Rationale:** Single source of truth. If bricks are defined in `bricks.yaml`, decorators are redundant and can drift. Fix organization at the source (bricks.yaml), don't paper over with scattered decorators.

**Alternative considered:** Allow `@jig.brick("B-001")` as override. Rejected to prevent drift and maintain single source of truth.

### Why No Dependencies in Brick Definitions?

**Rationale:** Dependencies are observable facts (F₁ calls F₂ across bricks). Storing them creates drift risk. Compute from implementation graph on demand.

**Trade-off:** Requires loading implementation graph to see dependencies. Acceptable because graph is fast to parse.

### Why Graphs Generated Before Brick Definitions?

**Rationale:** Breaks circular dependency. Implementation graph must exist before bricks can partition it. Brick assignment happens at query time (join operation).

**Alternative considered:** Include brick in implementation graph nodes. Rejected as circular (can't assign brick before bricks are defined).

---

## Hypotheses

We believe the Alignment Graph will:

### H1: Make Drift Visible

**Hypothesis:** By measuring alignment continuously, we will detect drift early (days, not months).

**Measurable:** Time from drift introduction to detection. Current baseline: weeks to months (discovered in code review or production). Target: hours to days (detected by alignment queries).

**Falsifiable:** If drift is not detected faster, hypothesis is false.

### H2: Reduce Unverified Code

**Hypothesis:** Making verification intent explicit will increase test coverage of specifications, not just line coverage.

**Measurable:** Percentage of specifications with `T → S` edges. Current baseline: unknown (no measurement). Target: >90% of specs have verifying tests.

**Falsifiable:** If spec verification remains low (<70%), hypothesis is false.

### H3: Simplify Onboarding

**Hypothesis:** New developers will understand system intent faster when specifications are directly linked to code.

**Measurable:** Time to first meaningful contribution. Survey: "How long until you understood what the code was supposed to do?"

**Falsifiable:** If onboarding time doesn't decrease, hypothesis is false.

### H4: Enable AI-Assisted Development

**Hypothesis:** AI agents given specifications can generate aligned code (with `@jig.implements` decorators) and verify implementation with alignment checks.

**Measurable:** Percentage of AI-generated code that is aligned on first attempt. Target: >80% alignment without human correction.

**Falsifiable:** If AI-generated code alignment is <50%, hypothesis is false.

### H5: Prevent Architecture Decay

**Hypothesis:** Boundary violation detection will prevent architectural decay (unintended dependencies between bricks).

**Measurable:** Number of boundary violations over time. Trend should be downward (violations detected and fixed). Violations should not accumulate.

**Falsifiable:** If violations accumulate (trend upward), hypothesis is false.

### H6: Improve Code Review Efficiency

**Hypothesis:** Reviewers will catch alignment issues faster with automated checks than manual review.

**Measurable:** Alignment issues detected in CI vs. code review. Target: >80% caught by CI, <20% caught by human review.

**Falsifiable:** If humans catch more alignment issues than CI, hypothesis is false.

### H7: Support Incremental Adoption

**Hypothesis:** Teams can adopt JIG incrementally (one brick at a time, one spec at a time) without all-or-nothing commitment.

**Measurable:** Adoption curve. Can teams achieve value with <30% of code annotated?

**Falsifiable:** If value requires >70% adoption, hypothesis is false (adoption barrier too high).

---

## What JIG Is

**JIG is an alignment measurement system.** It makes the relationship between intent (S), implementation (F), and verification (T) explicit, measurable, and queryable.

**JIG is a graph database.** Nodes are specifications, functions, tests. Edges are implements, verifies, covers. Queries traverse this graph to measure alignment.

**JIG is a developer tool.** Lightweight annotations (`@jig.implements`, `@jig.verifies`) make intent explicit without heavyweight process.

**JIG is an architectural visibility tool.** Bricks partition functions. Dependencies are computed. Boundaries are enforced.

**JIG is a CI/CD check.** Alignment queries run in continuous integration. Pull requests show alignment delta.

**JIG is a documentation system.** Specifications are markdown, versioned with code, always up-to-date because alignment is measured.

---

## What JIG Is Not

**JIG is not a requirements management system.** It doesn't replace Jira, Linear, or GitHub Issues. It connects requirements (specifications) to code.

**JIG is not a test framework.** It doesn't run tests. It measures whether tests verify specifications.

**JIG is not a code quality tool.** It doesn't measure cyclomatic complexity, maintainability index, or code smells. It measures alignment.

**JIG is not a project management tool.** It doesn't track sprints, velocity, or burndown. It measures whether intent is implemented and verified.

**JIG is not a monitoring system.** It doesn't measure production behavior. It measures development-time alignment.

**JIG is not mandatory.** Functions without `@jig.implements` are fine (internal helpers). Tests without `@jig.verifies` are fine (infrastructure tests). JIG measures what you annotate.

---

## The Focused Vision

**JIG v8 is deliberately minimal.** We removed:
- Deltas (too complex)
- Delta harvest pipeline (premature optimization)
- Constraints (orthogonal concern)
- Subsystems (bricks are sufficient)
- Nested subsystems (flat is better)

**We kept the irreducible core:**
- S-F-T triangle (intent, implementation, verification)
- Bricks as partitions (architectural boundaries)
- Five concrete artifacts (specs, outcomes, bricks, decorators, graphs)
- Measurable alignment (queries on the graph)

**This is the foundation.** Everything else builds from here.

**The measure of success:** Can we detect drift? Can we enforce boundaries? Can we measure alignment? If yes, we succeeded. If no, we failed.

---

## Next Steps

### For Early Adopters

1. **Write one specification** (`S-001.md`)
2. **Add one `@jig.implements` decorator** to existing code
3. **Add one `@jig.verifies` decorator** to existing test
4. **Generate graphs** and see alignment
5. **Iterate:** Add more specs, more decorators, measure continuously

### For Tool Builders

1. **Implement graph generators** (parse specs, parse decorators, run coverage)
2. **Implement validation** (check references, check partition)
3. **Implement alignment queries** (unimplemented, unverified, untested)
4. **Implement visualization** (show S-F-T triangle, show brick dependencies)
5. **Integrate with CI** (fail build on misalignment)

### For the JIG Project

1. **Validate hypotheses** with real projects
2. **Refine tooling** based on feedback
3. **Document patterns** (how to write good specs, when to create bricks)
4. **Build ecosystem** (IDE plugins, CI integrations, visualizations)
5. **Measure impact** (drift detection time, alignment percentage, adoption rate)

---

## Conclusion

The Alignment Graph is simple: specifications, functions, tests, and the relationships between them.

The implementation is minimal: markdown files, YAML definitions, Python decorators, NDJSON graphs.

The value is measurable: detect drift, enforce boundaries, verify intent.

**JIG v8 is the foundation. Let's build on it.**

---

## References

- **A001:** Core Artifacts Contract (normative specification)
- **AG019:** Irreducible Core (S-F-T triangle)
- **AG020:** Bricks as Partitions
- **AG002:** Alignment Graph Whitepaper (original concept)
- **J013:** JIG Concept v7 (predecessor, broader scope)
