---
title: "J026: Audit Architecture Simplification"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1765161786
created_human: "2025-12-07 20:43 CST"
parent: "[[J017_JIG-Concept-v9]]"
children: []
---
# J026: Audit Architecture Simplification

**Status:** Proposal
**Date:** 2025-12-07
**Refactors:** J023, J024
**Refined by:** J023 (revised 2025-12-16), J028 (Coverage Audit)

---

## Note: Two-Level Model Evolution

This document established the foundational architecture for JIG audits. The implementation has evolved to use a **two-level model**:

1. **Audit Log** — One entry per audit activity (not per edge)
2. **Detail Files** — Records (NDJSON) for coverage, Reports (Markdown) for semantic audits

See J023 (revised) for the current schema and J028 for coverage audit specifics. The principles in this document remain valid; the storage model has been refined.

---

## Context

After refactoring J022 (Content Hashing) and J023 (Audit Records and Triggers), a review of J024 (Audit Strategies and Mechanisms) revealed architectural redundancy and unclear responsibilities.

**Key insight from review:** The original J023 was under-engineered in one dimension (only tracked spec changes) and over-engineered in another (complex per-pair schema). We need to:

1. Track changes to ALL parts of the S-F-T triangle (specs, functions, tests)
2. Support T→F coverage audits as a first-class audit type
3. Simplify the schema with clear nesting

**The S-F-T Triangle has three edge types:**

| Edge | Meaning | Example Question |
|------|---------|------------------|
| F→S | Function implements spec | Does impl fulfill spec? |
| T→S | Test verifies spec | Does test validate spec? |
| T→F | Test covers function | Does test execute function? |

A change to ANY node (S, F, or T) could break alignment. All three edge types need audit tracking.

---

## Decisions

### 1. Audit Log is Per-Edge

The audit log stores one row per edge audited. An audit activity that reviews a spec with 3 implementations and 2 tests produces 5+ log rows (one per edge).

This enables:
- **Granular trigger detection** — detect which specific edge changed
- **Partial audits** — audit some edges now, others later
- **Coverage-only audits** — batch T→F audits without spec involvement

### 2. Audit Log Schema

Each log row represents one audited edge with a nested structure:

```json
{
  "edge": "T→F",
  "git_commit": "abc1234",
  "from": {
    "id": "T-test_layers.test_layers_command",
    "jig_hash": "c7d8e9"
  },
  "to": {
    "id": "F-jig.cli.layers.layers_command",
    "jig_hash": "d4e5f6"
  },
  "report": {
    "result": "covered",
    "confidence": 1.0,
    "method": "pytest-cov",
    "file": "audit-coverage-2025-12-07.md"
  }
}
```

**Compact NDJSON (one line per edge):**
```json
{"edge":"T→F","git_commit":"abc1234","from":{"id":"T-test_layers.test_layers_command","jig_hash":"c7d8e9"},"to":{"id":"F-jig.cli.layers.layers_command","jig_hash":"d4e5f6"},"report":{"result":"covered","confidence":1.0,"method":"pytest-cov","file":"audit-coverage-2025-12-07.md"}}
```

### 3. Field Definitions

**Top-level fields:**

| Field | Type | Description |
|-------|------|-------------|
| `edge` | enum | Edge type: `F→S`, `T→S`, `T→F` |
| `git_commit` | string | Git commit where nodes were audited |
| `from` | object | Source node (F-xxx or T-xxx) |
| `to` | object | Target node (S-xxx or F-xxx) |
| `report` | object | Audit judgment |

**Node fields (`from`, `to`):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Node identifier (F-xxx, T-xxx, S-xxx) |
| `jig_hash` | string | Content hash at audit time (from J022) |

**Report fields:**

| Field | Type | Description |
|-------|------|-------------|
| `result` | enum | Audit verdict |
| `confidence` | float | 0.0-1.0, calibration score |
| `method` | string | Audit method identifier |
| `file` | string | Path to detailed report file |

### 4. Result Values by Edge Type

| Edge | Results | Meaning |
|------|---------|---------|
| F→S | `aligned`, `diverged`, `inconclusive` | Does impl fulfill spec? |
| T→S | `aligned`, `diverged`, `inconclusive` | Does test verify spec? |
| T→F | `covered`, `not_covered` | Does test execute function? |

