# J022: Alignment Change Detection

**Status:** Proposal
**Date:** 2025-12-06
**Extends:** A001 (Core Artifacts Contract)

---

## Context

The jig system measures alignment between specifications (S), functions (F), and tests (T). However, alignment is not static—specifications evolve, implementations change, and tests are updated. Without change detection, we cannot know when alignment has drifted.

Currently, the system can tell us *what* is aligned, but not *when* alignment needs re-verification. This proposal introduces **bidirectional change detection** to answer: "Which spec↔implementation pairs need audit?"

### The Problem

Consider this scenario:
1. Developer writes `S-040` specifying layer visualization
2. Developer implements `layers_command()` with `@jig.implements("S-040")`
3. Alignment is verified ✓
4. *Time passes...*
5. Developer modifies `S-040` to require additional output formats
6. **Question:** How do we know `layers_command()` needs review?

Or the reverse:
1. Developer refactors `layers_command()` to change its behavior
2. **Question:** How do we know `S-040` alignment should be re-verified?

### Design Goals

1. **Deterministic detection** — reliably detect changes to specs or implementations
2. **Granular tracking** — identify exactly which pairs need audit, not "everything changed"
3. **Git-friendly storage** — clean diffs, grep-friendly, consistent with existing artifacts
4. **Minimal overhead** — hashing should be fast, storage should be compact
5. **S-F-T triangle coverage** — extend to tests via `@jig.verifies`

### Key Design Principle: All S-F-T Edges as Declared Intent

The S-F-T triangle has three edges:

```
         S (Spec)
        ╱   ╲
       ╱     ╲
  implements   verifies
     ╱           ╲
    F ─ ─ ─ ─ ─ ─ T
       (covers)
```

**All three edges are declared intent:**

| Edge | Declaration | Audit Mechanism |
|------|-------------|-----------------|
| F → S (implements) | `@jig.implements("S-001")` | Human/LLM review |
| T → S (verifies) | `@jig.verifies("S-001")` | Human/LLM review |
| T → F (covers) | *Derived from shared S* | Coverage analysis |

The key insight: **T → F is derived, not stored.**

If T verifies S, and F implements S, then T *should* cover F. This relationship is:
- **Derived** from the declared F→S and T→S edges
- **Audited** by coverage analysis (optional)
- **Not stored** in the verification graph

This design keeps all three edges philosophically consistent. We trust `@jig.implements` without machine-verifying that the function actually implements the spec. We should equally trust `@jig.verifies` without machine-verifying coverage. Coverage analysis becomes an optional audit mechanism, not a prerequisite for graph generation.

**Benefits:**
- Verification graph generation is fully deterministic (AST parsing only)
- No test execution required to build graphs
- Coverage analysis is an explicit audit step, not a hidden dependency
- Consistent philosophy across all S-F-T edges

---

## Decision

### 1. Content Hashing Strategy

All hashes SHALL use **SHA-256 truncated to 12 hexadecimal characters** (48 bits).

**Rationale:**
- SHA-256 is standard, widely supported, and fast
- 12 chars provides ~281 trillion possible values (collision probability negligible for change detection)
- Matches git short hash conventions for familiarity
- Not for security—purely for change detection

#### 1.1 Intent Artifact Hashing

**Specifications and Outcomes:**

Hash the **canonical JSON representation** of parsed frontmatter plus normalized body:

```python
import hashlib
import json
import yaml

def hash_intent_artifact(path: Path) -> str:
    """Hash a specification or outcome file."""
    content = path.read_text()

    # Parse frontmatter and body
    parts = content.split('---', 2)
    frontmatter = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
    body = parts[2].strip() if len(parts) >= 3 else content.strip()

    # Canonical representation
    canonical = json.dumps(
        {"frontmatter": frontmatter, "body": body},
        sort_keys=True,
        separators=(',', ':')
    )

    return hashlib.sha256(canonical.encode()).hexdigest()[:12]
```

**Benefits:**
- Ignores trailing whitespace changes
- Stable across line ending differences (CRLF vs LF)
- Captures both metadata and content changes

**Bricks:**

Hash each **brick definition independently** (not the entire bricks.yaml):

```python
def hash_brick(brick_dict: dict) -> str:
    """Hash a single brick's definition."""
    canonical = json.dumps(brick_dict, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]
```

**Benefits:**
- Changing one brick doesn't invalidate others
- Moving a module between bricks shows exactly which two bricks changed
- Layer changes are detected per-brick

#### 1.2 Implementation Artifact Hashing

**Functions with `@jig.implements`:**

Hash the **AST-normalized function** excluding decorators:

```python
import ast

def hash_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Hash function signature + body, excluding decorators."""
    # Clone node without decorators
    node_copy = type(node)(
        name=node.name,
        args=node.args,
        body=node.body,
        decorator_list=[],  # Exclude - tracked separately in 'implements' field
        returns=node.returns,
        type_comment=getattr(node, 'type_comment', None),
    )
    if isinstance(node, ast.AsyncFunctionDef):
        # Preserve async nature in canonical form
        pass

    # Canonical source via ast.unparse (Python 3.9+)
    canonical = ast.unparse(node_copy)
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]
```

