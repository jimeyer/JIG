# Bricks as Partitions of Functions

_The Simplest Definition That Could Possibly Work_

**Date:** 2025-11-25
**Status:** Principle
**Related:** AG002 (Alignment Graph Whitepaper), AG019 (Irreducible Core)

---

## The Core Definition

**A Brick is a partition of the function space F.**

That's it. Nothing more, nothing less.

Given the set of all functions in a codebase F = {F₁, F₂, F₃, ...}, a set of bricks B = {B₁, B₂, B₃, ...} partitions F such that:

1. **Every function belongs to exactly one brick:** ∀f ∈ F, ∃!b ∈ B : f ∈ b
2. **Bricks are disjoint:** ∀b₁, b₂ ∈ B where b₁ ≠ b₂ : b₁ ∩ b₂ = ∅
3. **Bricks cover all functions:** ⋃ B = F

A brick is simply a named subset of functions. Every function is in exactly one brick.

---

## Why This Matters

**Before this insight:**
- Bricks were a separate architectural abstraction
- Had their own definitions, constraints, interfaces, dependencies
- Required human design and maintenance
- Difficult to discover or validate

**After this insight:**
- Bricks are just names for sets of functions
- Everything else (specs, tests, dependencies, public API) derives from set membership
- Can be discovered automatically from code structure
- Validation is simple set operations

**The complexity collapses.**

---

## Practical Implementation: M, C, F Granularity

While theoretically bricks partition F (functions), practically we define them at three granularities:

### Module-Level Partitioning (Coarse)

```yaml
id: BRICK-AUTH
modules:
  - M-auth.session
  - M-auth.tokens
  - M-auth.validate
```

**Meaning:** All functions in these modules belong to BRICK-AUTH.

**When to use:**
- Modules are already well-organized
- Entire module has coherent responsibility
- Simple to define and maintain

**Expands to:**
```
BRICK-AUTH = {
  F-auth.session.authenticate,
  F-auth.session.logout,
  F-auth.session.create_session,
  F-auth.tokens.validate,
  F-auth.tokens.refresh,
  F-auth.validate.check_password,
  ...
}
```

---

### Class-Level Partitioning (Medium)

```yaml
id: BRICK-AUTH
classes:
  - C-auth.session.SessionManager
  - C-auth.tokens.TokenValidator
modules:
  - M-auth.utils  # Helper functions
```

**Meaning:** All methods of these classes, plus all functions in auth.utils, belong to BRICK-AUTH.

**When to use:**
- Module contains multiple concerns
- Only some classes belong together
- Finer control than module-level

**Expands to:**
```
BRICK-AUTH = {
  F-auth.session.SessionManager.create,
  F-auth.session.SessionManager.destroy,
  F-auth.tokens.TokenValidator.validate,
  F-auth.tokens.TokenValidator.refresh,
  F-auth.utils.hash_password,
  F-auth.utils.generate_salt,
  ...
}
```

---

### Function-Level Partitioning (Fine)

```yaml
id: BRICK-AUTH
functions:
  - F-auth.session.authenticate
  - F-auth.session.logout
  - F-auth.tokens.validate
```

**Meaning:** Exactly these functions belong to BRICK-AUTH.

**When to use:**
- Maximum control
- Module has mixed concerns
- Refactoring existing code into bricks

**Direct specification:**
```
BRICK-AUTH = {
  F-auth.session.authenticate,
  F-auth.session.logout,
  F-auth.tokens.validate
}
```

---

## The Non-Splitting Constraint

**Bricks should never split classes. They should rarely split modules.**

### Why Not Split Classes?

A class is a cohesion boundary. Methods share private state, invariants, and purpose.

**Bad:**
```yaml
# DON'T DO THIS
BRICK-AUTH:
  functions:
    - F-auth.SessionManager.create
    - F-auth.SessionManager.validate

BRICK-SESSION:
  functions:
    - F-auth.SessionManager.destroy
    - F-auth.SessionManager.refresh
```

If methods need to be in different bricks, the class itself is poorly designed. **Refactor the class first.**

