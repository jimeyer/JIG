---
title: "Brick Context Enforcement Proposal"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1763934216
created_human: "2025-11-23 15:43 CST"
parent: "[[AG001_Alignment-Graph-Bricks]]"
children: ['[[AG006_Enforcement-Quick-Reference]]']
---
# Brick Context Enforcement Proposal

**How to Constrain Claude Code to Work Only Inside a Brick**

---

## Overview

**Goal:** When an agent (Claude Code, Copilot, etc.) works on a task, it should only see and modify code within a single Brick's boundaries.

**Why:**
- Prevents accidental coupling across Brick boundaries
- Reduces context window noise (agent sees less irrelevant code)
- Enforces architectural integrity automatically
- Makes agent behavior more predictable and focused
- Enables true "clean room" implementation

**Challenge:** Claude Code has tools (Read, Edit, Glob, Grep) that can access any file in the project. How do we restrict access to only one Brick's context?

---

## The Brick Context Contract

From the Alignment Graph concept:

> **Inside a Brick, an agent can see:**
> - Brick definition file
> - Brick-level Intent nodes (O/S/C)
> - Brick-level code nodes
> - Brick-level test nodes
> - Public interfaces of adjacent Bricks
> - Brick dependency graph slice

> **Inside a Brick, an agent CANNOT see:**
> - Code from other Bricks
> - Tests from other Bricks
> - Internal details of other Bricks
> - Global call graphs
> - Repo-level filesystem structure

---

## Proposed Solution: Multi-Layer Enforcement

We need **multiple layers** because no single mechanism is foolproof:

```
┌─────────────────────────────────────────────────┐
│  Layer 1: Brick Definition Files (.brick.yaml) │
│           (Declare boundaries)                   │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  Layer 2: Brick Context Loader                  │
│           (Pre-load allowed context)             │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  Layer 3: Tool Wrappers                         │
│           (Filter file access at runtime)        │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  Layer 4: Validation & Audit                    │
│           (Check compliance after work)          │
└─────────────────────────────────────────────────┘
```

Let's detail each layer.

---

## Layer 1: Brick Definition Files

### Format: `.brick.yaml`

Each Brick has a definition file declaring its boundaries:

```yaml
# bricks/graph-core.brick.yaml
brick:
  id: BRICK-GRAPH
  name: "Graph Core"
  version: "1.0.0"
  layer: domain-core

responsibility: |
  Graph data structures and query operations.
  Manages Graph, Node, Edge, Subsystem domain models.

# === CONTEXT BOUNDARY DEFINITION ===

context:
  # Files that belong to this Brick
  source_files:
    - src/jig/core/graph.py
    - src/jig/core/relationships.py

  test_files:
    - tests/unit/test_graph.py
    - tests/unit/test_graph_queries.py
    - tests/unit/test_graph_traversal.py
    - tests/unit/test_relationship_parsing.py

  intent_nodes:
    - O-GRAPH-001
    - O-GRAPH-002
    - S-GRAPH-001
    - S-GRAPH-002
    - S-GRAPH-003

  # Artifacts this Brick produces/consumes
  artifacts:
    consumed:
      - name: graph-index.json
        path: jig/graph-index.json
        access: read
        owner: BRICK-INDEX
        schema: schemas/graph-index.schema.json

# === DEPENDENCIES (What this Brick can see) ===

dependencies:
  bricks:
    BRICK-PARSER:
      access: public_interface_only
      imports:
        - OSTCNode
        - parse_ostc_node
      # Agent can see type signatures, not implementation

    BRICK-UTILS:
      access: public_interface_only
      imports:
        - read_file
        - write_file
        - load_yaml

  external:
    - networkx
    - json

# === PUBLIC INTERFACE (What other Bricks can see) ===

interface:
  public:
    classes:
      - Graph
      - Edge
      - Subsystem

    functions:
      - load_from_dir
      - get_dependencies
      - get_dependents
      - find_path
      - get_nodes_by_subsystem

  stability: stable
  versioning: semver

# === FORBIDDEN (Explicit denials) ===

forbidden:
  # These patterns are explicitly off-limits
  - src/jig/cli/*
  - src/jig/decompose/*
  - src/jig/core/scanner.py
  - src/jig/core/annotation_validator.py
  - tests/integration/*

  # No global searches
  - glob: "**/*.py"  # Too broad
  - grep: ".*"       # Too broad
```

