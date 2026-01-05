---
title: "Core Artifacts Contract (Refined)"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1764187522
created_human: "2025-11-26 14:05 CST"
parent: "[[AG023_PROPOSAL_Core-Artifacts-Contract]]"
children: []
---
# Core Artifacts Contract (Refined)

_The Simplest Definition That Could Possibly Work_

**Date:** 2025-11-26
**Status:** Proposal (Refined from AG023)
**Related:** AG017, AG018, AG019, AG020, AG023

---

## Purpose

This document refines AG023 based on critical simplifications:

**Core principles:**
1. **Eliminate circular dependencies** (graphs generated before brick assignment)
2. **Remove derived data** (brick dependencies computed, not stored)
3. **Minimize required fields** (only what cannot be computed)
4. **Simplify IDs** (S-001 not S-AUTH-001)
5. **One source of truth** (bricks.yaml defines partition, not decorators)

---

## The Five Core Artifacts

1. **Specification files** (`.md` with minimal YAML frontmatter)
2. **Outcome files** (`.md` with minimal YAML frontmatter) - OPTIONAL
3. **Brick definitions** (`bricks.yaml`, single file)
4. **@jig decorators** (`@jig.implements`, `@jig.verifies`)
5. **Graph files** (`.ndjson`, machine-generated, in `jig/generated/`)

---

## 1. Specification Files

**Location:** `jig/specifications/S-{number}.md`

**Naming:** One spec per file, numbered sequentially
- `S-001.md`, `S-002.md`, `S-003.md`, etc.
- Numbers assigned sequentially as specs are created
- No domain prefix (removes undefined "domain" concept)

### Required YAML Frontmatter

```yaml
---
id: S-001
type: specification
---
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique identifier. Format: `S-{number}` (e.g., `S-001`, `S-042`) |
| `type` | string | ✓ | Must be exactly `"specification"` |

### Removed Fields (from AG023)

| Field | Why Removed |
|-------|-------------|
| `brick` | **Circular dependency.** Brick assignment derived from F→S edges. Spec doesn't know which brick implements it. |
| `depends_on` | **Not part of core triangle.** Spec dependencies are documentation, not structural. If needed, express in markdown body. |
| `content` | **Brittle.** Extracting first heading is fragile. Content stays in markdown, not extracted to graph. |

### Markdown Body

**Purpose:** Documentation for humans and AI agents. Not parsed by jig system.

**Contents:**
- What the specification requires
- Acceptance criteria
- Examples, rationale, constraints
- Related specs (informal references)

**Example:**

```markdown
---
id: S-001
type: specification
---

# Token Expiration

Authentication tokens MUST expire after 15 minutes of inactivity.

**Acceptance Criteria:**
- Token created with `expires_at = now() + 15 minutes`
- Any operation updates `last_activity` timestamp
- Token rejected if `now() > last_activity + 15 minutes`

**Rationale:** Limits exposure window if token is compromised.

**Related:** S-002 (rate limiting), S-003 (token validation)
```

### Why These Choices?

**Simple numeric IDs (S-001) instead of domain prefixes (S-AUTH-001):**
- Domain is an undefined concept (not brick, not subsystem)
- Introduces noise without structural benefit
- Grouping can be inferred from brick assignment or file organization
- Numbers are sufficient for uniqueness
- Simpler to reference in conversation ("spec one" vs "auth spec zero-zero-one")

**No brick field:**
- Spec is independent of implementation
- Brick assignment is derived: "Which functions implement S-001?" → those functions' brick
- Spec can be implemented by multiple bricks (cross-cutting concern)
- Removes circular dependency (spec doesn't need to know about bricks)

**No depends_on field:**
- Spec-to-spec dependencies are not part of core S-F-T triangle
- If implementation order matters, express as implementation dependency (F calls F)
- Can be documented informally in markdown ("requires S-002 to be implemented first")
- Removes field that's rarely used correctly

**No content field in graph:**
- Content is the markdown file itself
- Extracting first heading is brittle (what if heading changes? what if no heading?)
- Tools can read markdown directly when needed
- Graph stores structure (IDs, relationships), not content

---

## 2. Outcome Files (OPTIONAL)

**Location:** `jig/outcomes/O-{number}.md`

**Naming:** One outcome per file, numbered sequentially
- `O-001.md`, `O-002.md`, etc.

**Status:** Optional. Omit if:
- Specs are self-explanatory
- Prototyping/exploring
- Don't need stakeholder-facing documentation

### Required YAML Frontmatter (if present)

```yaml
---
id: O-001
type: outcome
specifies: [S-001, S-002]
---
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique identifier. Format: `O-{number}` |
| `type` | string | ✓ | Must be exactly `"outcome"` |
| `specifies` | array | ✓ | Array of Spec IDs this outcome decomposes into. May be empty `[]`. |

### Removed Fields (from AG023)

| Field | Why Removed |
|-------|-------------|
| `brick` | Same reasoning as specs. Brick assignment derived from which specs the outcome references. |
| `content` | Same reasoning as specs. Content stays in markdown. |

### Markdown Body

**Purpose:** Documentation for humans and AI agents. Explains WHY specs exist.

**Example:**

