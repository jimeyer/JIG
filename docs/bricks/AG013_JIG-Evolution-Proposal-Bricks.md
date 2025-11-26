# JIG Evolution Proposal: Bricks Integration

_Evolving JIG to Support the Alignment Graph Brick Model_

**Date:** 2025-11-25
**Status:** Proposal
**Authors:** Claude + Jim Meyer

---

## Executive Summary

This document proposes the integration of **Bricks** into the JIG (Jig Intent Graph) system as first-class architectural units. Bricks will become a core node type in the Intent Graph, enabling:

- **Architectural boundaries** - Machine-enforceable context boundaries for both humans and AI agents
- **Alignment tracking** - Explicit binding of Intent → Implementation → Verification at the Brick level
- **Context scoping** - Bounded contexts for agent work and human design
- **Drift detection** - Measurable alignment between architectural intent and implementation reality

This proposal covers changes to:
1. Graph data model and `graph-index.json` format
2. `jigy index rebuild` to discover and index Bricks
3. `jigy status` to show Brick health and alignment
4. New Brick-specific commands and queries
5. Validation rules for Brick boundaries
6. Integration with existing OSTC nodes

---

## 1. Problem Statement

### 1.1 Current State

JIG currently manages four node types in the Intent Graph:
- **O** (Outcomes): Why we're building something
- **S** (Specifications): What constraints must be satisfied
- **T** (Tests): What verification exists
- **C** (Code): What implementation exists

These nodes are organized by **subsystems** (flat or nested groups), but subsystems are:
- **Informal groupings** - No enforced boundaries
- **Documentation-level** - Not machine-enforceable
- **Missing semantic binding** - No explicit Intent → Code → Test binding
- **No context boundaries** - Agents see entire codebase or nothing

### 1.2 Gaps

Without Bricks, JIG cannot:
1. **Enforce architectural boundaries** - Subsystems are labels, not boundaries
2. **Provide bounded contexts for agents** - No way to scope what an agent should see
3. **Track Intent-Code-Test alignment** - Relationships are node-level, not architectural-unit-level
4. **Detect architectural drift** - No mechanism to measure boundary violations
5. **Support Architecture Mode vs Implementation Mode** - No way to operate at different abstraction levels

### 1.3 Opportunity

By integrating Bricks as a first-class node type (B), JIG can:
- ✅ Make architectural boundaries **explicit and enforceable**
- ✅ Provide **bounded contexts** for both human design and agent execution
- ✅ Track **tri-fold alignment** (Intent ↔ Code ↔ Test) at the Brick level
- ✅ Measure **architectural drift** objectively through graph queries
- ✅ Enable **Architecture Mode** (design with Bricks) and **Implementation Mode** (build inside a Brick)

---

## 2. Proposed Changes to Graph Model

### 2.1 New Node Type: Brick (B)

Add Brick as a fifth node type alongside O, S, T, C:

```yaml
# jig/bricks/graph-core.brick.yaml
brick:
  id: B-GRAPH-001           # New ID format: B-<PREFIX>-<NUMBER>
  name: "Graph Core"
  version: "1.0.0"
  layer: domain-core

responsibility: |
  Graph data structures and query operations.
  Defines Graph, Node, Edge, Subsystem classes.

interface:
  public:
    - class: Graph
      methods:
        - load_from_dir(intent_dir: Path) -> Graph
        - get_dependencies(node_id: str) -> list[str]
        # ... other public API

  stability: stable
  versioning: semver

dependencies:
  bricks:
    - B-PARSER-001         # Depends on Intent Parser Brick
    - B-UTILS-001          # Depends on Foundation Utils Brick
  external:
    - networkx
    - json

code:
  paths:
    - src/jig/core/graph.py
    - src/jig/core/relationships.py
  loc: 696

tests:
  paths:
    - tests/unit/test_graph.py
    - tests/unit/test_graph_queries.py
  count: 48
  coverage: 75%

intent:
  outcomes:
    - O-JIG-003            # Bricks "contain" Intent nodes
  specifications:
    - S-GRAPH-001
    - S-GRAPH-002
    - S-GRAPH-003

metrics:
  coupling_ratio: "12:1"
  boundary_violations: 0
  alignment_score: 0.85    # New: Intent-Code-Test alignment

health:
  score: fair
  status: stable
  last_review: 2025-11-25
```

### 2.2 Brick Relationships

New edge types in the graph:

| Edge Type | From | To | Meaning |
|-----------|------|-----|---------|
| `contains_intent` | Brick | O/S node | Brick contains this Intent node |
| `contains_code` | Brick | C node | Brick contains this Code node |
| `contains_test` | Brick | T node | Brick contains this Test node |
| `depends_on` | Brick | Brick | Brick depends on another Brick's interface |
| `exposes_interface` | Brick | Interface | Brick exposes this public interface |
| `implements_brick` | C node | Brick | Code node implements this Brick (reverse of contains_code) |
| `verifies_brick` | T node | Brick | Test node verifies this Brick (reverse of contains_test) |

Example edges:
```
B-GRAPH-001 --[contains_intent]--> O-JIG-003
B-GRAPH-001 --[contains_code]--> C-GRAPH-001
B-GRAPH-001 --[contains_test]--> T-GRAPH-001
B-GRAPH-001 --[depends_on]--> B-PARSER-001
```

### 2.3 Graph-Index.json Changes

