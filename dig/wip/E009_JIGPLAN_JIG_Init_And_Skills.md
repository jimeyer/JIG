---
title: "JIGPLAN: JIG Init and Skills"
type: jigplan
status: active
created: 1737237600
created_human: "2026-01-18 16:00 CST"
parent: "[[E006_SCOPE_JIG_Init_And_Skills]]"
children: []
---
# JIGPLAN: JIG Init and Skills

**SCOPE:** dig/wip/E006_SCOPE_JIG_Init_And_Skills.md
**Date:** 2026-01-18
**Status:** Approved
**Author:** agent

---

## Summary

Implements `jigy init` command and `/jig` agent skill. Creates 1 new outcome (O-028), 8 new specs (S-096 through S-103), and 2 new bricks (B-templates, B-init). Extends B-cli with M-jig.cli.init. Clean break - no backwards compatibility needed (greenfield feature).

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | O-019 | Intuitive CLI Experience | Init follows existing CLI patterns |
| REUSE | O-020 | Configurable Project Structure | jig.toml config aligns with existing config system |
| CREATE | O-028 | Easy Project Onboarding | New outcome for project bootstrapping value |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | S-061 | Minimal Global Options | Init uses standard -j/-m flags |
| REUSE | S-062 | Configuration File Discovery | Init creates jig.toml per existing discovery pattern |
| REUSE | S-093 | Universal Output Format Flags | Init supports -j/--json, -m/--markdown |
| CREATE | S-096 | Jigy Init Command | Main command behavior |
| CREATE | S-097 | Init Configuration Generation | jig.toml template |
| CREATE | S-098 | Init Charter Generation | Charter_<project>.md template |
| CREATE | S-099 | Init Bricks Scaffold | bricks.yaml scaffold |
| CREATE | S-100 | Init Generated Directory Management | jig/generated/ and .gitignore |
| CREATE | S-101 | Init Skill Installation | .agent/skills/jig/ installation |
| CREATE | S-102 | Init Idempotent Behavior | Safe re-run semantics |
| CREATE | S-103 | Init CLI Flags | --project, --no-skills, etc. |

---

## O/S Node Details

### Nodes to CREATE

All nodes have been written to disk per taskMakeJIGPLAN Step 5.

#### O-028: Easy Project Onboarding (NEW)

**File:** `jig/outcomes/O-028_Easy_Project_Onboarding.md`
**Supports:** G-002 (Continuity across sessions)
**Summary:** Projects can be bootstrapped with consistent JIG structure in one command, reducing onboarding friction.

#### S-096: Jigy Init Command (NEW)

**File:** `jig/specifications/S-096_Jigy_Init_Command.md`
**Outcome:** O-028
**Summary:** Creates project scaffolding (jig.toml, jig/ structure, skills) from current directory.

#### S-097: Init Configuration Generation (NEW)

**File:** `jig/specifications/S-097_Init_Configuration_Generation.md`
**Outcome:** O-028
**Summary:** Generates jig.toml with [integration] and [scan] sections; detects dig/ to set include_dig.

#### S-098: Init Charter Generation (NEW)

**File:** `jig/specifications/S-098_Init_Charter_Generation.md`
**Outcome:** O-028
**Summary:** Creates Charter_<project>.md with G-1 placeholder goal.

#### S-099: Init Bricks Scaffold (NEW)

**File:** `jig/specifications/S-099_Init_Bricks_Scaffold.md`
**Outcome:** O-028
**Summary:** Creates bricks.yaml with `bricks: []` scaffold.

#### S-100: Init Generated Directory Management (NEW)

**File:** `jig/specifications/S-100_Init_Generated_Directory_Management.md`
**Outcome:** O-028
**Summary:** Creates jig/generated/ and appends to .gitignore if needed.

#### S-101: Init Skill Installation (NEW)

**File:** `jig/specifications/S-101_Init_Skill_Installation.md`
**Outcome:** O-028
**Summary:** Installs SKILL.md and contextJIG.md to .agent/skills/jig/ (or ~/.agent/skills/ with --global-skills).

#### S-102: Init Idempotent Behavior (NEW)

**File:** `jig/specifications/S-102_Init_Idempotent_Behavior.md`
**Outcome:** O-028
**Summary:** Second run is safe; creates nothing if structure exists; skills always refresh.

#### S-103: Init CLI Flags (NEW)

**File:** `jig/specifications/S-103_Init_CLI_Flags.md`
**Outcome:** O-028
**Summary:** Defines --project, --no-skills, --skills-only, --global-skills, --force flags.

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| CREATE | B-templates | 0 | Template string constants (no dependencies) |
| CREATE | B-init | 0 | Core init logic, depends only on config |
| MODIFY | B-cli | 1 | Add M-jig.cli.init |
| FORBIDDEN | B-decorators | 0 | Core decorator infrastructure |
| FORBIDDEN | B-validation | 0 | Validation infrastructure |
| FORBIDDEN | B-impl-graph | 0 | Graph generation |
| FORBIDDEN | B-intent-graph | 0 | Graph generation |
| FORBIDDEN | B-config | 0 | May use but must not modify |
| UNAFFECTED | B-hashing | 0 | No changes needed |
| UNAFFECTED | B-languages | 0 | No changes needed |
| UNAFFECTED | B-verification-graph | 1 | No changes needed |
| UNAFFECTED | B-audit | 1 | No changes needed |
| UNAFFECTED | B-staleness | 0 | No changes needed |

---

### Brick Details