```markdown
---
id: O-001
type: outcome
specifies: [S-001, S-002, S-003]
---

# Secure Authentication Without Passwords

Users can authenticate securely without managing passwords or secrets.

**Value:** Reduces support burden (no password resets) and improves security (no passwords to steal).

**Approach:** Token-based authentication with expiration, rate limiting, and cryptographic validation.

**Success Metrics:** <95% support tickets related to authentication, zero password breaches.
```

### Do Outcomes Point to Specs?

**YES.** The `specifies` field creates O→S edges.

**Why:**
- Outcomes are high-level goals
- Specs are concrete requirements that achieve those goals
- O→S edges document decomposition (outcome broken into specs)
- Enables "which specs support this outcome?" query

**Example:**
```
O-001: Secure Authentication
  ├─ S-001: Token Expiration
  ├─ S-002: Rate Limiting
  └─ S-003: Cryptographic Signatures
```

---

## 3. Brick Definitions

**Location:** `jig/bricks.yaml` (single file, all bricks)

**Why one file?**
- See entire partition in one place
- Understand full system architecture
- Easier to validate (all bricks in one place, check coverage)
- Simpler for small/medium projects
- If project grows large (>20 bricks), can split later

### Structure

```yaml
bricks:
  - id: B-001
    name: Authentication & Session Management
    units:
      - M-auth.session
      - M-auth.tokens

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

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique identifier. Format: `B-{number}` (e.g., `B-001`, `B-002`) |
| `name` | string | ✓ | Human-readable name |
| `units` | array | ✓ | Array of implementation graph node IDs using M-/C-/F- prefixes (e.g., `M-auth.session`, `C-auth.tokens.TokenValidator`, `F-utils.hash_password`). References nodes directly from implementation-graph.ndjson. |

### Removed Fields (from AG023)

| Field | Why Removed |
|-------|-------------|
| `depends_on` | **Derived from implementation graph.** Brick B-001 depends on B-003 if any F in B-001 calls any F in B-003. Don't store what can be computed. |
| `public_api` | **Derived from call graph.** Function F is public if called from outside its brick. Computed, not stored. |
| `specs` | **Derived from F→S edges.** Brick implements specs that its functions implement. |

### Brick ID Format: B-{number}

**Why B-{number} (like S-001, O-001)?**
- **Consistency:** All human-authored artifact IDs follow same pattern (prefix + number)
- **Domain removed:** Same reasoning as removing domain from spec IDs
- **Name exists:** `name` field provides human-readable label
- **Parallel structure:** S-001, O-001, B-001 (clean, consistent)
- **Simpler:** Sequential numbering, no naming debates

Examples: `B-001`, `B-002`, `B-003`

**Human-readable names in `name` field:**
- ID: `B-001` → Name: "Authentication & Session Management"
- ID: `B-002` → Name: "Command Line Interface"
- ID: `B-003` → Name: "Core Utilities"

### Partition Definition: Direct Implementation Graph References

**Units reference implementation graph nodes directly** using M-/C-/F- prefixes:

```yaml
- id: B-001
  name: Authentication
  units:
    - M-auth.session                    # All functions in module (F-auth.session.*)
    - C-auth.tokens.TokenValidator      # All methods of class (F-auth.tokens.TokenValidator.*)
    - F-auth.utils.hash_password        # Exactly this function
```

**Why this approach:**
- **Unambiguous:** References actual node IDs from implementation-graph.ndjson
- **Direct:** No translation layer needed
- **Consistent:** Uses same M-/C-/F- prefixes as implementation graph
- **Language-agnostic foundation:** Easy to extend (P- for packages, K- for crates, etc.)

**Granularity options:**
- **Coarse (module-level):** `units: [M-auth.session]` → all functions in module
- **Medium (class-level):** `units: [C-auth.tokens.TokenValidator]` → all methods
- **Fine (function-level):** `units: [F-auth.session.authenticate]` → exactly this function
- **Mixed:** Combine all three in same brick (common, practical)

**Expansion examples:**
```
M-auth.session → [F-auth.session.authenticate, F-auth.session.logout, F-auth.session.create_session, ...]
C-auth.tokens.TokenValidator → [F-auth.tokens.TokenValidator.validate, F-auth.tokens.TokenValidator.refresh, ...]
F-auth.utils.hash_password → [F-auth.utils.hash_password]  (exactly one)
```

### Why M-/C-/F- Prefixes Are The Foundation

**Key insight:** Brick definitions directly reference implementation graph node IDs.

**This is unambiguous and foundational because:**

1. **No translation layer:** `M-auth.session` in bricks.yaml means module node `M-auth.session` from implementation-graph.ndjson
2. **Type-safe:** Prefix indicates what's being referenced (module vs class vs function)
3. **Verifiable:** Can validate that all unit IDs exist in implementation graph
4. **Language-agnostic:** Easy to add P- (packages), K- (crates), etc. for other languages
5. **Future-proof:** Implementation graph already uses these prefixes

**Comparison with alternatives:**

| Approach | Example | Problems |
|----------|---------|----------|
| **AG023** | Three arrays: `modules: [auth.session]`, `classes: [...]`, `functions: [...]` | Ambiguous (what if class and module have same name?), verbose (three fields) |
| **Plain strings** | `units: [auth.session]` | Ambiguous (module? class? function?), requires context to interpret |
| **Type prefixes** | `units: [module.auth.session]` | Verbose, doesn't match graph IDs, requires translation |
| **AG024 (M-/C-/F-)** | `units: [M-auth.session]` | ✓ Unambiguous, ✓ Direct graph reference, ✓ Concise |

**This is the foundation** because bricks partition the implementation graph. Using the graph's own ID format is the most direct, unambiguous choice.

### Do We Need depends_on?

**NO.** Dependencies are **derived from the implementation graph.**

**Derivation:**
```python
def compute_brick_dependencies(bricks, functions):
    deps = {brick["id"]: set() for brick in bricks}

    # For each function
    for func in functions.values():
        source_brick = get_brick_for_function(func["id"], bricks)

        # For each function it calls
        for called_id in func["calls"]:
            target_brick = get_brick_for_function(called_id, bricks)

            if source_brick != target_brick:
                deps[source_brick].add(target_brick)

    return deps
