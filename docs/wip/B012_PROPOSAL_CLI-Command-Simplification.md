# B012 PROPOSAL: CLI Command Simplification

**Status:** Proposal
**Date:** 2025-12-09
**Related:** JIG-CLI-Commands.md, J023 (Audit Records and Triggers)

---

## Context

The current JIG CLI has grown organically, resulting in:
- Inconsistent command structure (noun-first vs verb-first)
- Too many options and flags
- Options that should be configuration
- Verbose flags that clutter the interface

This proposal simplifies the CLI to a clean, minimal, verb-first structure.

---

## Design Principles

1. **Verb-first commands** - actions are verbs (`rebuild`, `validate`, `show`, `audit`)
2. **Bare `jigy` shows help** - standard CLI pattern (like `git`)
3. **One "do everything" command** - `jigy align` rebuilds, validates, shows summary
4. **Implicit rebuild** - `validate` and `align` rebuild automatically
5. **Noun subcommands** - `jigy rebuild intent`, `jigy show layers`
6. **Minimal options** - sensible defaults, configuration over flags
7. **No verbose flags** - output is designed to be useful by default
8. **Directories are discovered** - no `--source-dir`, `--test-dir`, `--output` flags
9. **Always strict** - fail fast on errors, no lenient mode

---

## Proposed Command Structure

### Core Commands

| Command | Description |
|---------|-------------|
| `jigy` | Show help and usage |
| `jigy align` | **Do everything:** rebuild all graphs, validate all, show summary |
| `jigy rebuild` | Rebuild all graphs |
| `jigy rebuild intent` | Rebuild intent graph only |
| `jigy rebuild impl` | Rebuild implementation graph only |
| `jigy rebuild verify` | Rebuild verification graph only |
| `jigy validate` | Validate all (implies rebuild) |
| `jigy validate intent` | Validate intent graph only |
| `jigy validate bricks` | Validate bricks only |
| `jigy validate full` | Validate everything (explicit) |
| `jigy show` | Show bricks + layers (default structural overview) |
| `jigy show layers` | Show layer hierarchy |
| `jigy show bricks` | Show bricks |

### Audit Commands

| Command | Description |
|---------|-------------|
| `jigy audit` | Show audit status and pending items (what needs audit) |
| `jigy audit history <id>` | Show audit history for a spec, function, or outcome |
| `jigy audit compact` | Compact the audit log (keep latest per edge) |

### Global Options

Only two global options exist:

| Option | Description |
|--------|-------------|
| `--help` | Show help for any command |
| `--version` | Show version (root command only) |

**That's it.** No `--project-root`, no `--verbose`, no `--format`. JIG discovers the project root by walking up from the current directory looking for `jig/` or `.jig/`. Output is human-readable and designed to be useful.

---

## Command Details

### `jigy align`

The "do everything" command. Runs the full JIG workflow:

1. Rebuild all graphs (intent, impl, verify)
2. Validate all artifacts
3. Display summary: specs, functions, tests, coverage, validation status

**Why "align"?** JIG is fundamentally about alignment - ensuring specs, functions, and tests are aligned. The term fits the domain and is a clear verb.

```bash
$ jigy align
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

### `jigy rebuild [target]`

Rebuild graphs without validation. Rarely needed directly since `validate` and `align` rebuild automatically.

```bash
$ jigy rebuild          # all graphs
$ jigy rebuild intent   # intent graph only
$ jigy rebuild impl     # implementation graph only
$ jigy rebuild verify   # verification graph only
```

### `jigy validate [target]`

Validate artifacts. Implies rebuild of relevant graphs.

```bash
$ jigy validate         # validate all
$ jigy validate intent  # validate intent graph
$ jigy validate bricks  # validate bricks
$ jigy validate full    # explicit "validate everything"
```

### `jigy show [target]`

Display structural information about the project. Without a target, shows bricks and layers overview.

```bash
$ jigy show             # show bricks + layers (default)
$ jigy show layers      # show layer hierarchy only
$ jigy show bricks      # show brick details only
```

```bash
$ jigy show
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

### `jigy audit`

Show audit status and what needs attention.

```bash
$ jigy audit
Audit Status:
  F→S: 45 edges (42 aligned, 2 diverged, 1 inconclusive)
  T→S: 38 edges (36 aligned, 2 diverged)
  T→F: 312 edges (298 covered, 14 not_covered)
  O→S: 12 edges (11 aligned, 1 diverged)

Pending (12 items):
  NEW (6):
    F→S: F-jig.cli.suggest.suggest_command → S-041
    T→S: T-test_suggest.test_suggest_basic → S-041
    ...
  CHANGED (4):
    F→S: F-jig.cli.layers.layers_command → S-040
      Last audited: commit abc1234
      To see changes: git diff abc1234..HEAD -- src/jig/cli/layers.py
    ...
  REMOVED (2):
    F→S: F-jig.old.deprecated_function → S-015
    ...
```

**CI usage:** `jigy audit` exits non-zero if there are pending items, making it suitable for CI gates without special flags.

### `jigy audit history <id>`

Show audit history for a specific node.

