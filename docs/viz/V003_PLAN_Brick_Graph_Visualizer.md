# PLAN: Brick Graph Visualizer

- **SCOPE**: Brick visualization using Cytoscape compound nodes
- **Depends On**: V002 (Implementation Graph Visualizer)
- **Start**: 2025-11-30
- **Status**: Draft
- **Branch**: TBD

## Overview

This plan extends the implementation graph visualizer to support brick visualization using Cytoscape compound nodes. The architecture follows A001 strictly:

```
Existing graphs per A001 §6:
  - intent-graph.ndjson (specs, outcomes, bricks)
  - implementation-graph.ndjson (pure, no brick info)

Viz tool:
  - Loads both graphs
  - Computes brick membership at query time (A001 §6.2)
  - Renders as Cytoscape compound nodes
```

**Key Architectural Principles** (per A001):
1. ✅ Only 3 graph types exist (A001 §6)
2. ✅ Implementation graph stays pure - no `brick` or `parent` fields (A001 §6.2)
3. ✅ Brick assignment computed at query time by joining (A001 §6.2, §9)
4. ✅ Intent graph contains brick nodes with metadata (A001 §6.1)
5. ✅ No circular dependencies - graphs generated before brick assignment

## Known Intent (Created Before Coding)

**Outcomes**:
- O-009: Developers can generate intent graph from specs, outcomes, and bricks.yaml
- O-010: Developers can visualize bricks as compound nodes with boundaries and labels
- O-011: Developers can interact with bricks (collapse/expand, filter, navigate)

**Specifications**:
- S-028: CLI command to generate intent-graph.ndjson (A001 §6.1)
- S-029: Viz loads and joins intent + implementation graphs
- S-030: Compute brick membership from bricks.yaml units at query time
- S-031: Render compound nodes with brick boundaries and labels
- S-032: Collapse/expand brick functionality
- S-033: Filter nodes by brick membership
- S-034: Layout algorithms respect compound node structure

**Bricks Affected**:
- B-002: CLI Interface (new `jigy intent rebuild` command)
- None for viz tool (standalone tool in viz/ folder)

## Work Unit Checklist

- [x] WU0: Create Intent nodes (O/S)
- [ ] WU1: Implement intent-graph generator (CLI)
- [ ] WU2: Multi-graph loading in viz
- [ ] WU3: Compute brick membership at query time
- [ ] WU4: Compound node rendering
- [ ] WU5: Brick interactions (collapse/expand)
- [ ] WU6: Brick filtering UI
- [ ] WU7: Layout integration and polish

## Work Units

### Work Unit 0: Create Known Intent

**Goal**: Capture all known Outcomes and Specifications before writing any code.

**Acceptance Criteria**:
- [ ] All known "why" statements → Outcome files in `jig/outcomes/`
- [ ] All known "what" requirements → Specification files in `jig/specifications/`
- [ ] All files have proper YAML frontmatter
- [ ] `jigy validate` passes
- [ ] Sample intent-graph created: `viz/tests/fixtures/sample-intent-graph.ndjson`

**Created Nodes**:
- O-009: Generate intent graph
- O-010: Visualize bricks as compound nodes
- O-011: Interact with bricks
- S-028: CLI intent-graph command
- S-029: Multi-graph loading
- S-030: Brick membership computation
- S-031: Compound node rendering
- S-032: Collapse/expand
- S-033: Brick filtering
- S-034: Layout integration

**Implementation Notes**:
1. Review A001 §6.1 for intent-graph schema
2. Create outcomes focusing on "why" brick visualization matters
3. Create specifications with concrete acceptance criteria
4. Create sample intent-graph.ndjson per A001 format

**Reflect**:
- What was clear: A001 §6.1 schema for intent graph nodes; outcome vs spec distinction (why vs what); sample fixture format with metadata, nodes, and edges
- What was ambiguous: Whether to include `implements` field in outcome frontmatter (decided to omit, following O-007/O-008 pattern)
- Surprises: Brick nodes need `units` array included in intent-graph despite A001 §6.1 not explicitly showing it - necessary for query-time joining
- Process win/improvement: Creating all intent artifacts before coding ensures complete specification; parallel structure of outcomes (value-focused) and specs (acceptance criteria) worked well

**Human Verification**:

Commands to run:
```bash
# Check that outcome files exist
ls -la jig/outcomes/O-009.md jig/outcomes/O-010.md jig/outcomes/O-011.md

# Check that spec files exist
ls -la jig/specifications/S-028.md jig/specifications/S-029.md jig/specifications/S-030.md jig/specifications/S-031.md jig/specifications/S-032.md jig/specifications/S-033.md jig/specifications/S-034.md

# Validate frontmatter format
head -5 jig/outcomes/O-009.md
head -5 jig/specifications/S-028.md

# Check sample fixture exists
ls -la viz/tests/fixtures/sample-intent-graph.ndjson
head -20 viz/tests/fixtures/sample-intent-graph.ndjson
```

Actions to verify:
- [ ] Open each outcome file, verify YAML frontmatter has `id` and `type` fields
- [ ] Read outcome bodies, verify they explain "why" brick visualization matters
- [ ] Open each spec file, verify clear acceptance criteria
- [ ] Verify spec S-028 describes CLI command for intent graph generation
- [ ] Verify spec S-030 describes brick membership computation at query time
- [ ] Read sample-intent-graph.ndjson, verify it has spec nodes, outcome nodes, and brick nodes
- [ ] Check brick nodes have `units` arrays with M-/C-/F- prefixes

**Links**:
- Commit: a33fbab

---

### Work Unit 1: Implement Intent Graph Generator

**Goal**: Create CLI command to generate intent-graph.ndjson per A001 §6.1.

**Planned Effort**: 2-3 hours

