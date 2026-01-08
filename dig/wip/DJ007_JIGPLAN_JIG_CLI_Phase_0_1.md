---
title: "JIGPLAN: JIG CLI Phase 0 and 1"
type: jigplan
status: implemented
decision: completed
created: 1736207400
created_human: 2026-01-06 16:30 CST
parent: "[[DJ006_SCOPE_JIG_Phase_0_1]]"
children: []
---

# JIGPLAN: JIG CLI Phase 0 and 1

**SCOPE:** dig/wip/DJ006_SCOPE_JIG_Phase_0_1.md
**Date:** 2026-01-06
**Status:** Draft
**Author:** agent

---

## Summary

This JIGPLAN covers JIG CLI Phase 0 (Flag Unification) and Phase 1 (Command Restructuring). It affects 1 brick (B-cli), updates 5 existing specs, creates 2 new specs, and updates 1 outcome. The work adds universal output format flags (`-j/-m/-v`) to all commands and consolidates `towers`/`matrix` under the `show` command group.

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| UPDATE | O-016 | CI and Tooling Integration | Add S-093, S-094 to specifies list |
| REUSE | O-019 | Intuitive CLI Experience | Already supports S-060, S-061 |
| REUSE | O-026 | Towers Enforce Component Isolation | Already supports S-090, S-091 |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| CREATE | S-093 | Universal Output Format Flags | New: defines -j/-m/-v flag behavior |
| CREATE | S-094 | Markdown Output Format | New: defines markdown output structure |
| UPDATE | S-026 | JSON Output Format for CI Integration | Extend to all commands, change flag syntax |
| UPDATE | S-060 | Show Command Structure | Add towers and matrix subcommands |
| UPDATE | S-061 | Minimal Global Options | Allow output format flags |
| UPDATE | S-090 | Jigy Towers Command | Change to `jigy show towers` |
| UPDATE | S-091 | Jigy Matrix Command | Change to `jigy show matrix` |
| REUSE | S-057 | Project Root Auto-Discovery | Unchanged |
| REUSE | S-058 | Verb-First Rebuild Commands | Unchanged |
| REUSE | S-059 | Align Command | Unchanged |
| REUSE | S-070 | Auto-Rebuild Before Commands | Unchanged |
| REUSE | S-071 | Skip Auto-Rebuild Flag | Unchanged |

---

## O/S Node Details

### Nodes Updated

#### O-016 Update Details

**Change:** Added S-093 and S-094 to `specifies` list.

```yaml
specifies: [S-026, S-093, S-094]  # was: [S-026]
```

#### S-026 Update Details

**Previous acceptance criteria:**
- Flag `--format json` available on validate commands only
- Specific to validation output

**Changes:**
- MODIFY: Flag changed from `--format json` to `-j/--json`
- MODIFY: Available on ALL commands, not just validate
- ADD: Verbose JSON mode (`-j -v`)
- ADD: Schema definitions for rebuild and show commands

#### S-060 Update Details

**Previous commands:**
- `jigy show`, `jigy show layers`, `jigy show bricks`

**Changes:**
- ADD: `jigy show towers` (moved from standalone)
- ADD: `jigy show matrix` (moved from standalone)
- ADD: Output format flag support (`-j/-m/-v`)

#### S-061 Update Details

**Previous stance:**
- `--format` removed (human-readable only)
- `--verbose` removed

**Changes:**
- ADD: Universal output flags section
- ADD: `-j/--json`, `-m/--markdown`, `-v/--verbose` as command-level flags
- MODIFY: Rationale updated to explain agent/CI integration need

#### S-090 Update Details

**Previous command:** `jigy towers`

**Changes:**
- MODIFY: Command changed to `jigy show towers`
- ADD: Output format flag support (`-j/-m/-v`)
- ADD: Reference to S-060 for show group membership

#### S-091 Update Details

**Previous command:** `jigy matrix`

**Changes:**
- MODIFY: Command changed to `jigy show matrix`
- ADD: Output format flag support (`-j/-m/-v`)
- ADD: Reference to S-060 for show group membership

---

### Nodes Created

#### S-093: Universal Output Format Flags (NEW)

**File:** `jig/specifications/S-093_Universal_Output_Format_Flags.md`
**Implements:** O-016
**Summary:** Defines the `-j/-m/-v` flags available on all CLI commands, their mutual exclusivity rules, and the shared infrastructure pattern.

#### S-094: Markdown Output Format (NEW)

**File:** `jig/specifications/S-094_Markdown_Output_Format.md`
**Implements:** O-016
**Summary:** Defines the structure and semantics of markdown output when `-m` flag is used, optimized for LLM consumption.

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| MODIFY | B-cli | 1 | Add output.py module, refactor commands |
| MODIFY | B-validation | 0 | Add markdown formatter to reporting.py |
| FORBIDDEN | B-decorators | 0 | Core decorator infrastructure unchanged |
| FORBIDDEN | B-impl-graph | 0 | Graph generation unchanged |
| FORBIDDEN | B-intent-graph | 0 | Intent graph unchanged |
| FORBIDDEN | B-config | 0 | Configuration unchanged |
| FORBIDDEN | B-hashing | 0 | Hashing unchanged |
| FORBIDDEN | B-languages | 0 | Language analyzers unchanged |
| FORBIDDEN | B-verification-graph | 1 | Verification graph unchanged |
| FORBIDDEN | B-audit | 1 | Audit system unchanged |
| FORBIDDEN | B-staleness | 0 | Staleness detection unchanged |

