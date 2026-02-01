---
title: "J028: Coverage Audit"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1765917865
created_human: "2025-12-16 14:44 CST"
parent: "[[J017_JIG-Concept-v9]]"
children: []
---
# J028: Coverage Audit

**Status:** Proposal
**Date:** 2025-12-16
**Extends:** J026 (Audit Architecture Simplification)
**Refines:** J023 (Audit Records and Triggers) for T→F edges

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
3. **Ephemeral source data** — Raw coverage data is intermediate; the audit record is the result

Coverage fits the audit model: collect evidence, make a determination, record the result.

### Design Goals

1. **Simple T→F edges** — Binary "covered" or "not_covered" per test/function pair
2. **Mid-altitude granularity** — "Did test T execute ≥1 line of function F?"
3. **Grep-able record** — One T→F pair per line for easy filtering
4. **Ephemeral raw data** — Discard `.coverage` after processing
5. **Two-level storage** — Audit log entry points to detailed record file

---

## Decision

### 1. Two-Level Audit Model

Coverage audits use a **two-level model** that separates the audit activity from its detailed results:

```
jig/audits/
├── audit-log.ndjson              # One entry per audit activity
└── records/
    └── coverage-2025-12-16.ndjson  # Detailed T→F edges (NDJSON)
```

**Why two levels?**

| Approach | Coverage Run | Problem |
|----------|--------------|---------|
| Per-edge rows | 1000 T→F edges = 1000 rows | Log bloat, redundant metadata |
| Per-activity | 1 row pointing to record | Clean log, detail in record |

The audit log stays compact (one entry per coverage run). The record file contains the detailed T→F edges.

**Contrast with semantic audits (F→S, T→S):**

| Audit Type | Log Points To | File Type | Contains |
|------------|---------------|-----------|----------|
| Coverage (T→F) | `record` | NDJSON | T→F edges (structured data) |
| Semantic (F→S, T→S) | `report` | Markdown | Reasoning + frontmatter (prose) |

Coverage produces structured data → NDJSON record.
Semantic audits produce reasoning → Markdown report.

---

### 2. Command: `jigy audit coverage`

Per A002 (CLI Command Architecture), coverage audit uses verb-first with noun subcommand:

```bash
jigy audit coverage    # Run coverage analysis, record T→F edges
```

**Behavior:**
1. Run test suite with coverage instrumentation
2. Parse coverage data to extract T→F relationships
3. Write detailed T→F edges to `jig/audits/records/coverage-YYYY-MM-DD.ndjson`
4. Append one activity entry to `jig/audits/audit-log.ndjson`
5. Discard raw coverage data

**Exit codes:**
- 0: Coverage analysis completed successfully
- 1: Test failures or coverage collection error
- 2: Usage error

---

### 3. T→F Edge Definition

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

### 4. Audit Log Entry Schema

The audit log entry for a coverage run:

```json
{
  "id": "coverage-2025-12-16",
  "type": "coverage",
  "git_commit": "abc1234",
  "timestamp": "2025-12-16T14:32:00Z",
  "method": "pytest-cov",
  "summary": {
    "tests": 89,
    "functions": 312,
    "edges": 847
  },
  "record": "records/coverage-2025-12-16.ndjson"
}
```

**Field definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for this audit activity |
| `type` | enum | `"coverage"` for T→F coverage audits |
| `git_commit` | string | Git commit at audit time |
| `timestamp` | ISO 8601 | When audit was performed |
| `method` | string | Coverage tool used (e.g., `"pytest-cov"`) |
| `summary` | object | Counts: tests, functions, edges |
| `record` | string | Path to detailed record file (NDJSON) |

**Note:** Coverage uses `record` (NDJSON). Semantic audits use `report` (Markdown). These are mutually exclusive fields.

---

### 5. Record File Format

The record file contains detailed T→F edges in **NDJSON format** (one edge per line):

**Location:** `jig/audits/records/coverage-YYYY-MM-DD.ndjson`