```

**Example:**
```
F-auth.session.authenticate ∈ B-001
F-auth.session.authenticate calls F-utils.io.read_file
F-utils.io.read_file ∈ B-003

Therefore: B-001 depends on B-003 (derived, not stored)
```

**Why not store it?**
- Implementation graph is source of truth (actual calls)
- Stored dependencies can drift from reality
- Code changes, dependencies change automatically
- No manual maintenance

**When to check dependencies?**
- `jigy status` computes and displays brick dependencies
- `jigy validate` checks for circular dependencies
- All computed on-demand from implementation graph

### Constraints

**1. Partition constraint:**
Every function MUST belong to exactly one brick.

**2. No class splitting:**
All methods of a class MUST be in the same brick.

**3. Completeness:**
All functions in codebase MUST be assigned to a brick (no gaps).

### Language Future-Proofing

**Current implementation (Python):**
```yaml
units:
  - M-auth.session                    # Module → all F-auth.session.*
  - C-auth.tokens.TokenValidator      # Class → all F-auth.tokens.TokenValidator.*
  - F-auth.session.authenticate       # Function → exactly this function
```

**Future languages** can extend with new prefixes:

**Go:**
```yaml
units:
  - P-auth/session          # Package (P-) → all functions in package
  - F-auth.Authenticate     # Function (no classes in Go)
```

**Java:**
```yaml
units:
  - P-com.example.auth      # Package (P-)
  - C-com.example.auth.SessionManager    # Class (C-)
  - M-validate              # Method (M- instead of F- for clarity)
```

**Rust:**
```yaml
units:
  - K-auth                  # Crate (K-)
  - M-auth::session         # Module (M-)
  - F-authenticate          # Function (F-)
```

**JavaScript:**
```yaml
units:
  - M-auth/session          # ES6 module (M-)
  - C-SessionManager        # Class (C-)
  - F-authenticate          # Function (F-)
```

**Advantages of this approach:**
1. **Extensible:** Add new prefixes per language (P-, K-, etc.)
2. **Consistent:** All languages use prefix-based node IDs
3. **Unambiguous:** Prefix indicates type, path indicates location
4. **Direct:** References implementation graph nodes exactly

**Decision: Start with Python M-/C-/F-, extend per language as needed.**

---

## 4. @jig Decorators

**Format:** `@jig.implements`, `@jig.verifies`

**Why include "jig." prefix?**
- Clear which system owns the decorator
- Avoids confusion with other decorators
- Standard Python practice (namespace decorators)
- Example: `@dataclass` (no prefix) vs `@pytest.fixture` (prefixed)

### @jig.implements (on functions)

**Purpose:** Declare which specifications a function implements.

**Syntax:**
```python
@jig.implements("S-001")
def authenticate(user: str, password: str) -> Token:
    """Authenticate user and return session token."""
    ...

@jig.implements("S-001", "S-002")
def validate_and_refresh(token: Token) -> Token:
    """Validate token and refresh expiration."""
    ...
```

**Rules:**
- Spec IDs must exist in specification files
- Format: `S-{number}`
- Multiple specs: pass as separate arguments
- Functions without decorator: no specs implemented (internal helpers)

### @jig.verifies (on test functions)

**Purpose:** Declare which specifications or outcomes a test verifies.

**Syntax:**
```python
@jig.verifies("S-001")
def test_token_expiration():
    """Verify tokens expire after 15 minutes."""
    ...

@jig.verifies("S-001", "S-002")
def test_session_security():
    """Verify session creation and expiration."""
    ...

@jig.verifies("O-001")  # Outcome verification (integration test)
def test_full_auth_flow():
    """End-to-end authentication flow."""
    ...
```

**Rules:**
- IDs must exist in specification/outcome files
- Format: `S-{number}` or `O-{number}`
- Tests may verify specs, outcomes, or both
- Tests without decorator: no specs verified (internal/infrastructure tests)

### Removed Decorator: @jig.brick

**From AG023, proposed optional @jig.brick decorator.**

**WHY REMOVE:**
1. **Duplication:** Bricks defined in bricks.yaml. Decorator is redundant.
2. **Source of truth:** If brick partition is in bricks.yaml, decorators are override/exception. Exceptions complicate.
3. **Drift risk:** Decorator and bricks.yaml can become inconsistent.
4. **Unnecessary:** If brick assignment is wrong, fix bricks.yaml (one place to fix, not scattered decorators).

**Edge case:** "What if a function in utils.py belongs to B-001, not B-003?"

**Answer:** Define it explicitly in bricks.yaml:
```yaml
- id: B-001
  units:
    - F-utils.special_auth_helper  # Exception, but explicit in one place
