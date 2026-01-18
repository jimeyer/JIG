---
id: S-025
title: Full Validation CLI Command
type: specification
outcomes: [O-004, O-006]
architecture: [A-002, A-004]
---

# Full Validation CLI Command

Provide `jigy validate` command that intelligently runs both intent and brick validation.

**Acceptance Criteria**:
- Command `jigy validate` (no subcommand) runs full validation
- Always runs intent validation (S-023)
- Conditionally runs brick validation (S-024) if implementation graph exists
- Skips brick validation gracefully if no implementation graph (not an error)
- Exit code 0 on success, 1 on validation failures, 2 on errors
- Use case: "check everything that's possible to check right now"

## Human Output Format

Success output is a single line combining rebuild and validation:
```
Rebuilt 3 graphs. Validated 92 specs, 25 outcomes, 15 bricks.
```

Components:
- Rebuild summary (if graphs were rebuilt): "Rebuilt N graphs."
- Artifact counts: "Validated X specs, Y outcomes, Z bricks."

On failure, errors are listed followed by summary:
```
jig/specifications/S-042.md: [S-018] Missing required field 'outcomes'

Validation failed: 1 error (1 auto-fixable, 0 manual)
```

## Verbose Output (-v)

Verbose mode shows category breakdown:
```
Intent: 122 artifacts
  ✓ 92 specifications
  ✓ 25 outcomes
  ✓ 5 goals

Bricks: 15 definitions
  ✓ 238 files partitioned
  ✓ 0 layer violations

Validated 92 specs, 25 outcomes, 15 bricks.
```

**Rationale**: Smart validation provides single command for developers without requiring them to know graph state. Graceful degradation when graphs don't exist.

**References**: AG026 §3 (CLI Interface)
