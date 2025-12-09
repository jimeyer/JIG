# J023: Audit Records and Triggers

**Status:** Proposal
**Date:** 2025-12-07
**Builds On:** J022 (Content Hashing), J026 (Audit Architecture)
**Related:** J024 (Audit Report Format), J025 (Audit Agents)

---

## Context

The JIG system tracks alignment between specifications (S), functions (F), and tests (T). This document addresses two related concerns:

1. **Audit Records** — How audit decisions are stored and queried
2. **Triggers** — How JIG detects which edges need audit

These belong together because **triggers are meaningless without audit records**. The trigger detection algorithm compares current graph hashes (from J022) against the last audited hashes stored in audit records. Without audit records, all edges would simply show as "new."

### The S-F-T-O Graph

JIG tracks four edge types in the alignment graph:

| Edge | Meaning                  | Question Answered                            |
| ---- | ------------------------ | -------------------------------------------- |
| F→S  | Function implements spec | Does implementation fulfill spec?            |
| T→S  | Test verifies spec       | Does test validate spec?                     |
| T→F  | Test covers function     | Does test execute function?                  |
| O→S  | Outcome specifies spec   | Does outcome correctly decompose into specs? |
|      |                          |                                              |

A change to ANY node (S, F, T, or O) could break alignment. All four edge types need audit tracking.

### What J023 Does

- Stores audit decisions in an append-only log (per-edge)
- Computes which edges need audit (triggers)
- Provides CLI for recording audits and viewing triggers
- Enables auditor diff workflow via `git_commit`

### What J023 Does NOT Do

