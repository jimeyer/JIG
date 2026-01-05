---
title: "SCOPE: Historical docs/ to dig/ Migration"
type: scope
status: active
created: 1767600000
created_human: "2026-01-04 15:00 CST"
parent: null
children: ['[[C013_MANIFEST_Docs-to-DIG-Migration]]']
---
# SCOPE: Historical docs/ to dig/ Migration

**ID:** C012
**Date:** 2026-01-04
**Status:** Draft

---

## Executive Summary

This document assesses 133 markdown files in `docs/` for migration to DIG (Deliberation Insight Graph). The files predate DIG but largely follow DIG patterns without the formal structure. This assessment categorizes each folder, recommends disposition, and identifies the transformation requirements.

**Key Finding:** ~85% of docs/ content is deliberation that belongs in dig/. The remaining ~15% is evergreen reference material that should move elsewhere or stay in docs/.

---

## Current State Analysis

### docs/ Structure

| Folder | Files | Description |
|--------|-------|-------------|
| `agents/` | 5 | AI agent context and guide documents |
| `architecture/` | 3 | A001-A003 architectural contracts |
| `audits/` | 2 | Audit results and journals |
| `bricks/` | 34 | AG001-AG029 bricks concept evolution |
| `done/` | 33 | B001-B029 completed deliberation chains |
| `examples/` | 0 | Empty directory |
| `jig-concept/` | 44 | J001-J029 JIG evolution + SELA (13 files) |
| `wip/` | 11 | C001-C011 active deliberation |
| Root | 1 | configuration.md |
| **Total** | **133** | |

### Existing Patterns (Proto-DIG)

Many files already follow DIG-like conventions:

**Type suffixes detected:**
- `_SCOPE_` — Problem/opportunity definition
- `_JIGPLAN_` — Alignment to JIG specs
- `_PLAN_` — Implementation breakdown
- `_JOURNAL_` — Running notes during execution
- `_PROPOSAL_` — Design proposals (divergent thinking)
- `_AUDIT_` — Point-in-time assessments
- `_CONCEPT_` — Concept documents

**Implicit relationships detected:**
- `Supersedes: J016` — Explicit supersession chains
- `SCOPE: B021_SCOPE_...` — Parent references in JIGPLANs
- Same prefix (B021, B022, B023, B024) — Sibling deliberation chains

**What's missing:**
- YAML frontmatter with required DIG fields
- Explicit parent/children wiki links
- Unix epoch timestamps
- Formal status values

---

## Disposition Recommendations

### Category 1: TO DIG (Deliberation) — 110 files

These are deliberation documents that capture reasoning, evolution of thinking, and decision traces.

#### `bricks/` → dig/archive/bricks/ (34 files)

| Pattern | Files | DIG Type | Rationale |
|---------|-------|----------|-----------|
| AG001-AG029 | 29 | exploration | Concept evolution of bricks/alignment graph |
| README.md | 1 | exploration | Overview document |
| Other | 4 | exploration | Supporting proposals |

**Status inference:** All implemented or superseded (concept evolved into current JIG)

**Parent/child structure:**
- AG001 is root (no parent)
- Subsequent docs reference earlier ones
- Chain: AG001 → AG002 → ... → AG029

---

#### `done/` → dig/archive/jigy-v1/ (33 files)

| Pattern | Files | DIG Type | Rationale |
|---------|-------|----------|-----------|
| `B###_SCOPE_*` | 6 | scope | Problem definitions |
| `B###_JIGPLAN_*` | 3 | jigplan | Spec alignment |
| `B###_PLAN_*` | 8 | plan | Implementation breakdown |
| `B###_JOURNAL_*` | 3 | journal | Execution notes |
| `B###_PROPOSAL_*` | 2 | exploration | Design proposals |
| `B###_AUDIT_*` | 2 | journal | Audit records |
| Other B### | 9 | exploration | Mixed deliberation |

**Status inference:** All implemented (in done/ folder)

**Parent/child structure:**
- SCOPE docs are roots within their B### series
- JIGPLAN references SCOPE as parent
- PLAN references JIGPLAN as parent
- JOURNAL references PLAN as parent

**Example chain:**
```
B021_SCOPE_Auto-Rebuild-Staleness.md (root)
  └── B022_JIGPLAN_Auto-Rebuild-Staleness.md
        └── B023_PLAN_Auto-Rebuild-Staleness.md
              └── B024_JOURNAL_Auto-Rebuild-Staleness.md
```

---

#### `wip/` → dig/wip/ (11 files)

