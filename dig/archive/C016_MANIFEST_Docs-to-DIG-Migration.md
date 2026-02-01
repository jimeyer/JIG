---
title: "MANIFEST: Historical docs/ to dig/ Migration"
type: plan
status: implemented
decision: completed
created: 1767620000
created_human: "2026-01-04 18:00 CST"
parent: "[[C012_SCOPE_Docs-to-DIG-Migration]]"
children: []
---
# MANIFEST: Historical docs/ to dig/ Migration

**ID:** C013
**Date:** 2026-01-04
**SCOPE:** C012_SCOPE_Docs-to-DIG-Migration.md
**Status:** Draft

---

## Overview

This manifest specifies the exact transformation for each file in `docs/` to its DIG destination. Each entry includes:
- Source path
- Destination path
- DIG frontmatter to inject
- Rationale for classification

Files are grouped by disposition category.

---

## Manifest Format

```yaml
- source: "docs/path/to/file.md"
  destination: "dig/path/to/file.md"  # or "KEEP" or "jig/path"
  frontmatter:
    type: <type>
    status: <status>
    created: <epoch>
    created_human: "<datetime>"
    parent: "<wiki-link>" | null
    children: ["<wiki-link>", ...]
    superseded_by: "<wiki-link>"  # optional
    prompt: |  # optional
      <prompt text if discoverable>
  rationale: "<why this classification>"
```

---

## Category 1: TO DIG — Active Work (wip/)

### docs/wip/ → dig/wip/

```yaml
# ═══════════════════════════════════════════════════════════════════════════
# C-SERIES: Extended Intent Hierarchy work chain
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/wip/C001_PROPOSAL_JIG-Core-Artifacts-Contract.md"
  destination: "dig/wip/C001_PROPOSAL_JIG-Core-Artifacts-Contract.md"
  frontmatter:
    type: exploration
    status: active
    created: 1767412904
    created_human: "2026-01-02 22:01 CST"
    parent: null
    children: ["[[C003_SCOPE_Extended-Intent-Hierarchy-and-Towers]]"]
  rationale: "Proposal doc, root of C001-C002 thinking that led to C003 SCOPE"

- source: "docs/wip/C002_PROPOSAL_Bricks-with-Towers.md"
  destination: "dig/wip/C002_PROPOSAL_Bricks-with-Towers.md"
  frontmatter:
    type: exploration
    status: active
    created: 1767412904
    created_human: "2026-01-02 22:01 CST"
    parent: null
    children: ["[[C003_SCOPE_Extended-Intent-Hierarchy-and-Towers]]"]
  rationale: "Proposal doc, sibling to C001, both feed into C003"

- source: "docs/wip/C003_SCOPE_Extended-Intent-Hierarchy-and-Towers.md"
  destination: "dig/wip/C003_SCOPE_Extended-Intent-Hierarchy-and-Towers.md"
  frontmatter:
    type: scope
    status: active
    created: 1767412904
    created_human: "2026-01-02 22:01 CST"
    parent: "[[C001_PROPOSAL_JIG-Core-Artifacts-Contract]]"
    children: ["[[C004_JIGPLAN_Extended-Intent-Hierarchy-and-Towers]]"]
  rationale: "SCOPE document, consolidates C001+C002 proposals"

- source: "docs/wip/C004_JIGPLAN_Extended-Intent-Hierarchy-and-Towers.md"
  destination: "dig/wip/C004_JIGPLAN_Extended-Intent-Hierarchy-and-Towers.md"
  frontmatter:
    type: jigplan
    status: active
    created: 1767412904
    created_human: "2026-01-02 22:01 CST"
    parent: "[[C003_SCOPE_Extended-Intent-Hierarchy-and-Towers]]"
    children: ["[[C008_PLAN_Extended-Intent-Hierarchy-and-Towers]]"]
  rationale: "JIGPLAN follows SCOPE in chain"

- source: "docs/wip/C005_INTENT_EXPLAINER_Intent-Artifacts-Guide.md"
  destination: "dig/wip/C005_INTENT_EXPLAINER_Intent-Artifacts-Guide.md"
  frontmatter:
    type: exploration
    status: active
    created: 1767412904
    created_human: "2026-01-02 22:01 CST"
    parent: "[[C003_SCOPE_Extended-Intent-Hierarchy-and-Towers]]"
    children: []
  rationale: "Explainer doc, sibling to JIGPLAN"

- source: "docs/wip/C006_PROPOSAL_JIG_Tools_Skills_Architecture.md"
  destination: "dig/wip/C006_PROPOSAL_JIG_Tools_Skills_Architecture.md"
  frontmatter:
    type: exploration
    status: active
    created: 1767479764
    created_human: "2026-01-03 16:36 CST"
    parent: null
    children: []
  rationale: "Standalone proposal, not part of C003 chain"

- source: "docs/wip/C007_PROPOSAL_Gitignore_Generated_Graphs.md"
  destination: "dig/wip/C007_PROPOSAL_Gitignore_Generated_Graphs.md"
  frontmatter:
    type: exploration
    status: active
    created: 1767479764
    created_human: "2026-01-03 16:36 CST"
    parent: null
    children: []
  rationale: "Standalone proposal"

- source: "docs/wip/C008_PLAN_Extended-Intent-Hierarchy-and-Towers.md"
  destination: "dig/wip/C008_PLAN_Extended-Intent-Hierarchy-and-Towers.md"
  frontmatter:
    type: plan
    status: active
    created: 1767537749
    created_human: "2026-01-04 08:42 CST"
    parent: "[[C004_JIGPLAN_Extended-Intent-Hierarchy-and-Towers]]"
    children: ["[[C009_JOURNAL-Extended-Intent-Hierarchy-and-Towers]]"]
  rationale: "PLAN follows JIGPLAN in chain"

- source: "docs/wip/C009_JOURNAL-Extended-Intent-Hierarchy-and-Towers.md"
  destination: "dig/wip/C009_JOURNAL_Extended-Intent-Hierarchy-and-Towers.md"
  frontmatter:
    type: journal
    status: active
    created: 1767537965
    created_human: "2026-01-04 08:46 CST"
    parent: "[[C008_PLAN_Extended-Intent-Hierarchy-and-Towers]]"
    children: []
  rationale: "JOURNAL follows PLAN in chain (rename: hyphen to underscore)"

# ═══════════════════════════════════════════════════════════════════════════
# C010-C011: Standardized Naming work chain
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/wip/C010_SCOPE_Standardized-Intent-Document-Naming.md"
  destination: "dig/wip/C010_SCOPE_Standardized-Intent-Document-Naming.md"
  frontmatter:
    type: scope
    status: active
    created: 1767550000
    created_human: "2026-01-04 12:00 CST"
    parent: null
    children: ["[[C011_JIGPLAN_Standardized-Intent-Document-Naming]]"]
  rationale: "SCOPE for new work chain"

- source: "docs/wip/C011_JIGPLAN_Standardized-Intent-Document-Naming.md"
  destination: "dig/wip/C011_JIGPLAN_Standardized-Intent-Document-Naming.md"
  frontmatter:
    type: jigplan
    status: active
    created: 1767550000
    created_human: "2026-01-04 12:00 CST"
    parent: "[[C010_SCOPE_Standardized-Intent-Document-Naming]]"
    children: []
  rationale: "JIGPLAN follows SCOPE"

# ═══════════════════════════════════════════════════════════════════════════
# C012: This migration scope (meta!)
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/wip/C012_SCOPE_Docs-to-DIG-Migration.md"
  destination: "dig/wip/C012_SCOPE_Docs-to-DIG-Migration.md"
  frontmatter:
    type: scope
    status: active
    created: 1767600000
    created_human: "2026-01-04 15:00 CST"
    parent: null
    children: ["[[C013_MANIFEST_Docs-to-DIG-Migration]]"]
  rationale: "SCOPE for this migration work"
```

