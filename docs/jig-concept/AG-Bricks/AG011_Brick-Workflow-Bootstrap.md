# Brick Workflow Bootstrap

**Practical Step-by-Step Workflow for Working Within Brick Boundaries**

**Status:** Ready to use today (no special tooling required)

---

## Overview

This document provides a **practical, immediately usable workflow** for working within Brick boundaries using existing tools. No new `jigy` commands required—this can be done today with manual processes and existing CLI tools.

**Goal:** Ensure all development work stays within a single Brick's boundaries, maintaining architectural integrity and reducing accidental coupling.

---

## Prerequisites

- Brick definition files exist in `jig/bricks/*.brick.yaml` (✓ Already done)
- Basic familiarity with git, grep, and file navigation
- Claude Code or similar agent tool (optional but recommended)

---

## The Brick Workflow (5 Steps)

### Step 1: Select Your Brick

Before starting any work, identify which Brick you'll be working in.

```bash
# List all available Bricks
ls jig/bricks/*.brick.yaml

# View a specific Brick definition
cat jig/bricks/graph-core.brick.yaml
```

**Example Bricks:**
- `BRICK-GRAPH` - Graph Core (graph data structures)
- `BRICK-PARSER` - Intent Parser (OSTC node parsing)
- `BRICK-SCANNER` - Annotation Scanner (code scanning)
- `BRICK-VALIDATOR-ANNOT` - Annotation Validator
- `BRICK-VALIDATOR-INTENT` - Intent Validator
- `BRICK-INDEX` - Index Builder
- `BRICK-DECOMPOSE` - Decomposition Analysis
- `BRICK-CLI` - CLI Commands
- `BRICK-CONFIG` - Configuration
- `BRICK-UTILS` - Foundation Utilities

**Decision criteria:**
- What code are you modifying?
- What feature/bug are you working on?
- Which Brick's responsibility matches your task?

---

### Step 2: Load Brick Context (Manual)

Read the Brick definition to understand its boundaries.

```bash
# Example: Working in Graph Core Brick
export BRICK_ID="BRICK-GRAPH"
export BRICK_FILE="jig/bricks/graph-core.brick.yaml"

# View the Brick definition
cat $BRICK_FILE
```

**Extract key information:**

1. **Source files** (what you CAN modify):
   ```bash
   # From graph-core.brick.yaml:
   # code.paths:
   #   - src/jig/core/graph.py
   #   - src/jig/core/relationships.py
   ```

2. **Test files** (what you CAN modify):
   ```bash
   # tests.paths:
   #   - tests/unit/test_graph.py
   #   - tests/unit/test_graph_queries.py
   #   - tests/unit/test_graph_traversal.py
   #   - tests/unit/test_relationship_parsing.py
   ```

3. **Dependencies** (what you CAN use):
   ```bash
   # dependencies.bricks:
   #   - BRICK-PARSER (public interface only)
   #   - BRICK-UTILS (public interface only)
   # external:
   #   - networkx
   #   - json
   ```

4. **Public interface** (what other Bricks can use):
   ```bash
   # interface.public:
   #   - Graph (class)
   #   - Edge (class)
   #   - Subsystem (class)
   #   - load_from_dir, get_dependencies, etc. (functions)
   ```

**Create a working note** (optional but helpful):

```bash
# Create a temporary context file for your session
cat > /tmp/brick-context.txt << 'EOF'
BRICK: BRICK-GRAPH (Graph Core)

ALLOWED FILES (can read/modify):
  - src/jig/core/graph.py
  - src/jig/core/relationships.py
  - tests/unit/test_graph.py
  - tests/unit/test_graph_queries.py
  - tests/unit/test_graph_traversal.py
  - tests/unit/test_relationship_parsing.py

DEPENDENCIES (can use public interfaces):
  - BRICK-PARSER: OSTCNode, parse_ostc_node()
  - BRICK-UTILS: read_file(), write_file(), load_yaml()
  - networkx (external)

FORBIDDEN (do NOT access):
  - src/jig/cli/* (different Brick)
  - src/jig/decompose/* (different Brick)
  - src/jig/core/scanner.py (different Brick)
  - src/jig/core/annotation_validator.py (different Brick)
  - Any file not listed above

TASK: [Describe your task here]
EOF

cat /tmp/brick-context.txt
```

---

### Step 3: Prepare Agent Session (If Using Claude Code)

