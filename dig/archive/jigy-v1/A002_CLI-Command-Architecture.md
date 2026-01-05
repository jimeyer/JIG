---
title: "A002: CLI Command Architecture"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1765336342
created_human: "2025-12-09 21:12 CST"
parent: "[[B012_PROPOSAL_CLI-Command-Simplification]]"
children: []
---
# A002: CLI Command Architecture

**Status:** Accepted
**Date:** 2025-12-09
**Related:** A001 (Core Artifacts Contract), B012 (CLI Simplification Proposal)

---

## Context

The JIG CLI is the primary interface for developers working with the alignment system. A well-designed CLI shapes how users think about the tool—it communicates the mental model, guides workflows, and reduces cognitive load.

This document establishes the enduring architecture of the JIG CLI: its philosophy, structure, and contract. It is evergreen—the authoritative reference for all CLI development.

---

## Philosophy

### The Unix Way, Applied

JIG draws inspiration from the Unix philosophy but adapts it for a domain-specific tool:

1. **Do one thing well** — Each command has a clear, singular purpose
2. **Compose operations** — Simple commands chain into complex workflows
3. **Sensible defaults** — Zero configuration for common cases
4. **Fail fast, fail clearly** — Errors surface immediately with actionable messages
5. **Human output by default** — Designed for reading, not just parsing

### The Git Model

Git's CLI is the gold standard for developer tools. JIG adopts its patterns:

| Git Pattern | JIG Application |
|-------------|-----------------|
| Bare command shows help | `jigy` → usage and available commands |
| Verb-first commands | `jigy rebuild`, not `jigy graph rebuild` |
| Noun subcommands | `jigy rebuild impl`, `jigy show layers` |
| Minimal flags | Only `--help` and `--version` globally |
| Auto-discovery | Find project root by walking up directory tree |
| Strict by default | No `--lenient`, `--permissive`, or silent failures |

### Why Verb-First?

Commands describe **actions users take**, not **objects in the system**:

```
# What the user wants to do (clear)
jigy rebuild impl
jigy validate bricks
jigy show layers

# What the system contains (unclear)
jigy impl rebuild      # "What can I do with impl?"
jigy graph impl build  # Nested hierarchy confusion
```

Verb-first commands answer "What can I do?" immediately. Noun subcommands narrow the scope.

---

## Role Models

### Git — The Standard

```bash
git status          # Show state
git commit          # Take action
git log             # View history
git diff HEAD~3     # Inspect changes
```

No `--output-format`, no `--project-dir`, no `--verbosity-level`. Git discovers the repository, produces human-readable output, and fails clearly.

### Cargo — Rust's Exemplar

```bash
cargo build         # Build the project
cargo test          # Run tests
cargo check         # Fast validation
cargo fmt           # Format code
```

Cargo is opinionated: it knows where source files live, where build artifacts go, and what "correct" looks like. Configuration exists but is rarely needed.

### Make — Task Orchestration

```bash
make                # Default target (often "all")
make build          # Build target
make test           # Test target
make clean          # Clean target
```

Simple, memorable, predictable. No flags required for common operations.

---

## Design Principles

### 1. Radical Simplicity

The CLI has exactly **two global flags**:

| Flag | Purpose |
|------|---------|
| `--help` | Show help for any command |
| `--version` | Show version (root command only) |

That's it. Everything else is configuration (future) or unnecessary.

### 2. Sensible Discovery

JIG finds what it needs automatically:

- **Project root**: Walk up from current directory looking for `jig/` or `.jig/`
- **Source directory**: Default `src/`, future config override
- **Test directory**: Default `tests/`, future config override
- **Output paths**: Canonical paths per A001 (`jig/generated/*.ndjson`)

If discovery fails, the error explains what's missing and how to fix it.

### 3. One Obvious Path

For any task, there should be one obvious command:

| Task | Command |
|------|---------|
| "Check if everything is aligned" | `jigy align` |
| "Rebuild all the graphs" | `jigy rebuild` |
| "See the project structure" | `jigy show` |
| "What needs attention?" | `jigy audit` |

