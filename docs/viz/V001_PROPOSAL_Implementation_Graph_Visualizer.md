# V001: Implementation Graph Visualizer - Proposal

## Overview

A self-contained, browser-based visualization tool for the JIG Alignment Graph system. This tool will render the implementation graph, verification graph, intent graph, and bricks as interactive, queryable visualizations.

**Phase 1 Scope:** Implementation graph only (classes, functions, modules, and their relationships)

**Future Phases:** Intent layer, verification layer, brick groupings, and alignment metrics

## Motivation

The Alignment Graph (AG002_Alignment_Graph_Whitepaper.md) describes a multi-layer semantic graph representing:
- **Dependency Layer** (implementation graph) - what actually exists in code
- **Intent Layer** - what should exist and why
- **Test Layer** - what is verified
- **Brick Layer** - architectural boundaries

Currently, these are represented as NDJSON files (machine-readable but not human-inspectable). We need a visual tool to:
1. Understand the current implementation structure
2. Detect architectural violations (illegal dependencies)
3. Identify orphaned code (no intent connection)
4. Visualize brick boundaries and their relationships
5. Measure alignment drift

## Design Principles

1. **Self-contained** - All code in `viz/` folder, no modifications to JIG core
2. **Read-only** - Renders existing artifacts, never modifies them
3. **Progressive enhancement** - Start simple (impl graph), add layers incrementally
4. **Browser-based** - No server required, runs as static HTML/JS/CSS
5. **Performant** - Handle graphs with 100+ nodes, 500+ edges smoothly
6. **Extensible** - Architecture supports future layers without rewrites

## Technology Stack

### Core Libraries

**Cytoscape.js** - Graph visualization and interaction
- Purpose-built for network/graph visualization
- Excellent layout algorithms (hierarchical, force-directed, circular, etc.)
- Rich API for filtering, styling, events
- Good performance (tested with thousands of nodes)
- Extensible with plugins

**Alternative considered:** D3.js (more flexible but requires more custom code for graph operations)

### Supporting Libraries

- **Papa Parse** - Fast NDJSON/CSV parsing
- **js-yaml** - Parse brick.yaml files (future phases)
- **Fuse.js** - Fuzzy search for node/edge discovery

### No Build Step Required

All libraries loaded via CDN or vendored in `viz/lib/`. No npm, webpack, or build process. Just open `index.html` in browser.

## Architecture

### File Structure

```
viz/
├── index.html                 # Main entry point
├── README.md                  # Usage instructions
├── css/
│   ├── layout.css             # Page layout, panels
│   ├── controls.css           # UI controls styling
│   └── graph.css              # Graph-specific styles
├── js/
│   ├── main.js                # Application initialization
│   ├── graph-loader.js        # Parse NDJSON, build Cytoscape model
│   ├── graph-renderer.js      # Render graph with layouts
│   ├── graph-interactions.js  # Click, hover, selection handlers
│   ├── filters.js             # Node/edge filtering logic
│   ├── search.js              # Search and highlight
│   ├── details-panel.js       # Node/edge detail display
│   └── layout-manager.js      # Layout algorithm switching
├── lib/                       # Third-party libraries (optional vendoring)
│   ├── cytoscape.min.js
│   ├── papaparse.min.js
│   └── fuse.min.js
└── examples/
    └── sample-graph.ndjson    # Small test graph for development
```

### Data Flow

```
implementation-graph.ndjson
         ↓
    graph-loader.js (parse NDJSON)
         ↓
    Cytoscape graph model
         ↓
    graph-renderer.js (apply layout, styles)
         ↓
    Interactive visualization in browser
         ↓
    User interactions (filters, search, selection)
         ↓
    details-panel.js (show node/edge metadata)
```

## Phase 1: Implementation Graph Features

### Core Visualization

**Node Rendering**
- **Classes** - Rectangle, color-coded by language
  - Show class name
  - Indicate if it implements specs (has `implements` field)
  - Show base classes as labels
- **Functions** - Circle/ellipse
  - Show function name
  - Indicate async functions
  - Distinguish methods (has `parent_class`) from standalone functions
- **Modules** - Rounded rectangle, different color
  - Internal modules vs external modules (different shading)

**Edge Rendering**
- **Contains** - Thick solid line (module → class, class → method)
- **Implements** - Dashed line with arrow (code → spec ID)
- **Imports** - Thin line with arrow (module → module)
- **Calls** - (Future: not in current graph, but reserved)

**Layout Algorithms**
- **Hierarchical** (default) - Top-down, shows containment clearly
- **Force-directed** - Organic clustering, reveals natural groupings
- **Circular** - Nodes in circle, good for seeing all connections
- **Grid** - Organized rows/columns
- User can switch layouts via dropdown

### Navigation & Interaction

**Zoom & Pan**
- Mouse wheel zoom
- Click-drag pan
- Zoom to fit button
- Zoom to selection button