If working with an AI agent (Claude Code, Cursor, etc.), give it explicit Brick constraints.

#### Option A: Inline Instructions

```bash
# Start Claude Code session
claude

# Then in the conversation:
```

**Message to agent:**

```
I'm working in the BRICK-GRAPH (Graph Core) Brick.

CONTEXT:
- Brick definition: jig/bricks/graph-core.brick.yaml
- Source files: src/jig/core/graph.py, src/jig/core/relationships.py
- Test files: tests/unit/test_graph*.py, tests/unit/test_relationship_parsing.py

CONSTRAINTS:
1. ONLY read/modify files listed above (Brick source + test files)
2. ONLY use public interfaces from dependency Bricks:
   - BRICK-PARSER: OSTCNode, parse_ostc_node()
   - BRICK-UTILS: read_file(), write_file(), load_yaml()
3. DO NOT access files from other Bricks (cli, decompose, scanner, validator)
4. DO NOT use implementation details from other Bricks (only public interfaces)

TASK: [Your task description]

Before making changes, confirm you understand the Brick boundaries.
```

#### Option B: Context File

```bash
# Create a detailed context file
cat > /tmp/brick-session.md << 'EOF'
# Brick Work Session: Graph Core (BRICK-GRAPH)

## Brick Definition
[Paste content of jig/bricks/graph-core.brick.yaml here]

## Task
[Your task description]

## Constraints
- Work ONLY within this Brick's boundaries
- Modify ONLY files listed in `code.paths` and `tests.paths`
- Use dependency Bricks via public interfaces only
- If you need to access other files, STOP and ask

## Source Code

### src/jig/core/graph.py
```python
[Paste full content here]
```

### src/jig/core/relationships.py
```python
[Paste full content here]
```

## Tests

### tests/unit/test_graph.py
```python
[Paste full content here]
```

[... include other test files ...]

## Dependency Interfaces

### BRICK-PARSER (Intent Parser)
Public interface:
- `OSTCNode` class (id, type, title, subsystem, body)
- `parse_ostc_node(path: Path) -> OSTCNode`

Implementation details HIDDEN (use interface only).

### BRICK-UTILS (Foundation Utilities)
Public interface:
- `read_file(path: Path) -> str`
- `write_file(path: Path, content: str) -> None`
- `load_yaml(path: Path) -> dict[str, Any]`

Implementation details HIDDEN (use interface only).
EOF

# Start Claude Code with context
claude
# Then: You: @/tmp/brick-session.md
```

---

### Step 4: Do the Work (Within Brick Boundaries)

Perform your development task while respecting Brick boundaries.

#### Manual Checks During Work

**Before reading a file:**
```bash
# Check if file is in your Brick
grep -q "path/to/file.py" $BRICK_FILE
echo $?  # 0 = found (OK), 1 = not found (STOP)
```

**Before importing from another module:**
```bash
# Check if dependency is declared
grep -A 10 "dependencies:" $BRICK_FILE | grep "BRICK-TARGET"
```

**If you need something not in your Brick:**
1. Check if it's a public interface of a dependency Brick
2. If yes, use it (you have permission)
3. If no, STOP—you may need to:
   - Add the dependency to your Brick definition
   - Request a new public interface from the other Brick
   - Re-evaluate which Brick should own this work

#### Agent Monitoring

If using Claude Code:
- Watch for file access outside allowed paths
- Remind agent if it tries to read forbidden files
- Paste Brick definition again if agent forgets constraints

#### Example Work Session

```bash
# Agent: "Let me read src/jig/core/graph.py"
✓ ALLOWED (in Brick's code.paths)

# Agent: "Let me check src/jig/cli/graph.py"
✗ FORBIDDEN (different Brick)
You: "That file is in BRICK-CLI, outside our BRICK-GRAPH boundaries.
     Stay within Graph Core files only."

# Agent: "Let me import from jig.core.parser"
✓ ALLOWED (BRICK-PARSER is a declared dependency)
BUT: Only use public interface (parse_ostc_node, OSTCNode)

# Agent: "Let me look at the Parser implementation"
✗ FORBIDDEN (internal details of other Brick)
You: "Use the Parser's public interface only. Do not read its implementation."
```

---

### Step 5: Validate Brick Boundaries (Manual)

After completing work, verify that Brick boundaries were respected.

#### 5.1 Check Modified Files

