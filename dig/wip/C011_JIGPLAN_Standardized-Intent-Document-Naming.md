---
title: "JIGPLAN: Standardized Intent Document Naming"
type: jigplan
status: active
created: 1767550000
created_human: "2026-01-04 12:00 CST"
parent: "[[C010_SCOPE_Standardized-Intent-Document-Naming]]"
children: ['[[C012_PLAN_Standardized-Intent-Document-Naming]]']
---
# JIGPLAN: Standardized Intent Document Naming

**SCOPE:** docs/wip/C010_SCOPE_Standardized-Intent-Document-Naming.md
**Date:** 2026-01-04
**Status:** Draft
**Author:** AI Agent (Claude)

---

## Summary

This JIGPLAN defines the architectural changes for C010: Standardized Intent Document Naming. The work updates 3 existing specs (S-018, S-019, S-076) to require title-in-filename format and H1 matching, and creates 1 new spec (S-092) for title selection guidance. One new outcome (O-027) groups the new documentation spec. Changes affect B-validation brick only.

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | O-005 | Actionable Error Messages | Contains S-018, S-019; validation improvements serve this outcome |
| REUSE | O-024 | Architecture Constrains Specifications | Contains S-076; H1 matching addition serves same outcome |
| CREATE | O-027 | Discoverable Intent Document Naming | New outcome for S-092 title guidance |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| UPDATE | S-018 | Specification File Validation | Add filename format `S-{NNN}_{Title}.md`, H1 must match title |
| UPDATE | S-019 | Outcome File Validation | Add filename format `O-{NNN}_{Title}.md`, H1 must match title |
| UPDATE | S-076 | Architecture File Location | Add H1 must match title (remove ID prefix from H1) |
| CREATE | S-092 | Intent Document Title Requirements | Documentation spec for title selection guidance |

---

## O/S Node Details

### Nodes to UPDATE

#### S-018 Update Details

**Current acceptance criteria:**
- Parse YAML frontmatter from specification markdown files
- Required fields validated: `id`, `type`
- ID format validated: must match `S-{number}` pattern
- ID uniqueness validated: no duplicate spec IDs across all files
- Filename matches ID: `S-001.md` must have `id: S-001` in frontmatter
- Excluded fields rejected: `brick`, `depends_on`, `content` must NOT be present
- Error messages include file path and specific field violations

**Changes:**
- ADD: Required field `title` in frontmatter
- MODIFY: ID format to `S-{NNN}` (3-digit zero-padded)
- ADD: Filename MUST follow pattern `S-{NNN}_{Title_Snake_Case}.md`
- ADD: Filename title MUST match frontmatter `title` field
- ADD: First H1 in body MUST match frontmatter `title` exactly
- ADD: H1 MUST NOT include ID prefix

#### S-019 Update Details

**Current acceptance criteria:**
- Parse YAML frontmatter from outcome markdown files
- Required fields validated: `id`, `type`
- ID format validated: must match `O-{number}` pattern
- ID uniqueness validated
- Excluded fields rejected: `brick`
- Validation works when no outcome files present

**Changes:**
- ADD: Required field `title` in frontmatter
- MODIFY: ID format to `O-{NNN}` (3-digit zero-padded)
- ADD: Filename MUST follow pattern `O-{NNN}_{Title_Snake_Case}.md`
- ADD: Filename title MUST match frontmatter `title` field
- ADD: First H1 in body MUST match frontmatter `title` exactly
- ADD: H1 MUST NOT include ID prefix

#### S-076 Update Details

**Current acceptance criteria:**
- Architecture files in jig/architecture/ directory
- Files follow naming pattern A-{NNN}_{Title}.md
- File name matches internal id

**Changes:**
- ADD: Filename title MUST match frontmatter `title` field
- ADD: First H1 MUST match frontmatter `title` exactly
- ADD: H1 MUST NOT include ID prefix (e.g., `# A-001: Title` invalid)

---

### Nodes to CREATE

#### S-092: Intent Document Title Requirements (NEW)

**File:** `jig/specifications/S-092.md` (created)
**Implements:** O-027
**Summary:** Documents title selection guidance for agents. NOT enforced by validation—guidance delivered via CLAUDE.md and Charter.

#### O-027: Discoverable Intent Document Naming (NEW)

**File:** `jig/outcomes/O-027.md` (created)
**Summary:** Intent document filenames include meaningful titles, enabling discovery without opening files.

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| MODIFY | B-validation | 0 | Add filename format, H1 matching validation |
| FORBIDDEN | B-decorators | 0 | Foundation layer, no changes |
| FORBIDDEN | B-impl-graph | 0 | Foundation layer, no changes |
| FORBIDDEN | B-intent-graph | 0 | Foundation layer, no changes |
| FORBIDDEN | B-config | 0 | Foundation layer, no changes |
| UNAFFECTED | B-cli | 1 | No CLI changes needed |
| UNAFFECTED | B-verification-graph | 1 | No changes needed |
| UNAFFECTED | B-audit | 1 | No changes needed |

