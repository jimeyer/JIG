---
type: plan
title: "JIG MCP Server"
status: active
created: 1739750400
created_human: "2026-02-16"
parent: E031
children: []
---

# PLAN: JIG MCP Server

- **SCOPE**: dig/wip/E030_SCOPE_MCP_Server.md
- **JIGPLAN**: dig/wip/E031_JIGPLAN_MCP_Server.md
- **Start**: 2026-02-16
- **Status**: Draft
- **Branch**: mcp

---

## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- B-decorators (Layer 0)
- B-validation (Layer 0) — consumed, not modified
- B-config (Layer 0) — consumed, not modified
- B-impl-graph (Layer 0)
- B-intent-graph (Layer 0)
- B-hashing (Layer 0)
- B-languages (Layer 0)
- B-staleness (Layer 0)
- B-templates (Layer 0)
- B-init (Layer 0)
- B-rules (Layer 0)
- B-mend (Layer 0)
- B-verification-graph (Layer 1)
- B-audit (Layer 1)

**Layer Constraints:**
- B-query at Layer 0 (MUST NOT depend on any Layer 1 brick)
- B-mcp-server at Layer 1 (depends on B-query, B-config)
- B-cli at Layer 1 (depends on B-query, existing Layer 0 deps)
- No upward dependencies, no same-layer dependencies

**Clean Break:**
- No compatibility shims
- Functions move from cli/ to query/ with re-imports in cli/ for backwards compat
- No legacy code to delete (this is additive + refactor)

---

## Key Existing Code References

| Concern | Location | Notes |
|---------|----------|-------|
| IdentifierError | src/jig/cli/context.py:47-50 | Moves to query/node.py |
| PATTERNS dict | src/jig/cli/context.py:22-31 | Moves to query/node.py |
| VALID_PATTERNS | src/jig/cli/context.py:34-44 | Moves to query/node.py |
| _load_graph | src/jig/cli/context.py:53-74 | Moves to query/node.py |
| _load_all_graphs | src/jig/cli/context.py:77-89 | Moves to query/node.py |
| _match_pattern | src/jig/cli/context.py:92-101 | Moves to query/node.py |
| resolve_identifier | src/jig/cli/context.py:104-162 | @jig.implements("S-111"), moves to query/node.py |
| EDGE_DIRECTIONS | src/jig/cli/context.py:169-176 | Moves to query/node.py |
| _build_adjacency | src/jig/cli/context.py:179-208 | Moves to query/node.py |
| _collect_ancestors | src/jig/cli/context.py:211-236 | Moves to query/node.py |
| _collect_descendants_breadth_first | src/jig/cli/context.py:239-301 | Moves to query/node.py |
| traverse_graph | src/jig/cli/context.py:304-362 | @jig.implements("S-112"), moves to query/node.py |
| EDGE_TO_PARENT | src/jig/cli/context.py:366-374 | Moves to query/node.py |
| _compute_depths | src/jig/cli/context.py:377-415 | Moves to query/node.py |
| _get_edge_type_for_node | src/jig/cli/context.py:418-463 | Moves to query/node.py |
| format_response | src/jig/cli/context.py:466-525 | @jig.implements("S-113"), moves to query/node.py |
| format_human | src/jig/cli/context.py:528-558 | Undecorated, moves to query/node.py |
| format_markdown | src/jig/cli/context.py:561-597 | Undecorated, moves to query/node.py |
| context_command | src/jig/cli/context.py:600-690 | @jig.implements("S-110"), STAYS in cli/ |
| _load_yaml_frontmatter | src/jig/cli/overview.py:18-29 | Moves to query/overview.py |
| _load_bricks | src/jig/cli/overview.py:32-47 | Moves to query/overview.py |
| _load_graph (overview) | src/jig/cli/overview.py:50-71 | Moves to query/overview.py |
| build_overview | src/jig/cli/overview.py:74-228 | @jig.implements("S-114"), moves to query/overview.py |
| format_overview_human | src/jig/cli/overview.py:231-274 | @jig.implements("S-114"), moves to query/overview.py |
| format_overview_json | src/jig/cli/overview.py:277-280 | @jig.implements("S-114"), moves to query/overview.py |
| format_overview_markdown | src/jig/cli/overview.py:283-353 | @jig.implements("S-114"), moves to query/overview.py |
| show_overview | src/jig/cli/overview.py:356-397 | @jig.implements("S-114"), STAYS in cli/ |
| _filter_errors_by_specs | src/jig/cli/validate.py:185-204 | Moves to query/validate.py (renamed public) |
| intent_specs set | src/jig/cli/validate.py:236 | Extracted to query/validate.py as INTENT_SPECS |
| brick_specs set | src/jig/cli/validate.py:296 | Extracted to query/validate.py as BRICK_SPECS |
| COMMAND_ORDER | src/jig/cli/main.py:16 | Add "mcp" after "context" |
| overview.py imports click | src/jig/cli/overview.py:10 | Only used by show_overview — no issue for move |
| overview.py imports OutputFormat | src/jig/cli/overview.py:14 | Only used by show_overview — no issue for move |

