# Scope of Work: Nested Subsystems

**Date:** 2025-11-20  
**Status:** Draft  
**Version:** 1.1  
**Related:** S004_JIG_DEVELOPMENT_STRATEGY_V2.md, S005_PLAN_phase_1_intent_graph.md, JIG-Concept-v7.md

> "Enable hierarchical subsystem organization for complex systems while maintaining simplicity for small projects."

---

## Executive Summary

This document defines the scope of work for implementing **nested subsystems** in JIG v7. Currently, JIG supports a flat subsystem structure where all subsystems exist at the same level. This enhancement will allow subsystems to contain child subsystems, enabling better organization of large, complex systems while maintaining backward compatibility with existing flat structures.

**JIG v7 Context:** This feature is part of the broader OSTCX model (Outcome, Specification, Test, Code, Constraint) where constraints act as predicates over the Intent Graph. Nested subsystems enhance the hierarchical organization of the OSTC graph while constraints provide cross-cutting validation.

**Key Benefits:**
1. **Hierarchical Organization** - Model real system architecture with parent/child subsystem relationships
2. **Scalability** - Support projects with dozens or hundreds of subsystems without overwhelming flat lists
3. **Flexible Granularity** - Allow both coarse-grained and fine-grained decomposition analysis
4. **Backward Compatible** - Existing flat subsystems continue to work unchanged
5. **Constraint Integration** (v7) - Constraints can target entire subsystem hierarchies or specific leaves, maintaining clean separation between architectural dependencies (OSTC edges) and system properties (constraint predicates)

**Example Use Case:**
```yaml
subsystems:
  crdt:
    name: "CRDT Core"
    description: "Conflict-free Replicated Data Types"
    nodes: []  # Parent subsystem has no direct nodes
    subsystems:
      crdt-ser:
        name: "CRDT Serialization"
        description: "Serialization layer for CRDTs"
        nodes:
          - O-CRDT-SER-001
          - O-CRDT-SER-002
          - S-CRDT-SER-001
          - S-CRDT-SER-002
      crdt-sync:
        name: "CRDT Synchronization"
        nodes:
          - O-CRDT-SYNC-001
          - S-CRDT-SYNC-001
```

---

## Part 1: Current State Analysis

### Existing Subsystem Implementation

**Current Data Model (`src/jig/core/graph.py`):**
```python
@dataclass
class Subsystem:
    """Represents a subsystem grouping of nodes."""
    name: str
    nodes: list[str] = field(default_factory=list)
```

**Current YAML Format (`jig/subsystems.yaml`):**
```yaml
subsystems:
  core:
    name: core
    description: "Core JIG infrastructure"
    max_exports: 5
    allowed_dependencies: []
    status: bootstrap
```

**Current Graph Index Format (`jig/graph-index.yaml`):**
```yaml
nodes:
  O-JIG-001:
    file: jig/outcomes/O-JIG-001.md
    type: outcome
    subsystem: core
    constraints: []

subsystems:
  core:
    nodes:
      - O-JIG-001
      - S-JIG-001
```

**Limitations:**
1. **Flat Structure Only** - No way to group related subsystems
2. **No Hierarchy in Metrics** - Decomposability analysis treats all subsystems equally
3. **Scaling Issues** - Large projects with 20+ subsystems become hard to navigate
4. **No Scoping** - Can't analyze a subset of the system (e.g., "just the CRDT subsystem")

---

## Part 2: Requirements

### Functional Requirements

**FR-1: Hierarchical Subsystem Definition**
- Subsystems MAY contain child subsystems
- Subsystems MAY contain nodes directly
- Subsystems MAY contain both child subsystems AND nodes
- Nesting depth SHOULD be unlimited (but recommend max 3-4 levels)
- Each subsystem MUST have a unique fully-qualified name (e.g., `crdt.ser`)

**FR-2: Backward Compatibility**
- Existing flat subsystem definitions MUST continue to work
- No breaking changes to existing YAML formats
- Existing commands MUST work with nested subsystems (show flattened view by default)

**FR-3: Node Assignment**
- Each node MUST belong to exactly one subsystem (leaf subsystem)
- Nodes CANNOT be assigned to parent subsystems that have children
- Node subsystem field uses fully-qualified name (e.g., `subsystem: crdt.ser`)

