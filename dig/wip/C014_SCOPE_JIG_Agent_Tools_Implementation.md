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
| **G-002: Continuity Across Sessions** | Structured JSON output enables programmatic context extraction |
| **G-003: Enforcing Constraints** | Enhanced validation with error codes and fix hints |
| **G-004: Intent Alignment** | `jigy spec new` ensures specs are created with correct format; `jigy search specs` prevents duplicate specs |
| **G-005: Full Traceability** | `jigy audit gaps` identifies breaks in the S-F-T traceability chain |

### Alignment with A-001 Architecture

Per A-001 (JIG Core Architecture), this work extends the CLI layer to expose the intent hierarchy programmatically. The new commands query the three generated graphs:

- `intent-graph.ndjson` — Charter, Goals, Architecture, Outcomes, Specifications, Bricks
- `implementation-graph.ndjson` — Functions, Classes, Modules, `@jig.implements` edges
- `verification-graph.ndjson` — Tests, `@jig.verifies` edges

---

## Current State Analysis

### Existing CLI Commands

| Command | Status | Agent-Friendly? |
|---------|--------|-----------------|
| `jigy rebuild` | ✓ Complete | Partial — no JSON |
| `jigy validate` | ✓ Complete | Partial — has `--format json` but limited |
| `jigy show layers` | ✓ Complete | No JSON mode |
| `jigy show bricks` | ✓ Complete | No JSON mode |
| `jigy show charter` | ✓ Complete | No JSON mode |
| `jigy show goals` | ✓ Complete | No JSON mode |
| `jigy show architecture` | ✓ Complete | No JSON mode |
| `jigy audit coverage` | ✓ Complete | No JSON mode |
| `jigy init` | ✗ Missing | N/A |
| `jigy show spec <id>` | ✗ Missing | N/A |
| `jigy show specs` | ✗ Missing | N/A |
| `jigy audit gaps` | ✗ Missing | N/A |
| `jigy next-id` | ✗ Missing | N/A |
| `jigy spec new` | ✗ Missing | N/A |
| `jigy outcome new` | ✗ Missing | N/A |
| `jigy search specs` | ✗ Missing | N/A |

### Missing Agent Capabilities

1. **Graph Queries**: Cannot query S-F-T triangle directly
2. **Gap Detection**: Cannot find unimplemented/unverified specs programmatically
3. **Structured Output**: Most commands lack JSON mode
4. **Artifact Creation**: No CLI for creating specs/outcomes with correct formatting
5. **Project Initialization**: No `jigy init` command

---

## Target State

### New CLI Commands (Prioritized)

#### P0: Critical (Phase 1)

| Command | Description | JSON Support |
|---------|-------------|--------------|
| `jigy context` | Generate dynamic project context for agents | Yes |
| `jigy show spec <id>` | Query single spec with implementations/verifications | Yes |
| `jigy show specs` | List specs with status filtering | Yes |
| `jigy audit gaps` | Find unimplemented/unverified specs | Yes |
| `jigy validate --format json` | Enhanced structured validation | Yes (improved) |

#### P1: High Value (Phase 2)

| Command | Description | JSON Support |
|---------|-------------|--------------|
| `jigy init` | Initialize JIG in a project | N/A |
| `jigy next-id spec` | Get next available spec ID | Yes |
| `jigy next-id outcome` | Get next available outcome ID | Yes |
| `jigy spec new` | Create new specification | N/A |
| `jigy outcome new` | Create new outcome | N/A |
| `jigy search specs <query>` | Search specs by keyword | Yes |

#### P2: Nice to Have (Phase 3)

| Command | Description | JSON Support |
|---------|-------------|--------------|
| `jigy show brick <id>` | Query single brick with specs/functions | Yes |
| `jigy show outcome <id>` | Query single outcome with specs | Yes |
| `--format json` on all show commands | Universal JSON support | Yes |

### Generated Directory Management (C007)

| Feature | Description |
|---------|-------------|
| `jig/generated/README.md` | Tracked file explaining regeneration |
| `*.ndjson` gitignored | Graph files not version controlled |
| Auto-create README | `jigy rebuild` creates README if missing |
| `jigy init` creates structure | Sets up directories and .gitignore |

---

## PART A: Graph Query Commands

Per A-001 (JIG Core Architecture), the intent hierarchy forms a G-A-O-S-C-T pyramid. These commands expose programmatic access to that hierarchy, supporting G-001 (Grounding in Reality) by letting agents query actual structure instead of guessing.

### A.1 `jigy show spec <id>`

**Purpose:** Query a single specification with its full S-F-T triangle (Spec → Functions → Tests).

**File:** `src/jig/cli/show.py`

#### A.1.1 Human Output

```
$ jigy show spec S-042

S-042: CRDT Value Observation
  Outcome: O-012 (Real-time Collaboration)
  Status: PARTIAL

  Implements (2):
    F-jig.crdt.observe.subscribe      src/jig/crdt/observe.py:45
    F-jig.crdt.observe.notify         src/jig/crdt/observe.py:78

  Verifies (1):
    T-test_observe.test_subscribe     tests/test_observe.py:23

  Missing:
    - No test for F-jig.crdt.observe.notify

  Brick: B-crdt-observe (layer 1)
```

#### A.1.2 JSON Output

```bash
jigy show spec S-042 --format json
```

```json
{"id":"S-042","title":"CRDT Value Observation","outcome":"O-012","status":"partial","implementations":[{"id":"F-jig.crdt.observe.subscribe","file":"src/jig/crdt/observe.py","line":45},{"id":"F-jig.crdt.observe.notify","file":"src/jig/crdt/observe.py","line":78}],"verifications":[{"id":"T-test_observe.test_subscribe","file":"tests/test_observe.py","line":23}],"gaps":["F-jig.crdt.observe.notify has no verifying test"],"brick":{"id":"B-crdt-observe","layer":1}}
```

#### A.1.3 Implementation

```python
@jig.implements("S-093")  # New spec for graph queries
def show_spec_command(
    config: JigConfig,
    spec_id: str,
    output_format: str = "human",
    skip_rebuild: bool = False,
) -> int:
    """Display detailed information about a specification.
    
    Queries all three graphs to build complete S-F-T picture.
    """
    # Load all graphs
    intent_graph = load_ndjson(config.paths.generated / "intent-graph.ndjson")
    impl_graph = load_ndjson(config.paths.generated / "implementation-graph.ndjson")
    verify_graph = load_ndjson(config.paths.generated / "verification-graph.ndjson")
    
    # Find spec in intent graph
    spec_node = find_node_by_id(intent_graph, spec_id)
    if not spec_node:
        click.echo(f"Specification '{spec_id}' not found.")
        return 1
    
    # Find implementations (from impl graph)
    implementations = find_nodes_implementing(impl_graph, spec_id)
    
    # Find verifications (from verify graph)
    verifications = find_nodes_verifying(verify_graph, spec_id)
    
    # Determine status
    status = compute_spec_status(implementations, verifications)
    
    # Find gaps
    gaps = compute_gaps(implementations, verifications)
    
    # Output
    if output_format == "json":
        output_json(spec_node, implementations, verifications, status, gaps)
    else:
        output_human(spec_node, implementations, verifications, status, gaps)
    
    return 0
```