**Current format:**
```json
{
  "version": "1.0",
  "generated": "2025-11-25T12:16:55.640936+00:00",
  "nodes": [
    {
      "id": "O-JIG-001",
      "type": "outcome",
      "title": "JIG tools run in <1 second",
      "subsystem": "core"
    }
  ],
  "subsystems": {
    "core": {
      "nodes": ["O-JIG-001", "S-JIG-002"]
    }
  }
}
```

**Proposed format (backward compatible):**
```json
{
  "version": "2.0",
  "generated": "2025-11-25T15:30:00.000000+00:00",
  "nodes": [
    {
      "id": "B-GRAPH-001",
      "type": "brick",
      "title": "Graph Core",
      "subsystem": "core",
      "status": "stable",
      "file": "jig/bricks/graph-core.brick.yaml",
      "version": "1.0.0",
      "layer": "domain-core",
      "responsibility": "Graph data structures and query operations",
      "contains_intent": ["O-JIG-003", "S-GRAPH-001", "S-GRAPH-002"],
      "contains_code": ["C-GRAPH-001", "C-GRAPH-004"],
      "contains_test": ["T-GRAPH-001", "T-GRAPH-002"],
      "depends_on": ["B-PARSER-001", "B-UTILS-001"],
      "interface": {
        "public": ["Graph", "Edge", "Subsystem"],
        "stability": "stable"
      },
      "metrics": {
        "coupling_ratio": 12.0,
        "test_coverage": 0.75,
        "alignment_score": 0.85,
        "boundary_violations": 0
      }
    },
    {
      "id": "O-JIG-003",
      "type": "outcome",
      "title": "JIG is composable (pipes work)",
      "subsystem": "core",
      "file": "jig/outcomes/O-JIG-003.md",
      "brick": "B-GRAPH-001"      // Reverse relationship
    }
  ],
  "bricks": {
    "B-GRAPH-001": {
      "name": "Graph Core",
      "layer": "domain-core",
      "intent": ["O-JIG-003", "S-GRAPH-001", "S-GRAPH-002", "S-GRAPH-003"],
      "code": ["C-GRAPH-001", "C-GRAPH-004"],
      "tests": ["T-GRAPH-001", "T-GRAPH-002"],
      "dependencies": ["B-PARSER-001", "B-UTILS-001"]
    }
  },
  "subsystems": {
    "core": {
      "nodes": ["O-JIG-001", "B-GRAPH-001", "C-GRAPH-001"],
      "bricks": ["B-GRAPH-001", "B-PARSER-001"]    // New: Bricks in subsystem
    }
  }
}
```

**Key changes:**
- Add `"type": "brick"` nodes with Brick-specific fields
- Add `"bricks"` top-level section (like `"subsystems"`)
- Add `"brick"` field to O/S/T/C nodes (reverse relationship)
- Add `"contains_intent"`, `"contains_code"`, `"contains_test"` arrays to Brick nodes
- Version bump to `"2.0"` (backward compatible - old tools ignore brick nodes)

---

## 3. Changes to `jigy index rebuild`

### 3.1 Current Behavior

`jigy index rebuild` currently:
1. Discovers Outcome nodes from `jig/outcomes/*.md`
2. Discovers Specification nodes from `jig/specifications/*.md`
3. Discovers Constraint nodes from `jig/constraints/*.md`
4. Discovers Code/Test nodes from `@jig` annotations in `src/` and `tests/`
5. Merges nodes, detects conflicts
6. Builds subsystem hierarchy from `subsystem:` frontmatter
7. Writes `graph-index.json`

### 3.2 Proposed Changes

Add Brick discovery as step 1.5:

```python
# In src/jig/core/index_builder.py

def discover_brick_nodes(self) -> list[OSTCNode]:
    """Discover Brick nodes from jig/bricks/*.brick.yaml files.

    Scans jig/bricks/ for .brick.yaml files with Brick definitions.

    Returns:
        List of parsed Brick nodes (type='brick')
    """
    nodes: list[OSTCNode] = []
    brick_dir = self.intent_dir / "bricks"

    if not brick_dir.exists():
        return nodes

    for brick_file in brick_dir.glob("*.brick.yaml"):
        try:
            brick_data = load_yaml(brick_file)
            brick = brick_data.get("brick", {})

            # Create Brick node
            node = OSTCNode(
                id=brick["id"],
                type="brick",
                title=brick["name"],
                subsystem=brick.get("subsystem"),
                status=brick.get("health", {}).get("status", "active"),
                body=brick.get("responsibility", ""),
                metadata={
                    "file": str(brick_file),
                    "version": brick.get("version"),
                    "layer": brick.get("layer"),
                    "interface": brick.get("interface"),
                    "dependencies": brick.get("dependencies"),
                    "code": brick.get("code"),
                    "tests": brick.get("tests"),
                    "intent": brick.get("intent"),
                    "metrics": brick.get("metrics"),
                    "health": brick.get("health"),
                    # Relationships from brick definition
                    "contains_intent": brick.get("intent", {}).get("outcomes", []) +
                                      brick.get("intent", {}).get("specifications", []),
                    "depends_on": [dep for dep in brick.get("dependencies", {}).get("bricks", [])],
                },
            )
            nodes.append(node)

        except Exception as e:
            self.parse_errors.append(f"Failed to parse {brick_file}: {str(e)}")

    return nodes
```

