# SCOPE: Verification Graph Implementation

- **SCOPE**: A001 (Core Artifacts Contract), J017 (JIG Concept v9), AG016 (Feasibility Analysis)
- **Start**: 2025-12-08
- **Status**: Draft
- **Branch**: verification-graph

## Context

The JIG system measures alignment via the S-F-T triangle:
- **Intent Graph** (S, O, B nodes) — implemented via `jigy intent rebuild`
- **Implementation Graph** (F nodes, F→S edges) — implemented via `jigy impl rebuild`
- **Verification Graph** (T nodes, T→S edges) — **NOT YET IMPLEMENTED**

The verification graph completes the triangle by tracking:
- Which tests verify which specifications (T→S via `@jig.verifies`)

**Important Simplification:** T→F coverage edges are NOT part of the verification graph. Coverage analysis is handled by the Audit system (J023, J024, J026). This keeps the verification graph purely static (no test execution required).

**Verification graph node schema:**

```json
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"jig_hash":"a1b2c3d4e5f6"}
```

**Key properties:**
- `id`: Format `T-{module}.{test_function}` or `T-{module}.{TestClass}.{test_method}`
- `verifies`: Array of spec/outcome IDs from `@jig.verifies` decorator
- `jig_hash`: Content hash per S-047 (same algorithm as functions)

**NOT included (handled by Audit system):**
- `covers`: T→F coverage edges are recorded in audit-log.ndjson, not in the verification graph

---

## Goals

1. **Complete the S-F-T triangle** — Enable T→S alignment queries
2. **Track verification intent** — Capture which tests claim to verify which specs
3. **Support audit triggers** — T→S edge changes trigger re-audit (per J023)
4. **Match existing patterns** — Follow implementation-graph architecture (builder, visitor, NDJSON writer)
5. **Update A001 contract** — Remove `covers` field from verification graph schema

---

## Constraints

### From AG016 (Feasibility Analysis)

1. **Static-only**: Test discovery and `@jig.verifies` extraction are purely static (no test execution)
2. **Determinism**: Output must be deterministic for same inputs (alphabetical ordering)
3. **Performance target**: <2s for static analysis (discovery + decorator extraction)

### From A001 (Core Artifacts Contract) — TO BE UPDATED

1. **Location**: `jig/generated/verification-graph.ndjson`
2. **Format**: NDJSON (one JSON object per line)
3. **Excluded fields**: `brick` (derived at query time), line numbers (brittle), `covers` (moved to Audit)
4. **Required fields**: `id`, `type`, `file`, `verifies`, `jig_hash`

### From J023/J024/J026 (Audit Architecture)

1. **T→F coverage is Audit domain**: Coverage edges live in audit-log.ndjson, not verification-graph
2. **Verification graph is static**: No test execution, no coverage instrumentation

---

## Non-Goals

1. **T→F coverage edges** — Handled by Audit system (J023), not verification graph
2. **Running tests** — Verification graph is purely static analysis
3. **Coverage collection** — Out of scope; Audit system responsibility
4. **Flaky test detection** — Out of scope
5. **Incremental rebuild** — Full rebuild only for V1
6. **Multi-framework support** — Python/pytest only for V1

---

## Architecture Overview

```
tests/              jig/specifications/
    │                       │
    ▼                       ▼
┌─────────────────┐   ┌─────────────────┐
│ Test Discovery  │   │ Intent Graph    │
│ (find test_*.py)│   │ (S nodes)       │
└────────┬────────┘   └────────┬────────┘
         │                     │
         ▼                     │
┌─────────────────┐            │
│ Test Analyzer   │            │
│ - Parse tests   │            │
│ - @jig.verifies │            │
│ - jig_hash      │            │
└────────┬────────┘            │
         │                     │
         ▼                     ▼
┌─────────────────────────────────────────┐
│          Verification Graph             │
│         T nodes + T→S edges             │
│    (T→F coverage handled by Audit)      │
└─────────────────────────────────────────┘
         │
         ▼
jig/generated/verification-graph.ndjson
```