---

## Execution Order

```
WU1 (query/node.py) ──┐
                       ├── WU3 (CLI refactor) ── WU5 (bricks + validation)
WU2 (query/overview,   │                              │
     validate, search) ┘                               │
                                                       │
WU4 (MCP server) ─── depends on WU1+WU2 ───── WU5 ── WU6 (scope validation)
```

WU1 and WU2 can execute in parallel (independent modules).
WU3 depends on WU1+WU2 (CLI needs query layer to delegate to).
WU4 depends on WU1+WU2 (MCP server wraps query layer).
WU3 and WU4 can execute in parallel.
WU5 depends on WU1-WU4 (bricks need all modules to exist).
WU6 depends on WU5 (scope validation needs everything wired).

---

## Test Strategy

- **New tests**: `tests/jig/query/test_node.py`, `tests/jig/query/test_search.py`, `tests/jig/query/test_validate.py`, `tests/jig/mcp/test_server.py`
- **Existing tests that MUST pass unchanged**:
  - `tests/cli/test_context.py`
  - `tests/cli/test_context_integration.py`
  - `tests/cli/test_overview.py`
  - `tests/cli/test_validate.py`
  - `tests/cli/test_validate_integration.py`
  - `tests/integration/test_validate_mend_cycle.py`
- **Deleted tests**: None (additive work)

---

## Work Unit Checklist

- [ ] WU1: Query layer — node resolution and traversal — tests ☐ / code ☐
- [ ] WU2: Query layer — overview, validate, search — tests ☐ / code ☐
- [ ] WU3: CLI refactor to use query layer — existing tests pass ☐ / code ☐
- [ ] WU4: MCP server — tests ☐ / code ☐
- [ ] WU5: Bricks update and project validation — bricks ☐ / validate ☐
- [ ] WU6: Scope validation — SCOPE verified ☐

---

## Work Units

### Work Unit 1: Query Layer — Node Resolution and Traversal

**Goal**: Create `jig.query.node` module by moving identifier resolution, graph traversal, and response formatting from `cli/context.py`. Add `config_to_graphs()` and `query_node()` wrappers.

**Specs Addressed**: S-111 (resolve_identifier), S-112 (traverse_graph), S-113 (format_response) — all MOVE

**Acceptance Criteria**:
- [ ] `src/jig/query/__init__.py` exists with public API exports
- [ ] `src/jig/query/node.py` contains all moved functions with decorators intact
- [ ] `config_to_graphs(config)` builds graphs dict from `JigConfig.paths.generated`
- [ ] `query_node(identifier, config)` returns node+neighbors dict or `{}` on not-found
- [ ] `query_node` catches `IdentifierError` → returns `{}`
- [ ] `query_node` with valid identifier returns same structure as `format_response(traverse_graph(...))`
- [ ] Tests with `@jig.verifies` decorators for `query_node` and `config_to_graphs`
- [ ] `jigy rebuild && jigy validate` passes

