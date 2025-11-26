# The Irreducible Core of the Alignment Graph

_Three Nodes, Three Edges, One Truth_

**Date:** 2025-11-25
**Status:** Principle
**Related:** AG002 (Alignment Graph Whitepaper), AG017 (Minimal Schema), AG018 (Storage Strategy)

---

## The Essential Claim

The Alignment Graph, at its core, is a relationship between exactly **three types of nodes**:

- **S** - Specifications (what we intend to build)
- **F** - Functions (what we actually built)
- **T** - Tests (what we actually verify)

And exactly **three types of edges**:

- **F → S** - implements (which functions implement which specs)
- **T → S** - verifies (which tests verify which specs)
- **T → F** - covers (which tests execute which functions)

**Everything else is organizational scaffolding.**

This is the irreducible core. Remove any node type or edge type, and alignment becomes unmeasurable. Add more, and you're adding convenience, not essence.

---

## The Triangle

```
         S
        ╱ ▲ ╲
       ╱  │  ╲
      ╱   │   ╲
     ╱    │    ╲
    ╱  verifies ╲
   ╱      │      ╲
  ╱       │       ╲
 ▼        │        ▼
F ────────┴────────> T
      covers
```

**Three questions define alignment:**

1. **Intent → Implementation:** Does function F implement specification S?
2. **Intent → Verification:** Does test T verify specification S?
3. **Implementation → Verification:** Does test T execute function F?

If all three edges exist for a given S, you have **perfect alignment** for that spec:
- It's implemented (F → S)
- It's verified (T → S)
- The verification actually tests the implementation (T → F)

---

## What Each Edge Means

### F → S (implements)

**Question:** "Which specifications does this function implement?"

**Source:** `@implements("S-*")` decorator on functions

**Example:**
```python
@implements("S-AUTH-001", "S-AUTH-002")
def authenticate(user: str, password: str) -> Token:
    """Authenticate user and return session token."""
    ...
```

**Graph edge:**
```
F-auth.session.authenticate → S-AUTH-001
F-auth.session.authenticate → S-AUTH-002
```

**Absence indicates:**
- Function exists but serves no documented specification (orphan code)
- Specification exists but has no implementing function (unimplemented spec)

---

### T → S (verifies)

**Question:** "Which specifications does this test verify?"

**Source:** `@verifies("S-*", "O-*")` decorator on tests

**Example:**
```python
@verifies("S-AUTH-001")
def test_token_expiration():
    """Verify tokens expire after inactivity."""
    token = authenticate("user", "pass")
    time.sleep(901)  # 15 min + 1 sec
    assert is_expired(token)
```

**Graph edge:**
```
T-test_auth.test_token_expiration → S-AUTH-001
```

**Absence indicates:**
- Test exists but verifies no specification (orphan test)
- Specification exists but has no verifying test (unverified spec)

---

### T → F (covers)

**Question:** "Which functions does this test execute?"

**Source:** Coverage analysis (pytest-cov, coverage.py)

**Example:**
```bash
# Run tests with coverage
$ pytest --cov=src tests/

# Coverage report shows test_token_expiration executes:
# - authenticate()
# - _validate_token()
# - _check_expiry()
```

**Graph edges:**
```
T-test_auth.test_token_expiration → F-auth.session.authenticate
T-test_auth.test_token_expiration → F-auth.session._validate_token
T-test_auth.test_token_expiration → F-auth.session._check_expiry
```

**Absence indicates:**
- Function exists but is never executed by any test (untested code)
- Test exists but doesn't execute any functions (broken test)

---

## The Alignment Queries

With these three edges, you can answer every fundamental alignment question:

### 1. Is specification S implemented?

```
Query: Does there exist F where F → S?
Answer: Yes if edge exists, No otherwise
```

### 2. Is specification S verified?

```
Query: Does there exist T where T → S?
Answer: Yes if edge exists, No otherwise
```

### 3. Does the test that verifies S actually execute the function that implements S?

```
Query: Given S, find F where (F → S), find T where (T → S).
       Does T → F exist?
Answer: Yes = aligned, No = drift (test doesn't cover implementation)
```

### 4. Which specifications have perfect alignment?

```
Query: Find all S where:
  - EXISTS F: F → S (implemented)
  - EXISTS T: T → S (verified)
  - AND T → F (verification covers implementation)
Result: Set of perfectly aligned specifications
```

### 5. Where is the drift?

**Unimplemented specs:**
```
Query: Find S where NOT EXISTS F: F → S
Result: Specifications with no implementing functions
```

**Unverified specs:**
```
Query: Find S where NOT EXISTS T: T → S
Result: Specifications with no verifying tests
```

