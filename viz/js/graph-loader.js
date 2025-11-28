/**
 * Graph Loader - Parse NDJSON implementation graphs
 *
 * This module handles loading and parsing NDJSON graph files.
 */

/**
 * Parse NDJSON content into structured graph data
 *
 * @jig.implements("S-007")
 *
 * @param {string} content - Raw NDJSON content
 * @returns {Object} Parsed graph with metadata, nodes, and edges
 * @throws {Error} If JSON parsing fails
 */
export function parseNDJSON(content) {
    if (!content || content.trim() === '') {
        return {
            metadata: {},
            nodes: [],
            edges: []
        };
    }

    const lines = content.trim().split('\n');
    const metadata = {};
    const nodes = [];
    const edges = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        try {
            const obj = JSON.parse(line);

            // First line is metadata
            if (i === 0 && obj._meta) {
                Object.assign(metadata, obj._meta);
            }
            // Lines with source/target are edges
            else if (obj.source && obj.target) {
                edges.push(obj);
            }
            // Everything else is a node
            else if (obj.id && obj.type) {
                nodes.push(obj);
            }
        } catch (err) {
            throw new Error(`Invalid JSON at line ${i + 1}: ${err.message}`);
        }
    }

    return { metadata, nodes, edges };
}

/**
 * Convert parsed graph data to Cytoscape elements format
 *
 * @jig.implements("S-007")
 *
 * @param {Object} graph - Parsed graph from parseNDJSON
 * @returns {Array} Array of Cytoscape elements (nodes and edges)
 */
export function toCytoscapeElements(graph) {
    const elements = [];

    // Add nodes
    for (const node of graph.nodes) {
        elements.push({
            group: 'nodes',
            data: {
                id: node.id,
                label: node.name || node.id,
                ...node
            }
        });
    }

    // Add edges
    for (const edge of graph.edges) {
        elements.push({
            group: 'edges',
            data: {
                id: `${edge.source}-${edge.target}-${edge.type}`,
                source: edge.source,
                target: edge.target,
                label: edge.type,
                ...edge
            }
        });
    }

    return elements;
}

/**
 * Load and parse a graph file
 *
 * @jig.implements("S-017")
 *
 * @param {File} file - File object from file input
 * @returns {Promise<Object>} Promise that resolves to parsed graph with elements
 */
export async function loadGraphFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = (event) => {
            try {
                const content = event.target.result;
                const graph = parseNDJSON(content);
                const elements = toCytoscapeElements(graph);

                resolve({
                    metadata: graph.metadata,
                    nodes: graph.nodes,
                    edges: graph.edges,
                    elements: elements
                });
            } catch (err) {
                reject(new Error(`Failed to parse graph: ${err.message}`));
            }
        };

        reader.onerror = () => {
            reject(new Error(`Failed to read file: ${reader.error.message}`));
        };

        reader.readAsText(file);
    });
}

/**
 * Fetch and load a graph from a URL
 *
 * @jig.implements("S-017")
 *
 * @param {string} url - URL to fetch graph from
 * @returns {Promise<Object>} Promise that resolves to parsed graph with elements
 */
export async function loadGraphFromURL(url) {
    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const content = await response.text();
        const graph = parseNDJSON(content);
        const elements = toCytoscapeElements(graph);

        return {
            metadata: graph.metadata,
            nodes: graph.nodes,
            edges: graph.edges,
            elements: elements
        };
    } catch (err) {
        throw new Error(`Failed to load graph from URL: ${err.message}`);
    }
}
