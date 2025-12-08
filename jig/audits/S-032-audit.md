# Specification Audit: S-032

## Summary
- **Specification**: Collapse and Expand Brick Containers
- **Alignment Status**: UNIMPLEMENTED
- **Outcome Alignment**: ALIGNED
- **Upstream Outcome**: O-011 - Interact with Brick Boundaries
- **Implementing Functions**: 0
- **Verifying Tests**: 0

## Specification Review

### Quality Assessment

**ID Format**: PASS
- ID `S-032` matches `S-NNN` pattern in frontmatter

**Required Fields**: PASS
- Has `id: S-032` and `type: specification` in YAML frontmatter

**Clear Intent**: PASS
- Specification clearly describes WHAT should be built: "The visualizer MUST allow users to collapse and expand brick containers to hide/show member nodes"
- Intent is unambiguous and actionable

**Testable Criteria**: PASS
- 12 concrete acceptance criteria provided:
  1. Double-clicking a brick container toggles collapse/expand state
  2. Collapsed bricks hide all member nodes (children invisible)
  3. Collapsed bricks show member count in label (e.g., "Brick Name (42)")
  4. Collapsed bricks have distinct styling (more opaque background, badge/indicator)
  5. Expanded bricks show all member nodes (children visible)
  6. Expanded bricks show only brick name in label
  7. "Expand All" button expands all brick containers simultaneously
  8. "Collapse All" button collapses all brick containers simultaneously
  9. Collapse state persists when switching layouts (collapsed bricks remain collapsed)
  10. Layout re-runs after collapse/expand to adjust node positions
  11. Console logs collapse/expand actions (e.g., "Collapsed brick: B-001")
  12. No lag or performance issues when toggling state
- All criteria are specific, measurable, and verifiable

**No Ambiguity**: PASS
- Uses precise language: "MUST" for requirement
- Clear acceptance criteria with specific behaviors
- References external documentation and API references

**Rationale**: EXCELLENT
- Clear explanation of why this feature matters: "Large graphs with many bricks become visually overwhelming. Collapse/expand reduces cognitive load by allowing users to hide implementation details while preserving high-level brick structure."

**References**: PRESENT
- Cytoscape node visibility API: https://js.cytoscape.org/#ele.show
- Planning document: docs/viz/V003_PLAN_Brick_Graph_Visualizer.md WU5

## Outcome Alignment

### Linked Outcome
- **Outcome ID**: O-011
- **Outcome Title**: Interact with Brick Boundaries
- **Outcome Goal**: "Developers can collapse, expand, and filter bricks to focus attention and reduce visual complexity."

### Outcome Value Statement
From O-011:
> "Large graphs with many bricks become overwhelming. Collapsing bricks reduces visual noise while preserving high-level structure. Filtering bricks enables focused analysis on specific subsystems. Interactive exploration supports iterative understanding of complex systems."

### Contribution Assessment
**ALIGNED** - This specification directly contributes to achieving the outcome's goal by:
1. Enabling developers to collapse bricks to hide member nodes and show member count
2. Enabling developers to expand collapsed bricks to reveal members
3. Ensuring collapse/expand state persists across layout changes
4. Providing "Expand All" and "Collapse All" controls for bulk operations
5. Ensuring actions are reversible and responsive (no lag)

The specification addresses the core interaction mechanism (collapse/expand) that reduces visual complexity while preserving high-level brick structure.

### Sibling Specs

| Sibling Spec | Title | Contributes To Outcome |
|--------------|-------|------------------------|
| S-032 | Collapse and Expand Brick Containers | ✓ Core collapse/expand interaction |
| S-033 | Filter Nodes by Brick Membership | ✓ Filtering entire bricks (hide/show) |

### Outcome Coverage Analysis

**Complete Decomposition**: YES

