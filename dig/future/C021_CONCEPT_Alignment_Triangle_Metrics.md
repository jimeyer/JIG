---
type: exploration
title: Alignment Triangle Metrics
status: active
created: 1736304000
created_human: 2026-01-07 17:00 PST
parent: "[[jig-dev/dig/future/C020_CONCEPT_Alignment_Integrity]]"
children: []
prompt: |
  Discussion of computational approaches to coherence assessment.
  Key insight: JIG has three bipartite graphs forming an alignment triangle:
    S→F (implements), S→T (verifies), T→F (covers)
  The third edge (coverage) closes the triangle and enables new metrics.
  Goal: rapid assessment using graph structure + optional small model augmentation.
---

# Alignment Triangle Metrics

_Graph-based coherence assessment through the S↔F↔T triangle_

---

## The Core Insight

JIG's alignment model is fundamentally a **triangle** of three bipartite graphs:

```
                    SPECIFICATIONS (S)
                         /    \
                        /      \
              implements        verifies
                      /          \
                     /            \
                    ↓              ↓
            FUNCTIONS (F) ←————→ TESTS (T)
                          covers
```

Each edge is a bipartite graph:

| Graph | Relation | Source | Declared Via |
|-------|----------|--------|--------------|
| **S→F** | implements | Decorators | `@jig.implements("S-###")` |
| **S→T** | verifies | Decorators | `@jig.verifies("S-###")` |
| **T→F** | covers | Runtime | Coverage report (pytest-cov, etc.) |

The first two edges are **declared intent**. The third is **observed behavior**. When all three align, the triangle closes cleanly. When they don't, coherence fractures.

---

## Why the Triangle Matters

### Declared vs Observed

S→F and S→T are human declarations: "This code implements this spec. This test verifies this spec."

T→F is machine-observed: "This test actually executes these functions."

The triangle lets us verify that declarations match reality:

```
If T verifies S, and S is implemented by F,
then T should cover F.

If T covers F but doesn't verify any S that F implements,
the coverage is accidental—not intentional verification.
```

### The Three Failures

| Failure | Pattern | Meaning |
|---------|---------|---------|
| **Open top** | F←T exists, S missing | Tests exercise code, but intent is undeclared |
| **Open left** | S→T exists, F missing | Spec has tests but no implementation |
| **Open right** | S→F exists, T missing | Spec implemented but not verified |
| **Open bottom** | S→F, S→T exist, T→F missing | Tests don't actually cover the implementation |
| **Twisted** | All edges exist but don't align | Everything exists, nothing coheres |

---

## The Graphs in Detail

### Graph 1: S→F (Specification → Function)

**Source:** `@jig.implements("S-###")` decorators in source code.

**Structure:**
```
S-042 ──implements──→ auth.token.create_token
S-042 ──implements──→ auth.token.validate_token
S-042 ──implements──→ auth.token.refresh_token
S-043 ──implements──→ auth.session.create_session
```

**Properties:**
- Many-to-many (spec can have multiple implementations, function can implement multiple specs)
- Relatively sparse (not every function has a decorator)
- Hierarchical clustering expected (specs in same outcome should share implementation structure)

**Derived metrics:**
- Implementations per spec (granularity)
- Specs per function (responsibility scatter)
- Brick distribution per spec (architectural alignment)

---

### Graph 2: S→T (Specification → Test)

**Source:** `@jig.verifies("S-###")` decorators in test code.

**Structure:**
```
S-042 ──verifies──→ test_token.test_create_token
S-042 ──verifies──→ test_token.test_token_expiration
S-042 ──verifies──→ test_token.test_refresh_flow
S-043 ──verifies──→ test_session.test_session_creation
```

**Properties:**
- Many-to-many
- Should parallel S→F structure (same specs, different targets)
- Test organization may differ from implementation organization

**Derived metrics:**
- Tests per spec (verification depth)
- Specs per test (test focus)
- Verification coverage (% specs with tests)

---

### Graph 3: T→F (Test → Function)

**Source:** Runtime coverage reports.

