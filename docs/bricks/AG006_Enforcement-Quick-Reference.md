# Brick Enforcement - Quick Reference

**How to work within Brick boundaries with Claude Code**

---

## The 4 Layers

```
1. Brick Definitions (.brick.yaml)     ← Declare what's in/out
2. Context Loader (jigy brick load)    ← Pre-load allowed context
3. Tool Wrappers (future)              ← Prevent violations at runtime
4. Validation (jigy brick validate)    ← Check compliance after
```

---

## Quick Workflow (Today)

### 1. Generate Context

```bash
$ jigy brick load BRICK-GRAPH --output context.md
```

### 2. Start Claude Code

```bash
$ claude
You: @context.md
You: Add caching to graph traversal. Stay within BRICK-GRAPH boundaries.
```

### 3. Agent Works (Constrained)

Claude sees only:
- ✅ Graph Core source files (2 files, 696 LOC)
- ✅ Graph Core tests (4 files)
- ✅ Intent nodes for this Brick
- ✅ **Interfaces only** of Parser and Utils Bricks
- ❌ No CLI code
- ❌ No other Bricks' implementation details

### 4. Validate After

```bash
$ jigy brick validate BRICK-GRAPH

✓ File Boundary: All changes within Brick
✓ Imports: Only declared dependencies
✓ Coupling: 14:1 (good)
✓ Interfaces: Only public APIs used
```

---

## What Goes in .brick.yaml

```yaml
brick:
  id: BRICK-GRAPH
  name: "Graph Core"

context:
  source_files:
    - src/jig/core/graph.py          # What the Brick owns
    - src/jig/core/relationships.py

  test_files:
    - tests/unit/test_graph.py       # Brick's tests

  intent_nodes:
    - O-GRAPH-001                     # Brick's intent
    - S-GRAPH-001

dependencies:
  bricks:
    BRICK-PARSER:                     # What the Brick can use
      access: public_interface_only   # Interface only, not implementation
      imports:
        - OSTCNode
        - parse_ostc_node

forbidden:
  - src/jig/cli/*                     # Explicit deny list
  - src/jig/decompose/*
```

---

## What Context Loader Produces

**context.md contains:**

1. ✅ **Full source code** of Brick files
2. ✅ **Full tests** of Brick
3. ✅ **Intent nodes** (O/S/C) for Brick
4. ✅ **Type signatures only** of dependencies (no implementation)
5. ✅ **Artifact schemas** (e.g., graph-index.json format)
6. ❌ **No implementation** of other Bricks
7. ❌ **No internal details** of dependencies

---

## Validation Checks

`jigy brick validate BRICK-GRAPH` checks:

| Check | What It Does |
|-------|-------------|
| **File Boundary** | Modified files are in Brick's source/test lists |
| **Imports** | Only declared dependencies imported |
| **Coupling** | Internal:external call ratio above threshold |
| **Interfaces** | Only public APIs of dependencies used |
| **Coverage** | Tests meet coverage target |

---

## Benefits

### Smaller Context
- **Before:** Agent sees 5,600 LOC (entire codebase)
- **After:** Agent sees ~700 LOC (one Brick)
- **Result:** 8x reduction in noise

### Clearer Boundaries
- **Before:** "Don't change CLI code" (vague)
- **After:** Tool restrictions + validation (enforced)
- **Result:** Fewer accidental violations

### Better Quality
- **Before:** Agent distracted by irrelevant code
- **After:** Agent focused on single responsibility
- **Result:** More coherent implementations

---

## Commands to Implement

### Phase 1 (Now)

```bash
# Load Brick context for agent work
jigy brick load <brick-id> [--output FILE]

# Validate Brick boundaries after work
jigy brick validate <brick-id> [--verbose]

# List all Bricks
jigy brick list

# Show Brick definition
jigy brick show <brick-id>
```

### Phase 2 (Later)

```bash
# Analyze Brick health
jigy brick health <brick-id>

# Visualize Brick dependencies
jigy brick graph [--format png|svg|mermaid]

# Check if change would violate boundaries (pre-commit)
jigy brick check-change <brick-id> <files...>
```

---

## Example Session

```bash
$ jigy brick load BRICK-GRAPH --output /tmp/context.md

Brick Context Generated: Graph Core (BRICK-GRAPH)
================================================

Included:
  ✓ 2 source files (696 LOC)
  ✓ 4 test files (320 tests)
  ✓ 3 intent nodes
  ✓ 2 dependency interfaces (Parser, Utils)

Excluded:
  ✗ CLI implementation (8 files)
  ✗ Decompose implementation (1 file)
  ✗ Scanner implementation (2 files)
  ✗ Other Brick internals

Context saved to: /tmp/context.md (45 KB)

Usage:
  1. Load in Claude Code: @/tmp/context.md
  2. Request agent to stay within boundaries
  3. After work: jigy brick validate BRICK-GRAPH

$ claude
You: @/tmp/context.md
You: Add a caching layer to graph traversal for frequently-accessed paths.
     You must work within BRICK-GRAPH boundaries only.

Claude: I'll add caching to the Graph Core Brick. Let me read the current
        graph.py implementation...

[Agent works...]

You: Done? Run validation.

$ jigy brick validate BRICK-GRAPH

Validating: Graph Core (BRICK-GRAPH)
====================================

✓ File Boundary: 2 files modified (both in Brick)
✓ Import Validation: All imports declared
✓ Coupling Ratio: 15:1 (above 10:1 threshold)
✓ Interface Usage: Only public APIs used
⚠ Test Coverage: 79% (target: 80%)

Brick Health: Good (88/100)

Recommendation: Add 2 more tests to reach coverage target

$ git add src/jig/core/graph.py tests/unit/test_graph.py
$ git commit -m "feat(graph): add path caching

Implemented within BRICK-GRAPH boundaries.
Validation: jigy brick validate BRICK-GRAPH ✓"
```

---

## Escape Hatches

When you need to break boundaries:

```bash
# Work across multiple Bricks (architectural changes)
$ jigy brick load --architect-mode
# Shows all Brick interfaces, no implementations

# Temporary cross-Brick work (refactoring)
$ jigy brick validate --allow-cross-brick BRICK-A,BRICK-B
# Permits changes across specified Bricks

# Emergency override (use sparingly!)
$ jigy brick validate --override
# Skips validation (requires justification)
```

---

## Key Principles

1. **Single Responsibility** - Each Brick has one clear purpose
2. **Published Interfaces** - Dependencies expose only public APIs
3. **Enforced Boundaries** - Can't accidentally couple across Bricks
4. **Measurable Quality** - Validation provides objective metrics
5. **Agent-Friendly** - Smaller context = better results

---

## Next Steps

1. ✅ Read full proposal: `Brick-Context-Enforcement-Proposal.md`
2. ✅ Create Brick definitions for all 10 JIG Bricks
3. ✅ Implement `jigy brick load` command
4. ✅ Implement `jigy brick validate` command
5. ✅ Try Brick Mode on next feature

---

**Full Details:** See `Brick-Context-Enforcement-Proposal.md`
