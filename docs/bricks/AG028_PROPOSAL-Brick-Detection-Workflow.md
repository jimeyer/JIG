# AG028: Brick Detection and Alignment Workflow (Proposal)

**Date:** 2025-11-30
**Status:** Proposal
**References:** AG027 (Community Detection Algorithms), J016 (JIG Concept v8), AG020 (Bricks as Partitions)

---

## Overview

This document proposes a semi-automated workflow for creating and updating brick definitions in JIG. The workflow combines:

- **Deterministic algorithms** (community detection, overlap analysis)
- **AI assistance** (semantic validation, naming)
- **Human oversight** (final approval, manual adjustments)

The key principle: **Respect existing brick definitions.** If a human has manually adjusted bricks, we bias towards preserving their decisions unless there's strong evidence of misalignment.

---

## Command-Line Interface

### Primary Command

```bash
jigy brick propose [OPTIONS]
```

**Purpose:** Analyze the implementation graph and propose brick definitions.

**Options:**
```
--mode=[discover|refine|validate]
  discover: Generate brick proposal from scratch (ignore existing bricks)
  refine:   Compare clusters to existing bricks, propose refinements (default)
  validate: Check if existing bricks align with current code structure

--auto-approve
  Skip interactive review, apply proposal automatically
  (Use with caution; intended for CI or trusted automation)

--output=PATH
  Write proposal to file instead of updating bricks.yaml
  (Useful for review before committing)

--algorithm=[louvain|leiden|label-prop]
  Which community detection algorithm to use (default: louvain)

--threshold=FLOAT
  Similarity threshold for considering existing brick "aligned" (default: 0.75)
  Higher = more conservative, preserve existing bricks more aggressively

--no-llm
  Skip LLM semantic validation (faster, less accurate)

--dry-run
  Show what would change without modifying files
```

### Supporting Commands

```bash
# Show current brick structure and metrics
jigy brick status

# Validate existing brick definitions
jigy brick validate

# Show detailed metrics for a specific brick
jigy brick inspect B-001
```

---

## The Workflow: Five Phases

### Phase 1: Load and Prepare (Deterministic)

**Input:**
- `jig/generated/implementation-graph.ndjson` (F nodes, F→F edges)
- `jig/bricks.yaml` (existing brick definitions, may be empty)

**Steps:**

1. **Load implementation graph**
   ```
   [DETERMINISTIC] Parse implementation-graph.ndjson
   [DETERMINISTIC] Extract F nodes (functions)
   [DETERMINISTIC] Extract F→F edges (call relationships)
   ```

2. **Build dependency graph**
   ```
   [DETERMINISTIC] Create NetworkX DiGraph
   [DETERMINISTIC] Nodes = F-auth.session.authenticate, F-utils.io.read_file, ...
   [DETERMINISTIC] Edges = (F₁, F₂) where F₁ calls F₂
   ```

3. **Extract semantic features**
   ```
   [DETERMINISTIC] For each F node:
     - module_path: "auth.session"
     - function_name: "authenticate"
     - file_path: "src/auth/session.py"
     - docstring: (if available in implementation graph)
   ```

4. **Load existing bricks (if present)**
   ```
   [DETERMINISTIC] Parse bricks.yaml
   [DETERMINISTIC] Build mapping: F → B (which functions are in which bricks)
   ```

**Output:**
- Dependency graph (NetworkX object)
- Semantic features (dict mapping F → features)
- Current brick assignments (dict mapping F → B, may be empty)

**Estimated time:** <1 second for typical codebase (<10k functions)

---

### Phase 2: Community Detection (Algorithmic)

**Algorithm:** Louvain community detection (per AG027 recommendation)

**Steps:**

1. **Prepare weighted graph**
   ```
   [DETERMINISTIC] Convert call graph to undirected for Louvain
   [DETERMINISTIC] Weight edges by call frequency (if available)
   [DETERMINISTIC] Default weight = 1.0 for all edges
   ```

2. **Run community detection**
   ```
   [ALGORITHMIC] Apply python-louvain library
   [ALGORITHMIC] Returns: {F → cluster_id} mapping
   [ALGORITHMIC] cluster_id = 0, 1, 2, ... (integer cluster labels)
   ```