**FR-4: Query and Navigation**
- `jigy graph list --subsystem crdt` SHOULD list all nodes in `crdt` and its children
- `jigy graph list --subsystem crdt.ser` SHOULD list only nodes in `crdt.ser`
- `jigy status` SHOULD show hierarchical subsystem breakdown (tree view)
- New option: `--flat` to show flattened view (backward compatible)
- Subsystem queries SHOULD integrate with constraint scoping (e.g., constraints can target `crdt` recursively)

**FR-5: Decomposability Analysis**
- `jigy decompose metrics` SHOULD calculate metrics at each level of hierarchy
- Parent subsystem metrics aggregate child metrics
- Boundary violations SHOULD respect hierarchy (edges within parent are OK)
- Option to analyze specific subsystem subtree: `jigy decompose metrics --subsystem crdt`

**FR-6: Validation**
- `jigy validate` MUST check for:
  - Unique subsystem names at each level
  - No cycles in subsystem hierarchy
  - Nodes reference valid subsystem paths
  - Parent subsystems with children have no direct nodes
  - Constraint scope selectors can resolve nested subsystem paths

### Non-Functional Requirements

**NFR-1: Performance**
- Loading nested subsystems MUST complete in <100ms for 100 subsystems
- Hierarchical queries MUST complete in <200ms for 100 subsystems
- No significant performance degradation vs. flat structure

**NFR-2: Usability**
- Hierarchical view MUST be clear and intuitive (tree formatting)
- Error messages MUST clearly indicate subsystem path issues
- Documentation MUST include migration guide from flat to nested

**NFR-3: Maintainability**
- Code changes SHOULD be localized to graph and decompose subsystems
- Existing tests SHOULD continue to pass (or require minimal updates)
- New tests SHOULD cover nested-specific scenarios

---

## Part 3: Design

### Data Model Changes

