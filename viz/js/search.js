/**
 * Search - Fuzzy search for nodes by name/ID
 *
 * This module provides fuzzy search functionality using Fuse.js.
 */

/**
 * Search nodes by name or ID using fuzzy matching
 *
 * @jig.implements("S-012")
 *
 * @param {Array} nodes - Array of node objects
 * @param {string} query - Search query string
 * @returns {Array} Array of matching nodes sorted by relevance
 */
export function searchNodes(nodes, query) {
    // Empty query returns all nodes
    if (!query || query.trim() === '') {
        return nodes;
    }

    // Configure Fuse.js for fuzzy search
    const options = {
        keys: ['name', 'id'],
        threshold: 0.4,  // 0 = exact match, 1 = match anything
        includeScore: true,
        ignoreLocation: true,  // Don't penalize matches based on position
        minMatchCharLength: 1
    };

    const fuse = new Fuse(nodes, options);
    const results = fuse.search(query);

    // Extract items from Fuse.js results
    return results.map(result => result.item);
}

/**
 * Highlight search results in the graph
 *
 * @jig.implements("S-012")
 *
 * @param {Object} cy - Cytoscape instance
 * @param {Array} matchingNodeIds - Array of node IDs to highlight
 */
export function highlightSearchResults(cy, matchingNodeIds) {
    if (!cy) return;

    const idSet = new Set(matchingNodeIds);

    cy.nodes().forEach(node => {
        if (idSet.has(node.id())) {
            node.addClass('search-match');
        } else {
            node.removeClass('search-match');
        }
    });
}

/**
 * Clear search highlights from the graph
 *
 * @jig.implements("S-012")
 *
 * @param {Object} cy - Cytoscape instance
 */
export function clearSearchHighlights(cy) {
    if (!cy) return;
    cy.nodes().removeClass('search-match');
}
