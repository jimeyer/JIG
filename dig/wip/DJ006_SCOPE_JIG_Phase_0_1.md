---
title: JIG CLI Phase 0 and 1 Implementation
type: scope
status: active
created: 1736207400
created_human: 2026-01-06 16:00 CST
parent: "[[DJ005_SCOPE_CLI_Implementation]]"
children: []
---
# JIG CLI Phase 0 and 1 Implementation

## Executive Summary

This scope document details the implementation work for JIG CLI Phase 0 (Flag Unification) and Phase 1 (Command Restructuring). Based on codebase exploration, the work is more focused than initially estimated—existing infrastructure can be leveraged.

**Key Findings:**
- CLI uses Click framework with well-structured command groups
- `validate` commands already have internal `output_format` parameter—just needs CLI flag exposure
- `layers.py` exists but is orphaned (not registered)—needs wiring, not writing
- `towers` and `matrix` are standalone commands—need to move under `show`

---

## Part I: Current State Analysis

### CLI Framework

- **Framework:** Click
- **Entry Point:** `jig.cli.main:cli`
- **Command Ordering:** Custom `OrderedGroup` class

### Current Command Structure

```
jigy
├── align                    # Full workflow (rebuild → validate → summary)
├── validate                 # Validation group
│   ├── (default)            # Full validation
│   ├── intent               # Intent artifacts only
│   ├── bricks               # Brick definitions only
│   └── full                 # Explicit full validation
├── show                     # Display group
│   ├── (default)            # Overview
│   ├── layers               # Layer hierarchy
│   ├── bricks               # Brick details
│   ├── charter              # Charter.md
│   ├── goals                # Goals with supporting artifacts
│   └── architecture [ID]    # Architecture documents
├── audit                    # Audit group
│   └── coverage             # Coverage audit pipeline
├── rebuild                  # Rebuild group
│   ├── (default)            # All graphs
│   ├── impl                 # Implementation graph
│   ├── intent               # Intent graph
│   └── verify               # Verification graph
├── towers [ID]              # Tower structure (ROOT - should move)
└── matrix                   # Layer × tower grid (ROOT - should move)
```

### Current Flag Support

| Flag | Status | Notes |
|------|--------|-------|
| `--help` | Implemented | Built-in Click |
| `--version` | Implemented | Built-in Click |
| `--no-rebuild` | Implemented | S-071, works on validate/show/audit |
| `-j` / `--json` | **Missing** | validate has internal support, no CLI flag |
| `-m` / `--markdown` | **Missing** | Not implemented anywhere |
| `-v` / `--verbose` | **Missing** | Not implemented anywhere |

### Existing Output Infrastructure

**Location:** `src/jig/validation/reporting.py`

```python
format_as_json(results: dict[str, ValidationResult]) -> str
format_validation_results(results: list[ValidationResult]) -> str
```

The `validate` commands already accept `output_format` parameter internally but it's hardcoded to `"human"` in the CLI layer.

### Orphaned Files

| File | Status | Action Needed |
|------|--------|---------------|
| `src/jig/cli/layers.py` | Not registered in CLI | Wire into `show layers` |
| `src/jig/cli/verify.py` | Not registered in CLI | Delete (redundant with rebuild verify) |

---

## Part II: Phase 0 — Flag Unification

### Goal

All commands support `-j`, `-m`, `-v` flags consistently.

### Work Items

#### P0.1: Create OutputFormat Infrastructure

**File:** `src/jig/cli/output.py` (new)

```python
from enum import Enum
from typing import Any
import json
import click

class OutputFormat(Enum):
    HUMAN = "human"
    JSON = "json"
    MARKDOWN = "markdown"

def add_output_options(func):
    """Decorator to add -j/-m/-v flags to a command."""
    func = click.option('-j', '--json', 'output_json', is_flag=True,
                        help='Output as JSON')(func)
    func = click.option('-m', '--markdown', 'output_markdown', is_flag=True,
                        help='Output as markdown')(func)
    func = click.option('-v', '--verbose', is_flag=True,
                        help='Verbose output')(func)
    return func

def resolve_format(output_json: bool, output_markdown: bool) -> OutputFormat:
    """Resolve flags to OutputFormat, error if mutually exclusive."""
    if output_json and output_markdown:
        raise click.UsageError("-j/--json and -m/--markdown are mutually exclusive")
    if output_json:
        return OutputFormat.JSON
    if output_markdown:
        return OutputFormat.MARKDOWN
    return OutputFormat.HUMAN

def output_result(data: Any, fmt: OutputFormat, verbose: bool = False) -> str:
    """Format data according to output format."""
    # Implementation varies by data type
    ...
```