**Acceptance Criteria**:
- [ ] `jigy intent rebuild` command exists
- [ ] Command reads all `jig/specifications/S-*.md` frontmatter
- [ ] Command reads all `jig/outcomes/O-*.md` frontmatter (if present)
- [ ] Command reads `jig/bricks.yaml`
- [ ] Command generates `jig/generated/intent-graph.ndjson` per A001 §6.1
- [ ] Spec nodes follow A001 schema: `{"id":"S-001","type":"specification","file":"..."}`
- [ ] Outcome nodes follow A001 schema: `{"id":"O-001","type":"outcome","file":"...","specifies":[...]}`
- [ ] Brick nodes follow A001 schema: `{"id":"B-001","type":"brick","name":"...","file":"jig/bricks.yaml"}`
- [ ] Brick nodes include `units` array from bricks.yaml (for viz joining)
- [ ] Unit tests cover all node types
- [ ] Command has `--help` documentation

**Implementation Notes**:

**Intent Graph Format** (per A001 §6.1, with units extension):

```
Line 1: Metadata
{"_meta": {"version": "1.0", "generated": "ISO-timestamp", "spec_count": 27, "outcome_count": 8, "brick_count": 5}}

Lines 2+: Specification nodes
{"id":"S-001","type":"specification","file":"jig/specifications/S-001.md"}
{"id":"S-002","type":"specification","file":"jig/specifications/S-002.md"}
...

Lines: Outcome nodes (if any)
{"id":"O-001","type":"outcome","file":"jig/outcomes/O-001.md","specifies":["S-001","S-002"]}
{"id":"O-002","type":"outcome","file":"jig/outcomes/O-002.md","specifies":["S-003"]}
...

Lines: Brick nodes
{"id":"B-001","type":"brick","name":"JIG Core Decorators","file":"jig/bricks.yaml","units":["M-jig.__init__"]}
{"id":"B-002","type":"brick","name":"CLI Interface","file":"jig/bricks.yaml","units":["M-jig.cli.main","M-jig.cli.validate"]}
...

Lines: Edges (O→S specifies relationships)
{"source":"O-001","target":"S-001","type":"specifies"}
{"source":"O-001","target":"S-002","type":"specifies"}
...
```

**Note on `units` field**: A001 §6.1 doesn't explicitly show `units` on brick nodes, but since:
- Intent graph is "Generated from: bricks.yaml" (A001 §6.1)
- Units are needed for query-time joining (A001 §6.2, §9)
- It's static data from bricks.yaml (not derived)

Including `units` on brick nodes is a reasonable extension of A001.

**Algorithm**:
```python
def generate_intent_graph(project_root: Path, output_path: Path):
    # 1. Load and parse all spec files
    specs = load_specifications(project_root / "jig/specifications")

    # 2. Load and parse all outcome files (optional)
    outcomes = load_outcomes(project_root / "jig/outcomes")

    # 3. Load bricks.yaml
    bricks = load_bricks_yaml(project_root / "jig/bricks.yaml")

    # 4. Create nodes
    spec_nodes = [{"id": s.id, "type": "specification", "file": s.file} for s in specs]
    outcome_nodes = [{"id": o.id, "type": "outcome", "file": o.file, "specifies": o.specifies} for o in outcomes]
    brick_nodes = [{"id": b.id, "type": "brick", "name": b.name, "file": "jig/bricks.yaml", "units": b.units} for b in bricks]

    # 5. Create edges (O→S specifies)
    edges = []
    for outcome in outcomes:
        for spec_id in outcome.specifies:
            edges.append({"source": outcome.id, "target": spec_id, "type": "specifies"})

    # 6. Create metadata
    metadata = {
        "_meta": {
            "version": "1.0",
            "generated": datetime.now(timezone.utc).isoformat(),
            "spec_count": len(specs),
            "outcome_count": len(outcomes),
            "brick_count": len(bricks)
        }
    }

    # 7. Write NDJSON
    write_ndjson(output_path, metadata, spec_nodes + outcome_nodes + brick_nodes, edges)
```

**CLI Interface**:
```bash
jigy intent rebuild [OPTIONS]

Generate intent-graph.ndjson from specifications, outcomes, and bricks.

Options:
  --project-root PATH   Project root directory [default: .]
  --output PATH         Output path [default: jig/generated/intent-graph.ndjson]
  --help                Show this message and exit
```

**Files to Create/Modify**:
- `src/jig/cli/main.py` - Add `intent` group and `rebuild` command
- `src/jig/intent_graph/generator.py` - Core logic
- `tests/jig/intent_graph/test_generator.py` - Unit tests

**Test Cases**:
1. Spec nodes have correct schema
2. Outcome nodes include specifies array
3. Brick nodes include name and units array
4. Edges created for O→S relationships
5. Metadata includes counts
6. Empty outcomes handled gracefully
7. Multiple bricks handled correctly

**Approach**:
1. Create intent_graph module
2. Implement parsers for specs/outcomes/bricks
3. Implement generator logic
4. Write unit tests
5. Add CLI command with Click
6. Test end-to-end with real data

**Reflect**:
- What was clear:
- What was ambiguous:
- Surprises:
- Process win/improvement:

**Human Verification**:

Commands to run:
```bash
# Run the intent rebuild command
jigy intent rebuild

# Verify output file exists
ls -lh jig/generated/intent-graph.ndjson

# Check first 30 lines to see metadata + sample nodes
head -30 jig/generated/intent-graph.ndjson

# Count node types
grep '"type":"specification"' jig/generated/intent-graph.ndjson | wc -l
grep '"type":"outcome"' jig/generated/intent-graph.ndjson | wc -l
grep '"type":"brick"' jig/generated/intent-graph.ndjson | wc -l

# Check brick nodes have units arrays
grep '"type":"brick"' jig/generated/intent-graph.ndjson | head -3

# Verify metadata line
head -1 jig/generated/intent-graph.ndjson | jq '._meta'

# Run tests
python -m pytest tests/jig/intent_graph/ -v
```

