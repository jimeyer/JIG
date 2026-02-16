---
type: jigplan
title: "JIG MCP Server"
status: active
created: 1739750400
created_human: "2026-02-16"
parent: E030
children: []
---

# JIGPLAN: JIG MCP Server

**SCOPE:** dig/wip/E030_SCOPE_MCP_Server.md
**Date:** 2026-02-16
**Status:** Draft
**Author:** AI agent (Claude)

---

## Summary

Extract query logic from B-cli into a new B-query brick (Layer 0), add text search as a new capability (S-116), and build an MCP server surface (S-117) in a new B-mcp-server brick (Layer 1). Creates 1 new outcome (O-031), 2 new specs, 2 new bricks; modifies B-cli to delegate to the query layer. Creates architecture document A-005 for the MCP surface contract.

---

## O/S Node Reconciliation

### Outcomes

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| CREATE | O-031 | Programmatic JIG Access for LLM Agents | New capability: agents query JIG via MCP tools |
| REUSE | O-030 | Graph Neighborhood Exploration | Query layer wraps the same traversal behavior |
| REUSE | O-016 | CI and Tooling Integration | MCP is another programmatic integration surface |
| REUSE | O-019 | Intuitive CLI Experience | CLI unchanged; refactored to use query layer internally |

### Specifications

| Action | Node | Title | Rationale |
|--------|------|-------|-----------|
| CREATE | S-116 | Text Search Across JIG Corpus | Genuinely new capability — no existing search |
| CREATE | S-117 | MCP Server for LLM Agent Access | New surface: MCP tools over query layer |
| REUSE | S-111 | Context Identifier Resolution | query_node wraps resolve_identifier — same behavior |
| REUSE | S-112 | Context Graph Traversal | query_node wraps traverse_graph — same behavior |
| REUSE | S-113 | Context Response Schema | query_node returns same schema |
| REUSE | S-114 | Project Overview Output | query_overview re-exports build_overview |
| REUSE | S-023 | Intent Validation CLI Command | query_validate wraps same engine + scope filtering |
| REUSE | S-024 | Brick Validation CLI Command | query_validate wraps same engine + scope filtering |
| REUSE | S-025 | Full Validation CLI Command | query_validate wraps same engine + scope filtering |

---

## O/S Node Details

### Nodes to CREATE

#### O-031: Programmatic JIG Access for LLM Agents (NEW)

**File:** `jig/outcomes/O-031_Programmatic_JIG_Access_for_LLM_Agents.md` (created)
**Summary:** LLM agents query JIG's graph, search docs, and check validation via structured MCP tools without parsing CLI output.

#### S-116: Text Search Across JIG Corpus (NEW)

**File:** `jig/specifications/S-116_Text_Search_Across_JIG_Corpus.md` (created)
**Implements:** O-031
**Summary:** Case-insensitive substring search across all JIG markdown files, returning structured results with document ID, title, path, and context snippet.

#### S-117: MCP Server for LLM Agent Access (NEW)

**File:** `jig/specifications/S-117_MCP_Server_for_LLM_Agent_Access.md` (created)
**Implements:** O-031
**Summary:** `jigy mcp` starts stdio MCP server exposing four read-only tools: lookup_node, search_docs, get_overview, validate_project. Graceful degradation on missing data.

---

## Brick Scope

| Action | Brick | Layer | Rationale |
|--------|-------|-------|-----------|
| CREATE | B-query | 0 | Shared query layer: pure functions consumed by both CLI and MCP |
| CREATE | B-mcp-server | 1 | MCP protocol surface over query layer |
| MODIFY | B-cli | 1 | Refactor: delegate to B-query instead of owning query logic |
| FORBIDDEN | B-decorators | 0 | Foundation — no changes |
| FORBIDDEN | B-validation | 0 | Consumed by query layer, not modified |
| FORBIDDEN | B-config | 0 | Consumed by query layer, not modified |
| FORBIDDEN | B-impl-graph | 0 | No changes |
| FORBIDDEN | B-intent-graph | 0 | No changes |
| FORBIDDEN | B-hashing | 0 | No changes |
| FORBIDDEN | B-languages | 0 | No changes |
| FORBIDDEN | B-staleness | 0 | No changes |
| FORBIDDEN | B-templates | 0 | No changes |
| FORBIDDEN | B-init | 0 | No changes |
| FORBIDDEN | B-rules | 0 | No changes |
| FORBIDDEN | B-mend | 0 | No changes |
| UNAFFECTED | B-verification-graph | 1 | No changes |
| UNAFFECTED | B-audit | 1 | No changes |

---

### Brick Details

#### B-query (NEW)

- **Layer:** 0
- **Purpose:** Shared query layer providing pure functions for JIG graph queries. Both CLI and MCP delegate here. This brick owns the behavioral logic; surfaces own only formatting and transport.
- **Units:**
  - M-jig.query
  - M-jig.query.node
  - M-jig.query.search
  - M-jig.query.validate
  - M-jig.query.overview
