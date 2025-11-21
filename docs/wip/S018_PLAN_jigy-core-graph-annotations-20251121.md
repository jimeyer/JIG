---
delta_type: plan
branch: orphaned-node-fixer
created: 2025-11-21
prompt: |
  build a PLAN to implement:
  Week 1: Core plumbing → read all artifacts
  Week 2: Graph navigation → explore relationships
  Week 4-5: Annotations → verify C/T linkage
  exclude(will do later): Week 3: Decomposability → measure coupling, Week 6-8: Deltas & harvest → capture future work
---

# PLAN: jigy v0.2-0.5 - Core Graph & Annotations

- **SCOPE:** S017_ANALYSIS_jig-alignment-gap-20251121.md (Part 3: Tool Enhancement Roadmap)
- **Start:** 2025-11-21
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** jigy-tool
- **Context:** Updating jigy v0.1.0 to support JIG v6.1 spec for ASE-A project

## Known Intent (Reference Existing)

This PLAN implements phases from the analysis document to make jigy tool read and interpret ASE-A's JIG artifacts.

**Related Analysis:**
- docs/wip/S017_ANALYSIS_jig-alignment-gap-20251121.md (comprehensive gap analysis)
- docs/wip/S016_jigy-tool-analysis-20251121.md (original investigation)
- docs/jig-concept/JIG-Concept-v6.1.md (target specification)

**Target Capabilities:**
- Read frontmatter relationships from O/S markdown files
- Load graph-index.yaml for complete node registry (including C/T nodes)
- Count and validate edges
- Navigate graph (queries, traces, paths)
- Discover @jig annotations in code/tests
- Rebuild graph-index from sources

**Out of Scope (Future Work):**
- Decomposability analysis (coupling metrics, modularity)
- Delta management and harvest pipeline
- LLM synthesis features

## Work Unit Checklist

### Phase 1: Core Plumbing (jigy v0.2.0)
- [ ] WU1: Parse frontmatter relationships — tests ☐ / docs ☐ / reflect ☐
- [ ] WU2: Load graph-index.yaml — tests ☐ / docs ☐ / reflect ☐
- [ ] WU3: Unified node registry — tests ☐ / docs ☐ / reflect ☐
- [ ] WU4: Edge validation & orphan detection — tests ☐ / docs ☐ / reflect ☐

### Phase 2: Graph Navigation (jigy v0.3.0)
- [ ] WU5: Graph data structure & queries — tests ☐ / docs ☐ / reflect ☐
- [ ] WU6: Path finding & traversal — tests ☐ / docs ☐ / reflect ☐
- [ ] WU7: Subsystem queries — tests ☐ / docs ☐ / reflect ☐

### Phase 3: Annotations (jigy v0.5.0)
- [ ] WU8: Fast code scanner for @jig annotations — tests ☐ / docs ☐ / reflect ☐
- [ ] WU9: Index rebuild from sources — tests ☐ / docs ☐ / reflect ☐
- [ ] WU10: Annotation validation — tests ☐ / docs ☐ / reflect ☐

### Integration & Polish
- [ ] WU11: ASE-A validation & fixes — tests ☐ / docs ☐ / reflect ☐
- [ ] WU12: Documentation & examples — tests ☐ / docs ☐ / reflect ☐

---

## Work Units

### Work Unit 1: Parse Frontmatter Relationships

**Goal:** Extract relationship fields (implements, satisfies, verifies, depends_on) from markdown frontmatter and build edge list

**Planned Effort:** 90m

**Acceptance Criteria:**
- PyYAML parses frontmatter from O/S markdown files
- Extracts `implements:`, `satisfies:`, `verifies:`, `depends_on:` fields
- Builds edge list from relationship fields
- Handles both single values (`implements: O-001`) and lists (`implements: [O-001, O-002]`)
- `jigy status` reports accurate edge count (not 0)

**Implementation Notes:**
- Current code location: Likely in markdown parser module
- Add YAML frontmatter extraction to existing node discovery
- Store relationships on node objects
- Build edges list: `{source: node_id, target: ref, type: rel_type}`
- Map frontmatter fields to edge types:
  - `implements:` → `implements` edge
  - `satisfies:` → `satisfies` edge  
  - `verifies:` → `verifies` edge
  - `depends_on:` → `depends_on` edge

