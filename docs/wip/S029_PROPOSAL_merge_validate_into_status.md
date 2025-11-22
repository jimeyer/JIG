---
delta_type: proposal
created: 2025-11-22
related_analysis: docs/wip/S023_EVALUATION_command_overlap_analysis.md
status: draft
---

# PROPOSAL: Merge `jigy validate` into `jigy status`

## Overview

Simplify JIG's command interface by consolidating validation functionality into the status command, reducing the core workflow to two commands: `jigy index rebuild` and `jigy status`.

## Motivation

### Current State Complexity

The current three-command model creates unnecessary cognitive overhead:

```
jigy index rebuild  → Sync sources to graph-index
jigy status         → Show health metrics
jigy validate       → Check consistency
```

**User confusion:**
- "Do I need to run validate AND status?"
- "Which command should I run before committing?"
- "Why does status show warnings but not fail?"

### Proposed Simplification

```
jigy index rebuild  → Sync sources to graph-index
jigy status         → Show health metrics + validate
```

**Later evolution:**
```
jigy status         → Auto-rebuild if stale + show health + validate
```

### Key Insight

**Status and validation are the same user intent:** "Tell me if my graph is healthy and ready to commit."

The artificial separation between "show me issues" (status) and "block on issues" (validate) creates a workflow bifurcation that doesn't match user mental models.

## Rationale

### 1. Workflow Simplification

**Current workflow (confusing):**
```bash
# Edit files
jigy index rebuild
jigy status          # Shows warnings, but doesn't fail
jigy validate        # Actually checks if it's valid
# Commit
```

**Proposed workflow (clear):**
```bash
# Edit files
jigy index rebuild
jigy status          # Shows everything + validates
# Commit if status passed
```

**Future workflow (seamless):**
```bash
# Edit files
jigy status          # Auto-rebuilds, shows everything, validates
# Commit if status passed
```

### 2. Single Source of Truth

Having two commands that report on graph health creates confusion:

- Status says "3 orphaned nodes" (warning, exit 0)
- Validate says "159 errors" (blocking, exit 1)
- User: "Which one is correct? Should I commit?"

**After merge:** One command, one answer, clear exit code.

### 3. Industry Precedent Supports Consolidation

While S023 cited Git as supporting separate commands, Git's model is different:

**Git has mutation commands:**
- `git add` (mutates staging)
- `git commit` (mutates history)
- `git status` (read-only view)
- `git fsck` (deep integrity check)

**JIG has ONE mutation command:**
- `jigy index rebuild` (mutates graph-index)
- `jigy status` (read-only view)
- `jigy validate` ← **Redundant with status**

**Better analogy - Rust's cargo:**
- `cargo build` → Build artifact
- `cargo check` → Fast check + warnings + errors (single command!)

**Cargo doesn't have separate "show status" and "validate" commands.** `cargo check` does both.

### 4. Exit Code is Orthogonal to Command Name

S023 argued that status should always exit 0 (informational) while validate should exit 1 (gating).

**This is a false constraint.** Exit codes should be based on severity, not command name:

```bash
jigy status                    # Exit 0 if no errors, exit 1 if errors
jigy status --warn-only        # Always exit 0 (only show warnings)
jigy status --strict           # Exit 1 even on warnings
```

This gives users the flexibility they need without requiring separate commands.

### 5. Validation IS Status

Consider what validate actually does:
- Checks node schemas ✓
- Checks edge consistency ✓
- Checks subsystem hierarchy ✓
- Reports orphaned nodes ✓
- Reports unassigned nodes ✓

**These are all status metrics.** There's no fundamental distinction between "showing status" and "validating consistency."

## Proposed Design

### Command Behavior

#### `jigy status` (enhanced)

**Purpose:** Display graph health metrics and validate consistency.

**Validation levels:**

```bash
jigy status                    # Default: show all, exit 1 on errors
jigy status --warn-only        # Show all, always exit 0 (CI preview)
jigy status --strict           # Exit 1 on errors OR warnings
jigy status --quiet            # Only show errors/warnings, suppress metrics
```

**Output format:**

