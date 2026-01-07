---
title: "JIG & DIG CLI Recommendations"
type: scope
status: active
created: 1736100000
created_human: "2026-01-05 12:00 CST"
parent: "[[DJ001_CONCEPT_CLI_Design_Manifesto]]"
children: ["[[DJ003_CONCEPT_Context_Integration]]"]
---
# JIG & DIG CLI Recommendations

**Date:** 2026-01-05
**Reference:** JIG_DIG_CLI_Design_Manifesto.md
**Based on:** A-002 (CLI Command Architecture), C014 (Agent Tools), D017 (CLI Output Unification)

---

## Executive Summary

JIG and DIG are complementary systems with distinct purposes but shared users. Their CLIs should be **parallel in structure** so that learning one teaches you the other, while remaining **distinct in semantics** to reflect their different domains.

| Aspect | DIG | JIG |
|--------|-----|-----|
| **Purpose** | Capture *why* decisions were made | Define *what* should be true |
| **Lifecycle** | Archival (fades over time) | Evergreen (updated, not deleted) |
| **Content** | Deliberation, exploration, reasoning | Specifications, outcomes, architecture |
| **Command** | `digy` | `jigy` |
| **Root Directory** | `dig/` | `jig/` |

**The goal:** A developer fluent in `jigy` should feel immediately at home with `digy`, and vice versa.

---

## Part I: Current State

### JIG CLI (per A-002)

Well-designed for humans:
- Verb-first commands
- Three global flags only
- Human output by default
- Fail fast, fail clearly

**Gap:** Agent tooling is incomplete. C014 addresses this but isn't implemented.

**Current commands:**
```
jigy align           # Full workflow
jigy rebuild [what]  # Rebuild graphs
jigy validate [what] # Validate artifacts
jigy show [what]     # Display structure
jigy towers          # Tower structure
jigy matrix          # Layer × tower grid
jigy audit           # Audit status
```

### DIG CLI (post-D017)

Recently unified output:
- Unified `--json` flag across all commands
- Minimal feedback with metrics for `validate` and `rebuild`
- `-v/--verbose` for detailed output

**Gap:** Lacks JIG-parallel ergonomics for navigation and agent tooling.

**Current commands:**
```
digy init            # Initialize project
digy new <type>      # Create documents
digy validate [path] # Validate documents
digy rebuild         # Rebuild graph
digy context         # Show context
```

---

## Part II: Parallel Command Structure

The core insight: **same verbs, different nouns**.

### Command Mapping

| Action             | DIG                            | JIG                       |
| ------------------ | ------------------------------ | ------------------------- |
| Initialize         | `digy init`                    | `jigy init`               |
| Validate           | `digy validate`                | `jigy validate`           |
| Create             | `digy new exploration "Title"` | `jigy new spec "Title"`   |
| Context (project)  | `digy context`                 | `jigy context`            |
| Context (artifact) | `digy context scope D016`      | `jigy context spec S-042` |
| Show list          | `digy show explorations`       | `jigy show specs`         |
| Show single        | `digy show scope D016`         | `jigy show spec S-042`    |
| Rebuild            | `digy rebuild`                 | `jigy rebuild`            |
| Audit              | `digy audit`                   | `jigy audit`              |

### Artifact Type Mapping

| DIG Types | JIG Types |
|-----------|-----------|
| `exploration` | `spec` (specification) |
| `scope` | `outcome` |
| `jigplan` | `architecture` |
| `plan` | — |
| `retrospective` | — |

### ID Convention Mapping

| DIG | JIG |
|-----|-----|
| Filename is identity | `S-NNN` (specs), `O-NNN` (outcomes), `A-NNN` (architecture) |
| `dig/wip/` | `jig/specifications/`, `jig/outcomes/`, `jig/architecture/` |
| `dig/archive/` | (evergreen, no archive) |

**DIG Filename Convention:**
- Suggested format: `LNNN_TYPE_Title.md` (e.g., `D023_SCOPE_Filename-As-Document-Identity.md`)
- The `LNNN_` prefix is **conventional but not required**
- No `id:` field in frontmatter — the filename itself is the document identity
- References use full filenames: `[[D024_JIGPLAN_Filename-As-Document-Identity]]`