#### A.1.4 Status Computation

| Status | Condition |
|--------|-----------|
| `unimplemented` | No functions with `@jig.implements(spec_id)` |
| `unverified` | Has implementations but no tests with `@jig.verifies(spec_id)` |
| `partial` | Has implementations and some tests, but gaps exist |
| `complete` | All implementations have corresponding tests |

### A.2 `jigy show specs`

**Purpose:** List all specifications with implementation/verification status.

#### A.2.1 Human Output

```
$ jigy show specs

Specifications (74):

  Complete (45):
    S-001  Python Code Structure Extraction
    S-002  Function Call Dependency Extraction
    ...

  Partial (15):
    S-042  CRDT Value Observation (2 impl, 1 test, 1 gap)
    S-043  CRDT Conflict Resolution (1 impl, 0 tests)
    ...

  Unimplemented (10):
    S-044  Offline Queue Persistence
    S-045  Network Partition Detection
    ...

  Orphan (4):
    S-098  Legacy Migration Shim (no outcome)
    S-099  Debug Logging (no outcome)
    ...
```

#### A.2.2 Filtering Options

```bash
jigy show specs                    # All specs
jigy show specs --unimplemented    # Only unimplemented
jigy show specs --unverified       # Only unverified (incl. partial)
jigy show specs --orphan           # No outcome assigned
jigy show specs --complete         # Fully verified
jigy show specs --format json      # NDJSON output
```

#### A.2.3 JSON Output (NDJSON)

```
{"id":"S-001","title":"Python Code Structure Extraction","outcome":"O-001","status":"complete","impl_count":3,"verify_count":2}
{"id":"S-002","title":"Function Call Dependency Extraction","outcome":"O-001","status":"complete","impl_count":2,"verify_count":2}
{"id":"S-042","title":"CRDT Value Observation","outcome":"O-012","status":"partial","impl_count":2,"verify_count":1,"gaps":1}
```

### A.3 Graph Loading Utilities

**File:** `src/jig/cli/graph_utils.py` (new)

```python
"""Utilities for loading and querying JIG graphs."""

import json
from pathlib import Path
from typing import Iterator, Optional


def load_ndjson(path: Path) -> list[dict]:
    """Load NDJSON file as list of dictionaries."""
    if not path.exists():
        return []
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def iter_ndjson(path: Path) -> Iterator[dict]:
    """Iterate over NDJSON file without loading all into memory."""
    if not path.exists():
        return
    with path.open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def find_node_by_id(graph: list[dict], node_id: str) -> Optional[dict]:
    """Find a node by its ID."""
    for node in graph:
        if node.get("id") == node_id:
            return node
    return None


def find_nodes_by_type(graph: list[dict], node_type: str) -> list[dict]:
    """Find all nodes of a given type."""
    return [n for n in graph if n.get("type") == node_type]


def find_nodes_implementing(impl_graph: list[dict], spec_id: str) -> list[dict]:
    """Find all functions implementing a specification."""
    results = []
    for node in impl_graph:
        implements = node.get("implements", [])
        if spec_id in implements:
            results.append(node)
    return results


def find_nodes_verifying(verify_graph: list[dict], spec_id: str) -> list[dict]:
    """Find all tests verifying a specification."""
    results = []
    for node in verify_graph:
        verifies = node.get("verifies", [])
        if spec_id in verifies:
            results.append(node)
    return results
```

---

## PART B: Audit Gaps Command

### B.1 `jigy audit gaps`

**Purpose:** Find all coverage gaps in the codebase.

**File:** `src/jig/cli/audit.py`

#### B.1.1 Human Output

```
$ jigy audit gaps

UNIMPLEMENTED SPECS (3):
  S-044  CRDT Conflict Resolution      (O-012)
  S-045  Offline Queue Persistence     (O-013)
  S-046  Network Partition Detection   (O-013)

UNVERIFIED SPECS (5):
  S-012  Token Expiration              (O-001)  [2 functions]
  S-023  Rate Limiting                 (O-003)  [1 function]
  S-042  CRDT Value Observation        (O-012)  [2 functions, 1 test, 1 gap]
  ...

ORPHAN FUNCTIONS (12):
  F-jig.utils.helpers.format_date      src/jig/utils/helpers.py:34
  F-jig.utils.helpers.parse_config     src/jig/utils/helpers.py:67
  ...

SPECS WITHOUT OUTCOME (2):
  S-098  Legacy Migration Shim
  S-099  Debug Logging

Summary: 3 unimplemented, 5 unverified, 12 orphan functions, 2 orphan specs
```

#### B.1.2 JSON Output

```bash
jigy audit gaps --format json
```

```json
{"unimplemented_specs":[{"id":"S-044","title":"CRDT Conflict Resolution","outcome":"O-012"},{"id":"S-045","title":"Offline Queue Persistence","outcome":"O-013"}],"unverified_specs":[{"id":"S-012","title":"Token Expiration","outcome":"O-001","impl_count":2,"verify_count":0}],"orphan_functions":[{"id":"F-jig.utils.helpers.format_date","file":"src/jig/utils/helpers.py","line":34}],"orphan_specs":[{"id":"S-098","title":"Legacy Migration Shim"}],"summary":{"unimplemented":3,"unverified":5,"orphan_functions":12,"orphan_specs":2}}
```

#### B.1.3 Implementation

```python
@jig.implements("S-094")  # New spec for gap auditing
def gaps_command(
    config: JigConfig,
    output_format: str = "human",
    skip_rebuild: bool = False,
) -> int:
    """Find all coverage gaps in the codebase.
    
    Analyzes intent, implementation, and verification graphs to find:
    - Unimplemented specs (no @jig.implements)
    - Unverified specs (no @jig.verifies)
    - Orphan functions (no @jig.implements decorator)
    - Orphan specs (no outcome assignment)
    """
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["impl", "verify", "intent"], config, skip_rebuild=skip_rebuild)
    
    # Load graphs
    intent_graph = load_ndjson(config.paths.generated / "intent-graph.ndjson")
    impl_graph = load_ndjson(config.paths.generated / "implementation-graph.ndjson")
    verify_graph = load_ndjson(config.paths.generated / "verification-graph.ndjson")
    
    # Find gaps
    unimplemented = find_unimplemented_specs(intent_graph, impl_graph)
    unverified = find_unverified_specs(intent_graph, impl_graph, verify_graph)
    orphan_functions = find_orphan_functions(impl_graph)
    orphan_specs = find_orphan_specs(intent_graph)
    
    # Output
    if output_format == "json":
        output_gaps_json(unimplemented, unverified, orphan_functions, orphan_specs)
    else:
        output_gaps_human(unimplemented, unverified, orphan_functions, orphan_specs)
    
    return 0
```