---

## Category 2: TO DIG — Completed Work (done/)

### docs/done/ → dig/archive/jigy-v1/

```yaml
# ═══════════════════════════════════════════════════════════════════════════
# B001: Implementation Graph Discovery
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B001_PLAN_Implementation_Graph_Discovery.md"
  destination: "dig/archive/jigy-v1/B001_PLAN_Implementation_Graph_Discovery.md"
  frontmatter:
    type: plan
    status: implemented
    created: 1764187522
    created_human: "2025-11-26 14:05 CST"
    parent: "[[AG022_PROPOSAL_Implementation-Graph-Discovery-Tool]]"
    children: []
  rationale: "PLAN that implemented AG022 proposal"

# ═══════════════════════════════════════════════════════════════════════════
# B002: Brick Partition
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B002_PROPOSAL-Brick-Partition.md"
  destination: "dig/archive/jigy-v1/B002_PROPOSAL_Brick-Partition.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764520553
    created_human: "2025-11-30 10:35 CST"
    parent: "[[AG020_Bricks-as-Partitions]]"
    children: []
  rationale: "Proposal implemented, evolved from AG020"

# ═══════════════════════════════════════════════════════════════════════════
# B003: Linter for Artifact Validation
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B003_PLAN_Linter-for-Artifact-Validation.md"
  destination: "dig/archive/jigy-v1/B003_PLAN_Linter-for-Artifact-Validation.md"
  frontmatter:
    type: plan
    status: implemented
    created: 1764540321
    created_human: "2025-11-30 16:05 CST"
    parent: "[[AG026_PROPOSAL_Linter-for-Artifact-Validation]]"
    children: []
  rationale: "PLAN that implemented AG026 proposal"

# ═══════════════════════════════════════════════════════════════════════════
# B004: Layer Validation and CLI
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B004_PLAN_Layer-Validation-and-CLI.md"
  destination: "dig/archive/jigy-v1/B004_PLAN_Layer-Validation-and-CLI.md"
  frontmatter:
    type: plan
    status: implemented
    created: 1764644099
    created_human: "2025-12-01 20:54 CST"
    parent: "[[AG029_PROPOSAL_Brick-Layers]]"
    children: []
  rationale: "PLAN that implemented AG029 proposal"

# ═══════════════════════════════════════════════════════════════════════════
# B005: Orphaned Intent Validation
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B005_PLAN_Orphaned-Intent-Validation.md"
  destination: "dig/archive/jigy-v1/B005_PLAN_Orphaned-Intent-Validation.md"
  frontmatter:
    type: plan
    status: implemented
    created: 1764679568
    created_human: "2025-12-02 06:46 CST"
    parent: null
    children: []
  rationale: "Standalone PLAN"

# ═══════════════════════════════════════════════════════════════════════════
# B006-B007: Standalone features
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B006-intent-summary-report.md"
  destination: "dig/archive/jigy-v1/B006_intent-summary-report.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764735485
    created_human: "2025-12-02 22:18 CST"
    parent: null
    children: []
  rationale: "Feature exploration"

- source: "docs/done/B007-rebuild-command.md"
  destination: "dig/archive/jigy-v1/B007_rebuild-command.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764772645
    created_human: "2025-12-03 08:37 CST"
    parent: null
    children: []
  rationale: "Feature exploration"

# ═══════════════════════════════════════════════════════════════════════════
# B008: Content Hashing
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B008_PLAN_Content-Hashing.md"
  destination: "dig/archive/jigy-v1/B008_PLAN_Content-Hashing.md"
  frontmatter:
    type: plan
    status: implemented
    created: 1765242592
    created_human: "2025-12-08 19:09 CST"
    parent: "[[J022_Content-Hashing]]"
    children: []
  rationale: "PLAN that implemented J022 concept"

# ═══════════════════════════════════════════════════════════════════════════
# B010-B011: Verification Graph chain
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B010_SCOPE_Verification-Graph.md"
  destination: "dig/archive/jigy-v1/B010_SCOPE_Verification-Graph.md"
  frontmatter:
    type: scope
    status: implemented
    created: 1765249815
    created_human: "2025-12-08 21:10 CST"
    parent: "[[AG016_Verification-Graph-Feasibility]]"
    children: ["[[B011_PLAN_Verification-Graph]]"]
  rationale: "SCOPE for verification graph work"

- source: "docs/done/B010_code_reuse.md"
  destination: "dig/archive/jigy-v1/B010_code_reuse.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765249815
    created_human: "2025-12-08 21:10 CST"
    parent: "[[B010_SCOPE_Verification-Graph]]"
    children: []
  rationale: "Supporting exploration for B010"

- source: "docs/done/B011_PLAN_Verification-Graph.md"
  destination: "dig/archive/jigy-v1/B011_PLAN_Verification-Graph.md"
  frontmatter:
    type: plan
    status: implemented
    created: 1765249815
    created_human: "2025-12-08 21:10 CST"
    parent: "[[B010_SCOPE_Verification-Graph]]"
    children: []
  rationale: "PLAN follows SCOPE"

# ═══════════════════════════════════════════════════════════════════════════
# B012-B013: CLI Command Restructure chain
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B012_PROPOSAL_CLI-Command-Simplification.md"
  destination: "dig/archive/jigy-v1/B012_PROPOSAL_CLI-Command-Simplification.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765288592
    created_human: "2025-12-09 07:56 CST"
    parent: null
    children: ["[[B013_PLAN_CLI-Command-Restructure]]"]
  rationale: "Proposal that led to B013 PLAN"

- source: "docs/done/B013_PLAN_CLI-Command-Restructure.md"
  destination: "dig/archive/jigy-v1/B013_PLAN_CLI-Command-Restructure.md"
  frontmatter:
    type: plan
    status: implemented
    created: 1765336342
    created_human: "2025-12-09 21:12 CST"
    parent: "[[B012_PROPOSAL_CLI-Command-Simplification]]"
    children: []
  rationale: "PLAN implements proposal"

# ═══════════════════════════════════════════════════════════════════════════
# B014: Test Directory Issue
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B014_jigy-test-directory-issue.md"
  destination: "dig/archive/jigy-v1/B014_jigy-test-directory-issue.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765408051
    created_human: "2025-12-10 17:07 CST"
    parent: null
    children: []
  rationale: "Bug investigation/fix"

# ═══════════════════════════════════════════════════════════════════════════
# B015-B016: Configuration File chain
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B015_PROPOSAL_JIG-Configuration-File.md"
  destination: "dig/archive/jigy-v1/B015_PROPOSAL_JIG-Configuration-File.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765378531
    created_human: "2025-12-10 08:55 CST"
    parent: null
    children: ["[[B016_PLAN_JIG-Configuration-MVP]]"]
  rationale: "Proposal for jig.toml"

- source: "docs/done/B016_PLAN_JIG-Configuration-MVP.md"
  destination: "dig/archive/jigy-v1/B016_PLAN_JIG-Configuration-MVP.md"
  frontmatter:
    type: plan
    status: implemented
    created: 1765378531
    created_human: "2025-12-10 08:55 CST"
    parent: "[[B015_PROPOSAL_JIG-Configuration-File]]"
    children: []
  rationale: "PLAN implements proposal"

# ═══════════════════════════════════════════════════════════════════════════
# B018: Class vs Function Decorators
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B018_class-vs-function-decorators.md"
  destination: "dig/archive/jigy-v1/B018_class-vs-function-decorators.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765408051
    created_human: "2025-12-10 17:07 CST"
    parent: null
    children: []
  rationale: "Design exploration"

# ═══════════════════════════════════════════════════════════════════════════
# B019-B020: Coverage Audit Record chain
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B019_SCOPE_Coverage-Audit-Record.md"
  destination: "dig/archive/jigy-v1/B019_SCOPE_Coverage-Audit-Record.md"
  frontmatter:
    type: scope
    status: implemented
    created: 1765921953
    created_human: "2025-12-16 15:52 CST"
    parent: null
    children: ["[[B020_PLAN_Coverage-Audit-Record]]"]
  rationale: "SCOPE for audit record feature"

- source: "docs/done/B019_AUDIT_outcomes-2025-12-13.md"
  destination: "dig/archive/jigy-v1/B019_AUDIT_outcomes-2025-12-13.md"
  frontmatter:
    type: journal
    status: implemented
    created: 1765657742
    created_human: "2025-12-13 14:29 CST"
    parent: "[[B019_SCOPE_Coverage-Audit-Record]]"
    children: []
  rationale: "Audit journal, part of B019 work"

- source: "docs/done/B019_agent-prompt-outcome-audit.md"
  destination: "dig/archive/jigy-v1/B019_agent-prompt-outcome-audit.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765657742
    created_human: "2025-12-13 14:29 CST"
    parent: "[[B019_SCOPE_Coverage-Audit-Record]]"
    children: []
  rationale: "Agent prompt exploration, part of B019"

- source: "docs/done/B020_PLAN_Coverage-Audit-Record.md"
  destination: "dig/archive/jigy-v1/B020_PLAN_Coverage-Audit-Record.md"
  frontmatter:
    type: plan
    status: implemented
    created: 1765921953
    created_human: "2025-12-16 15:52 CST"
    parent: "[[B019_SCOPE_Coverage-Audit-Record]]"
    children: []
  rationale: "PLAN follows SCOPE"

# ═══════════════════════════════════════════════════════════════════════════
# B021-B024: Auto-Rebuild Staleness chain (complete SCOPE→JIGPLAN→PLAN→JOURNAL)
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B021_SCOPE_Auto-Rebuild-Staleness.md"
  destination: "dig/archive/jigy-v1/B021_SCOPE_Auto-Rebuild-Staleness.md"
  frontmatter:
    type: scope
    status: implemented
    created: 1766013205
    created_human: "2025-12-17 17:13 CST"
    parent: null
    children: ["[[B022_JIGPLAN_Auto-Rebuild-Staleness]]"]
  rationale: "SCOPE root of B021-B024 chain"

- source: "docs/done/B022_JIGPLAN_Auto-Rebuild-Staleness.md"
  destination: "dig/archive/jigy-v1/B022_JIGPLAN_Auto-Rebuild-Staleness.md"
  frontmatter:
    type: jigplan
    status: implemented
    created: 1766428369
    created_human: "2025-12-22 11:32 CST"
    parent: "[[B021_SCOPE_Auto-Rebuild-Staleness]]"
    children: ["[[B023_PLAN_Auto-Rebuild-Staleness]]"]
  rationale: "JIGPLAN follows SCOPE"

- source: "docs/done/B023_PLAN_Auto-Rebuild-Staleness.md"
  destination: "dig/archive/jigy-v1/B023_PLAN_Auto-Rebuild-Staleness.md"
  frontmatter:
    type: plan
    status: implemented
    created: 1766428369
    created_human: "2025-12-22 11:32 CST"
    parent: "[[B022_JIGPLAN_Auto-Rebuild-Staleness]]"
    children: ["[[B024_JOURNAL_Auto-Rebuild-Staleness]]"]
  rationale: "PLAN follows JIGPLAN"

- source: "docs/done/B024_JOURNAL_Auto-Rebuild-Staleness.md"
  destination: "dig/archive/jigy-v1/B024_JOURNAL_Auto-Rebuild-Staleness.md"
  frontmatter:
    type: journal
    status: implemented
    created: 1766428369
    created_human: "2025-12-22 11:32 CST"
    parent: "[[B023_PLAN_Auto-Rebuild-Staleness]]"
    children: []
  rationale: "JOURNAL follows PLAN"

# ═══════════════════════════════════════════════════════════════════════════
# B025-B026: Intent Document Format
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B025_Intent-Document-Format.md"
  destination: "dig/archive/jigy-v1/B025_Intent-Document-Format.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1766525018
    created_human: "2025-12-23 14:23 MST"
    parent: null
    children: []
  rationale: "Format exploration"

- source: "docs/done/B025_Outcome-Format-Specification.md"
  destination: "dig/archive/jigy-v1/B025_Outcome-Format-Specification.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1766525018
    created_human: "2025-12-23 14:23 MST"
    parent: null
    children: []
  rationale: "Format exploration, sibling to B025_Intent"

- source: "docs/done/B026_AUDIT_Intent-Document-Titles.md"
  destination: "dig/archive/jigy-v1/B026_AUDIT_Intent-Document-Titles.md"
  frontmatter:
    type: journal
    status: implemented
    created: 1766525018
    created_human: "2025-12-23 14:23 MST"
    parent: null
    children: []
  rationale: "Audit journal"

# ═══════════════════════════════════════════════════════════════════════════
# B027-B029: Outcome Updates chain
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/B027_SCOPE_outcome-updates.md"
  destination: "dig/archive/jigy-v1/B027_SCOPE_outcome-updates.md"
  frontmatter:
    type: scope
    status: implemented
    created: 1767052325
    created_human: "2025-12-29 16:52 MST"
    parent: null
    children: ["[[B028_JIGPLAN_outcome-updates]]"]
  rationale: "SCOPE for outcome updates"

- source: "docs/done/B028_JIGPLAN_outcome-updates.md"
  destination: "dig/archive/jigy-v1/B028_JIGPLAN_outcome-updates.md"
  frontmatter:
    type: jigplan
    status: implemented
    created: 1767052325
    created_human: "2025-12-29 16:52 MST"
    parent: "[[B027_SCOPE_outcome-updates]]"
    children: ["[[B029_PLAN_outcome-updates]]"]
  rationale: "JIGPLAN follows SCOPE"

- source: "docs/done/B029_PLAN_outcome-updates.md"
  destination: "dig/archive/jigy-v1/B029_PLAN_outcome-updates.md"
  frontmatter:
    type: plan
    status: implemented
    created: 1767052325
    created_human: "2025-12-29 16:52 MST"
    parent: "[[B028_JIGPLAN_outcome-updates]]"
    children: ["[[B029_JOURNAL_outcome-updates]]"]
  rationale: "PLAN follows JIGPLAN"

- source: "docs/done/B029_JOURNAL_outcome-updates.md"
  destination: "dig/archive/jigy-v1/B029_JOURNAL_outcome-updates.md"
  frontmatter:
    type: journal
    status: implemented
    created: 1767052325
    created_human: "2025-12-29 16:52 MST"
    parent: "[[B029_PLAN_outcome-updates]]"
    children: []
  rationale: "JOURNAL follows PLAN"

# ═══════════════════════════════════════════════════════════════════════════
# AGX030: Jig-agx proposal (moved from AG series)
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/done/AGX030_PROPOSAL_Jig-agx.md"
  destination: "dig/archive/jigy-v1/AGX030_PROPOSAL_Jig-agx.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1766431994
    created_human: "2025-12-22 12:33 MST"
    parent: null
    children: []
  rationale: "Standalone proposal"
```

