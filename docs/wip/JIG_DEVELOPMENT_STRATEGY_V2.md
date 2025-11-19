# JIG Development Strategy v2
**Date:** 2025-11-19
**Status:** Active Development Plan
**Version:** 2.0
**Previous:** JIG_DEVELOPMENT_STRATEGY.md (v1.0)

> "Intent Graph first, Delta workflows second. Build the foundation before the narrative layer."

---

## Executive Summary

This document outlines the **revised** development strategy for building **JIG (Jig Intent Graph)**, based on learnings from completing Slice 0 (Bootstrap).

**Key Change from v1:** We now prioritize building out the **Intent Graph subsystem** completely before implementing Delta extraction and harvest workflows. This allows us to:
1. Establish a solid foundation for the core data model
2. Enable graph-based analysis and visualization early
3. Practice decomposability principles on real code
4. Defer LLM-based synthesis until the deterministic layer is rock-solid

**Status:** Slice 0 complete (v0.1.0-bootstrap). Ready to begin Phase 1: Intent Graph.

---

## Part 1: What We've Built (Slice 0)

### Completed Infrastructure (v0.1.0-bootstrap)

**Commands Available:**
```bash
jigy init                          # Initialize JIG structure
jigy node create                   # Create OSTC nodes from templates
jigy validate                      # Validate graph consistency
```

**Core Modules:**
- `src/jig/core/config.py` - Configuration loading (jig.toml)
- `src/jig/core/parser.py` - YAML frontmatter + Markdown parsing
- `src/jig/core/validator.py` - Schema and graph validation
- `src/jig/utils/io.py` - File I/O operations
- `src/jig/utils/yaml_utils.py` - YAML helpers
- `src/jig/cli/init.py` - Initialization command
- `src/jig/cli/node.py` - Node creation command
- `src/jig/cli/validate.py` - Validation command

**Quality Metrics:**
- Test coverage: 89.26% (110 tests)
- Performance: All operations <50ms (target: <1s)
- Type checking: 100% (mypy strict)
- Linting: 0 errors (ruff)

**Dogfooding Status:**
- JIG's own Intent Graph initialized (9 nodes: 5 Outcomes, 4 Specifications)
- All nodes validated successfully
- Graph relationships defined (implements edges)

---

## Part 2: Revised Build Order

### Philosophy: Intent Graph First, Deltas Second

**Rationale:**
- Intent Graph is the **foundation** - it defines project constraints
- Deltas are the **narrative layer** - they explain how we got there
- Building the graph tooling first lets us practice decomposability analysis on JIG's own code
- Delta extraction requires marker definitions, harvest reports, and LLM synthesis - complex subsystem
- Separating concerns reduces coupling between subsystems

**New Phase Structure:**

### Phase 1: Intent Graph (Slices 1-4)
Build complete Intent Graph subsystem with visualization and analysis.
- Slice 1: Status & Health Monitoring
- Slice 2: Graph Relationships & Queries
- Slice 3: Decomposability Analysis
- Slice 4: Documentation & v0.2.0 Release

### Phase 2: Delta Workflows (Slices 5-8)
Build Delta lifecycle, extraction, and harvest pipeline.
- Slice 5: Delta Extraction (Markers)
- Slice 6: Integration (Harvest → Graph)
- Slice 7: Git Integration & Delta Lifecycle
- Slice 8: Documentation & v0.3.0 Release

### Phase 3: Intelligence Layer (Slices 9-11)
Add LLM-based synthesis and high-level workflows.
- Slice 9: LLM Synthesis
- Slice 10: AI-Distill (Complete Pipeline)
- Slice 11: Polish & v1.0.0 Release

---

## Part 3: Phase 1 - Intent Graph (Detailed)

### Slice 1: Status & Health Monitoring (Week 2)

**Goal:** Git-like status command showing graph health and actionable next steps.

**Deliverables:**
```bash
jigy status
# Shows:
# - Graph summary (node counts by type)
# - Recent changes (from graph-index.yaml history)
# - Validation status
# - Subsystem breakdown
# - Suggestions for next actions
```

**Implementation:**
- `src/jig/core/graph.py` - Graph data structure and operations
  ```python
  @dataclass
  class Graph:
      nodes: dict[str, OSTCNode]
      edges: list[Edge]
      subsystems: dict[str, Subsystem]

      def load_from_dir(path: Path) -> Graph:
          """Load entire graph from jig/ directory."""

      def get_node_counts_by_type() -> dict[str, int]:
          """Return counts: {outcome: 5, specification: 4, ...}"""

      def get_nodes_by_subsystem() -> dict[str, list[str]]:
          """Return nodes grouped by subsystem."""

      def find_orphaned_nodes() -> list[str]:
          """Find nodes not connected to any edges."""
  ```