---

## PART B2: Dynamic Context Injection

### B2.1 Problem: Static Context is Suboptimal

Currently, agents receive JIG context through manual injection of `agents/contextJIG.md` (229 lines). This approach has limitations:

| Problem | Impact |
|---------|--------|
| **Manual friction** | User must remember to inject every session |
| **Static content** | Doesn't reflect current project state |
| **All-or-nothing** | 229 lines consumed regardless of task complexity |
| **No state awareness** | Agent doesn't know coverage gaps, recent changes |

### B2.2 Solution: Three-Layer Context Architecture

**Layer 1: CLAUDE.md (Always Injected, Minimal)**

Cursor auto-injects `CLAUDE.md` at session start. Keep it minimal (~20 lines) with just enough to orient the agent:

```markdown
## JIG Project

This codebase uses JIG for intent-implementation alignment.

**First command:** Run `jigy context` to understand current project state.

**Key commands:**
- `jigy context` — Dynamic project summary for agents
- `jigy show spec S-001` — Query specification details
- `jigy audit gaps` — Find coverage gaps
- `jigy validate` — Check all constraints

**Key locations:**
- `jig/Charter.md` — Project goals (G-001 through G-005)
- `jig/specifications/` — Behavioral requirements (S-###.md)
- `jig/bricks.yaml` — Architectural partitioning

**Before modifying code:** Run `jigy show spec S-###` to understand intent.
```

**Layer 2: `jigy context` (On-Demand, Dynamic)**

Agent runs at session start or when needing orientation. Generates **dynamic** context reflecting actual project state.

**Layer 3: `agents/contextJIG.md` (Deep Reference)**

Comprehensive JIG documentation. Agent reads when needing detailed understanding of concepts (layers, towers, evergreen principles). Not injected by default.

### B2.3 `jigy context` Command

**Purpose:** Generate dynamic, agent-oriented project context.

**File:** `src/jig/cli/context.py` (new)

#### Human Output

```
$ jigy context

╔══════════════════════════════════════════════════════════════════╗
║  JIG CONTEXT: jig-dev                                             ║
╚══════════════════════════════════════════════════════════════════╝

PROJECT STATE
─────────────
Charter:        jig/Charter.md (5 goals: G-001..G-005)
Architecture:   1 document (A-001)
Outcomes:       26 total
Specifications: 91 total │ 78 implemented │ 65 verified │ 3 gaps
Bricks:         11 total │ 3 layers │ single tower

COVERAGE SUMMARY
────────────────
  ✓ Implemented:   78/91 (86%)
  ✓ Verified:      65/91 (71%)
  ⚠ Unimplemented: 3 specs
  ⚠ Unverified:    13 specs

TOP GAPS (run `jigy audit gaps` for full list)
──────────────────────────────────────────────
  S-044  CRDT Conflict Resolution         unimplemented
  S-045  Offline Queue Persistence        unimplemented
  S-046  Network Partition Detection      unimplemented
  S-012  Token Expiration                 unverified (2 functions)
  S-023  Rate Limiting                    unverified (1 function)

KEY COMMANDS
────────────
  jigy show spec <id>    Query spec with implementations/tests
  jigy show specs        List all specs with status
  jigy audit gaps        Full coverage report
  jigy validate          Check all constraints
  jigy search specs      Find specs by keyword

ARCHITECTURE CONSTRAINTS (A-001)
────────────────────────────────
  • Decorators: @jig.implements("S-###"), @jig.verifies("S-###")
  • Bricks partition codebase (no gaps, no overlaps)
  • Layer N depends only on layers < N
  • Cross-tower dependencies forbidden (if towers used)

CHARTER GOALS
─────────────
  G-001: Grounding in Reality
  G-002: Continuity Across Sessions
  G-003: Enforcing Constraints
  G-004: Intent Alignment
  G-005: Full Traceability
```

#### JSON Output

```bash
$ jigy context --format json
```

```json
{"project":"jig-dev","charter":{"file":"jig/Charter.md","goals":["G-001","G-002","G-003","G-004","G-005"]},"stats":{"specs":{"total":91,"implemented":78,"verified":65,"unimplemented":3,"unverified":13},"outcomes":{"total":26},"bricks":{"total":11,"layers":3,"towers":1}},"top_gaps":[{"id":"S-044","title":"CRDT Conflict Resolution","status":"unimplemented"},{"id":"S-045","title":"Offline Queue Persistence","status":"unimplemented"},{"id":"S-012","title":"Token Expiration","status":"unverified","impl_count":2}],"commands":{"query_spec":"jigy show spec <id>","list_specs":"jigy show specs","audit_gaps":"jigy audit gaps","validate":"jigy validate"}}
```

#### Markdown Output (for LLM Injection)

```bash
$ jigy context --format markdown
```

Outputs clean markdown suitable for direct injection into agent context:

```markdown
# JIG Context: jig-dev

## Project State
- **Charter:** jig/Charter.md (5 goals)
- **Specs:** 91 total | 78 implemented | 65 verified
- **Bricks:** 11 total | 3 layers

## Top Coverage Gaps
1. S-044 CRDT Conflict Resolution — unimplemented
2. S-045 Offline Queue Persistence — unimplemented
3. S-012 Token Expiration — unverified

## Quick Commands
- `jigy show spec <id>` — Query spec details
- `jigy audit gaps` — Full coverage report

## Before Writing Code
1. Run `jigy show spec S-###` to understand the spec
2. Use `@jig.implements("S-###")` decorator
3. Run `jigy validate` before committing
```

### B2.4 Implementation

```python
"""Dynamic context generation for AI agents."""

import json
from dataclasses import dataclass
from pathlib import Path

import click

import jig
from jig.config import JigConfig


@dataclass
class ProjectContext:
    """Aggregated project context for agents."""
    
    project_name: str
    charter_file: str
    goals: list[str]
    spec_stats: dict
    outcome_stats: dict
    brick_stats: dict
    top_gaps: list[dict]
    validation_status: str


@jig.implements("S-103")
def context_command(
    config: JigConfig,
    output_format: str = "human",
    skip_rebuild: bool = False,
) -> int:
    """Generate dynamic project context for AI agents.
    
    Supports G-002 (Continuity Across Sessions) by providing
    machine-readable project state that persists across sessions.
    
    Output formats:
    - human: Rich terminal output with boxes and colors
    - json: Compact single-line JSON for programmatic use
    - markdown: Clean markdown for LLM context injection
    """
    from jig.cli.auto_rebuild import ensure_graphs_current
    ensure_graphs_current(["impl", "verify", "intent"], config, skip_rebuild=skip_rebuild)
    
    # Gather context from graphs
    context = gather_project_context(config)
    
    # Output in requested format
    if output_format == "json":
        click.echo(format_context_json(context))
    elif output_format == "markdown":
        click.echo(format_context_markdown(context))
    else:
        click.echo(format_context_human(context))
    
    return 0


