---
delta_type: plan
branch: phase-1-completion
supersedes: S005_PLAN_phase_1_intent_graph.md
---

# PLAN: Phase 1 Completion - Decomposability & Nested Subsystems

- **SUPERSEDES:** docs/wip/S005_PLAN_phase_1_intent_graph.md (Slices 0-2 complete)
- **SCOPE:** 
  - docs/wip/S004_JIG_DEVELOPMENT_STRATEGY_V2.md (Phase 1 - Decomposability)
  - docs/wip/S006_SCOPE_nested_subsystems.md (Nested Subsystems)
  - docs/jig-concept/JIG-Concept-v7.md (OSTCX model with constraints)
- **Start:** 2025-11-20
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** core (graph, decompose), docs

## Context: Work Completed in S005

**Slices 0-2 Complete (8 Work Units):**
- ✅ Slice 0: WU0 - Known Intent nodes created (O-GRAPH-001/002, O-DECOMP-001/002, S-GRAPH-001/002/003, S-DECOMP-001/002/003/004)
- ✅ Slice 1: WU1-WU3 - Status & Health Monitoring (Graph data structure, status command, output formatting)
- ✅ Slice 2: WU4-WU8 - Graph Relationships & Queries (Traversal, queries, show/deps/impact/path/list commands)

**Test Coverage Achieved:**
- Graph core: 94.94% (WU1)
- Status logic: 96.83% (WU2)
- Graph traversal: 96.26% (WU4)
- Graph queries: comprehensive coverage (WU5)

**Performance Benchmarks Met:**
- Status: ~25ms for 100 nodes (<100ms target) ✓
- Graph queries: <100ms for 100 nodes ✓
- Dependency traversal: <100ms for 100 nodes ✓

## Remaining Work from S005

**Slice 3: Decomposability Analysis (7 Work Units)**
- [ ] WU9: Metrics calculation (modularity, coupling)
- [ ] WU10: Community detection (Louvain)
- [ ] WU11: Boundary violation detection
- [ ] WU12: Decompose detect command
- [ ] WU13: Decompose metrics command
- [ ] WU14: Decompose validate command
- [ ] WU15: Decompose report command

**Slice 4: Documentation & Release (4 Work Units)**
- [ ] WU16: User guide for graph commands
- [ ] WU17: Architecture documentation
- [ ] WU18: Tutorial & quality gates
- [ ] WU19: Dogfooding & v0.2.0 release

## New Work: Nested Subsystems (JIG v7)

**Context:** JIG v7 introduces the OSTCX model where constraints act as predicates over the Intent Graph. Nested subsystems enable hierarchical organization while maintaining clean separation between architectural dependencies (OSTC edges) and system properties (constraint predicates).

**Benefits:**
1. Hierarchical organization reflecting real system architecture
2. Scalability for projects with 20+ subsystems
3. Both coarse-grained and fine-grained analysis
4. Improved coupling ratios (edges between siblings = internal to parent)
5. Constraint scoping works naturally with nested paths

**Slice 5: Nested Subsystems Implementation (4 Phases from S006)**
- [ ] WU20: Phase 1 - Data Model & Loading (Week 1)
- [ ] WU21: Phase 2 - Query & Navigation (Week 2)
- [ ] WU22: Phase 3 - Decomposability with Hierarchy (Week 3)
- [ ] WU23: Phase 4 - Documentation & Migration (Week 4)

## Known Intent (Created Before Coding)

**From S005 (Already Created):**
- O-GRAPH-001: "Graph queries complete in <100ms for 100 nodes"
- O-GRAPH-002: "Developers navigate Intent Graph via CLI efficiently"
- O-DECOMP-001: "JIG measures and validates subsystem boundaries"
- O-DECOMP-002: "Modularity score >0.7 for well-decomposed systems"
- S-GRAPH-001: "Status displays node counts, orphans, subsystems"
- S-GRAPH-002: "Graph data structure supports load, query, traversal"
- S-GRAPH-003: "Graph query commands: show, deps, impact, path, list"
- S-DECOMP-001: "Modularity calculation uses Newman algorithm"
- S-DECOMP-002: "Community detection uses Louvain method"
- S-DECOMP-003: "Coupling ratio = internal edges / external edges"
- S-DECOMP-004: "Boundary violation detection for cross-subsystem edges"

**New Intent for Nested Subsystems (To Be Created in WU20):**
- O-NESTED-001: "Subsystems can nest to arbitrary depth for hierarchical organization"
- O-NESTED-002: "Nested subsystem queries complete in <200ms for 100 subsystems"
- S-NESTED-001: "Subsystem dataclass supports recursive nesting"
- S-NESTED-002: "Dot notation for subsystem paths (e.g., crdt.ser)"
- S-NESTED-003: "Status command displays hierarchical tree view"
- S-NESTED-004: "Hierarchical coupling metrics aggregate child metrics"
- S-NESTED-005: "Validation ensures parent subsystems have no direct nodes"
- S-NESTED-006: "Constraint scopes can target nested subsystem paths"

