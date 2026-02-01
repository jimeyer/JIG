---
title: "JIGPLAN: CLI Command Consolidation"
type: jigplan
status: active
created: 1737741600
created_human: "2026-01-24 14:00 CST"
parent: "[[E023_SCOPE_CLI_Command_Consolidation]]"
children: ["[[E023_PLAN_CLI_Command_Consolidation]]"]
---

# JIGPLAN: CLI Command Consolidation

**SCOPE:** dig/wip/E023_SCOPE_CLI_Command_Consolidation.md
**Date:** 2026-01-24
**Status:** Draft
**Author:** Agent

---

## Summary

Consolidates jigy CLI around the `context` command. Deletes 2 specs (S-059 align, S-060 show), updates 2 specs (S-110, S-111), creates 2 specs (S-114 overview, S-115 aliases). Affects B-cli brick only. No layer changes.

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| UPDATE | O-019 | Intuitive CLI Experience | Remove S-059, S-060 refs; add S-110, S-114, S-115 |
| UPDATE | O-030 | Graph Neighborhood Exploration | Add S-114 reference |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| DELETE | S-059 | Align Command | Use `validate` which already auto-rebuilds |
| DELETE | S-060 | Show Command Structure | Folded into `context` overview |
| UPDATE | S-110 | Context CLI Command | Make identifier optional; add overview mode |
| UPDATE | S-111 | Context Identifier Resolution | Graceful fallback instead of error |
| CREATE | S-114 | Project Overview Output | Unified overview content |
| CREATE | S-115 | CLI Command Aliases | Maps hallucinated commands to real ones |

---

## O/S Node Details

### Nodes to UPDATE

#### S-110 Update Details

**Current behavior:** Requires identifier, errors on invalid

**Changes:**
- ADD: Bare mode returns Project Overview (S-114)
- ADD: Graceful fallback mode returns overview + "not found" note
- ADD: Reference O-019 in outcomes (CLI experience)
- MODIFY: Identifier is now optional

#### S-111 Update Details

**Current behavior:** Errors on unresolved identifiers

**Changes:**
- MODIFY: Unresolved identifiers return overview + note, not error
- ADD: Resolution process explicitly handles empty/None input
- ADD: Resolution outcomes table documenting all cases

### Nodes to DELETE

#### S-059 Deletion Rationale

**Reason:** `jigy validate` already auto-rebuilds stale graphs (S-070). The `align` command is redundant.
**Superseded by:** `jigy validate` (with auto-rebuild)
**Clean break:** Delete `align_command()` from main.py

#### S-060 Deletion Rationale

**Reason:** All show subcommands folded into context overview
**Superseded by:** S-110 (bare context) and S-114 (overview content)
**Clean break:** Delete show.py module, remove show command group

### Nodes to CREATE

#### S-114: Project Overview Output (NEW)

**File:** `jig/specifications/S-114_Project_Overview_Output.md` (created)
**Outcomes:** O-019, O-030
**Summary:** Defines unified overview content (charter, goals, architecture, outcomes, specs, bricks, towers, traversal keys)

#### S-115: CLI Command Aliases (NEW)

**File:** `jig/specifications/S-115_CLI_Command_Aliases.md` (created)
**Outcomes:** O-019
**Summary:** Maps hallucinated commands (graph, list, show, bricks, layers, towers, fix) to core commands

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| MODIFY | B-cli | 1 | Remove show.py, update main.py and context.py |
| FORBIDDEN | B-validation | 0 | Core validation unaffected |
| FORBIDDEN | B-impl-graph | 0 | Graph generation unaffected |
| FORBIDDEN | B-intent-graph | 0 | Intent generation unaffected |
| FORBIDDEN | B-rules | 0 | Rules engine unaffected |
| UNAFFECTED | B-mend | 0 | Mend logic unchanged (alias just invokes it) |

---

### Brick Details

#### B-cli Modifications

- **Current units:** M-jig.cli.main, M-jig.cli.validate, M-jig.cli.discovery, M-jig.cli.rebuild, M-jig.cli.show, M-jig.cli.audit, M-jig.cli.auto_rebuild, M-jig.cli.output, M-jig.cli.init, M-jig.cli.mend, M-jig.cli.context
- **Remove units:** M-jig.cli.show (delete entire module)
- **Layer change:** None (stays at layer 1)
- **Changes:**
  - main.py: Remove align command, remove show group, add aliases
  - context.py: Add overview mode, graceful fallback

