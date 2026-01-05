---
title: "Core Artifacts Contract"
type: exploration
status: superseded
created: 1764187522
created_human: "2025-11-26 14:05 CST"
parent: "[[AG001_Alignment-Graph-Bricks]]"
children: ['[[AG024_REFINED_Core-Artifacts-Contract]]']
superseded_by: "[[AG024_REFINED_Core-Artifacts-Contract]]"
---
# Core Artifacts Contract

_Locking Down the Foundation_

**Date:** 2025-11-26
**Status:** Proposal
**Related:** AG017 (Minimal Graph Schema), AG018 (Storage Strategy), AG019 (Irreducible Core), AG020 (Bricks as Partitions)

---

## Purpose

This document defines the **contract** for all core artifacts in the jig system. These are the baseline artifacts that:
- **MUST exist** for the system to function
- **MUST have specific structure** to enable automation
- **CANNOT be changed** without breaking the system

Missing elements will break the system. Extra elements create noise. This is the foundation.

---

## The Five Core Artifacts

1. **Specification files** (`.md` with YAML frontmatter)
2. **Outcome files** (`.md` with YAML frontmatter) - OPTIONAL
3. **Brick definition files** (`.brick.yaml`)
4. **@jig decorators** (in Python source)
5. **Graph files** (`.ndjson`, machine-generated)

**Principle:** Human-authored artifacts are the source of truth. Graph files are derived.

---

## 1. Specification Files

**Location:** `jig/specifications/*.md`

**Naming convention:** `{domain}.md` or `{brick-name}.md`
- Examples: `auth.md`, `cli.md`, `graph-storage.md`
- Multiple specs may live in one file (grouped by domain)

### Required YAML Frontmatter

```yaml
---
id: S-AUTH-001
type: specification
brick: BRICK-AUTH
depends_on: []
---
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique identifier. Format: `S-{DOMAIN}-{NNN}` where DOMAIN is uppercase (e.g., `S-AUTH-001`) |
| `type` | string | ✓ | Must be exactly `"specification"` |
| `brick` | string | ✓ | Brick ID this spec belongs to (format: `BRICK-{NAME}`) |
| `depends_on` | array | ✓ | Array of Spec IDs this depends on. Empty array `[]` if none. |

### Markdown Body

**Not parsed by tools.** For human reading only.

**Purpose:** Explain the specification in detail. Include:
- What the specification requires
- Acceptance criteria
- Examples, edge cases, constraints
- Rationale (why this spec exists)

**Example:**

```markdown
---
id: S-AUTH-001
type: specification
brick: BRICK-AUTH
depends_on: []
---

# Token Expiration

Authentication tokens MUST expire after 15 minutes of inactivity.

**Acceptance Criteria:**
- Token created with `expires_at = now() + 15 minutes`
- Any operation updates `last_activity` timestamp
- Token rejected if `now() > last_activity + 15 minutes`