---

### Brick Details

#### B-cli Modifications

- **Current units:** 10 modules
- **Add units:** `M-jig.cli.output` (new module)
- **Delete units:** None (layers.py, verify.py, towers.py stay until code moved/deleted)
- **Layer change:** None (stays at layer 1)
- **Changes:**
  - Create `output.py` with `OutputFormat` enum and flag decorator
  - Add `@add_output_options` decorator to all commands
  - Move `towers_command` and `matrix_command` from towers.py to show.py
  - Delete orphaned `layers.py` and `verify.py` after merge

#### B-validation Modifications

- **Current units:** 4 modules
- **Add units:** None
- **Layer change:** None (stays at layer 0)
- **Changes:**
  - Add `format_as_markdown()` function to `reporting.py`
  - Extend existing JSON formatter for verbose mode

#### FORBIDDEN Bricks

These bricks MUST NOT be modified:

- **B-decorators** (layer 0): Core `@jig.implements`/`@jig.verifies` decorators
- **B-impl-graph** (layer 0): Implementation graph generation
- **B-intent-graph** (layer 0): Intent graph generation
- **B-config** (layer 0): Configuration discovery and parsing
- **B-hashing** (layer 0): Content hashing
- **B-languages** (layer 0): Language analyzers
- **B-verification-graph** (layer 1): Verification graph generation
- **B-audit** (layer 1): Coverage audit system
- **B-staleness** (layer 0): Staleness detection

---

## Layer/Dependency Analysis

### Layer Structure (Affected Bricks)

```
Layer 0: FORBIDDEN (no changes)
  B-decorators
  B-validation ← ADD markdown formatter only
  B-impl-graph
  B-intent-graph
  B-config
  B-hashing
  B-languages
  B-staleness

Layer 1: AFFECTED
  B-cli (MODIFY)
    └─► depends on: B-validation, B-config, B-staleness ✓
  B-verification-graph (FORBIDDEN)
  B-audit (FORBIDDEN)
```

### Dependency Constraints

- B-cli (layer 1) depends on B-validation (layer 0) for formatting ✓
- B-cli (layer 1) depends on B-config (layer 0) for configuration ✓
- No new cross-brick dependencies introduced
- No layer constraint violations

---

## @jig Decorator Changes

### Decorators to ADD

| Type | Location | Spec |
|------|----------|------|
| implements | F-jig.cli.output.OutputFormat | S-093 |
| implements | F-jig.cli.output.add_output_options | S-093 |
| implements | F-jig.cli.output.resolve_format | S-093 |
| implements | F-jig.validation.reporting.format_as_markdown | S-094 |

### Decorators to MODIFY

| Type | Location | Old Spec | New Spec | Reason |
|------|----------|----------|----------|--------|
| implements | F-jig.cli.show.* | S-060 | S-060 | Spec updated |
| implements | F-jig.cli.towers.towers_command | S-090 | S-090 | Spec updated, move to show.py |
| implements | F-jig.cli.towers.matrix_command | S-091 | S-091 | Spec updated, move to show.py |

### Decorators to REMOVE

| Type | Location | Spec | Reason |
|------|----------|------|--------|
| implements | F-jig.cli.layers.* | (none) | Orphaned code, merge to show.py |
| implements | F-jig.cli.verify.* | (none) | Orphaned code, delete |

---

## Clean Break Actions

This work follows clean break protocol:

- [x] No backwards compatibility for old command names (`jigy towers` → `jigy show towers`)
- [x] No deprecation warnings (single user, clean break)
- [x] Orphaned code will be DELETED, not preserved
- [x] Old tests for moved commands will be updated, not duplicated

### Code to Delete

- `src/jig/cli/verify.py` (orphaned, redundant with `rebuild verify`)

### Code to Move

- `src/jig/cli/towers.py` → merge `towers_command` and `matrix_command` into `src/jig/cli/show.py`
- `src/jig/cli/layers.py` → merge useful functions into `src/jig/cli/show.py` if not already present

### Files to Create

- `src/jig/cli/output.py` (OutputFormat enum, decorators, formatters)

---

## Validation Commands

After implementation, verify with:

```bash
# Verify specs and bricks
jigy rebuild && jigy validate

# Test flag unification (Phase 0)
jigy validate -j          # JSON output
jigy validate -m          # Markdown output
jigy validate -v          # Verbose output
jigy validate -j -v       # Verbose JSON
jigy validate -j -m       # Should error (mutually exclusive)

# Test command restructuring (Phase 1)
jigy show towers          # Works
jigy show matrix          # Works
jigy towers               # Should fail (command not found)
```

---

## Approval Checklist

Before human approval:

- [x] All existing specs reviewed for REUSE opportunities
- [x] New specs follow evergreen guidelines (behavior, not implementation)
- [x] Brick layer constraints validated
- [x] FORBIDDEN bricks identified (9 bricks protected)
- [x] @jig decorator plan complete
- [x] Clean break actions specified
- [x] `jigy rebuild && jigy validate` passes

---

**Awaiting human approval before proceeding to PLAN.**
