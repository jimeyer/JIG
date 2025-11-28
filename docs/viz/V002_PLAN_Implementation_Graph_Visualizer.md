# PLAN: Implementation Graph Visualizer

- **SCOPE**: [V001_PROPOSAL_Implementation_Graph_Visualizer.md](./V001_PROPOSAL_Implementation_Graph_Visualizer.md)
- **Start**: 2025-11-28
- **Status**: Draft
- **Branch**: minimal-jig

## Known Intent (Created Before Coding)

**Outcomes**:
- O-007: Developers can visually inspect implementation graph structure (jig/outcomes/O-007.md)
- O-008: Developers can discover relationships between code elements (jig/outcomes/O-008.md)

**Specifications**:
- S-007: Parse NDJSON implementation graph format (jig/specifications/S-007.md)
- S-008: Render nodes distinguished by type (jig/specifications/S-008.md)
- S-009: Render edges distinguished by type (jig/specifications/S-009.md)
- S-010: Filter nodes by type with real-time update (jig/specifications/S-010.md)
- S-011: Filter edges by type with real-time update (jig/specifications/S-011.md)
- S-012: Search nodes by name/ID with fuzzy matching (jig/specifications/S-012.md)
- S-013: Display node metadata when selected (jig/specifications/S-013.md)
- S-014: Display edge metadata when selected (jig/specifications/S-014.md)
- S-015: Support zoom and pan navigation (jig/specifications/S-015.md)
- S-016: Switch between layout algorithms (jig/specifications/S-016.md)
- S-017: Load NDJSON file from filesystem (jig/specifications/S-017.md)

**Bricks Affected**:
- None (standalone tool in viz/ folder)

## Work Unit Checklist

- [x] WU0: Create Intent nodes (O/S)
- [x] WU1: Scaffold — tests ✅ / code ✅ / docs ✅
- [x] WU2: Graph Loading — tests ✅ / code ✅ / docs ✅
- [x] WU3: Basic Rendering — tests ✅ / code ✅ / docs ✅
- [x] WU4: Interaction — tests ✅ / code ✅ / docs ✅
- [ ] WU5: Filtering — tests ☐ / code ☐ / docs ☐
- [ ] WU6: Search — tests ☐ / code ☐ / docs ☐
- [ ] WU7: Layout Switching — tests ☐ / code ☐ / docs ☐
- [ ] WU8: Polish — tests ☐ / code ☐ / docs ☐

## Work Units

### Work Unit 0: Create Known Intent

**Goal**: Capture all known Outcomes and Specifications from V001 proposal before writing any code.

**Acceptance Criteria**:
- [x] All known "why" statements → Outcome files in `jig/outcomes/`
- [x] All known "what" requirements → Specification files in `jig/specifications/`
- [x] All files have proper YAML frontmatter
- [x] `jigy validate` passes (validate command not yet implemented, but files follow standard format)
- [x] Sample graph created: `viz/tests/fixtures/sample-graph.ndjson`

**Created Nodes**:
- O-007: Visual inspection of implementation graph
- O-008: Discovery of code relationships
- S-007: NDJSON parsing
- S-008: Node rendering by type
- S-009: Edge rendering by type
- S-010: Node type filtering
- S-011: Edge type filtering
- S-012: Fuzzy search
- S-013: Node details display
- S-014: Edge details display
- S-015: Zoom and pan
- S-016: Layout switching
- S-017: File loading

**Reflect**:
- What was clear from SCOPE: Phase 1 scope is well-defined, Cytoscape.js choice is solid, feature list translates cleanly to specifications
- What was ambiguous: Testing strategy for browser-based code (resolved: browser tests for logic, manual for UI)
- Surprises: Sample graph needed async function example - added synthetic node for completeness
- Process win: Creating all intent upfront clarifies scope and enables test-driven development

**Links**:
- Commit: df235d9

---

### Work Unit 1: Scaffold

**Goal**: Create basic HTML structure and confirm Cytoscape.js loads

**Planned Effort**: 60 minutes

**Acceptance Criteria**:
- [x] File structure created (`viz/index.html`, `viz/css/`, `viz/js/`)
- [x] Cytoscape.js loads from CDN
- [x] Basic layout renders (header, sidebar, canvas, details panel)
- [x] Page opens in browser without errors
- [x] Test infrastructure works (`viz/tests/test.html` runs)