**Success Gates** (all must pass):
- [ ] `pytest tests/jig/query/test_node.py -v` passes
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors: `ruff check src/jig/query/`

**Escalation Triggers** (stop and ask human if):
- Import cycle between query/ and cli/ detected
- resolve_identifier or traverse_graph depend on cli-specific code not visible in current analysis
- Test failures persist after 2 retry attempts
- FORBIDDEN brick modification needed

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| Lines 22-597 correct boundary? | Yes, ends at return of format_markdown; lines 598-599 blank, 600 starts context_command | context.py:595-600 |
| Does query/node.py need json import? | Yes, already in moved code (line 13 of current context.py) | context.py:13 |
| Will context_command work after move? | Yes — imports traverse_graph, format_response, IdentifierError etc. from query/ | context.py:627-690 |
| Any hidden CLI dependencies in moved code? | No — moved code uses only json, re, deque, Path, typing, jig decorators | context.py:11-19 |

**Implementation Notes**:
- Files: `src/jig/query/__init__.py` (new), `src/jig/query/node.py` (new)
- Move lines 22-597 from `cli/context.py` to `query/node.py`
- Keep module imports: `json`, `re`, `collections.deque`, `pathlib.Path`, `typing.Any`, `jig` (decorators)
- Add at top of `query/node.py`:
  ```python
  from jig.config import JigConfig
  ```
- Add `config_to_graphs()`: builds `{"intent": ..., "impl": ..., "verify": ..., "project_root": ...}` from config
- Add `query_node()`: calls `config_to_graphs` → `traverse_graph` → `format_response`, catches `IdentifierError` → `{}`
- `__init__.py` exports: `query_node`, `config_to_graphs`, `resolve_identifier`, `traverse_graph`, `format_response`, `IdentifierError`
- TDD: write tests for `query_node` and `config_to_graphs` first

**Human Verification**:
```bash
pytest tests/jig/query/test_node.py -v
python -c "from jig.query.node import query_node, config_to_graphs; print('OK')"
```

---

### Work Unit 2: Query Layer — Overview, Validate, Search

**Goal**: Create remaining query layer modules: move overview functions, extract validation filtering, implement text search.

**Specs Addressed**: S-114 (build_overview — MOVE), S-116 (search_docs — CREATE), S-023/S-024/S-025 (validation filtering — EXTRACT)

**Acceptance Criteria**:
- [ ] `src/jig/query/overview.py` contains `build_overview` + all `format_overview_*` functions with decorators intact
- [ ] `src/jig/query/validate.py` contains `INTENT_SPECS`, `BRICK_SPECS`, `filter_errors_by_specs()`, `query_validate()`
- [ ] `src/jig/query/search.py` contains `search_docs()`
- [ ] `query_validate(config, "intent")` returns same filtered result as CLI intent validation
- [ ] `query_validate(config, "bricks")` returns same filtered result as CLI brick validation
- [ ] `query_validate(config, "full")` returns unfiltered result
- [ ] `search_docs("", config)` returns `[]`
- [ ] `search_docs("nonexistent", config)` returns `[]`
- [ ] `search_docs` with matching query returns `[{id, title, path, match}]`
- [ ] `search_docs` respects `limit` parameter
- [ ] `query_validate` does NOT call `ensure_graphs_current` — assumes graphs are current (auto-rebuild is a surface concern)
- [ ] `search_docs` searches specs, outcomes, architecture, charter via `config.paths`
- [ ] Tests with `@jig.verifies` decorators
- [ ] `__init__.py` updated with all exports

**Success Gates** (all must pass):
- [ ] `pytest tests/jig/query/test_search.py tests/jig/query/test_validate.py -v` passes
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No modifications to FORBIDDEN bricks

