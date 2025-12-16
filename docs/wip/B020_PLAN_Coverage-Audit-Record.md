# PLAN: Coverage Audit Record

- **SCOPE**: docs/wip/B019_SCOPE_Coverage-Audit-Record.md
- **Start**: 2025-12-16
- **Status**: Draft
- **Branch**: audit-coverage

## Known Intent (Created Before Coding)

**Outcomes**:
- O-005: Verifiable Test-to-Implementation Coverage

**Specifications**:
- S-030: T→F Edge Collection via Coverage
- S-031: Coverage Record Format

**Bricks Affected**:

| Brick | Layer | Purpose | New Modules |
|-------|-------|---------|-------------|
| B-audit | 1 (new) | Audit system core | `M-jig.audit.coverage`, `M-jig.audit.record_writer` |
| B-cli | 1 (existing) | CLI command | `M-jig.cli.audit` |

**Brick Dependencies:**
```
B-cli (layer 1)
  └── B-audit (layer 1)
        ├── B-impl-graph (layer 0)      # read F nodes, line ranges
        └── B-verification-graph (layer 1)  # read T nodes, jig_hash
```

**Note:** B-audit at layer 1 because it depends on B-verification-graph (also layer 1). The CLI module calls into B-audit.

## Work Unit Checklist

- [ ] WU0: Create Intent nodes (O-005, S-030, S-031) and update bricks.yaml
- [ ] WU1: CLI + coverage collection — tests ☐ / code ☐ / docs ☐
- [ ] WU2: T→F extraction — tests ☐ / code ☐ / docs ☐
- [ ] WU3: Record file writer — tests ☐ / code ☐ / docs ☐
- [ ] WU4: End-to-end integration — tests ☐ / code ☐ / docs ☐

## Work Units

### Work Unit 0: Create Known Intent

**Goal**: Define outcome, specifications, and register new brick before writing code.

**Acceptance Criteria**:
- [ ] O-005 created in `jig/outcomes/`
- [ ] S-030 and S-031 created in `jig/specifications/`
- [ ] B-audit brick added to `jig/bricks.yaml`
- [ ] `jigy validate` passes

**Outcome to Create:**

**O-005: Verifiable Test-to-Implementation Coverage**
```markdown
---
id: O-005
type: outcome
specifies: [S-030, S-031]
---

# Verifiable Test-to-Implementation Coverage

Tests that claim to verify specifications demonstrably execute the implementing code.

**Value:** Completes the S-F-T alignment triangle with objective, execution-based
evidence. Detects cases where tests pass but don't actually execute the relevant
implementation—preventing false confidence in test suites.

**Why This Matters:**
- F→S and T→S edges require human judgment (does code fulfill spec?)
- T→F edges are objective facts determined by execution
- Without T→F, a test could verify a spec (T→S) but never run the implementation (no T→F)
- This gap represents "testing theater"—tests that pass without validating behavior
```

**Specifications to Create:**

**S-030: T→F Edge Collection via Coverage**
```markdown
---
id: S-030
type: specification
implements: [O-005]
---

# T→F Edge Collection via Coverage

The coverage audit determines which tests execute which functions by running
the test suite with coverage instrumentation.

**Acceptance Criteria:**
- Running `jigy audit coverage` executes tests with line-level coverage tracking
- For each test, the system identifies which functions had lines executed
- A T→F edge exists when test T executed at least one line of function F
- Edge data includes test ID, function ID, and coverage result

**Rationale:** T→F relationships are objective facts determined by execution,
unlike F→S and T→S which require semantic judgment.
```

**S-031: Coverage Record Format**
```markdown
---
id: S-031
type: specification
implements: [O-005]
---

# Coverage Record Format

Coverage audit results are persisted in a grep-able, diff-able record file
that supports staleness detection.

**Acceptance Criteria:**
- Record written to `jig/audits/records/coverage-YYYY-MM-DD.ndjson`
- Each line is a valid JSON object representing one T→F edge
- Edge records contain: edge type, from (test ID + jig_hash), to (function ID + jig_hash), result
- Lines sorted by test ID, then function ID
- Grep for test ID returns all functions that test covers
- Grep for function ID returns all tests that cover that function

**Rationale:** Line-oriented JSON enables standard Unix tools for querying and
comparing coverage across runs. Content hashes enable staleness detection.
```

