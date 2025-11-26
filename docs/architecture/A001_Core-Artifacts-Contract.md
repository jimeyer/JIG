# A001: Core Artifacts Contract

**Status:** Accepted
**Date:** 2025-11-26
**Supersedes:** AG023, AG024

---

## Context

The jig system measures alignment between intent (specifications), implementation (code), and verification (tests). This measurement requires a precise, unambiguous contract defining the structure of all core artifacts. These artifacts form the foundation upon which all tooling, automation, and analysis are built.

Missing elements break the system. Extra elements create noise and drift. This contract defines the irreducible minimum.

---

## Core Principle

**All artifacts SHALL follow the irreducible S-F-T triangle** (from AG019):
- **S** (Specifications) - what we intend to build
- **F** (Functions) - what we actually built
- **T** (Tests) - what we actually verify

Three relationships define alignment:
- **F → S** (implements) - which functions implement which specifications
- **T → S** (verifies) - which tests verify which specifications
- **T → F** (covers) - which tests execute which functions

Everything else is derived or organizational.

---

## Decision

### 1. Core Artifacts

The system SHALL consist of exactly five core artifacts:

1. **Specification files** (`.md` with YAML frontmatter)
2. **Outcome files** (`.md` with YAML frontmatter) - OPTIONAL
3. **Brick definitions** (`bricks.yaml`, single file)
4. **@jig decorators** (in source code)
5. **Graph files** (`.ndjson`, machine-generated)

These artifacts are interdependent but acyclic: graphs SHALL be generated before brick assignment, breaking circular dependencies.

### 2. Specification Files

**Location:** `jig/specifications/S-{number}.md`

**Naming:** Specifications SHALL be named `S-001.md`, `S-002.md`, etc., using sequential numbers without domain prefixes.

**Required YAML frontmatter:**
```yaml
---
id: S-001
type: specification
---
```

**Field contract:**
- `id` (string, REQUIRED): Format SHALL be `S-{number}` (e.g., `S-001`, `S-042`)
- `type` (string, REQUIRED): Value SHALL be exactly `"specification"`

**Excluded fields:**
- `brick` - SHALL NOT be present (creates circular dependency)
- `depends_on` - SHALL NOT be present (not part of core S-F-T triangle)
- `content` - SHALL NOT be present (brittle, content stays in markdown)

**Markdown body:** SHALL be present for human and AI agent consumption. SHALL NOT be parsed by jig system.

### 3. Outcome Files (Optional)

**Location:** `jig/outcomes/O-{number}.md`

**Naming:** Outcomes SHALL be named `O-001.md`, `O-002.md`, etc.

**Status:** Outcome files are OPTIONAL. They MAY be omitted entirely.

**Required YAML frontmatter (if present):**
```yaml
---
id: O-001
type: outcome
specifies: [S-001, S-002]
---
```

**Field contract:**
- `id` (string, REQUIRED): Format SHALL be `O-{number}`
- `type` (string, REQUIRED): Value SHALL be exactly `"outcome"`
- `specifies` (array, REQUIRED): SHALL contain spec IDs this outcome decomposes into. MAY be empty `[]`.

**Excluded fields:**
- `brick` - SHALL NOT be present (same reasoning as specifications)

### 4. Brick Definitions

**Location:** `jig/bricks.yaml` (single file)

**Structure:**
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
```

**Field contract:**
- `id` (string, REQUIRED): Format SHALL be `B-{number}` (e.g., `B-001`, `B-002`)
- `name` (string, REQUIRED): Human-readable name for display
- `units` (array, REQUIRED): SHALL contain implementation graph node IDs using M-/C-/F- prefixes

**Units format:**
- `M-{module.path}` - SHALL expand to all functions in module (e.g., `M-auth.session` → all `F-auth.session.*`)
- `C-{class.path}` - SHALL expand to all methods of class (e.g., `C-auth.tokens.TokenValidator` → all `F-auth.tokens.TokenValidator.*`)
- `F-{function.path}` - SHALL reference exactly one function (e.g., `F-auth.session.authenticate`)

**Units SHALL directly reference node IDs from implementation-graph.ndjson.** This is unambiguous and foundational.

**Excluded fields:**
- `depends_on` - SHALL NOT be present (derived from implementation graph)
- `public_api` - SHALL NOT be present (derived from call graph)
- `specs` - SHALL NOT be present (derived from F→S edges)

**Constraint:** Every function in the codebase SHALL belong to exactly one brick (partition constraint).

### 5. @jig Decorators

**Purpose:** Declare explicit relationships for alignment measurement.

**@jig.implements (on functions):**
```python
@jig.implements("S-001")
def authenticate(user: str, password: str) -> Token:
    ...

@jig.implements("S-001", "S-002")
def validate_and_refresh(token: Token) -> Token:
    ...
```

**Contract:**
- SHALL use format `@jig.implements("S-{number}", ...)`
- SHALL reference spec IDs that exist in specification files
- MAY accept multiple spec IDs as separate arguments
- Functions without decorator implement no specifications (internal helpers)

**@jig.verifies (on test functions):**
```python
@jig.verifies("S-001")
def test_token_expiration():
    ...