Actions to verify:
- [ ] Command runs without errors
- [ ] Output file created at `jig/generated/intent-graph.ndjson`
- [ ] First line contains `_meta` with `spec_count`, `outcome_count`, `brick_count`
- [ ] Spec nodes match schema: `{"id":"S-001","type":"specification","file":"..."}`
- [ ] Outcome nodes include `specifies` array
- [ ] Brick nodes include `name` and `units` arrays
- [ ] Brick units use M-/C-/F- prefixes
- [ ] Count matches: 27 specs, 8 outcomes, 5 bricks (current state)
- [ ] Help text displays: `jigy intent rebuild --help`
- [ ] All unit tests pass

**Links**:
- Commit:

---

### Work Unit 2: Multi-Graph Loading in Viz

**Goal**: Update viz to load both intent-graph and implementation-graph.

**Planned Effort**: 2 hours

**Acceptance Criteria**:
- [ ] Viz can load intent-graph.ndjson
- [ ] Viz can load implementation-graph.ndjson
- [ ] Viz can load both graphs simultaneously
- [ ] Graph selection UI added to header
- [ ] Loading state handles multiple files
- [ ] Error handling for missing graphs
- [ ] Console logs show which graphs loaded

**Implementation Notes**:

**UI Updates** (in `index.html`):
```html
<div class="header-controls">
    <button id="load-graph-btn" class="btn btn-primary">Load Graphs</button>
    <div class="graph-selection">
        <label><input type="checkbox" id="load-intent" checked> Intent</label>
        <label><input type="checkbox" id="load-impl" checked> Implementation</label>
        <label><input type="checkbox" id="load-verify"> Verification</label>
    </div>
    <button id="help-btn" class="btn btn-secondary">Help</button>
</div>
```

**Multi-Graph State** (in `main.js`):
```javascript
const state = {
    cy: null,
    graphs: {
        intent: null,        // Intent graph data
        impl: null,          // Implementation graph data
        verify: null         // Verification graph data
    },
    bricks: new Map(),       // B-001 → brick node data
    selectedLayout: 'hierarchical-cols',
    filters: { ... }
};
```

**Loading Logic** (in `graph-loader.js`):
```javascript
export async function loadMultipleGraphs(files) {
    const results = {};

    for (const file of files) {
        const graph = await loadGraphFile(file);

        // Detect graph type from nodes
        if (graph.nodes.some(n => n.type === 'brick')) {
            results.intent = graph;
        } else if (graph.nodes.some(n => n.type === 'function')) {
            results.impl = graph;
        } else if (graph.nodes.some(n => n.type === 'test')) {
            results.verify = graph;
        }
    }

    return results;
}
```

**Auto-load Default Graphs** (in `main.js`):
```javascript
async function tryLoadDefaultGraphs() {
    const paths = {
        intent: '../jig/generated/intent-graph.ndjson',
        impl: '../jig/generated/implementation-graph.ndjson'
    };

    for (const [type, path] of Object.entries(paths)) {
        try {
            const graph = await loadGraphFromURL(path);
            state.graphs[type] = graph;
            console.log(`${type} graph loaded:`, graph.metadata);
        } catch (err) {
            console.log(`${type} graph not available:`, err.message);
        }
    }

    // Extract bricks from intent graph
    if (state.graphs.intent) {
        extractBricks(state.graphs.intent);
    }
}

function extractBricks(intentGraph) {
    const brickNodes = intentGraph.nodes.filter(n => n.type === 'brick');
    brickNodes.forEach(brick => {
        state.bricks.set(brick.id, brick);
    });
    console.log(`Extracted ${state.bricks.size} bricks from intent graph`);
}
```

**Approach**:
1. Update file input to accept multiple files
2. Implement multi-graph loading logic
3. Update state management for multiple graphs
4. Extract brick data from intent graph
5. Update UI to show which graphs are loaded
6. Test with both graphs loaded

**Files to Modify**:
- `viz/index.html` - Add graph selection UI
- `viz/js/graph-loader.js` - Multi-graph loading
- `viz/js/main.js` - State management and auto-load
- `viz/css/controls.css` - Style graph selection

**Reflect**:
- What was clear:
- What was ambiguous:
- Surprises:
- Process win/improvement:

**Human Verification**:

Commands to run:
```bash
# Start viz server (if not already running)
cd viz
python3 -m http.server 8000

# Open browser
open http://localhost:8000

# Check console (open browser DevTools)
# Should see logs like:
#   "intent graph loaded: ..."
#   "impl graph loaded: ..."
#   "Extracted N bricks from intent graph"
```

Actions to verify:
- [ ] Open browser at http://localhost:8000
- [ ] Open DevTools console (F12 or Cmd+Option+I)
- [ ] Verify console shows: "intent graph loaded"
- [ ] Verify console shows: "impl graph loaded"
- [ ] Verify console shows: "Extracted 5 bricks from intent graph"
- [ ] Check header shows graph selection checkboxes (Intent, Implementation, Verification)
- [ ] Intent and Implementation checkboxes should be checked by default
- [ ] Click "Load Graph" button, select a file, verify multi-file loading works
- [ ] Refresh page, verify both graphs auto-load
- [ ] Check no errors in console

**Links**:
- Commit:

---

### Work Unit 3: Compute Brick Membership at Query Time

**Goal**: Implement brick membership computation per A001 §6.2, §9.

**Planned Effort**: 2-3 hours

**Acceptance Criteria**:
- [ ] Brick units expanded to function IDs (M-* → all F-* in module)
- [ ] Implementation nodes matched to bricks via units
- [ ] Parent-child relationships computed in memory
- [ ] No modification to graph data on disk
- [ ] Console logs show membership computation results
- [ ] Unit tests cover module expansion logic
- [ ] Unit tests cover ID matching logic

**Implementation Notes**:

**Brick Membership Computation** (new file: `viz/js/brick-membership.js`):