**Test Plan:**
- Unit: Test frontmatter parsing with various formats
- Unit: Test edge list building from relationships
- Integration: Run against ASE-A jig/outcomes/ and jig/specifications/
- Integration: Verify edge count matches expected (~113 edges from graph.json)

**Docs to Update:**
- README: Update capabilities section
- CHANGELOG: Add v0.2.0 section with relationship parsing

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy status
  # Should show: ✓ 65 nodes, ~113 edges, 7 subsystems (not 0 edges)
  ```
- Look for: Accurate edge count, no parsing errors

---

### Work Unit 2: Load graph-index.yaml

**Goal:** Read graph-index.yaml as primary node registry to discover C/T nodes

**Planned Effort:** 90m

**Acceptance Criteria:**
- YAML loader reads `jig/graph-index.yaml`
- Discovers all node types (O, S, C, T) from graph-index
- Node registry includes all 126 nodes (not just 65)
- Handles both node-centric format (relationships on nodes) and edge-centric format (separate edges section)
- Merges with markdown-discovered O/S nodes (markdown takes precedence for O/S)

**Implementation Notes:**
- Add graph-index.yaml loader module
- Parse nodes section into node objects
- Handle two relationship formats:
  - Node-centric: `implements: [O-001]` on nodes → build edges from this
  - Edge-centric: separate `edges: [{from, to, type}]` section → use directly
- Merge strategy:
  - graph-index.yaml provides C/T nodes
  - Markdown files provide canonical O/S content
  - Relationships come from both sources (union of edges)

**Test Plan:**
- Unit: Test YAML loading with sample graph-index.yaml
- Unit: Test node-centric relationship extraction
- Unit: Test edge-centric relationship extraction
- Unit: Test merge logic (markdown + graph-index)
- Integration: Load ASE-A graph-index.yaml (126 nodes)

**Docs to Update:**
- README: Document graph-index.yaml support
- Architecture notes: Explain merge strategy

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy status
  # Should show: ✓ 126 nodes (18 O, 47 S, 24 C, 37 T), ~113 edges, 7 subsystems
  ```
- Look for: All node types discovered, C/T nodes present

---

### Work Unit 3: Unified Node Registry

**Goal:** Create unified node lookup and query interface for all OSTC types

**Planned Effort:** 60m

**Acceptance Criteria:**
- Single NodeRegistry class manages all nodes
- Efficient lookup by node ID (O(1) hash lookup)
- Query methods: `get_node(id)`, `get_nodes_by_type(type)`, `get_nodes_by_subsystem(subsystem)`
- Edge registry with: `get_edges_from(node_id)`, `get_edges_to(node_id)`, `get_all_edges()`
- Load subsystems.yaml into registry
- Thread-safe (if needed for future parallelism)

**Implementation Notes:**
- Create NodeRegistry class
- Internal data structures:
  - `_nodes: Dict[str, Node]` - ID → Node
  - `_edges: List[Edge]` - all edges
  - `_edges_from: Dict[str, List[Edge]]` - source → edges
  - `_edges_to: Dict[str, List[Edge]]` - target → edges
  - `_subsystems: Dict[str, Subsystem]` - name → subsystem
- Load sequence:
  1. Load subsystems.yaml
  2. Load markdown O/S files
  3. Load graph-index.yaml (merge C/T, add edges)
  4. Build edge indices

**Test Plan:**
- Unit: Test node registration and lookup
- Unit: Test edge queries (from, to, all)
- Unit: Test subsystem queries
- Integration: Load full ASE-A graph, verify query performance

