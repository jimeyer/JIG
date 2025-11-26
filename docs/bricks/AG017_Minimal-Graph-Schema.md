# Minimal Alignment Graph Schema

_Git-Inspired Minimal Representation_

**Date:** 2025-11-25
**Status:** Proposal
**Related:** AG002 (Alignment Graph Whitepaper), AG014 (Implementation & Verification Graphs)

---

## Philosophy: Like Git, Store Only What You Can't Derive

Git's object model is minimal:
- Objects are content-addressed
- Metadata is sparse (author, timestamp, message)
- Relationships are pointers (parent commits, tree hashes)
- **Zero derived data** - all stats computed on demand from objects

The Alignment Graph should follow the same principle:
- Store only **discovered structure** and **explicit declarations**
- No metrics, no aggregations, no summaries
- All statistics, health scores, drift indicators → computed on demand
- Relationships are ID pointers, not duplicated data

---

## Human-Authored Artifacts vs. Machine-Generated Graphs

**Human authors write:**
- Outcome and Specification markdown files (in `jig/` directory)
- Brick definition files (`bricks/*.brick.yaml`)
- `@jig` decorators on code and tests

**Machine generates:**
- `intent-graph.json` (from markdown frontmatter + brick definitions)
- `implementation-graph.json` (from code + `@jig.implements` decorators)
- `verification-graph.json` (from tests + coverage + `@jig.verifies` decorators)

**All three graphs are derived from observable facts, not manually maintained.**

---

## The Three Files

```
jig/
  intent-graph.json           # Generated from markdown + brick definitions
  implementation-graph.json   # Generated from code + decorators
  verification-graph.json     # Generated from tests + coverage
```

**Separation rationale:**
1. **Intent** changes when design documents or brick definitions change
2. **Implementation** changes when code is edited
3. **Verification** changes when tests run

Keeping them separate allows regenerating each independently.

**No line numbers:** Functions are identified by fully-qualified ID (`F-module.path.function_name`), not by line number. Line numbers are computed on-demand when navigating to code (via AST search or grep). This prevents unnecessary git churn when code is edited.

---

## Human-Authored Input: Minimal Requirements

### Outcome Markdown File

**File:** `jig/outcomes/auth.md`

**Minimal YAML frontmatter:**
```yaml
---
id: O-AUTH-001
type: outcome
brick: BRICK-AUTH
specifies: [S-AUTH-001, S-AUTH-002]
---

# Authentication Without Passwords

Users can authenticate securely without managing passwords...
```

**Required fields:**
- `id`: Unique identifier (format: `O-<SUBSYSTEM>-<NUM>`)
- `type`: "outcome"
- `brick`: Brick ID this outcome belongs to
- `specifies`: Array of Specification IDs (optional, can be empty)

**Body:** Markdown explanation (not parsed into graph, for human reading)

---

### Specification Markdown File

**File:** `jig/specs/auth.md`

**Minimal YAML frontmatter:**
```yaml
---
id: S-AUTH-001
type: specification
brick: BRICK-AUTH
depends_on: []
---

# Token Expiration

Authentication tokens expire after 15 minutes of inactivity.
```

**Required fields:**
- `id`: Unique identifier (format: `S-<SUBSYSTEM>-<NUM>`)
- `type`: "specification"
- `brick`: Brick ID this spec belongs to
- `depends_on`: Array of Specification IDs this depends on (optional, can be empty)

**Body:** Markdown explanation (not parsed into graph)

---

### Brick Definition File

**File:** `bricks/auth.brick.yaml`

**Minimal YAML:**
```yaml
id: BRICK-AUTH
name: Authentication & Session Management
depends_on:
  - BRICK-UTILS
public_api:
  - F-auth.session.authenticate
  - F-auth.session.logout
```

**Required fields:**
- `id`: Unique identifier (format: `BRICK-<NAME>`)
- `name`: Human-readable name
- `depends_on`: Array of Brick IDs this brick may depend on (empty if none)
- `public_api`: Array of function/class IDs exposed as public interface (optional)

---

### @jig Decorator on Code

**File:** `src/auth/session.py`

```python
from jig import implements

@implements("S-AUTH-001", "S-AUTH-002")
def authenticate(user: str, password: str) -> Token:
    """Authenticate user and return token."""
    ...

@implements("S-AUTH-001")
def logout(token: Token) -> None:
    """Invalidate the given token."""
    ...
```

