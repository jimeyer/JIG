---
title: "J017: JIG Concept v9"
type: exploration
status: superseded
created: 1764685823
created_human: "2025-12-02 08:30 CST"
parent: "[[J016_JIG-Concept-v8]]"
children: ['[[J029_JIG-Manifesto-v10]]']
superseded_by: "[[J029_JIG-Manifesto-v10]]"
---
# J017: JIG Concept v9

_The Alignment Graph with Architectural Layers_

**Date:** 2025-12-02
**Status:** Concept
**Supersedes:** J016
**References:** AG002, AG019, AG020, AG029, A001

---

## The Problem

Software systems drift. Intent diverges from implementation. Implementation diverges from verification. Codebases become archaeological sites where the relationship between "what we meant to build," "what we actually built," and "what we actually tested" is lost to time.

This drift is invisible until it's catastrophic. We have tools that measure test coverage, but coverage alone doesn't tell us if we're testing the right things. We have documentation, but documentation drifts from reality. We have requirements, but requirements live in separate systems, disconnected from code.

**The fundamental problem: we cannot measure alignment between intent, implementation, and verification.**

Without measurement, we cannot detect drift. Without detecting drift, we cannot correct it. Without correcting drift, systems decay.

**The architectural problem: even with alignment measurement, we cannot prevent architectural decay.**

Without explicit stratification, foundation code depends on features. Without dependency discipline, circular dependencies accumulate. Without work ordering, teams build in random directions. Without measurement, architectural violations are invisible until catastrophic.

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

Real systems are not monoliths. They have structure, boundaries, modules. We need a way to organize the S-F-T triangle at scale. We will take inspiration from Legos - good code is a collection of 'bricks' that snap together.

**A Brick is a partition of the function space F.**

Given all functions in a codebase, bricks divide them into named sets where:
1. Every function belongs to exactly one brick
2. Bricks are disjoint (no overlap)
3. Bricks cover all functions (no gaps)

**Brick B-auth-session might contain:**
```
F-auth.session.authenticate
F-auth.session.logout
F-auth.tokens.validate
F-auth.tokens.refresh
...
```

**Why this matters:**
- **Scoped queries:** "Is brick B-auth-session aligned?" (measure alignment for just these functions)
- **Architectural visibility:** See dependencies between bricks (B-auth-session calls B-core-utils)
- **Boundary enforcement:** Detect violations (function in B-auth-session calls private function in B-user-mgmt)
- **Work assignment:** "Implement specs for brick B-auth-session"

**Bricks derive their properties:**
- **Specs assigned to brick:** Brick implements specs that its functions implement
- **Tests assigned to brick:** Brick's tests primarily cover its functions
- **Brick dependencies:** Brick B-auth depends on B-core-utils if any F in B-auth calls any F in B-core-utils
- **Public API:** Functions called from outside the brick

Everything flows from the partition of F.

---

## Layers: Architectural Stratification

Bricks partition the function space spatially (what functions belong together), but real architectures also have **vertical structure** (what depends on what, what should be built first).

**The problem without layers:**
- Circular dependencies accumulate (B-auth ↔ B-users)
- Foundation code depends on features (B-core-utils calls B-rest-api)
- Unclear build order (which brick should be implemented first?)
- Architectural decay is invisible until catastrophic

**The solution: Each brick has a layer.**

### Layer Definition

**Layer** (integer, 0, 1, 2, ...): The architectural depth of a brick.

**Layer constraint:** A brick at layer N MAY depend only on bricks at layers 0..(N-1), or other bricks at layer N if N=0.

**Stratification property:**
- Layer 0: Foundation bricks (may depend on external libraries or other layer 0 bricks, no cycles)
- Layer 1: Bricks that depend only on layer 0
- Layer 2: Bricks that depend on layers 0-1
- Layer N: Bricks that depend on layers 0..(N-1)

### Example Layer Structure

```
Layer 0: Foundation
  B-core-utils: Core Utilities (23 functions)
  B-data-models: Data Models (15 functions)
  ↓ (may depend on each other, no cycles)

Layer 1: Core Logic
  B-impl-graph: Implementation Graph (31 functions)
    ↓ depends on: B-core-utils
  B-validation: Artifact Validation (28 functions)
    ↓ depends on: B-core-utils, B-data-models

Layer 2: Interface
  B-cli: CLI Interface (12 functions)
    ↓ depends on: B-core-utils, B-impl-graph, B-validation
```