**Good:**
```yaml
# Split the class, then assign whole classes to bricks
BRICK-AUTH:
  classes:
    - C-auth.AuthManager  # create, validate

BRICK-SESSION:
  classes:
    - C-auth.SessionManager  # destroy, refresh
```

---

### Why Rarely Split Modules?

Modules are already an organizational boundary (usually). If a module needs splitting across bricks, it's often a sign the module is doing too much.

**Prefer:** Module → Brick (1:1 or N:1)

**Avoid:** Module split across multiple bricks

**Exception:** Large utility modules with mixed concerns:
```yaml
# Acceptable: utils module has truly diverse functions
BRICK-UTILS-IO:
  functions:
    - F-utils.read_file
    - F-utils.write_file

BRICK-UTILS-HASH:
  functions:
    - F-utils.hash_sha256
    - F-utils.hash_bcrypt
```

But even here, consider: should these be separate modules?

---

## Derivation Rules: Everything Follows from Partition

Once you have the partition (F → Brick assignment), everything else computes automatically.

### 1. Specs Assigned to Bricks

**Rule:** Specification S belongs to brick B if any function in B implements S.

```python
def brick_for_spec(spec_id):
    implementing_funcs = [
        f for f in functions
        if spec_id in f["implements"]
    ]

    # All implementing functions should be in same brick
    bricks = {f["brick"] for f in implementing_funcs}

    if len(bricks) == 1:
        return bricks.pop()
    elif len(bricks) == 0:
        return None  # Unimplemented spec
    else:
        # Warning: spec implemented across multiple bricks
        # This might indicate poor brick boundaries
        return bricks  # Return all bricks
```

**Example:**
```
F-auth.authenticate ∈ BRICK-AUTH
F-auth.authenticate implements S-AUTH-001
Therefore: S-AUTH-001 ∈ BRICK-AUTH
```

---

### 2. Tests Assigned to Bricks

**Rule:** Test T belongs to brick B if it primarily covers functions in B.

```python
def brick_for_test(test_id):
    covered_funcs = test["covers"]
    covered_bricks = [functions[f]["brick"] for f in covered_funcs]

    # Primary brick = most functions covered
    from collections import Counter
    brick_counts = Counter(covered_bricks)

    if brick_counts:
        primary_brick = brick_counts.most_common(1)[0][0]

        # If test covers multiple bricks significantly, it's integration
        if len(brick_counts) > 1 and brick_counts.most_common(2)[1][1] > 2:
            return None  # Integration test (no single brick)

        return primary_brick

    return None  # Test covers nothing (broken test)
```

**Example:**
```
T-test_auth.test_login covers {F-auth.authenticate, F-auth.create_session}
F-auth.authenticate ∈ BRICK-AUTH
F-auth.create_session ∈ BRICK-AUTH
Therefore: T-test_auth.test_login ∈ BRICK-AUTH
```

---

### 3. Brick Dependencies

**Rule:** Brick B₁ depends on brick B₂ if any function in B₁ calls any function in B₂.

```python
def compute_brick_dependencies(bricks):
    deps = {brick: set() for brick in bricks}

    for func in functions.values():
        source_brick = func["brick"]

        for called_func_id in func["calls"]:
            if called_func_id in functions:
                target_brick = functions[called_func_id]["brick"]

                if source_brick != target_brick:
                    deps[source_brick].add(target_brick)

    return deps
```

**Example:**
```
F-auth.authenticate ∈ BRICK-AUTH
F-auth.authenticate calls F-utils.hash
F-utils.hash ∈ BRICK-UTILS

Therefore: BRICK-AUTH depends on BRICK-UTILS
```

---

### 4. Public API

**Rule:** Function F in brick B is public if it's called from outside B.

```python
def compute_public_api(brick_id):
    brick_functions = [f for f in functions.values() if f["brick"] == brick_id]

    public_api = set()

    for func in functions.values():
        if func["brick"] != brick_id:  # Function outside brick
            for called_func_id in func["calls"]:
                if called_func_id in [f["id"] for f in brick_functions]:
                    public_api.add(called_func_id)

    return public_api
```