**Format:**
```ndjson
{"edge":"T→F","from":{"id":"T-test_auth.test_login","jig_hash":"a1b2c3"},"to":{"id":"F-auth.authenticate","jig_hash":"d4e5f6"},"result":"covered"}
{"edge":"T→F","from":{"id":"T-test_auth.test_login","jig_hash":"a1b2c3"},"to":{"id":"F-auth.validate_token","jig_hash":"e5f6a7"},"result":"covered"}
{"edge":"T→F","from":{"id":"T-test_auth.test_logout","jig_hash":"b2c3d4"},"to":{"id":"F-auth.invalidate_session","jig_hash":"f6a7b8"},"result":"covered"}
```

**Edge record fields:**

| Field | Type | Description |
|-------|------|-------------|
| `edge` | enum | Always `"T→F"` for coverage |
| `from.id` | string | Test node ID |
| `from.jig_hash` | string | Test content hash at audit time |
| `to.id` | string | Function node ID |
| `to.jig_hash` | string | Function content hash at audit time |
| `result` | enum | `"covered"` or `"not_covered"` |

**Grep-ability preserved:**
```bash
# What does test_login cover?
grep "T-test_auth.test_login" jig/audits/records/coverage-*.ndjson

# What tests cover authenticate?
grep "F-auth.authenticate" jig/audits/records/coverage-*.ndjson

# Convert to simple format
jq -r '"\(.from.id): \(.to.id)"' records/coverage-2025-12-16.ndjson

# Count edges
wc -l < jig/audits/records/coverage-2025-12-16.ndjson

# Diff between runs
diff records/coverage-2025-12-15.ndjson records/coverage-2025-12-16.ndjson
```

**Sorting:** Lines are sorted by test ID (from.id), then by function ID (to.id).

---

### 6. Trigger Detection for T→F Edges

T→F trigger detection works differently from F→S and T→S because edges are stored in record files, not directly in the log.

**Algorithm:**

```python
def detect_tf_triggers(
    current_impl_graph: Graph,
    current_verif_graph: Graph,
    latest_coverage_record: Path
) -> list[Trigger]:
    """
    Detect T→F edges needing re-audit.

    Compare current node hashes to hashes in latest coverage record.
    """
    triggers = []

    # Load latest coverage record
    if not latest_coverage_record.exists():
        # No coverage audit yet - all potential T→F edges are "new"
        return [Trigger(type="new", ...)]

    recorded_edges = load_ndjson(latest_coverage_record)
    recorded_by_key = {
        (r['from']['id'], r['to']['id']): r
        for r in recorded_edges
    }

    # Check each test/function pair
    for test in current_verif_graph.tests():
        for func in current_impl_graph.functions():
            key = (test.id, func.id)
            recorded = recorded_by_key.get(key)

            if recorded is None:
                # New pair (test or function added since last coverage)
                triggers.append(Trigger(key, reason='new'))
            elif recorded['from']['jig_hash'] != test.jig_hash:
                triggers.append(Trigger(key, reason='test_changed'))
            elif recorded['to']['jig_hash'] != func.jig_hash:
                triggers.append(Trigger(key, reason='function_changed'))

    return triggers
```

**Trigger reasons for T→F:**

| Reason | Meaning | Action |
|--------|---------|--------|
| `new` | No coverage record exists | Run `jigy audit coverage` |
| `test_changed` | Test jig_hash changed | Re-run coverage |
| `function_changed` | Function jig_hash changed | Re-run coverage |

**Practical implication:** Any code change to a test or function triggers a full coverage re-run. This is acceptable because:
- Coverage runs are typically part of CI anyway
- Partial coverage updates are complex and error-prone
- Full runs ensure consistency

---

### 7. Raw Coverage Data Lifecycle

Raw coverage data (`.coverage` file, JSON exports) is **ephemeral**:

```
[pytest --cov]  →  [.coverage]  →  [parse T→F]  →  [record file]
                       ↓                              ↓
                  (discard)                    (source of truth)
```

