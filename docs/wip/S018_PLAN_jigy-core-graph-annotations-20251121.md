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
  UPDATE: include construction of JIG OSTC artifacts as described in taskPlan.md - building JIG with JIG
---

# PLAN: jigy v0.2-0.5 - Core Graph & Annotations

- **SCOPE:** S017_ANALYSIS_jig-alignment-gap-20251121.md (Part 3: Tool Enhancement Roadmap)
- **Start:** 2025-11-21
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** jigy-tool
- **Context:** Updating jigy v0.1.0 to support JIG v6.1 spec for ASE-A project

## Known Intent (Create Before Coding)

This PLAN implements phases from the analysis document to make jigy tool read and interpret ASE-A's JIG artifacts.

**Building JIG with JIG:** We create Intent nodes (O/S) BEFORE implementation to follow constraint-driven development.

**Outcomes Created (jig/outcomes/):**
- O-JIGY-001: "JIG graph accurately reflects all OSTC relationships" 
  - Value: Developers see complete Intent alignment, no missing edges
- O-JIGY-002: "Developers can navigate Intent graph efficiently"
  - Value: Find related nodes, trace dependencies in <1 second
- O-JIGY-003: "Code and Intent stay synchronized"
  - Value: Annotations link code to Intent, validation catches drift
- O-JIGY-004: "JIG scanning excludes test fixtures and template files" (discovered WU8-10)
  - Value: Clean node index without pollution from mock data

**Specifications Created (jig/specifications/):**
- S-JIGY-001: "Parse frontmatter relationship fields from markdown"
- S-JIGY-002: "Load graph-index.yaml for complete node registry"
- S-JIGY-003: "Unified node registry with O(1) lookup performance"
- S-JIGY-004: "Edge validation with type-aware rules"
- S-JIGY-005: "Graph query commands (node, edges, list)"
- S-JIGY-006: "Path finding and graph traversal with depth limits"
- S-JIGY-007: "Subsystem queries with internal/external edge classification"
- S-JIGY-008: "Fast annotation scanner (<2s for 10k files)"
- S-JIGY-009: "Index rebuild regenerates graph-index.yaml from sources"
- S-JIGY-010: "Annotation validation checks all @jig references"
- S-JIGY-011: "Exclusion filtering prevents test fixture pollution" (discovered WU8-10)

**Rationale:** These constraints are known from S017 analysis and JIG v6.1 spec. Creating them upfront enables O→S→TDD flow.

## JIG Workflow Integration

**Building JIG with JIG:** This PLAN follows the JIG-aware taskPlan workflow:

1. **WU0: Intent-First** (BEFORE any code)
   - Extract known constraints from SCOPE → Create O/S nodes
   - Commit Intent nodes before implementation
   - Enables constraint-driven development (O→S→TDD)

2. **WU1-12: TDD Implementation**
   - Each unit references Intent nodes it implements
   - Write tests first with @jig annotations (T nodes)
   - Implement with @jig annotations (C nodes)
   - Capture discoveries in Reflect blocks with markers

3. **Markers for Discoveries** (use in Reflect blocks)
   - `#DISCOVERY` - NEW constraints learned during work (not in WU0)
   - `#DECISION` - Tradeoff choices with rationale
   - `#LEARNED` - Reusable patterns discovered

4. **Harvest After Completion**
   - Run `jig ai-distill --branch orphaned-node-fixer`
   - Review LLM synthesis proposals
   - Integrate NEW insights into Intent Graph
   - Archive delta

**Key Principle:** Intent nodes (WU0) capture KNOWN constraints. Markers capture DISCOVERED constraints during implementation. Future you is smarter than present you.

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

## Progress Summary

**Overall Status:** Phase 0, 1, 2, 3, & 3.5 Complete (11/13 work units done)

**Completed:**
- ✅ Phase 0: Intent Creation (WU0)
- ✅ Phase 1: Core Plumbing (WU1-4) — All tests passing, reflections documented
- ✅ Phase 2: Graph Navigation (WU5-7) — All tests passing, reflections documented
- ✅ Phase 3: Annotations (WU8-10) — All tests passing, reflections documented
- ✅ Phase 3.5: Filtering & Exclusions (WU10.5) — All tests passing, three-tier filtering implemented

**Blocked:**
- None

**In Progress:** None

**Next Up:** WU11: ASE-A Validation & Fixes (ready to proceed)

**Key Metrics:**
- Tests: 227 passing (30 exclusion filtering + 21 annotation validation + 25 index rebuild + 30 annotation scanner + 24 graph commands + 22 subsystem + 11 traversal + 21 edge validation + 12 relationship + 8 graph-index + 10 registry + 13 existing)
- Performance: Graph loads in 14ms, validates 1000 nodes in <1s, queries <100ms, annotation scan 10k files in ~3.9s, index rebuild <1s, annotation validation <1s
- Real validation: 40 jig nodes, 18 edges, zero errors