```bash
# See what files were changed
git status --short

# Verify all modified files belong to your Brick
git diff --name-only HEAD

# Example output:
# M src/jig/core/graph.py        ✓ (in BRICK-GRAPH)
# M tests/unit/test_graph.py     ✓ (in BRICK-GRAPH)
# M src/jig/cli/main.py          ✗ VIOLATION (in BRICK-CLI)
```

**If violations found:**
- Revert changes to files outside your Brick
- Move that work to a separate session in the correct Brick

#### 5.2 Check Imports (Static Analysis)

```bash
# Extract imports from modified Brick files
# For Python:
grep -rh "^from jig\." src/jig/core/graph.py src/jig/core/relationships.py | sort -u

# Example output:
# from jig.core.parser import OSTCNode, parse_ostc_node
# from jig.utils.yaml_utils import load_yaml

# Verify against Brick dependencies:
cat $BRICK_FILE | grep -A 5 "dependencies:"
```

**Check:**
- Are all imports from declared dependency Bricks? ✓
- Are any imports from non-dependency Bricks? ✗ (violation)

#### 5.3 Check Coupling (Manual Estimate)

```bash
# Count function calls within Brick (internal) vs external
# This is a rough estimate

# Internal calls (within Graph Core files)
grep -rh "def \w\+(" src/jig/core/graph.py src/jig/core/relationships.py | wc -l

# External calls (to other Bricks)
grep -rh "from jig\." src/jig/core/graph.py src/jig/core/relationships.py | wc -l
```

**Rough coupling ratio:**
- Internal:External should be > 10:1 (good)
- If ratio < 5:1, Brick may be too coupled (review design)

#### 5.4 Run Tests

```bash
# Run tests for your Brick only
pytest tests/unit/test_graph.py \
       tests/unit/test_graph_queries.py \
       tests/unit/test_graph_traversal.py \
       tests/unit/test_relationship_parsing.py -v

# All tests should pass ✓
```

#### 5.5 Validation Checklist

Create a manual checklist:

```
Brick Validation: BRICK-GRAPH
==============================

✓ Modified files:
  ✓ All in code.paths or tests.paths
  ✓ No files from other Bricks touched

✓ Imports:
  ✓ All from declared dependencies (BRICK-PARSER, BRICK-UTILS)
  ✓ No imports from non-dependency Bricks

✓ Interface usage:
  ✓ Used only public interfaces of dependencies
  ✓ Did not access internal details of other Bricks

✓ Tests:
  ✓ All Brick tests pass
  ✓ Added/updated tests for new functionality

✓ Coupling:
  ✓ Rough coupling ratio: 12:1 (internal:external)
  ✓ Brick remains cohesive

✓ Documentation:
  ✓ Updated Brick definition if needed
  ✓ Added comments for complex logic

Ready to commit: YES
```

---

### Step 6: Commit with Brick Tags

Tag your commits with Brick metadata for traceability.

```bash
# Stage only files from your Brick
git add src/jig/core/graph.py \
        src/jig/core/relationships.py \
        tests/unit/test_graph.py \
        tests/unit/test_graph_queries.py

# Commit with Brick tag
git commit -m "feat(graph): add shortest path caching

Implemented within BRICK-GRAPH (Graph Core) boundaries.

Changes:
- Added cache dict to Graph class
- Modified find_path() to use cache
- Added tests for cache hit/miss scenarios

Brick validation:
✓ All files within BRICK-GRAPH scope
✓ Dependencies unchanged (BRICK-PARSER, BRICK-UTILS)
✓ All tests passing (48/48)
✓ Coupling ratio: 12:1 (internal:external)

Brick: BRICK-GRAPH
Files: src/jig/core/graph.py (+45), tests/unit/test_graph.py (+20)"
```

**Commit message format:**

```
<type>(brick-name): <short description>

<detailed description>

Brick validation:
✓ <key checks passed>

Brick: BRICK-<ID>
Files: <files modified>
```

---

## Quick Reference Card

**Copy this for daily use:**

