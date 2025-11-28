/**
 * JIG Implementation Graph Visualizer - Main Application Entry Point
 *
 * This module initializes the application and wires up event handlers.
 * Actual functionality will be implemented in subsequent work units.
 */

import { loadGraphFile, loadGraphFromURL } from './graph-loader.js';

// Application state (will be expanded in later work units)
const state = {
    cy: null,              // Cytoscape instance
    graph: null,           // Parsed graph data
    filters: {
        nodeTypes: new Set(['class', 'function', 'module', 'external_module']),
        edgeTypes: new Set(['contains', 'implements', 'imports'])
    }
};

/**
 * Initialize the application on page load
 */
function init() {
    console.log('JIG Visualizer initializing...');

    // Wire up event handlers
    setupEventHandlers();

    // Try to load default graph
    tryLoadDefaultGraph();

    console.log('JIG Visualizer ready');
}

/**
 * Setup event handlers for UI controls
 */
function setupEventHandlers() {
    // Load graph button
    document.getElementById('load-graph-btn').addEventListener('click', () => {
        document.getElementById('file-input').click();
    });

    // File input change
    document.getElementById('file-input').addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (file) {
            await handleGraphLoad(file);
        }
    });

    // Help button
    document.getElementById('help-btn').addEventListener('click', () => {
        alert('JIG Implementation Graph Visualizer\n\nLoad a .ndjson graph file to visualize your codebase structure.\n\nSee README.md for more information.');
    });

    // Filter checkboxes (will be wired up in WU5)
    // Layout selector (will be wired up in WU7)
    // Zoom controls (will be wired up in WU4)
}

/**
 * Handle loading a graph file
 *
 * @jig.implements("S-017")
 */
async function handleGraphLoad(file) {
    // Show loading spinner
    document.getElementById('loading-spinner').style.display = 'flex';
    document.getElementById('empty-state').style.display = 'none';

    try {
        console.log('Loading graph from file:', file.name);
        const graph = await loadGraphFile(file);

        // Store in state
        state.graph = graph;

        // Update stats
        updateStats(graph.metadata);

        // Log to console for manual testing
        console.log('Graph loaded successfully:');
        console.log('- Metadata:', graph.metadata);
        console.log('- Nodes:', graph.nodes.length);
        console.log('- Edges:', graph.edges.length);
        console.log('- Cytoscape elements:', graph.elements.length);
        console.log('Full graph object:', graph);

        // Hide loading spinner
        document.getElementById('loading-spinner').style.display = 'none';

        // Will render graph in WU3
        // renderGraph(graph.elements);

    } catch (err) {
        console.error('Failed to load graph:', err);
        alert(`Failed to load graph: ${err.message}`);

        // Hide loading spinner, show empty state
        document.getElementById('loading-spinner').style.display = 'none';
        document.getElementById('empty-state').style.display = 'flex';
    }
}

/**
 * Update statistics display
 */
function updateStats(metadata) {
    const nodeCount = metadata.node_count || 0;
    const edgeCount = metadata.edge_count || 0;
    const timestamp = metadata.generated || '-';

    document.getElementById('stats-nodes').textContent = `Nodes: ${nodeCount}`;
    document.getElementById('stats-edges').textContent = `Edges: ${edgeCount}`;
    document.getElementById('stats-timestamp').textContent = `Generated: ${new Date(timestamp).toLocaleString()}`;
}

/**
 * Try to load the default graph file
 *
 * @jig.implements("S-017")
 */
async function tryLoadDefaultGraph() {
    const defaultPath = '../jig/generated/implementation-graph.ndjson';

    try {
        console.log('Attempting to load default graph from:', defaultPath);
        const graph = await loadGraphFromURL(defaultPath);

        // Store in state
        state.graph = graph;

        // Update stats
        updateStats(graph.metadata);

        console.log('Default graph loaded successfully');

        // Will render graph in WU3
        // renderGraph(graph.elements);

    } catch (err) {
        console.log('Default graph not available:', err.message);
        // This is expected - just show empty state
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for testing (if needed)
export { state, init };
