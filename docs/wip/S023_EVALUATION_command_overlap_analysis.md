---
delta_type: analysis
created: 2025-11-22
related_plan: docs/wip/S022_PLAN_validate_consistency.md
---

# EVALUATION: Command Overlap Analysis

## Overview

This document analyzes three core JIG commands (`index rebuild`, `validate`, `status`) to understand their distinctions, overlaps, and potential redundancies from both implementation and user value perspectives.

## Executive Summary

### The Three Commands

1. **`jigy index rebuild`** - *Source scanner and graph builder*
   - Scans all sources (markdown + code annotations)
   - Builds `graph-index.yaml` artifact
   - Performs build-time validation
   - **Primary role:** Synchronization and artifact generation

2. **`jigy validate`** - *Schema and consistency checker*
   - Validates markdown files (O/S/X nodes)
   - Checks graph-index.yaml consistency
   - Validates edge rules and relationships
   - **Primary role:** Quality assurance and error detection

3. **`jigy status`** - *Health dashboard and metrics*
   - Loads graph-index.yaml
   - Calculates health metrics
   - Shows subsystems, orphans, warnings
   - **Primary role:** Observability and actionable insights

### Key Finding

**Significant overlap exists in validation logic, but each command serves a distinct user need.** The redundancy is primarily in implementation (3 different code paths that load/validate the graph), not in user value (each command has unique output and workflow purpose).

---

## Detailed Analysis

### 1. Index Rebuild (`jigy index rebuild`)

#### Purpose
Generate `graph-index.yaml` from source files (markdown + code annotations), establishing sources as the source of truth.

#### Implementation Details

**Data Flow:**
```
Markdown files (O/S/X) → Parser → OSTCNode
Code annotations (C/T) → Scanner → OSTCNode
                               ↓
                    Merge + Detect Conflicts
                               ↓
                    Validate Relationships
                               ↓
                    Write graph-index.yaml
```

**Key Components:**
- `IndexBuilder.discover_markdown_nodes()` - Scans `jig/` directories
- `IndexBuilder.discover_annotation_nodes()` - Scans `src/`, `test/` for `@jig` annotations
- `IndexBuilder.build()` - Merges, detects conflicts, validates
- `IndexBuilder.write_yaml()` - Serializes to YAML

**Validation Performed:**
- ✓ Duplicate ID detection (across all sources)
- ✓ Node ID format validation (regex: `^[OSTC]-[A-Z]+-\d+$`)
- ✓ Node type validation (outcome, specification, constraint, code, test)
- ✓ Relationship target existence (validates edges reference valid nodes)
- ✓ Status-based filtering (excludes template/deprecated/draft)
- ⚠️ Warns on missing subsystem assignments

**Output:**
```
Scanning sources:
  ✓ jig/outcomes/*.md (16 nodes)
  ✓ jig/specifications/*.md (39 nodes)
  ✓ jig/constraints/*.md (1 node)
  ✓ src/ for @jig annotations (37 code nodes)
  ✓ test/ for @jig annotations (122 test nodes)

Total nodes: 215 (16 O, 39 S, 37 C, 122 T)
Total edges: ~422

Validating...
  ✓ All node IDs valid
  ✓ All edge targets exist
  ✓ No duplicate node IDs

Writing jig/graph-index.yaml...
  ✓ Backed up to jig/graph-index.yaml.bak
  ✓ Wrote 215 nodes

✅ Done!
```

**User Value:**
- **When to use:** After adding/modifying markdown files or code annotations
- **Outcome:** graph-index.yaml is synchronized with sources
- **Analogy:** Like running `make` or `build` - transforms sources into artifact

---

### 2. Validate (`jigy validate`)

#### Purpose
Check schema correctness and graph consistency without modifying files.

#### Implementation Details

**Data Flow:**
```
Markdown files → Parser → validate_node() → Schema checks
                                ↓
                    Collect all node IDs
                                ↓
graph-index.yaml → Load YAML → Compare node lists
                                ↓
    Graph.load_from_dir() → validate_edges() → Edge rules
                                ↓
                        Aggregate errors/warnings
```

