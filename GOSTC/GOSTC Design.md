

# GOSTC Design Document

**Graph of Outcomes, Specifications, Tests & Code**

_Deterministic infrastructure for AI-native development alignment_

---

## Executive Summary

GOSTC is the foundational data structure and CLI tooling for SELA (Software Engineering Lifecycle Alignment). It provides a deterministic, queryable semantic graph that maintains bidirectional relationships between business outcomes, technical specifications, test cases, and implementation code. Like pytest captures test structure or git captures version history, GOSTC captures alignment structure—making implicit development knowledge explicit and machine-readable for AI agent orchestration.

**Core Principle**: GOSTC is plumbing, not intelligence. It stores, validates, and retrieves—never interprets or generates. LLMs query GOSTC; GOSTC never queries LLMs.

---

## Goals

### Primary Goals

1. **Deterministic Alignment Storage**: Provide a canonical, version-controlled representation of the O-S-T-C graph that is completely deterministic in behavior
2. **High-Performance Querying**: Enable sub-100ms queries for AI agents navigating complex alignment relationships across thousands of nodes
3. **Data Integrity Guarantees**: Enforce graph consistency rules, detect broken alignments, prevent orphaned nodes
4. **Bidirectional Traceability**: Support navigation from any node to its connected nodes in any direction (outcome→specs→tests→code and reverse)
5. **Change Propagation Analysis**: Identify downstream impacts of proposed changes before they're made
6. **Version Control Native**: Store graph in formats that diff cleanly, merge predictably, and integrate naturally with Git workflows

### Secondary Goals

7. **Audit Trail Generation**: Produce compliance-ready reports showing full traceability chains for regulatory requirements
8. **Developer Experience**: Provide intuitive CLI that feels natural to developers familiar with git, pytest, or similar tools
9. **Extensibility**: Support custom node types, relationship types, and metadata without core rewrites
10. **Performance at Scale**: Handle graphs with 10,000+ nodes without degradation

---

## Non-Goals

- **LLM Integration**: GOSTC contains zero LLM logic. It's called by LLMs, not vice versa
- **Code Execution**: GOSTC doesn't run tests or execute code—it tracks relationships to things that do
- **Code Generation**: GOSTC doesn't create or modify code—it validates that relationships remain consistent
- **UI/Visualization**: Core GOSTC is CLI-first; visualization is a separate layer
- **Natural Language Processing**: GOSTC works with structured data; parsing intent is the LLM's job

---

## Architecture Overview

### Core Concepts

**Node Types** (4 layers):

- **Outcome (O)**: Business goal, user story, requirement
- **Specification (S)**: Technical spec, API contract, design decision
- **Test (T)**: Test case, validation rule, acceptance criteria
- **Code (C)**: Implementation unit (function, class, module)

**Relationships** (directed edges):

- `satisfies`: Specification satisfies Outcome
- `validates`: Test validates Specification
- `implements`: Code implements Specification
- `covers`: Test covers Code
- `derives`: Specification derives from another Specification
- `depends`: Code depends on other Code

**Node Properties**:

```typescript
interface Node {
  id: string;              // Unique identifier (UUID or content-addressed)
  type: 'O' | 'S' | 'T' | 'C';
  title: string;           // Human-readable name
  content: string;         // Full description/body
  metadata: {
    created: ISO8601;
    modified: ISO8601;
    author?: string;
    tags?: string[];
    status?: 'draft' | 'active' | 'deprecated';
    [key: string]: any;    // Extensible
  };
  location?: {             // For Code and Test nodes
    file: string;
    line?: number;
    symbol?: string;
  };
  alignmentHealth?: {      // Computed, not stored
    score: number;         // 0-100
    issues: Issue[];
  };
}

interface Edge {
  id: string;
  type: RelationType;
  source: string;          // Node ID
  target: string;          // Node ID
  metadata: {
    created: ISO8601;
    rationale?: string;
    [key: string]: any;
  };
}

interface Issue {
  type: 'broken_link' | 'orphaned_node' | 'missing_tests' | 'stale_spec';
  severity: 'error' | 'warning' | 'info';
  message: string;
  nodeId: string;
}
```