- Compute content hashes (that's J022)
- Perform audits or judge alignment (that's J025)
- Define report format (that's J024)

### Relationship to Other Documents

| Document | Role |
|----------|------|
| **J022** | Computes `jig_hash` for S, F, T, O nodes |
| **J024** | Defines audit report format (.md files) |
| **J025** | Describes audit strategies and agents |
| **J026** | Architecture decisions (this doc implements J026) |
| **J023** (this) | Stores audit records, detects triggers |

**The flow:**
```
J022 (hash) → J023 (compare → trigger) → J025 (audit) → J023 (record)
                                              ↓
                                         J024 (report)
```

---

## Part 1: Audit Records

When a human or agent audits alignment for an edge, the decision is recorded in an append-only log.

### Core Principle: Append-Only Log

The audit log is an **append-only** record of audit decisions. Each audit appends new records (one per edge); existing records are never modified or deleted (except via explicit compaction).

**Design pattern:** Modeled after **Kafka log compaction**.

**Why append-only?**
- **Git-friendly:** Appends show as additions, not modifications — cleaner diffs
- **No merge conflicts:** Concurrent audits just append separate records
- **Full history:** Complete audit trail is preserved
- **Compliance-ready:** Immutable history (like accounting ledgers)
- **Metrics-enabled:** Can analyze audit frequency, trends, methods used

**Current state is computed** from the log by finding the latest record per edge.

---

## Audit Log Schema

### Location

```
jig/audits/audit-log.ndjson
```

**Rationale:**
- Lives in `jig/audits/` alongside audit reports (J024)
- NDJSON format matches other JIG artifacts
- Git-tracked for shared history

### Format

**NDJSON** (Newline-Delimited JSON): One audit record per line, appended chronologically. Each line represents one audited edge.

### Record Schema

Each log row represents one audited edge with a nested structure:

```json
{
  "edge": "F→S",
  "git_commit": "abc1234",
  "from": {
    "id": "F-jig.cli.layers.layers_command",
    "jig_hash": "d4e5f6"
  },
  "to": {
    "id": "S-040",
    "jig_hash": "a1b2c3"
  },
  "report": {
    "result": "aligned",
    "confidence": 0.9,
    "method": "tiered-v1",
    "file": "audit-S-040.md"
  }
}
```

**Compact NDJSON (one line per edge):**
```json
{"edge":"F→S","git_commit":"abc1234","from":{"id":"F-jig.cli.layers.layers_command","jig_hash":"d4e5f6"},"to":{"id":"S-040","jig_hash":"a1b2c3"},"report":{"result":"aligned","confidence":0.9,"method":"tiered-v1","file":"audit-S-040.md"}}
```

### Field Definitions

**Top-level fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `edge` | enum | Yes | Edge type: `F→S`, `T→S`, `T→F`, `O→S` |
| `git_commit` | string | Yes | Git commit where nodes were audited |
| `from` | object | Yes | Source node |
| `to` | object | Yes | Target node |
| `report` | object | Yes | Audit judgment |

**Node fields (`from`, `to`):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Node identifier (F-xxx, T-xxx, S-xxx, O-xxx) |
| `jig_hash` | string | Yes | Content hash at audit time (from J022) |

**Report fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `result` | enum | Yes | Audit verdict |
| `confidence` | float | Yes | 0.0-1.0, calibration score |
| `method` | string | Yes | Audit method identifier |
| `file` | string | Yes | Path to detailed report file |

**Git commit requirement:** Audits MUST be performed on committed state. `jigy audit` commands SHALL refuse to record an audit if the working tree has uncommitted changes affecting the audited nodes. This ensures `git_commit` always points to a valid, reproducible state.

### Result Values by Edge Type

| Edge | Results | Meaning |
|------|---------|---------|
| F→S | `aligned`, `diverged`, `inconclusive` | Does impl fulfill spec? |
| T→S | `aligned`, `diverged`, `inconclusive` | Does test verify spec? |
| T→F | `covered`, `not_covered` | Does test execute function? |
| O→S | `aligned`, `diverged`, `inconclusive` | Does outcome correctly decompose into specs? |

**Additional result for all edge types:**
- `error` — Audit failed to run (API error, timeout, etc.)

**O→S alignment criteria:**
- `aligned` — The spec addresses part of the outcome's intent; the outcome logically decomposes into this spec
- `diverged` — The spec does not contribute to the outcome, or the outcome's intent has changed making this spec irrelevant
- `inconclusive` — Cannot determine if spec addresses outcome (outcome too vague, spec too abstract)

### Examples

**F→S edge (function implements spec):**
```json
{"edge":"F→S","git_commit":"abc1234","from":{"id":"F-jig.cli.layers.layers_command","jig_hash":"d4e5f6"},"to":{"id":"S-040","jig_hash":"a1b2c3"},"report":{"result":"aligned","confidence":0.9,"method":"tiered-v1","file":"audit-S-040.md"}}
```

**T→S edge (test verifies spec):**
```json
{"edge":"T→S","git_commit":"abc1234","from":{"id":"T-test_layers.test_layers_command","jig_hash":"c7d8e9"},"to":{"id":"S-040","jig_hash":"a1b2c3"},"report":{"result":"aligned","confidence":0.85,"method":"tiered-v1","file":"audit-S-040.md"}}
```

**T→F edge (test covers function):**
```json
{"edge":"T→F","git_commit":"abc1234","from":{"id":"T-test_layers.test_layers_command","jig_hash":"c7d8e9"},"to":{"id":"F-jig.cli.layers.layers_command","jig_hash":"d4e5f6"},"report":{"result":"covered","confidence":1.0,"method":"pytest-cov","file":"audit-coverage-2025-12-07.md"}}
```

**O→S edge (outcome specifies spec):**
```json
{"edge":"O→S","git_commit":"abc1234","from":{"id":"O-001","jig_hash":"f1a2b3"},"to":{"id":"S-001","jig_hash":"a1b2c3"},"report":{"result":"aligned","confidence":0.85,"method":"tiered-v1","file":"audit-O-001.md"}}
```

**Diverged edge:**
```json
{"edge":"F→S","git_commit":"789abcd","from":{"id":"F-jig.validation.intent.validate_specs","jig_hash":"e5f6a7"},"to":{"id":"S-015","jig_hash":"b2c3d4"},"report":{"result":"diverged","confidence":0.95,"method":"tiered-v1","file":"audit-S-015.md"}}
```

---

## Computing Current State

The audit log is append-only, but we often need to know the "current" state of each edge.

### Algorithm

```python
def compute_current_state(
    audit_log: list[dict]
) -> dict[tuple[str, str, str], dict]:
    """
    Compute current state from audit log.
    Returns the latest record per edge (edge_type, from_id, to_id).
    """
    state = {}
    for record in audit_log:  # Oldest to newest
        key = (record['edge'], record['from']['id'], record['to']['id'])
        state[key] = record  # Later records overwrite earlier
    return state
```

### Computing Spec Status

Spec status is NOT stored in the log. It's computed from edge records:

```python
def spec_status(spec_id: str, audit_log: list[dict]) -> str:
    """Compute overall status for a spec from its edge audits."""
    # Get latest record per edge
    current = compute_current_state(audit_log)

    # Find all edges pointing to this spec
    f_s_edges = [r for key, r in current.items()
                 if key[0] == 'F→S' and key[2] == spec_id]
    t_s_edges = [r for key, r in current.items()
                 if key[0] == 'T→S' and key[2] == spec_id]
    o_s_edges = [r for key, r in current.items()
                 if key[0] == 'O→S' and key[2] == spec_id]

    all_edges = f_s_edges + t_s_edges + o_s_edges

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

### Computing Outcome Status

Outcome status is computed from its O→S edges:

```python
def outcome_status(outcome_id: str, audit_log: list[dict]) -> str:
    """Compute overall status for an outcome from its edge audits."""
    current = compute_current_state(audit_log)

    # Find all O→S edges from this outcome
    o_s_edges = [r for key, r in current.items()
                 if key[0] == 'O→S' and key[1] == outcome_id]

    if not o_s_edges:
        return 'unaudited'
    if any(e['report']['result'] == 'diverged' for e in o_s_edges):
        return 'diverged'
    if any(e['report']['result'] == 'inconclusive' for e in o_s_edges):
        return 'inconclusive'
    return 'aligned'
```

---

## Log Compaction

Over time, the audit log grows. **Compaction** reduces size by keeping only the latest N records per edge.

### When to Compact

Compaction is **optional**. Teams should compact when:
- Log file exceeds a size threshold (e.g., >1MB)
- Log has >1000 records
- Quarterly maintenance

Teams that need full audit history for compliance should **never compact**.

### Compaction Strategies

#### Keep Latest Only

```bash
$ jigy audit compact
Compacted audit-log.ndjson: 2847 records → 542 edges
```

Keeps only the most recent record per edge.

#### Keep Latest N

```bash
$ jigy audit compact --keep-last 3
Compacted audit-log.ndjson: 2847 records → 1426 records
```

Keeps the 3 most recent records per edge (preserves some history).

### Compaction Algorithm

```python
def compact_log(
    audit_log: list[dict],
    keep_last: int = 1
) -> list[dict]:
    """Compact audit log, keeping latest N records per edge."""
    from collections import defaultdict

    # Group by edge
    by_edge = defaultdict(list)
    for record in audit_log:
        key = (record['edge'], record['from']['id'], record['to']['id'])
        by_edge[key].append(record)

    # Keep last N per edge (records are in chronological order)
    compacted = []
    for edge_key, records in by_edge.items():
        compacted.extend(records[-keep_last:])

    return compacted
```

### Compaction and Git

After compaction:
- Git diff shows removed lines (old records)
- History is preserved in git history if needed
- Consider tagging before compaction: `git tag pre-compact-2025-12`

---

## Part 2: Trigger Detection

Triggers identify which edges need audit by comparing current graph hashes against audit records.

### The Core Insight

```
jigy rebuild
    └─→ Computes current jig_hash for S, F, T, O (from J022)
    └─→ Writes to graph files (OVERWRITES previous)
    └─→ Graph only has "now" — no history

jigy triggers
    └─→ Reads current graphs (current jig_hash per node)
    └─→ Reads audit-log.ndjson (audited jig_hash per edge)
    └─→ Compares: current vs audited
    └─→ Difference = trigger
```

**Without audit records, everything is "new."** Triggers require a baseline to compare against.

### Change Detection Algorithm

```python
def detect_audit_triggers(
    intent_graph: Graph,
    impl_graph: Graph,
    verif_graph: Graph,
    audit_log: list[dict]
) -> list[Trigger]:
    """
    Detect which edges need audit.

    Args:
        intent_graph: Current intent graph with spec and outcome jig_hash values
        impl_graph: Current implementation graph with function jig_hash values
        verif_graph: Current verification graph with test jig_hash values
        audit_log: All audit records

    Returns:
        List of triggers indicating what needs audit and why
    """
    triggers = []

    # Get latest audit per edge
    latest_audits = compute_current_state(audit_log)

    # Collect all current edges from graphs
    current_edges = []

    # F→S edges (from implementation graph)
    for func in impl_graph.functions_with_implements():
        for spec_id in func.implements:
            spec = intent_graph.get_spec(spec_id)
            if spec:
                current_edges.append({
                    'edge': 'F→S',
                    'from': {'id': func.id, 'jig_hash': func.jig_hash},
                    'to': {'id': spec.id, 'jig_hash': spec.jig_hash},
                })

    # T→S edges (from verification graph)
    for test in verif_graph.tests_with_verifies():
        for spec_id in test.verifies:
            spec = intent_graph.get_spec(spec_id)
            if spec:
                current_edges.append({
                    'edge': 'T→S',
                    'from': {'id': test.id, 'jig_hash': test.jig_hash},
                    'to': {'id': spec.id, 'jig_hash': spec.jig_hash},
                })

    # T→F edges (from verification graph coverage data)
    for test in verif_graph.tests():
        for func_id in test.covers:
            func = impl_graph.get_function(func_id)
            if func:
                current_edges.append({
                    'edge': 'T→F',
                    'from': {'id': test.id, 'jig_hash': test.jig_hash},
                    'to': {'id': func.id, 'jig_hash': func.jig_hash},
                })

    # O→S edges (from intent graph outcomes)
    for outcome in intent_graph.outcomes():
        for spec_id in outcome.specifies:
            spec = intent_graph.get_spec(spec_id)
            if spec:
                current_edges.append({
                    'edge': 'O→S',
                    'from': {'id': outcome.id, 'jig_hash': outcome.jig_hash},
                    'to': {'id': spec.id, 'jig_hash': spec.jig_hash},
                })

    # Compare each current edge to its last audit
    for edge in current_edges:
        key = (edge['edge'], edge['from']['id'], edge['to']['id'])
        last_audit = latest_audits.get(key)

        if last_audit is None:
            triggers.append(Trigger(
                edge=edge['edge'],
                from_id=edge['from']['id'],
                to_id=edge['to']['id'],
                reason='new',
            ))
        elif last_audit['from']['jig_hash'] != edge['from']['jig_hash']:
            triggers.append(Trigger(
                edge=edge['edge'],
                from_id=edge['from']['id'],
                to_id=edge['to']['id'],
                reason='from_changed',
                git_commit=last_audit['git_commit'],
            ))
        elif last_audit['to']['jig_hash'] != edge['to']['jig_hash']:
            triggers.append(Trigger(
                edge=edge['edge'],
                from_id=edge['from']['id'],
                to_id=edge['to']['id'],
                reason='to_changed',
                git_commit=last_audit['git_commit'],
            ))
        # else: hashes match, no trigger needed

    # Detect removed edges (audited before, but no longer in graph)
    current_keys = {(e['edge'], e['from']['id'], e['to']['id']) for e in current_edges}
    for key in latest_audits.keys():
        if key not in current_keys:
            triggers.append(Trigger(
                edge=key[0],
                from_id=key[1],
                to_id=key[2],
                reason='removed',
            ))

    return triggers
```

### Trigger Reasons

| Reason | Meaning | Recommended Action |
|--------|---------|-------------------|
| `new` | Edge never audited | Audit required |
| `from_changed` | Source node jig_hash differs from last audit | Audit required |
| `to_changed` | Target node jig_hash differs from last audit | Audit required |
| `removed` | Edge no longer exists in graph | Archive audit records |

### Trigger Examples by Edge Type

**F→S trigger (function changed):**
```
F→S: F-jig.cli.layers.layers_command → S-040
  Reason: from_changed
  Last audited: commit abc1234
  F jig_hash: d4e5f6 → x7y8z9
  To see changes: git diff abc1234..HEAD -- src/jig/cli/layers.py
```

**T→S trigger (spec changed):**
```
T→S: T-test_layers.test_layers_command → S-040
  Reason: to_changed
  Last audited: commit abc1234
  S jig_hash: a1b2c3 → m4n5o6
  To see changes: git diff abc1234..HEAD -- jig/specifications/S-040.md
```

**T→F trigger (new coverage edge):**
```
T→F: T-test_auth.test_login → F-auth.validate_token
  Reason: new
  (never audited)
```

**O→S trigger (outcome changed):**
```
O→S: O-001 → S-001
  Reason: from_changed
  Last audited: commit abc1234
  O jig_hash: f1a2b3 → p9q8r7
  To see changes: git diff abc1234..HEAD -- jig/outcomes/O-001.md
```

**O→S trigger (spec removed from outcome):**
```
O→S: O-001 → S-005
  Reason: removed
  (spec no longer in outcome's specifies list)
```

---

## CLI Commands

### View Triggers

```bash
$ jigy triggers
Audit Triggers:

  NEW (6):
    F→S: F-jig.cli.suggest.suggest_command → S-041
    T→S: T-test_suggest.test_suggest_basic → S-041
    T→F: T-test_auth.test_login → F-auth.validate_token
    T→F: T-test_auth.test_login → F-auth.create_session
    T→F: T-test_auth.test_logout → F-auth.destroy_session
    O→S: O-002 → S-041

  FROM_CHANGED (3):
    F→S: F-jig.cli.layers.layers_command → S-040
      Last audited: commit abc1234
      To see changes: git diff abc1234..HEAD -- src/jig/cli/layers.py
    T→F: T-test_layers.test_layers_command → F-jig.cli.layers.layers_command
      Last audited: commit abc1234
    O→S: O-001 → S-001
      Last audited: commit abc1234
      To see changes: git diff abc1234..HEAD -- jig/outcomes/O-001.md

  TO_CHANGED (1):
    T→S: T-test_validation.test_brick_errors → S-038
      Last audited: commit def5678
      To see changes: git diff def5678..HEAD -- jig/specifications/S-038.md

  REMOVED (2):
    F→S: F-jig.old.deprecated_function → S-015
      (decorator removed or function deleted)
    O→S: O-001 → S-005
      (spec removed from outcome's specifies list)

Summary: 12 triggers (6 new, 3 from_changed, 1 to_changed, 2 removed)
```

### Filter Triggers

```bash
# Only show new edges (never audited)
$ jigy triggers --reason new

# Only show changes (exclude new and removed)
$ jigy triggers --reason from_changed --reason to_changed

# Only show specific edge type
$ jigy triggers --edge F→S
$ jigy triggers --edge T→F
$ jigy triggers --edge O→S

# Exit with non-zero if any triggers exist (for CI)
$ jigy triggers --exit-code
```

### Machine-Readable Output

```bash
$ jigy triggers --format json
```

```json
{
  "triggers": [
    {
      "edge": "F→S",
      "from": "F-jig.cli.layers.layers_command",
      "to": "S-040",
      "reason": "from_changed",
      "git_commit": "abc1234"
    },
    {
      "edge": "T→F",
      "from": "T-test_auth.test_login",
      "to": "F-auth.validate_token",
      "reason": "new"
    },
    {
      "edge": "O→S",
      "from": "O-001",
      "to": "S-001",
      "reason": "from_changed",
      "git_commit": "abc1234"
    }
  ],
  "summary": {
    "new": 6,
    "from_changed": 3,
    "to_changed": 1,
    "removed": 2,
    "total": 12
  }
}
```

### View Audit Status

```bash
$ jigy audit status
Audit Status:

  By Edge Type:
    F→S: 45 edges (42 aligned, 2 diverged, 1 inconclusive)
    T→S: 38 edges (36 aligned, 2 diverged)
    T→F: 312 edges (298 covered, 14 not_covered)
    O→S: 12 edges (11 aligned, 1 diverged)

  By Spec Status (computed):
    aligned: 35 specs
    diverged: 3 specs
    unverified: 5 specs
    unimplemented: 2 specs

  By Outcome Status (computed):
    aligned: 4 outcomes
    diverged: 1 outcome
    unaudited: 0 outcomes

  Recent Audits:
    2025-12-07: 15 edges audited (method: pytest-cov)
    2025-12-06: 8 edges audited (method: tiered-v1)
    2025-12-05: 3 edges audited (method: human-review)

Use 'jigy triggers' to see edges needing re-audit.
```

### View Audit History

```bash
$ jigy audit history S-040
Audit history for edges involving S-040:

  F→S: F-jig.cli.layers.layers_command → S-040
    2025-12-06  aligned  (tiered-v1, 0.9)  commit abc1234
    2025-11-20  aligned  (human-review, 1.0)  commit 9876543

  T→S: T-test_layers.test_layers_command → S-040
    2025-12-06  aligned  (tiered-v1, 0.85)  commit abc1234

  O→S: O-001 → S-040
    2025-12-06  aligned  (tiered-v1, 0.85)  commit abc1234

# To see what changed between audits:
  git diff 9876543..abc1234 -- jig/specifications/S-040.md
```

```bash
$ jigy audit history O-001
Audit history for edges from O-001:

  O→S: O-001 → S-001
    2025-12-06  aligned  (tiered-v1, 0.9)  commit abc1234
  O→S: O-001 → S-002
    2025-12-06  aligned  (tiered-v1, 0.85)  commit abc1234
  O→S: O-001 → S-003
    2025-12-06  diverged  (tiered-v1, 0.95)  commit abc1234
    2025-11-15  aligned  (human-review, 1.0)  commit 5678abc

# To see what changed in outcome:
  git diff 5678abc..abc1234 -- jig/outcomes/O-001.md
```

---

## Audit Workflow

### Single Audit Activity → Multiple Log Rows

An audit activity reviews alignment and produces:
- One report file (J024 format)
- Multiple log rows (one per edge audited)

For example, auditing spec S-040 might produce:

**Report:** `audit-S-040.md`
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

# Audit: S-040

[Detailed analysis...]
```

**Log rows:** 3 rows appended to audit-log.ndjson (one per edge).

### Coverage-Only Audit

A batch test coverage run is a valid audit activity:

```bash
$ jigy coverage --audit
Running pytest with coverage...
Analyzing T→F edges...
Recording 312 coverage edges...

Wrote: jig/audits/audit-coverage-2025-12-07.md
Appended: 312 rows to jig/audits/audit-log.ndjson
```

All T→F log rows point to the same report file.

### Partial Audits

Partial audits are valid. If spec S-040 has 5 implementing functions:
- Auditor can audit 2 of them now
- Log has 2 F→S rows for the 2 audited edges
- The other 3 edges have no audit record
- `jigy triggers` shows the 3 unaudited edges as `new`

No need for "complete audit" semantics. Unaudited edges simply trigger.

---

## Workflow Integration

### The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                         JIG WORKFLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. DECLARE                                                     │
│     Developer writes outcomes, specs, decorators, tests         │
│                        ↓                                        │
│  2. REBUILD                                                     │
│     jigy rebuild → generates graphs with jig_hash (J022)        │
│                        ↓                                        │
│  3. DETECT (this document)                                      │
│     jigy triggers → compares jig_hash to audit records          │
│     "These edges need audit"                                    │
│                        ↓                                        │
│  4. AUDIT (J024, J025)                                          │
│     Human or agent reviews alignment                            │
│     Writes report, appends log rows                             │
│                        ↓                                        │
│     (loop back to DECLARE as code evolves)                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Development Workflow

```
1. Developer modifies F-jig.cli.layers.layers_command (function)

2. Developer runs `jigy rebuild`
   └─→ Function's jig_hash changes in implementation-graph.ndjson

3. Developer runs `jigy triggers`
   └─→ Compares current jig_hash to audit records
   └─→ Reports: "F→S: F-jig.cli.layers.layers_command → S-040 (from_changed)"

4. Developer (or agent) performs audit (per J024/J025)
   └─→ Reviews function against spec
   └─→ Writes report, appends log row

5. Next `jigy triggers` shows no trigger for this edge
   └─→ jig_hash in audit record matches current jig_hash
```

### Outcome Workflow

```
1. Developer updates O-001 (outcome) — changes specifies list or description

2. Developer runs `jigy rebuild`
   └─→ Outcome's jig_hash changes in intent-graph.ndjson

3. Developer runs `jigy triggers`
   └─→ Reports: "O→S: O-001 → S-001 (from_changed)"
   └─→ (and for each spec in O-001's specifies list)

4. Developer (or agent) performs audit (per J024/J025)
   └─→ Reviews outcome against each spec
   └─→ Do specs still correctly decompose from outcome?
   └─→ Writes report, appends log rows (one per O→S edge)

5. Next `jigy triggers` shows no trigger for these edges
```

### CI Integration

```yaml
# .github/workflows/jig.yml
- name: Rebuild graphs
  run: jigy rebuild

- name: Run coverage audit
  run: jigy coverage --audit

- name: Check for audit triggers
  run: |
    jigy triggers --format json > triggers.json

    # Warn if there are triggers
    if [ $(jq '.summary.total' triggers.json) -gt 0 ]; then
      echo "::warning::$(jq '.summary.total' triggers.json) audit triggers detected"
      jq '.triggers[]' triggers.json
    fi

    # Optionally fail on new F→S edges (require audit before merge)
    new_impl=$(jq '[.triggers[] | select(.edge == "F→S" and .reason == "new")] | length' triggers.json)
    if [ $new_impl -gt 0 ]; then
      echo "::error::New F→S edges require audit before merge"
      exit 1
    fi
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

jigy rebuild --quiet

triggers=$(jigy triggers --format json)
total=$(echo "$triggers" | jq '.summary.total')

if [ "$total" -gt 0 ]; then
  echo "⚠ Audit triggers detected:"
  jigy triggers
  echo ""
  echo "Run 'jigy audit' to review, or commit with --no-verify to skip."
  exit 1
fi
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

# All edges from a specific function
jq 'select(.from.id == "F-jig.cli.layers.layers_command")' audit-log.ndjson

# Count edges by method
jq -s 'group_by(.report.method) | map({method: .[0].report.method, count: length})' audit-log.ndjson

# Find uncovered T→F edges
jq 'select(.edge == "T→F" and .report.result == "not_covered")' audit-log.ndjson

# Get latest audit per edge (for trigger detection)
jq -s 'group_by([.edge, .from.id, .to.id]) | map(.[-1])' audit-log.ndjson

# Edges audited by a specific method
jq 'select(.report.method == "tiered-v1")' audit-log.ndjson

# All O→S edges for a specific outcome
jq 'select(.edge == "O→S" and .from.id == "O-001")' audit-log.ndjson

# Find diverged O→S edges (specs that no longer fit outcomes)
jq 'select(.edge == "O→S" and .report.result == "diverged")' audit-log.ndjson

# All edges pointing to a spec (from F, T, or O)
jq 'select(.to.id == "S-001")' audit-log.ndjson
```

---

## File Structure

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
    ├── audit-log.ndjson              # Per-edge audit records
    ├── audit-S-040.md                # Spec-focused report
    ├── audit-O-001.md                # Outcome-focused report
    ├── audit-coverage-2025-12-07.md  # Coverage run report
    └── ...
```

---

## Proposed Changes to A001

### New Section: Audit Log

**Location:** `jig/audits/audit-log.ndjson`

**Purpose:** Append-only record of alignment audit decisions, per edge.

**Format:** NDJSON (one record per line, appended chronologically)

**Schema:**
```json
{"edge":"F→S","git_commit":"abc1234","from":{"id":"F-auth.authenticate","jig_hash":"d4e5f6"},"to":{"id":"S-001","jig_hash":"a1b2c3"},"report":{"result":"aligned","confidence":0.9,"method":"tiered-v1","file":"audit-S-001.md"}}
```

**Field contract:**
- `edge` (enum, REQUIRED): Edge type (`F→S`, `T→S`, `T→F`, `O→S`)
- `git_commit` (string, REQUIRED): Git commit where nodes were audited
- `from` (object, REQUIRED): Source node with `id` and `jig_hash`
- `to` (object, REQUIRED): Target node with `id` and `jig_hash`
- `report` (object, REQUIRED): Audit judgment with `result`, `confidence`, `method`, `file`

**Committed state requirement:**
- Audits MUST be performed on committed state
- `jigy audit` commands SHALL refuse if working tree has uncommitted changes to audited nodes
- This ensures `git_commit` always references a valid, reproducible state

**Lifecycle:**
- Records are **appended** on each audit decision (one per edge)
- Records are **never modified** after creation
- Current state is **computed** by finding latest record per edge
- **Compaction** is optional: `jigy audit compact` reduces file size

**Git behavior:**
- SHALL be committed to repository
- Append-only nature minimizes merge conflicts
- Compaction creates removal diffs (acceptable)

---

## Consequences

### What This Enables

1. **Full S-F-T-O coverage** — changes to any node trigger re-audit
2. **Granular tracking** — per-edge, not per-spec
3. **T→F as first-class** — coverage audits work independently
4. **O→S as first-class** — outcome decomposition audits work independently
5. **Partial audits** — audit what you can, trigger on the rest
6. **Auditor diff workflow** — `git_commit` enables easy diff commands
7. **Trend analysis** — track alignment health over time
8. **Team coordination** — shared audit state across developers
9. **CI integration** — automated detection of unaudited changes

### What This Constrains

1. **Log growth** — mitigated by optional compaction
2. **Git storage** — audit log is committed (acceptable size)
3. **Audit discipline** — team must actually record decisions
4. **Committed state** — audits require clean working tree

### What This Does NOT Do

1. **Compute hashes** — that's J022
2. **Perform audits** — that's J025
3. **Define report format** — that's J024

---

## Open Questions

### Should audit-log.ndjson be committed to git?

**Recommendation: Yes.**

Pros:
- Shared audit history across team
- Append-only means minimal merge conflicts
- Full trail visible in repo history
- Enables `jigy triggers` to work for all team members

Cons:
- File grows over time (mitigated by compaction)
- Adds to repo size

### Edge removal detection

If an edge is removed from the graph (decorator deleted, function removed), we detect it as `removed`. Should we:
- Just report it (current design)
- Auto-clean the audit log
- Require explicit acknowledgment

**Recommendation:** Just report for now. Let teams decide how to handle.

### Confidence for coverage edges

T→F coverage is deterministic (confidence=1.0). Should we:
- Keep confidence for schema uniformity (current design)
- Omit confidence for T→F edges

**Recommendation:** Keep for uniformity. Always 1.0 for coverage methods.

---

## References

- **J022:** Content Hashing (computes `jig_hash` for S, F, T, O nodes)
- **J024:** Audit Report Format (report .md files)
- **J025:** Audit Agents (how audits are performed)
- **J026:** Audit Architecture Simplification (design decisions)
- **A001:** Core Artifacts Contract (artifact schemas)
- **J017:** JIG Concept v9 (S-F-T triangle)

---

_Every edge has a story. The log remembers them all._