**Dependency graph flows downward:**
```
Layer 0:  [B-core-utils]  [B-data-models]
               ↓                ↓
Layer 1:   [B-impl-graph]  [B-validation]
               ↓                ↓
Layer 2:           [B-cli]
```

### What Layers Enable

**Architectural clarity:**
- System structure is explicit (not inferred from reading code)
- New developers see the layering immediately
- Diagrams show dependencies at a glance

**Dependency discipline:**
- Prevents upward dependencies (foundation depending on features)
- Prevents circular dependencies (enforced by layer constraint)
- Makes accidental coupling visible in validation

**Work sequencing:**
- Clear build order (layer 0 first, then layer 1, etc.)
- Can't implement layer N until layer N-1 is complete
- Testing follows same order (test layer 0, then layer 1)

**Impact analysis:**
- Changes in layer 0 → test all layers
- Changes in layer N → test only layers ≥ N
- Refactoring safety: changes flow upward, never downward

**AI guidance:**
- AI agents work layer by layer (bottom-up)
- Agents know what they can depend on (lower layers only)
- Layer violations caught in validation before merge

### Layer 0 Special Rules

**Layer 0 bricks are the foundation.**

They MAY depend on:
- External libraries (standard library, pip packages)
- Other layer 0 bricks (foundation bricks cooperate)

They SHALL NOT depend on:
- Bricks in higher layers (layer 1+)

**Circular dependencies are rejected at all layers, including layer 0.**

**Example valid layer 0 structure:**
```
B-core-utils (layer 0) → [no internal deps] ✓
B-data-models (layer 0) → B-core-utils ✓
B-validation-core (layer 0) → B-data-models → B-core-utils ✓
```

**Example invalid layer 0 structure:**
```
B-data-models (layer 0) ↔ B-validation-core (layer 0) ✗ (cycle)
B-core-utils (layer 0) → B-cli (layer 2) ✗ (upward dependency)
```

**Flat architecture:** If ALL bricks are layer 0, layering constraints are effectively disabled (all bricks at foundation level). This is valid for small projects or prototypes, but provides no stratification benefits. Cycles are still rejected.

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
  - id: B-auth-session
    name: Authentication & Session Management
    layer: 1                    # NEW in v9: layer field (REQUIRED)
    units:
      - M-auth.session      # All functions in module
      - M-auth.tokens       # All functions in module

  - id: B-cli
    name: Command Line Interface
    layer: 2
    units:
      - M-cli.main
      - M-cli.commands

  - id: B-core-utils
    name: Core Utilities
    layer: 0                    # Foundation layer
    units:
      - M-utils.io
      - M-utils.yaml_utils
```

**What changed in v9:**

1. **Brick ID format:** `B-{kebab-case-name}` instead of `B-{number}`
   - Old: `B-001`, `B-002`, `B-003`
   - New: `B-auth-session`, `B-cli`, `B-core-utils`
   - Rationale: Semantic IDs are readable at a glance

2. **Layer field:** (integer, REQUIRED)
   - Declares architectural depth of brick
   - Validated against actual dependencies
   - Enforces stratification

**What it is:**
- Partition definition (assigns functions to bricks)
- Architectural declaration (layer assignments)
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

**Format:** Decorators in source code

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

**Example: intent-graph.ndjson (v9 includes layer):**
```json
{"id":"S-001","type":"specification","name":"Token Expiration","file":"jig/specifications/S-001.md"}
{"id":"O-001","type":"outcome","name":"Secure Authentication","file":"jig/outcomes/O-001.md","specifies":["S-001","S-002","S-003"]}
{"id":"B-auth-session","type":"brick","name":"Auth & Session","layer":1,"file":"jig/bricks.yaml"}
{"id":"B-core-utils","type":"brick","name":"Core Utilities","layer":0,"file":"jig/bricks.yaml"}
```

**Example: implementation-graph.ndjson**
```json
{"id":"F-auth.session.authenticate","type":"function","file":"src/auth/session.py","implements":["S-001"],"calls":["F-auth.tokens.validate"]}
{"id":"F-auth.session.logout","type":"function","file":"src/auth/session.py","implements":[],"calls":[]}
{"id":"F-auth.tokens.validate","type":"function","file":"src/auth/tokens.py","implements":["S-001"],"calls":[]}
```

**What changed in v9:**
- Brick nodes in intent-graph.ndjson now include `layer` field
- Layer is included because it's architectural metadata useful for visualization
- Layer is declarative (not derived), so belongs in intent graph

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

Define bricks with layers:
```yaml
bricks:
  - id: B-core-utils
    name: Core Utilities
    layer: 0                # Foundation
    units:
      - M-utils.io

  - id: B-auth-session
    name: Authentication
    layer: 1                # Depends on core-utils
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