**Modified build flow:**
```python
def build(self) -> RebuildResult:
    # 1. Discover Bricks (NEW)
    brick_nodes = self.discover_brick_nodes()

    # 2. Discover markdown Intent nodes
    markdown_nodes = self.discover_markdown_nodes()

    # 3. Discover code/test annotations
    annotation_nodes = self.discover_annotation_nodes()

    # 4. Merge all nodes
    all_nodes = brick_nodes + markdown_nodes + annotation_nodes

    # 5. Build brick-to-node mappings (NEW)
    brick_mappings = self._build_brick_mappings(brick_nodes, all_nodes)

    # 6. Validate Brick boundaries (NEW)
    boundary_errors = self._validate_brick_boundaries(brick_mappings)

    # ... rest of existing logic
```

**New validation:**
```python
def _validate_brick_boundaries(self, brick_mappings: dict) -> list[str]:
    """Validate that Brick boundary declarations match reality.

    Checks:
    - All Intent nodes declared in brick.intent.* actually exist
    - All Code nodes in brick.code.paths have @jig annotations
    - All Test nodes in brick.tests.paths have @jig annotations
    - No code nodes belong to multiple Bricks
    """
    errors = []
    # ... validation logic
    return errors
```

### 3.3 Output Changes

**Current output:**
```
Rebuilding graph-index.json from sources...

Scanning sources:
  ✓ jig/outcomes/*.md (12 nodes)
  ✓ jig/specifications/*.md (43 nodes)
  ✓ jig/constraints/*.md (5 nodes)
  ✓ src/ and tests/ for @jig annotations (35 code, 15 test nodes)

Total nodes: 110 (12 O, 43 S, 5 X, 35 C, 15 T)
Total edges: 142 (after deduplication)

✅ Done!
```

**Proposed output:**
```
Rebuilding graph-index.json from sources...

Scanning sources:
  ✓ jig/bricks/*.brick.yaml (10 bricks)          <-- NEW
  ✓ jig/outcomes/*.md (12 nodes)
  ✓ jig/specifications/*.md (43 nodes)
  ✓ jig/constraints/*.md (5 nodes)
  ✓ src/ and tests/ for @jig annotations (35 code, 15 test nodes)

Total nodes: 120 (10 B, 12 O, 43 S, 5 X, 35 C, 15 T)  <-- NEW: includes Bricks
Total edges: 178 (after deduplication)                <-- More edges (Brick relationships)

Brick Alignment:                                       <-- NEW section
  ✓ Graph Core (B-GRAPH-001): 3 intent, 2 code, 2 test nodes
  ✓ Intent Parser (B-PARSER-001): 1 intent, 1 code, 1 test node
  ⚠ CLI Commands (B-CLI-001): 8 intent, 9 code, 0 test nodes (tests missing)
  ✗ Index Builder (B-INDEX-001): Boundary violation detected
      → C-SCANNER-001 calls code outside declared dependencies

Validation:
  ✓ All node IDs valid
  ✓ All edge targets exist
  ✓ No duplicate node IDs
  ⚠ 1 Brick has incomplete test coverage
  ✗ 1 Brick has boundary violations

⚠️  Warnings:
  • B-CLI-001: Intent nodes without tests
  • B-INDEX-001: Boundary violation in src/jig/core/index_builder.py:245

✅ Done! (with warnings)
```

---

## 4. Changes to `jigy status`

### 4.1 Current Output

```
JIG Graph Status

✓ 110 nodes, 142 edges, 5 subsystems

Node Summary:
  Outcomes: 12
  Specifications: 43
  Tests: 15
  Code: 35
  Constraints: 5

Subsystems:
  core: 85 nodes
  cli: 18 nodes
  decompose: 5 nodes
  jigy-tool: 2 nodes
  test-fixtures: 5 nodes

✓ Graph looks healthy!
```

### 4.2 Proposed Output

**Default view (shows Bricks):**
```
JIG Graph Status

✓ 120 nodes, 178 edges, 5 subsystems, 10 bricks     <-- NEW: brick count

Node Summary:
  Bricks: 10                                         <-- NEW node type
  Outcomes: 12
  Specifications: 43
  Tests: 15
  Code: 35
  Constraints: 5

Bricks by Layer:                                     <-- NEW section
  Foundation (2 bricks):
    ✓ Foundation Utilities (B-UTILS-001)
    ✓ Configuration & Filtering (B-CONFIG-001)

  Domain Core (3 bricks):
    ✓ Intent Parser (B-PARSER-001)
    ✓ Intent Validator (B-VALIDATOR-001)
    ⚠ Graph Core (B-GRAPH-001) - Low test coverage

  Analysis & Discovery (4 bricks):
    ✓ Index Builder (B-INDEX-001)
    ✓ Annotation Scanner (B-SCANNER-001)
    ✓ Annotation Validator (B-ANNOT-VAL-001)
    ✓ Decomposition Analysis (B-DECOMP-001)

  Interface (1 brick):
    ⚠ CLI Commands (B-CLI-001) - Missing tests

Brick Health:                                        <-- NEW section
  ✓ 8 bricks healthy
  ⚠ 2 bricks need attention
  ✗ 0 bricks failing

Alignment Metrics:                                   <-- NEW section
  Intent Coverage: 98% (54/55 intent nodes assigned to bricks)
  Code Coverage: 100% (35/35 code nodes assigned to bricks)
  Test Coverage: 73% (11/15 test nodes assigned to bricks)
  Boundary Integrity: 100% (0 violations)

Subsystems:
  core: 85 nodes (6 bricks)                         <-- Shows brick count
  cli: 18 nodes (1 brick)
  ...

✓ Graph looks healthy!
```