```javascript
/**
 * Compute brick membership from intent graph bricks and impl graph nodes
 * Per A001 §6.2: "Brick assignment SHALL be computed at query time"
 *
 * @jig.implements("S-030")
 */

/**
 * Expand brick units to concrete function IDs
 *
 * Units format (per A001 §4):
 * - M-{module.path} → all F-* in that module
 * - C-{class.path} → all F-* methods of that class
 * - F-{function.path} → exactly that function
 */
export function expandBrickUnits(bricks, implNodes) {
    const brickMembership = new Map(); // Function ID → Brick ID

    for (const brick of bricks.values()) {
        const expandedUnits = new Set();

        for (const unit of brick.units) {
            if (unit.startsWith('M-')) {
                // Module: expand to all functions/classes/modules with this prefix
                const prefix = unit;
                implNodes.forEach(node => {
                    if (node.id.startsWith(prefix)) {
                        expandedUnits.add(node.id);
                    }
                });
            } else if (unit.startsWith('C-')) {
                // Class: expand to class itself + all methods
                const prefix = unit;
                implNodes.forEach(node => {
                    if (node.id === unit || node.id.startsWith(prefix + '.')) {
                        expandedUnits.add(node.id);
                    }
                });
            } else if (unit.startsWith('F-')) {
                // Function: exact match
                expandedUnits.add(unit);
            }
        }

        // Record membership
        for (const unitId of expandedUnits) {
            brickMembership.set(unitId, brick.id);
        }
    }

    return brickMembership;
}

/**
 * Validate brick partition constraint (A001 §10)
 * Every function SHALL belong to exactly one brick
 */
export function validateBrickPartition(brickMembership, implNodes) {
    const functions = implNodes.filter(n => n.type === 'function');
    const errors = [];

    for (const func of functions) {
        const brickId = brickMembership.get(func.id);
        if (!brickId) {
            errors.push(`Function ${func.id} not in any brick (partition gap)`);
        }
    }

    if (errors.length > 0) {
        console.warn('Brick partition violations:', errors);
    }

    return errors;
}
```

**Integration** (in `main.js`):
```javascript
import { expandBrickUnits, validateBrickPartition } from './brick-membership.js';

async function tryLoadDefaultGraphs() {
    // ... load graphs ...

    if (state.graphs.intent && state.graphs.impl) {
        // Extract bricks
        const bricks = extractBricks(state.graphs.intent);

        // Compute brick membership (A001 §6.2)
        state.brickMembership = expandBrickUnits(bricks, state.graphs.impl.nodes);
        console.log(`Computed brick membership for ${state.brickMembership.size} nodes`);

        // Validate partition (A001 §10)
        const errors = validateBrickPartition(state.brickMembership, state.graphs.impl.nodes);
        if (errors.length === 0) {
            console.log('✓ Brick partition valid (all functions in exactly one brick)');
        }
    }
}
```

**Test Cases** (in `viz/tests/test-brick-membership.js`):
1. M-module expands to all child functions
2. C-class expands to class + methods
3. F-function matches exactly
4. Multiple bricks don't overlap
5. All functions assigned to exactly one brick
6. Nested modules handled correctly

**Approach**:
1. Create brick-membership.js module
2. Implement expansion logic for M-/C-/F- prefixes
3. Implement partition validation
4. Wire into main.js after graph loading
5. Write unit tests
6. Test with real data

**Files to Create/Modify**:
- `viz/js/brick-membership.js` - NEW: Core logic
- `viz/js/main.js` - Integration
- `viz/tests/test-brick-membership.js` - NEW: Unit tests

**Reflect**:
- What was clear:
- What was ambiguous:
- Surprises:
- Process win/improvement:

**Human Verification**:

Commands to run:
```bash
# Open browser with DevTools console
open http://localhost:8000

# Run unit tests for brick membership logic
cd viz
# Open viz/tests/test.html in browser to run Mocha tests
open tests/test.html
```

Actions to verify:
- [ ] Open browser at http://localhost:8000
- [ ] Open DevTools console
- [ ] Verify console shows: "Computed brick membership for N nodes"
- [ ] Verify console shows: "✓ Brick partition valid (all functions in exactly one brick)"
- [ ] If partition violations exist, should see warnings with specific function IDs
- [ ] Type in console: `state.brickMembership` - should see Map with entries
- [ ] Type in console: `state.brickMembership.size` - should show count
- [ ] Type in console: `state.brickMembership.get('M-jig.__init__')` - should return 'B-001'
- [ ] Open viz/tests/test.html, verify brick-membership tests pass (green)
- [ ] Tests should cover M- expansion, C- expansion, F- exact match
- [ ] No errors in console during membership computation

**Links**:
- Commit:

---

### Work Unit 4: Compound Node Rendering

**Goal**: Render bricks as Cytoscape compound nodes with computed parent relationships.

**Planned Effort**: 2-3 hours

**Acceptance Criteria**:
- [ ] Brick nodes created from intent graph brick nodes
- [ ] Implementation nodes assigned parent field from computed membership
- [ ] Cytoscape compound nodes render correctly
- [ ] Brick boundaries visible
- [ ] Brick labels display at top
- [ ] Member nodes positioned inside brick boundaries
- [ ] Manual test: load graphs shows brick containers
- [ ] Console logs confirm compound structure

**Implementation Notes**:

**Create Cytoscape Elements** (in `graph-renderer.js`):

