/**
 * JIG Implementation Graph Visualizer - Main Application Entry Point
 *
 * This module initializes the application and wires up event handlers.
 * Actual functionality will be implemented in subsequent work units.
 */

import { loadGraphFile, loadGraphFromURL } from './graph-loader.js';
import { renderGraph, applyLayout } from './graph-renderer.js';
import { setupInteractions, setupZoomControls } from './graph-interactions.js';
import { applyFilters } from './filters.js';
import { searchNodes, highlightSearchResults, clearSearchHighlights } from './search.js';
import { showNodeDetails } from './details-panel.js';

// Application state (will be expanded in later work units)
const state = {
    cy: null,              // Cytoscape instance
    graph: null,           // Parsed graph data
    selectedLayout: 'hierarchical',  // Current layout algorithm
    searchResults: [],     // Current search results
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

    // Layout selector
    // @jig.implements("S-016")
    document.getElementById('layout-select').addEventListener('change', (event) => {
        const layoutName = event.target.value;
        state.selectedLayout = layoutName;

        if (state.cy) {
            console.log(`Applying layout: ${layoutName}`);
            applyLayout(state.cy, layoutName);
        }
    });

    // Filter checkboxes
    // @jig.implements("S-010", "S-011")
    setupFilterHandlers();

    // Search input
    // @jig.implements("S-012")
    setupSearchHandler();
}

/**
 * Setup filter checkbox event handlers
 *
 * @jig.implements("S-010", "S-011")
 */
function setupFilterHandlers() {
    // Node type filters
    const nodeTypeCheckboxes = [
        { id: 'filter-class', type: 'class' },
        { id: 'filter-function', type: 'function' },
        { id: 'filter-module', type: 'module' },
        { id: 'filter-external', type: 'external_module' }
    ];

    nodeTypeCheckboxes.forEach(({ id, type }) => {
        document.getElementById(id).addEventListener('change', (event) => {
            if (event.target.checked) {
                state.filters.nodeTypes.add(type);
            } else {
                state.filters.nodeTypes.delete(type);
            }
            updateFilters();
        });
    });

    // Edge type filters
    const edgeTypeCheckboxes = [
        { id: 'filter-contains', type: 'contains' },
        { id: 'filter-implements', type: 'implements' },
        { id: 'filter-imports', type: 'imports' }
    ];

    edgeTypeCheckboxes.forEach(({ id, type }) => {
        document.getElementById(id).addEventListener('change', (event) => {
            if (event.target.checked) {
                state.filters.edgeTypes.add(type);
            } else {
                state.filters.edgeTypes.delete(type);
            }
            updateFilters();
        });
    });
}

/**
 * Update graph filters based on current state
 *
 * @jig.implements("S-010", "S-011")
 */
function updateFilters() {
    if (!state.cy) return;

    console.log('Applying filters:', {
        nodeTypes: Array.from(state.filters.nodeTypes),
        edgeTypes: Array.from(state.filters.edgeTypes)
    });

    applyFilters(state.cy, state.filters.nodeTypes, state.filters.edgeTypes);
}

/**
 * Setup search input event handler
 *
 * @jig.implements("S-012")
 */
function setupSearchHandler() {
    const searchInput = document.getElementById('search-input');
    const searchResultsDiv = document.getElementById('search-results');

    searchInput.addEventListener('input', (event) => {
        const query = event.target.value;

        if (!state.graph) {
            return;
        }

        // Search through nodes
        const results = searchNodes(state.graph.nodes, query);
        state.searchResults = results;

        console.log(`Search query: "${query}", found ${results.length} results`);

        // Update search results display
        displaySearchResults(results);

        // Highlight matching nodes in graph
        if (state.cy) {
            if (query.trim() === '') {
                clearSearchHighlights(state.cy);
            } else {
                const matchingIds = results.map(node => node.id);
                highlightSearchResults(state.cy, matchingIds);
            }
        }
    });

    // Clear search on escape key
    searchInput.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
        }
    });
}

/**
 * Display search results in the results panel
 *
 * @jig.implements("S-012")
 *
 * @param {Array} results - Array of matching nodes
 */
function displaySearchResults(results) {
    const searchResultsDiv = document.getElementById('search-results');

    if (results.length === 0) {
        searchResultsDiv.innerHTML = '<div class="search-no-results">No matches</div>';
        return;
    }

    // Limit to first 10 results
    const displayResults = results.slice(0, 10);

    let html = '<ul class="search-results-list">';
    displayResults.forEach(node => {
        html += `<li class="search-result-item" data-node-id="${escapeHtml(node.id)}">`;
        html += `<div class="search-result-name">${escapeHtml(node.name || node.id)}</div>`;
        html += `<div class="search-result-type">${escapeHtml(node.type)}</div>`;
        html += '</li>';
    });
    html += '</ul>';

    if (results.length > 10) {
        html += `<div class="search-more">+${results.length - 10} more results</div>`;
    }

    searchResultsDiv.innerHTML = html;

    // Wire up click handlers for results
    searchResultsDiv.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
            const nodeId = item.getAttribute('data-node-id');
            selectAndCenterNode(nodeId);
        });
    });
}

/**
 * Select and center a node in the graph
 *
 * @jig.implements("S-012")
 *
 * @param {string} nodeId - ID of node to select
 */
function selectAndCenterNode(nodeId) {
    if (!state.cy) return;

    const node = state.cy.getElementById(nodeId);
    if (node.length === 0) return;

    // Deselect all and select this node
    state.cy.elements().removeClass('highlighted');
    node.addClass('highlighted');

    // Center the node with animation
    state.cy.animate({
        center: {
            eles: node
        },
        zoom: 1.5,
        duration: 500
    });

    // Show node details (reuse existing details panel functionality)
    showNodeDetails(node.data());

    console.log(`Selected node: ${nodeId}`);
}

/**
 * HTML escape utility
 */
function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) return '';
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
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

        // Render graph
        state.cy = renderGraph(graph.elements);

        // Apply the currently selected layout
        applyLayout(state.cy, state.selectedLayout);

        // Setup interactions (click handlers, zoom controls)
        setupInteractions(state.cy);
        setupZoomControls(state.cy);

        console.log('Graph rendered successfully');

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

        // Render graph
        state.cy = renderGraph(graph.elements);

        // Apply the currently selected layout
        applyLayout(state.cy, state.selectedLayout);

        // Setup interactions (click handlers, zoom controls)
        setupInteractions(state.cy);
        setupZoomControls(state.cy);

        console.log('Default graph rendered successfully');

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
