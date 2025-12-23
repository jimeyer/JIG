---
id: S-038
title: Layer Constraint Validation
type: specification
---

# Layer Constraint Validation

Brick dependencies SHALL respect layer hierarchy: brick at layer N can only depend on bricks at layers < N, or other layer 0 bricks if N=0.

**Acceptance Criteria**:
- Validation derives brick dependencies from implementation graph (function calls)
- For each brick B at layer L, check all bricks B depends on
- If L > 0: All dependency bricks must have layer < L
- If L = 0: Dependency bricks must have layer = 0 (layer 0 can depend on layer 0)
- Violations are reported with:
  - Source brick ID and layer
  - Dependency brick ID and layer
  - The function call that creates the dependency (F-source → F-target)
  - Clear explanation of the violation
- Error message suggests fixes (raise source brick layer, lower dependency brick layer, or refactor)

**Rationale**: Layer constraints enforce architectural discipline. Foundation code (layer 0) cannot depend on high-level features (layer 2+). This prevents circular dependencies and makes system structure explicit. Same-layer dependencies are only allowed at layer 0 to form a foundation cluster.

**Valid Dependencies**:
- Layer 1 → Layer 0 ✓
- Layer 2 → Layer 1 ✓
- Layer 2 → Layer 0 ✓
- Layer 0 → Layer 0 ✓ (if no cycles)

**Invalid Dependencies**:
- Layer 1 → Layer 2 ✗ (upward dependency)
- Layer 0 → Layer 1 ✗ (foundation depending on higher layer)
- Layer 1 → Layer 1 ✗ (same-layer dependency, only allowed at layer 0)
- Layer 2 → Layer 2 ✗ (same-layer dependency, only allowed at layer 0)

**Example Error**:
```
ERROR: Layer constraint violation

B-impl-graph (layer 1) depends on B-cli (layer 2)
  → F-impl_graph.builder.build calls F-cli.main.run
  → Violation: Layer 1 cannot depend on layer 2

Fix options:
  - Raise B-impl-graph to layer 3
  - Lower B-cli to layer 0
  - Refactor to remove dependency
```

**References**:
- A001 Section 4: Brick Definitions (layer semantics)
- A001 Section 10: Validation Contract (rule #12)
- AG029 Section 2: Validation Rules (layer constraint compliance)
