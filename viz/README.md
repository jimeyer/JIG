# JIG Implementation Graph Visualizer

A browser-based visualization tool for exploring JIG implementation graphs.

## Status

**Phase 1: Implementation Graph Only - COMPLETE**

This tool was built incrementally following the plan in `docs/viz/V002_PLAN_Implementation_Graph_Visualizer.md`.

### Completed Work Units
- [x] WU0: Intent definition (Outcomes O-007, O-008; Specifications S-007 through S-017)
- [x] WU1: Scaffold (basic HTML/CSS/JS structure)
- [x] WU2: Graph Loading
- [x] WU3: Basic Rendering
- [x] WU4: Interaction
- [x] WU5: Filtering
- [x] WU6: Search
- [x] WU7: Layout Switching
- [x] WU8: Polish

**Phase 1 Complete!** All core functionality implemented and tested.

## Quick Start

### Important: Requires Local Web Server

Due to ES6 module CORS restrictions, you **must** run a local web server. Opening `index.html` directly with `file://` will not work.

**Start a local web server:**

```bash
# From the project root
cd viz
python3 -m http.server 8000
```

Then open in your browser:
```
http://localhost:8000
```

### Run Tests

With the web server running (see above), open in your browser:
```
http://localhost:8000/tests/test.html
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
   - Switch layouts using the dropdown:
     - **Hierarchical (Rows)**: Top-down tree structure showing containment
     - **Hierarchical (Columns)**: Left-to-right tree, modules on left descending right
     - **Force-directed**: Organic clustering based on connections
     - **Circular**: Nodes arranged in circle
     - **Grid**: Organized rows and columns

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
│   ├── graph-renderer.js # Cytoscape rendering (WU3) + layout switching (WU7)
│   ├── graph-interactions.js # Click/hover handlers (WU4)
│   ├── filters.js       # Filter logic (WU5) ✓
│   ├── search.js        # Search logic (WU6) ✓
│   └── details-panel.js # Details display (WU4)
├── tests/
│   ├── test.html        # Mocha test runner
│   ├── test-loader.js   # Parser tests (WU2) - 18 tests
│   ├── test-filters.js  # Filter tests (WU5) - 14 tests
│   ├── test-search.js   # Search tests (WU6) - 12 tests ✓
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

## Troubleshooting

### Graph doesn't load / "Load Graph" button doesn't work

**Problem**: ES6 modules require HTTP server due to CORS restrictions.

**Solution**: Make sure you're running a local web server:
```bash
cd viz
python3 -m http.server 8000
```
Then open `http://localhost:8000` (not `file://...`)

### "Can not create edge with nonexistent target" error

**Problem**: Graph file contains edges referencing nodes that don't exist.

**Solution**: The visualizer automatically skips these edges with console warnings. Check the browser console to see which edges were skipped. This is expected when the graph contains references to spec nodes or other intent layer elements.

### "No nodes found in graph" message

**Problem**: The NDJSON file is empty or doesn't contain any valid node entries.

**Solution**:
- Verify the file contains node objects with `id` and `type` fields
- Check the browser console for parsing errors
- Ensure the first line contains metadata: `{"_meta": {...}}`

### "Invalid JSON at line N" error

**Problem**: The NDJSON file contains malformed JSON on a specific line.

**Solution**:
- Open the file and check line N for syntax errors
- Common issues: missing commas, unquoted strings, trailing commas
- Each line must be valid standalone JSON

### Graph is too large / performance issues

**Problem**: Large graphs (1000+ nodes) may be slow to render or filter.

**Solution**:
- Use filters to hide node/edge types you don't need
- Use search to focus on specific areas
- Consider generating smaller subgraphs for specific modules

### Search doesn't find expected nodes

**Problem**: Search uses fuzzy matching which may not match exact expectations.

**Solution**:
- Try partial matches (e.g., "Token" instead of "TokenValidator")
- Search is case-insensitive
- Search looks in both `name` and `id` fields
- Empty query returns all nodes

### Sidebar doesn't appear on mobile

**Problem**: Responsive design hides sidebars on narrow screens.

**Solution**: On screens < 768px, the right sidebar is hidden. On screens < 480px, the left sidebar becomes a slide-out panel. This is intentional to maximize graph viewing area on small screens.

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