---

## Code Reuse Strategy

The verification graph is **dramatically simpler** than the implementation graph because:

1. **No structural analysis** — Just need test functions, not modules/classes/inheritance
2. **No call graph** — Just decorator → spec edges
3. **Single edge type** — Only T→S (verifies), not imports/calls/extends/contains
4. **Simple discovery** — Standard test patterns, not general source files

### Reusability Summary

| Category | Component | Reuse | Notes |
|----------|-----------|-------|-------|
| Core Infrastructure | `Graph` class | 100% | Completely generic |
| | `NDJSONWriter` | 100% | Completely generic |
| | `write_ndjson()` | 100% | Generic wrapper |
| Hashing | `compute_hash()` | 100% | Generic |
| | `hash_function()` | 100% | Works for test functions |
| | `hash_test()` | 100% | Already exists |
| Builder Pattern | `GraphBuilder` | 90% | Same pattern, different defaults |
| Registry | `AnalyzerRegistry` | 100% | Can register test analyzer |
| Base Classes | `LanguageAnalyzer` | 95% | Minor interface extension |
| Decorator Extraction | `_extract_implements_decorators` | 95% | Clone for `@jig.verifies` |

### Architecture Decision: Import from impl_graph (No Refactoring)

```
src/jig/
├── impl_graph/              # Existing (unchanged)
│   ├── graph.py            # Import Graph from here
│   ├── ndjson_writer.py    # Import write_ndjson from here
│   └── ...
│
└── verification_graph/      # NEW
    ├── __init__.py
    ├── builder.py          # Import Graph, write_ndjson from impl_graph
    ├── discovery.py        # Test-specific discovery (~50 lines)
    └── analyzer.py         # Simple test analyzer (~100 lines)
```

**Rationale:** Simpler approach — no moving files, no breaking existing imports. Verification graph simply imports shared components from impl_graph.

### Lines of Code Estimate

| Category | Existing Lines | New Lines Needed |
|----------|----------------|------------------|
| 100% Reusable | ~420 lines | 0 |
| 90% Reusable | ~440 lines | ~20 lines |
| New Code | — | ~200 lines |
| **Total New Code** | — | **~220 lines** |

---

## Known Intent (To Create in WU0)

### Outcome

**O-018: Test Alignment Tracking**
- Track which tests verify which specifications
- Enable detection of verification gaps (unverified specs)

### Specifications

