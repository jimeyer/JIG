# PLAN: Audit Records and Triggers (J023)

- **SCOPE**: docs/jig-concept/J023_Audit-Records-and-Triggers.md
- **Start**: 2025-12-08
- **Status**: Draft
- **Branch**: audit-triggers

## Overview

Implement the audit record system and trigger detection algorithm defined in J023. This enables tracking alignment audit decisions and detecting when edges need re-audit due to content changes.

**Dependencies:**
- J022 Content Hashing (implemented: S-044 through S-050, src/jig/hashing.py)
- Implementation graph with jig_hash on F nodes
- Intent graph with jig_hash on S, O nodes

**Key Concepts:**
- **Audit Record**: Per-edge record of an alignment audit decision
- **Trigger**: Edge that needs audit (new, changed, or removed)
- **Four Edge Types**: F→S, T→S, T→F, O→S

---

## Known Intent (Created Before Coding)

### Outcomes

**O-018**: Audit Trail for Alignment Decisions (jig/outcomes/O-018.md)
- Teams can track alignment audit decisions over time
- Enables compliance, accountability, trend analysis

**O-019**: Automatic Change Detection for Re-Audit (jig/outcomes/O-019.md)
- Developers know when code changes invalidate previous audits
- Prevents silent alignment drift

### Specifications

**Audit Log Core:**
- **S-051**: Audit Log Location & Format - jig/audits/audit-log.ndjson
- **S-052**: Audit Record Schema - edge, git_commit, from, to, report fields
- **S-053**: Audit Log Append-Only - new records appended, never overwriting
- **S-054**: Current State Computation - latest record per edge from log

**Trigger Detection:**
- **S-055**: New Edge Trigger - edges without audit records
- **S-056**: Changed Edge Trigger - jig_hash mismatch (from_changed/to_changed)
- **S-057**: Removed Edge Trigger - audited edges no longer in graph

**Computed Status:**
- **S-058**: Spec Status Computation - from F→S, T→S, O→S edges
- **S-059**: Outcome Status Computation - from O→S edges

**CLI Commands:**
- **S-060**: Triggers CLI - `jigy triggers` command
- **S-061**: Audit Status CLI - `jigy audit status` command
- **S-062**: Audit History CLI - `jigy audit history <node>` command
- **S-063**: Log Compaction CLI - `jigy audit compact` command

### Bricks Affected

- **B-cli**: New audit subgroup with triggers, status, history, compact commands
- **B-core-utils** (or new **B-audit**): Audit log I/O, trigger detection, status computation

---

## Work Unit Checklist

- [ ] WU0: Create Intent nodes (O-018, O-019, S-051 through S-063)
- [ ] WU1: Core data models (AuditRecord, Trigger) — tests ☐ / code ☐ / docs ☐
- [ ] WU2: Audit log I/O (read/write/append) — tests ☐ / code ☐ / docs ☐
- [ ] WU3: Current state computation — tests ☐ / code ☐ / docs ☐
- [ ] WU4: Trigger detection algorithm — tests ☐ / code ☐ / docs ☐
- [ ] WU5: Status computation (spec/outcome) — tests ☐ / code ☐ / docs ☐
- [ ] WU6: CLI - `jigy triggers` — tests ☐ / code ☐ / docs ☐
- [ ] WU7: CLI - `jigy audit status` — tests ☐ / code ☐ / docs ☐
- [ ] WU8: CLI - `jigy audit history` — tests ☐ / code ☐ / docs ☐
- [ ] WU9: CLI - `jigy audit compact` — tests ☐ / code ☐ / docs ☐
- [ ] WU10: Integration tests & validation — tests ☐ / code ☐ / docs ☐

---

## Work Units

### Work Unit 0: Create Known Intent

**Goal**: Capture all known Outcomes and Specifications from J023 before writing any code.

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] O-018 and O-019 created in jig/outcomes/
- [ ] S-051 through S-063 created in jig/specifications/
- [ ] All files have proper YAML frontmatter with `specifies:` links
- [ ] `jigy validate` passes

**Created Nodes**:
- O-018: Audit Trail for Alignment Decisions
- O-019: Automatic Change Detection for Re-Audit
- S-051 through S-063: (see detailed list above)

**Reflect**:
- (To be filled during execution)

---

### Work Unit 1: Core Data Models

**Goal**: Define AuditRecord and Trigger dataclasses with proper typing.

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] AuditRecord dataclass with all fields per J023 schema
- [ ] Trigger dataclass with edge, from_id, to_id, reason, git_commit fields
- [ ] Enums for EdgeType (F→S, T→S, T→F, O→S) and TriggerReason (new, from_changed, to_changed, removed)
- [ ] Enums for AuditResult per edge type
- [ ] Type hints complete, mypy passes

