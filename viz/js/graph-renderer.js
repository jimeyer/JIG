/**
 * Graph Renderer - Render graphs using Cytoscape.js
 *
 * This module handles rendering graphs with styled nodes and edges.
 */

/**
 * Get Cytoscape stylesheet for nodes and edges
 *
 * @jig.implements("S-008", "S-009")
 */
function getCytoscapeStylesheet() {
    return [
        // Base node style
        {
            selector: 'node',
            style: {
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'font-size': '12px',
                'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'color': '#333',
                'text-wrap': 'wrap',
                'text-max-width': '120px',
                'border-width': 2,
                'border-color': '#666',
                'background-color': '#e3f2fd',
                'width': 60,
                'height': 40
            }
        },

        // Class nodes - rectangles
        {
            selector: 'node[type="class"]',
            style: {
                'shape': 'rectangle',
                'background-color': '#bbdefb',
                'border-color': '#1976d2',
                'width': 80,
                'height': 50
            }
        },

        // Function nodes - circles/ellipses
        {
            selector: 'node[type="function"]',
            style: {
                'shape': 'ellipse',
                'background-color': '#c8e6c9',
                'border-color': '#388e3c',
                'width': 60,
                'height': 60
            }
        },

        // Module nodes - rounded rectangles
        {
            selector: 'node[type="module"]',
            style: {
                'shape': 'round-rectangle',
                'background-color': '#fff9c4',
                'border-color': '#f57f17',
                'width': 100,
                'height': 40
            }
        },

        // External module nodes - different color
        {
            selector: 'node[type="external_module"]',
            style: {
                'shape': 'round-rectangle',
                'background-color': '#f5f5f5',
                'border-color': '#9e9e9e',
                'border-style': 'dashed',
                'width': 100,
                'height': 40
            }
        },

        // Nodes with implements field - highlighted border
        {
            selector: 'node[implements]',
            style: {
                'border-width': 3,
                'border-color': '#d32f2f'
            }
        },

        // Selected nodes
        {
            selector: 'node:selected',
            style: {
                'border-width': 4,
                'border-color': '#ff6f00',
                'background-color': '#ffe0b2'
            }
        },

        // Base edge style
        {
            selector: 'edge',
            style: {
                'width': 2,
                'line-color': '#999',
                'target-arrow-color': '#999',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'arrow-scale': 1.5
            }
        },

        // Contains edges - thick solid lines
        {
            selector: 'edge[type="contains"]',
            style: {
                'width': 3,
                'line-color': '#1976d2',
                'target-arrow-color': '#1976d2',
                'line-style': 'solid'
            }
        },

        // Implements edges - dashed lines
        {
            selector: 'edge[type="implements"]',
            style: {
                'width': 2,
                'line-color': '#d32f2f',
                'target-arrow-color': '#d32f2f',
                'line-style': 'dashed'
            }
        },

        // Imports edges - thin lines
        {
            selector: 'edge[type="imports"]',
            style: {
                'width': 1.5,
                'line-color': '#388e3c',
                'target-arrow-color': '#388e3c',
                'line-style': 'solid'
            }
        },

        // Selected edges
        {
            selector: 'edge:selected',
            style: {
                'width': 4,
                'line-color': '#ff6f00',
                'target-arrow-color': '#ff6f00'
            }
        },

        // Highlighted elements (via .highlighted class)
        {
            selector: '.highlighted',
            style: {
                'opacity': 1,
                'z-index': 999
            }
        },

        // Non-highlighted elements when something is highlighted
        {
            selector: 'node.highlighted, edge.highlighted',
            style: {
                'opacity': 1
            }
        },

        // Search match highlighting
        {
            selector: '.search-match',
            style: {
                'border-width': 4,
                'border-color': '#ff6f00',
                'background-color': '#ffe0b2',
                'z-index': 998
            }
        }
    ];
}

/**
 * Render graph using Cytoscape.js
 *
 * @jig.implements("S-008", "S-009")
 *
 * @param {Array} elements - Cytoscape elements (nodes and edges)
 * @param {Object} container - DOM element to render into (defaults to #cy)
 * @returns {Object} Cytoscape instance
 */
export function renderGraph(elements, container = null) {
    const containerElement = container || document.getElementById('cy');

    if (!containerElement) {
        throw new Error('Graph container element not found');
    }

    // Initialize Cytoscape
    const cy = cytoscape({
        container: containerElement,
        elements: elements,
        style: getCytoscapeStylesheet(),
        layout: {
            name: 'preset'  // Will apply layout separately
        },
        minZoom: 0.01,  // Allow zooming way out to see large graphs
        maxZoom: 5,     // Allow zooming way in for details
        wheelSensitivity: 0.2
    });

    // Apply hierarchical layout by default
    applyLayout(cy, 'hierarchical-cols');

    // Show the canvas, hide empty state
    containerElement.classList.remove('hidden');
    document.getElementById('empty-state').style.display = 'none';

    return cy;
}