**Node Selection**
- Click node → highlight node and its immediate neighbors
- Show node details in side panel
- Double-click → zoom to node

**Edge Selection**
- Click edge → highlight edge and its source/target nodes
- Show edge metadata in side panel

**Multi-select**
- Ctrl+click to add to selection
- Shift+drag for box selection

### Filtering & Search

**Node Type Filter**
- Checkboxes: Classes | Functions | Modules | External Modules
- Real-time graph update

**Edge Type Filter**
- Checkboxes: Contains | Implements | Imports
- Real-time graph update

**Language Filter**
- Checkboxes: Python | (future: TypeScript, Go, etc.)

**Search**
- Fuzzy search by node name or ID
- Highlight matching nodes
- List of results with click-to-select

**Spec Implementation Filter**
- "Show only nodes that implement specs" toggle
- Helps identify which code has explicit intent connections

### Details Panel

When node/edge selected, show in right sidebar:

**Node Details**
- **ID** (unique identifier)
- **Type** (class/function/module)
- **Name**
- **File path** (if applicable)
- **Line number** (if applicable)
- **Language**
- **Signature** (for functions)
- **Bases** (for classes)
- **Implements** (spec IDs, if any)
- **Incoming edges** (count and list)
- **Outgoing edges** (count and list)

**Edge Details**
- **Type** (contains/implements/imports)
- **Source** node (with link to select)
- **Target** node (with link to select)
- **Line number** (for imports)

### Statistics Panel

Show in header or left sidebar:
- **Total nodes:** X (Y classes, Z functions, W modules)
- **Total edges:** X (Y contains, Z implements, W imports)
- **Graph generated:** timestamp from metadata
- **Graph version:** version from metadata

### File Loading

**Default behavior:**
- On page load, attempt to load `../jig/generated/implementation-graph.ndjson` (relative path from viz/)
- If not found, show file picker dialog

**Manual loading:**
- "Load Graph" button → file picker
- Drag-and-drop NDJSON file onto page

**Error handling:**
- Invalid NDJSON → show error message with line number
- Missing required fields → warn but attempt to render
- Empty graph → show message "No nodes found"

## Phase 2-4: Future Enhancements (Not in V1)

### Phase 2: Intent Layer
- Load Outcome and Specification nodes from intent graph
- Render intent nodes in separate layer or color-coded
- Show `implements` edges connecting code → specs
- Filter: "Show only unimplemented specs"

### Phase 3: Verification Layer
- Load Test nodes from verification graph
- Show `verifies` edges connecting tests → specs
- Show `covers` edges connecting tests → code
- Filter: "Show only unverified specs"
- Alignment metrics: coverage percentages

### Phase 4: Brick Visualization
- Load brick.yaml definitions
- Group nodes by brick membership
- Show brick boundaries as colored regions or containers
- Show brick dependency graph (separate view mode)
- Highlight illegal dependencies (cross-brick calls without declared dependency)
- Alignment metrics: boundary violations, orphaned code

### Phase 5: Alignment Metrics
- Intent ↔ Code alignment score
- Intent ↔ Test alignment score
- Code ↔ Architecture alignment score
- Drift detection: highlight drift areas in graph

## UI Mockup (Textual Description)

```
┌─────────────────────────────────────────────────────────────────────┐
│ JIG Implementation Graph Visualizer          [Load Graph] [Help]    │
├─────────────┬───────────────────────────────────────────┬───────────┤
│             │                                           │           │
│  Filters    │           Graph Canvas                    │  Details  │
│             │                                           │           │
│ Node Types  │                                           │ Selected: │
│ ☑ Classes   │         [Interactive Graph Here]         │           │
│ ☑ Functions │                                           │ Node ID:  │
│ ☑ Modules   │         (Cytoscape rendering)            │ C-jig...  │
│ ☐ External  │                                           │           │
│             │                                           │ Type:     │
│ Edge Types  │                                           │ class     │
│ ☑ Contains  │                                           │           │
│ ☑ Implements│                                           │ File:     │
│ ☑ Imports   │                                           │ src/...   │
│             │                                           │           │
│ Search      │                                           │ Implements│
│ [_______]   │                                           │ - S-001   │
│             │                                           │ - S-006   │
│ Layout      │                                           │           │
│ [Hierarchi▾]│                                           │ Edges:    │
│             │                                           │ In: 3     │
│ [Zoom Fit]  │                                           │ Out: 5    │
│ [Reset]     │                                           │           │
│             │                                           │           │
│ Stats       │                                           │           │
│ Nodes: 126  │                                           │           │
│ Edges: 158  │                                           │           │
│             │                                           │           │
└─────────────┴───────────────────────────────────────────┴───────────┘
```

## Implementation Plan

### Step 1: Scaffold (1-2 hours)
- Create `viz/` folder structure
- Basic `index.html` with layout (header, sidebar, main canvas, details panel)
- Load Cytoscape.js from CDN
- Confirm page loads and Cytoscape initializes