def gather_project_context(config: JigConfig) -> ProjectContext:
    """Gather project context from all graphs."""
    from jig.cli.graph_utils import load_ndjson
    
    # Load graphs
    intent = load_ndjson(config.paths.generated / "intent-graph.ndjson")
    impl = load_ndjson(config.paths.generated / "implementation-graph.ndjson")
    verify = load_ndjson(config.paths.generated / "verification-graph.ndjson")
    
    # Extract Charter and goals
    charter_node = next((n for n in intent if n.get("type") == "charter"), None)
    goals = charter_node.get("defines_goals", []) if charter_node else []
    
    # Count specs by status
    specs = [n for n in intent if n.get("type") == "specification"]
    implemented_ids = set()
    verified_ids = set()
    
    for node in impl:
        for spec_id in node.get("implements", []):
            implemented_ids.add(spec_id)
    
    for node in verify:
        for spec_id in node.get("verifies", []):
            verified_ids.add(spec_id)
    
    spec_ids = {s["id"] for s in specs}
    unimplemented = spec_ids - implemented_ids
    unverified = spec_ids - verified_ids
    
    # Find top gaps
    top_gaps = []
    for spec in specs:
        sid = spec["id"]
        if sid in unimplemented:
            top_gaps.append({
                "id": sid,
                "title": spec.get("title", ""),
                "status": "unimplemented"
            })
        elif sid in unverified:
            impl_count = sum(1 for n in impl if sid in n.get("implements", []))
            top_gaps.append({
                "id": sid,
                "title": spec.get("title", ""),
                "status": "unverified",
                "impl_count": impl_count
            })
    
    # Sort: unimplemented first, then unverified
    top_gaps.sort(key=lambda g: (0 if g["status"] == "unimplemented" else 1, g["id"]))
    
    # Count bricks/layers
    bricks = [n for n in intent if n.get("type") == "brick"]
    layers = set(b.get("layer", 0) for b in bricks)
    towers = set(b.get("tower") for b in bricks if b.get("tower"))
    
    return ProjectContext(
        project_name=config.project_root.name,
        charter_file=str(config.paths.charter.relative_to(config.project_root)),
        goals=goals,
        spec_stats={
            "total": len(specs),
            "implemented": len(implemented_ids & spec_ids),
            "verified": len(verified_ids & spec_ids),
            "unimplemented": len(unimplemented),
            "unverified": len(unverified),
        },
        outcome_stats={
            "total": len([n for n in intent if n.get("type") == "outcome"])
        },
        brick_stats={
            "total": len(bricks),
            "layers": len(layers),
            "towers": len(towers) if towers else 1,
        },
        top_gaps=top_gaps[:5],  # Top 5 gaps
        validation_status="unknown",
    )
```

### B2.5 Output Format Selection

| Format | Use Case | Size |
|--------|----------|------|
| `human` | Interactive terminal use | ~40 lines |
| `json` | Programmatic consumption | 1 line |
| `markdown` | LLM context injection | ~25 lines |

**Agent workflow:**
```bash
# At session start, agent runs:
jigy context --format markdown

# Output is compact, focused, and includes actionable next steps
```

### B2.6 CLAUDE.md Update Specification

Update `CLAUDE.md` to use the three-layer approach:

**Current** (122 lines with full JIG explanation):
- Full decorator examples
- Project structure
- Validation section

**Proposed** (~50 lines, pointing to dynamic context):
- Keep existing intro and key commands
- Add: "Run `jigy context` for current project state"
- Keep: filename format, title selection, H1 header guidance
- Remove: duplicated content that `jigy context` provides dynamically

### B2.7 `agents/contextJIG.md` Role

Keep `agents/contextJIG.md` as **deep reference documentation**:

| Aspect | Role |
|--------|------|
| **Purpose** | Comprehensive JIG concepts for complex tasks |
| **When used** | Agent reads on-demand when needing detailed understanding |
| **Injection** | NOT injected at session start |
| **Content** | G-A-O-S-C-T pyramid, ID formats, evergreen principles, validation rules |

Agent can reference it with:
```
Read agents/contextJIG.md for detailed JIG concepts
```

---

## PART C: Project Initialization (C007)

### C.1 `jigy init`

**Purpose:** Initialize JIG in a new project per A-001 File Structure.

**File:** `src/jig/cli/init.py` (new)

Per A-001 (JIG Core Architecture), the required file structure is:

```
project-root/
├── jig/
│   ├── Charter.md                    # Root document (singleton)
│   ├── architecture/                 # Architecture documents
│   ├── outcomes/                     # Outcome documents
│   ├── specifications/               # Specification documents
│   ├── bricks.yaml                   # Brick definitions
│   └── generated/                    # Machine-generated graphs
│       ├── README.md                 # (tracked)
│       ├── intent-graph.ndjson       # (gitignored)
│       ├── implementation-graph.ndjson  # (gitignored)
│       └── verification-graph.ndjson # (gitignored)
```

#### C.1.1 Usage

```bash
$ jigy init

Created:
  jig/
  jig/Charter.md              # Skeleton with G-001 placeholder
  jig/specifications/
  jig/outcomes/
  jig/architecture/
  jig/bricks.yaml
  jig/generated/
  jig/generated/README.md

