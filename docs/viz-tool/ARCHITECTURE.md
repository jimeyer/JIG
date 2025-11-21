# JIG Visualization Tool - Architecture Details

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    JIG Visualization System                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │      Generation Phase (Python)          │
        │                                         │
        │  1. Read graph-index.yaml               │
        │  2. Read all node files (*.md)          │
        │  3. Build JSON data structure           │
        │  4. Embed in HTML template              │
        │  5. Write jig-graph-viz.html            │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │      Runtime Phase (Browser)            │
        │                                         │
        │  1. Parse embedded JSON                 │
        │  2. Initialize D3.js                    │
        │  3. Render graph with constraints       │
        │  4. Handle user interactions            │
        │  5. Display node details                │
        └─────────────────────────────────────────┘
```

## Data Flow

```
graph-index.yaml ──┐
                   │
node files (*.md) ─┤
                   │
subsystems.yaml ───┤
                   │
                   ├──→ generate-viz.py ──→ jig-graph-viz.html
                   │                              │
                   │                              │
                   └──────────────────────────────┘
                          (embedded as JSON)
```

## Component Breakdown

### 1. Data Layer

```javascript
// Core data structures
{
  nodes: [
    {
      id: "O-JIG-001",
      type: "outcome",
      title: "...",
      subsystem: "core",
      file: "jig/outcomes/O-JIG-001.md",
      content: "...",  // Full file content
      x: 200,          // Column position
      y: null          // Calculated by force simulation
    }
  ],
  edges: [
    {
      from: "S-JIG-001",
      to: "O-JIG-001",
      type: "implements"
    }
  ],
  subsystems: {
    "core": {
      name: "core",
      nodes: ["O-JIG-001", ...],
      description: "..."
    }
  }
}
```

### 2. Layout Engine

```
┌─────────────────────────────────────────────────────────────┐
│                    Layout Algorithm                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: Assign Column X-coordinates                       │
│    ┌─────────────────────────────────────────┐            │
│    │ O nodes → x = 200                       │            │
│    │ S nodes → x = 500                       │            │
│    │ T nodes → x = 800                       │            │
│    │ C nodes → x = 1100                      │            │
│    └─────────────────────────────────────────┘            │
│                                                             │
│  Step 2: Apply Force Simulation                            │
│    ┌─────────────────────────────────────────┐            │
│    │ X-axis force: Strong (keep in columns)  │            │
│    │ Y-axis force: Weak (vertical spread)    │            │
│    │ Link force: Medium (pull connected)     │            │
│    │ Collision force: Strong (no overlap)    │            │
│    └─────────────────────────────────────────┘            │
│                                                             │
│  Step 3: Render                                            │
│    ┌─────────────────────────────────────────┐            │
│    │ Draw edges (lines with arrows)          │            │
│    │ Draw nodes (shapes + labels)            │            │
│    │ Apply zoom/pan transforms               │            │
│    └─────────────────────────────────────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. Rendering Pipeline

```
User opens HTML
      │
      ▼
Parse embedded JSON
      │
      ▼
Initialize D3 SVG
      │
      ▼
Create force simulation
      │
      ├──→ forceX (column constraint)
      ├──→ forceY (vertical spread)
      ├──→ forceLink (edge connections)
      └──→ forceCollide (no overlap)
      │
      ▼
Render edges
      │
      ├──→ Draw lines
      ├──→ Add arrows
      └──→ Style by type
      │
      ▼
Render nodes
      │
      ├──→ Draw shapes (circle/rect/diamond)
      ├──→ Add labels (node ID)
      ├──→ Color by type
      └──→ Add hover effects
      │
      ▼
Attach event handlers
      │
      ├──→ Zoom/pan
      ├──→ Node click
      ├──→ Reset button
      └──→ Keyboard shortcuts
      │
      ▼
Start simulation
      │
      └──→ Update positions on each tick
```

### 4. Interaction Flow