---

## Part III: The Flag System

Per the manifesto, flags are universal and consistent across both tools.

### Global Flags

| Flag           | Short | Purpose                      |
| -------------- | ----- | ---------------------------- |
| `--help`       | `-h`  | Show help for any command    |
| `--version`    | —     | Show version (root only)     |
| `--no-rebuild` | —     | Skip automatic graph rebuild |

### Output Format Flags (Universal)

All output flags work on **all commands**. No exceptions.

| Flag         | Short | Purpose                                        |
| ------------ | ----- | ---------------------------------------------- |
| `--json`     | `-j`  | Machine-parseable JSON (for agent tool calls)  |
| `--markdown` | `-m`  | LLM-optimized markdown (for context injection) |
| `--verbose`  | `-v`  | More detail in any format                      |

### Flag Combinations

| Combination | Behavior                       |
| ----------- | ------------------------------ |
| (none)      | Default human output           |
| `-v`        | Verbose human output           |
| `-j`        | Compact JSON                   |
| `-j -v`     | Verbose JSON (more fields)     |
| `-m`        | Compact markdown               |
| `-m -v`     | Verbose markdown (more detail) |
| `-j -m`     | **Error:** mutually exclusive  |

### Success Output Semantics

**All modes provide feedback on success.** Minimal output with metrics builds trust and aids discoverability.

```bash
# Default: one-line summary with metrics
$ jigy validate
Validated 91 specs, 11 bricks.

# With auto-rebuild enabled
$ jigy validate
Rebuilt 3 graphs. Validated 91 specs, 11 bricks.

# JSON: structured data for parsing
$ jigy validate -j
{"valid":true,"errors":[],"checked":{"specs":91,"bricks":11}}

# Markdown: human-readable confirmation
$ jigy validate -m
Validation passed. Checked 91 specs, 11 bricks.
```

### JSON Contract

Both tools produce JSON with:
- Single-line format (`separators=(",", ":")`)
- Error codes, not prose
- Suggested next actions
- Relevant counts and IDs

```json
{"valid":false,"errors":[{"code":"MISSING_FIELD","file":"S-042.md","line":1,"tip":"Add id to frontmatter"}]}
```

### Error Code Patterns

| JIG Error Codes | DIG Error Codes |
|-----------------|-----------------|
| `MISSING_REQUIRED_FIELD` | `MISSING_PARENT` |
| `INVALID_ID_FORMAT` | `INVALID_STATUS` |
| `INVALID_REFERENCE` | `ORPHAN_CHILD` |
| `DUPLICATE_ID` | `CIRCULAR_REFERENCE` |
| `PARTITION_GAP` | `INVALID_TYPE` |
| `LAYER_VIOLATION` | `STALE_TIMESTAMP` |

---

## Part IV: The `context` Command (Both Tools)

The most important command for agents. Synthesizes orientation, not just display.

### Project-Level Context

```bash
# JIG: Project overview with gaps
$ jigy context
JIG CONTEXT: my-project
════════════════════════
PROJECT STATE
  Specs: 91 total | 78 implemented | 65 verified
  Gaps: 3 unimplemented, 13 unverified
TOP GAPS
  S-044  CRDT Conflict Resolution     unimplemented
  ...

# DIG: Deliberation overview with activity
$ digy context
DIG CONTEXT: my-project
════════════════════════
ACTIVE DELIBERATIONS
  D015  EXPLORATION  CLI Output Design
  D016  SCOPE        CLI Output Unification
STALE (14+ days)
  D008  EXPLORATION  CRDT Options
  ...
```

### Artifact-Level Context

```bash
# JIG: Spec with S-F-T triangle and neighborhood
$ jigy context spec S-042
CONTEXT: S-042 CRDT Value Observation
═════════════════════════════════════
STATUS: PARTIAL (2 impl, 1 test, 1 gap)
OUTCOME: O-012 (Real-time Collaboration)
IMPLEMENTATIONS
  F-jig.crdt.observe.subscribe    src/jig/crdt/observe.py:45
  F-jig.crdt.observe.notify       src/jig/crdt/observe.py:78  ⚠ untested
RELATED SPECS (same outcome)
  S-040  Real-time Sync Protocol      complete
  S-044  Offline Queue                unimplemented

# DIG: Document with ancestry and children
$ digy context scope D016
CONTEXT: D016 SCOPE CLI Output Unification
═══════════════════════════════════════════
STATUS: Active
PARENT: D015 (EXPLORATION)
CHILDREN: D017 (PLAN)
RELATED (same topic)
  D008  EXPLORATION  Error Handling Patterns
```