## Work Unit Checklist

### Slice 3: Decomposability Analysis (Carry-over from S005)
- [ ] WU9: Metrics calculation (modularity, coupling) — tests ☐ / docs ☐ / reflect ☐
- [ ] WU10: Community detection (Louvain) — tests ☐ / docs ☐ / reflect ☐
- [ ] WU11: Boundary violation detection — tests ☐ / docs ☐ / reflect ☐
- [ ] WU12: Decompose detect command — tests ☐ / docs ☐ / reflect ☐
- [ ] WU13: Decompose metrics command — tests ☐ / docs ☐ / reflect ☐
- [ ] WU14: Decompose validate command — tests ☐ / docs ☐ / reflect ☐
- [ ] WU15: Decompose report command — tests ☐ / docs ☐ / reflect ☐

### Slice 5: Nested Subsystems Implementation (New)
- [ ] WU20: Phase 1 - Data Model & Loading — tests ☐ / docs ☐ / reflect ☐
- [ ] WU21: Phase 2 - Query & Navigation — tests ☐ / docs ☐ / reflect ☐
- [ ] WU22: Phase 3 - Decomposability with Hierarchy — tests ☐ / docs ☐ / reflect ☐
- [ ] WU23: Phase 4 - Documentation & Migration — tests ☐ / docs ☐ / reflect ☐

### Slice 4: Documentation & Release (Updated from S005)
- [ ] WU16: User guide for graph commands — tests ☐ / docs ☐ / reflect ☐
- [ ] WU17: Architecture documentation — tests ☐ / docs ☐ / reflect ☐
- [ ] WU18: Tutorial & quality gates — tests ☐ / docs ☐ / reflect ☐
- [ ] WU19: Dogfooding & v0.3.0 release — tests ☐ / docs ☐ / reflect ☐

---

## Slice 3: Decomposability Analysis

**Note:** These work units are carried over from S005_PLAN_phase_1_intent_graph.md with minimal changes. They will be implemented before starting nested subsystems work.

### Work Unit 9: Metrics Calculation (Modularity, Coupling)

**Goal:** Implement modularity and coupling ratio calculations.

**Planned Effort:** 120-150m

**Acceptance Criteria:**
- `src/jig/decompose/metrics.py` implements Newman modularity calculation
- Coupling ratio calculation (internal:external edges per subsystem)
- DecomposabilityMetrics dataclass with all fields
- Uses NetworkX for graph algorithms
- Handles edge cases (single subsystem, no edges)
- **NEW:** Coupling ratio excludes constraint relationships (v7 requirement)
- Unit tests >80% coverage with known test cases

**Implementation Notes:**
- Files to create:
  - `src/jig/decompose/__init__.py`
  - `src/jig/decompose/metrics.py`:
    ```python
    # @jig C-DECOMP-001 implements:S-DECOMP-001,S-DECOMP-003 subsystem:decompose interface:internal
    from dataclasses import dataclass
    from jig.core.graph import Graph
    import networkx as nx
    from networkx.algorithms import community

    @dataclass
    class SubsystemMetrics:
        name: str
        node_count: int
        internal_edges: int
        external_edges: int
        coupling_ratio: float

    @dataclass
    class DecomposabilityMetrics:
        modularity: float
        subsystem_count: int
        avg_coupling_ratio: float
        subsystems: dict[str, SubsystemMetrics]
        boundary_violations: list[str]

    def calculate_modularity(graph: Graph) -> float:
        """Calculate Newman modularity score.

        Q = (1/2m) Σ[A_ij - (k_i * k_j)/2m] * δ(c_i, c_j)
        where:
        - m = total edges
        - A_ij = adjacency matrix
        - k_i = degree of node i
        - δ(c_i, c_j) = 1 if nodes in same community, 0 otherwise
        """
        G = graph.to_networkx()

        # Convert subsystems to communities (list of sets)
        communities = []
        for subsystem in graph.subsystems.values():
            communities.append(set(subsystem.nodes))

        # Use NetworkX modularity calculation
        return community.modularity(G, communities)

    def calculate_coupling_ratio(subsystem_name: str, graph: Graph) -> SubsystemMetrics:
        """Calculate coupling ratio for a subsystem.

        Internal edges: both endpoints in subsystem
        External edges: one endpoint outside subsystem
        Ratio: internal / external (higher is better)
        
        Note: Constraint relationships are not counted as edges (v7).
        """
        if subsystem_name not in graph.subsystems:
            raise ValueError(f"Subsystem {subsystem_name} not found")

        subsystem_nodes = set(graph.subsystems[subsystem_name].nodes)
        internal = 0
        external = 0

        for edge in graph.edges:
            # Skip constraint edges (v7)
            if edge.type == 'satisfies':
                continue
                
            from_in = edge.from_node in subsystem_nodes
            to_in = edge.to_node in subsystem_nodes

            if from_in and to_in:
                internal += 1
            elif from_in or to_in:
                external += 1

        ratio = internal / external if external > 0 else float('inf')

        return SubsystemMetrics(
            name=subsystem_name,
            node_count=len(subsystem_nodes),
            internal_edges=internal,
            external_edges=external,
            coupling_ratio=ratio
        )

    def calculate_all_metrics(graph: Graph) -> DecomposabilityMetrics:
        """Calculate all decomposability metrics."""
        modularity = calculate_modularity(graph)

        subsystem_metrics = {}
        coupling_ratios = []

        for subsystem_name in graph.subsystems.keys():
            metrics = calculate_coupling_ratio(subsystem_name, graph)
            subsystem_metrics[subsystem_name] = metrics
            if metrics.coupling_ratio != float('inf'):
                coupling_ratios.append(metrics.coupling_ratio)

        avg_coupling = sum(coupling_ratios) / len(coupling_ratios) if coupling_ratios else 0.0

        return DecomposabilityMetrics(
            modularity=modularity,
            subsystem_count=len(graph.subsystems),
            avg_coupling_ratio=avg_coupling,
            subsystems=subsystem_metrics,
            boundary_violations=[]  # WU11 will populate this
        )
    ```

