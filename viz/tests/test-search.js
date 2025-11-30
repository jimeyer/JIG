/**
 * Tests for search.js
 */

import { searchNodes } from '../js/search.js';

const { describe, it, expect } = window;

describe('Search', () => {
    describe('searchNodes', () => {
        const testNodes = [
            { id: 'C-TokenValidator', type: 'class', name: 'TokenValidator' },
            { id: 'F-validate_token', type: 'function', name: 'validate_token' },
            { id: 'M-jig.impl_graph', type: 'module', name: 'jig.impl_graph' },
            { id: 'M-jig.impl_graph.analyzers', type: 'module', name: 'jig.impl_graph.analyzers' },
            { id: 'C-LanguageAnalyzer', type: 'class', name: 'LanguageAnalyzer' },
            { id: 'F-analyze', type: 'function', name: 'analyze' },
            { id: 'M-external.lib', type: 'external_module', name: 'numpy' }
        ];

        // @jig.verifies("S-012")
        it('should find exact matches', () => {
            const result = searchNodes(testNodes, 'TokenValidator');
            expect(result).to.have.length.greaterThan(0);
            expect(result[0].name).to.equal('TokenValidator');
        });

        // @jig.verifies("S-012")
        it('should find partial matches (fuzzy)', () => {
            const result = searchNodes(testNodes, 'TokenVal');
            expect(result).to.have.length.greaterThan(0);
            expect(result[0].name).to.equal('TokenValidator');
        });

        // @jig.verifies("S-012")
        it('should find matches by ID', () => {
            const result = searchNodes(testNodes, 'C-TokenValidator');
            expect(result).to.have.length.greaterThan(0);
            expect(result[0].id).to.equal('C-TokenValidator');
        });

        // @jig.verifies("S-012")
        it('should find matches by partial ID', () => {
            const result = searchNodes(testNodes, 'F-valid');
            expect(result).to.have.length.greaterThan(0);
            expect(result[0].id).to.equal('F-validate_token');
        });

        // @jig.verifies("S-012")
        it('should be case-insensitive', () => {
            const result = searchNodes(testNodes, 'tokenvalidator');
            expect(result).to.have.length.greaterThan(0);
            expect(result[0].name).to.equal('TokenValidator');
        });

        // @jig.verifies("S-012")
        it('should find module by partial name', () => {
            const result = searchNodes(testNodes, 'jig.impl');
            expect(result.length).to.be.greaterThan(0);
            expect(result.some(n => n.name === 'jig.impl_graph')).to.be.true;
        });

        // @jig.verifies("S-012")
        it('should return empty array for no matches', () => {
            const result = searchNodes(testNodes, 'xyznonexistent');
            expect(result).to.be.an('array');
            expect(result).to.have.lengthOf(0);
        });

        // @jig.verifies("S-012")
        it('should return all nodes for empty query', () => {
            const result = searchNodes(testNodes, '');
            expect(result).to.have.lengthOf(7);
        });

        // @jig.verifies("S-012")
        it('should return all nodes for whitespace query', () => {
            const result = searchNodes(testNodes, '   ');
            expect(result).to.have.lengthOf(7);
        });

        // @jig.verifies("S-012")
        it('should return all nodes for null query', () => {
            const result = searchNodes(testNodes, null);
            expect(result).to.have.lengthOf(7);
        });

        // @jig.verifies("S-012")
        it('should handle empty node array', () => {
            const result = searchNodes([], 'test');
            expect(result).to.be.an('array');
            expect(result).to.have.lengthOf(0);
        });

        // @jig.verifies("S-012")
        it('should rank more relevant results higher', () => {
            const result = searchNodes(testNodes, 'analyze');
            expect(result).to.have.length.greaterThan(0);
            // "analyze" function should rank higher than "LanguageAnalyzer" class
            expect(result[0].name).to.equal('analyze');
        });
    });
});