**Key Sections:**

1. **`context.source_files`** - Code this Brick owns
2. **`context.test_files`** - Tests this Brick owns
3. **`context.intent_nodes`** - Intent (O/S/C) this Brick implements
4. **`dependencies.bricks`** - Other Bricks this Brick uses
5. **`interface.public`** - What this Brick exposes
6. **`forbidden`** - Explicit deny list

---

## Layer 2: Brick Context Loader

### Tool: `jigy brick load <brick-id>`

This command prepares a **constrained context** for agent work.

**What it does:**

```bash
$ jigy brick load BRICK-GRAPH --output context.md

# Creates a context file with:
# 1. Brick definition
# 2. Full source code for this Brick
# 3. Full tests for this Brick
# 4. Intent nodes for this Brick
# 5. PUBLIC INTERFACES ONLY of dependency Bricks
# 6. Artifacts this Brick consumes (schemas)
```

**Output: `context.md`**

```markdown
# Brick Context: Graph Core (BRICK-GRAPH)

## Brick Definition

**ID:** BRICK-GRAPH
**Name:** Graph Core
**Responsibility:** Graph data structures and query operations

---

## Intent

### O-GRAPH-001: Fast Graph Queries
[full content of outcome node]

### S-GRAPH-001: NetworkX Integration
[full content of specification node]

---

## Source Code

### src/jig/core/graph.py
```python
[FULL CONTENT - 573 lines]
```

### src/jig/core/relationships.py
```python
[FULL CONTENT - 123 lines]
```

---

## Tests

### tests/unit/test_graph.py
```python
[FULL CONTENT]
```

[... more tests ...]

---

## Dependencies (Public Interfaces Only)

### BRICK-PARSER: Intent Parser

**Provides:**
- `OSTCNode` (class)
- `parse_ostc_node(path: Path) -> OSTCNode`

**Type Signatures:**
```python
@dataclass
class OSTCNode:
    id: str
    type: NodeType
    title: str
    subsystem: str | None
    body: str
    # ... (no implementation details)

def parse_ostc_node(path: Path) -> OSTCNode:
    """Parse OSTC node from markdown file with YAML frontmatter.

    Args:
        path: Path to .md file

    Returns:
        Parsed OSTCNode

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If YAML or structure invalid
    """
    ...  # Implementation hidden
```

### BRICK-UTILS: Foundation Utilities

**Provides:**
```python
def read_file(path: Path) -> str: ...
def write_file(path: Path, content: str) -> None: ...
def load_yaml(path: Path) -> dict[str, Any]: ...
```

---

## Artifacts

### graph-index.json (consumed, read-only)

**Owner:** BRICK-INDEX
**Schema:** schemas/graph-index.schema.json
**Access:** Read-only

```json
{
  "version": "1.0.0",
  "nodes": {
    "node-id": {
      "type": "outcome | specification | constraint",
      "title": "string",
      "subsystem": "string"
    }
  },
  "edges": [...],
  "subsystems": {...}
}
```

---

## Forbidden

You MUST NOT access:
- Files outside this Brick's source/test files
- Internal implementation of other Bricks
- CLI code (src/jig/cli/*)
- Decompose code (src/jig/decompose/*)
- Global searches (Glob "**/*.py", Grep across all files)

---

## Working Instructions

1. Only read/edit files listed in "Source Code" and "Tests"
2. Use dependency interfaces via their public APIs
3. Do not peek at other Bricks' implementations
4. If you need something from another Brick, use its public interface
5. If a needed interface doesn't exist, note it for architect review
6. Run tests in this Brick after changes
7. Validate compliance before completing: `jigy brick validate`
```