@jig.verifies("O-001")  # May verify outcomes
def test_full_auth_flow():
    ...
```

**Contract:**
- SHALL use format `@jig.verifies("S-{number}", ...)` or `@jig.verifies("O-{number}", ...)`
- SHALL reference spec or outcome IDs that exist
- MAY accept multiple IDs as separate arguments
- Tests without decorator verify nothing (infrastructure tests)

**Excluded decorator:**
- `@jig.brick` - SHALL NOT exist (bricks.yaml is sole source of truth)

### 6. Graph Files

**Location:** `jig/generated/`

**Three graph files SHALL exist:**
```
jig/generated/intent-graph.ndjson
jig/generated/implementation-graph.ndjson
jig/generated/verification-graph.ndjson
```

**Format:** All graph files SHALL use NDJSON (Newline-Delimited JSON): one JSON object per line.

**Rationale:** NDJSON enables clean git diffs (only changed lines show), streaming processing, and grep-friendly querying.

#### 6.1 Intent Graph

**Generated from:**
- `jig/specifications/S-*.md` frontmatter
- `jig/outcomes/O-*.md` frontmatter (if present)
- `jig/bricks.yaml`

**Node types and schemas:**

**Specification Node:**
```json
{"id":"S-001","type":"specification","file":"jig/specifications/S-001.md"}
```

Fields:
- `id` (string, REQUIRED): Spec ID
- `type` (string, REQUIRED): SHALL be `"specification"`
- `file` (string, REQUIRED): Relative path to markdown file

**Outcome Node:**
```json
{"id":"O-001","type":"outcome","file":"jig/outcomes/O-001.md","specifies":["S-001","S-002"]}
```

Fields:
- `id` (string, REQUIRED): Outcome ID
- `type` (string, REQUIRED): SHALL be `"outcome"`
- `file` (string, REQUIRED): Relative path to markdown file
- `specifies` (array, REQUIRED): Array of spec IDs

**Brick Node:**
```json
{"id":"B-001","type":"brick","name":"Authentication & Session Management","file":"jig/bricks.yaml"}
```

Fields:
- `id` (string, REQUIRED): Brick ID
- `type` (string, REQUIRED): SHALL be `"brick"`
- `name` (string, REQUIRED): Human-readable name
- `file` (string, REQUIRED): Always `"jig/bricks.yaml"`

**Excluded fields:**
- `content` - SHALL NOT be present in any node
- `brick` - SHALL NOT be present on spec/outcome nodes
- `depends_on` - SHALL NOT be present on any node

#### 6.2 Implementation Graph

**Generated from:**
- Python source files (AST parsing)
- `@jig.implements` decorators

**Node schema:**

**Function Node:**
```json
{"id":"F-auth.session.authenticate","type":"function","file":"src/auth/session.py","implements":["S-001","S-002"],"calls":["F-auth.tokens.validate"]}
```

Fields:
- `id` (string, REQUIRED): Format SHALL be `F-{module.path}.{function_name}` or `F-{module.path}.{Class}.{method}`
- `type` (string, REQUIRED): SHALL be `"function"`
- `file` (string, REQUIRED): Relative path to Python file
- `implements` (array, REQUIRED): Array of spec IDs from `@jig.implements`. SHALL be empty `[]` if none.
- `calls` (array, REQUIRED): Array of function IDs this calls (from AST). SHALL be empty `[]` if none.

**Module and Class Nodes (OPTIONAL):**
MAY be included for navigation. Format: `M-{module.path}` and `C-{class.path}`.

**Excluded fields:**
- `brick` - SHALL NOT be present (breaks circular dependency)
- Line numbers - SHALL NOT be present (brittle, computable on demand)

**Critical constraint:** Implementation graph SHALL be generated BEFORE brick definitions exist. Brick assignment SHALL be computed at query time by joining bricks.yaml with graph.

#### 6.3 Verification Graph

**Generated from:**
- Test discovery (pytest, unittest)
- Coverage analysis (pytest-cov, coverage.py)
- `@jig.verifies` decorators

**Node schema:**

**Test Node:**
```json
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"covers":["F-auth.session.authenticate","F-auth.tokens.validate"]}
```

Fields:
- `id` (string, REQUIRED): Format SHALL be `T-{module}.{test_function}` or `T-{module}.{TestClass}.{test_method}`
- `type` (string, REQUIRED): SHALL be `"test"`
- `file` (string, REQUIRED): Relative path to test file
- `verifies` (array, REQUIRED): Array of spec/outcome IDs from `@jig.verifies`. SHALL be empty `[]` if none.
- `covers` (array, REQUIRED): Array of function IDs executed by this test (from coverage). SHALL be empty `[]` if none.

**Excluded fields:**
- `brick` - SHALL NOT be present (derived from covered functions)

### 7. ID Format Contract

All IDs SHALL follow these formats:

| Type | Format | Example | Notes |
|------|--------|---------|-------|
| Specification | `S-{number}` | `S-001`, `S-042` | Sequential numbering |
| Outcome | `O-{number}` | `O-001`, `O-003` | Sequential numbering |
| Brick | `B-{number}` | `B-001`, `B-002` | Sequential numbering |
| Function | `F-{path}` | `F-auth.session.authenticate` | Fully-qualified path |
| Module | `M-{path}` | `M-auth.session` | Module path |
| Class | `C-{path}` | `C-auth.tokens.TokenValidator` | Fully-qualified class path |
| Test | `T-{path}` | `T-test_auth.test_token_expiration` | Test path |

**Human-authored IDs** (S-, O-, B-) SHALL use sequential numbers without domain prefixes.

**Code-derived IDs** (M-, C-, F-, T-) SHALL use fully-qualified paths from code structure.

### 8. File Structure Contract

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
│   └── generated/              # Machine-generated, separate directory
│       ├── intent-graph.ndjson
│       ├── implementation-graph.ndjson
│       └── verification-graph.ndjson
├── src/
│   └── [source code with @jig.implements decorators]
└── tests/
    └── [test code with @jig.verifies decorators]
```