3. **Calculate cluster metrics**
   ```
   [DETERMINISTIC] For each cluster:
     - size: number of functions
     - modularity: quality of clustering
     - internal_edges: calls within cluster
     - external_edges: calls to other clusters
     - cohesion: internal_edges / (internal_edges + external_edges)
   ```

4. **Filter/refine clusters**
   ```
   [HEURISTIC] If cluster size < 3 functions → mark as "too small"
   [HEURISTIC] If cluster size > 100 functions → mark as "too large"
   [HEURISTIC] If cohesion < 0.3 → mark as "weak cohesion"
   ```

**Output:**
- Cluster assignments: {F → cluster_id}
- Cluster metrics: {cluster_id → metrics}
- Quality flags: {cluster_id → [warnings]}

**Estimated time:** <5 seconds for typical codebase (Louvain is fast)

---

### Phase 3: Semantic Validation (AI-Assisted)

**Purpose:** Validate that structural clusters represent semantically coherent responsibilities.

**Steps:**

1. **Prepare cluster summaries**
   ```
   [DETERMINISTIC] For each cluster:
     - List all F nodes in cluster (up to 20 for LLM context)
     - Extract module paths, function names, docstrings
     - Calculate cluster metrics from Phase 2
   ```

2. **LLM semantic analysis (per cluster)**
   ```
   [AI] Prompt to LLM (Claude):
     "Given these functions from a Python codebase:
      - F-auth.session.authenticate
      - F-auth.session.logout
      - F-auth.tokens.validate
      - F-auth.tokens.create

      Do they share a coherent responsibility?
      If yes: Suggest a concise name (2-5 words).
      If no: Suggest how to split them."

   [AI] LLM returns:
     - coherence_score: 0.0-1.0 (how coherent)
     - suggested_name: "Authentication & Session Management"
     - split_suggestion: null | "Split into auth and session management"
   ```

3. **Aggregate validation results**
   ```
   [DETERMINISTIC] For each cluster:
     - If coherence_score >= 0.7 → "COHERENT"
     - If coherence_score < 0.5 → "INCOHERENT" (consider splitting)
     - Store suggested_name for later use
   ```

**Output:**
- Cluster semantic validation: {cluster_id → coherence_score, suggested_name}

**Estimated time:** ~2-5 seconds per cluster (LLM API call)

**Cost:** Minimal (small prompts, ~100 tokens per cluster)

**Fallback (--no-llm flag):**
```
[HEURISTIC] If module paths are similar → assume coherent
[HEURISTIC] Suggest name = common module prefix (e.g., "auth" → "Authentication")
```

---

### Phase 4: Alignment with Existing Bricks (Deterministic + Heuristic)

**Purpose:** Compare clusters to existing brick definitions and decide what to propose.

**Case 1: No existing bricks (cold start)**

```
[DETERMINISTIC] existing_bricks = []
[DETERMINISTIC] For each cluster:
  - Assign brick ID: B-001, B-002, B-003, ...
  - Use LLM suggested name (or fallback to module path)
  - Include all F nodes from cluster

[DETERMINISTIC] proposal = all clusters as new bricks
[DETERMINISTIC] changes = ["CREATE B-001", "CREATE B-002", ...]
```

**Case 2: Existing bricks present (refinement mode)**

This is the complex case. We need to measure overlap and decide how to align.

**Step 1: Calculate overlap matrix**

```
[DETERMINISTIC] For each (existing_brick, cluster) pair:
  - overlap = |functions_in_both| / |functions_in_cluster|
  - jaccard = |intersection| / |union|
  - Store: overlap_matrix[brick_id][cluster_id] = (overlap, jaccard)
```

**Step 2: Match clusters to existing bricks**

```
[HEURISTIC] For each cluster:
  - best_match_brick = brick with highest overlap
  - best_overlap = overlap_matrix[best_match_brick][cluster]

  If best_overlap >= threshold (default 0.75):
    → ALIGNED: cluster matches existing brick well
    → Propose: Keep existing brick (minor adjustments if needed)

  Else if best_overlap >= 0.4:
    → PARTIAL: cluster partially overlaps existing brick
    → Propose: Merge or split (requires human decision)

  Else:
    → NEW: cluster has no good match
    → Propose: Create new brick
```

**Step 3: Detect brick quality issues**

```
[HEURISTIC] For each existing brick:
  - If no cluster matches well (all overlaps < 0.4):
    → ORPHANED: brick may be outdated (functions moved/deleted)
    → Propose: Review or delete

  - If brick is split across multiple clusters:
    → FRAGMENTED: brick may need to be split
    → Propose: Split into multiple bricks
```

