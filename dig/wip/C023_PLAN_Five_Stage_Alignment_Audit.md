---
type: plan
title: Five Stage Alignment Audit
status: active
created: 1736312400
created_human: 2026-01-07 19:20 PST
parent: "[[C022_CONCEPT_Stratified_Alignment_Verification]]"
children: []
prompt: |-
  Agent-executable PLAN for running the 5-stage alignment audit manually.
  Orchestration agent launches subagents for each stage.
  Subagents may write scripts as needed.
  Results saved to dig/generated/audit/.
  Final report synthesizes all stages.
---

# Five Stage Alignment Audit

_Agent-executable plan for stratified alignment verification_

---

## Overview

This PLAN instructs an orchestration agent to run the 5-stage alignment audit on a JIG project. Each stage is executed by a subagent that:
1. Gathers required data
2. Computes metrics
3. Saves structured results
4. Returns summary to orchestrator

The orchestrator synthesizes stage results into a final report.

---

## Prerequisites

Before starting, verify:
- [ ] Project has `.venv` activated
- [ ] Project has `jig/` directory with intent artifacts
- [ ] Project has test suite with pytest
- [ ] Coverage can be generated (`pytest --cov`)

---

## Output Structure

All results saved to `dig/generated/audit/`:

```
dig/generated/audit/
├── stage1_code.json         # Stage 1 results
├── stage2_test.json         # Stage 2 results
├── stage3_spec.json         # Stage 3 results
├── stage4_hierarchy.json    # Stage 4 results
├── stage5_semantic.json     # Stage 5 results (if run)
├── scripts/                 # Generated analysis scripts
│   ├── analyze_imports.py
│   ├── analyze_coverage.py
│   ├── analyze_decorators.py
│   └── ...
└── AUDIT_REPORT.md          # Final synthesized report
```

---

## Orchestration Flow

```
ORCHESTRATOR
│
├─→ [Stage 1 Subagent] CODE
│   └─→ stage1_code.json
│
├─→ [Stage 2 Subagent] TEST
│   └─→ stage2_test.json
│
├─→ [Stage 3 Subagent] SPEC
│   └─→ stage3_spec.json
│
├─→ [Stage 4 Subagent] HIERARCHY
│   └─→ stage4_hierarchy.json
│
├─→ [Stage 5 Subagent] SEMANTIC (optional)
│   └─→ stage5_semantic.json
│
└─→ [Report Subagent] SYNTHESIZE
    └─→ AUDIT_REPORT.md
```

---

# Stage Instructions

## Stage 1: CODE

**Subagent Task:** Analyze structural health of codebase

### Inputs Required
- Source code directory (typically `src/` or project root)
- Brick definitions from `jig/architecture/` (if they exist)

### Steps

1. **Create output directory**
   ```bash
   mkdir -p dig/generated/audit/scripts
   ```