**Separation contract:**
- Human-authored artifacts SHALL reside in `jig/specifications/`, `jig/outcomes/`, and `jig/bricks.yaml`
- Machine-generated artifacts SHALL reside in `jig/generated/`
- This separation SHALL be maintained for clarity

### 9. Derivation Contract

The following data SHALL be computed on demand, NOT stored:

**Derived from implementation graph:**
- Brick dependencies (B-001 depends on B-003 if any F in B-001 calls any F in B-003)
- Public APIs (F is public if called from outside its brick)
- Brick assignments for functions (computed by expanding bricks.yaml units)

**Derived from graphs:**
- Brick assignments for tests (derived from covered functions)
- Coverage percentages (computed from T→F edges)
- Alignment metrics (computed from S-F-T triangle queries)
- All statistics, aggregations, health scores

**Rationale:** Stored derived data drifts from source of truth. Compute on demand ensures freshness.

### 10. Validation Contract

Implementations SHALL validate:

1. **ID uniqueness:** All spec IDs, outcome IDs, and brick IDs SHALL be unique within their type
2. **Reference integrity:** All `@jig.implements` SHALL reference existing spec IDs
3. **Reference integrity:** All `@jig.verifies` SHALL reference existing spec/outcome IDs
4. **Reference integrity:** All outcome `specifies` SHALL reference existing spec IDs
5. **Brick partition:** Every function SHALL belong to exactly one brick (no overlaps, no gaps)
6. **No class splitting:** All methods of a class SHALL belong to the same brick
7. **Unit prefix validity:** All brick units SHALL start with M-, C-, or F- (extensible for other languages)
8. **Unit existence:** All brick units SHALL reference nodes that exist in implementation graph

### 11. Language Extension Contract

**Current:** Python implementation using M- (modules), C- (classes), F- (functions)

**Future languages:** SHALL extend by adding new prefixes:
- **P-** for packages (Go, Java)
- **K-** for crates (Rust)
- Additional prefixes as needed per language

**Constraint:** All language extensions SHALL use the same pattern: `{Prefix}-{path}` directly referencing implementation graph nodes.

---

## Consequences

### What This Enables

1. **Unambiguous foundation:** All tooling builds on precise, well-defined contracts
2. **No circular dependencies:** Graphs generated independently, bricks defined separately, assignment computed at query time
3. **Minimal maintenance:** Only store what cannot be computed; derive everything else
4. **Clean git diffs:** NDJSON format, minimal required fields, no derived data
5. **Language extensibility:** Foundation supports multiple languages via prefix extension
6. **Tool automation:** Machine-readable contracts enable code generation, validation, analysis

### What This Constrains

1. **No additional fields:** Artifacts SHALL NOT include fields beyond this contract (eliminates drift)
2. **No manual brick assignment:** Functions SHALL NOT specify their brick (bricks.yaml is sole source)
3. **No derived data storage:** Metrics SHALL NOT be stored in graphs (computed on demand)
4. **No domain prefixes:** IDs SHALL use sequential numbers, not semantic names
5. **Single brick file:** All bricks SHALL be defined in one `bricks.yaml` file
6. **NDJSON only:** Graph files SHALL use NDJSON, not pretty-printed JSON

### Migration Path

Existing projects adopting jig SHALL follow:
1. Create specification files with minimal frontmatter
2. Generate implementation graph (no brick assignments)
3. Define bricks in bricks.yaml using M-/C-/F- references
4. Add @jig.implements decorators to code
5. Add @jig.verifies decorators to tests
6. Generate all graphs
7. Validate partition and references

---

## Compliance

All future work SHALL comply with this contract. Deviations SHALL require explicit architectural decision superseding this document.

Tools, automation, and analysis SHALL treat this contract as normative and immutable.

---

## References

- **AG019:** Irreducible Core (S-F-T triangle)
- **AG020:** Bricks as Partitions
- **AG024:** Core Artifacts Contract (Refined) - detailed rationale
