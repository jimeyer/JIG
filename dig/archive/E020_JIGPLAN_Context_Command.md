---
title: "Context Command JIGPLAN"
type: jigplan
status: implemented
decision: completed
created: 1737244800
created_human: "2026-01-18 18:30 CST"
parent: "[[E019_SCOPE_Context_Command_Node_List]]"
children: []
---

# Context Command JIGPLAN

**SCOPE:** dig/wip/E019_SCOPE_Context_Command_Node_List.md
**Date:** 2026-01-18
**Status:** Draft
**Author:** agent

---

## Summary

Adds `jigy context <identifier>` command for graph neighborhood exploration. Creates 1 outcome (O-030), 4 specs (S-110 through S-113), and adds M-jig.cli.context to B-cli brick. No backwards compatibility concerns—this is a new feature.

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | O-019 | Intuitive CLI Experience | Context command follows CLI patterns |
| CREATE | O-030 | Graph Neighborhood Exploration | New capability for agent graph traversal |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| REUSE | S-057 | Project Root Auto-Discovery | Context command uses auto-discovery |
| REUSE | S-093 | Universal Output Format Flags | Context command supports -j/-m/-v |
| CREATE | S-110 | Context CLI Command | New command entry point |
| CREATE | S-111 | Context Identifier Resolution | Parse and resolve identifiers |
| CREATE | S-112 | Context Graph Traversal | Traversal algorithm |
| CREATE | S-113 | Context Response Schema | JSON output format |

---

## O/S Node Details

### Nodes to CREATE

#### O-030: Graph Neighborhood Exploration (NEW)

**File:** `jig/outcomes/O-030_Graph_Neighborhood_Exploration.md` (created)
**Goals:** G-002, G-005
**Summary:** Enables agents to explore graph connections from any identifier, understanding context before modifying code.

#### S-110: Context CLI Command (NEW)

**File:** `jig/specifications/S-110_Context_CLI_Command.md` (created)
**Outcome:** O-030
**Summary:** The `jigy context <identifier>` command with `--max N` flag.

#### S-111: Context Identifier Resolution (NEW)

**File:** `jig/specifications/S-111_Context_Identifier_Resolution.md` (created)
**Outcome:** O-030
**Summary:** Resolution of S-###, O-###, G-###, A-###, B-*, F-*, T-*, Charter, and file paths.

#### S-112: Context Graph Traversal (NEW)

**File:** `jig/specifications/S-112_Context_Graph_Traversal.md` (created)
**Outcome:** O-030
**Summary:** Asymmetric traversal: full ancestors, immediate children, budget-limited descendants.

#### S-113: Context Response Schema (NEW)

**File:** `jig/specifications/S-113_Context_Response_Schema.md` (created)
**Outcome:** O-030
**Summary:** JSON schema with root, nodes (flat list with depth/edge), and more count.

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| MODIFY | B-cli | 1 | Add M-jig.cli.context unit |
| FORBIDDEN | B-decorators | 0 | Foundation, no changes |
| FORBIDDEN | B-intent-graph | 0 | Read-only for context |
| FORBIDDEN | B-impl-graph | 0 | Read-only for context |
| FORBIDDEN | B-verification-graph | 1 | Read-only for context |
| UNAFFECTED | B-validation | 0 | No changes needed |
| UNAFFECTED | B-config | 0 | No changes needed |
| UNAFFECTED | B-rules | 0 | No changes needed |

---

### Brick Details

#### B-cli Modifications

- **Current units:** M-jig.cli.{main, validate, discovery, rebuild, show, audit, auto_rebuild, output, init, mend}
- **Add units:** M-jig.cli.context
- **Layer change:** None (stays at layer 1)
- **New dependencies:** None (reads from existing graphs)
- **Changes:** New context.py module implementing S-110 through S-113

#### FORBIDDEN Bricks

These bricks MUST NOT be modified by any work unit:

- **B-decorators** (layer 0): Core @jig.implements/@jig.verifies infrastructure
- **B-intent-graph** (layer 0): Context reads intent graph, doesn't modify
- **B-impl-graph** (layer 0): Context reads impl graph, doesn't modify
- **B-verification-graph** (layer 1): Context reads verify graph, doesn't modify

**Sub-agent constraint:** Any modification to FORBIDDEN bricks is an immediate escalation trigger.

---

## Layer/Dependency Analysis

### Layer Structure (Affected Bricks)

```
Layer 0: FORBIDDEN (read-only access)
  B-intent-graph ← context reads
  B-impl-graph ← context reads
  B-config ← context uses for project root

Layer 1: AFFECTED
  B-cli (MODIFY)
    └─► depends on: B-intent-graph, B-impl-graph, B-verification-graph, B-config ✓
  B-verification-graph ← context reads
```

### Dependency Constraints

- B-cli (layer 1) MAY read from all layer 0 bricks
- B-cli (layer 1) MAY read from B-verification-graph (layer 1, same level)
- No new layer violations introduced

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
| implements | F-jig.cli.context.context_command | S-110 |
| implements | F-jig.cli.context.resolve_identifier | S-111 |
| implements | F-jig.cli.context.traverse_graph | S-112 |
| implements | F-jig.cli.context.format_response | S-113 |
| verifies | T-test_context.test_command_accepts_identifier | S-110 |
| verifies | T-test_context.test_identifier_resolution | S-111 |
| verifies | T-test_context.test_traversal_ancestors | S-112 |
| verifies | T-test_context.test_traversal_budget | S-112 |
| verifies | T-test_context.test_response_schema | S-113 |

### Decorators to REMOVE

None.

### Decorators to MODIFY

None.

---

## Clean Break Actions

This work follows clean break protocol:

- [x] New feature, no old code paths to delete
- [x] No backwards compatibility needed
- [x] Clean implementation with no shims
- [ ] Tests will be written from scratch

### Code to Delete

None (new feature).

### O/S Nodes to Delete (After Validation)

None.

---

## Fresh Agent Review Summary

### Review Findings

| Category | Type | Severity | Issue | Resolution |
|----------|------|----------|-------|------------|
| 5 | MECHANICAL | BLOCKER | Duplicate `outcome:` field in specs | Fixed: removed singular field, kept `outcomes: [O-030]` |
| 4 | MECHANICAL | WARNING | No test decorators listed | Fixed: added 5 @jig.verifies entries to decorator plan |
| 5 | MECHANICAL | WARNING | bricks.yaml already contains M-jig.cli.context | Intentional: Step 6 pre-adds units during JIGPLAN creation |
| 2 | JUDGMENT | NOTE | S-112 edge type table is implementation detail | Kept: edge types are stable schema, not impl detail |
| 2 | JUDGMENT | NOTE | S-113 edge field overlaps S-112 vocabulary | Kept: cross-reference is acceptable, no consolidation needed |

### Judgment Decisions

**Issue:** S-112 includes specific edge type names (defines_goal, supports_goal, etc.)

**Options considered:**
1. Abstract to "upward/downward edges" only
2. Keep specific edge type vocabulary

**Decision:** Option 2 - Keep specific edge types

**Rationale:** The edge types are part of the intent graph schema defined in S-083, S-084, S-085. They are stable vocabulary, not implementation details. Removing them would make S-112 ambiguous about which edges to traverse.

---

## Approval Checklist

Before human approval:

- [x] All existing specs reviewed for REUSE opportunities
- [x] New specs follow evergreen guidelines (behavior, not implementation)
- [x] Brick layer constraints validated
- [x] FORBIDDEN bricks identified
- [x] @jig decorator plan complete
- [x] Clean break actions specified
- [x] **Fresh Agent Review completed**
- [x] All MECHANICAL issues resolved
- [x] All JUDGMENT issues resolved

---

**Awaiting human approval before proceeding to PLAN.**