**What is hashed:**
- Function name
- Parameters and type annotations
- Return type annotation
- Function body (all statements)

**What is excluded:**
- Decorators (tracked in `implements` field)
- Comments (not preserved in AST)
- Whitespace/formatting (normalized by AST)

**Benefits:**
- Formatting changes don't trigger false positives
- Actual logic changes are detected
- Decorator changes update the `implements` field, not the hash

#### 1.3 Verification Artifact Hashing

**Tests with `@jig.verifies`:**

Same strategy as implementation functions:

```python
def hash_test(node: ast.FunctionDef) -> str:
    """Hash test function, excluding decorators."""
    # Same approach as hash_function
    ...
```

**Rationale:** Tests are code. When test logic changes, we may need to re-verify that it still properly validates the specification.

---

### 2. Graph Schema Extensions

#### 2.1 Intent Graph Changes

Add `hash` field to all nodes:

**Specification Node:**
```json
{"id":"S-001","type":"specification","file":"jig/specifications/S-001.md","hash":"a1b2c3d4e5f6"}
```

**Outcome Node:**
```json
{"id":"O-001","type":"outcome","file":"jig/outcomes/O-001.md","specifies":["S-001","S-002"],"hash":"b2c3d4e5f6a1"}
```

**Brick Node:**
```json
{"id":"B-cli","type":"brick","name":"CLI Interface","layer":2,"file":"jig/bricks.yaml","hash":"c3d4e5f6a1b2"}
```

#### 2.2 Implementation Graph Changes

Add `hash` field to function nodes that have `implements`:

```json
{"id":"F-jig.cli.layers.layers_command","type":"function","file":"src/jig/cli/layers.py","line":17,"implements":["S-040"],"signature":"layers_command(project_root: Path, ...) -> int","hash":"d4e5f6a7b8c9"}
```

**Note:** Functions without `@jig.implements` MAY omit the hash field (no alignment to track).

#### 2.3 Verification Graph Changes

Add `hash` field to test nodes that have `verifies`:

```json
{"id":"T-test_layers.test_layers_command","type":"test","file":"tests/unit/test_layers.py","verifies":["S-040"],"hash":"e5f6a7b8c9d0"}
```

**Note:** The `covers` field is NOT stored in the verification graph. The T → F relationship is **derived** from shared specs and **audited** by coverage analysis. See Section 3.7 (Path Audit Records).

This keeps all three S-F-T edges as declared intent:
- F → S is declared via `@jig.implements`
- T → S is declared via `@jig.verifies`
- T → F is derived: if T verifies S and F implements S, then T should cover F

---

### 3. Audit Log

> **Design Pattern:** Append-only event log with optional compaction, modeled after **Kafka log compaction**.

#### 3.1 Append-Only Semantics

The audit log is an **append-only** record of all audit decisions. Each audit appends a new record; existing records are never modified or deleted (except via explicit compaction).

**Why append-only?**
- **Git-friendly:** Appends show as additions, not modifications — cleaner diffs
- **No merge conflicts:** Concurrent audits just append separate records
- **Full history:** `grep S-040 audit-log.ndjson` shows complete audit trail
- **Compliance-ready:** Immutable audit history (like accounting ledgers)
- **Metrics-enabled:** Can analyze audit frequency, who audits what

**Current state is computed** from the log by finding the latest record per (spec_id, impl_id) pair.

#### 3.2 Format: NDJSON

**Location:** `jig/generated/audit-log.ndjson`

**Rationale:**
- **Consistent:** Matches intent-graph, implementation-graph, verification-graph format
- **Append-friendly:** NDJSON is ideal for append-only logs
- **Grep-friendly:** Easy to query specific specs or functions
- **Streaming:** Can process large files without loading entirely into memory

#### 3.3 Schema

**Audit Record (appended on each audit):**
```json
{"spec":"S-040","impl":"F-jig.cli.layers.layers_command","spec_hash":"a1b2c3","impl_hash":"d4e5f6","status":"aligned","ts":"2025-12-06T10:30:00Z","by":"human"}
{"spec":"S-040","impl":"F-jig.cli.layers.layers_command","spec_hash":"f7e8d9","impl_hash":"d4e5f6","status":"aligned","ts":"2025-12-15T14:20:00Z","by":"human","note":"Spec updated, impl still valid"}
```

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `spec` | string | Yes | Specification ID (S-xxx) |
| `impl` | string | Yes | Function ID (F-xxx) or Test ID (T-xxx) |
| `spec_hash` | string | Yes | Hash of spec at time of audit |
| `impl_hash` | string | Yes | Hash of function/test at time of audit |
| `status` | enum | Yes | `aligned` or `diverged` |
| `ts` | ISO 8601 | Yes | Timestamp of audit |
| `by` | string | No | `human`, `ai` (optional tracking) |
| `note` | string | No | Optional audit notes |

