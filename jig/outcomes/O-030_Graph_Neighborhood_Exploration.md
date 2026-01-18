---
id: O-030
title: Graph Neighborhood Exploration
type: outcome
goals: [G-002, G-005]
specifications: [S-110, S-111, S-112, S-113]
---

# Graph Neighborhood Exploration

**Value:** Agents discover connections from any identifier by traversing intent/impl/verify graphs, enabling contextual understanding without full codebase reads.

**Acceptance:** `jigy context S-042` returns ancestors (up to Charter), immediate children, and budget-limited descendants in a flat node list.

## AI Agent Benefit

Agents need to understand how artifacts relate. Before modifying code, an agent should know: what spec does this implement? what tests verify it? what outcome does it serve? The context command answers these questions in one call, returning a navigable neighborhood that agents can selectively read.

Without graph exploration, agents must grep across files, parse frontmatter, and build mental maps manually—wasting context tokens and risking incomplete understanding.

## Rationale

JIG maintains three graphs joined on spec IDs:
- **Intent graph**: Charter → Goals → Architecture/Outcomes → Specs
- **Implementation graph**: Modules → Classes → Functions (linked via @jig.implements)
- **Verification graph**: Test files → Test functions (linked via @jig.verifies)

The context command provides a unified traversal across all three. Given any identifier (S-###, O-###, G-###, F-*, T-*, file path), it returns the connected neighborhood.

The graph is asymmetric:
- Upward (toward Charter): bounded, low fanout, max 5 hops
- Downward (toward code): unbounded, high fanout, could be hundreds of nodes

The traversal algorithm respects this asymmetry: always return complete ancestors, always return immediate children, then budget-fill descendants breadth-first.

## Success Criteria

The context command must:
1. Resolve any valid identifier to its graph node
2. Return complete ancestor chain (always)
3. Return immediate children (always)
4. Return additional descendants up to `--max N` budget (default 50)
5. Report `more` count for truncated descendants
6. Support `-j/-m/-v` output flags per S-093

## Specified By

This outcome is delivered through:
- **S-110**: Context Command CLI Interface - the `jigy context` command
- **S-111**: Context Identifier Resolution - parsing and resolving identifiers
- **S-112**: Context Graph Traversal - the traversal algorithm
- **S-113**: Context Response Schema - JSON structure for agent consumption

## Charter Linkage

This outcome serves:
- **G-002** (Continuity Across Sessions): Agents discover context from identifiers, not session memory
- **G-005** (Full Traceability): Every function traces upward; context command enables these queries