**Test Plan:**
- Unit tests in `tests/unit/test_decompose_metrics.py`:
  ```python
  # @jig T-DECOMP-001 verifies:S-DECOMP-001 subsystem:decompose
  def test_modularity_calculation_known_graph():
      """Verify modularity score for known graph structure."""
      # Create graph with 2 subsystems, known modularity
      # Calculate and compare to expected value

  # @jig T-DECOMP-002 verifies:S-DECOMP-003 subsystem:decompose
  def test_coupling_ratio_calculation():
      """Verify coupling ratio for subsystem with known edges."""
      # Subsystem with 10 internal, 2 external → ratio = 5.0

  # @jig T-DECOMP-003 verifies:S-DECOMP-001 subsystem:decompose
  def test_modularity_single_subsystem():
      """Verify modularity = 0 for single subsystem (no structure)."""

  # @jig T-DECOMP-004 verifies:S-DECOMP-003 subsystem:decompose
  def test_coupling_ratio_no_external_edges():
      """Verify ratio = inf when subsystem has no external edges."""
      
  # @jig T-DECOMP-004a verifies:S-DECOMP-003 subsystem:decompose
  def test_coupling_ratio_excludes_constraint_edges():
      """Verify constraint edges (satisfies) not counted in coupling (v7)."""
  ```

**Docs to Update:**
- Add docstrings explaining modularity and coupling ratio
- Document formulas and interpretations
- **NEW:** Document constraint edge exclusion (v7)

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [to be filled]
- What could be better:
  - [to be filled]
- Discoveries:
  - [to be filled]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands: `pytest tests/unit/test_decompose_metrics.py -v`
- Look for: Tests pass, modularity calculation correct, constraint edges excluded

---

### Work Unit 10: Community Detection (Louvain)

**Goal:** Implement automatic subsystem detection using Louvain method.

**Planned Effort:** 90-120m

**Acceptance Criteria:**
- `src/jig/decompose/detector.py` implements community detection
- Uses NetworkX louvain_communities algorithm
- Suggests subsystem names based on node patterns
- Returns proposed subsystem structure
- Handles graphs with no clear communities
- Unit tests verify detection on sample graphs

**Implementation Notes:**
[Content from S005 WU10 - unchanged]

**Test Plan:**
[Content from S005 WU10 - unchanged]

**Docs to Update:**
- Document Louvain algorithm choice
- Explain confidence scoring

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [to be filled]
- What could be better:
  - [to be filled]
- Discoveries:
  - [to be filled]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands: `pytest tests/unit/test_decompose_detector.py -v`
- Look for: Community detection works on sample graphs

---

### Work Unit 11: Boundary Violation Detection

**Goal:** Detect edges that cross subsystem boundaries improperly.

**Planned Effort:** 60-75m

**Acceptance Criteria:**
- `src/jig/decompose/analyzer.py` implements violation detection
- Identifies edges between subsystems that shouldn't exist
- Configurable allowed cross-subsystem edge types
- **NEW:** Constraint edges (satisfies) not flagged as violations (v7)
- Returns list of violation descriptions
- Unit tests verify detection logic

**Implementation Notes:**
[Content from S005 WU11, with note about constraint edges]

**Test Plan:**
[Content from S005 WU11, add test for constraint edges]

**Docs to Update:**
- Document boundary violation concept
- Explain allowed edge types
- **NEW:** Document constraint edge handling (v7)

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [to be filled]
- What could be better:
  - [to be filled]
- Discoveries:
  - [to be filled]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands: `pytest tests/unit/test_boundary_violations.py -v`
- Look for: Violations detected correctly, constraint edges allowed

---

### Work Unit 12-15: Decompose Commands

[Content from S005 WU12-WU15, carried over with minimal changes]

---

## Slice 5: Nested Subsystems Implementation

**Context:** This slice implements the nested subsystems feature defined in S006_SCOPE_nested_subsystems.md. It integrates with JIG v7's OSTCX model, where constraints act as predicates over the hierarchical OSTC Intent Graph.

