---
id: S-022
title: Brick Partition Validation
type: specification
outcomes: [O-005]
architecture: [A-004]
---

# Brick Partition Validation

Validate brick partition constraint: every function belongs to exactly one brick, no class splitting.

**Acceptance Criteria**:
- Load implementation graph from `implementation-graph.ndjson`
- Expand module units (`M-auth.session`) to all contained function units
- Expand class units (`C-auth.Session`) to all method function units
- Build function-to-brick mapping from expanded units
- Detect partition gaps: functions in zero bricks
- Detect partition overlaps: functions in multiple bricks
- Detect class splitting: class methods split across different bricks
- Error messages list specific functions and their brick assignments
- Report all violations (don't stop at first error)

**Rationale**: Brick partition is a fundamental constraint. Gaps mean unassigned code, overlaps mean ambiguous ownership, class splitting violates cohesion.

**References**: A001 §10 (Validation Rules), AG026 (Linter Proposal)