### Output Modes for Context

The `context` command is dual-purpose for agents:

| Mode | Flag | Use Case |
|------|------|----------|
| Human | (default) | Terminal interaction |
| JSON | `-j` | Agent tool calls (parse → act) |
| Markdown | `-m` | LLM context injection (understand → reason) |

```bash
# For agent tool calls
jigy context spec S-042 -j

# For LLM context injection
jigy context -m > context.md
```

---

## Part V: The `show` Command Family (Both Tools)

Display artifacts statically. Unlike `context`, which synthesizes, `show` presents what exists.

### List Commands

```bash
# JIG
jigy show specs                     # All specs
jigy show specs --search "CRDT"     # Keyword search
jigy show specs --unimplemented     # Only unimplemented
jigy show outcomes                  # All outcomes
jigy show bricks                    # All bricks
jigy show layers                    # Layer hierarchy

# DIG
digy show explorations              # All explorations
digy show explorations --active     # Only active
digy show scopes --search "CLI"     # Keyword search
digy show plans --recent 7d         # Recent plans
```

### Single Display

```bash
# JIG: Spec with S-F-T triangle
$ jigy show spec S-042
S-042: CRDT Value Observation
  Outcome: O-012
  Status: PARTIAL
  Implements (2):
    F-jig.crdt.observe.subscribe    src/jig/crdt/observe.py:45
    F-jig.crdt.observe.notify       src/jig/crdt/observe.py:78
  Verifies (1):
    T-test_observe.test_subscribe   tests/test_observe.py:23

# DIG: Document with relationships
$ digy show scope D016
D016: CLI Output Unification
  Type: SCOPE
  Status: active
  Parent: D015 (EXPLORATION)
  Children: D017 (PLAN)
```

---

## Part VI: The `audit` Command (Both Tools)

Surface health issues. Different domains, same verb.

### JIG: Coverage Gaps

```bash
$ jigy audit gaps

UNIMPLEMENTED SPECS (3)
  S-044  CRDT Conflict Resolution      (O-012)
  S-045  Offline Queue Persistence     (O-013)
  S-046  Network Partition Detection   (O-013)

UNVERIFIED SPECS (5)
  S-012  Token Expiration              2 functions, 0 tests
  ...

ORPHAN FUNCTIONS (12)
  F-jig.utils.helpers.format_date  src/jig/utils/helpers.py:34
  ...

Summary: 3 unimplemented, 5 unverified, 12 orphan functions
```

### DIG: Deliberation Health

```bash
$ digy audit

ACTIVE (3)
  D015  EXPLORATION  CLI Output Design Principles
  D016  JIGPLAN      CLI Output Unification
  D017  PLAN         CLI Output Unification

STALE (no updates in 14+ days) (2)
  D008  EXPLORATION  CRDT Implementation Options
  D009  SCOPE        Offline Sync Strategy

ABANDONED (no retrospective) (5)
  D001  SCOPE        Initial Project Setup
  ...

Summary: 3 active, 2 stale, 5 abandoned
```

### Audit Subcommands

| JIG | DIG |
|-----|-----|
| `jigy audit gaps` | `digy audit` |
| `jigy audit coverage` | `digy audit stale` |
| — | `digy audit orphan` |

---

## Part VII: Creation Commands (Both Tools)

### `new` Command

```bash
# JIG: Auto-assign ID, create artifact
$ jigy new spec "Token Refresh"
Created S-094: Token Refresh
  File: jig/specifications/S-094_Token_Refresh.md

$ jigy new spec "Token Refresh" -j
{"id":"S-094","type":"specification","file":"jig/specifications/S-094_Token_Refresh.md"}

# DIG: Auto-assign ID, create document
$ digy new exploration "Error Handling"
Created D020: Error Handling
  File: dig/wip/D020_EXPLORATION_Error_Handling.md

$ digy new exploration "Error Handling" -j
{"id":"D020","type":"exploration","file":"dig/wip/D020_EXPLORATION_Error_Handling.md"}
```