### Step 2: Graph Loading (2-3 hours)
- Implement `graph-loader.js` to parse NDJSON
- Extract metadata line (line 1)
- Parse node lines (lines 2-127 in current graph)
- Parse edge lines (lines 128-285 in current graph)
- Build Cytoscape elements array (nodes + edges)
- Handle errors gracefully

### Step 3: Basic Rendering (2-3 hours)
- Implement `graph-renderer.js`
- Configure Cytoscape styles for node types (class, function, module)
- Configure edge styles (contains, implements, imports)
- Apply default hierarchical layout
- Render graph to canvas

### Step 4: Interaction (2-3 hours)
- Implement zoom, pan controls
- Node click → select and highlight
- Edge click → select and highlight
- Details panel population from node/edge data

### Step 5: Filtering (2-3 hours)
- Node type checkboxes → filter graph
- Edge type checkboxes → filter graph
- Update graph dynamically on filter change

### Step 6: Search (1-2 hours)
- Search input with fuzzy matching (Fuse.js)
- Highlight matching nodes
- Click result → select node

### Step 7: Layout Switching (1 hour)
- Layout dropdown (hierarchical, force-directed, circular, grid)
- Re-layout on selection

### Step 8: Polish (2-3 hours)
- Responsive design (handle window resize)
- Loading states and error messages
- Help documentation (modal or separate page)
- Styling improvements

**Total Estimated Effort:** 15-20 hours for Phase 1

## Success Criteria

Phase 1 (Implementation Graph) is successful if:

1. ✅ Loads `implementation-graph.ndjson` and renders all 126 nodes, 158 edges
2. ✅ Distinguishes node types visually (classes, functions, modules)
3. ✅ Shows containment relationships clearly (module → class → function)
4. ✅ Highlights `implements` edges (code → spec IDs)
5. ✅ Allows filtering by node type and edge type
6. ✅ Search finds nodes by name/ID
7. ✅ Clicking nodes shows full metadata in details panel
8. ✅ Graph is navigable (zoom, pan) and performant (no lag)
9. ✅ Runs without build step (just open HTML in browser)
10. ✅ Doesn't modify any JIG artifacts

## Open Questions

1. **Performance:** Current graph has 126 nodes. What if we scale to 1000+ nodes? May need virtual rendering or clustering.

2. **Layout:** Which layout algorithm works best for showing containment + dependencies? May need custom layout.

3. **Color scheme:** How to distinguish node types while remaining colorblind-friendly?

4. **Edge clutter:** With 158 edges, graph may be visually dense. Need edge bundling or hiding strategies?

5. **State persistence:** Should we save user preferences (layout choice, filters) to localStorage?

6. **Export:** Should we support exporting graph as PNG/SVG/PDF?

7. **Integration:** Should this eventually integrate with JIG CLI (e.g., `jigy visualize --open`)?

## Future Integration with JIG

Although initially self-contained, we could later:

1. **Generate launcher:** `jigy viz` command that opens `viz/index.html` in browser
2. **Watch mode:** Auto-reload graph when NDJSON regenerated
3. **Embedded in docs:** Include visualizations in generated documentation
4. **CI/CD:** Generate static graph images for PR reviews

But for V1, keep it simple: standalone HTML tool in `viz/` folder.

## Alternatives Considered

### Alternative 1: Python-based tool (Graphviz)
- **Pros:** Can integrate with JIG CLI directly
- **Cons:** Not interactive, requires Python environment, generates static images only

### Alternative 2: VS Code extension
- **Pros:** Integrated with developer workflow
- **Cons:** Platform-specific, requires extension development skills, harder to distribute

### Alternative 3: Jupyter notebook
- **Pros:** Good for exploratory analysis
- **Cons:** Requires Python + Jupyter setup, not standalone, not optimized for interactivity

**Decision:** Browser-based HTML/JS tool offers best balance of accessibility, interactivity, and distribution.

## Conclusion

This proposal outlines a pragmatic, incremental approach to visualizing the Alignment Graph:

- **Phase 1** focuses on implementation graph only (classes, functions, modules, edges)
- Self-contained in `viz/` folder, no impact on JIG core
- Browser-based, no build step, no server required
- Uses Cytoscape.js for robust graph visualization
- Extensible architecture for future layers (intent, verification, bricks)
- Estimated 15-20 hours to complete Phase 1

**Next Steps:**
1. Review and approve this proposal
2. Create `viz/` folder and scaffold
3. Implement Step 1 (basic page structure)
4. Iterate through Steps 2-8

Once Phase 1 is working, we can evaluate whether to proceed with Phases 2-4 (additional graph layers and alignment metrics).

---

**Author:** JIG Development Team
**Date:** 2025-11-28
**Status:** PROPOSED
**Related:** AG002_Alignment_Graph_Whitepaper.md