**Syntax:**
```python
@jig.implements("SPEC-ID-1", "SPEC-ID-2", ...)
def function_name(...):
    ...
```

**Or using alternate import:**
```python
from jig import implements

@implements("S-AUTH-001")
def authenticate(...):
    ...
```

**This decorator tells the implementation-graph generator:**
- This function implements the given specifications
- Creates `implements` edges from function → specs

---

### @jig Decorator on Tests

**File:** `tests/unit/test_auth.py`

```python
from jig import verifies

@verifies("S-AUTH-001")
def test_token_expiration():
    """Verify tokens expire after 15 minutes."""
    token = authenticate("user", "pass")
    time.sleep(901)  # 15 min + 1 sec
    assert is_expired(token)

@verifies("S-AUTH-002")
def test_rate_limiting():
    """Verify failed logins are rate-limited."""
    for _ in range(5):
        authenticate("user", "wrong")

    with pytest.raises(RateLimitError):
        authenticate("user", "wrong")
```

**Syntax:**
```python
@jig.verifies("SPEC-ID-1", "SPEC-ID-2", ...)
def test_function_name(...):
    ...

# Or for outcome verification:
@jig.verifies("O-AUTH-001")
def test_end_to_end_auth_flow():
    ...
```

**This decorator tells the verification-graph generator:**
- This test verifies the given specifications/outcomes
- Creates `verifies` edges from test → intent nodes

---

### Optional: Subsystem Grouping File

**File:** `jig/subsystems.yaml` (optional)

```yaml
subsystems:
  - id: SUBSYS-CORE
    name: Core Infrastructure
    contains:
      - BRICK-AUTH
      - BRICK-UTILS

  - id: SUBSYS-CLI
    name: Command Line Interface
    contains:
      - BRICK-CLI
      - BRICK-COMMANDS
```

If not provided, subsystems can be inferred from brick organization or omitted entirely.

---

## 1. intent-graph.json (Machine-Generated)

### Minimal Schema

```json
{
  "nodes": {
    "O-AUTH-001": {
      "type": "outcome",
      "content": "Users can authenticate securely without passwords",
      "file": "jig/outcomes/auth.md",
      "specifies": ["S-AUTH-001", "S-AUTH-002"],
      "brick": "BRICK-AUTH"
    },
    "S-AUTH-001": {
      "type": "specification",
      "content": "Authentication tokens expire after 15 minutes of inactivity",
      "file": "jig/specs/auth.md",
      "depends_on": [],
      "brick": "BRICK-AUTH"
    },
    "S-AUTH-002": {
      "type": "specification",
      "content": "Failed login attempts are rate-limited",
      "file": "jig/specs/auth.md",
      "depends_on": ["S-AUTH-001"],
      "brick": "BRICK-AUTH"
    },
    "BRICK-AUTH": {
      "type": "brick",
      "name": "Authentication & Session Management",
      "file": "bricks/auth.brick.yaml",
      "depends_on": ["BRICK-UTILS"],
      "public_api": [
        "F-auth.session.authenticate",
        "F-auth.session.logout"
      ]
    },
    "SUBSYS-CORE": {
      "type": "subsystem",
      "name": "Core Infrastructure",
      "contains": ["BRICK-AUTH", "BRICK-UTILS"]
    }
  }
}
```

### Required Fields