### JIG-Specific Types

```bash
jigy new spec "Title"           # Specification
jigy new outcome "Title"        # Outcome
jigy new architecture "Title"   # Architecture document
```

### DIG-Specific Types

```bash
digy new exploration "Title"    # Exploration
digy new scope "Title"          # Scope
digy new jigplan "Title"        # JIGplan
digy new plan "Title"           # Plan
digy new retrospective "Title"  # Retrospective
```

---

## Part VIII: Integration Points

DIG deliberation crystallizes into JIG intent. The tools should acknowledge this relationship.

### Peer Integration Configuration

Each tool automatically includes the other's context when both are present. This is controlled via explicit config created by `init`.

#### Config Files

Both config files live in the **project root** for discoverability and parallel structure:

```
project/
├── jig.toml          # JIG config (created by jigy init)
├── dig.toml          # DIG config (created by digy init)
├── jig/              # JIG artifacts
└── dig/              # DIG artifacts
```

`jigy init` creates `jig.toml`:
```toml
[integration]
include_dig = true   # Include DIG context when available
```

`digy init` creates `dig.toml`:
```toml
[integration]
include_jig = true   # Include JIG context when available
```

> **DIG Migration Required:** DIG currently uses `dig/digconfig.yaml`. This must change to `dig.toml` in the project root to align with JIG and follow the parallel config convention.

#### Behavior

```bash
jigy context   # Reads jig.toml, sees include_dig = true
               # Checks if digy exists and ./dig/ present
               # If yes: combined output
               # If no: JIG only (graceful degradation)
```

#### Design Rationale

**Explicit config > Implicit magic**

1. **No hidden behavior** — Integration is visible in the config file
2. **Progressive discovery** — User sees it, learns the option exists
3. **Easy to change** — Flip the bool to disable
4. **Self-documenting** — Config explains the system

### The Flow

```
dig/                               jig/
────────────                       ────────────
D015 exploration
    ↓
D016 scope
    ↓
D017 jigplan ─────────────────────→ S-004, S-005, S-007
    ↓
D018 plan
    ↓
D019 retrospective
```

### Cross-Tool Context

When peer integration is enabled, `context` commands automatically include context from the other tool:

```bash
jigy context S-004
# 1. Builds JIG context for S-004
# 2. Calls: digy context S-004 -m
# 3. Returns combined result

digy context D017
# 1. Builds DIG context for D017
# 2. Calls: jigy context D017 -m
# 3. Returns combined result
```

Each tool owns its own search logic. When DIG receives `digy context S-004`, it determines what DIG knows about that identifier (e.g., which deliberations produced S-004). JIG doesn't need to understand DIG internals, and vice versa.

**No special commands or flags required.** The `context` command handles cross-tool integration transparently based on config.

See **JIG_DIG_Context_Integration.md** for detailed design.

---

## Part IX: Implementation Roadmap

### Phase 1: Core Parallel Commands (P0)

**JIG:**
1. `jigy context` (project-level)
2. `jigy context spec/brick/outcome` (artifact-level)
3. `jigy show spec <id>`
4. `jigy show specs` with filtering
5. `jigy audit gaps`
6. Universal `-j`, `-m`, `-v` on all commands

**DIG:**
1. `digy show <type>` list commands
2. `digy show <type> <id>` single display
3. `digy context` enhancement (artifact-level)
4. `digy audit` command
5. Error codes in validation
6. Universal `-j`, `-m`, `-v` on all commands

### Phase 2: Creation & Lifecycle (P1)

**JIG:**
1. `jigy new spec/outcome/architecture`
2. `jigy init`
3. Move `towers`/`matrix` under `show`

**DIG:**
1. `digy promote <id> <type>`
2. `digy close <id>`

### Phase 3: Integration (P2)

**Both:**
1. Peer integration config in `.toml` files (root directory)
2. `context` command calls peer tool when configured
3. Each tool handles unknown IDs gracefully (returns relevant context or empty)

---