### Storage Format

**File-based, Git-friendly**:

```
.gostc/
├── config.json           # Project configuration
├── nodes/
│   ├── outcomes/
│   │   ├── O-001.md
│   │   └── O-002.md
│   ├── specifications/
│   │   ├── S-001.md
│   │   └── S-002.md
│   ├── tests/
│   │   ├── T-001.md
│   │   └── T-002.md
│   └── code/
│       ├── C-001.md      # Code nodes reference actual source
│       └── C-002.md
├── edges/
│   └── graph.json        # All edges in single file
└── index/
    ├── by-type.json      # Fast lookup indexes
    ├── by-file.json
    └── integrity.json    # Checksums, validation data
```

**Node File Format** (Markdown with YAML frontmatter):

```markdown
---
id: S-042
type: S
title: User Authentication API
created: 2025-03-15T10:30:00Z
modified: 2025-03-20T14:22:00Z
author: jim@example.com
tags: [auth, api, security]
status: active
---

# User Authentication API

## Overview
RESTful API for user authentication using JWT tokens.

## Endpoints
- POST /api/auth/login
- POST /api/auth/refresh
- POST /api/auth/logout

## Security Requirements
- Passwords hashed with bcrypt
- JWT expiry: 1 hour
- Refresh token expiry: 30 days
```

**Rationale**: Markdown is human-readable, diffable, and tooling-rich. YAML frontmatter provides structured metadata. Separate edge file prevents merge conflicts when multiple nodes update simultaneously.

---

## CLI Interface Design

### Command Structure

Inspired by git/pytest patterns:

```bash
# Initialize GOSTC in project
gostc init

# Node management
gostc add outcome "Enable SSO for enterprise customers"
gostc add spec "OAuth2 integration spec" --satisfies O-001
gostc add test "OAuth2 flow validation" --validates S-042
gostc add code src/auth/oauth.py:authenticate --implements S-042

gostc show S-042                    # Display node details
gostc edit S-042                    # Open in $EDITOR
gostc rm S-042 --cascade            # Remove node and edges
gostc list --type spec --tag auth  # List filtered nodes

# Edge management
gostc link S-042 satisfies O-001
gostc link T-015 validates S-042 --rationale "Tests happy path"
gostc unlink T-015 S-042

# Graph queries (THE POWER INTERFACE)
gostc query "from S-042 traverse validates"              # Find tests validating S-042
gostc query "from O-001 traverse satisfies.implements"   # Find code implementing O-001
gostc query "from src/auth/oauth.py traverse *"          # All nodes related to file
gostc query "orphans --type test"                        # Find unlinked tests
gostc query "path O-001 C-099"                           # Shortest path between nodes

# Alignment checks
gostc check                         # Validate entire graph
gostc check --type spec             # Check specs only
gostc check S-042                   # Check specific node
gostc health                        # Show alignment health scores

# Impact analysis
gostc impact src/auth/oauth.py      # What breaks if this changes?
gostc impact S-042 --depth 3        # Propagation depth
gostc diff HEAD~1                   # Alignment changes since last commit

# Export and reporting
gostc export --format json          # Export entire graph
gostc export --format dot | dot -Tpng > graph.png
gostc trace O-001                   # Full traceability report
gostc report --compliance sox       # SOX compliance report

# Integration hooks
gostc watch src/                    # Monitor for code changes
gostc sync --from-tests pytest.xml  # Import test structure
gostc sync --from-code src/         # Discover code nodes via AST
```

### Query Language

**Simple path queries** (80% of use cases):

```
gostc query "from <node-id> traverse <edge-type>[.<edge-type>]*"
```

**Advanced queries** (for AI agents):