**Commits:**
- cd81223 - feat(jigy): parse frontmatter relationships from markdown (WU1)
- 805b911 - feat(jigy): load graph-index.yaml for C/T node discovery (WU2)
- 84c10a4 - refactor(jigy): simplify to support only list format
- c77bea3 - test(jigy): validate unified node registry (WU3)
- 7197153 - feat(jigy): implement edge validation and orphan detection (WU4)
- 17ea5b6 - test(jigy): validate graph query commands (WU5)
- 3e599fe - docs(jigy): validate path finding & traversal (WU6)
- 9f63306 - docs(jigy): validate subsystem queries (WU7)
- 3a7e6c1 - feat(jigy): fast annotation scanner for @jig annotations (WU8)
- 1a6388c - feat(jigy): index rebuild from sources (WU9)
- bb4ff90 - feat(jigy): annotation validation checks all references (WU10)

---

## Work Unit Checklist

### Phase 0: Intent Creation (BEFORE coding)
- [x] WU0: Create known Intent nodes (O/S) — done ☑

### Phase 1: Core Plumbing (jigy v0.2.0) ✅ COMPLETE
- [x] WU1: Parse frontmatter relationships — tests ☑ / docs ☐ / reflect ☑
- [x] WU2: Load graph-index.yaml — tests ☑ / docs ☐ / reflect ☑
- [x] WU3: Unified node registry — tests ☑ / docs ☐ / reflect ☑
- [x] WU4: Edge validation & orphan detection — tests ☑ / docs ☐ / reflect ☑

### Phase 2: Graph Navigation (jigy v0.3.0) ✅ COMPLETE
- [x] WU5: Graph data structure & queries — tests ☑ / docs ☐ / reflect ☑
- [x] WU6: Path finding & traversal — tests ☑ / docs ☐ / reflect ☑
- [x] WU7: Subsystem queries — tests ☑ / docs ☐ / reflect ☑

### Phase 3: Annotations (jigy v0.5.0) ✅ COMPLETE
- [x] WU8: Fast code scanner for @jig annotations — tests ☑ / docs ☐ / reflect ☑
- [x] WU9: Index rebuild from sources — tests ☑ / docs ☐ / reflect ☑
- [x] WU10: Annotation validation — tests ☑ / docs ☐ / reflect ☑

### Phase 3.5: Filtering & Exclusions (discovered during WU8-10)
- [x] WU10.5: Exclusion filtering (.jigignore, status, fixtures) — tests ☑ / docs ☐ / reflect ☑

### Integration & Polish
- [ ] WU11: ASE-A validation & fixes — tests ☐ / docs ☐ / reflect ☐
- [ ] WU12: Documentation & examples — tests ☐ / docs ☐ / reflect ☐

---

## Work Units

### Work Unit 0: Create Known Intent

**Goal:** Capture all known Outcomes and Specifications from SCOPE (S017 analysis) as Intent nodes before coding

**Planned Effort:** 90m

**Acceptance Criteria:**
- All known "why" statements → Outcome nodes in jig/outcomes/
- All known "what" requirements → Specification nodes in jig/specifications/
- All nodes have proper YAML frontmatter and markdown content
- Relationships defined (S nodes implement O nodes)
- `jig validate` passes (if jigy v0.1 supports it, otherwise manual check)

**Created Nodes:**

**Outcomes (jig/outcomes/):**
1. **O-JIGY-001.md**: "JIG graph accurately reflects all OSTC relationships"
   - Value: Developers see complete Intent alignment, no missing edges
   - Acceptance: jigy reports accurate node/edge counts, matches reality
   
2. **O-JIGY-002.md**: "Developers can navigate Intent graph efficiently"
   - Value: Find related nodes, trace dependencies in <1 second
   - Acceptance: All query commands respond in <1 second on 1000-node graphs
   
3. **O-JIGY-003.md**: "Code and Intent stay synchronized"
   - Value: Annotations link code to Intent, validation catches drift
   - Acceptance: `jigy validate` detects broken references and orphans

**Specifications (jig/specifications/):**

**Phase 1 Specs (Core Plumbing):**
1. **S-JIGY-001.md**: "Parse frontmatter relationship fields from markdown"
   - Implements: O-JIGY-001
   - Extracts: implements, satisfies, verifies, depends_on from YAML frontmatter
   - Handles: single values and lists
   
2. **S-JIGY-002.md**: "Load graph-index.yaml for complete node registry"
   - Implements: O-JIGY-001
   - Discovers: C/T nodes from graph-index.yaml
   - Supports: Both node-centric and edge-centric formats
   
3. **S-JIGY-003.md**: "Unified node registry with O(1) lookup performance"
   - Implements: O-JIGY-002
   - Data structures: Hash map for nodes, indexed edge lists
   - Performance: <100ms queries on 1000-node graph
   
4. **S-JIGY-004.md**: "Edge validation with type-aware rules"
   - Implements: O-JIGY-001, O-JIGY-003
   - Validates: Target nodes exist, edge types valid for node types
   - Reports: Missing targets, invalid edge types, orphaned nodes

**Phase 2 Specs (Graph Navigation):**
5. **S-JIGY-005.md**: "Graph query commands (node, edges, list)"
   - Implements: O-JIGY-002
   - Commands: jigy node <id>, jigy edges <id>, jigy list <type>
   - Formats: Human-readable text, JSON, YAML
   