/**
 * Apply a layout to the graph
 *
 * @jig.implements("S-016")
 *
 * @param {Object} cy - Cytoscape instance
 * @param {string} layoutName - Name of layout (hierarchical, hierarchical-cols, force-directed, circular, grid)
 */
export function applyLayout(cy, layoutName = 'hierarchical') {
    let layoutOptions = {};
    let fitPadding = 50;  // Default fit padding for zoom-to-fit

    switch (layoutName) {
        case 'hierarchical': {
            // Spacing controls for vertical hierarchical layout
            const verticalSpacing = 1.5;  // Controls spacing between rows
            const horizontalSpacing = 1.5;  // Controls spacing within rows
            const edgePadding = 30;
            fitPadding = 50;  // Padding when fitting to viewport
            
            layoutOptions = {
                name: 'breadthfirst',
                directed: true,
                spacingFactor: verticalSpacing,
                padding: edgePadding,
                animate: true,
                animationDuration: 500
            };
            break;
        }

        case 'hierarchical-cols': {
            // Spacing controls for horizontal hierarchical layout
            // Note: x/y are swapped after layout, so:
            // - spacingFactor controls VERTICAL spacing before swap = HORIZONTAL after swap
            // - We compress vertically after swap by scaling y coordinates
            const horizontalSpacing = 2.0;  // Controls spacing between columns (left-to-right)
            const verticalCompression = 0.15;  // How much to compress vertically (lower = more compressed)
            const edgePadding = 3;
            fitPadding = 10;  // Padding when fitting to viewport (smaller = more zoomed in)
            
            layoutOptions = {
                name: 'breadthfirst',
                directed: true,
                spacingFactor: horizontalSpacing,
                padding: edgePadding,
                animate: true,
                animationDuration: 500,
                grid: false,
                avoidOverlap: true,
                nodeDimensionsIncludeLabels: true,
                fit: true,
                circle: false,
                // Store compression factor for use after layout
                _verticalCompression: verticalCompression
            };
            break;
        }

        case 'force-directed': {
            // Spacing controls for force-directed layout
            const nodeRepulsion = 8000;  // How strongly nodes push apart
            const edgeLength = 100;  // Ideal distance between connected nodes
            const edgeElasticity = 100;  // How strongly edges pull nodes together
            const gravity = 80;  // How strongly nodes are pulled to center
            fitPadding = 50;  // Padding when fitting to viewport
            
            layoutOptions = {
                name: 'cose',
                animate: true,
                animationDuration: 1000,
                nodeRepulsion: nodeRepulsion,
                idealEdgeLength: edgeLength,
                edgeElasticity: edgeElasticity,
                nestingFactor: 5,
                gravity: gravity,
                numIter: 1000,
                initialTemp: 200,
                coolingFactor: 0.95,
                minTemp: 1.0
            };
            break;
        }

        case 'circular': {
            // Spacing controls for circular layout
            const spacing = 1.5;  // Controls spacing around the circle
            const edgePadding = 30;
            fitPadding = 50;  // Padding when fitting to viewport
            
            layoutOptions = {
                name: 'circle',
                animate: true,
                animationDuration: 500,
                padding: edgePadding,
                spacingFactor: spacing
            };
            break;
        }

        case 'grid': {
            // Spacing controls for grid layout
            const gridSpacing = 1.5;  // Controls spacing between grid cells
            const edgePadding = 30;
            fitPadding = 50;  // Padding when fitting to viewport
            
            layoutOptions = {
                name: 'grid',
                animate: true,
                animationDuration: 500,
                padding: edgePadding,
                spacingFactor: gridSpacing,
                avoidOverlap: true
            };
            break;
        }

        default:
            console.warn(`Unknown layout: ${layoutName}, using hierarchical`);
            layoutOptions = {
                name: 'breadthfirst',
                directed: true,
                spacingFactor: 1.5,
                padding: 30
            };
    }

    const layout = cy.layout(layoutOptions);

    // For hierarchical-cols, we need to transform positions after layout
    if (layoutName === 'hierarchical-cols') {
        layout.one('layoutstop', () => {
            const compression = layoutOptions._verticalCompression || 1.0;
            
            // Swap x and y coordinates to convert vertical layout to horizontal
            // and apply vertical compression
            cy.nodes().forEach(node => {
                const pos = node.position();
                node.position({
                    x: pos.y,
                    y: pos.x * compression  // Compress vertically
                });
            });
            // Fit the graph after transformation
            cy.fit(fitPadding);
        });
    }

    // Store the fitPadding on the cy instance so zoom controls can use it
    cy.scratch('_fitPadding', fitPadding);

    layout.run();

    return layout;
}

/**
 * Update graph with new elements
 *
 * @param {Object} cy - Cytoscape instance
 * @param {Array} elements - New Cytoscape elements
 * @param {string} layoutName - Layout to apply (defaults to 'hierarchical')
 */
export function updateGraph(cy, elements, layoutName = 'hierarchical') {
    cy.elements().remove();
    cy.add(elements);
    applyLayout(cy, layoutName);
}
