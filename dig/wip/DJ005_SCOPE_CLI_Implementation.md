---
title: JIG DIG CLI Implementation Strategy
type: scope
status: active
created: 1736207400
created_human: 2026-01-06 15:30 CST
parent: "[[DJ002_SCOPE_CLI_Recommendations]]"
children: []
---
# JIG DIG CLI Implementation Strategy


## Executive Summary

This document defines the implementation strategy for aligning the JIG and DIG CLIs per the CLI Design Manifesto and Recommendations. Implementation proceeds in four phases, with JIG and DIG developed in parallel but independently.

**Key Principle:** Start simple. Rename existing commands and unify arguments first. New functionality comes later. Context Integration is the largest body of work and comes last.

```
Phase 0: Flag Unification          ← Foundation (both tools)
Phase 1: Command Restructuring     ← Rename/reorganize existing
Phase 2: New Commands              ← Add missing commands
Phase 3: Context Integration       ← Cross-tool features
```

---

## Part I: Current State

### JIG CLI (Current)

```
jigy
├── align           # Full workflow
├── rebuild [what]  # Rebuild graphs
├── validate [what] # Validate artifacts
├── show [what]     # Display structure (partial)
├── towers          # Tower structure (ROOT - should move)
├── matrix          # Layer × tower grid (ROOT - should move)
├── layers          # Layer hierarchy
└── audit           # Audit status (no subcommands)
```

**Gaps:**
- `towers` and `matrix` at root level (should be under `show`)
- No `context` command
- No `new` command for artifact creation
- No `init` command
- Inconsistent output flag support
- No `--markdown` flag

### DIG CLI (Current)

```
digy
├── init            # Initialize project
├── new <type>      # Create documents
├── validate [path] # Validate documents
├── rebuild         # Rebuild graph (was: graph)
├── context         # Show context
```

**Gaps:**
- No `show` command family
- No `audit` command
- No `promote` or `close` lifecycle commands
- Config in `dig/digconfig.yaml` (should be `dig.toml` in root)
- Inconsistent output flag support
- No `--markdown` flag

---

## Part II: Target State

### JIG CLI (Target)

```
jigy
├── align                        # Full workflow
├── context [target]             # Dynamic briefing
│   ├── (none)                   # Project context
│   ├── spec <id>                # Spec context
│   ├── brick <id>               # Brick context
│   ├── outcome <id>             # Outcome context
│   └── <dig-id>                 # JIG context related to DIG doc
├── show <what>                  # Static display
│   ├── spec <id>                # Single spec
│   ├── specs                    # List specs
│   ├── outcome <id>             # Single outcome
│   ├── outcomes                 # List outcomes
│   ├── brick <id>               # Single brick
│   ├── bricks                   # List bricks
│   ├── layers                   # Layer hierarchy
│   ├── towers                   # Tower structure (MOVED)
│   └── matrix                   # Layer × tower grid (MOVED)
├── audit <what>                 # Find issues
│   └── gaps                     # Coverage gaps
├── rebuild [what]               # Rebuild graphs
├── validate [what]              # Validate artifacts
├── new <type> "Title"           # Create artifacts
│   ├── spec                     # New specification
│   ├── outcome                  # New outcome
│   └── architecture             # New architecture doc
└── init                         # Initialize project

Universal flags: -j (JSON), -m (markdown), -v (verbose)
```

### DIG CLI (Target)

```
digy
├── context [target]             # Dynamic briefing
│   ├── (none)                   # Project context
│   ├── exploration <id>         # Exploration context
│   ├── scope <id>               # Scope context
│   ├── plan <id>                # Plan context
│   └── <jig-id>                 # DIG context related to JIG spec
├── show <what>                  # Static display
│   ├── exploration <id>         # Single exploration
│   ├── explorations             # List explorations
│   ├── scope <id>               # Single scope
│   ├── scopes                   # List scopes
│   ├── plan <id>                # Single plan
│   └── plans                    # List plans
├── audit [what]                 # Find issues
│   ├── (none)                   # Overall status
│   ├── stale                    # Stale documents
│   └── orphan                   # Orphan chains
├── rebuild                      # Rebuild graph
├── validate [path]              # Validate documents
├── new <type> "Title"           # Create documents
│   ├── exploration              # New exploration
│   ├── scope                    # New scope
│   ├── jigplan                  # New jigplan
│   ├── plan                     # New plan
│   └── retrospective            # New retrospective
├── promote <id> <type>          # Advance lifecycle
├── close <id>                   # Close deliberation
└── init                         # Initialize project

Universal flags: -j (JSON), -m (markdown), -v (verbose)
```

