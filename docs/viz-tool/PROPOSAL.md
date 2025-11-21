# JIG Intent Graph Visualization Tool - Proposal

**Date:** 2025-11-21  
**Status:** Proposal  
**Author:** System Design

---

## Executive Summary

This proposal outlines the design and implementation of an HTML-based visualization tool for the JIG Intent Graph. The tool will provide an interactive, zoomable view of the O-S-T-C (Outcome-Specification-Test-Code) graph structure, enabling developers to understand the relationships between intent and implementation at a glance.

---

## 1. Goals & Requirements

### 1.1 Primary Goals
- **Visualize the complete Intent Graph** showing all nodes (O, S, T, C) and their connections
- **Column-based layout** with O-S-T-C arranged left-to-right for intuitive flow
- **Interactive navigation** with zoom, pan, and reset capabilities
- **Node inspection** allowing users to view node file contents on click
- **Self-contained** single HTML file that can be opened directly in a browser

### 1.2 User Stories
1. As a developer, I want to see the entire Intent Graph to understand system architecture
2. As a developer, I want to zoom in/out to focus on specific areas or see the big picture
3. As a developer, I want to click on nodes to read their full documentation
4. As a developer, I want to see which specifications implement which outcomes
5. As a developer, I want to identify orphaned nodes or missing connections

---

## 2. Architecture Overview

### 2.1 Technology Stack

**Core Libraries:**
- **D3.js v7** - Data visualization and DOM manipulation
  - Mature, well-documented, powerful force-directed graphs
  - Excellent zoom/pan support
  - SVG-based rendering for crisp visuals at any scale
  
- **Vanilla JavaScript** - No build step required
  - Keep it simple and fast
  - Easy to maintain and extend
  - Works in any modern browser

**Data Format:**
- **Embedded JSON** - Graph data from `graph-index.yaml` converted to JSON
  - Nodes array with id, type, title, file, subsystem
  - Edges array with from, to, type
  - Can be generated via Python script or embedded manually

### 2.2 Component Architecture

```
┌─────────────────────────────────────────────────┐
│           jig-graph-viz.html                    │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │         HTML Structure                    │ │
│  │  - SVG container for graph               │ │
│  │  - Control panel (zoom, reset)           │ │
│  │  - Side panel for node details           │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │         CSS Styling                       │ │
│  │  - Node colors by type (O/S/T/C)         │ │
│  │  - Edge styles by relationship           │ │
│  │  - Responsive layout                     │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │         JavaScript Modules                │ │
│  │                                           │ │
│  │  1. Data Loader                          │ │
│  │     - Parse embedded JSON                │ │
│  │     - Build D3 data structures           │ │
│  │                                           │ │
│  │  2. Graph Renderer                       │ │
│  │     - Column-based layout engine         │ │
│  │     - Node/edge rendering                │ │
│  │     - Force simulation (constrained)     │ │
│  │                                           │ │
│  │  3. Interaction Handler                  │ │
│  │     - Zoom/pan with d3.zoom              │ │
│  │     - Node click → detail view           │ │
│  │     - Hover effects                      │ │
│  │                                           │ │
│  │  4. Detail Panel                         │ │
│  │     - Fetch node file content            │ │
│  │     - Markdown rendering (optional)      │ │
│  │     - Navigation history                 │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 3. Detailed Design

### 3.1 Layout Strategy

**Column-Based Constraint Layout:**

```
     O              S              T              C
  (Outcomes)   (Specifications)  (Tests)       (Code)
  
  ┌─────┐        ┌─────┐        ┌─────┐      ┌─────┐
  │O-001│───────→│S-001│───────→│T-001│─────→│C-001│
  └─────┘        └─────┘        └─────┘      └─────┘
     │              │
     │              ↓
     │           ┌─────┐        ┌─────┐      ┌─────┐
     └──────────→│S-002│───────→│T-002│─────→│C-002│
                 └─────┘        └─────┘      └─────┘