```javascript
/**
 * Create Cytoscape elements from multiple graphs with computed brick membership
 *
 * @jig.implements("S-031")
 */
export function createCompoundElements(intentGraph, implGraph, brickMembership) {
    const elements = [];

    // 1. Add brick nodes (parent containers) from intent graph
    if (intentGraph) {
        const brickNodes = intentGraph.nodes.filter(n => n.type === 'brick');
        brickNodes.forEach(brick => {
            elements.push({
                group: 'nodes',
                data: {
                    id: brick.id,
                    type: 'brick',
                    name: brick.name,
                    label: brick.name,
                    units: brick.units  // for display/debugging
                }
            });
        });
    }

    // 2. Add implementation nodes with parent field from computed membership
    if (implGraph) {
        implGraph.nodes.forEach(node => {
            const parent = brickMembership.get(node.id);  // Computed at query time

            elements.push({
                group: 'nodes',
                data: {
                    ...node,
                    label: node.name || node.id,
                    parent: parent  // Set parent for compound node structure
                }
            });
        });

        // Add edges
        implGraph.edges.forEach(edge => {
            elements.push({
                group: 'edges',
                data: edge
            });
        });
    }

    return elements;
}
```

**Update Render Flow** (in `main.js`):
```javascript
async function handleGraphLoad() {
    // ... load graphs ...
    // ... compute brick membership ...

    // Create Cytoscape elements with compound structure
    const elements = createCompoundElements(
        state.graphs.intent,
        state.graphs.impl,
        state.brickMembership
    );

    // Render graph
    state.cy = renderGraph(elements);

    // Apply layout
    applyLayout(state.cy, state.selectedLayout);
}
```

**Stylesheet for Bricks** (in `graph-renderer.js` stylesheet):
```javascript
// Brick container nodes
{
    selector: 'node[type="brick"]',
    style: {
        'shape': 'rectangle',
        'background-color': '#ffffff',
        'background-opacity': 0.05,
        'border-width': 3,
        'border-color': '#1976d2',
        'border-style': 'solid',
        'label': 'data(name)',
        'text-valign': 'top',
        'text-halign': 'center',
        'text-margin-y': -15,
        'font-size': '16px',
        'font-weight': 'bold',
        'color': '#1976d2',
        'padding': '30px',
        'min-width': '200px',
        'min-height': '150px'
    }
},

// Member nodes inside bricks - slightly smaller
{
    selector: 'node[parent]',  // nodes with parent (brick members)
    style: {
        'width': '50px',
        'height': '35px',
        'font-size': '10px'
    }
}
```

**Approach**:
1. Implement createCompoundElements function
2. Update render flow to use compound elements
3. Add brick styling to stylesheet
4. Test with sample data
5. Verify compound structure in browser console
6. Adjust styling for clarity

**Files to Modify**:
- `viz/js/graph-renderer.js` - Compound elements creation and styling
- `viz/js/main.js` - Update render flow
- `viz/tests/fixtures/sample-intent-graph.ndjson` - Test data

**Reflect**:
- What was clear:
- What was ambiguous:
- Surprises:
- Process win/improvement:

**Human Verification**:

Commands to run:
```bash
# Refresh browser to see updated rendering
open http://localhost:8000

# Inspect Cytoscape elements in console
# Type in browser console:
cy.nodes('[type="brick"]').length  # Should show 5 (number of bricks)
cy.nodes('[parent]').length        # Should show count of nodes with parents
```

Actions to verify:
- [ ] Refresh browser at http://localhost:8000
- [ ] **Visual check**: See blue rectangular boundaries around groups of nodes
- [ ] **Visual check**: Brick names appear at top of each container (e.g., "JIG Core Decorators")
- [ ] Count 5 brick containers visible (B-001 through B-005)
- [ ] Member nodes appear inside brick boundaries
- [ ] Brick boundaries have blue borders, semi-transparent background
- [ ] Brick labels are bold, larger font than member nodes
- [ ] Right-click a brick node → Inspect element → verify it has `type="brick"`
- [ ] Right-click a member node → Inspect element → verify it has `parent="B-XXX"`
- [ ] In console, type: `cy.nodes('[type="brick"]')[0].children().length` - should show member count
- [ ] No layout issues - nodes don't overlap brick boundaries
- [ ] Graph fits in viewport, can zoom/pan to see all bricks

**Links**:
- Commit:

---

### Work Unit 5: Brick Interactions (Collapse/Expand)

**Goal**: Implement collapse/expand functionality for brick compound nodes.

**Planned Effort**: 2-3 hours

**Acceptance Criteria**:
- [ ] Double-click brick to collapse
- [ ] Double-click collapsed brick to expand
- [ ] Collapsed bricks show member count badge
- [ ] Collapsed bricks hide member nodes
- [ ] Layout updates when collapsing/expanding
- [ ] Collapsed state persists during layout changes
- [ ] "Expand All" and "Collapse All" buttons work
- [ ] Manual test: collapse/expand in each layout mode

**Implementation Notes**:

**Collapse/Expand Logic** (in `graph-interactions.js`):
```javascript
/**
 * Setup brick collapse/expand interactions
 *
 * @jig.implements("S-032")
 */
export function setupBrickInteractions(cy) {
    // Double-click brick to toggle collapse
    cy.on('dblclick', 'node[type="brick"]', function(evt) {
        const brick = evt.target;
        toggleBrickCollapse(brick, cy);
    });
}

function toggleBrickCollapse(brick, cy) {
    const children = brick.children();
    const isCollapsed = brick.data('collapsed');

    if (isCollapsed) {
        // Expand
        children.show();
        brick.removeData('collapsed');
        brick.removeClass('collapsed');
        console.log(`Expanded brick: ${brick.id()}`);
    } else {
        // Collapse
        children.hide();
        brick.data('collapsed', true);
        brick.addClass('collapsed');
        console.log(`Collapsed brick: ${brick.id()}`);
    }

    // Re-run layout to adjust positions
    const currentLayout = cy.scratch('_currentLayout') || 'hierarchical-cols';
    applyLayout(cy, currentLayout);
}

export function expandAllBricks(cy) {
    cy.nodes('[type="brick"]').forEach(brick => {
        if (brick.data('collapsed')) {
            brick.children().show();
            brick.removeData('collapsed');
            brick.removeClass('collapsed');
        }
    });
    const currentLayout = cy.scratch('_currentLayout') || 'hierarchical-cols';
    applyLayout(cy, currentLayout);
}

export function collapseAllBricks(cy) {
    cy.nodes('[type="brick"]').forEach(brick => {
        if (!brick.data('collapsed')) {
            brick.children().hide();
            brick.data('collapsed', true);
            brick.addClass('collapsed');
        }
    });
    const currentLayout = cy.scratch('_currentLayout') || 'hierarchical-cols';
    applyLayout(cy, currentLayout);
}
```

