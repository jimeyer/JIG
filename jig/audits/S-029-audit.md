# Specification Audit: S-029

**Date**: 2025-12-07
**Auditor**: Claude (Automated Audit)

## Summary

- **Specification**: Multi-Graph Loading in Visualizer
- **Alignment Status**: UNIMPLEMENTED
- **Outcome Alignment**: ALIGNED
- **Upstream Outcome**: O-007 (Visual Inspection of Graphs)
- **Implementing Functions**: 0
- **Verifying Tests**: 0

## Specification Review

**Quality Assessment: HIGH QUALITY**

- **ID Format**: Correct (`S-029` matching `S-NNN` pattern)
- **Required Fields**: Present (`id`, `type: specification`)
- **Clear Intent**: YES - Specifies multi-graph loading capability for visualizer
- **Testable Criteria**: YES - 9 specific, concrete acceptance criteria
- **Precise Language**: Good use of MUST keyword, clear rationale linking to brick visualization

**Acceptance Criteria**:
1. Load intent-graph.ndjson with spec, outcome, brick nodes
2. Load implementation-graph.ndjson with function, class, module nodes
3. Load both graphs simultaneously without conflicts
4. Auto-detect graph type from node types
5. Support multiple loaded graphs with distinct storage
6. UI provides graph selection controls (checkboxes)
7. Auto-load attempts default graphs from `../jig/generated/`
8. Error handling for missing/malformed graphs
9. Console logs indicate successful graph loads

## Outcome Alignment

**Linked Outcome**: O-007 - Visual Inspection of Graphs

**Outcome Goal**: Enable developers to visually inspect implementation, intent, and verification graphs to understand codebase architecture and intent alignment.

**Sibling Specs**:

| Sibling Spec | Title | Status | Contributes To Outcome |
|--------------|-------|--------|------------------------|
| S-007 | Parse NDJSON Implementation Graph Format | PERFECT | Foundational parsing for single graph |
| S-008 | Render Nodes Distinguished by Type | PERFECT | Visual distinction of graph elements |
| S-009 | Render Edges Distinguished by Type | PERFECT | Visual distinction of relationships |
| S-017 | Load NDJSON File from Filesystem | PERFECT | File loading mechanism |
| S-015 | Support Zoom and Pan Navigation | PERFECT | Graph navigation |
| S-016 | Switch Between Layout Algorithms | PERFECT | Graph layout controls |
| S-029 | Multi-Graph Loading in Visualizer | UNIMPLEMENTED | **Multiple graph type support** |

**Contribution Assessment**: S-029 is CRITICAL to O-007's stated goal. The outcome explicitly requires:
- "Developers can load multiple graph types (intent, implementation, verification) simultaneously"
- "Graph accurately reflects current codebase structure from generated NDJSON"

Without S-029, the visualizer can only show one graph at a time, preventing the comprehensive system understanding promised by O-007.

### Outcome Coverage Analysis

O-007 is mostly complete (6/7 specs implemented), but S-029's absence is a significant gap. The outcome's acceptance criteria explicitly states: "Developers can load multiple graph types (intent, implementation, verification) simultaneously" - this cannot be achieved without S-029.

**Gap**: The current visualizer (as evidenced by `/Users/jamesmeyer/Code/jig/viz/js/main.js`) only supports loading a single graph. The state object has a single `graph` property, not multiple graph storage. No UI controls exist for selecting between graph types.

## Implementation Analysis

**No implementations found.**

### Expected Implementation Locations

Based on the V003 plan and current architecture:

1. **Multi-graph state management** (in `viz/js/main.js`):
   - Replace `state.graph` with `state.graphs = { intent: null, impl: null, verify: null }`
   - Add brick extraction logic from intent graph

2. **Multi-graph loading** (in `viz/js/graph-loader.js`):
   - Function to load multiple files simultaneously
   - Graph type auto-detection from node types
   - Merge/combine graphs for rendering

3. **UI controls** (in `viz/index.html`):
   - Checkboxes for Intent/Implementation/Verification graph selection
   - Visual indicators of which graphs are loaded