**With `--verbose` flag:**
```
jigy status --verbose

[... same as above, plus ...]

Brick Detail:

B-GRAPH-001: Graph Core
  Layer: domain-core
  Status: stable (⚠ needs attention)
  Intent: 3 nodes (O-JIG-003, S-GRAPH-001, S-GRAPH-002)
  Code: 2 nodes (C-GRAPH-001, C-GRAPH-004)
  Tests: 2 nodes (T-GRAPH-001, T-GRAPH-002)
  Dependencies: B-PARSER-001, B-UTILS-001
  Metrics:
    - Coupling Ratio: 12:1
    - Test Coverage: 75%
    - Alignment Score: 0.85
    - Boundary Violations: 0
  Issues:
    ⚠ Test coverage below target (75% < 80%)
    ⚠ Cyclomatic complexity: medium-high

[... repeat for each Brick ...]
```

**With `--bricks` flag (Brick-focused view):**
```
jigy status --bricks

Brick Architecture Overview

Layers (4):
  └─ Foundation
     ├─ B-UTILS-001: Foundation Utilities
     └─ B-CONFIG-001: Configuration & Filtering

  └─ Domain Core
     ├─ B-PARSER-001: Intent Parser
     ├─ B-VALIDATOR-001: Intent Validator
     └─ B-GRAPH-001: Graph Core

  └─ Analysis & Discovery
     ├─ B-INDEX-001: Index Builder
     ├─ B-SCANNER-001: Annotation Scanner
     ├─ B-ANNOT-VAL-001: Annotation Validator
     └─ B-DECOMP-001: Decomposition Analysis

  └─ Interface
     └─ B-CLI-001: CLI Commands

Brick Dependencies:
  B-CLI-001 → [ALL]
  B-INDEX-001 → [B-PARSER-001, B-SCANNER-001, B-GRAPH-001]
  B-DECOMP-001 → [B-GRAPH-001]
  B-GRAPH-001 → [B-PARSER-001, B-UTILS-001]
  ...

Brick Health Summary:
  ✓ 8 healthy
  ⚠ 2 need attention (low test coverage)
  ✗ 0 failing

Alignment Summary:
  Intent → Brick: 98% (54/55)
  Code → Brick: 100% (35/35)
  Test → Brick: 73% (11/15)
  Boundary Violations: 0
```

### 4.3 Implementation

```python
# In src/jig/cli/status.py

def calculate_brick_metrics(graph: Graph) -> BrickMetrics:
    """Calculate Brick-level alignment and health metrics.

    Returns:
        BrickMetrics with alignment scores, boundary violations, etc.
    """
    brick_nodes = [n for n in graph.nodes.values() if n.type == "brick"]

    metrics = BrickMetrics()

    for brick in brick_nodes:
        # Check Intent alignment
        declared_intent = brick.metadata.get("contains_intent", [])
        actual_intent = graph.get_nodes_by_brick(brick.id, types=["outcome", "specification"])
        metrics.intent_coverage[brick.id] = len(actual_intent) / len(declared_intent) if declared_intent else 1.0

        # Check boundary violations
        code_nodes = brick.metadata.get("code", {}).get("paths", [])
        declared_deps = brick.metadata.get("depends_on", [])
        violations = check_boundary_violations(graph, code_nodes, declared_deps)
        metrics.boundary_violations[brick.id] = violations

        # ... more checks

    return metrics
```

---

## 5. New Commands

### 5.1 `jigy brick` Command Group

New top-level command for Brick operations:

```bash
jigy brick --help

Usage: jigy brick [OPTIONS] COMMAND [ARGS]...

  Manage and query Bricks (architectural units).

Commands:
  list      List all Bricks
  show      Show details for a specific Brick
  validate  Validate Brick boundaries and alignment
  deps      Show Brick dependency graph
  context   Show Brick context (what's visible inside a Brick)
  health    Show Brick health report
  create    Create a new Brick definition file
```

#### 5.1.1 `jigy brick list`

```bash
jigy brick list

Bricks (10):

Foundation:
  B-UTILS-001     Foundation Utilities      stable    ✓
  B-CONFIG-001    Configuration             stable    ✓

Domain Core:
  B-PARSER-001    Intent Parser             stable    ✓
  B-VALIDATOR-001 Intent Validator          stable    ✓
  B-GRAPH-001     Graph Core                stable    ⚠

Analysis & Discovery:
  B-INDEX-001     Index Builder             stable    ✓
  B-SCANNER-001   Annotation Scanner        stable    ✓
  B-ANNOT-VAL-001 Annotation Validator      stable    ✓
  B-DECOMP-001    Decomposition Analysis    stable    ✓

Interface:
  B-CLI-001       CLI Commands              stable    ⚠
```

**With filters:**
```bash
jigy brick list --layer domain-core
jigy brick list --status needs-attention
jigy brick list --subsystem core
```

#### 5.1.2 `jigy brick show <brick-id>`