**Implementation Notes**:
- File: `src/jig/audit/models.py`
- Use `@dataclass` with `frozen=True` for immutability
- EdgeType enum values: `F_S = "F→S"`, `T_S = "T→S"`, `T_F = "T→F"`, `O_S = "O→S"`

**Test Plan**:
- Test dataclass instantiation
- Test enum values
- Test serialization to/from dict
- File: `tests/unit/test_audit_models.py`

**Human Verification**:
```bash
python -c "from jig.audit.models import AuditRecord, Trigger, EdgeType; print(EdgeType.F_S.value)"
```

**Reflect**: (To be filled)

---

### Work Unit 2: Audit Log I/O

**Goal**: Implement read, write, and append operations for audit-log.ndjson.

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-051 implemented: audit-log.ndjson at jig/audits/
- [ ] S-053 implemented: append-only semantics (append_audit_records)
- [ ] read_audit_log() returns list of AuditRecord
- [ ] append_audit_records() appends without overwriting
- [ ] Handles missing file (returns empty list on read, creates on write)

**Implementation Notes**:
- File: `src/jig/audit/log_io.py`
- NDJSON format: one JSON object per line
- Use pathlib for file paths
- Atomic append via file locking if needed (or just append mode)

```python
@jig.implements("S-051", "S-053")
def append_audit_records(log_path: Path, records: list[AuditRecord]) -> None:
    """Append audit records to log file (creates if missing)."""

@jig.implements("S-051")
def read_audit_log(log_path: Path) -> list[AuditRecord]:
    """Read all audit records from log file."""
```

**Test Plan**:
- Test read empty/missing file
- Test append to empty file
- Test append to existing file (verify append-only)
- Test round-trip (write then read)
- File: `tests/unit/test_audit_log_io.py`

**Human Verification**:
```bash
# After running tests, check generated test files
cat /tmp/test_audit_log.ndjson
```

**Reflect**: (To be filled)

---

### Work Unit 3: Current State Computation

**Goal**: Compute latest audit record per edge from append-only log.

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] S-054 implemented: compute_current_state()
- [ ] Returns dict mapping (edge_type, from_id, to_id) to latest AuditRecord
- [ ] Later records in log overwrite earlier for same edge
- [ ] Empty log returns empty dict

**Implementation Notes**:
- File: `src/jig/audit/state.py`

```python
@jig.implements("S-054")
def compute_current_state(
    audit_log: list[AuditRecord]
) -> dict[tuple[str, str, str], AuditRecord]:
    """Compute current state from audit log."""
```

**Test Plan**:
- Test empty log
- Test single record per edge
- Test multiple records per edge (latest wins)
- Test mixed edge types
- File: `tests/unit/test_audit_state.py`

**Human Verification**:
```python
from jig.audit.state import compute_current_state
# Run with sample data
```

**Reflect**: (To be filled)

---

### Work Unit 4: Trigger Detection Algorithm

**Goal**: Detect which edges need audit by comparing graph hashes to audit records.

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-055 implemented: new edges detected
- [ ] S-056 implemented: changed edges detected (from_changed, to_changed)
- [ ] S-057 implemented: removed edges detected
- [ ] detect_triggers() returns list of Trigger objects
- [ ] Works with all four edge types (F→S, T→S, T→F, O→S)

**Implementation Notes**:
- File: `src/jig/audit/triggers.py`
- Need to load intent graph (S, O nodes with jig_hash)
- Need to load implementation graph (F nodes with jig_hash)
- Future: verification graph for T nodes (may stub for now)

```python
@jig.implements("S-055", "S-056", "S-057")
def detect_triggers(
    intent_graph: IntentGraph,
    impl_graph: ImplGraph,
    audit_log: list[AuditRecord]
) -> list[Trigger]:
    """Detect edges needing audit."""
```

**Test Plan**:
- Test new edge (never audited)
- Test unchanged edge (no trigger)
- Test from_changed (source jig_hash changed)
- Test to_changed (target jig_hash changed)
- Test removed edge (in audit log, not in graph)
- Test each edge type
- File: `tests/unit/test_trigger_detection.py`

**Human Verification**:
```bash
# Will verify via CLI in WU6
```

**Reflect**: (To be filled)

---

### Work Unit 5: Status Computation

**Goal**: Compute spec_status and outcome_status from audit records.

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] S-058 implemented: spec_status() function
- [ ] S-059 implemented: outcome_status() function
- [ ] spec_status returns: aligned, diverged, inconclusive, unimplemented, unverified
- [ ] outcome_status returns: aligned, diverged, inconclusive, unaudited