**Docs to Update:**
- Architecture: Document NodeRegistry design

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy validate
  # Should complete in <1 second
  jigy status
  # Should show subsystem breakdown
  ```
- Look for: Fast queries, accurate subsystem assignment

---

### Work Unit 4: Edge Validation & Orphan Detection

**Goal:** Validate all edges point to existing nodes, detect orphans and broken references

**Planned Effort:** 90m

**Acceptance Criteria:**
- Edge validator checks:
  - Target node exists in registry
  - Edge type is valid for source/target node types
  - No self-loops (unless explicitly allowed)
- Orphan detection identifies nodes with no edges (in or out)
- `jigy validate` reports:
  - Missing target warnings (broken references)
  - Invalid edge type warnings
  - Orphaned nodes list
- Exit code 0 if valid, 1 if errors found

**Implementation Notes:**
- Edge validation rules (type compatibility):
  - `implements`: S→O or C→S allowed
  - `satisfies`: S→O allowed
  - `verifies`: T→S or T→O allowed
  - `depends_on`: Any→Any (generic dependency)
- Orphan detection:
  - Node with degree 0 (no incoming or outgoing edges)
  - Special case: Root outcomes (O nodes with no outgoing implements) are not orphans
- Warning vs Error:
  - ERROR: Target doesn't exist (broken reference)
  - ERROR: Invalid edge type for node types
  - WARNING: Orphaned node (may be expected for new nodes)

**Test Plan:**
- Unit: Test edge validation rules
- Unit: Test orphan detection logic
- Unit: Test error reporting
- Integration: Run against ASE-A (should find any issues)
- Regression: Create test fixtures with known issues

**Docs to Update:**
- README: Document validation rules
- User guide: Explain warnings vs errors

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy validate --check-all
  # Should report any broken references or orphans
  ```
- Look for: Clear error messages, helpful warnings

**Milestone: jigy v0.2.0 Complete**
- Reads all ASE-A artifacts
- Reports accurate node/edge counts
- Validates relationships
- Detects issues

---

### Work Unit 5: Graph Data Structure & Queries

**Goal:** Build graph representation and implement basic query commands

**Planned Effort:** 120m

**Acceptance Criteria:**
- Graph built from NodeRegistry (nodes + edges)
- Commands implemented:
  - `jigy node <id>` - show node details, relationships
  - `jigy edges <id>` - show all edges for node (incoming + outgoing)
  - `jigy list <type>` - list all nodes of type (O/S/T/C)
- Output formats: human-readable text (default), JSON (--json), YAML (--yaml)
- Performance: <100ms for queries on 1000-node graph

**Implementation Notes:**
- Use NetworkX for graph representation (mature, well-tested)
- Alternative: Custom graph class (lighter weight, more control)
- Node command output format:
  ```
  S-AIR-001: BikeState messages use operation_type field directly
  Type: specification
  Subsystem: airspace
  Status: active
  File: jig/specifications/S-AIR-001.md
  
  Implements:
    → O-AIR-001: Track bike states across multiple devices
    → O-AIR-002: BikeState changes propagate within 100ms
  
  Implemented by:
    ← C-AIR-003: BikeState class in airspace/bike_state.py
  
  Verified by:
    ← T-AIR-005: test_bike_state_operation_type
  ```

**Test Plan:**
- Unit: Test graph construction from node registry
- Unit: Test query functions
- Unit: Test output formatting (text, JSON, YAML)
- Integration: Run against ASE-A, verify output correctness
- Performance: Benchmark queries on large graphs

**Docs to Update:**
- README: Add query commands section
- User guide: Add examples of graph queries

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy node S-AIR-001
  # Should show full node details with relationships
  jigy edges S-AIR-001
  # Should list all edges
  jigy list specification --subsystem airspace
  # Should filter by subsystem
  ```
- Look for: Clear, useful output; accurate relationship display

---

### Work Unit 6: Path Finding & Traversal

**Goal:** Implement graph traversal queries (trace, path, dependencies)

**Planned Effort:** 120m

**Acceptance Criteria:**
- Commands implemented:
  - `jigy trace <id> [--depth N]` - traverse graph from node (default depth=2)
  - `jigy path <from> <to>` - find shortest path between nodes
  - `jigy deps <id> [--reverse]` - show dependencies (or dependents if --reverse)
- Trace output shows tree structure with indentation
- Path output shows sequence of nodes with edge types
- Performance: <500ms for complex traces on ASE-A graph

**Implementation Notes:**
- Use NetworkX algorithms:
  - `nx.bfs_tree()` for trace
  - `nx.shortest_path()` for path finding
  - `nx.descendants()` for dependencies
- Trace output format:
  ```
  O-AIR-001: Track bike states across multiple devices
  ├─ implements → S-AIR-001: BikeState messages use operation_type
  │  ├─ implements → C-AIR-003: BikeState class
  │  └─ verifies → T-AIR-005: test_bike_state_operation_type
  └─ implements → S-AIR-002: BikeState includes device_id
  ```
- Handle cycles gracefully (mark visited nodes)

**Test Plan:**
- Unit: Test BFS traversal with depth limit
- Unit: Test path finding (shortest path)
- Unit: Test cycle detection
- Integration: Trace from O nodes in ASE-A
- Edge case: Disconnected subgraphs

**Docs to Update:**
- User guide: Add traversal examples
- README: Update query capabilities

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy trace O-AIR-001 --depth 3
  # Should show tree of all related nodes
  jigy path O-PS-001 C-PS-005
  # Should find path through specifications
  ```
