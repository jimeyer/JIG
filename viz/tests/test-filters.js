/**
 * Tests for filters.js
 */

import { filterNodesByType, filterEdgesByType } from '../js/filters.js';

describe('Filters', () => {
    describe('filterNodesByType', () => {
        // @jig.verifies("S-010")

        const testNodes = [
            { id: 'N-001', type: 'class', name: 'MyClass' },
            { id: 'N-002', type: 'function', name: 'myFunction' },
            { id: 'N-003', type: 'module', name: 'myModule' },
            { id: 'N-004', type: 'external_module', name: 'externalLib' },
            { id: 'N-005', type: 'class', name: 'AnotherClass' },
            { id: 'N-006', type: 'function', name: 'anotherFunction' }
        ];

        it('should filter nodes by single type', () => {
            const result = filterNodesByType(testNodes, ['class']);
            expect(result).to.have.lengthOf(2);
            expect(result[0].id).to.equal('N-001');
            expect(result[1].id).to.equal('N-005');
        });

        it('should filter nodes by multiple types', () => {
            const result = filterNodesByType(testNodes, ['class', 'function']);
            expect(result).to.have.lengthOf(4);
            expect(result.map(n => n.type)).to.include('class');
            expect(result.map(n => n.type)).to.include('function');
        });

        it('should return empty array when types is empty', () => {
            const result = filterNodesByType(testNodes, []);
            expect(result).to.be.an('array');
            expect(result).to.have.lengthOf(0);
        });

        it('should return empty array when types is null', () => {
            const result = filterNodesByType(testNodes, null);
            expect(result).to.be.an('array');
            expect(result).to.have.lengthOf(0);
        });

        it('should return all nodes when all types specified', () => {
            const result = filterNodesByType(testNodes, ['class', 'function', 'module', 'external_module']);
            expect(result).to.have.lengthOf(6);
        });

        it('should return empty array when no matching types', () => {
            const result = filterNodesByType(testNodes, ['nonexistent']);
            expect(result).to.have.lengthOf(0);
        });

        it('should handle empty node array', () => {
            const result = filterNodesByType([], ['class']);
            expect(result).to.be.an('array');
            expect(result).to.have.lengthOf(0);
        });
    });

    describe('filterEdgesByType', () => {
        // @jig.verifies("S-011")

        const testEdges = [
            { source: 'N-001', target: 'N-002', type: 'contains' },
            { source: 'N-002', target: 'N-003', type: 'implements' },
            { source: 'N-003', target: 'N-004', type: 'imports' },
            { source: 'N-004', target: 'N-005', type: 'contains' },
            { source: 'N-005', target: 'N-006', type: 'implements' }
        ];

        it('should filter edges by single type', () => {
            const result = filterEdgesByType(testEdges, ['contains']);
            expect(result).to.have.lengthOf(2);
            expect(result[0].type).to.equal('contains');
            expect(result[1].type).to.equal('contains');
        });

        it('should filter edges by multiple types', () => {
            const result = filterEdgesByType(testEdges, ['implements', 'imports']);
            expect(result).to.have.lengthOf(3);
            expect(result.map(e => e.type)).to.include('implements');
            expect(result.map(e => e.type)).to.include('imports');
        });

        it('should return empty array when types is empty', () => {
            const result = filterEdgesByType(testEdges, []);
            expect(result).to.be.an('array');
            expect(result).to.have.lengthOf(0);
        });

        it('should return empty array when types is null', () => {
            const result = filterEdgesByType(testEdges, null);
            expect(result).to.be.an('array');
            expect(result).to.have.lengthOf(0);
        });

        it('should return all edges when all types specified', () => {
            const result = filterEdgesByType(testEdges, ['contains', 'implements', 'imports']);
            expect(result).to.have.lengthOf(5);
        });

        it('should return empty array when no matching types', () => {
            const result = filterEdgesByType(testEdges, ['nonexistent']);
            expect(result).to.have.lengthOf(0);
        });

        it('should handle empty edge array', () => {
            const result = filterEdgesByType([], ['contains']);
            expect(result).to.be.an('array');
            expect(result).to.have.lengthOf(0);
        });
    });
});