#### FORBIDDEN Bricks

These bricks MUST NOT be modified:

- **B-validation** (layer 0): Core validation logic unrelated to CLI surface
- **B-impl-graph** (layer 0): Graph building unrelated to CLI consolidation
- **B-intent-graph** (layer 0): Intent graph building unaffected
- **B-rules** (layer 0): Rules engine stable

---

## Layer/Dependency Analysis

### Layer Structure (Affected Bricks)

```
Layer 0: FORBIDDEN
  B-validation, B-impl-graph, B-intent-graph, B-rules, B-mend

Layer 1: AFFECTED
  B-cli (MODIFY)
    └─► depends on: Layer 0 bricks ✓
```

### Dependency Constraints

- B-cli at layer 1 already depends on layer 0 bricks
- No new dependencies introduced
- No layer changes

### Validation Commands

After implementation:
```bash
jigy rebuild && jigy validate
jigy layers  # Confirm layer structure unchanged
```

---

## @jig Decorator Changes

### Decorators to ADD

| Type | Location | Spec |
|------|----------|------|
| implements | context.py:build_overview() | S-114 |
| implements | main.py:register_aliases() | S-115 |
| verifies | test_context.py:test_bare_context_returns_overview | S-110 |
| verifies | test_context.py:test_invalid_id_graceful_fallback | S-111 |
| verifies | test_context.py:test_overview_content | S-114 |
| verifies | test_aliases.py:test_graph_alias | S-115 |
| verifies | test_aliases.py:test_fix_alias | S-115 |

### Decorators to REMOVE

| Type | Location | Spec | Reason |
|------|----------|------|--------|
| implements | main.py:align_command | S-059 | Spec deleted |
| implements | show.py:show_overview_command | S-060 | Spec deleted |
| implements | show.py:show_layers_command | S-060 | Spec deleted |
| implements | show.py:show_bricks_command | S-060 | Spec deleted |
| implements | show.py:show_charter_command | S-060 | Spec deleted |
| implements | show.py:show_goals_command | S-060 | Spec deleted |
| implements | show.py:show_architecture_command | S-060 | Spec deleted |
| implements | show.py:show_towers_command | S-060 | Spec deleted |
| implements | show.py:show_matrix_command | S-060 | Spec deleted |
| verifies | test_cli.py:test_align_* | S-059 | Spec deleted |
| verifies | test_show.py:* | S-060 | Spec deleted |

### Decorators to MODIFY

None. Existing S-110/S-111/S-112/S-113 decorators remain valid.

---

## Clean Break Actions

This work follows clean break protocol:

- [x] Old code paths will be DELETED, not feature-flagged
- [x] Old tests will be DELETED and new tests written from scratch
- [x] No backwards compatibility shims
- [x] Deleted O/S nodes removed after final validation

### Code to Delete

- `src/jig/cli/show.py` (entire module - 1278 lines)
- `align_command()` in main.py
- `tests/unit/cli/test_show.py` (if exists)
- `tests/unit/cli/test_align.py` (if exists)

### O/S Nodes to Delete (After Validation)

- `jig/specifications/S-059_Align_Command.md`
- `jig/specifications/S-060_Show_Command_Structure.md`

---

## Fresh Agent Review Summary

### Review Findings

| Category | Type | Severity | Issue | Resolution |
|----------|------|----------|-------|------------|
| 1 | MECHANICAL | NOTE | S-059/S-060 validation errors expected | Deletion planned |
| 4 | MECHANICAL | NOTE | New specs created, outcomes updated | Done |

### Judgment Decisions

No judgment issues requiring Charter philosophy. The consolidation follows the SCOPE directly.

---

## Approval Checklist

Before human approval:

- [x] All existing specs reviewed for REUSE opportunities
- [x] New specs follow evergreen guidelines (behavior, not implementation)
- [x] Brick layer constraints validated
- [x] FORBIDDEN bricks identified
- [x] @jig decorator plan complete
- [x] Clean break actions specified
- [x] Fresh Agent Review completed
- [x] All MECHANICAL issues resolved
- [x] All JUDGMENT issues resolved via Charter philosophy OR escalated

---

**Awaiting human approval before proceeding to PLAN.**