**Step 4: Generate proposal**

```
[DETERMINISTIC] Build proposal object:
  {
    "keep": [brick_ids that align well],
    "modify": [
      {
        "brick": "B-001",
        "action": "add_functions",
        "functions": ["F-auth.new_feature"],
        "reason": "New functions clustered with B-001"
      }
    ],
    "create": [
      {
        "name": "New Feature Module",
        "functions": [...],
        "reason": "New cluster detected with no existing brick"
      }
    ],
    "delete": [
      {
        "brick": "B-005",
        "reason": "No functions remain in this brick"
      }
    ],
    "warnings": [
      "B-002 is fragmented across 3 clusters - consider splitting"
    ]
  }
```

**Output:**
- Proposal object (keep/modify/create/delete)
- Alignment metrics (how well clusters match existing bricks)

**Estimated time:** <1 second (simple graph operations)

---

### Phase 5: User Review and Application (Interactive)

**Purpose:** Present proposal to user, get approval, apply changes.

**Step 1: Display proposal (interactive mode)**

```
[UI] Show summary:

  Brick Proposal Summary
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓ KEEP (5 bricks align well)
    B-001: Authentication & Session Management (23 functions)
    B-002: Command Line Interface (12 functions)
    ...

  ~ MODIFY (2 bricks need updates)
    B-003: Core Utilities
      + Add 3 new functions from recent commits
      Functions: F-utils.json.parse, F-utils.json.dump, ...
      Reason: New JSON utilities clustered with existing utilities

  + CREATE (1 new brick)
    Brick: Visualization & Export (suggested name)
      15 functions detected in new cluster
      Functions: F-viz.graph.render, F-viz.export.to_svg, ...
      Reason: New subsystem with no existing brick

  ⚠ WARNINGS (1)
    B-004: Graph Processing
      Fragmented across 2 clusters - consider splitting?

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Apply this proposal? [y/N]
```

**Step 2: Interactive refinement (optional)**

```
[UI] If user wants to review details:

  Show brick B-003:
    Current: 18 functions
    Proposed: 21 functions (+3 new)

    New functions:
      F-utils.json.parse
      F-utils.json.dump
      F-utils.json.validate

    Accept changes to B-003? [Y/n/skip]
```

**Step 3: Apply approved changes**

```
[DETERMINISTIC] For each approved change:
  - Update bricks.yaml with new function assignments
  - Preserve brick IDs for "keep" and "modify" actions
  - Assign new IDs (B-006, B-007, ...) for "create" actions
  - Remove bricks marked for "delete"

[DETERMINISTIC] Write updated bricks.yaml:
  - Maintain YAML structure
  - Add comments for new bricks (generated by this tool)
  - Preserve manual comments (don't overwrite)
```

**Step 4: Validate result**

```
[DETERMINISTIC] After writing bricks.yaml:
  - Check all F nodes are assigned to exactly one brick
  - Check no brick IDs are duplicated
  - Check all units reference valid nodes
  - Report any validation errors
```

**Output:**
- Updated `jig/bricks.yaml`
- Summary of changes applied

**Estimated time:** Depends on user interaction (seconds to minutes)

---

## Workflow Summary: Step-by-Step Execution

```bash
$ jigy brick propose --mode=refine
```

**Phase 1: Load and Prepare** [DETERMINISTIC]
```
Loading implementation graph... ✓ (1,247 functions loaded)
Loading existing bricks... ✓ (5 bricks defined)
Building dependency graph... ✓ (3,421 call edges)
```

**Phase 2: Community Detection** [ALGORITHMIC]
```
Running Louvain community detection...
  Detected 6 clusters
  Modularity score: 0.68 (good)
  Calculating cluster metrics... ✓
```

**Phase 3: Semantic Validation** [AI]
```
Validating cluster coherence with LLM...
  Cluster 0 (23 functions): Authentication & Session Management [coherent: 0.92] ✓
  Cluster 1 (12 functions): Command Line Interface [coherent: 0.88] ✓
  Cluster 2 (18 functions): Core Utilities [coherent: 0.85] ✓
  Cluster 3 (15 functions): Visualization & Export [coherent: 0.79] ✓
  Cluster 4 (8 functions): Graph Processing [coherent: 0.65] ⚠
  Cluster 5 (5 functions): [incoherent: 0.42] ✗
    → Suggestion: May be utility functions, consider merging with Cluster 2
```