```bash
jigy brick show B-GRAPH-001

Brick: B-GRAPH-001 (Graph Core)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Identity:
  ID: B-GRAPH-001
  Name: Graph Core
  Version: 1.0.0
  Layer: domain-core
  Status: stable

Responsibility:
  Graph data structures and query operations.
  Defines Graph, Node, Edge, Subsystem classes.
  Loads graph from jig/ directory, queries graph
  (dependencies, dependents, paths), and manages
  subsystem hierarchy.

Interface (Public API):
  Classes:
    • Graph
    • Edge
    • Subsystem

  Stability: stable
  Versioning: semver

Dependencies:
  Bricks:
    → B-PARSER-001 (Intent Parser)
    → B-UTILS-001 (Foundation Utilities)

  External:
    • networkx
    • json

Contents:
  Intent: 4 nodes
    • O-JIG-003: JIG is composable (pipes work)
    • S-GRAPH-001: Status calculation logic
    • S-GRAPH-002: Core graph data structures
    • S-GRAPH-003: Graph traversal and query

  Code: 2 files (696 LOC)
    • src/jig/core/graph.py
    • src/jig/core/relationships.py

  Tests: 4 files (48 tests, 75% coverage)
    • tests/unit/test_graph.py
    • tests/unit/test_graph_queries.py
    • tests/unit/test_graph_traversal.py
    • tests/unit/test_relationship_parsing.py

Metrics:
  Coupling Ratio: 12:1
  Test Coverage: 75%
  Alignment Score: 0.85
  Boundary Violations: 0
  Cyclomatic Complexity: medium-high

Health: ⚠ Needs Attention
  Issues:
    ⚠ Test coverage below target (75% < 80%)
    ⚠ Cyclomatic complexity medium-high

  Last Review: 2025-11-25
```

#### 5.1.3 `jigy brick validate`

```bash
jigy brick validate

Validating Brick boundaries and alignment...

B-UTILS-001 (Foundation Utilities):
  ✓ All declared Intent nodes exist
  ✓ All code files have @jig annotations
  ✓ All test files verified
  ✓ No boundary violations

B-GRAPH-001 (Graph Core):
  ✓ All declared Intent nodes exist
  ✓ Code files verified
  ⚠ Test coverage below target (75% < 80%)
  ✓ No boundary violations

B-INDEX-001 (Index Builder):
  ✓ All declared Intent nodes exist
  ✓ Code files verified
  ✓ Test files verified
  ✗ Boundary violation detected!
      File: src/jig/core/index_builder.py:245
      Calls: C-SCANNER-001.scan() outside declared dependencies
      Declared deps: [B-PARSER-001, B-GRAPH-001]
      Missing: B-SCANNER-001

Summary:
  ✓ 8 bricks valid
  ⚠ 1 brick with warnings
  ✗ 1 brick with errors

Run 'jigy brick validate --fix' to get suggestions for fixing issues.
```

#### 5.1.4 `jigy brick deps <brick-id>`

```bash
jigy brick deps B-INDEX-001

B-INDEX-001 (Index Builder)

Direct Dependencies (3):
  → B-PARSER-001 (Intent Parser)
  → B-SCANNER-001 (Annotation Scanner)
  → B-GRAPH-001 (Graph Core)

Transitive Dependencies (2):
  → B-UTILS-001 (Foundation Utilities)  [via B-PARSER-001, B-GRAPH-001]
  → B-CONFIG-001 (Configuration)        [via B-SCANNER-001]

Dependents (1):
  ← B-CLI-001 (CLI Commands)

Dependency Path to Foundation:
  B-INDEX-001 → B-PARSER-001 → B-UTILS-001

With --graph flag:
  Shows ASCII dependency graph
```

#### 5.1.5 `jigy brick context <brick-id>`

```bash
jigy brick context B-INDEX-001

Brick Context: B-INDEX-001 (Index Builder)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What's VISIBLE inside this Brick:

This Brick:
  Intent: 2 nodes
    • O-INDEX-001: Graph index accurately reflects sources
    • S-INDEX-001: Index rebuild regenerates from sources

  Code: 1 file (530 LOC)
    • src/jig/core/index_builder.py

  Tests: 3 files (18 tests)
    • tests/unit/test_index_rebuild.py
    • tests/unit/test_graph_index_loading.py
    • tests/unit/test_node_registry.py

Dependencies (Public Interfaces Only):
  From B-PARSER-001:
    • class OSTCNode
    • function parse_ostc_node(path: Path) -> OSTCNode

  From B-SCANNER-001:
    • class AnnotationScanner
    • function scan(paths: list[Path]) -> list[Annotation]

  From B-GRAPH-001:
    • class Graph
    • class Edge

What's HIDDEN (not accessible):
  • All implementation details of dependency Bricks
  • All code outside this Brick's declared files
  • All Bricks not in dependency list

This enforces the Brick Context Contract.
```

#### 5.1.6 `jigy brick health`

