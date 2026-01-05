---
title: "SCOPE: JIG Agent Tools Implementation"
type: scope
status: active
created: 1736128800
created_human: "2026-01-05 17:00 CST"
parent: null
children: []
---
# SCOPE: JIG Agent Tools Implementation

**ID:** C014
**Status:** Draft
**Date:** 2026-01-05
**Implements:** C006_PROPOSAL_JIG_Tools_Skills_Architecture.md, C007_PROPOSAL_Gitignore_Generated_Graphs.md

---

## Executive Summary

This scope document defines the work required to implement agent-oriented tooling for JIG. The goal is to transform JIG from a human-oriented CLI into a dual-mode tool that serves both humans (readable output) and AI agents (structured JSON output with graph queries).

**Two complementary proposals being implemented:**

1. **C006**: Agent tools architecture — graph queries, structured validation, artifact creation
2. **C007**: Gitignore generated graphs — `jigy init`, auto-create README, templates

**Core Insight:** Agents want to query the JIG graph directly, not reconstruct it from files. Every tool call saved is context that can be used for actual work.

### Alignment with Charter Goals

This implementation directly supports the five Charter goals:

| Charter Goal | How Agent Tools Support It |
|--------------|---------------------------|
| **G-001: Grounding in Reality** | Graph queries let agents query actual code structure instead of guessing |
| **G-002: Continuity Across Sessions** | `jigy context` provides dynamic project state; JSON output enables programmatic extraction |
| **G-003: Enforcing Constraints** | Enhanced validation with error codes and fix hints |
| **G-004: Intent Alignment** | `jigy new spec` ensures specs are created with correct format |
| **G-005: Full Traceability** | `jigy audit gaps` identifies breaks in the S-F-T traceability chain |

### Alignment with A-002 CLI Architecture

Per A-002 (CLI Command Architecture), this work follows established CLI patterns:

| A-002 Principle | How C014 Complies |
|-----------------|-------------------|
| **Verb-first commands** | `show`, `audit`, `new`, `context` — actions users take |
| **Minimal global flags** | Only `--help`, `--version`, `--no-rebuild` (per A-002) |
| **Human output by default** | Rich terminal output; `--json` per-command for agents |
| **Progressive disclosure** | `jigy context` → `jigy context spec S-042` |
| **Fail fast, fail clearly** | Errors include tips for both humans and agents |

---

## CLI Design Philosophy

### Alignment with A-002

A-002 establishes the CLI contract. C014 extends it while respecting these principles:

1. **Verb-First**: Commands describe actions (`show`, `audit`, `new`, `context`)
2. **Git Model**: Human output by default, minimal flags, auto-discovery
3. **Three Global Flags Only**: `--help`, `--version`, `--no-rebuild`
4. **Progressive Disclosure**: Simple commands, optional narrowing

### Output Philosophy