**Untested functions:**
```
Query: Find F where NOT EXISTS T: T → F
Result: Functions never executed by any test
```

**Orphan code:**
```
Query: Find F where NOT EXISTS S: F → S
Result: Functions implementing no documented specification
```

**Orphan tests:**
```
Query: Find T where (NOT EXISTS S: T → S) AND (NOT EXISTS F: T → F)
Result: Tests verifying nothing and covering nothing
```

**Misaligned verification:**
```
Query: Find (S, F, T) where (F → S) AND (T → S) but NOT (T → F)
Result: Test claims to verify spec, but doesn't execute the implementation
```

---

## Everything Else Is Scaffolding

### Outcomes (O)

**Purpose:** Explain WHY specifications exist

**Relationship:** O → S (outcome specifies)

**Why it's not core:**
- Removing O doesn't break alignment measurement
- O provides human context, not machine-checkable relationships
- O is documentation for the design decisions behind S

**Example:**
```
O-AUTH-001: "Users can authenticate without passwords"
  ├─ S-AUTH-001: "Tokens expire after 15 min"
  ├─ S-AUTH-002: "Failed logins are rate-limited"
  └─ S-AUTH-003: "Tokens use cryptographic signatures"
```

The alignment question is: "Are S-AUTH-001, S-AUTH-002, S-AUTH-003 implemented and verified?"

Whether they're grouped under O-AUTH-001 is organizational, not alignment-critical.

---

### Modules (M) and Classes (C)

**Purpose:** Navigate to functions in code structure

**Relationships:**
- M → F (module contains function)
- C → F (class contains method)

**Why they're not core:**
- F nodes can exist without M or C (we just need function IDs)
- M and C help answer "where is this function?" not "is this function aligned?"
- They're implementation organization, not alignment relationships

**Example:**
```
M-auth.session
  ├─ C-auth.session.SessionManager
  │   ├─ F-auth.session.SessionManager.create
  │   └─ F-auth.session.SessionManager.destroy
  └─ F-auth.session.authenticate
```

For alignment, we only care about:
```
F-auth.session.authenticate → S-AUTH-001
T-test_auth.test_auth → S-AUTH-001
T-test_auth.test_auth → F-auth.session.authenticate
```

The module/class hierarchy helps us navigate to the function, but doesn't participate in alignment.

---

### Bricks (B) and Subsystems

**Purpose:** Group S, F, T into architectural units

**Relationships:**
- S → B (spec assigned to brick)
- F → B (function assigned to brick)
- T → B (test assigned to brick)
- B → B (brick depends on brick)

**Why they're not core:**
- Bricks are organizational boundaries for humans and agents
- Alignment exists at the S-F-T level regardless of brick assignment
- You can measure alignment without bricks; bricks help you organize and scope

**Example:**
```
BRICK-AUTH
  ├─ S-AUTH-001, S-AUTH-002, S-AUTH-003
  ├─ F-auth.session.authenticate, F-auth.tokens.validate
  └─ T-test_auth.test_token_expiration, T-test_auth.test_rate_limiting
```

Bricks let you ask: "Is BRICK-AUTH aligned?" (scoped alignment query)

But the alignment calculation is still the same S-F-T triangle, just filtered to one brick.

---

## Minimum Human Input

To build the alignment graph, humans must provide exactly:

### 1. Specification IDs (S nodes)

**Source:** YAML frontmatter in markdown files

**Minimum:**
```yaml
---
id: S-AUTH-001
---
```

That's it. The rest (title, description, rationale) is documentation.

---

### 2. Implementation Declarations (F → S edges)

**Source:** `@implements` decorators

**Minimum:**
```python
@implements("S-AUTH-001")
def authenticate(...):
    ...
```

No other metadata needed. The edge is the information.

---

### 3. Verification Declarations (T → S edges)

**Source:** `@verifies` decorators

**Minimum:**
```python
@verifies("S-AUTH-001")
def test_token_expiration():
    ...
```

Again, just the edge.

---

### 4. Coverage Data (T → F edges)

**Source:** Automated coverage analysis

**Generated, not authored:**
```bash
pytest --cov=src tests/
```

Coverage tool observes which functions are executed by which tests. This generates T → F edges automatically.

---

## What Can Be Automatically Derived

From the minimum human input above, we can derive:

**F nodes:**
- Function names, signatures, locations
- Discovered by parsing code with AST

**T nodes:**
- Test names, locations
- Discovered by pytest/unittest test discovery

**M nodes (optional):**
- Module structure
- Derived from file paths

**C nodes (optional):**
- Class hierarchy
- Derived from AST parsing

**O nodes (optional):**
- Outcome descriptions
- Parsed from markdown frontmatter (if present)