**Tasks:**
- [ ] Create `output.py` module
- [ ] Implement `OutputFormat` enum
- [ ] Implement `add_output_options` decorator
- [ ] Implement `resolve_format` function
- [ ] Implement base `output_result` function

#### P0.2: Add Flags to CLI Parser

**File:** `src/jig/cli/main.py`

Update command registration to use the `@add_output_options` decorator.

**Tasks:**
- [ ] Import output module
- [ ] Apply decorator to all command groups/commands
- [ ] Pass format options through context or parameters

#### P0.3: Refactor `validate` Commands

**File:** `src/jig/cli/validate.py`

The internal `output_format` parameter already exists. Need to:
1. Add CLI flags
2. Wire flags to existing parameter
3. Add markdown output support

**Current (line ~130):**
```python
@validate.command(name="intent")
@click.pass_context
def validate_intent(ctx) -> None:
    exit_code = validate_intent_command(config, skip_rebuild=skip_rebuild)
```

**Target:**
```python
@validate.command(name="intent")
@add_output_options
@click.pass_context
def validate_intent(ctx, output_json, output_markdown, verbose) -> None:
    fmt = resolve_format(output_json, output_markdown)
    exit_code = validate_intent_command(config, skip_rebuild=skip_rebuild,
                                         output_format=fmt.value, verbose=verbose)
```

**Tasks:**
- [ ] Add flags to `validate` group default
- [ ] Add flags to `validate intent`
- [ ] Add flags to `validate bricks`
- [ ] Add flags to `validate full`
- [ ] Add markdown formatting to `reporting.py`
- [ ] Update `validate_intent_command()` for verbose mode
- [ ] Update `validate_bricks_command()` for verbose mode

#### P0.4: Refactor `rebuild` Commands

**File:** `src/jig/cli/rebuild.py`

Currently no output format support. Add minimal output formatting.

**Tasks:**
- [ ] Add flags to `rebuild` group default
- [ ] Add flags to `rebuild impl`
- [ ] Add flags to `rebuild intent`
- [ ] Add flags to `rebuild verify`
- [ ] Implement JSON output (metrics: graphs rebuilt, time)
- [ ] Implement markdown output

#### P0.5: Refactor `align` Command

**File:** `src/jig/cli/rebuild.py`

`align` is a compound command (rebuild + validate + summary).

**Tasks:**
- [ ] Add flags to `align`
- [ ] Pass format through to sub-operations
- [ ] Implement combined JSON output
- [ ] Implement combined markdown output

#### P0.6: Refactor `show` Commands

**File:** `src/jig/cli/show.py`

**Tasks:**
- [ ] Add flags to `show` group default
- [ ] Add flags to `show layers`
- [ ] Add flags to `show bricks`
- [ ] Add flags to `show charter`
- [ ] Add flags to `show goals`
- [ ] Add flags to `show architecture`
- [ ] Implement JSON output for each
- [ ] Implement markdown output for each

#### P0.7: Refactor `towers` Command

**File:** `src/jig/cli/towers.py`

**Tasks:**
- [ ] Add flags to `towers`
- [ ] Implement JSON output (tower list with brick counts)
- [ ] Implement markdown output

#### P0.8: Refactor `matrix` Command

**File:** `src/jig/cli/towers.py`

**Tasks:**
- [ ] Add flags to `matrix`
- [ ] Implement JSON output (2D grid data)
- [ ] Implement markdown output (table format)

#### P0.9: Refactor `audit` Commands

**File:** `src/jig/cli/audit.py`

**Tasks:**
- [ ] Add flags to `audit` group
- [ ] Add flags to `audit coverage`
- [ ] Implement JSON output
- [ ] Implement markdown output

#### P0.10: Add Tests

**File:** `tests/cli/test_output_modes.py` (new)

**Tasks:**
- [ ] Test every command × every flag combination
- [ ] Test `-j -m` produces error
- [ ] Test JSON output is valid JSON
- [ ] Test markdown output is valid markdown
- [ ] Test verbose adds detail

### Phase 0 Success Criteria

1. Every command accepts `-j`, `-m`, and `-v` flags
2. `-j -m` produces clear error message
3. JSON output is always single-line (compact)
4. Exit codes: 0 = success, 1 = validation failure, 2 = usage error

---

## Part III: Phase 1 — Command Restructuring

### Goal

Reorganize commands to match target structure. No new functionality.

### Work Items

#### P1.1: Move `towers` → `show towers`

**Files:**
- `src/jig/cli/towers.py` (source)
- `src/jig/cli/show.py` (target)

**Tasks:**
- [ ] Move `towers_command()` function to `show.py`
- [ ] Register as `show.command(name="towers")`
- [ ] Remove standalone `towers` from `main.py`
- [ ] Update `OrderedGroup` command list