```

**Better answer:** This indicates poor module organization. Refactor:
- Move `special_auth_helper` to `auth.utils`
- Or extract to `auth.helpers`

**Principle:** Fix organization, don't add decorators to paper over it.

---

## 5. Graph Files

**Location:** `jig/generated/`

**Why jig/generated/?**
- Clear separation: human-authored (jig/specifications, jig/outcomes, jig/bricks.yaml) vs machine-generated (jig/generated)
- Enables .gitignore of generated/ (if desired, though we recommend committing)
- Clearly marks derived artifacts

**File naming:** `intent-graph.ndjson` (noun-based, natural reading)

**Three files:**
```
jig/generated/intent-graph.ndjson
jig/generated/implementation-graph.ndjson
jig/generated/verification-graph.ndjson
```

### Why NDJSON? (from AG018)
- One node per line (clean git diffs)
- Only changed lines show in diffs
- Streamable (don't load entire file)
- Grep/sed friendly

### File 1: intent-graph.ndjson

**Generated from:**
- `jig/specifications/S-*.md` frontmatter
- `jig/outcomes/O-*.md` frontmatter (if present)
- `jig/bricks.yaml`

**Minimal schema (one JSON object per line):**

```json
{"id":"S-001","type":"specification","file":"jig/specifications/S-001.md"}
{"id":"S-002","type":"specification","file":"jig/specifications/S-002.md"}
{"id":"O-001","type":"outcome","file":"jig/outcomes/O-001.md","specifies":["S-001","S-002"]}
{"id":"B-001","type":"brick","name":"Authentication & Session Management","file":"jig/bricks.yaml"}
{"id":"B-003","type":"brick","name":"Core Utilities","file":"jig/bricks.yaml"}
```

**Specification Node:**
```json
{
  "id": "S-001",
  "type": "specification",
  "file": "jig/specifications/S-001.md"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Spec ID (from frontmatter) |
| `type` | string | `"specification"` |
| `file` | string | Relative path to markdown file |

**Outcome Node:**
```json
{
  "id": "O-001",
  "type": "outcome",
  "file": "jig/outcomes/O-001.md",
  "specifies": ["S-001", "S-002"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Outcome ID (from frontmatter) |
| `type` | string | `"outcome"` |
| `file` | string | Relative path to markdown file |
| `specifies` | array | Array of spec IDs (from frontmatter) |

**Brick Node:**
```json
{
  "id": "B-001",
  "type": "brick",
  "name": "Authentication & Session Management",
  "file": "jig/bricks.yaml"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Brick ID (from YAML) |
| `type` | string | `"brick"` |
| `name` | string | Human-readable name (from YAML) |
| `file` | string | Always "jig/bricks.yaml" (single file) |

**Removed Fields (from AG023):**

| Field | Why Removed |
|-------|-------------|
| `content` | Brittle (extracting first heading). Content stays in markdown files. |
| `brick` (on specs) | Circular dependency. Derived from F→S edges. |
| `depends_on` (on specs) | Not part of core triangle. Document in markdown if needed. |
| `depends_on` (on bricks) | Derived from implementation graph (F→F calls). |

### File 2: implementation-graph.ndjson

**Generated from:**
- Python source files (AST parsing)
- `@jig.implements` decorators

**Minimal schema:**

```json
{"id":"F-auth.session.authenticate","type":"function","file":"src/auth/session.py","implements":["S-001","S-002"],"calls":["F-auth.tokens.validate"]}
{"id":"F-auth.tokens.validate","type":"function","file":"src/auth/tokens.py","implements":["S-001"],"calls":[]}
{"id":"F-utils.io.read_file","type":"function","file":"src/utils/io.py","implements":[],"calls":[]}
```

**Function Node:**
```json
{
  "id": "F-auth.session.authenticate",
  "type": "function",
  "file": "src/auth/session.py",
  "implements": ["S-001", "S-002"],
  "calls": ["F-auth.tokens.validate"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Function ID. Format: `F-{module.path}.{function_name}` or `F-{module.path}.{Class}.{method}` |
| `type` | string | `"function"` (includes methods) |
| `file` | string | Relative path to Python file |
| `implements` | array | Array of spec IDs (from `@jig.implements`). Empty `[]` if none. |
| `calls` | array | Array of function IDs this calls (from AST). Empty `[]` if none. |

**Removed Fields (from AG023):**

| Field | Why Removed |
|-------|-------------|
| `brick` | **Circular dependency.** Implementation graph is generated BEFORE brick definitions. Brick assignment happens at query time by loading bricks.yaml and mapping F→brick. |

**Critical insight: Breaking the circular dependency**

**AG023 had:**
1. Generate implementation-graph (includes brick assignment)
2. Use implementation-graph to define bricks

**This is circular!** Can't generate graph with brick assignments before bricks are defined.

**AG024 (refined):**
1. Generate implementation-graph (NO brick assignments, just F nodes and F→F edges)
2. Define bricks in bricks.yaml (partition of F nodes)
3. At query time: load both graphs + bricks.yaml, compute brick assignment

**Example:**
```python
def get_brick_for_function(func_id, bricks):
    for brick in bricks:
        if func_id in expand_brick_to_functions(brick):
            return brick["id"]
    return None  # Unassigned (validation error)
```

**Brick assignment is a mapping, not a graph property.**

### File 3: verification-graph.ndjson

**Generated from:**
- Test discovery (pytest, unittest)
- Coverage analysis (pytest-cov, coverage.py)
- `@jig.verifies` decorators

**Minimal schema:**

```json
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"covers":["F-auth.session.authenticate","F-auth.tokens.validate"]}
{"id":"T-test_auth.test_rate_limiting","type":"test","file":"tests/unit/test_auth.py","verifies":["S-002"],"covers":["F-auth.session.authenticate"]}
```

**Test Node:**
```json
{
  "id": "T-test_auth.test_token_expiration",
  "type": "test",
  "file": "tests/unit/test_auth.py",
  "verifies": ["S-001"],
  "covers": ["F-auth.session.authenticate", "F-auth.tokens.validate"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Test ID. Format: `T-{module}.{test_function}` or `T-{module}.{TestClass}.{test_method}` |
| `type` | string | `"test"` |
| `file` | string | Relative path to test file |
| `verifies` | array | Array of spec/outcome IDs (from `@jig.verifies`). Empty `[]` if none. |
| `covers` | array | Array of function IDs executed by this test (from coverage). Empty `[]` if none. |

**Removed Fields (from AG023):**

| Field | Why Removed |
|-------|-------------|
| `brick` | **Not circular, but unnecessary.** Test brick can be derived from covered functions (T covers F, F belongs to brick). Generate verification graph before brick definitions for consistency. |

**Brick assignment for tests (derived at query time):**
```python
def get_brick_for_test(test, functions, bricks):
    # Test belongs to brick of functions it primarily covers
    covered_bricks = [get_brick_for_function(f, bricks)
                      for f in test["covers"]]

    if not covered_bricks:
        return None  # Test covers nothing (broken)

    # Primary brick = most functions covered
    from collections import Counter
    brick_counts = Counter(covered_bricks)
    primary = brick_counts.most_common(1)[0][0]

    # If test covers multiple bricks significantly, it's integration
    if len(brick_counts) > 1 and brick_counts.most_common(2)[1][1] > 2:
        return None  # Integration test (no single brick)

    return primary
```

---

## File Structure (Complete)

```
project-root/
├── jig/
│   ├── specifications/
│   │   ├── S-001.md            # Human-authored
│   │   ├── S-002.md
│   │   └── S-003.md
│   ├── outcomes/               # OPTIONAL, human-authored
│   │   ├── O-001.md
│   │   └── O-002.md
│   ├── bricks.yaml             # Human-authored, single file
│   └── generated/              # Machine-generated
│       ├── intent-graph.ndjson
│       ├── implementation-graph.ndjson
│       └── verification-graph.ndjson
├── src/
│   ├── auth/
│   │   ├── session.py          # @jig.implements decorators
│   │   └── tokens.py
│   └── utils/
│       └── io.py
└── tests/
    ├── unit/
    │   └── test_auth.py        # @jig.verifies decorators
    └── integration/
        └── test_flows.py
```

---

## Required vs Optional vs Excluded

### REQUIRED (system breaks without these)

**Human-authored:**
1. ✓ Specification files (`jig/specifications/S-*.md`) with minimal frontmatter (`id`, `type`)
2. ✓ Brick definition file (`jig/bricks.yaml`) with minimal fields (`id`, `name`, `units`)
3. ✓ `@jig.implements` decorators on functions that implement specs
4. ✓ `@jig.verifies` decorators on tests that verify specs

**Machine-generated:**
5. ✓ `jig/generated/intent-graph.ndjson`
6. ✓ `jig/generated/implementation-graph.ndjson`
7. ✓ `jig/generated/verification-graph.ndjson`

### OPTIONAL

1. ○ Outcome files (`jig/outcomes/O-*.md`)
2. ○ Markdown body in spec/outcome files (documentation)
3. ○ `@jig.implements` (functions without decorator are internal helpers)
4. ○ `@jig.verifies` (tests without decorator are infrastructure tests)

### EXCLUDED (deliberately not supported)

1. ✗ Domain prefixes in IDs (S-AUTH-001 → S-001)
2. ✗ `brick` field in spec/outcome frontmatter (circular dependency)
3. ✗ `depends_on` field in spec frontmatter (not part of core triangle)
4. ✗ `depends_on` field in brick definitions (derived from implementation graph)
5. ✗ `public_api` field in brick definitions (derived from call graph)
6. ✗ `content` field in graph nodes (stays in markdown)
7. ✗ `brick` field in implementation/verification graph nodes (derived at query time)
8. ✗ Line numbers in graph files (brittle)
9. ✗ Metrics/aggregations in graph files (computed on demand)
10. ✗ Timestamps in graph files (use git)
11. ✗ `@jig.brick` decorator (bricks.yaml is source of truth)
12. ✗ Multiple brick definition files (one bricks.yaml for all bricks)

---

## Validation Rules

### Validation 1: All IDs are unique within type

```python
def validate_unique_ids(specs, outcomes, bricks):
    spec_ids = [s["id"] for s in specs]
    outcome_ids = [o["id"] for o in outcomes]
    brick_ids = [b["id"] for b in bricks]

    if len(spec_ids) != len(set(spec_ids)):
        raise ValueError("Duplicate spec IDs")
    if len(outcome_ids) != len(set(outcome_ids)):
        raise ValueError("Duplicate outcome IDs")
    if len(brick_ids) != len(set(brick_ids)):
        raise ValueError("Duplicate brick IDs")
```

### Validation 2: All @jig.implements references exist

```python
def validate_implements(functions, specs):
    spec_ids = {s["id"] for s in specs}
    for func in functions:
        for spec_id in func["implements"]:
            if spec_id not in spec_ids:
                raise ValueError(f"{func['id']} implements non-existent {spec_id}")
```

### Validation 3: All @jig.verifies references exist

```python
def validate_verifies(tests, specs, outcomes):
    valid_ids = {s["id"] for s in specs} | {o["id"] for o in outcomes}
    for test in tests:
        for id in test["verifies"]:
            if id not in valid_ids:
                raise ValueError(f"{test['id']} verifies non-existent {id}")
```

### Validation 4: Brick partition is complete and non-overlapping

```python
def validate_partition(bricks, functions):
    brick_assignments = {}

    for brick in bricks:
        for func_id in expand_brick_to_functions(brick):
            if func_id in brick_assignments:
                raise ValueError(f"{func_id} assigned to both {brick_assignments[func_id]} and {brick['id']}")
            brick_assignments[func_id] = brick["id"]

    # All functions must be assigned
    unassigned = set(f["id"] for f in functions) - set(brick_assignments.keys())
    if unassigned:
        raise ValueError(f"{len(unassigned)} functions not assigned to any brick: {unassigned}")
```

### Validation 5: No class splitting

```python
def validate_no_class_split(classes, bricks):
    for class_id, method_ids in classes.items():
        method_bricks = {get_brick_for_function(m, bricks) for m in method_ids}
        if len(method_bricks) > 1:
            raise ValueError(f"Class {class_id} split across bricks {method_bricks}")
```

### Validation 6: Outcome specifies references exist

```python
def validate_outcome_specifies(outcomes, specs):
    spec_ids = {s["id"] for s in specs}
    for outcome in outcomes:
        for spec_id in outcome.get("specifies", []):
            if spec_id not in spec_ids:
                raise ValueError(f"{outcome['id']} specifies non-existent {spec_id}")
```

### Validation 7: Brick units have valid prefixes

```python
def validate_brick_units(bricks):
    valid_prefixes = {"M-", "C-", "F-"}  # Extend with P-, K- for other languages

    for brick in bricks:
        for unit_id in brick["units"]:
            prefix = unit_id[:2] if len(unit_id) >= 2 else ""
            if prefix not in valid_prefixes:
                raise ValueError(f"{brick['id']} has invalid unit '{unit_id}' (must start with M-/C-/F-)")
```

### Validation 8: All brick units exist in implementation graph

```python
def validate_brick_units_exist(bricks, implementation_graph):
    # For M- and C- units, check expansion will find functions
    # For F- units, check function exists directly

    for brick in bricks:
        for unit_id in brick["units"]:
            if unit_id.startswith("F-"):
                # Function must exist
                if unit_id not in implementation_graph["functions"]:
                    raise ValueError(f"{brick['id']} references non-existent function {unit_id}")

            elif unit_id.startswith("M-") or unit_id.startswith("C-"):
                # Module/class must have at least one function
                expanded = expand_brick_to_functions({"units": [unit_id]}, implementation_graph)
                if not expanded:
                    raise ValueError(f"{brick['id']} unit {unit_id} expands to zero functions")
```

---

## Complete Example (Minimal)

### Human writes specification

**File:** `jig/specifications/S-001.md`

```markdown
---
id: S-001
type: specification
---

# Token Expiration

Authentication tokens MUST expire after 15 minutes of inactivity.
```

---

### Human defines bricks

**File:** `jig/bricks.yaml`

```yaml
bricks:
  - id: B-001
    name: Authentication & Session Management
    units:
      - M-auth.session
      - M-auth.tokens

  - id: B-003
    name: Core Utilities
    units:
      - M-utils.io
```

---

### Human implements function

**File:** `src/auth/session.py`

```python
from datetime import datetime, timedelta

@jig.implements("S-001")
def authenticate(user: str, password: str) -> Token:
    """Authenticate user and return session token."""
    token = Token(
        user=user,
        expires_at=datetime.now() + timedelta(minutes=15)
    )
    return token
```

---

### Human writes test

**File:** `tests/unit/test_auth.py`

```python
@jig.verifies("S-001")
def test_token_expiration():
    """Verify tokens expire after 15 minutes."""
    token = authenticate("user", "pass")
    token.last_activity = datetime.now() - timedelta(minutes=15, seconds=1)
    assert is_expired(token)
```

---

### Machine generates graphs

**Command:**
```bash
jigy index         # Generate intent-graph.ndjson
jigy impl rebuild  # Generate implementation-graph.ndjson
jigy verify rebuild --run-tests  # Generate verification-graph.ndjson
```

**Generated: `jig/generated/intent-graph.ndjson`**
```json
{"id":"S-001","type":"specification","file":"jig/specifications/S-001.md"}
{"id":"B-001","type":"brick","name":"Authentication & Session Management","file":"jig/bricks.yaml"}
{"id":"B-003","type":"brick","name":"Core Utilities","file":"jig/bricks.yaml"}
```

**Generated: `jig/generated/implementation-graph.ndjson`**
```json
{"id":"F-auth.session.authenticate","type":"function","file":"src/auth/session.py","implements":["S-001"],"calls":[]}
```

**Generated: `jig/generated/verification-graph.ndjson`**
```json
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"covers":["F-auth.session.authenticate"]}
```

---

### Query alignment (with brick assignment)

**Command:**
```bash
jigy status
```

**Process:**
1. Load `jig/generated/intent-graph.ndjson` (S-001, B-001, B-003)
2. Load `jig/generated/implementation-graph.ndjson` (F-auth.session.authenticate)
3. Load `jig/generated/verification-graph.ndjson` (T-test_auth.test_token_expiration)
4. Load `jig/bricks.yaml` (brick definitions)
5. Compute brick assignment for each F, T node
6. Compute alignment

**Output:**
```
Loading graphs...
  intent-graph.ndjson (3 nodes)
  implementation-graph.ndjson (1 node)
  verification-graph.ndjson (1 node)
  bricks.yaml (2 bricks)

Computing brick assignments...
  F-auth.session.authenticate → B-001 (via module: auth.session)
  T-test_auth.test_token_expiration → B-001 (covers F-auth.session.authenticate)

Computing alignment...

S-001: Token Expiration
  ✓ Implemented by: F-auth.session.authenticate (B-001)
  ✓ Verified by: T-test_auth.test_token_expiration (B-001)
  ✓ Test covers implementation

  Alignment: PERFECT

Overall: 100% (1/1 specs perfectly aligned)
```

---

## Breaking the Circular Dependency (Detailed)

### The Problem (AG023)

**Workflow:**
1. Parse code → generate implementation-graph with brick assignments
2. Define bricks based on implementation-graph

**But brick assignment requires brick definitions!**

**Circular:**
- Implementation-graph needs bricks.yaml (to assign F→brick)
- bricks.yaml needs implementation-graph (to know which F exist)

### The Solution (AG024)

**Workflow:**
1. Parse code → generate implementation-graph (NO brick assignments, just F nodes)
2. Human defines bricks in bricks.yaml (partition of F nodes)
3. Tools load both, compute brick assignment at query time

**No circular dependency:**
- Implementation-graph is independent (just code structure)
- bricks.yaml partitions F nodes (references F-* IDs from graph)
- Brick assignment is computed by joining graph + bricks.yaml

**Example:**

**Step 1: Generate implementation-graph (no bricks)**
```json
{"id":"F-auth.session.authenticate","type":"function","file":"src/auth/session.py","implements":["S-001"],"calls":[]}
{"id":"F-auth.tokens.validate","type":"function","file":"src/auth/tokens.py","implements":["S-001"],"calls":[]}
{"id":"F-utils.io.read_file","type":"function","file":"src/utils/io.py","implements":[],"calls":[]}
```

**Step 2: Human defines bricks (references implementation graph node IDs)**
```yaml
bricks:
  - id: B-001
    name: Authentication
    units:
      - M-auth.session  # Expands to all F-auth.session.*
      - M-auth.tokens   # Expands to all F-auth.tokens.*

  - id: B-003
    name: Utilities
    units:
      - M-utils.io      # Expands to all F-utils.io.*
```

**Step 3: Tool computes brick assignment**
```python
def expand_brick_to_functions(brick, implementation_graph):
    """Expand brick units (M-/C-/F- prefixes) to F-* IDs."""
    funcs = set()

    for unit_id in brick["units"]:
        if unit_id.startswith("M-"):
            # Module: all functions in this module
            module_path = unit_id[2:]  # Strip "M-" prefix
            for func_id in implementation_graph["functions"]:
                if func_id.startswith(f"F-{module_path}."):
                    funcs.add(func_id)

        elif unit_id.startswith("C-"):
            # Class: all methods of this class
            class_path = unit_id[2:]  # Strip "C-" prefix
            for func_id in implementation_graph["functions"]:
                if func_id.startswith(f"F-{class_path}."):
                    funcs.add(func_id)

        elif unit_id.startswith("F-"):
            # Function: exactly this function
            if unit_id in implementation_graph["functions"]:
                funcs.add(unit_id)

    return funcs

# Compute brick assignment
brick_assignments = {}
for brick in bricks:
    for func_id in expand_brick_to_functions(brick, impl_graph):
        brick_assignments[func_id] = brick["id"]

# Result:
# F-auth.session.authenticate → B-001
# F-auth.tokens.validate → B-001
# F-utils.io.read_file → B-003
```

**No circular dependency. Implementation-graph is generated first, bricks.yaml references it.**

---

## Why These Simplifications Matter

### 1. Eliminates Circular Dependencies

**Before (AG023):**
- Specs have `brick` field → Brick assignment in spec frontmatter
- Implementation-graph has `brick` field → Brick assignment in graph
- But bricks are defined based on implementation-graph structure
- **Circular!**

**After (AG024):**
- Specs don't know about bricks (independent)
- Implementation-graph doesn't include bricks (independent)
- Bricks defined separately (partition of F nodes)
- Brick assignment computed at query time (join operation)
- **No circular dependency!**

### 2. Single Source of Truth

**Before (AG023):**
- Brick assignment in spec frontmatter
- Brick assignment in implementation-graph
- Brick assignment via `@jig.brick` decorator
- **Three places to maintain!**

**After (AG024):**
- Brick assignment in bricks.yaml only
- **One place to maintain!**

### 3. Simpler IDs

**Before (AG023):**
- `S-AUTH-001` (domain prefix undefined)
- `BRICK-AUTH` (verbose)

**After (AG024):**
- `S-001` (simple, sufficient)
- `B-001` (short, parallel to S-)

### 4. Minimal Required Fields

**Before (AG023) - Spec frontmatter:**
```yaml
id: S-AUTH-001
type: specification
brick: BRICK-AUTH
depends_on: [S-AUTH-000]
```

**After (AG024) - Spec frontmatter:**
```yaml
id: S-001
type: specification
```

**67% reduction in required fields!**

### 5. Derived Data is Computed, Not Stored

**Before (AG023):**
- Brick dependencies stored in bricks.yaml
- Public API stored in bricks.yaml
- Brick assignment stored in graphs

**After (AG024):**
- Brick dependencies computed from implementation-graph
- Public API computed from call graph
- Brick assignment computed from bricks.yaml + graphs

**Principle:** Don't store what can be computed.

---

## Migration Path (Updated)

For existing projects adopting jig:

### Phase 1: Document Intent
1. Create `jig/specifications/` directory
2. Write specs (one per file: `S-001.md`, `S-002.md`, etc.)
3. Minimal frontmatter (`id`, `type` only)

### Phase 2: Generate Implementation Graph
1. Run `jigy impl scan` (generates implementation-graph without brick assignments)
2. Review function nodes (all F-* IDs discovered)

### Phase 3: Define Bricks
1. Create `jig/bricks.yaml`
2. Run `jigy discover bricks` (suggests partitions based on call graph clustering)
3. Refine brick definitions manually
4. Validate partition (every function assigned to one brick)

### Phase 4: Annotate Code
1. Add `@jig.implements` decorators to functions
2. Regenerate implementation-graph
3. Validate (all spec IDs exist)

### Phase 5: Annotate Tests
1. Add `@jig.verifies` decorators to tests
2. Run tests with coverage
3. Generate verification-graph
4. Validate (all spec/outcome IDs exist)

### Phase 6: Measure Alignment
1. Run `jigy status` (computes brick assignments, displays alignment)
2. Identify gaps (unimplemented specs, unverified specs, untested code)
3. Iterate

---

## Conclusion

**AG024 simplifies AG023 through six key insights:**

1. **Break circular dependencies:** Graphs generated before brick assignment
2. **Single source of truth:** bricks.yaml defines partition, nothing else
3. **Minimal IDs:** S-001 not S-AUTH-001, B-001 not B-AUTH (consistent numbering)
4. **Minimal required fields:** Only what cannot be computed
5. **Derived data computed:** Dependencies, public APIs, brick assignments
6. **Direct graph references:** Bricks use M-/C-/F- prefixes to reference implementation graph nodes unambiguously

**The core remains (from AG019):**
- S (specs) - intent
- F (functions) - implementation
- T (tests) - verification

**Everything else is derived or organizational.**

**Five artifacts:**
1. Specification files (`jig/specifications/S-*.md`) - minimal frontmatter
2. Outcome files (`jig/outcomes/O-*.md`) - optional
3. Brick definitions (`jig/bricks.yaml`) - single file, `units` array with M-/C-/F- prefixes
4. @jig decorators (`@jig.implements`, `@jig.verifies`) - no @jig.brick
5. Graph files (`jig/generated/*.ndjson`) - no brick field

**This is the simplest definition that could possibly work.**

---

## Changes from AG023

| Aspect | AG023 | AG024 (Refined) | Rationale |
|--------|-------|-----------------|-----------|
| Spec IDs | `S-AUTH-001` | `S-001` | Domain is undefined concept |
| Brick IDs | `BRICK-AUTH` | `B-001` | Sequential numbering, consistent with S-001/O-001 pattern |
| Spec frontmatter | 4 fields (`id`, `type`, `brick`, `depends_on`) | 2 fields (`id`, `type`) | Eliminate circular dependency |
| Outcome frontmatter | 4 fields | 3 fields (no `brick`) | Eliminate circular dependency |
| Brick file | Multiple `.brick.yaml` files | Single `bricks.yaml` | See full partition in one place |
| Brick partition | `modules`, `classes`, `functions` arrays | Single `units` array with M-/C-/F- prefixes | Direct reference to implementation graph nodes |
| Brick fields | `depends_on`, `public_api` | Neither (both derived) | Don't store what can compute |
| @jig decorators | `@implements`, `@verifies`, `@brick` | `@jig.implements`, `@jig.verifies` (no `@brick`) | Single source of truth (bricks.yaml) |
| Implementation graph | Includes `brick` field | No `brick` field | Break circular dependency |
| Verification graph | Includes `brick` field | No `brick` field | Consistency, generate before bricks |
| Graph location | `jig/` | `jig/generated/` | Separate human vs machine |
| Graph content field | Extracted from markdown | Excluded | Brittle, content stays in markdown |

---

## References

- **AG017:** Minimal Graph Schema
- **AG018:** Graph Storage Strategy (NDJSON choice)
- **AG019:** Irreducible Core (S-F-T triangle)
- **AG020:** Bricks as Partitions
- **AG023:** Core Artifacts Contract (first draft, this document refines)