**Field naming:** Short names (`spec`, `impl`, `ts`, `by`) since this file can grow over time.

**Test Audit Record (for T→S relationships):**
```json
{"spec":"S-040","impl":"T-test_layers.test_layers_command","spec_hash":"a1b2c3","impl_hash":"e5f6a7","status":"aligned","ts":"2025-12-06T10:30:00Z"}
```

#### 3.4 Status Values (Stored vs Computed)

**Stored in audit log** (explicit human/AI decisions):
| Status | Meaning |
|--------|---------|
| `aligned` | Auditor confirmed spec and impl match |
| `diverged` | Auditor found spec and impl don't match |

**Computed on-the-fly** (not stored):
| Status | Meaning | How Detected |
|--------|---------|--------------|
| `needs_review` | Hash changed since last audit | Current graph hash ≠ audit log hash |
| `new` | Never audited | No audit record exists for this pair |
| `removed` | Relationship no longer exists | Audit record exists but no graph edge |

This separation keeps the audit log purely about decisions, not transient state.

#### 3.5 Computing Current State

```python
def compute_current_state(audit_log: list[AuditRecord]) -> dict[tuple[str, str], AuditRecord]:
    """Compute current state from audit log (latest record per pair)."""
    state = {}
    for record in audit_log:  # Oldest to newest
        key = (record.spec, record.impl)
        state[key] = record  # Later records overwrite earlier
    return state
```

#### 3.6 Log Compaction (Kafka-Style)

Over time, the audit log grows. **Compaction** reduces size by keeping only the latest record per (spec, impl) pair.

```bash
# Keep only latest audit per spec↔impl pair
$ jigy audit compact
Compacted audit-log.ndjson: 847 records → 142 records

# Keep latest N records per pair (preserve some history)
$ jigy audit compact --keep-last 3
Compacted audit-log.ndjson: 847 records → 426 records

# Keep records newer than date
$ jigy audit compact --after 2025-01-01
Compacted audit-log.ndjson: 847 records → 312 records
```

**Compaction is optional.** Default behavior keeps full history (like accounting ledgers). Teams can compact periodically if file size becomes a concern.

**Implementation:**
```python
def compact_log(
    audit_log: list[AuditRecord],
    keep_last: int = 1,
    after: datetime | None = None
) -> list[AuditRecord]:
    """Compact audit log, keeping latest N records per pair."""
    from collections import defaultdict

    # Group by (spec, impl) pair
    by_pair = defaultdict(list)
    for record in audit_log:
        if after and record.ts < after:
            continue  # Skip old records
        by_pair[(record.spec, record.impl)].append(record)

    # Keep last N per pair
    compacted = []
    for pair, records in by_pair.items():
        records.sort(key=lambda r: r.ts)
        compacted.extend(records[-keep_last:])

    # Sort by timestamp for clean output
    compacted.sort(key=lambda r: r.ts)
    return compacted
```

#### 3.7 Path Audit Records

The audit log also tracks **path audits** — validation that tests actually execute their implementing functions.

**The Derived Covers Relationship:**

The T → F ("covers") relationship is not stored in the verification graph. Instead, it is **derived** from shared specifications:

```
If:  T verifies S  (declared via @jig.verifies)
And: F implements S  (declared via @jig.implements)
Then: T SHOULD cover F  (derived, audited by coverage)
```

This keeps all three S-F-T edges as declared intent, with coverage analysis serving as the audit mechanism.

**Path Derivation Algorithm:**
```python
def derive_expected_coverage(test: TestNode, impl_graph: Graph) -> set[str]:
    """Derive which functions a test should cover based on shared specs."""
    expected = set()
    for spec_id in test.verifies:
        for func in impl_graph.functions_implementing(spec_id):
            expected.add(func.id)
    return expected

def audit_path(test: TestNode, impl_graph: Graph, coverage_data: CoverageData) -> PathAuditRecord:
    """Audit whether test executes at least one implementing function."""
    expected = derive_expected_coverage(test, impl_graph)
    executed = coverage_data.functions_executed_by(test.id)

    # Test should execute at least one function implementing the shared spec
    covered = expected & executed

    return PathAuditRecord(
        type="path",
        spec=test.verifies[0],  # Primary spec (or iterate for multiple)
        test=test.id,
        executed=list(covered),
        status="aligned" if covered else "broken"
    )
```

**Path Audit Record Schema:**
```json
{"type":"path","spec":"S-040","test":"T-test_layers.test_layers_command","executed":["F-jig.cli.layers.layers_command"],"status":"aligned","ts":"2025-12-06T11:00:00Z","by":"coverage"}
```

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Always `"path"` (distinguishes from spec↔impl audits) |
| `spec` | string | Yes | The shared specification connecting T and F |
| `test` | string | Yes | Test ID (T-xxx) |
| `executed` | array | Yes | Function IDs actually executed by test (intersection of expected and covered) |
| `status` | enum | Yes | `aligned` or `broken` |
| `ts` | ISO 8601 | Yes | Timestamp of audit |
| `by` | string | No | Always `"coverage"` for path audits |