```bash
$ jigy audit history S-040
Audit history for edges involving S-040:

  F→S: F-jig.cli.layers.layers_command → S-040
    2025-12-06  aligned  (tiered-v1, 0.9)  commit abc1234
    2025-11-20  aligned  (human-review, 1.0)  commit 9876543

  T→S: T-test_layers.test_layers_command → S-040
    2025-12-06  aligned  (tiered-v1, 0.85)  commit abc1234
```

### `jigy audit compact`

Compact the audit log to reduce size. Keeps only the latest record per edge.

```bash
$ jigy audit compact
Compacted audit-log.ndjson: 2847 records → 542 edges
```

---

## Migration from Current Commands

| Current | New |
|---------|-----|
| `jigy impl rebuild` | `jigy rebuild impl` |
| `jigy intent rebuild` | `jigy rebuild intent` |
| `jigy verify rebuild` | `jigy rebuild verify` |
| `jigy rebuild` | `jigy rebuild` (unchanged) |
| `jigy validate` | `jigy validate` (unchanged) |
| `jigy validate bricks` | `jigy validate bricks` (unchanged) |
| `jigy validate intent` | `jigy validate intent` (unchanged) |
| `jigy validate full` | `jigy validate full` (unchanged) |
| `jigy layers` | `jigy show layers` |
| `jigy layers suggest` | **Removed** (agent skill) |
| (none) | `jigy align` (new) |
| (none) | `jigy show` (new) |
| (none) | `jigy show bricks` (new) |
| (none) | `jigy audit` (new, from J023) |
| (none) | `jigy audit history` (new, from J023) |
| (none) | `jigy audit compact` (new, from J023) |

---

## Removed Commands

| Removed | Reason |
|---------|--------|
| `jigy layers suggest` | Non-deterministic, better as agent skill |
| `jigy impl` (bare) | Just showed help, not useful |
| `jigy intent` (bare) | Just showed help, not useful |
| `jigy verify` (bare) | Just showed help, not useful |

---

## Removed Options

The following CLI options are removed in favor of sensible defaults or future configuration:

| Removed Option | Was On | Reason |
|----------------|--------|--------|
| `--project-root DIR` | All | Auto-discovered by walking up to find `jig/` |
| `--output PATH` | rebuild commands | Use canonical paths per A001 |
| `--source-dir DIR` | impl rebuild | Auto-discovered or future config |
| `--test-dir DIR` | verify rebuild | Auto-discovered or future config |
| `--exclude PATTERN` | impl rebuild | Future config file |
| `--format [human\|json]` | validate, audit | Human output only; scripts can parse or use future API |
| `--verbose` / `-v` | various | Output designed to be useful by default |
| `--summary` | layers | Removed with layers command |
| `--strict / --lenient` | impl rebuild | Always strict |
| `--skip-validation` | impl rebuild | Validation always runs |
| `--no-timestamp` | rebuild commands | Future config file |
| `--pending-only` | audit | Just show everything |
| `--exit-code` | audit | Default behavior: exit non-zero on pending |
| `--keep-last N` | audit compact | Always keep latest only |
| `--apply` | layers suggest | Command removed |

### Future: Configuration File

Some removed options may return as configuration in a future `jig.yaml` or `.jigrc`:

```yaml
# jig.yaml (future)
source_dir: src
test_dir: tests
exclude:
  - "**/migrations/**"
  - "**/generated/**"
deterministic: false  # omit timestamps
```

This keeps the CLI clean while allowing project-specific customization.

---

## Examples

```bash
# Daily workflow - just run align
$ jigy align

# Quick validation check
$ jigy validate

# See project structure
$ jigy show

# Check what needs audit before a release
$ jigy audit

# CI pipeline
$ jigy align && jigy audit
```

---

## Open Questions

1. **Future commands?** Room for `jigy audit record` or similar when we implement audit recording.

2. **`jigy show` evolution?** Currently shows bricks + layers. May expand to show other structural info as JIG evolves.

---

## Consequences

### Benefits
- **Radically simpler** - only `--help` and `--version` flags
- **Zero configuration required** - sensible defaults work out of the box
- **Clean, consistent verb-first structure**
- **One obvious "do everything" command** (`align`)
- **Clear separation**: `rebuild` (generate), `validate` (check), `show` (display), `audit` (track)
- **Intuitive for new users** - no flag soup to learn

### Trade-offs
- Breaking change from current command structure
- Users need to update scripts/muscle memory
- No JSON output (scripts must parse human output or wait for future API)
- `layers suggest` functionality moves to agent
- Power users lose some flexibility (mitigated by future config file)

---

## Summary: Before and After

**Before (current):**
```bash
jigy impl rebuild --project-root ~/proj --source-dir src --exclude "*.test.py" \
  --output out.ndjson --verbose --strict --no-timestamp --skip-validation
```

**After (proposed):**
```bash
jigy rebuild impl
```

**Before (current):**
```bash
jigy validate --project-root ~/proj --format json
jigy layers --project-root ~/proj --summary --verbose
```

**After (proposed):**
```bash
jigy validate
jigy show
```

---

_Align your specs, functions, and tests. `jigy align`._