---

## Part III: Phase 0 — Flag Unification (Foundation)

**Goal:** All commands support the universal output flags consistently. This is the foundation that enables everything else.

### Why First?

Flags are the **interface contract**. Once flags work consistently:
- Command restructuring can happen without breaking agent integrations
- An agent using `jigy validate -j` works regardless of command reorganization
- Testing becomes systematic (every command × every flag combination)

### Flag Specification

#### Global Flags (Both Tools)

| Flag | Short | Purpose |
|------|-------|---------|
| `--help` | `-h` | Show help for any command |
| `--version` | — | Show version (root only) |
| `--no-rebuild` | — | Skip automatic graph rebuild |

#### Output Format Flags (Universal on All Commands)

| Flag | Short | Purpose |
|------|-------|---------|
| `--json` | `-j` | Machine-parseable JSON output |
| `--markdown` | `-m` | LLM-optimized markdown output |
| `--verbose` | `-v` | More detail in any format |

#### Flag Combinations

| Combination | Behavior |
|-------------|----------|
| (none) | Default human output (rich terminal formatting) |
| `-v` | Verbose human output |
| `-j` | Compact single-line JSON |
| `-j -v` | Verbose JSON (more fields) |
| `-m` | Compact markdown |
| `-m -v` | Verbose markdown (more detail) |
| `-j -m` | **Error:** mutually exclusive |

### Output Semantics by Command Type

| Command Type | Default Success Output | Examples |
|--------------|------------------------|----------|
| Validation | One-line summary with metrics | `Validated 91 specs, 11 bricks.` |
| Rebuild | One-line summary with metrics | `Rebuilt 3 graphs.` |
| Creation | Minimal confirmation | `Created S-094: Title` |
| Query/Display | Full output | `context`, `show`, `audit` |

### Implementation: OutputFormat Enum

Both tools should implement a shared pattern:

```python
from enum import Enum

class OutputFormat(Enum):
    HUMAN = "human"      # Rich terminal output (default)
    JSON = "json"        # Single-line JSON for agents
    MARKDOWN = "markdown" # LLM-optimized markdown
```

### JSON Output Contract

All JSON output must be:
- **Single-line** — No pretty-print (saves tokens)
- **Complete** — All data needed, no follow-up queries required
- **Typed** — Numbers are numbers, not strings like "91 specs"
- **Actionable** — Includes error codes and suggested next steps

```json
{"valid":true,"errors":[],"checked":{"specs":91,"bricks":11}}
```

### Markdown Output Contract

All markdown output must be:
- **Readable** — Headers, bullets, emphasis
- **Semantic** — Structure conveys meaning
- **Dense** — Information-rich without verbosity
- **Complete** — Stands alone as context

```markdown
# Validation Result

**Status:** Passed
**Checked:** 91 specs, 11 bricks
```

### Error Output Contract

All errors must include:
- **Code** — Machine-parseable identifier (e.g., `INVALID_REFERENCE`)
- **Location** — File and line number
- **Message** — What went wrong
- **Tip** — How to fix it

```bash
# Human
Error: INVALID_REFERENCE
  File: jig/specifications/S-042.md:7
  Reference: O-999 (does not exist)
  Tip: Run `jigy show outcomes` to see valid outcome IDs

# JSON
{"code":"INVALID_REFERENCE","file":"S-042.md","line":7,"tip":"Run jigy show outcomes"}
```

### Phase 0 Work Items

#### JIG

| ID | Task | Files |
|----|------|-------|
| J0.1 | Add `OutputFormat` enum | `src/jig/cli/output.py` (new) |
| J0.2 | Add `-j/-m/-v` flags to CLI parser | `src/jig/cli/main.py` |
| J0.3 | Refactor `validate` for all output modes | `src/jig/cli/validate.py` |
| J0.4 | Refactor `rebuild` for all output modes | `src/jig/cli/rebuild.py` |
| J0.5 | Refactor `align` for all output modes | `src/jig/cli/align.py` |
| J0.6 | Refactor `towers` for all output modes | `src/jig/cli/towers.py` |
| J0.7 | Refactor `matrix` for all output modes | `src/jig/cli/matrix.py` |
| J0.8 | Refactor `layers` for all output modes | `src/jig/cli/layers.py` |
| J0.9 | Refactor `audit` for all output modes | `src/jig/cli/audit.py` |
| J0.10 | Standardize error format with codes | `src/jig/validation/` |
| J0.11 | Add tests for flag combinations | `tests/cli/test_output_modes.py` |