```
User Action                Handler                Result
─────────────────────────────────────────────────────────────
Mouse wheel             │ d3.zoom()           │ Scale transform
                        │                     │ Update SVG viewBox
                        │                     │
Click + Drag            │ d3.zoom()           │ Translate transform
                        │                     │ Update SVG position
                        │                     │
Click Node              │ handleNodeClick()   │ 1. Highlight node
                        │                     │ 2. Highlight edges
                        │                     │ 3. Show detail panel
                        │                     │ 4. Display content
                        │                     │
Click Reset             │ resetView()         │ 1. Transition to identity
                        │                     │ 2. Reset zoom level
                        │                     │ 3. Center graph
                        │                     │
Hover Node              │ CSS :hover          │ 1. Brightness increase
                        │                     │ 2. Show tooltip
                        │                     │ 3. Cursor change
```

## Visual Design System

### Color Palette

```
Node Types:
  Outcome (O)        #4A90E2  ████  Blue
  Specification (S)  #7ED321  ████  Green
  Test (T)           #F5A623  ████  Orange
  Code (C)           #BD10E0  ████  Purple

Edge Types:
  implements         #333333  ████  Dark Gray (solid)
  verifies           #F5A623  ████  Orange (dashed)
  depends_on         #999999  ████  Light Gray (dotted)

UI Elements:
  Background         #F8F9FA  ████  Light Gray
  Grid Lines         #E0E0E0  ████  Very Light Gray
  Selected Glow      #FFD700  ████  Gold
  Panel Background   #FFFFFF  ████  White
```

### Node Shapes

```
Outcome (O):
  ┌─────┐
  │  ○  │  Circle, r=30
  └─────┘

Specification (S):
  ┌─────┐
  │ ▭   │  Rectangle, 50x50
  └─────┘

Test (T):
  ┌─────┐
  │ ◇   │  Diamond, 50x50 rotated
  └─────┘

Code (C):
  ┌─────┐
  │ ▭   │  Rectangle, 50x50
  └─────┘
```

### Layout Grid

```
     200px   300px   300px   300px
    ◄────►  ◄────►  ◄────►  ◄────►
    
    x=200   x=500   x=800   x=1100
      │       │       │       │
      │       │       │       │
  ┌───┴───┬───┴───┬───┴───┬───┴───┐
  │   O   │   S   │   T   │   C   │
  │       │       │       │       │
  │  ○    │  ▭    │  ◇    │  ▭    │
  │       │       │       │       │
  │  ○────┼──▭────┼──◇────┼──▭    │
  │       │       │       │       │
  │  ○    │  ▭    │  ◇    │  ▭    │
  │   │   │   │   │   │   │   │   │
  │   └───┼───┴───┼───┴───┼───┘   │
  │       │       │       │       │
  └───────┴───────┴───────┴───────┘
  
  Vertical spacing: Dynamic (force simulation)
  Horizontal spacing: Fixed (column constraint)
```

## Performance Characteristics

### Complexity Analysis

```
Operation              Time Complexity    Notes
─────────────────────────────────────────────────────────────
Initial Parse          O(n)               n = nodes + edges
Force Simulation       O(n²) per tick     With collision detection
Render Nodes           O(n)               One-time setup
Render Edges           O(e)               e = edges
Zoom/Pan               O(1)               Transform only
Node Click             O(n + e)           Highlight connected
Search (future)        O(n)               Linear scan
```

### Optimization Strategies

```
Scale           Strategy                    Reason
─────────────────────────────────────────────────────────────
< 100 nodes     Full force simulation       Fast enough
100-500 nodes   Simplified forces           Reduce ticks
> 500 nodes     Static layout + Canvas      SVG too slow
> 1000 nodes    Virtualization              Only render visible
```

## File Structure

```
docs/viz-tool/
│
├── PROPOSAL.md              # This document
├── ARCHITECTURE.md          # Detailed architecture (this file)
├── README.md                # Quick start guide
│
├── generate-viz.py          # Generation script
│   ├── read_graph_index()
│   ├── read_node_files()
│   ├── build_json()
│   └── embed_in_template()
│
├── template.html            # HTML template
│   ├── <style>              # CSS
│   ├── <div#controls>       # UI controls
│   ├── <div#graph>          # SVG container
│   ├── <div#detail>         # Detail panel
│   ├── <script#data>        # Embedded JSON
│   └── <script>             # Visualization code
│       ├── loadData()
│       ├── initGraph()
│       ├── renderNodes()
│       ├── renderEdges()
│       ├── handleZoom()
│       ├── handleNodeClick()
│       └── resetView()
│
└── jig-graph-viz.html       # Generated output (gitignored)
```

