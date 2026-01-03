# B006: Intent Summary Report

**Status:** Proposal (Revised v2)
**Author:** AI Assistant
**Date:** 2025-12-02
**Updated:** 2025-12-02

## Problem Statement

There is no quick-reference document that shows the **intent** (outcomes and specifications) organized by architectural structure (layers → bricks). Currently:

- Outcomes and specs are flat directories
- Understanding "what does brick X intend to do?" requires reading multiple files
- AI agents and humans lack a quick reference for brick-level intent

## Goal

Generate a deterministic (no LLM) report that organizes all intent artifacts by:

```
Layer N
└── Brick
    └── Outcome (O-xxx: Title)
        └── Specification (S-xxx: Title)
```

This provides a scannable "table of contents" for the project's intent.

---

## Design Decisions (Resolved)

| Question | Decision |
|----------|----------|
| **Schema: Title location** | Add `title:` to frontmatter (safer, more deterministic) |
| **Specs in multiple outcomes** | Allow - spec repeats under each brick |
| **B-visualizer outcomes** | Separate project - will be removed from JIG core |
| **Output location** | `jig/generated/` (official output location) |
| **Store alignment graph?** | NO - compute on-the-fly per A001 §9 (derivation contract) |

---

## A001 Compliance Analysis

### Issue: A001 §9 Derivation Contract

A001 states:
> "The following data SHALL be computed on demand, NOT stored:
> - Brick assignments for functions
> - Alignment metrics"

Storing `alignment-graph.ndjson` would violate this. Instead:
- Compute alignment graph **in-memory** on demand
- Provide reusable function for multiple consumers
- Optionally output to stdout for inspection (not stored in `jig/generated/`)

### Required A001 Amendments

The following changes to A001 are needed to support this feature:

#### 1. Add `title` to Specification Frontmatter (Section 2)

```yaml
---
id: S-001
type: specification
title: Python code structure extracted via AST analysis   # NEW (REQUIRED)
---
```

#### 2. Add `title` to Outcome Frontmatter (Section 3)

```yaml
---
id: O-001
type: outcome
title: Implementation structure is discoverable from source code   # NEW (REQUIRED)
specifies: [S-001, S-002]
---
```

#### 3. Add `title` to Specification Node Schema (Section 6.1)

```json
{"id":"S-001","type":"specification","title":"Python code structure...","file":"jig/specifications/S-001.md"}
```

#### 4. Add `title` to Outcome Node Schema (Section 6.1)

```json
{"id":"O-001","type":"outcome","title":"Implementation structure...","file":"jig/outcomes/O-001.md","specifies":["S-001","S-002"]}
```

#### 5. Add `units` to Brick Node Schema (Section 6.1)

Currently in practice but not in A001:
```json
{"id":"B-auth","type":"brick","name":"...","layer":1,"units":["M-auth.session"],"file":"jig/bricks.yaml"}
```

---

## Solution: In-Memory Alignment Graph

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AlignmentGraph (in-memory)                │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐        │
│  │intent-graph │ + │ impl-graph  │ = │  Computed   │        │
│  │  .ndjson    │   │  .ndjson    │   │  Indexes    │        │
│  └─────────────┘   └─────────────┘   └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │jigy intent   │ │jigy align    │ │ AI Agent     │
      │   summary    │ │   (stdout)   │ │   queries    │
      └──────────────┘ └──────────────┘ └──────────────┘
              │               │
              ▼               ▼
      intent-summary.md   NDJSON to stdout
      (stored)            (ephemeral)
```

### Data Structure

```python
@dataclass
class AlignedSpec:
    """Specification with computed alignment data."""
    id: str
    title: str
    file: str
    implementing_functions: list[str]  # [F-xxx, C-xxx, ...]
    bricks: list[str]                  # [B-xxx, ...] derived from functions
    outcomes: list[str]                # [O-xxx, ...] reverse lookup
    status: Literal["implemented", "unimplemented", "partial"]