**Implementation Notes**:
- File: `src/jig/audit/status.py`

```python
@jig.implements("S-058")
def spec_status(spec_id: str, current_state: dict) -> str:
    """Compute overall status for a spec from its edge audits."""

@jig.implements("S-059")
def outcome_status(outcome_id: str, current_state: dict) -> str:
    """Compute overall status for an outcome from its O→S edges."""
```

**Test Plan**:
- Test spec with all aligned edges
- Test spec with diverged edge
- Test spec with no F→S edges (unimplemented)
- Test spec with no T→S edges (unverified)
- Test outcome with all aligned O→S edges
- Test outcome with no O→S edges (unaudited)
- File: `tests/unit/test_audit_status.py`

**Human Verification**:
```bash
# Will verify via CLI in WU7
```

**Reflect**: (To be filled)

---

### Work Unit 6: CLI - `jigy triggers`

**Goal**: Implement `jigy triggers` command to display edges needing audit.

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] S-060 implemented: `jigy triggers` command
- [ ] Groups output by reason (NEW, FROM_CHANGED, TO_CHANGED, REMOVED)
- [ ] Shows git diff command for changed edges
- [ ] Supports --format json for machine-readable output
- [ ] Supports --reason filter
- [ ] Supports --edge filter
- [ ] Supports --exit-code for CI

**Implementation Notes**:
- File: `src/jig/cli/audit.py` (new file for audit commands)
- Add `audit` group to main.py
- Add `triggers` command under audit group (or top-level as `jigy triggers`)

```python
@cli.command()
@click.option("--format", type=click.Choice(["human", "json"]))
@click.option("--reason", multiple=True)
@click.option("--edge", multiple=True)
@click.option("--exit-code", is_flag=True)
def triggers(format, reason, edge, exit_code):
    """Display edges needing audit."""
```

**Test Plan**:
- Test with no audit log (all edges "new")
- Test with partial audit log
- Test --format json output
- Test --reason filter
- Test --edge filter
- Test --exit-code returns non-zero when triggers exist
- File: `tests/integration/test_cli_triggers.py`

**Human Verification**:
```bash
jigy triggers
jigy triggers --format json
jigy triggers --reason new
jigy triggers --edge "F→S"
```

**Reflect**: (To be filled)

---

### Work Unit 7: CLI - `jigy audit status`

**Goal**: Implement `jigy audit status` command to show audit status overview.

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] S-061 implemented: `jigy audit status` command
- [ ] Shows counts by edge type (F→S, T→S, T→F, O→S)
- [ ] Shows computed spec status (aligned, diverged, etc.)
- [ ] Shows computed outcome status
- [ ] Shows recent audit activity
- [ ] Supports --format json

**Implementation Notes**:
- File: `src/jig/cli/audit.py`

```python
@audit.command()
def status():
    """Show audit status overview."""
```

**Test Plan**:
- Test with empty audit log
- Test with populated audit log
- Test --format json
- File: `tests/integration/test_cli_audit_status.py`

**Human Verification**:
```bash
jigy audit status
jigy audit status --format json
```

**Reflect**: (To be filled)

---

### Work Unit 8: CLI - `jigy audit history`

**Goal**: Implement `jigy audit history` command to show audit history for a node.

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] S-062 implemented: `jigy audit history <node>` command
- [ ] Shows all audit records involving the node (as from or to)
- [ ] Chronological order with timestamps
- [ ] Shows git diff commands for easy navigation

**Implementation Notes**:
- File: `src/jig/cli/audit.py`

```python
@audit.command()
@click.argument("node_id")
def history(node_id: str):
    """Show audit history for a node."""
```

**Test Plan**:
- Test with spec ID (shows F→S, T→S, O→S edges to it)
- Test with outcome ID (shows O→S edges from it)
- Test with function ID (shows F→S edges from it)
- Test with unknown node ID
- File: `tests/integration/test_cli_audit_history.py`

**Human Verification**:
```bash
jigy audit history S-001
jigy audit history O-001
jigy audit history F-jig.cli.main.cli
```

**Reflect**: (To be filled)

---

### Work Unit 9: CLI - `jigy audit compact`

**Goal**: Implement `jigy audit compact` command to reduce log size.

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [ ] S-063 implemented: `jigy audit compact` command
- [ ] Default: keep only latest record per edge
- [ ] --keep-last N: keep N most recent per edge
- [ ] Reports before/after counts
- [ ] Creates backup before compacting (optional)

**Implementation Notes**:
- File: `src/jig/cli/audit.py`
- File: `src/jig/audit/compaction.py`