### 4. Progressive Disclosure

Basic usage requires zero knowledge:

```bash
jigy align          # Does everything, shows everything useful
```

Advanced usage narrows scope:

```bash
jigy rebuild impl   # Just the implementation graph
jigy validate bricks # Just brick validation
jigy show layers    # Just layer hierarchy
```

### 5. Designed for Humans

Output is crafted for terminal reading:

- Clear section headers
- Consistent formatting
- Color when appropriate (respects `NO_COLOR`)
- Counts and summaries for large outputs
- Exit codes for scripting (success = 0, failure = non-zero)

Scripts that need machine-readable output should use the graph files directly (`jig/generated/*.ndjson`) or a future API.

### 6. Fail Fast, Fail Clearly

No silent failures. No warnings that should be errors. No `--strict` flag because strict is the only mode.

```bash
$ jigy validate
Error: Brick B-auth references M-auth.session which does not exist in implementation graph

  Defined in: jig/bricks.yaml:7
  Fix: Either add src/auth/session.py or remove M-auth.session from brick

$ echo $?
1
```

---

## Command Contract

This section defines the complete CLI surface. All commands listed here are **contractual**—they will not be removed without a major version bump and migration path.

### Command Hierarchy

```
jigy
├── align                       # Full workflow: rebuild + validate + summary
├── rebuild [target]            # Rebuild graphs
│   ├── (none)                  # All graphs
│   ├── intent                  # Intent graph only
│   ├── impl                    # Implementation graph only
│   └── verify                  # Verification graph only
├── validate [target]           # Validate artifacts (implies rebuild)
│   ├── (none)                  # All validation
│   ├── intent                  # Intent artifacts only
│   ├── bricks                  # Brick definitions only
│   └── full                    # Explicit full validation
├── show [target]               # Display structural information
│   ├── (none)                  # Bricks + layers overview
│   ├── layers                  # Layer hierarchy only
│   └── bricks                  # Brick details only
└── audit [subcommand]          # Audit status and history
    ├── (none)                  # Show pending items and status
    ├── history <id>            # History for specific node
    └── compact                 # Compact audit log
```

### Command Specifications

#### `jigy`

**Purpose:** Show help and usage.

**Behavior:** Display available commands, brief descriptions, and examples.

**Exit code:** 0

---

#### `jigy align`

**Purpose:** The "do everything" command. Runs the complete JIG workflow.

**Steps executed:**
1. Rebuild all graphs (intent, impl, verify)
2. Validate all artifacts
3. Display summary (specs, functions, tests, coverage, status)

**Output:**
```
Rebuilding graphs...
  intent: 45 specs, 5 outcomes
  impl: 312 functions
  verify: 89 tests

Validating...
  intent: OK
  bricks: OK (12 bricks, 3 layers)

Summary:
  Specs: 45 total (42 implemented, 38 verified)
  Coverage: 87%
  Status: ALIGNED
```

**Exit code:** 0 if aligned, non-zero if validation fails or graphs cannot be built.

**Rationale:** "Align" captures JIG's core purpose—ensuring specs, functions, and tests are aligned. One command to rule them all.

---

#### `jigy rebuild [target]`

**Purpose:** Rebuild graph files without validation.

**Targets:**
| Target | Graph File | Source |
|--------|------------|--------|
| (none) | All three | All sources |
| `intent` | `intent-graph.ndjson` | Specifications, outcomes, bricks.yaml |
| `impl` | `implementation-graph.ndjson` | Python source files |
| `verify` | `verification-graph.ndjson` | Test files |

**Output:** Count of nodes generated, output file path.

**Exit code:** 0 on success, non-zero on error (parse failure, missing files).

**Note:** Rarely needed directly—`align` and `validate` rebuild automatically.

---

#### `jigy validate [target]`

**Purpose:** Validate JIG artifacts. Implies rebuild of relevant graphs.