```typescript
// JSON-based query for programmatic access
{
  "from": ["S-042", "S-043"],
  "traverse": ["validates", "covers"],
  "filter": {
    "type": "T",
    "metadata.status": "active"
  },
  "depth": 2,
  "return": ["id", "title", "metadata.tags"]
}
```

**Common query patterns**:

```bash
# "What tests validate this spec?"
gostc query "from S-042 traverse validates"

# "What code implements this outcome?"
gostc query "from O-001 traverse satisfies.implements"

# "What outcomes does this code contribute to?"
gostc query "from C-099 traverse implements.satisfies"

# "Is this test orphaned?"
gostc query "from T-015 traverse validates, covers" --expect-nonzero

# "What's the blast radius of changing this function?"
gostc impact C-099 --show-outcomes
```

---

## Design Considerations

### 1. **Performance**

**Index Strategy**:

- In-memory indexes loaded at startup from `.gostc/index/`
- B-tree indexes on node ID, type, file location
- Adjacency list for graph traversal
- LRU cache for frequent queries (AI agents often repeat patterns)

**Benchmarks** (target):

- Node lookup by ID: <1ms
- Single-hop traversal: <5ms
- Multi-hop traversal (depth 3): <50ms
- Full graph integrity check: <500ms for 10K nodes

**Optimization strategies**:

- Lazy-load node content (index contains only IDs/metadata)
- Memoize query results during single CLI invocation
- Incremental integrity checks (only validate changed subgraphs)

### 2. **Integrity Guarantees**

**Validation rules** (enforced on `gostc check`):

1. No dangling edges (source and target must exist)
2. Type constraints (e.g., `validates` must connect T→S)
3. No cycles in `satisfies` or `implements` chains
4. Required edges: each S should have ≥1 `satisfies` and ≥1 `validates`
5. Code nodes must reference real files/symbols

**Integrity levels**:

- `strict`: All rules enforced (default for CI)
- `loose`: Warnings only (during active development)
- `custom`: User-defined rules via `.gostc/config.json`

### 3. **Version Control Integration**

**Git hooks** (optional installation):

```bash
# Pre-commit: validate changed nodes
gostc check --staged

# Post-merge: reindex graph
gostc index rebuild

# Pre-push: ensure no broken alignments
gostc health --min-score 80 || exit 1
```

**Merge strategies**:

- Node files: standard 3-way merge (rare conflicts due to separate files)
- Edge file: custom merge driver that combines edge arrays
- Index files: auto-regenerated, never committed

### 4. **Extensibility**

**Plugin system**:

```javascript
// .gostc/plugins/custom-validator.js
module.exports = {
  name: 'fintech-compliance',
  validate: (node, graph) => {
    if (node.type === 'S' && node.metadata.tags?.includes('financial')) {
      // Ensure every financial spec has audit trail
      const outcomes = graph.traverse(node.id, 'satisfies');
      if (outcomes.length === 0) {
        return { error: 'Financial specs must link to outcomes' };
      }
    }
    return { ok: true };
  }
};
```

**Custom node types** (via config):

```json
{
  "nodeTypes": {
    "R": {
      "name": "Risk",
      "description": "Risk mitigation requirement",
      "requiredFields": ["severity", "mitigation"],
      "allowedEdges": ["mitigatedBy"]
    }
  }
}
```

### 5. **AI Agent Integration**

**JSON API** (over stdin/stdout):

```bash
# Agent sends query
echo '{"command": "query", "params": {"from": "S-042", "traverse": "validates"}}' | gostc api

# GOSTC responds
{"status": "ok", "result": [{"id": "T-015", "title": "OAuth2 flow validation"}]}
```

**Structured output modes**:

```bash
gostc query "from S-042 traverse validates" --format json
gostc query "from S-042 traverse validates" --format compact  # Single line per result
gostc query "from S-042 traverse validates" --format tsv     # Tab-separated
```

**Batch operations** (reduce process startup overhead):