```

**Implementation Approach:**
1. **Fixed X-coordinates** based on node type:
   - Outcomes: x = 200
   - Specifications: x = 500
   - Tests: x = 800
   - Code: x = 1100

2. **Dynamic Y-coordinates** using D3 force simulation:
   - Vertical force to spread nodes
   - Collision detection to prevent overlap
   - Link force (weak) to pull connected nodes closer vertically
   - X-axis constraint to keep nodes in columns

3. **Subsystem grouping** (optional enhancement):
   - Visual grouping with background rectangles
   - Color coding by subsystem

### 3.2 Visual Design

**Node Styling:**
```javascript
const nodeStyles = {
  outcome: {
    color: '#4A90E2',      // Blue
    shape: 'circle',
    radius: 30,
    label: 'O'
  },
  specification: {
    color: '#7ED321',      // Green
    shape: 'rect',
    size: 50,
    label: 'S'
  },
  test: {
    color: '#F5A623',      // Orange
    shape: 'diamond',
    size: 50,
    label: 'T'
  },
  code: {
    color: '#BD10E0',      // Purple
    shape: 'rect',
    size: 50,
    label: 'C'
  }
}
```

**Edge Styling:**
```javascript
const edgeStyles = {
  implements: {
    color: '#333',
    width: 2,
    style: 'solid',
    arrow: true
  },
  verifies: {
    color: '#F5A623',
    width: 2,
    style: 'dashed',
    arrow: true
  },
  depends_on: {
    color: '#999',
    width: 1,
    style: 'dotted',
    arrow: true
  }
}
```

**Color Palette:**
- Background: `#F8F9FA` (light gray)
- Grid lines: `#E0E0E0` (subtle)
- Selected node: Glow effect with shadow
- Hover: Brightness increase + tooltip

### 3.3 Interaction Design

**Zoom & Pan:**
```javascript
// D3 zoom behavior
const zoom = d3.zoom()
  .scaleExtent([0.1, 4])  // 10% to 400%
  .on('zoom', (event) => {
    svg.attr('transform', event.transform);
  });

// Reset button
function resetView() {
  svg.transition()
    .duration(750)
    .call(zoom.transform, d3.zoomIdentity);
}
```