- `src/jig/cli/status.py` - Status command implementation
  ```python
  @click.command()
  @click.option('--verbose', is_flag=True, help='Show detailed statistics')
  def status(verbose: bool):
      """Show JIG graph status and health."""
  ```

**Success Criteria:**
- Runs in <100ms (like `git status`)
- Clear, actionable output with color coding
- Shows subsystem breakdown
- Identifies orphaned nodes
- Suggests next actions (e.g., "5 nodes need subsystem assignment")
- Test coverage >80%

**Test Plan:**
```python
# tests/integration/test_status_command.py
def test_status_shows_node_counts():
    """Verify status displays correct node counts by type."""

def test_status_identifies_orphaned_nodes():
    """Verify status detects nodes without edges."""

def test_status_performance():
    """Verify status completes in <100ms for 100 nodes."""
```

**Expected Duration:** 3-4 days

---

### Slice 2: Graph Relationships & Queries (Week 3)

**Goal:** Navigate and query the Intent Graph programmatically and via CLI.

**Deliverables:**
```bash
jigy graph show O-JIG-001           # Show node details with relationships
jigy graph deps O-JIG-001           # Show dependency tree (what implements this?)
jigy graph impact S-JIG-002         # Show impact (what depends on this?)
jigy graph path O-JIG-001 S-JIG-004 # Find path between nodes
jigy graph list --type outcome      # List all nodes of type
jigy graph list --subsystem core    # List all nodes in subsystem
```

**Implementation:**
- `src/jig/core/graph.py` - Extend with query methods
  ```python
  class Graph:
      def get_dependencies(node_id: str) -> list[str]:
          """Return nodes that this node depends on (incoming edges)."""

      def get_dependents(node_id: str) -> list[str]:
          """Return nodes that depend on this node (outgoing edges)."""

      def find_path(start: str, end: str) -> list[str] | None:
          """Find shortest path between two nodes."""

      def filter_by_type(node_type: str) -> list[OSTCNode]:
          """Return all nodes of given type."""

      def filter_by_subsystem(subsystem: str) -> list[OSTCNode]:
          """Return all nodes in given subsystem."""
  ```
- `src/jig/cli/graph.py` - Graph command group
  ```python
  @click.group()
  def graph():
      """Query and navigate the Intent Graph."""

  @graph.command()
  @click.argument('node_id')
  def show(node_id: str):
      """Show node details and relationships."""

  @graph.command()
  @click.argument('node_id')
  def deps(node_id: str):
      """Show dependency tree for a node."""

  @graph.command()
  @click.argument('node_id')
  def impact(node_id: str):
      """Show impact analysis (what depends on this node)."""

  @graph.command()
  @click.argument('start')
  @click.argument('end')
  def path(start: str, end: str):
      """Find path between two nodes."""

  @graph.command()
  @click.option('--type', help='Filter by node type')
  @click.option('--subsystem', help='Filter by subsystem')
  def list(type: str | None, subsystem: str | None):
      """List nodes with optional filters."""
  ```

**Success Criteria:**
- All query operations <100ms for graphs with 100 nodes
- Clear, formatted output (tree structure for deps/impact)
- Handles missing nodes gracefully (clear error messages)
- Output is pipeable (can use `| grep`, `| jq` if YAML output)
- Test coverage >80%

**Test Plan:**
```python
# tests/integration/test_graph_queries.py
def test_graph_show_displays_relationships():
    """Verify show command displays node and its edges."""

def test_graph_deps_builds_tree():
    """Verify deps builds correct dependency tree."""

def test_graph_impact_finds_dependents():
    """Verify impact finds all nodes that depend on target."""

def test_graph_path_finds_shortest_path():
    """Verify path finds shortest route between nodes."""

def test_graph_list_filters_correctly():
    """Verify list filters by type and subsystem."""
```

**Expected Duration:** 4-5 days

---

### Slice 3: Decomposability Analysis (Week 4-5)

**Goal:** Measure and visualize subsystem boundaries, detect violations.

**Deliverables:**
```bash
jigy decompose detect               # Auto-detect subsystems from code
jigy decompose metrics              # Calculate health scores
jigy decompose validate             # Check for boundary violations
jigy decompose report               # Generate detailed analysis
```