**Structure:**
```
test_token.test_create_token ──covers──→ auth.token.create_token
test_token.test_create_token ──covers──→ auth.token._internal_hash
test_token.test_create_token ──covers──→ auth.token.validate_token
test_token.test_token_expiration ──covers──→ auth.token.create_token
test_token.test_token_expiration ──covers──→ auth.token._check_expiry
```

**Properties:**
- Dense (tests typically cover many functions)
- Includes internal/private functions not decorated
- Captures actual execution paths, not declared intent

**Derived metrics:**
- Functions per test (test scope)
- Tests per function (coverage depth)
- Coverage distribution (hot spots and cold spots)

---

## Graph Projections

Each bipartite graph can be projected onto either node set, creating similarity graphs.

### Implementation Similarity (project S→F onto S×S)

Two specs are similar if they share implementing functions:

```
sim_impl(S-042, S-043) = |F(S-042) ∩ F(S-043)| / |F(S-042) ∪ F(S-043)|
```

**Insight:** Specs that share implementation are functionally coupled. This should correlate with being in the same outcome.

---

### Verification Similarity (project S→T onto S×S)

Two specs are similar if they share verifying tests:

```
sim_verify(S-042, S-043) = |T(S-042) ∩ T(S-043)| / |T(S-042) ∪ T(S-043)|
```

**Insight:** Specs verified by the same tests are coupled from a testing perspective. May indicate test is too broad, or specs are inherently related.

---

### Test Similarity (project T→F onto T×T)

Two tests are similar if they cover the same functions:

```
sim_cover(T1, T2) = |F(T1) ∩ F(T2)| / |F(T1) ∪ F(T2)|
```

**Insight:** Tests with high coverage overlap may be redundant, or may test related behaviors.

---

### Function Similarity (project T→F onto F×F)

Two functions are similar if they're covered by the same tests:

```
sim_tested(F1, F2) = |T(F1) ∩ T(F2)| / |T(F1) ∪ T(F2)|
```

**Insight:** Functions covered together are behaviorally coupled. This is a proxy for runtime coupling that doesn't require call graph analysis.

---

### Projection Comparison

**Key coherence signal:** Do different projections agree?

```
impl_clusters = cluster(sim_impl matrix)
verify_clusters = cluster(sim_verify matrix)
coverage_clusters = cluster(project T→F→S matrix)

agreement_impl_verify = adjusted_rand_index(impl_clusters, verify_clusters)
agreement_impl_coverage = adjusted_rand_index(impl_clusters, coverage_clusters)
```

If projections cluster differently, the triangle is incoherent.

---

## The 19 Metrics

### Category A: Single-Graph Metrics (S→F)

| # | Metric | Computation | Signal |
|---|--------|-------------|--------|
| A1 | **Granularity Distribution** | histogram(|F(S)|) | Inconsistent spec sizes |
| A2 | **Implementation Scatter** | mean(bricks_per_spec) | Specs crossing boundaries |
| A3 | **Code Responsibility** | mean(specs_per_function) | Fragmented functions |
| A4 | **Implementation Overlap** | Jaccard matrix on F(S) | Natural spec clustering |
| A5 | **Bipartite Modularity (impl)** | modularity(S→F, outcomes) | Outcome-structure fit |

---

### Category B: Single-Graph Metrics (S→T)

| # | Metric | Computation | Signal |
|---|--------|-------------|--------|
| B1 | **Verification Depth** | histogram(|T(S)|) | Testing thoroughness |
| B2 | **Test Scatter** | mean(bricks_per_test) | Test organization |
| B3 | **Test Focus** | mean(specs_per_test) | Test breadth |
| B4 | **Verification Overlap** | Jaccard matrix on T(S) | Natural test clustering |
| B5 | **Bipartite Modularity (verify)** | modularity(S→T, outcomes) | Outcome-test fit |

---

### Category C: Single-Graph Metrics (T→F)

