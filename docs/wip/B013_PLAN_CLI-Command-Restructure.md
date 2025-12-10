# B013 PLAN: CLI Command Restructure

**Status:** Plan
**Date:** 2025-12-09
**Implements:** B012 (CLI Simplification Proposal)
**Contract:** A002 (CLI Command Architecture)

---

## Overview

This plan restructures the JIG CLI from noun-first (`jigy impl rebuild`) to verb-first (`jigy rebuild impl`) command structure, conforming to the A002 contract.

**Scope:** Only commands with existing functionality. New commands requiring new backend functionality (e.g., `jigy audit`) are excluded.

---

## Current State → Target State

| Current Command | Target Command | Change Type |
|-----------------|----------------|-------------|
| `jigy rebuild` | `jigy align` | Rename (semantic) |
| `jigy impl rebuild` | `jigy rebuild impl` | Restructure |
| `jigy intent rebuild` | `jigy rebuild intent` | Restructure |
| `jigy verify rebuild` | `jigy rebuild verify` | Restructure |
| `jigy validate` | `jigy validate` | Unchanged |
| `jigy validate intent` | `jigy validate intent` | Unchanged |
| `jigy validate bricks` | `jigy validate bricks` | Unchanged |
| `jigy validate full` | `jigy validate full` | Unchanged |
| `jigy layers` | `jigy show layers` | Restructure |
| `jigy layers suggest` | — | **Removed** |
| — | `jigy show` | New (default) |
| — | `jigy show bricks` | New |
| — | `jigy rebuild` | New (all graphs) |

---

## Removed Options

Per A002, the following options are removed from all commands:

| Option | Removed From | Replacement |
|--------|--------------|-------------|
| `--project-root` | All | Auto-discovery |
| `--source-dir` | `impl rebuild` | Default `src/` |
| `--test-dir` | `verify rebuild` | Default `tests/` |
| `--output` | All rebuild | Canonical paths per A001 |
| `--exclude` | `impl rebuild` | Future config |
| `--format` | `validate` | Human only |
| `--verbose` | All | Designed output |
| `--strict/--lenient` | `impl rebuild` | Always strict |
| `--skip-validation` | `impl rebuild` | Always validate |
| `--no-timestamp` | All rebuild | Future config |
| `--summary` | `layers` | Use `show layers` |
| `--apply` | `layers suggest` | Command removed |

---

## Work Units

### WU1: Project Root Discovery Utility

**Goal:** Create a utility to auto-discover project root by walking up directories.

**Files:**
- `src/jig/cli/discovery.py` (new)

**Implementation:**
```python
def find_project_root(start_dir: Path = None) -> Path:
    """Walk up from start_dir looking for jig/ or .jig/ directory.

    Returns project root path.
    Raises ClickException if not found.
    """
```

**Acceptance Criteria:**
- Walks up from current directory (or specified start)
- Finds `jig/` directory
- Returns parent of `jig/` as project root
- Clear error message if not found: "Not in a JIG project. Run from a directory containing jig/ or run 'jigy init'."

---

### WU2: Restructure Rebuild Commands

**Goal:** Move rebuild subcommands from `jigy {noun} rebuild` to `jigy rebuild {noun}`.

**Files:**
- `src/jig/cli/main.py`

**Changes:**

1. **Create new `rebuild` group** (invoke_without_command=True):
   ```python
   @cli.group(invoke_without_command=True)
   @click.pass_context
   def rebuild(ctx):
       """Rebuild graph files."""
       if ctx.invoked_subcommand is None:
           # Rebuild all graphs
           rebuild_all()
   ```

2. **Add subcommands:**
   - `jigy rebuild impl` — move logic from `impl.rebuild()`
   - `jigy rebuild intent` — move logic from `intent.rebuild()`
   - `jigy rebuild verify` — move logic from `verify.rebuild()`

3. **Remove old groups:**
   - Remove `impl` group entirely
   - Remove `intent` group entirely
   - Remove `verify` group entirely

4. **Simplify options:** No options except inherited `--help`

**Example result:**
```python
@rebuild.command()
def impl():
    """Rebuild implementation graph."""
    project_root = find_project_root()
    # ... existing logic with defaults
```

**Acceptance Criteria:**
- `jigy rebuild` → rebuilds all three graphs (impl, verify, intent)
- `jigy rebuild impl` → rebuilds implementation graph only
- `jigy rebuild intent` → rebuilds intent graph only
- `jigy rebuild verify` → rebuilds verification graph only
- No options (uses auto-discovery and defaults)
- Exit code 0 on success, 1 on error