## Extension Points

### Adding New Node Types

```javascript
// 1. Add to column mapping
const COLUMNS = {
  outcome: 200,
  specification: 500,
  test: 800,
  code: 1100,
  goal: 0,           // NEW: Add before outcomes
  constraint: 1400   // NEW: Add after code
};

// 2. Add to style mapping
const NODE_STYLES = {
  // ... existing ...
  goal: {
    color: '#E74C3C',  // Red
    shape: 'star',
    size: 40
  }
};

// 3. Update rendering logic
function renderNode(node) {
  if (node.type === 'goal') {
    // Custom rendering for goals
  }
}
```

### Adding New Edge Types

```javascript
// 1. Add to style mapping
const EDGE_STYLES = {
  // ... existing ...
  blocks: {
    color: '#E74C3C',
    width: 3,
    style: 'solid',
    arrow: true
  }
};

// 2. Update rendering
function renderEdge(edge) {
  const style = EDGE_STYLES[edge.type];
  // Apply style...
}
```

### Adding Subsystem Grouping

```javascript
// 1. Calculate subsystem bounds
function calculateSubsystemBounds(subsystem) {
  const nodes = subsystem.nodes.map(id => nodeById[id]);
  return {
    x: d3.min(nodes, d => d.x) - 50,
    y: d3.min(nodes, d => d.y) - 50,
    width: d3.max(nodes, d => d.x) - d3.min(nodes, d => d.x) + 100,
    height: d3.max(nodes, d => d.y) - d3.min(nodes, d => d.y) + 100
  };
}

// 2. Render background rectangles
function renderSubsystems() {
  svg.selectAll('.subsystem-bg')
    .data(subsystems)
    .enter()
    .append('rect')
    .attr('class', 'subsystem-bg')
    .attr('fill', d => subsystemColor(d.name))
    .attr('opacity', 0.1)
    .attr('rx', 10);
}
```

## Testing Strategy

### Unit Tests (Future)

```javascript
describe('Layout Engine', () => {
  test('assigns correct column X coordinates', () => {
    const nodes = [
      { id: 'O-001', type: 'outcome' },
      { id: 'S-001', type: 'specification' }
    ];
    applyColumnConstraints(nodes);
    expect(nodes[0].x).toBe(200);
    expect(nodes[1].x).toBe(500);
  });
});

describe('Node Rendering', () => {
  test('renders correct shape for each type', () => {
    // ...
  });
});
```

### Integration Tests

```python
# test_generate_viz.py
def test_generate_from_graph_index():
    """Test that generate-viz.py produces valid HTML."""
    result = subprocess.run(['python', 'generate-viz.py'], 
                          capture_output=True)
    assert result.returncode == 0
    assert os.path.exists('jig-graph-viz.html')
    
    # Validate HTML
    with open('jig-graph-viz.html') as f:
        html = f.read()
        assert '<script src="https://d3js.org/d3.v7.min.js">' in html
        assert 'graph-data' in html
```

### Manual Testing Checklist

- [ ] Graph loads without errors
- [ ] All nodes are visible
- [ ] All edges are visible
- [ ] Nodes are in correct columns
- [ ] Zoom in/out works smoothly
- [ ] Pan works in all directions
- [ ] Reset button returns to default view
- [ ] Clicking node shows detail panel
- [ ] Detail panel displays correct content
- [ ] Closing detail panel works
- [ ] No console errors
- [ ] Performance is acceptable (60 FPS)

## Deployment

### Build Process

```bash
# 1. Generate visualization
cd docs/viz-tool
python generate-viz.py

# 2. Verify output
open jig-graph-viz.html

# 3. (Optional) Commit to git if desired
git add jig-graph-viz.html
git commit -m "Update graph visualization"
```

### CI/CD Integration (Future)

```yaml
# .github/workflows/generate-viz.yml
name: Generate Visualization
on:
  push:
    paths:
      - 'jig/graph-index.yaml'
      - 'jig/**/*.md'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate viz
        run: |
          cd docs/viz-tool
          python generate-viz.py
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: visualization
          path: docs/viz-tool/jig-graph-viz.html
```

---

**End of Architecture Document**