| # | Metric | Computation | Signal |
|---|--------|-------------|--------|
| C1 | **Coverage Breadth** | |F covered| / |F total| | Overall coverage |
| C2 | **Coverage Depth** | mean(|T(F)|) | Test redundancy |
| C3 | **Test Scope** | mean(|F(T)|) | Test granularity |
| C4 | **Coverage Hot Spots** | top_k(|T(F)|) | Over-tested code |
| C5 | **Coverage Cold Spots** | bottom_k(|T(F)|) | Under-tested code |

---

### Category D: Cross-Graph Metrics (Triangle Analysis)

| # | Metric | Computation | Signal |
|---|--------|-------------|--------|
| D1 | **Triangle Closure** | |F(S) ∩ covered_by(T(S))| / |F(S)| | Intent-test alignment |
| D2 | **Orphan Functions** | covered - implements_any | Tested but unspecified |
| D3 | **Orphan Coverage** | implements_any - covered | Specified but untested |
| D4 | **Impl/Verify Ratio** | |T(S)| / |F(S)| per spec | Testing balance |
| D5 | **Cross-Graph Brick Consistency** | KL(impl_bricks, test_bricks) | Org alignment |
| D6 | **Projection Agreement** | ARI(impl_clusters, verify_clusters) | Structural consistency |
| D7 | **Triangle Density by Outcome** | per-outcome closure scores | Outcome verification |

---

### Category E: Semantic Metrics (Haiku-Augmented)

| # | Metric | Computation | Signal |
|---|--------|-------------|--------|
| E1 | **Semantic Fingerprints** | embed(haiku_summary(S)) → cluster | Semantic structure |
| E2 | **Topic Classification** | haiku_topic(S) → entropy per outcome | Outcome cohesion |
| E3 | **Name-Body Coherence** | haiku_match(title, content) | Title accuracy |
| E4 | **Spec-Code Alignment** | haiku_compare(spec, docstrings) | Semantic drift |

---

## Triangle Closure Analysis

The most important triangle metric. For each spec:

```python
def triangle_closure(spec):
    implementations = F(spec)           # Functions claiming to implement
    tests = T(spec)                     # Tests claiming to verify
    covered = union(coverage(t) for t in tests)  # What tests actually cover

    # How much of the implementation is actually tested?
    closure = len(implementations & covered) / len(implementations)

    # What's covered but not claimed as implementation?
    accidental = covered - implementations

    # What's implemented but not covered by spec's tests?
    gap = implementations - covered

    return {
        "closure": closure,
        "accidental_coverage": accidental,
        "verification_gap": gap
    }
```

### Closure Patterns

```
PERFECT TRIANGLE (closure = 1.0)
================================
S-042
  ├── implements: {f1, f2, f3}
  └── verifies: {T1, T2}
        └── covers: {f1, f2, f3, f4}  ← Superset of implementations ✓

VERIFICATION GAP (closure < 1.0)
================================
S-043
  ├── implements: {f1, f2, f3, f4, f5}
  └── verifies: {T1}
        └── covers: {f1, f2}  ← Only covers 2/5 ✗

GAP: {f3, f4, f5} are implemented but not covered by S-043's tests.
     May be covered by other tests, but not linked to this spec.

TWISTED TRIANGLE (accidental > 0)
=================================
S-044
  ├── implements: {f1, f2}
  └── verifies: {T1, T2}
        └── covers: {f1, f2, f3, f4, f5, f6}  ← Covers much more

ACCIDENTAL: {f3, f4, f5, f6} covered but not part of S-044.
            Either:
            - Missing @jig.implements on f3-f6
            - Tests are too broad (integration tests)
            - Specs are too narrow
```

### Aggregate Closure Metrics

```python
closure_scores = [triangle_closure(s)["closure"] for s in specs]

metrics = {
    "mean_closure": mean(closure_scores),
    "min_closure": min(closure_scores),
    "fully_closed": sum(1 for c in closure_scores if c == 1.0) / len(specs),
    "critical_gaps": [s for s in specs if closure(s) < 0.5]
}
```

---

## The Alignment Tensor

Think of the triangle as a 3D space:

```
Dimension 1: Specifications (S)
Dimension 2: Functions (F)
Dimension 3: Tests (T)
```

Each valid triple (s, f, t) where:
- f implements s
- t verifies s
- t covers f

...is a point in this tensor.

### Tensor Properties

**Density:** `|valid triples| / (|S| × |F| × |T|)`

Very sparse in practice. But the pattern of sparsity is informative.

**Slices:**
- Fix S: See which (F, T) pairs are connected for this spec
- Fix F: See which (S, T) pairs relate to this function
- Fix T: See which (S, F) pairs this test touches

**Projections:**
- Project onto S×F: The implementation graph (with test info lost)
- Project onto S×T: The verification graph (with coverage info lost)
- Project onto F×T: The coverage graph (with intent info lost)

### Tensor Coherence

A coherent codebase has a tensor where:
- Each spec slice is "compact" (not spread across too many F or T)
- Each function slice has few specs (clear responsibility)
- Each test slice has focused specs (not testing everything)
- Valid triples cluster (related things are related in all three dimensions)

---

## Hypergraph View

Each (S, F, T) triple can be viewed as a hyperedge connecting three nodes.

```
Hyperedge H1: {S-042, auth.token.create, test_token_create}
Hyperedge H2: {S-042, auth.token.validate, test_token_expiry}
Hyperedge H3: {S-043, auth.session.create, test_session}
```

### Hypergraph Metrics

**Hyperedge degree of S:** How many distinct (F, T) pairs connect to this spec?
- High degree = complex spec with many implementation-test combinations
- Low degree = focused spec

**Hyperedge clustering:** Do hyperedges "clump" in the tensor?
- Coherent: Hyperedges form distinct clusters
- Incoherent: Hyperedges spread uniformly

**Missing hyperedges:** Where (S, F) exists and (S, T) exists, but (F, T) doesn't?
- These are the triangle closure gaps
- The "should be tested but isn't" situations

---

## Network Analysis on the Triangle

### Small-World Properties

Construct the unified graph: S ∪ F ∪ T with all three edge types.

Compute:
- Average path length
- Clustering coefficient
- Small-world index (σ = C/C_random × L_random/L)

**Insight:** A well-structured codebase should have small-world properties:
- High clustering (related things are near each other)
- Short paths (everything reachable)

If the graph is too clustered (components disconnected) or too random (no structure), coherence suffers.

---

### Community Detection

Run community detection (Louvain, etc.) on the unified graph.

Compare detected communities to:
- Declared outcomes
- Brick assignments
- Module structure

```
Detected communities: 7
Declared outcomes: 26
Declared bricks: 12

Community-Outcome alignment: NMI = 0.45
Community-Brick alignment: NMI = 0.72

→ Natural structure aligns with architecture better than intent.
```

---

### Centrality Analysis

**Betweenness centrality on specs:** Which specs are "bridges" between otherwise separate clusters?

```
High-centrality specs:
  S-001 (Config Loading): Connects all bricks
  S-012 (Error Handling): Connects all outcomes

→ These are cross-cutting concerns. Expect high scatter.
```

**Betweenness centrality on functions:** Which functions are architectural chokepoints?

```
High-centrality functions:
  core.graph.load_graph: 0.34
  utils.config.get: 0.28

→ Many tests and specs flow through these.
```

---

## Information-Theoretic Metrics

### Mutual Information

How much information does one graph give about another?

```
I(S→F ; S→T) = How much does knowing implementations tell you about tests?
I(S→F ; T→F) = How much does knowing implementations tell you about coverage?
I(S→T ; T→F) = How much does knowing verification tell you about coverage?
```

High mutual information = graphs are consistent.
Low mutual information = graphs are independent (incoherent).

---

### Entropy Analysis

**Spec entropy over functions:**
```
H(F|S) = -Σ p(f|s) log p(f|s)
```
High entropy = specs spread across many functions.

**Outcome entropy over bricks:**
```
H(B|O) = -Σ p(b|o) log p(b|o)
```
High entropy = outcomes spread across many bricks.