**Key Components:**
- `validate_graph(intent_dir)` - Main validation logic
- `validate_node(node)` - Single node schema validation
- `validate_edges(graph)` - Edge type and target validation
- `validate_nested_subsystems(graph)` - Subsystem hierarchy validation

**Validation Performed:**
- ✓ Required fields (id, type, title)
- ✓ ID format (regex + prefix matches type)
- ✓ Valid type values (outcome, specification, constraint)
- ✓ No duplicate node IDs
- ✓ Graph index references existing nodes
- ✓ Edge types match allowed source/target types
- ✓ No self-loops
- ✓ Subsystem hierarchy has no cycles
- ⚠️ Warns on missing subsystem
- ⚠️ Warns on missing created date
- ⚠️ Warns on orphaned nodes (no edges)

**Current Limitation (Pre-WU1):**
- ❌ **Does NOT understand C/T nodes** (only scans markdown)
- ❌ **False errors:** Reports all C/T nodes as "non-existent" (159 false errors)
- ❌ **Root cause:** Manual markdown scanning instead of using `Graph.load_from_dir()`

**Output:**
```
Validating JIG graph...
✗ Validation failed: 159 errors

Node Summary:
  16 outcomes, 39 specifications, 1 constraint

Errors found:
  ✗ Graph index references non-existent node: C-CLI-003
  ✗ Graph index references non-existent node: C-CLI-004
  ... (157 more)

Warnings:
  ⚠ Unassigned nodes (5):
    O-TEST-001, S-AUTH-003, S-GRAPH-005, S-NESTED-002, S-NESTED-006

Suggestions:
  💡 Run 'jigy status' for detailed graph health metrics
  💡 Add 'subsystem: <name>' to frontmatter for 5 unassigned nodes
```

**User Value:**
- **When to use:** Before committing changes, in CI pipeline
- **Outcome:** Confidence that graph structure is valid
- **Analogy:** Like running `lint` or `test` - checks quality without changing files
- **Exit code:** 0 if valid, 1 if errors → suitable for CI gating

---

### 3. Status (`jigy status`)

#### Purpose
Display graph health metrics and provide actionable insights.

#### Implementation Details

**Data Flow:**
```
graph-index.yaml → Graph.load_from_dir() → Complete graph
                                ↓
                    Calculate Metrics:
                    - Node counts by type
                    - Subsystem hierarchy
                    - Orphaned nodes
                    - Unassigned nodes
                                ↓
                    Format with colors/styling
                                ↓
                    Show warnings + suggestions
```

**Key Components:**
- `calculate_status(intent_dir)` - Loads graph and computes metrics
- `format_status_output(status_data, verbose, flat, graph)` - Formats for display
- `format_subsystem_tree(subsystem, graph)` - Hierarchical tree rendering

**Metrics Calculated:**
- Total nodes, edges, subsystems
- Node counts by type (O/S/X/C/T)
- Subsystem hierarchy (tree view)
- Orphaned nodes (no edges)
- Unassigned nodes (no subsystem)

**Current Limitation (Pre-WU2):**
- ❌ **Shows 0 subsystems** (graph-index.yaml missing `subsystems:` section)
- ❌ **Root cause:** Index rebuild doesn't write subsystems section

**Output:**
```
JIG Graph Status

✓ 215 nodes, 183 edges, 0 subsystems

Node Summary:
  16 outcomes, 39 specifications, 1 constraint, 37 code, 122 test

Subsystems:
  (none shown - missing subsystems section)

Warnings:
  ⚠ Orphaned nodes (3):
    O-TEST-002, S-AUTH-007, C-CLI-015
  ⚠ Unassigned nodes (5):
    O-TEST-001, S-AUTH-003, S-GRAPH-005

Suggestions:
  💡 Add relationships to 3 orphaned nodes (use 'implements:', 'verifies:', or 'depends_on:')
  💡 Assign 5 nodes to subsystems (add 'subsystem: <name>' to frontmatter)
  💡 Run 'jigy validate' to check graph consistency
```