**Example:**
```
F-cli.login ∈ BRICK-CLI
F-cli.login calls F-auth.authenticate
F-auth.authenticate ∈ BRICK-AUTH

Therefore: F-auth.authenticate ∈ BRICK-AUTH.public_api
```

**Corollary:** Functions never called from outside are private (internal implementation details).

---

### 5. Brick Metrics

All computed from the function partition:

```python
def brick_metrics(brick_id):
    funcs = [f for f in functions.values() if f["brick"] == brick_id]

    return {
        "function_count": len(funcs),
        "loc": sum(f["loc"] for f in funcs),
        "complexity": sum(f["complexity"] for f in funcs) / len(funcs),
        "spec_count": len(set(s for f in funcs for s in f["implements"])),
        "test_count": len([t for t in tests.values() if t["brick"] == brick_id]),
        "public_api_size": len(compute_public_api(brick_id)),
        "dependency_count": len(compute_brick_dependencies({brick_id})[brick_id]),
        "cohesion": compute_cohesion(funcs),
        "coupling": compute_coupling(funcs)
    }
```

Everything derived from F partition + core S-F-T edges.

---

## Discovery: Clustering F Nodes

Bricks can be discovered automatically from code structure.

### Algorithm: Modularity-Based Clustering

```python
def discover_bricks(functions):
    # 1. Build call graph (F → F edges)
    call_graph = build_call_graph(functions)

    # 2. Add import relationships (stronger signal)
    import_graph = build_import_graph(functions)

    # 3. Combine into weighted graph
    weighted_graph = combine_graphs(call_graph, import_graph, weights=(1, 3))

    # 4. Run community detection (Louvain, Leiden, or modularity clustering)
    communities = louvain_clustering(weighted_graph)

    # 5. Each community = proposed brick
    proposed_bricks = []
    for i, community in enumerate(communities):
        brick = {
            "id": f"BRICK-PROPOSED-{i}",
            "functions": community,
            "cohesion": compute_cohesion(community),
            "coupling": compute_coupling(community),
            "size": len(community)
        }
        proposed_bricks.append(brick)

    return proposed_bricks
```

**Metrics for quality:**
- **High cohesion:** Functions in same brick call each other frequently
- **Low coupling:** Functions in same brick rarely call functions in other bricks
- **Modularity score:** Standard graph metric (0-1, higher is better)

---

### Suggesting Names

```python
def suggest_brick_name(functions):
    # Heuristics:
    # 1. Common module prefix
    module_prefixes = {f["module"].split(".")[0] for f in functions}
    if len(module_prefixes) == 1:
        return f"BRICK-{module_prefixes.pop().upper()}"

    # 2. Common spec theme
    specs = {s for f in functions for s in f["implements"]}
    spec_prefixes = {s.split("-")[1] for s in specs if "-" in s}
    if len(spec_prefixes) == 1:
        return f"BRICK-{spec_prefixes.pop()}"

    # 3. Dominant verb in function names
    verbs = extract_verbs([f["name"] for f in functions])
    if verbs:
        return f"BRICK-{verbs[0].upper()}"

    # 4. Fall back to generic
    return "BRICK-PROPOSED"
```

---

### Example Discovery Session

```bash
$ jigy discover bricks

Analyzing codebase...
  Found 456 functions in 87 modules
  Building call graph... 1,247 edges
  Building import graph... 312 edges

Running Louvain clustering...
  Modularity score: 0.73 (good separation)

Discovered 8 brick proposals:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRICK-PROPOSED-1 (23 functions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Suggested name: BRICK-AUTH
Cohesion: 0.87 (high)
Coupling: 0.12 (low)
Modules: auth.session, auth.tokens, auth.validate
Functions: authenticate, logout, validate_token, ...

Specs implemented (inferred):
  S-AUTH-001, S-AUTH-002, S-AUTH-003, S-AUTH-005

Public API (inferred from calls):
  ✓ F-auth.session.authenticate (called from BRICK-CLI, BRICK-API)
  ✓ F-auth.session.logout (called from BRICK-CLI)
  • F-auth.tokens.validate (internal only)

Accept as BRICK-AUTH? [y/n/edit]
```