```
BRICK WORKFLOW QUICK REFERENCE
===============================

1. SELECT BRICK
   $ cat jig/bricks/<brick>.brick.yaml
   Note: code.paths, tests.paths, dependencies

2. LOAD CONTEXT
   $ grep -A 10 "code:" jig/bricks/<brick>.brick.yaml
   $ grep -A 10 "tests:" jig/bricks/<brick>.brick.yaml
   $ grep -A 10 "dependencies:" jig/bricks/<brick>.brick.yaml

3. WORK WITHIN BOUNDARIES
   - Modify ONLY files in code.paths + tests.paths
   - Use ONLY public interfaces of dependency Bricks
   - Do NOT access files from other Bricks

4. VALIDATE (manual checks)
   $ git diff --name-only HEAD    # Check modified files
   $ grep "^from jig\." <files>   # Check imports
   $ pytest tests/unit/...        # Run Brick tests

5. COMMIT WITH TAGS
   $ git commit -m "type(brick): description

   Brick: BRICK-<ID>
   Files: <modified files>"
```

---

## Handling Common Scenarios

### Scenario 1: Need to Use Another Brick's Function

**Problem:** You need a function from BRICK-PARSER but don't know if it's public.

**Solution:**
1. Check the dependency Brick's definition:
   ```bash
   cat jig/bricks/intent-parser.brick.yaml | grep -A 20 "interface:"
   ```

2. If the function is listed in `interface.public`, you can use it ✓

3. If not listed, you have options:
   - Use a different public function that achieves the same goal
   - Request that the function be added to the public interface
   - Re-evaluate if this work belongs in the other Brick

### Scenario 2: Accidentally Modified Wrong Brick

**Problem:** You modified files from multiple Bricks in one session.

**Solution:**
1. Identify which files belong to which Bricks:
   ```bash
   for f in $(git diff --name-only); do
     echo "File: $f"
     grep -l "$f" jig/bricks/*.brick.yaml
   done
   ```

2. Create separate commits for each Brick:
   ```bash
   # Commit Brick 1 changes
   git add <brick1-files>
   git commit -m "feat(brick1): ..."

   # Commit Brick 2 changes
   git add <brick2-files>
   git commit -m "feat(brick2): ..."
   ```

3. In future: Use separate work sessions for each Brick

### Scenario 3: Need to Refactor Across Multiple Bricks

**Problem:** You need to rename a function used by multiple Bricks.

**Solution:**
1. This is a **cross-Brick refactoring**—it requires special care
2. Workflow:
   - Identify all Bricks affected
   - For each Brick, create a separate work session
   - Update public interfaces first
   - Update implementations second
   - Update callers third
3. Document: "Cross-Brick refactoring: BRICK-A, BRICK-B, BRICK-C"
4. Consider: Is this a sign that boundaries need adjustment?

### Scenario 4: Unclear Which Brick Owns the Work

**Problem:** Your task touches functionality in multiple Bricks.

**Solution:**
1. Read responsibilities of candidate Bricks:
   ```bash
   grep -A 5 "responsibility:" jig/bricks/*.brick.yaml
   ```

2. Choose the Brick whose responsibility best matches your task

3. If still unclear:
   - Work in the Brick that owns the primary functionality
   - Use public interfaces to interact with other Bricks
   - Document rationale in commit message

4. If the work genuinely spans Bricks:
   - Break task into sub-tasks, one per Brick
   - Do each sub-task in a separate session

### Scenario 5: Public Interface Missing What You Need

**Problem:** A dependency Brick doesn't expose the function you need.

**Solution:**
1. **Check if there's an alternative** - Can you achieve your goal with existing public functions?

2. **Request interface expansion** - Create a note:
   ```bash
   echo "BRICK-PARSER needs to expose: extract_frontmatter(path: Path) -> dict" >> /tmp/interface-requests.txt
   ```

3. **Workaround for now** - Can you duplicate the functionality in your Brick? (Not ideal, but unblocks you)

4. **Schedule interface addition** - In a separate session, update the dependency Brick's public interface

---

## Tips for Effective Brick Work

### 1. One Brick Per Session
- Start a new work session for each Brick
- Don't context-switch between Bricks mid-session
- Keeps cognitive load low and boundaries clear

### 2. Trust the Interfaces
- Don't peek at implementations of dependency Bricks
- Treat them as black boxes with known interfaces
- This is the "clean room" principle

### 3. Keep Brick Definitions Updated
- If you add new files, update `code.paths` or `tests.paths`
- If you add dependencies, update `dependencies.bricks`
- If you change public API, update `interface.public`

### 4. Small, Focused Changes
- Brick boundaries encourage small, cohesive changes
- This is a feature, not a limitation
- Embrace it for better code quality

