---
id: S-040
title: 'CLI Command: jigy layers'
type: specification
outcomes: [O-014]
architecture: [A-002]
---

# CLI Command: jigy layers

The `jigy layers` command SHALL visualize brick layer structure, showing bricks grouped by layer with their dependencies.

**Acceptance Criteria**:
- Command loads bricks.yaml and implementation-graph.ndjson
- Output groups bricks by layer (Layer 0, Layer 1, Layer 2, ...)
- For each brick, shows:
  - Brick ID and name
  - Function count
  - Dependencies (other bricks it depends on)
- Output is formatted for terminal readability (boxes, colors, alignment)
- Command supports options:
  - `--summary`: Show only layer counts and brick counts per layer
  - `--verbose`: Show detailed function lists and full dependency information
  - Default: Show brick-level summary with dependencies
- Displays total summary at bottom: brick count, layer count, function count, DAG status
- If dependency graph is not a DAG, indicates "⚠ Cycles detected"

**Rationale**: Developers need to visualize the layer structure to understand system architecture and verify that bricks are organized correctly. AG029 Section 6.2 specifies this command as essential for architectural visibility.

**Example Output (Default)**:
```
Brick Layer Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Layer 0: Foundation (2 bricks)
─────────────────────────────────────────────
  B-core-utils: Core Utilities (23 functions)
  B-data-models: Data Models (15 functions)

Layer 1: Core Logic (3 bricks)
─────────────────────────────────────────────
  B-impl-graph: Implementation Graph Core (31 functions)
    ↓ depends on: B-core-utils

  B-validation: Artifact Validation (28 functions)
    ↓ depends on: B-core-utils, B-data-models

  B-analyzers: Language Analyzers (18 functions)
    ↓ depends on: B-core-utils, B-impl-graph

Layer 2: Interface (1 brick)
─────────────────────────────────────────────
  B-cli: CLI Interface (12 functions)
    ↓ depends on: B-core-utils, B-impl-graph, B-validation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 6 bricks, 3 layers, 127 functions
Dependency graph: DAG ✓ (no cycles)
```

**Example Output (--summary)**:
```
Layer Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Layer 0: 2 bricks, 38 functions
Layer 1: 3 bricks, 77 functions
Layer 2: 1 brick, 12 functions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 6 bricks, 3 layers, 127 functions
```

**Usage**:
```bash
jigy layers                    # Show layer structure
jigy layers --summary          # Show counts only
jigy layers --verbose          # Show full details
```

**References**:
- AG029 Section 6.2: New Command: jigy layers
- A001 Section 4: Brick Definitions (layer field)
