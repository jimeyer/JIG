---
title: Alignment Audit Report
type: journal
status: active
created: 1736348160
created_human: "2026-01-08"
parent: null
children: []
---

# Alignment Audit Report

**Project:** jig-dev
**Date:** 2026-01-08T14:56:00Z
**Stages Run:** 1-4

---

## Overall Score: 76/100

| Stage | Score | Status |
|-------|-------|--------|
| 1. CODE | 75/100 | Good |
| 2. TEST | 84/100 | Good |
| 3. SPEC | 68/100 | Needs Work |
| 4. HIERARCHY | 80/100 | Good |

**Score Calculation:** 0.20×75 + 0.25×84 + 0.30×68 + 0.25×80 = 76.4

---

## Stage Summaries

### Stage 1: CODE (75/100)

**Strengths:**
- Zero layer violations - layered architecture properly enforced
- Zero tower isolation violations (single-tower project)
- No brick dependency cycles - clean acyclic graph
- 11 well-defined bricks with clear boundaries

**Areas for Improvement:**
- **37 complexity outliers** (functions with cyclomatic complexity >10)
  - Worst: `show_towers_command` (55), `analyze_file` (44), `align_command` (35)
- **5 high fan-out modules** (>10 imports)
  - `cli/rebuild.py` (17), `cli/validate.py` (13), `audit/coverage.py` (13)
- **Low mean cohesion** (0.19) - expected for CLI application orchestrating other bricks

| Metric | Value |
|--------|-------|
| Layer Violations | 0 |
| Tower Isolation | 0 |
| Brick Cycles | 0 |
| Max Fan-Out | 17 |
| Max Fan-In | 29 |
| Mean Cohesion | 0.19 |
| Complexity Outliers | 37 |
| LOC Gini | 0.52 |

---

### Stage 2: TEST (84/100)

**Strengths:**
- **86.8% coverage breadth** (3728/4296 lines)
- **Low coverage Gini** (0.0661) - well-distributed coverage
- **88.4% test-brick alignment**
- **7 files with 100% coverage** (core utilities)
- **20 proto-specs identified** - tests cluster naturally

**Areas for Improvement:**
- 1 orphan file with 0% coverage (`__main__.py` - CLI entry point, 3 lines)

| Metric | Value |
|--------|-------|
| Coverage Breadth | 86.8% |
| Coverage Depth | 13.89 tests/100 lines |
| Coverage Gini | 0.0661 |
| Test-Brick Alignment | 88.4% |
| Orphan Count | 1 |
| Hot Spots | 7 |

**Top Proto-Specs by Test Count:**
1. `proto-verification-graph-analyzer` (48 tests)
2. `proto-cli-show` (36 tests)
3. `proto-validation-intent` (32 tests)
4. `proto-hashing` (30 tests)
5. `proto-cli-validate` (30 tests)

---

### Stage 3: SPEC (68/100)

**Strengths:**
- **87.7% triangle closure** - most specs have implementations covered by tests
- **88.6% decorator coverage** on tests
- **100% proto-spec match** - inferred clusters match declared specs
- 77 total specs, 73 with implementations

**Areas for Improvement:**
- **53.8% decorator coverage** on implementations (129/240 functions)
- **9 verification gaps** - specs with implementations but no `@jig.verifies` tests
- **4 orphan specs** - no implementations at all

| Metric | Value |
|--------|-------|
| Decorator Coverage (impl) | 53.8% |
| Decorator Coverage (verify) | 88.6% |
| Triangle Closure | 87.7% |
| Verification Gaps | 9 |
| Granularity Variance | 6.0 |
| Mean Impl Scatter | 1.6 files/spec |
| Proto-Spec Match | 100% |

**Verification Gaps (need `@jig.verifies` tests):**
- S-027 Auto-Validation in Rebuild Commands
- S-028 CLI Command to Generate Intent Graph
- S-080 through S-086 (Intent Graph hierarchy nodes/edges)

**Orphan Specs (need implementations):**
- S-040 CLI Command: jigy layers
- S-041 CLI Command: jigy layers suggest
- S-056 CLI Verify Rebuild Command
- S-092 Intent Document Title Requirements

---

### Stage 4: HIERARCHY (80/100)

**Strengths:**
- **83.1% mean outcome cohesion** - specs cluster well within outcomes
- **87% outcome-brick affinity** - most outcomes have clear dominant brick
- **Low goal distribution Gini** (0.141) - balanced outcome coverage across goals
- **97.8% outcome closure** - most outcomes fully triangulated

**Areas for Improvement:**
- **1 grab-bag outcome** - O-026 (Towers Enforce Component Isolation) with 44.4% cohesion
- **7 outcomes with verification gaps**
- **22 high-coupling outcome pairs** (shared implementation files)