```bash
gostc batch << EOF
query from S-042 traverse validates
query from S-043 traverse validates
health S-042
EOF
```

---

## Use Cases

### Use Case 1: AI Agent Generates Code, Maintains Alignment

**Scenario**: Agent generates new authentication function.

```bash
# 1. Agent queries: "What spec should I implement?"
gostc query "from O-001 traverse satisfies" --filter 'metadata.status=active'
# Returns: S-042

# 2. Agent generates code in src/auth/oauth.py

# 3. Agent registers code node
gostc add code src/auth/oauth.py:authenticate --implements S-042

# 4. Agent queries: "What tests should I write?"
gostc query "from S-042 traverse validates"
# Returns: T-015, T-016

# 5. Agent generates tests, links them
gostc add code tests/test_oauth.py:test_authenticate --covers src/auth/oauth.py:authenticate

# 6. Validate alignment
gostc check S-042
# ✓ S-042 has outcome (O-001)
# ✓ S-042 has tests (T-015, T-016)
# ✓ S-042 has implementation (C-099)
```

### Use Case 2: Developer Changes Code, Discovers Impact

**Scenario**: Developer refactors authentication logic.

```bash
# Developer about to modify src/auth/oauth.py
gostc impact src/auth/oauth.py

# Output:
# Direct impacts:
#   - S-042: OAuth2 integration spec [IMPLEMENTS]
#   - T-015: OAuth2 flow validation [COVERED_BY]
#   - T-016: OAuth2 error handling [COVERED_BY]
#
# Upstream impacts (outcomes affected):
#   - O-001: Enable SSO for enterprise customers [CRITICAL]
#
# Recommendation: Review T-015, T-016 after changes

# After changes, validate alignment still holds
gostc check src/auth/oauth.py --ci
```

### Use Case 3: Compliance Audit Trail

**Scenario**: SOX audit requires traceability from requirement to code.

```bash
# Generate full trace report
gostc trace O-001 --format html > audit_trail_O001.html

# Report contains:
# O-001: Enable SSO for enterprise customers
#   └─ S-042: OAuth2 integration spec [satisfies]
#      ├─ T-015: OAuth2 flow validation [validates]
#      │  └─ tests/test_oauth.py:test_authenticate [covers]
#      │     └─ src/auth/oauth.py:authenticate
#      ├─ T-016: OAuth2 error handling [validates]
#      └─ C-099: src/auth/oauth.py:authenticate [implements]
#
# All relationships timestamped and attributed
```

### Use Case 4: Progressive Refinement

**Scenario**: Outcome is defined, agent progressively adds specs/tests/code.

```bash
# Day 1: Product manager adds outcome
gostc add outcome "Support multi-factor authentication"

# Day 2: Architect adds specs
gostc add spec "TOTP-based 2FA" --satisfies O-042
gostc add spec "SMS-based 2FA" --satisfies O-042

# Day 3: QA writes test cases
gostc add test "TOTP generation and validation" --validates S-100
gostc add test "SMS delivery and verification" --validates S-101

# Day 4: Check readiness
gostc health O-042
# Score: 60/100
# ✓ Outcome has specs (2)
# ✓ Specs have tests (2)
# ✗ No code implementing specs
# → Ready for development

# Day 5: Developer implements
gostc add code src/auth/mfa.py:verify_totp --implements S-100
gostc health O-042
# Score: 100/100 ✓
```

### Use Case 5: Breaking Change Detection

**Scenario**: API spec changes, need to find what breaks.