**Targets:**
| Target | Validation Performed |
|--------|---------------------|
| (none) | All validation |
| `intent` | Specification files, outcome files, decorator references |
| `bricks` | Brick definitions, partition, layers, cycles |
| `full` | Explicit all (same as bare `validate`) |

**Output:** Validation results with errors and warnings.

**Exit code:** 0 if valid, non-zero if validation fails.

---

#### `jigy show [target]`

**Purpose:** Display structural information about the project.

**Targets:**
| Target | Information Displayed |
|--------|----------------------|
| (none) | Bricks and layers overview |
| `layers` | Layer hierarchy only |
| `bricks` | Brick details only |

**Output example (`jigy show`):**
```
Bricks (12):
  auth, users, orders, payments, notifications, ...

Layers:
  presentation
    └── api, web
  application
    └── auth, users, orders, payments
  domain
    └── core, notifications
  infrastructure
    └── db, cache, messaging
```

**Exit code:** 0 on success, non-zero if project not found or graphs missing.

---

#### `jigy audit`

**Purpose:** Show audit status and what needs attention.

**Output example:**
```
Audit Status:
  F→S: 45 edges (42 aligned, 2 diverged, 1 inconclusive)
  T→S: 38 edges (36 aligned, 2 diverged)
  T→F: 312 edges (298 covered, 14 not_covered)
  O→S: 12 edges (11 aligned, 1 diverged)

Pending (12 items):
  NEW (6):
    F→S: F-jig.cli.suggest.suggest_command → S-041
    ...
  CHANGED (4):
    F→S: F-jig.cli.layers.layers_command → S-040
      Last audited: commit abc1234
      To see changes: git diff abc1234..HEAD -- src/jig/cli/layers.py
    ...
```

**Exit code:** 0 if no pending items, non-zero if items need attention.

**CI usage:** `jigy audit` as a pipeline gate—fails if anything needs human review.

---

#### `jigy audit history <id>`

**Purpose:** Show audit history for a specific specification, function, or outcome.

**Arguments:**
- `<id>`: Node ID (e.g., `S-040`, `F-jig.cli.layers.layers_command`, `O-001`)

**Output example:**
```
Audit history for edges involving S-040:

  F→S: F-jig.cli.layers.layers_command → S-040
    2025-12-06  aligned  (tiered-v1, 0.9)  commit abc1234
    2025-11-20  aligned  (human-review, 1.0)  commit 9876543

  T→S: T-test_layers.test_layers_command → S-040
    2025-12-06  aligned  (tiered-v1, 0.85)  commit abc1234
```

**Exit code:** 0 on success, non-zero if ID not found.

---

#### `jigy audit compact`

**Purpose:** Compact the audit log, keeping only the latest record per edge.

**Output:**
```
Compacted audit-log.ndjson: 2847 records → 542 edges
```

**Exit code:** 0 on success.

---

### Global Options

| Option | Availability | Purpose |
|--------|--------------|---------|
| `--help` | All commands | Show help for the command |
| `--version` | Root only | Show JIG version |

No other global options exist. No `--verbose`, no `--project-root`, no `--format`.

---

## Common Workflows

### Daily Development

```bash
# Start of day: check alignment status
jigy align

# After making changes: quick validation
jigy validate

# Before commit: full alignment check
jigy align
```

### Investigation

```bash
# See project structure
jigy show

# See just layers
jigy show layers

# Check what needs audit review
jigy audit

# Investigate specific spec history
jigy audit history S-040
```

### CI Pipeline

```bash
# Basic gate: everything must be aligned
jigy align

# Strict gate: no pending audit items
jigy align && jigy audit

# Rebuild and validate separately (rare)
jigy rebuild && jigy validate full
```

### Targeted Rebuilds (Rare)

```bash
# Only rebuild implementation graph after code changes
jigy rebuild impl

# Only rebuild intent graph after spec changes
jigy rebuild intent

# Only rebuild verification graph after test changes
jigy rebuild verify
```

---

## Migration from Pre-A002 Commands