**Joint entropy:**
```
H(S, F, T) = entropy of the tensor
```
Measures total "disorder" in the triangle.

---

### Compression Ratio

Conceptually: How compressible is the triangle?

If specs cleanly partition into outcomes, and outcomes map to bricks, and tests follow implementations, the triangle should be highly compressible.

```
raw_size = |S→F edges| + |S→T edges| + |T→F edges|
compressed_size = represent using outcome+brick structure

compression_ratio = raw_size / compressed_size
```

High ratio = structure is regular, coherent.
Low ratio = structure is irregular, incoherent.

---

## Rapid Assessment Pipeline

### Phase 1: Graph Construction (< 1s)

```python
# Already have from JIG
impl_graph = load_ndjson("implementation-graph.ndjson")
intent_graph = load_ndjson("intent-graph.ndjson")
verify_graph = load_ndjson("verification-graph.ndjson")

# Need to generate
coverage_graph = parse_coverage_report("coverage.json")

# Build bipartite graphs
S_F = build_bipartite(impl_graph, "implements")
S_T = build_bipartite(verify_graph, "verifies")
T_F = build_bipartite(coverage_graph, "covers")
```

---

### Phase 2: Pure Graph Metrics (< 2s)

```python
metrics = {}

# Category A: S→F metrics
metrics["A1_granularity"] = distribution_stats([len(F(s)) for s in specs])
metrics["A2_impl_scatter"] = mean([brick_entropy(s) for s in specs])
metrics["A3_code_responsibility"] = mean([len(S(f)) for f in functions])
metrics["A4_impl_overlap"] = jaccard_matrix(S_F)
metrics["A5_impl_modularity"] = bipartite_modularity(S_F, outcomes)

# Category B: S→T metrics (parallel)
metrics["B1_verify_depth"] = distribution_stats([len(T(s)) for s in specs])
# ... etc

# Category C: T→F metrics
metrics["C1_coverage_breadth"] = len(covered_functions) / len(all_functions)
# ... etc

# Category D: Triangle metrics
metrics["D1_triangle_closure"] = mean([closure(s) for s in specs])
metrics["D2_orphan_functions"] = len(covered - implements_any)
metrics["D6_projection_agreement"] = adjusted_rand_index(
    cluster(impl_overlap), cluster(verify_overlap)
)
```

---

### Phase 3: Semantic Augmentation (< 15s, optional)

```python
# Only if enabled and Haiku available

# E1: Semantic fingerprints
fingerprints = [haiku_summarize(s, max_words=5) for s in specs]
embeddings = embed(fingerprints)
semantic_clusters = cluster(embeddings)
metrics["E1_semantic_structure"] = adjusted_rand_index(semantic_clusters, outcomes)

# E2: Topic classification
topics = [haiku_classify_topic(s) for s in specs]
metrics["E2_topic_entropy"] = mean([entropy(topics_in(o)) for o in outcomes])

# E3: Name-body coherence
metrics["E3_name_body"] = mean([haiku_title_matches_body(s) for s in specs])
```

---

### Phase 4: Composite Score (< 1s)

```python
# Weights (tunable)
weights = {
    "graph_structure": 0.40,
    "triangle_closure": 0.25,
    "cross_graph": 0.20,
    "semantic": 0.15,
}

scores = {
    "graph_structure": combine(A1-A5, B1-B5, C1-C5),
    "triangle_closure": combine(D1-D4),
    "cross_graph": combine(D5-D7),
    "semantic": combine(E1-E4) if available else None,
}

coherence_score = weighted_average(scores, weights)
```

---

## Output: Triangle Coherence Report