**Implementation Notes**:
- Approach:
  1. Create folder structure per proposal
  2. Basic `index.html` with three-column layout
  3. Load Cytoscape.js, Mocha, Chai from CDN
  4. Create empty JS module files
  5. Create test.html with Mocha setup
- Files:
  - `viz/index.html` - Main application
  - `viz/css/layout.css` - Page structure
  - `viz/js/main.js` - App initialization (empty)
  - `viz/tests/test.html` - Test runner
  - `viz/README.md` - Usage instructions

**Test Plan**:
- Manual: Open `index.html` in browser, confirm no console errors
- Manual: Open `tests/test.html`, confirm Mocha loads

**Docs Updated**:
- `viz/README.md` - Basic usage instructions

**Reflect**:
- What worked well: CSS custom properties made theming consistent, three-column layout works cleanly, CDN-based libraries avoid build complexity
- What could be better: Could add dark mode support in future, mobile responsiveness is basic
- Surprises/discoveries: Cytoscape.js is a larger library than expected (3.28.1), but necessary for graph features
- Risks identified: No offline mode (CDN dependency), browser compatibility not tested across all browsers

**Links**:
- Commit: 4c33dbe

---

### Work Unit 2: Graph Loading

**Goal**: Parse NDJSON and convert to Cytoscape elements

**Planned Effort**: 90 minutes

**Implements**: S-007 (NDJSON parsing), S-017 (File loading)

**Acceptance Criteria**:
- [x] S-007 is implemented by `parseNDJSON()` function
- [x] S-017 is implemented by `loadGraphFile()` function
- [x] Tests verify parsing of metadata line
- [x] Tests verify parsing of node lines
- [x] Tests verify parsing of edge lines
- [x] Tests verify Cytoscape elements structure
- [x] Manual test: Load sample-graph.ndjson shows elements in console

**Implementation Notes**:
- Approach:
  1. Create sample-graph.ndjson (10 nodes, 10 edges from real graph)
  2. Implement `parseNDJSON()` - split lines, parse JSON
  3. Implement `toCytoscapeElements()` - transform to Cytoscape format
  4. Implement `loadGraphFile()` - file input handler
  5. Wire up to file picker in UI
- Files:
  - `viz/js/graph-loader.js` - Parsing logic
  - `viz/tests/fixtures/sample-graph.ndjson` - Test data
  - `viz/tests/test-loader.js` - Parser tests
- Decorators added:
  - `// @jig.implements("S-007")` on parseNDJSON
  - `// @jig.implements("S-017")` on loadGraphFile

**Test Plan**:
- Browser tests in `test-loader.js`:
  - Parse valid NDJSON → returns metadata, nodes, edges
  - Parse metadata line → extracts node_count, edge_count, version
  - Parse node line → creates Cytoscape node with correct data
  - Parse edge line → creates Cytoscape edge with source/target
  - Handle empty input → returns empty arrays
  - Handle malformed JSON → throws descriptive error
- Manual: Load sample graph, inspect console output

**Docs Updated**:
- `viz/README.md` - Document NDJSON format expectations (already documented in WU1)

**Reflect**:
- What worked well: NDJSON parsing is straightforward, FileReader API works well, comprehensive test coverage (18 tests), Cytoscape elements transform is clean
- What could be better: Error messages could be more specific about what's wrong with malformed data
- Surprises/discoveries: Need to filter out empty lines in NDJSON, edge IDs need to be unique (using source-target-type pattern)
- Risks identified: Large files might be slow to parse (no streaming yet), no validation that source/target nodes exist for edges

**Links**:
- Commit: 1f2c4b2

---

### Work Unit 3: Basic Rendering

**Goal**: Render graph with styled nodes and edges

**Planned Effort**: 90 minutes

**Implements**: S-008 (Node rendering), S-009 (Edge rendering)

**Acceptance Criteria**:
- [x] S-008 is implemented by `renderGraph()` with node styling
- [x] S-009 is implemented by `renderGraph()` with edge styling
- [x] Classes render as rectangles
- [x] Functions render as circles
- [x] Modules render as rounded rectangles
- [x] External modules have different color
- [x] Contains edges are thick solid lines
- [x] Implements edges are dashed lines
- [x] Imports edges are thin lines
- [x] Hierarchical layout applied by default
- [x] Manual test: Sample graph renders visually