| Metric | Value |
|--------|-------|
| Mean Outcome Cohesion | 83.1% |
| Mean Outcome Coupling | 0.52 |
| Outcome-Brick Affinity | 87% |
| Goal Distribution Gini | 0.141 |
| Spec Cluster Match | 83.1% |
| Hierarchy Depth Variance | 3.26 |
| Mean Outcome Closure | 97.8% |

**Goals Coverage:**
| Goal | Outcomes |
|------|----------|
| G-001 Grounding in Reality | 9 |
| G-002 Continuity Across Sessions | 8 |
| G-003 Enforcing Constraints | 9 |
| G-004 Intent Alignment | 8 |
| G-005 Full Traceability | 3 (lowest) |

**Grab-Bag Outcomes:**
- O-026 (Towers Enforce Component Isolation) - specs scattered across validation, intent_graph, cli

---

## Priority Actions

### CRITICAL (None)
No layer violations, no tower isolation breaks, no brick cycles.

### HIGH
1. **Add `@jig.verifies` tests for 9 specs** (S-027, S-028, S-080-S-086)
   - These specs have implementations but no verifying tests
   - Triangle closure incomplete

2. **Implement 4 orphan specs**
   - S-040, S-041: `jigy layers` commands (planned but not implemented)
   - S-056: CLI Verify Rebuild Command
   - S-092: Intent Document Title Requirements

### MEDIUM
3. **Increase `@jig.implements` decorator coverage** (currently 54%)
   - 111 functions without decorators that should probably have them
   - Improves spec-to-code traceability

4. **Refactor grab-bag outcome O-026** (Towers Enforce Component Isolation)
   - Low cohesion (44%) suggests specs may belong to different outcomes
   - Consider splitting by brick (validation vs cli concerns)

5. **Reduce complexity in CLI commands**
   - `show_towers_command`: 55 complexity
   - `analyze_file`: 44 complexity
   - `align_command`: 35 complexity
   - Consider extracting helper functions

### LOW
6. **Review high-coupling outcome pairs** (22 pairs)
   - Some coupling is intentional (O-004/O-006 share validation commands)
   - May indicate opportunities for outcome consolidation

7. **Goal G-005 coverage**
   - Only 3 outcomes support Full Traceability
   - May want to expand coverage

---

## Detailed Findings

### Specs with Zero Triangle Closure
| Spec | Title | Issue |
|------|-------|-------|
| S-027 | Auto-Validation in Rebuild Commands | Has impl, no tests |
| S-028 | CLI Command to Generate Intent Graph | Has impl, no tests |
| S-080 | Charter Node In Intent Graph | Has impl, no tests |
| S-081 | Goal Nodes In Intent Graph | Has impl, no tests |
| S-082 | Architecture Nodes In Intent Graph | Has impl, no tests |
| S-083 | Defines Goal Edges | Has impl, no tests |
| S-084 | Supports Goal Edges | Has impl, no tests |
| S-085 | Constrains Edges | Has impl, no tests |
| S-086 | Brick Tower Field Optional | Has impl, no tests |
| S-040 | CLI Command: jigy layers | No impl, no tests |
| S-041 | CLI Command: jigy layers suggest | No impl, no tests |
| S-056 | CLI Verify Rebuild Command | No impl, no tests |
| S-092 | Intent Document Title Requirements | No impl, no tests |

### Complexity Outliers (Top 10)
| File | Function | Complexity |
|------|----------|------------|
| cli/show.py | show_towers_command | 55 |
| impl_graph/analyzers/python.py | analyze_file | 44 |
| cli/rebuild.py | align_command | 35 |
| cli/show.py | show_layers_command | 33 |
| cli/show.py | show_goals_command | 33 |
| cli/show.py | show_architecture_command | 33 |
| cli/show.py | show_matrix_command | 29 |
| cli/show.py | show_bricks_command | 24 |
| validation/bricks.py | validate_brick_definitions | 23 |
| cli/audit.py | coverage_command | 21 |

### Brick Dependency Graph
```
B-cli (L1) → B-audit, B-impl-graph, B-intent-graph, B-staleness, B-validation, B-verification-graph
B-verification-graph (L1) → B-hashing, B-impl-graph
B-intent-graph (L0) → B-hashing
B-languages (L0) → B-hashing
B-validation (L0) → B-config
```

---

## Summary

The jig-dev project shows **good overall alignment** (76/100) with strong architectural discipline:
- Clean layered architecture with no violations
- High test coverage (87%) well-distributed across modules
- Strong outcome-spec alignment (83% cohesion)

Key areas for improvement:
1. Add missing test coverage for intent graph hierarchy specs (S-080-S-086)
2. Implement planned but missing features (S-040, S-041, S-056)
3. Increase `@jig.implements` decorator coverage from 54% to >80%
4. Consider refactoring high-complexity CLI commands

---

*Generated by Five Stage Alignment Audit*
*Report path: dig/generated/audit/AUDIT_REPORT.md*