**Status Values:**
- `aligned` — Test executed at least one function implementing the shared spec
- `broken` — Test verifies spec but executed no implementing functions

**CLI Integration:**
```bash
# Run path audits (requires test execution with coverage)
$ jigy audit paths --run-coverage
Running pytest with coverage...
Analyzing T→S→F paths...

Path Audit Results:
  ✓ 42 paths aligned
  ✗ 2 paths broken:
    - T-test_users.test_creation → S-015 (executed 0 of 2 implementing functions)
    - T-test_cache.test_invalidation → S-022 (executed 0 of 1 implementing functions)

# Path audits are optional - teams may trust developer intent
$ jigy audit paths --dry-run
Would audit 44 T→S→F paths (use --run-coverage to execute)
```

**Design Rationale:**

Why derive covers instead of storing it?

1. **Consistent philosophy** — All three S-F-T edges become declared intent. We don't empirically verify that `@jig.implements` actually implements the spec; why should we empirically verify `@jig.verifies`?

2. **Deterministic graphs** — Verification graph generation requires only AST parsing, no test execution. Fast, reliable, works even if tests are broken.

3. **Coverage as audit** — Coverage analysis becomes an optional validation step, not a prerequisite for graph generation.

4. **No new decorator** — The T → F relationship is implied by shared specs. Developers don't need to annotate "this test covers this function" explicitly.

5. **Graceful adoption** — Teams can start with just `@jig.verifies` and add path audits later when ready.

---

### 4. Change Detection Algorithm

#### 4.1 Detecting Changes

```python
def detect_alignment_changes(
    intent_graph: Graph,
    impl_graph: Graph,
    audit_log: list[AuditRecord]
) -> list[AlignmentChange]:
    """Detect which alignments need review."""
    changes = []

    # Compute current state from audit log (latest record per pair)
    audited_state = compute_current_state(audit_log)

    # Build current state from graphs
    current_alignments = {}
    for func in impl_graph.functions_with_implements():
        for spec_id in func.implements:
            spec = intent_graph.get_spec(spec_id)
            current_alignments[(spec_id, func.id)] = {
                'spec_hash': spec.hash,
                'impl_hash': func.hash,
            }

    # Compare graph state to audited state
    for (spec_id, impl_id), current in current_alignments.items():
        audited = audited_state.get((spec_id, impl_id))

        if audited is None:
            changes.append(AlignmentChange(
                spec=spec_id,
                impl=impl_id,
                reason='new',
                status='new'
            ))
        elif audited.spec_hash != current['spec_hash']:
            changes.append(AlignmentChange(
                spec=spec_id,
                impl=impl_id,
                reason='spec_changed',
                status='needs_review',
                last_audited=audited.ts
            ))
        elif audited.impl_hash != current['impl_hash']:
            changes.append(AlignmentChange(
                spec=spec_id,
                impl=impl_id,
                reason='impl_changed',
                status='needs_review',
                last_audited=audited.ts
            ))
        elif audited.status == 'diverged':
            changes.append(AlignmentChange(
                spec=spec_id,
                impl=impl_id,
                reason='marked_diverged',
                status='diverged',
                last_audited=audited.ts
            ))
        # else: aligned and hashes match — no change needed

    # Detect removed alignments (in audit log but not in graph)
    for (spec_id, impl_id) in audited_state.keys():
        if (spec_id, impl_id) not in current_alignments:
            changes.append(AlignmentChange(
                spec=spec_id,
                impl=impl_id,
                reason='removed',
                status='removed'
            ))

    return changes
```

#### 4.2 CLI Integration

```bash
# Check for alignment changes (computes state from audit log)
$ jigy audit status
Alignment Status:
  ✓ 38 aligned (no changes)
  ⚠ 3 need review:
    - S-040 ↔ F-jig.cli.layers.layers_command (spec changed, last audited 2025-12-01)
    - S-023 ↔ F-jig.cli.validate.validate_intent_command (impl changed)
    - S-041 ↔ F-jig.cli.layers.suggest_layers_command (new)
  ✗ 1 diverged:
    - S-015 ↔ F-jig.validation.intent.validate_specs (marked diverged 2025-11-15)

# Record an audit decision (appends to audit log)
$ jigy audit mark S-040 F-jig.cli.layers.layers_command --status aligned
Appended audit record: S-040 ↔ F-jig.cli.layers.layers_command → aligned

$ jigy audit mark S-015 F-jig.validation.intent.validate_specs --status diverged --note "Missing error case"
Appended audit record: S-015 ↔ F-jig.validation.intent.validate_specs → diverged

# Show audit history for a spec (reads from audit log)
$ jigy audit history S-040
Audit history for S-040:
  2025-12-15 F-jig.cli.layers.layers_command  aligned  (by: human) "Spec updated, impl still valid"
  2025-12-06 F-jig.cli.layers.layers_command  aligned  (by: human)
  2025-11-20 F-jig.cli.layers.layers_command  aligned  (by: human)

# Show what changed since last audit
$ jigy audit diff S-040
Spec S-040:
  - Hash: a1b2c3... → f7e8d9...
  - Last audited: 2025-12-15
  - Implementations needing review:
    - F-jig.cli.layers.layers_command (impl unchanged, spec changed)

# Compact the audit log
$ jigy audit compact
Compacted audit-log.ndjson: 847 records → 142 records

$ jigy audit compact --keep-last 3
Compacted audit-log.ndjson: 847 records → 426 records
```