#### DIG

| ID | Task | Files |
|----|------|-------|
| D0.1 | Add `OutputFormat` enum | `src/dig/cli/output.py` (new) |
| D0.2 | Ensure `-j/-m/-v` flags on CLI parser | `src/dig/cli/main.py` |
| D0.3 | Refactor `validate` for all output modes | `src/dig/cli/validate.py` |
| D0.4 | Refactor `rebuild` for all output modes | `src/dig/cli/rebuild.py` |
| D0.5 | Refactor `context` for all output modes | `src/dig/cli/context.py` |
| D0.6 | Refactor `new` for all output modes | `src/dig/cli/new.py` |
| D0.7 | Refactor `init` for all output modes | `src/dig/cli/init.py` |
| D0.8 | Standardize error format with codes | `src/dig/validate.py` |
| D0.9 | Add tests for flag combinations | `tests/cli/test_output_modes.py` |

### Phase 0 Success Criteria

1. Every command accepts `-j`, `-m`, and `-v` flags
2. `-j -m` produces a clear error message
3. JSON output is always single-line
4. All errors include code, location, message, and tip
5. Exit codes: 0 = success, 1 = validation failure, 2 = usage error

---

## Part IV: Phase 1 — Command Restructuring

**Goal:** Reorganize existing commands to match target structure without adding new functionality.

### JIG Changes

| Current | Target | Change Type |
|---------|--------|-------------|
| `jigy towers` | `jigy show towers` | Move under `show` |
| `jigy matrix` | `jigy show matrix` | Move under `show` |
| `jigy layers` | `jigy show layers` | Move under `show` |
| `jigy audit` | `jigy audit gaps` | Add subcommand structure |

### Backwards Compatibility

Keep old commands as aliases during deprecation period:

```python
# In CLI registration
@cli.command(name="towers", hidden=True, deprecated=True)
def towers_deprecated():
    """Deprecated: Use 'jigy show towers' instead."""
    click.echo("Warning: 'jigy towers' is deprecated. Use 'jigy show towers'.", err=True)
    return show_towers()
```

**Deprecation timeline:** One minor version with warnings, then remove in next major version.

### DIG Changes

DIG has fewer restructuring needs. Main change:
- Ensure `rebuild` is the canonical name (was `graph` historically)

### Phase 1 Work Items

#### JIG

| ID | Task | Files |
|----|------|-------|
| J1.1 | Create `show` command group | `src/jig/cli/show.py` |
| J1.2 | Move `towers` → `show towers` | `src/jig/cli/show.py` |
| J1.3 | Move `matrix` → `show matrix` | `src/jig/cli/show.py` |
| J1.4 | Move `layers` → `show layers` | `src/jig/cli/show.py` |
| J1.5 | Add deprecation aliases for old commands | `src/jig/cli/main.py` |
| J1.6 | Restructure `audit` with `gaps` subcommand | `src/jig/cli/audit.py` |
| J1.7 | Update all documentation and help text | `docs/`, CLI help |
| J1.8 | Add tests for restructured commands | `tests/cli/` |

#### DIG

| ID | Task | Files |
|----|------|-------|
| D1.1 | Verify `rebuild` is canonical (not `graph`) | `src/dig/cli/` |
| D1.2 | Update documentation | `docs/` |

### Phase 1 Success Criteria

1. `jigy show towers` works (same output as old `jigy towers`)
2. `jigy towers` emits deprecation warning to stderr, then works
3. `jigy audit gaps` works
4. All restructured commands support `-j`, `-m`, `-v` flags
5. Documentation updated

---

## Part V: Phase 2 — New Commands

**Goal:** Add commands that don't exist yet.

### JIG New Commands