```
JIG Graph Status

✓ 215 nodes, 183 edges, 7 subsystems

Node Summary:
  16 outcomes, 39 specifications, 1 constraint, 37 code, 122 test

Subsystems:
  ✓ cli (12 nodes)
  ✓ core (45 nodes)
  ✓ validation (8 nodes)
  ...

Validation Results:

✓ Schema Checks
  ✓ All node IDs valid (215 nodes)
  ✓ No duplicate IDs
  ✓ All frontmatter fields valid

✓ Graph Consistency
  ✓ All edge targets exist (183 edges)
  ✓ No self-loops
  ✓ No subsystem cycles

Warnings:
  ⚠ Orphaned nodes (3):
    O-TEST-002, S-AUTH-007, C-CLI-015
  ⚠ Unassigned nodes (5):
    O-TEST-001, S-AUTH-003, S-GRAPH-005

Suggestions:
  💡 Add relationships to 3 orphaned nodes
  💡 Assign 5 nodes to subsystems

✅ Graph is valid (exit 0)
```

**Error output:**

```
JIG Graph Status

✗ 215 nodes, 183 edges, 7 subsystems

Node Summary:
  16 outcomes, 39 specifications, 1 constraint, 37 code, 122 test

Validation Results:

✗ Schema Checks
  ✗ Invalid node ID format: OTEST-001 (should be O-TEST-001)
  ✗ Missing required field 'title' in S-AUTH-003
  ✗ Unknown node type 'implementation' in C-CLI-007

✗ Graph Consistency
  ✗ Edge target does not exist: O-CLI-001 → S-CLI-999
  ✗ Invalid edge type 'requires' from specification to outcome
  ✗ Self-loop detected: S-AUTH-003 → S-AUTH-003

Warnings:
  ⚠ Orphaned nodes (3)
  ⚠ Unassigned nodes (5)

❌ Graph has 6 errors (exit 1)

Suggestions:
  💡 Fix schema errors in node files
  💡 Run 'jigy index rebuild' to regenerate graph-index
```

### Implementation Changes

#### 1. Merge Validation Logic into Status

**File: `src/jig/cli/status.py`**

Current:
```python
def status_command(intent_dir, verbose, flat):
    """Show graph status."""
    status_data = calculate_status(intent_dir)
    output = format_status_output(status_data, verbose, flat)
    print(output)
    return 0  # Always informational
```

Proposed:
```python
def status_command(intent_dir, verbose, flat, warn_only, strict, quiet):
    """Show graph status and validate consistency."""
    # Load graph
    graph = Graph.load_from_dir(intent_dir)
    
    # Calculate metrics (if not quiet)
    if not quiet:
        status_data = calculate_status(intent_dir, graph)
        print(format_status_output(status_data, verbose, flat))
    
    # Run validation
    validation_result = validate_graph_comprehensive(graph)
    print(format_validation_output(validation_result))
    
    # Determine exit code
    if warn_only:
        return 0
    if strict and (validation_result.errors or validation_result.warnings):
        return 1
    if validation_result.errors:
        return 1
    return 0
```

#### 2. Extract Validation Core Logic

**File: `src/jig/core/validation.py`** (new)

```python
@dataclass
class ValidationResult:
    """Result of graph validation."""
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    node_count: int
    edge_count: int
    checks_passed: dict[str, bool]
    
    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

def validate_graph_comprehensive(graph: Graph) -> ValidationResult:
    """
    Comprehensive graph validation.
    
    Checks:
    - Schema validation (node IDs, types, required fields)
    - Graph consistency (edge targets, no self-loops)
    - Subsystem hierarchy (no cycles, valid references)
    - Relationship rules (valid edge types)
    
    Returns ValidationResult with errors and warnings.
    """
    errors = []
    warnings = []
    
    # Schema checks
    for node in graph.nodes.values():
        errors.extend(validate_node_schema(node))
    
    # Graph consistency
    errors.extend(validate_edges(graph))
    errors.extend(validate_subsystem_hierarchy(graph))
    
    # Warnings
    warnings.extend(find_orphaned_nodes(graph))
    warnings.extend(find_unassigned_nodes(graph))
    
    return ValidationResult(
        errors=errors,
        warnings=warnings,
        node_count=len(graph.nodes),
        edge_count=len(graph.edges),
        checks_passed={
            "schema": len([e for e in errors if e.category == "schema"]) == 0,
            "consistency": len([e for e in errors if e.category == "consistency"]) == 0,
            "subsystems": len([e for e in errors if e.category == "subsystems"]) == 0,
        }
    )
```