**UI for Brick Controls** (in `index.html`):
```html
<section class="sidebar-section">
    <h3>Bricks</h3>
    <button id="expand-all-btn" class="btn btn-block">Expand All</button>
    <button id="collapse-all-btn" class="btn btn-block">Collapse All</button>
    <div id="brick-list" class="brick-list"></div>
</section>
```

**Wire Up UI** (in `main.js`):
```javascript
// Brick expand/collapse buttons
document.getElementById('expand-all-btn').addEventListener('click', () => {
    if (state.cy) {
        expandAllBricks(state.cy);
    }
});

document.getElementById('collapse-all-btn').addEventListener('click', () => {
    if (state.cy) {
        collapseAllBricks(state.cy);
    }
});
```

**Collapsed Brick Styling** (in `graph-renderer.js`):
```javascript
// Collapsed bricks - show member count
{
    selector: 'node[type="brick"].collapsed',
    style: {
        'background-color': '#e3f2fd',
        'background-opacity': 0.9,
        'label': function(ele) {
            const memberCount = ele.children().length;
            return `${ele.data('name')} (${memberCount})`;
        }
    }
}
```

**Approach**:
1. Add collapse/expand event handlers
2. Implement toggle logic
3. Add UI buttons
4. Wire up event handlers
5. Add collapsed styling
6. Test across all layouts

**Files to Modify**:
- `viz/js/graph-interactions.js` - Collapse/expand logic
- `viz/index.html` - Brick controls UI
- `viz/js/main.js` - Wire up buttons
- `viz/js/graph-renderer.js` - Collapsed styling
- `viz/css/controls.css` - Style brick controls

**Reflect**:
- What was clear:
- What was ambiguous:
- Surprises:
- Process win/improvement:

**Human Verification**:

Commands to run:
```bash
# Refresh browser
open http://localhost:8000
```

Actions to verify:
- [ ] Refresh browser at http://localhost:8000
- [ ] Locate "Bricks" section in left sidebar
- [ ] See "Expand All" and "Collapse All" buttons
- [ ] **Test double-click collapse**:
  - [ ] Double-click a brick container (e.g., B-001)
  - [ ] Brick should collapse - member nodes hidden
  - [ ] Brick label shows member count: "JIG Core Decorators (4)"
  - [ ] Brick background becomes more opaque
- [ ] **Test double-click expand**:
  - [ ] Double-click the collapsed brick again
  - [ ] Member nodes reappear
  - [ ] Label returns to just brick name
- [ ] **Test Collapse All button**:
  - [ ] Click "Collapse All"
  - [ ] All 5 bricks collapse simultaneously
  - [ ] All show member counts in labels
- [ ] **Test Expand All button**:
  - [ ] Click "Expand All"
  - [ ] All bricks expand
  - [ ] All member nodes visible
- [ ] **Test layout persistence**:
  - [ ] Collapse a brick
  - [ ] Switch layout (e.g., Hierarchical → Force-directed)
  - [ ] Brick remains collapsed after layout change
- [ ] In console, check: `cy.nodes('[type="brick"].collapsed').length` shows collapsed count
- [ ] Console shows "Collapsed brick: B-XXX" / "Expanded brick: B-XXX" messages

**Links**:
- Commit:

---

### Work Unit 6: Brick Filtering UI

**Goal**: Add UI to filter nodes by brick membership.

**Planned Effort**: 2 hours

**Acceptance Criteria**:
- [ ] Brick checkboxes appear in left sidebar
- [ ] Brick list dynamically populated from intent graph
- [ ] Unchecking brick hides all member nodes
- [ ] Unchecking brick hides the brick container
- [ ] Re-checking shows nodes and container
- [ ] "All Bricks" / "No Bricks" toggle buttons
- [ ] Filter state persists during layout changes
- [ ] Works with existing node type filters

**Implementation Notes**:

**Dynamic Brick Filter UI** (in `main.js`):
```javascript
/**
 * Populate brick filter checkboxes from loaded intent graph
 *
 * @jig.implements("S-033")
 */
function populateBrickFilters(intentGraph) {
    const bricks = intentGraph.nodes.filter(n => n.type === 'brick');
    const container = document.getElementById('brick-list');
    container.innerHTML = '';

    bricks.forEach(brick => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `filter-brick-${brick.id}`;
        checkbox.checked = true;
        checkbox.dataset.brickId = brick.id;

        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(` ${brick.name}`));
        container.appendChild(label);

        // Add to filter state
        state.filters.bricks = state.filters.bricks || new Set();
        state.filters.bricks.add(brick.id);

        checkbox.addEventListener('change', updateBrickFilters);
    });

    console.log(`Added ${bricks.length} brick filters`);
}

function updateBrickFilters() {
    if (!state.cy) return;

    // Update filter state
    state.filters.bricks = new Set();
    document.querySelectorAll('[id^="filter-brick-"]').forEach(cb => {
        if (cb.checked) {
            state.filters.bricks.add(cb.dataset.brickId);
        }
    });

    // Show/hide bricks and their children
    state.cy.nodes('[type="brick"]').forEach(brick => {
        if (state.filters.bricks.has(brick.id())) {
            brick.show();
            // Show children unless brick is collapsed
            if (!brick.data('collapsed')) {
                brick.children().show();
            }
        } else {
            brick.hide();
            brick.children().hide();
        }
    });

    // Apply existing node/edge filters
    applyFilters(state.cy, state.filters.nodeTypes, state.filters.edgeTypes);
}
```

