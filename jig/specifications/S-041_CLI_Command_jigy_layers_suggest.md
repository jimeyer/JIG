---
id: S-041
title: "CLI Command: jigy layers suggest"
type: specification
---

# CLI Command: jigy layers suggest

The `jigy layers suggest` command SHALL analyze brick dependencies and suggest appropriate layer assignments based on the dependency structure.

**Acceptance Criteria**:
- Command loads bricks.yaml and implementation-graph.ndjson
- Derives brick dependencies from function call graph
- Performs topological sort of brick dependency graph
- Assigns layers using algorithm: `layer = max(dependency_layers) + 1`
- Bricks with no dependencies are assigned layer 0
- Compares current layer assignments (from bricks.yaml) with suggested assignments
- Displays comparison showing:
  - Brick ID and name
  - Current layer (if present)
  - Suggested layer
  - Reason for suggestion (e.g., "depends on B-x at layer 1")
- Identifies mismatches between current and suggested
- Supports `--apply` flag to update bricks.yaml with suggested layers
- With `--apply`, prompts for confirmation before modifying file
- Returns error if circular dependencies exist (cannot assign layers to graph with cycles)

**Rationale**: Layer assignment can be derived mechanically from dependency structure. This command helps developers discover appropriate layers when starting with a flat architecture or when refactoring. AG029 Section 7 describes the suggestion algorithm and its role in discovering layer structure.

**Example Output**:
```
Suggested layer assignments based on dependencies:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

B-core-utils: Core Utilities
  Current layer: (not set)
  Suggested: 0 (no dependencies)

B-data-models: Data Models
  Current layer: (not set)
  Suggested: 0 (no dependencies)

B-impl-graph: Implementation Graph Core
  Current layer: 1
  Suggested: 1 (depends on B-core-utils at layer 0) ✓ MATCHES

B-cli: CLI Interface
  Current layer: 3
  Suggested: 2 (depends on B-impl-graph at layer 1, B-validation at layer 1) ⚠ MISMATCH

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1 brick matches, 1 mismatch, 2 unset

Apply suggestions? [y/N]
```

**Algorithm (Topological Layer Assignment)**:
1. Build directed graph of brick dependencies
2. Check for cycles (if cycles exist, report error and exit)
3. Initialize all bricks with layer = -1 (unassigned)
4. For each brick in topological order:
   - If brick has no dependencies: assign layer 0
   - Otherwise: assign layer = max(dependency layers) + 1
5. Return layer assignments

**Usage**:
```bash
jigy layers suggest              # Show suggestions
jigy layers suggest --apply      # Apply suggestions to bricks.yaml
```

**Error Handling**:
- If cycles detected: "Cannot suggest layers: circular dependencies exist. Run 'jigy validate bricks' to see cycles."
- If implementation graph missing: "Implementation graph not found. Run 'jigy impl rebuild' first."
- If bricks.yaml invalid: "bricks.yaml validation failed. Run 'jigy validate bricks' first."

**References**:
- AG029 Section 7: Layer Assignment Heuristics
- AG029 Section 8: Integration with Brick Detection
- A001 Section 4: Brick Definitions (layer field)