---

### 5. Workflow Integration

#### 5.1 Development Workflow

```
1. Developer modifies S-040.md (spec)
   └─→ On next `jigy intent rebuild`:
       └─→ S-040 hash changes in intent-graph.ndjson

2. Developer runs `jigy audit status`
   └─→ Computes current state from audit-log.ndjson
   └─→ Compares to current graph hashes
   └─→ Reports: "S-040 ↔ F-jig.cli.layers.layers_command needs review (spec changed)"

3. Developer reviews alignment
   └─→ Either: updates implementation to match spec
   └─→ Or: confirms implementation still satisfies spec

4. Developer runs `jigy audit mark S-040 F-... --status aligned`
   └─→ Appends new record to audit-log.ndjson with current hashes
   └─→ Git diff shows single line addition
```

#### 5.2 CI Integration

```yaml
# .github/workflows/alignment.yml
- name: Check alignment status
  run: |
    jigy audit status --format json > audit-report.json
    if jq -e '.needs_review | length > 0' audit-report.json; then
      echo "::warning::Alignments need review"
      jq '.needs_review[]' audit-report.json
    fi
```

#### 5.3 Pre-commit Hook (Optional)

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Rebuild graphs
jigy impl rebuild
jigy intent rebuild

# Check for unaudited changes
if jigy audit status --quiet --exit-code; then
  exit 0
else
  echo "Warning: Unaudited alignment changes detected"
  jigy audit status
  # Could block commit or just warn
fi
```

#### 5.4 Periodic Maintenance

```bash
# Quarterly: compact audit log to reduce size (optional)
$ jigy audit compact --keep-last 3
Compacted audit-log.ndjson: 1247 records → 426 records

# Or archive old records
$ jigy audit compact --after 2025-01-01
```

---

### 6. Proposed Changes to A001

The following changes to `A001_Core-Artifacts-Contract.md` are proposed:

#### 6.1 Section 6.1 Intent Graph - Add hash field

**Current:**
```json
{"id":"S-001","type":"specification","file":"jig/specifications/S-001.md"}
```

**Proposed:**
```json
{"id":"S-001","type":"specification","file":"jig/specifications/S-001.md","hash":"a1b2c3d4e5f6"}
```

Add to field definitions:
- `hash` (string, REQUIRED): SHA-256 hash (first 12 hex chars) of canonical content

#### 6.2 Section 6.2 Implementation Graph - Add hash field

**Current:**
```json
{"id":"F-auth.session.authenticate","type":"function","file":"src/auth/session.py","implements":["S-001","S-002"],"calls":["F-auth.tokens.validate"]}
```

**Proposed:**
```json
{"id":"F-auth.session.authenticate","type":"function","file":"src/auth/session.py","implements":["S-001","S-002"],"calls":["F-auth.tokens.validate"],"hash":"d4e5f6a7b8c9"}
```

Add to field definitions:
- `hash` (string, CONDITIONAL): SHA-256 hash of AST-normalized function. REQUIRED if `implements` is non-empty. SHALL be omitted if function has no `@jig.implements`.

#### 6.3 Section "Core Principle" - Clarify T → F as Derived

**Current (A001 lines 24-29):**
```markdown
Three relationships define alignment:
- **F → S** (implements) - which functions implement which specifications
- **T → S** (verifies) - which tests verify which specifications
- **T → F** (covers) - which tests execute which functions
```

**Proposed:**
```markdown
Three relationships define alignment:
- **F → S** (implements) - which functions implement which specifications
- **T → S** (verifies) - which tests verify which specifications
- **T → F** (covers) - which tests should exercise which functions (derived from shared specs)

The first two edges are **declared** via decorators. The third is **derived**: if T verifies S and F implements S, then T should cover F. This derived relationship is **audited** by coverage analysis.
```

#### 6.4 Section 6.3 Verification Graph - Major Revision

**Current (A001 lines 282-304):**
```markdown
**Generated from:**
- Test discovery (pytest, unittest)
- Coverage analysis (pytest-cov, coverage.py)
- `@jig.verifies` decorators

**Test Node:**
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"covers":["F-auth.session.authenticate","F-auth.tokens.validate"]}

Fields:
- `covers` (array, REQUIRED): Array of function IDs executed by this test (from coverage). SHALL be empty `[]` if none.
```

**Proposed:**
```markdown
**Generated from:**
- Test discovery (pytest, unittest naming conventions)
- `@jig.verifies` decorators (AST parsing)

