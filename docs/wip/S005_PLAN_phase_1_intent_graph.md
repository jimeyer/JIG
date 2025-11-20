---
delta_type: plan
branch: phase-1-intent-graph
---

# PLAN: Phase 1 - Intent Graph Subsystem

- **SCOPE:** docs/wip/JIG_DEVELOPMENT_STRATEGY_V2.md (Part 3: Phase 1 - Intent Graph)
- **Start:** 2025-11-19
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** core (graph, decompose)

## Known Intent (Created Before Coding)

**Outcomes Created:**
- O-GRAPH-001: "Graph queries complete in <100ms for 100 nodes" (jig/outcomes/O-GRAPH-001.md)
- O-GRAPH-002: "Developers navigate Intent Graph via CLI efficiently" (jig/outcomes/O-GRAPH-002.md)
- O-DECOMP-001: "JIG measures and validates subsystem boundaries" (jig/outcomes/O-DECOMP-001.md)
- O-DECOMP-002: "Modularity score >0.7 for well-decomposed systems" (jig/outcomes/O-DECOMP-002.md)

**Specifications Created:**
- S-GRAPH-001: "Status displays node counts, orphans, subsystems in <100ms" (jig/specifications/S-GRAPH-001.md)
- S-GRAPH-002: "Graph data structure supports load, query, traversal" (jig/specifications/S-GRAPH-002.md)
- S-GRAPH-003: "Graph commands: show, deps, impact, path, list" (jig/specifications/S-GRAPH-003.md)
- S-DECOMP-001: "Modularity calculation uses Newman algorithm" (jig/specifications/S-DECOMP-001.md)
- S-DECOMP-002: "Community detection uses Louvain method (NetworkX)" (jig/specifications/S-DECOMP-002.md)
- S-DECOMP-003: "Coupling ratio = internal edges / external edges" (jig/specifications/S-DECOMP-003.md)
- S-DECOMP-004: "Boundary violation detection for cross-subsystem edges" (jig/specifications/S-DECOMP-004.md)

**Rationale:** These constraints are explicitly defined in JIG_DEVELOPMENT_STRATEGY_V2.md Part 3. Creating them upfront enables O→S→TDD flow for all 4 slices in Phase 1.

## Work Unit Checklist

### Slice 0 (Complete)
- [x] WU0: Create known Intent nodes (O/S) — done ☑

### Slice 1: Status & Health Monitoring
- [x] WU1: Graph data structure implementation — tests ☑ / docs ☑ / reflect ☑
- [x] WU2: Status command implementation — tests ☑ / docs ☑ / reflect ☐
- [ ] WU3: Status output formatting & CLI — tests ☐ / docs ☐ / reflect ☐

### Slice 2: Graph Relationships & Queries
- [ ] WU4: Graph traversal methods (deps, dependents, path) — tests ☐ / docs ☐ / reflect ☐
- [ ] WU5: Graph query methods (filter by type, subsystem) — tests ☐ / docs ☐ / reflect ☐
- [ ] WU6: Graph show command — tests ☐ / docs ☐ / reflect ☐
- [ ] WU7: Graph deps/impact commands — tests ☐ / docs ☐ / reflect ☐
- [ ] WU8: Graph path/list commands — tests ☐ / docs ☐ / reflect ☐

### Slice 3: Decomposability Analysis
- [ ] WU9: Metrics calculation (modularity, coupling) — tests ☐ / docs ☐ / reflect ☐
- [ ] WU10: Community detection (Louvain) — tests ☐ / docs ☐ / reflect ☐
- [ ] WU11: Boundary violation detection — tests ☐ / docs ☐ / reflect ☐
- [ ] WU12: Decompose detect command — tests ☐ / docs ☐ / reflect ☐
- [ ] WU13: Decompose metrics command — tests ☐ / docs ☐ / reflect ☐
- [ ] WU14: Decompose validate command — tests ☐ / docs ☐ / reflect ☐
- [ ] WU15: Decompose report command — tests ☐ / docs ☐ / reflect ☐

### Slice 4: Documentation & Release
- [ ] WU16: User guide for graph commands — tests ☐ / docs ☐ / reflect ☐
- [ ] WU17: Architecture documentation — tests ☐ / docs ☐ / reflect ☐
- [ ] WU18: Tutorial & quality gates — tests ☐ / docs ☐ / reflect ☐
- [ ] WU19: Dogfooding & v0.2.0 release — tests ☐ / docs ☐ / reflect ☐

---

## Work Units

### Work Unit 0: Create Known Intent

**Goal:** Capture all known Outcomes and Specifications from SCOPE (JIG_DEVELOPMENT_STRATEGY_V2.md Part 3) as Intent nodes before coding.

**Planned Effort:** 60-90m

**Acceptance Criteria:**
- All 4 Outcome nodes created in jig/outcomes/ with proper YAML frontmatter
- All 7 Specification nodes created in jig/specifications/ with proper YAML frontmatter
- Each O node has clear value proposition and success metrics
- Each S node has rationale, requirements, and links to parent O nodes
- `jig validate` passes
- Graph-index.yaml updated with new nodes and relationships

**Implementation Notes:**
- Create directory structure if needed
- Follow OSTC node format from existing nodes (O-JIG-001, S-JIG-001, etc.)
- Use ID pattern: O-GRAPH-NNN, S-GRAPH-NNN, O-DECOMP-NNN, S-DECOMP-NNN
- Link S nodes to O nodes via "implements" relationship
- Mark subsystem as "core" for graph nodes, "decompose" for decomposability nodes

**Created Nodes:**
- O-GRAPH-001.md - Performance outcome (<100ms queries)
- O-GRAPH-002.md - Developer experience outcome (efficient navigation)
- O-DECOMP-001.md - Measurement outcome (subsystem boundaries)
- O-DECOMP-002.md - Quality outcome (modularity >0.7)
- S-GRAPH-001.md - Status command spec
- S-GRAPH-002.md - Graph data structure spec
- S-GRAPH-003.md - Graph query commands spec
- S-DECOMP-001.md - Modularity calculation spec (Newman)
- S-DECOMP-002.md - Community detection spec (Louvain)
- S-DECOMP-003.md - Coupling ratio spec
- S-DECOMP-004.md - Boundary violation spec

**Test Plan:**
- Manual validation: Read each file, verify format
- Check YAML frontmatter parses correctly
- Verify all required fields present (id, type, title)
- Confirm markdown content is clear and actionable
- Run `jigy validate --check-all`

**Docs to Update:**
- jig/graph-index.yaml - Add 11 new nodes and implements relationships
- jig/subsystems.yaml - Add "decompose" subsystem if needed

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [clarity] SCOPE (V2 strategy) clearly defined these constraints
  - [process] Building on Slice 0 template speeds up Intent creation
- What could be better:
  - [scope] Some performance targets (e.g., <5s for decompose) may need adjustment
- Discoveries:
  - [to be filled after execution]

**Links:**
- Commit: [to be filled]

**Human Validation:**
- Commands: `ls -la jig/outcomes/ jig/specifications/`, `jigy validate --check-all`
- Look for: 11 new files created, proper YAML frontmatter, validation passes

---

## Slice 1: Status & Health Monitoring

### Work Unit 1: Graph Data Structure Implementation

**Goal:** Implement core Graph class with loading, node counting, and subsystem grouping.

**Planned Effort:** 90-120m