**User Value:**
- **When to use:** Quick health check during development
- **Outcome:** Understand graph state and get actionable suggestions
- **Analogy:** Like running `git status` - shows current state and next actions
- **Exit code:** Always 0 (informational, not gating)

---

## Overlap Analysis

### Implementation Overlap

#### 1. Graph Loading (HIGH overlap)

All three commands load the graph, but in **different ways**:

| Command | Loading Strategy | Node Types |
|---------|-----------------|------------|
| `index rebuild` | Scans sources directly | O/S/X/C/T |
| `validate` | Scans markdown + loads graph-index.yaml | **O/S/X only** ⚠️ |
| `status` | `Graph.load_from_dir()` | O/S/X/C/T |

**Problem:** Inconsistent loading strategies lead to inconsistent results.

**Solution (S-JIGY-012):** All commands should use `Graph.load_from_dir()`.

#### 2. Node Validation (MEDIUM overlap)

Both `index rebuild` and `validate` perform validation:

| Validation Check | Index Rebuild | Validate |
|-----------------|---------------|----------|
| ID format | ✓ | ✓ |
| Type validity | ✓ | ✓ |
| Duplicate IDs | ✓ | ✓ |
| Relationship targets exist | ✓ | ✓ |
| Edge type rules | ✗ | ✓ |
| Subsystem cycles | ✗ | ✓ |
| Schema (frontmatter) | ✗ | ✓ |

**Overlap:** Both check ID format, type validity, duplicates, relationship targets.

**Distinction:** 
- `validate` performs **deeper checks** (edge rules, subsystem cycles, schema)
- `index rebuild` performs **build-time validation** (fail fast if sources are broken)

**Is this redundancy necessary?**
- **Yes, for `index rebuild`**: Prevents writing invalid graph-index.yaml
- **Yes, for `validate`**: Provides comprehensive schema checks

**Potential consolidation:** Extract common validation into reusable functions (already done via `validate_node()`, `validate_edges()`).

#### 3. Counting Logic (HIGH overlap)

All three commands count nodes and edges:

| Command | Counting Method | Current Counts |
|---------|----------------|----------------|
| `index rebuild` | `len(result.nodes)` | 211 nodes, ~422 edges |
| `validate` | `_count_nodes(intent_dir)` | 56 nodes (O/S/X only) |
| `status` | `len(graph.nodes)`, `len(graph.edges)` | 215 nodes, 183 edges |

**Problem:** Three different implementations, three different answers!

**Solution (S-JIGY-014):** Use unified counting logic, shared across all commands.

### User Value Overlap

#### 1. Error Reporting (LOW overlap)

All three commands report errors, but for **different purposes**:

| Command | Error Context | User Action |
|---------|---------------|-------------|
| `index rebuild` | Build failed | Fix sources, retry rebuild |
| `validate` | Schema invalid | Fix frontmatter, fix relationships |
| `status` | Graph unhealthy | Add edges, assign subsystems |

**Overlap:** All show "unassigned nodes" warning.

**Distinction:**
- `validate` → **Blocks** (exit code 1, fails CI)
- `status` → **Suggests** (exit code 0, informational)
- `index rebuild` → **Prevents artifact** (exit code 1, fails build)

#### 2. Workflow Role (NO overlap)

Each command serves a **distinct workflow step**:

```
Developer Workflow:
1. Edit markdown/code → Add nodes, add relationships
2. Run `jigy index rebuild` → Synchronize graph-index.yaml
3. Run `jigy status` → Check health, get suggestions
4. Run `jigy validate` → Confirm no schema errors
5. Commit → CI runs `validate` again
```

**Sequential usage:**
- `rebuild` → `status` → `validate` → commit
- Each step adds value, none are redundant

**Parallel usage:**
- `status` (quick check during dev)
- `validate` (thorough check before commit)

---

## Redundancy Assessment

### What is Truly Redundant?

#### ❌ Minimal User-Facing Redundancy