**Implementation Notes**:
- Approach:
  1. Implement `renderGraph()` in graph-renderer.js
  2. Define Cytoscape stylesheet (node shapes, colors, edge styles)
  3. Apply hierarchical layout
  4. Initialize Cytoscape instance on page load
- Files:
  - `viz/js/graph-renderer.js` - Rendering logic
  - `viz/js/main.js` - Initialize on page load
  - `viz/css/graph.css` - Graph container styles
- Decorators added:
  - `// @jig.implements("S-008", "S-009")` on renderGraph

**Test Plan**:
- Manual testing only (visual verification):
  - Load sample graph
  - Confirm classes are rectangles
  - Confirm functions are circles
  - Confirm modules are rounded rectangles
  - Confirm edge styles differ (contains/implements/imports)
  - Confirm layout is hierarchical

**Docs Updated**:
- `viz/README.md` - Add screenshot or description of visual output (no changes needed - visual only)

**Reflect**:
- What worked well: Cytoscape.js stylesheet is powerful and intuitive, breadthfirst layout works great for hierarchical graphs, visual distinction between node types is clear, edge styling makes relationship types obvious
- What could be better: Could add more layout options (dagre for better DAG layout), node labels could be smarter about truncation
- Surprises/discoveries: Nodes with `implements` field get special highlighting (thicker red border) to show intent connections, bezier curves look better than straight lines for edges, animate option on layouts provides nice transitions
- Risks identified: Performance with 100+ nodes not yet tested, overlapping labels on dense graphs

**Links**:
- Commit: f417127

---

### Work Unit 4: Interaction

**Goal**: Click nodes/edges to see details, zoom and pan

**Planned Effort**: 90 minutes

**Implements**: S-013 (Node details), S-014 (Edge details), S-015 (Zoom/pan)

**Acceptance Criteria**:
- [x] S-013 is implemented by node click handler
- [x] S-014 is implemented by edge click handler
- [x] S-015 is implemented by Cytoscape zoom/pan config
- [x] Click node → details panel shows node metadata
- [x] Click edge → details panel shows edge metadata
- [x] Mouse wheel zooms graph
- [x] Click-drag pans graph
- [x] "Zoom to Fit" button works
- [x] Manual test: All interactions work smoothly

**Implementation Notes**:
- Approach:
  1. Implement `showNodeDetails()` in details-panel.js
  2. Implement `showEdgeDetails()` in details-panel.js
  3. Implement click handlers in graph-interactions.js
  4. Configure Cytoscape pan/zoom settings
  5. Add "Zoom to Fit" button
- Files:
  - `viz/js/graph-interactions.js` - Click/hover handlers
  - `viz/js/details-panel.js` - Details rendering
  - `viz/css/controls.css` - Button styles
- Decorators added:
  - `// @jig.implements("S-013")` on showNodeDetails
  - `// @jig.implements("S-014")` on showEdgeDetails
  - `// @jig.implements("S-015")` on Cytoscape config

**Test Plan**:
- Manual testing only (interaction verification):
  - Click class node → see id, type, name, file, line, bases, implements
  - Click function node → see id, type, name, signature, parent_class
  - Click module node → see id, type, name, file
  - Click edge → see source, target, type, line
  - Zoom in/out with mouse wheel
  - Pan with click-drag
  - Click "Zoom to Fit" → graph fits viewport

**Docs Updated**:
- `viz/README.md` - Document interaction controls (no changes needed - already documented in WU1)

**Reflect**:
- What worked well: Cytoscape's event system is clean and easy to use, details panel updates instantly on click, highlighting connected elements provides good visual feedback, zoom controls work smoothly, HTML escaping prevents XSS in details panel
- What could be better: Could add double-click to center on node, could add hover tooltips for quick info without clicking, details panel could be collapsible on mobile
- Surprises/discoveries: Need to distinguish between tapping background vs elements (event.target === cy), highlighting class needs both .highlighted selector and removal of previous highlights, Cytoscape handles pan/zoom natively with good defaults
- Risks identified: Long signatures or file paths might overflow details panel on narrow screens, clicking rapidly can queue up multiple detail updates

**Links**:
- Commit: f961d36

---

### Work Unit 5: Filtering

**Goal**: Filter nodes and edges by type

**Planned Effort**: 90 minutes

**Implements**: S-010 (Node filtering), S-011 (Edge filtering)