---

## Category 3: TO DIG — Bricks Concept Evolution

### docs/bricks/ → dig/archive/bricks/

```yaml
# ═══════════════════════════════════════════════════════════════════════════
# AG001-AG029: Evolution of Alignment Graph and Bricks concepts
# These form a conceptual evolution chain, not strict parent-child
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/bricks/AG001_Alignment-Graph-Bricks.md"
  destination: "dig/archive/bricks/AG001_Alignment-Graph-Bricks.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763934216
    created_human: "2025-11-23 15:43 CST"
    parent: null
    children: ["[[AG002_Alignment_Graph_Whitepaper]]", "[[AG002_Understanding_Alignment_and_Bricks]]"]
  rationale: "Root document for Alignment Graph concept"

- source: "docs/bricks/AG002_Alignment_Graph_Whitepaper.md"
  destination: "dig/archive/bricks/AG002_Alignment_Graph_Whitepaper.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764019099
    created_human: "2025-11-24 15:18 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Whitepaper expanding on AG001"

- source: "docs/bricks/AG002_Understanding_Alignment_and_Bricks.md"
  destination: "dig/archive/bricks/AG002_Understanding_Alignment_and_Bricks.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763934216
    created_human: "2025-11-23 15:43 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Understanding doc, sibling to whitepaper"

- source: "docs/bricks/AG003_Brick-Analysis-JIG-System.md"
  destination: "dig/archive/bricks/AG003_Brick-Analysis-JIG-System.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763934216
    created_human: "2025-11-23 15:43 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Analysis doc"

- source: "docs/bricks/AG003_Brick-Summary.md"
  destination: "dig/archive/bricks/AG003_Brick-Summary.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763934216
    created_human: "2025-11-23 15:43 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Summary doc"

- source: "docs/bricks/AG005_Shared-Artifacts-And-Bricks.md"
  destination: "dig/archive/bricks/AG005_Shared-Artifacts-And-Bricks.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763934216
    created_human: "2025-11-23 15:43 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Shared artifacts exploration"

- source: "docs/bricks/AG006_Brick-Context-Enforcement-Proposal.md"
  destination: "dig/archive/bricks/AG006_Brick-Context-Enforcement-Proposal.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763934216
    created_human: "2025-11-23 15:43 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: ["[[AG006_Enforcement-Quick-Reference]]"]
  rationale: "Enforcement proposal"

- source: "docs/bricks/AG006_Enforcement-Quick-Reference.md"
  destination: "dig/archive/bricks/AG006_Enforcement-Quick-Reference.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763934216
    created_human: "2025-11-23 15:43 CST"
    parent: "[[AG006_Brick-Context-Enforcement-Proposal]]"
    children: []
  rationale: "Quick reference for AG006"

- source: "docs/bricks/AG007_Clean-Breaks-And-Cross-Brick-Refactoring.md"
  destination: "dig/archive/bricks/AG007_Clean-Breaks-And-Cross-Brick-Refactoring.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763934216
    created_human: "2025-11-23 15:43 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: ["[[AG007_Clean-Breaks-Quick-Reference]]"]
  rationale: "Refactoring exploration"

- source: "docs/bricks/AG007_Clean-Breaks-Quick-Reference.md"
  destination: "dig/archive/bricks/AG007_Clean-Breaks-Quick-Reference.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763934216
    created_human: "2025-11-23 15:43 CST"
    parent: "[[AG007_Clean-Breaks-And-Cross-Brick-Refactoring]]"
    children: []
  rationale: "Quick reference for AG007"

- source: "docs/bricks/AG008_Brick-First-File-Organization.md"
  destination: "dig/archive/bricks/AG008_Brick-First-File-Organization.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763956181
    created_human: "2025-11-23 21:49 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "File organization exploration"

- source: "docs/bricks/AG009_Context-Fencing-Across-Ecosystems.md"
  destination: "dig/archive/bricks/AG009_Context-Fencing-Across-Ecosystems.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764019099
    created_human: "2025-11-24 15:18 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Context fencing exploration"

- source: "docs/bricks/AG010_Brick-Discovery-Workflow.md"
  destination: "dig/archive/bricks/AG010_Brick-Discovery-Workflow.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764019099
    created_human: "2025-11-24 15:18 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Discovery workflow exploration"

- source: "docs/bricks/AG011_Brick-Analysis-ASE.md"
  destination: "dig/archive/bricks/AG011_Brick-Analysis-ASE.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764019099
    created_human: "2025-11-24 15:18 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "ASE-specific analysis"

- source: "docs/bricks/AG011_Brick-Workflow-Bootstrap.md"
  destination: "dig/archive/bricks/AG011_Brick-Workflow-Bootstrap.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764019099
    created_human: "2025-11-24 15:18 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Bootstrap workflow"

- source: "docs/bricks/AG012_Intent-Discovery-Workflow.md"
  destination: "dig/archive/bricks/AG012_Intent-Discovery-Workflow.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764019099
    created_human: "2025-11-24 15:18 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Intent discovery exploration"

- source: "docs/bricks/AG013_JIG-Evolution-Proposal-Bricks.md"
  destination: "dig/archive/bricks/AG013_JIG-Evolution-Proposal-Bricks.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764174215
    created_human: "2025-11-26 10:23 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "JIG evolution proposal"

- source: "docs/bricks/AG014_Implementation-Verification-Graphs.md"
  destination: "dig/archive/bricks/AG014_Implementation-Verification-Graphs.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764174215
    created_human: "2025-11-26 10:23 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: ["[[AG015_Implementation-Graph-Feasibility]]", "[[AG016_Verification-Graph-Feasibility]]"]
  rationale: "Graph exploration parent"

- source: "docs/bricks/AG015_Implementation-Graph-Feasibility.md"
  destination: "dig/archive/bricks/AG015_Implementation-Graph-Feasibility.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764174215
    created_human: "2025-11-26 10:23 CST"
    parent: "[[AG014_Implementation-Verification-Graphs]]"
    children: []
  rationale: "Implementation graph feasibility"

- source: "docs/bricks/AG016_Verification-Graph-Feasibility.md"
  destination: "dig/archive/bricks/AG016_Verification-Graph-Feasibility.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764174215
    created_human: "2025-11-26 10:23 CST"
    parent: "[[AG014_Implementation-Verification-Graphs]]"
    children: []
  rationale: "Verification graph feasibility"

- source: "docs/bricks/AG017_Minimal-Graph-Schema.md"
  destination: "dig/archive/bricks/AG017_Minimal-Graph-Schema.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764174215
    created_human: "2025-11-26 10:23 CST"
    parent: "[[AG014_Implementation-Verification-Graphs]]"
    children: []
  rationale: "Schema exploration"

- source: "docs/bricks/AG018_Graph-Storage-Strategy.md"
  destination: "dig/archive/bricks/AG018_Graph-Storage-Strategy.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764174215
    created_human: "2025-11-26 10:23 CST"
    parent: "[[AG014_Implementation-Verification-Graphs]]"
    children: []
  rationale: "Storage strategy"

- source: "docs/bricks/AG019_Irreducible-Core.md"
  destination: "dig/archive/bricks/AG019_Irreducible-Core.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764174215
    created_human: "2025-11-26 10:23 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Core concept crystallization"

- source: "docs/bricks/AG020_Bricks-as-Partitions.md"
  destination: "dig/archive/bricks/AG020_Bricks-as-Partitions.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764174215
    created_human: "2025-11-26 10:23 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Partition concept"

- source: "docs/bricks/AG021_Spec-Stable-Reference.md"
  destination: "dig/archive/bricks/AG021_Spec-Stable-Reference.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764174215
    created_human: "2025-11-26 10:23 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Stable reference exploration"

- source: "docs/bricks/AG022_PROPOSAL_Implementation-Graph-Discovery-Tool.md"
  destination: "dig/archive/bricks/AG022_PROPOSAL_Implementation-Graph-Discovery-Tool.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764174215
    created_human: "2025-11-26 10:23 CST"
    parent: "[[AG015_Implementation-Graph-Feasibility]]"
    children: ["[[B001_PLAN_Implementation_Graph_Discovery]]"]
  rationale: "Proposal that became B001"

- source: "docs/bricks/AG023_PROPOSAL_Core-Artifacts-Contract.md"
  destination: "dig/archive/bricks/AG023_PROPOSAL_Core-Artifacts-Contract.md"
  frontmatter:
    type: exploration
    status: superseded
    created: 1764187522
    created_human: "2025-11-26 14:05 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: ["[[AG024_REFINED_Core-Artifacts-Contract]]"]
    superseded_by: "[[AG024_REFINED_Core-Artifacts-Contract]]"
  rationale: "Initial proposal, superseded by refined version"

- source: "docs/bricks/AG024_REFINED_Core-Artifacts-Contract.md"
  destination: "dig/archive/bricks/AG024_REFINED_Core-Artifacts-Contract.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764187522
    created_human: "2025-11-26 14:05 CST"
    parent: "[[AG023_PROPOSAL_Core-Artifacts-Contract]]"
    children: []
  rationale: "Refined version that became A001"

- source: "docs/bricks/AG025_Brick-Scoped-Plans-Practical-Approach.md"
  destination: "dig/archive/bricks/AG025_Brick-Scoped-Plans-Practical-Approach.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764195163
    created_human: "2025-11-26 16:12 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Practical approach exploration"

- source: "docs/bricks/AG026_PROPOSAL_Linter-for-Artifact-Validation.md"
  destination: "dig/archive/bricks/AG026_PROPOSAL_Linter-for-Artifact-Validation.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764195163
    created_human: "2025-11-26 16:12 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: ["[[B003_PLAN_Linter-for-Artifact-Validation]]"]
  rationale: "Proposal that became B003"

- source: "docs/bricks/AG027-Community-Detection-Algorithms.md"
  destination: "dig/archive/bricks/AG027_Community-Detection-Algorithms.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764518198
    created_human: "2025-11-30 09:56 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: []
  rationale: "Algorithm exploration"

- source: "docs/bricks/AG028_PROPOSAL-Brick-Detection-Workflow.md"
  destination: "dig/archive/bricks/AG028_PROPOSAL_Brick-Detection-Workflow.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764520553
    created_human: "2025-11-30 10:35 CST"
    parent: "[[AG027_Community-Detection-Algorithms]]"
    children: []
  rationale: "Detection workflow proposal"

- source: "docs/bricks/AG029_PROPOSAL_Brick-Layers.md"
  destination: "dig/archive/bricks/AG029_PROPOSAL_Brick-Layers.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764648793
    created_human: "2025-12-01 22:13 CST"
    parent: "[[AG001_Alignment-Graph-Bricks]]"
    children: ["[[B004_PLAN_Layer-Validation-and-CLI]]"]
  rationale: "Layers proposal that became B004"

- source: "docs/bricks/README.md"
  destination: "dig/archive/bricks/README.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763934216
    created_human: "2025-11-23 15:43 CST"
    parent: null
    children: ["[[AG001_Alignment-Graph-Bricks]]"]
  rationale: "Index doc for bricks folder"
```