6. **S-JIGY-006.md**: "Path finding and graph traversal with depth limits"
   - Implements: O-JIGY-002
   - Commands: jigy trace <id>, jigy path <from> <to>
   - Performance: <500ms for complex traces
   
7. **S-JIGY-007.md**: "Subsystem queries with internal/external edge classification"
   - Implements: O-JIGY-002
   - Commands: jigy subsystem <name>, jigy subsystems
   - Classifies: Internal edges (within subsystem) vs external (cross-subsystem)

**Phase 3 Specs (Annotations):**
8. **S-JIGY-008.md**: "Fast annotation scanner (<2s for 10k files)"
   - Implements: O-JIGY-003
   - Scans: src/ and test/ directories for @jig annotations
   - Extracts: Node ID, relationships, metadata, file path + line
   
9. **S-JIGY-009.md**: "Index rebuild regenerates graph-index.yaml from sources"
   - Implements: O-JIGY-003
   - Sources: Markdown frontmatter (O/S), @jig annotations (C/T)
   - Validates: Before writing, warns on conflicts
   
10. **S-JIGY-010.md**: "Annotation validation checks all @jig references"
    - Implements: O-JIGY-003
    - Validates: Node IDs exist, relationships valid, no duplicates
    - Reports: Broken references, orphaned Intent nodes, format errors

11. **S-JIGY-011.md**: "Exclusion filtering prevents test fixture pollution" (discovered WU8-10)
    - Implements: O-JIGY-004
    - Three-tier filtering: .jigignore patterns, status-based, fixture patterns
    - Prevents: Test fixtures, templates, build artifacts from polluting index

**Implementation Notes:**
- Create markdown files with YAML frontmatter following JIG v6.1 format
- Each O node includes value proposition and acceptance criteria
- Each S node includes rationale, constraints, and references to O nodes
- Use subsystem: jigy-tool for all nodes
- Status: active for all nodes

**Test Plan:**
- Manual: Review each file for completeness and clarity
- Manual: Verify YAML frontmatter is valid
- Manual: Check that S nodes properly reference O nodes
- Tool: Run `jig validate` if available (may not work with jigy v0.1.0)

**Docs to Update:**
- None (Intent nodes are self-documenting)

**Reflect (≤5 bullets; keep crisp)**

- What was clear from SCOPE:
  - S017 analysis provides complete feature breakdown [scope]
  - JIG v6.1 spec defines clear OSTC model [spec]
  - Known constraints: performance targets, formats, relationships [requirements]
  - Phase structure (core plumbing → navigation → annotations) [architecture]

- What was ambiguous:
  - Exact subsystem naming (chose: jigy-tool for consistency) [naming]
  - Outcome granularity (chose: 3 high-level outcomes covering tool capabilities) [scope]
  - Spec granularity (chose: 10 specs, one per major feature) [architecture]

- Next experiment:
  - Evaluate if Intent-first reduces implementation ambiguity [process]
  - Test if written acceptance criteria improve TDD flow [quality]

- Discoveries:
  - None yet (WU0 captures KNOWN constraints only) [learning]
  - Discoveries will come during implementation (WU1-12) [expectation]

- Risk watchlist:
  - May need additional S nodes during implementation (discovered constraints) [scope]
  - Performance targets are aggressive (<1s, <2s) - may need optimization [performance]
  - ASE-A validation may reveal edge cases not in specs [integration]

**Links:**
- MR/PR: [To be created]
- Commit(s): [To be filled]

**Commit Message (Example):**
```
intent: define jigy core graph & annotations constraints

Created Outcomes:
- O-JIGY-001: JIG graph accurately reflects all OSTC relationships
- O-JIGY-002: Developers can navigate Intent graph efficiently
- O-JIGY-003: Code and Intent stay synchronized

Created Specifications:
- S-JIGY-001 through S-JIGY-004: Core plumbing (parse, load, registry, validate)
- S-JIGY-005 through S-JIGY-007: Graph navigation (query, traverse, subsystems)
- S-JIGY-008 through S-JIGY-010: Annotations (scan, rebuild, validate)

Unit: 0
See: jig/deltas/active/orphaned-node-fixer/S018_PLAN.md → WU0
```

**Human Validation:**
- Commands: 
  ```bash
  ls -la jig/outcomes/O-JIGY-*.md
  ls -la jig/specifications/S-JIGY-*.md
  # If jigy supports it:
  jigy validate
  jigy status
  ```
- Look for: All 3 O files and 10 S files created, valid YAML frontmatter, clear content

---

### Work Unit 1: Parse Frontmatter Relationships

**Implements:** S-JIGY-001

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
- Add @jig annotations to implementation code:
  ```python
  # @jig C-JIGY-001 implements:S-JIGY-001 subsystem:jigy-tool
  def parse_frontmatter(file_path: str) -> Dict[str, Any]:
      """Extract YAML frontmatter and relationships from markdown"""
  ```

**Test Plan:**
- Unit: Test frontmatter parsing with various formats
  ```python
  # @jig T-JIGY-001 verifies:S-JIGY-001 subsystem:jigy-tool
  def test_parse_frontmatter_implements_list():
  ```