**Acceptance Criteria**:
- [ ] S-010 is implemented by `filterNodesByType()` function
- [ ] S-011 is implemented by `filterEdgesByType()` function
- [ ] Tests verify node filtering logic
- [ ] Tests verify edge filtering logic
- [ ] Node type checkboxes (Classes, Functions, Modules, External)
- [ ] Edge type checkboxes (Contains, Implements, Imports)
- [ ] Unchecking checkbox hides nodes/edges in real-time
- [ ] Re-checking checkbox shows nodes/edges again
- [ ] Manual test: Filtering works smoothly

**Implementation Notes**:
- Approach:
  1. Implement `filterNodesByType()` in filters.js
  2. Implement `filterEdgesByType()` in filters.js
  3. Add checkboxes to sidebar
  4. Wire up checkbox change handlers
  5. Update Cytoscape graph on filter change
- Files:
  - `viz/js/filters.js` - Filtering logic
  - `viz/index.html` - Add filter checkboxes
  - `viz/tests/test-filters.js` - Filter tests
- Decorators added:
  - `// @jig.implements("S-010")` on filterNodesByType
  - `// @jig.implements("S-011")` on filterEdgesByType

**Test Plan**:
- Browser tests in `test-filters.js`:
  - `// @jig.verifies("S-010")` - Filter nodes by type
    - Input: nodes array, types=['class'] → returns only class nodes
    - Input: nodes array, types=[] → returns empty array
    - Input: nodes array, types=['class', 'function'] → returns both
  - `// @jig.verifies("S-011")` - Filter edges by type
    - Input: edges array, types=['contains'] → returns only contains edges
    - Input: edges array, types=[] → returns empty array
    - Input: edges array, types=['implements', 'imports'] → returns both
- Manual: Uncheck "Classes" → classes disappear, check again → reappear

**Docs Updated**:
- `viz/README.md` - Document filter controls

**Reflect**:
- What worked well:
- What could be better:
- Surprises/discoveries:
- Risks identified:

**Links**:
- Commit:

---

### Work Unit 6: Search

**Goal**: Fuzzy search for nodes by name/ID

**Planned Effort**: 60 minutes

**Implements**: S-012 (Fuzzy search)

**Acceptance Criteria**:
- [ ] S-012 is implemented by `searchNodes()` function
- [ ] Tests verify search logic
- [ ] Search input field in sidebar
- [ ] Type query → matching nodes highlighted
- [ ] Click search result → selects node
- [ ] Clear search → removes highlights
- [ ] Manual test: Search works for partial matches

**Implementation Notes**:
- Approach:
  1. Implement `searchNodes()` using Fuse.js in search.js
  2. Add search input to sidebar
  3. Wire up input change handler
  4. Highlight matching nodes in graph
  5. Show results list below search box
- Files:
  - `viz/js/search.js` - Search logic
  - `viz/index.html` - Add search input
  - `viz/tests/test-search.js` - Search tests
- Decorators added:
  - `// @jig.implements("S-012")` on searchNodes

**Test Plan**:
- Browser tests in `test-search.js`:
  - `// @jig.verifies("S-012")` - Fuzzy search
    - Input: nodes, query="TokenVal" → finds "TokenValidator" class
    - Input: nodes, query="jig.impl" → finds module "jig.impl_graph"
    - Input: nodes, query="xyz" → returns empty array
    - Input: nodes, query="" → returns all nodes
- Manual: Type "Token" → see TokenValidator highlighted

**Docs Updated**:
- `viz/README.md` - Document search functionality

**Reflect**:
- What worked well:
- What could be better:
- Surprises/discoveries:
- Risks identified:

**Links**:
- Commit:

---

### Work Unit 7: Layout Switching

**Goal**: Switch between layout algorithms

**Planned Effort**: 60 minutes

**Implements**: S-016 (Layout switching)