- Each command serves a distinct purpose in the workflow
- Output format is different (build log vs. health dashboard vs. validation report)
- Exit codes have different meanings (gating vs. informational)

#### ✅ Significant Implementation Redundancy

1. **Graph loading logic** - Three different implementations (should be unified)
2. **Basic validation** - Duplicate ID checks, ID format validation (should reuse functions)
3. **Node counting** - Three different counting methods (should use shared utility)
4. **Warning formatting** - Similar warning messages (already shared via `formatting.py`)

### What Could Be Consolidated?

#### High-Value Consolidation (Recommended)

1. **Unified graph loading** (S-JIGY-012)
   - All commands use `Graph.load_from_dir()`
   - Eliminates false errors, count mismatches
   - **Effort:** 90-120 min (WU1)
   - **Impact:** Fixes 159 false errors

2. **Shared counting logic** (S-JIGY-014)
   - Extract `count_nodes_by_type()` and `count_edges()` to utility module
   - All commands use same functions
   - **Effort:** 45-60 min (WU4)
   - **Impact:** Consistent counts across commands

3. **Edge deduplication** (S-JIGY-014)
   - Ensure edges deduplicated: `{(from, to, type)}`
   - Use in both `rebuild` and `status`
   - **Effort:** 60-90 min (WU3)
   - **Impact:** Accurate edge counts

#### Low-Value Consolidation (Not Recommended)

1. **Merge `validate` into `index rebuild`**
   - **Why not:** Different workflows (build vs. check)
   - **User cost:** Lose CI-friendly validation-only command
   - **Analogy:** Don't merge `make` and `lint` into one command

2. **Merge `status` into `validate`**
   - **Why not:** Different output goals (health metrics vs. error list)
   - **User cost:** Lose quick health check (status is informational, validate gates)
   - **Analogy:** Don't merge `git status` and `git fsck` into one command

3. **Add `--validate` flag to `rebuild`**
   - **Why not:** Rebuild already validates during build
   - **Confusion:** What does "validate" mean in rebuild context?
   - **Better:** Keep validate as separate command

---

## Implementation Perspective

### Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Source Files                            │
│  jig/*.md  +  src/**/*.py (with @jig annotations)           │
└─────────────────────────────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
        ┌─────────────────┐   ┌─────────────────┐
        │ index rebuild   │   │   validate      │
        │ (scans sources) │   │ (scans markdown)│
        └────────┬────────┘   └────────┬────────┘
                 │                     │
                 ▼                     ▼
        ┌─────────────────────────────────────┐
        │      graph-index.yaml               │
        └─────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     status      │
                    │ (loads artifact)│
                    └─────────────────┘
```

**Problem:** `validate` doesn't understand `graph-index.yaml` C/T nodes, leading to false errors.

### Proposed Architecture (Post-WU1)

```
┌─────────────────────────────────────────────────────────────┐
│                      Source Files                            │
│  jig/*.md  +  src/**/*.py (with @jig annotations)           │
└─────────────────────────────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 │
        ┌─────────────────┐           │
        │ index rebuild   │           │
        │ (scans sources) │           │
        └────────┬────────┘           │
                 │                    │
                 ▼                    │
        ┌─────────────────────────────────────┐
        │      graph-index.yaml               │
        └─────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
        ┌─────────────────┐   ┌─────────────────┐
        │    validate     │   │     status      │
        │ (Graph.load)    │   │ (Graph.load)    │
        └─────────────────┘   └─────────────────┘