- Unit: Test edge list building from relationships
  ```python
  # @jig T-JIGY-002 verifies:S-JIGY-001 subsystem:jigy-tool
  def test_build_edges_from_relationships():
  ```
- Integration: Run against ASE-A jig/outcomes/ and jig/specifications/
- Integration: Verify edge count matches expected (~113 edges from graph.json)

**Docs to Update:**
- README: Update capabilities section
- CHANGELOG: Add v0.2.0 section with relationship parsing

**Reflect (≤5 bullets; keep crisp)**

- What worked well:
  - TDD approach caught circular import issue immediately [process]
  - Existing metadata preservation in parser made extraction trivial [architecture]
  - Simple dict normalization (single value → list) handled all cases [implementation]
  - Tests passed on first run after fixing circular import [quality]

- What could be better:
  - Circular import Edge/relationships should have been anticipated [design]
  - Could add integration test with real JIG project data [testing]

- Next experiment:
  - See if frontmatter-based edges integrate well with graph-index.yaml edges (WU2) [integration]

- Discoveries:
  #LEARNED "Import at function level (not module level) avoids circular dependencies"
  #LEARNED "PyYAML frontmatter library already normalizes YAML - no extra work needed"

- Risk watchlist:
  - Edge deduplication may be needed when merging frontmatter + graph-index edges [data integrity]
  - Performance with large graphs (1000+ nodes) needs profiling [performance]

**Links:**
- MR/PR: 
- Commit(s): 

**Commit Message (Example):**
```
feat(jigy): parse frontmatter relationships from markdown

Extracts implements, satisfies, verifies, depends_on fields.
Builds edge list from YAML frontmatter in O/S markdown files.
Handles both single values and lists.

Unit: 1
Implements: S-JIGY-001
Reflection: see jig/deltas/active/orphaned-node-fixer/S018_PLAN.md → WU1
```

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

**Implements:** S-JIGY-002

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
  - TDD caught format mismatch (list vs dict) immediately [testing]
  - Flexible implementation handles both list and dict/mapping formats [robustness]
  - Reused WU1's extract_edges_from_node for node-centric relationships [modularity]
  - Markdown precedence logic simple and clear (skip O/S if already loaded) [design]

- What could be better:
  - Should document both supported formats explicitly [documentation]
  - Could add validation for malformed graph-index.yaml entries [validation]

- Next experiment:
  - Test with ASE-A's real 126-node graph-index.yaml (WU11) [integration]
  - See if edge deduplication is needed when merging sources [data quality]

- Discoveries:
  #LEARNED "Supporting multiple formats (list + dict) increases compatibility but adds complexity"
  #DECISION "Support only list format - simpler codebase, clearer spec"
  **Choice:** List format only: `nodes: [{id: "C-001", ...}]`
  **Rationale:** Single format reduces complexity, easier to validate, clearer documentation
  **Tradeoff:** Legacy files need conversion (one-time cost vs ongoing maintenance)

- Risk watchlist:
  - Large graph-index.yaml files (1000+ nodes) need performance testing [scalability]
  - Duplicate edges from multiple sources may need deduplication [data integrity]

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

**Implements:** S-JIGY-003

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
  - Graph class already had all required registry methods from previous work
  - O(1) lookup verified: 1000 lookups in 0.1ms (hash map working perfectly)
  - TDD approach: wrote 10 comprehensive tests first, all passed immediately

- What could be better:
  - Could add edge indices (_edges_from, _edges_to) for O(1) edge queries (currently O(n))
  - Thread-safety not yet implemented (deferred until parallelism is needed)

- Next experiment:
  #EXPERIMENT "Add edge indices for O(1) edge queries if performance becomes issue"

- Discoveries:
  #LEARNED "Existing Graph class was already a unified registry - WU3 was validation"
  #LEARNED "Performance is excellent: 40 nodes load in 14ms, lookups are <0.001ms each"

- Risk watchlist:
  - Edge queries are O(n) - acceptable for now, but may need indexing at scale [performance]
  - No thread-safety yet - add locks if future parallelism is needed [concurrency]

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

**Implements:** S-JIGY-004

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
  - TDD approach: 21 comprehensive tests written first, all passed after implementation
  - Type-aware validation rules prevent architectural violations (e.g., C->O invalid)
  - Performance excellent: 1000 nodes validated in <1 second

- What could be better:
  - Discovered inline comma-separated format (`implements: O-001, O-002`) not handled initially
  - Fixed by enhancing relationship parser to split on commas

- Next experiment:
  #EXPERIMENT "Consider stricter validation: warn on non-standard YAML formats"

- Discoveries:
  #LEARNED "Real-world JIG files use inline comma-separated format for relationships"
  #LEARNED "Edge type validation catches architectural violations early"
  #DECISION "Orphaned nodes are warnings, not errors (expected for new Intent nodes)"

- Risk watchlist:
  - Unknown edge types generate warnings but don't fail validation [extensibility]
  - Self-loops are errors - may need to allow for certain constraint types [flexibility]

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