### Work Unit 20: Phase 1 - Data Model & Loading

**Goal:** Implement nested subsystem data structures and loading from YAML.

**Planned Effort:** 5-7 days (40-56 hours over calendar week)

**Acceptance Criteria:**
- Subsystem dataclass supports nesting (subsystems field)
- Graph.load_from_dir() correctly parses nested subsystems from YAML
- Validation detects cycles in subsystem hierarchy
- Validation ensures nodes reference valid subsystem paths
- Validation prevents nodes in parent subsystems with children
- Unit tests cover 3-level nesting scenarios
- Backward compatibility: flat subsystems still load correctly

**Implementation Notes:**

**Files to Modify:**
1. `src/jig/core/graph.py` - Update Subsystem dataclass:
   ```python
   # @jig C-NESTED-001 implements:S-NESTED-001 subsystem:core interface:internal
   @dataclass
   class Subsystem:
       """Represents a subsystem grouping of nodes.
       
       Attributes:
           name: Subsystem name (local, not fully-qualified)
           nodes: List of node IDs in this subsystem (leaf only)
           subsystems: Dictionary of child subsystems (optional)
           description: Human-readable description (optional)
           parent_path: Fully-qualified parent path (e.g., "crdt")
       """
       name: str
       nodes: list[str] = field(default_factory=list)
       subsystems: dict[str, "Subsystem"] = field(default_factory=dict)
       description: str = ""
       parent_path: str = ""
       
       @property
       def full_path(self) -> str:
           """Return fully-qualified subsystem path."""
           if self.parent_path:
               return f"{self.parent_path}.{self.name}"
           return self.name
       
       def is_leaf(self) -> bool:
           """Return True if this subsystem has no children."""
           return len(self.subsystems) == 0
       
       def get_all_nodes(self, recursive: bool = False) -> list[str]:
           """Return all nodes in this subsystem.
           
           Args:
               recursive: If True, include nodes from child subsystems
           """
           if not recursive:
               return self.nodes
           
           all_nodes = list(self.nodes)
           for child in self.subsystems.values():
               all_nodes.extend(child.get_all_nodes(recursive=True))
           return all_nodes
       
       def find_subsystem(self, path: str) -> "Subsystem | None":
           """Find subsystem by path (e.g., 'ser' or 'crdt.ser')."""
           parts = path.split(".", 1)
           if parts[0] != self.name:
               return None
           
           if len(parts) == 1:
               return self
           
           # Recurse into children
           child_path = parts[1]
           for child in self.subsystems.values():
               result = child.find_subsystem(child_path)
               if result:
                   return result
           
           return None
   ```

2. `src/jig/core/graph.py` - Add Graph methods for hierarchical subsystems:
   ```python
   # @jig C-NESTED-002 implements:S-NESTED-002 subsystem:core interface:internal
   class Graph:
       def get_subsystem_by_path(self, path: str) -> Subsystem | None:
           """Get subsystem by fully-qualified path.
           
           Args:
               path: Subsystem path (e.g., 'core', 'crdt.ser')
           
           Returns:
               Subsystem object or None if not found
           """
           parts = path.split(".")
           root_name = parts[0]
           
           if root_name not in self.subsystems:
               return None
           
           subsystem = self.subsystems[root_name]
           
           # Navigate down the hierarchy
           for part in parts[1:]:
               if part not in subsystem.subsystems:
                   return None
               subsystem = subsystem.subsystems[part]
           
           return subsystem
       
       def get_all_subsystem_paths(self, flat: bool = False) -> list[str]:
           """Return all subsystem paths.
           
           Args:
               flat: If True, return only leaf subsystems
           
           Returns:
               List of fully-qualified subsystem paths
           """
           paths = []
           
           def collect_paths(subsystem: Subsystem, include_parents: bool):
               if include_parents or subsystem.is_leaf():
                   paths.append(subsystem.full_path)
               
               for child in subsystem.subsystems.values():
                   collect_paths(child, include_parents)
           
           for root in self.subsystems.values():
               collect_paths(root, not flat)
           
           return sorted(paths)
       
       def get_constraints_for_subsystem(self, path: str, recursive: bool = True) -> list[str]:
           """Return all constraints that apply to a subsystem (v7).
           
           Args:
               path: Subsystem path (e.g., 'core', 'crdt.ser')
               recursive: If True, include constraints from child subsystems
           
           Returns:
               List of constraint IDs (e.g., ['X-PERF-001'])
           """
           subsystem = self.get_subsystem_by_path(path)
           if not subsystem:
               return []
           
           constraints = set()
           
           # Get nodes in this subsystem
           nodes = subsystem.get_all_nodes(recursive=recursive)
           
           # Collect constraints from all nodes
           for node_id in nodes:
               if node_id in self.nodes:
                   node = self.nodes[node_id]
                   if hasattr(node, 'constraints'):
                       constraints.update(node.constraints)
           
           return sorted(list(constraints))
   ```