#### 3. Remove validate.py

**File: `src/jig/cli/validate.py`** → DELETE

**File: `src/jig/cli/main.py`** → Remove `validate` subcommand

```python
# Remove this:
# @cli.command()
# def validate(...):
#     ...
```

#### 4. Update CLI Help

```bash
$ jigy --help

Usage: jigy [OPTIONS] COMMAND [ARGS]...

Commands:
  init           Initialize a new JIG project
  index rebuild  Rebuild graph index from sources
  status         Show graph status and validate consistency
  node           Interact with individual nodes
  graph          Graph visualization and queries
  decompose      Decomposition metrics

$ jigy status --help

Usage: jigy status [OPTIONS]

  Show graph health metrics and validate consistency.
  
  By default, shows all metrics and exits with code 1 if errors are found.

Options:
  --verbose         Show detailed node listings
  --flat            Show flat subsystem list (no tree)
  --warn-only       Always exit 0 (show warnings but don't fail)
  --strict          Exit 1 on errors OR warnings
  --quiet           Only show validation results (suppress metrics)
  --help            Show this message and exit

Examples:
  jigy status                     # Full status + validation
  jigy status --quiet             # Validation only
  jigy status --warn-only         # Never fail (CI preview mode)
  jigy status --strict            # Fail on warnings too
```

### Migration Path

#### Phase 1: Merge validate into status (this proposal)

**Changes:**
1. Add validation logic to `status` command
2. Add `--warn-only`, `--strict`, `--quiet` flags
3. Keep `validate` command as deprecated alias
4. Update documentation

**Timeline:** 1-2 weeks

**Backward compatibility:**
```bash
jigy validate        # Still works, shows deprecation warning
# → "Warning: 'jigy validate' is deprecated. Use 'jigy status' instead."
# → Runs status command with same exit code behavior
```

#### Phase 2: Auto-rebuild on stale index

**Changes:**
1. Detect if graph-index is stale (file mtimes)
2. Auto-run rebuild before status
3. Show "Rebuilding index..." message
4. Make `index rebuild` manual command for advanced use

**Timeline:** 2-4 weeks after Phase 1

**User experience:**
```bash
$ jigy status
Rebuilding index (sources changed)...
  ✓ Scanned 215 nodes
  ✓ Updated graph-index.json

JIG Graph Status
✓ 215 nodes, 183 edges, 7 subsystems
...
```

#### Phase 3: Remove validate command entirely

**Changes:**
1. Remove deprecated `validate` command
2. Update all documentation
3. Update CI examples

**Timeline:** 2-3 months after Phase 1 (allow deprecation period)

## Benefits

### 1. Simplified Mental Model

**Before:**
- User must remember 3 commands
- Unclear when to use each
- Redundant functionality

**After:**
- Two clear commands: build and check
- Obvious workflow: rebuild → status
- Single source of truth for health

### 2. Better Default Behavior

**Current problem:**
- `status` shows warnings but exits 0 → User commits broken graph
- `validate` shows errors but exits 1 → User doesn't know if it's serious

**After merge:**
- Errors → exit 1 (block commit)
- Warnings → exit 0 (allow commit)
- Clear distinction, single command

### 3. Easier CI Integration

**Before (confusing):**
```yaml
# Which command should CI run?
- run: jigy status      # This or...
- run: jigy validate    # ...this?
```

**After (obvious):**
```yaml
- run: jigy status      # That's it
```

### 4. Preparation for Auto-Rebuild

Merging validation into status is a prerequisite for auto-rebuild:

```python
def status_command(...):
    # Check if index is stale
    if index_is_stale():
        rebuild_index()
    
    # Show status + validate
    show_status_and_validate()
```

This flow only makes sense if status includes validation.

### 5. Consistent with "Status" Semantics

In most tools, "status" means "tell me if everything is OK":

- `git status` → Shows if working tree is clean (validation!)
- `systemctl status` → Shows if service is healthy (validation!)
- `docker ps` → Shows if containers are running (validation!)

**Status inherently includes validation.** The current separation is artificial.

## Validation Separation of Concerns

### The Fundamental Question