- Look for: Accurate traversal, clear visualization

---

### Work Unit 7: Subsystem Queries

**Goal:** Enable subsystem-level queries and cross-subsystem edge detection

**Planned Effort:** 90m

**Acceptance Criteria:**
- Commands implemented:
  - `jigy subsystem <name>` - show subsystem details and nodes
  - `jigy subsystem <name> --edges` - show internal vs external edges
  - `jigy subsystems` - list all subsystems with node counts
- External edges identified (edges crossing subsystem boundaries)
- Output includes:
  - Node counts by type
  - Internal edge count
  - External edges list (shows cross-subsystem dependencies)

**Implementation Notes:**
- Load subsystems.yaml
- Assign nodes to subsystems (from node.subsystem field)
- Edge classification:
  - Internal: source.subsystem == target.subsystem
  - External: source.subsystem != target.subsystem
- Subsystem detail output:
  ```
  Subsystem: airspace
  Description: Airspace subsystem
  
  Nodes: 33
    Outcomes: 10
    Specifications: 12
    Code: 6
    Tests: 5
  
  Internal edges: 28
  External edges: 5
    → protocol: 3 edges
    → gateway: 2 edges
  ```

**Test Plan:**
- Unit: Test subsystem assignment
- Unit: Test internal/external edge classification
- Integration: Run against ASE-A subsystems
- Validate: External edges make architectural sense

**Docs to Update:**
- User guide: Add subsystem query examples
- README: Update subsystem support section

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy subsystems
  # Should list all 7 subsystems
  jigy subsystem airspace --edges
  # Should show internal/external breakdown
  ```
- Look for: Accurate classification, useful architectural insight

**Milestone: jigy v0.3.0 Complete**
- Graph exploration working
- Query and traversal commands functional
- Subsystem analysis available

---

### Work Unit 8: Fast Code Scanner for @jig Annotations

**Goal:** Scan source/test files to discover @jig annotations and extract metadata

**Planned Effort:** 120m

**Acceptance Criteria:**
- Fast scanner (ripgrep-based or Python equivalent) finds `@jig` annotations
- Regex pattern: `@jig\s+([A-Z]-[A-Z]+-\d+)\s+(.*)`
- Extracts from annotation:
  - Node ID (C-XXX-NNN or T-XXX-NNN)
  - Relationships (implements:, verifies:, depends:)
  - Metadata (subsystem:, interface:)
  - File path + line number
- Scans src/ and test/ directories (configurable paths)
- Performance: <2 seconds for 10,000 files

**Implementation Notes:**
- Option 1: Use subprocess to call `rg` (ripgrep) - fastest
- Option 2: Use Python `pathlib` + `re` - pure Python, portable
- Annotation format (from JIG v6.1 spec):
  ```python
  # @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth interface:public
  class JWTAuthenticator:
  
  # @jig T-AUTH-001 verifies:S-AUTH-001 subsystem:auth
  def test_jwt_validation():
  ```
- Parse metadata:
  - Split on whitespace
  - Extract key:value pairs
  - Handle multiple relationships: `implements:S-001,S-002`
- Return list of discovered nodes with:
  - id, type (code/test), file, line, relationships, metadata

**Test Plan:**
- Unit: Test annotation regex parsing
- Unit: Test metadata extraction
- Unit: Test file scanning
- Integration: Scan ASE-A codebase (verify against code_index.json)
- Performance: Benchmark large codebases

**Docs to Update:**
- README: Document annotation discovery
- User guide: Explain annotation format

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy scan --dry-run
  # Should discover C/T nodes from @jig annotations
  # Compare count with existing code_index.json/test_index.json
  ```