3. `src/jig/core/validator.py` - Add validation for nested structures:
   ```python
   # @jig C-NESTED-003 implements:S-NESTED-005 subsystem:core interface:internal
   def validate_nested_subsystems(graph: Graph) -> list[str]:
       """Validate nested subsystem structure.
       
       Checks:
       - No cycles in subsystem hierarchy
       - Parent subsystems with children have no direct nodes
       - Node subsystem paths are valid
       """
       errors = []
       
       # Check for cycles (DFS)
       def check_cycles(subsystem: Subsystem, visited: set) -> bool:
           if subsystem.name in visited:
               return True  # Cycle detected
           visited.add(subsystem.name)
           for child in subsystem.subsystems.values():
               if check_cycles(child, visited.copy()):
                   return True
           return False
       
       for subsystem in graph.subsystems.values():
           if check_cycles(subsystem, set()):
               errors.append(f"Cycle detected in subsystem hierarchy at {subsystem.name}")
       
       # Check parent subsystems don't have direct nodes
       def check_parent_nodes(subsystem: Subsystem):
           if subsystem.subsystems and subsystem.nodes:
               errors.append(
                   f"Parent subsystem '{subsystem.full_path}' has both children and direct nodes"
               )
           for child in subsystem.subsystems.values():
               check_parent_nodes(child)
       
       for subsystem in graph.subsystems.values():
           check_parent_nodes(subsystem)
       
       # Check node subsystem paths are valid
       for node_id, node in graph.nodes.items():
           if node.subsystem:
               if not graph.get_subsystem_by_path(node.subsystem):
                   errors.append(
                       f"Node {node_id} references invalid subsystem path '{node.subsystem}'"
                   )
       
       return errors
   ```

**Test Plan:**
- Unit tests in `tests/unit/test_nested_subsystems.py`:
  ```python
  # @jig T-NESTED-001 verifies:S-NESTED-001 subsystem:core
  def test_nested_subsystem_loading():
      """Verify Graph loads nested subsystems from YAML."""

  # @jig T-NESTED-002 verifies:S-NESTED-002 subsystem:core
  def test_subsystem_path_resolution():
      """Verify get_subsystem_by_path() navigates hierarchy."""

  # @jig T-NESTED-003 verifies:S-NESTED-001 subsystem:core
  def test_recursive_node_collection():
      """Verify get_all_nodes(recursive=True) includes children."""

  # @jig T-NESTED-004 verifies:S-NESTED-005 subsystem:core
  def test_cycle_detection():
      """Verify validation detects cycles in subsystem hierarchy."""

  # @jig T-NESTED-005 verifies:S-NESTED-005 subsystem:core
  def test_parent_with_nodes_validation():
      """Verify validation prevents nodes in parent subsystems."""
      
  # @jig T-NESTED-006 verifies:S-NESTED-001 subsystem:core
  def test_backward_compatibility_flat():
      """Verify flat subsystems still load correctly."""
  ```

**Docs to Update:**
- Update docstrings for all new methods
- Document dot notation for subsystem paths
- Add examples of nested YAML structure

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [to be filled]
- What could be better:
  - [to be filled]
- Discoveries:
  - [to be filled]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands: `pytest tests/unit/test_nested_subsystems.py -v`
- Look for: All tests pass, backward compatibility maintained

---

### Work Unit 21: Phase 2 - Query & Navigation

**Goal:** Update graph query methods and status command for hierarchical subsystems.

**Planned Effort:** 5-7 days

**Acceptance Criteria:**
- `Graph.get_subsystem_by_path("crdt.ser")` returns correct subsystem
- `jigy status` displays hierarchical tree with proper indentation
- `jigy status --flat` displays flattened view (backward compatible)
- `jigy graph list --subsystem crdt` lists all nodes recursively
- `jigy graph list --subsystem crdt.ser` lists only leaf nodes
- Constraint information displayed in status output (per subsystem)
- Subsystem queries work with constraint scope selectors (v7)
- Performance: queries complete in <200ms for 100 subsystems
- Integration tests verify tree formatting

**Implementation Notes:**

1. `src/jig/cli/status.py` - Add hierarchical tree formatting:
   ```python
   # @jig C-NESTED-004 implements:S-NESTED-003 subsystem:core interface:public
   def format_subsystem_tree(subsystem: Subsystem, graph: Graph, indent: str = "") -> list[str]:
       """Format subsystem hierarchy as tree.
       
       Args:
           subsystem: Root subsystem to format
           graph: Graph for constraint lookup
           indent: Current indentation level
       
       Returns:
           List of formatted lines
       """
       lines = []
       node_count = len(subsystem.get_all_nodes(recursive=True))
       lines.append(f"{indent}{subsystem.name} ({node_count} nodes)")
       
       # Show constraints for this subsystem
       constraints = graph.get_constraints_for_subsystem(subsystem.full_path)
       if constraints:
           lines.append(f"{indent}  └── Constraints: {constraints}")
       
       # Show child subsystems
       children = list(subsystem.subsystems.values())
       for i, child in enumerate(children):
           is_last = (i == len(children) - 1)
           connector = "└── " if is_last else "├── "
           extension = "    " if is_last else "│   "
           
           child_lines = format_subsystem_tree(child, graph, indent + extension)
           child_lines[0] = indent + connector + child_lines[0].lstrip()
           lines.extend(child_lines)
       
       return lines
   ```