- **Dependencies:** B-config (Layer 0), B-validation (Layer 0), B-decorators (Layer 0)

#### B-mcp-server (NEW)

- **Layer:** 1
- **Purpose:** MCP protocol surface. Thin FastMCP tool decorators over B-query functions. No business logic — only transport and tool registration.
- **Units:**
  - M-jig.mcp
  - M-jig.mcp.server
- **Dependencies:** B-query (Layer 0), B-config (Layer 0)

#### B-cli Modifications

- **Layer change:** None (stays at Layer 1)
- **Unit list change:** None (modules stay, functions move internally)
- **New dependency:** B-query (Layer 0)
- **Changes:** CLI commands (`context_command`, `validate_intent_command`, `validate_bricks_command`) refactored to call B-query functions instead of inlining query logic. Pure functions (`resolve_identifier`, `traverse_graph`, `build_overview`, `_filter_errors_by_specs`) move to B-query; CLI modules re-import them for backwards compatibility.

#### FORBIDDEN Bricks

All Layer 0 bricks except B-query (new) are FORBIDDEN. All Layer 1 bricks except B-cli and B-mcp-server (new) are UNAFFECTED.

**Sub-agent constraint:** Any modification to FORBIDDEN bricks is an immediate escalation trigger.

---

## Layer/Dependency Analysis

### Layer Structure (Affected Bricks)

```
Layer 0: NEW + FORBIDDEN
  B-query (NEW)
    └─► depends on: B-config ✓, B-validation ✓, B-decorators ✓
  B-config ← consumed, not modified (FORBIDDEN)
  B-validation ← consumed, not modified (FORBIDDEN)
  B-decorators ← consumed, not modified (FORBIDDEN)

Layer 1: NEW + MODIFY
  B-mcp-server (NEW)
    └─► depends on: B-query ✓ (Layer 0), B-config ✓ (Layer 0)
  B-cli (MODIFY)
    └─► depends on: B-query ✓ (Layer 0, new dependency)
    └─► existing dependencies on Layer 0 bricks unchanged
```

### Dependency Constraints

- B-query (Layer 0) MUST NOT depend on B-cli (Layer 1) — this drives the function move
- B-query (Layer 0) MUST NOT depend on B-mcp-server (Layer 1)
- B-mcp-server (Layer 1) and B-cli (Layer 1) are peers — no dependency between them
- No circular dependencies between any affected bricks

### Architectural Decision: Move Functions vs. Wrap

**Issue:** The SCOPE (E030) describes the query layer as wrapping functions that remain in `cli/context.py` and `cli/overview.py`. However, `jig.query` importing from `jig.cli` creates a Layer 0 → Layer 1 dependency violation.

**Resolution:** Move the pure functions (resolve_identifier, traverse_graph, build_overview, filter_errors_by_specs, and their helpers) from `cli/` to `query/`. CLI modules re-import from `query/` for backwards compatibility. This satisfies:
- Layer constraint (B-query at Layer 0, no upward dependency)
- SCOPE principle ("surfaces don't own behavior")
- Backwards compat (re-imports mean existing test imports work)

The alternative — B-query at Layer 2 wrapping B-cli — would push B-mcp-server to Layer 3, creating unnecessary depth and contradicting the principle that query logic is foundational.

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
| implements | F-jig.query.search.search_docs | S-116 |
| implements | F-jig.mcp.server.run_server | S-117 |
| verifies | (test functions for search) | S-116 |
| verifies | (test functions for MCP server) | S-117 |

### Decorators to MOVE (with function relocation)

| Type | Old Location | New Location | Spec |
|------|-------------|-------------|------|
| implements | F-jig.cli.context.resolve_identifier | F-jig.query.node.resolve_identifier | S-111 |
| implements | F-jig.cli.context.traverse_graph | F-jig.query.node.traverse_graph | S-112 |
| implements | F-jig.cli.context.format_response | F-jig.query.node.format_response | S-113 |
| implements | F-jig.cli.overview.build_overview | F-jig.query.overview.build_overview | S-114 |
| implements | F-jig.cli.overview.format_overview_human | F-jig.query.overview.format_overview_human | S-114 |
| implements | F-jig.cli.overview.format_overview_json | F-jig.query.overview.format_overview_json | S-114 |
| implements | F-jig.cli.overview.format_overview_markdown | F-jig.query.overview.format_overview_markdown | S-114 |

Note: `format_human` and `format_markdown` in context.py are undecorated — they move with format_response but have no decorator changes. `show_overview` in overview.py (S-114 decorator) stays in B-cli — it's the Click command handler.

### Decorators to REMOVE

None.

### Decorators to MODIFY

None.

---

## Clean Break Actions

This work follows clean break protocol:

- [x] No backwards compatibility shims needed (re-imports serve as migration path, not compat shim)
- [x] No feature flags
- [x] No old code paths to delete (this is additive + refactor)
- [x] Unimplemented features will raise NotImplementedError

### Code to Move (Not Delete)

The following functions move from `cli/` to `query/`. The original modules retain re-imports for backwards compatibility.

