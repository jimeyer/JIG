---
title: "J023: Audit Records and Triggers"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1765161786
created_human: "2025-12-07 20:43 CST"
parent: "[[J017_JIG-Concept-v9]]"
children: []
---
# J023: Audit Records and Triggers

**Status:** Proposal
**Date:** 2025-12-07 (revised 2025-12-16)
**Builds On:** J022 (Content Hashing), J026 (Audit Architecture)
**Related:** J024 (Audit Report Format), J025 (Audit Agents), J028 (Coverage Audit)

---

## Context

The JIG system tracks alignment between specifications (S), functions (F), and tests (T). This document addresses two related concerns:

1. **Audit Records** — How audit decisions are stored and queried
2. **Triggers** — How JIG detects which edges need audit

These belong together because **triggers are meaningless without audit records**. The trigger detection algorithm compares current graph hashes (from J022) against the last audited hashes stored in audit records. Without audit records, all edges would simply show as "new."

### The S-F-T-O Graph

JIG tracks four edge types in the alignment graph:

| Edge | Meaning | Question Answered |
|------|---------|-------------------|
| F→S | Function implements spec | Does implementation fulfill spec? |
| T→S | Test verifies spec | Does test validate spec? |
| T→F | Test covers function | Does test execute function? |
| O→S | Outcome specifies spec | Does outcome correctly decompose into specs? |

A change to ANY node (S, F, T, or O) could break alignment. All four edge types need audit tracking.

### What J023 Does

- Stores audit decisions in an append-only log (per-activity)
- Points to detailed records (NDJSON) or reports (Markdown) for edge-level data
- Computes which edges need audit (triggers)
- Provides CLI for recording audits and viewing triggers
- Enables auditor diff workflow via `git_commit`

### What J023 Does NOT Do