**"If index rebuild succeeds, shouldn't the graph already be valid? What's left for status to check?"**

This is the RIGHT question to ask, and the answer clarifies the entire design.

### Two Types of Validity

#### 1. Structural Validity (checked by `index rebuild`)

**Definition:** Can a well-formed artifact be built from these sources?

**Checks that MUST block artifact generation:**
- ✗ **Parse errors** - Malformed YAML/frontmatter → Can't parse file
- ✗ **Invalid node ID format** - `OTEST-001` instead of `O-TEST-001` → Violates schema
- ✗ **Duplicate node IDs** - Two nodes with `O-CLI-001` → Ambiguous references
- ✗ **Missing required fields** - No `id`, `type`, or `title` → Incomplete node definition
- ✗ **Dangling edge references** - Edge points to `S-GHOST-001` that doesn't exist → Broken graph
- ✗ **Invalid node types** - `type: implementation` → Unknown type

**Result:** If `index rebuild` exits 0, the artifact is **structurally sound**.

**Rationale:** You cannot build a corrupted artifact. Sources must be parseable and internally consistent.

#### 2. Semantic Validity (checked by `status`)

**Definition:** Is this well-formed artifact also semantically correct and high quality?

**Checks that DON'T block artifact generation but indicate problems:**

**Semantic Errors (should exit 1):**
- ✗ **Invalid edge types** - Outcome "implements" another Outcome → Violates JIG semantics
- ✗ **Subsystem cycles** - SubsystemA contains SubsystemB contains SubsystemA → Impossible hierarchy  
- ✗ **Self-loops** - `S-AUTH-001` depends on `S-AUTH-001` → Logical impossibility
- ✗ **Orphaned critical nodes** - Outcome with zero edges → Unreachable, meaningless

**Quality Warnings (should exit 0):**
- ⚠ **Orphaned nodes** - Specification with no edges → Should be connected
- ⚠ **Unassigned nodes** - Node missing `subsystem` field → Hard to organize
- ⚠ **Missing optional fields** - No `created` date → Incomplete metadata

**Result:** If `status` exits 0, the artifact is **semantically valid and high quality**.

**Rationale:** The artifact is buildable but may violate domain rules or best practices.

### Why This Separation Makes Sense

**Analogy: Compiling vs. Linting**

```
gcc program.c          → Compiler (like index rebuild)
  - Checks: Valid syntax, type errors, undefined references
  - Output: Binary executable (if valid)
  - Fails on: Parse errors, undefined symbols
  
lint program.c         → Linter (like status)
  - Checks: Code style, unreachable code, suspicious patterns
  - Output: Warnings and errors
  - Fails on: Semantic errors, quality issues
  - Assumes: Code already compiles
```

**JIG Workflow:**

```
jigy index rebuild     → Graph builder
  - Checks: Parseable files, valid IDs, complete nodes, resolvable references
  - Output: graph-index.json (if valid)
  - Fails on: Structural errors
  
jigy status            → Graph linter
  - Checks: Edge semantics, subsystem rules, quality metrics
  - Output: Health report + validation results
  - Fails on: Semantic errors
  - Assumes: graph-index.json already built
```

### Concrete Examples

#### Example 1: Structural error (blocks rebuild)

```yaml
# jig/outcomes/O-CLI-001.md
---
id: OCLI-001           # ✗ Invalid format (missing dash)
type: outcome
title: CLI works
---
```

```bash
$ jigy index rebuild
✗ Error: Invalid node ID format in jig/outcomes/O-CLI-001.md
  Expected: O-CLI-001
  Got: OCLI-001

✗ Rebuild failed
$ echo $?
1
```

**Rebuild MUST fail** - Can't build artifact with malformed IDs.

#### Example 2: Semantic error (rebuild succeeds, status fails)

```yaml
# jig/outcomes/O-CLI-001.md
---
id: O-CLI-001
type: outcome
title: CLI works
implements: O-CLI-002  # ✗ Outcome can't implement another outcome!
---
```

```bash
$ jigy index rebuild
✓ Scanned 215 nodes
✓ Built graph-index.json
$ echo $?
0

$ jigy status
✗ Invalid edge type: Outcome cannot implement Outcome
  Source: O-CLI-001
  Target: O-CLI-002
  Edge type: implements
  
❌ Graph has 1 semantic error
$ echo $?
1
```