**Rationale:** Limits exposure window if token is compromised.
```

### Why This Structure?

**`id` format `S-{DOMAIN}-{NNN}`:**
- Globally unique across all specs
- Human-readable (not UUIDs)
- Sortable (numbers allow ordering)
- Domain prefix groups related specs

**`type: specification`:**
- Enables tools to distinguish specs from outcomes in same directory
- Future-proof (could add other types to same directory)

**`brick` assignment:**
- Explicit ownership (which brick owns this requirement)
- Enables "show all specs for BRICK-AUTH"
- Validates against actual brick definitions

**`depends_on` array:**
- Makes spec dependencies explicit (S-002 requires S-001 to be implemented first)
- Enables topological sort (implementation order)
- Empty array `[]` required (explicit "no dependencies")

**Markdown body not parsed:**
- Tools only read frontmatter (fast, predictable)
- Body is for humans, not machines
- Flexibility in documentation format

---

## 2. Outcome Files (OPTIONAL)

**Location:** `jig/outcomes/*.md`

**Naming convention:** `{domain}.md` (same as specs)

**Status:** Optional scaffolding. Not required for core alignment.

### Required YAML Frontmatter (if present)

```yaml
---
id: O-AUTH-001
type: outcome
brick: BRICK-AUTH
specifies: [S-AUTH-001, S-AUTH-002]
---
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique identifier. Format: `O-{DOMAIN}-{NNN}` |
| `type` | string | ✓ | Must be exactly `"outcome"` |
| `brick` | string | ✓ | Brick ID this outcome belongs to |
| `specifies` | array | ✓ | Array of Spec IDs this outcome decomposes into. May be empty `[]`. |

### Why Optional?

From AG019 (Irreducible Core):
> Removing O doesn't break alignment measurement. O provides human context, not machine-checkable relationships.

**Outcomes explain WHY specs exist. They are documentation, not requirements.**

**Keep if:**
- You need to explain design decisions
- You're working with non-technical stakeholders
- You want to group related specs conceptually

**Omit if:**
- Specs are self-explanatory
- Prototyping/exploring
- Additional documentation feels like overhead

---

## 3. Brick Definition Files

**Location:** `bricks/*.brick.yaml`

**Naming convention:** `{brick-name}.brick.yaml`
- Examples: `auth.brick.yaml`, `cli.brick.yaml`, `utils.brick.yaml`
- One brick per file

### Required Structure

```yaml
id: BRICK-AUTH
name: Authentication & Session Management
depends_on: [BRICK-UTILS]
modules: []
classes: []
functions: []
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique identifier. Format: `BRICK-{NAME}` (uppercase) |
| `name` | string | ✓ | Human-readable name |
| `depends_on` | array | ✓ | Array of Brick IDs this brick may call. Empty `[]` if none. |
| `modules` | array | ✓ | Python module paths (e.g., `auth.session`). Empty `[]` if using classes/functions. |
| `classes` | array | ✓ | Fully-qualified class names (e.g., `auth.tokens.TokenValidator`). Empty `[]` if not used. |
| `functions` | array | ✓ | Fully-qualified function names (e.g., `auth.session.authenticate`). Empty `[]` if not used. |

### Partition Definition (M, C, F)

**A brick is defined by listing modules, classes, or functions** (from AG020).

**Choose ONE primary approach per brick:**

**Option A: Module-level (coarse, simple)**
```yaml
modules:
  - auth.session
  - auth.tokens
classes: []
functions: []
```
→ All functions in `auth.session.*` and `auth.tokens.*` belong to BRICK-AUTH.

**Option B: Class-level (medium granularity)**
```yaml
modules: []
classes:
  - auth.session.SessionManager
  - auth.tokens.TokenValidator
functions: []
```
→ All methods of these classes belong to BRICK-AUTH.

**Option C: Function-level (fine control)**
```yaml
modules: []
classes: []
functions:
  - auth.session.authenticate
  - auth.session.logout
  - auth.tokens.validate
```
→ Exactly these functions belong to BRICK-AUTH.

**Option D: Mixed (practical)**
```yaml
modules:
  - auth.session  # Entire module
classes:
  - auth.tokens.TokenValidator  # Just this class from auth.tokens
functions:
  - auth.utils.hash_password  # Just this function from utils
```

### Constraints

**1. Partition constraint:**
Every function MUST belong to exactly one brick (no overlaps, no gaps).

**2. No class splitting:**
All methods of a class MUST be in the same brick. Never split a class across bricks.

**3. Dependency direction (optional):**
Brick dependency graph SHOULD be acyclic (no circular dependencies). Violations indicate design problems.

### Why This Structure?

**`depends_on` explicit:**
- Documents architectural dependencies (which bricks may call which)
- Enables boundary violation detection (F in BRICK-A calls F in BRICK-B, but BRICK-A does not depend on BRICK-B)
- Forces architectural thinking

**Module/class/function partition:**
- Flexible granularity (choose what fits your codebase)
- All expand to function-level partition for core S-F-T triangle
- Module-level is simplest (matches directory structure)

**No public_api field:**
- Public API is **derived** (functions called from outside the brick)
- Don't manually maintain what can be computed

---

## 4. @jig Decorators

**Location:** Python source files (`src/**/*.py`, `tests/**/*.py`)

### @implements Decorator (on functions)

**Purpose:** Declare which specifications a function implements.

**Syntax:**
```python
from jig import implements

@implements("S-AUTH-001")
def authenticate(user: str, password: str) -> Token:
    """Authenticate user and return session token."""
    ...

@implements("S-AUTH-001", "S-AUTH-002")
def validate_and_refresh(token: Token) -> Token:
    """Validate token and refresh expiration."""
    ...