**Escalation Triggers** (stop and ask human if):
- `build_overview` depends on `click` or `OutputFormat` at runtime (not just import)
- Validation engine API doesn't match expected `validate(project_root) → dict`
- Test failures persist after 2 retry attempts

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| Does build_overview use click/OutputFormat? | No — only show_overview uses them (stays in cli/) | overview.py:10,14,359 |
| Validation engine signature? | `validate(project_root: Path) -> dict[str, Any]` with `{errors, summary}` | validation/engine.py:22 |
| Should query_validate call ensure_graphs_current? | No — auto-rebuild is a surface concern, not query layer | validate.py:230,275 |
| Overview lines 18-353 correct boundary? | Yes — line 353 ends format_overview_markdown, line 356 starts show_overview | overview.py:353-356 |

**Implementation Notes**:
- Files: `src/jig/query/overview.py` (new), `src/jig/query/validate.py` (new), `src/jig/query/search.py` (new)
- **overview.py**: Move lines 18-353 from `cli/overview.py`. Imports needed: `json`, `re`, `defaultdict`, `Path`, `Any`, `yaml`, `jig`, `jig.config.JigConfig`. Do NOT import `click` or `OutputFormat`.
- **validate.py**: Extract `_filter_errors_by_specs` from `cli/validate.py:185-204`, rename to `filter_errors_by_specs` (public). Extract spec sets from lines 236 and 296 as `INTENT_SPECS` and `BRICK_SPECS`. Add `query_validate(config, scope)` that calls `validate(config.project_root)` then filters by scope.
- **search.py**: Implement `search_docs(query, config, limit=20)`. Walk `config.paths.specifications`, `config.paths.outcomes`, `config.paths.architecture`, `config.paths.charter`. For each `.md` file: case-insensitive substring match. Extract frontmatter `id` and `title`. Return first matching line as `match` field. Cap at `limit`.
- Update `__init__.py` with exports: `search_docs`, `query_validate`, `filter_errors_by_specs`, `INTENT_SPECS`, `BRICK_SPECS`, `build_overview`, `format_overview_human`, `format_overview_json`, `format_overview_markdown`
- TDD: write search tests first (new capability), then validate tests

**Human Verification**:
```bash
pytest tests/jig/query/ -v
python -c "from jig.query import search_docs, query_validate, build_overview; print('OK')"
```

---

### Work Unit 3: CLI Refactor to Use Query Layer

**Goal**: Refactor CLI command handlers to delegate to `jig.query` instead of owning query logic. Existing CLI tests must pass unchanged.

**Specs Addressed**: S-110 (context_command — unchanged behavior), S-023/S-024/S-025 (validation — unchanged behavior)

**Acceptance Criteria**:
- [ ] `cli/context.py` imports from `jig.query.node` and delegates to `query_node` or uses `config_to_graphs`
- [ ] `cli/context.py` re-exports `resolve_identifier`, `traverse_graph`, `IdentifierError` etc. for backwards compat
- [ ] `cli/overview.py` imports from `jig.query.overview` and delegates
- [ ] `cli/overview.py` re-exports `build_overview`, `format_overview_*` for backwards compat
- [ ] `cli/validate.py` imports `INTENT_SPECS`, `BRICK_SPECS`, `filter_errors_by_specs` from `jig.query.validate`
- [ ] ALL existing CLI tests pass without modification
- [ ] `jigy context` produces identical output (bare, traversal, and fallback modes)
- [ ] `jigy validate intent` / `jigy validate bricks` / `jigy validate` produce identical output

**Success Gates** (all must pass):
- [ ] `pytest tests/cli/test_context.py tests/cli/test_context_integration.py -v` passes
- [ ] `pytest tests/cli/test_overview.py -v` passes
- [ ] `pytest tests/cli/test_validate.py tests/cli/test_validate_integration.py -v` passes
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No modifications to FORBIDDEN bricks

