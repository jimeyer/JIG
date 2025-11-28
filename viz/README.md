# JIG Implementation Graph Visualizer

A browser-based visualization tool for exploring JIG implementation graphs.

## Status

**Phase 1: Implementation Graph Only (In Progress)**

This tool is being built incrementally following the plan in `docs/viz/V002_PLAN_Implementation_Graph_Visualizer.md`.

### Completed Work Units
- [x] WU0: Intent definition (Outcomes O-007, O-008; Specifications S-007 through S-017)
- [x] WU1: Scaffold (basic HTML/CSS/JS structure)
- [ ] WU2: Graph Loading
- [ ] WU3: Basic Rendering
- [ ] WU4: Interaction
- [ ] WU5: Filtering
- [ ] WU6: Search
- [ ] WU7: Layout Switching
- [ ] WU8: Polish

## Quick Start

### Option 1: Open Directly in Browser

```bash
# From the project root
open viz/index.html
```

Or simply double-click `viz/index.html` in your file browser.

### Option 2: Run Tests

```bash
# Open test runner in browser
open viz/tests/test.html
```

## Usage (Once Complete)

1. **Load a graph**: Click "Load Graph" and select a `.ndjson` file from `jig/generated/implementation-graph.ndjson`

2. **Navigate**:
   - Mouse wheel to zoom
   - Click and drag to pan
   - Click "Zoom to Fit" to see the entire graph

3. **Filter**:
   - Use checkboxes to show/hide node types (Classes, Functions, Modules)
   - Use checkboxes to show/hide edge types (Contains, Implements, Imports)

4. **Search**:
   - Type in the search box to find nodes by name or ID
   - Click a search result to select and center that node

5. **Explore**:
   - Click nodes or edges to see details in the right panel
   - Switch layouts using the dropdown (Hierarchical, Force-directed, Circular, Grid)

## Architecture

```
viz/
├── index.html           # Main application
├── css/
│   ├── layout.css       # Page structure (header, sidebars, canvas)
│   ├── controls.css     # UI controls (buttons, checkboxes, inputs)
│   └── graph.css        # Graph canvas styling
├── js/
│   ├── main.js          # Application entry point
│   ├── graph-loader.js  # NDJSON parsing (WU2)
│   ├── graph-renderer.js # Cytoscape rendering (WU3)
│   ├── graph-interactions.js # Click/hover handlers (WU4)
│   ├── filters.js       # Filter logic (WU5)
│   ├── search.js        # Search logic (WU6)
│   ├── details-panel.js # Details display (WU4)
│   └── layout-manager.js # Layout switching (WU7)
├── tests/
│   ├── test.html        # Mocha test runner
│   ├── test-loader.js   # Parser tests (WU2)
│   ├── test-filters.js  # Filter tests (WU5)
│   ├── test-search.js   # Search tests (WU6)
│   └── fixtures/
│       └── sample-graph.ndjson # Test data
└── README.md            # This file
```

## Development

### No Build Step Required

This tool uses vanilla HTML/CSS/JavaScript with libraries loaded from CDN. No npm, webpack, or build process required.

### Running Tests

Open `viz/tests/test.html` in a browser to run the test suite. Tests use Mocha + Chai.

### Testing Strategy

- **Automated tests** (browser-based): Parsing, filtering, search logic
- **Manual tests** (visual verification): Rendering, interactions, layouts

### Adding Features

Follow the work units in `docs/viz/V002_PLAN_Implementation_Graph_Visualizer.md`:

1. Write specifications (already defined in `jig/specifications/S-*.md`)
2. Write tests (for logic-heavy features)
3. Implement code with `// @jig.implements("S-NNN")` comments
4. Manual testing for visual features
5. Update this README

## NDJSON Format

The visualizer expects NDJSON files in this format:

```
Line 1: {"_meta": {"node_count": N, "edge_count": M, "version": "1.0", "generated": "ISO-timestamp"}}
Lines 2-N+1: Node objects {"id": "...", "type": "class|function|module|external_module", ...}
Lines N+2-end: Edge objects {"source": "...", "target": "...", "type": "contains|implements|imports", ...}
```

See `viz/tests/fixtures/sample-graph.ndjson` for an example.

## Dependencies

Loaded from CDN (no installation required):

- **Cytoscape.js** (3.28.1) - Graph visualization
- **Fuse.js** (7.0.0) - Fuzzy search
- **Mocha** (10.2.0) - Test framework
- **Chai** (4.3.10) - Assertion library

## Future Phases

- **Phase 2**: Intent layer (Outcomes, Specifications)
- **Phase 3**: Verification layer (Tests, coverage)
- **Phase 4**: Brick visualization (boundaries, alignment metrics)

## Related Documentation

- **Proposal**: `docs/viz/V001_PROPOSAL_Implementation_Graph_Visualizer.md`
- **Plan**: `docs/viz/V002_PLAN_Implementation_Graph_Visualizer.md`
- **Alignment Graph Whitepaper**: `docs/bricks/AG002_Alignment_Graph_Whitepaper.md`

## License

Part of the JIG project.