```
ALIGNMENT TRIANGLE ANALYSIS
===========================
Project: jig-dev
Date: 2026-01-07

GRAPH STATISTICS
----------------
Specifications: 91
Functions: 456
Tests: 234

Edges:
  S→F (implements): 312
  S→T (verifies): 187
  T→F (covers): 8,432

TRIANGLE CLOSURE
----------------
Mean closure: 0.71
Fully closed specs: 45/91 (49%)
Critical gaps (<50% closure): 12 specs

Top gaps:
  S-042: closure 0.32 (5 functions, only 2 covered by its tests)
  S-067: closure 0.40 (10 functions, only 4 covered)
  S-089: closure 0.00 (3 functions, no verifying tests)

ORPHAN ANALYSIS
---------------
Orphan functions (covered but unspecified): 23
  auth/legacy.py:validate_old_token
  api/compat.py:handle_v1_request
  ...

Orphan coverage (specified but untested): 8 specs
  S-089, S-090, S-091, ...

PROJECTION AGREEMENT
--------------------
Implementation clusters: 8
Verification clusters: 11
Coverage clusters: 6

ARI (impl ↔ verify): 0.67 [MODERATE]
ARI (impl ↔ coverage): 0.52 [LOW]
ARI (verify ↔ coverage): 0.61 [MODERATE]

→ Test organization differs from implementation structure.

CROSS-GRAPH CONSISTENCY
-----------------------
Mean brick divergence (impl ↔ test): KL = 0.28 [OK]
Specs with high divergence (KL > 0.5):
  S-042: impl in B-auth, tests in B-integration
  S-023: impl in B-cache, tests in B-api

OUTCOME TRIANGLES
-----------------
           S→F    S→T    Closure   Verdict
O-015      100%   100%   0.95      ✓ Solid
O-016       95%    80%   0.72      ~ Gaps
O-019       80%    40%   0.31      ✗ Desert
O-022      100%    90%   0.88      ✓ Good
O-025       70%     0%   0.00      ✗ No tests

SEMANTIC ANALYSIS (Haiku-augmented)
-----------------------------------
Topic entropy by outcome:
  O-015 "Auth Flow": 0.12 [LOW] ✓ Cohesive
  O-019 "Utilities": 0.89 [HIGH] ✗ Grab-bag
  O-022 "Caching": 0.23 [LOW] ✓ Cohesive

Name-body coherence: 87% of specs match

COHERENCE SCORES
----------------
Graph Structure:    68/100
Triangle Closure:   52/100
Cross-Graph:        71/100
Semantic:           79/100
─────────────────────────
Overall:            65/100

PRIORITY ACTIONS
----------------
1. [CRITICAL] Add tests for S-089, S-090, S-091 (0% closure)
2. [HIGH] Fix triangle gaps in S-042, S-067 (<50% closure)
3. [MEDIUM] Reorganize O-019 (high topic entropy, low cohesion)
4. [MEDIUM] Add @jig.implements to orphan functions (23 unclaimed)
5. [LOW] Align test organization with implementation bricks
```

---

## Visualization Concepts

### The Triangle Dashboard

```
┌────────────────────────────────────────────────────────────────┐
│                    ALIGNMENT TRIANGLE                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│              S (91)                                            │
│             /╲    ╲                                            │
│            /  ╲    ╲                                           │
│     312   /    ╲    ╲  187                                     │
│          /      ╲    ╲                                         │
│         /        ╲    ╲                                        │
│        ↓          ╲    ↓                                       │
│     F (456) ←──────────→ T (234)                               │
│              8,432                                             │
│                                                                │
│   Triangle Closure: ████████████░░░░░░ 71%                     │
│   Projection Agreement: ████████░░░░░░░░ 58%                   │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  OVERLAP MATRICES                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ S×S (impl)  │  │ S×S (verify)│  │ Agreement   │            │
│  │▓▓▒░░░░░░░░░│  │▓▓▓░░░░░░░░░│  │▓░▒░░░░░░░░░│            │
│  │▒▓▓▒░░░░░░░░│  │▓▓▓▒░░░░░░░░│  │░▓░▒░░░░░░░░│            │
│  │░▒▓▓▓░░░░░░░│  │░▒▓▓░░░░░░░░│  │▒░▓░░░░░░░░░│            │
│  │░░▓▓▓▓░░░░░░│  │░░░▓▓▓░░░░░░│  │░▒░▓▓░░░░░░░│            │
│  │░░░░▓▓▒░░░░░│  │░░░░▓▓▒░░░░░│  │░░░▓▓▓░░░░░░│            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  Clusters: 8        Clusters: 11    ARI: 0.67                  │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  OUTCOME HEALTH                    CLOSURE DISTRIBUTION        │
│  ┌────────────────────────┐        ┌────────────────────┐     │
│  │O-015 ████████████ 95%  │        │                    │     │
│  │O-016 ███████░░░░░ 72%  │        │    ▁▂▃▄▅▆▇█       │     │
│  │O-019 ███░░░░░░░░░ 31%  │        │    0%      100%   │     │
│  │O-022 █████████░░░ 88%  │        │                    │     │
│  │O-025 ░░░░░░░░░░░░  0%  │        │    Mean: 71%       │     │
│  └────────────────────────┘        └────────────────────┘     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Sankey Diagram: Outcome → Brick → Test Module

```
Outcomes          Bricks           Test Modules
─────────         ──────           ────────────
O-015 ═══════════► B-auth ════════► tests/auth/
     ╲            ╱      ╲
      ╲          ╱        ╲