| Command | Purpose | Priority |
|---------|---------|----------|
| `jigy context` | Dynamic project briefing | P0 |
| `jigy context spec <id>` | Spec-level context with neighborhood | P0 |
| `jigy context brick <id>` | Brick-level context | P1 |
| `jigy context outcome <id>` | Outcome-level context | P1 |
| `jigy show spec <id>` | Display single spec with S-F-T triangle | P0 |
| `jigy show specs` | List all specs (with filters) | P0 |
| `jigy show outcome <id>` | Display single outcome | P1 |
| `jigy show outcomes` | List all outcomes | P1 |
| `jigy show brick <id>` | Display single brick | P1 |
| `jigy show bricks` | List all bricks | P1 |
| `jigy new spec "Title"` | Create new specification | P1 |
| `jigy new outcome "Title"` | Create new outcome | P1 |
| `jigy new architecture "Title"` | Create new architecture doc | P2 |
| `jigy init` | Initialize JIG in a project | P1 |

### DIG New Commands

| Command | Purpose | Priority |
|---------|---------|----------|
| `digy show exploration <id>` | Display single exploration | P0 |
| `digy show explorations` | List all explorations | P0 |
| `digy show scope <id>` | Display single scope | P0 |
| `digy show scopes` | List all scopes | P0 |
| `digy show plan <id>` | Display single plan | P1 |
| `digy show plans` | List all plans | P1 |
| `digy context <type> <id>` | Artifact-level context | P0 |
| `digy audit` | Overall health check | P0 |
| `digy audit stale` | Find stale documents | P1 |
| `digy audit orphan` | Find orphan chains | P1 |
| `digy promote <id> <type>` | Advance document lifecycle | P2 |
| `digy close <id>` | Close deliberation chain | P2 |

### Filter Options for List Commands

Both tools should support consistent filtering:

```bash
# JIG
jigy show specs --search "CRDT"      # Keyword search
jigy show specs --unimplemented      # Status filter
jigy show specs --unverified         # Coverage filter
jigy show specs --outcome O-012      # By outcome
jigy show specs --brick B-crdt       # By brick

# DIG
digy show explorations --active      # Status filter
digy show scopes --search "CLI"      # Keyword search
digy show plans --recent 7d          # Time filter
digy show plans --parent D015        # By parent
```

### Phase 2 Work Items

#### JIG

| ID | Task | Files |
|----|------|-------|
| J2.1 | Implement `context` (project-level) | `src/jig/cli/context.py` |
| J2.2 | Implement `context spec <id>` | `src/jig/cli/context.py` |
| J2.3 | Implement `context brick <id>` | `src/jig/cli/context.py` |
| J2.4 | Implement `context outcome <id>` | `src/jig/cli/context.py` |
| J2.5 | Implement `show spec <id>` | `src/jig/cli/show.py` |
| J2.6 | Implement `show specs` with filters | `src/jig/cli/show.py` |
| J2.7 | Implement `show outcome <id>` | `src/jig/cli/show.py` |
| J2.8 | Implement `show outcomes` | `src/jig/cli/show.py` |
| J2.9 | Implement `show brick <id>` | `src/jig/cli/show.py` |
| J2.10 | Implement `show bricks` | `src/jig/cli/show.py` |
| J2.11 | Implement `new spec` | `src/jig/cli/new.py` |
| J2.12 | Implement `new outcome` | `src/jig/cli/new.py` |
| J2.13 | Implement `new architecture` | `src/jig/cli/new.py` |
| J2.14 | Implement `init` | `src/jig/cli/init.py` |
| J2.15 | Create `jig.toml` config support | `src/jig/config.py` |
| J2.16 | Add tests for all new commands | `tests/cli/` |

#### DIG

| ID | Task | Files |
|----|------|-------|
| D2.1 | Create `show` command group | `src/dig/cli/show.py` |
| D2.2 | Implement `show exploration(s)` | `src/dig/cli/show.py` |
| D2.3 | Implement `show scope(s)` | `src/dig/cli/show.py` |
| D2.4 | Implement `show plan(s)` | `src/dig/cli/show.py` |
| D2.5 | Enhance `context` for artifact-level | `src/dig/cli/context.py` |
| D2.6 | Implement `audit` | `src/dig/cli/audit.py` |
| D2.7 | Implement `audit stale` | `src/dig/cli/audit.py` |
| D2.8 | Implement `audit orphan` | `src/dig/cli/audit.py` |
| D2.9 | Implement `promote` | `src/dig/cli/promote.py` |
| D2.10 | Implement `close` | `src/dig/cli/close.py` |
| D2.11 | Move config to `dig.toml` in project root | `src/dig/config.py` |
| D2.12 | Add tests for all new commands | `tests/cli/` |