**Acceptance Criteria**:
- [ ] S-016 is implemented by `applyLayout()` function
- [ ] Layout dropdown in sidebar
- [ ] Options: Hierarchical, Force-directed, Circular, Grid
- [ ] Select layout → graph re-layouts smoothly
- [ ] Layout persists (doesn't reset on interaction)
- [ ] Manual test: All layouts work

**Implementation Notes**:
- Approach:
  1. Implement `applyLayout()` in layout-manager.js
  2. Add layout dropdown to sidebar
  3. Wire up dropdown change handler
  4. Configure Cytoscape layout options for each type
- Files:
  - `viz/js/layout-manager.js` - Layout logic
  - `viz/index.html` - Add layout dropdown
- Decorators added:
  - `// @jig.implements("S-016")` on applyLayout

**Test Plan**:
- Manual testing only (visual verification):
  - Select "Hierarchical" → top-down tree layout
  - Select "Force-directed" → organic clustering
  - Select "Circular" → nodes in circle
  - Select "Grid" → organized rows/columns

**Docs Updated**:
- `viz/README.md` - Document layout options

**Reflect**:
- What worked well:
- What could be better:
- Surprises/discoveries:
- Risks identified:

**Links**:
- Commit:

---

### Work Unit 8: Polish

**Goal**: Error handling, loading states, responsive design

**Planned Effort**: 90 minutes

**Acceptance Criteria**:
- [ ] File load errors show user-friendly message
- [ ] Invalid NDJSON shows line number in error
- [ ] Empty graph shows "No nodes found" message
- [ ] Loading spinner while parsing large graphs
- [ ] Responsive design (works on different screen sizes)
- [ ] Statistics panel shows node/edge counts, timestamp
- [ ] Help documentation (modal or README link)
- [ ] Manual test: All error cases handled gracefully

**Implementation Notes**:
- Approach:
  1. Add error handling to graph-loader.js
  2. Add loading spinner to UI
  3. Add statistics panel to header
  4. Add help button/modal
  5. CSS media queries for responsive layout
  6. Test with various invalid inputs
- Files:
  - `viz/js/graph-loader.js` - Enhanced error handling
  - `viz/index.html` - Add stats panel, help button
  - `viz/css/layout.css` - Responsive design
- Decorators added: None (cross-cutting concerns)

**Test Plan**:
- Manual testing only:
  - Load empty file → see "No nodes found"
  - Load invalid JSON → see error with line number
  - Load large graph → see loading spinner
  - Resize window → layout adapts
  - Click help → see usage instructions

**Docs Updated**:
- `viz/README.md` - Complete usage documentation
- `viz/README.md` - Add troubleshooting section

**Reflect**:
- What worked well:
- What could be better:
- Surprises/discoveries:
- Risks identified:

**Links**:
- Commit:

---

## Notes

### Testing Strategy

**Automated (browser-based):**
- `viz/tests/test.html` - Mocha + Chai test runner
- `test-loader.js` - NDJSON parsing tests (S-007, S-017)
- `test-filters.js` - Filter logic tests (S-010, S-011)
- `test-search.js` - Search logic tests (S-012)

**Manual (visual verification):**
- Rendering tests (S-008, S-009)
- Interaction tests (S-013, S-014, S-015)
- Layout tests (S-016)
- Polish tests (WU8)

### JS Comment Decorators

Since we don't have Python decorators, use comments:

```javascript
// @jig.implements("S-007")
function parseNDJSON(content) {
  // implementation
}

// @jig.verifies("S-007")
describe('parseNDJSON', () => {
  it('should parse metadata line', () => {
    // test
  });
});
```

These comments serve as manual linkage between code and specs. In commit messages, we'll reference them as:

```
Implements: S-007 (parseNDJSON in graph-loader.js)
Tests: test-loader.js::parseNDJSON tests (manual verification: passing)
```

### Sample Graph Creation

`viz/tests/fixtures/sample-graph.ndjson` should include:
- 1 metadata line
- 2 class nodes (one with implements field)
- 3 function nodes (one method, one async, one standalone)
- 2 module nodes (one internal, one external)
- 10 edges (mix of contains, implements, imports)

This gives enough variety to test all node/edge types without overwhelming the UI during development.

---

## Completion Summary

_(To be filled in after all work units complete)_

**Scope Delivered**:
-

**Metrics**:
- Work Units: 8
- Specifications Created: 11 (S-007 through S-017)
- Specifications Implemented:
- Tests: Browser-based (Mocha+Chai) + Manual

**Key Decisions**:
-

**Deltas from Original Scope**:
-

**Reflection Roll-Up**:
- **Repeatable wins**:
- **Systemic frictions**:
- **Open questions**:

**Final Validation**:
- [ ] All work unit checklists complete
- [ ] `jigy validate` passes (for O/S nodes)
- [ ] All browser tests passing (open test.html)
- [ ] Manual testing complete (all features work)
- [ ] Documentation updated (viz/README.md)