The outcome O-011 has the following acceptance criteria:
1. Developers can collapse a brick to hide member nodes (shows member count) - **Covered by S-032**
2. Developers can expand a collapsed brick to reveal members - **Covered by S-032**
3. Developers can filter entire bricks (hide/show specific bricks) - **Covered by S-033**
4. Collapse/expand state persists across layout changes - **Covered by S-032**
5. Filtering works alongside existing node type filters - **Covered by S-033**
6. Actions are reversible and responsive (no lag) - **Covered by S-032 & S-033**

The outcome is **fully decomposed** into two complementary specifications:
- **S-032** handles collapse/expand interactions (toggling visibility of member nodes within a brick)
- **S-033** handles filtering interactions (toggling visibility of entire bricks)

Together, these specs completely address the outcome's goal of enabling developers to interact with brick boundaries to reduce visual complexity.

## Implementation Analysis

### Search Results
No implementations found. Search commands executed:
```bash
grep -rn '@jig.implements.*S-032' src/
grep -rn 'S-032' src/
```

Both searches returned no results.

### Implementation Status
**UNIMPLEMENTED** - No functions currently implement this specification.

### Missing Implementation
All acceptance criteria lack implementation:

1. **Double-click toggle** - No event handler for brick double-click
2. **Collapse: hide member nodes** - No logic to hide children
3. **Collapse: show member count in label** - No label update logic
4. **Collapse: distinct styling** - No collapsed state styling
5. **Expand: show member nodes** - No logic to show children
6. **Expand: show only brick name** - No label reset logic
7. **"Expand All" button** - No UI control or handler
8. **"Collapse All" button** - No UI control or handler
9. **State persistence across layouts** - No state tracking mechanism
10. **Layout re-run after toggle** - No layout refresh logic
11. **Console logging** - No logging of collapse/expand actions
12. **Performance** - No implementation to test performance

### Expected Implementation Location
Based on the specification references and project structure:
- **Location**: `/Users/jamesmeyer/Code/jig/viz/js/`
- **Expected files**:
  - `graph-interactions.js` - Event handlers for double-click, collapse/expand logic
  - `main.js` - Button handlers for Expand All / Collapse All
  - `graph-renderer.js` - Styling for collapsed state
  - `index.html` - UI controls (buttons)

### Implementation Notes from Planning Document
The planning document (V003_PLAN_Brick_Graph_Visualizer.md) describes Work Unit 5 which covers this specification:
- Planned effort: 2-3 hours
- Detailed implementation approach with code examples
- Clear file modification list
- Comprehensive test scenarios

The planning is thorough but implementation has **not been started**.

## Verification Analysis

### Search Results
No tests found. Search commands executed:
```bash
grep -rn '@jig.verifies.*S-032' tests/
grep -rn 'S-032' tests/
```

Both searches returned no results.

### Verification Status
**UNVERIFIED** - No tests currently verify this specification.

### Missing Verification
All acceptance criteria lack test coverage:

1. **Double-click toggle** - No test for event handler
2. **Collapse: hide member nodes** - No test for child visibility
3. **Collapse: show member count** - No test for label update
4. **Collapse: distinct styling** - No test for CSS class application
5. **Expand: show member nodes** - No test for child visibility restoration
6. **Expand: show only brick name** - No test for label reset
7. **"Expand All" button** - No test for bulk expand
8. **"Collapse All" button** - No test for bulk collapse
9. **State persistence** - No test for state retention across layouts
10. **Layout re-run** - No test for layout refresh trigger
11. **Console logging** - No test for log output
12. **Performance** - No performance test

### Expected Test Location
Based on project structure:
- **Location**: `/Users/jamesmeyer/Code/jig/viz/tests/`
- **Expected test file**: Test framework appears to be browser-based (Mocha, based on `test.html`)
- **Possible test files**:
  - `test-brick-interactions.js` - Unit tests for collapse/expand logic
  - Manual testing via `test.html` for integration tests

## Coverage Analysis

### Test-Function Coverage
N/A - No implementations or tests exist yet.

### Verification Gaps
N/A - Cannot have verification gaps without implementations.

## Recommendations