2. `src/jig/cli/graph.py` - Update list command for recursive queries:
   ```python
   # @jig C-NESTED-005 implements:S-NESTED-002 subsystem:core interface:public
   @graph.command()
   @click.option('--type', 'node_type', help='Filter by node type')
   @click.option('--subsystem', help='Filter by subsystem (use dot notation for nested)')
   @click.option('--recursive', is_flag=True, help='Include child subsystems')
   @click.option('--format', type=click.Choice(['table', 'yaml']), default='table')
   def list(node_type: str | None, subsystem: str | None, recursive: bool, format: str):
       """List nodes with optional filters."""
       config = load_config()
       g = Graph.load_from_dir(config.intent_dir)
       
       nodes = list(g.nodes.values())
       
       if node_type:
           nodes = g.filter_by_type(node_type)
       
       if subsystem:
           subsys = g.get_subsystem_by_path(subsystem)
           if not subsys:
               click.echo(click.style(f"Error: Subsystem {subsystem} not found", fg="red"))
               sys.exit(1)
           
           # Get nodes from subsystem
           node_ids = subsys.get_all_nodes(recursive=recursive)
           nodes = [g.nodes[nid] for nid in node_ids if nid in g.nodes]
       
       # Output formatting (same as before)
       if format == 'yaml':
           import yaml
           data = [{'id': n.id, 'type': n.type, 'title': n.title, 'subsystem': n.subsystem} for n in nodes]
           click.echo(yaml.dump(data))
       else:
           click.echo(f"{'ID':<20} {'Type':<15} {'Subsystem':<20} {'Title'}")
           click.echo("-" * 90)
           for node in sorted(nodes, key=lambda n: n.id):
               subsys = node.subsystem or "(none)"
               title = node.title[:43] if len(node.title) > 43 else node.title
               click.echo(f"{node.id:<20} {node.type:<15} {subsys:<20} {title}")
   ```

**Test Plan:**
- Integration tests in `tests/integration/test_nested_status.py`:
  ```python
  # @jig T-NESTED-007 verifies:S-NESTED-003 subsystem:core
  def test_status_hierarchical_view(tmp_path):
      """Verify status displays tree view for nested subsystems."""

  # @jig T-NESTED-008 verifies:S-NESTED-003 subsystem:core
  def test_status_flat_view(tmp_path):
      """Verify --flat option shows flattened view."""

  # @jig T-NESTED-009 verifies:S-NESTED-002 subsystem:core
  def test_graph_list_recursive(tmp_path):
      """Verify list --subsystem includes child nodes."""

  # @jig T-NESTED-010 verifies:S-NESTED-006 subsystem:core
  def test_constraint_scope_nested_subsystems(tmp_path):
      """Verify constraint scopes work with nested subsystem paths (v7)."""
  ```

**Docs to Update:**
- Update status command help text
- Document --flat and --recursive options
- Add examples of nested subsystem queries

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [to be filled]
- What could be better:
  - [to be filled]
- Discoveries:
  - [to be filled]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands:
  ```bash
  jigy status
  jigy status --flat
  jigy graph list --subsystem crdt --recursive
  jigy graph list --subsystem crdt.ser
  ```
- Look for: Tree formatting, recursive queries work

---

### Work Unit 22: Phase 3 - Decomposability with Hierarchy

**Goal:** Update decomposability metrics for hierarchical subsystems.

**Planned Effort:** 5-7 days

**Acceptance Criteria:**
- Modularity calculation works for nested subsystems
- Coupling ratio aggregates child subsystem metrics
- Boundary violations respect hierarchy (edges within parent OK)
- Coupling ratio excludes constraint relationships (v7)
- `jigy decompose metrics --subsystem crdt` analyzes subtree
- `jigy decompose report` includes hierarchical breakdown and constraint compliance
- Constraint compliance metrics shown per subsystem
- Performance: metrics calculation <5s for 100 subsystems
- Unit tests verify hierarchical metric calculations

**Implementation Notes:**