---

### Brick Details

#### B-validation Modifications

- **Current units:** M-jig.validation.intent, M-jig.validation.bricks, M-jig.validation.models, M-jig.validation.reporting
- **Add units:** (none)
- **Layer change:** (none - stays at layer 0)
- **New dependencies:** (none)
- **Changes:**
  - Add `to_snake_case()` helper function
  - Add `validate_filename_format()` function
  - Add `validate_h1_matches_title()` function
  - Update `validate_specification_files()` to call new functions
  - Update `validate_outcome_files()` to call new functions
  - Update `validate_architecture_files()` to call new functions

#### FORBIDDEN Bricks

These bricks MUST NOT be modified by any work unit:

- **B-decorators** (layer 0): Core decorator definitions
- **B-impl-graph** (layer 0): Implementation graph generation
- **B-intent-graph** (layer 0): Intent graph generation
- **B-config** (layer 0): Configuration loading

**Sub-agent constraint:** Any modification to FORBIDDEN bricks is an immediate escalation trigger.

---

## Layer/Dependency Analysis

### Layer Structure (Affected Bricks)

```
Layer 0: AFFECTED
  B-validation (MODIFY)
    └─► depends on: (none within JIG)

Layer 0: FORBIDDEN
  B-decorators ← no changes
  B-impl-graph ← no changes
  B-intent-graph ← no changes
  B-config ← no changes

Layer 1: UNAFFECTED
  B-cli ← no changes
  B-verification-graph ← no changes
  B-audit ← no changes
```

### Dependency Constraints

- B-validation (layer 0) has no dependencies on other JIG bricks
- Changes are isolated to validation module
- No layer violations possible

### Validation Commands

After implementation, verify with:
```bash
jigy rebuild && jigy validate
jigy layers  # Confirm layer structure
```

---

## @jig Decorator Changes

### Decorators to ADD

| Type | Location | Spec |
|------|----------|------|
| implements | F-jig.validation.intent.to_snake_case | S-018, S-019, S-076 |
| implements | F-jig.validation.intent.validate_filename_format | S-018, S-019, S-076 |
| implements | F-jig.validation.intent.validate_h1_matches_title | S-018, S-019, S-076 |
| verifies | T-test_filename_validation.test_valid_spec_filename | S-018 |
| verifies | T-test_filename_validation.test_valid_outcome_filename | S-019 |
| verifies | T-test_filename_validation.test_h1_matches_title | S-018, S-019, S-076 |

### Decorators to REMOVE

(none)

### Decorators to MODIFY

(none - existing validation functions already have decorators, they will gain additional behavior)

---

## Clean Break Actions

This work follows clean break protocol:

- [x] No backwards compatibility shims needed (adding validation, not removing)
- [x] No feature flags
- [x] Migration script provides clean transition for existing files
- [ ] After migration: all files renamed, validation enforced

### Files to Create

- `scripts/migrate_intent_filenames.py` - Migration script for renaming files

### Migration Scope

| Type | Count | Current Pattern | Target Pattern |
|------|-------|-----------------|----------------|
| Specification | 75 | `S-{NNN}.md` | `S-{NNN}_{Title}.md` |
| Outcome | 23 | `O-{NNN}.md` | `O-{NNN}_{Title}.md` |
| Architecture | 1 | `A-{NNN}_{Title}.md` | (already compliant, update H1 only) |

**Note:** Migration happens AFTER validation code is updated, so new validation can verify correct migration.

---

## Agent Context Updates (Non-Code)

Per SCOPE J.5, title guidance must be added to agent context:

### CLAUDE.md Updates

Add "Creating JIG Intent Documents" section with title selection guidance.

### Charter Updates

Add title guidance to "For AI Agents" section.

**Note:** These are documentation updates, not code changes. They complement S-092 by making guidance discoverable before file creation.

---

## Approval Checklist

Before human approval:

- [x] All existing specs reviewed for REUSE opportunities
- [x] Updated specs (S-018, S-019, S-076) are evergreen behavior definitions
- [x] New spec (S-092) follows documentation-only pattern (not validated)
- [x] New outcome (O-027) delivers clear business value
- [x] Brick layer constraints validated (B-validation at layer 0)
- [x] FORBIDDEN bricks identified (B-decorators, B-impl-graph, B-intent-graph, B-config)
- [x] @jig decorator plan complete
- [x] Clean break actions specified
- [x] `jigy rebuild && jigy validate` passes

---

**Awaiting human approval before proceeding to PLAN.**