**Additional result for all edge types:**
- `error` — Audit failed to run (API error, timeout, etc.)

### 5. Audit Report Format

The report file contains human-readable analysis. Metadata (timestamp, auditor) lives in the report, not the log.

**Frontmatter:**

```yaml
---
audited_at: 2025-12-07T14:32:00Z
by: agent
method: tiered-v1
edges:
  - edge: F→S
    from: F-jig.cli.layers.layers_command
    to: S-040
  - edge: T→S
    from: T-test_layers.test_layers_command
    to: S-040
  - edge: T→F
    from: T-test_layers.test_layers_command
    to: F-jig.cli.layers.layers_command
---

# Audit Report

[Human-readable analysis produced by the audit method...]
```

**The report:**
- Lists all edges audited in frontmatter
- Contains detailed reasoning in prose
- Is referenced by log rows via `report.file`

**Report naming:** Freeform. Examples:
- `audit-S-040.md` — spec-focused audit
- `audit-coverage-2025-12-07.md` — batch coverage run
- `audit-B-cli-2025-12-07.md` — brick-focused audit

### 6. Trigger Detection

Trigger detection compares current graph hashes to audit log:

```python
def detect_triggers(current_graph, audit_log_path):
    """Detect edges needing re-audit based on hash changes."""
    # Get latest audit per edge from log
    latest = {}
    for record in read_ndjson(audit_log_path):
        key = (record['edge'], record['from']['id'], record['to']['id'])
        latest[key] = record

    triggers = []
    for edge in current_graph.all_edges():  # F→S, T→S, T→F
        key = (edge.type, edge.from_id, edge.to_id)
        last_audit = latest.get(key)

        if not last_audit:
            triggers.append(Trigger(edge, reason='new'))
        elif last_audit['from']['jig_hash'] != edge.from_node.jig_hash:
            triggers.append(Trigger(edge, reason='from_changed'))
        elif last_audit['to']['jig_hash'] != edge.to_node.jig_hash:
            triggers.append(Trigger(edge, reason='to_changed'))

    return triggers
```

**Trigger reasons:**

| Reason | Meaning |
|--------|---------|
| `new` | Edge never audited |
| `from_changed` | Source node hash changed |
| `to_changed` | Target node hash changed |

### 7. Overall Spec Status (Computed)

Spec status is NOT stored in the log. It's computed from log rows:

```python
def spec_status(spec_id, audit_log):
    """Compute overall status for a spec from its edge audits."""
    f_s_edges = [r for r in audit_log
                 if r['edge'] == 'F→S' and r['to']['id'] == spec_id]
    t_s_edges = [r for r in audit_log
                 if r['edge'] == 'T→S' and r['to']['id'] == spec_id]

    all_edges = f_s_edges + t_s_edges

    if any(e['report']['result'] == 'diverged' for e in all_edges):
        return 'diverged'
    if any(e['report']['result'] == 'inconclusive' for e in all_edges):
        return 'inconclusive'
    if not f_s_edges:
        return 'unimplemented'
    if not t_s_edges:
        return 'unverified'
    return 'aligned'
```

### 8. Coverage-Only Audits

A batch test coverage run is a valid audit activity:

**Report:** `audit-coverage-2025-12-07.md`
```yaml
---
audited_at: 2025-12-07T14:32:00Z
by: ci
method: pytest-cov
edges:
  - edge: T→F
    from: T-test_auth.test_login
    to: F-auth.authenticate
  - edge: T→F
    from: T-test_auth.test_login
    to: F-auth.validate_token
  # ... hundreds of T→F edges
---

# Coverage Analysis Report

Full test suite coverage run...
```

**Log rows:** One per T→F edge, all pointing to same report file.

This enables:
- Batch coverage analysis across entire test suite
- T→F edges audited independently of specs
- Trigger detection when tests or functions change

### 9. Partial Audits

Partial audits are valid. If spec S-040 has 5 implementing functions:
- Auditor can audit 2 of them now
- Log has 2 rows for the 2 audited edges
- The other 3 edges have no audit record
- `jigy triggers` shows the 3 unaudited edges as `new`

No need for "complete audit" semantics. Unaudited edges simply trigger.

---