**Escalation Triggers** (stop and ask human if):
- Existing CLI test fails (indicates behavioral change — must investigate before proceeding)
- Import cycle between cli/ and query/
- context_command behavior changes (fallback mode, output formatting)

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| context_command graph dict building | Replace lines 634-641 with `config_to_graphs(config)` from query/ | context.py:634-641 |
| context.py needs json after refactor? | Yes — `json.dumps()` at line 663 in context_command | context.py:663 |
| context_command uses IdentifierError? | Yes — catch at line 671. Must import from query/node | context.py:671 |
| Are PATTERNS/VALID_PATTERNS used externally? | No — only used by resolve_identifier. Re-export for safety. | grep shows no external imports |

**Implementation Notes**:
- Files: `src/jig/cli/context.py` (modify), `src/jig/cli/overview.py` (modify), `src/jig/cli/validate.py` (modify)
- **context.py refactor**: Replace lines 22-597 (moved code) with imports from `jig.query.node`. Keep `context_command()` (lines 600-690). Add re-export block:
  ```python
  # Re-exports for backwards compatibility
  from jig.query.node import (
      IdentifierError, PATTERNS, VALID_PATTERNS,
      resolve_identifier, traverse_graph, format_response,
      format_human, format_markdown,
      _load_graph, _load_all_graphs,
  )
  ```
- **overview.py refactor**: Replace lines 18-353 (moved code) with imports from `jig.query.overview`. Keep `show_overview()` (lines 356-397). Add re-export block.
- **validate.py refactor**: Replace inline `intent_specs`, `brick_specs`, `_filter_errors_by_specs` with imports from `jig.query.validate`.
- **Critical**: Run existing tests BEFORE and AFTER to prove behavioral parity.
- **Critical**: `context_command` currently builds graphs dict inline at lines 634-641. Replace with `config_to_graphs(config)` import from query layer.
- **Critical**: After refactor, `context.py` still needs `import json` at top — `context_command` calls `json.dumps()` at line 663.

**Human Verification**:
```bash
# Run ALL existing CLI tests
pytest tests/cli/ -v
# Spot-check CLI output
jigy context
jigy context S-001
jigy validate intent
```

---

### Work Unit 4: MCP Server

**Goal**: Create MCP server module with four tools (lookup_node, search_docs, get_overview, validate_project) and register `jigy mcp` CLI command.

**Specs Addressed**: S-117

**Acceptance Criteria**:
- [ ] `fastmcp>=2.0.0` added as optional dependency in `pyproject.toml` under `[project.optional-dependencies] mcp = [...]`
- [ ] `src/jig/mcp/__init__.py` and `src/jig/mcp/server.py` exist
- [ ] `server.py` creates FastMCP instance with stdio transport
- [ ] `lookup_node(node_id)` tool delegates to `query_node()` — returns dict or `{}`
- [ ] `search_docs(query, limit=20)` tool delegates to `search_docs()` — returns list
- [ ] `get_overview()` tool delegates to `build_overview()` — returns dict
- [ ] `validate_project(scope="full")` tool delegates to `query_validate()` — returns dict
- [ ] `run_server()` function starts the MCP server
- [ ] `jigy mcp` command registered in `cli/main.py`
- [ ] `COMMAND_ORDER` updated to include `"mcp"`
- [ ] All tools are read-only
- [ ] Code with `@jig.implements("S-117")` decorator
- [ ] Tests with `@jig.verifies("S-117")` decorators