**Bricks Update:**
```yaml
# Add to jig/bricks.yaml

# New brick for audit system
  - id: B-audit
    name: Audit System
    layer: 1
    units:
      - M-jig.audit.coverage
      - M-jig.audit.record_writer

# Update B-cli units list to include:
      - M-jig.cli.audit
```

**Reflect**:
- What was clear from SCOPE: Edge definition (binary covered/not_covered), record format (NDJSON)
- What was ambiguous: Exact pytest context string format (will discover during implementation)

---

### Work Unit 1: CLI + Coverage Collection

**Goal**: Add `jigy audit coverage` command that runs pytest with coverage instrumentation.

**Implements**: S-030 (T→F Edge Collection via Coverage)

**Acceptance Criteria**:
- [ ] `jigy audit coverage` command exists and is callable
- [ ] Pytest runs with `--cov=src --cov-context=test`
- [ ] Coverage data written to `.coverage` file
- [ ] Creates `jig/audits/records/` directory if missing
- [ ] Test failures captured (exit code 1) but coverage still collected

**Implementation Notes**:
- Approach:
  1. Add `audit` command group to CLI
  2. Add `coverage` subcommand
  3. Invoke pytest via subprocess with coverage flags
  4. Ensure directory structure created on invocation
- Files:
  - `src/jig/cli/audit.py` (new) — CLI command in B-cli
  - `src/jig/audit/__init__.py` (new) — B-audit package
  - `src/jig/audit/coverage.py` (new) — coverage collection logic
- Decorators: `@jig.implements("S-030")`

**Test Plan**:
- Unit tests: Command construction, directory creation
- Integration test: Run on fixture project, verify .coverage created
- Test file: `test/audit/test_coverage.py`
- Decorators: `@jig.verifies("S-030")`

**Human Verification**:
```bash
jigy audit coverage --help    # Should show help
jigy audit coverage           # Should run pytest with coverage
ls .coverage                  # Should exist after run
ls jig/audits/records/        # Directory should exist
```

---

### Work Unit 2: T→F Extraction

**Goal**: Parse `.coverage` database and map to function IDs using implementation graph.

**Implements**: S-030 (T→F Edge Collection via Coverage)

**Acceptance Criteria**:
- [ ] Read `.coverage` SQLite database
- [ ] Extract test contexts (which test covered which lines)
- [ ] Load implementation graph for line→function resolution
- [ ] Produce list of (test_id, function_id, result) tuples
- [ ] Handle edge cases: nested functions, parametrized tests

**Implementation Notes**:
- Approach:
  1. Open `.coverage` as SQLite database
  2. Query for test contexts and covered lines per context
  3. Load `jig/generated/implementation-graph.ndjson`
  4. Build file:line → function_id index from F nodes
  5. Map covered lines to function IDs
  6. Collapse parametrized test variants to single test ID
- Files:
  - `src/jig/audit/coverage.py` — extend with parsing logic
- Decorators: `@jig.implements("S-030")`

**Test Plan**:
- Unit tests:
  - Parse mock .coverage database
  - Map lines to functions with fixture graph
  - Handle nested functions (map to outermost)
  - Handle parametrized tests (collapse variants)
- Test file: `test/audit/test_coverage.py`
- Decorators: `@jig.verifies("S-030")`

**Human Verification**:
```bash
# After running coverage, check parsed output
python -c "from jig.audit.coverage import extract_tf_edges; print(extract_tf_edges('.coverage', 'jig/generated/implementation-graph.ndjson'))"
```

---

### Work Unit 3: Record File Writer

**Goal**: Write T→F edges to NDJSON record file with proper format.

**Implements**: S-031 (Coverage Record Format)

**Acceptance Criteria**:
- [ ] Record file created at `jig/audits/records/coverage-YYYY-MM-DD.ndjson`
- [ ] Each line is valid JSON with edge, from, to, result fields
- [ ] Lines sorted by from.id then to.id
- [ ] jig_hash included for both test and function nodes
- [ ] `.coverage` deleted after successful processing

**Implementation Notes**:
- Approach:
  1. Load verification graph for test jig_hash values
  2. Load implementation graph for function jig_hash values
  3. Build edge records with all required fields
  4. Sort by (from.id, to.id)
  5. Write NDJSON to dated file
  6. Delete `.coverage`
- Files:
  - `src/jig/audit/record_writer.py` (new)
- Decorators: `@jig.implements("S-031")`

**Test Plan**:
- Unit tests:
  - NDJSON format validation
  - Sorting verification
  - jig_hash inclusion
  - File cleanup after write