**Updated Subsystem Dataclass:**
```python
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

**Updated Graph Dataclass:**
```python
@dataclass
class Graph:
    nodes: dict[str, OSTCNode] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    subsystems: dict[str, Subsystem] = field(default_factory=dict)
    
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
        """Return all constraints that apply to a subsystem.
        
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

**Integration with Constraints (v7):**

The nested subsystem structure integrates seamlessly with JIG v7's constraint system:
- Constraints can target specific leaf subsystems: `scope: {subsystems: [crdt.ser]}`
- Constraints can target parent subsystems recursively: `scope: {subsystems: [crdt], recursive: true}`
- Constraint queries use dot notation: `query: "subsystem:crdt.* AND type:C"`
- Metrics exclude constraint relationships to preserve decomposability
- Status commands show constraint compliance per subsystem

### YAML Format Changes

**subsystems.yaml (Enhanced):**
```yaml
version: 1.0.0
created: 2025-11-20

subsystems:
  core:
    name: core
    description: "Core JIG infrastructure - config, parsing, validation, graph"
    max_exports: 5
    allowed_dependencies: []
    status: active
    # Flat subsystem - no children
  
  crdt:
    name: crdt
    description: "CRDT implementation and supporting infrastructure"
    max_exports: 10
    allowed_dependencies: [core]
    status: active
    subsystems:
      ser:
        name: ser
        description: "CRDT serialization layer"
        max_exports: 3
        allowed_dependencies: [core]
        status: active
      sync:
        name: sync
        description: "CRDT synchronization protocol"
        max_exports: 4
        allowed_dependencies: [core, crdt.ser]
        status: active
```

**graph-index.yaml (Enhanced):**
```yaml
version: 1.0.0
created: 2025-11-20

nodes:
  O-JIG-001:
    file: jig/outcomes/O-JIG-001.md
    type: outcome
    subsystem: core
    constraints: []
  
  O-CRDT-SER-001:
    file: jig/outcomes/O-CRDT-SER-001.md
    type: outcome
    subsystem: crdt.ser
    constraints: [X-PERF-001]

subsystems:
  core:
    nodes:
      - O-JIG-001
      - S-JIG-001
    constraints: []
  
  crdt.ser:  # Fully-qualified path for nested subsystem
    nodes:
      - O-CRDT-SER-001
      - O-CRDT-SER-002
      - S-CRDT-SER-001
    constraints: [X-PERF-001]
  
  crdt.sync:
    nodes:
      - O-CRDT-SYNC-001
      - S-CRDT-SYNC-001
    constraints: [X-PERF-001]
```

**Node Frontmatter (Enhanced):**
```yaml
---
id: O-CRDT-SER-001
type: outcome
title: "CRDT serialization is deterministic"
subsystem: crdt.ser  # Fully-qualified path
status: active
created: 2025-11-20
constraints: [X-PERF-001]  # Constraints that apply (optional)
---
```

### Command Output Changes

**jigy status (Hierarchical View):**
```
JIG Graph Status

Total nodes: 47
  outcome: 12
  specification: 28
  test: 7

Subsystems:
  core (15 nodes)
    ├── O-JIG-001, O-JIG-002, ...
    └── Constraints: [X-SEC-001]
  crdt (32 nodes)
    ├── ser (18 nodes)
    │   ├── O-CRDT-SER-001, O-CRDT-SER-002, ...
    │   └── Constraints: [X-PERF-001]
    └── sync (14 nodes)
        ├── O-CRDT-SYNC-001, ...
        └── Constraints: [X-PERF-001]

Health: ✓ Good
Suggestions:
  • Run 'jigy decompose metrics' to analyze subsystem boundaries
  • Run 'jigy validate --constraints' to check constraint compliance
```

**jigy status --flat (Backward Compatible):**
```
JIG Graph Status

Total nodes: 47
  outcome: 12
  specification: 28
  test: 7

Subsystems:
  core: 15 nodes
  crdt.ser: 18 nodes
  crdt.sync: 14 nodes

Health: ✓ Good
```

**jigy graph list --subsystem crdt:**
```
Listing nodes in subsystem 'crdt' (recursive)

ID                   Type            Subsystem      Title
--------------------------------------------------------------------------------
O-CRDT-SER-001       outcome         crdt.ser       CRDT serialization is deterministic
O-CRDT-SER-002       outcome         crdt.ser       Serialization handles all CRDT types
S-CRDT-SER-001       specification   crdt.ser       Serialize CRDTs to protobuf
O-CRDT-SYNC-001      outcome         crdt.sync      CRDT sync completes in <100ms
...

Total: 32 nodes
```

**jigy decompose metrics --subsystem crdt:**
```
Decomposability Metrics for 'crdt' subsystem

Modularity: 0.82 (target: >0.7) ✓
Subsystems: 2 (ser, sync)
Avg Coupling Ratio: 15.3 (target: >10:1) ✓

Per-Subsystem Metrics:
Subsystem            Nodes    Internal   External   Ratio    Constraints
--------------------------------------------------------------------------
crdt.ser             18       42         3          14.0 ✓   X-PERF-001 (100%)
crdt.sync            14       28         2          14.0 ✓   X-PERF-001 (88%)

Boundary Violations: 0 ✓
Constraint Compliance: 94% overall (1 minor violation in crdt.sync)
```

---

## Part 4: Implementation Plan

### Phase 1: Data Model & Loading (Week 1)

**Deliverables:**
- Updated `Subsystem` dataclass with nesting support
- Updated `Graph.load_from_dir()` to parse nested subsystems
- Validation for nested subsystem structure
- Unit tests for hierarchical loading

**Files to Modify:**
- `src/jig/core/graph.py` - Add nesting to Subsystem, update Graph methods
- `src/jig/core/validator.py` - Add validation for nested structure
- `tests/unit/test_graph.py` - Add nested subsystem tests
- `tests/unit/test_validator.py` - Add nested validation tests

**Acceptance Criteria:**
- [ ] Subsystem dataclass supports nesting (subsystems field)
- [ ] Graph.load_from_dir() correctly parses nested subsystems from YAML
- [ ] Validation detects cycles in subsystem hierarchy
- [ ] Validation ensures nodes reference valid subsystem paths
- [ ] Validation prevents nodes in parent subsystems with children
- [ ] Unit tests cover 3-level nesting scenarios
- [ ] Backward compatibility: flat subsystems still load correctly

---

### Phase 2: Query & Navigation (Week 2)

**Deliverables:**
- Updated graph query methods to support hierarchical paths
- `jigy status` with hierarchical tree view
- `jigy graph list --subsystem` with recursive option
- Integration tests for nested queries

**Files to Modify:**
- `src/jig/core/graph.py` - Add `get_subsystem_by_path()`, `get_all_subsystem_paths()`
- `src/jig/cli/status.py` - Add hierarchical tree formatting
- `src/jig/cli/graph.py` - Update list command for recursive subsystem queries
- `tests/integration/test_status_command.py` - Add nested subsystem tests
- `tests/integration/test_graph_path_list.py` - Add nested query tests

**Acceptance Criteria:**
- [ ] `Graph.get_subsystem_by_path("crdt.ser")` returns correct subsystem
- [ ] `jigy status` displays hierarchical tree with proper indentation
- [ ] `jigy status --flat` displays flattened view (backward compatible)
- [ ] `jigy graph list --subsystem crdt` lists all nodes recursively
- [ ] `jigy graph list --subsystem crdt.ser` lists only leaf nodes
- [ ] Constraint information displayed in status output (per subsystem)
- [ ] Subsystem queries work with constraint scope selectors
- [ ] Performance: queries complete in <200ms for 100 subsystems
- [ ] Integration tests verify tree formatting

---

### Phase 3: Decomposability Analysis (Week 3)

**Deliverables:**
- Hierarchical modularity calculation
- Coupling ratio calculation respects hierarchy
- Boundary violation detection with hierarchy awareness
- `jigy decompose metrics --subsystem` for subtree analysis

**Files to Modify:**
- `src/jig/decompose/metrics.py` - Update for hierarchical metrics
- `src/jig/decompose/analyzer.py` - Update boundary violation logic
- `src/jig/cli/decompose.py` - Add `--subsystem` option to commands
- `tests/unit/test_decompose_metrics.py` - Add nested subsystem tests

**Acceptance Criteria:**
- [ ] Modularity calculation works for nested subsystems
- [ ] Coupling ratio aggregates child subsystem metrics
- [ ] Boundary violations respect hierarchy (edges within parent OK)
- [ ] Coupling ratio excludes constraint relationships (preserves decomposability)
- [ ] `jigy decompose metrics --subsystem crdt` analyzes subtree
- [ ] `jigy decompose report` includes hierarchical breakdown and constraint compliance
- [ ] Constraint compliance metrics shown per subsystem
- [ ] Performance: metrics calculation <5s for 100 subsystems
- [ ] Unit tests verify hierarchical metric calculations

---

### Phase 4: Documentation & Migration (Week 4)

**Deliverables:**
- User guide for nested subsystems
- Migration guide from flat to nested
- Updated architecture documentation
- Example project with nested subsystems
- Tutorial walkthrough

**Files to Create/Modify:**
- `docs/user-guide/NESTED_SUBSYSTEMS.md` - Complete guide
- `docs/user-guide/MIGRATION_NESTED.md` - Migration guide
- `docs/architecture/GRAPH_SUBSYSTEM.md` - Update with nesting
- `docs/tutorials/NESTED_SUBSYSTEMS_TUTORIAL.md` - Example walkthrough
- `README.md` - Update with nested subsystem examples

**Acceptance Criteria:**
- [ ] User guide explains nested subsystem concepts
- [ ] Migration guide provides step-by-step instructions
- [ ] Tutorial includes 3-level nesting example
- [ ] Architecture docs explain design decisions
- [ ] All examples tested and working
- [ ] README updated with nested subsystem example

---

## Part 5: Testing Strategy

### Unit Tests

**Test Coverage Requirements:**
- Subsystem nesting (3+ levels)
- Path resolution (`crdt.ser.internal`)
- Recursive node collection
- Cycle detection in hierarchy
- Validation of nested structures

**Key Test Cases:**
```python
def test_nested_subsystem_loading():
    """Verify Graph loads nested subsystems from YAML."""

def test_subsystem_path_resolution():
    """Verify get_subsystem_by_path() navigates hierarchy."""

def test_recursive_node_collection():
    """Verify get_all_nodes(recursive=True) includes children."""

def test_cycle_detection():
    """Verify validation detects cycles in subsystem hierarchy."""

def test_parent_with_nodes_validation():
    """Verify validation prevents nodes in parent subsystems."""

def test_hierarchical_modularity():
    """Verify modularity calculation for nested subsystems."""

def test_hierarchical_coupling_ratio():
    """Verify coupling ratio aggregates child metrics."""

def test_constraint_exclusion_from_coupling():
    """Verify constraint relationships not counted in coupling metrics (v7)."""
```

### Integration Tests

**Test Coverage Requirements:**
- Status command with nested subsystems
- Graph list with recursive queries
- Decompose metrics with subtree analysis
- Validation of nested structures
- Backward compatibility with flat subsystems

**Key Test Cases:**
```python
def test_status_hierarchical_view():
    """Verify status displays tree view for nested subsystems."""

def test_status_flat_view():
    """Verify --flat option shows flattened view."""

def test_graph_list_recursive():
    """Verify list --subsystem includes child nodes."""

def test_decompose_metrics_subtree():
    """Verify metrics --subsystem analyzes subtree only."""

def test_backward_compatibility_flat():
    """Verify flat subsystems still work unchanged."""

def test_constraint_scope_nested_subsystems():
    """Verify constraint scopes work with nested subsystem paths (v7)."""

def test_constraint_recursive_matching():
    """Verify recursive constraint scopes match all child subsystems (v7)."""
```

### Performance Tests

**Benchmarks:**
- Load 100 nested subsystems (3 levels): <100ms
- Query subsystem by path (100 subsystems): <10ms
- Recursive node collection (100 subsystems): <50ms
- Hierarchical metrics calculation (100 subsystems): <5s

---

## Part 6: Migration Strategy

### Backward Compatibility

**Guarantees:**
1. Existing flat subsystems work unchanged
2. No breaking changes to YAML formats
3. All existing commands work with flat subsystems
4. Default behavior shows flattened view (opt-in to hierarchical)

**Deprecation Policy:**
- No deprecations required (additive changes only)
- Flat subsystems remain fully supported

### Migration Path

**Step 1: Identify Groupings**
```bash
# Analyze existing subsystems
jigy graph list --subsystem auth
jigy graph list --subsystem user
# Determine if auth and user should be grouped under "identity"
```

**Step 2: Update subsystems.yaml**
```yaml
# Before (flat)
subsystems:
  auth:
    name: auth
  user:
    name: user

# After (nested)
subsystems:
  identity:
    name: identity
    description: "Identity and access management"
    subsystems:
      auth:
        name: auth
      user:
        name: user
```

**Step 3: Update graph-index.yaml**
```yaml
# Before
subsystems:
  auth:
    nodes: [O-AUTH-001, S-AUTH-001]

# After
subsystems:
  identity.auth:
    nodes: [O-AUTH-001, S-AUTH-001]
```

**Step 4: Update Node Frontmatter**
```yaml
# Before
subsystem: auth

# After
subsystem: identity.auth
```

**Step 5: Validate**
```bash
jigy validate --check-all
jigy status --verbose
```

---

## Part 7: Success Criteria

### Functional Success

- [ ] Subsystems can be nested to arbitrary depth
- [ ] Nodes reference subsystems via fully-qualified paths
- [ ] All query commands support hierarchical paths
- [ ] Status command displays hierarchical tree view
- [ ] Decomposability analysis respects hierarchy
- [ ] Validation catches hierarchy errors (cycles, invalid paths)
- [ ] Backward compatibility maintained for flat subsystems

### Performance Success

- [ ] Load 100 nested subsystems in <100ms
- [ ] Query subsystem by path in <10ms
- [ ] Recursive node collection in <50ms
- [ ] Hierarchical metrics calculation in <5s
- [ ] No performance regression for flat subsystems

### Quality Success

- [ ] Test coverage >80% for new code
- [ ] All existing tests pass (or updated appropriately)
- [ ] Type checking passes (mypy strict)
- [ ] Linting passes (ruff)
- [ ] Documentation complete and accurate

### Usability Success

- [ ] Hierarchical view is clear and intuitive
- [ ] Error messages clearly indicate path issues
- [ ] Migration guide enables smooth transition
- [ ] Tutorial demonstrates real-world use case
- [ ] Commands have consistent behavior across flat/nested

---

## Part 8: Risks & Mitigations

### Technical Risks

**Risk 1: Performance Degradation**
- **Impact:** High - Recursive operations could be slow
- **Likelihood:** Medium
- **Mitigation:**
  - Cache subsystem path lookups
  - Benchmark continuously during development
  - Set performance budgets per operation
  - Consider lazy loading for deep hierarchies

**Risk 2: Complexity Explosion**
- **Impact:** Medium - Code becomes harder to maintain
- **Likelihood:** Medium
- **Mitigation:**
  - Keep nesting methods isolated in Subsystem class
  - Maintain clear separation between flat and nested logic
  - Keep constraint integration clean (predicates not graph edges)
  - Comprehensive unit tests for edge cases
  - Code review for complexity

**Risk 3: Backward Compatibility Breakage**
- **Impact:** High - Breaks existing projects
- **Likelihood:** Low
- **Mitigation:**
  - Extensive testing with flat subsystems
  - Default to flat view in commands
  - Clear migration guide
  - Version subsystems.yaml format

### Usability Risks

**Risk 4: Confusing Hierarchical Syntax**
- **Impact:** Medium - Users struggle with path notation
- **Likelihood:** Medium
- **Mitigation:**
  - Clear documentation with examples
  - Helpful error messages for path issues
  - Tutorial with real-world example
  - Consider tab-completion for paths

**Risk 5: Over-Nesting**
- **Impact:** Low - Users create too-deep hierarchies
- **Likelihood:** Low
- **Mitigation:**
  - Document recommended max depth (3-4 levels)
  - Warning for deep nesting (>4 levels)
  - Best practices guide

---

## Part 9: Open Questions

### Design Questions

**Q1: Should parent subsystems be allowed to have nodes?**
- **Current Decision:** No - only leaf subsystems can have nodes
- **Rationale:** Simplifies metrics calculation and prevents ambiguity
- **Alternative:** Allow mixed (nodes + children) but complicate analysis

**Q2: How should modularity be calculated for hierarchies?**
- **Current Decision:** Calculate at each level, aggregate to parent
- **Rationale:** Provides both fine-grained and coarse-grained views
- **Alternative:** Flatten hierarchy for modularity calculation

**Q3: Should subsystem names be globally unique or locally unique?**
- **Current Decision:** Locally unique (within parent)
- **Rationale:** Allows natural naming (e.g., `auth.api`, `user.api`)
- **Alternative:** Globally unique (prevents `api` in multiple places)

**Q4: What's the default view for status command?**
- **Current Decision:** Hierarchical tree view (opt-in to flat with `--flat`)
- **Rationale:** Showcases new feature, more informative
- **Alternative:** Flat view (opt-in to hierarchical with `--tree`)

### Implementation Questions

**Q5: Should we support subsystem references across hierarchy?**
- **Example:** `crdt.ser` depends on `core` (not `core.parser`)
- **Current Decision:** Yes - dependencies can reference any level
- **Rationale:** Flexibility for coarse-grained dependencies

**Q6: Should validation enforce max nesting depth?**
- **Current Decision:** Warning only (not error) for >4 levels
- **Rationale:** Don't artificially limit, but discourage deep nesting

**Q7: How do constraints integrate with nested subsystems? (v7)**
- **Current Decision:** Constraints can target nested paths via scope selectors
- **Rationale:** Constraints are predicates over OSTC graph; nested paths are first-class in queries
- **Example:** `scope: {subsystems: [crdt], recursive: true}` matches all nodes under `crdt` parent

**Q8: Should coupling metrics exclude constraint edges? (v7)**
- **Current Decision:** Yes - constraint relationships are not counted as graph edges
- **Rationale:** Constraints are system properties (predicates), not architectural dependencies
- **Impact:** Preserves decomposability metrics; cross-cutting constraints don't pollute coupling ratios

---

## Part 10: Timeline & Effort

### Estimated Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Data Model & Loading | Week 1 (5 days) | Nested Subsystem dataclass, loading, validation |
| Phase 2: Query & Navigation | Week 2 (5 days) | Status tree view, recursive queries |
| Phase 3: Decomposability | Week 3 (5 days) | Hierarchical metrics, boundary violations |
| Phase 4: Documentation | Week 4 (5 days) | User guide, migration guide, tutorial |
| **Total** | **4 weeks** | **Complete nested subsystem support** |

### Effort Breakdown

**Development:** 60 hours
- Phase 1: 15 hours (data model, loading, validation)
- Phase 2: 15 hours (queries, status, navigation)
- Phase 3: 15 hours (metrics, analysis, violations)
- Phase 4: 15 hours (documentation, migration, tutorial)

**Testing:** 20 hours
- Unit tests: 10 hours
- Integration tests: 8 hours
- Performance tests: 2 hours

**Documentation:** 10 hours
- User guide: 4 hours
- Migration guide: 3 hours
- Tutorial: 3 hours

**Total Effort:** 90 hours (≈2.25 weeks full-time, 4 weeks part-time)

---

## Part 11: Deliverables Checklist

### Code Deliverables

- [ ] `src/jig/core/graph.py` - Updated Subsystem and Graph classes
- [ ] `src/jig/core/validator.py` - Nested subsystem validation
- [ ] `src/jig/cli/status.py` - Hierarchical tree view
- [ ] `src/jig/cli/graph.py` - Recursive subsystem queries
- [ ] `src/jig/decompose/metrics.py` - Hierarchical metrics
- [ ] `src/jig/decompose/analyzer.py` - Hierarchical boundary violations
- [ ] Unit tests for all new functionality
- [ ] Integration tests for commands
- [ ] Performance benchmarks

### Documentation Deliverables

- [ ] `docs/user-guide/NESTED_SUBSYSTEMS.md` - User guide
- [ ] `docs/user-guide/MIGRATION_NESTED.md` - Migration guide
- [ ] `docs/tutorials/NESTED_SUBSYSTEMS_TUTORIAL.md` - Tutorial
- [ ] `docs/architecture/GRAPH_SUBSYSTEM.md` - Updated architecture
- [ ] `README.md` - Updated with nested examples
- [ ] `CHANGELOG.md` - Version entry

### Quality Deliverables

- [ ] Test coverage >80%
- [ ] All tests passing
- [ ] Type checking clean (mypy)
- [ ] Linting clean (ruff)
- [ ] Performance benchmarks met
- [ ] Backward compatibility verified

---

## Part 12: Future Enhancements

### Post-MVP Features

**Feature 1: Subsystem Visualization**
- Generate hierarchical diagrams (graphviz)
- Interactive web-based subsystem explorer
- Export to various formats (SVG, PNG, PDF)

**Feature 2: Subsystem Templates**
- Template for common subsystem patterns
- Quick creation of nested subsystem structures
- Best practices baked into templates

**Feature 3: Subsystem Refactoring**
- Command to move nodes between subsystems
- Automatic update of frontmatter and graph-index
- Validation of refactoring impact

**Feature 4: Subsystem Metrics History**
- Track modularity and coupling over time
- Detect regressions in subsystem boundaries
- Generate trend reports

**Feature 5: Cross-Subsystem Analysis**
- Identify subsystems that should be merged
- Detect subsystems that should be split
- Recommend hierarchy restructuring

**Feature 6: Constraint-Aware Subsystem Recommendations (v7)**
- Suggest subsystem groupings based on shared constraints
- Identify missing constraint coverage in subsystems
- Recommend constraint scope refinements based on actual hierarchy
- Visualize constraint overlay on subsystem hierarchy

---

## Conclusion

This scope of work defines a comprehensive approach to implementing nested subsystems in JIG v7. The design maintains backward compatibility while enabling hierarchical organization for complex systems. The nested subsystem feature integrates seamlessly with the OSTCX model, where constraints act as predicates over the hierarchical OSTC Intent Graph. The phased implementation plan ensures incremental delivery of value, and the testing strategy ensures quality and performance.

**Key Success Factors:**
1. Maintain backward compatibility throughout (flat subsystems continue to work)
2. Keep performance within targets (<100ms for most operations)
3. Integrate cleanly with constraint system (v7) without polluting metrics
4. Provide clear documentation and migration path
5. Test extensively with both flat and nested structures
6. Ensure constraint queries work naturally with nested paths
7. Dogfood on JIG's own codebase (if it grows to need nesting)

**Next Steps:**
1. Review and approve this scope document
2. Create OSTC nodes for nested subsystem feature
3. Ensure constraint system (Phase 4 of v7) is complete or near-complete
4. Begin Phase 1 implementation (Data Model & Loading)
5. Coordinate with constraint validation during Phase 2-3
6. Iterate based on feedback and discoveries

---

**Document Version:** 1.1  
**Last Updated:** 2025-11-20  
**Status:** Draft (Ready for Review)  
**Approver:** [To be assigned]  
**JIG Version:** v7 (OSTCX model with constraints and nested subsystems)