## Resulting Architecture

```
jig/audits/
├── audit-log.ndjson              # Per-edge audit records
├── audit-S-040.md                # Spec-focused report
├── audit-coverage-2025-12-07.md  # Coverage run report
└── ...
```

**Data flow:**

```
jigy rebuild
  └─→ Computes jig_hash for S, F, T nodes (J022)
  └─→ Stores in graphs

jigy triggers
  └─→ Reads current graphs (current hashes)
  └─→ Reads audit-log.ndjson (audited hashes)
  └─→ Compares hashes for each edge → triggers

jigy audit run S-040 --method tiered-v1
  └─→ Performs audit (J025 strategies)
  └─→ Writes audit-S-040.md (human readable report)
  └─→ Appends N rows to audit-log.ndjson (one per edge)

jigy coverage --audit
  └─→ Runs test suite with coverage
  └─→ Writes audit-coverage-YYYY-MM-DD.md
  └─→ Appends T→F rows to audit-log.ndjson
```

---

## Example Queries

```bash
# All edges at a specific commit
jq 'select(.git_commit == "abc1234")' audit-log.ndjson

# All diverged F→S edges
jq 'select(.edge == "F→S" and .report.result == "diverged")' audit-log.ndjson

# Low confidence audits (candidates for re-audit)
jq 'select(.report.confidence < 0.7)' audit-log.ndjson

# All edges for a specific spec
jq 'select(.to.id == "S-040")' audit-log.ndjson

# Get report file for edges from a specific test
jq -r 'select(.from.id | startswith("T-")) | .report.file' audit-log.ndjson

# Count edges by method
jq -s 'group_by(.report.method) | map({method: .[0].report.method, count: length})' audit-log.ndjson

# Find uncovered T→F edges
jq 'select(.edge == "T→F" and .report.result == "not_covered")' audit-log.ndjson
```

---

## Changes Required

### J023 (Audit Records and Triggers)

1. **Rewrite audit-log schema:**
   - Per-edge rows (F→S, T→S, T→F)
   - Nested structure: edge, git_commit, from{}, to{}, report{}
   - Remove `ts`, `by` (move to report)

2. **Update trigger detection:**
   - Check all three edge types
   - Compare both `from.jig_hash` and `to.jig_hash`

3. **Remove spec-centric sections:**
   - No "current state computation" per spec
   - Spec status is computed from edges

### J024 (Audit Report Format)

1. **Rename from "Audit Strategies and Mechanisms"**

2. **Define report frontmatter:**
   - `audited_at`, `by`, `method`
   - `edges` list with edge type, from, to

3. **Remove index.ndjson entirely**

4. **Provide guidelines for report prose**

### J025 (Audit Agents)

1. **Document method identifiers** (e.g., `tiered-v1`, `pytest-cov`)
2. **Define confidence computation** per method
3. **Clarify agents produce:**
   - One report file (markdown)
   - Multiple log rows (one per edge)

---

## Benefits

1. **Full S-F-T coverage** — changes to any node trigger re-audit
2. **T→F as first-class citizen** — coverage audits work independently
3. **Granular tracking** — per-edge, not per-spec
4. **Partial audits** — audit what you can, trigger on the rest
5. **Clean schema** — nested structure, clear responsibilities
6. **Batch operations** — coverage runs produce many log rows efficiently

---

## Open Questions

1. **Report per audit activity vs per spec?** Current design allows either. A single audit activity can produce one report covering multiple specs, or separate reports per spec.

2. **Method registry?** Should method identifiers be documented in a registry file, or is J025 documentation sufficient?

3. **Confidence for coverage?** T→F coverage is deterministic (confidence=1.0). Should we omit confidence for coverage edges, or keep for schema uniformity?

4. **Edge removal detection?** If an edge is removed from the graph (decorator deleted), should we detect and flag it? Currently only tracks edges that exist.

---

## References

- **J022:** Content Hashing (computes jig_hash for S, F, T nodes)
- **J023:** Audit Records and Triggers (to be updated per this doc)
- **J024:** Audit Report Format (to be renamed and updated)
- **J025:** Audit Agents (defines methods and confidence)
- **J017:** JIG Concept v9 (S-F-T triangle)

---

_Every edge tells a story. The log remembers them all._