| Pattern | Files | DIG Type | Rationale |
|---------|-------|----------|-----------|
| `C###_SCOPE_*` | 2 | scope | Problem definitions |
| `C###_JIGPLAN_*` | 2 | jigplan | Spec alignment |
| `C###_PLAN_*` | 1 | plan | Implementation breakdown |
| `C###_JOURNAL_*` | 1 | journal | Execution notes |
| `C###_PROPOSAL_*` | 4 | exploration | Design proposals |
| `C###_INTENT_EXPLAINER_*` | 1 | exploration | Explanatory doc |

**Status inference:** All active (in wip/ folder)

**Parent/child structure:**
- Same pattern as done/
- C003_SCOPE → C004_JIGPLAN → C008_PLAN → C009_JOURNAL

---

#### `jig-concept/J###` → dig/archive/jig-concept/ (31 files)

| Pattern | Files | DIG Type | Rationale |
|---------|-------|----------|-----------|
| `J###-JIG-Concept-v*` | 8 | exploration | Major version iterations |
| `J###-PROPOSAL_*` | 4 | exploration | Feature proposals |
| `J###-EXPLORATION_*` | 1 | exploration | Open-ended thinking |
| Other J### | 18 | exploration | Supporting concept docs |

**Status inference:**
- Earlier versions (v4-v8) → superseded
- J029 (v10) → implemented (current concept)
- Others → implemented or superseded based on content

**Parent/child structure (supersession chain):**
```
J001 (v4)
  └── J006 (v5)
        └── J010 (v6)
              └── J011 (v6.1)
                    └── J013 (v7)
                          └── J016 (v8)
                                └── J017 (v9)
                                      └── J029 (v10)
```

---

#### `jig-concept/SELA/` → dig/archive/sela/ (13 files)

| Pattern | Files | DIG Type | Rationale |
|---------|-------|----------|-----------|
| SELA-Concept-* | 3 | exploration | Main concept docs |
| GOSTC-* | 3 | exploration | Related concept (OSE-to-OSTC) |
| Other | 7 | exploration | Supporting exploration |

**Status inference:** All parked (SELA not actively pursued, but valuable thinking)

**Parent/child structure:**
- SELA-Concept-Document.md is root
- Others reference it or each other

---

### Category 2: NOT DIG (Evergreen Reference) — 11 files

These are canonical reference documents, not deliberation. They describe how things work, not why decisions were made.

#### `agents/` → Keep or move to `agents/` at root (5 files)

| File | Disposition | Rationale |
|------|-------------|-----------|
| AI-Agent-Context-Delivery-Guide.md | Keep in docs/ or agents/ | Guide for writing context docs |
| AI-Agent-Task-Crafting-Guide.md | Keep in docs/ or agents/ | Guide for writing task docs |
| contextJIG-syllabus.md | Move to agents/ | Agent context document |
| O-S-Writing-Guide.md | Keep in docs/ or agents/ | Guide for writing O/S nodes |
| S008-O-S-Conformance-Audit.md | Move to dig/ as journal | Audit record (deliberation) |

**Rationale:** These are instructional/reference docs optimized for repeated use. They teach how to do things, not capture reasoning about why.

---

#### `architecture/` → Move to `jig/architecture/` (3 files)

| File | Disposition | Rationale |
|------|-------------|-----------|
| A001_Core-Artifacts-Contract.md | jig/architecture/A-001.md | Canonical architectural contract |
| A002_CLI-Command-Architecture.md | jig/architecture/A-002.md | Canonical architectural contract |
| A003_Configuration-Architecture.md | jig/architecture/A-003.md | Canonical architectural contract |

**Rationale:** Architecture documents are JIG artifacts (evergreen intent), not deliberation. They belong in `jig/architecture/` following JIG naming conventions.

---

#### `audits/` → Split (2 files)

| File | Disposition | Rationale |
|------|-------------|-----------|
| AUDIT-RESULTS-2025-12-24-1600.md | Keep in docs/audits/ or new location | Point-in-time audit results (not deliberation) |
| JOURNAL-audit-2025-12-24-1600.md | Move to dig/ as journal | Deliberation about conducting the audit |

---

#### Root file (1 file)

| File | Disposition | Rationale |
|------|-------------|-----------|
| configuration.md | Keep in docs/ | User documentation for jig.toml |

---

### Category 3: EMPTY (0 files)

#### `examples/` → Delete or repurpose

Empty directory. Can be deleted or used for example DIG documents.

---

## Type Mapping Rules

Existing suffixes map to DIG types:

| Existing Suffix | DIG Type | Mode |
|-----------------|----------|------|
| `_SCOPE_` | scope | convergent |
| `_JIGPLAN_` | jigplan | convergent |
| `_PLAN_` | plan | convergent |
| `_JOURNAL_` | journal | mixed |
| `_PROPOSAL_` | exploration | divergent |
| `_CONCEPT_` | exploration | divergent |
| `_EXPLORATION_` | exploration | divergent |
| `_AUDIT_` | journal | mixed |
| `_INTENT_EXPLAINER_` | exploration | divergent |
| (no suffix) | exploration | divergent |

---

## Status Inference Rules

| Condition | Inferred Status |
|-----------|-----------------|
| File in `done/` | implemented |
| File in `wip/` | active |
| Doc explicitly says "Supersedes: X" | The superseded doc X gets `superseded` |
| Doc says "Status: Abandoned" or similar | abandoned |
| SELA docs | parked (not pursued but valuable) |
| Early JIG concept versions (v4-v8) | superseded |

---

## Parent/Child Inference Rules

1. **Same prefix series** (B021, B022, B023, B024):
   - SCOPE is root (parent: null)
   - JIGPLAN parent: SCOPE
   - PLAN parent: JIGPLAN
   - JOURNAL parent: PLAN

2. **Explicit "Supersedes: X"**:
   - Parent: the superseded doc
   - Superseded doc gets `superseded_by: [[this doc]]`

3. **Explicit "SCOPE: X" in header**:
   - Parent: the referenced SCOPE doc

4. **Sequential numbering** (AG001, AG002, ...):
   - Earlier number is potential parent
   - Requires content analysis to confirm

5. **Version chains** (v4 → v5 → v6):
   - Earlier version is parent
   - Earlier version gets `superseded_by`

---

## Frontmatter Template

For each migrated file, add:

```yaml
---
type: <inferred from suffix>
status: <inferred from location/content>
created: <unix epoch - use git log --follow --format=%at --diff-filter=A -- filename>
created_human: "<from git log or approximate>"
parent: <inferred from rules above, or null>
children: <populated by reverse lookup, or []>
prompt: |
  <if discoverable from content, otherwise omit>
---
```

---

## Migration Summary

| Source | Destination | Files | Action |
|--------|-------------|-------|--------|
| `bricks/` | `dig/archive/bricks/` | 34 | Add frontmatter, rename to D### |
| `done/` | `dig/archive/jigy-v1/` | 33 | Add frontmatter, keep B### |
| `wip/` | `dig/wip/` | 11 | Add frontmatter, keep C### |
| `jig-concept/J###` | `dig/archive/jig-concept/` | 31 | Add frontmatter, keep J### |
| `jig-concept/SELA/` | `dig/archive/sela/` | 13 | Add frontmatter, add S### prefix |
| `agents/` (4 of 5) | Keep in `docs/` or `agents/` | 4 | No change (not DIG) |
| `agents/` (1 of 5) | `dig/` | 1 | Add frontmatter |
| `architecture/` | `jig/architecture/` | 3 | Rename to A-###.md |
| `audits/` (results) | Keep in `docs/audits/` | 1 | No change |
| `audits/` (journal) | `dig/` | 1 | Add frontmatter |
| `configuration.md` | Keep in `docs/` | 1 | No change |
| **Total** | | **133** | |

**Summary:**
- **To dig/:** 122 files (92%)
- **To jig/architecture/:** 3 files (2%)
- **Stay in docs/:** 8 files (6%)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Git history loss from moves | Use `git mv` to preserve history |
| Broken internal references | Search/replace wiki links after migration |
| Incorrect status inference | Manual review pass before finalizing |
| Missing parent relationships | Content analysis for ambiguous cases |
| Timestamp accuracy | Use git log for creation dates |

---

## Next Steps

1. **Step 2 (Manifest):** Create explicit manifest listing every file with:
   - Source path
   - Destination path
   - New filename (if renamed)
   - Complete frontmatter to inject

2. **Step 3 (Implementation):** Execute migration with:
   - Deterministic script for file moves and frontmatter injection
   - AI agent for content analysis (parent inference, status validation)
   - Validation pass with `digy validate`

---

## Open Questions

1. **Prefix scheme:** Should all DIG docs use D### prefix, or keep historical prefixes (AG, B, C, J)?
   - **Recommendation:** Keep historical prefixes for traceability. New docs use D###.

2. **Archive subfolder structure:** One flat archive/ or topic-based subfolders?
   - **Recommendation:** Topic-based (archive/bricks/, archive/jig-concept/, etc.) for navigability.

3. **What to do with docs/ after migration?**
   - **Recommendation:** Keep for non-DIG reference docs (agents/, configuration.md, audits/).

4. **Should architecture docs get DIG deliberation traces?**
   - **Recommendation:** The A-### contracts go to jig/. The deliberation that created them (AG### proposals) goes to dig/.
