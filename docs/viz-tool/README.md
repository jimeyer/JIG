# JIG Intent Graph Visualization Tool

A self-contained HTML visualization tool for exploring the JIG Intent Graph structure.

## Quick Start

```bash
# Generate the visualization
python generate-viz.py

# Open in browser
open jig-graph-viz.html
```

## Features

- **Column Layout**: O-S-T-C nodes arranged left-to-right
- **Interactive**: Zoom, pan, and click nodes to view details
- **Self-Contained**: Single HTML file, works offline
- **Fast**: Renders in <1 second for typical graphs

## Files

- `PROPOSAL.md` - Detailed design document
- `generate-viz.py` - Script to generate visualization from graph-index.yaml
- `jig-graph-viz.html` - Generated visualization (not in git)

## Usage

### Viewing the Graph

1. Generate the visualization: `python generate-viz.py`
2. Open `jig-graph-viz.html` in any modern browser
3. Use mouse wheel to zoom, drag to pan
4. Click "Reset View" button to return to default view
5. Click any node to see its details

### Controls

- **Mouse Wheel**: Zoom in/out
- **Click + Drag**: Pan around
- **Click Node**: View node details
- **Reset Button**: Return to default view

### Keyboard Shortcuts (planned)

- `R` - Reset view
- `+` / `-` - Zoom in/out
- `ESC` - Close detail panel
- `F` - Fit to screen

## Implementation Status

See `PROPOSAL.md` for detailed implementation plan.

**Current Phase**: Proposal Complete

**Next Steps**:
1. Implement Phase 1: Core Visualization (MVP)
2. Implement Phase 2: Interactivity
3. Implement Phase 3: Generation Script
4. Implement Phase 4: Polish & Features

## Requirements

- Python 3.8+ (for generation script)
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- No build tools or dependencies required

## Architecture

- **Technology**: D3.js v7 + Vanilla JavaScript
- **Format**: Single HTML file with embedded data
- **Layout**: Force-directed with column constraints
- **Data Source**: `jig/graph-index.yaml` + node files

## Contributing

See `PROPOSAL.md` Section 4 (Implementation Plan) for development phases and priorities.

## License

Same as parent project.