### 6. Machine Validates Architecture

**NEW in v9: Layer validation**

```bash
jigy validate bricks
```

Output:
```
Validating brick partition... ✓
Validating no class splits... ✓
Validating unit references... ✓
Validating brick ID format... ✓
Validating layer constraints... ✓
  B-core-utils (layer 0): No dependencies ✓
  B-auth-session (layer 1): Depends on [B-core-utils] (all layer 0) ✓
  B-cli (layer 2): Depends on [B-core-utils, B-auth-session] (all layer <2) ✓

All validations passed.
```

**If layer violations exist:**
```
Validating layer constraints... ✗

ERROR: Layer constraint violations detected:

  B-core-utils (layer 0) depends on B-cli (layer 2)
    → F-utils.io.read_file calls F-cli.main.parse_args
    → Violation: Layer 0 cannot depend on layer 2
    → Fix: Remove the dependency or adjust layer assignments

Validation failed.
```

### 7. Machine Measures Alignment

```bash
jigy status
```

Output:
```
S-001: Token Expiration
  ✓ Implemented by: F-auth.session.authenticate (B-auth-session)
  ✓ Verified by: T-test_auth.test_token_expiration (B-auth-session)
  ✓ Test covers implementation

  Alignment: PERFECT

Overall: 100% (1/1 specs perfectly aligned)
```

### 8. Machine Visualizes Layers

**NEW in v9: Layer visualization**

```bash
jigy layers
```

Output:
```
Brick Layer Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Layer 0: Foundation (2 bricks)
─────────────────────────────────────────────
  B-core-utils: Core Utilities (23 functions)
  B-data-models: Data Models (15 functions)

Layer 1: Core Logic (2 bricks)
─────────────────────────────────────────────
  B-auth-session: Authentication (31 functions)
    ↓ depends on: B-core-utils

  B-validation: Artifact Validation (28 functions)
    ↓ depends on: B-core-utils, B-data-models

Layer 2: Interface (1 brick)
─────────────────────────────────────────────
  B-cli: CLI Interface (12 functions)
    ↓ depends on: B-core-utils, B-auth-session, B-validation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 5 bricks, 3 layers, 109 functions
Dependency graph: DAG ✓ (no cycles)
```

### 9. Machine Suggests Layers

**NEW in v9: Layer suggestion**

```bash
jigy layers suggest
```

Output:
```
Suggested layer assignments based on dependencies:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

B-core-utils: Core Utilities
  Current layer: 0
  Suggested: 0 (no dependencies)
  Status: ✓ MATCHES

B-auth-session: Authentication
  Current layer: 2
  Suggested: 1 (depends on B-core-utils at layer 0)
  Status: ⚠ MISMATCH (current too high)

Apply suggestions? [y/N]
```

With `--apply` flag:
```bash
jigy layers suggest --apply
```