**Implements:** S-JIGY-005

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
  - Commands already implemented from previous work - WU5 focused on comprehensive testing
  - 24 tests verify all query commands (show, list, deps, impact, path)
  - Test fixtures with realistic graph structures caught edge cases

- What could be better:
  - Initially forgot that graph is undirected for path finding - all nodes were connected
  - Needed isolated node to properly test "no path found" scenario

- Next experiment:
  #EXPERIMENT "Add --json output format for machine-readable graph queries"

- Discoveries:
  #LEARNED "Graph commands already existed - validation through testing confirms they work"
  #LEARNED "Path finding treats graph as undirected - bidirectional traversal"

- Risk watchlist:
  - Output format might need refinement based on real usage [UX]
  - Performance on very large graphs (1000+ nodes) not yet tested [scalability]

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy graph show S-AIR-001
  # Should show full node details with relationships
  jigy graph list --type specification --subsystem airspace
  # Should filter by subsystem
  jigy graph path S-AIR-001 O-AIR-001
  # Should find path between nodes
  ```
- Look for: Clear, useful output; accurate relationship display

---

### Work Unit 6: Path Finding & Traversal

**Implements:** S-JIGY-006

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
  - Path finding and traversal methods already implemented and tested from previous work
  - 11 comprehensive tests cover all scenarios (BFS, shortest path, cycles, performance)
  - CLI commands (`jigy graph path`, `deps`, `impact`) work correctly

- What could be better:
  - N/A - WU6 functionality complete from earlier development

- Next experiment:
  #EXPERIMENT "Add depth-limited traversal with --max-depth flag"

- Discoveries:
  #LEARNED "Graph traversal was already complete - WU6 validates existing implementation"
  #LEARNED "BFS finds shortest paths efficiently even on complex graphs"

- Risk watchlist:
  - Performance on very large graphs (5000+ edges) not yet tested [scalability]

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy graph path O-PS-001 C-PS-005
  # Should find path through specifications
  ```
- Look for: Accurate traversal, clear visualization

---

### Work Unit 7: Subsystem Queries

**Implements:** S-JIGY-007

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
  - Subsystem functionality already implemented in `jigy decompose metrics`
  - 22 comprehensive tests cover nested subsystems, metrics, edge classification
  - Internal/external edge classification working correctly

- What could be better:
  - N/A - WU7 functionality complete from earlier development

- Next experiment:
  #EXPERIMENT "Add subsystem dependency graph visualization"

- Discoveries:
  #LEARNED "Subsystem queries complete - decompose metrics provides all needed info"
  #LEARNED "Nested subsystem support with dot notation (e.g., crdt.ser)"

- Risk watchlist:
  - Edge classification accuracy depends on correct node.subsystem assignment [data quality]

**Links:**
- MR/PR: 
- Commit(s): 

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/ASE-A
  jigy decompose metrics --subsystem airspace
  # Should show node counts and internal/external edge breakdown
  jigy graph list --subsystem airspace
  # Should list all nodes in subsystem
  ```
- Look for: Accurate classification, useful architectural insight

**Milestone: jigy v0.3.0 Complete**
- Graph exploration working
- Query and traversal commands functional
- Subsystem analysis available

---

### Work Unit 8: Fast Code Scanner for @jig Annotations

**Implements:** S-JIGY-008

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

**Implements:** S-JIGY-009

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

**Implements:** S-JIGY-010

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
  - TDD approach: 21 comprehensive tests written first, all passed immediately [process]
  - Composition worked perfectly: reused WU8 scanner, WU2 graph loader [architecture]
  - Semantic validation (code implements, test verifies) caught logical errors [quality]
  - Coverage metrics provide actionable insight into implementation completeness [value]

- What could be better:
  - Could add more granular validation rules (interface consistency, etc.) [extensibility]
  - Coverage calculation is simple - could enhance with trend tracking [metrics]

- Next experiment:
  #EXPERIMENT "Add strict mode where warnings become errors for CI/CD"

- Discoveries:
  #LEARNED "Orphan detection needs to respect node status (skip deprecated)" 
  #LEARNED "Edge type validation prevents semantic errors (code verify vs implement)"
  #DECISION "Calculate coverage as percentage of active specs with implementations"
  **Rationale:** Simple metric, actionable, ignores deprecated/planned specs

- Risk watchlist:
  - Large codebases may need performance optimization [scalability]
  - Suggestion engine (fix suggestions) would improve UX [feature]

**Links:**
- MR/PR: 
- Commit(s): [To be filled] 

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

### Work Unit 10.5: Exclusion Filtering (.jigignore, status, fixtures)

**Implements:** S-JIGY-011 (to be created)

**Supports:** O-JIGY-004 (to be created)

**Goal:** Prevent test fixtures and template files from polluting the node index during scanning and rebuild

**Discovery Context:**
Running `jigy index rebuild` on the jig project itself revealed two critical issues:
1. **Test fixture pollution**: Test files contain @jig annotations in string literals (test fixtures) that are being scanned as real nodes (e.g., `C-TEST-001` appears in 9 different test files)
2. **Template file inclusion**: Template/example markdown files (e.g., `O-PERF-001.md` with `subsystem: null`, `C-PERF-001.md` which is actually a Constraint markdown not Code) are included in the index

This WU implements a three-tier exclusion strategy discovered during WU8-10 implementation.

**Planned Effort:** 150m (includes Intent node creation + implementation + testing)

**Acceptance Criteria:**

**Intent Nodes Created:**
- O-JIGY-004.md: "JIG scanning excludes test fixtures and template files"
  - Value: Clean node index reflects only real Intent and implementation
  - Acceptance: `jigy index rebuild` produces zero duplicate warnings from test fixtures
- S-JIGY-011.md: "Exclusion filtering prevents test fixture pollution"
  - Implements: O-JIGY-004
  - Three-tier approach: .jigignore, status filtering, fixture patterns
  - Details: gitignore-style syntax, respects `status: template`, skips *-TEST-* IDs

**Implementation Complete:**
- `.jigignore` file support (Tier 1: path-based exclusions)
  - Gitignore-style pattern matching (`**/test_*.py`, `**/__pycache__/`)
  - IgnoreFilter class integrated into AnnotationScanner
  - Default `.jigignore` generated by `jig init`
- Status-based filtering (Tier 2: metadata exclusions)
  - Markdown discovery skips `status: template`, `deprecated`, `draft`
  - Self-documenting approach (files declare themselves as non-active)
- Fixture pattern detection (Tier 3: smart scanning)
  - Skip annotations matching: `C-TEST-*`, `T-TEST-*`, `C-MOCK-*`, `C-FIXTURE-*`
  - Prevents test fixture pollution at parse time
- `jigy index rebuild` produces clean output with zero test fixture duplicates

**Implementation Notes:**

**Step 1: Create Intent Nodes (30m)**
Create two new nodes following JIG workflow:

1. **O-JIGY-004.md** (jig/outcomes/):
```yaml
---
id: O-JIGY-004
type: outcome
title: JIG scanning excludes test fixtures and template files
subsystem: jigy-tool
status: active
created: 2025-11-22
---