```bash
jigy brick health

Brick Health Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Health: ⚠ Fair (8 healthy, 2 need attention)

By Layer:

Foundation (2 bricks):
  ✓ B-UTILS-001: Excellent (100% test coverage, 0 violations)
  ✓ B-CONFIG-001: Excellent (90% test coverage, 0 violations)

Domain Core (3 bricks):
  ✓ B-PARSER-001: Good (85% test coverage)
  ✓ B-VALIDATOR-001: Good (80% test coverage)
  ⚠ B-GRAPH-001: Fair (75% test coverage, high complexity)

Analysis & Discovery (4 bricks):
  ✓ B-INDEX-001: Good
  ✓ B-SCANNER-001: Excellent (90% coverage)
  ✓ B-ANNOT-VAL-001: Good
  ✓ B-DECOMP-001: Excellent

Interface (1 brick):
  ⚠ B-CLI-001: Fair (70% test coverage, high coupling)

Metrics Summary:
  Average Test Coverage: 82%
  Average Coupling Ratio: 11:1
  Total Boundary Violations: 0
  Average Alignment Score: 0.88

Top Issues:
  1. B-GRAPH-001: Test coverage below target (75% < 80%)
  2. B-CLI-001: Test coverage below target (70% < 80%)
  3. B-GRAPH-001: High cyclomatic complexity
  4. B-CLI-001: High coupling (expected for orchestrator)

Recommendations:
  → Add tests to B-GRAPH-001 (focus on graph traversal)
  → Add tests to B-CLI-001 (focus on formatting logic)
  → Consider splitting B-GRAPH-001 if complexity grows
```

### 5.2 Enhanced `jigy graph` Commands

Add Brick-aware queries to existing graph commands:

#### 5.2.1 `jigy graph deps --brick`

```bash
jigy graph deps O-JIG-003 --brick

Dependencies of O-JIG-003:
  [direct dependencies as before]

Brick Context:
  O-JIG-003 is contained in: B-GRAPH-001 (Graph Core)

  Visible from B-GRAPH-001:
    • All nodes in B-GRAPH-001
    • Public interfaces of B-PARSER-001, B-UTILS-001
```

#### 5.2.2 `jigy graph path --respect-bricks`

```bash
jigy graph path O-CLI-001 S-GRAPH-002 --respect-bricks

Path found (respecting Brick boundaries):
  O-CLI-001
    → [in B-CLI-001]
  B-CLI-001
    → [depends_on]
  B-GRAPH-001
    → [contains_intent]
  S-GRAPH-002

This path respects Brick boundaries (goes through public interfaces).

Without --respect-bricks, shortest path would be:
  O-CLI-001 → C-STATUS-001 → S-GRAPH-002
  (but C-STATUS-001 is internal to B-CLI-001)
```

### 5.3 `jigy validate` Enhancement

Add Brick validation to existing validation:

```bash
jigy validate

Validating JIG graph...

Schema Validation:
  ✓ All node IDs valid (120 nodes)
  ✓ No duplicate IDs
  ✓ All edge targets exist (178 edges)

Graph Consistency:
  ✓ No self-loops
  ✓ Edge type rules valid
  ✓ Subsystem hierarchy valid

Brick Validation:                                    <-- NEW
  ✓ All Brick definitions valid (10 bricks)
  ✓ All Brick dependencies exist
  ⚠ 2 Bricks below test coverage target
  ✗ 1 Brick has boundary violations

  Issues:
    ⚠ B-GRAPH-001: Test coverage 75% (target: 80%)
    ⚠ B-CLI-001: Test coverage 70% (target: 80%)
    ✗ B-INDEX-001: Boundary violation in index_builder.py:245

Exit code: 1 (errors present)

Run 'jigy brick validate' for detailed Brick validation.
```

---

## 6. Alignment Queries

New graph queries specifically for Brick alignment:

### 6.1 Intent → Brick Alignment

**Query:** Which Intent nodes are not assigned to any Brick?

```bash
jigy graph query unassigned-intent

Intent nodes without Brick assignment (1):
  O-JIG-006: JIG demonstrates modularity >0.7
    Suggestion: Assign to B-DECOMP-001 (Decomposition Analysis)

Run 'jigy brick assign O-JIG-006 B-DECOMP-001' to fix.
```

### 6.2 Code → Brick Alignment

**Query:** Which Code nodes are not assigned to any Brick?

```bash
jigy graph query unassigned-code

Code nodes without Brick assignment (2):
  C-UTIL-003 (src/jig/utils/string_utils.py:10)
    Suggestion: Assign to B-UTILS-001 (Foundation Utilities)

  C-TEMP-001 (src/jig/templates/node_template.py:5)
    Suggestion: Create new Brick for template system

Run 'jigy brick assign <node-id> <brick-id>' to fix.
```

### 6.3 Test → Brick Alignment

**Query:** Which Bricks have insufficient test coverage?

```bash
jigy graph query brick-test-coverage

Bricks with insufficient test coverage (2):

B-GRAPH-001 (Graph Core):
  Coverage: 75% (target: 80%)
  Missing tests for:
    • src/jig/core/graph.py:234-267 (Subsystem.find_subsystem)
    • src/jig/core/relationships.py:89-102 (extract_edges)

B-CLI-001 (CLI Commands):
  Coverage: 70% (target: 80%)
  Missing tests for:
    • src/jig/cli/formatting.py:145-178 (format_node_summary)
    • src/jig/cli/status.py:334-365 (format_suggestions)
```

### 6.4 Boundary Violations

**Query:** Which code nodes call across Brick boundaries illegally?

```bash
jigy graph query boundary-violations

Boundary violations (1):

B-INDEX-001 (Index Builder):
  src/jig/core/index_builder.py:245
    Calls: scanner.scan(paths)
    Target: C-SCANNER-001 in B-SCANNER-001
    Problem: B-SCANNER-001 not in declared dependencies

    Fix: Add B-SCANNER-001 to dependencies in jig/bricks/index-builder.brick.yaml

Total violations: 1
```