1. `src/jig/decompose/metrics.py` - Update for hierarchical metrics:
   ```python
   # @jig C-NESTED-006 implements:S-NESTED-004 subsystem:decompose interface:internal
   def calculate_hierarchical_coupling(subsystem: Subsystem, graph: Graph) -> SubsystemMetrics:
       """Calculate coupling ratio for hierarchical subsystem.
       
       For parent subsystems:
       - Internal edges: edges between any nodes within the subtree (including cross-child)
       - External edges: edges to nodes outside the subtree
       
       This enables refactoring into hierarchies without degrading metrics.
       """
       # Get all nodes in this subsystem tree
       all_nodes = set(subsystem.get_all_nodes(recursive=True))
       
       internal = 0
       external = 0
       
       for edge in graph.edges:
           # Skip constraint edges (v7)
           if edge.type == 'satisfies':
               continue
           
           from_in = edge.from_node in all_nodes
           to_in = edge.to_node in all_nodes
           
           if from_in and to_in:
               internal += 1
           elif from_in or to_in:
               external += 1
       
       ratio = internal / external if external > 0 else float('inf')
       
       return SubsystemMetrics(
           name=subsystem.full_path,
           node_count=len(all_nodes),
           internal_edges=internal,
           external_edges=external,
           coupling_ratio=ratio
       )
   
   def calculate_all_metrics_hierarchical(graph: Graph, subsystem_path: str | None = None) -> DecomposabilityMetrics:
       """Calculate metrics for entire graph or specific subsystem subtree.
       
       Args:
           graph: The graph to analyze
           subsystem_path: Optional path to analyze just that subtree
       """
       if subsystem_path:
           subsystem = graph.get_subsystem_by_path(subsystem_path)
           if not subsystem:
               raise ValueError(f"Subsystem {subsystem_path} not found")
           
           # Calculate metrics for this subtree only
           # ... implementation
       else:
           # Calculate metrics for entire graph
           # ... implementation (similar to calculate_all_metrics)
   ```

2. `src/jig/cli/decompose.py` - Add --subsystem option:
   ```python
   # @jig C-NESTED-007 implements:S-NESTED-004 subsystem:decompose interface:public
   @decompose.command()
   @click.option('--subsystem', help='Analyze specific subsystem subtree')
   @click.option('--format', type=click.Choice(['table', 'yaml']), default='table')
   def metrics(subsystem: str | None, format: str):
       """Calculate decomposability health scores."""
       config = load_config()
       graph = Graph.load_from_dir(config.intent_dir)
       
       if subsystem:
           click.echo(click.style(f"Analyzing subsystem '{subsystem}'...", bold=True))
       else:
           click.echo(click.style("Calculating metrics...", bold=True))
       
       metrics = calculate_all_metrics_hierarchical(graph, subsystem)
       
       # Format output with hierarchical structure
       # ... (include constraint compliance per subsystem)
   ```

**Test Plan:**
- Unit tests in `tests/unit/test_hierarchical_metrics.py`:
  ```python
  # @jig T-NESTED-011 verifies:S-NESTED-004 subsystem:decompose
  def test_hierarchical_modularity():
      """Verify modularity calculation for nested subsystems."""

  # @jig T-NESTED-012 verifies:S-NESTED-004 subsystem:decompose
  def test_hierarchical_coupling_ratio():
      """Verify coupling ratio aggregates child metrics."""
      
  # @jig T-NESTED-013 verifies:S-NESTED-004 subsystem:decompose
  def test_constraint_exclusion_from_coupling():
      """Verify constraint relationships not counted in coupling metrics (v7)."""
      
  # @jig T-NESTED-014 verifies:S-NESTED-004 subsystem:decompose
  def test_cross_child_edges_internal_to_parent():
      """Verify edges between children counted as internal to parent."""
  ```

**Docs to Update:**
- Document hierarchical coupling calculation
- Explain how parent metrics aggregate children
- Document constraint exclusion from metrics (v7)

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [to be filled]
- What could be better:
  - [to be filled]
- Discoveries:
  - [to be filled]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands:
  ```bash
  jigy decompose metrics
  jigy decompose metrics --subsystem crdt
  ```
- Look for: Hierarchical metrics, constraint compliance shown

---

### Work Unit 23: Phase 4 - Documentation & Migration

**Goal:** Document nested subsystems and provide migration guide.

**Planned Effort:** 5-7 days

**Acceptance Criteria:**
- User guide explains nested subsystem concepts
- Migration guide provides step-by-step instructions
- Tutorial includes 3-level nesting example
- Architecture docs explain design decisions
- All examples tested and working
- README updated with nested subsystem example

**Implementation Notes:**

1. Create `docs/user-guide/NESTED_SUBSYSTEMS.md`:
   - Overview of nested subsystems
   - When to use nesting vs flat
   - Dot notation for paths
   - Examples with YAML and CLI commands
   - Best practices (max depth 3-4)

2. Create `docs/user-guide/MIGRATION_NESTED.md`:
   - Step-by-step migration from flat to nested
   - Search/replace patterns for frontmatter
   - Validation checklist
   - Example migration (auth + user → identity)

3. Update `docs/architecture/GRAPH_SUBSYSTEM.md`:
   - Nested subsystem data structures
   - Path resolution algorithm
   - Hierarchical metrics calculation
   - Design decision: nodes only in leaf subsystems
   - Integration with constraints (v7)

4. Create `docs/tutorials/NESTED_SUBSYSTEMS_TUTORIAL.md`:
   - Tutorial with sample project
   - Create flat structure first
   - Refactor to nested structure
   - Show metrics improvement

5. Update `README.md`:
   - Add nested subsystem example
   - Update status output example
   - Link to nested subsystems guide

