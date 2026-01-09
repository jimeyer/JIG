---
type: exploration
title: Stratified Alignment Verification
status: active
created: 1736308800
created_human: 2026-01-07 18:20 PST
parent: "[[C020_CONCEPT_Alignment_Integrity]]"
children:
  - "[[C023_PLAN_Five_Stage_Alignment_Audit]]"
prompt: |-
  Formalization of the 5-stage verification ladder for JIG alignment.
  Key insight: each stage provides ground truth that constrains expectations
  for the stage above. Structural verification precedes semantic validation.
  Enables both bootstrapping JIG into existing codebases and auditing
  drift/coherence in established implementations.
---

# Stratified Alignment Verification

_A layered approach to measuring alignment without reading content_

---

## The Core Principle

**Lower layers are cheaper to measure and provide constraints on what upper layers should look like.**

Each stage's health is verified by the stage below, not by reading its content. Content validation is reserved for the final stage, and only for items flagged by graph analysis.

```
Stage 5: SEMANTIC    ← LLM validates flagged content
    ↑
Stage 4: HIERARCHY   ← inferred from spec clustering
    ↑
Stage 3: SPEC        ← inferred from test clustering + entry points
    ↑
Stage 2: TEST        ← T→F from coverage report (observable)
    ↑
Stage 1: CODE        ← static analysis + brick graph (observable)
```

---

## The Five Stages

### Stage 1: CODE

**Scope:** Source code and brick model. No tests, no coverage, no JIG artifacts.

**Goal:** Assess structural health of implementation independent of intent documentation.

**Inputs:**
- Import graph (module dependencies)
- Brick assignments (layer/tower membership)
- Static analysis (complexity, LOC, linting)

**Outputs:**
- Code health score
- Layer/tower violations
- Structural anomalies (god modules, orphan code)

**Key Question:** _Is the implementation architecturally sound?_

**Ground Truth:** Code compiles/runs. Brick model is declared.

---

### Stage 2: TEST

**Scope:** Test suite and coverage report. Adds T→F graph.

**Goal:** Assess test health and coverage patterns. Identify test clustering that implies spec boundaries.

**Inputs:**
- Coverage report (pytest-cov, coverage.py)
- Test organization (directory/module structure)
- Stage 1 outputs (brick model)

**Outputs:**
- Coverage health score
- Test clusters (by coverage overlap)
- Proto-spec boundaries (inferred from clusters)
- Coverage gaps and hot spots

**Key Question:** _Do tests exercise the code coherently?_

**Ground Truth:** Tests pass. Coverage is measurable.

---

### Stage 3: SPEC

**Scope:** Specification layer. Adds S→F and S→T graphs from decorators.

**Goal:** Assess spec coverage against expectations inferred from test clusters. Compute triangle closure.

**Inputs:**
- `@jig.implements` decorators (S→F)
- `@jig.verifies` decorators (S→T)
- Stage 2 outputs (test clusters, proto-specs)

**Outputs:**
- Spec health score
- Triangle closure per spec
- Decorator coverage gaps
- Inferred vs declared spec alignment

**Key Question:** _Do specs match the structure implied by tests?_

**Ground Truth:** Decorators exist. Tests verify; code implements.

---

### Stage 4: HIERARCHY

**Scope:** Outcomes and Architecture. Adds O→S and G→O relationships.

**Goal:** Assess hierarchy shape and alignment with lower structures.

**Inputs:**
- Outcome `specifies:` fields (O→S)
- Goal support chains (G→O)
- Stage 3 outputs (spec clusters)

**Outputs:**
- Hierarchy health score
- Outcome cohesion scores
- Goal distribution balance
- Structural coherence (inferred vs declared groupings)

**Key Question:** _Does the hierarchy match natural spec clustering?_

**Ground Truth:** Intent graph links resolve. Hierarchy is declared.

---

### Stage 5: SEMANTIC

**Scope:** Content validation. Reads actual prose, uses LLM.