### Phase 2 Success Criteria

1. All P0 commands implemented and working
2. All commands support `-j`, `-m`, `-v` flags
3. Filter options work correctly
4. Config files in project root (`jig.toml`, `dig.toml`)
5. Tests pass

---

## Part VI: Phase 3 — Context Integration

**Goal:** Enable cross-tool context via subprocess calls.

### Overview

When JIG and DIG are both present, `context` commands should automatically include relevant context from the peer tool.

```bash
jigy context S-004
# Returns: JIG context for S-004 + DIG deliberations that produced S-004

digy context D017
# Returns: DIG context for D017 + JIG specs that D017 produced
```

### Configuration

#### Config File Location

Both config files live in **project root**:

```
project/
├── jig.toml          # JIG config (created by jigy init)
├── dig.toml          # DIG config (created by digy init)
├── jig/              # JIG artifacts
└── dig/              # DIG artifacts
```

#### Integration Settings

**jig.toml:**
```toml
[integration]
include_dig = true   # Call digy for cross-tool context
```

**dig.toml:**
```toml
[integration]
include_jig = true   # Call jigy for cross-tool context
```

### Cross-Reference Fields

#### DIG → JIG: `produces` field

```yaml
# In DIG document D017_JIGPLAN_CLI_Output.md
---
title: CLI Output Unification
type: jigplan
produces: [S-004, S-005, S-007]
---
```

#### JIG → DIG: `deliberation` field

```yaml
# In JIG spec S-004_Minimal_Success_Feedback.md
---
id: S-004
title: Minimal Success Feedback
deliberation: D017
---
```

### Subprocess Protocol

When `jigy context <id>` is called:

1. JIG builds its own context for `<id>`
2. If `include_dig=true` in `jig.toml`:
   - JIG calls `digy context <id> -m` as subprocess
   - DIG returns relevant context (or empty)
   - JIG appends DIG's output
3. Return combined result

**Circular call prevention:** Use environment variable:
```bash
JIG_PEER_CALL=1 digy context S-004 -m
# DIG sees JIG_PEER_CALL=1, skips calling jigy back
```

### Reverse Lookup Indexes

For fast cross-reference resolution, build indexes during graph rebuild:

```json
// dig/generated/produces_index.json
{
  "S-004": ["D017"],
  "S-005": ["D017"],
  "S-007": ["D017", "D022"]
}
```

### Phase 3 Work Items

#### JIG

| ID | Task | Files |
|----|------|-------|
| J3.1 | Add `jig.toml` config with `[integration]` | `src/jig/config.py` |
| J3.2 | Add `deliberation` field to spec schema | `src/jig/schema.py` |
| J3.3 | Implement peer subprocess call in `context` | `src/jig/cli/context.py` |
| J3.4 | Build reverse lookup index for `deliberation` | `src/jig/graph/` |
| J3.5 | Handle peer timeout/errors gracefully | `src/jig/cli/context.py` |
| J3.6 | Add `JIG_PEER_CALL` env var check | `src/jig/cli/context.py` |
| J3.7 | Tests for cross-tool integration | `tests/integration/` |

#### DIG

| ID | Task | Files |
|----|------|-------|
| D3.1 | Move config from `dig/digconfig.yaml` to `dig.toml` | `src/dig/config.py` |
| D3.2 | Add `[integration]` section to config | `src/dig/config.py` |
| D3.3 | Add `produces` field validation | `src/dig/validate.py` |
| D3.4 | Build reverse lookup index for `produces` | `src/dig/graph.py` |
| D3.5 | Implement peer subprocess call in `context` | `src/dig/cli/context.py` |
| D3.6 | Handle peer timeout/errors gracefully | `src/dig/cli/context.py` |
| D3.7 | Add `DIG_PEER_CALL` env var check | `src/dig/cli/context.py` |
| D3.8 | Tests for cross-tool integration | `tests/integration/` |

### Phase 3 Success Criteria

1. `jigy context S-004` includes related DIG deliberations (when present)
2. `digy context D017` includes related JIG specs (when present)
3. Missing peer tool doesn't cause errors (graceful degradation)
4. `include_dig=false` / `include_jig=false` is respected
5. No circular calls (env var prevention works)
6. Cross-tool context adds < 300ms latency
7. Token budget respected (< 5000 tokens combined)