O-016 ══════════► B-api ═══════════► tests/api/
              ╲  ╱  ╲
               ╲╱    ╲
O-019 ══════════► B-cache ═════════► tests/integration/
      ╲         ╱
       ╲       ╱
        ╲     ╱
         ► B-utils ════════════════► tests/unit/
```

Clean flow = coherent. Spaghetti = incoherent.

### Force-Directed Graph

Render S, F, T as nodes. Color by:
- S: outcome membership
- F: brick membership
- T: test module

Force-directed layout should show:
- Specs cluster by outcome
- Functions cluster by brick
- Tests cluster by module
- Triangle edges pull related items together

If visual clusters match declared structure, coherence is high.

---

## Cost Model

| Phase | Time (100 specs) | API Calls | Data Required |
|-------|------------------|-----------|---------------|
| Graph construction | <1s | 0 | NDJSON graphs + coverage |
| Pure graph metrics | <2s | 0 | Graphs only |
| Projections & clustering | <3s | 0 | Graphs only |
| Network analysis | <5s | 0 | Graphs only |
| Semantic fingerprints | ~10s | 100 | Spec content |
| Topic classification | ~10s | 100 | Spec content |
| Full semantic analysis | ~30s | 300 | All content |

**Sweet spot:** Pure graph metrics + fingerprints = ~15s, high signal, low cost.

---

## Implementation Notes

### Dependencies

```python
# Graph operations
import networkx as nx
from scipy import sparse
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_index

# Already have
from jig.graphs import load_impl_graph, load_intent_graph, load_verify_graph

# Need to add
from coverage import CoverageData  # or parse pytest-cov JSON
```

### Data Flow

```
┌─────────────────────┐
│ implementation.ndjson│
│ verification.ndjson  │──────► Build bipartite graphs
│ intent.ndjson        │              │
└─────────────────────┘              │
                                     ▼
┌─────────────────────┐        ┌──────────────┐
│ coverage.json       │───────►│ Triangle     │
│ (pytest-cov output) │        │ Constructor  │
└─────────────────────┘        └──────┬───────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │ Metrics      │
                               │ Calculator   │
                               └──────┬───────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
       Pure Graph             Triangle              Semantic
       Metrics                Metrics               Metrics
       (A1-C5)               (D1-D7)               (E1-E4)
              │                       │                       │
              └───────────────────────┴───────────────────────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │ Coherence    │
                               │ Score        │
                               └──────────────┘
```

### Proposed Command

```bash
jigy audit triangle [OPTIONS]

Options:
  --coverage PATH      Coverage report (pytest-cov JSON)
  --semantic           Enable Haiku-augmented analysis
  --format text|json   Output format
  --visualize          Generate HTML dashboard
  --threshold N        Closure threshold for warnings (default: 0.5)