This updates `jig/bricks.yaml` with suggested layer assignments.

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
For brick B-auth-session:
  - Which specs are assigned? (specs implemented by B-auth-session's functions)
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

### Layer Queries (NEW in v9)

**Layer constraint violations:**
```
Find (B₁, B₂) where:
  B₁.layer = L₁
  B₂.layer = L₂
  B₁ depends on B₂
  L₂ >= L₁ (unless both at layer 0)

Result: Layer constraint violated
```

**Circular dependencies:**
```
Find cycle (B₁ → B₂ → ... → Bₙ → B₁) where:
  B_i depends on B_{i+1}

Result: Circular dependency (rejected at all layers)
```

**Layer impact analysis:**
```
For brick B at layer L:
  - Direct dependents: Find B₂ where (B₂ depends on B) AND (B₂.layer > L)
  - All dependents: Transitive closure upward
  - Max impact layer: Max(dependent layers)

Result: Changing B affects all layers > L
```

**Work order by layer:**
```
For incomplete specs:
  Group by brick
  Group bricks by layer
  Order: Layer 0, then Layer 1, then Layer 2, ...

Result: Build foundation first, then features
```

### Impact Analysis

**What breaks if I change this function?**
```
For F:
  - Direct callers: Find F₂ where F₂ calls F
  - Indirect callers: Transitive closure of calls
  - Affected tests: Find T where T covers F
  - Affected specs: Find S where F → S
  - Affected bricks: Brick containing F, bricks calling F
  - Affected layers: Layers containing affected bricks
```

**What do I need to update if this spec changes?**
```
For S:
  - Implementing functions: Find F where F → S
  - Verifying tests: Find T where T → S
  - Affected bricks: Bricks containing implementing functions
  - Affected layers: Layers containing affected bricks
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

**Alternative considered:** Allow `@jig.brick("B-auth-session")` as override. Rejected to prevent drift and maintain single source of truth.

### Why No Dependencies in Brick Definitions?

**Rationale:** Dependencies are observable facts (F₁ calls F₂ across bricks). Storing them creates drift risk. Compute from implementation graph on demand.

**Trade-off:** Requires loading implementation graph to see dependencies. Acceptable because graph is fast to parse.

### Why Graphs Generated Before Brick Definitions?

**Rationale:** Breaks circular dependency. Implementation graph must exist before bricks can partition it. Brick assignment happens at query time (join operation).

**Alternative considered:** Include brick in implementation graph nodes. Rejected as circular (can't assign brick before bricks are defined).

### NEW in v9: Why Kebab-Case Brick IDs?

**Rationale:** Semantic naming (B-auth-session) is readable at a glance. Numeric IDs (B-001) provide no information about what the brick does. Kebab-case is standard for identifiers (URLs, filenames, package names).

**Trade-off:** Longer IDs. Acceptable because IDs are rarely typed manually (tools generate them).

**Migration:** Old `B-001` format is deprecated. Projects adopting v9 MUST migrate to kebab-case IDs.

### NEW in v9: Why Layer Field is REQUIRED?

**Rationale:** Forces architectural thinking. Every brick MUST declare its place in the hierarchy. This makes architecture explicit, not implicit.

**Escape hatch:** Projects that don't want stratification can set all bricks to `layer: 0` (flat architecture). This keeps the schema simple while supporting both use cases.

**Alternative considered:** Make layer optional. Rejected because it allows architectural debt to accumulate invisibly.

### NEW in v9: Why Include Layer in Intent Graph?

**Rationale:** Layer is architectural metadata declared by humans, not derived from implementation. It's useful for visualization and querying. It's small (one integer per brick). It doesn't create circular dependencies.

**Alternative considered:** Store layers only in bricks.yaml. Rejected because tools would need to load two files to visualize architecture.

### NEW in v9: Why Allow Layer 0 Bricks to Depend on Each Other?

**Rationale:** Foundation bricks often need each other (data models use utils, validation uses data models). Forcing them all to be independent creates artificial constraints. Cycles are still rejected.

**Trade-off:** More complex validation logic. Acceptable because it matches real architectural patterns.

**Alternative considered:** Layer 0 bricks must be independent. Rejected as too restrictive for real codebases.

### NEW in v9: Why Validate Layers Against Implementation Graph?

**Rationale:** Layers are declarations, dependencies are facts. Validation ensures declarations match reality. This catches architectural drift early.

**Alternative considered:** Only suggest layers, don't enforce. Rejected because violations accumulate without enforcement.

**Trade-off:** Requires implementation graph to validate. Acceptable because graph generation is fast.

### NEW in v9: Why Layer Violations Are Errors, Not Warnings?

**Rationale:** Layer constraints are architectural contracts. Violating them is as serious as a partition violation. Warnings are ignored; errors force fixes.

**Alternative considered:** Make layer violations warnings initially, errors later. Rejected because technical debt accumulates. Start strict, stay strict.

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

### NEW in v9 - H5a: Layer Constraints Prevent Architectural Decay

**Hypothesis:** Enforcing layer constraints will prevent upward dependencies and circular dependencies, maintaining architectural stratification over time.

**Measurable:** Number of layer constraint violations detected in validation. Trend should be downward. Zero violations should be maintainable.

**Falsifiable:** If layer violations accumulate despite validation, hypothesis is false.

**Evidence so far:** Implementation on JIG codebase (self-hosted) detected 5 bricks with missing layer fields and revealed actual dependency structure. After adding layers, validation catches violations immediately.

### H6: Improve Code Review Efficiency

**Hypothesis:** Reviewers will catch alignment issues faster with automated checks than manual review.

**Measurable:** Alignment issues detected in CI vs. code review. Target: >80% caught by CI, <20% caught by human review.

**Falsifiable:** If humans catch more alignment issues than CI, hypothesis is false.

### H7: Support Incremental Adoption

**Hypothesis:** Teams can adopt JIG incrementally (one brick at a time, one spec at a time) without all-or-nothing commitment.

**Measurable:** Adoption curve. Can teams achieve value with <30% of code annotated?

**Falsifiable:** If value requires >70% adoption, hypothesis is false (adoption barrier too high).

### NEW in v9 - H8: Layer-Guided Work Sequencing

**Hypothesis:** Teams working bottom-up (layer 0 first) will have fewer integration problems than teams working in random order.

**Measurable:** Number of integration failures in CI. Compare layer-guided development vs random order. Target: 50% reduction in integration failures.

**Falsifiable:** If layer-guided development shows no reduction in integration failures, hypothesis is false.

### NEW in v9 - H9: AI Agents Work Better with Layer Context

**Hypothesis:** AI agents given layer context ("you are working on layer 1, you may use layer 0") will produce fewer layer violations than agents without layer context.

**Measurable:** Layer violations in AI-generated code. Target: <10% of AI-generated code violates layer constraints when given layer context.

**Falsifiable:** If AI violations remain high (>30%) even with layer context, hypothesis is false.

---

## What JIG Is

**JIG is an alignment measurement system.** It makes the relationship between intent (S), implementation (F), and verification (T) explicit, measurable, and queryable.

**JIG is a graph database.** Nodes are specifications, functions, tests, bricks. Edges are implements, verifies, covers, depends. Queries traverse this graph to measure alignment.

**JIG is a developer tool.** Lightweight annotations (`@jig.implements`, `@jig.verifies`) make intent explicit without heavyweight process.

**JIG is an architectural visibility tool.** Bricks partition functions. Layers stratify bricks. Dependencies are computed. Boundaries are enforced.

**NEW in v9: JIG is an architectural stratification system.** Layers make vertical structure explicit. Layer validation prevents architectural decay. Layer visualization shows system structure at a glance.

**JIG is a CI/CD check.** Alignment queries run in continuous integration. Layer validation runs in continuous integration. Pull requests show alignment delta and layer violations.

**JIG is a documentation system.** Specifications are markdown, versioned with code, always up-to-date because alignment is measured.

**JIG is a work sequencing tool.** Layers define build order. Work proceeds from layer 0 upward. Impact analysis is bounded by layers.

---

## What JIG Is Not

**JIG is not a requirements management system.** It doesn't replace Jira, Linear, or GitHub Issues. It connects requirements (specifications) to code.

**JIG is not a test framework.** It doesn't run tests. It measures whether tests verify specifications.

**JIG is not a code quality tool.** It doesn't measure cyclomatic complexity, maintainability index, or code smells. It measures alignment.

**JIG is not a project management tool.** It doesn't track sprints, velocity, or burndown. It measures whether intent is implemented and verified.

**JIG is not a monitoring system.** It doesn't measure production behavior. It measures development-time alignment.

**JIG is not mandatory.** Functions without `@jig.implements` are fine (internal helpers). Tests without `@jig.verifies` are fine (infrastructure tests). JIG measures what you annotate.

**NEW in v9: JIG is not a module system.** It doesn't replace Python packages, Java modules, or Rust crates. It partitions and stratifies existing module structures to enforce architectural boundaries.

---

## The Evolution from v8 to v9

### What v8 Established

**Core concepts:**
- S-F-T triangle (intent, implementation, verification)
- Bricks as partitions (spatial organization)
- Five concrete artifacts (specs, outcomes, bricks, decorators, graphs)
- Measurable alignment (queries on the graph)

**Design philosophy:**
- Deliberately minimal (irreducible core)
- Measurable (objective facts)
- Queryable (graph traversal)

### What v9 Adds

**One new dimension: Layers**
- Vertical stratification (what depends on what)
- Work sequencing (build order)
- Architectural discipline (dependency constraints)

**Four new capabilities:**
1. **Layer validation:** Detect upward dependencies and cycles
2. **Layer visualization:** See system structure at a glance (`jigy layers`)
3. **Layer suggestion:** Derive layers from dependencies (`jigy layers suggest`)
4. **Layer-guided work:** Build from foundation upward

**One ID format change:**
- Brick IDs: `B-001` → `B-auth-session` (semantic naming)

**One new field:**
- `layer` (integer, REQUIRED) in brick definitions

### What Didn't Change

- S-F-T triangle (still the core)
- Bricks as partitions (still spatial organization)
- Five artifacts (still the same files)
- Decorators (still `@jig.implements`, `@jig.verifies`)
- Alignment measurement (still the fundamental value)

### Why v9 is Still Minimal

**We added one field and one constraint.**
- Field: `layer` (integer)
- Constraint: `dep_layer < brick_layer` (or both layer 0)

**Everything else flows from this:**
- Validation derives from constraint
- Visualization groups by layer
- Suggestion computes layers from dependencies
- Work sequencing follows layer order

**The irreducible core is still S-F-T.**
Layers organize bricks (which organize functions).
Layers don't change the alignment measurement.
Layers add architectural discipline without adding complexity to the core.

**This is still the foundation. Everything else builds from here.**

---

## The Focused Vision

**JIG v9 is deliberately minimal.** We removed (in v8):
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

**We added one dimension (v9):**
- Layers as stratification (vertical organization)

**This is the foundation.** Everything else builds from here.

**The measure of success:** Can we detect drift? Can we enforce boundaries? Can we measure alignment? **Can we prevent architectural decay?** If yes, we succeeded. If no, we failed.

---

## Next Steps

### For Early Adopters

1. **Write one specification** (`S-001.md`)
2. **Add one `@jig.implements` decorator** to existing code
3. **Add one `@jig.verifies` decorator** to existing test
4. **Define one brick with a layer** (`B-core-utils`, `layer: 0`)
5. **Generate graphs** and see alignment
6. **Validate architecture** and see layer structure
7. **Iterate:** Add more specs, more decorators, more bricks, measure continuously

### For Tool Builders

1. **Implement graph generators** (parse specs, parse decorators, run coverage)
2. **Implement validation** (check references, check partition, **check layers**)
3. **Implement alignment queries** (unimplemented, unverified, untested)
4. **Implement visualization** (show S-F-T triangle, show brick dependencies, **show layer structure**)
5. **Integrate with CI** (fail build on misalignment **or layer violations**)

### For the JIG Project

1. **Validate hypotheses** with real projects (especially H5a, H8, H9)
2. **Refine tooling** based on feedback
3. **Document patterns** (how to write good specs, when to create bricks, **how to assign layers**)
4. **Build ecosystem** (IDE plugins, CI integrations, visualizations, **layer-aware AI agents**)
5. **Measure impact** (drift detection time, alignment percentage, adoption rate, **layer violation trends**)

---

## Conclusion

The Alignment Graph is simple: specifications, functions, tests, bricks, layers, and the relationships between them.

The implementation is minimal: markdown files, YAML definitions, Python decorators, NDJSON graphs, one integer field.

The value is measurable: detect drift, enforce boundaries, verify intent, **prevent architectural decay**.

**JIG v9 adds layers to the foundation. Alignment in three dimensions: intent, boundaries, and structure.**

**Let's build on it.**

---

## References

- **A001:** Core Artifacts Contract (normative specification, updated for layers)
- **AG029:** Brick Layers - Architectural Stratification (layer design rationale)
- **AG019:** Irreducible Core (S-F-T triangle)
- **AG020:** Bricks as Partitions
- **AG002:** Alignment Graph Whitepaper (original concept)
- **J016:** JIG Concept v8 (predecessor, before layers)
- **J013:** JIG Concept v7 (predecessor, broader scope)
- **B004:** Layer Validation and CLI Implementation Plan (actual implementation)

---

## Validation Evidence

**v9 implemented and validated on JIG codebase itself (self-hosted):**

**Specifications created:** S-035 through S-041 (7 specs defining layer validation system)

**Implementation:**
- Brick ID format validation (S-035)
- Layer field presence validation (S-036)
- Layer value validation (S-037)
- Layer constraint validation (S-038)
- Circular dependency detection (S-039)
- CLI `jigy layers` visualization (S-040)
- CLI `jigy layers suggest` (S-041)

**Test coverage:** 220 tests passing
- 29 brick validation tests
- 20 layer/cycle validation tests
- 19 CLI layers tests
- 5 integration tests
- 147 existing tests (all still passing)

**Results:**
- ✓ Layer validation detected 5 bricks with missing layer fields in JIG codebase
- ✓ Layer suggestion correctly computed layer assignments from dependency structure
- ✓ Layer visualization shows 3-layer architecture (foundation, core logic, interface)
- ✓ No layer constraint violations after layer assignment
- ✓ No circular dependencies detected

**Implementation time:** 7 work units over 5 days (WU0-WU7 in B004)

**Conclusion:** Layers are implementable, validatable, and provide immediate architectural visibility on a real codebase. The concept works in practice.

---

_Alignment in three dimensions: intent, boundaries, and structure._