**Human output by default** (following Git's model, per A-002):

```bash
$ jigy new spec "Token Refresh"
Created S-094: Token Refresh
  File: jig/specifications/S-094_Token_Refresh.md

$ jigy rebuild
Rebuilt 3 graphs:
  impl: 342 nodes, 1204 edges
  verify: 156 nodes, 89 edges
  intent: 128 nodes, 312 edges
```

**Machine output on request** (`--json` per-command, not global):

```bash
$ jigy new spec "Token Refresh" --json
{"id":"S-094","file":"jig/specifications/S-094_Token_Refresh.md"}

$ jigy rebuild --json
{"impl":{"nodes":342,"edges":1204},"verify":{"nodes":156,"edges":89},"intent":{"nodes":128,"edges":312}}
```

**Quiet mode for scripts** (`--quiet` suppresses success output):

```bash
$ jigy new spec "Token Refresh" --quiet && echo "done"
done
```

### Flag Strategy

Per A-002, global flags are minimal:

| Flag | Scope | Purpose |
|------|-------|---------|
| `--help` | Global | Show help |
| `--version` | Root only | Show version |
| `--no-rebuild` | Global | Skip auto-rebuild |

Command-specific flags:

| Flag | Commands | Purpose |
|------|----------|---------|
| `--json` | Most commands | Machine-readable output |
| `--quiet` | Mutating commands | Suppress success output |
| `--markdown` | `context` only | LLM-optimized markdown |

---

## Command Hierarchy

Per A-002 verb-first principle, the complete CLI structure:

```
jigy
├── align                     # Full workflow (rebuild + validate + summary)
│
├── context [target]          # Dynamic project briefing (FIRST-CLASS)
│   ├── (none)                # Full project context
│   ├── spec <id>             # Context around a specification
│   ├── brick <id>            # Context around a brick
│   ├── outcome <id>          # Context around an outcome
│   └── goal <id>             # Context around a charter goal
│
├── show <what>               # Display artifacts (static)
│   ├── spec <id>             # Single spec with S-F-T triangle
│   ├── specs                 # List specs (with --search, --unimplemented, etc.)
│   ├── outcome <id>          # Single outcome
│   ├── outcomes              # List outcomes
│   ├── brick <id>            # Single brick
│   ├── bricks                # List bricks
│   ├── layers                # Layer hierarchy
│   ├── towers                # Tower structure
│   ├── matrix                # Layer × tower grid
│   ├── charter               # Charter document
│   ├── goals                 # Goal list
│   └── architecture          # Architecture documents
│
├── audit <what>              # Find issues
│   ├── gaps                  # Unimplemented/unverified specs
│   └── coverage              # Coverage report
│
├── rebuild [what]            # Rebuild graphs
│   ├── (none)                # All graphs
│   ├── impl                  # Implementation graph
│   ├── intent                # Intent graph
│   └── verify                # Verification graph
│
├── validate [what]           # Validate artifacts
│   ├── (none)                # All validation
│   ├── intent                # Intent artifacts
│   └── bricks                # Brick definitions
│
├── new <type> <title>        # Create artifacts (auto-assigns ID)
│   ├── spec                  # New specification
│   ├── outcome               # New outcome
│   └── architecture          # New architecture doc
│
└── init                      # Initialize JIG in project
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `context` is first-class | It's synthesized, not static; distinct from `show` |
| No `jigy next-id` | `jigy new` auto-assigns and returns the ID |
| No `jigy search specs` | Use `jigy show specs --search "query"` |
| `towers`/`matrix` under `show` | They display artifacts, verb-first consistency |
| `--json` per-command | A-002 limits global flags to 3 |

---

## Current State Analysis

### Existing CLI Commands

| Command | Status | Agent-Friendly? |
|---------|--------|-----------------|
| `jigy rebuild` | Complete | Partial — no JSON |
| `jigy validate` | Complete | Partial — has `--json` but limited |
| `jigy show layers` | Complete | No JSON mode |
| `jigy show bricks` | Complete | No JSON mode |
| `jigy show charter` | Complete | No JSON mode |
| `jigy show goals` | Complete | No JSON mode |
| `jigy show architecture` | Complete | No JSON mode |
| `jigy towers` | Complete | **Move to** `show towers` |
| `jigy matrix` | Complete | **Move to** `show matrix` |
| `jigy audit coverage` | Complete | No JSON mode |

### Missing Commands

| Command | Priority | Description |
|---------|----------|-------------|
| `jigy context` | P0 | Dynamic project briefing |
| `jigy context spec <id>` | P0 | Context around a spec |
| `jigy show spec <id>` | P0 | Single spec with S-F-T |
| `jigy show specs` | P0 | List specs with filtering |
| `jigy audit gaps` | P0 | Find coverage gaps |
| `jigy init` | P1 | Initialize JIG project |
| `jigy new spec` | P1 | Create specification |
| `jigy new outcome` | P1 | Create outcome |

---

## PART A: The `context` Command (First-Class)

### A.1 Why `context` is First-Class

Per our design discussion, `context` is fundamentally different from `show`:

| Aspect | `show` | `context` |
|--------|--------|-----------|
| **Nature** | Display existing artifact | Synthesize briefing |
| **Data** | Static (from files) | Dynamic (computed) |
| **Scope** | Single artifact | Artifact + neighborhood |
| **Audience** | Human checking details | Agent needing orientation |

**Marketing note:** "Context engineering" is a hot topic. `jigy context` positions JIG as a context-aware tool.

### A.2 `jigy context` (Project-Level)

**Purpose:** Generate dynamic, agent-oriented project briefing.

**File:** `src/jig/cli/context.py` (new)

#### Human Output

```
$ jigy context

JIG CONTEXT: jig-dev
════════════════════

PROJECT STATE
  Charter:        jig/Charter.md (5 goals: G-001..G-005)
  Architecture:   2 documents (A-001, A-002)
  Outcomes:       26 total
  Specifications: 91 total | 78 implemented | 65 verified
  Bricks:         11 total | 3 layers | single tower

COVERAGE
  Implemented:    78/91 (86%)
  Verified:       65/91 (71%)
  Gaps:           3 unimplemented, 13 unverified

TOP GAPS (run `jigy audit gaps` for full list)
  S-044  CRDT Conflict Resolution         unimplemented
  S-045  Offline Queue Persistence        unimplemented
  S-046  Network Partition Detection      unimplemented
  S-012  Token Expiration                 unverified (2 functions)
  S-023  Rate Limiting                    unverified (1 function)

QUICK COMMANDS
  jigy context spec <id>   Context around a specification
  jigy show spec <id>      Display spec with implementations
  jigy audit gaps          Full coverage report
  jigy validate            Check all constraints

CHARTER GOALS
  G-001: Grounding in Reality
  G-002: Continuity Across Sessions
  G-003: Enforcing Constraints
  G-004: Intent Alignment
  G-005: Full Traceability
```

#### JSON Output

```bash
$ jigy context --json
```

```json
{"project":"jig-dev","charter":{"file":"jig/Charter.md","goals":["G-001","G-002","G-003","G-004","G-005"]},"stats":{"specs":{"total":91,"implemented":78,"verified":65},"outcomes":{"total":26},"bricks":{"total":11,"layers":3,"towers":1}},"top_gaps":[{"id":"S-044","title":"CRDT Conflict Resolution","status":"unimplemented"}]}
```

#### Markdown Output (for LLM injection)

```bash
$ jigy context --markdown
```

```markdown
# JIG Context: jig-dev

## Project State
- **Charter:** jig/Charter.md (5 goals)
- **Specs:** 91 total | 78 implemented | 65 verified
- **Bricks:** 11 total | 3 layers

## Top Gaps
1. S-044 CRDT Conflict Resolution — unimplemented
2. S-045 Offline Queue Persistence — unimplemented
3. S-012 Token Expiration — unverified (2 functions)

## Quick Commands
- `jigy context spec <id>` — Context around a spec
- `jigy show spec <id>` — Spec with implementations
- `jigy audit gaps` — Full coverage report
```

### A.3 `jigy context spec <id>` (Spec-Level)

**Purpose:** Orient agent to a specific specification and its neighborhood.

#### Human Output

```
$ jigy context spec S-042

CONTEXT: S-042 CRDT Value Observation
═════════════════════════════════════

STATUS: PARTIAL (2 impl, 1 test, 1 gap)
OUTCOME: O-012 (Real-time Collaboration)
BRICK: B-crdt-observe (layer 1)

IMPLEMENTATIONS
  F-jig.crdt.observe.subscribe    src/jig/crdt/observe.py:45
  F-jig.crdt.observe.notify       src/jig/crdt/observe.py:78  ⚠ untested

TESTS
  T-test_observe.test_subscribe   tests/test_observe.py:23

RELATED SPECS (same brick)
  S-041  CRDT State Merge             complete
  S-043  CRDT Conflict Resolution     unimplemented

RELATED SPECS (same outcome)
  S-040  Real-time Sync Protocol      complete
  S-044  Offline Queue                unimplemented

NEXT STEPS
  - Add test for F-jig.crdt.observe.notify
  - Run: jigy show spec S-042 for full details
```

This is **context** — not just the spec, but its neighborhood, status, and actionable next steps.

### A.4 `jigy context brick <id>`

```
$ jigy context brick B-crdt

CONTEXT: B-crdt (CRDT Operations)
═════════════════════════════════

LAYER: 1
TOWER: (default)
SPECS: 5 total | 3 complete | 1 partial | 1 unimplemented

SPECIFICATIONS
  S-040  CRDT State Merge             complete
  S-041  CRDT State Diff              complete
  S-042  CRDT Value Observation       partial (1 gap)
  S-043  CRDT Conflict Resolution     unimplemented
  S-044  CRDT Garbage Collection      complete

DEPENDENCIES (layer 0 bricks this depends on)
  B-core      Core utilities
  B-types     Type definitions

DEPENDENTS (layer 2+ bricks that depend on this)
  B-sync      Synchronization layer
  B-storage   Persistence layer
```

### A.5 Implementation

```python
"""Dynamic context generation for AI agents."""

import click
import jig
from jig.config import JigConfig


@click.command()
@click.argument("target", required=False)
@click.argument("target_id", required=False)
@click.option("--json", "json_output", is_flag=True, help="Output JSON")
@click.option("--markdown", is_flag=True, help="Output markdown for LLM injection")
@click.pass_context
@jig.implements("S-103")
def context(ctx, target: str | None, target_id: str | None, json_output: bool, markdown: bool):
    """Generate dynamic project context.

    Examples:
        jigy context                  # Full project context
        jigy context spec S-042       # Context around spec S-042
        jigy context brick B-crdt     # Context around brick B-crdt
        jigy context --json           # JSON output
        jigy context --markdown       # Markdown for LLM injection
    """
    config = ctx.obj["config"]

    if target is None:
        return project_context(config, json_output, markdown)
    elif target == "spec":
        return spec_context(config, target_id, json_output, markdown)
    elif target == "brick":
        return brick_context(config, target_id, json_output, markdown)
    elif target == "outcome":
        return outcome_context(config, target_id, json_output, markdown)
    elif target == "goal":
        return goal_context(config, target_id, json_output, markdown)
    else:
        click.echo(f"Unknown target: {target}", err=True)
        click.echo("Valid targets: spec, brick, outcome, goal", err=True)
        return 1
```

---

## PART B: Graph Query Commands (`show`)

Per A-002, `show` displays artifacts. These are **static** queries, unlike `context` which is **synthesized**.

### B.1 `jigy show spec <id>`

**Purpose:** Display a specification with its S-F-T triangle.

```
$ jigy show spec S-042

S-042: CRDT Value Observation
  Outcome: O-012 (Real-time Collaboration)
  Status: PARTIAL

  Implements (2):
    F-jig.crdt.observe.subscribe    src/jig/crdt/observe.py:45
    F-jig.crdt.observe.notify       src/jig/crdt/observe.py:78

  Verifies (1):
    T-test_observe.test_subscribe   tests/test_observe.py:23

  Gaps:
    - F-jig.crdt.observe.notify has no test

  Brick: B-crdt-observe (layer 1)
```

### B.2 `jigy show specs`

**Purpose:** List specifications with filtering.

```bash
jigy show specs                      # All specs
jigy show specs --search "CRDT"      # Search by keyword
jigy show specs --unimplemented      # Only unimplemented
jigy show specs --unverified         # Only unverified
jigy show specs --complete           # Only complete
jigy show specs --orphan             # No outcome assigned
jigy show specs --json               # NDJSON output
```

**Human output:**

```
$ jigy show specs --search "CRDT"

Specifications matching "CRDT" (4):
  S-040  CRDT State Merge             complete     (O-012)
  S-041  CRDT State Diff              complete     (O-012)
  S-042  CRDT Value Observation       partial      (O-012)
  S-043  CRDT Conflict Resolution     unimplemented (O-012)
```

### B.3 `jigy show towers` and `jigy show matrix`

**Move existing commands** under `show` for verb-first consistency:

```bash
jigy show towers    # Was: jigy towers
jigy show matrix    # Was: jigy matrix
```

---

## PART C: Audit Commands

### C.1 `jigy audit gaps`

**Purpose:** Find all coverage gaps in the codebase.

```
$ jigy audit gaps

COVERAGE GAPS
═════════════

UNIMPLEMENTED SPECS (3)
  S-044  CRDT Conflict Resolution      (O-012)
  S-045  Offline Queue Persistence     (O-013)
  S-046  Network Partition Detection   (O-013)

UNVERIFIED SPECS (5)
  S-012  Token Expiration              (O-001)  2 functions, 0 tests
  S-023  Rate Limiting                 (O-003)  1 function, 0 tests
  S-042  CRDT Value Observation        (O-012)  2 functions, 1 test, 1 gap

ORPHAN FUNCTIONS (12)
  F-jig.utils.helpers.format_date      src/jig/utils/helpers.py:34
  F-jig.utils.helpers.parse_config     src/jig/utils/helpers.py:67
  ...

ORPHAN SPECS (2)
  S-098  Legacy Migration Shim         (no outcome)
  S-099  Debug Logging                 (no outcome)

Summary: 3 unimplemented, 5 unverified, 12 orphan functions, 2 orphan specs
```

---

## PART D: Artifact Creation (`new`)

### D.1 Design: Auto-Assign IDs

**No `jigy next-id` command.** Instead, `jigy new` auto-assigns the ID and returns it:

```bash
$ jigy new spec "Token Refresh"
Created S-094: Token Refresh
  File: jig/specifications/S-094_Token_Refresh.md

$ jigy new spec "Token Refresh" --json
{"id":"S-094","type":"specification","title":"Token Refresh","file":"jig/specifications/S-094_Token_Refresh.md"}
```

The agent gets the ID from the output. No separate command needed.

### D.2 `jigy new spec <title>`

```bash
# Basic creation
$ jigy new spec "CRDT Garbage Collection"
Created S-093: CRDT Garbage Collection
  File: jig/specifications/S-093_CRDT_Garbage_Collection.md

# With options
$ jigy new spec "Token Refresh" --outcome O-012 --body "Tokens refresh automatically."
Created S-094: Token Refresh
  File: jig/specifications/S-094_Token_Refresh.md

# Quiet mode (for scripts)
$ jigy new spec "Another Spec" --quiet

# JSON output
$ jigy new spec "Another Spec" --json
{"id":"S-095","file":"jig/specifications/S-095_Another_Spec.md"}
```

### D.3 Error Handling with Tips

```bash
$ jigy new spec "CRDT Garbage Collection"
Error: Similar specification already exists
  Existing: S-093 "CRDT Garbage Collection"
  File: jig/specifications/S-093_CRDT_Garbage_Collection.md

Tips:
  - Use `jigy show spec S-093` to view existing spec
  - Use `jigy show specs --search "CRDT"` to find related specs
  - Choose a different title if this is a new requirement
```

### D.4 `jigy new outcome <title>`

```bash
$ jigy new outcome "Offline Support" --goals G-001,G-002
Created O-028: Offline Support
  File: jig/outcomes/O-028_Offline_Support.md
```

### D.5 `jigy new architecture <title>`

```bash
$ jigy new architecture "Event Sourcing" --goals G-002
Created A-003: Event Sourcing
  File: jig/architecture/A-003_Event_Sourcing.md
```

---

## PART E: Project Initialization

### E.1 `jigy init`

**Purpose:** Initialize JIG in a new project per A-001 File Structure.

```bash
$ jigy init

Initialized JIG project:
  jig/Charter.md              (skeleton with G-001 placeholder)
  jig/specifications/
  jig/outcomes/
  jig/architecture/
  jig/bricks.yaml
  jig/generated/
  jig/generated/README.md

Recommended: Add to .gitignore:
  jig/generated/*.ndjson

Add now? [Y/n] y
Updated .gitignore
```

---

## PART F: Enhanced Validation

### F.1 Error Codes and Tips

All validation errors include actionable tips:

```bash
$ jigy validate

Validation failed: 2 errors

Error: MISSING_REQUIRED_FIELD
  File: jig/specifications/S-003_Example.md:1
  Field: id
  Tip: Add `id: S-003` to frontmatter

Error: H1_TITLE_MISMATCH
  File: jig/specifications/S-047_Token_Auth.md:8
  Tip: Change H1 to match frontmatter title exactly
```

### F.2 JSON Output

```bash
$ jigy validate --json
{"valid":false,"errors":[{"code":"MISSING_REQUIRED_FIELD","file":"jig/specifications/S-003_Example.md","line":1,"field":"id","tip":"Add `id: S-003` to frontmatter"}]}
```

### F.3 Error Code Reference

| Code | Meaning | Tip |
|------|---------|-----|
| `MISSING_REQUIRED_FIELD` | Frontmatter missing required field | Add field |
| `INVALID_ID_FORMAT` | ID doesn't match pattern | Fix ID format |
| `INVALID_REFERENCE` | Reference to non-existent artifact | Update reference |
| `DUPLICATE_ID` | Two artifacts with same ID | Rename one |
| `PARTITION_GAP` | Function not in any brick | Add to brick |
| `PARTITION_OVERLAP` | Function in multiple bricks | Remove from one |
| `LAYER_VIOLATION` | Upward dependency | Restructure |
| `H1_TITLE_MISMATCH` | H1 doesn't match frontmatter | Fix H1 |

---

## PART G: Three-Layer Context Architecture

### G.1 The Problem

Agents receive JIG context through manual injection of `agents/contextJIG.md`. This is:
- Manual friction (must remember to inject)
- Static (doesn't reflect current project state)
- All-or-nothing (229 lines regardless of task)

### G.2 The Solution

**Layer 1: CLAUDE.md (Auto-Injected, Minimal)**

Keep minimal (~50 lines). Points to `jigy context`:

```markdown
## JIG Project

This codebase uses JIG for intent-implementation alignment.

**First command:** Run `jigy context` to understand current project state.

**Key commands:**
- `jigy context` — Dynamic project briefing
- `jigy context spec S-001` — Context around a spec
- `jigy show spec S-001` — Display spec details
- `jigy audit gaps` — Find coverage gaps
```

**Layer 2: `jigy context` (On-Demand, Dynamic)**

Agent runs at session start. Gets current project state, top gaps, actionable commands.

**Layer 3: `agents/contextJIG.md` (Deep Reference)**

Comprehensive documentation. Agent reads when needing detailed understanding of JIG concepts. NOT injected by default.

---

## PART H: New Specifications

### H.1 Specification List

| ID | Title | Charter Goal |
|----|-------|--------------|
| S-093 | Graph Query Commands | G-001 |
| S-094 | Coverage Gap Auditing | G-005 |
| S-095 | Project Initialization | G-004 |
| S-096 | Specification Creation | G-004 |
| S-097 | Outcome Creation | G-004 |
| S-098 | Specification Search | G-001 |
| S-099 | JSON Output Format | G-002 |
| S-100 | Generated Directory README | G-003 |
| S-101 | Gitignore Recommendation | G-003 |
| S-102 | Dynamic Context Generation | G-002 |
| S-103 | Context Target Arguments | G-002 |
| S-104 | Context Output Formats | G-002 |
| S-105 | Agent Context Architecture | G-002, G-004 |

**Note:** S-096 (Artifact ID Generation) removed — `jigy new` auto-assigns.

### H.2 New Outcome

| ID | Title | supports_goals | specifies |
|----|-------|----------------|-----------|
| O-027 | Agent-Oriented Tooling | [G-001, G-002, G-003, G-004, G-005] | [S-093..S-105] |

---

## PART I: Work Units

### Phase 1: Core Agent Tools (P0)

| WU | Scope | Files | Specs |
|----|-------|-------|-------|
| WU-1 | Graph loading utilities | `src/jig/cli/graph_utils.py` | S-093 |
| WU-2 | `jigy context` (project-level) | `src/jig/cli/context.py` | S-102, S-104 |
| WU-3 | `jigy context spec/brick/outcome` | `src/jig/cli/context.py` | S-103 |
| WU-4 | `jigy show spec <id>` | `src/jig/cli/show.py` | S-093 |
| WU-5 | `jigy show specs` with `--search` | `src/jig/cli/show.py` | S-093, S-098 |
| WU-6 | `jigy audit gaps` | `src/jig/cli/audit.py` | S-094 |
| WU-7 | Move `towers`/`matrix` under `show` | `src/jig/cli/show.py` | — |

### Phase 2: Initialization & Creation (P1)

| WU | Scope | Files | Specs |
|----|-------|-------|-------|
| WU-8 | `jigy init` | `src/jig/cli/init.py` | S-095, S-100, S-101 |
| WU-9 | `jigy new spec/outcome/architecture` | `src/jig/cli/create.py` | S-096, S-097 |
| WU-10 | Template files | `src/jig/templates/` | S-095 |
| WU-11 | Auto-create README on rebuild | `src/jig/cli/rebuild.py` | S-100 |

### Phase 3: Enhanced Output (P2)

| WU | Scope | Files | Specs |
|----|-------|-------|-------|
| WU-12 | `--json` on all show commands | `src/jig/cli/show.py` | S-099 |
| WU-13 | Enhanced validation JSON | `src/jig/validation/` | S-099 |
| WU-14 | CLAUDE.md update | `CLAUDE.md` | S-105 |
| WU-15 | Document `agents/contextJIG.md` role | `agents/contextJIG.md` | S-105 |
| WU-16 | Create specifications S-093..S-105 | `jig/specifications/` | — |
| WU-17 | Tests for new commands | `tests/cli/` | — |

### Work Unit Count

| Category | Count |
|----------|-------|
| Core context/query | 7 |
| Initialization/creation | 4 |
| Enhanced output | 6 |
| **Total** | **17 work units** |

---

## PART J: Success Criteria

### J.1 Functional

1. `jigy context` generates dynamic project briefing
2. `jigy context spec S-042` shows spec with neighborhood
3. `jigy show spec S-042` displays S-F-T triangle
4. `jigy show specs --search "CRDT"` finds matching specs
5. `jigy audit gaps` identifies all coverage gaps
6. `jigy new spec "Title"` creates spec and returns ID
7. `jigy init` creates A-001-compliant structure
8. All commands support `--json` where appropriate

### J.2 A-002 Compliance

1. Only 3 global flags: `--help`, `--version`, `--no-rebuild`
2. Human output by default (Git model)
3. Verb-first command structure
4. `towers` and `matrix` moved under `show`

### J.3 Context Architecture

1. `CLAUDE.md` points to `jigy context`
2. `jigy context` provides dynamic state
3. `agents/contextJIG.md` documented as deep reference
4. Agent orientation: CLAUDE.md (auto) + `jigy context` (one call)

---

## PART K: Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Graph file size | Use `iter_ndjson()` for streaming |
| Stale graphs | Auto-rebuild before queries (S-070) |
| Template distribution | Explicit `package-data` in pyproject.toml |
| Breaking `towers`/`matrix` | Deprecation warning, alias for 1 release |

---

## References

### Architecture
- `jig/architecture/A-001_JIG_Core_Architecture.md` — File structure, artifact formats
- `jig/architecture/A-002_CLI_Command_Architecture.md` — CLI design principles

### Source Proposals
- `dig/wip/C006_PROPOSAL_JIG_Tools_Skills_Architecture.md`
- `dig/wip/C007_PROPOSAL_Gitignore_Generated_Graphs.md`

### Implementation
- `src/jig/cli/` — Existing CLI commands
- `src/jig/validation/` — Existing validation