**Acceptance Criteria:**
- `src/jig/core/graph.py` implemented with Graph dataclass
- Graph.load_from_dir() loads all OSTC nodes and graph-index.yaml
- Graph.get_node_counts_by_type() returns counts dict
- Graph.get_nodes_by_subsystem() returns subsystem grouping
- Graph.find_orphaned_nodes() identifies nodes without edges
- Type hints throughout (mypy passes)
- Unit tests >80% coverage

**Implementation Notes:**
- Files to create:
  - `src/jig/core/graph.py`:
    ```python
    # @jig C-GRAPH-001 implements:S-GRAPH-002 subsystem:core interface:internal
    from dataclasses import dataclass
    from pathlib import Path
    from jig.core.parser import OSTCNode

    @dataclass
    class Edge:
        from_node: str
        to_node: str
        type: str  # implements, verifies, depends_on

    @dataclass
    class Subsystem:
        name: str
        nodes: list[str]

    @dataclass
    class Graph:
        nodes: dict[str, OSTCNode]
        edges: list[Edge]
        subsystems: dict[str, Subsystem]

        @staticmethod
        def load_from_dir(intent_dir: Path) -> "Graph":
            """Load entire graph from jig/ directory."""
            # Load all .md files from outcomes/, specifications/, constraints/, tests/
            # Load graph-index.yaml for edges and subsystems
            # Parse each file with OSTCNode parser
            # Build Graph object

        def get_node_counts_by_type(self) -> dict[str, int]:
            """Return counts: {outcome: 5, specification: 12, ...}"""

        def get_nodes_by_subsystem(self) -> dict[str, list[str]]:
            """Return nodes grouped by subsystem."""

        def find_orphaned_nodes(self) -> list[str]:
            """Find nodes not connected to any edges."""
            # Node is orphaned if it appears in no edges (as from or to)

        def to_networkx(self) -> "nx.Graph":
            """Convert to NetworkX graph for algorithms."""
            # Used later for decomposability analysis
    ```
- Reuse existing parser from Slice 0 (WU3)
- Load graph-index.yaml with yaml_utils from Slice 0 (WU2)
- Handle missing files gracefully (e.g., no tests/ directory yet)

**Test Plan:**
- Unit tests in `tests/unit/test_graph.py`:
  ```python
  # @jig T-GRAPH-001 verifies:S-GRAPH-002 subsystem:core
  def test_load_from_dir_success(tmp_path):
      """Verify Graph loads from jig/ directory with valid nodes."""
      # Create sample nodes and graph-index.yaml
      # Load and assert correct counts

  # @jig T-GRAPH-002 verifies:S-GRAPH-002 subsystem:core
  def test_get_node_counts_by_type():
      """Verify node counting by type."""

  # @jig T-GRAPH-003 verifies:S-GRAPH-002 subsystem:core
  def test_find_orphaned_nodes():
      """Verify orphaned node detection."""
      # Create graph with some nodes not in edges
      # Assert orphaned list is correct
  ```
- Coverage target: >80%

**Docs to Update:**
- Add docstrings to all Graph methods
- Document Edge and Subsystem dataclasses

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [clarity] Graph dataclass design mapped cleanly to graph-index.yaml structure
  - [reuse] Leveraging existing parser and yaml_utils from Slice 0 was seamless
  - [coverage] 94.94% test coverage achieved with comprehensive unit tests
- What could be better:
  - [tooling] pytest-cov has issues with YAML frontmatter parsing; used coverage.py directly instead
- Discoveries:
  - [test] NetworkX integration for to_networkx() will enable community detection algorithms

**Links:**
- Commit: a02f25f8bb8e55b4e35c7f1b3b9c3c24b8e5c8e0

**Human Validation:**
- Commands: `pytest tests/unit/test_graph.py -v`, `mypy src/jig/core/graph.py`
- Look for: All tests pass, coverage >80%, type checking clean

---

### Work Unit 2: Status Command Implementation

**Goal:** Implement core status logic to analyze graph health.

**Planned Effort:** 75-90m

**Acceptance Criteria:**
- `src/jig/cli/status.py` extended with graph analysis
- Loads Graph from current directory's jig/
- Calculates node counts, subsystem breakdown, orphaned nodes
- Returns structured status data (not formatting yet - WU3)
- Handles missing jig/ directory gracefully
- Performance: completes in <100ms for JIG's own graph (15 nodes)
- Unit tests >80% coverage

**Implementation Notes:**
- Files to update:
  - `src/jig/cli/status.py` (already exists from Slice 0):
    ```python
    # @jig C-STATUS-001 implements:S-GRAPH-001 subsystem:core interface:public
    from jig.core.graph import Graph
    from jig.core.config import load_config
    from dataclasses import dataclass

    @dataclass
    class StatusData:
        total_nodes: int
        node_counts: dict[str, int]
        subsystems: dict[str, list[str]]
        orphaned_nodes: list[str]
        validation_errors: list[str]

    def calculate_status(intent_dir: Path) -> StatusData:
        """Calculate graph health metrics."""
        graph = Graph.load_from_dir(intent_dir)
        # Calculate all metrics
        return StatusData(...)

    @click.command()
    @click.option('--verbose', is_flag=True, help='Show detailed statistics')
    def status(verbose: bool):
        """Show JIG graph status and health."""
        config = load_config()
        status_data = calculate_status(config.intent_dir)
        # Format and print (WU3 handles formatting)
    ```