```python
@jig.implements("S-063")
def compact_log(audit_log: list[AuditRecord], keep_last: int = 1) -> list[AuditRecord]:
    """Compact audit log, keeping latest N records per edge."""

@audit.command()
@click.option("--keep-last", default=1, type=int)
def compact(keep_last: int):
    """Compact the audit log."""
```

**Test Plan**:
- Test compact with keep_last=1
- Test compact with keep_last=3
- Test preserves chronological order within kept records
- Test dry-run mode
- File: `tests/unit/test_audit_compaction.py`

**Human Verification**:
```bash
jigy audit compact --dry-run
jigy audit compact --keep-last 3
```

**Reflect**: (To be filled)

---

### Work Unit 10: Integration Tests & Validation

**Goal**: End-to-end testing and validation of the complete audit system.

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] Full workflow test: create audit → rebuild → detect triggers
- [ ] Test with real JIG codebase
- [ ] All specs (S-051 through S-063) have @jig.implements decorators
- [ ] All test functions have @jig.verifies decorators
- [ ] `jigy validate` passes
- [ ] `jigy status` shows alignment for audit specs

**Test Plan**:
- Integration test: full audit workflow
- Test edge cases: concurrent audits, corrupted log, etc.
- File: `tests/integration/test_audit_workflow.py`

**Human Verification**:
```bash
jigy validate
jigy rebuild
jigy triggers
jigy audit status
```

**Reflect**: (To be filled)

---

## Architecture Notes

### File Structure

```
src/jig/
├── audit/
│   ├── __init__.py
│   ├── models.py         # AuditRecord, Trigger, enums
│   ├── log_io.py         # read/write/append NDJSON
│   ├── state.py          # compute_current_state
│   ├── triggers.py       # detect_triggers
│   ├── status.py         # spec_status, outcome_status
│   └── compaction.py     # compact_log
└── cli/
    ├── audit.py          # CLI commands (triggers, status, history, compact)
    └── main.py           # Add audit group

tests/
├── unit/
│   ├── test_audit_models.py
│   ├── test_audit_log_io.py
│   ├── test_audit_state.py
│   ├── test_trigger_detection.py
│   ├── test_audit_status.py
│   └── test_audit_compaction.py
└── integration/
    ├── test_cli_triggers.py
    ├── test_cli_audit_status.py
    ├── test_cli_audit_history.py
    └── test_audit_workflow.py

jig/
└── audits/
    └── audit-log.ndjson  # Created on first audit
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    jigy triggers                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. Load graphs (intent, impl) with jig_hash values        │
│   2. Load audit-log.ndjson                                  │
│   3. compute_current_state(audit_log)                       │
│   4. detect_triggers(graphs, current_state)                 │
│   5. Format and display triggers                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Append-only log**: Matches J023 spec, enables full audit trail
2. **Current state computed**: Not stored, derived from log on demand
3. **Edge-centric**: All operations work on edges, not nodes
4. **Four edge types**: F→S, T→S, T→F, O→S (as defined in J023)
5. **Git commit required**: Audits reference committed state for reproducibility

### Dependencies on Other Systems

- **J022 (hashing.py)**: Provides jig_hash values for comparison
- **Intent graph**: S, O nodes with jig_hash
- **Implementation graph**: F nodes with jig_hash
- **Verification graph**: T nodes with jig_hash (future, may stub)

---

## Risk Assessment

### Technical Risks

1. **Verification graph not implemented**: T→F edges require verification graph
   - Mitigation: Stub T→F edge collection initially, implement when verification graph exists

2. **Large audit logs**: Performance with thousands of records
   - Mitigation: Compaction command, efficient NDJSON parsing

3. **Concurrent access**: Multiple processes appending to log
   - Mitigation: File locking or accept eventual consistency

### Scope Risks

1. **CLI complexity**: Many options and output formats
   - Mitigation: Start with human format, add JSON later

2. **Integration with existing graphs**: Graph schemas may need jig_hash
   - Mitigation: Verify J022 integration before starting

---

## Completion Summary

(To be filled when work is complete)

**Scope Delivered**:
- (Summary)

**Metrics**:
- Work Units: 11
- Specifications Created: 13 (S-051 through S-063)
- Outcomes Created: 2 (O-018, O-019)
- Alignment: TBD

**Key Decisions**:
- (To be filled)

**Deltas from Original Scope**:
- (To be filled)

**Reflection Roll-Up**:
- **Repeatable wins**: (To be filled)
- **Systemic frictions**: (To be filled)
- **Open questions**: (To be filled)

**Final Validation**:
- [ ] All work unit checklists complete
- [ ] `jigy validate` passes
- [ ] `jigy status` shows expected alignment
- [ ] All tests passing
- [ ] Documentation updated