```

**Multiple specs:** Pass multiple spec IDs as separate arguments.

**Required:**
- Spec IDs must exist in specification files
- Format: `S-{DOMAIN}-{NNN}`

**Excluded:**
- ❌ No outcome IDs (decorators point to specs, never outcomes)
- ❌ No file paths (use spec IDs, not filenames)
- ❌ No metadata (just spec IDs)

### @verifies Decorator (on test functions)

**Purpose:** Declare which specifications or outcomes a test verifies.

**Syntax:**
```python
from jig import verifies

@verifies("S-AUTH-001")
def test_token_expiration():
    """Verify tokens expire after 15 minutes."""
    token = authenticate("user", "pass")
    time.sleep(901)  # 15 min + 1 sec
    assert is_expired(token)

@verifies("S-AUTH-001", "S-AUTH-002")
def test_session_security():
    """Verify session creation and expiration."""
    ...

@verifies("O-AUTH-001")  # Outcome verification (integration test)
def test_full_auth_flow():
    """End-to-end authentication flow."""
    ...
```

**Spec IDs or Outcome IDs:** Tests may verify either (or both).

**Required:**
- IDs must exist in specification/outcome files
- Format: `S-{DOMAIN}-{NNN}` or `O-{DOMAIN}-{NNN}`

### @brick Decorator (OPTIONAL)

**Purpose:** Explicitly assign function/test to a brick (overrides module-based assignment).

**Syntax:**
```python
from jig import brick, implements

@brick("BRICK-AUTH")
@implements("S-AUTH-001")
def authenticate(user: str, password: str) -> Token:
    ...
