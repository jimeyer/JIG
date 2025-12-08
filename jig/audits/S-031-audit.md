# Specification Audit: S-031

## Summary
- **Specification**: Render Bricks as Cytoscape Compound Nodes
- **Alignment Status**: UNIMPLEMENTED
- **Outcome Alignment**: ALIGNED
- **Upstream Outcome**: O-010 (Visualize Bricks as Compound Nodes)
- **Implementing Functions**: 0
- **Verifying Tests**: 0

## Specification Review

### Quality Assessment
- **ID Format**: Valid - `S-031` matches `S-NNN` pattern in frontmatter
- **Required Fields**: Present - has `id: S-031` and `type: specification` in YAML frontmatter
- **Clear Intent**: Excellent - specification clearly describes rendering bricks as Cytoscape compound nodes with computed parent-child relationships
- **Testable Criteria**: Strong - 10 specific acceptance criteria covering:
  - Cytoscape node element creation from intent graph
  - Parent field assignment from computed membership
  - Visual styling (rectangles, semi-transparent background, borders)
  - Label positioning and typography (text-valign: top, font-size: 16px, bold)
  - Member node positioning and styling
  - Memory-only parent assignment (no disk modification)
  - Console confirmation logging
- **No Ambiguity**: Excellent - uses MUST directive and provides concrete technical specifications including CSS properties and Cytoscape-specific syntax
- **References**: Well-documented - includes Cytoscape compound nodes documentation, A001 §6.2 compliance, and V003 plan reference

### Specification Strengths
1. Highly detailed technical requirements with specific Cytoscape API syntax
2. Strong A001 compliance emphasis (no modification to NDJSON files on disk)
3. Clear visual design specifications (opacity, font size, positioning)
4. Observable behavior (console logging for verification)
5. Rationale explains architectural reasoning (native grouping, A001 compliance)

### Specification Weaknesses
None identified - this is a well-crafted specification with clear, testable criteria.

## Outcome Alignment

### Linked Outcome
**O-010**: Visualize Bricks as Compound Nodes

**Outcome Goal**: Developers can see brick boundaries as visual containers around member implementation nodes in the graph visualizer. Makes brick architecture tangible and visible, helping developers understand code organization without reading YAML files.

**Outcome Value Statement**: "Makes brick architecture tangible and visible. Helps developers understand which code belongs to which brick without reading YAML files or memorizing boundaries. Reduces cognitive load when reasoning about brick alignment and cohesion."

### Sibling Specifications

| Sibling Spec | Title | Status | Contributes To Outcome |
|--------------|-------|--------|------------------------|
| S-030 | Compute Brick Membership at Query Time | UNIMPLEMENTED | Yes - provides data foundation for visualization |
| S-031 | Render Bricks as Cytoscape Compound Nodes | UNIMPLEMENTED | Yes - core rendering implementation |
| S-034 | Layout Algorithms Support Compound Nodes | UNIMPLEMENTED | Yes - ensures visualization works across layouts |

### Contribution Assessment
S-031 is the **core rendering specification** for O-010. It directly implements the visual representation of brick boundaries as compound nodes. This spec is essential to achieving the outcome's goal of making brick architecture visible.

**Semantic Alignment**: STRONG
- S-031 directly addresses "brick boundaries as visual containers" from outcome
- Visual styling criteria align with "clear visual boundaries (borders, background)" from outcome
- Member node positioning addresses "positioned inside brick boundaries" from outcome
- Compound node structure follows "Cytoscape conventions for consistency" from outcome

### Outcome Coverage Analysis

**Decomposition Assessment**: The outcome is **well-decomposed** across three complementary specifications:

1. **S-030** (Compute Brick Membership): Data layer - computes which nodes belong to which bricks at query time per A001 §6.2
2. **S-031** (Render Compound Nodes): Presentation layer - renders the visual representation using Cytoscape compound nodes
3. **S-034** (Layout Support): Integration layer - ensures all layout algorithms work with compound structure

**Coverage Completeness**: COMPLETE
- Data computation → S-030
- Visual rendering → S-031
- Layout integration → S-034

Together, these three specs fully address the outcome's goal. No gaps identified.

**Inter-Spec Dependencies**:
- S-031 depends on S-030 providing brick membership map (node ID → brick ID)
- S-034 depends on S-031 creating compound node structure
- Clear dependency chain: S-030 → S-031 → S-034

## Implementation Analysis

### Implementing Functions
No implementations found.

**Search Results**:
- `grep -rn '@jig.implements.*S-031' src/` → No results
- `grep -rn 'S-031' src/` → No results
- `grep -rn 'S-031' viz/` → No results (JavaScript visualization code)
- `grep -rn 'compound.*node|brick.*container' viz/` → No results

### Implementation Context
According to V003_PLAN_Brick_Graph_Visualizer.md:
- Work Unit 4 (WU4) is designated for "Compound Node Rendering" implementing S-031
- Planned implementation location: `viz/js/graph-renderer.js`
- Planned decorator: `@jig.implements("S-031")` in JavaScript code
- Status in plan: NOT STARTED (checkbox unchecked)

**Note**: This is a JavaScript/frontend visualization feature, not Python backend code.

### Missing Implementation
All 10 acceptance criteria lack implementation:

1. Create Cytoscape node elements for bricks from intent graph
2. Assign parent field to implementation nodes from computed membership
3. Brick nodes render as rectangles with visible borders
4. Brick nodes have semi-transparent background (background-opacity < 1)
5. Brick labels display at top of container (text-valign: 'top')
6. Brick labels use larger, bold font (font-size: 16px, font-weight: bold)
7. Member nodes positioned inside brick boundaries by layout engine
8. Member nodes styled distinctly (smaller size, normal font weight)
9. Compound node structure does NOT modify NDJSON files on disk
10. Console confirms compound structure created