**Phase 4: Alignment Analysis** [DETERMINISTIC + HEURISTIC]
```
Comparing clusters to existing bricks...
  B-001 ↔ Cluster 0: 95% overlap → KEEP ✓
  B-002 ↔ Cluster 1: 100% overlap → KEEP ✓
  B-003 ↔ Cluster 2: 86% overlap → KEEP (add 3 functions) ~
  B-004 ↔ Cluster 4: 75% overlap → KEEP ✓
  B-005 ↔ No cluster: 0% overlap → DELETE (functions moved) ✗
  Cluster 3 ↔ No brick: NEW brick needed +
  Cluster 5 ↔ Cluster 2: Consider merging with B-003 ⚠
```

**Phase 5: User Review** [INTERACTIVE]
```
[Shows detailed proposal as above]

Apply this proposal? [y/N] y

Applying changes...
  Updating B-003 (Core Utilities): +3 functions ✓
  Creating B-006 (Visualization & Export): 15 functions ✓
  Deleting B-005 (deprecated): 0 functions ✓

Writing jig/bricks.yaml... ✓

Summary:
  5 bricks kept unchanged
  1 brick modified
  1 brick created
  1 brick deleted
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total: 6 bricks, 1,247 functions, 100% coverage ✓
```

---

## Design Decisions

### Why Bias Towards Existing Bricks?

**Rationale:** Humans adjust bricks for reasons not captured in the graph:
- Domain knowledge (functions belong together conceptually)
- Team organization (brick ownership maps to teams)
- Historical reasons (legacy code grouped intentionally)

**Implementation:** High threshold (default 0.75) for "aligned". Only propose changes if cluster diverges significantly.

**Trade-off:** May miss opportunities to improve brick structure. Acceptable because:
- Human can lower threshold if they want more aggressive refactoring
- `--mode=discover` allows fresh start if needed

### Why LLM Validation is Optional (--no-llm)?

**Rationale:**
- Some teams may not have LLM access (air-gapped environments)
- Some teams may prefer pure algorithmic approach (reproducibility)
- LLM adds cost and latency

**Fallback:** Use heuristics (module path similarity, function name prefixes)

**Trade-off:** Lower quality clustering without LLM. Acceptable for initial drafts.

### Why Interactive Mode is Default?

**Rationale:** Brick definitions are architectural decisions. Humans should approve.

**Alternative:** `--auto-approve` for CI or trusted automation.

**Trade-off:** Requires human interaction. Acceptable for important structural changes.

### Why Not Store Cluster History?

**Alternative considered:** Track cluster assignments over time, detect drift.

**Rejected:** Adds complexity. Current approach (compare to existing bricks) is sufficient.

**Future:** Could add `jigy brick history` to show how bricks evolved (via git history).

---

## Edge Cases

### Empty Implementation Graph

**Scenario:** No functions in codebase (early project).

**Behavior:**
```
No functions found in implementation graph.
Cannot generate brick proposal.
Run 'jigy impl rebuild' to generate implementation graph first.
```

### All Functions in One Giant Cluster

**Scenario:** Louvain finds no clear boundaries (monolithic codebase).

**Behavior:**
```
Warning: All functions clustered into single community.
Codebase may lack clear module boundaries.
Consider:
  1. Refactoring code to improve modularity
  2. Using --mode=discover with manual seeding
  3. Manually defining initial bricks in bricks.yaml
```

### Cluster Smaller Than Minimum Threshold

**Scenario:** Cluster has only 1-2 functions.

**Behavior:**
```
Cluster 7: 2 functions (too small)
  F-utils.deprecated.old_function
  F-utils.deprecated.legacy_helper

Suggestion: Merge with nearest cluster or mark as utilities.
```

**Heuristic:** Merge small clusters with nearest neighbor (highest inter-cluster edge weight).

### Existing Brick Completely Misaligned

**Scenario:** Existing brick has 0% overlap with any cluster.

**Behavior:**
```
Warning: B-007 has no overlap with any detected cluster.
  Functions may have been deleted or moved.

Propose: DELETE B-007
Review functions before deletion:
  F-old.deprecated.function (file not found)
  F-old.legacy.helper (file not found)
```

---