**Implementation:**
- `src/jig/decompose/__init__.py`
- `src/jig/decompose/detector.py` - Community detection algorithms
  ```python
  def detect_subsystems(graph: Graph) -> dict[str, Subsystem]:
      """Auto-detect subsystems using Louvain method."""
      import networkx as nx
      from networkx.algorithms import community

      G = graph.to_networkx()
      communities = community.louvain_communities(G)
      # Convert to Subsystem objects

  def suggest_subsystem_names(subsystem: Subsystem) -> list[str]:
      """Suggest names based on node titles and patterns."""
  ```
- `src/jig/decompose/metrics.py` - Modularity and coupling calculations
  ```python
  @dataclass
  class DecomposabilityMetrics:
      modularity: float              # Newman modularity score
      coupling_ratio: float          # Internal:external edges
      module_depth: float            # LOC per export (code analysis)
      subsystem_count: int
      avg_subsystem_size: float
      boundary_violations: list[str]

  def calculate_modularity(graph: Graph) -> float:
      """Calculate Newman modularity score."""

  def calculate_coupling_ratio(subsystem: Subsystem, graph: Graph) -> float:
      """Calculate internal:external edge ratio."""

  def detect_boundary_violations(graph: Graph) -> list[str]:
      """Find edges that violate subsystem boundaries."""
  ```
- `src/jig/decompose/analyzer.py` - High-level analysis orchestration
  ```python
  def analyze_decomposability(graph: Graph) -> DecomposabilityMetrics:
      """Run full decomposability analysis."""

  def generate_report(metrics: DecomposabilityMetrics) -> str:
      """Generate human-readable analysis report."""
  ```
- `src/jig/cli/decompose.py` - Decompose command group
  ```python
  @click.group()
  def decompose():
      """Analyze subsystem decomposability."""

  @decompose.command()
  def detect():
      """Auto-detect subsystems from graph structure."""

  @decompose.command()
  def metrics():
      """Calculate decomposability health scores."""

  @decompose.command()
  def validate():
      """Check for subsystem boundary violations."""

  @decompose.command()
  @click.option('--output', help='Report output file')
  def report(output: str | None):
      """Generate detailed decomposability analysis."""
  ```

**Success Criteria:**
- Modularity calculation correct (Newman algorithm)
- Coupling ratio calculation works for all subsystems
- Detects community structure automatically (Louvain)
- Runs in <5s for graphs with 100 nodes, 10 subsystems
- Identifies boundary violations (edges crossing subsystems)
- Generates clear, actionable reports
- Test coverage >80%

**Algorithms:**
- Newman modularity: Q = (1/2m) Σ[A_ij - (k_i * k_j)/2m] * δ(c_i, c_j)
- Louvain method: Iterative community detection (NetworkX implementation)
- Coupling ratio: |internal_edges| / |external_edges|

**Test Plan:**
```python
# tests/unit/test_decompose_metrics.py
def test_modularity_calculation():
    """Verify modularity score for known graph structures."""

def test_coupling_ratio_calculation():
    """Verify coupling ratio for subsystem with known edges."""

def test_detect_boundary_violations():
    """Verify detection of edges crossing subsystem boundaries."""

# tests/integration/test_decompose_workflow.py
def test_decompose_detect_finds_communities():
    """Verify community detection on sample graph."""

def test_decompose_metrics_calculates_scores():
    """Verify metrics command outputs correct scores."""

def test_decompose_performance():
    """Verify decompose completes in <5s for 100-node graph."""
```

**Note on Visualization:**
Graph visualization (rendering to images) is intentionally deferred. This can be added later as a plugin/extension using graphviz or similar tools. For v0.2.0, text-based output is sufficient.

**Expected Duration:** 6-8 days

---

### Slice 4: Documentation & v0.2.0 Release (Week 6)

**Goal:** Complete Phase 1 documentation and release v0.2.0-intent-graph.

**Deliverables:**
- Complete user guide for Intent Graph commands
- Architecture documentation for graph subsystem
- API documentation (docstrings + Sphinx)
- Tutorial: "Building an Intent Graph for Your Project"
- Quality gates pass (tests, coverage, linting, type checking)
- Git tag: v0.2.0-intent-graph

**Implementation:**
- `docs/user-guide/GRAPH_COMMANDS.md` - Guide to jigy graph, status, decompose
- `docs/architecture/GRAPH_SUBSYSTEM.md` - Technical architecture of graph subsystem
- `docs/tutorials/INTENT_GRAPH_TUTORIAL.md` - Step-by-step guide
- `docs/api/` - Sphinx-generated API docs
- Update README.md with new commands and examples