**Brick Filter Controls** (already in sidebar from WU5):
```html
<section class="sidebar-section">
    <h3>Bricks</h3>
    <div class="filter-brick-controls">
        <button id="filter-bricks-all" class="btn-small">All</button>
        <button id="filter-bricks-none" class="btn-small">None</button>
    </div>
    <button id="expand-all-btn" class="btn btn-block">Expand All</button>
    <button id="collapse-all-btn" class="btn btn-block">Collapse All</button>
    <div id="brick-list" class="brick-list"></div>
</section>
```

**All/None Toggles** (in `main.js`):
```javascript
document.getElementById('filter-bricks-all').addEventListener('click', () => {
    document.querySelectorAll('[id^="filter-brick-"]').forEach(cb => {
        cb.checked = true;
    });
    updateBrickFilters();
});

document.getElementById('filter-bricks-none').addEventListener('click', () => {
    document.querySelectorAll('[id^="filter-brick-"]').forEach(cb => {
        cb.checked = false;
    });
    updateBrickFilters();
});
```

**Approach**:
1. Populate brick filters when graph loads
2. Implement filter update logic
3. Add All/None toggle buttons
4. Integrate with existing filters
5. Test with multiple bricks

**Files to Modify**:
- `viz/index.html` - Brick filter controls (already added in WU5)
- `viz/js/main.js` - Populate and update logic
- `viz/css/controls.css` - Style brick list

**Reflect**:
- What was clear:
- What was ambiguous:
- Surprises:
- Process win/improvement:

**Human Verification**:

Commands to run:
```bash
# Refresh browser
open http://localhost:8000
```

Actions to verify:
- [ ] Refresh browser at http://localhost:8000
- [ ] Check "Bricks" section in left sidebar
- [ ] See list of brick checkboxes (5 bricks listed)
- [ ] All checkboxes should be checked by default
- [ ] See "All" and "None" buttons above checkbox list
- [ ] **Test individual brick filtering**:
  - [ ] Uncheck "B-002: CLI Interface"
  - [ ] B-002 brick container disappears
  - [ ] All member nodes of B-002 disappear
  - [ ] Other bricks remain visible
  - [ ] Check the checkbox again
  - [ ] B-002 reappears with members
- [ ] **Test "None" button**:
  - [ ] Click "None"
  - [ ] All brick checkboxes uncheck
  - [ ] All bricks and members disappear
  - [ ] Graph appears empty
- [ ] **Test "All" button**:
  - [ ] Click "All"
  - [ ] All checkboxes check
  - [ ] All bricks reappear
- [ ] **Test interaction with collapse**:
  - [ ] Collapse a brick (double-click)
  - [ ] Uncheck that brick's checkbox
  - [ ] Brick disappears
  - [ ] Check checkbox again
  - [ ] Brick reappears still collapsed
- [ ] **Test with node type filters**:
  - [ ] Uncheck "Modules" in node type filters
  - [ ] Module nodes disappear from all bricks
  - [ ] Brick containers remain visible
- [ ] Console shows "Added 5 brick filters" on page load
- [ ] Filter state persists across layout changes

**Links**:
- Commit:

---

### Work Unit 7: Layout Integration and Polish

**Goal**: Ensure all layouts work with compound nodes and polish the UX.

**Planned Effort**: 2-3 hours

**Acceptance Criteria**:
- [ ] Hierarchical (Rows) layout respects compound structure
- [ ] Hierarchical (Columns) layout respects compound structure
- [ ] Force-directed layout keeps brick members together
- [ ] Circular and Grid layouts work with bricks
- [ ] Brick padding/margins visually clear
- [ ] Brick labels don't overlap with member nodes
- [ ] Zoom-to-fit accounts for brick boundaries
- [ ] Performance acceptable with 5+ bricks
- [ ] README updated with brick visualization workflow
- [ ] Help dialog updated with brick features

**Implementation Notes**:

**Layout Tuning for Compound Nodes** (in `graph-renderer.js`):

```javascript
// Force-directed layout with compound node support
case 'force-directed': {
    layoutOptions = {
        name: 'cose',
        animate: true,
        animationDuration: 1000,
        nodeRepulsion: 8000,
        idealEdgeLength: 100,
        edgeElasticity: 100,
        nestingFactor: 1.2,        // Tighter nesting for bricks
        gravity: 80,
        gravityRangeCompound: 1.5, // Gravity for compound nodes
        gravityCompound: 1.0,
        gravityRange: 3.8,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0
    };
    break;
}
```

**README Updates** (in `viz/README.md`):
```markdown
## Brick Visualization

The visualizer can display implementation graphs with brick boundaries using Cytoscape compound nodes.

### Generating Required Graphs

```bash
# 1. Generate intent graph (includes brick definitions)
jigy intent rebuild

# 2. Generate implementation graph (pure, no brick info)
jigy impl rebuild

# Graphs are written to jig/generated/
```

### Using Brick Visualization

1. **Load graphs**: Open viz tool, it auto-loads both graphs
2. **View bricks**: Brick boundaries appear as containers around member nodes
3. **Collapse/expand**: Double-click a brick or use Expand/Collapse All buttons
4. **Filter bricks**: Use checkboxes in left sidebar to show/hide specific bricks
5. **Switch layouts**: All layouts support brick structure

### How It Works (per A001)

- **Intent graph** contains brick nodes with metadata
- **Implementation graph** contains pure code structure (no brick info)
- **Viz tool** computes brick membership at load time by joining:
  - Brick units from intent graph
  - Implementation nodes from impl graph
- **Compound nodes** created with computed parent-child relationships
- **No modification** to graph files on disk

This follows A001 §6.2: "Brick assignment SHALL be computed at query time"
```

**Help Dialog Updates** (in `main.js`):
```javascript
const helpText = `JIG Implementation Graph Visualizer

...existing help text...

