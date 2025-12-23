---
id: S-037
title: Layer Value Validation
type: specification
---

# Layer Value Validation

Layer field values SHALL be non-negative integers (>= 0).

**Acceptance Criteria**:
- Validation function checks that `layer` values are integers
- Validation function checks that `layer` values are >= 0
- Type errors (string, float, null, etc.) are reported clearly
- Negative values are reported with error message
- Error message shows the invalid value and brick ID

**Rationale**: Layer numbers represent architectural depth. Layer 0 is the foundation, and each higher layer depends only on lower layers. Negative layers have no semantic meaning. Non-integer values would break layer constraint logic.

**Valid Examples**:
- `layer: 0` (foundation)
- `layer: 1`
- `layer: 2`
- `layer: 10`

**Invalid Examples**:
- `layer: -1` (negative number)
- `layer: "0"` (string, not integer)
- `layer: 1.5` (float, not integer)
- `layer: null` (null value)
- `layer: []` (wrong type)

**References**:
- A001 Section 4: Brick Definitions (layer semantics)
- A001 Section 10: Validation Contract (rule #11)
- AG029 Section 1: Decision (non-negative integers)
