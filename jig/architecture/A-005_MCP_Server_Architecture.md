---
id: A-005
type: architecture
title: MCP Server Architecture
goals: [G-001, G-002, G-004, G-005]
specifications: [S-116, S-117]
---

# MCP Server Architecture

## Overview

JIG exposes an MCP (Model Context Protocol) server as a first-class surface for LLM agent access. The MCP server is a peer to the CLI — both are thin surfaces over the shared query layer (`jig.query`). This document governs the MCP surface contract: what tools exist, what they return, and what invariants they maintain.

This architecture is parallel to A-002 (CLI Command Architecture). A-002 governs the human-facing CLI surface; A-005 governs the machine-facing MCP surface. The shared query layer connects them.

---

## Relationship to CLI

### The Core Principle: Surfaces Don't Own Behavior

CLI and MCP are serialization formats, not behavior owners. Both delegate to `jig.query` for all query logic. The query layer is the single source of truth for "what does JIG know and how do you ask it."

This means:
- If a query behavior exists in MCP, it exists identically in CLI (and vice versa)
- Differences between surfaces are intentional and concern-specific, never accidental results of build order
- New query capabilities are born in the query layer and available to both surfaces immediately

### What Each Surface Owns

| Concern | CLI (A-002) | MCP (A-005) |
|---------|-------------|-------------|
| **Transport** | Terminal stdin/stdout | MCP stdio (JSON-RPC) |
| **Lifecycle** | One-shot (run and exit) | Long-lived server process |
| **Output** | human/json/markdown flags (S-093) | Structured data (always dict/JSON) |
| **Error signaling** | Exit codes (0/1/2) + stderr | Graceful degradation (empty results) |
| **Config loading** | Per invocation | Once at startup |
| **Dispatch** | Click command routing | MCP tool dispatch |

### Layer Diagram

```
         ┌───────────────┐         ┌──────────────┐
         │  jigy context │         │   jigy mcp   │ ◄── LLM agent (stdio)
         │  jigy validate│         │  (FastMCP)   │
         │  (Click CLI)  │         └──────┬───────┘
         │    A-002      │                │  A-005
         └───────┬───────┘                │
                 │                        │
    formatting + │                        │ tool decorators +
    exit codes   │                        │ graceful degradation
                 │                        │
         ┌───────┴────────────────────────┴───────┐
         │           jig.query (shared)            │
         │                                         │
         │  query_node(identifier, config) → dict  │
         │  search_docs(query, config) → list      │
         │  query_overview(config) → dict           │
         │  query_validate(config, scope) → dict   │
         │  config_to_graphs(config) → dict        │
         └─────────────────┬───────────────────────┘
                           │
                    ┌──────────────┐
                    │  JigConfig   │
                    │  load_config │
                    └──────┬───────┘
                           ▼
              jig/**/*.md  +  jig/generated/*.ndjson
```

### Why `jigy mcp` Is Not in A-002

`jigy mcp` is architecturally different from every other CLI command:
- Not verb-first — it is a transport mode, not a user action
- Not one-shot — starts a long-lived server process
- Not human-facing — serves machine consumers
- No output format flags — MCP protocol handles serialization

Therefore `jigy mcp` lives under A-005's governance, not A-002's command contract. The Click registration in `main.py` is merely a launch mechanism.

---

## Design Principles

### 1. Read-Only

The MCP server is a pure observer. No tools mutate JIG artifacts. No tools trigger graph rebuilds, file writes, or mend operations.

**Rationale:** Mutation requires careful design around confirmation, side effects, and error recovery. Read-only access is safe, useful, and sufficient for the primary use case: agents reading intent before modifying code.

**Future:** Mutation tools (creating specs, running mend) are a separate, later concern. They will require explicit confirmation protocols.

### 2. Graceful Degradation

Missing data produces empty results, never errors. The LLM agent should never receive an exception or error message from JIG for a well-formed query that happens to match nothing.

| Situation | Response |
|-----------|----------|
| Unknown identifier | `{}` (empty dict) |
| Empty search query | `[]` (empty list) |
| No search matches | `[]` (empty list) |
| Missing graph files | Neighbors omitted silently |
| Missing charter | Charter fields omitted |
| Non-existent project | Empty overview |

**Rationale:** LLM agents interpret errors as signals to retry or escalate. Missing data is not an error — it is information ("this doesn't exist"). Empty results are semantically clear and don't consume agent context with stack traces.

**Where this is enforced:** The query layer (`jig.query`), not the MCP surface. This means CLI also benefits from the same graceful degradation when using query layer functions directly.

### 3. JIG's Native Vocabulary

MCP tools use JIG's domain language, not generic terms.

| Tool Name | Not This |
|-----------|----------|
| `lookup_node` | `lookup_jig`, `get_document`, `read_file` |
| `search_docs` | `search_jig`, `find`, `grep` |
| `get_overview` | `get_summary`, `status`, `info` |
| `validate_project` | `check`, `lint`, `verify` |

**Rationale:** Agents interact with JIG's conceptual model — nodes in a graph, documents in a corpus, validation of a project. Tool names should teach the model, not abstract it away.

### 4. Full Identifier Support

All tools that accept identifiers support the complete JIG identifier vocabulary:

| Pattern | Example | Resolves To |
|---------|---------|-------------|
| `S-###` | `S-042` | Specification |
| `O-###` | `O-016` | Outcome |
| `G-###` | `G-001` | Goal |
| `A-###` | `A-002` | Architecture |
| `B-*` | `B-cli` | Brick |
| `F-*` | `F-jig.cli.main.cli` | Function |
| `T-*` | `T-test_context.test_resolve` | Test |
| `Charter` | `Charter` | Charter document |
| File path | `src/jig/cli/main.py` | File's nodes |

**This is a strict superset of ASE's implementation**, which only handled S/A/O/G/Charter.

### 5. Config-Driven Paths

All file access goes through `JigConfig.paths`. The MCP server never constructs paths from string literals.

```
# Never this:
Path("jig") / "specifications" / f"S-{num}.md"

# Always this:
config.paths.specifications / f"S-{num}.md"
```

**Rationale:** JIG supports `jig.toml` path overrides. Hardcoded paths break for any project with non-default configuration.

### 6. stdio Transport

The MCP server uses stdio transport exclusively. No HTTP, no SSE, no WebSocket.

**Rationale:** stdio is the simplest integration with Claude Code. No ports to manage, no network configuration, no firewall issues. This matches ASE's proven deployment pattern.

---

## Tool Contract

### `lookup_node`

**Purpose:** Resolve an identifier to its full context — content, frontmatter, and graph neighborhood.

**Parameters:**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `node_id` | `str` | yes | — |

**Returns:** Dict with node content, frontmatter fields, and graph neighbors. Empty dict `{}` if identifier cannot be resolved.

**Delegates to:** `jig.query.query_node()`

**Behavioral contract:**
- Full identifier vocabulary (all patterns above)
- Graph neighbors are best-effort — included when graphs exist, omitted when they don't
- Never raises on unresolvable identifiers

---

### `search_docs`

**Purpose:** Text search across JIG's markdown corpus.

**Parameters:**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `query` | `str` | yes | — |
| `limit` | `int` | no | `20` |

**Returns:** List of `{id, title, path, match}` dicts. Empty list if no matches or empty query.

**Delegates to:** `jig.query.search_docs()`

**Behavioral contract:**
- Case-insensitive substring matching
- Searches specifications, outcomes, architecture, charter
- `match` field contains first matching line as context snippet
- Results ordered by corpus position, capped at `limit`

---

### `get_overview`

**Purpose:** Project summary — the same orientation data as `jigy context` (bare mode).

**Parameters:** None.

**Returns:** Dict with charter, goals, architecture, outcomes, spec counts, bricks by layer, towers, and traversal keys.

**Delegates to:** `jig.query.query_overview()`

**Behavioral contract:**
- Returns same data structure as `jigy context -j` (bare mode)
- Missing artifacts produce empty/null fields, not errors
- Spec counts reflect current graph state (implemented, verified)

---

### `validate_project`

**Purpose:** Run validation and return results. Read-only query — no side effects.

**Parameters:**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `scope` | `str` | no | `"full"` |

**Scope values:** `"intent"`, `"bricks"`, `"full"`

**Returns:** Dict with errors, summary (total, auto_fixable, manual), and counts.

**Delegates to:** `jig.query.query_validate()`

**Behavioral contract:**
- Same validation results as `jigy validate intent -j`, `jigy validate bricks -j`, or `jigy validate -j`
- Scope filtering uses the same spec sets as CLI
- Does not trigger graph rebuilds — validates against current graph state

---

## Resources

**Deferred.** MCP resources (`jig://` URIs) are not included in v1. Tools cover all query needs. Resources can be added without breaking changes when a demonstrated need arises.

---

## Consumer Configuration

Projects consuming JIG's MCP server configure their `.mcp.json`:

```json
{
  "mcpServers": {
    "jig": {
      "command": "uv",
      "args": ["run", "--extra", "mcp", "jigy", "mcp"]
    }
  }
}
```

The `--extra mcp` flag ensures the `fastmcp` optional dependency is installed.

---

## Extensibility

### Adding New Tools

New MCP tools SHALL:

1. Delegate to a `jig.query` function (no business logic in the MCP surface)
2. Follow JIG's native vocabulary for naming
3. Return structured data (dict or list), never formatted strings
4. Degrade gracefully on missing data
5. Be read-only (no mutation)
6. Be documented in this contract before implementation

### Reserved Tool Names

The following tool names are reserved for future use:

- `get_node_history` — Audit trail for a specific node
- `get_coverage` — Implementation and verification coverage report
- `get_graph_summary` — Lightweight graph metadata (node/edge counts by type)

### Mutation Tools (Future)

When mutation tools are added (creating specs, running mend, rebuilding graphs), they will:
- Require explicit confirmation before executing
- Be governed by a separate "MCP Mutation" architecture document
- Not be added to this read-only contract

---

## Compliance

All MCP development SHALL comply with this architecture. New tools, parameters, or behaviors SHALL be documented here before implementation. The read-only and graceful degradation invariants are non-negotiable within the scope of this document.

This contract is evergreen — it evolves with JIG but maintains backward compatibility for tool names and parameter schemas within major versions.