### 5. Document Boundary Decisions
- When in doubt about what belongs where, document your reasoning
- These notes help refine Brick boundaries over time

---

## Measuring Success

Track these metrics over time to see if Brick workflow is working:

```bash
# Commits per Brick (distribution)
git log --oneline | grep "Brick:" | cut -d: -f2 | sort | uniq -c

# Files modified per commit (should be low)
git log --oneline --numstat | awk '{print NF}' | sort -n | uniq -c

# Cross-Brick commits (should be rare)
git log --oneline | grep "Cross-Brick"

# Brick health (manual check)
# - Are tests passing?
# - Is coupling staying low?
# - Are boundaries holding?
```

---

## Recommendations: Tools to Build Next

Now that you have a working manual process, these deterministic tools would make the workflow much smoother:

### Priority 1: Essential Automation (High Value, Low Effort)

#### 1.1 `jigy brick load <brick-id>`
**Purpose:** Generate a Brick context file automatically

**What it does:**
- Reads Brick definition from `jig/bricks/<brick>.brick.yaml`
- Outputs a markdown file with:
  - Brick metadata
  - Full content of all source files
  - Full content of all test files
  - Public interfaces of dependency Bricks (stub form)
  - Allowed/forbidden file lists
- Output to stdout or file

**Usage:**
```bash
$ jigy brick load BRICK-GRAPH --output /tmp/context.md
$ claude # then paste /tmp/context.md
```

**Estimated effort:** 2-4 hours (just file reading + formatting)

**Value:** Eliminates manual context gathering (Step 2)

---

#### 1.2 `jigy brick validate <brick-id>`
**Purpose:** Automated boundary validation

**What it does:**
- Checks `git diff` to see modified files
- Verifies all modified files are in Brick's `code.paths` or `tests.paths`
- Checks imports against declared dependencies
- Reports violations

**Usage:**
```bash
$ git add .
$ jigy brick validate BRICK-GRAPH
✓ All files within Brick scope
✓ All imports from declared dependencies
✓ Ready to commit
```

**Estimated effort:** 4-6 hours (git integration + static analysis)

**Value:** Automates validation (Step 5), catches errors before commit

---

#### 1.3 `jigy brick list`
**Purpose:** Quick Brick discovery

**What it does:**
- Lists all Bricks with ID, name, and responsibility
- Shows which files belong to which Brick
- Helps answer "which Brick owns this file?"

**Usage:**
```bash
$ jigy brick list
BRICK-GRAPH    Graph Core             src/jig/core/graph.py
BRICK-PARSER   Intent Parser          src/jig/core/parser.py
BRICK-SCANNER  Annotation Scanner     src/jig/core/scanner.py
...

$ jigy brick list --file src/jig/core/graph.py
BRICK-GRAPH (Graph Core)
```

**Estimated effort:** 1-2 hours (simple file enumeration)

**Value:** Speeds up Brick selection (Step 1)

---

### Priority 2: Workflow Enhancement (Medium Value, Medium Effort)

#### 2.1 `jigy brick interfaces <brick-id>`
**Purpose:** Show public interface of a Brick

**What it does:**
- Extracts `interface.public` from Brick definition
- Formats as usable stubs (function signatures, class definitions)
- Can generate `.pyi` stub files for type checking

**Usage:**
```bash
$ jigy brick interfaces BRICK-PARSER
from pathlib import Path

class OSTCNode:
    id: str
    type: NodeType
    title: str
    subsystem: str | None
    body: str

def parse_ostc_node(path: Path) -> OSTCNode: ...
```

**Estimated effort:** 3-5 hours (parsing + formatting)

**Value:** Makes dependency interfaces discoverable

---

#### 2.2 `jigy brick deps <brick-id>`
**Purpose:** Visualize Brick dependency graph

**What it does:**
- Reads all Brick definitions
- Builds dependency graph
- Shows upstream/downstream Bricks

**Usage:**
```bash
$ jigy brick deps BRICK-GRAPH
Dependencies (upstream):
  BRICK-PARSER → BRICK-GRAPH
  BRICK-UTILS  → BRICK-GRAPH

Dependents (downstream):
  BRICK-GRAPH → BRICK-INDEX
  BRICK-GRAPH → BRICK-CLI
  BRICK-GRAPH → BRICK-DECOMPOSE
```

**Estimated effort:** 2-3 hours (graph traversal)

