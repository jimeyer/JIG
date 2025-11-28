/**
 * Graph Interactions - Handle user interactions with the graph
 *
 * This module handles click events, hover effects, and other interactions.
 */

import { showNodeDetails, showEdgeDetails, clearDetails } from './details-panel.js';

/**
 * Setup interaction handlers for a Cytoscape instance
 *
 * @jig.implements("S-013", "S-014", "S-015")
 *
 * @param {Object} cy - Cytoscape instance
 */
export function setupInteractions(cy) {
    if (!cy) {
        console.warn('Cannot setup interactions: Cytoscape instance is null');
        return;
    }

    // Node click handler
    cy.on('tap', 'node', (event) => {
        const node = event.target;
        const nodeData = node.data();

        console.log('Node clicked:', nodeData);

        // Show node details in panel
        showNodeDetails(nodeData);

        // Highlight node and neighbors
        highlightElement(cy, node);
    });

    // Edge click handler
    cy.on('tap', 'edge', (event) => {
        const edge = event.target;
        const edgeData = edge.data();

        console.log('Edge clicked:', edgeData);

        // Show edge details in panel
        showEdgeDetails(edgeData);

        // Highlight edge
        highlightElement(cy, edge);
    });

    // Click on background (deselect)
    cy.on('tap', (event) => {
        // Only handle background clicks (not nodes or edges)
        if (event.target === cy) {
            cy.elements().removeClass('highlighted');
            clearDetails();
            console.log('Background clicked - selection cleared');
        }
    });

    console.log('Graph interactions initialized');
}

/**
 * Highlight an element and its connections
 *
 * @param {Object} cy - Cytoscape instance
 * @param {Object} element - Node or edge to highlight
 */
function highlightElement(cy, element) {
    // Remove previous highlights
    cy.elements().removeClass('highlighted');

    // Add highlight class to selected element
    element.addClass('highlighted');

    // If it's a node, also highlight connected edges
    if (element.isNode()) {
        element.connectedEdges().addClass('highlighted');
    }

    // If it's an edge, also highlight connected nodes
    if (element.isEdge()) {
        element.connectedNodes().addClass('highlighted');
    }
}

/**
 * Setup zoom and pan controls
 *
 * @jig.implements("S-015")
 *
 * @param {Object} cy - Cytoscape instance
 */
export function setupZoomControls(cy) {
    if (!cy) {
        console.warn('Cannot setup zoom controls: Cytoscape instance is null');
        return;
    }

    // Zoom to Fit button
    const zoomFitBtn = document.getElementById('zoom-fit-btn');
    if (zoomFitBtn) {
        zoomFitBtn.addEventListener('click', () => {
            cy.fit(null, 50); // 50px padding
            console.log('Zoom to fit');
        });
    }

    // Reset button (zoom to fit + clear selection)
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            cy.fit(null, 50);
            cy.elements().removeClass('highlighted');
            clearDetails();
            console.log('View reset');
        });
    }

    console.log('Zoom controls initialized');
}