**Node Click Behavior:**
1. Click node → highlight node and connected edges
2. Slide in detail panel from right
3. Fetch node file content (via relative path)
4. Display with syntax highlighting
5. Show metadata (type, subsystem, connections)
6. Provide "Open in Editor" link (file:// protocol)

**Keyboard Shortcuts:**
- `R` - Reset view
- `+` / `-` - Zoom in/out
- `ESC` - Close detail panel
- `F` - Fit to screen

### 3.4 Data Loading Strategy

**Option A: Embedded JSON (Recommended for v1)**
```html
<script id="graph-data" type="application/json">
{
  "nodes": [
    {
      "id": "O-JIG-001",
      "type": "outcome",
      "title": "JIG tools run in <1 second",
      "file": "jig/outcomes/O-JIG-001.md",
      "subsystem": "core"
    },
    ...
  ],
  "edges": [
    {
      "from": "S-JIG-001",
      "to": "O-JIG-001",
      "type": "implements"
    },
    ...
  ]
}
</script>
```

**Option B: Dynamic Loading (Future enhancement)**
- Fetch `graph-index.yaml` via HTTP
- Parse YAML in browser (js-yaml library)
- Requires serving via local web server

**Recommendation:** Start with Option A for simplicity. Add Option B later if needed.

### 3.5 File Content Display

**Challenge:** Accessing local files from browser

**Solutions:**

1. **Embedded Content (Best for portability)**
   - Include all node file contents in the HTML
   - Pre-process during generation
   - Instant display, no network requests
   - Larger file size (~100KB for typical graph)

2. **File Protocol Links (Best for development)**
   - Link to `file:///absolute/path/to/node.md`
   - Opens in user's default editor/viewer
   - No content embedding needed
   - Requires absolute paths

3. **Local Server (Best for features)**
   - Serve via `python -m http.server`
   - Fetch files dynamically
   - Enables search, filtering, etc.
   - Requires running server

**Recommendation:** Implement #1 (embedded) for v1, add #2 (file links) as fallback.

---

## 4. Implementation Plan

### 4.1 File Structure

```
docs/viz-tool/
├── PROPOSAL.md                    # This document
├── jig-graph-viz.html             # Main visualization (self-contained)
├── generate-viz.py                # Python script to generate HTML
├── README.md                      # Usage instructions
└── examples/
    └── screenshot.png             # Example visualization
```

### 4.2 Development Phases

**Phase 1: Core Visualization (MVP)**
- [ ] Create HTML template with D3.js
- [ ] Implement column-based layout
- [ ] Render nodes and edges
- [ ] Add basic styling
- [ ] Implement zoom/pan
- [ ] Add reset button
- **Deliverable:** Static visualization of current graph

**Phase 2: Interactivity**
- [ ] Node click handler
- [ ] Detail panel slide-in
- [ ] Display node metadata
- [ ] Show embedded file content
- [ ] Highlight connected nodes
- **Deliverable:** Interactive exploration

**Phase 3: Generation Script**
- [ ] Python script to read `graph-index.yaml`
- [ ] Read all node files
- [ ] Generate JSON data structure
- [ ] Embed in HTML template
- [ ] Write output file
- **Deliverable:** Automated generation

**Phase 4: Polish & Features**
- [ ] Keyboard shortcuts
- [ ] Search/filter nodes
- [ ] Subsystem grouping
- [ ] Export to PNG/SVG
- [ ] Responsive design
- **Deliverable:** Production-ready tool

### 4.3 Estimated Effort

| Phase | Complexity | Time Estimate |
|-------|-----------|---------------|
| Phase 1 | Medium | 4-6 hours |
| Phase 2 | Medium | 3-4 hours |
| Phase 3 | Low | 2-3 hours |
| Phase 4 | Medium | 4-6 hours |
| **Total** | | **13-19 hours** |

---

## 5. Technical Specifications

### 5.1 Browser Compatibility

**Minimum Requirements:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Features Used:**
- ES6+ JavaScript (arrow functions, const/let, template literals)
- SVG rendering
- Fetch API (for dynamic loading)
- CSS Grid/Flexbox

### 5.2 Performance Considerations

**Expected Scale:**
- Nodes: 10-500 (typical: 50-100)
- Edges: 20-1000 (typical: 100-200)

**Optimization Strategies:**
1. **Lazy rendering** - Only render visible nodes when zoomed in
2. **Simplified edges** - Use straight lines instead of curves for >100 edges
3. **Canvas fallback** - Switch from SVG to Canvas for >500 nodes
4. **Debounced updates** - Throttle force simulation updates

**Performance Targets:**
- Initial render: <1 second
- Zoom/pan: 60 FPS
- Node click response: <100ms

### 5.3 Accessibility

- Keyboard navigation support
- ARIA labels for screen readers
- High contrast mode support
- Focus indicators
- Semantic HTML structure

---

## 6. Example Usage

### 6.1 Generating the Visualization

```bash
# From project root
cd docs/viz-tool

# Generate visualization from current graph
python generate-viz.py

# Output: jig-graph-viz.html
```

### 6.2 Viewing the Visualization

```bash
# Option 1: Open directly in browser
open jig-graph-viz.html

# Option 2: Serve via HTTP (for dynamic features)
python -m http.server 8000
# Then open http://localhost:8000/jig-graph-viz.html
```

### 6.3 Updating the Visualization

```bash
# After modifying graph-index.yaml or node files
python generate-viz.py

# Refresh browser to see changes
```

---

## 7. Future Enhancements

### 7.1 Short Term (Post-MVP)
- **Search & Filter** - Find nodes by ID, title, or subsystem
- **Diff View** - Compare two versions of the graph
- **Export** - Save as PNG, SVG, or PDF
- **Minimap** - Overview of entire graph with viewport indicator
- **Node Templates** - Quick create new nodes from visualization

### 7.2 Long Term
- **Live Updates** - Watch `graph-index.yaml` and auto-refresh
- **Collaboration** - Share annotated views via URL
- **Metrics Dashboard** - Show graph statistics (coverage, orphans, etc.)
- **AI Integration** - Suggest missing connections or nodes
- **Time Travel** - Visualize graph evolution over git history
- **3D View** - Experimental 3D graph for large systems

---

## 8. Alternatives Considered

### 8.1 Graphviz/DOT
**Pros:**
- Simple text format
- Automatic layout
- PNG/SVG export

**Cons:**
- No interactivity
- Limited customization
- Separate tool required
- No node content display

**Decision:** Rejected - Need interactivity

### 8.2 Cytoscape.js
**Pros:**
- Powerful graph library
- Many layout algorithms
- Good documentation

**Cons:**
- Larger bundle size
- More complex API
- Overkill for our needs

**Decision:** Rejected - D3.js is sufficient

### 8.3 Mermaid.js
**Pros:**
- Simple syntax
- Markdown integration
- Lightweight

**Cons:**
- Limited layout control
- No column constraints
- Less interactive

**Decision:** Rejected - Need custom layout

### 8.4 React + React Flow
**Pros:**
- Modern framework
- Component-based
- Good for complex UIs

**Cons:**
- Requires build step
- Heavier dependency
- More complexity

**Decision:** Rejected - Keep it simple

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| D3.js learning curve | Medium | Low | Use examples, start simple |
| Browser file access limits | High | Medium | Embed content in HTML |
| Performance with large graphs | Low | Medium | Implement lazy rendering |
| Layout algorithm complexity | Medium | Medium | Start with simple force layout |
| Maintenance burden | Low | Low | Keep code simple, document well |

---

## 10. Success Criteria

### 10.1 Functional Requirements
- ✅ Displays all nodes from `graph-index.yaml`
- ✅ Shows all edges with correct directionality
- ✅ Arranges O-S-T-C in columns left-to-right
- ✅ Supports zoom in/out
- ✅ Supports pan
- ✅ Provides reset view button
- ✅ Opens node details on click
- ✅ Displays node file content

### 10.2 Non-Functional Requirements
- ✅ Single HTML file (self-contained)
- ✅ Works offline
- ✅ Loads in <2 seconds
- ✅ Responsive to window resize
- ✅ Visually appealing
- ✅ Intuitive to use (no documentation needed)

### 10.3 User Acceptance
- Developer can understand graph structure in <30 seconds
- Developer can navigate to any node in <10 seconds
- Developer finds visualization useful for planning work
- Developer prefers visualization over reading YAML directly

---

## 11. Conclusion

This proposal outlines a pragmatic, implementable solution for visualizing the JIG Intent Graph. By using proven technologies (D3.js), keeping the scope focused (single HTML file), and prioritizing user needs (column layout, interactivity), we can deliver a valuable tool that enhances developer understanding of the system architecture.

The phased approach allows for incremental delivery, with an MVP that provides immediate value and a clear path to enhanced features. The estimated 13-19 hour implementation time is reasonable for the value delivered.

**Recommendation:** Proceed with implementation, starting with Phase 1 (Core Visualization).

---

## Appendix A: Code Snippets

### A.1 Basic HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JIG Intent Graph Visualization</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #F8F9FA;
    }
    #graph-container {
      width: 100vw;
      height: 100vh;
    }
    .node {
      cursor: pointer;
      transition: all 0.2s;
    }
    .node:hover {
      filter: brightness(1.2);
    }
    .edge {
      fill: none;
      stroke-width: 2px;
    }
  </style>
