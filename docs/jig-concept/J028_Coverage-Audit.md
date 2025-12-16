# J028: Coverage Audit

**Status:** Proposal
**Date:** 2025-12-16
**Extends:** J026 (Audit Architecture Simplification)
**Part of:** J026 T→F audit support

---

## Context

The JIG audit system (J026) defines three edge types in the S-F-T triangle:

| Edge | Meaning | Audit Method |
|------|---------|--------------|
| F→S | Function implements spec | Agent review (J025) |
| T→S | Test verifies spec | Agent review (J025) |
| T→F | Test covers function | **Coverage analysis** |

F→S and T→S audits require judgment—an agent reads code and specs to determine alignment. T→F audits are different: they're determined by **code execution**. Running tests with coverage instrumentation produces objective T→F data.

**This document defines how JIG collects and records T→F coverage data.**

### Why Coverage is an "Audit"

The three fast graphs (intent, implementation, verification) are built by parsing source files—no execution required. Coverage is different:

1. **Slow** — Requires running the test suite with coverage instrumentation
2. **Execution-dependent** — Results depend on runtime behavior, not just source
3. **Ephemeral source data** — Raw coverage data is intermediate; the audit log is the record

Coverage fits the audit model: collect evidence, make a determination, record the result.

### Design Goals

1. **Simple T→F edges** — Binary "covered" or "not_covered" per test/function pair
2. **Mid-altitude granularity** — "Did test T execute ≥1 line of function F?"
3. **Grep-able report** — One T→F pair per line for easy filtering
4. **Ephemeral raw data** — Discard `.coverage` after processing; audit log is source of truth
5. **J026 compatible** — T→F edges use the standard audit log schema

---

## Decision

### 1. Command: `jigy audit coverage`

Per A002 (CLI Command Architecture), coverage audit uses verb-first with noun subcommand:

```bash
jigy audit coverage    # Run coverage analysis, record T→F edges
```

**Behavior:**
1. Run test suite with coverage instrumentation
2. Parse coverage data to extract T→F relationships
3. Write T→F edges to `jig/audits/audit-log.ndjson`
4. Write human-readable report to `jig/audits/audit-coverage-YYYY-MM-DD.md`
5. Discard raw coverage data

**Exit codes:**
- 0: Coverage analysis completed successfully
- 1: Test failures or coverage collection error
- 2: Usage error

---

### 2. T→F Edge Definition

A T→F edge exists when **test T executed at least one line of function F**.

This is binary:
- `covered` — Test executed ≥1 line of the function
- `not_covered` — Test did not execute any lines of the function

