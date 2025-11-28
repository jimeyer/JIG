/**
 * JIG Implementation Graph Visualizer - Main Application Entry Point
 *
 * This module initializes the application and wires up event handlers.
 * Actual functionality will be implemented in subsequent work units.
 */

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
    // (Will be implemented in WU2: Graph Loading)
    // tryLoadDefaultGraph();

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
    document.getElementById('file-input').addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            console.log('File selected:', file.name);
            // loadGraphFile(file) - will be implemented in WU2
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
 * Try to load the default graph file
 * (Will be implemented in WU2)
 */
function tryLoadDefaultGraph() {
    // const defaultPath = '../jig/generated/implementation-graph.ndjson';
    // fetch(defaultPath).then(...).catch(...)
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for testing (if needed)
export { state, init };