**Import relationships, call graphs, complexity metrics:**
- All derived from static analysis

**Everything except the three core edges** can be derived from observable facts in code and markdown.

---

## The Minimum Graph Files

### intent-graph.json (core)

```json
{
  "specs": {
    "S-AUTH-001": {
      "file": "jig/specs/auth.md"
    },
    "S-AUTH-002": {
      "file": "jig/specs/auth.md"
    }
  }
}
```

Just the spec IDs and where they're defined. Everything else is organizational.

---

### implementation-graph.json (core)

```json
{
  "functions": {
    "F-auth.session.authenticate": {
      "file": "src/auth/session.py",
      "implements": ["S-AUTH-001", "S-AUTH-002"]
    }
  }
}
```

Function IDs, locations, and **F → S edges**. Modules/classes can be inferred from IDs or added for navigation.

---

### verification-graph.json (core)

```json
{
  "tests": {
    "T-test_auth.test_token_expiration": {
      "file": "tests/test_auth.py",
      "verifies": ["S-AUTH-001"],
      "covers": ["F-auth.session.authenticate", "F-auth.tokens.validate"]
    }
  }
}
```

Test IDs, **T → S edges** (from decorators), and **T → F edges** (from coverage).

---

## The Alignment Calculation

Given the three graphs above, alignment is computable:

### For a single specification S-AUTH-001:

```python
# 1. Is it implemented?
implemented = any(
    "S-AUTH-001" in f["implements"]
    for f in implementation_graph["functions"].values()
)

# 2. Is it verified?
verified = any(
    "S-AUTH-001" in t["verifies"]
    for t in verification_graph["tests"].values()
)

# 3. Does verification cover implementation?
impl_funcs = {
    f_id for f_id, f in implementation_graph["functions"].items()
    if "S-AUTH-001" in f["implements"]
}

verify_tests = {
    t_id for t_id, t in verification_graph["tests"].items()
    if "S-AUTH-001" in t["verifies"]
}

covered_funcs = {
    f_id
    for t_id in verify_tests
    for f_id in verification_graph["tests"][t_id]["covers"]
}

full_coverage = impl_funcs.issubset(covered_funcs)

# Alignment status:
alignment = {
    "implemented": implemented,
    "verified": verified,
    "coverage_complete": full_coverage,
    "aligned": implemented and verified and full_coverage
}
```

**Perfect alignment requires all three.**

---

## Example: Full Lifecycle

### Human writes:

**1. Specification**
```markdown
---
id: S-AUTH-001
---
# Token Expiration
Tokens expire after 15 minutes of inactivity.
```

**2. Implementation**
```python
@implements("S-AUTH-001")
def authenticate(user, password):
    token = create_token(user)
    token.expires_at = now() + timedelta(minutes=15)
    return token
```

**3. Test**
```python
@verifies("S-AUTH-001")
def test_token_expiration():
    token = authenticate("user", "pass")
    assert token.expires_at == now() + timedelta(minutes=15)
```

**4. Run tests with coverage**
```bash
pytest --cov=src tests/
```

---

### Machine generates:

**intent-graph.json:**
```json
{
  "specs": {
    "S-AUTH-001": {"file": "jig/specs/auth.md"}
  }
}
```

**implementation-graph.json:**
```json
{
  "functions": {
    "F-auth.authenticate": {
      "file": "src/auth.py",
      "implements": ["S-AUTH-001"]
    }
  }
}
```

**verification-graph.json:**
```json
{
  "tests": {
    "T-test_auth.test_token_expiration": {
      "file": "tests/test_auth.py",
      "verifies": ["S-AUTH-001"],
      "covers": ["F-auth.authenticate"]
    }
  }
}
```

---

### Alignment check:

```bash
$ jigy status

S-AUTH-001: Token Expiration
  ✓ Implemented by: F-auth.authenticate
  ✓ Verified by: T-test_auth.test_token_expiration
  ✓ Test covers implementation

  Alignment: PERFECT
```

---

## Why This Matters

### 1. Simplicity

The model is now trivial to explain:
- "Does the function implement the spec?"
- "Does the test verify the spec?"
- "Does the test execute the function?"

Three yes/no questions. That's the entire alignment model.

---

### 2. Minimal Overhead