@dataclass
class AlignedOutcome:
    """Outcome with computed alignment data."""
    id: str
    title: str
    file: str
    specifies: list[str]               # [S-xxx, ...]
    bricks: list[str]                  # union of spec.bricks

@dataclass
class AlignedBrick:
    """Brick with computed alignment data."""
    id: str
    name: str
    layer: int
    units: list[str]                   # [M-xxx, C-xxx, F-xxx, ...]
    specs: list[str]                   # specs implemented by this brick
    outcomes: list[str]                # outcomes with specs in this brick
    functions: list[str]               # all functions in this brick

@dataclass
class AlignmentGraph:
    """Complete alignment graph with computed indexes."""
    # Primary data (from source graphs)
    specs: dict[str, AlignedSpec]
    outcomes: dict[str, AlignedOutcome]
    bricks: dict[str, AlignedBrick]
    functions: dict[str, dict]         # raw function nodes from impl-graph

    # Computed indexes for fast lookup
    function_to_brick: dict[str, str]  # F-xxx -> B-xxx

    # Summary stats
    total_specs: int
    implemented_specs: int
    unimplemented_specs: list[str]
    multi_brick_specs: list[str]       # specs spanning multiple bricks
```

### Core Function

```python
def build_alignment_graph(
    project_root: Path,
    intent_graph_path: Path | None = None,
    impl_graph_path: Path | None = None,
) -> AlignmentGraph:
    """
    Build alignment graph by joining intent and implementation graphs.

    This is the single source of truth for alignment computation.
    All alignment queries should use this function.

    Args:
        project_root: Project root directory
        intent_graph_path: Override path to intent-graph.ndjson
        impl_graph_path: Override path to implementation-graph.ndjson

    Returns:
        AlignmentGraph with all computed indexes

    Raises:
        FileNotFoundError: If required graph files don't exist
    """
```

### Join Algorithm

```python
def _compute_spec_to_bricks(
    specs: dict[str, AlignedSpec],
    functions: dict[str, dict],
    function_to_brick: dict[str, str],
) -> None:
    """Compute which bricks implement each spec."""

    # For each function with implements: [S-xxx, ...]
    for func_id, func_node in functions.items():
        if not func_node.get("implements"):
            continue

        brick_id = function_to_brick.get(func_id)
        if not brick_id:
            continue  # function not in any brick (validation issue)

        for spec_id in func_node["implements"]:
            if spec_id in specs:
                specs[spec_id].implementing_functions.append(func_id)
                if brick_id not in specs[spec_id].bricks:
                    specs[spec_id].bricks.append(brick_id)
```

### Unit Matching Logic

```python
def _function_matches_unit(func_id: str, unit: str) -> bool:
    """Check if function ID matches a brick unit pattern."""

    # Strip prefixes for comparison
    func_path = func_id[2:]  # Remove "F-" or "C-"
    unit_path = unit[2:]     # Remove "M-", "C-", or "F-"
    unit_type = unit[0]      # "M", "C", or "F"

    if unit_type == "F":
        # Exact function match
        return func_id == unit

    elif unit_type == "M":
        # Module match: F-a.b.c.func matches M-a.b.c
        # Also: F-a.b.c.Class.method matches M-a.b.c
        return func_path.startswith(unit_path + ".")

    elif unit_type == "C":
        # Class match: F-a.b.c.Class.method matches C-a.b.c.Class
        return func_path.startswith(unit_path + ".")

    return False