---

## Spec-First vs Code-First: Both Are Valid

### Code-First (Discovery)

**Common in:**
- Brownfield projects
- Prototyping
- Exploring solution space
- Refactoring existing code

**Workflow:**
1. Write functions (implement solution)
2. Discover brick boundaries (cluster functions)
3. Document intent (write specs to explain what you built)
4. Write tests (verify behavior)

**The specs capture the implicit understanding** that existed in the developer's head while coding.

---

### Spec-First (Design)

**Common in:**
- Regulated industries (medical, finance, aerospace)
- Large team coordination
- AI-assisted development
- Safety-critical systems
- Contract-driven development

**Workflow:**
1. Write specs (document requirements)
2. Design bricks (architectural boundaries)
3. Implement functions (satisfy specs)
4. Write tests (verify specs)

**The specs are explicit requirements** before any code exists.

---

### The AI Agent Shift

With AI agents as coding assistants, **spec-first becomes more practical:**

**Before (human-only):**
- Writing detailed specs feels like bureaucracy
- Specs drift from implementation
- Developers want to "just code"

**With AI agents:**
- Specs are executable instructions for agents
- "Implement S-AUTH-001" → agent generates code
- Specs don't drift (they're the input, code is output)
- Specs provide agent boundaries (don't implement more than spec says)

**The Alignment Graph supports both workflows:**

```yaml
# Spec-first: Define brick intent, agent fills in functions
id: BRICK-AUTH
specs: [S-AUTH-001, S-AUTH-002, S-AUTH-003]
functions: []  # Agent will implement

# Code-first: Functions exist, specs added later
id: BRICK-AUTH
functions: [F-auth.authenticate, F-auth.logout]
specs: []  # Will be written to document intent
```

**In both cases, the brick is still just a partition of F.**

The difference is: Do functions or specs get created first?

---

### Hybrid: Iterative Refinement

Most real projects iterate:

1. **Sketch:** Write rough specs, identify major bricks
2. **Prototype:** Implement some functions, see what emerges
3. **Refine:** Adjust brick boundaries based on coupling/cohesion
4. **Document:** Write specs for what actually works
5. **Verify:** Write tests for specs
6. **Repeat:** Add features, refactor bricks as needed

**Bricks evolve.** The partition is not static.

---

## Brick Definition Format

Given the above, brick definitions are minimal:

### Option 1: Module-Level (Simplest)

```yaml
id: BRICK-AUTH
name: Authentication & Session Management
modules:
  - auth.session
  - auth.tokens
  - auth.validate
```

**Expands to all functions in these modules.**

---

### Option 2: Class-Level (More Control)

```yaml
id: BRICK-AUTH
name: Authentication & Session Management
classes:
  - auth.session.SessionManager
  - auth.tokens.TokenValidator
modules:
  - auth.utils  # Helper functions
```

**Expands to all methods in these classes plus all functions in auth.utils.**

---

### Option 3: Function-Level (Maximum Control)

```yaml
id: BRICK-AUTH
name: Authentication & Session Management
functions:
  - auth.session.authenticate
  - auth.session.logout
  - auth.tokens.validate
  - auth.tokens.refresh
```

**Explicit list. No expansion.**

---

### Option 4: Mixed (Practical)

```yaml
id: BRICK-AUTH
name: Authentication & Session Management
modules:
  - auth.session  # Entire module
classes:
  - auth.tokens.TokenValidator  # Just this class from auth.tokens
functions:
  - auth.utils.hash_password  # Just this function from utils
```

**Most expressive.** Allows coarse and fine control.

---

## Validation Rules

### 1. Partition Constraint

**Every function must belong to exactly one brick.**

```python
def validate_partition(bricks, functions):
    brick_assignments = {}

    for brick in bricks:
        for func_id in expand_brick(brick):  # Expand M,C,F to F
            if func_id in brick_assignments:
                return f"Error: {func_id} assigned to both {brick_assignments[func_id]} and {brick['id']}"
            brick_assignments[func_id] = brick["id"]

    # Check all functions covered
    unassigned = set(functions.keys()) - set(brick_assignments.keys())
    if unassigned:
        return f"Error: {len(unassigned)} functions not assigned to any brick"

    return "Valid partition"
```

---

### 2. No Class Splitting

**All methods of a class must be in the same brick.**

```python
def validate_no_class_split(bricks):
    for class_id, methods in classes.items():
        method_bricks = {functions[m]["brick"] for m in methods}

        if len(method_bricks) > 1:
            return f"Error: Class {class_id} split across bricks {method_bricks}"

    return "No class splits"
```

---

### 3. Dependency Acyclicity (Optional)

**Brick dependency graph should be acyclic (DAG).**

```python
def validate_acyclic(brick_dependencies):
    if has_cycle(brick_dependencies):
        cycle = find_cycle(brick_dependencies)
        return f"Error: Circular dependency detected: {' → '.join(cycle)}"

    return "Acyclic"
```

This is a best practice, not a hard requirement. Cycles indicate design problems.

---

## Complete Example: From Code to Bricks

### Step 1: Code Exists

```python
# src/auth/session.py
def authenticate(user, password):
    if _check_password(user, password):
        return _create_session(user)
    return None

def logout(session_id):
    _invalidate_session(session_id)

def _check_password(user, password):
    return hash(password) == user.password_hash

def _create_session(user):
    return Session(user, expires=now() + timedelta(hours=1))

def _invalidate_session(session_id):
    sessions.delete(session_id)

# src/auth/tokens.py
class TokenValidator:
    def validate(self, token):
        return not self._is_expired(token)

    def _is_expired(self, token):
        return token.expires_at < now()

# src/utils/crypto.py
def hash(data):
    return hashlib.sha256(data.encode()).hexdigest()
```

**Functions discovered:**
```
F-auth.session.authenticate
F-auth.session.logout
F-auth.session._check_password
F-auth.session._create_session
F-auth.session._invalidate_session
F-auth.tokens.TokenValidator.validate
F-auth.tokens.TokenValidator._is_expired
F-utils.crypto.hash
```

---

### Step 2: Discover Brick Boundaries

```bash
$ jigy discover bricks

Call graph analysis:
  auth.session.authenticate → auth.session._check_password
  auth.session.authenticate → auth.session._create_session
  auth.session.logout → auth.session._invalidate_session
  auth.session._check_password → utils.crypto.hash
  auth.tokens.TokenValidator.validate → auth.tokens.TokenValidator._is_expired

Clustering...
  Cluster 1: auth.session.* (5 functions, cohesion: 0.89)
  Cluster 2: auth.tokens.TokenValidator.* (2 functions, cohesion: 0.95)
  Cluster 3: utils.crypto.* (1 function, coupling with Cluster 1: 0.2)

Proposed bricks:

BRICK-AUTH-SESSION (5 functions)
  - auth.session.authenticate
  - auth.session.logout
  - auth.session._check_password
  - auth.session._create_session
  - auth.session._invalidate_session

BRICK-AUTH-TOKENS (2 functions)
  - auth.tokens.TokenValidator.validate
  - auth.tokens.TokenValidator._is_expired

BRICK-UTILS-CRYPTO (1 function)
  - utils.crypto.hash

Merge BRICK-AUTH-SESSION + BRICK-AUTH-TOKENS → BRICK-AUTH? [y/n]
```

---

### Step 3: Accept/Refine Brick Definitions

```yaml
# bricks/auth.brick.yaml
id: BRICK-AUTH
name: Authentication & Session Management
modules:
  - auth.session
classes:
  - auth.tokens.TokenValidator

# bricks/utils.brick.yaml
id: BRICK-UTILS
name: Core Utilities
modules:
  - utils.crypto
```

**This expands to:**
```
BRICK-AUTH = {
  F-auth.session.authenticate,
  F-auth.session.logout,
  F-auth.session._check_password,
  F-auth.session._create_session,
  F-auth.session._invalidate_session,
  F-auth.tokens.TokenValidator.validate,
  F-auth.tokens.TokenValidator._is_expired
}

BRICK-UTILS = {
  F-utils.crypto.hash
}
```

---

### Step 4: Compute Derived Properties

```bash
$ jigy brick info BRICK-AUTH

BRICK-AUTH: Authentication & Session Management
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Functions: 7
  ✓ auth.session.authenticate
  ✓ auth.session.logout
  • auth.session._check_password (private)
  • auth.session._create_session (private)
  • auth.session._invalidate_session (private)
  ✓ auth.tokens.TokenValidator.validate
  • auth.tokens.TokenValidator._is_expired (private)

Public API (2 functions):
  F-auth.session.authenticate (called from: BRICK-CLI, BRICK-API)
  F-auth.session.logout (called from: BRICK-CLI)

Dependencies (1):
  BRICK-UTILS (via F-utils.crypto.hash)

Specs implemented (0):
  (No specs yet - code-first approach)

Tests covering (2):
  T-test_auth.test_successful_login
  T-test_auth.test_logout

Metrics:
  LOC: 87
  Cohesion: 0.87 (high internal coupling)
  Coupling: 0.12 (low external coupling)
  Coverage: 78%
```

**All of this computed from the F partition.**

---

### Step 5: Add Specs (Optional)

```python
# src/auth/session.py
from jig import implements

@implements("S-AUTH-001")
def authenticate(user, password):
    ...

@implements("S-AUTH-001")
def logout(session_id):
    ...
```

```bash
$ jigy brick info BRICK-AUTH

Specs implemented (1):
  S-AUTH-001: Session Management (implemented by 2 functions)
```

**Spec assignment derived from F partition + F→S edges.**

---

## Implications for Architecture Mode vs Implementation Mode

From AG002, we have two modes:

**Architecture Mode:** See brick boundaries, interfaces, dependencies
**Implementation Mode:** See inside one brick (functions, tests, specs)

With bricks as F partitions, the modes are clear:

### Architecture Mode

**What you see:**
- Brick IDs and names
- Brick dependencies (B → B)
- Brick public APIs (which F are public)
- Brick sizes (# functions, LOC)
- Specs assigned to each brick (derived from F→S)

**What you don't see:**
- Function implementations
- Private functions within bricks
- Test implementations

**Purpose:** Design and reason about system structure.

---

### Implementation Mode

**What you see (for brick B):**
- All functions F where F ∈ B (full implementations)
- All specs S implemented by any F ∈ B
- All tests T that primarily cover F ∈ B
- Public APIs of bricks B depends on

**What you don't see:**
- Functions in other bricks (except public APIs)
- Implementation details of other bricks

**Purpose:** Implement and test within architectural constraints.

---

## Integration with AG019 (Irreducible Core)

The irreducible core is S-F-T triangle:
- S (specs)
- F (functions)
- T (tests)

Bricks add one layer:
- **F → Brick** (partition assignment)

From this, everything else derives:
- S → Brick (via F→S edges)
- T → Brick (via T→F edges)
- B → B dependencies (via F→F calls across bricks)
- Public APIs (F called from outside its brick)

**Bricks don't add complexity to the core. They organize it.**

---

## Summary

**A brick is a partition of F (functions).**

That's the entire definition. Everything else follows:

1. **Defined practically:** List modules, classes, or functions
2. **Constraint:** Never split classes, rarely split modules
3. **Derived properties:**
   - Specs assigned (from F→S edges)
   - Tests assigned (from T→F edges)
   - Dependencies (from F→F calls)
   - Public API (F called from outside)
   - All metrics (computed from F properties)
4. **Discoverable:** Cluster F nodes by coupling/cohesion
5. **Validates:** Simple set operations
6. **Supports both workflows:** Code-first (discover) and spec-first (design)

**The simplicity is intentional.** Bricks are not a complex abstraction. They're just named sets of functions that help organize the irreducible S-F-T core.

---

## References

- **AG002:** Alignment Graph Whitepaper (original brick concept)
- **AG019:** Irreducible Core (S-F-T triangle)
- **Simon (1962):** "The Architecture of Complexity" (nearly decomposable systems)
- **Newman (2006):** "Modularity and community structure in networks" (clustering algorithms)

---

_Simplicity is the ultimate sophistication._