**What we track:**
- Test T (identified by `T-{module}.{test_name}`)
- Function F (identified by `F-{module}.{function_name}`)
- The relationship: T covers F (or doesn't)

**What we don't track (in this scope):**
- Line-level detail (which specific lines)
- Branch coverage (which branches taken)
- Coverage percentage per function

This is a solid mid-altitude first pass. More granular tooling can be built on top.

---

### 3. Audit Log Schema (per J026)

T→F edges are recorded in `jig/audits/audit-log.ndjson` using the J026 schema:

```json
{
  "edge": "T→F",
  "git_commit": "abc1234",
  "from": {
    "id": "T-test_auth.test_login",
    "jig_hash": "a1b2c3d4e5f6"
  },
  "to": {
    "id": "F-auth.authenticate",
    "jig_hash": "b2c3d4e5f6a7"
  },
  "report": {
    "result": "covered",
    "confidence": 1.0,
    "method": "pytest-cov",
    "file": "audit-coverage-2025-12-16.md"
  }
}
```

**Field notes:**
- `edge`: Always `"T→F"` for coverage audits
- `git_commit`: Current HEAD at audit time
- `from.id`: Test node ID (matches verification graph)
- `from.jig_hash`: Test's content hash (from J022)
- `to.id`: Function node ID (matches implementation graph)
- `to.jig_hash`: Function's content hash (from J022)
- `report.result`: `"covered"` or `"not_covered"`
- `report.confidence`: Always `1.0` (coverage is deterministic)
- `report.method`: `"pytest-cov"` (or other coverage tool)
- `report.file`: Path to human-readable report

---

### 4. Report Format

The report is stored at `jig/audits/audit-coverage-YYYY-MM-DD.md`.

**Design principle:** One T→F pair per line, grep-able.

```markdown
# Coverage Audit Report

**Date:** 2025-12-16T14:32:00Z
**Commit:** abc1234
**Method:** pytest-cov
**Tests:** 89
**Functions:** 312
**T→F edges:** 847

---

T-test_auth.test_login: F-auth.authenticate
T-test_auth.test_login: F-auth.validate_token
T-test_auth.test_login: F-auth.hash_password
T-test_auth.test_logout: F-auth.invalidate_session
T-test_auth.test_logout: F-auth.clear_cookie
T-test_crdt.test_merge: F-crdt.lww.merge
T-test_crdt.test_merge: F-crdt.lww.timestamp_compare
T-test_crdt.test_converge: F-crdt.lww.merge
T-test_crdt.test_converge: F-crdt.primitives.deep_merge
...
```

**Usage:**
```bash
# What does test_login cover?
grep "T-test_auth.test_login:" jig/audits/audit-coverage-*.md

# What tests cover authenticate?
grep "F-auth.authenticate$" jig/audits/audit-coverage-*.md

# Count edges
wc -l < jig/audits/audit-coverage-2025-12-16.md

# Diff between runs
diff audit-coverage-2025-12-15.md audit-coverage-2025-12-16.md
```

**Sorting:** Lines are sorted by test ID (T), then by function ID (F).

---

### 5. Raw Coverage Data Lifecycle

Raw coverage data (`.coverage` file, JSON exports) is **ephemeral**:

```
[pytest --cov]  →  [.coverage]  →  [parse T→F]  →  [audit-log.ndjson]
                       ↓                              ↓
                  (discard)                     (source of truth)
```

**Rationale:**
- Raw coverage data is large and redundant once T→F edges are extracted
- The audit log is the canonical record
- Like `pytest --cov` overwrites `.coverage` each run, we don't accumulate raw data
- If more granular data is needed later, re-run coverage

---

### 6. Coverage Collection Strategy

**Default implementation (pytest-cov):**

```bash
# Internal to jigy audit coverage
pytest \
    --cov=src \
    --cov-context=test \
    --cov-report= \
    test/
```

**Key flags:**
- `--cov=src`: Cover the source directory
- `--cov-context=test`: Track which test covers which lines (critical for T→F)
- `--cov-report=`: Suppress default report (we generate our own)

**Extracting T→F from coverage data:**

```python
def extract_tf_edges(coverage_data: CoverageData) -> list[tuple[str, str]]:
    """
    Extract T→F edges from coverage data.

    Returns list of (test_id, function_id) pairs where test covered function.
    """
    edges = []

    for context in coverage_data.contexts():
        # context is like "test_auth.py::test_login"
        test_id = context_to_test_id(context)

        for file, lines in coverage_data.lines(context):
            # Map covered lines to function nodes
            functions = lines_to_functions(file, lines, impl_graph)
            for func_id in functions:
                edges.append((test_id, func_id))

    return dedupe(edges)
```

---

### 7. Integration with Existing Graphs

Coverage audit requires the implementation graph to exist (to map lines → functions):

```
jigy rebuild impl     # Must exist first
jigy audit coverage   # Uses impl graph to resolve F nodes
```

**Dependency:** `jig/generated/implementation-graph.ndjson` must be current.

**Node ID matching:**
- Test IDs must match verification graph format: `T-{module}.{test_name}`
- Function IDs must match implementation graph format: `F-{module}.{function_name}`

---

### 8. Handling Edge Cases

#### 8.1 Test Covers Function Not in Graph

If a test covers a function that isn't in the implementation graph (no `@jig.implements`):

- **Include the edge** — Coverage is objective fact
- The function ID is still generated: `F-{module}.{function_name}`
- These edges are useful for coverage visibility even without spec alignment

#### 8.2 Nested Functions / Closures

Coverage at line level may hit inner functions. For simplicity:

- Map to the **outermost function** containing the line
- Inner functions don't get separate F nodes (they're part of the parent)