**Rebuild succeeds** - The file is parseable, ID is valid, edge target exists.  
**Status fails** - But the relationship violates JIG semantics (outcomes don't implement outcomes).

#### Example 3: Quality warning (both succeed)

```yaml
# jig/specifications/S-AUTH-003.md
---
id: S-AUTH-003
type: specification
title: Password hashing
# No edges, no subsystem assignment
---
```

```bash
$ jigy index rebuild
✓ Scanned 215 nodes
⚠ Warning: 1 unassigned node (S-AUTH-003)
⚠ Warning: 1 orphaned node (S-AUTH-003)
✓ Built graph-index.json
$ echo $?
0

$ jigy status
⚠ Orphaned nodes (1): S-AUTH-003
⚠ Unassigned nodes (1): S-AUTH-003

💡 Suggestions:
  - Add relationships to S-AUTH-003
  - Assign S-AUTH-003 to a subsystem

✓ Graph is valid (0 errors, 2 warnings)
$ echo $?
0
```

**Both succeed** - The node is valid, just isolated and unorganized.

### Updated Command Responsibilities

#### `jigy index rebuild`

**Purpose:** Build artifact from sources

**Validates:**
- File parseability
- Node ID format and uniqueness
- Required field presence
- Edge target existence
- Node type validity

**On structural errors:**
- Print error details
- Do NOT write graph-index.json
- Exit 1

**On quality issues:**
- Print warnings
- STILL write graph-index.json (artifact is valid!)
- Exit 0

**Guarantees:** If exit 0, artifact is structurally valid.

#### `jigy status`

**Purpose:** Check artifact health

**Validates:**
- Edge type semantics (O→S, S→S, etc.)
- Subsystem hierarchy (no cycles)
- Graph topology (no self-loops)
- Quality metrics (orphans, assignments)

**On semantic errors:**
- Print error details
- Exit 1

**On quality warnings:**
- Print warnings
- Exit 0

**Guarantees:** If exit 0, artifact is semantically valid and high quality.

### Why Rebuild Can't Catch Everything

**Rebuild operates on sources in isolation:**
- Scans each file independently
- Doesn't understand relationship semantics
- Can validate "this edge exists" but not "this edge makes sense"

**Example:**
```yaml
# O-CLI-001.md
implements: S-CLI-001  # ✓ S-CLI-001 exists (rebuild happy)
                       # ✗ But outcome shouldn't implement spec (status catches)
```

**Status operates on the complete graph:**
- Sees all nodes and edges together
- Understands JIG domain rules
- Can validate semantic correctness

### Implementation Implications

**In `IndexBuilder.build()`:**

```python
def build(self):
    """Build graph-index from sources."""
    nodes = []
    structural_errors = []
    quality_warnings = []
    
    for source in self.discover_sources():
        try:
            node = self.parse_node(source)
            
            # Structural validation (MUST pass)
            if not self.validate_node_structure(node):
                structural_errors.append(...)
                continue  # Skip this node
            
            # Quality checks (MAY warn)
            if not node.subsystem:
                quality_warnings.append(f"Unassigned: {node.id}")
            
            nodes.append(node)
            
        except ParseError as e:
            structural_errors.append(...)
    
    if structural_errors:
        print_errors(structural_errors)
        return 1  # FAIL - don't write artifact
    
    # Artifact is structurally valid, build it
    self.write_artifact(nodes)
    
    if quality_warnings:
        print_warnings(quality_warnings)
    
    return 0  # SUCCESS - artifact written
```

**In `status_command()`:**

```python
def status_command():
    """Show status and validate semantics."""
    # Load artifact (assumes structurally valid)
    graph = Graph.load_from_dir()
    
    # Show metrics
    print_metrics(graph)
    
    # Semantic validation
    semantic_errors = []
    quality_warnings = []
    
    # Check edge semantics
    for edge in graph.edges:
        if not valid_edge_type(edge.from_node.type, edge.to_node.type, edge.type):
            semantic_errors.append(...)
    
    # Check subsystem cycles
    if has_subsystem_cycles(graph):
        semantic_errors.append(...)
    
    # Check quality
    orphans = find_orphans(graph)
    if orphans:
        quality_warnings.append(...)
    
    print_validation_results(semantic_errors, quality_warnings)
    
    if semantic_errors:
        return 1  # FAIL - semantic errors
    return 0  # SUCCESS - valid and high quality
```

### This Strengthens the Proposal

The separation of concerns is now crystal clear:

1. **Rebuild = Structural gatekeeper**
   - "Can I build this?"
   - Fast fail on broken sources
   
2. **Status = Semantic gatekeeper**  
   - "Should I commit this?"
   - Assumes structural validity, checks meaning

3. **No redundancy**
   - Each command validates different things
   - Both are necessary
   - Neither is sufficient alone

4. **Clear user mental model**
   - Rebuild → "Sources → Artifact"
   - Status → "Is artifact good?"

This actually makes the case for merging validate into status STRONGER, because validate's semantic checks naturally belong with status's health checks, not with rebuild's structural checks.

## Concerns & Mitigations

### Concern 1: "Status should always exit 0"

**Addressed by:**
- `--warn-only` flag for informational mode
- Default behavior exits 1 on errors (most useful)
- Users can choose behavior with flags

### Concern 2: "Validate is more thorough than status"

**Addressed by:**
- Merge ALL validation logic into status
- Status runs same comprehensive checks
- No loss of validation coverage

### Concern 3: "CI needs validation-only mode"

**Addressed by:**
- `jigy status --quiet` → Validation-only output
- Exit code behavior is the same
- CI pipelines unchanged (just rename command)

### Concern 4: "Loss of command composability"

**Not a real concern:**
- Status is still composable: `jigy status --quiet`
- More composable: fewer commands, more flags
- Standard Unix pattern: one command, multiple modes

### Concern 5: "Users might want quick status without validation"

**Addressed by:**
- Validation is fast (<1s for typical graphs)
- Graph already loaded for metrics, validation adds minimal overhead
- Performance is not a concern

### Concern 6: "Deviation from Git model"

**Git is different:**
- Git has mutation commands that change state
- JIG has ONE mutation command (rebuild)
- Git fsck is for deep corruption checking (not normal workflow)
- JIG validate is for normal workflow checking (not deep diagnostics)

**Better analogy:**
- `cargo check` → Fast validation + warnings (like our status)
- `cargo build` → Full build (like our rebuild)
- Cargo doesn't separate "show me status" and "validate"

## Testing Strategy

### Unit Tests

**Test: Validation integration**
```python
def test_status_includes_validation():
    """Status command runs comprehensive validation."""
    graph = create_invalid_graph()  # Missing node ID, invalid edge
    result = status_command(graph)
    
    assert result.exit_code == 1
    assert "Invalid node ID" in result.output
    assert "Edge target does not exist" in result.output
```

**Test: Exit code modes**
```python
def test_status_exit_codes():
    """Status exit codes match validation results."""
    # Errors present
    assert status_command(invalid_graph) == 1
    assert status_command(invalid_graph, warn_only=True) == 0
    
    # Only warnings
    assert status_command(warning_graph) == 0
    assert status_command(warning_graph, strict=True) == 1
    
    # Valid graph
    assert status_command(valid_graph) == 0
```

**Test: Output modes**
```python
def test_status_output_modes():
    """Status supports quiet and verbose modes."""
    result_quiet = status_command(graph, quiet=True)
    assert "Node Summary" not in result_quiet.output
    assert "Validation Results" in result_quiet.output
    
    result_verbose = status_command(graph, verbose=True)
    assert "Node Summary" in result_verbose.output
    assert "Validation Results" in result_verbose.output
```

### Integration Tests

**Test: CI workflow**
```bash
#!/bin/bash
# Test CI integration after merge

# Valid graph should pass
jigy status
assert_exit_code 0

# Invalid graph should fail
create_invalid_node
jigy index rebuild
jigy status
assert_exit_code 1

# Preview mode never fails
jigy status --warn-only
assert_exit_code 0
```

**Test: Backward compatibility**
```bash
# Deprecated validate command still works
jigy validate 2>&1 | grep "deprecated"
assert_exit_code $?  # Same exit code as status
```

### User Acceptance Testing

**Scenario 1: Developer workflow**
```
1. User edits markdown file
2. User runs: jigy index rebuild
3. User runs: jigy status
4. Status shows errors → User fixes → Repeat
5. Status shows no errors → User commits
```

**Scenario 2: CI pipeline**
```
1. CI checks out code
2. CI runs: jigy status
3. Status exits 1 → CI fails build → No merge
4. Status exits 0 → CI passes → Merge allowed
```

**Scenario 3: Quick check**
```
1. User wants quick validation
2. User runs: jigy status --quiet
3. See only validation results (no metrics)
4. Fast feedback (<1s)
```

## Documentation Updates

### User Guide: Command Reference

**Update:** `docs/user-guide/commands.md`

```markdown
## jigy status

Show graph health metrics and validate consistency.

### Usage

jigy status [OPTIONS]

### Options

- `--verbose`: Show detailed node listings
- `--flat`: Show flat subsystem list (no tree)
- `--warn-only`: Always exit 0 (show warnings but don't fail)
- `--strict`: Exit 1 on errors OR warnings
- `--quiet`: Only show validation results (suppress metrics)

### Exit Codes

- `0`: Graph is valid (or `--warn-only` mode)
- `1`: Graph has errors (or warnings in `--strict` mode)

### Examples

#### Default: Full status + validation

jigy status

Shows metrics, subsystems, validation results. Exits 1 if errors found.

#### Quiet mode: Validation only

jigy status --quiet

Shows only validation results. Useful for CI or quick checks.

#### Preview mode: Never fail

jigy status --warn-only

Shows all issues but always exits 0. Useful for previewing issues without blocking CI.

#### Strict mode: Fail on warnings

jigy status --strict

Exits 1 if errors OR warnings found. Useful for enforcing high quality.

### Migration from jigy validate

The `jigy validate` command has been merged into `jigy status`.

**Before:**
jigy validate

**After:**
jigy status --quiet

The functionality is identical. `jigy status` runs the same comprehensive validation checks.
```

### Tutorial: Basic Workflow

**Update:** `docs/tutorials/basic-workflow.md`

```markdown
## Basic JIG Workflow

### 1. Edit sources

Edit markdown files in `jig/` or add `@jig` annotations to code.

### 2. Rebuild index

jigy index rebuild

This synchronizes `jig/graph-index.json` with your sources.

### 3. Check status

jigy status

This shows graph health metrics and validates consistency.

- **Exit 0:** Graph is valid, ready to commit
- **Exit 1:** Graph has errors, fix before committing

### 4. Commit

If status passes, commit your changes:

git add .
git commit -m "Add new specification"
git push
```

### CI Integration Guide

**Update:** `docs/tutorials/ci-integration.md`

```markdown
## Continuous Integration

### GitHub Actions

.github/workflows/jig.yml:

name: JIG Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install JIG
        run: pip install -e .
      
      - name: Validate JIG graph
        run: jigy status

That's it! `jigy status` will exit 1 if the graph has errors, failing the CI build.

### Advanced: Show warnings without failing

If you want to see warnings without blocking CI:

- name: Preview JIG issues
  run: jigy status --warn-only

### Advanced: Fail on warnings

If you want to enforce zero warnings:

- name: Strict JIG validation
  run: jigy status --strict
```

## Implementation Plan

### Work Unit 1: Core Integration (4-6 hours)

**File changes:**
- Create `src/jig/core/validation.py` (extract from validate.py)
- Update `src/jig/cli/status.py` (add validation)
- Add tests: `tests/unit/test_validation_core.py`
- Add tests: `tests/integration/test_status_validation.py`

**Deliverable:** `jigy status` runs validation and exits with appropriate code

### Work Unit 2: CLI Flags (2-3 hours)

**File changes:**
- Update `src/jig/cli/status.py` (add flags)
- Update `src/jig/cli/main.py` (update help text)
- Add tests: `tests/unit/test_status_flags.py`

**Deliverable:** All status flags work correctly

### Work Unit 3: Deprecate validate (1-2 hours)

**File changes:**
- Update `src/jig/cli/main.py` (add deprecation warning)
- Update `src/jig/cli/validate.py` (add redirect to status)

**Deliverable:** `jigy validate` shows deprecation message and runs status

### Work Unit 4: Documentation (2-3 hours)

**File changes:**
- Update `README.md`
- Update `docs/user-guide/commands.md`
- Update `docs/tutorials/basic-workflow.md`
- Update `docs/tutorials/ci-integration.md`
- Add migration guide: `docs/user-guide/MIGRATION_validate_to_status.md`

**Deliverable:** All docs reflect new command structure

### Work Unit 5: Integration Tests (2-3 hours)

**File changes:**
- Add `tests/integration/test_workflow_end_to_end.py`
- Add `tests/integration/test_ci_simulation.py`

**Deliverable:** Full workflow tests pass

### Work Unit 6: Remove validate command (1 hour)

**File changes:**
- Delete `src/jig/cli/validate.py`
- Remove validate subcommand from `main.py`
- Remove validate tests

**Deliverable:** Clean removal after deprecation period

**Total effort:** 12-18 hours (1.5-2 days)

**Timeline:** 1-2 weeks (including review and testing)

## Success Metrics

### User Experience

- ✅ New users complete workflow with 2 commands (rebuild + status)
- ✅ CI integration requires 1 command (status)
- ✅ No confusion about which command to run

### Technical

- ✅ Status includes all validation logic from validate
- ✅ Exit codes work correctly for CI gating
- ✅ Performance: status + validation < 1s for typical graphs
- ✅ Backward compatibility: validate command works with deprecation warning

### Documentation

- ✅ All examples updated to use new command structure
- ✅ Migration guide published
- ✅ CI integration guide updated

## Risks & Mitigation

### Risk 1: User confusion during migration

**Mitigation:**
- Keep validate as deprecated alias for 3 months
- Clear deprecation message with migration instructions
- Update all documentation immediately

### Risk 2: CI pipelines break

**Mitigation:**
- Validate command still works (just deprecated)
- Clear migration path: `jigy validate` → `jigy status --quiet`
- Document in release notes

### Risk 3: Performance regression

**Mitigation:**
- Validation adds <100ms overhead
- Graph already loaded for metrics
- Measure performance before/after

### Risk 4: Feature parity

**Mitigation:**
- Comprehensive test coverage
- All validation logic ported to status
- No functionality removed, only consolidated

## Alternatives Considered

### Alternative 1: Keep three commands

**Rejected because:**
- Adds cognitive overhead for users
- Redundant functionality (status and validate overlap significantly)
- Doesn't prepare for auto-rebuild future
- Creates confusion about workflow

### Alternative 2: Make validate deeper than status

**Rejected because:**
- No clear "deeper" checks to add
- Both commands need same validation logic
- Creates false distinction

### Alternative 3: Add --validate flag to status

**Rejected because:**
- Validation should be default, not opt-in
- Adds flag complexity without benefit
- Status without validation is incomplete

### Alternative 4: Remove status, keep only validate

**Rejected because:**
- Status metrics are valuable (subsystems, node counts)
- "Status" is more intuitive name than "validate"
- Status implies read-only (correct), validate implies checking (subset)

## Future Evolution

### Phase 1: Merge (this proposal)
```
jigy index rebuild    → Explicit sync
jigy status           → Metrics + validation
```

### Phase 2: Auto-rebuild (2-4 weeks later)
```
jigy status           → Auto-rebuild + metrics + validation
jigy index rebuild    → Manual sync (advanced use)
```

### Phase 3: Watch mode (3-6 months later)
```
jigy status --watch   → Continuous rebuild + validation on file changes
```

### Phase 4: Language Server Protocol (6-12 months later)
```
VSCode extension      → Real-time validation in editor
                      → No CLI needed for most users
```

## Conclusion

Merging `jigy validate` into `jigy status` simplifies the user experience, prepares for automatic rebuilds, and aligns with industry standards (cargo check). The concerns raised in S023 are addressed through flags (`--warn-only`, `--strict`, `--quiet`) that provide the flexibility users need without requiring separate commands.

**Recommendation:** Proceed with implementation.

---

**Document Status:** Draft  
**Approval Required:** Yes (architectural change)  
**Next Steps:** Review, discuss concerns, implement if approved  
**Related Documents:**
- docs/wip/S023_EVALUATION_command_overlap_analysis.md
- docs/wip/S022_PLAN_validate_consistency.md
- docs/wip/S021_SCOPE_validate_consistency.md

