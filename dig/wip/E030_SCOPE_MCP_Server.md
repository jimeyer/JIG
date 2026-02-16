---
type: scope
title: "JIG MCP Server"
status: active
created: 1739750400
created_human: "2026-02-16"
parent: null
children: []
prompt: |
  Extract JIG-specific MCP tools from ASE into JIG proper. JIG should ship its own MCP server
  (`jigy mcp`) so any JIG-enabled project gets LLM-accessible traceability without project-specific wiring.
  Informed by lessons learned from ASE's F270 MCP implementation.
  Central design constraint: CLI and MCP are thin surfaces over a shared query layer — no behavioral divergence.
---

# JIG MCP Server

## Problem Statement

JIG's graph — specs, outcomes, goals, architecture, bricks, implementation, verification — is exactly the kind of structured context that LLM agents need to reason about codebases. But today, JIG can only be queried via CLI (`jigy context`, `jigy validate`). There is no programmatic interface for LLM agents to discover and traverse JIG artifacts.

**Current workaround:** ASE's MCP server (F270) includes `lookup_jig_tool` and `search_jig_tool`. These work, but they belong to the wrong project. ASE reimplements JIG's own concerns — identifier resolution, frontmatter parsing, graph traversal — with ad-hoc glue code that bypasses JIG's config system and duplicates logic from `jig.cli.context`.

**Why this matters:**
- **Responsibility misplacement** — ASE guards invariants it doesn't own (how IDs resolve, where files live). If JIG changes its layout, ASE breaks silently.
- **Not reusable** — Every JIG-enabled project would need to reimplement these tools. JIG is a general-purpose tool; MCP access should ship with it.
- **Wrong abstraction** — ASE's implementation operates at the filesystem level (globbing markdown, pattern-matching prefixes). JIG's native abstraction is the graph (nodes, edges, traversals). An MCP server in JIG should speak graph, not filesystem.

**Deeper problem exposed during scoping:** The query logic that both CLI and MCP need — identifier resolution, graph traversal, overview construction, validation with scope filtering — currently lives inside CLI command handlers. Functions like `resolve_identifier()` and `traverse_graph()` are pure and reusable, but glue logic (constructing graph paths from config, catching `IdentifierError` for graceful degradation, validation scope filtering) is scattered across `cli/context.py` and `cli/validate.py`. Building MCP as a second consumer of this logic requires extracting it into a shared query layer first, or we'll duplicate glue code and create accidental behavioral divergence between surfaces.

---

## Lessons From ASE's F270 Implementation

ASE built a working MCP server (S-102, F270/F273) with JIG tools. Key observations:

### What Worked Well

| Pattern | Detail |
|---------|--------|
| **Read-only constraint** | No mutation tools. MCP server is a pure observer. Keep this. |
| **Graceful degradation** | Missing files → empty results, not errors. Missing graphs → skip neighbors. |
| **Core/wrapper separation** | Pure functions with `jig_dir` parameter for testability, thin `@mcp_server.tool()` wrappers on top. |
| **stdio transport** | Simplest integration with Claude Code. No ports, no network. |
| **Tool parameter design** | `node_id`, `query`, `limit` — simple, composable parameters. |

### What Was Wrong

| Issue | Detail |
|-------|--------|
| **Duplicated identifier resolution** | ASE wrote `_resolve_jig_file()` — a degraded copy of JIG's `resolve_identifier()`. Only handles S/A/O/G/Charter; misses B-*, F-*, T-*, file paths. |
| **Hardcoded directory layout** | ASE assumes `jig/specifications/`, `jig/architecture/`, etc. JIG's `JigConfig.paths` already abstracts this. |
| **Hardcoded graph paths** | ASE constructs `jig_dir.parent / "jig" / "generated" / "intent-graph.ndjson"`. JIG's config knows where `generated/` lives. |
| **Imported JIG internals** | `from jig.mend.yaml_editor import parse_frontmatter_file` and `from jig.cli.context import traverse_graph, _load_all_graphs`. Reaching into private functions. |
| **No config awareness** | ASE never calls `load_config()`. Breaks for any project with non-default `jig.toml` paths. |