```

**Unified approach:**
- `validate` and `status` both use `Graph.load_from_dir()`
- `index rebuild` is the **only** command that scans sources
- Eliminates false errors, ensures consistency

---

## User Value Perspective

### What Users Expect

#### 1. Quick Health Check: `jigy status`

**Mental model:** "Show me the current state of my graph"

**Expected behavior:**
- Fast (< 1 second)
- Visual (colors, tree view)
- Actionable (suggestions for improvement)
- Non-blocking (always exit 0)

**Analogy:** `git status`, `docker ps`, `npm list`

**Current gaps:**
- ❌ Shows 0 subsystems (should show 7)
- ❌ Count doesn't match other commands

#### 2. Thorough Check: `jigy validate`

**Mental model:** "Is my graph correct? Can I commit?"

**Expected behavior:**
- Comprehensive (all schema checks)
- Blocking (exit 1 on errors)
- CI-friendly (parseable output)
- Conservative (better to fail safe than pass invalid)

**Analogy:** `eslint`, `pytest`, `cargo check`

**Current gaps:**
- ❌ 159 false errors for C/T nodes
- ❌ Can't use in CI (always fails)

#### 3. Synchronization: `jigy index rebuild`

**Mental model:** "Update graph-index.yaml from my sources"

**Expected behavior:**
- Deterministic (same input → same output)
- Atomic (backup + write)
- Validated (don't write invalid artifact)
- Verbose (show what changed)

**Analogy:** `make`, `npm run build`, `cargo build`

**Current gaps:**
- ❌ Doesn't export subsystems to graph-index.yaml
- ❌ Edge count is ~2x higher than expected

### Are All Three Commands Necessary?

#### ✅ Yes - Each Serves Distinct User Need

**Option 1: Merge all into one "super command"**
- ❌ Loses workflow clarity
- ❌ Confusing flags (--rebuild? --validate? --status?)
- ❌ Can't use in CI (can't run validate-only)
- ❌ Poor UX (different intents mixed together)

**Option 2: Keep all three commands**
- ✓ Clear workflow steps
- ✓ Composable (use in scripts, CI)
- ✓ Single Responsibility Principle
- ✓ Predictable behavior

**Analogy from Git:**
```
git add     → Stage changes (like index rebuild)
git status  → Show status (like jigy status)
git fsck    → Check integrity (like jigy validate)
```

**Analogy from Build Systems:**
```
make        → Build artifact (like index rebuild)
make test   → Run tests (like validate)
make status → Show info (like status)
```

---

## Recommendations

### 1. Keep All Three Commands (High Confidence)

**Rationale:**
- Distinct user value
- Clear workflow roles
- Industry standard patterns (git, cargo, npm)

**No merger recommended.**

### 2. Consolidate Implementation (High Priority)

**S-JIGY-012:** Unified graph loading
- All commands use `Graph.load_from_dir()`
- Eliminates false errors

**S-JIGY-013:** Subsystem export
- `index rebuild` writes subsystems to graph-index.yaml
- `status` can show subsystems

**S-JIGY-014:** Consistent counting
- Shared utility functions for node/edge counts
- All commands report same numbers

### 3. Clarify Command Relationships (Documentation)

Add to user guide:

```markdown
## Command Workflow

1. **After editing sources:** `jigy index rebuild`
   - Synchronizes graph-index.yaml with markdown and code annotations
   - Validates during build (fails if sources are invalid)

2. **During development:** `jigy status`
   - Quick health check with actionable suggestions
   - Shows subsystems, orphans, warnings
   - Always informational (never fails)

3. **Before committing:** `jigy validate`
   - Comprehensive schema and consistency checks
   - Blocks on errors (suitable for CI)
   - More thorough than rebuild validation