---

### WU3: Create `jigy align` Command

**Goal:** Rename current top-level `rebuild` to `align` with improved output.

**Files:**
- `src/jig/cli/main.py`

**Changes:**

1. **Rename command:**
   ```python
   @cli.command()
   def align():
       """Full workflow: rebuild all graphs, validate, show summary."""
   ```

2. **Improve output format** per A002 contract:
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

3. **Workflow steps:**
   1. Rebuild impl graph
   2. Rebuild verify graph
   3. Rebuild intent graph
   4. Validate all
   5. Display summary

4. **No options** except inherited `--help`

**Acceptance Criteria:**
- `jigy align` runs complete workflow
- Output matches A002 format (concise, informative)
- Exit code 0 if aligned, non-zero on failure
- Stops on first failure with clear message

---

### WU4: Restructure Show Commands

**Goal:** Create `jigy show` group replacing `jigy layers`.

**Files:**
- `src/jig/cli/main.py`
- `src/jig/cli/layers.py` (rename functions)

**Changes:**

1. **Create `show` group:**
   ```python
   @cli.group(invoke_without_command=True)
   @click.pass_context
   def show(ctx):
       """Display structural information."""
       if ctx.invoked_subcommand is None:
           # Default: show bricks + layers overview
           show_overview()
   ```

2. **Add subcommands:**
   - `jigy show layers` — existing `layers_command()` logic
   - `jigy show bricks` — new, shows brick list with details

3. **Remove `layers` group** entirely

4. **Remove `layers suggest`** — functionality moves to agent skill

**New `jigy show` output:**
```
Bricks (12):
  B-auth, B-users, B-orders, B-payments, ...

Layers:
  Layer 0 (foundation):
    └── B-core-utils (5 functions)
  Layer 1 (domain):
    └── B-auth (12 functions), B-users (8 functions)
  Layer 2 (application):
    └── B-api (15 functions)
```

**New `jigy show bricks` output:**
```
Bricks (12):
  B-auth
    Layer: 1
    Functions: 12
    Units: M-auth.session, M-auth.tokens

  B-users
    Layer: 1
    Functions: 8
    Units: M-users.manager, M-users.validation
  ...
```

**Acceptance Criteria:**
- `jigy show` → overview of bricks and layers
- `jigy show layers` → layer hierarchy (existing functionality)
- `jigy show bricks` → brick details
- No options (uses auto-discovery)
- `jigy layers suggest` is gone (error if attempted)

---

### WU5: Simplify Validate Commands

**Goal:** Remove `--format` and `--project-root` options from validate commands.

**Files:**
- `src/jig/cli/main.py`
- `src/jig/cli/validate.py`

**Changes:**

1. **Remove options from all validate commands:**
   - Remove `--project-root` (use auto-discovery)
   - Remove `--format` (always human output)

2. **Update function signatures:**
   ```python
   def validate_intent_command(project_root: Path) -> int:
   def validate_bricks_command(project_root: Path) -> int:
   def validate_full_command(project_root: Path) -> int:
   ```

3. **CLI commands become simple:**
   ```python
   @validate.command(name="intent")
   def validate_intent_cli():
       """Validate intent artifacts."""
       project_root = find_project_root()
       exit_code = validate_intent_command(project_root)
       sys.exit(exit_code)
   ```

**Acceptance Criteria:**
- `jigy validate` — validates all, human output
- `jigy validate intent` — validates intent, human output
- `jigy validate bricks` — validates bricks, human output
- `jigy validate full` — explicit full validation
- No options except `--help`

---

### WU6: Update Help Text and Root Command

**Goal:** Make `jigy` (bare) show proper help per A002.

**Files:**
- `src/jig/cli/main.py`

**Changes:**

1. **Update root group:**
   ```python
   @click.group(invoke_without_command=True)
   @click.version_option()
   @click.pass_context
   def cli(ctx):
       """JIG - Align your specs, functions, and tests."""
       if ctx.invoked_subcommand is None:
           click.echo(ctx.get_help())
   ```

2. **Update command docstrings** to be concise and match A002:
   - `align`: "Full workflow: rebuild all graphs, validate, show summary"
   - `rebuild`: "Rebuild graph files"
   - `validate`: "Validate JIG artifacts"
   - `show`: "Display structural information"

