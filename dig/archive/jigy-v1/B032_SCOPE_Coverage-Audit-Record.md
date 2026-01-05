---
title: "B019: Coverage Audit Record Implementation"
type: scope
status: implemented
decision: "Superseded by newer deliberation"
created: 1765921953
created_human: "2025-12-16 15:52 CST"
parent: null
children: ['[[B020_PLAN_Coverage-Audit-Record]]']
---
# B019: Coverage Audit Record Implementation

**Status:** WIP
**Date:** 2025-12-16
**Implements:** J028 (Coverage Audit) - partial
**Brick:** B019

---

## Objective

Implement the core coverage audit pipeline that runs tests with coverage instrumentation and produces a T→F record file. This establishes the foundation for coverage-based audit evidence.

---

## In Scope

### 1. CLI Command: `jigy audit coverage`

Add the `audit coverage` subcommand to run coverage analysis.

**Behavior:**
1. Run test suite with `pytest-cov` instrumentation
2. Parse coverage data to extract T→F relationships
3. Write T→F edges to `jig/audits/records/coverage-YYYY-MM-DD.ndjson`
4. Discard raw `.coverage` file after processing

**Exit codes:**
- 0: Coverage analysis completed successfully
- 1: Test failures or coverage collection error
- 2: Usage error

### 2. Coverage Collection

Invoke pytest with coverage context tracking:

```bash
pytest \
    --cov=src \
    --cov-context=test \
    --cov-report= \
    test/
```

The `--cov-context=test` flag is critical—it tracks which test covers which lines.

### 3. Coverage Data Parser

Extract T→F edges from the `.coverage` SQLite database:

- Read coverage contexts (test identifiers)
- Map covered lines to source files
- Identify which functions contain those lines

### 4. Line-to-Function Mapper

Use the implementation graph to resolve covered lines to function IDs:

- Read `jig/generated/implementation-graph.ndjson`
- For each covered line, find the containing function
- Generate function ID: `F-{module}.{function_name}`

### 5. Record File Writer

Write T→F edges in NDJSON format:

**Location:** `jig/audits/records/coverage-YYYY-MM-DD.ndjson`

**Format per line:**
```json
{"edge":"T→F","from":{"id":"T-test_module.test_name","jig_hash":"abc123"},"to":{"id":"F-module.function","jig_hash":"def456"},"result":"covered"}
```

**Requirements:**
- One edge per line
- Sorted by test ID, then function ID
- Include `jig_hash` for both test and function nodes

### 6. Directory Structure

Ensure directory exists before writing:

```
jig/audits/
└── records/
    └── coverage-YYYY-MM-DD.ndjson
```

---

## Out of Scope

| Item | Reason | Future Brick |
|------|--------|--------------|
| Audit log entry | J023 integration deferred | TBD |
| `jigy audit` status display | Depends on audit log | TBD |
| `jigy audit history` integration | Depends on audit log | TBD |
| Trigger detection | Depends on audit log | TBD |
| Summary statistics | Nice-to-have, not core | TBD |
| Progress output during run | Polish, not core | TBD |

---

## Dependencies

### Requires

| Artifact | Purpose |
|----------|---------|
| `jig/generated/implementation-graph.ndjson` | Map lines → function IDs |
| `jig/generated/verification-graph.ndjson` | Get test node jig_hash values |

### Assumes

- pytest-cov is installed (`pip install pytest-cov`)
- Implementation graph is current (`jigy rebuild impl`)
- Verification graph is current (`jigy rebuild verify`)

---

## Edge Cases to Handle

### 6.1 Test Covers Function Not in Graph

Coverage may hit functions without `@jig.implements` decorators.

**Decision:** Include the edge. Coverage is objective fact regardless of spec alignment.

### 6.2 Nested Functions / Closures

Multiple functions may share line ranges.

**Decision:** Map to the outermost function containing the line.

### 6.3 Parametrized Tests

Tests like `test_foo[case1]`, `test_foo[case2]` produce multiple contexts.

**Decision:** Collapse to single test ID `T-module.test_foo`. Merge coverage from all variants.

### 6.4 Missing Implementation Graph

Cannot map lines to functions without the graph.

**Decision:** Exit with error, message: "Run `jigy rebuild impl` first"

### 6.5 Multiple Runs Per Day

Record naming uses YYYY-MM-DD.

**Decision:** Overwrite previous same-day record. Latest run supersedes.

---

## Implementation Tasks

### Phase 1: Infrastructure

1. [ ] Create `jig/audits/records/` directory structure
2. [ ] Add `audit` command group to CLI
3. [ ] Add `coverage` subcommand skeleton

### Phase 2: Coverage Collection

4. [ ] Implement pytest-cov invocation with context tracking
5. [ ] Capture exit code and handle test failures
6. [ ] Parse `.coverage` SQLite database

### Phase 3: T→F Extraction

7. [ ] Load implementation graph for line→function mapping
8. [ ] Load verification graph for test jig_hash lookup
9. [ ] Map coverage contexts to test IDs
10. [ ] Map covered lines to function IDs
11. [ ] Build T→F edge list

### Phase 4: Record Writing

12. [ ] Generate record filename with current date
13. [ ] Write NDJSON record file (sorted)
14. [ ] Delete `.coverage` after successful processing

### Phase 5: CLI Polish

15. [ ] Add basic output messages (running, complete, counts)
16. [ ] Handle missing graph files gracefully

---

## Acceptance Criteria

```
Given: Implementation and verification graphs exist
When:  jigy audit coverage
Then:
  - Tests run with coverage instrumentation
  - Record file created at jig/audits/records/coverage-YYYY-MM-DD.ndjson
  - Each line is valid JSON with edge, from, to, result fields
  - Lines sorted by from.id then to.id
  - .coverage file deleted after processing
  - Exit code 0 on success
```

```
Given: Implementation graph does not exist
When:  jigy audit coverage
Then:
  - Error message displayed
  - Exit code 1
  - No record file created
```

```
Given: Tests fail during coverage run
When:  jigy audit coverage
Then:
  - Coverage still collected for passing tests
  - Record file still written
  - Exit code 1 (test failures)
```

---

## References

- **J028:** Coverage Audit (specification)
- **A002:** CLI Command Architecture (command structure)
- **A001:** Core Artifacts Contract (graph schemas)

---

_Run coverage. Write the record. Discard the noise._