**Expected Implementation Location**: `/Users/jamesmeyer/Code/jig/viz/js/graph-renderer.js`

**Expected Function Signature** (per V003 plan):
```javascript
/**
 * Create Cytoscape elements from multiple graphs with computed brick membership
 *
 * @jig.implements("S-031")
 */
export function createCompoundElements(intentGraph, implGraph, brickMembership) {
    // Implementation to create Cytoscape nodes and edges with parent relationships
}
```

## Verification Analysis

### Verifying Tests
No tests found.

**Search Results**:
- `grep -rn '@jig.verifies.*S-031' tests/` → No results
- `grep -rn 'S-031' tests/` → No results
- No test files exist for visualization components

### Missing Verification
All acceptance criteria lack test coverage:

| Criterion | Test Coverage | Notes |
|-----------|---------------|-------|
| Cytoscape node creation | None | Need visual/integration test |
| Parent field assignment | None | Need unit test for membership mapping |
| Rectangle rendering | None | Need visual verification |
| Background opacity | None | Need stylesheet assertion |
| Label positioning | None | Need stylesheet assertion |
| Font styling | None | Need stylesheet assertion |
| Layout positioning | None | Need integration test |
| Member styling | None | Need stylesheet assertion |
| No disk modification | None | Need file system assertion |
| Console logging | None | Need output verification |

**Expected Test Location**: `/Users/jamesmeyer/Code/jig/viz/tests/test-compound-rendering.js` (does not exist)

**Testing Challenges**:
- Frontend visualization testing requires browser environment
- Visual validation may require manual testing or screenshot comparison
- Cytoscape compound node behavior needs integration testing
- Console output verification needs capture mechanism

## Coverage Analysis

### Test-Function Coverage
N/A - No implementations or tests exist.

### Verification Gaps
Since neither implementations nor tests exist, there are no verification gaps in the traditional sense. However, once implemented, the following coverage challenges should be addressed:

1. **Visual Verification**: How to programmatically verify compound node rendering (borders, opacity, positioning)?
2. **Layout Integration**: How to test that Cytoscape layout engine respects compound structure?
3. **Memory-Only Assertion**: How to verify NDJSON files are never modified during visualization?

## Recommendations

### Priority 1: Implementation (Critical)
1. **Implement S-030 first** - S-031 depends on brick membership computation being available
   - Location: `viz/js/brick-membership.js`
   - Function: `expandBrickUnits()` to compute node → brick mapping
2. **Implement createCompoundElements()** in `viz/js/graph-renderer.js`
   - Add `@jig.implements("S-031")` decorator comment
   - Create brick nodes from intent graph
   - Assign parent field from computed membership
3. **Define Cytoscape stylesheet** for brick and member node styling
   - Brick container style: rectangle, opacity 0.05, border 3px, blue color
   - Brick label style: top-aligned, 16px, bold
   - Member style: smaller size, normal weight

### Priority 2: Verification (High)
4. **Create manual verification checklist** at minimum
   - Document visual verification steps from V003 plan WU4
   - Include console output verification
5. **Consider automated testing approach**:
   - Unit tests for element creation logic (can mock Cytoscape)
   - Integration tests using Cypress or Playwright for browser automation
   - Screenshot comparison for visual regression testing
6. **Add test file**: `viz/tests/test-compound-rendering.js`
   - Test element structure (parent field assignment)
   - Test stylesheet configuration
   - Test console logging output

### Priority 3: Architecture (Medium)
7. **Ensure A001 compliance verification**
   - Add explicit check that NDJSON files are not modified
   - Add file system watch or hash comparison test
8. **Document JavaScript decorator pattern**
   - JIG currently uses Python decorators (`@jig.implements`)
   - JavaScript uses comment-based annotations
   - Document in agents/audit-specification.md or similar

### Priority 4: Planning (Low)
9. **Update V003 plan** to reflect implementation status
10. **Consider demo/screenshot** for documentation once implemented

## Alignment Score

### Breakdown
- **Outcome Alignment**: ALIGNED (100%) - Spec strongly contributes to O-010's goal
- **Implementation**: 0/10 criteria covered (0%)
- **Verification**: 0/10 criteria tested (0%)
- **Execution**: N/A - no implementations or tests exist

### Overall Score: 0%

**Status**: UNIMPLEMENTED

**Interpretation**:
- This is a well-specified, outcome-aligned requirement that is **planned but not yet implemented**
- The specification quality is high (clear, testable, A001-compliant)
- Implementation is documented in V003 plan as Work Unit 4
- No code has been written yet
- This is expected for specifications created as "known intent before coding" per JIG methodology

## Next Steps

1. **Before implementing S-031**: Complete S-030 (brick membership computation) as it's a dependency
2. **Implementation path**: Follow V003 plan Work Unit 4 checklist
3. **Verification strategy**: Start with manual verification, add automated tests as feasible
4. **Integration**: Ensure compatibility with existing viz tool at `/Users/jamesmeyer/Code/jig/viz/`
5. **A001 compliance**: Maintain strict separation - no modifications to NDJSON files, all computation at query time

## References

- **Specification**: `/Users/jamesmeyer/Code/jig/jig/specifications/S-031.md`
- **Outcome**: `/Users/jamesmeyer/Code/jig/jig/outcomes/O-010.md`
- **Implementation Plan**: `/Users/jamesmeyer/Code/jig/docs/viz/V003_PLAN_Brick_Graph_Visualizer.md` (WU4)
- **A001 Compliance**: A001 §6.2 (no brick fields in implementation graph)
- **Visualization Tool**: `/Users/jamesmeyer/Code/jig/viz/`
- **Cytoscape Docs**: https://js.cytoscape.org/#notation/compound-nodes