3. **Help output should show:**
   ```
   Usage: jigy [OPTIONS] COMMAND [ARGS]...

   JIG - Align your specs, functions, and tests.

   Options:
     --version  Show the version and exit.
     --help     Show this message and exit.

   Commands:
     align     Full workflow: rebuild all graphs, validate, show summary
     rebuild   Rebuild graph files
     show      Display structural information
     validate  Validate JIG artifacts
   ```

**Acceptance Criteria:**
- `jigy` shows help (not error)
- Help is concise and useful
- Commands listed alphabetically
- Only `--version` and `--help` shown

---

### WU7: Update Tests

**Goal:** Update CLI tests to match new command structure.

**Files:**
- `tests/cli/test_*.py`
- `tests/integration/test_cli.py`

**Changes:**

1. **Update command invocations:**
   - `["impl", "rebuild"]` → `["rebuild", "impl"]`
   - `["intent", "rebuild"]` → `["rebuild", "intent"]`
   - `["verify", "rebuild"]` → `["rebuild", "verify"]`
   - `["layers"]` → `["show", "layers"]`
   - `["rebuild"]` → `["align"]`

2. **Remove tests for removed features:**
   - `layers suggest` tests
   - Tests for removed options (`--format`, `--verbose`, etc.)

3. **Add tests for new commands:**
   - `jigy show` (default behavior)
   - `jigy show bricks`
   - `jigy rebuild` (all graphs)

4. **Update assertions** to not expect removed options in help

**Acceptance Criteria:**
- All existing tests pass with new command structure
- New commands have test coverage
- No tests for removed functionality

---

### WU8: Documentation Updates

**Goal:** Update user-facing documentation.

**Files:**
- `README.md` (if exists)
- Any other docs referencing CLI commands

**Changes:**

1. **Update command examples** throughout docs
2. **Remove references to removed options**
3. **Add migration note** for users of old commands

**Acceptance Criteria:**
- All documentation reflects new command structure
- No references to old commands or removed options

---

## Implementation Order

```
WU1 (discovery) ──┐
                  ├──→ WU2 (rebuild) ──┐
                  │                    ├──→ WU3 (align) ──┐
                  ├──→ WU4 (show) ─────┤                  │
                  │                    │                  ├──→ WU7 (tests) ──→ WU8 (docs)
                  └──→ WU5 (validate) ─┘                  │
                                                          │
WU6 (help) ───────────────────────────────────────────────┘
```

**Critical path:** WU1 → WU2 → WU3 → WU7

**Parallel work:** WU4, WU5, WU6 can proceed after WU1

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking existing scripts | Document migration path, consider deprecation warnings in v1 |
| Discovery fails in edge cases | Comprehensive error messages, explicit fallback instructions |
| Lost functionality (`layers suggest`) | Document as agent skill, ensure agent can perform this |

---

## Validation Checklist

After implementation, verify:

- [ ] `jigy` shows help (exit 0)
- [ ] `jigy --version` shows version
- [ ] `jigy align` runs full workflow
- [ ] `jigy rebuild` rebuilds all graphs
- [ ] `jigy rebuild impl` rebuilds impl graph only
- [ ] `jigy rebuild intent` rebuilds intent graph only
- [ ] `jigy rebuild verify` rebuilds verify graph only
- [ ] `jigy validate` validates all
- [ ] `jigy validate intent` validates intent only
- [ ] `jigy validate bricks` validates bricks only
- [ ] `jigy validate full` validates all (explicit)
- [ ] `jigy show` shows bricks + layers overview
- [ ] `jigy show layers` shows layer hierarchy
- [ ] `jigy show bricks` shows brick details
- [ ] `jigy impl rebuild` fails with helpful error (command not found)
- [ ] `jigy layers` fails with helpful error (command not found)
- [ ] `jigy layers suggest` fails with helpful error (command not found)
- [ ] No `--project-root` option on any command
- [ ] No `--format` option on any command
- [ ] No `--verbose` option on any command
- [ ] All tests pass
- [ ] Exit codes follow A002 contract (0=success, 1=error, 2=usage)

---

## Summary

This plan transforms the CLI from:
```bash
jigy impl rebuild --project-root ~/proj --source-dir src --verbose
jigy layers --project-root ~/proj --summary
```

To:
```bash
jigy rebuild impl
jigy show layers
```

8 work units. Critical path through WU1→WU2→WU3→WU7. Approximately 400-500 lines of code changes, mostly restructuring existing logic.