**Test Plan:**
- Manual: Follow all guides step-by-step
- Verify all code examples work
- Test migration guide on sample project

**Docs to Update:**
- All listed above

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [to be filled]
- What could be better:
  - [to be filled]
- Discoveries:
  - [to be filled]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands: Follow migration guide on test project
- Look for: Clear instructions, working examples

---

## Slice 4: Documentation & Release (Updated)

### Work Unit 16-18: Documentation Work Units

[Content from S005 WU16-WU18, updated to include nested subsystems in documentation]

### Work Unit 19: Dogfooding & v0.3.0 Release

**Goal:** Run all Phase 1 commands on JIG's own graph with nested subsystems, tag v0.3.0 release.

**Planned Effort:** 60-90m

**Acceptance Criteria:**
- JIG's own subsystems refactored to nested structure (if appropriate)
- Run `jigy status` on JIG's graph - hierarchical tree displayed
- Run `jigy graph list --subsystem core --recursive` - works correctly
- Run `jigy decompose metrics` on JIG - modularity >0.7, constraint compliance shown
- Run `jigy decompose report` on JIG - hierarchical breakdown included
- All Phase 1 OSTC nodes validated (including nested subsystem nodes)
- Git tag: v0.3.0-phase-1-complete
- Release notes written

**Implementation Notes:**
- Dogfooding checklist:
  ```bash
  # Status with hierarchical tree
  jigy status
  jigy status --flat  # Backward compatibility
  jigy status --verbose
  
  # Graph queries with nested subsystems
  jigy graph show O-NESTED-001
  jigy graph list --subsystem core
  jigy graph list --subsystem core --recursive
  
  # Decompose with hierarchical metrics
  jigy decompose metrics
  jigy decompose metrics --subsystem core
  jigy decompose validate
  jigy decompose report --output docs/metrics/jig-v0.3.0-decomposability.md
  
  # Validation
  jigy validate --check-all
  ```

- Create release notes:
  - Phase 1 complete: Intent Graph + Decomposability + Nested Subsystems
  - New commands: status, graph (6 subcommands), decompose (5 subcommands)
  - Features: hierarchical subsystems, coupling metrics, constraint integration
  - Performance: all targets met (<100ms queries, <5s decompose)
  - Breaking changes: none (backward compatible)

- Tag release:
  ```bash
  git tag -a v0.3.0-phase-1-complete -m "Phase 1 Complete: Intent Graph, Decomposability, Nested Subsystems"
  ```

**Test Plan:**
- Manual validation of all dogfooding commands
- Verify JIG's modularity score and constraint compliance
- Check nested subsystem structure (if applied)

**Docs to Update:**
- CHANGELOG.md - Add v0.3.0 entry
- README.md - Update version, features, examples
- Include nested subsystem examples in README

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [to be filled]
- What could be better:
  - [to be filled]
- Discoveries:
  - [to be filled]

**Links:**
- Commit: [to be filled]
- Tag: v0.3.0-phase-1-complete

**Human Validation:**
- Commands: All dogfooding commands above
- Look for: 
  - JIG's graph is healthy
  - Modularity >0.7
  - Nested subsystems work correctly
  - All constraint compliance shown
  - Release tagged

---

## Completion Summary

### Summary
- Scope delivered: [to be filled]
- Key decisions: [to be filled]
- Deltas from SCOPE: [to be filled]

### Metrics
- Units: 23 total (WU9-WU23, continuing from S005 WU8)
- Rework rate: [to be filled]
- Flaky test events: [to be filled]
- Test coverage: [target: >80%]
- Docs lag: [to be filled]
- Markers captured: [to be filled]

### Reflection Roll-up
- Repeatable wins:
  - [to be filled from WU reflects and S005 patterns]
- Systemic frictions (top 3):
  - [to be filled]
- Process changes adopted:
  - [to be filled]
- Open questions for next plan:
  - [to be filled]

### Harvest Preparation (JIG)

**Markers Summary:**
- Discoveries: [count from all WU reflects]
- Decisions: [count]
- Learned patterns: [count]

**Recommended OSTCX Nodes (from DISCOVERIES only):**
- [to be filled by AIA based on #DISCOVERY markers]

**Subsystems Touched:**
- core (graph data structures, queries, nested subsystems)
- decompose (metrics, detection, analysis, hierarchical metrics)
- cli (status, graph, decompose commands)
- docs (user guides, architecture, tutorials)

**Constraints Considered (v7):**
- Constraint relationships excluded from coupling metrics
- Constraint scoping works with nested subsystem paths
- Status shows constraint compliance per subsystem

**Next Step:** Phase 2 - Delta Workflows (Slice 6-9)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-20
**Status:** Draft (Ready to execute WU9)
**Supersedes:** S005_PLAN_phase_1_intent_graph.md (Slices 0-2 complete)
**References:**
- S005_PLAN_phase_1_intent_graph.md (completed work)
- S006_SCOPE_nested_subsystems.md (nested subsystems design)
- JIG-Concept-v7.md (OSTCX model, constraints as predicates)


