# J023: Audit Strategies and Mechanisms

**Status:** Proposal
**Date:** 2025-12-06
**Extends:** J017 (JIG Concept v9), J022 (Alignment Change Detection)

---

## Context

JIG measures alignment between specifications (S), functions (F), and tests (T). But measurement alone is not enough—we need **auditing** to verify that alignment is semantically correct, not just structurally present.

An audit answers deeper questions:
- Does the implementation actually fulfill the spec's intent?
- Does the test actually validate the requirement?
- Does the spec meaningfully contribute to its upstream outcome?
- Are there patterns of misalignment across the codebase?

### The Problem

Markdown audit reports are human-readable but terrible for:
- **Filtering**: Find all UNVERIFIED specs
- **Aggregation**: Average alignment score by brick
- **Trend analysis**: Alignment drift over time
- **Bulk operations**: Create work items for all coverage gaps
- **Cross-referencing**: Which outcomes have incomplete decomposition

Without machine-readable audit outputs, we must rely on LLMs to parse and analyze results—expensive, slow, and non-deterministic.

### Design Goals

1. **Separate human-readable from machine-readable** — don't compromise either
2. **Follow JIG patterns** — NDJSON worked well for graphs
3. **Enable standard tooling** — jq, grep, awk should work
4. **Support incremental updates** — re-audit one spec without regenerating all
5. **Git-friendly** — line-based diffs, no binary files

---

## Audit Structure

### Directory Layout

```
jig/audits/
├── index.ndjson           # Aggregated summary (regenerated)
├── audit-S-001.ndjson     # Individual audit (machine-readable)
├── audit-S-001.md         # Individual audit (human-readable)
├── audit-S-020.ndjson
├── audit-S-020.md
├── audit-S-038.ndjson
├── audit-S-038.md
└── ...
```

**Rationale:**
- Dual output (`.ndjson` + `.md`) per audit serves both machines and humans
- Index file enables fast queries without loading all audits
- Individual files enable incremental updates and clean git history

---

## Individual Audit Schema

Each audit produces an NDJSON file with typed records.

### File: `audit-S-001.ndjson`

```json
{"_meta":{"spec_id":"S-001","audited_at":"2025-12-06T14:32:00Z","auditor":"agent","schema_version":"1"}}
{"_status":{"alignment":"PERFECT","outcome_alignment":"ALIGNED","score":92.7}}
{"_outcome":{"id":"O-001","title":"AST Analysis","sibling_specs":["S-002","S-003"],"contribution":"ALIGNED"}}
{"_spec":{"id":"S-001","title":"Python code structure extracted via AST","criteria_count":7}}
{"_impl":{"count":6,"criteria_covered":7,"criteria_total":7,"missing":[]}}
{"_verify":{"count":23,"criteria_covered":7,"criteria_total":7,"missing":[]}}
{"_coverage":{"percentage":80.72,"gaps":[]}}
{"impl":"F-jig.impl_graph.analyzers.python_visitor.PythonVisitor","file":"src/jig/impl_graph/analyzers/python_visitor.py","line":45,"criteria":[1,2,3,4,5,6,7]}
{"impl":"F-jig.impl_graph.analyzers.python_visitor.visit_Module","file":"src/jig/impl_graph/analyzers/python_visitor.py","line":78,"criteria":[1]}
{"verify":"T-test_python_analyzer.test_discovers_modules","file":"tests/unit/test_python_analyzer.py","line":12,"criteria":[1]}
{"verify":"T-test_python_analyzer.test_discovers_classes","file":"tests/unit/test_python_analyzer.py","line":25,"criteria":[1]}
{"issue":"UNCOVERED_PATH","severity":"LOW","location":"src/jig/impl_graph/analyzers/python_visitor.py:380","description":"Latin-1 fallback not tested"}
```

### Record Types

| Prefix | Purpose | Required |
|--------|---------|----------|
| `_meta` | Audit metadata (timestamp, auditor, schema version) | Yes |
| `_status` | Overall alignment status and score | Yes |
| `_outcome` | Upstream outcome linkage | Yes |
| `_spec` | Specification metadata | Yes |
| `_impl` | Implementation summary | Yes |
| `_verify` | Verification summary | Yes |
| `_coverage` | Execution coverage summary | Yes |
| `impl` | Individual implementing function | 0..n |
| `verify` | Individual verifying test | 0..n |
| `issue` | Detected problem | 0..n |