---

## 7. Brick Definition File Format

### 7.1 Schema

```yaml
# jig/bricks/<brick-name>.brick.yaml
brick:
  id: B-<PREFIX>-<NUMBER>         # Required: Unique Brick ID
  name: string                     # Required: Human-readable name
  version: semver                  # Required: Brick version
  layer: string                    # Required: architectural layer
                                   #   (foundation, domain-core, analysis, interface)

responsibility: |                  # Required: What this Brick does
  Multiline description of
  Brick's responsibility.

interface:                         # Required: Public API
  public:
    - class: ClassName             # Public classes
      methods:                     # Optional: key methods
        - method_name(args) -> return_type
    - function: function_name      # Public functions

  stability: stable | unstable     # API stability guarantee
  versioning: semver | date        # Versioning strategy

dependencies:                      # Required: What this Brick uses
  bricks:
    - B-OTHER-001                  # Other Bricks (by ID)
  external:
    - library-name                 # External dependencies

code:                              # Required: Code location
  paths:
    - src/path/to/file.py          # List of source files
  loc: number                      # Lines of code (informational)

tests:                             # Required: Test location
  paths:
    - tests/path/to/test.py        # List of test files
  count: number                    # Test count (informational)
  coverage: percentage             # Test coverage (informational)

intent:                            # Required: Intent nodes
  outcomes:
    - O-PREFIX-001                 # Outcome IDs
  specifications:
    - S-PREFIX-001                 # Specification IDs
  notes: |                         # Optional: Intent notes
    Additional context about Intent mapping.

metrics:                           # Optional: Health metrics
  coupling_ratio: string           # e.g., "12:1"
  test_coverage: percentage        # e.g., 0.75
  cyclomatic_complexity: low | medium | high
  boundary_violations: number      # Count of violations
  alignment_score: float           # 0.0-1.0

health:                            # Optional: Health status
  score: excellent | good | fair | poor
  status: stable | needs-attention | failing
  last_review: date                # ISO date
  notes: |
    Health notes and observations.
```

### 7.2 Validation Rules

A valid Brick definition must:
1. ✅ Have a unique ID in format `B-<PREFIX>-<NUMBER>`
2. ✅ Declare a non-empty responsibility
3. ✅ Declare at least one public interface element
4. ✅ List all code file paths (must exist)
5. ✅ List all test file paths (must exist)
6. ✅ Reference existing Brick IDs in `dependencies.bricks`
7. ✅ Reference existing O/S nodes in `intent.outcomes` and `intent.specifications`
8. ✅ Have code files that contain `@jig` annotations matching the Brick ID
9. ✅ Not have circular dependencies (detected via graph cycle check)

**Validation command:**
```bash
jigy brick validate jig/bricks/graph-core.brick.yaml

Validating jig/bricks/graph-core.brick.yaml...

✓ Valid Brick ID: B-GRAPH-001
✓ Responsibility declared
✓ Public interface declared (3 classes)
✓ All code paths exist (2 files)
✓ All test paths exist (4 files)
✓ All dependencies exist (2 bricks)
✓ All intent references valid (4 nodes)
✓ No circular dependencies
⚠ Test coverage below target (75% < 80%)

Valid with warnings.
```

---

## 8. Migration Path

### 8.1 Phase 1: Add Brick Support (Backward Compatible)

**Week 1: Data Model**
- [ ] Add `Brick` node type to data model
- [ ] Add Brick relationship edges
- [ ] Update `graph-index.json` format to v2.0 (backward compatible)
- [ ] Update `OSTCNode` class to support `type="brick"`

**Week 2: Discovery**
- [ ] Implement `discover_brick_nodes()` in `IndexBuilder`
- [ ] Add `.brick.yaml` parser
- [ ] Update `jigy index rebuild` to discover Bricks
- [ ] Add Brick validation to `IndexBuilder._validate_nodes()`

**Week 3: Display**
- [ ] Update `jigy status` to show Brick count
- [ ] Add Brick section to status output
- [ ] Update subsystem display to show Brick count

**Deliverable:** `jigy index rebuild` and `jigy status` recognize Bricks

### 8.2 Phase 2: Brick Commands

**Week 4: Basic Queries**
- [ ] Implement `jigy brick list`
- [ ] Implement `jigy brick show <id>`
- [ ] Add `--bricks` flag to `jigy status`

**Week 5: Validation**
- [ ] Implement `jigy brick validate`
- [ ] Add boundary violation detection
- [ ] Add alignment checking (Intent ↔ Code ↔ Test)

**Week 6: Dependency Analysis**
- [ ] Implement `jigy brick deps <id>`
- [ ] Implement `jigy brick context <id>`
- [ ] Add cycle detection for Brick dependencies

**Deliverable:** Full `jigy brick` command suite

### 8.3 Phase 3: Alignment Tracking

**Week 7: Alignment Metrics**
- [ ] Implement alignment score calculation
- [ ] Add Intent → Brick coverage metric
- [ ] Add Code → Brick coverage metric
- [ ] Add Test → Brick coverage metric

**Week 8: Drift Detection**
- [ ] Implement boundary violation detection
- [ ] Add unassigned node detection
- [ ] Add orphaned Intent detection

**Week 9: Health Reporting**
- [ ] Implement `jigy brick health`
- [ ] Add health scoring algorithm
- [ ] Add health trend tracking