**Usage in Claude Code:**

```bash
# Human starts Claude Code session
$ claude

# Load Brick context
You: @context.md (or paste the content)
You: I need to add a new graph traversal function. Stay within the BRICK-GRAPH boundaries.

Claude: I'll work within the Graph Core Brick. Let me read the current graph.py file...
[Claude uses Read tool, but only on files listed in context]
```

---

## Layer 3: Tool Wrappers (Runtime Enforcement)

### Option A: Modified Claude Code Tools

If Claude Code supported Brick mode, it could wrap tools:

```python
# In Claude Code internals (conceptual)

class BrickEnforcedFileSystem:
    def __init__(self, brick_def: BrickDefinition):
        self.brick_def = brick_def
        self.allowed_paths = set(brick_def.context.source_files +
                                 brick_def.context.test_files)
        self.forbidden_patterns = brick_def.forbidden

    def read_file(self, path: Path) -> str:
        if not self._is_allowed(path):
            raise BrickBoundaryViolation(
                f"Cannot read {path}: outside BRICK-{self.brick_def.id} boundary"
            )
        return _actual_read_file(path)

    def edit_file(self, path: Path, old: str, new: str) -> None:
        if not self._is_allowed(path):
            raise BrickBoundaryViolation(
                f"Cannot edit {path}: outside BRICK-{self.brick_def.id} boundary"
            )
        return _actual_edit_file(path, old, new)

    def glob(self, pattern: str) -> list[Path]:
        # Only return files within Brick
        all_matches = _actual_glob(pattern)
        return [p for p in all_matches if self._is_allowed(p)]

    def grep(self, pattern: str, path: Path = None) -> list[Match]:
        # Restrict to Brick files
        if path and not self._is_allowed(path):
            raise BrickBoundaryViolation(...)

        # If no path, search only Brick files
        if not path:
            results = []
            for allowed_path in self.allowed_paths:
                results.extend(_actual_grep(pattern, allowed_path))
            return results

        return _actual_grep(pattern, path)

    def _is_allowed(self, path: Path) -> bool:
        # Check against allowed list
        if path not in self.allowed_paths:
            return False

        # Check against forbidden patterns
        for pattern in self.forbidden_patterns:
            if fnmatch(path, pattern):
                return False

        return True
```

**Claude Code would launch with:**

```bash
$ claude --brick BRICK-GRAPH
# All file operations restricted to Brick boundaries
```

### Option B: Wrapper Script (Practical Today)

Since we can't modify Claude Code, we can use **social enforcement** + **validation**:

```bash
# brick-work.sh - Wrapper script
#!/bin/bash

BRICK_ID=$1
shift

# Load Brick context into a file
jigy brick load "$BRICK_ID" --output /tmp/brick-context.md

echo "======================================"
echo "Brick Mode: $BRICK_ID"
echo "======================================"
echo ""
echo "Context loaded to: /tmp/brick-context.md"
echo ""
echo "IMPORTANT: You are constrained to this Brick's boundaries."
echo "  - Only read/edit files listed in the context"
echo "  - Use dependency interfaces, not implementations"
echo "  - Run 'jigy brick validate $BRICK_ID' when done"
echo ""
echo "Starting Claude Code..."
echo "======================================"
echo ""

# Start Claude with pre-loaded context
claude --context /tmp/brick-context.md "$@"

# After session ends, validate
echo ""
echo "======================================"
echo "Validating Brick boundaries..."
jigy brick validate "$BRICK_ID"
```

**Usage:**

```bash
$ ./brick-work.sh BRICK-GRAPH "Add shortest path caching"
```

---

## Layer 4: Validation & Audit