**Note:** Graph generation is fully deterministic. No test execution required.

**Test Node:**
{"id":"T-test_auth.test_token_expiration","type":"test","file":"tests/unit/test_auth.py","verifies":["S-001"],"hash":"e5f6a7b8c9d0"}

Fields:
- `id` (string, REQUIRED): Format SHALL be `T-{module}.{test_function}` or `T-{module}.{TestClass}.{test_method}`
- `type` (string, REQUIRED): SHALL be `"test"`
- `file` (string, REQUIRED): Relative path to test file
- `verifies` (array, REQUIRED): Array of spec/outcome IDs from `@jig.verifies`. SHALL be empty `[]` if none.
- `hash` (string, CONDITIONAL): Content hash for change detection. REQUIRED if `verifies` is non-empty.

**Excluded fields:**
- `covers` - SHALL NOT be stored. The T → F relationship is derived from shared specs and audited by coverage analysis. See Section 7.2.
- `brick` - SHALL NOT be present (derived from verifies → implements → brick)
```

**Rationale:** This change makes all three S-F-T edges consistent:
- F → S is declared via `@jig.implements` (trusted)
- T → S is declared via `@jig.verifies` (trusted)
- T → F is derived from shared S (audited by coverage)

Graph generation becomes fully deterministic (AST parsing only, no test execution).

#### 6.5 New Section 6.4: Covers Relationship

**Add new section after Section 6.3:**

```markdown
#### 6.4 Covers Relationship (T → F)

**The T → F edge is derived, not stored.**

**Definition:** Test T "covers" function F if:
1. T verifies spec S (`@jig.verifies("S")`)
2. F implements spec S (`@jig.implements("S")`)

**Implication:** If a test verifies a spec, it SHOULD exercise at least one function that implements that spec.

**Computation:**
def derive_covers(test: TestNode, impl_graph: Graph) -> set[str]:
    covers = set()
    for spec_id in test.verifies:
        for func in impl_graph.functions_implementing(spec_id):
            covers.add(func.id)
    return covers

**Audit:** Coverage analysis validates that the derived relationship holds in execution. See Section 7.2 (Path Audit).
```

#### 6.6 New Section 7.2: Path Audit

**Add new section after Section 7 (Audit Log):**

```markdown
### 7.2 Path Audit

**Purpose:** Validate that the derived T → F relationship holds in execution.

**The Path:** For each test T that verifies spec S:
    T ──verifies──> S <──implements── F
           └─────── should cover ─────┘

**Audit Question:** Does test T execute at least one function F that implements the same spec S?

**Audit Mechanism:** Coverage analysis (pytest-cov, coverage.py)

**Path Audit Record:**
{"type":"path","spec":"S-001","test":"T-test_auth.test_authentication","executed":["F-auth.authenticate"],"status":"aligned","ts":"2025-12-06T11:00:00Z","by":"coverage"}

**Status Values:**
- `aligned` - Test executes at least one implementing function
- `broken` - Test verifies spec but doesn't execute any implementing function

**Note:** Path audits are optional. Teams may choose to trust developer intent without coverage validation.
```

#### 6.7 Update Section 9: Derivation Contract

**Add to "Derived from graphs":**

```markdown
**Derived from graphs:**
- **T → F covers relationship** (derived from T→S and F→S via shared specs)
- Brick assignments for tests (derived from verifies → implements → brick)
- Coverage percentages (computed from T→F edges via audit)
- Alignment metrics (computed from S-F-T triangle queries)
- All statistics, aggregations, health scores
```

#### 6.8 New Section: Audit Log

Add new section after Section 6 (Graph Files):

**Section 7: Audit Log**

**Location:** `jig/generated/audit-log.ndjson`

**Purpose:** Append-only record of alignment audit decisions, enabling change detection and audit history.

**Design Pattern:** Append-only event log with optional compaction (modeled after Kafka log compaction).

**Format:** NDJSON (one audit record per line, appended chronologically)

**Schema:**
```json
{"spec":"S-001","impl":"F-auth.session.authenticate","spec_hash":"a1b2c3","impl_hash":"d4e5f6","status":"aligned","ts":"2025-12-06T10:30:00Z","by":"human"}
{"spec":"S-001","impl":"F-auth.session.authenticate","spec_hash":"f7e8d9","impl_hash":"d4e5f6","status":"aligned","ts":"2025-12-15T14:20:00Z","by":"human","note":"Spec updated, impl still valid"}
```

**Field contract:**
- `spec` (string, REQUIRED): Specification or outcome ID
- `impl` (string, REQUIRED): Function ID (F-xxx) or Test ID (T-xxx)
- `spec_hash` (string, REQUIRED): Hash of spec at time of audit
- `impl_hash` (string, REQUIRED): Hash of function/test at time of audit
- `status` (enum, REQUIRED): `aligned` or `diverged`
- `ts` (string, REQUIRED): ISO 8601 timestamp
- `by` (string, OPTIONAL): `human` or `ai`
- `note` (string, OPTIONAL): Audit notes

**Lifecycle:**
- Records are **appended** on each audit decision (never modified)
- Current state is **computed** by finding latest record per (spec, impl) pair
- Transient statuses (`needs_review`, `new`, `removed`) are computed on-the-fly by comparing audit log to current graphs
- **Compaction** (optional): `jigy audit compact` reduces file size by keeping only latest N records per pair

#### 6.5 Update File Structure (Section 8)

```
project-root/
├── jig/
│   ├── specifications/
│   ├── outcomes/
│   ├── bricks.yaml
│   └── generated/
│       ├── intent-graph.ndjson
│       ├── implementation-graph.ndjson
│       ├── verification-graph.ndjson
│       └── audit-log.ndjson    # NEW (append-only)
```

---

### 7. Hash Stability Guarantees

To ensure hashes are stable across environments:

1. **Canonical JSON:** Always use `sort_keys=True, separators=(',', ':')`
2. **UTF-8 encoding:** All content SHALL be encoded as UTF-8 before hashing
3. **Normalized line endings:** Convert all line endings to `\n` before hashing
4. **Stripped whitespace:** Trailing whitespace removed from body content
5. **AST normalization:** Use `ast.unparse()` for consistent code representation

**Cross-platform guarantee:** The same source content SHALL produce the same hash on any platform (Windows, macOS, Linux).

---

### 8. Edge Cases

#### 8.1 Function Implements Multiple Specs

```python
@jig.implements("S-001", "S-002")
def authenticate_and_log(user: str) -> Token:
    ...