**Deliverable:** Full alignment tracking and drift detection

### 8.4 Phase 4: Agent Integration (Future)

**Month 4+: Agent Context Enforcement**
- [ ] Design Brick Context Contract enforcement
- [ ] Implement context generation for agents
- [ ] Add Architecture Mode (Brick-level view)
- [ ] Add Implementation Mode (single-Brick context)
- [ ] Integrate with Claude Code or other AI tools

**Deliverable:** Agent-ready Brick contexts

---

## 9. Backward Compatibility

### 9.1 Guarantees

1. **Existing projects without Bricks continue to work**
   - `jigy` commands work as before
   - No Bricks → no Brick-related output
   - `graph-index.json` v1.0 still valid

2. **Incremental adoption**
   - Projects can add Bricks gradually
   - Mixed state (some subsystems with Bricks, some without) is valid
   - No forced migration

3. **Old tools can read new format**
   - `graph-index.json` v2.0 is backward compatible
   - Old tools ignore `"type": "brick"` nodes
   - `"bricks"` section is optional

### 9.2 Breaking Changes

None. All changes are additive.

### 9.3 Migration Tools

```bash
jigy brick bootstrap

Analyzing codebase to suggest Brick definitions...

Discovered 10 potential Bricks:
  1. Foundation Utilities (2 files, 173 LOC)
  2. Configuration (2 files, 219 LOC)
  ...

Create Brick definition files? [y/n]: y

Creating jig/bricks/foundation-utilities.brick.yaml... ✓
Creating jig/bricks/configuration.brick.yaml... ✓
...

Run 'jigy index rebuild' to include Bricks in graph-index.json.
```

---

## 10. Open Questions

### 10.1 Technical

1. **Brick granularity:** What's the right size for a Brick?
   - Current proposal: 100-700 LOC per Brick
   - Need empirical data from usage

2. **Nested Bricks:** Should Bricks support hierarchy?
   - Current proposal: Flat Bricks with layering
   - Alternative: Allow Bricks to contain sub-Bricks

3. **Dynamic boundaries:** How to handle runtime-only dependencies?
   - Current proposal: Static analysis only
   - Future: Runtime instrumentation

4. **External code:** How to handle third-party libraries?
   - Current proposal: External dependencies are declared but not Bricks
   - Alternative: Create "virtual Bricks" for major libraries

### 10.2 Process

1. **Brick ownership:** Who maintains Brick definitions?
   - Proposal: Same as code ownership (file-based)

2. **Brick evolution:** How do Bricks split/merge/deprecate?
   - Proposal: Version field + migration path

3. **Enforcement:** Should boundary violations block CI?
   - Proposal: Warning by default, error in strict mode

### 10.3 Validation

1. **Alignment threshold:** What's acceptable alignment score?
   - Proposal: ≥0.80 (80%)

2. **Test coverage:** What's the target per Brick?
   - Proposal: ≥80%

3. **Coupling ratio:** What's healthy coupling?
   - Proposal: ≥5:1 (domain), ≥10:1 (utilities)

---

## 11. Success Metrics

How do we know Bricks are working?

### 11.1 Adoption Metrics

- **Brick coverage:** % of code assigned to Bricks
  - Target: ≥90% within 3 months

- **Brick count:** Number of Bricks defined
  - Target: 8-15 Bricks for JIG codebase

- **Developer usage:** Frequency of `jigy brick` commands
  - Target: Used daily by active developers

### 11.2 Quality Metrics

- **Alignment score:** Avg Intent ↔ Code ↔ Test alignment
  - Target: ≥0.85

- **Boundary integrity:** % of code respecting boundaries
  - Target: 100% (zero violations)

- **Test coverage:** Avg test coverage per Brick
  - Target: ≥80%

### 11.3 Agent Metrics (Future)

- **Context efficiency:** Reduction in context size for agent tasks
  - Target: 70% reduction (seeing 1 Brick vs. entire codebase)

- **Agent accuracy:** Fewer boundary violations by agents
  - Target: 90% of agent changes respect Brick boundaries

- **Task success rate:** Agent task completion rate
  - Target: Improve by 30% with Brick context

---

## 12. Conclusion

Integrating Bricks into JIG as first-class architectural units enables:

✅ **Machine-enforceable boundaries** - Architecture becomes mechanism, not just documentation

✅ **Tri-fold alignment tracking** - Explicit binding of Intent → Implementation → Verification

✅ **Agent-ready contexts** - Bounded scopes for both human design and AI execution

✅ **Drift detection** - Measurable architectural health over time

✅ **Progressive adoption** - Backward compatible, incremental migration

### Next Steps

1. **Review this proposal** - Gather feedback from team
2. **Refine Brick schema** - Finalize `.brick.yaml` format
3. **Implement Phase 1** - Add Brick support to `jigy index rebuild` and `jigy status`
4. **Bootstrap JIG Bricks** - Create 10 Brick definitions for JIG itself (dogfooding)
5. **Validate hypothesis** - Measure alignment metrics and developer experience

The Brick model transforms JIG from an Intent tracking tool into an **Alignment Graph** - a unified, queryable representation of architectural intent, implementation reality, and verification coverage.

Architecture should be observable, measurable, and enforceable. Bricks make this possible.

---

**Document Status:** Draft for Review
**Next Review:** 2025-11-26
**Feedback:** [GitHub Issue](https://github.com/jmeyer/jig/issues/new)