---

## Category 4: TO DIG — JIG Concept Evolution

### docs/jig-concept/ → dig/archive/jig-concept/

```yaml
# ═══════════════════════════════════════════════════════════════════════════
# JIG Concept Version Chain (v4 → v5 → v6 → v6.1 → v7 → v8 → v9 → v10)
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/jig-concept/J001-JIG-Concept-v4.md"
  destination: "dig/archive/jig-concept/J001_JIG-Concept-v4.md"
  frontmatter:
    type: exploration
    status: superseded
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: null
    children: ["[[J006_JIG-Concept-v5]]"]
    superseded_by: "[[J006_JIG-Concept-v5]]"
  rationale: "Initial JIG concept, superseded by v5"

- source: "docs/jig-concept/J002-JIG-Annotation-Based-Docs-Proposal.md"
  destination: "dig/archive/jig-concept/J002_JIG-Annotation-Based-Docs-Proposal.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[J001_JIG-Concept-v4]]"
    children: []
  rationale: "Annotation proposal"

- source: "docs/jig-concept/J003-JIG-Annotation-Syntax-Options.md"
  destination: "dig/archive/jig-concept/J003_JIG-Annotation-Syntax-Options.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[J001_JIG-Concept-v4]]"
    children: []
  rationale: "Syntax options exploration"

- source: "docs/jig-concept/J004-JIG-Link-Reference-Scoping.md"
  destination: "dig/archive/jig-concept/J004_JIG-Link-Reference-Scoping.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[J001_JIG-Concept-v4]]"
    children: []
  rationale: "Link scoping exploration"

- source: "docs/jig-concept/J005-JIG_DECOMPOSITION_STRATEGY.md"
  destination: "dig/archive/jig-concept/J005_JIG_DECOMPOSITION_STRATEGY.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[J001_JIG-Concept-v4]]"
    children: []
  rationale: "Decomposition strategy"

- source: "docs/jig-concept/J006-JIG-Concept-v5.md"
  destination: "dig/archive/jig-concept/J006_JIG-Concept-v5.md"
  frontmatter:
    type: exploration
    status: superseded
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[J001_JIG-Concept-v4]]"
    children: ["[[J010_JIG-Concept-v6]]"]
    superseded_by: "[[J010_JIG-Concept-v6]]"
  rationale: "v5, superseded by v6"

- source: "docs/jig-concept/J007-PROPOSAL_Subsystem_Test_Execution.md"
  destination: "dig/archive/jig-concept/J007_PROPOSAL_Subsystem_Test_Execution.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[J001_JIG-Concept-v4]]"
    children: []
  rationale: "Test execution proposal"

- source: "docs/jig-concept/J008-PROPOSAL_Delta_Harvest_and_Distillation.md"
  destination: "dig/archive/jig-concept/J008_PROPOSAL_Delta_Harvest_and_Distillation.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[J001_JIG-Concept-v4]]"
    children: []
  rationale: "Delta harvest proposal"

- source: "docs/jig-concept/J009-PROPOSAL_Working_Docs_and_Intent_Lifecycle.md"
  destination: "dig/archive/jig-concept/J009_PROPOSAL_Working_Docs_and_Intent_Lifecycle.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[J001_JIG-Concept-v4]]"
    children: []
  rationale: "Lifecycle proposal"

- source: "docs/jig-concept/J010-JIG-Concept-v6.md"
  destination: "dig/archive/jig-concept/J010_JIG-Concept-v6.md"
  frontmatter:
    type: exploration
    status: superseded
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[J006_JIG-Concept-v5]]"
    children: ["[[J011_JIG-Concept-v6.1]]"]
    superseded_by: "[[J011_JIG-Concept-v6.1]]"
  rationale: "v6, superseded by v6.1"

- source: "docs/jig-concept/J011-JIG-Concept-v6.1.md"
  destination: "dig/archive/jig-concept/J011_JIG-Concept-v6.1.md"
  frontmatter:
    type: exploration
    status: superseded
    created: 1763501375
    created_human: "2025-11-18 15:29 CST"
    parent: "[[J010_JIG-Concept-v6]]"
    children: ["[[J013_JIG-Concept-v7]]"]
    superseded_by: "[[J013_JIG-Concept-v7]]"
  rationale: "v6.1, superseded by v7"

- source: "docs/jig-concept/J012-JIG-Constraints.md"
  destination: "dig/archive/jig-concept/J012_JIG-Constraints.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763668191
    created_human: "2025-11-20 13:49 CST"
    parent: "[[J011_JIG-Concept-v6.1]]"
    children: []
  rationale: "Constraints exploration"

- source: "docs/jig-concept/J013-JIG-Concept-v7.md"
  destination: "dig/archive/jig-concept/J013_JIG-Concept-v7.md"
  frontmatter:
    type: exploration
    status: superseded
    created: 1763668191
    created_human: "2025-11-20 13:49 CST"
    parent: "[[J011_JIG-Concept-v6.1]]"
    children: ["[[J016_JIG-Concept-v8]]"]
    superseded_by: "[[J016_JIG-Concept-v8]]"
  rationale: "v7, superseded by v8"

- source: "docs/jig-concept/J014-EXPLORATION_Non-Deterministic-Components.md"
  destination: "dig/archive/jig-concept/J014_EXPLORATION_Non-Deterministic-Components.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763733275
    created_human: "2025-11-21 07:54 CST"
    parent: "[[J013_JIG-Concept-v7]]"
    children: []
  rationale: "Non-determinism exploration"

- source: "docs/jig-concept/J015-PROPOSAL_JIG_Bricks_Integration.md"
  destination: "dig/archive/jig-concept/J015_PROPOSAL_JIG_Bricks_Integration.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764025026
    created_human: "2025-11-24 16:57 CST"
    parent: "[[J013_JIG-Concept-v7]]"
    children: []
  rationale: "Bricks integration proposal"

- source: "docs/jig-concept/J016_JIG-Concept-v8.md"
  destination: "dig/archive/jig-concept/J016_JIG-Concept-v8.md"
  frontmatter:
    type: exploration
    status: superseded
    created: 1764187522
    created_human: "2025-11-26 14:05 CST"
    parent: "[[J013_JIG-Concept-v7]]"
    children: ["[[J017_JIG-Concept-v9]]"]
    superseded_by: "[[J017_JIG-Concept-v9]]"
  rationale: "v8, superseded by v9"

- source: "docs/jig-concept/J017_JIG-Concept-v9.md"
  destination: "dig/archive/jig-concept/J017_JIG-Concept-v9.md"
  frontmatter:
    type: exploration
    status: superseded
    created: 1764685823
    created_human: "2025-12-02 08:30 CST"
    parent: "[[J016_JIG-Concept-v8]]"
    children: ["[[J029_JIG-Manifesto-v10]]"]
    superseded_by: "[[J029_JIG-Manifesto-v10]]"
  rationale: "v9, superseded by v10"

- source: "docs/jig-concept/J018_JIG-When-In-Rome-Whitepaper.md"
  destination: "dig/archive/jig-concept/J018_JIG-When-In-Rome-Whitepaper.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764855299
    created_human: "2025-12-04 07:34 CST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: []
  rationale: "When-In-Rome whitepaper"

- source: "docs/jig-concept/J019_JIG-Native-Bricks-Whitepaper.md"
  destination: "dig/archive/jig-concept/J019_JIG-Native-Bricks-Whitepaper.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764980842
    created_human: "2025-12-05 18:27 CST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: []
  rationale: "Native Bricks whitepaper"

- source: "docs/jig-concept/J020_JIG-Architectural-Intent-Manifesto.md"
  destination: "dig/archive/jig-concept/J020_JIG-Architectural-Intent-Manifesto.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764980842
    created_human: "2025-12-05 18:27 CST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: []
  rationale: "Manifesto doc"

- source: "docs/jig-concept/J021_JIG-Rust-Zephyr-strategy-concept.md"
  destination: "dig/archive/jig-concept/J021_JIG-Rust-Zephyr-strategy-concept.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765113139
    created_human: "2025-12-07 07:12 CST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: []
  rationale: "Rust/Zephyr strategy"

- source: "docs/jig-concept/J022_Content-Hashing.md"
  destination: "dig/archive/jig-concept/J022_Content-Hashing.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765161786
    created_human: "2025-12-07 20:43 CST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: ["[[B008_PLAN_Content-Hashing]]"]
  rationale: "Content hashing concept, led to B008"

- source: "docs/jig-concept/J023_Audit-Records-and-Triggers.md"
  destination: "dig/archive/jig-concept/J023_Audit-Records-and-Triggers.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765161786
    created_human: "2025-12-07 20:43 CST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: []
  rationale: "Audit records concept"

- source: "docs/jig-concept/J024_Audit-Report-Format.md"
  destination: "dig/archive/jig-concept/J024_Audit-Report-Format.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765161786
    created_human: "2025-12-07 20:43 CST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: []
  rationale: "Audit format concept"

- source: "docs/jig-concept/J025_Audit-Agents.md"
  destination: "dig/archive/jig-concept/J025_Audit-Agents.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765113139
    created_human: "2025-12-07 07:12 CST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: []
  rationale: "Audit agents concept"

- source: "docs/jig-concept/J026_Audit-Architecture-Simplification.md"
  destination: "dig/archive/jig-concept/J026_Audit-Architecture-Simplification.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765161786
    created_human: "2025-12-07 20:43 CST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: []
  rationale: "Audit simplification"

- source: "docs/jig-concept/J027_Traceability-Matrix-Pattern.md"
  destination: "dig/archive/jig-concept/J027_Traceability-Matrix-Pattern.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765341219
    created_human: "2025-12-09 22:33 CST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: []
  rationale: "Traceability pattern"

- source: "docs/jig-concept/J028_Coverage-Audit.md"
  destination: "dig/archive/jig-concept/J028_Coverage-Audit.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1765917865
    created_human: "2025-12-16 14:44 CST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: []
  rationale: "Coverage audit concept"

- source: "docs/jig-concept/J029_JIG-Manifesto-v10.md"
  destination: "dig/archive/jig-concept/J029_JIG-Manifesto-v10.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1766525018
    created_human: "2025-12-23 14:23 MST"
    parent: "[[J017_JIG-Concept-v9]]"
    children: []
  rationale: "Current JIG manifesto (v10)"

# ═══════════════════════════════════════════════════════════════════════════
# Other jig-concept docs (not in version chain)
# ═══════════════════════════════════════════════════════════════════════════

- source: "docs/jig-concept/ARCHITECTURE_JIG_Core_vs_AI.md"
  destination: "dig/archive/jig-concept/ARCHITECTURE_JIG_Core_vs_AI.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: null
    children: []
  rationale: "Architectural exploration"

- source: "docs/jig-concept/Bricks-and-Layers-by-Language.md"
  destination: "dig/archive/jig-concept/Bricks-and-Layers-by-Language.md"
  frontmatter:
    type: exploration
    status: implemented
    created: 1764767474
    created_human: "2025-12-03 07:11 CST"
    parent: null
    children: []
  rationale: "Language comparison exploration"
```

