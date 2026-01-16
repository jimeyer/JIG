---
id: S-042
title: Outcomes Must Specify Specifications
type: specification
outcomes: [O-015]
architecture: [A-004]
---

# Outcomes Must Specify Specifications

All outcomes SHALL have a non-empty `specifications` array containing at least one specification ID.

**Acceptance Criteria**:
- Validation function checks every outcome node for `specifications` field
- Empty `specifications: []` arrays are reported as errors
- Error message identifies which outcome(s) have empty specifications arrays
- Error message explains that outcomes must decompose into concrete specifications
- Suggests action: "Add specification IDs to the `specifications` array"

**Rationale**: Outcomes capture WHY we build something (business value, user needs). Without concrete specifications (WHAT to build), outcomes cannot be implemented or verified. The `specifications` array decomposes high-level outcomes into actionable specifications that can be implemented and tested. An outcome with an empty `specifications` array is incomplete and blocks the O→S→TDD workflow.

**Valid Example**:
```yaml
---
id: O-001
type: outcome
specifications: [S-001, S-003, S-005, S-006]
---
```

**Invalid Example**:
```yaml
---
id: O-015
type: outcome
specifications: []  # ERROR: Outcome must specify at least one specification
---
```

**Error Message Format**:
```
ERROR: jig/outcomes/O-015.md
  - Outcome completeness: Outcome 'O-015' has empty specifications array
  - Outcomes must decompose into at least one concrete specification
  - Fix: Add specification IDs to the 'specifications' array
```

**References**:
- A001 Section 3: Outcome Files (specifications field REQUIRED, MAY be empty but should not)
- O-015: Completeness validation for intent graph