### Alignment Status Values

| Status | F → S | T → S | T → F | Meaning |
|--------|-------|-------|-------|---------|
| `PERFECT` | ✓ | ✓ | ✓ | Fully aligned |
| `UNVERIFIED` | ✓ | ✗ | - | Implemented but needs tests |
| `UNTESTED` | ✓ | ✓ | ✗ | Tests don't execute implementation |
| `UNIMPLEMENTED` | ✗ | ? | - | Spec not yet implemented |

### Outcome Alignment Values

| Status | Meaning |
|--------|---------|
| `ALIGNED` | Spec contributes meaningfully to outcome goal |
| `PARTIAL` | Spec addresses outcome but incompletely |
| `MISALIGNED` | Spec doesn't support the outcome's stated goal |
| `ORPHAN` | Spec has no upstream outcome |

### Issue Types

| Type | Severity | Description |
|------|----------|-------------|
| `ORPHAN_SPEC` | MEDIUM | Spec has no upstream outcome |
| `MISALIGNED_SPEC` | HIGH | Spec listed in outcome but doesn't contribute |
| `INCOMPLETE_DECOMPOSITION` | MEDIUM | Outcome not fully addressed by specs |
| `COVERAGE_GAP` | HIGH | Test verifies spec but doesn't execute implementation |
| `HOLLOW_IMPL` | HIGH | Decorator present but function doesn't implement |
| `HOLLOW_VERIFY` | HIGH | Decorator present but test doesn't validate |
| `UNCOVERED_PATH` | LOW | Code path not exercised by tests |
| `STALE_REFERENCE` | HIGH | Spec modified but implementation not updated |

---

## Index Schema

The index aggregates all audits for fast queries.

### File: `index.ndjson`

```json
{"_meta":{"generated_at":"2025-12-06T14:35:00Z","total_specs":43,"schema_version":"1"}}
{"_summary":{"PERFECT":30,"UNVERIFIED":8,"UNTESTED":3,"UNIMPLEMENTED":2}}
{"_outcome_summary":{"ALIGNED":25,"PARTIAL":5,"MISALIGNED":2,"ORPHAN":11}}
{"_issue_summary":{"COVERAGE_GAP":5,"HOLLOW_IMPL":2,"ORPHAN_SPEC":11,"MISSING_TEST":8}}
{"_brick_summary":{"B-core-utils":{"specs":8,"avg_score":95.2},"B-validation":{"specs":12,"avg_score":82.1}}}
{"_layer_summary":{"0":{"bricks":2,"specs":15,"avg_score":94.1},"1":{"bricks":3,"specs":20,"avg_score":88.3},"2":{"bricks":1,"specs":8,"avg_score":82.0}}}
{"spec":"S-001","status":"PERFECT","score":92.7,"outcome":"O-001","brick":"B-core-utils","layer":0,"impl_count":6,"verify_count":23,"issues":1}
{"spec":"S-020","status":"UNTESTED","score":85.0,"outcome":"O-005","brick":"B-validation","layer":0,"impl_count":1,"verify_count":6,"issues":2}
{"spec":"S-038","status":"PERFECT","score":97.7,"outcome":"O-008","brick":"B-validation","layer":0,"impl_count":1,"verify_count":11,"issues":0}
```

### Index Record Types

| Prefix | Purpose |
|--------|---------|
| `_meta` | Index generation metadata |
| `_summary` | Counts by alignment status |
| `_outcome_summary` | Counts by outcome alignment |
| `_issue_summary` | Counts by issue type |
| `_brick_summary` | Stats grouped by brick |
| `_layer_summary` | Stats grouped by layer |
| `spec` | Per-spec summary (one per spec) |

**Rationale for index:**
- Single file to load for dashboards/reports
- Enables queries without reading all individual audits
- Regenerated from individual audits (derived, not authoritative)

---

## Query Examples

### Using jq