**From `src/jig/cli/context.py` to `src/jig/query/node.py`:**
- `IdentifierError` class
- `PATTERNS` dict
- `VALID_PATTERNS` list
- `_load_graph()`, `_load_all_graphs()`, `_match_pattern()`
- `resolve_identifier()`
- `traverse_graph()` and all traversal helpers (`_build_adjacency`, `_get_ancestors`, `_collect_children`, `_collect_descendants`)
- `format_response()` and format helpers (`format_human`, `format_markdown`)
- New: `config_to_graphs()`, `query_node()`

**From `src/jig/cli/overview.py` to `src/jig/query/overview.py`:**
- `_load_yaml_frontmatter()`, `_load_ndjson()` (helper functions)
- `build_overview()` (@jig.implements S-114)
- `format_overview_human()` (@jig.implements S-114)
- `format_overview_json()` (@jig.implements S-114)
- `format_overview_markdown()` (@jig.implements S-114)
- All pure formatters (string → string). No click dependency.

**From `src/jig/cli/validate.py` to `src/jig/query/validate.py`:**
- `_filter_errors_by_specs()` → renamed to `filter_errors_by_specs()` (public)
- Hardcoded spec sets → `INTENT_SPECS`, `BRICK_SPECS` (named constants)
- New: `query_validate()`

**Remaining in CLI modules:**
- `context.py`: `context_command()` (Click command handler) + re-imports from `query.node`
- `overview.py`: `show_overview()` (Click command handler) + re-imports from `query.overview`
- `validate.py`: `validate_intent_command()`, `validate_bricks_command()`, `validate_full_command()` (Click handlers) + re-imports from `query.validate`

---

## Architecture Document

### A-005: MCP Server Architecture (NEW)

**File:** `jig/architecture/A-005_MCP_Server_Architecture.md`
**Goals:** G-001, G-002, G-004, G-005
**Specifications:** S-116, S-117

This document governs the MCP surface contract, parallel to how A-002 governs the CLI. Content defined in E030 SCOPE "Architectural Intent" section:

- Surface contract: tool names, parameter schemas, return shapes
- Read-only invariant
- Graceful degradation contract
- Transport: stdio only
- Tool naming: JIG's native vocabulary (lookup_node, not lookup_jig)
- Relationship to CLI: both surfaces delegate to shared query layer
- Relationship to A-002: `jigy mcp` is a transport mode, not a verb-first command

---

## Fresh Agent Review Summary

### Review Findings

| Category | Type | Severity | Issue | Resolution |
|----------|------|----------|-------|------------|
| 4 | MECHANICAL | BLOCKER | Assumed format_human/format_markdown had S-113 decorators; missing from move list | Verified: they are undecorated. Move list was correct. No change needed. |
| 4 | MECHANICAL | WARNING | S-114 decorators on format_overview_* functions not in move list | Added all three format_overview_* functions to decorator move table |
| 5 | MECHANICAL | WARNING | Helper function move list completeness | Verified "Code to Move" section covers all helpers; decorator table only covers decorated functions (correct) |
| 3 | MECHANICAL | NOTE | All FORBIDDEN bricks verified in bricks.yaml | No action needed |
| 5 | MECHANICAL | NOTE | O-031 ↔ S-116/S-117 cross-references verified | No action needed |
| 3 | MECHANICAL | NOTE | No circular dependency risk detected | No action needed |

### Judgment Decisions

**Issue:** Query layer importing from CLI creates layer violation
**Options considered:**
1. Move pure functions from cli/ to query/ (B-query at Layer 0)
2. B-query at Layer 2 wrapping B-cli (Layer 1)

**Heuristic analysis:**
| Heuristic | Option 1 (Move) | Option 2 (Wrap) |
|-----------|-----------------|-----------------|
| Conceptual clarity | ✅ Surfaces don't own behavior | ❌ Behavior still lives in surface brick |
| Single responsibility | ✅ B-query owns queries, B-cli owns formatting | ❌ B-cli owns both queries and formatting |
| Clean breaks | ✅ Clean layer structure | ❌ Unnecessary depth (Layer 2→3) |
| Documentation value | ✅ Layer 0 = foundational capability | ❌ Layer 2 = derived, suggests optional |

**Decision:** Option 1 (move functions), driven by conceptual clarity and single responsibility. The SCOPE principle "surfaces don't own behavior" requires this.

---

## Approval Checklist

Before human approval:

- [x] All existing specs reviewed for REUSE opportunities
- [x] New specs follow evergreen guidelines (behavior, not implementation)
- [x] Brick layer constraints validated
- [x] FORBIDDEN bricks identified
- [x] @jig decorator plan complete
- [x] Clean break actions specified
- [x] **Fresh Agent Review completed (Step 9)**
- [x] All MECHANICAL issues resolved (decorator move list updated, helpers verified)
- [x] All JUDGMENT issues resolved via Charter philosophy (move vs. wrap decided)

---

**Awaiting Fresh Agent Review, then human approval before proceeding to PLAN.**