#### 8.3 Test Fixtures and Conftest

Coverage from fixtures is attributed to the test that invoked them:

- `conftest.py` functions covered during `test_foo` → edges from `T-test_foo`
- This matches pytest's execution model

#### 8.4 Parametrized Tests

Parametrized tests (e.g., `test_foo[case1]`, `test_foo[case2]`) are collapsed:

- Single test ID: `T-module.test_foo`
- Coverage from all parameter variants is merged
- This keeps the model simple; parameter-level detail is future scope

---

## Resulting Artifacts

### Files Written

| File | Content |
|------|---------|
| `jig/audits/audit-log.ndjson` | Appended T→F edge records |
| `jig/audits/audit-coverage-YYYY-MM-DD.md` | Human-readable T→F listing |

### Files Read

| File | Purpose |
|------|---------|
| `jig/generated/implementation-graph.ndjson` | Resolve lines → function IDs |
| `.coverage` (temporary) | Raw coverage data from pytest |

### Files Discarded

| File | Reason |
|------|--------|
| `.coverage` | Ephemeral; audit log is source of truth |

---

## CLI Integration

### Command Hierarchy Update (A002)

```
jigy audit
├── (none)              # Show pending items and status
├── history <id>        # History for specific node
├── compact             # Compact audit log
└── coverage            # NEW: Run coverage analysis
```

### Example Workflow

```bash
# Rebuild graphs first
jigy rebuild

# Run coverage audit
jigy audit coverage

# Check what needs attention (includes T→F status)
jigy audit

# See coverage history for a specific function
jigy audit history F-auth.authenticate
```

---

## Implementation Order

### Phase 1: Core Pipeline

1. Coverage collection wrapper (pytest-cov invocation)
2. Coverage data parser (extract T→F from `.coverage`)
3. Line-to-function mapper (using implementation graph)
4. Audit log writer (J026 schema)
5. Report generator (grep-able format)

### Phase 2: CLI Integration

1. `jigy audit coverage` command
2. Integration with `jigy audit` status display
3. T→F edges in `jigy audit history`

### Phase 3: Polish

1. Error handling (test failures, missing graphs)
2. Progress output during coverage run
3. Summary statistics in report header

---

## Success Criteria

```
jigy audit coverage:
  - Runs test suite with coverage
  - Produces T→F edges in audit-log.ndjson
  - Produces grep-able report
  - Discards raw coverage data

Report format:
  - One T: F per line
  - Sorted by test, then function
  - Grep-able for both T and F queries

Integration:
  - jigy audit shows T→F status
  - jigy audit history shows T→F edges
  - T→F trigger detection works (hash comparison)
```

---

## Open Questions

1. **Multiple runs per day?** Report naming uses YYYY-MM-DD. If run multiple times, overwrite or append timestamp? (Suggest: overwrite, audit log has full history anyway)

2. **Partial coverage runs?** Should we support running coverage on a subset of tests? (Suggest: future scope, full suite first)

3. **Coverage tool abstraction?** pytest-cov is default, but should we abstract for other tools? (Suggest: pytest-cov only for now, abstract later if needed)

---

## References

- **J026:** Audit Architecture Simplification (T→F as first-class audit type)
- **J022:** Content Hashing (jig_hash for T and F nodes)
- **A002:** CLI Command Architecture (verb-first commands)
- **A001:** Core Artifacts Contract (graph schemas)

---

_Coverage tells you what ran. The audit log remembers._