For users of the older noun-first command structure:

| Old Command | New Command |
|-------------|-------------|
| `jigy impl rebuild` | `jigy rebuild impl` |
| `jigy intent rebuild` | `jigy rebuild intent` |
| `jigy verify rebuild` | `jigy rebuild verify` |
| `jigy layers` | `jigy show layers` |
| `jigy layers suggest` | Removed (agent skill) |
| — | `jigy align` (new) |
| — | `jigy show` (new) |
| — | `jigy show bricks` (new) |
| — | `jigy audit` (new) |

### Removed Options

The following CLI options were removed in favor of sensible defaults:

| Removed Option | Reason |
|----------------|--------|
| `--project-root` | Auto-discovered |
| `--output` | Canonical paths per A001 |
| `--source-dir` | Auto-discovered (future: config) |
| `--test-dir` | Auto-discovered (future: config) |
| `--exclude` | Future: config file |
| `--format` | Human output only; use graph files for machine processing |
| `--verbose` | Output designed to be useful by default |
| `--strict/--lenient` | Always strict |
| `--skip-validation` | Validation always matters |
| `--no-timestamp` | Future: config file |
| `--summary` | Use `jigy show` variants |

---

## Future: Configuration File

Some project-specific settings may be supported via `jig.yaml` or `.jigrc` in the future:

```yaml
# jig.yaml (future consideration)
source_dir: src
test_dir: tests
exclude:
  - "**/migrations/**"
  - "**/generated/**"
deterministic: true  # omit timestamps for reproducible builds
```

This keeps the CLI clean while allowing customization where truly needed.

---

## Exit Codes

All commands follow standard exit code conventions:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation failure or error |
| 2 | Command usage error (bad arguments) |

Scripts can rely on exit codes for control flow:

```bash
jigy align && echo "All aligned!" || echo "Problems found"
```

---

## Extensibility

### Adding New Commands

New commands SHALL:

1. Follow verb-first naming: `jigy <verb> [noun]`
2. Have a clear, singular purpose
3. Produce human-readable output by default
4. Return appropriate exit codes
5. Require no flags for common operations
6. Be documented in this contract before implementation

### Reserved Command Names

The following command names are reserved for future use:

- `jigy init` — Initialize a new JIG project
- `jigy status` — Quick status check (may alias to `jigy align`)
- `jigy diff` — Show changes since last alignment
- `jigy report` — Generate detailed reports

---

## Consequences

### Benefits

- **Radical simplicity** — Only two global flags (`--help`, `--version`)
- **Zero configuration** — Works out of the box with sensible defaults
- **Consistent structure** — Verb-first, noun subcommands throughout
- **One obvious path** — `jigy align` for the common case
- **Clear separation** — `rebuild` (generate), `validate` (check), `show` (display), `audit` (track)
- **Scriptable** — Meaningful exit codes, predictable behavior
- **Memorable** — Small command surface, easy to learn

### Trade-offs

- **No JSON output** — Scripts use graph files directly or wait for future API
- **No verbose mode** — Output must be well-designed by default
- **Breaking change** — Users must update muscle memory and scripts
- **Power users** — Some flexibility traded for simplicity (mitigated by future config)

---

## Compliance

All CLI development SHALL comply with this architecture. New commands, options, or behaviors SHALL be documented here before implementation. Deviations require explicit amendment to this document.

This contract is evergreen—it evolves with JIG but maintains backward compatibility within major versions.

---

## Summary

The JIG CLI is designed around a single insight: **developers want to know if their code is aligned with their specifications**. Everything else is secondary.

```bash
# The one command you need to remember
jigy align
```

For those who need more control, the verb-first commands provide surgical precision:

```bash
jigy rebuild impl     # Just rebuild the code graph
jigy validate bricks  # Just validate brick structure
jigy show layers      # Just see the architecture
jigy audit            # Just see what needs review
```

No flags. No configuration. Just alignment.

---

_Align your specs, functions, and tests. `jigy align`._