---

## Part VII: Testing Strategy

### Per-Phase Testing

| Phase | Test Focus |
|-------|------------|
| Phase 0 | Every command × every flag combination |
| Phase 1 | Aliases work, restructured commands same output |
| Phase 2 | New commands have all three output modes |
| Phase 3 | Cross-tool context works, graceful degradation |

### Test Matrix Template

```python
@pytest.mark.parametrize("command,flags", [
    ("validate", []),
    ("validate", ["-j"]),
    ("validate", ["-m"]),
    ("validate", ["-v"]),
    ("validate", ["-j", "-v"]),
    ("validate", ["-m", "-v"]),
    # ... for each command
])
def test_output_modes(command, flags):
    result = runner.invoke(cli, [command] + flags)
    assert result.exit_code == 0
    if "-j" in flags:
        assert_valid_json(result.output)
    if "-m" in flags:
        assert_valid_markdown(result.output)
```

### Validation Commands

```bash
# Phase 0 validation
jigy validate           # Default output
jigy validate -j        # JSON output
jigy validate -m        # Markdown output
jigy validate -v        # Verbose
jigy validate -j -v     # Verbose JSON
jigy validate -j -m     # Should error (mutually exclusive)

# Phase 1 validation
jigy show towers        # Works
jigy towers             # Works with deprecation warning

# Phase 2 validation
jigy context            # Project context
jigy context spec S-001 # Spec context

# Phase 3 validation
jigy context S-001      # Includes DIG context if available
```

---

## Part VIII: Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing scripts | Deprecation warnings for one version before removal |
| Flag inconsistency | Shared `OutputFormat` enum and formatting library |
| JSON schema changes | Version JSON output, document schema |
| Peer tool not installed | Graceful degradation (no errors, just omit peer context) |
| Large context output | Token budgets enforced (see Context Integration doc) |
| Circular subprocess calls | `JIG_PEER_CALL` / `DIG_PEER_CALL` env vars |

---

## Part IX: Implementation Order Summary

### Recommended Sequence

1. **JIG Phase 0** — Flag unification (establishes pattern)
2. **DIG Phase 0** — Flag unification (follows JIG pattern)
3. **JIG Phase 1** — Command restructuring
4. **DIG Phase 1** — Command restructuring (minimal)
5. **JIG Phase 2** — New commands
6. **DIG Phase 2** — New commands
7. **JIG Phase 3** — Context integration
8. **DIG Phase 3** — Context integration

### First PR Scope (Recommended)

Start with JIG Phase 0:
- Add `OutputFormat` enum
- Add `-j/-m/-v` flag parsing
- Refactor `jigy validate` for all output modes
- Refactor `jigy rebuild` for all output modes
- Add tests

This gives a working pattern that can be replicated.

---

## Part X: Success Metrics

### Functional

1. All commands support `-j`, `-m`, `-v` flags
2. Flag semantics identical across both tools
3. Error messages include code, location, message, tip
4. Cross-tool context works transparently

### Performance

1. Single-tool context < 200ms latency
2. Cross-tool context < 500ms latency
3. Default output < 1000 tokens
4. Verbose output < 2500 tokens

### User Experience

1. Learning one CLI teaches you the other
2. Output clearly separates JIG and DIG sections
3. Config is discoverable and documented
4. Deprecation warnings are actionable

### Agent Experience

1. Single context call provides sufficient orientation
2. Agents don't hallucinate specs/functions after reading context
3. Task completion rate improves vs. no context baseline

---

## Part XI: Design Decisions

1. **No deprecation period.** Single user currently. Clean break to new commands.

2. **No schema versioning.** JSON output parsed by agents, which are adaptable. May lock down schemas once tools mature.

3. **No error code registry.** Use descriptive stderr output. Agents know how to read.

4. **Document as we go.** Verbose field details will evolve with use.

---

## References

- `dig/wip/DJ001_CONCEPT_CLI_Design_Manifesto.md` — Principles
- `dig/wip/DJ002_SCOPE_CLI_Recommendations.md` — Target command structure
- `dig/wip/DJ003_CONCEPT_Context_Integration.md` — Phase 3 design details
- `jig/Charter.md` — JIG Charter goals
- `jig/architecture/A-002_CLI_Command_Architecture.md` — JIG CLI architecture

---

*This document is the authoritative implementation plan. Update as implementation progresses.*