### Behavioral Spec Worth Preserving

These behaviors from ASE's tests (39 tests in `tests/ase/mcp/test_mcp_server.py`) define the contract:

- `lookup_jig("S-042")` → `{id, kind, frontmatter, body, neighbors}`
- `lookup_jig("Charter")` → charter content; `lookup_jig("G-1")` → also charter content
- `lookup_jig("S-999")` → `{}` (not found)
- `search_jig("convergence")` → `[{path, match}]` with first matching line as context
- `search_jig("")` → `[]`
- Graph neighbors are best-effort — included when graphs exist, omitted silently when they don't

---

## Charter Alignment

This scope directly serves four of five Charter goals:

| Goal | How MCP Serves It |
|------|-------------------|
| **G-001: Grounding in Reality** | Agents query the actual graph instead of guessing. MCP returns structured data — stronger grounding than CLI text output that agents must parse. |
| **G-002: Continuity Across Sessions** | MCP gives agents persistent access to intent/impl/verify graphs across sessions. The graph *is* the continuity mechanism. |
| **G-004: Intent Alignment** | `lookup_node` lets agents read specs/outcomes *before* modifying code. The Charter says "Read before writing" — MCP makes this frictionless for agents. |
| **G-005: Full Traceability** | Graph traversal exposes the full Charter→Goal→Outcome→Spec→Function→Test chain. Agents can ask "what is the purpose of this function?" and get a structured answer. |

G-003 (Enforcing Constraints) is served indirectly via `validate_project` — agents can check constraints, but enforcement remains a CI/human gate. Read-only is correct here.

No Charter update is required. MCP is a natural expression of existing goals, not a new direction.

---

## Architectural Intent

### The Core Principle: Surfaces Don't Own Behavior

CLI and MCP are **serialization formats, not behavior owners.** Both are thin surfaces over a shared query layer. The query layer is the single source of truth for "what does JIG know and how do you ask it."

This means:
- If a query behavior exists in MCP, it exists identically in CLI (and vice versa)
- Differences between surfaces are intentional and concern-specific (output formatting, error signaling, transport), never accidental results of build order
- New query capabilities (like text search) are born in the query layer and available to both surfaces immediately

### Layer Diagram

```
         ┌───────────────┐         ┌──────────────┐
         │  jigy context │         │   jigy mcp   │ ◄── LLM agent (stdio)
         │  jigy validate│         │  (FastMCP)   │
         │  (Click CLI)  │         └──────┬───────┘
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
              ┌────────────┼────────────────┐
              ▼            ▼                ▼
       resolve_identifier  traverse_graph   validate()
       (context.py)        (context.py)     (engine.py)
              │            │                │
              └────────────┼────────────────┘
                           ▼
                    ┌──────────────┐
                    │  JigConfig   │  ← single source of truth for paths
                    │  load_config │
                    └──────┬───────┘
                           ▼
              jig/**/*.md  +  jig/generated/*.ndjson
```

### What the Query Layer Owns

| Function | Responsibility | Wraps |
|----------|---------------|-------|
| `config_to_graphs(config)` | Build the `graphs: dict[str, Path]` that `resolve_identifier` and `traverse_graph` require | Replaces inline construction at `context.py:634-641` |
| `query_node(identifier, config)` | Resolve + traverse + graceful degradation (`IdentifierError` → `{}`) | `resolve_identifier()` + `traverse_graph()` + `format_response()` |
| `search_docs(query, config, limit)` | Text search across JIG markdown corpus | New capability — no existing function to wrap |
| `query_overview(config)` | Project summary (re-export of `build_overview`) | `build_overview()` from `overview.py` (already pure) |
| `query_validate(config, scope)` | Run validation engine + scope filtering | `validate()` + extracted `_filter_errors_by_specs()` + scope spec sets |

### What Each Surface Owns

| Concern | CLI | MCP |
|---------|-----|-----|
| **Transport** | Terminal stdin/stdout | MCP stdio (JSON-RPC) |
| **Lifecycle** | One-shot (run and exit) | Long-lived server process |
| **Output formatting** | human/json/markdown flags (S-093) | Always structured dict (JSON-like) |
| **Error signaling** | Exit codes (0/1/2) + stderr | Graceful degradation (empty results, never raise to LLM) |
| **Config loading** | Per invocation | Once at startup |
| **Dispatch** | Click command routing | MCP tool/resource dispatch |

