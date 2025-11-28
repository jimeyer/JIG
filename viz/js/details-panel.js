/**
 * Details Panel - Display node and edge metadata
 *
 * This module handles displaying detailed information about selected elements.
 */

/**
 * Show node details in the details panel
 *
 * @jig.implements("S-013")
 *
 * @param {Object} nodeData - Cytoscape node data object
 */
export function showNodeDetails(nodeData) {
    const panel = document.getElementById('details-panel');

    // Build details HTML
    let html = '<dl class="details-list">';

    // ID
    html += '<dt>ID</dt>';
    html += `<dd><code>${escapeHtml(nodeData.id)}</code></dd>`;

    // Type
    html += '<dt>Type</dt>';
    html += `<dd>${escapeHtml(nodeData.type)}</dd>`;

    // Name
    if (nodeData.name) {
        html += '<dt>Name</dt>';
        html += `<dd>${escapeHtml(nodeData.name)}</dd>`;
    }

    // Language
    if (nodeData.language) {
        html += '<dt>Language</dt>';
        html += `<dd>${escapeHtml(nodeData.language)}</dd>`;
    }

    // File path
    if (nodeData.file) {
        html += '<dt>File</dt>';
        html += `<dd><code>${escapeHtml(nodeData.file)}</code></dd>`;
    }

    // Line number
    if (nodeData.line !== undefined) {
        html += '<dt>Line</dt>';
        html += `<dd>${nodeData.line}</dd>`;
    }

    // Function-specific fields
    if (nodeData.type === 'function') {
        // Signature
        if (nodeData.signature) {
            html += '<dt>Signature</dt>';
            html += `<dd><code>${escapeHtml(nodeData.signature)}</code></dd>`;
        }

        // Parent class (for methods)
        if (nodeData.parent_class) {
            html += '<dt>Parent Class</dt>';
            html += `<dd><code>${escapeHtml(nodeData.parent_class)}</code></dd>`;
        }

        // Async flag
        if (nodeData.async !== undefined) {
            html += '<dt>Async</dt>';
            html += `<dd>${nodeData.async ? 'Yes' : 'No'}</dd>`;
        }
    }

    // Class-specific fields
    if (nodeData.type === 'class') {
        // Base classes
        if (nodeData.bases && nodeData.bases.length > 0) {
            html += '<dt>Bases</dt>';
            html += '<dd>';
            nodeData.bases.forEach((base, i) => {
                if (i > 0) html += ', ';
                html += `<code>${escapeHtml(base)}</code>`;
            });
            html += '</dd>';
        }
    }

    // Implements field (for any node type)
    if (nodeData.implements && nodeData.implements.length > 0) {
        html += '<dt>Implements</dt>';
        html += '<dd>';
        nodeData.implements.forEach((specId, i) => {
            if (i > 0) html += ', ';
            html += `<code>${escapeHtml(specId)}</code>`;
        });
        html += '</dd>';
    }

    html += '</dl>';

    panel.innerHTML = html;
}

/**
 * Show edge details in the details panel
 *
 * @jig.implements("S-014")
 *
 * @param {Object} edgeData - Cytoscape edge data object
 */
export function showEdgeDetails(edgeData) {
    const panel = document.getElementById('details-panel');

    // Build details HTML
    let html = '<dl class="details-list">';

    // Type
    html += '<dt>Edge Type</dt>';
    html += `<dd>${formatEdgeType(edgeData.type)}</dd>`;

    // Source
    html += '<dt>Source</dt>';
    html += `<dd><code>${escapeHtml(edgeData.source)}</code></dd>`;

    // Target
    html += '<dt>Target</dt>';
    html += `<dd><code>${escapeHtml(edgeData.target)}</code></dd>`;

    // Line number (for imports)
    if (edgeData.line !== undefined) {
        html += '<dt>Line</dt>';
        html += `<dd>${edgeData.line}</dd>`;
    }

    html += '</dl>';

    // Add note about clickable nodes
    html += '<p style="margin-top: 16px; font-size: 12px; color: #666; font-style: italic;">Click a node to see its details</p>';

    panel.innerHTML = html;
}

/**
 * Clear the details panel
 */
export function clearDetails() {
    const panel = document.getElementById('details-panel');
    panel.innerHTML = '<p class="details-empty">Select a node or edge to see details</p>';
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) {
        return '';
    }
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * Format edge type for display
 */
function formatEdgeType(type) {
    const typeMap = {
        'contains': 'Contains',
        'implements': 'Implements',
        'imports': 'Imports',
        'calls': 'Calls',
        'verifies': 'Verifies'
    };
    return typeMap[type] || type;
}