---

## Category 5: TO DIG — SELA Concept

### docs/jig-concept/SELA/ → dig/archive/sela/

```yaml
- source: "docs/jig-concept/SELA/SELA-Concept-Document.md"
  destination: "dig/archive/sela/SELA001_SELA-Concept-Document.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: null
    children: ["[[SELA002_SELA-Concept-v2]]"]
  rationale: "SELA root concept"

- source: "docs/jig-concept/SELA/SELA-Concept-v2.md"
  destination: "dig/archive/sela/SELA002_SELA-Concept-v2.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA001_SELA-Concept-Document]]"
    children: ["[[SELA003_SELA-Concept-v3]]"]
    superseded_by: "[[SELA003_SELA-Concept-v3]]"
  rationale: "SELA v2"

- source: "docs/jig-concept/SELA/SELA-Concept-v3.md"
  destination: "dig/archive/sela/SELA003_SELA-Concept-v3.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA002_SELA-Concept-v2]]"
    children: []
  rationale: "Current SELA concept (parked)"

- source: "docs/jig-concept/SELA/SELA-alignment-lexicon.md"
  destination: "dig/archive/sela/SELA004_SELA-alignment-lexicon.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA001_SELA-Concept-Document]]"
    children: []
  rationale: "Lexicon doc"

- source: "docs/jig-concept/SELA/SELA-Related-Work.md"
  destination: "dig/archive/sela/SELA005_SELA-Related-Work.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA001_SELA-Concept-Document]]"
    children: []
  rationale: "Related work"

- source: "docs/jig-concept/SELA/SELA-OSE-to-OSTC.md"
  destination: "dig/archive/sela/SELA006_SELA-OSE-to-OSTC.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA001_SELA-Concept-Document]]"
    children: []
  rationale: "OSE to OSTC exploration"

- source: "docs/jig-concept/SELA/SELA-VIBTC-to-OSE.md"
  destination: "dig/archive/sela/SELA007_SELA-VIBTC-to-OSE.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA001_SELA-Concept-Document]]"
    children: []
  rationale: "VIBTC to OSE exploration"

- source: "docs/jig-concept/SELA/GOSTC - Personal Expense Tracker.md"
  destination: "dig/archive/sela/SELA008_GOSTC-Personal-Expense-Tracker.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA001_SELA-Concept-Document]]"
    children: []
  rationale: "GOSTC example"

- source: "docs/jig-concept/SELA/GOSTC Design.md"
  destination: "dig/archive/sela/SELA009_GOSTC-Design.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA008_GOSTC-Personal-Expense-Tracker]]"
    children: []
  rationale: "GOSTC design"

- source: "docs/jig-concept/SELA/gostc-v2-instructions.md"
  destination: "dig/archive/sela/SELA010_gostc-v2-instructions.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA008_GOSTC-Personal-Expense-Tracker]]"
    children: []
  rationale: "GOSTC v2 instructions"

- source: "docs/jig-concept/SELA/Open_Source_SELA_alternatives.md"
  destination: "dig/archive/sela/SELA011_Open_Source_SELA_alternatives.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA001_SELA-Concept-Document]]"
    children: []
  rationale: "Alternatives research"

- source: "docs/jig-concept/SELA/IDEA-constraint-balance.md"
  destination: "dig/archive/sela/SELA012_IDEA-constraint-balance.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA001_SELA-Concept-Document]]"
    children: []
  rationale: "Constraint balance idea"

- source: "docs/jig-concept/SELA/Claude Custom Skills for SELA Workflows.md"
  destination: "dig/archive/sela/SELA013_Claude-Custom-Skills-for-SELA-Workflows.md"
  frontmatter:
    type: exploration
    status: parked
    created: 1763493911
    created_human: "2025-11-18 13:25 CST"
    parent: "[[SELA001_SELA-Concept-Document]]"
    children: []
  rationale: "Skills workflow"
```