```bash
# All unverified specs
jq -r 'select(.spec and .status == "UNVERIFIED") | .spec' jig/audits/index.ndjson

# Specs with score below 80%
jq -r 'select(.spec and .score < 80) | "\(.spec): \(.score)%"' jig/audits/index.ndjson

# Count by status
jq 'select(._summary) | ._summary' jig/audits/index.ndjson

# Average score by brick
jq 'select(._brick_summary) | ._brick_summary' jig/audits/index.ndjson

# Specs missing outcome linkage
jq -r 'select(.spec and .outcome == null) | .spec' jig/audits/index.ndjson

# All implementations of a specific spec
jq 'select(.impl)' jig/audits/audit-S-001.ndjson

# All high-severity issues across all audits
grep -h '"severity":"HIGH"' jig/audits/audit-*.ndjson | jq -r '"\(.location): \(.description)"'

# Specs in a specific brick
jq -r 'select(.spec and .brick == "B-validation") | .spec' jig/audits/index.ndjson
```

### Using grep

```bash
# Find specs with coverage gaps
grep '"COVERAGE_GAP"' jig/audits/audit-*.ndjson | cut -d: -f1 | sort -u

# Count total issues
grep -c '"issue":' jig/audits/audit-*.ndjson

# Find all hollow implementations
grep '"HOLLOW_IMPL"' jig/audits/audit-*.ndjson
```

### Using standard shell

```bash
# Generate work items for unverified specs
jq -r 'select(.spec and .status == "UNVERIFIED") | "TODO: Add tests for \(.spec)"' \
  jig/audits/index.ndjson

# Find functions implementing unverified specs
for spec in $(jq -r 'select(.status == "UNVERIFIED") | .spec' jig/audits/index.ndjson); do
  echo "=== $spec ==="
  jq -r 'select(.impl) | "  \(.impl) at \(.file):\(.line)"' jig/audits/audit-$spec.ndjson
done

# Specs grouped by outcome
jq -rs '[.[] | select(.spec)] | group_by(.outcome) | .[] | {outcome: .[0].outcome, specs: [.[].spec]}' \
  jig/audits/index.ndjson
```

---

## Bulk Operations

### Generate Issue Report

```bash
# Create markdown report of all issues
echo "# Audit Issues Report"
echo ""
echo "Generated: $(date)"
echo ""

for severity in HIGH MEDIUM LOW; do
  echo "## $severity Severity"
  echo ""
  grep "\"severity\":\"$severity\"" jig/audits/audit-*.ndjson | \
    jq -r '"- **\(.issue)** at `\(.location)`: \(.description)"'
  echo ""
done
```

### Create Work Items

```bash
# Generate GitHub issues for all UNVERIFIED specs
jq -r 'select(.spec and .status == "UNVERIFIED") |
  "gh issue create --title \"Add tests for \(.spec)\" --body \"Spec \(.spec) is implemented but has no verifying tests.\n\nBrick: \(.brick)\nScore: \(.score)%\""' \
  jig/audits/index.ndjson | sh
```

### Regenerate Index

```bash
# Rebuild index from individual audits
{
  echo '{"_meta":{"generated_at":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","total_specs":'$(ls jig/audits/audit-S-*.ndjson | wc -l)',"schema_version":"1"}}'

  # Aggregate summaries...
  cat jig/audits/audit-*.ndjson | jq -s '
    [.[] | select(._status)] |
    group_by(._status.alignment) |
    map({(.[0]._status.alignment): length}) |
    add' | jq -c '{_summary: .}'

  # Per-spec summaries
  for f in jig/audits/audit-S-*.ndjson; do
    jq -s '.[0] as $meta | .[1] as $status |
      {spec: $meta._meta.spec_id, status: $status._status.alignment, score: $status._status.score}' "$f"
  done
} > jig/audits/index.ndjson
```

---

## Historical Tracking

For trend analysis, maintain snapshots of the index.

### Directory Structure

```
jig/audits/
├── current/              # Latest audits
│   ├── index.ndjson
│   └── audit-*.ndjson
└── snapshots/            # Point-in-time snapshots
    ├── 2025-12-01/
    │   └── index.ndjson  # Just the index, not full audits
    ├── 2025-12-06/
    │   └── index.ndjson
    └── ...
```

