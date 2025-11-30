/**
 * Tests for graph-loader.js
 */

import { parseNDJSON, toCytoscapeElements } from '../js/graph-loader.js';

const { describe, it, expect } = window;

describe('Graph Loader', () => {
    describe('parseNDJSON', () => {
        // @jig.verifies("S-007")
        it('should parse valid NDJSON with metadata, nodes, and edges', () => {
            const ndjson = `{"_meta": {"node_count": 2, "edge_count": 1, "version": "1.0"}}
{"id": "N-001", "type": "class", "name": "MyClass"}
{"id": "N-002", "type": "function", "name": "myFunction"}
{"source": "N-001", "target": "N-002", "type": "contains"}`;

            const result = parseNDJSON(ndjson);

            expect(result).to.have.property('metadata');
            expect(result).to.have.property('nodes');
            expect(result).to.have.property('edges');

            expect(result.metadata.node_count).to.equal(2);
            expect(result.metadata.edge_count).to.equal(1);
            expect(result.metadata.version).to.equal('1.0');

            expect(result.nodes).to.have.lengthOf(2);
            expect(result.edges).to.have.lengthOf(1);
        });

        // @jig.verifies("S-007")
        it('should extract metadata from first line', () => {
            const ndjson = `{"_meta": {"node_count": 5, "version": "2.0", "generated": "2025-11-28"}}`;

            const result = parseNDJSON(ndjson);

            expect(result.metadata.node_count).to.equal(5);
            expect(result.metadata.version).to.equal('2.0');
            expect(result.metadata.generated).to.equal('2025-11-28');
        });

        // @jig.verifies("S-007")
        it('should parse node objects with id and type', () => {
            const ndjson = `{"_meta": {}}
{"id": "C-test", "type": "class", "name": "TestClass", "file": "test.py", "line": 10}
{"id": "F-test", "type": "function", "name": "testFunc", "async": false}`;

            const result = parseNDJSON(ndjson);

            expect(result.nodes).to.have.lengthOf(2);
            expect(result.nodes[0].id).to.equal('C-test');
            expect(result.nodes[0].type).to.equal('class');
            expect(result.nodes[0].name).to.equal('TestClass');
            expect(result.nodes[0].file).to.equal('test.py');
            expect(result.nodes[0].line).to.equal(10);

            expect(result.nodes[1].id).to.equal('F-test');
            expect(result.nodes[1].type).to.equal('function');
            expect(result.nodes[1].async).to.equal(false);
        });

        // @jig.verifies("S-007")
        it('should parse edge objects with source and target', () => {
            const ndjson = `{"_meta": {}}
{"source": "N-001", "target": "N-002", "type": "contains"}
{"source": "N-002", "target": "S-001", "type": "implements", "line": 42}`;

            const result = parseNDJSON(ndjson);

            expect(result.edges).to.have.lengthOf(2);
            expect(result.edges[0].source).to.equal('N-001');
            expect(result.edges[0].target).to.equal('N-002');
            expect(result.edges[0].type).to.equal('contains');

            expect(result.edges[1].source).to.equal('N-002');
            expect(result.edges[1].target).to.equal('S-001');
            expect(result.edges[1].type).to.equal('implements');
            expect(result.edges[1].line).to.equal(42);
        });

        // @jig.verifies("S-007")
        it('should handle empty input', () => {
            const result = parseNDJSON('');

            expect(result.metadata).to.deep.equal({});
            expect(result.nodes).to.deep.equal([]);
            expect(result.edges).to.deep.equal([]);
        });

        // @jig.verifies("S-007")
        it('should handle whitespace-only input', () => {
            const result = parseNDJSON('   \n\n  \n  ');

            expect(result.metadata).to.deep.equal({});
            expect(result.nodes).to.deep.equal([]);
            expect(result.edges).to.deep.equal([]);
        });

        // @jig.verifies("S-007")
        it('should throw error with line number for malformed JSON', () => {
            const ndjson = `{"_meta": {}}
{"id": "N-001", "type": "class"}
{this is not valid json}
{"id": "N-002", "type": "function"}`;

            expect(() => parseNDJSON(ndjson)).to.throw(/Invalid JSON at line 3/);
        });

        // @jig.verifies("S-007")
        it('should skip empty lines', () => {
            const ndjson = `{"_meta": {"node_count": 1}}

{"id": "N-001", "type": "class"}

{"source": "N-001", "target": "N-002", "type": "contains"}
`;

            const result = parseNDJSON(ndjson);

            expect(result.nodes).to.have.lengthOf(1);
            expect(result.edges).to.have.lengthOf(1);
        });
    });

    describe('toCytoscapeElements', () => {
        // @jig.verifies("S-007")
        it('should convert nodes to Cytoscape format', () => {
            const graph = {
                metadata: {},
                nodes: [
                    { id: 'N-001', type: 'class', name: 'TestClass' },
                    { id: 'N-002', type: 'function', name: 'testFunc' }
                ],
                edges: []
            };

            const elements = toCytoscapeElements(graph);

            const nodes = elements.filter(el => el.group === 'nodes');
            expect(nodes).to.have.lengthOf(2);
            expect(nodes[0].data.id).to.equal('N-001');
            expect(nodes[0].data.label).to.equal('TestClass');
            expect(nodes[0].data.type).to.equal('class');
        });

        // @jig.verifies("S-007")
        it('should use id as label if name is missing', () => {
            const graph = {
                metadata: {},
                nodes: [
                    { id: 'M-module', type: 'module' }
                ],
                edges: []
            };

            const elements = toCytoscapeElements(graph);

            const nodes = elements.filter(el => el.group === 'nodes');
            expect(nodes[0].data.label).to.equal('M-module');
        });

        // @jig.verifies("S-007")
        it('should convert edges to Cytoscape format', () => {
            const graph = {
                metadata: {},
                nodes: [
                    { id: 'N-001', type: 'class', name: 'A' },
                    { id: 'N-002', type: 'function', name: 'B' },
                    { id: 'S-001', type: 'spec', name: 'C' }
                ],
                edges: [
                    { source: 'N-001', target: 'N-002', type: 'contains' },
                    { source: 'N-002', target: 'S-001', type: 'implements' }
                ]
            };

            const elements = toCytoscapeElements(graph);

            const edges = elements.filter(el => el.group === 'edges');
            expect(edges).to.have.lengthOf(2);
            expect(edges[0].data.source).to.equal('N-001');
            expect(edges[0].data.target).to.equal('N-002');
            expect(edges[0].data.label).to.equal('contains');
        });

        // @jig.verifies("S-007")
        it('should create unique edge IDs', () => {
            const graph = {
                metadata: {},
                nodes: [
                    { id: 'N-001', type: 'class', name: 'A' },
                    { id: 'N-002', type: 'function', name: 'B' }
                ],
                edges: [
                    { source: 'N-001', target: 'N-002', type: 'contains' }
                ]
            };

            const elements = toCytoscapeElements(graph);

            const edges = elements.filter(el => el.group === 'edges');
            expect(edges[0].data.id).to.equal('N-001-N-002-contains');
        });

        // @jig.verifies("S-007")
        it('should preserve all node properties in data', () => {
            const graph = {
                metadata: {},
                nodes: [
                    { id: 'C-001', type: 'class', name: 'MyClass', file: 'test.py', line: 10, bases: ['ABC'] }
                ],
                edges: []
            };

            const elements = toCytoscapeElements(graph);

            const node = elements[0].data;
            expect(node.id).to.equal('C-001');
            expect(node.type).to.equal('class');
            expect(node.name).to.equal('MyClass');
            expect(node.file).to.equal('test.py');
            expect(node.line).to.equal(10);
            expect(node.bases).to.deep.equal(['ABC']);
        });

        // @jig.verifies("S-007")
        it('should preserve all edge properties in data', () => {
            const graph = {
                metadata: {},
                nodes: [
                    { id: 'M-001', type: 'module', name: 'A' },
                    { id: 'M-002', type: 'module', name: 'B' }
                ],
                edges: [
                    { source: 'M-001', target: 'M-002', type: 'imports', line: 5 }
                ]
            };

            const elements = toCytoscapeElements(graph);

            const edges = elements.filter(el => el.group === 'edges');
            const edge = edges[0].data;
            expect(edge.source).to.equal('M-001');
            expect(edge.target).to.equal('M-002');
            expect(edge.type).to.equal('imports');
            expect(edge.line).to.equal(5);
        });

        // @jig.verifies("S-007")
        it('should handle empty graph', () => {
            const graph = {
                metadata: {},
                nodes: [],
                edges: []
            };

            const elements = toCytoscapeElements(graph);

            expect(elements).to.be.an('array');
            expect(elements).to.have.lengthOf(0);
        });

        // @jig.verifies("S-007")
        it('should return array with both nodes and edges', () => {
            const graph = {
                metadata: {},
                nodes: [
                    { id: 'N-001', type: 'class', name: 'A' },
                    { id: 'N-002', type: 'function', name: 'B' }
                ],
                edges: [
                    { source: 'N-001', target: 'N-002', type: 'contains' }
                ]
            };

            const elements = toCytoscapeElements(graph);

            expect(elements).to.have.lengthOf(3);
            expect(elements[0].group).to.equal('nodes');
            expect(elements[1].group).to.equal('nodes');
            expect(elements[2].group).to.equal('edges');
        });
    });
});