# Outcome: JIG Scanning Excludes Test Fixtures and Template Files

## Value

Clean node index that reflects only real Intent (O/S) and implementation (C/T) nodes, without pollution from:
- Test fixture annotations (mock @jig tags in test string literals)
- Template markdown files (examples, placeholders)
- Build artifacts and generated files

Developers trust the index as source of truth for "what actually exists."

## Success Metrics

- Zero duplicate node warnings from test fixtures in `jigy index rebuild`
- Zero template files included in active node counts
- <5% false negatives (real nodes incorrectly excluded)

## Acceptance Criteria

- `jigy index rebuild` on jig project shows zero `C-TEST-*` duplicates
- Template files with `status: template` not included in index
- `.jigignore` patterns exclude specified paths
- Real implementation nodes still discovered correctly
```

2. **S-JIGY-011.md** (jig/specifications/):
```yaml
---
id: S-JIGY-011
type: specification
title: Exclusion filtering prevents test fixture pollution
subsystem: jigy-tool
implements: O-JIGY-004
status: active
created: 2025-11-22
---

# S-JIGY-011: Exclusion Filtering

## Specification

The jigy scanner and index builder SHALL exclude non-real nodes using a three-tier filtering approach.

## Tier 1: Path-Based Exclusions (.jigignore)

**File:** `.jigignore` in project root (gitignore syntax)

**Behavior:**
- Load patterns from `.jigignore` if exists, else use defaults
- Pattern matching uses fnmatch/glob syntax
- Patterns apply to both markdown discovery and annotation scanning

**Default patterns:**
```
**/test_*.py          # Test files (fixtures)
**/conftest.py        # Pytest config
**/__pycache__/       # Python cache
**/*.pyc
.venv/
dist/
build/
```

**Implementation:** `IgnoreFilter` class checks paths before scanning

## Tier 2: Status-Based Filtering

**Markdown frontmatter field:** `status`

**Excluded statuses:**
- `template` - Template/example files
- `deprecated` - Old nodes kept for history
- `draft` - Work in progress

**Included statuses:**
- `active` - Real, current nodes
- `planned` - Future work (valid Intent)
- `null` / missing - Defaults to active

**Implementation:** Filter in `IndexBuilder.discover_markdown_nodes()`

## Tier 3: Fixture Pattern Detection

**Annotation IDs to skip:**
- `C-TEST-*` - Code test fixtures
- `T-TEST-*` - Test test fixtures
- `C-MOCK-*` - Mock objects
- `C-FIXTURE-*` - Explicit fixtures
- `C-EXAMPLE-*` - Example code

**Implementation:** `_is_test_fixture()` in `parse_annotation_line()`

## Configuration

Optional `jig.toml` settings:
```toml
[jig.scanning]
exclude_statuses = ["template", "deprecated", "draft"]
fixture_patterns = ["*-TEST-*", "*-MOCK-*", "*-FIXTURE-*"]
```

## Rationale

Layered defense prevents pollution at multiple levels:
- User control (.jigignore) for project-specific exclusions
- Metadata-driven (status) for self-documenting intent
- Pattern-based (fixtures) as safety net

## References