```

---

## CLI Commands

### `jigy intent summary`

Generates the human-readable intent summary report.

```bash
jigy intent summary                    # Output to jig/generated/intent-summary.md
jigy intent summary --output report.md # Custom output path
jigy intent summary --stdout           # Output to stdout (no file)
```

### `jigy align`

Outputs the computed alignment graph for inspection/AI agents.

```bash
jigy align                             # NDJSON to stdout
jigy align --format json               # Pretty JSON to stdout
jigy align --format yaml               # YAML to stdout
jigy align --query "brick:B-cli"       # Filter to specific brick
jigy align --query "spec:S-001"        # Filter to specific spec
```

**Key point:** `jigy align` outputs to **stdout**, not to a file. This respects A001's derivation contract while still providing the data for consumption.

**Use cases:**
- AI agents: `jigy align | jq '.specs["S-001"]'`
- Debugging: `jigy align --format json | less`
- Piping: `jigy align | custom-tool`

---

## Workflow

```bash
# Step 1: Generate implementation graph (discovers @jig.implements)
jigy impl rebuild

# Step 2: Validate JIG artifacts
jigy validate

# Step 3: Generate intent graph (specs, outcomes, bricks - now with titles)
jigy intent rebuild

# Step 4: Generate intent summary report (computes alignment on-the-fly)
jigy intent summary

# Optional: Inspect alignment graph directly
jigy align --format json
```

---

## Data Flow Diagram

```
┌──────────────────┐     ┌──────────────────┐
│  jig/specs/*.md  │     │  jig/outcomes/*  │
│  jig/bricks.yaml │     │                  │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         ▼                        ▼
┌──────────────────────────────────────────┐
│         jigy intent rebuild              │
└────────────────────┬─────────────────────┘
                     ▼
         ┌───────────────────────┐
         │ intent-graph.ndjson   │
         │ (specs, outcomes,     │
         │  bricks with titles)  │
         └───────────┬───────────┘
                     │
┌──────────────────┐ │
│  src/**/*.py     │ │
│  @jig.implements │ │
└────────┬─────────┘ │
         │           │
         ▼           │
┌────────────────────┴─────────────────────┐
│            jigy impl rebuild             │
└────────────────────┬─────────────────────┘
                     ▼
         ┌───────────────────────┐
         │ implementation-graph  │
         │    .ndjson            │
         │ (functions with       │
         │  implements:[...])    │
         └───────────┬───────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│       build_alignment_graph()            │
│       (in-memory, on-demand)             │
└────────────────────┬─────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│jigy intent      │    │jigy align       │
│   summary       │    │   (stdout)      │
└────────┬────────┘    └────────┬────────┘
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│intent-summary.md│    │NDJSON to stdout │
│(stored)         │    │(ephemeral)      │
└─────────────────┘    └─────────────────┘
```

---

## Output: intent-summary.md

**Location:** `jig/generated/intent-summary.md`

```markdown
# Intent Summary

> Generated: 2025-12-02T18:45:19Z
> Specs: 43 | Outcomes: 16 | Bricks: 6 | Layers: 2

---

## Layer 0: Foundation

### B-decorators: JIG Core Decorators

**O-002: Traceability decorators enable spec coverage tracking**
- S-002: @jig.implements() decorator extracts spec IDs

### B-impl-graph: Implementation Graph

**O-001: Implementation structure is discoverable from source code**
- S-001: Python code structure extracted via AST analysis
- S-003: NDJSON output format deterministic and git-friendly
- S-005: External dependencies tracked at package level
- S-006: Parse errors fail fast with clear file:line reporting

**O-003: Support for multiple programming languages**
- S-004: Language analyzer plugin architecture

### B-validation: Artifact Validation

**O-005: Clear Actionable Error Messages**
- S-018: Validation errors include file paths
- S-019: Error messages grouped by phase
- S-020: Summary shows total error count
- S-021: Errors describe what's wrong
- S-022: Errors imply how to fix

**O-012: Brick definitions comply with A001 format requirements**
- S-035: Brick ID format validation
- S-036: Layer field presence validation
- S-037: Layer value validation

**O-013: Layer architecture is enforced and validated**
- S-038: Layer constraint validation
- S-039: Circular dependency detection

**O-015: Completeness validation for intent graph**
- S-042: Validate outcomes specify at least one specification
- S-043: Validate specifications are specified by at least one outcome