```

Creates two alignment records:
```json
{"spec_id":"S-001","impl_id":"F-auth.authenticate_and_log","impl_hash":"abc123",...}
{"spec_id":"S-002","impl_id":"F-auth.authenticate_and_log","impl_hash":"abc123",...}
```

Both share the same `impl_hash`. If the function changes, both alignments need review.

#### 8.2 Multiple Functions Implement Same Spec

```python
@jig.implements("S-001")
def authenticate_password(user: str, password: str) -> Token: ...

@jig.implements("S-001")
def authenticate_oauth(provider: str, token: str) -> Token: ...
```

Creates two alignment records with different `impl_id` and `impl_hash` values. If `S-001` changes, both need review.

#### 8.3 Spec Removed

If a spec is deleted:
- All alignment records referencing it become orphaned
- Detection algorithm reports these as `removed`
- Implementation still has `@jig.implements("S-xxx")` pointing to non-existent spec
- Validation (A001 Section 10) catches this as reference integrity error

#### 8.4 Function Decorator Changed

If `@jig.implements("S-001")` changes to `@jig.implements("S-002")`:
- Old alignment (S-001 ↔ F-xxx) is detected as `removed`
- New alignment (S-002 ↔ F-xxx) is detected as `new`
- Function hash unchanged (decorators excluded from hash)

---

## Consequences

### What This Enables

1. **Proactive alignment maintenance** — know when to audit before alignment drifts too far
2. **Efficient reviews** — only audit what changed, not everything
3. **Audit trail** — track when alignments were last verified and by whom
4. **CI integration** — automated detection of unaudited changes
5. **Full S-F-T coverage** — extends to tests via `@jig.verifies`

### What This Constrains

1. **Graph rebuild required** — must rebuild graphs to detect changes
2. **Hash computation overhead** — minor, but present during graph generation
3. **Additional artifact** — `audit-log.ndjson` must be managed
4. **Audit discipline** — team must actually perform audits when flagged
5. **Log growth** — audit log grows over time (mitigated by optional compaction)

### Migration Path

1. Implement hash computation in graph generators
2. Add `hash` fields to graph schemas
3. Create `audit-log.ndjson` append functionality
4. Add `jigy audit` CLI commands (status, mark, history, compact)
5. Document workflow in team practices

---

## Open Questions

1. **Should `audit-log.ndjson` be committed to git?**
   - Pro: Shared audit history across team
   - Pro: Append-only format means no merge conflicts (just append both)
   - Pro: Full audit trail visible in repo history
   - Recommendation: **Yes, commit it.** Append-only nature eliminates merge conflict concerns.

2. **Should we track `by` (audited_by) field?**
   - Pro: Accountability, distinguish human vs AI audits
   - Pro: Useful for compliance and audit trail
   - Con: Additional data to manage
   - Recommendation: Optional field, include when available.

3. **Should we auto-mark as `aligned` on certain conditions?**
   - Example: If only whitespace changed in spec, auto-approve?
   - Recommendation: No. All changes require explicit audit. Whitespace-only changes won't trigger (hashing normalizes whitespace).

4. **When should teams compact the audit log?**
   - Recommendation: Optional, based on file size concerns. Suggested: quarterly or when file exceeds N records.
   - Teams requiring full audit trail should never compact.

5. **Should compaction create an archive file?**
   - Option: `jigy audit compact` could move old records to `audit-log.2024.ndjson`
   - Recommendation: Future enhancement. Initial implementation just removes old records.

---

## Future Optimization: Git Integration

> **Status:** Future consideration, not part of initial implementation.
>
> The baseline implementation SHALL use JIG's own semantic hashing, which works universally regardless of version control system. The optimization below is optional for git-based projects.

### Rationale

Git already hashes every file as a "blob" using SHA-1 (or SHA-256 in newer versions). This presents an optimization opportunity: if git's blob hash hasn't changed, the file bytes are identical, which means our semantic hash is also unchanged.

### Key Differences

| Aspect | Git Blob Hash | JIG Semantic Hash |
|--------|---------------|-------------------|
| Algorithm | SHA-1 / SHA-256 | SHA-256 (truncated) |
| Input | Raw bytes + header | Normalized content |
| Granularity | Whole file | Per-artifact |
| Sensitivity | Every byte | Ignores formatting |

### Tiered Detection Strategy

```
Level 1: Git blob hash (O(1) lookup, already computed)
         └─→ unchanged? Skip file entirely (fast path)
         └─→ changed? Continue to Level 2