### Tool: `jigy brick validate <brick-id>`

After an agent finishes work, validate that it stayed within boundaries.

**Checks:**

```python
# brick_validator.py

class BrickValidator:
    def validate(self, brick_id: str, git_ref: str = "HEAD") -> ValidationResult:
        """Validate that recent changes respect Brick boundaries."""

        brick_def = load_brick_definition(brick_id)

        checks = [
            self._check_modified_files(brick_def, git_ref),
            self._check_imports(brick_def),
            self._check_coupling(brick_def),
            self._check_interface_usage(brick_def),
        ]

        return ValidationResult(checks)

    def _check_modified_files(self, brick_def, git_ref):
        """Ensure only Brick's files were modified."""
        modified = git_diff_files(git_ref)
        allowed = set(brick_def.context.source_files +
                      brick_def.context.test_files)

        violations = [f for f in modified if f not in allowed]

        if violations:
            return CheckResult(
                name="File Boundary",
                passed=False,
                message=f"Modified files outside Brick: {violations}"
            )

        return CheckResult(name="File Boundary", passed=True)

    def _check_imports(self, brick_def):
        """Ensure imports only use declared dependencies."""
        for source_file in brick_def.context.source_files:
            imports = extract_imports(source_file)

            for imp in imports:
                if imp.startswith("jig."):
                    # Check if this import is allowed
                    module = imp.split('.')[1]  # cli, core, utils, etc.

                    allowed_modules = {
                        dep.brick_id for dep in brick_def.dependencies.bricks
                    }

                    if module not in allowed_modules:
                        return CheckResult(
                            name="Import Validation",
                            passed=False,
                            message=f"{source_file} imports {imp}, but {module} not in dependencies"
                        )

        return CheckResult(name="Import Validation", passed=True)

    def _check_coupling(self, brick_def):
        """Check coupling ratio hasn't degraded."""
        # Count internal vs external calls
        # Use AST or static analysis

        internal_calls = count_internal_function_calls(brick_def)
        external_calls = count_external_function_calls(brick_def)

        coupling_ratio = internal_calls / max(external_calls, 1)

        if coupling_ratio < brick_def.health.min_coupling_ratio:
            return CheckResult(
                name="Coupling Ratio",
                passed=False,
                message=f"Coupling ratio {coupling_ratio:.1f}:1 below threshold"
            )

        return CheckResult(name="Coupling Ratio", passed=True)

    def _check_interface_usage(self, brick_def):
        """Ensure only public interfaces of dependencies are used."""

        for source_file in brick_def.context.source_files:
            tree = ast.parse(read_file(source_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check if call is to dependency Brick
                    func_name = get_function_name(node)

                    for dep in brick_def.dependencies.bricks:
                        if func_name.startswith(dep.module_name):
                            # Check if function is in public interface
                            if func_name not in dep.interface.public_functions:
                                return CheckResult(
                                    name="Interface Usage",
                                    passed=False,
                                    message=f"Using private function {func_name} from {dep.brick_id}"
                                )

        return CheckResult(name="Interface Usage", passed=True)
```

**Output:**

```bash
$ jigy brick validate BRICK-GRAPH

Validating Brick: Graph Core (BRICK-GRAPH)
=========================================

✓ File Boundary: All changes within Brick scope
✓ Import Validation: Only declared dependencies imported
✓ Coupling Ratio: 14:1 (above threshold of 10:1)
✓ Interface Usage: Only public interfaces used

All checks passed! ✓

Changes:
  Modified: src/jig/core/graph.py (+45 lines)
  Modified: tests/unit/test_graph.py (+20 lines)

Brick health: Excellent
```

---

## Advanced: Brick Mode in Claude Code

### Ideal Implementation (Feature Request)

If Claude Code natively supported Bricks:

```bash
$ claude brick --id BRICK-GRAPH --task "Add graph caching"

Entering Brick Mode: Graph Core (BRICK-GRAPH)
============================================

Context loaded:
  - 2 source files (696 LOC)
  - 4 test files (320 tests)
  - 3 intent nodes
  - 2 dependency interfaces (Parser, Utils)

Restrictions active:
  ✓ File access limited to Brick scope
  ✓ Imports validated against dependencies
  ✓ Public interfaces only for dependencies
  ✓ Validation will run on completion

How can I help with this Brick?
```

**Features:**

1. **Automatic context loading** - No manual file reading
2. **Tool restrictions** - Read/Edit/Glob/Grep filtered
3. **Dependency resolution** - Interface stubs auto-loaded
4. **Validation on save** - Automatic boundary checks
5. **Clear feedback** - Agent knows its constraints

---

## Enforcement Strategies Comparison

| Strategy | Enforcement Strength | Ease of Implementation | User Experience |
|----------|---------------------|------------------------|-----------------|
| **Prompt-only** | ⚠️ Weak (relies on agent compliance) | ✅ Very Easy | ⚠️ Agent may violate accidentally |
| **Pre-loaded context** | ⚠️ Medium (social contract) | ✅ Easy | ✅ Good (clear boundaries) |
| **Tool wrappers** | ✅ Strong (technical enforcement) | ❌ Hard (requires Claude Code mods) | ✅ Excellent (automatic) |
| **Post-validation** | ⚠️ Medium (detects but doesn't prevent) | ✅ Easy | ⚠️ Violations found after work |
| **Combined approach** | ✅ Very Strong (multiple layers) | ⚠️ Medium (requires tooling) | ✅ Very Good |

**Recommendation:** Use **combined approach** today:
- Layer 1: Brick definitions (easy)
- Layer 2: Pre-loaded context (easy)
- Layer 4: Post-validation (medium)

Wait for Claude Code to support Layer 3 (tool wrappers).

---

## Practical Workflow Today

### Step 1: Define Bricks

```bash
# Create Brick definitions
$ mkdir bricks/
$ cat > bricks/graph-core.brick.yaml << EOF
brick:
  id: BRICK-GRAPH
  name: "Graph Core"
  ...
EOF
```

### Step 2: Generate Context

```bash
# Implement jigy brick load command
$ jigy brick load BRICK-GRAPH --output brick-context.md
```

### Step 3: Start Agent Session

```bash
# Start Claude Code with context
$ claude

You: @brick-context.md

You: I need to add a caching layer to the graph traversal.
You must stay within the BRICK-GRAPH boundaries defined in the context file.

Claude: I'll work within Graph Core Brick boundaries. Let me read the current graph.py implementation...
```

### Step 4: Agent Works

Claude Code:
- ✅ Reads `src/jig/core/graph.py` (allowed)
- ✅ Reads `tests/unit/test_graph.py` (allowed)
- ✅ Uses `OSTCNode` from Parser interface (allowed)
- ❌ Tries to read `src/jig/cli/graph.py` → User reminds: "That's outside the Brick"
- ✅ Edits only Graph Core files

### Step 5: Validate

```bash
$ jigy brick validate BRICK-GRAPH

✓ All checks passed
Brick health: Excellent
```

### Step 6: Commit

```bash
$ git add src/jig/core/graph.py tests/unit/test_graph.py
$ git commit -m "feat(graph): add caching to graph traversal

Implemented within BRICK-GRAPH boundaries.
Validated with: jigy brick validate BRICK-GRAPH ✓"
```

---

## Implementation Phases

### Phase 1: Manual Enforcement (Immediate)
**Effort:** Low
**Value:** Medium

- ✅ Create Brick definition schema
- ✅ Write `.brick.yaml` files for all Bricks
- ✅ Create Brick context loader (`jigy brick load`)
- ✅ Use pre-loaded context files
- ✅ Manual compliance (agent prompted to follow)

**Deliverable:** Brick definitions + context loader

---

### Phase 2: Automated Validation (Short-term)
**Effort:** Medium
**Value:** High

- ✅ Implement `jigy brick validate` command
- ✅ Check file boundaries
- ✅ Check import restrictions
- ✅ Check coupling ratios
- ✅ Check interface usage
- ✅ Add to CI pipeline

**Deliverable:** Validation tool + CI integration

---

### Phase 3: Runtime Enforcement (Long-term)
**Effort:** High (requires Claude Code support)
**Value:** Very High

- ✅ Request Brick mode feature from Anthropic
- ✅ Tool wrappers for Read/Edit/Glob/Grep
- ✅ Automatic context scoping
- ✅ Real-time boundary violation prevention
- ✅ Seamless UX

**Deliverable:** Native Brick mode in Claude Code

---

## Benefits of Enforcement

### For Humans

1. **Architectural Integrity** - Boundaries can't erode silently
2. **Predictable Changes** - Know exactly what an agent might touch
3. **Easier Reviews** - Changes scoped to one Brick
4. **Clearer Responsibilities** - Each Brick has clear ownership

### For Agents

1. **Smaller Context** - See only relevant code (~500 LOC vs ~5000 LOC)
2. **Clearer Constraints** - Explicit boundaries, less ambiguity
3. **Better Quality** - Focused work produces better results
4. **Faster Execution** - Less to read and reason about

### For the System

1. **Reduced Coupling** - Can't accidentally add cross-Brick dependencies
2. **Stable Interfaces** - Public APIs become clear and enforced
3. **Measurable Health** - Brick metrics track quality over time
4. **Safe Refactoring** - Changes can't leak outside Brick

---

## Escape Hatches

Sometimes you need to violate boundaries:

### 1. Architect Mode

Work across Bricks to redesign:

```bash
$ claude --mode architect
# Can see all Bricks, but only interfaces (no implementations)
# Used for architectural decisions
```

### 2. Cross-Brick Refactoring

```bash
$ jigy brick validate --allow-cross-brick BRICK-GRAPH,BRICK-PARSER
# Temporary permission for refactoring that touches multiple Bricks
# Requires justification and review
```

### 3. Emergency Fixes

```bash
$ jigy brick validate --override
# Skip validation (use sparingly!)
# Must document why in commit message
```

---

## Open Questions

1. **How granular?** Should sub-Brick contexts exist (e.g., single file)?
2. **Testing?** Should test Bricks have different rules?
3. **Shared utilities?** How to handle truly shared code (e.g., utils)?
4. **Evolution?** How to handle Brick splitting/merging?
5. **Performance?** Does validation slow down workflow too much?

---

## Recommendations

### Immediate Actions

1. ✅ Create Brick definition schema (`brick.schema.yaml`)
2. ✅ Write `.brick.yaml` for all 10 JIG Bricks
3. ✅ Implement `jigy brick load` command
4. ✅ Implement `jigy brick validate` command
5. ✅ Document Brick Mode workflow

### Short-term Goals

1. Use Brick Mode for next feature development
2. Measure effectiveness (violations, agent quality)
3. Refine boundaries based on experience
4. Add Brick metrics to `jigy status`
5. Integrate validation into CI

### Long-term Vision

1. Request native Brick support from Anthropic
2. Build tool ecosystem around Bricks
3. Use Alignment Graph to track Brick health
4. Extend to other agent systems (Cursor, Copilot)
5. Publish Brick pattern as open standard

---

## Conclusion

**Brick boundaries can be enforced today** using:

1. **Brick definition files** - Declare boundaries explicitly
2. **Context loaders** - Pre-load only allowed context
3. **Validation tools** - Check compliance after work
4. **Social contracts** - Clear instructions to agents

**Future enforcement** would add:
- Runtime tool restrictions (requires Claude Code support)
- Automatic context scoping
- Real-time violation prevention

**The key insight:** Enforcement is not about restricting the agent—it's about **clarifying constraints** to produce better, more focused work.

Bricks make architectural boundaries **explicit, measurable, and enforceable**.

---

## Appendix A: Brick Definition Schema

```yaml
# brick.schema.yaml
type: object
required: [brick, context, interface]
properties:
  brick:
    type: object
    required: [id, name, version, layer]
    properties:
      id: {type: string, pattern: "^BRICK-[A-Z]+$"}
      name: {type: string}
      version: {type: string, pattern: "^\\d+\\.\\d+\\.\\d+$"}
      layer: {enum: [foundation, domain-core, analysis, interface]}

  responsibility: {type: string}

  context:
    type: object
    required: [source_files, test_files]
    properties:
      source_files: {type: array, items: {type: string}}
      test_files: {type: array, items: {type: string}}
      intent_nodes: {type: array, items: {type: string}}
      artifacts:
        type: object
        properties:
          produced: {type: array}
          consumed: {type: array}

  dependencies:
    type: object
    properties:
      bricks: {type: object}
      external: {type: array, items: {type: string}}

  interface:
    type: object
    required: [public, stability]
    properties:
      public:
        type: object
        properties:
          classes: {type: array}
          functions: {type: array}
      stability: {enum: [experimental, stable, deprecated]}
      versioning: {enum: [semver, calver]}

  forbidden:
    type: array
    items: {type: string}

  health:
    type: object
    properties:
      min_coupling_ratio: {type: number, minimum: 1}
      target_test_coverage: {type: number, minimum: 0, maximum: 100}
```

---

## Appendix B: Example Validation Output

```bash
$ jigy brick validate BRICK-GRAPH --verbose

Brick Validation Report
=======================
Brick: Graph Core (BRICK-GRAPH)
Date: 2025-11-22 21:45:00
Git ref: HEAD (abc123f)

File Boundary Check
-------------------
✓ Modified files within Brick scope
  - src/jig/core/graph.py (modified)
  - tests/unit/test_graph.py (modified)

Import Validation
-----------------
✓ All imports use declared dependencies

Checking src/jig/core/graph.py:
  - from jig.core.parser import OSTCNode ✓ (BRICK-PARSER declared)
  - from jig.utils.yaml_utils import load_yaml ✓ (BRICK-UTILS declared)
  - import networkx ✓ (external dependency declared)

Coupling Analysis
-----------------
✓ Coupling ratio: 14.2:1 (above threshold of 10:1)

  Internal calls: 142
  External calls: 10

  External calls breakdown:
    - BRICK-PARSER: 5 calls (parse_ostc_node)
    - BRICK-UTILS: 5 calls (load_yaml, read_file)

Interface Usage
---------------
✓ Only public interfaces used

  BRICK-PARSER interfaces used:
    - OSTCNode (class) ✓ public
    - parse_ostc_node (function) ✓ public

  BRICK-UTILS interfaces used:
    - load_yaml (function) ✓ public
    - read_file (function) ✓ public

Test Coverage
-------------
⚠ Coverage: 78.5% (target: 80%)

  Missing coverage:
    - src/jig/core/graph.py:234-245 (error handling)
    - src/jig/core/graph.py:401-408 (edge case)

Brick Health Score
------------------
Overall: Good (87/100)

  - Boundary compliance: 100/100 ✓
  - Coupling ratio: 95/100 ✓
  - Interface usage: 100/100 ✓
  - Test coverage: 78/100 ⚠

Recommendations
---------------
1. Add tests for error handling (lines 234-245)
2. Add tests for edge case (lines 401-408)
3. Consider extracting complex graph algorithms to separate module

Summary
-------
✓ Brick boundaries respected
⚠ Improve test coverage to meet 80% target
✓ Ready for commit
```

---

**Next Steps:**
1. Review this proposal
2. Implement Phase 1 (Brick definitions + context loader)
3. Test with real development tasks
4. Iterate based on experience
5. Request native support from Anthropic