## Validation and Metrics

After applying brick proposal, validate:

```bash
jigy brick validate
```

**Checks:**

1. **Coverage:** Do all F nodes have a brick assignment?
   ```
   ✓ 1,247 / 1,247 functions assigned to bricks (100%)
   ```

2. **Partition:** Is each F assigned to exactly one brick?
   ```
   ✓ No functions assigned to multiple bricks
   ✓ No functions unassigned
   ```

3. **Cohesion:** Are bricks internally cohesive?
   ```
   B-001: Internal cohesion 0.82 ✓
   B-002: Internal cohesion 0.71 ✓
   B-003: Internal cohesion 0.58 ⚠ (consider refining)
   ```

4. **Coupling:** Are brick dependencies reasonable?
   ```
   B-001 → B-003 (23 calls) [normal]
   B-002 → B-001 (45 calls) [heavy, review]
   B-004 → B-005 (2 calls) [light]
   ```

**Output metrics:**
- Partition quality (coverage, uniqueness)
- Cohesion scores (internal vs external edges)
- Coupling matrix (dependencies between bricks)
- Suggestions for improvement

---

## Future Enhancements

### 1. Incremental Updates (Efficiency)

**Problem:** Re-running full clustering on every code change is wasteful.

**Solution:** Detect delta (new/changed/deleted functions) and only re-cluster affected regions.

**Implementation:**
```bash
jigy brick propose --incremental
```
- Load previous cluster assignments (from last run)
- Identify new/changed functions
- Re-cluster only affected neighborhood
- Merge results with stable clusters

### 2. Manual Seeding (Control)

**Problem:** User wants specific functions grouped together.

**Solution:** Allow manual hints in bricks.yaml that constrain clustering.

**Implementation:**
```yaml
bricks:
  - id: B-001
    name: Authentication
    seed: true  # Don't modify this brick
    units:
      - M-auth.session
```

Clustering algorithm treats seeded bricks as fixed, clusters remaining functions.

### 3. Brick Dependencies as Constraints

**Problem:** User wants to enforce "foundation cannot depend on domain" rule.

**Solution:** Use brick dependencies as constraints in clustering.

**Implementation:**
```yaml
brick_layers:
  - name: foundation
    bricks: [B-001, B-002]
  - name: domain
    bricks: [B-003, B-004]
  - name: interface
    bricks: [B-005]

constraints:
  - foundation CANNOT depend on domain
  - foundation CANNOT depend on interface
```

Clustering algorithm rejects solutions that violate constraints.

### 4. Multi-Objective Clustering

**Problem:** Want to optimize for both coupling AND semantic coherence.

**Solution:** Combine graph-based and semantic-based clustering.

**Implementation:**
- Louvain on dependency graph (structural clustering)
- Embedding-based clustering on semantic features (word2vec)
- Multi-objective optimization (find clusters that score well on both)

---

## Implementation Roadmap

### Phase 1: MVP (Minimum Viable Product)
- [x] Louvain community detection (deterministic)
- [ ] Basic overlap analysis (deterministic)
- [ ] Simple CLI output (show clusters)
- [ ] Manual editing of bricks.yaml

**Goal:** Prove community detection works on real codebases.

### Phase 2: LLM Integration
- [ ] LLM semantic validation (per cluster)
- [ ] Suggested names from LLM
- [ ] Coherence scoring

**Goal:** Improve cluster quality with AI assistance.

### Phase 3: Alignment and Refinement
- [ ] Compare clusters to existing bricks
- [ ] Propose keep/modify/create/delete
- [ ] Interactive approval workflow

**Goal:** Support incremental refinement, not just cold start.

### Phase 4: Validation and Metrics
- [ ] Cohesion/coupling metrics
- [ ] Brick quality scoring
- [ ] Visualization (brick dependency graph)

**Goal:** Help users understand and improve brick structure.

---

## Conclusion

The proposed workflow balances automation and human oversight:

- **Deterministic algorithms** provide objective, reproducible baseline (Louvain clustering)
- **AI assistance** improves quality (semantic validation, naming)
- **Human approval** ensures architectural decisions reflect domain knowledge
- **Bias towards existing bricks** prevents unnecessary churn

The result: A tool that helps developers discover and maintain good brick boundaries, while respecting the architectural decisions they've already made.

**Next step:** Implement Phase 1 MVP and validate on the JIG codebase itself.
