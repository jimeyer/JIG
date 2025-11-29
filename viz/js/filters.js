/**
 * Filters - Filter nodes and edges by type
 *
 * This module provides filtering logic for nodes and edges.
 */

/**
 * Filter nodes by type
 *
 * @jig.implements("S-010")
 *
 * @param {Array} nodes - Array of node objects
 * @param {Array} types - Array of node types to include (e.g., ['class', 'function'])
 * @returns {Array} Filtered array of nodes
 */
export function filterNodesByType(nodes, types) {
    if (!types || types.length === 0) {
        return [];
    }

    const typeSet = new Set(types);
    return nodes.filter(node => typeSet.has(node.type));
}

/**
 * Filter edges by type
 *
 * @jig.implements("S-011")
 *
 * @param {Array} edges - Array of edge objects
 * @param {Array} types - Array of edge types to include (e.g., ['contains', 'implements'])
 * @returns {Array} Filtered array of edges
 */
export function filterEdgesByType(edges, types) {
    if (!types || types.length === 0) {
        return [];
    }

    const typeSet = new Set(types);
    return edges.filter(edge => typeSet.has(edge.type));
}

/**
 * Apply filters to Cytoscape instance
 *
 * @jig.implements("S-010", "S-011")
 *
 * @param {Object} cy - Cytoscape instance
 * @param {Set} nodeTypes - Set of node types to show
 * @param {Set} edgeTypes - Set of edge types to show
 */
export function applyFilters(cy, nodeTypes, edgeTypes) {
    if (!cy) return;

    // Show/hide nodes based on type
    cy.nodes().forEach(node => {
        const nodeType = node.data('type');
        if (nodeTypes.has(nodeType)) {
            node.style('display', 'element');
        } else {
            node.style('display', 'none');
        }
    });

    // Show/hide edges based on type
    cy.edges().forEach(edge => {
        const edgeType = edge.data('type');
        if (edgeTypes.has(edgeType)) {
            edge.style('display', 'element');
        } else {
            edge.style('display', 'none');
        }
    });
}
