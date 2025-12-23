---
id: S-042
title: Outcome Specification Requirement
type: specification
---

# Outcome Specification Requirement

All outcomes SHALL have a non-empty `specifies` array containing at least one specification ID.

**Acceptance Criteria**:
- Validation function checks every outcome node for `specifies` field
- Empty `specifies: []` arrays are reported as errors
- Error message identifies which outcome(s) have empty specifies arrays
- Error message explains that outcomes must decompose into concrete specifications
- Suggests action: "Add specification IDs to the `specifies` array"

**Rationale**: Outcomes capture WHY we build something (business value, user needs). Without concrete specifications (WHAT to build), outcomes cannot be implemented or verified. The `specifies` array decomposes high-level outcomes into actionable specifications that can be implemented and tested. An outcome with an empty `specifies` array is incomplete and blocks the O→S→TDD workflow.

**Valid Example**:
```yaml
---
id: O-001
type: outcome
specifies: [S-001, S-003, S-005, S-006]
---
```

**Invalid Example**:
```yaml
---
id: O-015
type: outcome
specifies: []  # ERROR: Outcome must specify at least one specification
---
```

**Error Message Format**:
```
ERROR: jig/outcomes/O-015.md
  - Outcome completeness: Outcome 'O-015' has empty specifies array
  - Outcomes must decompose into at least one concrete specification
  - Fix: Add specification IDs to the 'specifies' array
```

**References**:
- A001 Section 3: Outcome Files (specifies field REQUIRED, MAY be empty but should not)
- O-015: Completeness validation for intent graph
