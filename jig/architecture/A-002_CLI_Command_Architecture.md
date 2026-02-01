---
id: A-002
type: architecture
title: CLI Command Architecture
goals: [G-002, G-004]
specifications: [S-023, S-024, S-025, S-027, S-028, S-040, S-041, S-056, S-057, S-058, S-061, S-070, S-071, S-090, S-091, S-110, S-114, S-115]
---

# CLI Command Architecture

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

The CLI has minimal global flags plus universal output format flags:

**Global flags:**
| Flag | Purpose |
|------|---------|
| `--help` | Show help for any command |
| `--version` | Show version (root command only) |
| `--no-rebuild` | Skip automatic graph rebuild |

**Output format flags (all commands):**
| Flag | Purpose |
|------|---------|
| `-j/--json` | Machine-parseable JSON output |
| `-m/--markdown` | LLM-optimized markdown output |
| `-v/--verbose` | Additional detail in any format |

### 2. Sensible Discovery

JIG finds what it needs automatically:

- **Project root**: Walk up from current directory looking for `jig/` or `.jig/`
- **Source directory**: Default `src/`, configurable via `jig.toml`
- **Test directory**: Default `test/`, configurable via `jig.toml`
- **Output paths**: Canonical paths per A-001 (`jig/generated/*.ndjson`)

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

### 5. Three Output Modes

Every command supports three output modes per S-093:

| Mode | Flag | Audience | Characteristics |
|------|------|----------|-----------------|
| Human | (default) | Terminal | Clear headers, color, summaries |
| JSON | `-j` | CI/Agents | Single-line, typed, complete |
| Markdown | `-m` | LLMs | Structured, semantic, dense |

Human output is the default—crafted for terminal reading with clear section headers, color (respects `NO_COLOR`), and summary counts. Exit codes work for scripting (success = 0, failure = non-zero).

JSON and Markdown modes enable CI pipelines, AI agents, and LLM context injection without fragile text parsing.

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
├── mend [--dry-run]            # Auto-fix validation errors
├── show [target]               # Display structural information
│   ├── (none)                  # Bricks + layers overview
│   ├── layers                  # Layer hierarchy only
│   └── bricks                  # Brick details only
├── towers                      # Display tower structure
├── matrix                      # Display layer × tower grid
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

#### `jigy mend`

**Purpose:** Auto-fix validation errors that have machine-applicable fixes.

**Options:**
| Option | Purpose |
|--------|---------|
| `--dry-run` | Show what would be fixed without applying changes |

**Behavior:**
1. Run validation to identify errors
2. For each error with `auto: true` in its fix template, apply the fix
3. Report changes made (or to be made in dry-run mode)

**Fix Types (per S-104):**
| Action | Description |
|--------|-------------|
| `set_field` | Set a frontmatter field value |
| `rename_file` | Rename a file to match conventions |
| `update_header` | Update H1 header to match title |
| `manual_review` | Cannot be auto-fixed (skipped) |

**Output:**
- Human mode: List of fixes applied with file paths
- JSON mode: Structured fix report per S-104
- Dry-run: "Would fix..." prefixes

**Exit code:** 0 if all auto-fixable errors resolved, 1 if manual fixes remain.

**Related specs:** S-104 (fix templates), S-105 (mend command), S-106 (dry-run mode)

---

#### `jigy show [target]`

**Purpose:** Display structural information about the project.

**Targets:**
| Target | Information Displayed |
|--------|----------------------|
| (none) | Bricks and layers overview |
| `layers` | Layer hierarchy only |
| `bricks` | Brick details only |

**Exit code:** 0 on success, non-zero if project not found or graphs missing.

---

#### `jigy towers`

**Purpose:** Display tower structure with brick counts per tower.

**Exit code:** 0 on success.

---

#### `jigy matrix`

**Purpose:** Display layer × tower grid showing brick distribution.

**Exit code:** 0 on success.

---

#### `jigy audit`

**Purpose:** Show audit status and what needs attention.

**Exit code:** 0 if no pending items, non-zero if items need attention.

**CI usage:** `jigy audit` as a pipeline gate—fails if anything needs human review.

---

### Global Options

| Option | Availability | Purpose |
|--------|--------------|---------|
| `--help` | All commands | Show help for the command |
| `--version` | Root only | Show JIG version |
| `--no-rebuild` | Root | Skip automatic graph rebuild before commands |
| `-j/--json` | All commands | Machine-parseable JSON output (S-026) |
| `-m/--markdown` | All commands | LLM-optimized markdown output (S-094) |
| `-v/--verbose` | All commands | Additional detail in any format |

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