- Look for: Accurate discovery, no false positives/negatives

---

### Work Unit 9: Index Rebuild from Sources

**Goal:** Regenerate graph-index.yaml from markdown frontmatter + code annotations

**Planned Effort:** 120m

**Acceptance Criteria:**
- Command: `jigy index --rebuild` regenerates graph-index.yaml
- Source of truth:
  - O/S nodes: Markdown frontmatter (jig/outcomes/, jig/specifications/)
  - C/T nodes: @jig annotations in code/tests
  - Edges: Relationships from both sources (union)
- Generated graph-index.yaml includes:
  - All nodes with: id, type, title, subsystem, status, file, (line for C/T)
  - Node-centric relationships (implements, verifies, etc. on nodes)
- Warns on conflicts (e.g., same ID in multiple files)
- Validates generated index before writing

**Implementation Notes:**
- Rebuild sequence:
  1. Scan markdown files for O/S nodes
  2. Scan code/tests for C/T annotations
  3. Extract all relationships
  4. Build unified node list
  5. Detect conflicts (duplicate IDs)
  6. Validate graph structure
  7. Generate YAML in node-centric format
  8. Write to graph-index.yaml
- Backup existing graph-index.yaml before overwriting
- Format: Use node-centric (relationships on nodes) as default
- Include metadata: generation timestamp, source files

**Test Plan:**
- Unit: Test YAML generation
- Unit: Test conflict detection
- Integration: Rebuild ASE-A graph-index.yaml
- Validation: Compare rebuilt vs existing (should be equivalent)
- Regression: Ensure rebuild is idempotent (rebuild twice = same output)

**Docs to Update:**
- README: Document index rebuild workflow
- User guide: Explain when to rebuild

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy index --rebuild --dry-run
  # Should show what would be generated
  jigy index --rebuild
  # Should regenerate graph-index.yaml
  jigy validate
  # Should pass validation
  ```
- Look for: Valid YAML, no data loss, equivalent to hand-maintained

---

### Work Unit 10: Annotation Validation

**Goal:** Validate @jig annotations match Intent nodes and are properly formatted

**Planned Effort:** 90m

**Acceptance Criteria:**
- Command: `jigy validate --check-annotations` validates annotations
- Checks performed:
  - All @jig node IDs exist in Intent graph (O/S nodes)
  - Relationship targets exist (implements:S-001 → S-001 must exist)
  - Annotation format is valid (regex match)
  - Subsystem assignments match graph-index.yaml
  - No duplicate annotations (same ID in multiple locations)
- Reports:
  - Broken references (annotation points to non-existent node)
  - Orphaned Intent nodes (O/S without C/T implementations)
  - Format errors (malformed annotations)

**Implementation Notes:**
- Validation checks:
  ```python
  for annotation in discovered_annotations:
      # Check node ID format
      assert re.match(r'[A-Z]-[A-Z]+-\d+', annotation.id)
      
      # Check relationships target existing nodes
      for rel_type, targets in annotation.relationships.items():
          for target in targets:
              assert target in node_registry
              assert valid_edge_type(annotation.type, rel_type, node_registry[target].type)
      
      # Check no duplicate IDs
      assert annotation.id not in seen_annotations
  ```
- Warnings for common issues:
  - C/T node in annotation but not in graph-index.yaml (suggest rebuild)
  - Subsystem mismatch (annotation vs graph-index.yaml)

**Test Plan:**
- Unit: Test validation rules
- Unit: Test error reporting
- Integration: Run against ASE-A (find any issues)
- Create test fixtures with known annotation errors

**Docs to Update:**
- README: Document annotation validation
- User guide: Common validation errors and fixes

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy validate --check-annotations
  # Should report any annotation issues
  ```
- Look for: Clear error messages, helpful suggestions

**Milestone: jigy v0.5.0 Complete**
- Annotation discovery working
- Index rebuild from sources
- Full validation pipeline