```

---

## Relation to C020

This document extends [[jig-dev/dig/future/C020_CONCEPT_Alignment_Integrity]]:

- C020 defined **drift** (accuracy) and **coherence** (clarity)
- C021 provides **computational methods** for coherence assessment
- C020's coherence dimensions map to C021's metrics:

| C020 Dimension | C021 Metrics |
|----------------|--------------|
| Granularity | A1, A2 |
| Outcome Cohesion | A4, A5, D6 |
| Outcome Coupling | D5, projection analysis |
| Coverage Balance | C1, C4, C5 |
| Spec Scatter | A2, A3 |
| Arch Alignment | D5, brick analysis |
| Naming | E3 |

The triangle model adds **verification alignment** as a new coherence dimension not fully captured in C020.

---

## Open Questions

1. **Coverage granularity:** Function-level? Line-level? Branch-level? Function is probably sufficient for coherence, but finer granularity could catch more gaps.

2. **Test categorization:** Should integration tests be treated differently? They naturally have high coverage and low focus. May need test-type annotations.

3. **Cross-cutting specs:** Some specs (logging, config) legitimately touch everything. How to avoid false positives? Maybe mark specs as `cross-cutting: true`?

4. **Historical analysis:** Track triangle metrics over time? Could show coherence trends ("coverage closure declining").

5. **CI integration:** Block on closure < threshold? Or just report? Probably report initially, block after baseline established.

6. **Tensor visualization:** Is there a good way to visualize the 3D alignment tensor? Interactive 3D plot? Parallel coordinates?

---

## Next Steps

1. **Validate metrics** — Run on JIG codebase, check if signals match intuition
2. **Implement coverage parsing** — pytest-cov JSON → T→F graph
3. **Prototype dashboard** — HTML visualization of triangle health
4. **Calibrate thresholds** — What closure levels are "good"?
5. **Integrate with C020** — `jigy audit` subsumes both drift and triangle analysis

---

## Appendix: Metric Formulas

### A4: Implementation Overlap Matrix

```python
def impl_overlap_matrix(specs, S_F):
    n = len(specs)
    matrix = np.zeros((n, n))
    for i, s1 in enumerate(specs):
        for j, s2 in enumerate(specs):
            if i < j:
                f1, f2 = S_F[s1], S_F[s2]
                jaccard = len(f1 & f2) / len(f1 | f2) if f1 | f2 else 0
                matrix[i, j] = matrix[j, i] = jaccard
    return matrix
```

### D1: Triangle Closure

```python
def triangle_closure(spec, S_F, S_T, T_F):
    implementations = S_F.get(spec, set())
    if not implementations:
        return None  # Spec not implemented

    tests = S_T.get(spec, set())
    if not tests:
        return 0.0  # No tests = zero closure

    covered = set()
    for t in tests:
        covered |= T_F.get(t, set())

    covered_implementations = implementations & covered
    return len(covered_implementations) / len(implementations)
```

### D6: Projection Agreement

```python
def projection_agreement(specs, S_F, S_T):
    impl_matrix = impl_overlap_matrix(specs, S_F)
    verify_matrix = impl_overlap_matrix(specs, S_T)  # Same function, different graph

    impl_clusters = AgglomerativeClustering(n_clusters=None,
                                            distance_threshold=0.5).fit_predict(impl_matrix)
    verify_clusters = AgglomerativeClustering(n_clusters=None,
                                              distance_threshold=0.5).fit_predict(verify_matrix)

    return adjusted_rand_index(impl_clusters, verify_clusters)
```

### E1: Semantic Fingerprints

```python
async def semantic_fingerprints(specs, haiku_client):
    fingerprints = []
    for spec in specs:
        prompt = f"Summarize this specification in exactly 5 words: {spec.content}"
        response = await haiku_client.complete(prompt)
        fingerprints.append(response.strip())

    embeddings = embed_model.encode(fingerprints)
    clusters = AgglomerativeClustering(n_clusters=None,
                                       distance_threshold=0.3).fit_predict(embeddings)

    return clusters, adjusted_rand_index(clusters, [s.outcome for s in specs])
```