- Compute content hashes (that's J022)
- Perform audits or judge alignment (that's J025)
- Define report prose format (that's J024)

### Relationship to Other Documents

| Document | Role |
|----------|------|
| **J022** | Computes `jig_hash` for S, F, T, O nodes |
| **J024** | Defines audit report format (Markdown for semantic audits) |
| **J025** | Describes audit strategies and agents |
| **J026** | Architecture decisions (this doc implements J026) |
| **J028** | Coverage audit specifics (T→F edges) |
| **J023** (this) | Stores audit records, detects triggers |

**The flow:**
```
J022 (hash) → J023 (compare → trigger) → J025 (audit) → J023 (record)
                                              ↓
                                    J024 (report) or J028 (coverage record)
```

---

## Part 1: Two-Level Audit Model

### The Core Insight

Different audit types produce different amounts of data:

| Audit Type | Edges | Output Type |
|------------|-------|-------------|
| Semantic (F→S, T→S, O→S) | Few (1-10) | Prose reasoning |
| Coverage (T→F) | Many (100s-1000s) | Structured data |

A per-edge log format works for semantic audits but creates log bloat for coverage. Solution: **two-level storage**.

### Architecture

```
jig/audits/
├── audit-log.ndjson          # One entry per audit ACTIVITY
├── records/                   # NDJSON files (structured data)
│   └── coverage-2025-12-16.ndjson
└── reports/                   # Markdown files (prose reasoning)
    └── S-040-2025-12-16.md
```

**Level 1: Audit Log** — Compact log of audit activities (one row per audit run)

**Level 2: Records/Reports** — Detailed per-edge data
- **Records** (NDJSON): For structured data (coverage T→F edges)
- **Reports** (Markdown): For prose reasoning (semantic F→S, T→S, O→S audits)

### Log Entry Points to Detail File

Each audit log entry points to either a `record` (NDJSON) or `report` (Markdown):

```json
{"id": "coverage-2025-12-16", "type": "coverage", "record": "records/coverage-2025-12-16.ndjson", ...}
{"id": "S-040-2025-12-16", "type": "spec", "report": "reports/S-040-2025-12-16.md", ...}
```

The `record` and `report` fields are **mutually exclusive**.

---

## Part 2: Audit Log Schema

### Location

```
jig/audits/audit-log.ndjson
```

**Rationale:**
- Lives in `jig/audits/` alongside records and reports
- NDJSON format matches other JIG artifacts
- Git-tracked for shared history

### Format

**NDJSON** (Newline-Delimited JSON): One audit activity per line, appended chronologically.

### Entry Schema

Each log entry represents one audit activity:

```json
{
  "id": "S-040-2025-12-16",
  "type": "spec",
  "git_commit": "abc1234",
  "timestamp": "2025-12-16T14:32:00Z",
  "method": "tiered-v1",
  "summary": {
    "edges": 3,
    "aligned": 3,
    "diverged": 0
  },
  "report": "reports/S-040-2025-12-16.md"
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for this audit activity |
| `type` | enum | Yes | Audit type: `spec`, `outcome`, `coverage` |
| `git_commit` | string | Yes | Git commit where audit was performed |
| `timestamp` | ISO 8601 | Yes | When audit was performed |
| `method` | string | Yes | Audit method identifier (see J025) |
| `summary` | object | Yes | Summary counts (varies by type) |
| `record` | string | Conditional | Path to NDJSON record file (for coverage) |
| `report` | string | Conditional | Path to Markdown report file (for semantic) |

**Note:** Exactly one of `record` or `report` must be present.

### Summary Fields by Type

**Spec audit (`type: "spec"`):**
```json
"summary": {"edges": 3, "aligned": 2, "diverged": 1, "inconclusive": 0}
```

**Outcome audit (`type: "outcome"`):**
```json
"summary": {"edges": 5, "aligned": 4, "diverged": 1, "inconclusive": 0}
```

**Coverage audit (`type: "coverage"`):**
```json
"summary": {"tests": 89, "functions": 312, "edges": 847}
```

### Examples

**Spec audit:**
```json
{"id":"S-040-2025-12-16","type":"spec","git_commit":"abc1234","timestamp":"2025-12-16T14:32:00Z","method":"tiered-v1","summary":{"edges":3,"aligned":3,"diverged":0,"inconclusive":0},"report":"reports/S-040-2025-12-16.md"}
```

**Coverage audit:**
```json
{"id":"coverage-2025-12-16","type":"coverage","git_commit":"abc1234","timestamp":"2025-12-16T14:32:00Z","method":"pytest-cov","summary":{"tests":89,"functions":312,"edges":847},"record":"records/coverage-2025-12-16.ndjson"}
```

**Git commit requirement:** Audits MUST be performed on committed state. `jigy audit` commands SHALL refuse to record an audit if the working tree has uncommitted changes affecting the audited nodes. This ensures `git_commit` always points to a valid, reproducible state.

---

## Part 3: Record File Format (NDJSON)

Records are used for **structured data** — primarily coverage T→F edges.

### Location

```
jig/audits/records/coverage-YYYY-MM-DD.ndjson
```

### Format

NDJSON with one edge per line:

```ndjson
{"edge":"T→F","from":{"id":"T-test_auth.test_login","jig_hash":"a1b2c3"},"to":{"id":"F-auth.authenticate","jig_hash":"d4e5f6"},"result":"covered"}
{"edge":"T→F","from":{"id":"T-test_auth.test_login","jig_hash":"a1b2c3"},"to":{"id":"F-auth.validate_token","jig_hash":"e5f6a7"},"result":"covered"}
```

### Edge Record Fields

| Field | Type | Description |
|-------|------|-------------|
| `edge` | enum | Edge type: `T→F` |
| `from.id` | string | Source node ID |
| `from.jig_hash` | string | Source node content hash at audit time |
| `to.id` | string | Target node ID |
| `to.jig_hash` | string | Target node content hash at audit time |
| `result` | enum | Audit result (e.g., `covered`, `not_covered`) |

### Result Values for T→F

| Result | Meaning |
|--------|---------|
| `covered` | Test executed ≥1 line of the function |
| `not_covered` | Test did not execute the function |

See J028 for full coverage audit specification.

---

## Part 4: Report File Format (Markdown)

Reports are used for **prose reasoning** — semantic audits of F→S, T→S, and O→S edges.

### Location

```
jig/audits/reports/S-040-2025-12-16.md
jig/audits/reports/O-001-2025-12-16.md
```

### Format

Markdown with YAML frontmatter containing edge results:

```yaml
---
id: S-040-2025-12-16
audited_at: 2025-12-16T14:32:00Z
git_commit: abc1234
method: tiered-v1
edges:
  - edge: F→S
    from: F-jig.cli.layers.layers_command
    to: S-040
    result: aligned
    jig_hash_from: d4e5f6
    jig_hash_to: a1b2c3
  - edge: T→S
    from: T-test_layers.test_layers_command
    to: S-040
    result: aligned
    jig_hash_from: e5f6a7
    jig_hash_to: a1b2c3
---

# Audit Report: S-040

## Summary

All edges aligned. The `layers_command` function correctly implements S-040...

## F→S: layers_command → S-040

[Detailed reasoning...]

## T→S: test_layers_command → S-040

[Detailed reasoning...]
```

### Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Same as log entry ID |
| `audited_at` | ISO 8601 | When audit was performed |
| `git_commit` | string | Git commit at audit time |
| `method` | string | Audit method identifier |
| `edges` | list | Per-edge results with hashes |

### Edge Result Fields (in frontmatter)

| Field | Type | Description |
|-------|------|-------------|
| `edge` | enum | Edge type: `F→S`, `T→S`, `O→S` |
| `from` | string | Source node ID |
| `to` | string | Target node ID |
| `result` | enum | `aligned`, `diverged`, `inconclusive` |
| `jig_hash_from` | string | Source node hash at audit time |
| `jig_hash_to` | string | Target node hash at audit time |

### Result Values for Semantic Edges

| Edge | Results | Meaning |
|------|---------|---------|
| F→S | `aligned`, `diverged`, `inconclusive` | Does impl fulfill spec? |
| T→S | `aligned`, `diverged`, `inconclusive` | Does test verify spec? |
| O→S | `aligned`, `diverged`, `inconclusive` | Does outcome decompose to spec? |

See J024 for full report format specification.

---

## Part 5: Trigger Detection

Triggers identify which edges need audit by comparing current graph hashes against audit records.

### The Core Insight

```
jigy rebuild
    └─→ Computes current jig_hash for S, F, T, O (from J022)
    └─→ Writes to graph files

jigy triggers
    └─→ Reads current graphs (current jig_hash per node)
    └─→ Reads audit records (audited jig_hash per edge)
    └─→ Compares: current vs audited
    └─→ Difference = trigger
```

**Without audit records, everything is "new."** Triggers require a baseline to compare against.

### Finding Audited Hashes

**For semantic audits (F→S, T→S, O→S):**
- Find latest log entry for the relevant spec/outcome
- Read the report file's frontmatter
- Extract per-edge hashes from frontmatter

**For coverage audits (T→F):**
- Find latest coverage log entry
- Read the record file
- Extract per-edge hashes from NDJSON

### Trigger Detection Algorithm

```python
def detect_audit_triggers(
    intent_graph: Graph,
    impl_graph: Graph,
    verif_graph: Graph,
    audit_log: list[dict],
    records_dir: Path,
    reports_dir: Path
) -> list[Trigger]:
    """
    Detect which edges need audit.
    """
    triggers = []

    # Get latest audit per type
    latest_by_type = get_latest_audits_by_type(audit_log)

    # Check F→S and T→S edges (from reports)
    triggers.extend(
        detect_semantic_triggers(intent_graph, impl_graph, verif_graph,
                                 latest_by_type, reports_dir)
    )

    # Check T→F edges (from coverage records)
    triggers.extend(
        detect_coverage_triggers(impl_graph, verif_graph,
                                 latest_by_type.get('coverage'), records_dir)
    )

    return triggers


def detect_semantic_triggers(
    intent_graph, impl_graph, verif_graph, latest_audits, reports_dir
) -> list[Trigger]:
    """Detect F→S, T→S, O→S edges needing audit."""
    triggers = []

    # For each spec, find its latest audit report
    for spec in intent_graph.specs():
        audit = find_latest_audit_for_spec(spec.id, latest_audits)

        if audit is None:
            # Spec never audited
            triggers.append(Trigger(spec.id, reason='new'))
            continue

        # Load report frontmatter
        report_path = reports_dir / audit['report']
        report_edges = load_report_frontmatter(report_path)['edges']

        # Check each edge
        for edge in report_edges:
            current_from = get_node(edge['from'], impl_graph, verif_graph)
            current_to = get_node(edge['to'], intent_graph)

            if current_from.jig_hash != edge['jig_hash_from']:
                triggers.append(Trigger(edge, reason='from_changed'))
            elif current_to.jig_hash != edge['jig_hash_to']:
                triggers.append(Trigger(edge, reason='to_changed'))

    return triggers


def detect_coverage_triggers(
    impl_graph, verif_graph, latest_coverage, records_dir
) -> list[Trigger]:
    """Detect T→F edges needing audit."""
    if latest_coverage is None:
        return [Trigger('coverage', reason='new')]

    record_path = records_dir / latest_coverage['record']
    recorded_edges = load_ndjson(record_path)

    # Build lookup
    recorded_by_key = {
        (r['from']['id'], r['to']['id']): r
        for r in recorded_edges
    }

    triggers = []
    for test in verif_graph.tests():
        for func in impl_graph.functions():
            key = (test.id, func.id)
            recorded = recorded_by_key.get(key)

            if recorded is None:
                triggers.append(Trigger(key, reason='new'))
            elif recorded['from']['jig_hash'] != test.jig_hash:
                triggers.append(Trigger(key, reason='test_changed'))
            elif recorded['to']['jig_hash'] != func.jig_hash:
                triggers.append(Trigger(key, reason='function_changed'))

    return triggers
```

### Trigger Reasons

| Reason | Meaning | Applies To |
|--------|---------|------------|
| `new` | Edge/spec never audited | All |
| `from_changed` | Source node jig_hash differs | F→S, T→S, O→S |
| `to_changed` | Target node jig_hash differs | F→S, T→S, O→S |
| `test_changed` | Test jig_hash differs | T→F |
| `function_changed` | Function jig_hash differs | T→F |
| `removed` | Edge no longer exists in graph | All |

---

## Part 6: Computing Current State

### Spec Status

Spec status is computed from its latest audit report:

```python
def spec_status(spec_id: str, audit_log: list[dict], reports_dir: Path) -> str:
    """Compute overall status for a spec from its audit."""
    audit = find_latest_audit_for_spec(spec_id, audit_log)

    if audit is None:
        return 'unaudited'

    report = load_report_frontmatter(reports_dir / audit['report'])
    edges = report['edges']

    f_s_edges = [e for e in edges if e['edge'] == 'F→S']
    t_s_edges = [e for e in edges if e['edge'] == 'T→S']

    if any(e['result'] == 'diverged' for e in edges):
        return 'diverged'
    if any(e['result'] == 'inconclusive' for e in edges):
        return 'inconclusive'
    if not f_s_edges:
        return 'unimplemented'
    if not t_s_edges:
        return 'unverified'
    return 'aligned'
```

### Outcome Status

```python
def outcome_status(outcome_id: str, audit_log: list[dict], reports_dir: Path) -> str:
    """Compute overall status for an outcome from its audit."""
    audit = find_latest_audit_for_outcome(outcome_id, audit_log)

    if audit is None:
        return 'unaudited'

    report = load_report_frontmatter(reports_dir / audit['report'])
    edges = report['edges']

    if any(e['result'] == 'diverged' for e in edges):
        return 'diverged'
    if any(e['result'] == 'inconclusive' for e in edges):
        return 'inconclusive'
    return 'aligned'
```

---

## Part 7: Log Compaction

Over time, the audit log grows. **Compaction** reduces size by keeping only the latest N records per audit target.

### When to Compact

Compaction is **optional**. Teams should compact when:
- Log file exceeds a size threshold (e.g., >1MB)
- Quarterly maintenance

Teams that need full audit history for compliance should **never compact**.

### Compaction Strategy

```bash
$ jigy audit compact
Compacted audit-log.ndjson: 847 entries → 52 entries
```

Keeps only the most recent entry per (type, target) combination.

**Note:** Compaction does NOT delete record/report files. Old files can be cleaned up separately if desired.

---

## Part 8: CLI Commands

### View Triggers

```bash
$ jigy triggers
Audit Triggers:

  NEW (6):
    spec: S-041 (never audited)
    coverage: (no coverage audit exists)
    ...

  FROM_CHANGED (3):
    F→S: F-jig.cli.layers.layers_command → S-040
      Last audited: commit abc1234
      To see changes: git diff abc1234..HEAD -- src/jig/cli/layers.py
    ...

  TO_CHANGED (1):
    T→S: T-test_validation.test_brick_errors → S-038
      Last audited: commit def5678
      To see changes: git diff def5678..HEAD -- jig/specifications/S-038.md

Summary: 10 triggers
```

### View Audit Status

```bash
$ jigy audit
Audit Status:

  Specs: 45 total
    aligned: 35
    diverged: 3
    unverified: 5
    unimplemented: 2

  Coverage:
    Last run: 2025-12-16 (commit abc1234)
    T→F edges: 847

  Recent Activity:
    2025-12-16: coverage (pytest-cov)
    2025-12-15: S-040 audit (tiered-v1)
    2025-12-14: S-038 audit (tiered-v1)

Use 'jigy triggers' to see edges needing re-audit.
```

### View Audit History

```bash
$ jigy audit history S-040
Audit history for S-040:

  2025-12-16  aligned  (tiered-v1)  commit abc1234
    Report: reports/S-040-2025-12-16.md

  2025-11-20  aligned  (human-review)  commit 9876543
    Report: reports/S-040-2025-11-20.md

To see what changed between audits:
  git diff 9876543..abc1234 -- jig/specifications/S-040.md
```

### Compact Log

```bash
$ jigy audit compact
Compacted audit-log.ndjson: 847 entries → 52 entries
```

---

## Part 9: File Structure

```
jig/
├── specifications/
│   └── S-040.md
├── outcomes/
│   └── O-001.md
├── bricks.yaml
├── generated/
│   ├── intent-graph.ndjson
│   ├── implementation-graph.ndjson
│   └── verification-graph.ndjson
└── audits/
    ├── audit-log.ndjson              # Activity log
    ├── records/                       # NDJSON (structured)
    │   ├── coverage-2025-12-15.ndjson
    │   └── coverage-2025-12-16.ndjson
    └── reports/                       # Markdown (prose)
        ├── S-040-2025-12-15.md
        ├── S-040-2025-12-16.md
        └── O-001-2025-12-16.md
```

---

## Part 10: Workflow Integration

### Development Workflow

```
1. Developer modifies F-jig.cli.layers.layers_command

2. Developer runs `jigy rebuild`
   └─→ Function's jig_hash changes in implementation-graph.ndjson

3. Developer runs `jigy triggers`
   └─→ Reports: "F→S: from_changed for S-040"

4. Developer (or agent) performs audit
   └─→ Creates report: reports/S-040-2025-12-16.md
   └─→ Appends entry to audit-log.ndjson

5. Next `jigy triggers` shows no trigger
   └─→ jig_hash in report matches current jig_hash
```

### CI Integration

```yaml
# .github/workflows/jig.yml
- name: Rebuild graphs
  run: jigy rebuild

- name: Run coverage audit
  run: jigy audit coverage

- name: Check for triggers
  run: |
    triggers=$(jigy triggers --format json)
    if [ $(echo "$triggers" | jq '.total') -gt 0 ]; then
      echo "::warning::Audit triggers detected"
      jigy triggers
    fi
```

---

## Consequences

### What This Enables

1. **Compact audit log** — One entry per activity, not per edge
2. **Flexible detail storage** — Records (NDJSON) for data, reports (Markdown) for reasoning
3. **Granular trigger detection** — Per-edge hash comparison
4. **Full history** — Append-only log preserves audit trail
5. **Team coordination** — Shared audit state across developers

### What This Constrains

1. **Two-level lookup** — Must read detail file for per-edge data
2. **File management** — More files to track (records/, reports/)
3. **Audit discipline** — Team must actually record decisions

---

## References

- **J022:** Content Hashing (computes `jig_hash` for S, F, T, O nodes)
- **J024:** Audit Report Format (Markdown report specification)
- **J025:** Audit Agents (how audits are performed)
- **J026:** Audit Architecture Simplification (design rationale)
- **J028:** Coverage Audit (T→F record specification)
- **A001:** Core Artifacts Contract (artifact schemas)

---

_The log records what happened. The detail files explain why._