</head>
<body>
  <div id="controls">
    <button onclick="resetView()">Reset View</button>
  </div>
  <div id="graph-container"></div>
  <div id="detail-panel" style="display: none;">
    <div id="detail-content"></div>
  </div>
  
  <script id="graph-data" type="application/json">
    <!-- JSON data here -->
  </script>
  
  <script>
    // Visualization code here
  </script>
</body>
</html>
```

### A.2 Column Layout Logic

```javascript
function getColumnX(nodeType) {
  const columns = {
    'outcome': 200,
    'specification': 500,
    'test': 800,
    'code': 1100
  };
  return columns[nodeType] || 500;
}

function applyColumnConstraints(simulation) {
  simulation.force('x', d3.forceX(d => getColumnX(d.type)).strength(1));
  simulation.force('y', d3.forceY(height / 2).strength(0.1));
  simulation.force('collision', d3.forceCollide().radius(40));
}
```

### A.3 Node Rendering

```javascript
function renderNodes(svg, nodes) {
  const nodeGroups = svg.selectAll('.node')
    .data(nodes)
    .enter()
    .append('g')
    .attr('class', 'node')
    .on('click', handleNodeClick);
  
  // Add shapes based on type
  nodeGroups.each(function(d) {
    const g = d3.select(this);
    if (d.type === 'outcome') {
      g.append('circle')
        .attr('r', 30)
        .attr('fill', '#4A90E2');
    } else {
      g.append('rect')
        .attr('width', 50)
        .attr('height', 50)
        .attr('x', -25)
        .attr('y', -25)
        .attr('fill', getNodeColor(d.type));
    }
  });
  
  // Add labels
  nodeGroups.append('text')
    .text(d => d.id)
    .attr('text-anchor', 'middle')
    .attr('dy', 4)
    .attr('fill', 'white')
    .attr('font-size', '10px');
  
  return nodeGroups;
}
```

---

## Appendix B: Sample Data Structure

```json
{
  "metadata": {
    "version": "1.0.0",
    "generated": "2025-11-21T10:30:00Z",
    "source": "jig/graph-index.yaml"
  },
  "nodes": [
    {
      "id": "O-JIG-001",
      "type": "outcome",
      "title": "JIG tools run in <1 second for most operations",
      "subsystem": "core",
      "file": "jig/outcomes/O-JIG-001.md",
      "content": "---\nid: O-JIG-001\n..."
    },
    {
      "id": "S-JIG-001",
      "type": "specification",
      "title": "Marker extraction processes 1000 files in <1s",
      "subsystem": "core",
      "file": "jig/specifications/S-JIG-001.md",
      "content": "---\nid: S-JIG-001\n..."
    }
  ],
  "edges": [
    {
      "id": "e1",
      "from": "S-JIG-001",
      "to": "O-JIG-001",
      "type": "implements"
    }
  ],
  "subsystems": {
    "core": {
      "name": "core",
      "description": "Core JIG infrastructure",
      "nodes": ["O-JIG-001", "S-JIG-001"]
    }
  }
}
```

---

**End of Proposal**