```bash
# Edit specification
gostc edit S-042

# Check what depends on this spec
gostc query "to S-042 traverse *"
# Returns:
#   T-015 [validates]
#   T-016 [validates]
#   C-099 [implements]
#   O-001 [satisfies]

# Mark tests as outdated
gostc annotate T-015 --status stale --reason "S-042 API changed"

# Find all stale tests
gostc list --filter 'metadata.status=stale'
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (Weeks 1-4)

- [ ] Define TypeScript schemas
- [ ] Implement file-based storage (nodes, edges)
- [ ] Build in-memory index system
- [ ] Basic CLI: init, add, show, list
- [ ] Node and edge validation
- [ ] Simple query engine (single-hop)

### Phase 2: Graph Operations (Weeks 5-8)

- [ ] Multi-hop traversal
- [ ] Path finding algorithms
- [ ] Integrity checker
- [ ] Impact analysis
- [ ] Health scoring system
- [ ] Git integration basics

### Phase 3: Developer Experience (Weeks 9-12)

- [ ] Advanced query language
- [ ] Batch operations
- [ ] JSON API for agents
- [ ] Export formats (JSON, DOT, HTML)
- [ ] Watch mode
- [ ] Plugin system

### Phase 4: Scale & Polish (Weeks 13-16)

- [ ] Performance optimization
- [ ] Large graph testing (10K+ nodes)
- [ ] Documentation and examples
- [ ] CI/CD integration guides
- [ ] Compliance report templates
- [ ] Migration tools

---

## Success Metrics

### Developer Adoption

- **Time to first value**: Developer can `init`, `add outcome`, `add spec`, `check` in <5 minutes
- **Query latency**: 95th percentile <100ms for typical AI agent queries
- **False positive rate**: <5% for integrity checks (balance strictness vs. workflow friction)

### Technical Performance

- **Graph size**: Support 10,000 nodes with <1GB memory footprint
- **Concurrent access**: 10 simultaneous AI agents querying without lock contention
- **Merge conflicts**: <1% of multi-developer commits require manual merge of edge file

### Business Impact

- **Audit compliance**: Generate SOX/HIPAA traces in <30 seconds
- **Change confidence**: 80% reduction in "what will this break?" questions
- **Onboarding speed**: New developers understand codebase relationships in days, not weeks

---

## Comparison to Analogous Tools

|Tool|Purpose|GOSTC Parallel|
|---|---|---|
|**pytest**|Discovers and runs tests|Discovers and validates test-spec-code alignment|
|**git**|Tracks code changes over time|Tracks alignment relationships across layers|
|**GraphQL**|Queries data graphs|Queries semantic development graphs|
|**clang AST**|Parses code structure|Parses alignment structure|

**Key differentiator**: GOSTC is the only tool that treats alignment as first-class data, making the _relationships_ between artifacts queryable and enforceable.

---

## Open Questions

1. **Node ID strategy**: UUID (portable, opaque) vs. content-addressed hashes (deterministic, verbose)?
2. **Edge file format**: Single JSON (simple, potentially conflicts) vs. one-file-per-edge (complex, no conflicts)?
3. **Index persistence**: Store indexes in `.gostc/index/` (faster startup) or rebuild on demand (simpler, more reliable)?
4. **Code node granularity**: Track functions, classes, and modules—or just files?
5. **Concurrent access**: Use file locks, optimistic concurrency, or assume single-developer context?

**Recommendation**: Start with simplest viable options (UUID, single edge file, rebuild indexes, file-level code nodes, single developer), evolve based on real usage.

---

## Conclusion

GOSTC is to alignment what pytest is to testing: **simple, powerful, indispensable**. It doesn't do the thinking—it makes thinking tractable. By providing deterministic infrastructure for storing, validating, and querying alignment relationships, GOSTC enables AI agents to work confidently within bounded correctness guarantees.

The design prioritizes:

- **Developer ergonomics** (familiar CLI patterns)
- **AI agent efficiency** (fast queries, structured output)
- **Data integrity** (validation rules, type safety)
- **Version control harmony** (diffable formats, merge strategies)

This is foundational infrastructure for AI-native development. It should feel boring, reliable, and obvious—like any good plumbing should.

---

**Next Steps**: Review this design, challenge assumptions, then prototype Phase 1 in TypeScript with a test suite covering core operations. Validate the mental model by implementing 3 real-world scenarios before expanding scope.