4. **In CI pipeline:** `jigy validate`
   - Gate commits on graph validity
   - Fast (loads artifact, doesn't rebuild)
```

### 4. Future Enhancements (Post-WU5)

**Incremental rebuild:**
- Track file mtimes, only rescan changed files
- Performance: <1s for incremental updates

**Validate-on-rebuild:**
- Option to skip validation during rebuild (for speed)
- `jigy index rebuild --skip-validation` (not recommended for CI)

**Status caching:**
- Cache metrics between runs (invalidate on graph-index.yaml change)
- Performance: <0.1s for cached status

---

## Comparison to Other Tools

### Git

| Git Command | JIG Equivalent | Purpose |
|-------------|----------------|---------|
| `git add` | `jigy index rebuild` | Stage changes |
| `git status` | `jigy status` | Show current state |
| `git fsck` | `jigy validate` | Check integrity |

**Lesson:** Three distinct commands for three distinct workflows.

### Cargo (Rust)

| Cargo Command | JIG Equivalent | Purpose |
|---------------|----------------|---------|
| `cargo build` | `jigy index rebuild` | Build artifact |
| `cargo check` | `jigy validate` | Fast validation |
| `cargo tree` | `jigy status` | Show dependencies |

**Lesson:** Build, validate, and visualize are separate concerns.

### NPM

| NPM Command | JIG Equivalent | Purpose |
|-------------|----------------|---------|
| `npm install` | `jigy index rebuild` | Sync dependencies |
| `npm audit` | `jigy validate` | Check for issues |
| `npm list` | `jigy status` | Show package tree |

**Lesson:** Synchronization, checking, and reporting are distinct.

---

## Conclusion

### Summary

1. **Overlap exists primarily in implementation, not user value**
   - All three commands serve distinct workflow needs
   - Redundancy is in graph loading and counting logic

2. **Consolidation should focus on internal code, not user-facing commands**
   - Unified graph loading (S-JIGY-012)
   - Shared counting utilities (S-JIGY-014)
   - Keep three separate CLI commands

3. **Current inconsistencies harm user trust**
   - Different commands report different counts
   - False errors make validation unusable
   - Missing subsystems make status incomplete

### Recommended Action

**Execute S022_PLAN_validate_consistency.md:**
- WU1: Fix validator (use unified graph loading)
- WU2: Fix subsystem export
- WU3-5: Fix counting consistency

**Do NOT merge commands.** Instead, fix the implementation inconsistencies that make them appear redundant.

### Final Verdict

**Three commands are the right design.** The problem is not too many commands, but inconsistent implementations. Fix the implementations (per S022_PLAN), and the overlap concerns will resolve naturally.

---

## Appendix: Implementation Consolidation Checklist

### Shared Utility Functions (To Create)

**`jig.core.graph_utils`** (new module):

```python
def count_nodes_by_type(graph: Graph) -> dict[str, int]:
    """Count nodes by type. Used by rebuild, validate, status."""
    counts = {}
    for node in graph.nodes.values():
        counts[node.type] = counts.get(node.type, 0) + 1
    return counts

def count_edges(graph: Graph, deduplicate: bool = True) -> int:
    """Count edges, optionally deduplicated by (from, to, type)."""
    if deduplicate:
        unique = {(e.from_node, e.to_node, e.type) for e in graph.edges}
        return len(unique)
    return len(graph.edges)

def format_node_type_summary(counts: dict[str, int]) -> str:
    """Format node counts like '16 O, 39 S, 1 X, 37 C, 122 T'."""
    type_map = {
        "outcome": "O",
        "specification": "S",
        "constraint": "X",
        "code": "C",
        "test": "T",
    }
    parts = []
    for type_name in ["outcome", "specification", "constraint", "code", "test"]:
        count = counts.get(type_name, 0)
        if count > 0:
            parts.append(f"{count} {type_map[type_name]}")
    return ", ".join(parts)
```

### Usage in Commands

**index.py (rebuild):**
```python
from jig.core.graph_utils import count_nodes_by_type, count_edges, format_node_type_summary

# Replace inline counting with:
type_counts = count_nodes_by_type(graph)
edge_count = count_edges(graph, deduplicate=True)
summary = format_node_type_summary(type_counts)
```

**status.py:**
```python
from jig.core.graph_utils import count_nodes_by_type, count_edges

# Replace inline counting with:
node_counts = count_nodes_by_type(graph)
total_edges = count_edges(graph, deduplicate=True)
```

**validate.py:**
```python
from jig.core.graph_utils import count_nodes_by_type

# Replace inline counting with:
type_counts = count_nodes_by_type(graph)
```

---

**Document Status:** Draft  
**Next Steps:** Review, then execute S022_PLAN WU1-WU5  
**Related:** docs/wip/S021_SCOPE_validate_consistency.md, docs/wip/S022_PLAN_validate_consistency.md

