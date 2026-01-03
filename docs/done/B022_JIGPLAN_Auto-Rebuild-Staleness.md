# JIGPLAN: Auto-Rebuild with Staleness Detection

**SCOPE:** docs/wip/B021_SCOPE_Auto-Rebuild-Staleness.md
**Date:** 2025-12-22
**Status:** Draft
**Author:** AI Agent

---

## Summary

This JIGPLAN adds automatic graph rebuild before `validate`, `show`, and `audit` commands, with fast git-based staleness detection to avoid unnecessary rebuilds. Creates 1 new outcome (O-022), 4 new specifications (S-068 through S-071), and 1 new brick (B-staleness). Modifies B-cli for command integration and B-impl-graph, B-intent-graph, B-verification-graph for metadata storage.

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| CREATE | O-022 | Commands Operate on Current Data | New outcome for auto-rebuild value proposition |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | S-058 | Verb-First Rebuild Commands | Existing rebuild infrastructure used by auto-rebuild |
| REUSE | S-065 | CLI Integration with Configuration | Path config used for staleness input directories |
| CREATE | S-068 | Graph Metadata for Staleness Detection | Store git state in graph `_meta` blocks |
| CREATE | S-069 | Staleness Detection Module | Core staleness detection logic |
| CREATE | S-070 | Auto-Rebuild Before Commands | Command integration behavior |
| CREATE | S-071 | Skip Auto-Rebuild Flag | `--no-rebuild` global flag |

---

## O/S Node Details

### Nodes to REUSE

#### S-058: Verb-First Rebuild Commands

Auto-rebuild leverages existing `jigy rebuild {impl|verify|intent}` commands. No changes needed to rebuild logic itself.

#### S-065: CLI Integration with Configuration

Staleness detection uses configured paths (`paths.source`, `paths.tests`, `paths.specifications`, etc.) to determine input directories for each graph type.

---

### Nodes to CREATE

#### O-022: Commands Operate on Current Data (NEW)

**File:** `jig/outcomes/O-022.md` (created)
**Specifies:** S-068, S-069, S-070, S-071
**Summary:** JIG commands operate on up-to-date graph data without requiring manual rebuild invocation. Eliminates "stale data" bugs while maintaining fast execution.

#### S-068: Graph Metadata for Staleness Detection (NEW)

**File:** `jig/specifications/S-068.md` (created)
**Implements:** O-022
**Summary:** Graph NDJSON files include git state metadata (`git_head`, `git_tree_hashes`, `git_dirty_files`) enabling efficient staleness comparison.

#### S-069: Staleness Detection Module (NEW)

**File:** `jig/specifications/S-069.md` (created)
**Implements:** O-022
**Summary:** Provides `is_stale()` and `get_staleness_status()` functions that compare current git state to recorded graph metadata. Completes in <100ms.

#### S-070: Auto-Rebuild Before Commands (NEW)

**File:** `jig/specifications/S-070.md` (created)
**Implements:** O-022
**Summary:** Commands (`validate`, `show`, `audit`) check staleness and rebuild only affected graphs before executing their main logic.

#### S-071: Skip Auto-Rebuild Flag (NEW)

**File:** `jig/specifications/S-071.md` (created)
**Implements:** O-022
**Summary:** Global `--no-rebuild` flag allows power users and CI to skip staleness detection when graphs are known to be current.

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| CREATE | B-staleness | 0 | New staleness detection module |
| MODIFY | B-impl-graph | 0 | Add git metadata to `_meta` block |
| MODIFY | B-intent-graph | 0 | Add git metadata to `_meta` block |
| MODIFY | B-verification-graph | 1 | Add git metadata to `_meta` block |
| MODIFY | B-cli | 1 | Add `--no-rebuild` flag and auto-rebuild integration |
| FORBIDDEN | B-decorators | 0 | Core decorator API unchanged |
| FORBIDDEN | B-validation | 0 | Validation logic unchanged |
| FORBIDDEN | B-config | 0 | Config schema unchanged |
| FORBIDDEN | B-hashing | 0 | Hashing logic unchanged |
| FORBIDDEN | B-languages | 0 | Language analyzers unchanged |
| FORBIDDEN | B-audit | 1 | Audit logic unchanged |

---

### Brick Details

#### B-staleness (NEW - Add During Implementation)

- **Layer:** 0
- **Purpose:** Detect whether graphs are stale by comparing git state to stored metadata
- **Units:**
  - M-jig.staleness
- **Dependencies:** B-config (for path resolution)
- **Note:** Add to `bricks.yaml` when `src/jig/staleness.py` is created (brick validation requires module to exist)

#### B-impl-graph Modifications

- **Current units:** M-jig.impl_graph.graph, M-jig.impl_graph.builder, M-jig.impl_graph.ndjson_writer
- **Add units:** (none)
- **Layer change:** (none - stays at layer 0)
- **Changes:** `ndjson_writer.py` writes git metadata to `_meta` block per S-068

#### B-intent-graph Modifications

- **Current units:** M-jig.intent_graph.generator
- **Add units:** (none)
- **Layer change:** (none - stays at layer 0)
- **Changes:** `generator.py` writes git metadata to `_meta` block per S-068

#### B-verification-graph Modifications

- **Current units:** M-jig.verification_graph.discovery, M-jig.verification_graph.analyzer, M-jig.verification_graph.builder
- **Add units:** (none)
- **Layer change:** (none - stays at layer 1)
- **Changes:** `builder.py` writes git metadata to `_meta` block per S-068