**Rationale:**
- Raw coverage data is large and redundant once T→F edges are extracted
- The record file is the canonical record
- Like `pytest --cov` overwrites `.coverage` each run, we don't accumulate raw data
- If more granular data is needed later, re-run coverage

---

### 8. Coverage Collection Strategy

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

### 9. Integration with Existing Graphs

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

### 10. Handling Edge Cases

#### 10.1 Test Covers Function Not in Graph

If a test covers a function that isn't in the implementation graph (no `@jig.implements`):

- **Include the edge** — Coverage is objective fact
- The function ID is still generated: `F-{module}.{function_name}`
- These edges are useful for coverage visibility even without spec alignment

#### 10.2 Nested Functions / Closures

Coverage at line level may hit inner functions. For simplicity:

- Map to the **outermost function** containing the line
- Inner functions don't get separate F nodes (they're part of the parent)

#### 10.3 Test Fixtures and Conftest

Coverage from fixtures is attributed to the test that invoked them:

- `conftest.py` functions covered during `test_foo` → edges from `T-test_foo`
- This matches pytest's execution model

#### 10.4 Parametrized Tests

Parametrized tests (e.g., `test_foo[case1]`, `test_foo[case2]`) are collapsed:

- Single test ID: `T-module.test_foo`
- Coverage from all parameter variants is merged
- This keeps the model simple; parameter-level detail is future scope

---

## Resulting Artifacts

### File Structure

```
jig/audits/
├── audit-log.ndjson                    # Audit activity log
└── records/
    ├── coverage-2025-12-15.ndjson      # Previous coverage record
    └── coverage-2025-12-16.ndjson      # Latest coverage record
```

### Files Written

| File | Content |
|------|---------|
| `jig/audits/audit-log.ndjson` | One entry appended per coverage run |
| `jig/audits/records/coverage-YYYY-MM-DD.ndjson` | All T→F edges from this run |

### Files Read

| File | Purpose |
|------|---------|
| `jig/generated/implementation-graph.ndjson` | Resolve lines → function IDs |
| `.coverage` (temporary) | Raw coverage data from pytest |

### Files Discarded

| File | Reason |
|------|--------|
| `.coverage` | Ephemeral; record file is source of truth |

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
4. Record file writer (NDJSON format)
5. Audit log entry writer

### Phase 2: CLI Integration

1. `jigy audit coverage` command
2. Integration with `jigy audit` status display
3. T→F edges in `jigy audit history`

### Phase 3: Polish

1. Error handling (test failures, missing graphs)
2. Progress output during coverage run
3. Summary statistics in log entry

---

## Success Criteria

```
jigy audit coverage:
  - Runs test suite with coverage
  - Produces record file with T→F edges
  - Appends one entry to audit log
  - Discards raw coverage data

Record format:
  - NDJSON, one edge per line
  - Sorted by test, then function
  - Grep-able for both T and F queries
  - Contains jig_hash for trigger detection

Integration:
  - jigy audit shows T→F status
  - jigy audit history shows T→F edges
  - T→F trigger detection works (compare to latest record)
```

---

## Open Questions

1. **Multiple runs per day?** Record naming uses YYYY-MM-DD. If run multiple times, overwrite or add timestamp suffix? (Suggest: overwrite, previous run is superseded)

2. **Partial coverage runs?** Should we support running coverage on a subset of tests? (Suggest: future scope, full suite first)

3. **Coverage tool abstraction?** pytest-cov is default, but should we abstract for other tools? (Suggest: pytest-cov only for now, abstract later if needed)

---

## References

- **J026:** Audit Architecture Simplification (audit model)
- **J023:** Audit Records and Triggers (two-level model)
- **J022:** Content Hashing (jig_hash for T and F nodes)
- **A002:** CLI Command Architecture (verb-first commands)
- **A001:** Core Artifacts Contract (graph schemas)

---

_Coverage tells you what ran. The record remembers._