**Outcome Node:**
- `type`: "outcome"
- `content`: The outcome statement (what value we're delivering)
- `file`: Source location (for traceability)
- `specifies`: Array of Specification IDs this outcome refines to
- `brick`: Brick ID (assignment)

**Specification Node:**
- `type`: "specification"
- `content`: The specification statement (testable requirement)
- `file`: Source location
- `depends_on`: Array of Specification IDs this depends on
- `brick`: Brick ID (assignment)

**Brick Node:**
- `type`: "brick"
- `name`: Human-readable name
- `file`: Brick definition file
- `depends_on`: Array of Brick IDs this brick may depend on
- `public_api`: Array of code node IDs exposed as public interface

**Subsystem Node:**
- `type`: "subsystem"
- `name`: Human-readable name
- `contains`: Array of Brick IDs

### Relationship Direction

Edges point **forward** (from abstract to concrete, from dependency to dependent):
- Outcome → Specification (`specifies`)
- Specification → Specification (`depends_on`)
- Brick → Brick (`depends_on`)
- Subsystem → Brick (`contains`)

Reverse traversal (e.g., "which Outcomes lead to S-AUTH-001?") requires graph traversal, like git.

---

## 2. implementation-graph.json

### Minimal Schema

```json
{
  "nodes": {
    "M-auth.session": {
      "type": "module",
      "file": "src/auth/session.py",
      "brick": "BRICK-AUTH",
      "imports": ["M-auth.tokens", "M-utils.time"],
      "contains": ["F-auth.session.authenticate", "F-auth.session.logout"]
    },
    "C-auth.tokens.TokenValidator": {
      "type": "class",
      "file": "src/auth/tokens.py",
      "brick": "BRICK-AUTH",
      "contains": ["F-auth.tokens.TokenValidator.validate"]
    },
    "F-auth.session.authenticate": {
      "type": "function",
      "file": "src/auth/session.py",
      "brick": "BRICK-AUTH",
      "implements": ["S-AUTH-001", "S-AUTH-002"],
      "calls": ["F-auth.tokens.validate", "F-utils.time.now"]
    },
    "F-auth.tokens.validate": {
      "type": "function",
      "file": "src/auth/tokens.py",
      "brick": "BRICK-AUTH",
      "implements": ["S-AUTH-001"],
      "calls": []
    },
    "M-external:jwt": {
      "type": "external",
      "package": "pyjwt"
    }
  }
}
```

### Required Fields

**Module Node:**
- `type`: "module"
- `file`: File path (relative to project root)
- `brick`: Brick ID (assignment)
- `imports`: Array of module IDs (internal + external)
- `contains`: Array of class/function IDs defined in this module

**Class Node:**
- `type`: "class"
- `file`: File path
- `brick`: Brick ID
- `contains`: Array of method IDs (functions belonging to this class)

**Function Node:**
- `type`: "function" (includes methods)
- `file`: File path
- `brick`: Brick ID
- `implements`: Array of Intent node IDs (Outcomes/Specs this implements)
- `calls`: Array of function IDs this function calls

**External Module Node:**
- `type`: "external"
- `package`: Package name (e.g., "pyjwt", "networkx")

### Why No Line Numbers?

Line numbers are **brittle** - they change whenever code above is edited. This creates unnecessary diff churn in git.

**Problem scenario:**
```python
# Someone adds 3 imports at top of file
import logging  # NEW
import typing   # NEW
import dataclasses  # NEW

# This function didn't change at all, but line number shifts
def authenticate(...):  # Was line 45, now line 48
    ...
```

With line numbers stored, the graph shows a "change" even though the function is identical. Git shows unnecessary diffs.

**Solution:**
- **For navigation**: Run AST search when needed (`ast.parse()` to find symbol)
- **For uniqueness**: The fully-qualified ID is already unique
- **For display**: Compute line numbers on demand (like `git blame`)

**Example workflow:**
```bash
# User clicks on F-auth.session.authenticate in visualization
# Tool runs:
$ grep -n "def authenticate" src/auth/session.py
48:def authenticate(...)

# Shows current line number without storing it in graph
```

The graph stores the **identity** of the function, not its **location**.

### Relationship Direction

Edges point **forward** (from caller to callee, from importer to imported):
- Module → Module (`imports`)
- Module → Class/Function (`contains`)
- Class → Method (`contains`)
- Function → Function (`calls`)
- Function → Intent (`implements`)

### Discovery Method

Generated by static analysis:
1. Parse all Python files with AST
2. Extract module, class, function definitions
3. Extract import statements → `imports` edges
4. Extract function calls (where determinable) → `calls` edges
5. Parse `@jig.implements("S-*", "O-*")` decorators → `implements` edges
6. Assign to bricks (from `@jig.brick("BRICK-ID")` decorator or from brick definition file)

**Optional: Explicit brick assignment:**
```python
from jig import implements, brick

@brick("BRICK-AUTH")
@implements("S-AUTH-001")
def authenticate(...):
    ...
```

If `@brick` is not present, assignment is determined from brick definition's file path patterns or inferred from imports.

---

## 3. verification-graph.json

### Minimal Schema

```json
{
  "nodes": {
    "T-test_auth.test_token_expiration": {
      "type": "test",
      "file": "tests/unit/test_auth.py",
      "brick": "BRICK-AUTH",
      "covers": ["F-auth.session.authenticate", "F-auth.tokens.validate"],
      "verifies": ["S-AUTH-001"]
    },
    "T-test_auth.test_rate_limiting": {
      "type": "test",
      "file": "tests/unit/test_auth.py",
      "brick": "BRICK-AUTH",
      "covers": ["F-auth.session.authenticate"],
      "verifies": ["S-AUTH-002"]
    },
    "T-test_integration.TestAuthFlow": {
      "type": "test_class",
      "file": "tests/integration/test_integration.py",
      "brick": null,
      "contains": ["T-test_integration.TestAuthFlow.test_full_login"]
    },
    "T-test_integration.TestAuthFlow.test_full_login": {
      "type": "test",
      "file": "tests/integration/test_integration.py",
      "brick": null,
      "covers": [
        "F-auth.session.authenticate",
        "F-auth.session.logout",
        "F-auth.tokens.validate"
      ],
      "verifies": ["O-AUTH-001"]
    }
  }
}
```

### Required Fields

**Test Function Node:**
- `type`: "test"
- `file`: Test file path
- `brick`: Brick ID (null for integration tests spanning multiple bricks)
- `covers`: Array of code node IDs executed by this test (from coverage analysis)
- `verifies`: Array of Intent node IDs this test verifies (from `@jig.verifies` decorator)

**Test Class Node:**
- `type`: "test_class"
- `file`: Test file path
- `brick`: Brick ID (or null)
- `contains`: Array of test method IDs

### Relationship Direction

Edges point **forward** (from test to code, from test to intent):
- Test → Code (`covers`)
- Test → Intent (`verifies`)
- TestClass → TestMethod (`contains`)

### Discovery Method

Generated by test discovery + coverage:
1. Discover tests (pytest, unittest)
2. Run coverage analysis (pytest-cov, coverage.py)
3. Parse test files to extract test functions/classes
4. Map coverage data to code nodes → `covers` edges
5. Parse `@jig.verifies("S-*", "O-*")` decorators → `verifies` edges
6. Assign to bricks (from `@jig.brick("BRICK-ID")` decorator or inferred from covered code)

**Optional: Explicit brick assignment:**
```python
from jig import verifies, brick

@brick("BRICK-AUTH")
@verifies("S-AUTH-001")
def test_token_expiration():
    ...
```

If `@brick` is not present, assignment is inferred from the code being covered.

---

## Node ID Conventions

**Intent Nodes:**
- `O-<SUBSYSTEM>-<NUM>` - Outcome (e.g., `O-AUTH-001`)
- `S-<SUBSYSTEM>-<NUM>` - Specification (e.g., `S-AUTH-002`)
- `BRICK-<NAME>` - Brick (e.g., `BRICK-AUTH`)
- `SUBSYS-<NAME>` - Subsystem (e.g., `SUBSYS-CORE`)

**Implementation Nodes:**
- `M-<module.path>` - Module (e.g., `M-auth.session`)
- `C-<module.path>.<ClassName>` - Class (e.g., `C-auth.tokens.TokenValidator`)
- `F-<module.path>.<function_name>` - Function (e.g., `F-auth.session.authenticate`)
- `F-<module.path>.<Class>.<method>` - Method (e.g., `F-auth.tokens.TokenValidator.validate`)
- `M-external:<package>` - External module (e.g., `M-external:jwt`)

**Verification Nodes:**
- `T-<test_module>.<test_name>` - Test function (e.g., `T-test_auth.test_token_expiration`)
- `T-<test_module>.<TestClass>` - Test class (e.g., `T-test_auth.TestAuthFlow`)
- `T-<test_module>.<TestClass>.<method>` - Test method (e.g., `T-test_auth.TestAuthFlow.test_login`)

---

## What's Excluded (Computed on Demand)

The following are **NOT** stored in the graphs, but computed when needed:

### Excluded from All Graphs
- Timestamps (use git for this)
- Metadata (project name, description)
- Totals/counts (total nodes, total edges)
- Health scores

### Excluded from Intent Graph
- "Implemented by" reverse edges (traverse implementation-graph)
- "Verified by" reverse edges (traverse verification-graph)
- Completion percentages
- Drift indicators

### Excluded from Implementation Graph
- LOC (lines of code) - compute from files
- Cyclomatic complexity - compute from AST
- Fan-in/fan-out metrics - compute from edges
- Coupling scores - compute from edges
- Boundary violations - compute by checking edges against brick dependencies
- Reverse call graph (who calls this function) - traverse forward edges

### Excluded from Verification Graph
- Coverage percentages - compute from `covers` edges + code LOC
- Branch coverage - run coverage tool on demand
- Test counts - count nodes
- Drift indicators (untested code, unverified specs) - compute from cross-graph queries
- Test ratios - compute from node counts

---

## Computing Derived Data (Examples)

### Coverage Percentage for a Function

```python
# NOT stored in graph:
"coverage_percent": 87.5

# Computed on demand:
def compute_coverage(function_id):
    tests = [t for t in verification_graph if function_id in t['covers']]
    if not tests:
        return 0.0
    # Run coverage tool to get exact line coverage
    return run_coverage_analysis(tests, function_id)
```

### Boundary Violations

```python
# NOT stored in graph:
"boundary_violations": [...]

# Computed on demand:
def find_violations():
    violations = []
    for func_id, func in implementation_graph.items():
        func_brick = func['brick']
        allowed_bricks = get_brick_dependencies(func_brick)

        for called_id in func['calls']:
            called_brick = implementation_graph[called_id]['brick']
            if called_brick not in allowed_bricks:
                violations.append({
                    'from': func_id,
                    'to': called_id,
                    'brick_violation': f"{func_brick} -> {called_brick}"
                })
    return violations
```

### Unverified Specifications

```python
# NOT stored in graph:
"unverified_specs": [...]

# Computed on demand:
def find_unverified_specs():
    all_specs = [id for id, node in intent_graph.items() if node['type'] == 'specification']
    verified_specs = set()

    for test_id, test in verification_graph.items():
        verified_specs.update(test['verifies'])

    return [s for s in all_specs if s not in verified_specs]
```

---

## Graph Regeneration Commands

### Rebuild Intent Graph
```bash
jigy index
# Scans jig/ directory for Outcome/Spec markdown files
# Parses YAML frontmatter from each file
# Loads brick definitions from bricks/*.brick.yaml
# Loads subsystem definitions from jig/subsystems.yaml (if present)
# Builds relationships (outcome → specs, brick → brick, subsystem → bricks)
# Writes intent-graph.json
```

**What triggers rebuild:**
- New/modified/deleted `.md` files in `jig/`
- Changes to brick definition files
- Changes to subsystem definitions

---

### Rebuild Implementation Graph
```bash
jigy impl rebuild
# Scans src/ for Python files
# Parses AST for modules, classes, functions, imports, calls
# Extracts @jig.implements("S-*") decorators → implements edges
# Extracts @jig.brick("BRICK-*") decorators → brick assignments
# Assigns functions to bricks (from decorator or brick file path patterns)
# Writes implementation-graph.json
```

**What triggers rebuild:**
- Code changes (new/modified/deleted `.py` files)
- New/modified `@jig.implements` decorators
- New/modified `@jig.brick` decorators

---

### Rebuild Verification Graph
```bash
jigy verify rebuild --run-tests
# Discovers tests (pytest)
# Runs coverage analysis (pytest-cov)
# Parses test files for @jig.verifies("S-*", "O-*") decorators
# Extracts @jig.brick("BRICK-*") decorators from tests
# Maps coverage data to code nodes → covers edges
# Maps @jig.verifies to intent nodes → verifies edges
# Writes verification-graph.json
```

**What triggers rebuild:**
- Test code changes
- New/modified `@jig.verifies` decorators
- Test execution (coverage data changes)

---

### Compute All Metrics
```bash
jigy status
# Loads all three graphs
# Computes alignment metrics on-the-fly
# Displays health, drift, violations
# NO persistent metric storage
```

---

## Cross-Graph Queries

All alignment queries traverse the three graphs:

### Query: "Which specs are implemented but not verified?"

```python
# 1. Get all specs
specs = {id: node for id, node in intent_graph.items()
         if node['type'] == 'specification'}

# 2. Find implemented specs (from implementation-graph)
implemented = set()
for func in implementation_graph.values():
    implemented.update(func.get('implements', []))

# 3. Find verified specs (from verification-graph)
verified = set()
for test in verification_graph.values():
    verified.update(test.get('verifies', []))

# 4. Compute difference
implemented_not_verified = implemented - verified
```

### Query: "Impact analysis - what breaks if I change this function?"

```python
def impact_analysis(function_id):
    # 1. Find direct callers (implementation-graph)
    callers = [f for f in implementation_graph.values()
               if function_id in f.get('calls', [])]

    # 2. Find indirect callers (transitive closure)
    indirect = compute_transitive_callers(function_id)

    # 3. Find affected tests (verification-graph)
    affected_tests = [t for t in verification_graph.values()
                      if function_id in t.get('covers', [])]

    # 4. Find affected specs (intent-graph via implementation-graph)
    affected_specs = set()
    for func in callers + indirect:
        affected_specs.update(func.get('implements', []))

    return {
        'direct_callers': callers,
        'indirect_callers': indirect,
        'affected_tests': affected_tests,
        'affected_specs': list(affected_specs)
    }
```

---

## Comparison: Minimal vs. Full Schema (AG014)

| Data | AG014 (Full) | AG017 (Minimal) | Rationale |
|------|--------------|-----------------|-----------|
| Node IDs | ✓ | ✓ | Essential |
| Node types | ✓ | ✓ | Essential |
| File paths | ✓ | ✓ | Essential (traceability) |
| Line numbers | ✓ | ✗ | Brittle - compute via AST search |
| Relationships | ✓ | ✓ | Essential (graph structure) |
| Brick assignments | ✓ | ✓ | Essential (boundaries) |
| Timestamps | ✓ | ✗ | Derivable from git |
| LOC counts | ✓ | ✗ | Derivable from files |
| Complexity metrics | ✓ | ✗ | Computable from AST |
| Coverage percentages | ✓ | ✗ | Computable from coverage tool |
| Boundary violations | ✓ | ✗ | Computable from edges |
| Drift indicators | ✓ | ✗ | Computable from queries |
| Health scores | ✓ | ✗ | Computable from metrics |
| Metadata summaries | ✓ | ✗ | Computable from node counts |

**File size reduction:** ~70% smaller (estimated)

**Trade-off:** Compute metrics on demand vs. store pre-computed

---

## Benefits of Minimal Schema

1. **Smaller files** - Faster to load, parse, diff
2. **No stale data** - Metrics always fresh (computed on demand)
3. **Simpler regeneration** - Only store observable facts, not derived stats
4. **Git-friendly** - Minimal diffs when code changes
5. **Clear separation** - Structure vs. metrics
6. **Extensible** - Add new metrics without changing schema

---

## When to Compute vs. Store

**Store:**
- Observable facts (code structure, decorators, file locations)
- Explicit relationships (imports, calls, implements, verifies)
- Human declarations (brick assignments, intent content)

**Compute on demand:**
- Aggregations (totals, averages, percentages)
- Derived relationships (reverse edges, transitive closures)
- Health scores, drift indicators, violations
- Any metric that can be calculated from stored data

**Rule of thumb:** If git doesn't store it, neither should we.

---

## Implementation Strategy

### Phase 1: Minimal Graph Generation
1. Implement minimal schema writers (intent, impl, verify)
2. No metrics, no aggregations
3. Store only structure + relationships

### Phase 2: On-Demand Metrics
1. Implement metric computation functions
2. `jigy status` computes all metrics fresh
3. `jigy impl status` computes boundary violations on-the-fly
4. `jigy verify status` runs coverage analysis on demand

### Phase 3: Caching (Optional)
1. Cache computed metrics in memory during session
2. Invalidate cache when graphs regenerate
3. Never persist cached metrics to disk

---

## Example: Minimal vs. Full

### AG014 (Full Schema)
```json
{
  "metadata": {
    "generated": "2025-11-25T12:00:00Z",
    "total_modules": 87,
    "total_functions": 456,
    "total_loc": 12141
  },
  "nodes": [{
    "id": "F-auth.session.authenticate",
    "type": "function",
    "file": "src/auth/session.py",
    "line": 45,
    "loc": 67,
    "cyclomatic_complexity": 8,
    "parameter_count": 2,
    "calls": ["F-auth.tokens.validate"],
    "implements": ["S-AUTH-001"],
    "brick": "BRICK-AUTH"
  }],
  "metrics": {
    "average_cyclomatic": 5.2,
    "max_cyclomatic": 24
  },
  "boundary_violations": [...]
}
```

### AG017 (Minimal Schema)
```json
{
  "nodes": {
    "F-auth.session.authenticate": {
      "type": "function",
      "file": "src/auth/session.py",
      "brick": "BRICK-AUTH",
      "implements": ["S-AUTH-001"],
      "calls": ["F-auth.tokens.validate"]
    }
  }
}
```

**Size:** 2,847 bytes → 265 bytes (91% reduction for this node)

All metrics (LOC, complexity, averages, violations) computed when running `jigy status`.

---

## Complete Example: From Markdown to Graphs

### Human writes (source of truth):

**jig/outcomes/auth.md:**
```markdown
---
id: O-AUTH-001
type: outcome
brick: BRICK-AUTH
specifies: [S-AUTH-001, S-AUTH-002]
---
# Authentication Without Passwords
Users can authenticate securely without managing passwords.
```

**jig/specs/auth.md:**
```markdown
---
id: S-AUTH-001
type: specification
brick: BRICK-AUTH
depends_on: []
---
# Token Expiration
Authentication tokens expire after 15 minutes of inactivity.
```

**bricks/auth.brick.yaml:**
```yaml
id: BRICK-AUTH
name: Authentication & Session Management
depends_on: [BRICK-UTILS]
public_api:
  - F-auth.session.authenticate
```

**src/auth/session.py:**
```python
from jig import implements

@implements("S-AUTH-001", "S-AUTH-002")
def authenticate(user: str, password: str) -> Token:
    """Authenticate user."""
    ...
```

**tests/unit/test_auth.py:**
```python
from jig import verifies

@verifies("S-AUTH-001")
def test_token_expiration():
    """Verify tokens expire."""
    ...
```

---

### Machine generates:

**jig/intent-graph.json:**
```json
{
  "nodes": {
    "O-AUTH-001": {
      "type": "outcome",
      "content": "Authentication Without Passwords",
      "file": "jig/outcomes/auth.md",
      "brick": "BRICK-AUTH",
      "specifies": ["S-AUTH-001", "S-AUTH-002"]
    },
    "S-AUTH-001": {
      "type": "specification",
      "content": "Token Expiration",
      "file": "jig/specs/auth.md",
      "brick": "BRICK-AUTH",
      "depends_on": []
    },
    "BRICK-AUTH": {
      "type": "brick",
      "name": "Authentication & Session Management",
      "file": "bricks/auth.brick.yaml",
      "depends_on": ["BRICK-UTILS"],
      "public_api": ["F-auth.session.authenticate"]
    }
  }
}
```

**jig/implementation-graph.json:**
```json
{
  "nodes": {
    "F-auth.session.authenticate": {
      "type": "function",
      "file": "src/auth/session.py",
      "brick": "BRICK-AUTH",
      "implements": ["S-AUTH-001", "S-AUTH-002"],
      "calls": []
    }
  }
}
```

**jig/verification-graph.json:**
```json
{
  "nodes": {
    "T-test_auth.test_token_expiration": {
      "type": "test",
      "file": "tests/unit/test_auth.py",
      "brick": "BRICK-AUTH",
      "verifies": ["S-AUTH-001"],
      "covers": ["F-auth.session.authenticate"]
    }
  }
}
```

**All three graphs generated from observable facts:**
- Markdown frontmatter
- Brick definitions
- `@jig` decorators
- Code structure (AST)
- Test coverage

---

## Conclusion

The minimal schema stores only:
1. **Node identity** (id, type, location)
2. **Explicit relationships** (edges as ID arrays)
3. **Human declarations** (via frontmatter and decorators)

**All graphs are machine-generated from human-authored artifacts:**
- Intent graph ← Markdown files + brick definitions
- Implementation graph ← Code + `@jig.implements` decorators
- Verification graph ← Tests + coverage + `@jig.verifies` decorators

Everything else is **computed from these primitives**, like git computes stats from commits.

This keeps the graphs:
- Small and fast to load
- Git-friendly (minimal diffs)
- Free from stale metrics
- Simple to regenerate
- Easy to extend

**Next step:** Implement minimal graph builders for all three graphs, then build metric computation layer on top.