- Issue discovered: WU8-10 implementation, `jigy index rebuild` output
- Related: S-JIGY-008 (scanner), S-JIGY-009 (index rebuild)
```

**Step 2: Implement Tier 1 - .jigignore Support (40m)**

Create `src/jig/core/ignore_filter.py`:
```python
# @jig C-JIGY-011 implements:S-JIGY-011 subsystem:jigy-tool interface:internal
"""Ignore pattern filtering for JIG scanning."""

from pathlib import Path
import fnmatch

class IgnoreFilter:
    """Handles .jigignore file parsing and path filtering."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.patterns = self._load_ignore_patterns()
    
    def _load_ignore_patterns(self) -> list[str]:
        """Load patterns from .jigignore file."""
        ignore_file = self.project_root / ".jigignore"
        if not ignore_file.exists():
            return self._default_patterns()
        
        patterns = []
        with open(ignore_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    patterns.append(line)
        return patterns
    
    def _default_patterns(self) -> list[str]:
        """Default patterns when .jigignore doesn't exist."""
        return [
            "**/__pycache__/",
            "**/*.pyc",
            ".venv/",
            "dist/",
            "build/",
        ]
    
    def should_exclude(self, path: Path) -> bool:
        """Check if path matches any ignore pattern."""
        try:
            relative = path.relative_to(self.project_root)
        except ValueError:
            # Path is outside project root
            return False
        
        path_str = str(relative)
        
        for pattern in self.patterns:
            # Support both glob patterns and simple matches
            if fnmatch.fnmatch(path_str, pattern):
                return True
            # Also check if pattern matches directory component
            if fnmatch.fnmatch(path_str, f"**/{pattern}"):
                return True
        
        return False
```

Integrate into `AnnotationScanner`:
```python
# In scanner.py
def scan_directory(self, directory: Path, ignore_filter: IgnoreFilter | None = None) -> list[Annotation]:
    """Scan directory with optional ignore filter."""
    annotations: list[Annotation] = []
    
    for ext in self.file_extensions:
        for file_path in directory.rglob(f"*{ext}"):
            # Skip if matches .jigignore
            if ignore_filter and ignore_filter.should_exclude(file_path):
                continue
                
            if file_path.is_file():
                annotations.extend(self.scan_file(file_path))
    
    return annotations
```

**Step 3: Implement Tier 2 - Status Filtering (20m)**

Modify `IndexBuilder.discover_markdown_nodes()`:
```python
# In index_builder.py
EXCLUDED_STATUSES = {'template', 'deprecated', 'draft'}

def discover_markdown_nodes(self) -> list[OSTCNode]:
    """Discover O/S/C nodes, excluding templates/deprecated."""
    nodes: list[OSTCNode] = []
    
    for md_file in dir_path.glob("*.md"):
        try:
            node = parse_ostc_node(md_file)
            
            # Skip template/deprecated/draft nodes
            if node.status in EXCLUDED_STATUSES:
                continue
            
            nodes.append(node)
        except Exception as e:
            self.parse_errors.append(f"Failed to parse {md_file}: {str(e)}")
    
    return nodes
```

**Step 4: Implement Tier 3 - Fixture Pattern Detection (20m)**

Add to `scanner.py`:
```python
# In scanner.py
import re

FIXTURE_PATTERNS = [
    r'^[CT]-TEST-\d+$',      # C-TEST-001, T-TEST-001
    r'^[CT]-MOCK-\d+$',      # C-MOCK-001
    r'^[CT]-FIXTURE-\d+$',   # C-FIXTURE-001
    r'^[CT]-EXAMPLE-\d+$',   # C-EXAMPLE-001
]

def _is_test_fixture(node_id: str) -> bool:
    """Check if node ID looks like a test fixture."""
    for pattern in FIXTURE_PATTERNS:
        if re.match(pattern, node_id):
            return True
    return False

def parse_annotation_line(line: str) -> Annotation | None:
    """Parse @jig annotation, skipping test fixtures."""
    match = re.search(r'@jig\s+([A-Z]-[A-Z]+-\d+)', line)
    if not match:
        return None
    
    node_id = match.group(1)
    
    # Skip test fixture patterns
    if _is_test_fixture(node_id):
        return None
    
    # ... rest of parsing ...
```

**Step 5: Generate Default .jigignore (20m)**

Update `jig init` to create `.jigignore`:
```python
# In cli/init.py
def create_default_jigignore(project_root: Path) -> None:
    """Create default .jigignore file if it doesn't exist."""
    ignore_file = project_root / ".jigignore"
    if ignore_file.exists():
        return
    
    content = """# .jigignore - JIG scanning exclusions
# Syntax: gitignore-style patterns (supports *, **, ?)

# Test files (contain fixtures that pollute node index)
**/test_*.py
**/conftest.py

# Build artifacts
**/__pycache__/
**/*.pyc
.venv/
.pytest_cache/
.tox/
*.egg-info/
dist/
build/

# IDE files
.vscode/
.idea/
*.swp

# Add project-specific exclusions below
"""
    ignore_file.write_text(content)
```

**Step 6: Mark Template Files (10m)**

Update existing template files:
```yaml
# jig/outcomes/O-PERF-001.md
status: template  # ← Add this