```

**When to use:**
- Module-based brick assignment is ambiguous
- Shared utility modules (assign different functions to different bricks)

**Default behavior (no @brick):**
Function assigned to brick based on brick definition file (which module/class it's in).

### Why Decorators?

**@implements makes intent explicit:**
- Developer declares "this function satisfies this spec"
- No guessing from comments or docstrings
- Parseable, enforceable, queryable

**@verifies connects tests to requirements:**
- Test declares "I verify this spec"
- Coverage analysis alone doesn't show intent (test might execute code accidentally)
- Enables "which tests verify S-AUTH-001?"

**Decorators are lightweight:**
- One line per function/test
- No separate mapping file to maintain
- Lives with the code (git tracks together)

**Why decorators point to specs, not outcomes?**
- Outcomes are high-level (too abstract to implement/verify directly)
- Specs are concrete requirements (implementable, testable)
- Outcomes group specs conceptually, but code implements specs

---

## 5. Graph Files (Machine-Generated)

**Location:** `jig/`

**Three files:**
```
jig/intent-graph.ndjson
jig/implementation-graph.ndjson
jig/verification-graph.ndjson
```

**Format:** NDJSON (Newline-Delimited JSON)

**Why NDJSON?** (from AG018)
- One node per line (clean git diffs)
- Only changed nodes show in diffs
- Can grep/sed individual nodes
- Streaming processing (don't load entire file)

### File 1: intent-graph.ndjson

**Generated from:**
- `jig/specifications/*.md` frontmatter
- `jig/outcomes/*.md` frontmatter (if present)
- `bricks/*.brick.yaml`

**Schema (one JSON object per line):**

```json
{"id":"S-AUTH-001","type":"specification","content":"Token Expiration","file":"jig/specifications/auth.md","brick":"BRICK-AUTH","depends_on":[]}
{"id":"S-AUTH-002","type":"specification","content":"Rate Limiting","file":"jig/specifications/auth.md","brick":"BRICK-AUTH","depends_on":["S-AUTH-001"]}
{"id":"O-AUTH-001","type":"outcome","content":"Secure Authentication","file":"jig/outcomes/auth.md","brick":"BRICK-AUTH","specifies":["S-AUTH-001","S-AUTH-002"]}
{"id":"BRICK-AUTH","type":"brick","name":"Authentication & Session Management","file":"bricks/auth.brick.yaml","depends_on":["BRICK-UTILS"]}
```

**Node Types:**

**Specification Node:**
```json
{
  "id": "S-AUTH-001",
  "type": "specification",
  "content": "Token Expiration",
  "file": "jig/specifications/auth.md",
  "brick": "BRICK-AUTH",
  "depends_on": []
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Spec ID (from frontmatter) |
| `type` | string | ✓ | `"specification"` |
| `content` | string | ✓ | First heading from markdown body (e.g., `# Token Expiration` → `"Token Expiration"`) |
| `file` | string | ✓ | Relative path to markdown file |
| `brick` | string | ✓ | Brick ID (from frontmatter) |
| `depends_on` | array | ✓ | Array of spec IDs (from frontmatter) |

**Outcome Node (optional):**
```json
{
  "id": "O-AUTH-001",
  "type": "outcome",
  "content": "Secure Authentication",
  "file": "jig/outcomes/auth.md",
  "brick": "BRICK-AUTH",
  "specifies": ["S-AUTH-001", "S-AUTH-002"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Outcome ID (from frontmatter) |
| `type` | string | ✓ | `"outcome"` |
| `content` | string | ✓ | First heading from markdown body |
| `file` | string | ✓ | Relative path to markdown file |
| `brick` | string | ✓ | Brick ID (from frontmatter) |
| `specifies` | array | ✓ | Array of spec IDs (from frontmatter) |

**Brick Node:**
```json
{
  "id": "BRICK-AUTH",
  "type": "brick",
  "name": "Authentication & Session Management",
  "file": "bricks/auth.brick.yaml",
  "depends_on": ["BRICK-UTILS"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Brick ID (from YAML) |
| `type` | string | ✓ | `"brick"` |
| `name` | string | ✓ | Human-readable name (from YAML) |
| `file` | string | ✓ | Path to brick definition file |
| `depends_on` | array | ✓ | Array of brick IDs (from YAML) |

### File 2: implementation-graph.ndjson

**Generated from:**
- Python source files (AST parsing)
- `@implements` decorators
- `@brick` decorators (optional)
- Brick definition files (for assignment)

**Schema (one JSON object per line):**

```json
{"id":"F-auth.session.authenticate","type":"function","file":"src/auth/session.py","brick":"BRICK-AUTH","implements":["S-AUTH-001","S-AUTH-002"],"calls":["F-auth.tokens.validate"]}
{"id":"F-auth.tokens.validate","type":"function","file":"src/auth/tokens.py","brick":"BRICK-AUTH","implements":["S-AUTH-001"],"calls":[]}
```

**Function Node:**
```json
{
  "id": "F-auth.session.authenticate",
  "type": "function",
  "file": "src/auth/session.py",
  "brick": "BRICK-AUTH",
  "implements": ["S-AUTH-001", "S-AUTH-002"],
  "calls": ["F-auth.tokens.validate"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Function ID. Format: `F-{module.path}.{function_name}` or `F-{module.path}.{Class}.{method}` |
| `type` | string | ✓ | `"function"` (includes methods) |
| `file` | string | ✓ | Relative path to Python file |
| `brick` | string | ✓ | Brick ID (from brick definition or `@brick` decorator) |
| `implements` | array | ✓ | Array of spec IDs (from `@implements` decorator). Empty `[]` if none. |
| `calls` | array | ✓ | Array of function IDs this function calls (from AST analysis). Empty `[]` if none. |

**Module and Class Nodes (OPTIONAL):**

May include for navigation:
```json
{"id":"M-auth.session","type":"module","file":"src/auth/session.py","brick":"BRICK-AUTH","imports":["M-auth.tokens"],"contains":["F-auth.session.authenticate"]}
{"id":"C-auth.tokens.TokenValidator","type":"class","file":"src/auth/tokens.py","brick":"BRICK-AUTH","contains":["F-auth.tokens.TokenValidator.validate"]}
```

**These are scaffolding.** Core alignment only needs F nodes.

### File 3: verification-graph.ndjson

**Generated from:**
- Test discovery (pytest, unittest)
- Coverage analysis (pytest-cov, coverage.py)
- `@verifies` decorators
- `@brick` decorators (optional)

**Schema (one JSON object per line):**

```json
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","brick":"BRICK-AUTH","verifies":["S-AUTH-001"],"covers":["F-auth.session.authenticate","F-auth.tokens.validate"]}
{"id":"T-test_auth.test_rate_limiting","type":"test","file":"tests/unit/test_auth.py","brick":"BRICK-AUTH","verifies":["S-AUTH-002"],"covers":["F-auth.session.authenticate"]}
```

**Test Node:**
```json
{
  "id": "T-test_auth.test_token_expiration",
  "type": "test",
  "file": "tests/unit/test_auth.py",
  "brick": "BRICK-AUTH",
  "verifies": ["S-AUTH-001"],
  "covers": ["F-auth.session.authenticate", "F-auth.tokens.validate"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Test ID. Format: `T-{module}.{test_function}` or `T-{module}.{TestClass}.{test_method}` |
| `type` | string | ✓ | `"test"` |
| `file` | string | ✓ | Relative path to test file |
| `brick` | string or null | ✓ | Brick ID (from `@brick` decorator or inferred from coverage). `null` for integration tests. |
| `verifies` | array | ✓ | Array of spec/outcome IDs (from `@verifies` decorator). Empty `[]` if none. |
| `covers` | array | ✓ | Array of function IDs executed by this test (from coverage analysis). Empty `[]` if none. |

### Why NDJSON for Graphs?

**From AG018:**
- Clean git diffs (only changed lines show)
- Streaming processing (no need to load entire file)
- One node per line (grep/sed-friendly)
- Sortable by ID (stable diffs)

**Trade-off:**
- Not pretty-printed (less human-readable than regular JSON)
- No schema validation on file level (validate per line)

**Acceptable because:**
- Graphs are machine-generated (humans read markdown, not graphs)
- Tools parse graphs, not humans
- Git diffs are more important than readability

---

## File Structure Summary

```
project-root/
├── jig/
│   ├── specifications/
│   │   ├── auth.md              # Spec S-AUTH-001, S-AUTH-002
│   │   ├── cli.md               # Spec S-CLI-001, S-CLI-002
│   │   └── storage.md           # Spec S-STORAGE-001
│   ├── outcomes/                # OPTIONAL
│   │   ├── auth.md              # Outcome O-AUTH-001
│   │   └── cli.md               # Outcome O-CLI-001
│   ├── intent-graph.ndjson      # Generated
│   ├── implementation-graph.ndjson  # Generated
│   └── verification-graph.ndjson    # Generated
├── bricks/
│   ├── auth.brick.yaml          # BRICK-AUTH
│   ├── cli.brick.yaml           # BRICK-CLI
│   └── utils.brick.yaml         # BRICK-UTILS
├── src/
│   ├── auth/
│   │   ├── session.py           # @implements decorators
│   │   └── tokens.py
│   ├── cli/
│   │   └── main.py
│   └── utils/
│       └── io.py
└── tests/
    ├── unit/
    │   ├── test_auth.py         # @verifies decorators
    │   └── test_cli.py
    └── integration/
        └── test_flows.py        # @verifies outcome IDs
```

---

## Required vs Optional vs Excluded

### REQUIRED (system breaks without these)

**Human-authored:**
1. ✓ Specification files (`jig/specifications/*.md`) with required frontmatter
2. ✓ Brick definition files (`bricks/*.brick.yaml`) with required fields
3. ✓ `@implements` decorators on functions that implement specs
4. ✓ `@verifies` decorators on tests that verify specs

**Machine-generated:**
5. ✓ `jig/intent-graph.ndjson`
6. ✓ `jig/implementation-graph.ndjson`
7. ✓ `jig/verification-graph.ndjson`

### OPTIONAL (nice to have, not required for core alignment)

**Human-authored:**
1. ○ Outcome files (`jig/outcomes/*.md`)
2. ○ `@brick` decorators (if brick assignment is clear from brick definition)
3. ○ Markdown body in spec/outcome files (documentation, not parsed)
4. ○ Module/class nodes in implementation graph (navigation, not alignment)
5. ○ `depends_on` in spec frontmatter (if no dependencies)

### EXCLUDED (deliberately not supported)

**Never include:**
1. ✗ Line numbers in graph files (brittle, from AG017)
2. ✗ Metrics/aggregations in graph files (computed on demand, from AG017)
3. ✗ Timestamps in graph files (use git for this, from AG017)
4. ✗ `public_api` field in brick definitions (derived from calls, from AG020)
5. ✗ `specs` field in brick definitions (derived from F→S edges, from AG020)
6. ✗ Decorators pointing to outcome IDs in `@implements` (functions implement specs, not outcomes)
7. ✗ Decorators pointing to file paths (use IDs, not paths)
8. ✗ Multiple bricks per file (one brick = one file)
9. ✗ Spec IDs not matching format `S-{DOMAIN}-{NNN}` (must be consistent)
10. ✗ Functions split across multiple bricks (partition constraint, from AG020)

---

## Validation Rules

### Validation 1: Spec IDs are unique

```python
def validate_spec_ids(specs):
    ids = [s["id"] for s in specs]
    duplicates = [id for id in ids if ids.count(id) > 1]
    if duplicates:
        raise ValueError(f"Duplicate spec IDs: {duplicates}")
```

### Validation 2: Brick IDs are unique

```python
def validate_brick_ids(bricks):
    ids = [b["id"] for b in bricks]
    duplicates = [id for id in ids if ids.count(id) > 1]
    if duplicates:
        raise ValueError(f"Duplicate brick IDs: {duplicates}")
```

### Validation 3: All @implements references exist

```python
def validate_implements(functions, specs):
    spec_ids = {s["id"] for s in specs}
    for func in functions:
        for spec_id in func["implements"]:
            if spec_id not in spec_ids:
                raise ValueError(f"{func['id']} implements non-existent {spec_id}")
```

### Validation 4: All @verifies references exist

```python
def validate_verifies(tests, specs, outcomes):
    valid_ids = {s["id"] for s in specs} | {o["id"] for o in outcomes}
    for test in tests:
        for id in test["verifies"]:
            if id not in valid_ids:
                raise ValueError(f"{test['id']} verifies non-existent {id}")
```

### Validation 5: All brick dependencies exist

```python
def validate_brick_deps(bricks):
    brick_ids = {b["id"] for b in bricks}
    for brick in bricks:
        for dep_id in brick["depends_on"]:
            if dep_id not in brick_ids:
                raise ValueError(f"{brick['id']} depends on non-existent {dep_id}")
```

### Validation 6: Every function belongs to exactly one brick

```python
def validate_partition(bricks, functions):
    brick_assignments = {}
    for brick in bricks:
        for func_id in expand_brick_to_functions(brick):
            if func_id in brick_assignments:
                raise ValueError(f"{func_id} assigned to both {brick_assignments[func_id]} and {brick['id']}")
            brick_assignments[func_id] = brick["id"]

    # Check all functions are assigned
    unassigned = set(f["id"] for f in functions) - set(brick_assignments.keys())
    if unassigned:
        raise ValueError(f"{len(unassigned)} functions not assigned to any brick")
```

### Validation 7: No class splitting

```python
def validate_no_class_split(classes, functions):
    for class_id, method_ids in classes.items():
        method_bricks = {functions[m]["brick"] for m in method_ids}
        if len(method_bricks) > 1:
            raise ValueError(f"Class {class_id} split across bricks {method_bricks}")
```

---

## Why These Choices?

### Why YAML frontmatter in markdown?

**Alternatives considered:**
- Separate YAML files (specs.yaml, outcomes.yaml)
- JSON files
- Database

**Chosen because:**
1. **Human-readable:** Markdown is familiar, writable, reviewable
2. **Single file:** Frontmatter + body in one place (no sync issues)
3. **Git-friendly:** Markdown diffs are readable
4. **Tooling:** Every language can parse YAML frontmatter
5. **Flexibility:** Body can be rich documentation (examples, diagrams, links)

**Trade-off:** Parsing markdown frontmatter is slower than pure YAML. Acceptable because:
- Spec files change infrequently (not performance-critical)
- Tooling caches parsed frontmatter

---

### Why decorators instead of mapping files?

**Alternatives considered:**
- Separate mapping file (`spec-to-code.yaml`)
- Comments in docstrings (`"""Implements: S-AUTH-001"""`)
- Convention-based (function name → spec ID)

**Chosen because:**
1. **Co-located:** Decorator lives with the code (git tracks together)
2. **Parseable:** AST parsing extracts decorators reliably
3. **Explicit:** No guessing from comments or conventions
4. **Refactor-safe:** Renaming function doesn't break mapping
5. **Type-checkable:** IDEs can validate decorator arguments

**Trade-off:** Adds one line per function. Acceptable because:
- One-time cost per function
- Makes intent explicit (good for readability)
- Enables automated alignment checking

---

### Why NDJSON for graphs instead of JSON?

**Alternatives considered:**
- Pretty-printed JSON (one file per graph)
- JSON (minified)
- SQLite database
- Per-module JSON files

**Chosen because:**
1. **Git diffs:** Only changed lines show (critical for frequent updates)
2. **Streaming:** Can process without loading entire file
3. **Grep-friendly:** One node per line
4. **Simplicity:** No database setup, human-inspectable

**Trade-off:** Less readable than pretty-printed JSON. Acceptable because:
- Graphs are machine-generated (humans read markdown, not graphs)
- Tools parse graphs, not humans
- Can convert NDJSON → pretty JSON for inspection

---

### Why three separate graph files instead of one?

**Alternatives considered:**
- Single `alignment-graph.ndjson` (all nodes in one file)
- Per-brick graph files
- Database with tables

**Chosen because:**
1. **Minimal git churn:** Intent changes rarely, implementation changes frequently (from AG018)
2. **Independent updates:** Rebuild impl without touching intent
3. **Clear separation:** Design (intent) vs code (impl) vs tests (verify)

**Trade-off:** Cross-graph queries require loading all three. Acceptable because:
- Files are small (<1MB for most projects)
- Modern machines parse JSON fast
- Can lazy-load graphs as needed

---

### Why brick definitions in separate files?

**Alternatives considered:**
- Bricks defined inline in code (`@brick` decorators everywhere)
- Bricks in intent-graph.ndjson
- One `bricks.yaml` with all bricks

**Chosen because:**
1. **Centralized architecture:** See all brick boundaries in one place
2. **One brick per file:** Easy to find, easy to review
3. **Independent of code:** Can design bricks before code exists
4. **Validation:** Can validate brick definitions before code

**Trade-off:** Brick definitions can drift from code. Mitigated by:
- Validation on every rebuild
- Discovery tool suggests brick definitions from code

---

### Why no line numbers in graph files?

**Alternatives considered:**
- Store line numbers for all functions/tests
- Store line ranges (start, end)
- Store file offsets

**Chosen because (from AG017):**
1. **Brittle:** Line numbers change when code above is edited
2. **Git churn:** Unnecessary diffs when line numbers shift
3. **Computable:** Can find line number on demand (AST search, grep)

**Trade-off:** Need to search for function when navigating. Acceptable because:
- Navigation is infrequent (compared to git commits)
- AST search is fast (<100ms)
- Git doesn't show false diffs

---

### Why specs use domain prefixes (S-AUTH-001) instead of UUIDs?

**Alternatives considered:**
- UUIDs (`S-a3f2e9d7-...`)
- Sequential numbers (`S-001`, `S-002`)
- Hash-based (`S-auth-a3f2e9`)

**Chosen because:**
1. **Human-readable:** `S-AUTH-001` tells you it's about auth
2. **Sortable:** Numbers allow ordering
3. **Groupable:** All `S-AUTH-*` specs are related
4. **Memorable:** Can reference in conversation ("triple-zero-one")

**Trade-off:** Risk of ID collisions (two people create S-AUTH-042). Mitigated by:
- Validation on rebuild (detect duplicates)
- Convention: one person owns each domain prefix
- Tooling: `jigy new spec --domain AUTH` auto-assigns next number

---

## Complete Example: End-to-End

### Step 1: Human writes specification

**File:** `jig/specifications/auth.md`

```markdown
---
id: S-AUTH-001
type: specification
brick: BRICK-AUTH
depends_on: []
---

# Token Expiration

Authentication tokens MUST expire after 15 minutes of inactivity.

**Acceptance Criteria:**
- Token created with `expires_at = now() + 15 minutes`
- Any operation updates `last_activity` timestamp
- Token rejected if `now() > last_activity + 15 minutes`
```

---

### Step 2: Human defines brick

**File:** `bricks/auth.brick.yaml`

```yaml
id: BRICK-AUTH
name: Authentication & Session Management
depends_on: [BRICK-UTILS]
modules:
  - auth.session
  - auth.tokens
classes: []
functions: []
```

---

### Step 3: Human implements function

**File:** `src/auth/session.py`

```python
from datetime import datetime, timedelta
from jig import implements

@implements("S-AUTH-001")
def authenticate(user: str, password: str) -> Token:
    """Authenticate user and return session token."""
    if _check_password(user, password):
        token = Token(
            user=user,
            expires_at=datetime.now() + timedelta(minutes=15),
            last_activity=datetime.now()
        )
        return token
    return None

def _check_password(user: str, password: str) -> bool:
    # Implementation detail (no @implements)
    ...
```

---

### Step 4: Human writes test

**File:** `tests/unit/test_auth.py`

```python
from jig import verifies
import time

@verifies("S-AUTH-001")
def test_token_expiration():
    """Verify tokens expire after 15 minutes of inactivity."""
    token = authenticate("user", "pass")

    # Token should be valid initially
    assert not is_expired(token)

    # Simulate 15 minutes + 1 second
    token.last_activity = datetime.now() - timedelta(minutes=15, seconds=1)

    # Token should now be expired
    assert is_expired(token)
```

---

### Step 5: Machine generates graphs

**Command:**
```bash
jigy index         # Generate intent-graph.ndjson
jigy impl rebuild  # Generate implementation-graph.ndjson
jigy verify rebuild --run-tests  # Generate verification-graph.ndjson
```

**Generated: `jig/intent-graph.ndjson`**
```json
{"id":"S-AUTH-001","type":"specification","content":"Token Expiration","file":"jig/specifications/auth.md","brick":"BRICK-AUTH","depends_on":[]}
{"id":"BRICK-AUTH","type":"brick","name":"Authentication & Session Management","file":"bricks/auth.brick.yaml","depends_on":["BRICK-UTILS"]}
{"id":"BRICK-UTILS","type":"brick","name":"Core Utilities","file":"bricks/utils.brick.yaml","depends_on":[]}
```

**Generated: `jig/implementation-graph.ndjson`**
```json
{"id":"F-auth.session.authenticate","type":"function","file":"src/auth/session.py","brick":"BRICK-AUTH","implements":["S-AUTH-001"],"calls":["F-auth.session._check_password"]}
{"id":"F-auth.session._check_password","type":"function","file":"src/auth/session.py","brick":"BRICK-AUTH","implements":[],"calls":[]}
```

**Generated: `jig/verification-graph.ndjson`**
```json
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","brick":"BRICK-AUTH","verifies":["S-AUTH-001"],"covers":["F-auth.session.authenticate","F-auth.session._check_password"]}
```

---

### Step 6: Query alignment

**Command:**
```bash
jigy status
```

**Output:**
```
Loading graphs...
  intent-graph.ndjson (3 nodes)
  implementation-graph.ndjson (2 nodes)
  verification-graph.ndjson (1 node)

Computing alignment...

S-AUTH-001: Token Expiration
  ✓ Implemented by: F-auth.session.authenticate
  ✓ Verified by: T-test_auth.test_token_expiration
  ✓ Test covers implementation

  Alignment: PERFECT

Overall Alignment: 100% (1/1 specs perfectly aligned)
```

---

## Migration Path

For existing projects adopting jig:

### Phase 1: Document Intent (Specs)
1. Create `jig/specifications/` directory
2. Write specification files for existing features (reverse-engineer from code)
3. Generate `jig/intent-graph.ndjson`

### Phase 2: Define Architecture (Bricks)
1. Create `bricks/` directory
2. Run `jigy discover bricks` to propose partitions
3. Refine brick definitions manually
4. Validate partition (every function assigned to one brick)

### Phase 3: Annotate Code (Decorators)
1. Add `@implements` decorators to functions
2. Generate `jig/implementation-graph.ndjson`
3. Validate (all spec IDs exist)

### Phase 4: Annotate Tests (Decorators)
1. Add `@verifies` decorators to tests
2. Run tests with coverage
3. Generate `jig/verification-graph.ndjson`
4. Validate (all spec/outcome IDs exist)

### Phase 5: Measure Alignment
1. Run `jigy status` to see current alignment
2. Identify gaps (unimplemented specs, unverified specs, untested code)
3. Iterate (add missing implementations/tests)

**Tooling support:**
```bash
jigy migrate init           # Create directories
jigy migrate discover       # Auto-generate specs from code
jigy migrate annotate       # Suggest decorators for existing code
jigy migrate validate       # Check for errors
```

---

## Conclusion

This contract defines the **irreducible foundation** of the jig system:

**Five artifacts:**
1. Specification files (YAML frontmatter in markdown)
2. Outcome files (YAML frontmatter in markdown) - OPTIONAL
3. Brick definition files (.brick.yaml)
4. @jig decorators (in Python source)
5. Graph files (.ndjson, machine-generated)

**Three core relationships (from AG019):**
- F → S (implements)
- T → S (verifies)
- T → F (covers)

**Everything else is derived or optional.**

**Missing elements will break the system:**
- No spec files → no intent to align to
- No brick files → no architectural boundaries
- No decorators → no F→S or T→S edges
- No graph files → no queryable alignment

**Extra elements create noise:**
- Line numbers in graphs (brittle)
- Metrics in graphs (should be computed)
- Manual public_api fields (derivable)

**This is the foundation.** Build on it, but don't break it.

---

## References

- **AG017:** Minimal Graph Schema (storage format)
- **AG018:** Graph Storage Strategy (NDJSON choice)
- **AG019:** Irreducible Core (S-F-T triangle)
- **AG020:** Bricks as Partitions (brick definition)