---

### Work Unit 11: ASE-A Validation & Fixes

**Goal:** Run jigy v0.5.0 against ASE-A project and fix any discovered issues

**Planned Effort:** 120m

**Acceptance Criteria:**
- `jigy status` shows accurate graph (126 nodes, ~113 edges, 7 subsystems)
- `jigy validate --check-all` passes with no errors
- `jigy validate --check-annotations` verifies all C/T annotations
- Any ASE-A artifact issues identified and fixed:
  - Missing file references in graph-index.yaml
  - Broken edge references
  - Subsystem naming inconsistencies
  - Missing @jig annotations (if needed)

**Implementation Notes:**
- Run full validation suite on ASE-A
- Document any issues found:
  - graph-index.yaml format issues
  - Missing annotations in code/tests
  - Subsystem naming (protocol vs protocol-stack, mps vs multi_plane_server)
- Create fixes in ASE-A repo:
  - Add missing file: fields to graph-index.yaml
  - Standardize subsystem names
  - Add @jig annotations if missing (based on code_index.json/test_index.json)
- Verify edge type terminology (validates vs verifies)

**Test Plan:**
- Integration: Full jigy test suite against ASE-A
- Validation: All commands work correctly
- Performance: Commands complete in target time (<1 sec for validate)
- Regression: Re-run after fixes to confirm resolution

**Docs to Update:**
- S017 analysis: Add "Implementation Results" section
- ASE-A jig/README.md: Update with jigy v0.5.0 usage

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy status
  jigy validate --check-all
  jigy node O-AIR-001
  jigy trace O-PS-001 --depth 2
  jigy subsystem airspace --edges
  ```
- Look for: All commands work, accurate output, no errors

---

### Work Unit 12: Documentation & Examples

**Goal:** Complete user documentation and create example usage

**Planned Effort:** 90m

**Acceptance Criteria:**
- README.md updated with:
  - Installation instructions
  - Quick start guide
  - All commands documented
  - Examples for common workflows
- User guide created:
  - Graph querying patterns
  - Validation workflow
  - Annotation best practices
  - Troubleshooting common issues
- CHANGELOG.md updated:
  - v0.2.0: Core plumbing
  - v0.3.0: Graph navigation
  - v0.5.0: Annotations
- Example project or tutorial

**Implementation Notes:**
- Documentation structure:
  - README.md: Quick start, command reference
  - docs/user-guide.md: Detailed usage
  - docs/architecture.md: Design decisions
  - CHANGELOG.md: Version history
- Examples to include:
  - Basic graph queries
  - Finding implementation chains (O→S→C→T)
  - Subsystem analysis
  - Validation workflow
  - Index rebuild
- Screenshots or ASCII art for complex outputs

**Test Plan:**
- Review: Have fresh eyes read docs (test clarity)
- Validation: Run all documented examples
- Completeness: Check all commands documented

**Docs to Update:**
- README.md
- docs/user-guide.md (new)
- CHANGELOG.md
- docs/architecture.md (optional)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: Follow quick start guide from scratch
- Look for: Clear instructions, no missing steps

**Milestone: jigy v0.5.0 Released**
- Full documentation
- ASE-A validated
- Ready for production use

---

## Summary (To Be Filled On Completion)

### Scope Delivered
- [To be filled after completion]

### Key Decisions
- [To be filled during execution]

### Deltas from SCOPE
- [To be filled during execution]

### Metrics
- Units: 12
- Estimated total effort: ~21 hours
- Target velocity: 2-3 units per day
- Expected duration: 5-7 days intensive work

### Reflection Roll-up
- [To be filled after completion]

### Next Steps
After this PLAN completes, jigy v0.5.0 will support:
- ✅ Reading all JIG v6.1 artifacts
- ✅ Graph navigation and queries
- ✅ Annotation discovery and validation
- ✅ ASE-A full compatibility

**Future work (deferred):**
- Week 3: Decomposability analysis (coupling metrics, modularity)
- Week 6-8: Delta management and harvest pipeline
- LLM synthesis features

---

**Status:** Draft (ready to begin)  
**Next Action:** Review PLAN, adjust if needed, begin Work Unit 1