### Key Invariant

The MCP server never resolves paths, constructs graph dicts, filters validation scopes, or handles `IdentifierError` itself. It delegates all of this to `jig.query`. The CLI does the same. If JIG's layout changes, query logic changes, or new identifier types are added, both surfaces get it for free.

### Relationship to A-002 (CLI Command Architecture)

`jigy mcp` is architecturally different from other CLI commands:
- Not verb-first (it's a **transport mode**, not a user action)
- Not one-shot (long-lived server process)
- Not human-facing (machine consumer)
- No output format flags (MCP protocol handles serialization)

Therefore `jigy mcp` does not belong in A-002's command contract. MCP is a distinct surface that warrants its own architecture document: **A-005 MCP Server Architecture**. A-005 documents the MCP surface contract (tool naming, graceful degradation, read-only invariant) parallel to how A-002 documents the CLI surface contract. The shared query layer connects them.

---

## Proposed Changes

### WU1: Architecture Document A-005

File: `jig/architecture/A-005_MCP_Server_Architecture.md` (new)

Create the architecture document that governs the MCP surface. Parallel to A-002 (CLI), this document establishes:

- **Surface contract** — tool names, parameter schemas, return shapes
- **Read-only invariant** — no mutation tools; MCP is a pure observer
- **Graceful degradation contract** — missing data → empty results, never errors to LLM
- **Transport** — stdio only (matches Claude Code integration)
- **Tool naming convention** — JIG's native vocabulary (`lookup_node`, not `lookup_jig`)
- **Relationship to CLI** — both surfaces delegate to the shared query layer; behavioral parity is the invariant

Goals: G-001, G-002, G-004, G-005.

This document must exist before implementation begins. Per A-002: "New commands SHALL be documented before implementation." While `jigy mcp` lives outside A-002's contract, the principle applies: architecture first, code second.

### WU2: Shared Query Layer

File: `src/jig/query/__init__.py` (new), `src/jig/query/node.py` (new), `src/jig/query/search.py` (new), `src/jig/query/validate.py` (new)

Extract query logic from CLI into a shared layer that both CLI and MCP import. This is the central structural change of the scope.

**`query/__init__.py`** — public API:
```python
from jig.query.node import query_node, config_to_graphs
from jig.query.search import search_docs
from jig.query.validate import query_validate
from jig.cli.overview import build_overview as query_overview
```

**`query/node.py`** — identifier resolution + traversal:
```python
def config_to_graphs(config: JigConfig) -> dict[str, Path]:
    """Build graphs dict from config. Single source of truth for graph path construction."""
    generated = config.paths.generated
    return {
        "intent": generated / "intent-graph.ndjson",
        "impl": generated / "implementation-graph.ndjson",
        "verify": generated / "verification-graph.ndjson",
        "project_root": config.project_root,
    }

def query_node(identifier: str, config: JigConfig, max_nodes: int = 50) -> dict:
    """Resolve identifier and traverse graph. Returns {} on not-found (graceful degradation)."""
    # Wraps resolve_identifier + traverse_graph + format_response
    # Catches IdentifierError → returns {}
```

**`query/search.py`** — text search (new capability):
```python
def search_docs(query: str, config: JigConfig, limit: int = 20) -> list[dict]:
    """Case-insensitive text search across JIG markdown corpus.

    Returns [{id, title, path, match}] where match is first matching line.
    Empty query → []. No matches → [].
    """
```

Walks `config.paths.specifications`, `config.paths.outcomes`, `config.paths.architecture`, `config.paths.charter`. Uses `JigConfig.paths` exclusively — never hardcodes directory layout. Extracts frontmatter `id` and `title` from matches.

**`query/validate.py`** — validation with scope filtering:
```python
# Scope spec sets — extracted from cli/validate.py, now shared
INTENT_SPECS = {"S-018", "S-019", "S-020", "S-042", "S-043", "S-072", "S-079", "S-095"}
BRICK_SPECS = {"S-021", "S-022", "S-035", "S-036", "S-037", "S-038", "S-039", "S-086", "S-087", "S-088", "S-089"}

def filter_errors_by_specs(result: dict, spec_ids: set[str]) -> dict:
    """Filter validation result to only include errors for specific specs."""
    # Extracted from cli/validate.py _filter_errors_by_specs (now public)

def query_validate(config: JigConfig, scope: str = "full") -> dict:
    """Run validation engine and apply scope filtering.

    Scope: "intent" | "bricks" | "full"
    Returns {errors, summary, counts}.
    """
```

### WU3: Refactor CLI to Use Query Layer

Files: `src/jig/cli/context.py` (modify), `src/jig/cli/validate.py` (modify)

Refactor existing CLI commands to import from `jig.query` instead of inlining query logic. **No behavioral change** — CLI output is identical before and after. This is a pure refactor.

Changes in `context.py`:
- Replace inline graph dict construction (L634-641) with `config_to_graphs(config)`
- Replace `resolve_identifier` + `traverse_graph` + `IdentifierError` catch with `query_node(identifier, config)`
- `build_overview` import stays the same (already used via `jig.cli.overview`, re-exported by query layer)

Changes in `validate.py`:
- Replace hardcoded `intent_specs` and `brick_specs` sets with imports from `jig.query.validate`
- Replace `_filter_errors_by_specs()` with import from `jig.query.validate.filter_errors_by_specs()`
- Validation commands call `query_validate(config, scope)` instead of `validate(config.project_root)` + inline filtering

**This WU is the firewall against divergence.** After this, both CLI and MCP call the same query functions. Neither surface owns business logic.

### WU4: Add MCP SDK Dependency

File: `pyproject.toml`

Add `fastmcp` as an optional dependency group so projects not using MCP don't pay the install cost.

```toml
[project.optional-dependencies]
mcp = ["fastmcp>=2.0.0"]
```

Using `fastmcp` (not raw `mcp` SDK) for the cleaner decorator API — same choice ASE made, proven in production.

### WU5: MCP Server Module

File: `src/jig/mcp/server.py` (new), `src/jig/mcp/__init__.py` (new)

FastMCP server instance with stdio transport. Thin decorators over `jig.query` functions — no business logic in this module.

**Tools exposed:**

| Tool | Parameters | Delegates to | Notes |
|------|-----------|-------------|-------|
| `lookup_node` | `node_id: str` | `query_node()` | Returns content + frontmatter + graph neighbors. Full identifier support: S/A/O/G/B/F/T/Charter/file paths. |
| `search_docs` | `query: str, limit: int = 20` | `search_docs()` | Case-insensitive substring. Returns `[{id, title, match}]`. |
| `get_overview` | *(none)* | `query_overview()` | Project summary: goals, spec counts, bricks, coverage. |
| `validate_project` | `scope: str = "full"` | `query_validate()` | Validation results. Scope: "intent", "bricks", "full". Read-only. |

**Design notes:**
- `lookup_node` replaces ASE's `lookup_jig`. Named `lookup_node` because JIG's abstraction is nodes, not "jig docs".
- `search_docs` replaces ASE's `search_jig`.
- `get_overview` wraps `query_overview()` (which wraps `build_overview()`).
- `validate_project` wraps `query_validate()`. Agents can check if specs/code/tests are aligned without running CLI.
- **No MCP resources in v1.** Resources duplicate tool functionality with a different access pattern. Defer until there's a demonstrated need. Can be added later without breaking changes.

### WU6: CLI Command Registration

File: `src/jig/cli/main.py`

Add `mcp` command to Click group:

```python
@cli.command()
def mcp():
    """Start MCP server (stdio transport) for LLM agent access."""
    from jig.mcp.server import run_server
    run_server()
```

Update `OrderedGroup.COMMAND_ORDER` to include `"mcp"`.

Note: `jigy mcp` is a transport mode, not a verb-first query command. It starts a long-lived server process. This is documented in A-005 as architecturally distinct from other CLI commands.

### WU7: Tests

**Query layer tests:** `tests/jig/query/test_node.py`, `tests/jig/query/test_search.py`, `tests/jig/query/test_validate.py` (new)

Test the query layer directly. These are the primary behavioral tests.

Coverage:
- `query_node` with each identifier type (S-###, A-###, O-###, G-#, Charter, B-*, F-*, T-*)
- `query_node` with missing identifier → `{}`
- `query_node` graph neighbors present when graphs exist
- `query_node` graph neighbors absent when graphs missing (graceful degradation)
- `config_to_graphs` produces correct paths from config
- `search_docs` with matches, no matches, empty query
- `query_validate` for each scope value ("intent", "bricks", "full")
- `filter_errors_by_specs` filters correctly
- All tests use `tmp_path` fixtures with synthetic JIG layouts via `JigConfig`

**MCP server tests:** `tests/jig/mcp/test_server.py` (new)

Thin integration tests verifying MCP wrappers call query layer correctly. Not duplicating query layer test coverage — just confirming the wiring.

**CLI regression tests:** Verify that refactored CLI commands (WU3) produce identical output to pre-refactor. Existing tests should pass unchanged; if any need updating, that indicates an accidental behavioral change.

### WU8: Configuration for Consumers

File: `.mcp.json` template (documentation, not shipped)

Document how consuming projects configure their `.mcp.json`:

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

After JIG ships MCP, ASE's `.mcp.json` adds a `jig` server entry and ASE's `server.py` drops `lookup_jig_tool`, `search_jig_tool`, `lookup_jig()`, `search_jig()`, `get_jig_doc()`, `_resolve_jig_file()`, `_doc_kind()`, and the `ase://jig/{doc_id}` resource.

---

## Dependency Graph

```
WU1 (A-005 architecture doc)
 │
 └──► WU2 (query layer) ──► WU3 (CLI refactor) ──► WU7 (tests: CLI regression)
       │                                              │
       ├──► WU4 (mcp dependency)                      │
       │     │                                        │
       │     └──► WU5 (MCP server) ──► WU6 (CLI reg) │
       │                    │                         │
       │                    └────────► WU7 (tests: query + MCP)
       │
       └──► WU7 (tests: query layer)
                    │
                    └──► WU8 (consumer config docs)
```

Critical path: WU1 → WU2 → WU3 + WU5 → WU7

WU2 (query layer) is the keystone. WU3 (CLI refactor) and WU5 (MCP server) can proceed in parallel after WU2, since both depend only on the query layer interface. WU7 tests all three layers. WU8 is documentation only.

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Shared query layer | `src/jig/query/` module | CLI and MCP are surfaces, not behavior owners. Single source of truth prevents accidental divergence. |
| CLI refactor first | WU3 before WU5 | Proves the query layer works by demonstrating behavioral parity with existing CLI. If refactored CLI tests pass, the abstraction is correct. |
| Architecture doc first | WU1 before code | Per A-002's principle: architecture before implementation. A-005 governs MCP surface contract. |
| Optional dependency | `[project.optional-dependencies] mcp = [...]` | Not all JIG users need MCP. Don't bloat base install. |
| `fastmcp` over raw `mcp` SDK | `fastmcp>=2.0.0` | Cleaner decorator API. Same choice ASE made, proven in production. |
| Transport | stdio | Matches Claude Code integration. Same as ASE's proven approach. |
| Config-driven paths | All file access via `JigConfig.paths`, mediated by `config_to_graphs()` | Never hardcode directory layout. Respects `jig.toml` overrides. One function owns the config→paths translation. |
| Graph-level abstraction | Use `resolve_identifier` + `traverse_graph` via query layer | Not filesystem globbing. Supports full identifier vocabulary (S/A/O/G/B/F/T/Charter/paths). |
| Tool naming | `lookup_node`, not `lookup_jig` | MCP tools should use JIG's native vocabulary. Agents interact with "nodes", not "jig docs". |
| Read-only | No mutation tools | Proven pattern from ASE. Mutation (creating specs, running mend) is a separate, later concern. |
| Graceful degradation | Missing files/graphs → empty results | Proven pattern from ASE. Never raise to the LLM on missing data. Owned by query layer, not surface. |
| No MCP resources in v1 | Defer `jig://` resources | Resources duplicate tool functionality. Add when demonstrated need exists. No breaking change to add later. |
| Search in query layer | `src/jig/query/search.py`, not `src/jig/mcp/search.py` | Search is a JIG capability, not an MCP concern. Available to both surfaces. Future `jigy search` CLI command imports from same module. |
| Validation scope filtering extracted | `INTENT_SPECS`, `BRICK_SPECS`, `filter_errors_by_specs()` in `query/validate.py` | Currently private to `cli/validate.py`. Both surfaces need it. Single definition prevents drift. |

---

## Success Criteria

- [ ] A-005 architecture document exists and governs MCP surface contract
- [ ] `jig.query` module exists with `query_node`, `search_docs`, `query_overview`, `query_validate`
- [ ] CLI commands (`jigy context`, `jigy validate`) delegate to `jig.query` — no inline query logic
- [ ] Existing CLI tests pass unchanged after refactor (behavioral parity proven)
- [ ] `jigy mcp` starts MCP server with stdio transport
- [ ] `lookup_node("S-042")` returns content, frontmatter, and graph neighbors
- [ ] `lookup_node("B-ank")` works (brick identifiers — not supported by ASE's version)
- [ ] `lookup_node("F-some_function")` works (function identifiers — not supported by ASE's version)
- [ ] `lookup_node("S-999")` returns `{}` (graceful degradation)
- [ ] `search_docs("convergence")` returns matching docs with context snippets
- [ ] `get_overview()` returns project summary matching `jigy context` output
- [ ] `validate_project("intent")` returns same errors as `jigy validate intent -j`
- [ ] All paths resolved through `JigConfig`, not hardcoded
- [ ] Works with non-default `jig.toml` path configuration
- [ ] Missing graph files don't cause errors (graceful degradation)
- [ ] Claude Code can connect via `.mcp.json` and use all tools

---

## Out of Scope

- **Mutation tools** (creating specs, running mend, rebuilding graphs) — Read-only first. Mutation requires careful design around confirmation and side effects.
- **MCP resources** (`jig://` URIs) — Defer to v2. Tools cover all query needs. Resources can be added without breaking changes.
- **Live file watching / notifications** — MCP 2.0 feature. Historical queries only.
- **SSE transport** — stdio is sufficient for local Claude Code. SSE adds port management complexity.
- **Full graph NDJSON export** — Exposing raw graph data is low value vs. structured traversal. Agents don't need to parse NDJSON.
- **ASE-side cleanup** — Removing JIG tools from ASE's MCP server is ASE's concern, not JIG's. Document the migration path in WU8 but don't couple the work.
- **`jigy search` CLI command** — Natural follow-on. The `search_docs()` function in `jig.query` is designed for this, but CLI surface registration is separate scope.
- **`jigy context` refactor beyond query delegation** — WU3 changes the internal delegation, not the external contract. Context command modes (bare/traversal/fallback per S-110) are unchanged.

---

## Related Documents

- A-002 `jig/architecture/A-002_CLI_Command_Architecture.md` — CLI surface contract (parallel to A-005)
- A-005 `jig/architecture/A-005_MCP_Server_Architecture.md` — MCP surface contract (created by WU1)
- ASE F270 — `dig/wip/F270_SCOPE_MCP_Server_Option_A.md` — Original MCP scope in ASE
- ASE F273 — Implementation journal for ASE's MCP server
- ASE `src/ase/mcp/server.py` — Current implementation with JIG tools to be replaced
- JIG `src/jig/cli/context.py` — `resolve_identifier()`, `traverse_graph()` — wrapped by query layer
- JIG `src/jig/cli/overview.py` — `build_overview()` — re-exported by query layer
- JIG `src/jig/cli/validate.py` — `_filter_errors_by_specs()`, scope spec sets — extracted to query layer
- JIG `src/jig/validation/engine.py` — `validate()` — wrapped by `query_validate()`
- JIG `src/jig/config/schema.py` — `JigConfig`, `load_config()` — path resolution
- JIG `jig/Charter_JIG.md` — Goals G-001, G-002, G-004, G-005 served by this scope

---

**End of Scope**
