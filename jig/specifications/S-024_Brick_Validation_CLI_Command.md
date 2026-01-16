---
id: S-024
title: Brick Validation CLI Command
type: specification
outcomes: [O-004, O-006]
architecture: [A-002, A-004]
---

# Brick Validation CLI Command

Provide `jigy validate bricks` command to validate brick definitions and partition constraints AGAINST implementation graph.

**Acceptance Criteria**:
- Command `jigy validate bricks` runs all Phase 3 validators
- Validates brick definitions (S-021)
- Validates brick partition (S-022)
- Requires `implementation-graph.ndjson` to exist (error if missing)
- Exit code 0 on success, 1 on validation failures, 2 on errors
- Output grouped by validation phase (definitions, partition)
- Shows count of bricks and functions validated
- Support granular subcommands: `jigy validate bricks definitions`, `jigy validate bricks partition`
- Error message if no implementation graph: "implementation graph not found, run 'jigy impl rebuild' first"

**Rationale**: Brick validation requires implementation graph as reference. Clear dependency on graph existence.

**References**: AG026 §2.3 (Phase 3: Validate Bricks)