**Value:** Helps understand impact of changes

---

#### 2.3 `jigy brick check-interface <brick-id>`
**Purpose:** Verify public interface matches implementation

**What it does:**
- Extracts actual exported classes/functions from code
- Compares to `interface.public` in Brick definition
- Reports mismatches (missing or extra exports)

**Usage:**
```bash
$ jigy brick check-interface BRICK-GRAPH
✓ Graph (class) - found
✓ Edge (class) - found
✗ get_dependencies (function) - NOT EXPORTED (should be public)
⚠ internal_helper (function) - EXPORTED but not in interface.public
```

**Estimated effort:** 4-6 hours (AST parsing)

**Value:** Keeps Brick definitions accurate

---

### Priority 3: Advanced Features (High Value, High Effort)

#### 3.1 `jigy brick work <brick-id> <task>`
**Purpose:** Integrated Brick work session

**What it does:**
- Loads Brick context
- Starts agent with context pre-loaded
- Monitors file access in real-time
- Blocks access to files outside Brick
- Validates on exit

**Usage:**
```bash
$ jigy brick work BRICK-GRAPH "add shortest path caching"
[Context loaded: BRICK-GRAPH]
[Agent started with Brick constraints]
[Working...]
[Validation: ✓ All checks passed]
```

**Estimated effort:** 10-15 hours (requires agent integration or wrapper)

**Value:** Seamless Brick-aware workflow

---

#### 3.2 Brick Health Metrics
**Purpose:** Track Brick quality over time

**What it does:**
- Calculates coupling ratio (internal:external calls)
- Measures test coverage per Brick
- Tracks cyclomatic complexity
- Generates health score

**Usage:**
```bash
$ jigy brick health BRICK-GRAPH
Coupling ratio: 12:1 ✓
Test coverage: 75% ⚠ (target: 80%)
Complexity: medium-high ⚠
Health score: 87/100 (Good)
```

**Estimated effort:** 8-12 hours (static analysis)

**Value:** Identifies Bricks that need attention

---

### Priority 4: Ecosystem Integration (Long-term)

#### 4.1 IDE Integration
- VS Code extension: Highlight Brick boundaries
- Show which Brick a file belongs to in status bar
- Warn when editing file outside current Brick

#### 4.2 Git Hooks
- Pre-commit hook: Auto-run `jigy brick validate`
- Commit-msg hook: Auto-add Brick tags

#### 4.3 CI Integration
- GitHub Action: Validate all commits respect Brick boundaries
- PR checks: Show which Bricks were modified
- Brick-level test runs

---

## Build Order Recommendation

If implementing tools, do them in this order:

1. **`jigy brick list`** (1-2h) - Helps with Brick discovery
2. **`jigy brick load`** (2-4h) - Eliminates manual context prep
3. **`jigy brick validate`** (4-6h) - Catches violations automatically
4. **`jigy brick interfaces`** (3-5h) - Makes dependencies discoverable
5. **`jigy brick deps`** (2-3h) - Shows Brick relationships
6. **`jigy brick check-interface`** (4-6h) - Keeps definitions accurate

**Total effort for core tools: ~16-26 hours**

Then, if valuable:
7. **`jigy brick work`** (10-15h) - Integrated workflow
8. **Brick health metrics** (8-12h) - Quality tracking

---

## Conclusion

**You can start using Brick workflow TODAY** with this manual process:

1. Read Brick definition
2. Load context manually (or create context file)
3. Work within boundaries (with agent or solo)
4. Validate manually (check files, imports, tests)
5. Commit with Brick tags

**This works right now** without any new tooling.

**Build tools incrementally** to automate the tedious parts:
- Context loading (`brick load`)
- Validation (`brick validate`)
- Interface discovery (`brick interfaces`)

**The key insight:** Bricks are a **discipline**, not just a tool. The manual workflow establishes the discipline. Tools make it easier to maintain.

**Start with one Brick, one task.** See how it feels. Refine the process. Build tools when you feel the friction.

---

**Next Actions:**

1. ✓ Brick definitions exist (done)
2. ☐ Try manual workflow on one small task
3. ☐ Document what was painful vs helpful
4. ☐ Build first tool (`jigy brick list` or `jigy brick load`)
5. ☐ Iterate

---

**Questions? Feedback?**

This is a living document. Update it as you learn what works and what doesn't.

Brick on! 🧱