#### B-templates (NEW)

- **Layer:** 0
- **Purpose:** Template string constants for generated files
- **Units:**
  - M-jig.templates
- **Dependencies:** None (pure data)

**Contains:**
- `JIG_TOML_TEMPLATE` - jig.toml template
- `CHARTER_MD_TEMPLATE` - Charter markdown template
- `BRICKS_YAML_TEMPLATE` - bricks.yaml scaffold
- `SKILL_MD_TEMPLATE` - SKILL.md content
- `CONTEXT_JIG_MD_TEMPLATE` - contextJIG.md content

#### B-init (NEW)

- **Layer:** 0
- **Purpose:** Core initialization logic
- **Units:**
  - M-jig.init
- **Dependencies:** B-templates (layer 0), B-config (layer 0)

**Contains:**
- `InitResult` dataclass
- `init_project()` function - main logic
- `install_skills()` function - skill installation

#### B-cli Modifications

- **Current units:** M-jig.cli.main, M-jig.cli.validate, M-jig.cli.discovery, M-jig.cli.rebuild, M-jig.cli.show, M-jig.cli.audit, M-jig.cli.auto_rebuild, M-jig.cli.output
- **Add units:** M-jig.cli.init
- **Layer change:** None (stays at layer 1)
- **New dependencies:** B-init (layer 0)

#### FORBIDDEN Bricks

These bricks MUST NOT be modified by any work unit:

- **B-decorators** (layer 0): Core `@jig.implements`/`@jig.verifies` infrastructure
- **B-validation** (layer 0): Validation engine
- **B-impl-graph** (layer 0): Implementation graph generation
- **B-intent-graph** (layer 0): Intent graph generation
- **B-config** (layer 0): May be used (read) but not modified

**Sub-agent constraint:** Any modification to FORBIDDEN bricks is an immediate escalation trigger.

---

## Layer/Dependency Analysis

### Layer Structure (Affected Bricks)

```
Layer 0: FOUNDATION
  B-templates (NEW)
    └─► depends on: nothing (pure data)
  B-init (NEW)
    └─► depends on: B-templates, B-config ✓

Layer 1: AFFECTED
  B-cli (MODIFY)
    └─► depends on: B-init, B-config, B-validation, etc. ✓
```

### Dependency Constraints

- B-templates (layer 0) has NO dependencies
- B-init (layer 0) depends only on layer 0 bricks (B-templates, B-config)
- B-cli (layer 1) depends on layer 0 bricks including new B-init
- No circular dependencies

### Validation Commands

After implementation, verify with:
```bash
jigy rebuild && jigy validate
jigy show layers  # Confirm layer structure
```

**Note:** Current brick validation shows expected errors for not-yet-implemented modules:
- `M-jig.cli.init` not found
- `M-jig.templates` not found
- `M-jig.init` not found

These will resolve once implementation is complete.

---

## @jig Decorator Changes

### Decorators to ADD

| Type | Location | Spec |
|------|----------|------|
| implements | F-jig.init.init_project | S-096, S-097, S-098, S-099, S-102 |
| implements | F-jig.init.update_gitignore | S-100 |
| implements | F-jig.init.install_skills | S-101 |
| implements | F-jig.cli.init.init_command | S-103 |
| verifies | T-test_init.test_init_creates_structure | S-096 |
| verifies | T-test_init.test_init_idempotent | S-102 |
| verifies | T-test_templates.test_jig_toml_template | S-097 |
| verifies | T-test_templates.test_charter_template | S-098 |
| verifies | T-test_templates.test_bricks_yaml_template | S-099 |
| verifies | T-test_init.test_gitignore_update | S-100 |
| verifies | T-test_init.test_skill_installation | S-101 |
| verifies | T-test_init.test_cli_flags | S-103 |

### Decorators to REMOVE

None.

### Decorators to MODIFY

None.

---

## Clean Break Actions

This work follows clean break protocol (greenfield feature, no existing code to replace):

- [x] No old code paths to delete (greenfield)
- [x] No backwards compatibility needed
- [x] No feature flags
- [x] Skills always overwrite (templates, not user content)

### Code to Delete

None (greenfield feature).

### O/S Nodes to Delete (After Validation)

None.

---

## Version Bump

Per SCOPE:
- `src/jig/__init__.py` → `__version__ = "0.2.0"`
- `pyproject.toml` → `version = "0.2.0"`

---

## Implementation Notes

### File Structure

```
src/jig/
├── __init__.py              # Version bump to 0.2.0
├── templates/
│   ├── __init__.py          # Module init
│   └── templates.py         # Template constants
├── init.py                  # Core init logic
└── cli/
    └── init.py              # CLI command
```

### Skill Files (Template Content)

SKILL.md and contextJIG.md content is defined in E006 SCOPE. Implementation should use those exact templates.

### Testing Strategy

- Unit tests for template content validity (YAML/TOML parsing)
- Unit tests for init_project() with temp directories
- Unit tests for idempotency (run twice, second creates nothing)
- Integration test: init → jigy validate passes

---

## Approval Checklist

Before human approval:

- [x] All existing specs reviewed for REUSE opportunities
- [x] New specs follow evergreen guidelines (behavior, not implementation)
- [x] Brick layer constraints validated
- [x] FORBIDDEN bricks identified
- [x] @jig decorator plan complete
- [x] Clean break actions specified
- [x] O/S node files written to disk
- [x] Intent validation passes (`jigy validate intent`)

---

**Awaiting human approval before proceeding to PLAN.**