**Success Criteria:**
- All commands documented with examples
- Architecture docs explain design decisions
- Tutorial walkthrough works end-to-end
- All quality gates pass:
  - `pytest` - all tests pass
  - `pytest --cov` - coverage >80%
  - `ruff check` - no errors
  - `mypy src/` - no type errors
- Dogfooding: JIG's own graph analyzed with decompose commands
- Git tag created: v0.2.0-intent-graph

**Test Plan:**
- Manual review: Follow tutorial start to finish
- Automated: Run all quality gates in CI
- Dogfooding: Run all new commands on JIG's own graph

**Expected Duration:** 3-4 days

---

## Part 4: Phase 2 - Delta Workflows (Summary)

After completing Phase 1, we'll build Delta extraction and harvest workflows:

### Slice 5: Delta Extraction (Week 7-8)
**Goal:** Extract markers from Delta documents, generate harvest reports.
- Implement marker definitions (#VIB, #OSTC, #DISCOVERY, #DECISION, #LEARNED)
- Build deterministic extractor using ripgrep + regex
- Generate structured HarvestReport (YAML)
- Commands: `jigy extract --branch <name>`

### Slice 6: Integration (Week 9)
**Goal:** Update Intent Graph from harvest reports.
- Implement integrator to update OSTC nodes
- Handle conflicts (human review required)
- Commands: `jigy integrate --harvest <file>`

### Slice 7: Git Integration & Delta Lifecycle (Week 10)
**Goal:** Branch-bound Delta management, git hooks.
- Delta templates and creation workflow
- Branch binding (Deltas tied to git branches)
- Auto-archiving on merge
- Git hooks (pre-push warnings)
- Commands: `jigy delta new`, `jigy delta archive`, `jigy git install-hooks`

### Slice 8: Documentation & v0.3.0 Release (Week 11)
**Goal:** Complete Phase 2 documentation, release v0.3.0-delta-workflows.

---

## Part 5: Phase 3 - Intelligence Layer (Summary)

After completing Phase 2, we'll add LLM-based synthesis:

### Slice 9: LLM Synthesis (Week 12-13)
**Goal:** LLM-assisted synthesis of harvest into Intent proposals.
- Implement LLM orchestration (Anthropic API)
- Prompt engineering for synthesis
- Conflict detection
- Commands: `jigy ai-synthesize --harvest <file>`

### Slice 10: AI-Distill (Week 14)
**Goal:** One-command harvest workflow.
- Orchestrate: extract → ai-synthesize → ai-integrate
- Interactive approval UI
- Commands: `jigy ai-distill --branch <name>`

### Slice 11: Polish & v1.0.0 Release (Week 15)
**Goal:** Production-ready v1.0.0.
- Complete user guide
- Performance benchmarks
- PyPI packaging: `pip install jig-cli`
- Full test suite with >85% coverage

---

## Part 6: Technical Architecture

### Subsystem Boundaries (Updated)

| Subsystem | Purpose | Key Exports | Dependencies |
|-----------|---------|-------------|--------------|
| **core** | Graph data structures, validation | `Graph`, `OSTCNode`, `Validator`, `Parser` | utils |
| **decompose** | Architecture analysis | `MetricsCalculator`, `Detector`, `Analyzer` | core, networkx |
| **delta** | Delta lifecycle (Phase 2) | `DeltaManager`, `HarvestReport` | core, utils |
| **synthesis** | LLM intelligence (Phase 3) | `Synthesizer`, `SynthesisProposal` | core, delta |
| **git_integration** | Git hooks (Phase 2) | `GitHooks`, `BranchManager` | delta, core |
| **cli** | User-facing commands | `jigy` command group | all subsystems |

### Data Formats

**Graph Index (YAML):**
```yaml
version: 1.0.0
created: 2025-11-19

nodes:
  O-JIG-001:
    file: jig/outcomes/O-JIG-001.md
    type: outcome
    title: "JIG tools run in <1 second"
    subsystem: core

edges:
  - from: S-JIG-001
    to: O-JIG-001
    type: implements

subsystems:
  core:
    nodes:
      - O-JIG-001
      - S-JIG-001
```

**OSTC Node (Markdown with YAML frontmatter):**
```markdown
---
id: O-JIG-001
type: outcome
title: "JIG tools run in <1 second"
subsystem: core
status: active
created: 2025-11-18
---

JIG tools must provide instant feedback to developers...

## Success Metrics
- `jigy status` completes in <100ms
- `jigy validate` completes in <1s for 1000 nodes
...
```

**Decomposability Report (YAML):**
```yaml
analysis:
  timestamp: 2025-11-19T10:30:00Z
  graph_size: 47
  subsystem_count: 3

metrics:
  modularity: 0.73
  avg_coupling_ratio: 12.5
  boundary_violations: []

subsystems:
  core:
    node_count: 35
    internal_edges: 42
    external_edges: 3
    coupling_ratio: 14.0
    modularity_contribution: 0.62
```

### Performance Targets (Phase 1)

| Operation | Target | Rationale |
|-----------|--------|-----------|
| `jigy status` | <100ms | Must feel instant (like `git status`) |
| `jigy graph show` | <100ms | Simple node lookup |
| `jigy graph deps` | <200ms | Requires graph traversal |
| `jigy validate` | <1s | Deterministic file I/O |
| `jigy decompose metrics` | <5s | Complex graph algorithms |

---

## Part 7: Dogfooding Strategy (Phase 1)

### Using JIG to Build JIG - Phase 1 Focus

**Current State:**
- JIG's Intent Graph initialized (9 nodes)
- Slice 0 completed without Deltas (pre-dogfooding)

**Phase 1 Dogfooding:**
1. **Manually create OSTC nodes for Phase 1 work**
   - Create Outcome nodes for each slice (O-STATUS-001, O-GRAPH-001, O-DECOMP-001)
   - Create Specification nodes for commands (S-STATUS-001, S-GRAPH-001, etc.)
   - Use `jigy node create` and manual editing

2. **Test commands on JIG's own graph**
   - Run `jigy status` to see JIG's own health
   - Run `jigy graph show O-JIG-001` to navigate JIG's constraints
   - Run `jigy decompose metrics` to measure JIG's modularity

3. **Update graph as Phase 1 progresses**
   - Add Test nodes (T-STATUS-001, etc.) as tests are written
   - Update graph-index.yaml with new relationships
   - Use `jigy validate` to ensure consistency

4. **Measure JIG's own decomposability**
   - Target: Modularity >0.7
   - Target: Coupling ratio >10:1 for all subsystems
   - Target: <5 exports per subsystem

**Note:** Full Delta-based dogfooding (writing Deltas for each slice) begins in Phase 2 when Delta tooling is available.

---

## Part 8: Development Principles (Unchanged from v1)

### Build Philosophy

**1. Vertical Slices Over Horizontal Layers**
- Build complete workflows before adding features
- Each slice delivers end-to-end value

**2. Dogfood Relentlessly**
- Use JIG to build JIG from Day 1
- Practice what we preach (decomposability)

**3. Simple > Clever**
- Regex over AST parsing
- YAML over SQL
- Grep over indexing

**4. Fast > Feature-Rich**
- Deterministic operations <1s
- Defer expensive operations (LLM) to later phases

**5. Explicit > Implicit**
- No magic: developers control everything
- No hidden state: everything in git

**6. Test Before Scale**
- Unit tests for algorithms
- Integration tests for workflows
- E2E tests for user journeys

---

## Part 9: Risk Management

### Known Risks (Phase 1)

| Risk | Mitigation |
|------|------------|
| **NetworkX performance degrades** | Benchmark continuously; consider graph-tool if needed |
| **Graph complexity explodes** | Enforce size limits; test with 100-1000 node graphs |
| **Modularity calculation expensive** | Cache results; optimize algorithm; set timeout |
| **Subsystem detection inaccurate** | Provide manual override; allow user-defined subsystems |
| **Boundary violation detection too strict** | Make configurable; allow exceptions |

### Validation Checkpoints (After Each Slice)

- [ ] All tests pass (>80% coverage)
- [ ] Performance targets met
- [ ] Dogfooding successful (used on JIG itself)
- [ ] Documentation updated
- [ ] No regressions in existing commands

---

## Part 10: Success Criteria

### Phase 1 Success (v0.2.0-intent-graph)

**Functionality:**
- [ ] `jigy status` shows graph health
- [ ] `jigy graph` commands enable navigation
- [ ] `jigy decompose` analyzes subsystem boundaries
- [ ] All commands work on JIG's own graph

**Performance:**
- [ ] `jigy status` <100ms
- [ ] `jigy graph show` <100ms
- [ ] `jigy graph deps` <200ms
- [ ] `jigy decompose metrics` <5s for 100 nodes

**Quality:**
- [ ] Test coverage >80%
- [ ] Type hints throughout (mypy clean)
- [ ] Passes ruff linting
- [ ] Zero critical bugs

**Dogfooding:**
- [ ] JIG's own graph contains 20+ OSTC nodes
- [ ] Modularity score >0.7 for JIG codebase
- [ ] Coupling ratio >10:1 for core subsystem
- [ ] All Phase 1 constraints captured as OSTC nodes

---

## Part 11: Timeline Summary (Revised)

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **✓ Slice 0: Bootstrap** | Week 1 (DONE) | `jigy init`, `jigy node create`, `jigy validate` |
| **Phase 1: Intent Graph** | Weeks 2-6 | Graph queries, status, decomposability |
| └─ Slice 1: Status | Week 2 | `jigy status` |
| └─ Slice 2: Graph Queries | Week 3 | `jigy graph show/deps/impact/path/list` |
| └─ Slice 3: Decompose | Weeks 4-5 | `jigy decompose detect/metrics/validate/report` |
| └─ Slice 4: Docs & v0.2.0 | Week 6 | User guide, v0.2.0-intent-graph release |
| **Phase 2: Delta Workflows** | Weeks 7-11 | Extract, integrate, lifecycle |
| └─ Slice 5: Extraction | Weeks 7-8 | `jigy extract` |
| └─ Slice 6: Integration | Week 9 | `jigy integrate` |
| └─ Slice 7: Git & Lifecycle | Week 10 | `jigy delta`, `jigy git` |
| └─ Slice 8: Docs & v0.3.0 | Week 11 | v0.3.0-delta-workflows release |
| **Phase 3: Intelligence Layer** | Weeks 12-15 | LLM synthesis, AI-distill |
| └─ Slice 9: Synthesis | Weeks 12-13 | `jigy ai-synthesize` |
| └─ Slice 10: AI-Distill | Week 14 | `jigy ai-distill` |
| └─ Slice 11: Polish & v1.0 | Week 15 | v1.0.0 release, PyPI package |

**Total:** 15 weeks to v1.0 (assuming 1 developer, part-time)

**Next Milestone:** v0.2.0-intent-graph (end of Week 6)

---

## Part 12: Next Steps

### Immediate Actions (Week 2 - Slice 1)

**Branch:** `feature/slice-1-status`

**Tasks:**
1. **Create OSTC nodes for Slice 1**
   ```bash
   jigy node create --type outcome --id O-STATUS-001 --title "Status shows graph health in <100ms" --subsystem core
   jigy node create --type specification --id S-STATUS-001 --title "Status displays node counts and subsystem breakdown" --subsystem core
   ```

2. **Implement Graph data structure**
   ```bash
   touch src/jig/core/graph.py
   touch tests/unit/test_graph.py
   # Implement Graph class with load_from_dir, get_node_counts_by_type, etc.
   ```

3. **Implement status command**
   ```bash
   touch src/jig/cli/status.py
   touch tests/integration/test_status_command.py
   # Implement status command with colorized output
   ```

4. **Test on JIG's own graph**
   ```bash
   jigy status
   jigy status --verbose
   # Verify output is clear and actionable
   ```

5. **Write documentation**
   ```bash
   # Update docs/user-guide/ with status command examples
   # Update README.md with new command
   ```

**Expected Duration:** 3-4 days

**Success Metrics:**
- [ ] `jigy status` runs in <100ms on JIG's own graph
- [ ] Clear output with node counts, subsystem breakdown
- [ ] Identifies orphaned nodes (if any)
- [ ] Test coverage >80%
- [ ] All quality gates pass

---

## Conclusion

This revised strategy prioritizes building a **solid Intent Graph foundation** before adding Delta workflows. By completing Phase 1 first, we:

1. **Establish the core data model** - Graph operations, validation, queries
2. **Practice decomposability** - Measure JIG's own modularity
3. **Deliver incremental value** - Each slice adds usable commands
4. **Defer complexity** - LLM synthesis comes last, when foundation is solid
5. **Maintain focus** - One subsystem at a time, fully tested

**The ultimate validation:** If JIG's own graph demonstrates modularity >0.7 and coupling >10:1, we prove the concept works.

---

**Status:** Ready to begin Slice 1 (Status & Health Monitoring)
**Next:** Implement `jigy status` command and Graph data structure
**Version:** 2.0 (revised 2025-11-19)