| ID | Name | Description |
|----|------|-------------|
| S-051 | Test Discovery | Find all test files and test functions in tests/ directory |
| S-052 | Test Node Schema | T node format (NO covers field — that's Audit domain) |
| S-053 | @jig.verifies Extraction | Parse T→S edges from `@jig.verifies` decorators |
| S-054 | Test Hashing | Compute jig_hash for test functions (uses S-047) |
| S-055 | Verification Graph Generation | Generate verification-graph.ndjson |
| S-056 | CLI jigy verify rebuild | CLI command to trigger verification graph generation |
| S-057 | A001 Contract Update | Remove `covers` field from verification graph schema |

### Brick

**B-verification-graph** (new brick, layer 1)
- Depends on: B-hashing (layer 0)
- Units: `M-jig.verification_graph`

---

## Work Unit Checklist

- [ ] WU0: Create Intent nodes (O/S) and update A001
- [ ] WU1: Test Discovery — tests / code / docs
- [ ] WU2: Test Analyzer (parse + @jig.verifies) — tests / code / docs
- [ ] WU3: Verification Graph Builder — tests / code / docs
- [ ] WU4: CLI Integration — tests / code / docs

---

## Work Units

### Work Unit 0: Create Known Intent + Update A001

**Goal**: Capture all verification graph requirements as O/S nodes, and update A001 to remove `covers` field from verification graph schema.

**Implements**: S-057

**Acceptance Criteria**:
- [ ] O-018 created for test alignment tracking
- [ ] S-051 through S-057 created for verification graph specs
- [ ] A001 updated: verification graph schema no longer includes `covers` field
- [ ] All files have proper YAML frontmatter
- [ ] `jigy validate intent` passes

**Actions**:

1. **Update A001** (`docs/architecture/A001_Core-Artifacts-Contract.md`):
   - Remove `covers` field from verification graph test node schema
   - Add note that T→F coverage is handled by Audit system (J023)
   - Update the node schema example

2. Create `jig/outcomes/O-018.md`:
```markdown
---
id: O-018
type: outcome
specifies: [S-051, S-052, S-053, S-054, S-055, S-056, S-057]
---

# Test Alignment Tracking

Track which tests verify which specifications, enabling detection of verification gaps and supporting audit triggers.

**Value**: Completes the S-F-T triangle, enabling queries like "which specs have no verifying tests?"

**Acceptance Criteria**:
- Tests with @jig.verifies decorators are discovered
- T→S edges are captured in verification graph
- Test functions have content hashes for change detection
- T→F coverage is handled separately by Audit system (not in verification graph)
```

3. Create specifications S-051 through S-057 (see detailed specs in sections below)

4. Update `jig/bricks.yaml` to add B-verification-graph brick

**A001 Changes** (Section 6.3 Verification Graph):

Before:
```json
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"covers":["F-auth.session.authenticate","F-auth.tokens.validate"]}
```

After:
```json
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"jig_hash":"a1b2c3d4e5f6"}
```

**Rationale for A001 change:**
- T→F coverage requires test execution (dynamic analysis)
- Verification graph should be purely static (no test runs needed)
- Coverage audits are recorded in audit-log.ndjson per J023/J026
- This simplifies the verification graph and clarifies responsibilities

---

### Work Unit 1: Test Discovery

**Goal**: Create test file discovery that finds all test files and parses test functions.

**Implements**: S-051

**Reuses**: Standard library only (`pathlib.rglob`). Simpler than impl_graph discovery since test patterns are well-defined.

**Est. New Code**: ~50 lines

**Acceptance Criteria**:
- [ ] Discovers test files matching `test_*.py` and `*_test.py` patterns
- [ ] Finds test functions (`def test_*`) and test methods (`class Test*`)
- [ ] Respects `tests/` directory convention (configurable)
- [ ] Returns structured list of test file paths with test function metadata
- [ ] Unit tests verify discovery patterns

**New Files**:
- `src/jig/verification_graph/__init__.py`
- `src/jig/verification_graph/discovery.py`
- `tests/verification_graph/test_discovery.py`

**Key Functions**:

```python
def discover_test_files(
    project_root: Path,
    test_dir: Optional[Path] = None,  # defaults to tests/
    exclude_patterns: Optional[List[str]] = None,
) -> List[Path]:
    """Discover all test files in project."""

def discover_tests(
    test_files: List[Path],
) -> List[TestInfo]:
    """Discover test functions/methods from test files."""
```

**TestInfo Structure**:
```python
@dataclass
class TestInfo:
    id: str           # T-test_auth.test_login
    file: Path        # tests/unit/test_auth.py
    name: str         # test_login
    class_name: Optional[str]  # TestAuth (if method)
    line: int         # 42
```

---

### Work Unit 2: Test Analyzer (Parse + @jig.verifies)

**Goal**: Create AST-based test analyzer that extracts `@jig.verifies` decorators.

**Implements**: S-052, S-053, S-054

**Reuses**:
- `hash_function()` from `hashing.py` (100% reuse)
- `_extract_implements_decorators()` pattern from `python_visitor.py` (clone & modify)
- `_validate_spec_id()` from `python_visitor.py` (100% reuse)

**Est. New Code**: ~100 lines (vs. PythonAnalyzer's ~480 lines)

**Acceptance Criteria**:
- [ ] Parses test files with AST (mirrors python_visitor.py pattern)
- [ ] Extracts `@jig.verifies("S-001")` decorators
- [ ] Handles multiple specs: `@jig.verifies("S-001", "S-002")`
- [ ] Handles short form: `@verifies("S-001")` (if imported)
- [ ] Computes jig_hash using existing `hash_function()` from hashing.py
- [ ] Validates spec ID format (S-NNN or O-NNN)
- [ ] Unit tests verify extraction from various patterns

**New Files**:
- `src/jig/verification_graph/analyzer.py`
- `tests/verification_graph/test_analyzer.py`
- `tests/fixtures/python/test_with_verifies.py` (fixture)

**Key Functions**:

```python
class TestAnalyzer:
    def analyze_file(self, file_path: Path) -> dict:
        """Analyze test file and return test nodes with verifies edges."""
        return {
            "nodes": [...],  # T nodes
            "edges": [...],  # T→S edges (verifies)
        }
```

**Test Node Schema** (per updated A001):
```python
{
    "id": "T-test_auth.test_token_expiration",
    "type": "test",
    "file": "tests/unit/test_auth.py",
    "verifies": ["S-001"],  # From @jig.verifies
    "jig_hash": "a1b2c3d4e5f6",  # Content hash
}
```

**Note:** No `covers` field — T→F coverage is handled by Audit system (J023).

---

### Work Unit 3: Verification Graph Builder

**Goal**: Create graph builder that orchestrates discovery, analysis, and NDJSON output.

**Implements**: S-055

**Reuses**:
- `Graph` class from `impl_graph/graph.py` (100% reuse)
- `NDJSONWriter` from `impl_graph/ndjson_writer.py` (100% reuse)
- `write_ndjson()` from `impl_graph/ndjson_writer.py` (100% reuse)
- `GraphBuilder` pattern (follow pattern, don't import)

**Est. New Code**: ~40 lines (thin orchestration layer)

**Acceptance Criteria**:
- [ ] Orchestrates discovery → analysis → serialization
- [ ] Generates `jig/generated/verification-graph.ndjson`
- [ ] Matches implementation-graph builder pattern
- [ ] Deterministic output (sorted by test ID)
- [ ] Includes metadata line with node/edge counts
- [ ] Integration tests verify end-to-end

**New Files**:
- `src/jig/verification_graph/builder.py`
- `tests/verification_graph/test_builder.py`

**Key Functions**:

```python
from jig.impl_graph.graph import Graph

@jig.implements("S-055")
def build_verification_graph(
    project_root: Path,
    test_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
    exclude_patterns: Optional[List[str]] = None,
    include_timestamp: bool = True,
) -> Graph:
    """Build verification graph from test files.

    Returns the existing Graph class — no new dataclass needed.
    """
```

**VerificationGraph Structure** (uses existing `Graph` class):
```python
from jig.impl_graph.graph import Graph
from jig.impl_graph.ndjson_writer import write_ndjson

# No new dataclass needed — use Graph directly
graph = Graph()
graph.add_node({"id": "T-...", "type": "test", ...})
graph.add_edge({"source": "T-...", "target": "S-...", "type": "verifies"})

# Write using existing infrastructure
write_ndjson(graph, output_path, include_timestamp=True)
```

**NDJSON Output**:
```json
{"_meta":{"version":"1.0","node_count":42,"edge_count":87,"generated":"2025-12-08T..."}}
{"id":"T-test_auth.test_login","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"jig_hash":"a1b2c3d4e5f6"}
{"source":"T-test_auth.test_login","target":"S-001","type":"verifies"}
```

**Note:** No T→F edges — coverage is recorded in audit-log.ndjson per J023.

---

### Work Unit 4: CLI Integration

**Goal**: Add `jigy verify rebuild` command and integrate with `jigy rebuild`.

**Implements**: S-056

**Reuses**:
- CLI patterns from `src/jig/cli/main.py` (follow existing structure)
- `impl` subcommand as template for `verify` subcommand

**Est. New Code**: ~30 lines

**Acceptance Criteria**:
- [ ] `jigy verify rebuild` generates verification-graph.ndjson
- [ ] `jigy rebuild` includes verification graph generation
- [ ] Supports `--test-dir` to specify test directory
- [ ] Supports `--skip-validation` flag
- [ ] Supports `--no-timestamp` for deterministic testing
- [ ] CLI tests verify command behavior

**Modified Files**:
- `src/jig/cli/main.py` — Add verify subcommand
- `src/jig/cli/verify.py` — New file for verify commands

**CLI Commands**:

```bash
# Generate verification graph only
jigy verify rebuild [--test-dir TESTS/] [--skip-validation] [--no-timestamp]

# Full rebuild (now includes verification)
jigy rebuild  # adds step 5: verification graph
```

**Output Example**:
```
$ jigy verify rebuild
[1] Discovering tests...
    Found 42 test files
[2] Analyzing test functions...
    Found 320 tests
    Found 87 @jig.verifies edges
[3] Writing verification-graph.ndjson...
    Wrote 320 nodes, 87 edges

Verification graph written to: jig/generated/verification-graph.ndjson
```

---

## Specification Details

### S-051: Test Discovery

```markdown
---
id: S-051
type: specification
---

# Test Discovery

The verification graph builder MUST discover all test files and test functions.

**Acceptance Criteria:**
- Discovers files matching `test_*.py` and `*_test.py` patterns
- Default test directory is `tests/` (configurable)
- Discovers `def test_*()` functions and `class Test*` methods
- Excludes `__pycache__`, `.venv`, and other noise directories
- Returns deterministic ordering (alphabetical by path)

**Rationale:** Test discovery is the foundation of verification tracking.
```

### S-052: Test Node Schema

```markdown
---
id: S-052
type: specification
---

# Test Node Schema

Test nodes in the verification graph MUST conform to the A001 contract.

**Required Fields:**
- `id` (string): Format `T-{module}.{test_function}` or `T-{module}.{TestClass}.{test_method}`
- `type` (string): Value SHALL be `"test"`
- `file` (string): Relative path to test file
- `verifies` (array): Spec/outcome IDs from `@jig.verifies`, empty if none
- `jig_hash` (string): Content hash per S-047

**Excluded Fields:**
- `brick` — derived at query time
- `line` — brittle, computable on demand
- `covers` — T→F coverage is handled by Audit system (J023), not verification graph

**Rationale:** Consistent schema enables tooling and queries. Coverage is a separate concern.
```

### S-053: @jig.verifies Extraction

```markdown
---
id: S-053
type: specification
---

# @jig.verifies Decorator Extraction

Test analyzer MUST extract T→S edges from `@jig.verifies` decorators.

**Acceptance Criteria:**
- Parses `@jig.verifies("S-001")`
- Parses `@jig.verifies("S-001", "S-002", "S-003")`
- Parses `@verifies("S-001")` (short form, if imported)
- Validates spec ID format: `^[SO]-\d+$`
- Logs warning for invalid spec IDs (does not fail)
- Tests without decorator have empty `verifies` array

**Rationale:** T→S edges are the primary verification relationship.
```

### S-054: Test Hashing

```markdown
---
id: S-054
type: specification
---

# Test Hashing

Test functions MUST have content hashes computed using S-047 (AST-based hashing).

**Acceptance Criteria:**
- Uses same algorithm as S-046/S-047 (hash_function)
- Excludes decorators from hash
- Normalizes formatting (AST unparse)
- Hash changes when test logic changes
- Hash stable across whitespace/comment changes

**Rationale:** Hash enables change detection for audit triggers (J023).
```

### S-055: Verification Graph Generation

```markdown
---
id: S-055
type: specification
---

# Verification Graph Generation

Generate `jig/generated/verification-graph.ndjson` from test analysis.

**Acceptance Criteria:**
- Output is NDJSON (one JSON object per line)
- First line is metadata: `{"_meta": {...}}`
- Nodes sorted alphabetically by ID
- Edges sorted by (source, target, type)
- Deterministic output for same input
- Includes all T nodes and T→S edges

**Rationale:** NDJSON enables clean git diffs and streaming processing.
```

### S-056: CLI jigy verify rebuild

```markdown
---
id: S-056
type: specification
---

# CLI: jigy verify rebuild

CLI command to generate verification graph.

**Usage:**
```bash
jigy verify rebuild [--test-dir TESTS/] [--skip-validation] [--no-timestamp]
```

**Behavior:**
- Discovers tests in specified directory (default: tests/)
- Parses @jig.verifies decorators
- Generates jig/generated/verification-graph.ndjson
- Prints summary (node count, edge count)

**Integration:**
- `jigy rebuild` includes verification graph as step 5

**Rationale:** CLI parity with impl and intent commands.
```

### S-057: A001 Contract Update

```markdown
---
id: S-057
type: specification
---

# A001 Contract Update for Verification Graph

Update A001 (Core Artifacts Contract) to reflect that T→F coverage is handled by the Audit system, not the verification graph.

**Changes to A001:**

1. **Section 6.3 Verification Graph:**
   - Remove `covers` field from test node schema
   - Add `jig_hash` field to test node schema
   - Add note that T→F edges are recorded in audit-log.ndjson

2. **Updated Test Node Schema:**
```json
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"jig_hash":"a1b2c3d4e5f6"}
```

3. **Add Excluded Fields:**
   - `covers` — T→F coverage is handled by Audit system (J023, J024, J026)

**Rationale:**
- Verification graph should be purely static (no test execution required)
- T→F coverage requires running tests with coverage instrumentation
- Separation of concerns: verification-graph tracks T→S intent, audit-log tracks T→F coverage
- Simplifies verification graph generation and reduces coupling

**References:**
- J023: Audit Records and Triggers (T→F edges in audit-log.ndjson)
- J024: Audit Report Format (coverage report format)
- J026: Audit Architecture Simplification (design rationale)
```

---

## Testing Strategy

### Unit Tests

| Component | Test File | Key Tests |
|-----------|-----------|-----------|
| Discovery | `test_discovery.py` | File patterns, exclusions, ordering |
| Analyzer | `test_analyzer.py` | Decorator extraction, edge cases, hashing |
| Builder | `test_builder.py` | End-to-end, NDJSON format, determinism |

### Integration Tests

| Test | Description |
|------|-------------|
| `test_cli.py` | CLI commands work end-to-end |
| `test_full_rebuild.py` | `jigy rebuild` includes verification graph |
| `test_round_trip.py` | Generate → load → verify structure |

### Fixtures

Create `tests/fixtures/python/test_with_verifies.py`:
```python
import jig

@jig.verifies("S-001")
def test_simple():
    assert True

@jig.verifies("S-001", "S-002")
def test_multiple_specs():
    assert True

class TestWithClass:
    @jig.verifies("S-003")
    def test_method(self):
        assert True

def test_no_decorator():
    """Test without @jig.verifies - should have empty verifies array."""
    assert True
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Test discovery misses edge cases | Medium | Medium | Comprehensive fixtures, real-world testing on JIG |
| AST parsing fails on complex tests | Low | High | Fall back to file-level discovery, log warnings |
| Performance regression | Low | Medium | Benchmark against implementation graph |
| Decorator validation too strict | Medium | Low | Warn on invalid, don't fail |

---

## Dependencies

### 100% Reusable (Import Directly)

| Component | Location | Lines | Purpose |
|-----------|----------|-------|---------|
| `Graph` | `src/jig/impl_graph/graph.py` | 93 | Node/edge storage, add/get methods |
| `NDJSONWriter` | `src/jig/impl_graph/ndjson_writer.py` | 142 | Deterministic NDJSON output |
| `write_ndjson()` | `src/jig/impl_graph/ndjson_writer.py` | — | Convenience wrapper |
| `hash_function()` | `src/jig/hashing.py` | — | AST-based content hashing |
| `hash_test()` | `src/jig/hashing.py` | — | Test function hashing |
| `compute_hash()` | `src/jig/hashing.py` | — | Generic hash computation |
| `AnalyzerRegistry` | `src/jig/impl_graph/analyzers/registry.py` | 176 | Analyzer registration |
| `ParseError` | `src/jig/impl_graph/analyzers/base.py` | 19 | Error handling |

### 95% Reusable (Clone & Modify)

| Component | Location | Lines | Modification Needed |
|-----------|----------|-------|---------------------|
| `_extract_implements_decorators()` | `python_visitor.py:345` | ~60 | Change `implements` → `verifies` |
| `_validate_spec_id()` | `python_visitor.py` | ~10 | Use as-is |

### Patterns to Follow (Don't Import, Match Style)

| Pattern | Location | Purpose |
|---------|----------|---------|
| `GraphBuilder` | `src/jig/impl_graph/builder.py` | Builder orchestration pattern |
| `LanguageAnalyzer` | `src/jig/impl_graph/analyzers/base.py` | Analyzer interface |
| CLI subcommands | `src/jig/cli/main.py` | Command structure |

### New Code (~220 lines)

| Component | Est. Lines | Description |
|-----------|------------|-------------|
| `discovery.py` | ~50 | Test file discovery (test_*.py patterns) |
| `analyzer.py` | ~100 | Simple test analyzer (much smaller than PythonAnalyzer) |
| `builder.py` | ~40 | Thin builder using Graph + NDJSONWriter |
| `cli/verify.py` | ~30 | CLI integration |

### External Dependencies

None — uses standard library (`ast`, `pathlib`) and existing JIG modules only.

---

## Success Criteria

1. **Functional**: `jigy verify rebuild` generates valid verification-graph.ndjson
2. **Complete**: All tests with `@jig.verifies` decorators are captured
3. **Correct**: T→S edges match decorator arguments
4. **Deterministic**: Same codebase produces identical output
5. **Integrated**: `jigy rebuild` includes verification step
6. **Tested**: >80% coverage on new code
7. **A001 Updated**: Contract updated to reflect no `covers` field in verification graph

---

## Timeline Estimate

| Work Unit | Complexity | Est. Time | Code Reuse Impact |
|-----------|------------|-----------|-------------------|
| WU0: Intent + A001 update | Low | 1 hour | N/A (documentation) |
| WU1: Discovery | Low | 1 hour | Simple patterns (~50 lines) |
| WU2: Analyzer | Medium | 2 hours | Clone decorator extraction (~100 lines) |
| WU3: Builder | Low | 1 hour | Import Graph + NDJSONWriter (~40 lines) |
| WU4: CLI | Low | 1 hour | Follow existing CLI patterns (~30 lines) |

**Revised Total**: ~6 hours (down from 10-14 hours)

**Why Faster:**
- 100% reuse of Graph, NDJSONWriter, hashing infrastructure (~420 lines)
- TestAnalyzer is ~100 lines vs PythonAnalyzer's ~480 lines
- No structural analysis (modules, classes, inheritance)
- No call graph or complex edge types
- Single decorator to extract (`@jig.verifies`)

---

## References

- **A001**: Core Artifacts Contract — verification-graph.ndjson schema (TO BE UPDATED)
- **J017**: JIG Concept v9 — S-F-T triangle, verification relationships
- **J023**: Audit Records and Triggers — T→S edge change detection; T→F coverage in audit-log
- **J024**: Audit Report Format — coverage report format
- **J026**: Audit Architecture Simplification — T→F as Audit domain, not verification graph
- **AG016**: Verification Graph Feasibility — determinism, performance analysis
- **S-047**: Test Hashing via AST — hash algorithm for tests
- **B008**: Content Hashing Plan — pattern for work unit structure
- **B010_code_reuse.md**: Code sharing analysis — detailed breakdown of reusable components