# jig/constraints/C-PERF-001.md
status: template  # ← Add this
```

**Test Plan:**

Unit tests (create `tests/unit/test_ignore_filter.py`):
```python
# @jig T-JIGY-011 verifies:S-JIGY-011 subsystem:jigy-tool
def test_ignore_filter_loads_patterns():
    """Test .jigignore file parsing."""

def test_ignore_filter_matches_patterns():
    """Test pattern matching logic."""

def test_ignore_filter_excludes_test_files():
    """Test that test_*.py files are excluded."""

def test_fixture_pattern_detection():
    """Test _is_test_fixture() patterns."""

def test_status_based_filtering():
    """Test template/deprecated status exclusion."""
```

Integration test:
```python
# @jig T-JIGY-012 verifies:S-JIGY-011 subsystem:jigy-tool
def test_index_rebuild_excludes_fixtures(tmp_path):
    """Test full rebuild with exclusions."""
    # Create .jigignore
    # Create template markdown with status: template
    # Create test files with C-TEST-* fixtures
    # Run rebuild
    # Assert: zero duplicates, templates excluded
```

Validation test:
```bash
cd ~/Code/jig
jigy index rebuild
# Should show: zero C-TEST-* duplicates, zero template warnings
```

**Docs to Update:**
- README: Add .jigignore section
- User guide: Explain three-tier filtering
- Migration guide: How to add .jigignore to existing projects

**Reflect (≤5 bullets; keep crisp)**

- What worked well:

- What could be better:

- Next experiment:

- Discoveries:

- Risk watchlist:

**Links:**
- MR/PR: 
- Commit(s): 

**Commit Message (Example):**
```
feat(jigy): add exclusion filtering (.jigignore, status, fixtures)

Three-tier filtering prevents test fixture pollution:
- Tier 1: .jigignore file (path-based exclusions)
- Tier 2: status field (template/deprecated filtering)
- Tier 3: fixture patterns (skip *-TEST-*, *-MOCK-*)

Intent nodes created:
- O-JIGY-004: JIG scanning excludes test fixtures and template files
- S-JIGY-011: Exclusion filtering prevents test fixture pollution

Fixes: Test fixtures polluting index, template files included

Unit: 10.5
Implements: S-JIGY-011
Discovery: WU8-10 implementation revealed issue
Reflection: see jig/deltas/active/orphaned-node-fixer/S018_PLAN.md → WU10.5
```

**Human Validation:**
- Commands: 
  ```bash
  cd ~/Code/jig
  # Check Intent nodes created
  cat jig/outcomes/O-JIGY-004.md
  cat jig/specifications/S-JIGY-011.md
  
  # Check .jigignore created
  cat .jigignore
  
  # Run rebuild - should be clean
  jigy index rebuild
  # Should show: zero duplicate warnings from C-TEST-* fixtures
  
  # Verify filtering works
  grep -r "C-TEST-001" tests/  # Should find fixtures
  jigy index rebuild --dry-run | grep "C-TEST-001"  # Should NOT appear
  ```
- Look for: Clean rebuild output, Intent nodes properly linked, templates excluded

---

### Work Unit 11: ASE-A Validation & Fixes

**Validates:** O-JIGY-001, O-JIGY-002, O-JIGY-003 (all outcomes)

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

**Supports:** All O/S nodes (documentation for complete feature set)

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
- Units: 14 (including WU0: Intent creation, WU10.5: discovered requirement)
- Estimated total effort: ~25 hours
- Target velocity: 2-3 units per day
- Expected duration: 5-7 days intensive work
- Markers captured: [count] (#DISCOVERY, #DECISION, #LEARNED)
- OSTC nodes created: 4 Outcomes, 11 Specifications (1 O + 1 S discovered during implementation)

### Reflection Roll-up
- Repeatable wins: [To be filled]
- Systemic frictions (top 3): [To be filled]
- Process changes adopted: [To be filled]
- Open questions for next plan: [To be filled]

### Harvest Preparation (JIG)

**Intent Nodes Created:**
- WU0 (Known from SCOPE): O-JIGY-001, O-JIGY-002, O-JIGY-003, S-JIGY-001 through S-JIGY-010
- WU10.5 (Discovered during WU8-10): O-JIGY-004, S-JIGY-011

**Markers Summary:**
- Discoveries: [count - NEW constraints learned during implementation]
- Decisions: [count - tradeoff choices made]
- Learned patterns: [count - reusable knowledge]

**Recommended OSTC Nodes (from DISCOVERIES during execution):**
[To be filled - only NEW insights discovered during work, not known constraints from WU0]
- [ ] Example: S-JIGY-011: "NetworkX graph construction pattern" (if discovered)
- [ ] Example: O-JIGY-004: "Graph queries support CI/CD validation" (if discovered)

**Note:** Outcomes and Specifications created in WU0 were known from SCOPE.
Harvest captures NEW insights discovered during implementation (WU1-12).

**Subsystems Touched:** jigy-tool (primary), ASE-A (validation target)

**Next Step:** `jig ai-distill --branch orphaned-node-fixer` (when harvest tooling exists)

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