---

## Category 6: TO DIG — Audits (journal)

### docs/audits/ (partial) → dig/archive/audits/

```yaml
- source: "docs/audits/JOURNAL-audit-2025-12-24-1600.md"
  destination: "dig/archive/audits/AUDIT001_JOURNAL-audit-2025-12-24.md"
  frontmatter:
    type: journal
    status: implemented
    created: 1767052325
    created_human: "2025-12-29 16:52 MST"
    parent: null
    children: []
  rationale: "Audit journal (deliberation about conducting audit)"
```

---

## Category 7: NOT DIG — Stay in docs/ or move elsewhere

### docs/agents/ → KEEP in docs/agents/

```yaml
- source: "docs/agents/AI-Agent-Context-Delivery-Guide.md"
  destination: "KEEP"
  rationale: "Evergreen reference guide, not deliberation"

- source: "docs/agents/AI-Agent-Task-Crafting-Guide.md"
  destination: "KEEP"
  rationale: "Evergreen reference guide, not deliberation"

- source: "docs/agents/contextJIG-syllabus.md"
  destination: "KEEP"
  rationale: "Agent context doc, not deliberation"

- source: "docs/agents/O-S-Writing-Guide.md"
  destination: "KEEP"
  rationale: "Evergreen reference guide, not deliberation"

- source: "docs/agents/S008-O-S-Conformance-Audit.md"
  destination: "dig/archive/audits/AUDIT002_S008-O-S-Conformance-Audit.md"
  frontmatter:
    type: journal
    status: implemented
    created: 1764735485
    created_human: "2025-12-02 22:18 CST"
    parent: null
    children: []
  rationale: "Actually an audit journal, belongs in DIG"
```

