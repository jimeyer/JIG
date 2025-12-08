# Specification Audit: S-030

**Date**: 2025-12-07
**Auditor**: Claude (Automated Audit)

## Summary

- **Specification**: Compute Brick Membership at Query Time
- **Alignment Status**: UNIMPLEMENTED
- **Outcome Alignment**: ALIGNED
- **Upstream Outcome**: O-010 (Visualize Bricks as Compound Nodes)
- **Implementing Functions**: 0
- **Verifying Tests**: 0

## Specification Review

**Quality Assessment: HIGH QUALITY**

- **ID Format**: Correct (`S-030` matching `S-NNN` pattern)
- **Required Fields**: Present (`id`, `type: specification`)
- **Clear Intent**: YES - Specifies computation of brick-to-node membership at query time per A001 §6.2
- **Testable Criteria**: YES - 9 concrete acceptance criteria covering computation, expansion, validation, and logging
- **Precise Language**: EXCELLENT - Uses RFC 2119 keyword "MUST", clear requirements

**Acceptance Criteria Summary**:
1. Extract brick nodes from intent graph with `units` arrays
2. Expand M- prefixed units to all implementation nodes with matching module prefix
3. Expand C- prefixed units to class node + all method nodes
4. Expand F- prefixed units to exact function match
5. Return brick membership map: implementation node ID → brick ID
6. Validate brick partition constraint per A001 §10 (every function belongs to exactly one brick)
7. Log warnings for partition violations (functions in multiple bricks or no brick)
8. Computation happens in memory at query time (no modification to NDJSON files on disk)
9. Console logs show membership computation results (count of nodes assigned, validation status)

**Rationale**: Clear reference to A001 §6.2 mandate for query-time computation. Ensures implementation graph remains pure and brick assignments stay synchronized with bricks.yaml source of truth.

## Outcome Alignment

**Upstream Outcome**: O-010 - Visualize Bricks as Compound Nodes

- **Bidirectional Consistency**: CONFIRMED - O-010 specifies [S-030, S-031, S-034]
- **Outcome Goal**: Enable developers to see brick boundaries as visual containers around member implementation nodes in the graph visualizer
- **Semantic Contribution**: STRONG - S-030 provides the foundational membership computation that S-031 and S-034 build upon for visualization

### Sibling Specifications

| Sibling Spec | Title | Status | Contributes To Outcome |
|--------------|-------|--------|------------------------|
| S-030 | Compute Brick Membership at Query Time | UNIMPLEMENTED | Foundation: Computes brick membership |
| S-031 | Render Bricks as Cytoscape Compound Nodes | UNIMPLEMENTED | Visualization: Renders compound nodes |
| S-034 | Layout Algorithms Support Compound Nodes | UNIMPLEMENTED | Interaction: Ensures layouts work correctly |

### Outcome Coverage Analysis

**Assessment**: COMPLETE DECOMPOSITION

The three specifications form a coherent pipeline:
1. **S-030**: Compute membership (data layer) - Maps implementation nodes to bricks
2. **S-031**: Render compound nodes (presentation layer) - Creates visual representation
3. **S-034**: Layout integration (interaction layer) - Ensures usability across all layouts

Together, these specifications fully address O-010's goal of making brick architecture visible and tangible. No gaps detected in the decomposition.

**Dependencies**: S-031 depends on S-030's membership computation. S-034 depends on S-031's compound node structure.

## Implementation Analysis

**STATUS**: NO IMPLEMENTATIONS FOUND

No functions decorated with `@jig.implements("S-030")` were found in the codebase.

### Related Code Found

While no direct S-030 implementations exist, related brick membership logic was found in:

1. **`src/jig/validation/bricks.py`** - Contains `_expand_units_to_functions()` function (line 385)
   - Implements M-/C-/F- prefix expansion logic
   - Used for validation purposes, not query-time computation
   - Could be refactored/reused for S-030 implementation

2. **`src/jig/cli/layers.py`** - Contains brick-to-unit mapping (lines 90-95)
   - Builds `unit_to_brick` mapping from bricks.yaml
   - Does NOT expand M-/C-/F- prefixes
   - Used for layer visualization, not general membership computation

### Missing Implementation

All 9 acceptance criteria lack implementation:

1. **Extract brick nodes**: No function extracts bricks with units arrays from intent graph
2. **Expand M- units**: Partial logic exists in validation code but not exposed for query-time use
3. **Expand C- units**: Partial logic exists in validation code but not exposed for query-time use
4. **Expand F- units**: Partial logic exists in validation code but not exposed for query-time use
5. **Return membership map**: No function returns implementation node ID → brick ID mapping
6. **Validate partition**: Validation exists (S-022) but not integrated into query-time computation
7. **Log warnings**: No logging for partition violations during query-time computation
8. **In-memory computation**: No query-time computation exists
9. **Console logs**: No console output for membership computation results

**Impact**: Without S-030 implementation, brick visualization (O-010) cannot be achieved. S-031 and S-034 cannot proceed.

## Verification Analysis

**STATUS**: NO TESTS FOUND

No tests decorated with `@jig.verifies("S-030")` were found in the test suite.

### Missing Verification

All 9 acceptance criteria lack test coverage:

1. No test verifies brick node extraction from intent graph
2. No test verifies M- prefix expansion (e.g., `M-jig.cli` → all matching nodes)
3. No test verifies C- prefix expansion (e.g., `C-auth.Token` → class + methods)
4. No test verifies F- prefix exact matching
5. No test verifies membership map structure and correctness
6. No test verifies partition constraint validation
7. No test verifies warning logs for partition violations
8. No test verifies in-memory computation (no NDJSON file modification)
9. No test verifies console log output for membership results

**Test Requirements**: Should include:
- Unit tests for prefix expansion logic (M-/C-/F-)
- Integration tests for full membership computation
- Tests verifying partition constraint detection
- Tests verifying no file modifications occur
- Tests verifying console output format and content

## Coverage Analysis

**STATUS**: NOT APPLICABLE

No implementing functions or tests exist, so coverage analysis cannot be performed.

## Recommendations

### Critical Priority

1. **IMPLEMENT S-030 FOUNDATION** - This is a blocking dependency for O-010
   - Create dedicated membership computation module (e.g., `src/jig/graph/brick_membership.py`)
   - Refactor `_expand_units_to_functions()` from validation code into reusable utility
   - Implement query-time membership map computation
   - Add partition validation with logging
   - Ensure in-memory computation only (no file modifications)

2. **ADD COMPREHENSIVE TESTS**
   - Create `tests/unit/test_brick_membership.py` for unit tests
   - Create `tests/integration/test_brick_membership_computation.py` for end-to-end tests
   - Test all prefix expansion types (M-, C-, F-)
   - Test partition validation and warning generation
   - Test edge cases (empty bricks, overlapping units, gaps)

3. **INTEGRATE WITH VISUALIZER**
   - Once S-030 is implemented, integrate membership computation into visualizer query flow
   - Ensure S-031 can consume the membership map
   - Coordinate with S-034 for layout integration

### High Priority

4. **DOCUMENT COMPUTATION API**
   - Document the expected input format (intent graph structure)
   - Document the output format (membership map structure)
   - Document error handling and warning scenarios
   - Add usage examples for visualizer integration

5. **PERFORMANCE CONSIDERATIONS**
   - Benchmark computation time for typical project sizes
   - Ensure <2 second computation time per S-034's layout timing requirement
   - Consider caching strategies if needed (while maintaining query-time freshness)

### Medium Priority

6. **REFACTOR EXISTING CODE**
   - Extract shared expansion logic from `src/jig/validation/bricks.py`
   - Create reusable utilities to avoid code duplication
   - Ensure consistency between validation and query-time expansion

7. **ADD VALIDATION INTEGRATION**
   - Consider using S-022 validation results in query-time warnings
   - Ensure consistent error messages between validation and query-time checks

## Alignment Score

- **Outcome Alignment**: ALIGNED (Strong semantic contribution to O-010)
- **Implementation**: 0/9 criteria covered (0%)
- **Verification**: 0/9 criteria tested (0%)
- **Execution**: N/A (no implementations or tests)
- **Overall**: 0% (UNIMPLEMENTED)

## Critical Path

S-030 is on the critical path for O-010 delivery:

```
S-030 (Compute Membership)
  ↓
S-031 (Render Compound Nodes) → depends on S-030 membership map
  ↓
S-034 (Layout Support) → depends on S-031 compound structure
  ↓
O-010 (Visualize Bricks) → BLOCKED until S-030 implemented
```

**Recommendation**: Prioritize S-030 implementation immediately to unblock the visualization outcome.