## Part X: Success Metrics

### JIG

After implementation:
1. `jigy context` provides dynamic project briefing
2. `jigy context spec S-042` shows spec with neighborhood
3. All commands support `-j` and `-m` with structured output
4. Error codes are machine-parseable
5. Agent can accomplish tasks with fewer tool calls

### DIG

After implementation:
1. `digy context scope D016` shows deliberation with neighborhood
2. `digy show explorations --active` lists active explorations
3. `digy audit` surfaces stale/orphan deliberations
4. `digy context S-004` returns deliberations that produced S-004
5. Agent can navigate deliberation history efficiently

### Both

1. Learning one CLI teaches you the other
2. Flag semantics are identical
3. All flags work on all commands (universal applicability)
4. Minimal feedback with metrics on success (all modes)
5. Cross-tool context works transparently via peer integration

---

## Part XI: Compliance Checklists

### Both Tools (Per Manifesto)

**Global Flags:**
- [ ] `--help` / `-h` — Show help
- [ ] `--version` — Show version (root only)
- [ ] `--no-rebuild` — Skip automatic graph rebuild

**Output Flags (Universal):**
- [ ] `-j` / `--json` — Single-line JSON, always outputs
- [ ] `-m` / `--markdown` — LLM-optimized markdown, always outputs
- [ ] `-v` / `--verbose` — More detail in any format
- [ ] All flags work on all commands (no exceptions)
- [ ] `-j -m` produces error (mutually exclusive)

**Output Behavior:**
- [ ] Human output by default (rich terminal formatting)
- [ ] One-line feedback with metrics for validation/rebuild commands
- [ ] Minimal confirmation for creation commands
- [ ] Full output for query/display commands
- [ ] Errors to stderr with codes, locations, and tips
- [ ] Exit codes: 0 = success, 1 = error, 2 = usage

**Peer Integration:**
- [ ] `init` creates `.toml` config in project root with `[integration]` section
- [ ] `include_dig` / `include_jig` defaults to `true` when peer detected
- [ ] `context` command respects integration config
- [ ] Graceful degradation when peer not installed

**DIG Migration:**
- [ ] Move config from `dig/digconfig.yaml` to `dig.toml` in project root

### JIG (A-002 Compliance)

- [ ] Verb-first command structure
- [ ] `towers` and `matrix` moved under `show`
- [ ] New commands documented before implementation

### DIG

- [ ] `show` commands parallel JIG structure
- [ ] Lifecycle commands (`promote`, `close`) are explicit
- [ ] Archival vs active distinction respected

---

## Appendix: Command Reference

### JIG Commands (Target State)

```
jigy
├── align                        # Full workflow
├── context [target]             # Dynamic briefing (accepts any ID)
│   ├── (none)                   # Project context
│   ├── spec <id>                # Spec context
│   ├── brick <id>               # Brick context
│   ├── outcome <id>             # Outcome context
│   └── <dig-id>                 # Returns JIG context related to DIG doc
├── show <what>                  # Static display
│   ├── spec <id>                # Single spec
│   ├── specs                    # List specs
│   ├── outcome <id>             # Single outcome
│   ├── outcomes                 # List outcomes
│   ├── brick <id>               # Single brick
│   ├── bricks                   # List bricks
│   ├── layers                   # Layer hierarchy
│   ├── towers                   # Tower structure
│   └── matrix                   # Layer × tower grid
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

### DIG Commands (Target State)

```
digy
├── context [target]             # Dynamic briefing (accepts any ID)
│   ├── (none)                   # Project context
│   ├── exploration <id>         # Exploration context
│   ├── scope <id>               # Scope context
│   ├── plan <id>                # Plan context
│   └── <jig-id>                 # Returns DIG context related to JIG spec
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

## Quick Reference

### The Three Modes

```bash
command           # Human: rich terminal output
command -j        # Agent: JSON for parsing
command -m        # LLM: Markdown for context
```

### The Mental Model

```
Who's reading?     What are they doing?     Use:
─────────────────────────────────────────────────
Human in terminal  Interacting              (default)
Human exporting    Saving/copying           -m
Agent tool call    Parsing → acting         -j
Agent context      Understanding → reasoning -m
```