### docs/architecture/ → Move to jig/architecture/

```yaml
- source: "docs/architecture/A001_Core-Artifacts-Contract.md"
  destination: "jig/architecture/A-001.md"
  rationale: "Canonical architecture contract, JIG artifact"

- source: "docs/architecture/A002_CLI-Command-Architecture.md"
  destination: "jig/architecture/A-002.md"
  rationale: "Canonical architecture contract, JIG artifact"

- source: "docs/architecture/A003_Configuration-Architecture.md"
  destination: "jig/architecture/A-003.md"
  rationale: "Canonical architecture contract, JIG artifact"
```

### docs/audits/ (partial) → KEEP in docs/audits/

```yaml
- source: "docs/audits/AUDIT-RESULTS-2025-12-24-1600.md"
  destination: "KEEP"
  rationale: "Audit results data, not deliberation"
```

### docs/configuration.md → KEEP in docs/

```yaml
- source: "docs/configuration.md"
  destination: "KEEP"
  rationale: "User documentation, not deliberation"
```

---

## Summary Statistics

| Category | Files | Destination |
|----------|-------|-------------|
| wip/ → dig/wip/ | 12 | Active deliberation |
| done/ → dig/archive/jigy-v1/ | 33 | Completed work |
| bricks/ → dig/archive/bricks/ | 34 | Bricks concept evolution |
| jig-concept/ → dig/archive/jig-concept/ | 31 | JIG concept evolution |
| SELA/ → dig/archive/sela/ | 13 | SELA exploration |
| audits (partial) → dig/archive/audits/ | 2 | Audit journals |
| **Total to DIG** | **125** | |
| architecture/ → jig/architecture/ | 3 | Canonical contracts |
| KEEP in docs/ | 5 | Reference docs |
| **Total NOT DIG** | **8** | |
| **GRAND TOTAL** | **133** | |

---

## Implementation Notes

### Filename Normalization

Several files need filename normalization:
- Replace hyphens with underscores in type position: `B024_JOURNAL_` not `B024_JOURNAL-`
- Replace hyphens with underscores between prefix and type: `AG027_` not `AG027-`
- Remove spaces from SELA filenames

### Directory Creation

Create these directories before migration:
```
dig/
├── wip/
└── archive/
    ├── jigy-v1/
    ├── bricks/
    ├── jig-concept/
    ├── sela/
    └── audits/
```

### git mv for History

Use `git mv` for all moves to preserve history:
```bash
git mv "docs/path/old.md" "dig/path/new.md"
```

### Frontmatter Injection

For each file, prepend the frontmatter block after moving:
```yaml
---
type: <type>
status: <status>
created: <epoch>
created_human: "<datetime>"
parent: <parent>
children: <children>
---

<original content>
```

### Validation

After migration, run:
```bash
digy validate dig/
```