- Error handling for:
  - Directory not initialized (`jig/` doesn't exist) → exit code 3
  - Parse errors in OSTC nodes → include in status output
  - Missing graph-index.yaml → warning, best-effort mode

**Test Plan:**
- Unit tests in `tests/unit/test_status_logic.py`:
  ```python
  # @jig T-STATUS-001 verifies:S-GRAPH-001 subsystem:core
  def test_calculate_status_with_valid_graph(tmp_path):
      """Verify status calculation with valid graph."""

  # @jig T-STATUS-002 verifies:S-GRAPH-001 subsystem:core
  def test_calculate_status_identifies_orphans(tmp_path):
      """Verify status identifies orphaned nodes."""

  # @jig T-STATUS-003 verifies:S-GRAPH-001 subsystem:core
  def test_status_handles_missing_directory():
      """Verify graceful handling when jig/ doesn't exist."""
  ```
- Integration test in `tests/integration/test_status_command.py`:
  ```python
  # @jig T-STATUS-004 verifies:S-GRAPH-001 subsystem:core
  def test_status_performance(tmp_path):
      """Verify status completes in <100ms for 100 nodes."""
      # Create 100 node files
      # Time execution
      # Assert <100ms
  ```

**Docs to Update:**
- Add docstring to calculate_status()
- Document StatusData dataclass fields

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [architecture] StatusData dataclass cleanly separates logic from presentation
  - [testing] Click.testing.CliRunner enabled CLI integration tests with mocking
  - [coverage] 96.83% test coverage achieved (15 tests)
- What could be better:
  - [test-helpers] Duplicated create_test_node helper across test files (could extract to conftest.py)
- Discoveries:
  - [performance] Status calculation on 100 nodes completes in ~25ms, well under 100ms target

**Links:**
- Commit: 4204d0e7b9473650e7cb6095d1df83bbdca3ba63

**Human Validation:**
- Commands: `pytest tests/unit/test_status_logic.py -v`, `jigy status`
- Look for: Tests pass, status runs without errors

---

### Work Unit 3: Status Output Formatting & CLI

**Goal:** Implement clear, colorized status output with actionable suggestions.

**Planned Effort:** 60-75m

**Acceptance Criteria:**
- Status command prints formatted output with colors
- Shows: total nodes, counts by type, subsystem breakdown, orphaned nodes
- Suggests next actions (e.g., "5 nodes need subsystem assignment")
- `--verbose` flag shows additional details (node lists)
- Exit codes: 0 (success), 3 (not initialized)
- Output matches example from SCOPE
- Integration tests verify output format

**Implementation Notes:**
- Update `src/jig/cli/status.py`:
  ```python
  def format_status_output(status_data: StatusData, verbose: bool) -> str:
      """Format status data for terminal output."""
      output = []
      output.append(click.style("JIG Graph Status", bold=True))
      output.append("")

      # Node counts
      output.append(f"Total nodes: {status_data.total_nodes}")
      for node_type, count in status_data.node_counts.items():
          output.append(f"  {node_type}: {count}")

      # Subsystems
      output.append("")
      output.append(click.style("Subsystems:", bold=True))
      for subsystem, nodes in status_data.subsystems.items():
          output.append(f"  {subsystem}: {len(nodes)} nodes")
          if verbose:
              for node_id in nodes:
                  output.append(f"    - {node_id}")

      # Orphaned nodes (warnings)
      if status_data.orphaned_nodes:
          output.append("")
          output.append(click.style("⚠ Orphaned nodes:", fg="yellow"))
          for node_id in status_data.orphaned_nodes:
              output.append(f"  - {node_id}")

      # Suggestions
      output.append("")
      output.append(click.style("Suggestions:", fg="cyan"))
      if status_data.orphaned_nodes:
          output.append(f"  • {len(status_data.orphaned_nodes)} nodes need relationships")
      # More suggestions...

      return "\n".join(output)
  ```
- Use click.style() for colors (green ✓, red ✗, yellow ⚠)
- Similar to validate command output from Slice 0

**Test Plan:**
- Integration tests in `tests/integration/test_status_command.py`:
  ```python
  # @jig T-STATUS-005 verifies:S-GRAPH-001 subsystem:core
  def test_status_output_format(tmp_path):
      """Verify status output contains expected sections."""
      # Run status, capture output
      # Assert contains: Total nodes, Subsystems, Suggestions

  # @jig T-STATUS-006 verifies:S-GRAPH-001 subsystem:core
  def test_status_verbose_shows_details(tmp_path):
      """Verify --verbose shows node lists."""

  # @jig T-STATUS-007 verifies:S-GRAPH-001 subsystem:core
  def test_status_not_initialized_error(tmp_path):
      """Verify clear error when jig/ doesn't exist."""
      # Exit code 3, helpful message
  ```

**Docs to Update:**
- README.md - Add `jigy status` example with output
- Update user guide with status command usage

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
  jigy status --verbose
  cd /tmp && jigy status  # Should fail gracefully
  ```
- Look for: Clear output, helpful suggestions, proper colors, exit codes

---

## Slice 2: Graph Relationships & Queries

### Work Unit 4: Graph Traversal Methods

**Goal:** Implement dependency and impact analysis methods in Graph class.

**Planned Effort:** 90-120m

**Acceptance Criteria:**
- Graph.get_dependencies(node_id) returns incoming edges (what this depends on)
- Graph.get_dependents(node_id) returns outgoing edges (what depends on this)
- Graph.find_path(start, end) returns shortest path or None
- All methods handle missing nodes gracefully
- Performance: <100ms for graphs with 100 nodes
- Unit tests >80% coverage

**Implementation Notes:**
- Extend `src/jig/core/graph.py`:
  ```python
  # @jig C-GRAPH-002 implements:S-GRAPH-003 subsystem:core interface:internal
  class Graph:
      def get_dependencies(self, node_id: str) -> list[str]:
          """Return nodes that this node depends on (incoming edges).

          For 'implements' edges: S-001 implements O-001 → O-001 is dependency of S-001
          For 'verifies' edges: T-001 verifies S-001 → S-001 is dependency of T-001
          """
          dependencies = []
          for edge in self.edges:
              if edge.from_node == node_id:
                  dependencies.append(edge.to_node)
          return dependencies

      def get_dependents(self, node_id: str) -> list[str]:
          """Return nodes that depend on this node (outgoing edges).

          For 'implements' edges: S-001 implements O-001 → S-001 is dependent of O-001
          """
          dependents = []
          for edge in self.edges:
              if edge.to_node == node_id:
                  dependents.append(edge.from_node)
          return dependents

      def find_path(self, start: str, end: str) -> list[str] | None:
          """Find shortest path between two nodes using BFS."""
          if start not in self.nodes or end not in self.nodes:
              return None

          # BFS implementation
          from collections import deque
          queue = deque([(start, [start])])
          visited = {start}

          while queue:
              current, path = queue.popleft()
              if current == end:
                  return path

              # Explore neighbors (both directions since graph may be directed)
              neighbors = self.get_dependencies(current) + self.get_dependents(current)
              for neighbor in neighbors:
                  if neighbor not in visited:
                      visited.add(neighbor)
                      queue.append((neighbor, path + [neighbor]))

          return None  # No path found
  ```

**Test Plan:**
- Unit tests in `tests/unit/test_graph_traversal.py`:
  ```python
  # @jig T-GRAPH-004 verifies:S-GRAPH-003 subsystem:core
  def test_get_dependencies():
      """Verify dependency detection for implements edges."""
      # S-001 implements O-001 → O-001 is dependency of S-001

  # @jig T-GRAPH-005 verifies:S-GRAPH-003 subsystem:core
  def test_get_dependents():
      """Verify dependent detection."""
      # S-001 implements O-001 → S-001 is dependent of O-001

  # @jig T-GRAPH-006 verifies:S-GRAPH-003 subsystem:core
  def test_find_path_exists():
      """Verify BFS finds shortest path."""

  # @jig T-GRAPH-007 verifies:S-GRAPH-003 subsystem:core
  def test_find_path_no_path():
      """Verify returns None when no path exists."""

  # @jig T-GRAPH-008 verifies:S-GRAPH-003 subsystem:core
  def test_traversal_performance():
      """Verify traversal completes in <100ms for 100 nodes."""
  ```

**Docs to Update:**
- Add docstrings to traversal methods
- Document edge direction semantics

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
- Commands: `pytest tests/unit/test_graph_traversal.py -v`
- Look for: All tests pass, performance within target

---

### Work Unit 5: Graph Query Methods

**Goal:** Implement filtering methods for querying nodes by type and subsystem.

**Planned Effort:** 60-75m

**Acceptance Criteria:**
- Graph.filter_by_type(node_type) returns all nodes of given type
- Graph.filter_by_subsystem(subsystem) returns all nodes in subsystem
- Both methods return sorted lists for consistent output
- Handle case-insensitive queries
- Unit tests >80% coverage

**Implementation Notes:**
- Extend `src/jig/core/graph.py`:
  ```python
  # @jig C-GRAPH-003 implements:S-GRAPH-003 subsystem:core interface:internal
  class Graph:
      def filter_by_type(self, node_type: str) -> list[OSTCNode]:
          """Return all nodes of given type (case-insensitive)."""
          node_type_lower = node_type.lower()
          filtered = [
              node for node in self.nodes.values()
              if node.type.lower() == node_type_lower
          ]
          return sorted(filtered, key=lambda n: n.id)

      def filter_by_subsystem(self, subsystem: str) -> list[OSTCNode]:
          """Return all nodes in given subsystem (case-insensitive)."""
          subsystem_lower = subsystem.lower()
          filtered = [
              node for node in self.nodes.values()
              if node.subsystem and node.subsystem.lower() == subsystem_lower
          ]
          return sorted(filtered, key=lambda n: n.id)
  ```

**Test Plan:**
- Unit tests in `tests/unit/test_graph_queries.py`:
  ```python
  # @jig T-GRAPH-009 verifies:S-GRAPH-003 subsystem:core
  def test_filter_by_type_outcome():
      """Verify filtering by outcome type."""

  # @jig T-GRAPH-010 verifies:S-GRAPH-003 subsystem:core
  def test_filter_by_type_case_insensitive():
      """Verify case-insensitive type filtering."""

  # @jig T-GRAPH-011 verifies:S-GRAPH-003 subsystem:core
  def test_filter_by_subsystem():
      """Verify filtering by subsystem."""

  # @jig T-GRAPH-012 verifies:S-GRAPH-003 subsystem:core
  def test_filter_returns_sorted():
      """Verify results are sorted by ID."""
  ```

**Docs to Update:**
- Add docstrings to filter methods

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
- Commands: `pytest tests/unit/test_graph_queries.py -v`
- Look for: All tests pass, sorted output

---

### Work Unit 6: Graph Show Command

**Goal:** Implement `jigy graph show <node-id>` to display node details and relationships.

**Planned Effort:** 75-90m

**Acceptance Criteria:**
- `jigy graph show O-JIG-001` displays node content and relationships
- Shows: ID, type, title, subsystem, status, body (first 10 lines)
- Shows dependencies (implements, verifies edges)
- Shows dependents (nodes that reference this one)
- Colorized output (type in bold, relationships in cyan)
- Exit codes: 0 (success), 1 (node not found), 3 (not initialized)
- Integration tests verify output format

**Implementation Notes:**
- Files to create:
  - `src/jig/cli/graph.py`:
    ```python
    # @jig C-GRAPH-004 implements:S-GRAPH-003 subsystem:core interface:public
    import click
    from jig.core.graph import Graph
    from jig.core.config import load_config

    @click.group()
    def graph():
        """Query and navigate the Intent Graph."""
        pass

    @graph.command()
    @click.argument('node_id')
    def show(node_id: str):
        """Show node details and relationships."""
        config = load_config()
        g = Graph.load_from_dir(config.intent_dir)

        if node_id not in g.nodes:
            click.echo(click.style(f"Error: Node {node_id} not found", fg="red"))
            sys.exit(1)

        node = g.nodes[node_id]

        # Display node
        click.echo(click.style(f"{node.id}", bold=True))
        click.echo(f"Type: {node.type}")
        click.echo(f"Title: {node.title}")
        if node.subsystem:
            click.echo(f"Subsystem: {node.subsystem}")
        click.echo("")
        # Show first 10 lines of body
        lines = node.body.split("\n")[:10]
        click.echo("\n".join(lines))
        if len(node.body.split("\n")) > 10:
            click.echo(click.style("... (use 'cat' to see full content)", fg="cyan"))

        # Show relationships
        click.echo("")
        click.echo(click.style("Dependencies:", fg="cyan"))
        deps = g.get_dependencies(node_id)
        if deps:
            for dep in deps:
                click.echo(f"  → {dep}")
        else:
            click.echo("  (none)")

        click.echo("")
        click.echo(click.style("Dependents:", fg="cyan"))
        dependents = g.get_dependents(node_id)
        if dependents:
            for dependent in dependents:
                click.echo(f"  ← {dependent}")
        else:
            click.echo("  (none)")
    ```
- Register `graph` command group in `src/jig/cli/main.py`:
  ```python
  from jig.cli.graph import graph
  cli.add_command(graph)
  ```

**Test Plan:**
- Integration tests in `tests/integration/test_graph_show.py`:
  ```python
  # @jig T-GRAPH-013 verifies:S-GRAPH-003 subsystem:core
  def test_graph_show_displays_node(tmp_path):
      """Verify show command displays node details."""

  # @jig T-GRAPH-014 verifies:S-GRAPH-003 subsystem:core
  def test_graph_show_displays_relationships(tmp_path):
      """Verify show displays dependencies and dependents."""

  # @jig T-GRAPH-015 verifies:S-GRAPH-003 subsystem:core
  def test_graph_show_node_not_found(tmp_path):
      """Verify clear error for missing node."""
      # Exit code 1
  ```

**Docs to Update:**
- README.md - Add `jigy graph show` example
- Add `--help` text to show command

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
  jigy graph show O-JIG-001
  jigy graph show S-JIG-001
  jigy graph show INVALID-001  # Should error
  ```
- Look for: Clear output, relationships shown, error handling

---

### Work Unit 7: Graph Deps/Impact Commands

**Goal:** Implement `jigy graph deps` and `jigy graph impact` for dependency analysis.

**Planned Effort:** 90-120m

**Acceptance Criteria:**
- `jigy graph deps <node-id>` shows dependency tree (what this depends on)
- `jigy graph impact <node-id>` shows impact tree (what depends on this)
- Tree formatting with proper indentation (├── └──)
- Shows transitive dependencies (recursive traversal)
- Detects and handles cycles gracefully
- Performance: <200ms for 100-node graphs
- Integration tests verify tree output

**Implementation Notes:**
- Extend `src/jig/cli/graph.py`:
  ```python
  # @jig C-GRAPH-005 implements:S-GRAPH-003 subsystem:core interface:public
  def format_tree(node_id: str, graph: Graph, visited: set, prefix: str = "") -> list[str]:
      """Recursively format dependency tree."""
      if node_id in visited:
          return [f"{prefix}↻ {node_id} (cycle)"]

      visited.add(node_id)
      lines = [f"{prefix}{node_id}"]

      deps = graph.get_dependencies(node_id)
      for i, dep in enumerate(deps):
          is_last = (i == len(deps) - 1)
          connector = "└── " if is_last else "├── "
          extension = "    " if is_last else "│   "
          subtree = format_tree(dep, graph, visited, prefix + extension)
          subtree[0] = prefix + connector + subtree[0].lstrip()
          lines.extend(subtree)

      return lines

  @graph.command()
  @click.argument('node_id')
  def deps(node_id: str):
      """Show dependency tree for a node."""
      config = load_config()
      g = Graph.load_from_dir(config.intent_dir)

      if node_id not in g.nodes:
          click.echo(click.style(f"Error: Node {node_id} not found", fg="red"))
          sys.exit(1)

      click.echo(click.style(f"Dependency tree for {node_id}:", bold=True))
      tree = format_tree(node_id, g, set())
      click.echo("\n".join(tree))

  @graph.command()
  @click.argument('node_id')
  def impact(node_id: str):
      """Show impact analysis (what depends on this node)."""
      # Similar to deps, but traverse dependents instead
  ```

**Test Plan:**
- Integration tests in `tests/integration/test_graph_deps.py`:
  ```python
  # @jig T-GRAPH-016 verifies:S-GRAPH-003 subsystem:core
  def test_graph_deps_shows_tree(tmp_path):
      """Verify deps shows dependency tree."""

  # @jig T-GRAPH-017 verifies:S-GRAPH-003 subsystem:core
  def test_graph_deps_handles_cycles(tmp_path):
      """Verify cycle detection in dependency tree."""

  # @jig T-GRAPH-018 verifies:S-GRAPH-003 subsystem:core
  def test_graph_impact_shows_dependents(tmp_path):
      """Verify impact shows what depends on node."""

  # @jig T-GRAPH-019 verifies:S-GRAPH-003 subsystem:core
  def test_graph_deps_performance():
      """Verify deps completes in <200ms for 100 nodes."""
  ```

**Docs to Update:**
- Add examples of `jigy graph deps` and `jigy graph impact` to user guide

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
  jigy graph deps S-JIG-001
  jigy graph impact O-JIG-001
  ```
- Look for: Tree formatting, cycle handling, performance

---

### Work Unit 8: Graph Path/List Commands

**Goal:** Implement `jigy graph path` and `jigy graph list` for path finding and filtering.

**Planned Effort:** 75-90m

**Acceptance Criteria:**
- `jigy graph path <start> <end>` finds shortest path between nodes
- `jigy graph list --type outcome` lists all nodes of type
- `jigy graph list --subsystem core` lists all nodes in subsystem
- Path command shows visual path with arrows (→)
- List command shows table format (ID, Type, Title)
- Both commands support YAML output for piping
- Integration tests verify output formats

**Implementation Notes:**
- Extend `src/jig/cli/graph.py`:
  ```python
  # @jig C-GRAPH-006 implements:S-GRAPH-003 subsystem:core interface:public
  @graph.command()
  @click.argument('start')
  @click.argument('end')
  def path(start: str, end: str):
      """Find path between two nodes."""
      config = load_config()
      g = Graph.load_from_dir(config.intent_dir)

      if start not in g.nodes:
          click.echo(click.style(f"Error: Node {start} not found", fg="red"))
          sys.exit(1)
      if end not in g.nodes:
          click.echo(click.style(f"Error: Node {end} not found", fg="red"))
          sys.exit(1)

      path = g.find_path(start, end)
      if path:
          click.echo(click.style(f"Path from {start} to {end}:", bold=True))
          click.echo(" → ".join(path))
      else:
          click.echo(click.style(f"No path found from {start} to {end}", fg="yellow"))

  @graph.command()
  @click.option('--type', help='Filter by node type')
  @click.option('--subsystem', help='Filter by subsystem')
  @click.option('--format', type=click.Choice(['table', 'yaml']), default='table')
  def list(type: str | None, subsystem: str | None, format: str):
      """List nodes with optional filters."""
      config = load_config()
      g = Graph.load_from_dir(config.intent_dir)

      nodes = list(g.nodes.values())
      if type:
          nodes = g.filter_by_type(type)
      if subsystem:
          nodes = g.filter_by_subsystem(subsystem)

      if format == 'yaml':
          # Output YAML for piping
          import yaml
          data = [{'id': n.id, 'type': n.type, 'title': n.title} for n in nodes]
          click.echo(yaml.dump(data))
      else:
          # Table format
          click.echo(f"{'ID':<20} {'Type':<15} {'Title'}")
          click.echo("-" * 80)
          for node in nodes:
              click.echo(f"{node.id:<20} {node.type:<15} {node.title}")
  ```

**Test Plan:**
- Integration tests in `tests/integration/test_graph_path_list.py`:
  ```python
  # @jig T-GRAPH-020 verifies:S-GRAPH-003 subsystem:core
  def test_graph_path_finds_route(tmp_path):
      """Verify path command finds route between nodes."""

  # @jig T-GRAPH-021 verifies:S-GRAPH-003 subsystem:core
  def test_graph_path_no_route(tmp_path):
      """Verify message when no path exists."""

  # @jig T-GRAPH-022 verifies:S-GRAPH-003 subsystem:core
  def test_graph_list_all_nodes(tmp_path):
      """Verify list shows all nodes in table format."""

  # @jig T-GRAPH-023 verifies:S-GRAPH-003 subsystem:core
  def test_graph_list_filter_by_type(tmp_path):
      """Verify list filters by type."""

  # @jig T-GRAPH-024 verifies:S-GRAPH-003 subsystem:core
  def test_graph_list_yaml_output(tmp_path):
      """Verify list outputs valid YAML for piping."""
  ```

**Docs to Update:**
- Add examples of path and list commands to user guide
- Document YAML output format for piping

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
  jigy graph path O-JIG-001 S-JIG-001
  jigy graph list --type outcome
  jigy graph list --subsystem core
  jigy graph list --format yaml | head
  ```
- Look for: Correct paths, filtered lists, valid YAML

---

## Slice 3: Decomposability Analysis

### Work Unit 9: Metrics Calculation (Modularity, Coupling)

**Goal:** Implement modularity and coupling ratio calculations.

**Planned Effort:** 120-150m

**Acceptance Criteria:**
- `src/jig/decompose/metrics.py` implements Newman modularity calculation
- Coupling ratio calculation (internal:external edges per subsystem)
- DecomposabilityMetrics dataclass with all fields
- Uses NetworkX for graph algorithms
- Handles edge cases (single subsystem, no edges)
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
        """
        if subsystem_name not in graph.subsystems:
            raise ValueError(f"Subsystem {subsystem_name} not found")

        subsystem_nodes = set(graph.subsystems[subsystem_name].nodes)
        internal = 0
        external = 0

        for edge in graph.edges:
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
  ```

**Docs to Update:**
- Add docstrings explaining modularity and coupling ratio
- Document formulas and interpretations

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
- Look for: Tests pass, modularity calculation correct

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
- Files to create:
  - `src/jig/decompose/detector.py`:
    ```python
    # @jig C-DECOMP-002 implements:S-DECOMP-002 subsystem:decompose interface:internal
    from jig.core.graph import Graph, Subsystem
    import networkx as nx
    from networkx.algorithms import community

    @dataclass
    class SubsystemProposal:
        name: str
        nodes: list[str]
        confidence: float  # 0.0-1.0

    def detect_subsystems(graph: Graph) -> list[SubsystemProposal]:
        """Auto-detect subsystems using Louvain method."""
        G = graph.to_networkx()

        # Run Louvain community detection
        communities = community.louvain_communities(G)

        proposals = []
        for i, node_set in enumerate(communities):
            nodes = sorted(list(node_set))
            name = suggest_subsystem_name(nodes, graph)
            confidence = calculate_confidence(nodes, G)

            proposals.append(SubsystemProposal(
                name=name,
                nodes=nodes,
                confidence=confidence
            ))

        return proposals

    def suggest_subsystem_name(nodes: list[str], graph: Graph) -> str:
        """Suggest subsystem name based on node IDs and titles."""
        # Extract common prefix from node IDs
        # e.g., [O-AUTH-001, S-AUTH-001, S-AUTH-002] → "auth"

        if not nodes:
            return "unknown"

        # Get prefix from first node ID (between first and second dash)
        first_id = nodes[0]
        parts = first_id.split('-')
        if len(parts) >= 2:
            prefix = parts[1].lower()
            return prefix

        return f"subsystem_{hash(tuple(nodes)) % 1000}"

    def calculate_confidence(nodes: list[str], G: nx.Graph) -> float:
        """Calculate confidence score for detected community.

        Based on:
        - Internal edge density
        - Consistency of node ID prefixes
        """
        # Simple heuristic: ratio of internal edges to possible edges
        subgraph = G.subgraph(nodes)
        num_edges = subgraph.number_of_edges()
        num_nodes = len(nodes)
        max_edges = num_nodes * (num_nodes - 1) / 2

        density = num_edges / max_edges if max_edges > 0 else 0.0
        return min(density * 2, 1.0)  # Scale up, cap at 1.0
    ```

**Test Plan:**
- Unit tests in `tests/unit/test_decompose_detector.py`:
  ```python
  # @jig T-DECOMP-005 verifies:S-DECOMP-002 subsystem:decompose
  def test_detect_subsystems_two_communities():
      """Verify Louvain detects two clear communities."""
      # Create graph with auth and user nodes, well separated

  # @jig T-DECOMP-006 verifies:S-DECOMP-002 subsystem:decompose
  def test_suggest_subsystem_name_from_prefix():
      """Verify name suggestion extracts prefix from IDs."""
      # [O-AUTH-001, S-AUTH-002] → "auth"

  # @jig T-DECOMP-007 verifies:S-DECOMP-002 subsystem:decompose
  def test_confidence_calculation():
      """Verify confidence based on edge density."""
  ```

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
- Returns list of violation descriptions
- Unit tests verify detection logic

**Implementation Notes:**
- Files to create:
  - `src/jig/decompose/analyzer.py`:
    ```python
    # @jig C-DECOMP-003 implements:S-DECOMP-004 subsystem:decompose interface:internal
    from jig.core.graph import Graph

    @dataclass
    class BoundaryViolation:
        from_node: str
        to_node: str
        from_subsystem: str
        to_subsystem: str
        edge_type: str
        reason: str

    def detect_boundary_violations(graph: Graph, allowed_types: set[str] | None = None) -> list[BoundaryViolation]:
        """Find edges that violate subsystem boundaries.

        Violations are edges between different subsystems,
        excluding allowed edge types (e.g., 'implements' is usually OK).
        """
        if allowed_types is None:
            # By default, 'implements' edges can cross boundaries
            # (S-AUTH-001 can implement O-CORE-001)
            allowed_types = {'implements'}

        violations = []

        # Build node → subsystem mapping
        node_to_subsystem = {}
        for subsystem_name, subsystem in graph.subsystems.items():
            for node_id in subsystem.nodes:
                node_to_subsystem[node_id] = subsystem_name

        # Check each edge
        for edge in graph.edges:
            from_subsystem = node_to_subsystem.get(edge.from_node)
            to_subsystem = node_to_subsystem.get(edge.to_node)

            # Skip if either node has no subsystem
            if not from_subsystem or not to_subsystem:
                continue

            # Skip if same subsystem
            if from_subsystem == to_subsystem:
                continue

            # Skip if allowed edge type
            if edge.type in allowed_types:
                continue

            # This is a violation
            violations.append(BoundaryViolation(
                from_node=edge.from_node,
                to_node=edge.to_node,
                from_subsystem=from_subsystem,
                to_subsystem=to_subsystem,
                edge_type=edge.type,
                reason=f"'{edge.type}' edge crosses from {from_subsystem} to {to_subsystem}"
            ))

        return violations
    ```

**Test Plan:**
- Unit tests in `tests/unit/test_boundary_violations.py`:
  ```python
  # @jig T-DECOMP-008 verifies:S-DECOMP-004 subsystem:decompose
  def test_detect_boundary_violations():
      """Verify detection of cross-subsystem edges."""
      # Create graph with auth and user subsystems
      # Add 'depends_on' edge from auth to user
      # Should be flagged as violation

  # @jig T-DECOMP-009 verifies:S-DECOMP-004 subsystem:decompose
  def test_allowed_edge_types_not_flagged():
      """Verify 'implements' edges are allowed across boundaries."""
      # S-AUTH-001 implements O-CORE-001 should NOT be violation

  # @jig T-DECOMP-010 verifies:S-DECOMP-004 subsystem:decompose
  def test_no_violations_same_subsystem():
      """Verify edges within subsystem are not violations."""
  ```

**Docs to Update:**
- Document boundary violation concept
- Explain allowed edge types

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
- Look for: Violations detected correctly

---

### Work Unit 12: Decompose Detect Command

**Goal:** Implement `jigy decompose detect` to auto-detect subsystems.

**Planned Effort:** 60-75m

**Acceptance Criteria:**
- `jigy decompose detect` runs Louvain community detection
- Displays proposed subsystems with confidence scores
- Option to save proposals to subsystems.yaml
- Colorized output (high confidence green, low yellow)
- Integration tests verify output

**Implementation Notes:**
- Files to create:
  - `src/jig/cli/decompose.py`:
    ```python
    # @jig C-DECOMP-004 implements:S-DECOMP-002 subsystem:decompose interface:public
    import click
    from jig.core.graph import Graph
    from jig.core.config import load_config
    from jig.decompose.detector import detect_subsystems

    @click.group()
    def decompose():
        """Analyze subsystem decomposability."""
        pass

    @decompose.command()
    @click.option('--save', is_flag=True, help='Save proposals to subsystems.yaml')
    def detect(save: bool):
        """Auto-detect subsystems from graph structure."""
        config = load_config()
        graph = Graph.load_from_dir(config.intent_dir)

        click.echo(click.style("Detecting subsystems...", bold=True))
        proposals = detect_subsystems(graph)

        click.echo(f"\nFound {len(proposals)} subsystem(s):\n")

        for proposal in proposals:
            confidence_color = "green" if proposal.confidence > 0.7 else "yellow"
            click.echo(click.style(f"{proposal.name}", bold=True) +
                      f" ({len(proposal.nodes)} nodes, " +
                      click.style(f"confidence: {proposal.confidence:.2f}", fg=confidence_color) + ")")

            for node_id in proposal.nodes:
                click.echo(f"  - {node_id}")
            click.echo()

        if save:
            # Save to jig/subsystems.yaml
            click.echo(click.style("Saving to jig/subsystems.yaml...", fg="cyan"))
            # Implementation to save proposals
    ```
- Register in `src/jig/cli/main.py`:
  ```python
  from jig.cli.decompose import decompose
  cli.add_command(decompose)
  ```

**Test Plan:**
- Integration tests in `tests/integration/test_decompose_detect.py`:
  ```python
  # @jig T-DECOMP-011 verifies:S-DECOMP-002 subsystem:decompose
  def test_decompose_detect_output(tmp_path):
      """Verify detect displays subsystem proposals."""

  # @jig T-DECOMP-012 verifies:S-DECOMP-002 subsystem:decompose
  def test_decompose_detect_save_option(tmp_path):
      """Verify --save writes to subsystems.yaml."""
  ```

**Docs to Update:**
- Add `jigy decompose detect` example to user guide

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
  jigy decompose detect
  jigy decompose detect --save
  ```
- Look for: Subsystem proposals, confidence scores

---

### Work Unit 13: Decompose Metrics Command

**Goal:** Implement `jigy decompose metrics` to calculate health scores.

**Planned Effort:** 75-90m

**Acceptance Criteria:**
- `jigy decompose metrics` calculates and displays modularity, coupling ratios
- Shows per-subsystem metrics (internal/external edges, ratio)
- Overall graph health score
- Option for YAML output
- Performance: <5s for 100-node graphs
- Integration tests verify calculations

**Implementation Notes:**
- Extend `src/jig/cli/decompose.py`:
  ```python
  # @jig C-DECOMP-005 implements:S-DECOMP-001,S-DECOMP-003 subsystem:decompose interface:public
  from jig.decompose.metrics import calculate_all_metrics

  @decompose.command()
  @click.option('--format', type=click.Choice(['table', 'yaml']), default='table')
  def metrics(format: str):
      """Calculate decomposability health scores."""
      config = load_config()
      graph = Graph.load_from_dir(config.intent_dir)

      click.echo(click.style("Calculating metrics...", bold=True))
      metrics = calculate_all_metrics(graph)

      if format == 'yaml':
          import yaml
          click.echo(yaml.dump(metrics))
      else:
          # Table format
          click.echo(f"\nModularity: {click.style(f'{metrics.modularity:.3f}', bold=True)}")
          click.echo(f"Subsystems: {metrics.subsystem_count}")
          click.echo(f"Avg Coupling Ratio: {metrics.avg_coupling_ratio:.2f}\n")

          click.echo(click.style("Per-Subsystem Metrics:", bold=True))
          click.echo(f"{'Subsystem':<20} {'Nodes':<8} {'Internal':<10} {'External':<10} {'Ratio':<10}")
          click.echo("-" * 70)

          for name, sm in metrics.subsystems.items():
              ratio_str = f"{sm.coupling_ratio:.2f}" if sm.coupling_ratio != float('inf') else "∞"
              ratio_color = "green" if sm.coupling_ratio >= 10 else "yellow" if sm.coupling_ratio >= 5 else "red"

              click.echo(f"{name:<20} {sm.node_count:<8} {sm.internal_edges:<10} {sm.external_edges:<10} " +
                        click.style(f"{ratio_str:<10}", fg=ratio_color))
  ```

**Test Plan:**
- Integration tests in `tests/integration/test_decompose_metrics.py`:
  ```python
  # @jig T-DECOMP-013 verifies:S-DECOMP-001,S-DECOMP-003 subsystem:decompose
  def test_decompose_metrics_output(tmp_path):
      """Verify metrics displays modularity and coupling ratios."""

  # @jig T-DECOMP-014 verifies:S-DECOMP-001 subsystem:decompose
  def test_decompose_metrics_performance(tmp_path):
      """Verify metrics completes in <5s for 100 nodes."""

  # @jig T-DECOMP-015 verifies:S-DECOMP-001 subsystem:decompose
  def test_decompose_metrics_yaml_output(tmp_path):
      """Verify YAML output format."""
  ```

**Docs to Update:**
- Document metrics output and interpretation
- Explain target values (modularity >0.7, coupling >10:1)

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
  jigy decompose metrics --format yaml
  ```
- Look for: Correct calculations, color coding, performance

---

### Work Unit 14: Decompose Validate Command

**Goal:** Implement `jigy decompose validate` to check for boundary violations.

**Planned Effort:** 60m

**Acceptance Criteria:**
- `jigy decompose validate` checks for subsystem boundary violations
- Displays violations with clear descriptions
- Exit codes: 0 (no violations), 1 (violations found)
- Shows violation count and details
- Integration tests verify detection

**Implementation Notes:**
- Extend `src/jig/cli/decompose.py`:
  ```python
  # @jig C-DECOMP-006 implements:S-DECOMP-004 subsystem:decompose interface:public
  from jig.decompose.analyzer import detect_boundary_violations

  @decompose.command()
  def validate():
      """Check for subsystem boundary violations."""
      config = load_config()
      graph = Graph.load_from_dir(config.intent_dir)

      click.echo(click.style("Checking subsystem boundaries...", bold=True))
      violations = detect_boundary_violations(graph)

      if not violations:
          click.echo(click.style("✓ No boundary violations found", fg="green"))
          sys.exit(0)

      click.echo(click.style(f"✗ Found {len(violations)} boundary violation(s):", fg="red"))
      click.echo()

      for v in violations:
          click.echo(f"  {v.from_node} ({v.from_subsystem}) " +
                    click.style(f"--[{v.edge_type}]-->", fg="red") +
                    f" {v.to_node} ({v.to_subsystem})")
          click.echo(f"    Reason: {v.reason}\n")

      sys.exit(1)
  ```

**Test Plan:**
- Integration tests in `tests/integration/test_decompose_validate.py`:
  ```python
  # @jig T-DECOMP-016 verifies:S-DECOMP-004 subsystem:decompose
  def test_decompose_validate_no_violations(tmp_path):
      """Verify validate passes when no violations."""
      # Exit code 0

  # @jig T-DECOMP-017 verifies:S-DECOMP-004 subsystem:decompose
  def test_decompose_validate_detects_violations(tmp_path):
      """Verify validate detects cross-subsystem edges."""
      # Create violation, exit code 1
  ```

**Docs to Update:**
- Document boundary validation rules
- Explain allowed vs. disallowed edge types

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
- Commands: `jigy decompose validate`
- Look for: Correct violation detection, exit codes

---

### Work Unit 15: Decompose Report Command

**Goal:** Implement `jigy decompose report` to generate comprehensive analysis.

**Planned Effort:** 60-75m

**Acceptance Criteria:**
- `jigy decompose report` combines all analyses into one report
- Includes: metrics, violations, recommendations
- Option to save report to file (YAML or Markdown)
- Report includes timestamp and graph metadata
- Integration tests verify report generation

**Implementation Notes:**
- Extend `src/jig/cli/decompose.py`:
  ```python
  # @jig C-DECOMP-007 implements:S-DECOMP-001,S-DECOMP-004 subsystem:decompose interface:public
  from datetime import datetime

  @decompose.command()
  @click.option('--output', help='Output file (default: stdout)')
  @click.option('--format', type=click.Choice(['yaml', 'markdown']), default='markdown')
  def report(output: str | None, format: str):
      """Generate comprehensive decomposability analysis."""
      config = load_config()
      graph = Graph.load_from_dir(config.intent_dir)

      click.echo(click.style("Generating report...", bold=True))

      # Calculate all metrics
      metrics = calculate_all_metrics(graph)
      violations = detect_boundary_violations(graph)

      # Generate report
      if format == 'yaml':
          report_data = {
              'timestamp': datetime.now().isoformat(),
              'graph_size': len(graph.nodes),
              'metrics': metrics,
              'violations': [v.__dict__ for v in violations]
          }
          report_text = yaml.dump(report_data)
      else:  # markdown
          report_text = f"""# Decomposability Analysis Report

**Generated:** {datetime.now().isoformat()}
**Graph Size:** {len(graph.nodes)} nodes

## Overall Metrics

- **Modularity:** {metrics.modularity:.3f} (target: >0.7)
- **Subsystems:** {metrics.subsystem_count}
- **Avg Coupling Ratio:** {metrics.avg_coupling_ratio:.2f} (target: >10:1)

## Subsystem Details

{''.join([f'''
### {name}
- Nodes: {sm.node_count}
- Internal edges: {sm.internal_edges}
- External edges: {sm.external_edges}
- Coupling ratio: {sm.coupling_ratio:.2f}
''' for name, sm in metrics.subsystems.items()])}

## Boundary Violations

{f"Found {len(violations)} violation(s):" if violations else "✓ No violations found"}

{''.join([f"- {v.from_node} → {v.to_node}: {v.reason}\n" for v in violations])}

## Recommendations

{generate_recommendations(metrics, violations)}
"""

      if output:
          with open(output, 'w') as f:
              f.write(report_text)
          click.echo(click.style(f"Report saved to {output}", fg="green"))
      else:
          click.echo(report_text)

  def generate_recommendations(metrics, violations) -> str:
      """Generate actionable recommendations."""
      recs = []

      if metrics.modularity < 0.7:
          recs.append("- Consider refactoring to improve modularity (current: {:.2f}, target: >0.7)".format(metrics.modularity))

      for name, sm in metrics.subsystems.items():
          if sm.coupling_ratio < 10:
              recs.append(f"- Subsystem '{name}' has low coupling ratio ({sm.coupling_ratio:.2f}), consider reducing external dependencies")

      if violations:
          recs.append(f"- Address {len(violations)} boundary violations to improve subsystem independence")

      if not recs:
          recs.append("✓ All metrics meet targets - excellent decomposition!")

      return "\n".join(recs)
  ```

**Test Plan:**
- Integration tests in `tests/integration/test_decompose_report.py`:
  ```python
  # @jig T-DECOMP-018 verifies:S-DECOMP-001 subsystem:decompose
  def test_decompose_report_markdown(tmp_path):
      """Verify report generates markdown format."""

  # @jig T-DECOMP-019 verifies:S-DECOMP-001 subsystem:decompose
  def test_decompose_report_yaml(tmp_path):
      """Verify report generates YAML format."""

  # @jig T-DECOMP-020 verifies:S-DECOMP-001 subsystem:decompose
  def test_decompose_report_saves_to_file(tmp_path):
      """Verify --output saves report to file."""
  ```

**Docs to Update:**
- Add report examples to user guide
- Document report format and sections

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
  jigy decompose report
  jigy decompose report --output report.md
  jigy decompose report --format yaml --output report.yaml
  ```
- Look for: Complete report, recommendations, saved files

---

## Slice 4: Documentation & Release

### Work Unit 16: User Guide for Graph Commands

**Goal:** Write comprehensive user guide for all graph and decompose commands.

**Planned Effort:** 90-120m

**Acceptance Criteria:**
- `docs/user-guide/GRAPH_COMMANDS.md` created with examples
- Covers: status, graph (all subcommands), decompose (all subcommands)
- Each command has: purpose, usage, examples, output interpretation
- Screenshots or example outputs included
- Tutorial walkthrough for common workflows
- Cross-linked with README.md

**Implementation Notes:**
- Files to create:
  - `docs/user-guide/GRAPH_COMMANDS.md`:
    ```markdown
    # Graph Commands User Guide

    ## Overview
    JIG provides commands to query, navigate, and analyze the Intent Graph...

    ## Status Command
    ### Purpose
    Show graph health and actionable next steps...

    ### Usage
    ```bash
    jigy status [--verbose]
    ```

    ### Examples
    ...

    ## Graph Commands
    ### jigy graph show
    ...

    [Continue for all commands]
    ```
- Include real output examples from JIG's own graph
- Add troubleshooting section

**Test Plan:**
- Manual review: Follow guide step-by-step
- Verify all examples work
- Test commands on fresh JIG installation

**Docs to Update:**
- README.md - Link to GRAPH_COMMANDS.md
- Add "Graph Navigation" section to README

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
- Commands: Follow guide from start to finish
- Look for: All examples work, clear explanations

---

### Work Unit 17: Architecture Documentation

**Goal:** Write technical architecture documentation for graph and decompose subsystems.

**Planned Effort:** 75-90m

**Acceptance Criteria:**
- `docs/architecture/GRAPH_SUBSYSTEM.md` created
- Documents: data structures, algorithms, design decisions
- Explains modularity calculation, Louvain method, coupling ratio
- Includes diagrams (text-based or ASCII art)
- References to relevant papers/algorithms
- Subsystem boundary documentation

**Implementation Notes:**
- Files to create:
  - `docs/architecture/GRAPH_SUBSYSTEM.md`:
    ```markdown
    # Graph Subsystem Architecture

    ## Overview
    The graph subsystem provides core data structures and algorithms for managing the Intent Graph...

    ## Data Structures
    ### Graph
    ...

    ### Edge
    ...

    ## Algorithms
    ### Modularity Calculation (Newman)
    Formula: Q = (1/2m) Σ[A_ij - (k_i * k_j)/2m] * δ(c_i, c_j)
    ...

    ### Community Detection (Louvain)
    Implementation: NetworkX louvain_communities
    ...

    ## Design Decisions
    ### Why NetworkX?
    ...
    ```

**Test Plan:**
- Manual review for technical accuracy
- Peer review by another developer

**Docs to Update:**
- Link from README.md architecture section

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
- Commands: Read and verify technical accuracy
- Look for: Clear explanations, correct algorithms

---

### Work Unit 18: Tutorial & Quality Gates

**Goal:** Create end-to-end tutorial and ensure all quality gates pass.

**Planned Effort:** 90-120m

**Acceptance Criteria:**
- `docs/tutorials/INTENT_GRAPH_TUTORIAL.md` created
- Walkthrough: init → create nodes → query → analyze decomposability
- Uses sample project (not JIG itself)
- All quality gates pass:
  - `pytest` - all tests pass
  - `pytest --cov` - coverage >80%
  - `ruff check` - no errors
  - `mypy src/` - no type errors
- Performance benchmarks documented

**Implementation Notes:**
- Create tutorial with sample "task management" app
- Include:
  1. Initialize JIG
  2. Create Outcomes and Specifications
  3. Query graph with various commands
  4. Run decompose analysis
  5. Interpret results
- Run all quality gates, fix any issues

**Test Plan:**
- Manual: Follow tutorial start to finish
- Automated: Run quality gates in CI

**Docs to Update:**
- README.md - Link to tutorial

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
- Commands: Follow tutorial, run quality gates
- Look for: Tutorial works, all gates pass

---

### Work Unit 19: Dogfooding & v0.2.0 Release

**Goal:** Run all Phase 1 commands on JIG's own graph, tag v0.2.0 release.

**Planned Effort:** 60-90m

**Acceptance Criteria:**
- Run `jigy status` on JIG's graph - output looks good
- Run `jigy graph` commands on JIG nodes - navigation works
- Run `jigy decompose metrics` on JIG - modularity >0.7 target met
- Run `jigy decompose report` on JIG - generate report
- All Phase 1 OSTC nodes validated
- Git tag: v0.2.0-intent-graph
- Release notes written

**Implementation Notes:**
- Dogfooding checklist:
  ```bash
  jigy status --verbose
  jigy graph show O-GRAPH-001
  jigy graph deps S-GRAPH-002
  jigy graph list --type outcome
  jigy decompose metrics
  jigy decompose validate
  jigy decompose report --output docs/metrics/jig-decomposability.md
  jigy validate --check-all
  ```
- Create release notes:
  - New commands added
  - Features delivered
  - Performance metrics
  - Breaking changes (if any)
- Tag release:
  ```bash
  git tag -a v0.2.0-intent-graph -m "Phase 1: Intent Graph subsystem complete"
  ```

**Test Plan:**
- Manual validation of all dogfooding commands
- Verify JIG's modularity score
- Check for any issues

**Docs to Update:**
- CHANGELOG.md - Add v0.2.0 entry
- README.md - Update version and features

**Reflect (≤5 bullets; keep crisp)**
- What worked well:
  - [to be filled]
- What could be better:
  - [to be filled]
- Discoveries:
  - [to be filled]

**Links:**
- Commit: [to be filled]
- Tag: v0.2.0-intent-graph

**Human Validation:**
- Commands: All dogfooding commands above
- Look for: JIG's own graph is healthy, modularity >0.7, release tagged

---

## Completion Summary

### Summary
- Scope delivered: [to be filled]
- Key decisions: [to be filled]
- Deltas from SCOPE: [to be filled]

### Metrics
- Units: 19 total (WU0-WU19)
- Rework rate: [to be filled]
- Flaky test events: [to be filled]
- Test coverage: [target: >80%]
- Docs lag: [to be filled]
- Markers captured: [to be filled]

### Reflection Roll-up
- Repeatable wins:
  - [to be filled from WU reflects]
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

**Recommended OSTC Nodes (from DISCOVERIES only):**
(These are NEW constraints discovered during Phase 1 implementation, not the ones created in WU0)
- [to be filled by AIA based on #DISCOVERY markers]

**Subsystems Touched:**
- core (graph data structures, queries)
- decompose (metrics, detection, analysis)
- cli (status, graph, decompose commands)

**Next Step:** Phase 2 - Delta Workflows (Slice 5-8)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-19
**Status:** Draft (Ready to execute WU0)