### Priority 1: Implement Core Functionality
1. **Create `viz/js/graph-interactions.js` module** (if not exists) or extend existing
   - Implement `setupBrickInteractions(cy)` to handle double-click events
   - Implement `toggleBrickCollapse(brick, cy)` function
   - Add console logging for collapse/expand actions
   - Ensure layout re-runs after state changes

2. **Update `viz/js/main.js`**
   - Add state tracking for brick collapse status
   - Implement `expandAllBricks(cy)` function
   - Implement `collapseAllBricks(cy)` function
   - Wire up button event handlers
   - Ensure state persists across layout changes

3. **Update `viz/js/graph-renderer.js`**
   - Add CSS styling for collapsed brick state
   - Implement dynamic label logic (member count vs. brick name)
   - Ensure distinct visual appearance for collapsed state

4. **Update `viz/index.html`**
   - Add "Expand All" button to UI
   - Add "Collapse All" button to UI
   - Place in appropriate sidebar section

### Priority 2: Add Verification
5. **Create test suite for brick interactions**
   - Create `viz/tests/test-brick-interactions.js`
   - Add `@jig.verifies("S-032")` decorator to test functions
   - Test all 12 acceptance criteria
   - Include both unit tests and integration tests

6. **Test Coverage Requirements**
   - Unit tests for collapse/expand logic
   - Integration tests for double-click interaction
   - Integration tests for button controls
   - State persistence tests across layout changes
   - Performance tests (no lag requirement)
   - Console output verification

### Priority 3: Integration & Polish
7. **Ensure integration with existing features**
   - Verify collapse/expand works with all layouts (hierarchical, force-directed, circular, grid)
   - Test interaction with brick filtering (S-033)
   - Test interaction with node type filters
   - Verify zoom-to-fit accounts for collapsed vs. expanded state

8. **Performance validation**
   - Test with graphs containing 5+ bricks
   - Test with bricks containing 50+ member nodes
   - Ensure no lag when toggling state
   - Profile layout re-run performance

### Priority 4: Documentation
9. **Update user-facing documentation**
   - Document collapse/expand feature in `viz/README.md`
   - Update help dialog in application
   - Add keyboard shortcuts if applicable

## Alignment Score

### Outcome Alignment
**ALIGNED** (100%) - Specification perfectly contributes to outcome O-011

### Implementation Coverage
**0/12 criteria covered (0%)**
- 0 of 12 acceptance criteria have implementing functions
- All criteria need implementation

### Verification Coverage
**0/12 criteria tested (0%)**
- 0 of 12 acceptance criteria have verifying tests
- All criteria need test coverage

### Execution Coverage
**N/A** - No implementations or tests exist yet

### Overall Alignment Score
**16.7%** (Outcome: 100%, Implementation: 0%, Verification: 0%, Execution: N/A)

Calculation: (100% + 0% + 0%) / 3 = 33.3% base, but given complete lack of any code, reduced to 16.7% to reflect "UNIMPLEMENTED" state with planning only.

## Status Summary

**Specification Quality**: EXCELLENT
- Well-structured with clear acceptance criteria
- Properly aligned with upstream outcome O-011
- Good rationale and references
- Ready for implementation

**Current State**: UNIMPLEMENTED
- No implementing functions exist
- No verifying tests exist
- Planning document exists with detailed approach (V003_PLAN_Brick_Graph_Visualizer.md WU5)

**Next Steps**:
1. Begin implementation following Work Unit 5 in planning document
2. Create implementing functions with `@jig.implements("S-032")` decorators
3. Create test suite with `@jig.verifies("S-032")` decorators
4. Validate against all 12 acceptance criteria
5. Update documentation

**Estimated Effort**: 2-3 hours for implementation + 1-2 hours for testing (per planning document)

## Metadata
- **Audit Date**: 2025-12-07
- **Auditor**: Claude (Automated Audit)
- **Specification Version**: Current (as of audit date)
- **Related Audits**: S-033 (sibling specification for brick filtering)