### Trend Query

```bash
# Alignment trend over time
for snapshot in jig/audits/snapshots/*/index.ndjson; do
  date=$(dirname $snapshot | xargs basename)
  perfect=$(jq 'select(._summary) | ._summary.PERFECT' "$snapshot")
  total=$(jq 'select(._meta) | ._meta.total_specs' "$snapshot")
  echo "$date: $perfect/$total perfect"
done
```

---

## SQLite Export (Optional)

For complex queries, export to SQLite.

```bash
# Export command
jigy audit export --format sqlite --output audits.db

# Example queries
sqlite3 audits.db "
  SELECT spec_id, status, score
  FROM specs
  WHERE brick = 'B-validation'
  ORDER BY score ASC
"

sqlite3 audits.db "
  SELECT outcome_id, COUNT(*) as spec_count, AVG(score) as avg_score
  FROM specs
  GROUP BY outcome_id
  ORDER BY avg_score ASC
"

sqlite3 audits.db "
  SELECT issue_type, COUNT(*)
  FROM issues
  GROUP BY issue_type
  ORDER BY COUNT(*) DESC
"
```

**Note:** NDJSON remains the source of truth (git-tracked). SQLite is a derived view for ad-hoc analysis.

---

## CLI Commands

### Proposed Interface

```bash
# Run audit for single spec
jigy audit run S-001

# Run audit for all specs
jigy audit run --all

# Run audit for specs in a brick
jigy audit run --brick B-validation

# Regenerate index from individual audits
jigy audit index

# Query audits
jigy audit query --status UNVERIFIED
jigy audit query --brick B-core-utils --min-score 90
jigy audit query --issues HIGH

# Export to other formats
jigy audit export --format csv --output audits.csv
jigy audit export --format sqlite --output audits.db
jigy audit export --format markdown --output AUDIT_REPORT.md

# Create snapshot
jigy audit snapshot

# Show trend
jigy audit trend --days 30
```

---

## Agent Instructions

The audit agent prompt at `jig/agents/audit-specification.md` should be updated to:

1. **Produce dual output**: Both `.md` (human) and `.ndjson` (machine)
2. **Follow schema**: Use the record types defined in this document
3. **Assign issue types**: Classify problems using the standard issue taxonomy
4. **Calculate scores**: Use consistent scoring algorithm

### Scoring Algorithm

```
criteria_impl = count of acceptance criteria with implementing functions
criteria_verify = count of acceptance criteria with verifying tests
coverage_pairs = count of (impl, test) pairs where test covers impl

impl_score = criteria_impl / total_criteria * 100
verify_score = criteria_verify / total_criteria * 100
coverage_score = coverage_pairs / expected_pairs * 100

overall_score = (impl_score + verify_score + coverage_score) / 3
```

---

## Design Decisions

### Why NDJSON per audit?

- Each line is independently parseable
- Can grep for specific record types: `grep '"impl":' audit-S-001.ndjson`
- Clean git diffs when audit is updated
- Schema allows evolution (add fields without breaking)

### Why separate index file?

- Fast queries without loading 43+ individual files
- Dashboard can read single file
- Derived from authoritative individual audits
- Can be regenerated if corrupted

### Why not a database?

- Git can't track binary files well
- Requires additional tooling
- NDJSON + jq handles 90% of use cases
- SQLite export available for complex analysis

### Why dual output (markdown + NDJSON)?

- Humans need readable reports
- Machines need structured data
- Neither format serves both needs
- Generation cost is minimal

---

## References

- **J017**: JIG Concept v9 (S-F-T triangle, alignment measurement)
- **J022**: Alignment Change Detection (when to re-audit)
- **A001**: Core Artifacts Contract (artifact schemas)
- **jig/agents/audit-specification.md**: Agent prompt for running audits

---

## Next Steps

1. **Formalize schema**: Create JSON Schema for audit records
2. **Implement CLI**: Add `jigy audit` commands
3. **Update agent prompt**: Produce dual output per this spec
4. **Build index generator**: Script to aggregate individual audits
5. **Add to CI**: Run audits on PR, fail on regressions

---

_Machine-readable audits enable machine-assisted improvement._