**O-016: Reporting formats**
- S-026: Multiple output formats for validation results

### B-intent-graph: Intent Graph

**O-009: Intent artifacts captured in queryable graph**
- S-028: Intent graph generation from JIG artifacts

### B-languages: Language Analyzers

**O-003: Support for multiple programming languages**
- S-004: Language analyzer plugin architecture

---

## Layer 1: Interface

### B-cli: CLI Interface

**O-004: Automated validation catches configuration errors**
- S-023: Intent Validation CLI Command
- S-024: Brick Validation CLI Command
- S-025: Full Validation CLI Command
- S-027: Auto-validate decorators after impl rebuild

**O-006: Single command validates entire project**
- S-023: Intent Validation CLI Command
- S-024: Brick Validation CLI Command
- S-025: Full Validation CLI Command

**O-014: Layer structure is visible and manageable**
- S-040: CLI Command: jigy layers
- S-041: CLI Command: jigy layers suggest

---

## Unimplemented Specifications

The following specs have no `@jig.implements` decorators:

| Spec | Title | Outcome |
|------|-------|---------|
| S-007 | Implementation graph visualization | O-007 (visualizer) |
| S-008 | ... | O-007 (visualizer) |

*Note: Visualizer specs (O-007, O-008, O-010, O-011) will move to separate project.*

---

## Specs in Multiple Bricks

The following specs are implemented across multiple bricks:

| Spec | Title | Bricks |
|------|-------|--------|
| (none detected) | | |
```

---

## Implementation Plan

### Phase 1: Schema Migration
1. Add `title:` field to all 43 specifications (frontmatter)
2. Add `title:` field to all 16 outcomes (frontmatter)
3. Update `jigy intent rebuild` to extract and include titles in intent-graph nodes
4. Validate: every spec/outcome has title field
5. Update A001 to document new required fields

### Phase 2: Alignment Graph Module
1. Create `src/jig/alignment/__init__.py`
2. Create `src/jig/alignment/graph.py` with:
   - `AlignedSpec`, `AlignedOutcome`, `AlignedBrick` dataclasses
   - `AlignmentGraph` dataclass
   - `build_alignment_graph()` function
   - Unit matching logic (`_function_matches_unit`)
   - Spec → brick computation (`_compute_spec_to_bricks`)
3. Create `src/jig/alignment/serializers.py` with:
   - `to_ndjson()` - for stdout output
   - `to_json()` - for pretty-printed output
   - `to_yaml()` - optional

### Phase 3: Summary Report Generator
1. Create `src/jig/alignment/summary.py` with:
   - `generate_intent_summary()` function
   - Markdown template/formatting
   - Layer → Brick → Outcome → Spec organization
2. Output to `jig/generated/intent-summary.md`

### Phase 4: CLI Integration
1. Add `jigy align` command (outputs to stdout)
   - `--format ndjson|json|yaml`
   - `--query brick:B-xxx` or `--query spec:S-xxx` filtering
2. Add `jigy intent summary` command
   - `--output <path>` (default: jig/generated/intent-summary.md)
   - `--stdout` flag
3. Update help text and documentation

### Phase 5: New Brick
1. Add `B-alignment` brick to bricks.yaml
   - Layer 0 (depends on nothing, foundation)
   - Units: `M-jig.alignment`
2. Create specifications for alignment graph (if needed)

---

## Edge Cases

### Spec implemented by multiple bricks

**Scenario:** S-006 is implemented by functions in both B-impl-graph and B-languages.

**Resolution:** `spec.bricks = ["B-impl-graph", "B-languages"]`

In report, spec appears under BOTH bricks. This is useful information (shows cross-cutting concern or potential design smell).

### Spec with no implementations

**Scenario:** S-007 (visualizer spec) has no `@jig.implements` decorators.

**Resolution:** `spec.bricks = []`, `spec.status = "unimplemented"`

In report, shown in "Unimplemented Specifications" section.

### Outcome spanning multiple bricks

**Scenario:** O-004's specs are implemented across B-cli and B-validation.

**Resolution:** `outcome.bricks = ["B-cli", "B-validation"]`

In report, outcome appears under BOTH bricks. This might indicate:
- Outcome is cross-cutting (OK)
- Outcome should be split (design smell)

### Brick with no specs

**Scenario:** B-languages has no specs with implementations yet.

**Resolution:** Brick appears in report with no outcomes/specs listed. Shows intent gap.

### Function not in any brick

**Scenario:** Implementation graph has function F-xxx but no brick unit matches it.

**Resolution:** Log warning during alignment graph build. Function's `implements` specs are orphaned (no brick assignment). This is a brick partition validation issue.

---

## Future: Caching Strategy

If performance becomes an issue (large projects, frequent queries), we can add caching:

1. **Location:** `jig/generated/.cache/alignment-graph.json`
2. **Invalidation:** Check mtime of intent-graph.ndjson and implementation-graph.ndjson
3. **Gitignore:** Add `.cache/` to `.gitignore`
4. **CLI flag:** `--no-cache` to force rebuild

This respects A001's derivation contract (cache is ephemeral, not source of truth) while improving performance.

---

## Visualizer Specs: Migration Plan

**Decision:** Visualizer is a separate project.

**Action items:**
1. Remove outcomes O-007, O-008, O-010, O-011 from jig/outcomes/
2. Remove specs S-007 through S-017, S-029 through S-034 from jig/specifications/
3. Move to separate viz repository
4. Update JIG to only contain core functionality

**Result:** JIG core will have ~25 specs (down from 43).

---

## Appendix: Current Implementation Coverage

Based on implementation-graph.ndjson analysis:

| Spec | Implementing Functions | Brick |
|------|------------------------|-------|
| S-001 | C-jig.impl_graph.builder.GraphBuilder | B-impl-graph |
| S-003 | C-jig.impl_graph.graph.Graph, C-jig.impl_graph.ndjson_writer.NDJSONWriter | B-impl-graph |
| S-004 | C-jig.impl_graph.analyzers.base.LanguageAnalyzer | B-languages |
| S-005 | F-jig.impl_graph.analyzers.python.PythonAnalyzer._is_internal_module | B-languages |
| S-006 | C-jig.impl_graph.analyzers.python.ParseError, C-jig.impl_graph.builder.GraphBuilder | B-impl-graph, B-languages |
| S-023 | F-jig.cli.validate.validate_intent_command | B-cli |
| S-024 | F-jig.cli.validate.validate_bricks_command | B-cli |
| S-025 | F-jig.cli.validate.validate_full_command | B-cli |
| S-027 | F-jig.cli.validate.auto_validate_decorators | B-cli |
| S-040 | F-jig.cli.layers.layers_command | B-cli |
| S-041 | F-jig.cli.layers.suggest_layers_command | B-cli |

*Partial list - full coverage will be computed by `jigy align`.*

---

## Summary

**The plan works.** The data exists:
- implementation-graph has `implements: [spec_ids]` on functions/classes
- intent-graph has `units: [M-xxx, ...]` on bricks

**Architecture:**
- `AlignmentGraph` - in-memory data structure, computed on-demand
- `build_alignment_graph()` - reusable function, single source of truth
- No stored alignment file (respects A001 §9 derivation contract)

**New module:**
- `src/jig/alignment/` - graph builder, serializers, summary generator

**Schema changes to A001:**
- Add `title:` to spec/outcome frontmatter (REQUIRED)
- Add `title:` to spec/outcome nodes in intent-graph
- Add `units:` to brick nodes in intent-graph (already in practice)

**CLI commands:**
- `jigy align` - output alignment graph to stdout (NDJSON/JSON/YAML)
- `jigy intent summary` - generate intent-summary.md report

**Output:**
- `jig/generated/intent-summary.md` - human-readable Layer → Brick → Outcome → Spec report