- Test file: `test/audit/test_record_writer.py`
- Decorators: `@jig.verifies("S-031")`

**Human Verification**:
```bash
jigy audit coverage
cat jig/audits/records/coverage-2025-12-16.ndjson | head -5
# Verify JSON format, sorting, required fields
jq '.' jig/audits/records/coverage-2025-12-16.ndjson | head -20
# Verify grep-ability
grep "T-test_" jig/audits/records/coverage-*.ndjson | head -3
```

---

### Work Unit 4: End-to-End Integration

**Goal**: Wire all components together and verify complete pipeline.

**Implements**: S-030, S-031 (integration of both specs)

**Acceptance Criteria**:
- [ ] `jigy audit coverage` produces valid record file end-to-end
- [ ] Record file grep-able for test and function queries
- [ ] Missing implementation graph produces helpful error
- [ ] Missing verification graph produces helpful error
- [ ] Multiple runs overwrite same-day record
- [ ] Basic progress/summary output displayed

**Implementation Notes**:
- Approach:
  1. Wire all components in CLI command handler
  2. Add error handling for missing graphs
  3. Add progress messages: "Running tests...", "Extracting edges...", "Writing record..."
  4. Display summary: "Wrote N edges to jig/audits/records/coverage-YYYY-MM-DD.ndjson"
- Files:
  - `src/jig/cli/audit.py` — wire components
  - `src/jig/audit/coverage.py` — add run_coverage_audit() orchestrator
- Decorators: `@jig.implements("S-030")`, `@jig.implements("S-031")`

**Test Plan**:
- Integration test: Full pipeline on fixture project
- Error handling tests: Missing impl graph, missing verify graph, test failures
- Test file: `test/audit/test_coverage_integration.py`
- Decorators: `@jig.verifies("S-030")`, `@jig.verifies("S-031")`

**Human Verification**:
```bash
# Full workflow
jigy rebuild
jigy audit coverage

# Query record
grep "T-test_" jig/audits/records/coverage-*.ndjson | wc -l
grep "F-jig" jig/audits/records/coverage-*.ndjson | head -5

# Error cases
rm jig/generated/implementation-graph.ndjson
jigy audit coverage   # Should show: "Run 'jigy rebuild impl' first"

rm jig/generated/verification-graph.ndjson
jigy audit coverage   # Should show: "Run 'jigy rebuild verify' first"
```

---

## Dependency Graph

```
WU0 (Intent + bricks.yaml)
  ↓
WU1 (CLI + coverage collection)
  ↓
WU2 (T→F extraction)
  ↓
WU3 (Record writer)
  ↓
WU4 (Integration)
```

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| `.coverage` SQLite schema varies by coverage.py version | Pin coverage.py version, document expected schema |
| Large projects produce huge record files | Accept for now; compression is future scope |
| Parametrized test context strings complex to parse | Use regex, handle common patterns first |
| Nested function line ranges overlap | Map to outermost function per J028 decision |

---

## File Structure (After Implementation)

```
src/jig/
├── cli/
│   ├── main.py          # Updated: register audit command group
│   └── audit.py         # NEW: jigy audit coverage command
└── audit/
    ├── __init__.py      # NEW: B-audit package
    ├── coverage.py      # NEW: collection + extraction logic
    └── record_writer.py # NEW: NDJSON record output

test/audit/
├── test_coverage.py            # NEW: collection + extraction tests
├── test_record_writer.py       # NEW: record format tests
└── test_coverage_integration.py # NEW: end-to-end tests

jig/
├── outcomes/
│   └── O-005.md         # NEW: Verifiable Test-to-Implementation Coverage
├── specifications/
│   ├── S-030.md         # NEW: T→F Edge Collection
│   └── S-031.md         # NEW: Coverage Record Format
├── bricks.yaml          # Updated: add B-audit brick
└── audits/
    └── records/         # Created by command
        └── coverage-YYYY-MM-DD.ndjson
```

---

## References

- **B019**: SCOPE document (docs/wip/B019_SCOPE_Coverage-Audit-Record.md)
- **J028**: Coverage Audit specification (docs/jig-concept/J028_Coverage-Audit.md)
- **taskPlan.md**: Work unit template (agents/taskPlan.md)
- **O-S-Writing-Guide.md**: Spec writing guidelines (docs/agents/O-S-Writing-Guide.md)

---

_Plan first. Then execute._