#### P1.2: Move `matrix` → `show matrix`

**Files:**
- `src/jig/cli/towers.py` (source)
- `src/jig/cli/show.py` (target)

**Tasks:**
- [ ] Move `matrix_command()` function to `show.py`
- [ ] Register as `show.command(name="matrix")`
- [ ] Remove standalone `matrix` from `main.py`
- [ ] Delete `towers.py` after moves complete

#### P1.3: Wire Orphaned `layers` Command

**Files:**
- `src/jig/cli/layers.py` (orphaned)
- `src/jig/cli/show.py` (target)

The `show layers` command exists but may use different implementation than orphaned `layers.py`.

**Tasks:**
- [ ] Compare `show.py` layers implementation vs `layers.py`
- [ ] Merge any missing functionality from `layers.py`
- [ ] Delete `layers.py` after merge
- [ ] Delete orphaned `verify.py`

#### P1.4: Update Documentation

**Tasks:**
- [ ] Update CLI help text to reflect new structure
- [ ] Update any docs referencing old command names

#### P1.5: Add Tests

**File:** `tests/cli/test_command_structure.py` (new)

**Tasks:**
- [ ] Test `show towers` works
- [ ] Test `show matrix` works
- [ ] Test old commands removed (no `jigy towers`)
- [ ] Test all show subcommands listed in help

### Phase 1 Success Criteria

1. `jigy show towers` works (same output as old `jigy towers`)
2. `jigy show matrix` works (same output as old `jigy matrix`)
3. `jigy towers` returns "command not found"
4. All restructured commands support `-j`, `-m`, `-v` flags
5. No orphaned CLI files remain

---

## Part IV: Implementation Order

### Recommended Sequence

```
P0.1  OutputFormat infrastructure     ← Foundation for everything
P0.2  Add flags to CLI parser         ← Makes flags available
P0.3  Refactor validate               ← Easiest (existing internal support)
P0.10 Add tests for validate          ← Verify pattern works
P0.4  Refactor rebuild                ← Apply pattern
P0.5  Refactor align                  ← Apply pattern
P0.6  Refactor show                   ← Apply pattern
P0.7  Refactor towers                 ← Apply pattern (before move)
P0.8  Refactor matrix                 ← Apply pattern (before move)
P0.9  Refactor audit                  ← Apply pattern
P1.1  Move towers → show towers       ← Restructure
P1.2  Move matrix → show matrix       ← Restructure
P1.3  Wire/cleanup orphaned files     ← Cleanup
P1.4  Update documentation            ← Finalize
P1.5  Add structure tests             ← Verify
```

### First Commit Scope

Start with:
- P0.1: Create `output.py`
- P0.2: Add flags to validate commands only
- P0.3: Wire flags to existing validate infrastructure
- Partial P0.10: Tests for validate output modes

This validates the pattern before applying it everywhere.

---

## Part V: File Changes Summary

### New Files

| File | Purpose |
|------|---------|
| `src/jig/cli/output.py` | OutputFormat enum, flag decorator, formatters |
| `tests/cli/test_output_modes.py` | Flag combination tests |
| `tests/cli/test_command_structure.py` | Structure tests |

### Modified Files

| File | Changes |
|------|---------|
| `src/jig/cli/main.py` | Import output module, update command registration |
| `src/jig/cli/validate.py` | Add flag decorator, wire to existing params |
| `src/jig/cli/rebuild.py` | Add flag decorator, implement formatters |
| `src/jig/cli/show.py` | Add flag decorator, implement formatters, absorb towers/matrix |
| `src/jig/cli/audit.py` | Add flag decorator, implement formatters |
| `src/jig/validation/reporting.py` | Add markdown formatter |

### Deleted Files

| File | Reason |
|------|--------|
| `src/jig/cli/towers.py` | Moved to show.py |
| `src/jig/cli/layers.py` | Orphaned, merged to show.py |
| `src/jig/cli/verify.py` | Orphaned, redundant |

---

## Part VI: Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing scripts | No deprecation needed (single user) |
| Inconsistent flag behavior | Shared decorator enforces consistency |
| Missing edge cases in output | Comprehensive test matrix |
| Merge conflicts with other work | Complete Phase 0 before Phase 1 |

---

## References

- `dig/wip/DJ005_SCOPE_CLI_Implementation.md` — Parent implementation strategy
- `dig/wip/DJ001_CONCEPT_CLI_Design_Manifesto.md` — Design principles
- `jig/specifications/S-026_JSON_Output_Format.md` — JSON output spec
- `jig/specifications/S-061_Minimal_Global_Options.md` — Global options spec

---

*This document scopes Phase 0 and Phase 1 for JIG CLI. DIG CLI will follow in a separate scope document.*