#### B-cli Modifications

- **Current units:** M-jig.cli.main, M-jig.cli.validate, M-jig.cli.layers, M-jig.cli.verify, M-jig.cli.discovery, M-jig.cli.rebuild, M-jig.cli.show, M-jig.cli.audit
- **Add units:** (none - logic added to existing modules)
- **Layer change:** (none - stays at layer 1)
- **New dependencies:** B-staleness (layer 0)
- **Changes:** 
  - `main.py`: Add global `--no-rebuild` flag
  - `validate.py`, `show.py`, `audit.py`: Call auto-rebuild helper before execution

#### FORBIDDEN Bricks

These bricks MUST NOT be modified by any work unit:

- **B-decorators** (layer 0): Core decorator API is stable
- **B-validation** (layer 0): Validation logic unaffected by auto-rebuild
- **B-config** (layer 0): Configuration schema unchanged
- **B-hashing** (layer 0): Content hashing logic unchanged
- **B-languages** (layer 0): Language analyzers unchanged
- **B-audit** (layer 1): Audit system logic unchanged (only auto-rebuild before audit)

**Sub-agent constraint:** Any modification to FORBIDDEN bricks is an immediate escalation trigger.

---

## Layer/Dependency Analysis

### Layer Structure (Affected Bricks)

```
Layer 0: FOUNDATION
  B-staleness (NEW)
    └─► depends on: B-config ✓
  B-impl-graph (MODIFY)
    └─► no new dependencies
  B-intent-graph (MODIFY)
    └─► no new dependencies

Layer 1: INTEGRATION
  B-verification-graph (MODIFY)
    └─► no new dependencies
  B-cli (MODIFY)
    └─► NEW dependency: B-staleness (layer 0 → layer 1) ✓
```

### Dependency Constraints

- B-staleness (layer 0) MUST NOT depend on B-cli (layer 1)
- B-staleness (layer 0) MUST NOT depend on B-verification-graph (layer 1)
- B-cli (layer 1) MAY depend on B-staleness (layer 0) ✓
- No circular dependencies introduced

### Validation Commands

After implementation, verify with:
```bash
jigy rebuild && jigy validate
jigy show layers  # Confirm layer structure
```

---

## @jig Decorator Changes

### Decorators to ADD

| Type | Location | Spec |
|------|----------|------|
| implements | F-jig.staleness.is_stale | S-069 |
| implements | F-jig.staleness.get_staleness_status | S-069 |
| implements | F-jig.impl_graph.ndjson_writer.* (metadata logic) | S-068 |
| implements | F-jig.intent_graph.generator.* (metadata logic) | S-068 |
| implements | F-jig.verification_graph.builder.* (metadata logic) | S-068 |
| implements | F-jig.cli.validate.* (auto-rebuild logic) | S-070 |
| implements | F-jig.cli.show.* (auto-rebuild logic) | S-070 |
| implements | F-jig.cli.audit.* (auto-rebuild logic) | S-070 |
| implements | F-jig.cli.main.* (--no-rebuild flag) | S-071 |

### Decorators to REMOVE

(none)

### Decorators to MODIFY

(none)

---

## Clean Break Actions

This work follows clean break protocol:

- [x] No backwards compatibility shims needed (new feature, not replacing existing)
- [x] No old code paths to delete (additive change)
- [x] No deprecated O/S nodes

### Code to Add (Not Delete)

- `src/jig/staleness.py` (new module)
- Git metadata logic in graph builders
- Auto-rebuild integration in CLI commands
- `--no-rebuild` flag in CLI main

---

## Test Requirements

### Unit Tests

| Test File | Coverage |
|-----------|----------|
| `tests/unit/test_staleness.py` | S-069: is_stale(), get_staleness_status(), git helpers |

### Integration Tests

| Test File | Coverage |
|-----------|----------|
| `tests/cli/test_auto_rebuild.py` | S-070, S-071: Auto-rebuild behavior, --no-rebuild flag |

### Test Cases (from SCOPE)

- Fresh project (no graphs) → rebuilds all
- Nothing changed → no rebuild, fast completion
- Source file modified → only impl rebuilds
- Test file modified → only verify rebuilds
- Spec file modified → only intent rebuilds
- New uncommitted file → detects as dirty
- Non-git project → always rebuilds (graceful fallback)
- `--no-rebuild` flag → skips staleness check

---

## Work Unit Mapping (from SCOPE)

| SCOPE WU | Specs | Files |
|----------|-------|-------|
| WU1: Staleness Detection Module | S-069 | `src/jig/staleness.py` |
| WU2: Update Graph Metadata | S-068 | `ndjson_writer.py`, `builder.py`, `generator.py` |
| WU3: Add Auto-Rebuild to Commands | S-070 | `validate.py`, `show.py`, `audit.py` |
| WU4: Add `--no-rebuild` Flag | S-071 | `main.py` |
| WU5: Tests | S-069, S-070, S-071 | `test_staleness.py`, `test_auto_rebuild.py` |

---

## Approval Checklist

Before human approval:

- [x] All existing specs reviewed for REUSE opportunities (S-058, S-065 reused)
- [x] New specs follow evergreen guidelines (behavior, not implementation)
- [x] Brick layer constraints validated
- [x] FORBIDDEN bricks identified (6 bricks protected)
- [x] @jig decorator plan complete
- [x] Clean break actions specified (additive change, no deletions)
- [x] Test requirements documented

---

**Awaiting human approval before proceeding to PLAN.**