4. **Auto-load logic** (in `viz/js/main.js`):
   - Attempt to load `../jig/generated/intent-graph.ndjson`
   - Attempt to load `../jig/generated/implementation-graph.ndjson`
   - Attempt to load `../jig/generated/verification-graph.ndjson` (future)

### Missing Implementation

All 9 acceptance criteria lack implementation:
- No multi-graph state storage
- No graph type detection
- No UI controls for graph selection
- Auto-load only attempts single graph (`implementation-graph.ndjson`)
- No distinct storage for multiple graphs

## Verification Analysis

**No verifying tests found.**

### Missing Verification

All 9 acceptance criteria lack test coverage:
1. Intent-graph loading with spec/outcome/brick nodes
2. Implementation-graph loading with function/class/module nodes
3. Simultaneous loading without conflicts
4. Graph type auto-detection logic
5. Multi-graph state management
6. UI controls for graph selection
7. Auto-load behavior for default graphs
8. Error handling for missing/malformed graphs
9. Console logging of successful loads

## Coverage Analysis

**N/A** - No implementations or tests exist.

### Verification Gaps

Complete verification gap. When implemented, tests should verify:
- Multi-graph loading functions execute correctly
- State management handles multiple graphs
- UI controls trigger correct loading behavior
- Auto-load falls back gracefully when graphs missing

## Recommendations

### Critical Priority

1. **Implement multi-graph state management**: Update `state` object in `main.js` to support multiple graphs as planned in V003 Work Unit 2.

2. **Add graph type detection**: Implement logic to detect whether loaded NDJSON contains intent nodes (spec/outcome/brick), implementation nodes (function/class/module), or verification nodes (test).

3. **Create UI controls**: Add checkboxes to header for Intent/Implementation/Verification graph selection.

4. **Update auto-load logic**: Modify `tryLoadDefaultGraph()` to attempt loading all three graph types from `../jig/generated/`.

5. **Write comprehensive tests**: Create test suite covering all 9 acceptance criteria, especially:
   - Multi-graph loading without conflicts
   - Graph type detection accuracy
   - State isolation between graphs

### High Priority

6. **Add `@jig.implements("S-029")` decorator**: Once implemented, annotate relevant functions with decorator for traceability.

7. **Enhance error handling**: Implement graceful degradation when one or more graphs are missing.

8. **Document multi-graph workflow**: Update viz/README.md with instructions for generating and loading multiple graphs.

### Medium Priority

9. **Add RFC 2119 keywords**: Change "MUST" to "SHALL" for consistency with JIG standards.

10. **Clarify conflict resolution**: Specify behavior when intent-graph and impl-graph contain nodes with same ID.

## Alignment Score

- **Outcome Alignment**: ALIGNED (critical contribution to O-007)
- **Implementation**: 0/9 criteria covered (0%)
- **Verification**: 0/9 criteria tested (0%)
- **Execution**: 0/0 test-function pairs (N/A)
- **Overall**: 0%

## Notes

**Context from V003 Plan**: This specification is part of V003 Work Unit 2 ("Multi-Graph Loading in Viz"), which has planned effort of 2 hours. The detailed implementation plan exists in `/Users/jamesmeyer/Code/jig/docs/viz/V003_PLAN_Brick_Graph_Visualizer.md`.

**Rationale**: S-029 is prerequisite for brick visualization per A001 §6.2. The architecture requires:
1. Intent graph contains brick definitions with units
2. Implementation graph contains pure code structure
3. Visualizer computes brick membership at query time by joining both graphs

**No implementation exists yet** because V003 WU2 has not been started (checklist shows unchecked).

**Current State**: The visualizer in `/Users/jamesmeyer/Code/jig/viz/` only supports single-graph loading. The `state` object has `graph` (singular), not `graphs` (plural). The HTML has no graph selection controls.

**Next Steps**: Follow V003 WU2 implementation plan to achieve PERFECT alignment status.