Recommended: Add to .gitignore:
  # JIG generated graphs (regenerate with: jigy rebuild)
  jig/generated/*.ndjson

Add now? [Y/n] y
Updated .gitignore
```

#### C.1.2 Implementation

```python
"""JIG project initialization."""

from pathlib import Path

import click

import jig

BRICKS_TEMPLATE = """# JIG Brick Definitions
# See: docs/configuration.md

bricks: []
"""

GENERATED_README = """# Generated JIG Graphs

These files are machine-generated. Do not edit.

**Regenerate with:**
```bash
jigy rebuild
```

**Files:**
- `intent-graph.ndjson` — specs, outcomes, bricks
- `implementation-graph.ndjson` — functions, calls, decorators
- `verification-graph.ndjson` — tests, coverage

These files should be gitignored. See project `.gitignore`.
"""

GITIGNORE_SNIPPET = """
# JIG generated graphs (regenerate with: jigy rebuild)
jig/generated/*.ndjson
"""


CHARTER_TEMPLATE = """---
id: Charter
type: charter
defines_goals: [G-001]
---

# Project Charter

## Purpose

[Describe why this project exists and what problems it solves]

## Charter Goals

### G-001: [First Goal Title]

[Describe what this goal achieves and why it matters]

---

## For AI Agents Reading This

If you are an AI agent working on this codebase:

1. **Read before writing**: Query the graphs to understand what exists
2. **Link your work**: Use `@jig.implements()` and `@jig.verifies()` decorators
3. **Validate continuously**: Run `jigy validate` before committing
4. **Understand intent first**: Read specs before modifying implementation

JIG exists because you exist. Use it.
"""


@jig.implements("S-095")  # New spec for init command
def init_command(project_root: Path, add_gitignore: bool = True) -> int:
    """Initialize JIG in a project per A-001 File Structure.
    
    Creates directory structure and optionally updates .gitignore.
    """
    jig_root = project_root / "jig"
    
    # Create directories (per A-001)
    directories = [
        jig_root,
        jig_root / "specifications",
        jig_root / "outcomes",
        jig_root / "architecture",
        jig_root / "generated",
    ]
    
    created = []
    for d in directories:
        if not d.exists():
            d.mkdir(parents=True)
            created.append(str(d.relative_to(project_root)))
    
    # Create Charter.md if missing (per A-001 - singleton root document)
    charter_file = jig_root / "Charter.md"
    if not charter_file.exists():
        charter_file.write_text(CHARTER_TEMPLATE)
        created.append(str(charter_file.relative_to(project_root)))
    
    # Create bricks.yaml if missing
    bricks_file = jig_root / "bricks.yaml"
    if not bricks_file.exists():
        bricks_file.write_text(BRICKS_TEMPLATE)
        created.append(str(bricks_file.relative_to(project_root)))
    
    # Create generated/README.md (always tracked)
    readme_file = jig_root / "generated" / "README.md"
    if not readme_file.exists():
        readme_file.write_text(GENERATED_README)
        created.append(str(readme_file.relative_to(project_root)))
    
    # Display results
    if created:
        click.echo("Created:")
        for path in created:
            click.echo(f"  {path}")
    else:
        click.echo("JIG already initialized.")
        return 0
    
    # Handle .gitignore
    if add_gitignore:
        gitignore_path = project_root / ".gitignore"
        gitignore_entry = "jig/generated/*.ndjson"
        
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if gitignore_entry not in content:
                click.echo()
                click.echo("Recommended: Add to .gitignore:")
                click.echo(f"  {gitignore_entry}")
                
                if click.confirm("Add now?", default=True):
                    with gitignore_path.open("a") as f:
                        f.write(GITIGNORE_SNIPPET)
                    click.echo("Updated .gitignore")
        else:
            click.echo()
            if click.confirm("Create .gitignore with JIG entry?", default=True):
                gitignore_path.write_text(GITIGNORE_SNIPPET.strip() + "\n")
                click.echo("Created .gitignore")
    
    return 0
```

### C.2 Auto-Create README on Rebuild

**File:** `src/jig/cli/rebuild.py`

Update rebuild functions to ensure README exists:

```python
def _ensure_generated_readme(config: JigConfig) -> None:
    """Ensure jig/generated/README.md exists."""
    readme_path = config.paths.generated / "README.md"
    if not readme_path.exists():
        config.paths.generated.mkdir(parents=True, exist_ok=True)
        readme_path.write_text(GENERATED_README)
```

Call at start of each rebuild function:
```python
def rebuild_all_command(config: JigConfig) -> int:
    _ensure_generated_readme(config)
    # ... existing code ...
```

---

## PART D: Artifact Creation Commands

### D.1 `jigy next-id`

**Purpose:** Get next available ID for artifact type.

**File:** `src/jig/cli/create.py` (new)

```bash
$ jigy next-id spec
S-093

$ jigy next-id outcome
O-027

$ jigy next-id spec --format json
{"type":"specification","next_id":"S-093"}
```

#### D.1.1 Implementation

```python
@jig.implements("S-096")  # New spec for ID generation
def next_id_command(
    config: JigConfig,
    artifact_type: str,
    output_format: str = "human",
) -> int:
    """Get next available ID for artifact type."""
    if artifact_type == "spec":
        directory = config.paths.specifications
        prefix = "S-"
    elif artifact_type == "outcome":
        directory = config.paths.outcomes
        prefix = "O-"
    elif artifact_type == "architecture":
        directory = config.paths.architecture
        prefix = "A-"
    else:
        click.echo(f"Unknown type: {artifact_type}")
        click.echo("Valid types: spec, outcome, architecture")
        return 1
    
    # Find highest existing ID
    pattern = re.compile(rf"^{prefix}(\d{{3}})")
    max_num = 0
    
    if directory.exists():
        for f in directory.glob(f"{prefix}*.md"):
            match = pattern.match(f.stem)
            if match:
                num = int(match.group(1))
                max_num = max(max_num, num)
    
    next_num = max_num + 1
    next_id = f"{prefix}{next_num:03d}"
    
    if output_format == "json":
        click.echo(json.dumps({"type": artifact_type, "next_id": next_id}))
    else:
        click.echo(next_id)
    
    return 0
```

### D.2 `jigy spec new`

**Purpose:** Create a new specification with correct formatting.

```bash
$ jigy spec new "CRDT Garbage Collection" --implements O-012

Created: jig/specifications/S-093_CRDT_Garbage_Collection.md

$ jigy spec new "CRDT Garbage Collection" --implements O-012 --body "CRDTs automatically garbage collect tombstones.

**Acceptance Criteria:**
- Tombstones older than gc_threshold are removed
- GC runs on configurable interval"

Created: jig/specifications/S-093_CRDT_Garbage_Collection.md
```

#### D.2.1 Implementation

```python
@jig.implements("S-097")  # New spec for spec creation
def spec_new_command(
    config: JigConfig,
    title: str,
    implements_outcome: str | None = None,
    body: str | None = None,
) -> int:
    """Create a new specification with correct formatting.
    
    Validates:
    - ID not already used
    - Outcome reference valid (if provided)
    - Title format follows guidelines
    """
    # Get next ID
    next_id = get_next_id(config.paths.specifications, "S-")
    
    # Convert title to snake_case for filename
    snake_title = to_snake_case(title)
    filename = f"{next_id}_{snake_title}.md"
    filepath = config.paths.specifications / filename
    
    # Validate outcome if provided
    if implements_outcome:
        outcome_dir = config.paths.outcomes
        if not any(outcome_dir.glob(f"{implements_outcome}*.md")):
            click.echo(f"Warning: Outcome '{implements_outcome}' not found.")
            if not click.confirm("Create anyway?", default=False):
                return 1
    
    # Build content
    content = f"""---
id: {next_id}
type: specification
title: {title}
---

# {title}

"""
    if body:
        content += body + "\n"
    else:
        content += """[Describe the behavioral requirement here]

**Acceptance Criteria:**
- [Criterion 1]
- [Criterion 2]
"""
    
    # Write file
    filepath.write_text(content)
    click.echo(f"Created: {filepath.relative_to(config.project_root)}")
    
    return 0
```

### D.3 `jigy search specs`

**Purpose:** Search specifications by keyword.

```bash
$ jigy search specs "authentication"

S-001  Token Expiration           (O-001) [complete]
S-002  Password Hashing           (O-001) [complete]
S-007  Session Invalidation       (O-001) [unimplemented]

$ jigy search specs "authentication" --format json
{"id":"S-001","title":"Token Expiration","outcome":"O-001","status":"complete","match":"title"}
{"id":"S-002","title":"Password Hashing","outcome":"O-001","status":"complete","match":"body"}
```

---

## PART E: Enhanced Validation Output

### E.1 Improved JSON Structure

Current validation JSON is basic. Enhance with:
- Error codes for all errors
- Fix hints where applicable
- File paths (absolute for agent use)
- Line numbers

**File:** `src/jig/validation/models.py`

```python
@dataclass
class ValidationError:
    """Represents a single validation error."""
    
    file: str
    message: str
    line: Optional[int] = None
    code: Optional[str] = None
    severity: str = "error"
    field: Optional[str] = None
    fix: Optional[dict] = None  # NEW: Fix suggestion
```

### E.2 Error Codes Standardization

| Code | Meaning | Suggested Fix |
|------|---------|---------------|
| `MISSING_REQUIRED_FIELD` | Frontmatter missing required field | Add field |
| `INVALID_ID_FORMAT` | ID doesn't match pattern | Fix ID |
| `INVALID_REFERENCE` | Reference to non-existent artifact | Update reference |
| `DUPLICATE_ID` | Two artifacts with same ID | Rename one |
| `PARTITION_GAP` | Function not in any brick | Add to brick |
| `PARTITION_OVERLAP` | Function in multiple bricks | Remove from one |
| `LAYER_VIOLATION` | Upward dependency | Restructure or re-layer |
| `UNIMPLEMENTED_SPEC` | Spec has no `@jig.implements` | Implement |
| `UNVERIFIED_SPEC` | Spec has no `@jig.verifies` | Add tests |
| `INVALID_FILENAME_FORMAT` | Filename doesn't match convention | Rename file |
| `H1_TITLE_MISMATCH` | H1 doesn't match frontmatter title | Update H1 |

### E.3 Fix Hints

```json
{
  "code": "MISSING_REQUIRED_FIELD",
  "file": "jig/specifications/S-003_Example.md",
  "line": 1,
  "field": "id",
  "fix": {
    "action": "add_frontmatter_field",
    "field": "id",
    "suggested_value": "S-003"
  }
}
```

---

## PART F: Templates

### F.1 Template Directory Structure

Per A-001 File Structure, templates must create artifacts in the correct format:

```
src/jig/templates/
├── charter.md              # Skeleton Charter per A-001
├── generated_README.md     # README for generated/ directory
├── gitignore_snippet.txt   # .gitignore entry for generated files
├── specification.md        # Spec template with correct frontmatter
├── outcome.md              # Outcome template with supports_goals
├── architecture.md         # Architecture template with supports_goals
└── bricks.yaml             # Empty bricks structure
```

### F.2 Template Frontmatter Requirements

Per A-001, each artifact type has required frontmatter fields:

| Template | Required Fields |
|----------|-----------------|
| `charter.md` | `id: Charter`, `type: charter`, `defines_goals: [G-001]` |
| `specification.md` | `id`, `type: specification`, `title` |
| `outcome.md` | `id`, `type: outcome`, `title`, `supports_goals`, `specifies` |
| `architecture.md` | `id`, `type: architecture`, `title`, `status`, `supports_goals` |

### F.3 Package Data

Update `pyproject.toml`:

```toml
[tool.setuptools.package-data]
jig = ["templates/*.md", "templates/*.txt", "templates/*.yaml"]
```

---

## PART G: New Specifications

### G.1 Agent Tools Specifications

Per A-001 (JIG Core Architecture), all specifications must follow the `S-{NNN}` format. These new specifications extend the CLI layer to support agent workflows:

| ID | Title | Charter Goal | Description |
|----|-------|--------------|-------------|
| S-093 | Graph Query Commands | G-001 | `jigy show spec/specs` queries graphs directly |
| S-094 | Coverage Gap Auditing | G-005 | `jigy audit gaps` finds breaks in traceability |
| S-095 | Project Initialization | G-004 | `jigy init` creates correct directory structure |
| S-096 | Artifact ID Generation | G-004 | `jigy next-id` returns next available ID |
| S-097 | Specification Creation | G-004 | `jigy spec new` creates valid spec file |
| S-098 | Outcome Creation | G-004 | `jigy outcome new` creates valid outcome file |
| S-099 | Specification Search | G-001 | `jigy search specs` searches by keyword |
| S-100 | JSON Output Format | G-002 | `--format json` produces NDJSON/compact JSON |
| S-101 | Generated Directory README | G-003 | Auto-create README in generated/ |
| S-102 | Gitignore Recommendation | G-003 | Init suggests .gitignore entry |
| S-103 | Dynamic Context Generation | G-002 | `jigy context` generates agent-oriented project state |
| S-104 | Context Output Formats | G-002 | Context supports human/json/markdown output |
| S-105 | Agent Context Architecture | G-002, G-004 | Three-layer context: CLAUDE.md + jigy context + deep reference |

### G.2 New Outcome

Per A-001, outcomes must have `supports_goals` and `specifies` fields:

| ID | Title | supports_goals | specifies |
|----|-------|----------------|-----------|
| O-027 | Agent-Oriented Tooling | [G-001, G-002, G-004, G-005] | [S-093..S-105] |

**Full specification list for O-027:**
`[S-093, S-094, S-095, S-096, S-097, S-098, S-099, S-100, S-101, S-102, S-103, S-104, S-105]`

**Rationale for Goal Alignment:**
- **G-001 (Grounding)**: Graph queries and search let agents query actual structure
- **G-002 (Continuity)**: `jigy context` provides dynamic state; JSON output enables programmatic extraction
- **G-004 (Intent Alignment)**: Artifact creation ensures correct spec format before implementation
- **G-005 (Traceability)**: Gap auditing identifies breaks in the S-F-T chain

---

## PART H: Work Units

### Phase 1: Core Graph Queries (P0)

#### WU-1: Graph Loading Utilities

**Scope:**
- Create `src/jig/cli/graph_utils.py`
- Implement `load_ndjson()`, `iter_ndjson()`
- Implement `find_node_by_id()`, `find_nodes_by_type()`
- Implement `find_nodes_implementing()`, `find_nodes_verifying()`

**Files:** `src/jig/cli/graph_utils.py`

**Specs:** S-093 (partial)

---

#### WU-2: Show Spec Command

**Scope:**
- Add `jigy show spec <id>` command
- Implement human and JSON output
- Query all three graphs for complete picture
- Compute status (unimplemented/unverified/partial/complete)

**Files:**
- `src/jig/cli/show.py`
- `src/jig/cli/main.py`

**Specs:** S-093

---

#### WU-3: Show Specs Command

**Scope:**
- Add `jigy show specs` command
- Implement filtering: `--unimplemented`, `--unverified`, `--orphan`, `--complete`
- Human and JSON (NDJSON) output
- Group by status in human output

**Files:**
- `src/jig/cli/show.py`
- `src/jig/cli/main.py`

**Specs:** S-093

---

#### WU-4: Audit Gaps Command

**Scope:**
- Add `jigy audit gaps` command
- Find unimplemented specs
- Find unverified specs
- Find orphan functions (no decorator)
- Find orphan specs (no outcome)
- Human and JSON output

**Files:**
- `src/jig/cli/audit.py`
- `src/jig/cli/main.py`

**Specs:** S-094

---

#### WU-4B: Context Command

**Scope:**
- Create `src/jig/cli/context.py`
- Implement `jigy context` command
- Support three output formats: human, json, markdown
- Gather project state from all three graphs
- Compute coverage statistics
- Extract top 5 coverage gaps
- Display Charter goals
- Show architecture constraints summary

**Files:**
- `src/jig/cli/context.py`
- `src/jig/cli/main.py`

**Specs:** S-103, S-104

**Charter Goal:** G-002 (Continuity Across Sessions)

---

#### WU-4C: Context Markdown Format

**Scope:**
- Implement `--format markdown` output
- Optimize for LLM context injection (~25 lines)
- Include actionable commands
- Include top gaps
- Clean, parseable format

**Files:** `src/jig/cli/context.py`

**Specs:** S-104

---

#### WU-4D: CLAUDE.md Update

**Scope:**
- Update `CLAUDE.md` to use three-layer context approach
- Add "Run `jigy context` for current project state" guidance
- Keep minimal (~50 lines, not 122)
- Point to `agents/contextJIG.md` for deep reference
- Remove duplicated content that `jigy context` provides dynamically

**Files:** `CLAUDE.md`

**Specs:** S-105

**Note:** This is a documentation change, not a code change.

---

#### WU-4E: Document `agents/contextJIG.md` Role

**Scope:**
- Add header comment to `agents/contextJIG.md` clarifying its role
- Document that it's deep reference, not session-start injection
- Add note pointing to `jigy context` for dynamic state

**Files:** `agents/contextJIG.md`

**Specs:** S-105

---

### Phase 2: Initialization & Creation (P1)

#### WU-5: Init Command

**Scope:**
- Create `src/jig/cli/init.py`
- Implement `jigy init` command
- Create directory structure per A-001 File Structure
- Create Charter.md skeleton (singleton per A-001)
- Create bricks.yaml template
- Create generated/README.md
- Optionally update .gitignore

**Files:**
- `src/jig/cli/init.py`
- `src/jig/cli/main.py`

**Specs:** S-095, S-101, S-102

**A-001 Compliance:**
- Directory structure matches A-001 File Structure section
- Charter.md created with valid frontmatter (id: Charter, defines_goals)

---

#### WU-6: Auto-Create README on Rebuild

**Scope:**
- Add `_ensure_generated_readme()` helper
- Call from all rebuild commands
- Ensure README exists before writing graphs

**Files:** `src/jig/cli/rebuild.py`

**Specs:** S-101

---

#### WU-7: Template Files

**Scope:**
- Create `src/jig/templates/` directory
- Add charter.md template (per A-001 Charter validation rules)
- Add generated_README.md
- Add gitignore_snippet.txt
- Add specification.md template (per A-001 ID format)
- Add outcome.md template (with supports_goals per A-001)
- Add architecture.md template (with supports_goals per A-001)
- Add bricks.yaml template
- Update pyproject.toml for package data

**Files:**
- `src/jig/templates/charter.md`
- `src/jig/templates/generated_README.md`
- `src/jig/templates/gitignore_snippet.txt`
- `src/jig/templates/specification.md`
- `src/jig/templates/outcome.md`
- `src/jig/templates/architecture.md`
- `src/jig/templates/bricks.yaml`
- `pyproject.toml`

**Specs:** S-095, S-097, S-098

---

#### WU-8: Next-ID Command

**Scope:**
- Create `src/jig/cli/create.py`
- Implement `jigy next-id spec/outcome/architecture`
- Human and JSON output

**Files:**
- `src/jig/cli/create.py`
- `src/jig/cli/main.py`

**Specs:** S-096

---

#### WU-9: Spec New Command

**Scope:**
- Add `jigy spec new <title>` command
- Options: `--implements <outcome_id>`, `--body <text>`
- Validate outcome reference
- Use snake_case for filename
- Write with correct frontmatter

**Files:**
- `src/jig/cli/create.py`
- `src/jig/cli/main.py`

**Specs:** S-097

---

#### WU-10: Outcome New Command

**Scope:**
- Add `jigy outcome new <title>` command
- Options: `--specifies <spec_ids>`, `--body <text>`
- Validate spec references
- Use snake_case for filename
- Write with correct frontmatter

**Files:**
- `src/jig/cli/create.py`
- `src/jig/cli/main.py`

**Specs:** S-098

---

#### WU-11: Search Specs Command

**Scope:**
- Add `jigy search specs <query>` command
- Search title and body content
- Show match location (title/body)
- Human and JSON output

**Files:**
- `src/jig/cli/show.py`
- `src/jig/cli/main.py`

**Specs:** S-099

---

### Phase 3: Enhanced Output (P2)

#### WU-12: JSON Output on Show Commands

**Scope:**
- Add `--format json` to all existing show commands
- Consistent NDJSON for lists, compact JSON for single objects
- Update: `show layers`, `show bricks`, `show charter`, etc.

**Files:** `src/jig/cli/show.py`, `src/jig/cli/towers.py`

**Specs:** S-100

---

#### WU-13: Enhanced Validation JSON

**Scope:**
- Add `fix` field to ValidationError
- Standardize all error codes
- Add fix hints for common errors
- Update JSON output format

**Files:**
- `src/jig/validation/models.py`
- `src/jig/validation/reporting.py`
- `src/jig/validation/intent.py`
- `src/jig/validation/bricks.py`

**Specs:** S-100

---

#### WU-14: Create Specifications

**Scope:**
- Create S-093 through S-105 (13 specifications)
- Create O-027

**Files:**
- `jig/specifications/S-093_Graph_Query_Commands.md`
- `jig/specifications/S-094_Coverage_Gap_Auditing.md`
- `jig/specifications/S-095_Project_Initialization.md`
- `jig/specifications/S-096_Artifact_ID_Generation.md`
- `jig/specifications/S-097_Specification_Creation.md`
- `jig/specifications/S-098_Outcome_Creation.md`
- `jig/specifications/S-099_Specification_Search.md`
- `jig/specifications/S-100_JSON_Output_Format.md`
- `jig/specifications/S-101_Generated_Directory_README.md`
- `jig/specifications/S-102_Gitignore_Recommendation.md`
- `jig/specifications/S-103_Dynamic_Context_Generation.md`
- `jig/specifications/S-104_Context_Output_Formats.md`
- `jig/specifications/S-105_Agent_Context_Architecture.md`
- `jig/outcomes/O-027_Agent_Oriented_Tooling.md`

---

#### WU-15: Tests for New Commands

**Scope:**
- Tests for graph_utils.py
- Tests for show spec/specs
- Tests for audit gaps
- Tests for context command (all three formats)
- Tests for init command
- Tests for next-id, spec new, outcome new
- Tests for search specs

**Files:** `tests/cli/test_*.py`

---

## PART I: Dependency Graph

```
                    WU-14 (create specs S-093..S-105, O-027)
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
     WU-1                       WU-7                      WU-4D
  (graph utils)              (templates)              (CLAUDE.md
         │                          │                   update)
    ┌────┴────┬─────────┐          │                      │
    │         │         │          │                      ▼
    ▼         ▼         ▼          ▼                   WU-4E
 WU-2      WU-4      WU-4B      WU-5              (contextJIG.md
(show      (audit   (context   (init)                 role doc)
 spec)      gaps)    cmd)         │
    │         │         │         │
    ▼         │         ▼         ▼
 WU-3        │      WU-4C      WU-6
(show        │    (markdown  (auto-readme
 specs)      │     format)   on rebuild)
             │
             └──────────────────────────┐
                                        │
                    WU-8                │
                  (next-id)             │
                     │                  │
         ┌───────────┴───────────┐      │
         │                       │      │
         ▼                       ▼      │
      WU-9                    WU-10     │
  (spec new)              (outcome new) │
         │                       │      │
         └───────────┬───────────┘      │
                     │                  │
                     ▼                  │
                  WU-11                 │
              (search specs)            │
                                        │
         ┌───────────────────────┐      │
         │                       │      │
         ▼                       ▼      │
      WU-12                   WU-13     │
   (JSON on                (enhanced    │
 show cmds)              validation)    │
         │                       │      │
         └───────────┬───────────┘      │
                     │                  │
                     ▼                  │
                  WU-15 ◄───────────────┘
                 (tests)
```

### Phase Organization

| Phase | Work Units | Focus |
|-------|------------|-------|
| **Phase 1 (P0)** | WU-1, WU-2, WU-3, WU-4, WU-4B, WU-4C, WU-4D, WU-4E | Graph queries, context command, documentation |
| **Phase 2 (P1)** | WU-5, WU-6, WU-7, WU-8, WU-9, WU-10, WU-11 | Init, templates, artifact creation |
| **Phase 3 (P2)** | WU-12, WU-13, WU-14, WU-15 | JSON enhancement, specs, tests |

### Work Unit Count

| Category | Count |
|----------|-------|
| Core graph queries | 4 (WU-1..WU-4) |
| Context injection | 4 (WU-4B..WU-4E) |
| Initialization | 3 (WU-5..WU-7) |
| Artifact creation | 4 (WU-8..WU-11) |
| Enhancement & docs | 4 (WU-12..WU-15) |
| **Total** | **19 work units** |

---

## PART J: Risks and Mitigations

### J.1 Risk: Graph File Size

**Risk:** Loading entire graphs into memory may be slow for large codebases.

**Mitigation:**
- Use `iter_ndjson()` for scanning operations
- Only load full graph when needed for cross-referencing
- Consider caching parsed graph in memory during command

### J.2 Risk: Stale Graphs

**Risk:** Queries may return stale data if graphs not rebuilt.

**Mitigation:**
- All query commands call `ensure_graphs_current()` first
- Auto-rebuild is already implemented (S-070)
- `--no-rebuild` flag available for explicit skip

### J.3 Risk: Template File Distribution

**Risk:** Templates not included in package.

**Mitigation:**
- Explicit `package-data` in pyproject.toml
- Test that templates load correctly after install
- Fallback to inline strings if file missing

### J.4 Risk: Breaking Change to Validation JSON

**Risk:** Enhanced JSON format may break existing consumers.

**Mitigation:**
- New fields are additive (existing fields unchanged)
- `fix` field is optional
- Document schema in validation module docstring

---

## PART K: Success Criteria

### K.1 Functional Criteria

1. `jigy show spec S-001` displays complete S-F-T triangle
2. `jigy show specs --unimplemented` lists only unimplemented specs
3. `jigy audit gaps` identifies all coverage gaps
4. `jigy context` generates dynamic project summary
5. `jigy context --format markdown` outputs LLM-optimized context (~25 lines)
6. `jigy context --format json` outputs compact JSON for programmatic use
7. `jigy init` creates complete directory structure (per A-001 File Structure)
8. `jigy next-id spec` returns next available ID (format per A-001: `S-{NNN}`)
9. `jigy spec new "Title"` creates valid specification file
10. `jigy search specs "keyword"` finds matching specs
11. All new commands support `--format json`

### K.2 C007 Criteria

1. `jig/generated/README.md` is auto-created on rebuild
2. `jigy init` offers to update .gitignore
3. Templates exist in `src/jig/templates/`
4. Generated directory structure matches A-001 File Structure section

### K.3 Charter Alignment Criteria

1. New commands support G-001 (Grounding) — agents query, don't guess
2. JSON output supports G-002 (Continuity) — programmatic context extraction
3. Validation supports G-003 (Constraints) — error codes and fix hints
4. Artifact creation supports G-004 (Intent Alignment) — correct format before coding
5. Gap auditing supports G-005 (Traceability) — identify breaks in S-F-T chain

### K.4 Context Architecture Criteria

1. `CLAUDE.md` is minimal (~50 lines) and points to `jigy context`
2. `jigy context` outputs dynamic project state (not static documentation)
3. `agents/contextJIG.md` has header clarifying its role as deep reference
4. Agent can get full orientation with: CLAUDE.md (auto) + `jigy context` (one call)
5. Manual injection of `agents/contextJIG.md` is no longer required for basic tasks

### K.5 Documentation Criteria

1. CLAUDE.md references new commands including `jigy context`
2. Specifications S-093 through S-105 exist with proper A-001 format
3. Outcome O-027 exists with `supports_goals` referencing Charter goals
4. All new specs have `@jig.implements` decorators in implementation

### K.6 Test Criteria

1. All new commands have test coverage
2. `jigy context` tested with all three output formats
3. `jigy validate` passes
4. `jigy rebuild` succeeds
5. `jigy align` shows complete traceability for new specs

---

## References

### Charter and Architecture
- `jig/Charter.md` — Defines G-001 through G-005 (the five Charter goals this work supports)
- `jig/architecture/A-001_JIG_Core_Architecture.md` — Defines intent hierarchy, artifact formats, file structure

### Source Proposals
- `dig/wip/C006_PROPOSAL_JIG_Tools_Skills_Architecture.md` — Agent tools architecture proposal
- `dig/wip/C007_PROPOSAL_Gitignore_Generated_Graphs.md` — Gitignore and init command proposal

### Related SCOPE Documents
- `dig/archive/C003_SCOPE_Extended-Intent-Hierarchy-and-Towers.md` — Established G-A-O-S-C-T hierarchy
- `dig/wip/C010_SCOPE_Standardized-Intent-Document-Naming.md` — Filename format conventions

### Current Implementation
- `src/jig/cli/` — Existing CLI commands to extend
- `src/jig/validation/` — Existing validation to enhance