BRICK VISUALIZATION:
• Bricks appear as containers with boundaries around member nodes
• Double-click brick to collapse/expand
• Use "Expand All" / "Collapse All" buttons
• Filter bricks with checkboxes in left sidebar
• Brick membership computed from intent-graph.ndjson + bricks.yaml

...rest of help text...`;
```

**Approach**:
1. Test each layout with compound nodes
2. Tune layout parameters for clarity
3. Adjust brick styling for readability
4. Test performance with real data (5+ bricks, 100+ nodes)
5. Update documentation
6. Create demo screenshots

**Files to Modify**:
- `viz/js/graph-renderer.js` - Layout tuning
- `viz/README.md` - Documentation
- `viz/index.html` - Help dialog
- `viz/css/graph.css` - Final styling polish

**Reflect**:
- What was clear:
- What was ambiguous:
- Surprises:
- Process win/improvement:

**Human Verification**:

Commands to run:
```bash
# Refresh browser
open http://localhost:8000

# Check README updates
cat viz/README.md | grep -A 20 "Brick Visualization"

# Verify all graphs generated
ls -lh jig/generated/
```

Actions to verify:
- [ ] Refresh browser at http://localhost:8000
- [ ] **Test all layouts with bricks**:
  - [ ] Hierarchical (Rows): Bricks arranged top-to-bottom, members inside
  - [ ] Hierarchical (Columns): Bricks arranged left-to-right, members inside
  - [ ] Force-directed: Bricks cluster together, members stay within boundaries
  - [ ] Circular: Bricks arranged in circle, members visible inside
  - [ ] Grid: Bricks in grid, members positioned inside
- [ ] **Visual quality checks**:
  - [ ] Brick boundaries clearly visible in all layouts
  - [ ] Brick labels don't overlap member nodes
  - [ ] Adequate padding around member nodes
  - [ ] No visual artifacts or rendering glitches
  - [ ] Zoom to fit includes all brick boundaries
- [ ] **Performance check**:
  - [ ] All 5 bricks + ~125 nodes load within 2 seconds
  - [ ] Layout changes complete within 1 second
  - [ ] Collapse/expand is responsive
  - [ ] No lag when filtering
- [ ] **Documentation**:
  - [ ] Open viz/README.md
  - [ ] See "Brick Visualization" section
  - [ ] Instructions for generating graphs are clear
  - [ ] "How It Works" explains A001 compliance
  - [ ] Help dialog (click Help button) includes brick features
- [ ] **End-to-end workflow**:
  - [ ] Run: `jigy intent rebuild && jigy impl rebuild`
  - [ ] Refresh viz (auto-loads both graphs)
  - [ ] See 5 bricks with boundaries
  - [ ] Collapse B-001, expand it
  - [ ] Filter: uncheck B-002, recheck it
  - [ ] Switch to Force-directed layout
  - [ ] Search for a function, see it highlighted within brick
- [ ] Take screenshot for documentation

**Links**:
- Commit:

---

## Success Criteria

**Phase Complete When**:
1. `jigy intent rebuild` generates valid intent-graph.ndjson per A001 §6.1
2. Viz tool loads both intent-graph and implementation-graph
3. Brick membership computed at query time (A001 §6.2)
4. Bricks render as compound nodes with clear boundaries
5. Users can collapse/expand bricks
6. Users can filter by brick
7. All 5 layouts work with compound nodes
8. Documentation complete

**Demo Scenario**:
```bash
# Generate graphs per A001
jigy intent rebuild   # Creates intent-graph.ndjson
jigy impl rebuild     # Creates implementation-graph.ndjson (already exists)

# Start viz server
cd viz
python3 -m http.server 8000

# Open http://localhost:8000
# Auto-loads both graphs
# See 5 bricks with boundaries (B-001 through B-005)
# Collapse B-001, expand it again
# Filter: uncheck B-002, check it again
# Switch layouts: all work with bricks
# Search for a node in a brick, see it highlighted within brick boundary
```

## Alignment with A001

This plan strictly follows A001:

✅ **§6**: Only 3 graph types (intent, impl, verify) - no 4th graph
✅ **§6.1**: Intent graph includes brick nodes with units
✅ **§6.2**: Implementation graph stays pure (no brick/parent fields)
✅ **§6.2**: "Brick assignment SHALL be computed at query time by joining"
✅ **§9**: Derived data not stored - computed on demand
✅ **§10**: Brick partition validated at query time

**Key Architectural Wins**:
- No modification to implementation-graph.ndjson
- No new graph files created
- Computation happens in viz tool (query time)
- Clean separation per A001 constraints

## Open Questions

1. **Units field on brick nodes**: A001 §6.1 doesn't explicitly show `units` on brick nodes. Should we add it or load bricks.yaml separately in viz?
   - **Proposed**: Include `units` in intent-graph brick nodes since it's static data from bricks.yaml
2. **Performance**: How do compound nodes perform with 10+ bricks?
3. **Cross-Brick Edges**: How to visualize edges between nodes in different bricks?
4. **Empty Bricks**: How to handle bricks with no members (all filtered out)?
5. **Intent Graph Edges**: Should we include O→S specifies edges in the graph?

## Future Enhancements (Not in Scope)

- Brick metrics visualization (alignment scores)
- Drag-and-drop nodes between bricks
- Export brick view as image
- Brick-level search/filtering
- Intent layer overlay (specs/outcomes visualization)
- Brick dependency graph (brick-to-brick relationships)
- Verification graph integration (tests with brick boundaries)

## References

- **A001**: docs/architecture/A001_Core-Artifacts-Contract.md
- **Cytoscape Compound Nodes**: https://js.cytoscape.org/#notation/compound-nodes
- **V002 Plan**: docs/viz/V002_PLAN_Implementation_Graph_Visualizer.md
- **Bricks Whitepaper**: docs/bricks/AG002_Alignment_Graph_Whitepaper.md