**Goal:** Validate semantic accuracy of flagged items from Stages 1-4.

**Inputs:**
- Flagged items (high-priority gaps, violations)
- Spec content, code docstrings, test descriptions
- LLM for semantic comparison

**Outputs:**
- Semantic health score
- Drift detections (spec doesn't match code)
- Naming violations
- Remediation suggestions

**Key Question:** _Does the content accurately describe the code?_

**Ground Truth:** Human or LLM judgment. Expensive, targeted.

---

## Stage Dependencies

```
┌─────────────────────────────────────────────────────────────────┐
│                        STAGE 5: SEMANTIC                        │
│  Validates content of flagged items using LLM                   │
│  Depends on: Stages 1-4 identify what to validate               │
└─────────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────────┐
│                       STAGE 4: HIERARCHY                        │
│  Validates O/A shape against spec clustering                    │
│  Depends on: Stage 3 provides expected spec groupings           │
└─────────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────────┐
│                         STAGE 3: SPEC                           │
│  Validates S→F, S→T against test clusters                       │
│  Depends on: Stage 2 provides test clusters, proto-specs        │
└─────────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────────┐
│                         STAGE 2: TEST                           │
│  Validates T→F graph, infers proto-specs                        │
│  Depends on: Stage 1 provides brick context for clustering      │
└─────────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────────┐
│                         STAGE 1: CODE                           │
│  Validates brick model, structural health                       │
│  Depends on: Nothing (ground truth)                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Metrics by Stage

### Stage 1: CODE Metrics

| ID | Metric | Computation | Signal |
|----|--------|-------------|--------|
| **C1.1** | Layer Violations | imports crossing layer boundary upward | Architecture broken |
| **C1.2** | Tower Isolation | imports between declared towers | Isolation violated |
| **C1.3** | Brick Cycles | strongly connected components in brick graph | Tangled concerns |
| **C1.4** | Import Fan-Out | max(distinct bricks imported per module) | God modules |
| **C1.5** | Import Fan-In | max(modules importing a given module) | Implicit shared infra |
| **C1.6** | Module Cohesion | intra-brick imports / total imports per module | Low = scattered responsibility |
| **C1.7** | Complexity Outliers | functions with cyclomatic complexity >15 | Complexity debt |
| **C1.8** | LOC Distribution | Gini coefficient of function sizes | High = uneven decomposition |

**Composite: Code Health Score**
```
code_health = (
    0.25 × (1 - violation_rate)      # C1.1, C1.2
  + 0.20 × (1 - cycle_rate)          # C1.3
  + 0.20 × (1 - fanout_outlier_rate) # C1.4
  + 0.15 × mean(module_cohesion)     # C1.6
  + 0.10 × (1 - complexity_outliers) # C1.7
  + 0.10 × (1 - gini(LOC))           # C1.8
)
```

---

### Stage 2: TEST Metrics

| ID | Metric | Computation | Signal |
|----|--------|-------------|--------|
| **T2.1** | Coverage Breadth | \|covered functions\| / \|all functions\| | Overall coverage |
| **T2.2** | Coverage Depth | mean(\|tests covering function\|) | Test redundancy |
| **T2.3** | Coverage Gini | Gini coefficient of coverage per brick | Uneven = coverage deserts |
| **T2.4** | Test Scope Distribution | histogram of \|functions per test\| | Should be bimodal |
| **T2.5** | Test-Brick Alignment | tests in `tests/X/` covering `src/X/` | Organization coherence |
| **T2.6** | Scope Bimodality | bimodality coefficient of test scope | Low = missing unit or integration |
| **T2.7** | Orphan Functions | functions with 0 test coverage | Untested code |
| **T2.8** | Hot Spots | functions covered by >10 tests | Over-tested utilities |

**Derived: Test Clusters**
```python
def compute_test_clusters(T_F):
    """Cluster tests by coverage overlap (Jaccard similarity)."""
    similarity = jaccard_matrix(T_F)
    clusters = agglomerative_clustering(similarity, threshold=0.3)
    return clusters
```

Each cluster = proto-spec boundary.

**Composite: Test Health Score**
```
test_health = (
    0.25 × coverage_breadth          # T2.1
  + 0.15 × (1 - gini(coverage))      # T2.3
  + 0.20 × bimodality_coefficient    # T2.6
  + 0.20 × test_brick_alignment      # T2.5
  + 0.10 × (1 - orphan_rate)         # T2.7
  + 0.10 × (1 - hot_spot_rate)       # T2.8
)
```

---

### Stage 3: SPEC Metrics

Maps to [[C021_CONCEPT_Alignment_Triangle_Metrics]] Categories A, B, D.

| ID | Metric | C021 Ref | Computation | Signal |
|----|--------|----------|-------------|--------|
| **S3.1** | Decorator Coverage (impl) | — | \|functions with @jig.implements\| / \|entry points\| | Implementation linkage |
| **S3.2** | Decorator Coverage (verify) | — | \|tests with @jig.verifies\| / \|focused tests\| | Verification linkage |
| **S3.3** | Triangle Closure | D1 | mean(closure per spec) | Intent-test alignment |
| **S3.4** | Verification Gap | D3 | \|implemented but not tested\| | Untested specs |
| **S3.5** | Granularity Variance | A1 | stddev(implementations per spec) | Inconsistent spec sizes |
| **S3.6** | Impl Scatter | A2 | mean(bricks per spec) | Specs crossing boundaries |
| **S3.7** | Projection Agreement | D6 | ARI(impl_clusters, verify_clusters) | Structural consistency |
| **S3.8** | Proto-Spec Match | — | overlap(inferred clusters, declared specs) | Spec boundaries correct |

**Key Inference: Proto-Spec Matching**
```python
def proto_spec_match(test_clusters, declared_specs, S_T):
    """
    Compare test clusters (Stage 2) against declared spec assignments.
    If tests in same cluster verify different specs → boundary problem.
    """
    for cluster in test_clusters:
        specs_in_cluster = {S for T in cluster for S in specs_verified_by(T)}
        if len(specs_in_cluster) > 2:
            yield IncoherenceWarning(cluster, specs_in_cluster)
```

**Coverage Thresholds:**
- Tests with `@jig.verifies`: **60-80%** is healthy (not all tests need spec linkage)
- Entry points with `@jig.implements`: **80-90%** (public API should be intentional)
- Specs with at least one test: **100%** (untested spec = untested behavior)
- Triangle closure: **>70%** healthy, **<50%** concerning

**Composite: Spec Health Score**
```
spec_health = (
    0.20 × decorator_coverage_impl   # S3.1
  + 0.15 × decorator_coverage_verify # S3.2
  + 0.25 × mean_triangle_closure     # S3.3
  + 0.15 × (1 - verification_gap)    # S3.4
  + 0.10 × (1 - granularity_var)     # S3.5
  + 0.15 × projection_agreement      # S3.7
)
```

---

### Stage 4: HIERARCHY Metrics

Maps to [[C021_CONCEPT_Alignment_Triangle_Metrics]] Category D (partial) and [[C020_CONCEPT_Alignment_Integrity]] coherence dimensions.

| ID | Metric | Source | Computation | Signal |
|----|--------|--------|-------------|--------|
| **H4.1** | Outcome Cohesion | C020 | mean impl overlap within outcome | Grab-bag outcomes |
| **H4.2** | Outcome Coupling | C020 | mean impl overlap across outcomes | Poor boundaries |
| **H4.3** | Outcome-Brick Affinity | — | mean(dominant brick % per outcome) | Arch alignment |
| **H4.4** | Goal Distribution | C020 | Gini(outcomes per goal) | Lopsided hierarchy |
| **H4.5** | Spec Cluster Match | — | ARI(spec_clusters, outcome_assignments) | Natural vs declared |
| **H4.6** | Hierarchy Depth Balance | — | variance(specs per outcome) | Consistent decomposition |
| **H4.7** | Triangle Density by Outcome | D7 | per-outcome closure scores | Outcome verification |

**Key Inference: Spec Clustering**
```python
def infer_outcomes(specs, S_F):
    """
    Cluster specs by implementation overlap.
    Each cluster = inferred outcome boundary.
    """
    overlap_matrix = jaccard_matrix(S_F)
    clusters = agglomerative_clustering(overlap_matrix, threshold=0.4)
    return clusters

def hierarchy_coherence(inferred_outcomes, declared_outcomes):
    """Compare inferred vs declared."""
    return adjusted_rand_index(inferred_outcomes, declared_outcomes)
```

**Composite: Hierarchy Health Score**
```
hierarchy_health = (
    0.20 × mean(outcome_cohesion)    # H4.1
  + 0.15 × (1 - outcome_coupling)    # H4.2
  + 0.20 × outcome_brick_affinity    # H4.3
  + 0.15 × (1 - gini(goal_dist))     # H4.4
  + 0.20 × spec_cluster_match        # H4.5
  + 0.10 × mean(outcome_closure)     # H4.7
)
```

---

### Stage 5: SEMANTIC Metrics

Maps to [[C021_CONCEPT_Alignment_Triangle_Metrics]] Category E.

| ID | Metric | C021 Ref | Computation | Signal |
|----|--------|----------|-------------|--------|
| **M5.1** | Semantic Fingerprints | E1 | cluster(embed(haiku_summary(S))) | Semantic structure |
| **M5.2** | Topic Entropy | E2 | entropy(topics per outcome) | Outcome cohesion |
| **M5.3** | Name-Body Coherence | E3 | haiku_match(title, content) | Title accuracy |
| **M5.4** | Spec-Code Alignment | E4 | haiku_compare(spec, docstrings) | Semantic drift |
| **M5.5** | Naming Violations | C020 | anti-pattern match on titles | Naming hygiene |
| **M5.6** | Temporal Divergence | C020 | spec_modified vs code_modified | Staleness |

**Targeting: Only Flagged Items**

Stage 5 does not process all artifacts. It processes:
1. Items flagged by Stages 1-4 (violations, gaps, outliers)
2. High-priority samples (high modification divergence, low closure)
3. Random sample for baseline validation

```python
def select_semantic_targets(stage_results, sample_size=10):
    """Select items for semantic validation."""
    targets = []

    # All flagged items
    targets.extend(stage_results.violations)
    targets.extend(stage_results.gaps)

    # Top N by priority score
    priority_ranked = sorted(
        stage_results.specs,
        key=lambda s: s.modification_divergence * (1 - s.closure),
        reverse=True
    )
    targets.extend(priority_ranked[:sample_size])

    # Random sample for baseline
    remaining = [s for s in stage_results.specs if s not in targets]
    targets.extend(random.sample(remaining, min(5, len(remaining))))

    return targets
```

**Composite: Semantic Health Score**
```
semantic_health = (
    0.20 × semantic_cluster_match    # M5.1 vs declared outcomes
  + 0.15 × (1 - topic_entropy)       # M5.2
  + 0.25 × name_body_coherence       # M5.3
  + 0.25 × spec_code_alignment       # M5.4
  + 0.10 × (1 - naming_violations)   # M5.5
  + 0.05 × (1 - temporal_staleness)  # M5.6
)
```

---

## Composite Alignment Score

```python
def alignment_score(stage_scores, semantic_available=True):
    """
    Compute overall alignment score from stage health scores.

    Weights emphasize structural stages (1-4) over semantic (5).
    Semantic is optional and expensive.
    """
    if semantic_available:
        return (
            0.15 × stage_scores.code          # Stage 1
          + 0.20 × stage_scores.test          # Stage 2
          + 0.25 × stage_scores.spec          # Stage 3
          + 0.20 × stage_scores.hierarchy     # Stage 4
          + 0.20 × stage_scores.semantic      # Stage 5
        )
    else:
        # Reweight without semantic
        return (
            0.20 × stage_scores.code          # Stage 1
          + 0.25 × stage_scores.test          # Stage 2
          + 0.30 × stage_scores.spec          # Stage 3
          + 0.25 × stage_scores.hierarchy     # Stage 4
        )
```

---

## The Verification Ladder

| Stage | Source of Truth | Verifies Against | Cost |
|-------|-----------------|------------------|------|
| 1. CODE | runs, compiles | brick model | O(imports) |
| 2. TEST | tests pass, coverage exists | code structure | O(coverage) |
| 3. SPEC | decorators exist | test clusters | O(decorators) |
| 4. HIERARCHY | intent graph resolves | spec clusters | O(intent graph) |
| 5. SEMANTIC | LLM judgment | flagged content | O(LLM calls) |

**Cost Model (100 specs, 500 functions, 300 tests):**

| Stage | Time | LLM Calls | Data Required |
|-------|------|-----------|---------------|
| CODE | <1s | 0 | Import graph, brick model |
| TEST | <2s | 0 | Coverage report |
| SPEC | <3s | 0 | Decorator graphs |
| HIERARCHY | <2s | 0 | Intent graph |
| SEMANTIC | ~30s | ~50 | Flagged content only |

**Total structural audit (Stages 1-4): <10s, zero LLM cost.**

---

## Command Structure

### Audit Commands

```bash
jigy audit code       # Stage 1 only
jigy audit test       # Stages 1-2
jigy audit spec       # Stages 1-3
jigy audit hierarchy  # Stages 1-4
jigy audit semantic   # All stages (expensive)
jigy audit full       # Alias for semantic

# Options
--format text|json|markdown
--coverage PATH       # Coverage report for Stage 2+
--sample N            # Semantic sample size (default: 10)
--threshold N         # Score threshold for warnings
--ci                  # CI mode: structural only, strict exit codes
```

### Bootstrap Commands

```bash
jigy bootstrap infer      # Run Stages 1-2, output proto-specs
jigy bootstrap suggest    # Suggest decorator placements
jigy bootstrap generate   # LLM-generate spec drafts (requires approval)

# Options
--coverage PATH           # Required: coverage report
--output PATH             # Output suggestions to file
--dry-run                 # Show what would be created
```

---

## Use Cases

### Use Case 1: Audit Existing JIG

```bash
# Quick structural check (Stages 1-4, <10s)
jigy audit hierarchy --coverage .coverage.json

# Full audit with semantic validation
jigy audit full --coverage .coverage.json --sample 20
```

**Output:**
```
STRATIFIED ALIGNMENT AUDIT
==========================
Project: my-project
Date: 2026-01-07

STAGE 1: CODE
─────────────
Health Score: 87/100
Violations: 2 layer violations, 0 tower violations
Outliers: 3 high-complexity functions

STAGE 2: TEST
─────────────
Health Score: 72/100
Coverage: 78%
Test Clusters: 23 (proto-specs inferred)
Gaps: 12 functions with 0 coverage

STAGE 3: SPEC
─────────────
Health Score: 65/100
Decorator Coverage: impl=82%, verify=61%
Triangle Closure: 68% mean
Verification Gap: 8 specs with no tests
Proto-Spec Match: 0.73 (moderate alignment)

STAGE 4: HIERARCHY
──────────────────
Health Score: 71/100
Outcome Cohesion: 0.65 mean
Goal Distribution: Gini=0.42 (moderate)
Cluster Match: 0.58 (inferred differs from declared)

STAGE 5: SEMANTIC (15 items sampled)
────────────────────────────────────
Health Score: 79/100
Name-Body Coherence: 91%
Spec-Code Alignment: 74%
Temporal Staleness: 3 specs >90 days divergent

OVERALL ALIGNMENT SCORE: 73/100

PRIORITY ACTIONS
────────────────
1. [STAGE 3] Add @jig.verifies to 12 tests (low verify coverage)
2. [STAGE 3] Fix triangle gaps: S-042, S-067 (<50% closure)
3. [STAGE 4] Review O-019: low cohesion, high topic entropy
4. [STAGE 5] Update stale specs: S-023, S-034, S-089
```

### Use Case 2: Bootstrap New Codebase

```bash
# Step 1: Run tests with coverage
pytest --cov=src --cov-report=json

# Step 2: Infer proto-specs from test clusters
jigy bootstrap infer --coverage coverage.json --output proto-specs.json

# Step 3: Review and refine proto-specs
# (human reviews proto-specs.json, adjusts boundaries)

# Step 4: Generate decorator suggestions
jigy bootstrap suggest --proto proto-specs.json --output decorators.md

# Step 5: Apply decorators, create spec files
# (human applies suggestions, creates spec markdown files)

# Step 6: LLM-assist spec content (optional)
jigy bootstrap generate --specs jig/specifications/ --sample 10
```

**Bootstrap Output (proto-specs.json):**
```json
{
  "proto_specs": [
    {
      "id": "proto-1",
      "test_cluster": ["test_auth.test_login", "test_auth.test_logout"],
      "covered_functions": ["auth.session.login", "auth.session.logout"],
      "suggested_entry_points": ["auth.session.login", "auth.session.logout"],
      "suggested_name": "Session Lifecycle",
      "confidence": 0.85
    },
    {
      "id": "proto-2",
      "test_cluster": ["test_token.test_create", "test_token.test_validate"],
      "covered_functions": ["auth.token.create", "auth.token.validate", "auth.token._hash"],
      "suggested_entry_points": ["auth.token.create", "auth.token.validate"],
      "suggested_name": "Token Management",
      "confidence": 0.91
    }
  ]
}
```

---

## CI Integration

```yaml
# .github/workflows/jig-audit.yml
jobs:
  jig-structural:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=json

      - name: Structural Audit (Stages 1-4)
        run: jigy audit hierarchy --coverage coverage.json --ci
        # Fails on: layer violations, orphan specs, broken chains
        # Warns on: low coverage, triangle gaps, hierarchy imbalance

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: jig-audit
          path: jig-audit.json

  jig-semantic:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    needs: jig-structural
    steps:
      - name: Semantic Audit (Stage 5)
        run: jigy audit semantic --coverage coverage.json --sample 5
        # Advisory only, does not block merge
```

**CI Philosophy:**
- **Structural (Stages 1-4)**: Fast, cheap, blocks on violations
- **Semantic (Stage 5)**: Slow, expensive, advisory only

---

## The Key Insight Restated

Tests are evidence of intended behavior. If a test exists and exercises code, there's probably a reason. That reason should be a spec (or should become one).

The T→F graph implies an expected S graph:
- Test clusters → spec boundaries
- Covered entry points → decorated functions
- Test organization → outcome structure

By computing expectations from lower stages before reading upper stages, we can:
1. **Bootstrap**: Generate JIG structure from existing code/tests
2. **Audit**: Detect drift between declared and inferred structure
3. **Prioritize**: Focus expensive semantic validation on discrepancies

---

## Relation to Prior Concepts

| Document | Contribution | This Document Adds |
|----------|--------------|-------------------|
| [[C020_CONCEPT_Alignment_Integrity]] | Drift vs coherence distinction | Stage-based verification order |
| [[C021_CONCEPT_Alignment_Triangle_Metrics]] | Triangle metrics (S↔F↔T) | Stage assignment, inference methods |
| **C022 (this)** | — | Stratified verification, bootstrap flow |

C020 asked: "Are artifacts accurate? Are they clear?"
C021 asked: "How do we measure alignment computationally?"
C022 asks: "In what order should we verify, and what can we infer?"

---

## Open Questions

1. **Threshold calibration**: What decorator coverage % is "healthy"? What triangle closure is acceptable? Need empirical data from real projects.

2. **Test type handling**: Integration tests naturally have wide scope. Should they be weighted differently in clustering? Maybe require `@jig.integration` marker?

3. **Private functions**: Not all code needs specs. How to distinguish "intentionally unspecified utility" from "missing spec"? Perhaps brick-level spec density expectations?

4. **Bootstrap cold start**: For codebases with poor test coverage, Stage 2 can't infer proto-specs. Fallback strategy needed.

5. **Proto-spec granularity**: How many clusters is right? Too few = specs too coarse. Too many = specs too fine. May need configurable clustering threshold.

6. **Incremental audit**: Can we audit only changed artifacts? Stages 1-2 probably yes, Stages 3-4 need full graph for coupling metrics.

---

## Next Steps

1. **Implement Stage 1** — Brick violation detection, complexity analysis
2. **Implement Stage 2** — Coverage parsing, test clustering
3. **Implement Stage 3** — Decorator extraction, triangle closure
4. **Prototype bootstrap** — `jigy bootstrap infer` with proto-spec output
5. **Calibrate thresholds** — Run on JIG codebase, compare to intuition
6. **Define O-028+** — Decompose into implementable specs

---

## Appendix: Metric Summary Table

| Stage | ID | Metric | C021 Ref |
|-------|----|--------|----------|
| CODE | C1.1 | Layer Violations | — |
| CODE | C1.2 | Tower Isolation | — |
| CODE | C1.3 | Brick Cycles | — |
| CODE | C1.4 | Import Fan-Out | — |
| CODE | C1.5 | Import Fan-In | — |
| CODE | C1.6 | Module Cohesion | — |
| CODE | C1.7 | Complexity Outliers | — |
| CODE | C1.8 | LOC Distribution | — |
| TEST | T2.1 | Coverage Breadth | C1 |
| TEST | T2.2 | Coverage Depth | C2 |
| TEST | T2.3 | Coverage Gini | — |
| TEST | T2.4 | Test Scope Distribution | C3 |
| TEST | T2.5 | Test-Brick Alignment | — |
| TEST | T2.6 | Scope Bimodality | — |
| TEST | T2.7 | Orphan Functions | D2 |
| TEST | T2.8 | Hot Spots | C4 |
| SPEC | S3.1 | Decorator Coverage (impl) | — |
| SPEC | S3.2 | Decorator Coverage (verify) | — |
| SPEC | S3.3 | Triangle Closure | D1 |
| SPEC | S3.4 | Verification Gap | D3 |
| SPEC | S3.5 | Granularity Variance | A1 |
| SPEC | S3.6 | Impl Scatter | A2 |
| SPEC | S3.7 | Projection Agreement | D6 |
| SPEC | S3.8 | Proto-Spec Match | — |
| HIERARCHY | H4.1 | Outcome Cohesion | — |
| HIERARCHY | H4.2 | Outcome Coupling | — |
| HIERARCHY | H4.3 | Outcome-Brick Affinity | — |
| HIERARCHY | H4.4 | Goal Distribution | — |
| HIERARCHY | H4.5 | Spec Cluster Match | — |
| HIERARCHY | H4.6 | Hierarchy Depth Balance | — |
| HIERARCHY | H4.7 | Triangle Density by Outcome | D7 |
| SEMANTIC | M5.1 | Semantic Fingerprints | E1 |
| SEMANTIC | M5.2 | Topic Entropy | E2 |
| SEMANTIC | M5.3 | Name-Body Coherence | E3 |
| SEMANTIC | M5.4 | Spec-Code Alignment | E4 |
| SEMANTIC | M5.5 | Naming Violations | — |
| SEMANTIC | M5.6 | Temporal Divergence | — |