**Success Gates** (all must pass):
- [ ] `pytest tests/jig/mcp/test_server.py -v` passes
- [ ] `jigy mcp --help` shows command (doesn't error)
- [ ] `jigy rebuild && jigy validate` passes
- [ ] No modifications to FORBIDDEN bricks

**Escalation Triggers** (stop and ask human if):
- `fastmcp` API doesn't match expected decorator patterns
- stdio transport doesn't work with simple test client
- Import of `jig.mcp.server` fails when `fastmcp` not installed (optional dependency must be handled gracefully)
- Test failures persist after 2 retry attempts

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| FastMCP decorator syntax? | `@mcp.tool` or `@mcp.tool()` — both work | PyPI fastmcp docs |
| Where to add optional dep? | pyproject.toml line 33, existing `[project.optional-dependencies]` section | pyproject.toml:33 |
| COMMAND_ORDER location? | main.py:16, insert "mcp" after "context" | main.py:16 |
| Lazy import needed? | Yes — `from jig.mcp.server import run_server` inside CLI handler to avoid ImportError when fastmcp not installed | main.py pattern |

**Implementation Notes**:
- Files: `pyproject.toml` (modify), `src/jig/mcp/__init__.py` (new), `src/jig/mcp/server.py` (new), `src/jig/cli/main.py` (modify)
- **pyproject.toml**: Add `[project.optional-dependencies]` section: `mcp = ["fastmcp>=2.0.0"]`
- **server.py** structure:
  ```python
  from fastmcp import FastMCP
  from jig.config import load_config
  from jig.query import query_node, search_docs, build_overview, query_validate

  mcp = FastMCP(name="jig")

  @mcp.tool
  def lookup_node(node_id: str) -> dict: ...

  @mcp.tool
  def search_docs(query: str, limit: int = 20) -> list: ...

  @mcp.tool
  def get_overview() -> dict: ...

  @mcp.tool
  def validate_project(scope: str = "full") -> dict: ...

  def run_server():
      mcp.run()
  ```
- **main.py**: Add `mcp` to `COMMAND_ORDER`. Add command:
  ```python
  @cli.command()
  def mcp():
      """Start MCP server (stdio transport) for LLM agent access."""
      from jig.mcp.server import run_server
      run_server()
  ```
- **Lazy import**: `from jig.mcp.server import run_server` inside command handler to avoid import error when fastmcp not installed
- **Tests**: Test core functions (query layer calls), not MCP protocol. Use `tmp_path` fixtures with synthetic JIG layout.
- Install fastmcp first: `pip install -e ".[mcp]"`

**Human Verification**:
```bash
pip install -e ".[mcp]"
pytest tests/jig/mcp/test_server.py -v
jigy mcp --help
```

---

### Work Unit 5: Bricks Update and Project Validation

**Goal**: Register new bricks in `bricks.yaml`, run full JIG validation to confirm layer structure and partition.

**Specs Addressed**: (none — infrastructure)

**Acceptance Criteria**:
- [ ] `bricks.yaml` contains `B-query` (Layer 0) with units: M-jig.query, M-jig.query.node, M-jig.query.search, M-jig.query.validate, M-jig.query.overview
- [ ] `bricks.yaml` contains `B-mcp-server` (Layer 1) with units: M-jig.mcp, M-jig.mcp.server
- [ ] `jigy rebuild && jigy validate` passes (full validation)
- [ ] `jigy validate bricks` passes (partition valid, no layer violations)
- [ ] `jigy show layers` shows correct layer structure
- [ ] No functions orphaned (every function in a brick)

**Success Gates** (all must pass):
- [ ] `jigy rebuild && jigy validate` passes
- [ ] `jigy validate bricks` passes
- [ ] `pytest tests/ -v` — full test suite passes
- [ ] No modifications to FORBIDDEN bricks beyond bricks.yaml itself

**Escalation Triggers** (stop and ask human if):
- Layer violation detected (B-query depends on Layer 1)
- Partition violation (function in multiple bricks or no brick)
- Full test suite has failures unrelated to this work

**Resolved Context** (from pre-execution review):
| Question | Answer | Source |
|----------|--------|--------|
| All 6 test files exist? | Yes — verified by glob | tests/cli/, tests/integration/ |
| Brick ordering in bricks.yaml? | Layer 0 bricks first, then Layer 1. B-query goes with Layer 0 group. | bricks.yaml:1-135 |

**Implementation Notes**:
- Files: `jig/bricks.yaml` (modify)
- Add B-query brick BEFORE B-cli (since Layer 0):
  ```yaml
  - id: B-query
    name: Query Layer
    layer: 0
    units:
      - M-jig.query
      - M-jig.query.node
      - M-jig.query.search
      - M-jig.query.validate
      - M-jig.query.overview
  ```
- Add B-mcp-server brick after B-cli (Layer 1):
  ```yaml
  - id: B-mcp-server
    name: MCP Server
    layer: 1
    units:
      - M-jig.mcp
      - M-jig.mcp.server
  ```
- Run `jigy rebuild` to regenerate all graphs with new module locations
- Run `jigy validate` to check partition and layers
- Run `jigy validate bricks` specifically to verify no layer violations

**Human Verification**:
```bash
jigy rebuild && jigy validate
jigy validate bricks
jigy show layers
```

---

### Work Unit 6: Scope Validation

**Goal**: Verify SCOPE problem is solved at system boundary — Claude Code can connect to JIG MCP server and use all four tools.

**SCOPE Reference**:
"JIG should ship its own MCP server (`jigy mcp`) so any JIG-enabled project gets LLM-accessible traceability without project-specific wiring."

**Validation Approach**: Integration Test + Manual Checklist

**Verification Steps**:
```bash
# 1. Verify MCP server starts and responds
pip install -e ".[mcp]"
jigy mcp  # Should start without error (Ctrl-C to stop)

# 2. Run integration test that exercises all tools
pytest tests/jig/mcp/test_server.py -v

# 3. Verify .mcp.json template works
# Create temporary .mcp.json and verify jigy mcp is invocable

# 4. Run full validation
jigy rebuild && jigy validate

# 5. Verify all success criteria from SCOPE
```

**Expected Result**:
- `jigy mcp` starts stdio MCP server without error
- All four tools return structured data matching their contracts in A-005
- lookup_node resolves S-###, O-###, B-*, F-*, Charter (full vocabulary)
- lookup_node with unknown ID returns `{}`
- search_docs returns matching documents
- get_overview returns project summary
- validate_project returns validation results for each scope
- All paths resolved through JigConfig
- Missing graphs degrade gracefully

**Deliverable**:
- [ ] Integration test covers all tool contracts: `tests/jig/mcp/test_integration.py`
- [ ] Manual verification checklist completed (below)

**Manual Checklist**:
- [ ] `jigy mcp` starts without error
- [ ] `lookup_node("S-042")` returns content + frontmatter + neighbors
- [ ] `lookup_node("B-cli")` works (brick identifier)
- [ ] `lookup_node("S-999")` returns `{}`
- [ ] `search_docs("validation")` returns matches
- [ ] `get_overview()` returns charter, goals, spec counts
- [ ] `validate_project("intent")` returns same errors as `jigy validate intent -j`
- [ ] All tests pass: `pytest tests/ -v`
- [ ] JIG validation clean: `jigy rebuild && jigy validate`

**If Validation Fails**:
- Investigate root cause (likely wiring/integration gap)
- Fix the issue
- Add regression test
- Re-run validation

**Human Verification**:
```bash
pytest tests/ -v
jigy rebuild && jigy validate
```

---

## Execution Log

(Filled in by orchestrator during execution)

---

## Completion Summary

(Filled in after all WUs complete)

**Scope Delivered:**
- <to be filled>

**JIG Summary:**
- <to be filled>

**Clean Break Actions:**
- [ ] No deprecated O/S nodes to delete
- [ ] No legacy code to delete
- [ ] Final `jigy rebuild && jigy validate` passed

**Reflection Roll-Up:**
- Repeatable wins: <patterns that worked>
- Systemic frictions: <process issues>
- Open questions: <items for future work>