Developers add three things:
- Spec IDs in markdown (design documentation they'd write anyway)
- `@implements` on functions (one line)
- `@verifies` on tests (one line)

Coverage is automatic. Everything else is derived.

---

### 3. Objective Measurement

Alignment is now boolean, not subjective:
- Edge exists or it doesn't
- No interpretation required
- Queryable, automatable, enforceable

---

### 4. Clear Failure Modes

When alignment fails, the cause is explicit:
- Missing F → S edge → unimplemented spec or orphan code
- Missing T → S edge → unverified spec or orphan test
- Missing T → F edge → test doesn't cover implementation

Each has a clear remediation.

---

### 5. Scalability

The model scales linearly:
- 1 spec, 1 function, 1 test = 3 edges to check
- 1000 specs = 3000 edges to check
- Complexity: O(S + F + T), not O(S × F × T)

Graph queries are fast. Storage is minimal.

---

## What We Gained by Reducing to Core

### Before (full model):
- Outcomes, Specifications, Bricks, Subsystems, Modules, Classes, Functions, Tests
- 8 node types, dozens of edge types
- Complex dependencies, unclear what's essential

### After (irreducible core):
- Specifications, Functions, Tests
- 3 node types, 3 edge types
- Clear purpose for each

### The rest becomes:
- **Optional organizational layers** (Bricks, Subsystems, Modules, Classes)
- **Optional documentation** (Outcomes)
- **Optional metrics** (complexity, coupling, etc.)

You can add these layers for convenience, but alignment exists without them.

---

## Implications for Implementation

### Graph Files Can Be Simpler

**Option 1: Three minimal files**
```
jig/specs.json          # Just spec IDs
jig/implements.json     # F → S edges
jig/verifies.json       # T → S and T → F edges
```

**Option 2: One alignment file**
```json
{
  "specs": ["S-AUTH-001", "S-AUTH-002"],
  "implements": {
    "F-auth.authenticate": ["S-AUTH-001", "S-AUTH-002"]
  },
  "verifies": {
    "T-test_auth.test_expiration": {
      "specs": ["S-AUTH-001"],
      "covers": ["F-auth.authenticate"]
    }
  }
}
```

Everything else (full metadata, organizational structure) can be in separate files or computed on demand.

---

### Validation Becomes Trivial

```python
def validate_alignment():
    errors = []

    # Check all F → S edges reference valid specs
    for func_id, func in implementation_graph.items():
        for spec_id in func["implements"]:
            if spec_id not in specs:
                errors.append(f"{func_id} implements non-existent {spec_id}")

    # Check all T → S edges reference valid specs
    for test_id, test in verification_graph.items():
        for spec_id in test["verifies"]:
            if spec_id not in specs:
                errors.append(f"{test_id} verifies non-existent {spec_id}")

    # Check all T → F edges reference valid functions
    for test_id, test in verification_graph.items():
        for func_id in test["covers"]:
            if func_id not in implementation_graph:
                errors.append(f"{test_id} covers non-existent {func_id}")

    return errors
```

---

### Queries Become Simple Graph Traversals

No complex joins, no nested lookups. Just follow edges.

```python
# Unverified specs
unverified = [
    s for s in specs
    if not any(s in t["verifies"] for t in tests.values())
]

# Untested functions
untested = [
    f for f in functions
    if not any(f in t["covers"] for t in tests.values())
]

# Perfectly aligned specs
aligned = [
    s for s in specs
    if has_implementation(s) and has_verification(s) and verification_covers_implementation(s)
]
```

---

## The Core Principle

**The Alignment Graph is not about modeling the entire software system.**

**It's about making three specific relationships explicit and measurable:**

1. **Intent → Implementation** (F → S)
2. **Intent → Verification** (T → S)
3. **Implementation → Verification** (T → F)

Everything else—modules, classes, outcomes, bricks, subsystems, metrics—exists to **organize**, **navigate**, and **present** these core relationships.

But the alignment itself lives entirely in the S-F-T triangle.

---

## Conclusion

The Alignment Graph reduces to:

**Three node types:**
- S (Specifications) - what we intend
- F (Functions) - what we built
- T (Tests) - what we verify

**Three edge types:**
- F → S (implements)
- T → S (verifies)
- T → F (covers)

**Three human inputs:**
- Spec IDs in markdown
- `@implements` decorators
- `@verifies` decorators

**Plus one machine input:**
- Coverage analysis (generates T → F)

This is the **irreducible core**. You cannot remove any part and still measure alignment. Everything else is derived, organizational, or optional.

**The simplicity is the point.** Alignment is a simple concept that's been made complex by tooling. The Alignment Graph makes it simple again.

---

## References

- **AG002:** Alignment Graph Whitepaper (full model)
- **AG017:** Minimal Graph Schema (storage format)
- **AG018:** Graph Storage Strategy (implementation approach)
- **Simon (1962):** "The Architecture of Complexity" (nearly decomposable systems)
- **Parnas (1972):** "On the Criteria To Be Used in Decomposing Systems into Modules" (information hiding)

---

_The essence of architecture is knowing what to leave out._