2. **Build import graph**
   - Scan all `.py` files in source directories
   - Extract import statements
   - Build module dependency graph
   - Identify which brick each module belongs to (from A-### files or infer from directory)

3. **Compute metrics**

   | Metric | How to Compute |
   |--------|----------------|
   | C1.1 Layer Violations | Count imports from higher layer to lower |
   | C1.2 Tower Isolation | Count imports between declared towers |
   | C1.3 Brick Cycles | Find SCCs in brick dependency graph |
   | C1.4 Import Fan-Out | Max distinct modules imported per file |
   | C1.5 Import Fan-In | Max files importing a given module |
   | C1.6 Module Cohesion | Intra-brick imports / total imports |
   | C1.7 Complexity | Count functions with high cyclomatic complexity (use `radon` or manual) |
   | C1.8 LOC Distribution | Compute Gini coefficient of function sizes |

4. **Identify violations**
   - List all layer violations with file:line
   - List all tower isolation breaks
   - List high fan-out modules (>10 imports)
   - List complexity outliers

5. **Save results**
   ```json
   // dig/generated/audit/stage1_code.json
   {
     "stage": 1,
     "name": "CODE",
     "timestamp": "2026-01-07T19:30:00Z",
     "metrics": {
       "C1.1_layer_violations": 2,
       "C1.2_tower_isolation": 0,
       "C1.3_brick_cycles": 0,
       "C1.4_max_fan_out": 12,
       "C1.5_max_fan_in": 8,
       "C1.6_mean_cohesion": 0.73,
       "C1.7_complexity_outliers": 3,
       "C1.8_loc_gini": 0.42
     },
     "health_score": 85,
     "violations": [
       {"type": "layer", "file": "src/api/handler.py", "imports": "src/core/internal.py"},
       ...
     ],
     "outliers": [
       {"type": "complexity", "file": "src/graph/builder.py", "function": "build_graph", "cc": 18},
       ...
     ],
     "brick_graph": {
       "nodes": ["B-core", "B-api", "B-cli"],
       "edges": [["B-api", "B-core"], ["B-cli", "B-api"]]
     }
   }
   ```

6. **Return summary to orchestrator**
   ```
   Stage 1 Complete: CODE
   Health Score: 85/100
   Violations: 2 layer, 0 tower
   Outliers: 3 complexity
   Saved: dig/generated/audit/stage1_code.json
   ```

---

## Stage 2: TEST

**Subagent Task:** Analyze test coverage and infer proto-specs

### Inputs Required
- Stage 1 results (for brick context)
- Test suite location
- Ability to run pytest with coverage

### Steps

1. **Generate coverage report**
   ```bash
   pytest --cov=src --cov=jig --cov-report=json:dig/generated/audit/coverage.json -q
   ```

2. **Parse coverage data**
   - Extract function-level coverage (which tests hit which functions)
   - Build T→F graph (test → functions covered)

3. **Compute metrics**

   | Metric | How to Compute |
   |--------|----------------|
   | T2.1 Coverage Breadth | covered_functions / total_functions |
   | T2.2 Coverage Depth | mean(tests_per_function) |
   | T2.3 Coverage Gini | Gini coefficient of coverage % per brick |
   | T2.4 Test Scope | histogram of functions_per_test |
   | T2.5 Test-Brick Alignment | % of tests in tests/X/ that cover src/X/ |
   | T2.6 Scope Bimodality | Check if test scope is bimodal (unit vs integration) |
   | T2.7 Orphan Functions | Functions with 0 test coverage |
   | T2.8 Hot Spots | Functions covered by >10 tests |

4. **Cluster tests by coverage overlap**
   ```python
   # Pseudocode for proto-spec inference
   def cluster_tests(T_F_graph):
       # Compute Jaccard similarity between tests
       # Cluster with threshold ~0.3
       # Each cluster = proto-spec
       return clusters
   ```

5. **Identify proto-specs**
   - For each test cluster:
     - List member tests
     - List covered functions (intersection)
     - Identify entry points (public functions)
     - Suggest proto-spec name from test names

6. **Save results**
   ```json
   // dig/generated/audit/stage2_test.json
   {
     "stage": 2,
     "name": "TEST",
     "timestamp": "2026-01-07T19:35:00Z",
     "metrics": {
       "T2.1_coverage_breadth": 0.78,
       "T2.2_coverage_depth": 2.3,
       "T2.3_coverage_gini": 0.31,
       "T2.5_test_brick_alignment": 0.85,
       "T2.6_scope_bimodality": 0.72,
       "T2.7_orphan_count": 12,
       "T2.8_hot_spot_count": 5
     },
     "health_score": 72,
     "proto_specs": [
       {
         "id": "proto-1",
         "tests": ["test_graph.test_load", "test_graph.test_save"],
         "functions": ["graph.loader.load", "graph.loader.save"],
         "entry_points": ["graph.loader.load", "graph.loader.save"],
         "suggested_name": "Graph Persistence"
       },
       ...
     ],
     "orphan_functions": [
       "src/utils/legacy.py:old_helper",
       ...
     ],
     "hot_spots": [
       {"function": "core.config.get", "test_count": 23},
       ...
     ]
   }
   ```

7. **Return summary to orchestrator**
   ```
   Stage 2 Complete: TEST
   Health Score: 72/100
   Coverage: 78%
   Proto-specs inferred: 15
   Orphan functions: 12
   Saved: dig/generated/audit/stage2_test.json
   ```

---

## Stage 3: SPEC

**Subagent Task:** Analyze spec coverage and triangle closure

### Inputs Required
- Stage 2 results (proto-specs, T→F graph)
- Decorator locations from source code
- Spec files from `jig/specifications/`

### Steps

1. **Extract decorators**
   - Grep for `@jig.implements("S-###")` in source files
   - Grep for `@jig.verifies("S-###")` in test files
   - Build S→F graph (spec → implementing functions)
   - Build S→T graph (spec → verifying tests)

2. **Load spec definitions**
   - Parse all `jig/specifications/S-###_*.md` files
   - Extract spec IDs and titles

3. **Compute triangle closure**
   ```python
   for spec in specs:
       implementations = S_F[spec]  # functions
       tests = S_T[spec]            # tests
       covered = union(T_F[t] for t in tests)  # what tests actually cover

       closure = len(implementations & covered) / len(implementations)
       gap = implementations - covered
   ```

4. **Compute metrics**

   | Metric | How to Compute |
   |--------|----------------|
   | S3.1 Decorator Coverage (impl) | functions_with_decorator / entry_points |
   | S3.2 Decorator Coverage (verify) | tests_with_decorator / focused_tests |
   | S3.3 Triangle Closure | mean(closure per spec) |
   | S3.4 Verification Gap | specs with no verifying tests |
   | S3.5 Granularity Variance | stddev(implementations per spec) |
   | S3.6 Impl Scatter | mean(bricks per spec) |
   | S3.7 Projection Agreement | Compare impl clusters to verify clusters |
   | S3.8 Proto-Spec Match | Compare proto-specs to declared specs |

5. **Compare proto-specs to declared specs**
   - For each proto-spec from Stage 2:
     - Do the tests have `@jig.verifies`?
     - Do the functions have `@jig.implements`?
     - If yes, do they reference the same spec?
   - Flag mismatches

6. **Save results**
   ```json
   // dig/generated/audit/stage3_spec.json
   {
     "stage": 3,
     "name": "SPEC",
     "timestamp": "2026-01-07T19:40:00Z",
     "metrics": {
       "S3.1_decorator_coverage_impl": 0.82,
       "S3.2_decorator_coverage_verify": 0.61,
       "S3.3_mean_triangle_closure": 0.68,
       "S3.4_verification_gap": 8,
       "S3.5_granularity_variance": 4.2,
       "S3.6_mean_impl_scatter": 1.3,
       "S3.7_projection_agreement": 0.73,
       "S3.8_proto_spec_match": 0.65
     },
     "health_score": 65,
     "specs": [
       {
         "id": "S-001",
         "title": "Graph Loading",
         "implementations": ["graph.loader.load_graph"],
         "tests": ["test_graph.test_load_valid"],
         "closure": 1.0,
         "status": "healthy"
       },
       {
         "id": "S-042",
         "title": "Token Expiration",
         "implementations": ["auth.token.create", "auth.token.validate", "auth.token.refresh"],
         "tests": ["test_token.test_create"],
         "closure": 0.33,
         "status": "gap",
         "gap_functions": ["auth.token.validate", "auth.token.refresh"]
       },
       ...
     ],
     "missing_decorators": {
       "implements": [
         {"function": "src/api/handler.py:process", "proto_spec": "proto-3"}
       ],
       "verifies": [
         {"test": "tests/test_api.py:test_process", "proto_spec": "proto-3"}
       ]
     },
     "orphan_specs": ["S-089", "S-090"]
   }
   ```

7. **Return summary to orchestrator**
   ```
   Stage 3 Complete: SPEC
   Health Score: 65/100
   Triangle Closure: 68% mean
   Verification Gap: 8 specs without tests
   Proto-Spec Match: 65%
   Saved: dig/generated/audit/stage3_spec.json
   ```

---

## Stage 4: HIERARCHY

**Subagent Task:** Analyze outcome/goal structure

### Inputs Required
- Stage 3 results (spec data)
- Outcome files from `jig/outcomes/`
- Goal files from `jig/goals/` (or charter)
- Architecture files from `jig/architecture/`

### Steps

1. **Load hierarchy**
   - Parse all outcome files, extract `specifies:` lists
   - Parse goal files or charter, extract goal→outcome relationships
   - Build O→S and G→O graphs

2. **Cluster specs by implementation overlap**
   ```python
   # Use S→F from Stage 3
   # Compute Jaccard similarity between specs
   # Cluster to find natural groupings
   inferred_outcomes = cluster(spec_similarity_matrix)
   ```

3. **Compute metrics**

   | Metric | How to Compute |
   |--------|----------------|
   | H4.1 Outcome Cohesion | mean impl overlap within outcome |
   | H4.2 Outcome Coupling | mean impl overlap across outcomes |
   | H4.3 Outcome-Brick Affinity | dominant brick % per outcome |
   | H4.4 Goal Distribution | Gini(outcomes per goal) |
   | H4.5 Spec Cluster Match | ARI(inferred, declared) |
   | H4.6 Hierarchy Depth Balance | variance(specs per outcome) |
   | H4.7 Outcome Closure | mean triangle closure per outcome |

4. **Compare inferred vs declared**
   - Do specs that cluster together belong to same outcome?
   - Do outcomes with high coupling need merging?
   - Are there grab-bag outcomes (low cohesion)?

5. **Save results**
   ```json
   // dig/generated/audit/stage4_hierarchy.json
   {
     "stage": 4,
     "name": "HIERARCHY",
     "timestamp": "2026-01-07T19:45:00Z",
     "metrics": {
       "H4.1_mean_outcome_cohesion": 0.65,
       "H4.2_mean_outcome_coupling": 0.18,
       "H4.3_outcome_brick_affinity": 0.72,
       "H4.4_goal_distribution_gini": 0.42,
       "H4.5_spec_cluster_match": 0.58,
       "H4.6_hierarchy_depth_variance": 3.2,
       "H4.7_mean_outcome_closure": 0.71
     },
     "health_score": 71,
     "outcomes": [
       {
         "id": "O-015",
         "title": "Authentication Flow",
         "specs": ["S-042", "S-043", "S-044"],
         "cohesion": 0.82,
         "closure": 0.95,
         "dominant_brick": "B-auth",
         "status": "healthy"
       },
       {
         "id": "O-019",
         "title": "System Utilities",
         "specs": ["S-067", "S-068", "S-069"],
         "cohesion": 0.12,
         "closure": 0.31,
         "dominant_brick": null,
         "status": "grab-bag"
       },
       ...
     ],
     "inferred_clusters": [
       {"specs": ["S-042", "S-043", "S-044"], "suggested_outcome": "O-015"},
       {"specs": ["S-067"], "suggested_outcome": "new-outcome-1"},
       ...
     ],
     "coupling_warnings": [
       {"outcome1": "O-016", "outcome2": "O-017", "coupling": 0.67}
     ]
   }
   ```

6. **Return summary to orchestrator**
   ```
   Stage 4 Complete: HIERARCHY
   Health Score: 71/100
   Outcome Cohesion: 65% mean
   Spec Cluster Match: 58%
   Grab-bag outcomes: 2
   Saved: dig/generated/audit/stage4_hierarchy.json
   ```

---

## Stage 5: SEMANTIC (Optional)

**Subagent Task:** Validate content of flagged items using LLM

### Inputs Required
- Stage 1-4 results (flagged items)
- Spec content files
- Code content
- LLM access

### Steps

1. **Select targets**
   - All items flagged as violations in Stages 1-4
   - Top N specs by priority (low closure × high modification divergence)
   - Random sample for baseline (5-10 specs)

2. **For each target spec:**
   - Read spec content
   - Read implementing code (docstrings, function bodies)
   - Ask LLM: "Does this code match this spec?"
   - Record alignment score

3. **Check naming coherence**
   - Does spec title match spec body?
   - Does spec title follow naming conventions?
   - Flag anti-patterns (temporal words, implementation details)

4. **Compute metrics**

   | Metric | How to Compute |
   |--------|----------------|
   | M5.1 Semantic Clustering | Do LLM-summarized specs cluster like outcomes? |
   | M5.2 Topic Entropy | Topic diversity within outcomes |
   | M5.3 Name-Body Coherence | % specs where title matches content |
   | M5.4 Spec-Code Alignment | LLM assessment of match |
   | M5.5 Naming Violations | Anti-pattern count |
   | M5.6 Temporal Divergence | Specs with stale modification dates |

5. **Save results**
   ```json
   // dig/generated/audit/stage5_semantic.json
   {
     "stage": 5,
     "name": "SEMANTIC",
     "timestamp": "2026-01-07T19:50:00Z",
     "items_reviewed": 15,
     "metrics": {
       "M5.3_name_body_coherence": 0.87,
       "M5.4_spec_code_alignment": 0.74,
       "M5.5_naming_violations": 3,
       "M5.6_temporal_staleness": 4
     },
     "health_score": 79,
     "reviews": [
       {
         "spec": "S-042",
         "title": "Token Expiration",
         "alignment": 0.6,
         "issue": "Spec says 15 min, code implements 1 hour",
         "recommendation": "Update spec or fix code"
       },
       ...
     ],
     "naming_violations": [
       {"spec": "S-045", "title": "Improved Token Handling", "violation": "temporal: Improved"},
       {"spec": "S-091", "title": "Redis Cache Layer", "violation": "implementation: Redis"}
     ],
     "stale_specs": [
       {"spec": "S-023", "days_since_update": 134, "code_commits_since": 28}
     ]
   }
   ```

6. **Return summary to orchestrator**
   ```
   Stage 5 Complete: SEMANTIC
   Health Score: 79/100
   Items Reviewed: 15
   Alignment Issues: 3
   Naming Violations: 3
   Saved: dig/generated/audit/stage5_semantic.json
   ```

---

## Final Report

**Subagent Task:** Synthesize all stage results into final report

### Steps

1. **Load all stage results**
   ```python
   stage1 = load_json("dig/generated/audit/stage1_code.json")
   stage2 = load_json("dig/generated/audit/stage2_test.json")
   stage3 = load_json("dig/generated/audit/stage3_spec.json")
   stage4 = load_json("dig/generated/audit/stage4_hierarchy.json")
   stage5 = load_json("dig/generated/audit/stage5_semantic.json")  # if exists
   ```

2. **Compute overall alignment score**
   ```python
   if stage5:
       overall = (
           0.15 * stage1.health_score +
           0.20 * stage2.health_score +
           0.25 * stage3.health_score +
           0.20 * stage4.health_score +
           0.20 * stage5.health_score
       )
   else:
       overall = (
           0.20 * stage1.health_score +
           0.25 * stage2.health_score +
           0.30 * stage3.health_score +
           0.25 * stage4.health_score
       )
   ```

3. **Prioritize actions**
   - Stage 1 violations (layer/tower) = CRITICAL
   - Stage 3 triangle gaps (<50%) = HIGH
   - Stage 4 grab-bag outcomes = MEDIUM
   - Stage 5 semantic issues = MEDIUM
   - Other warnings = LOW

4. **Generate report**

   Write to `dig/generated/audit/AUDIT_REPORT.md`:

   ```markdown
   # Alignment Audit Report

   **Project:** [project name]
   **Date:** [timestamp]
   **Stages Run:** 1-4 (or 1-5)

   ## Overall Score: XX/100

   | Stage | Score | Status |
   |-------|-------|--------|
   | 1. CODE | XX/100 | ✓/✗ |
   | 2. TEST | XX/100 | ✓/✗ |
   | 3. SPEC | XX/100 | ✓/✗ |
   | 4. HIERARCHY | XX/100 | ✓/✗ |
   | 5. SEMANTIC | XX/100 | ✓/✗ |

   ## Stage Summaries

   ### Stage 1: CODE
   [summary of violations, outliers]

   ### Stage 2: TEST
   [summary of coverage, proto-specs]

   ### Stage 3: SPEC
   [summary of triangle closure, gaps]

   ### Stage 4: HIERARCHY
   [summary of cohesion, coupling]

   ### Stage 5: SEMANTIC (if run)
   [summary of semantic issues]

   ## Priority Actions

   1. [CRITICAL] ...
   2. [HIGH] ...
   3. [MEDIUM] ...

   ## Detailed Findings

   [tables of violations, gaps, recommendations]
   ```

5. **Return to orchestrator**
   ```
   Audit Complete
   Overall Alignment Score: XX/100
   Report: dig/generated/audit/AUDIT_REPORT.md
   ```

---

## Orchestrator Instructions

### Execution Order

```
1. Verify prerequisites
2. Create output directory: mkdir -p dig/generated/audit/scripts
3. Launch Stage 1 subagent → wait for completion
4. Launch Stage 2 subagent → wait for completion
5. Launch Stage 3 subagent → wait for completion
6. Launch Stage 4 subagent → wait for completion
7. (Optional) Launch Stage 5 subagent → wait for completion
8. Launch Report subagent → wait for completion
9. Return final report path to user
```

### Subagent Spawning

For each stage, spawn subagent with:
- Stage number and name
- Path to previous stage results (if applicable)
- Output path for this stage
- Clear success criteria

### Error Handling

- If a stage fails, save partial results with `"status": "failed"`
- Continue to next stage if possible
- Report subagent should handle missing stages gracefully

### Time Budget

| Stage | Expected Time |
|-------|---------------|
| Stage 1 | 1-2 minutes |
| Stage 2 | 2-5 minutes (includes pytest) |
| Stage 3 | 1-2 minutes |
| Stage 4 | 1-2 minutes |
| Stage 5 | 5-10 minutes (LLM calls) |
| Report | <1 minute |

**Total without Stage 5:** ~10 minutes
**Total with Stage 5:** ~20 minutes

---

## Notes for Implementation

1. **Scripts are optional** — Subagents can compute metrics directly using grep, file reading, and arithmetic. Scripts are for complex computations (clustering, Gini coefficients).

2. **Coverage granularity** — pytest-cov JSON gives line-level coverage. For function-level, may need to parse and aggregate.

3. **Decorator extraction** — Simple grep patterns:
   ```bash
   grep -r '@jig.implements' src/ --include='*.py'
   grep -r '@jig.verifies' tests/ --include='*.py'
   ```

4. **Clustering** — Can be approximated by manual inspection for small projects. For larger projects, write a Python script using scikit-learn.

5. **Proto-spec naming** — Derive from test file/function names and covered module names.

---

## Success Criteria

Audit is successful if:
- [ ] All 4 structural stages complete
- [ ] Each stage produces valid JSON
- [ ] Final report is generated
- [ ] No unhandled errors

Audit reveals value if:
- [ ] Triangle closure gaps identified
- [ ] Proto-specs vs declared specs compared
- [ ] Actionable priority list generated