Level 2: Parse file, compute semantic hashes (expensive)
         └─→ Compare to stored semantic hashes
```

**The invariant:** If git blob hash unchanged → file bytes unchanged → semantic hash unchanged.

**The subtle case:** Git hash changed but semantic hash unchanged (formatting-only change). We still do the expensive parse, but no audit is triggered. This is correct behavior.

### Proposed Schema Extension

Store git blob hashes at the file level in graph metadata:

```json
{"_meta": {
  "version": "1.0",
  "git_commit": "4f11c9a...",
  "file_blobs": {
    "jig/specifications/S-001.md": "a1b2c3d4e5f6",
    "jig/specifications/S-002.md": "b2c3d4e5f6a1",
    "src/jig/cli/layers.py": "c3d4e5f6a1b2"
  }
}}
```

### Implementation Sketch

```python
import subprocess

def get_git_blob_hash(file_path: Path) -> str | None:
    """Get git's blob hash for a file. Returns None if not in a git repo."""
    try:
        result = subprocess.run(
            ["git", "hash-object", str(file_path)],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()[:12]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None  # Not a git repo or git not installed

def incremental_rebuild(graph: Graph) -> Graph:
    """Rebuild graph, skipping unchanged files when possible."""
    stored_blobs = graph.meta.get('file_blobs', {})
    new_blobs = {}

    for file_path in discover_files():
        current_blob = get_git_blob_hash(file_path)
        stored_blob = stored_blobs.get(str(file_path))

        if current_blob and current_blob == stored_blob:
            # Fast path: git says file unchanged, reuse existing nodes
            graph.preserve_nodes_from_file(file_path)
        else:
            # Slow path: file changed (or no git), reparse and rehash
            nodes = parse_and_hash(file_path)
            graph.update_nodes(nodes)

        if current_blob:
            new_blobs[str(file_path)] = current_blob

    graph.meta['file_blobs'] = new_blobs
    return graph
```

### Additional Git Optimizations

**1. Use `git ls-files -s` for bulk hash retrieval:**
```bash
$ git ls-files -s jig/specifications/
100644 a1b2c3d4... 0   jig/specifications/S-001.md
100644 b2c3d4e5... 0   jig/specifications/S-002.md
```
One command returns all staged file hashes — faster than per-file `git hash-object`.

**2. Use `git diff --name-only` for changed file discovery:**
```bash
# Find files changed since last graph generation
$ git diff --name-only 4f11c9a HEAD -- 'jig/**/*.md' 'src/**/*.py'
```
This limits which files need any processing at all.

**3. Choose the right git state:**
| State | Command | Use Case |
|-------|---------|----------|
| Working tree | `git hash-object <file>` | Current uncommitted state |
| Index (staged) | `git ls-files -s` | Pre-commit validation |
| HEAD commit | `git ls-tree HEAD` | CI/CD pipelines |

### Why This is Optional

1. **Not everyone uses git** — Mercurial, SVN, Perforce, or no VCS at all
2. **Baseline must work universally** — JIG's semantic hashing is the source of truth
3. **Optimization, not correctness** — git integration speeds things up but doesn't change results
4. **Graceful degradation** — if git unavailable, fall back to full rebuild

### Decision

The initial implementation SHALL:
1. Implement semantic hashing as the baseline (always required)
2. NOT depend on git for correctness
3. MAY add git integration as a future performance optimization
4. SHALL detect git availability and use it opportunistically if present

---

## References

- **A001:** Core Artifacts Contract (proposed changes in Section 6)
- **AG019:** Irreducible Core (S-F-T triangle)
- **J017:** JIG Concept v9 (alignment graph with architectural layers)
- Discussion: "Bidirectional change detection for spec↔implementation alignment audits"
- Discussion: "Derived covers relationship and path audits" (T→F as derived from shared specs)
