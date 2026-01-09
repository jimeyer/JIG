---
type: exploration
title: "Alignment Integrity"
status: active
created: 1736300400
created_human: "2026-01-07 16:00 PST"
parent: null
children:
  - "[[C021_CONCEPT_Alignment_Triangle_Metrics]]"
  - "[[C022_CONCEPT_Stratified_Alignment_Verification]]"
prompt: |
  Discussion of JIG failure modes when artifacts exist but alignment has degraded.
  Two distinct problems emerged:
  1. Drift: artifacts no longer match reality (semantic accuracy)
  2. Coherence: artifacts don't illuminate reality (structural clarity)
  Both leave agents unable to reason effectively about the codebase.
---

# Alignment Integrity

_When JIG artifacts exist but fail their purpose_

---

## The Meta-Question

JIG validation answers: **Do artifacts exist and link correctly?**

But existence and linkage are necessary, not sufficient. Two deeper questions remain:

| Question | Failure Mode | Result |
|----------|--------------|--------|
| **Do artifacts match reality?** | Drift | Artifacts lie |
| **Do artifacts illuminate reality?** | Incoherence | Artifacts confuse |

A perfectly coherent but drifted system **lies clearly**.
A perfectly accurate but incoherent system **tells the truth badly**.

Both failure modes leave agents unable to reason effectively. JIG's structural validation catches neither.

---

## The Two Failures

### Drift

Artifacts diverge from implementation over time. Spec S-042 describes tokens expiring in 15 minutes; code sets 1 hour. The decorator links them. Validation passes. The graph describes a codebase that no longer exists.

**Drift is about accuracy.** The map no longer matches the territory.

### Incoherence

Artifacts exist and are accurate, but their organization is weak. Specs vary wildly in granularity. Outcomes are grab-bags of unrelated concerns. The hierarchy is lopsided. Reading the intent graph doesn't help you understand the system—it just gives you 91 facts with no narrative.

**Incoherence is about clarity.** The map is accurate but unreadable.

---

# Part I: Drift

_When artifacts stop matching reality_

---

## Categories of Drift

### 1. Spec-Code Semantic Drift

Spec prose no longer describes code behavior. The most insidious form—structurally invisible.

**Example:** Spec says "passwords must be 8+ characters." Code enforces 12. Decorator links them. Both are valid. Neither matches.

**Detection:** Requires semantic comparison. Human or LLM review.

---

### 2. Asymmetric Evolution

Code evolves. Spec doesn't. The spec describes original intent, not current behavior.

**Example:** `auth/session.py` modified 47 times in 6 months. Its linked spec S-042 unchanged since creation.

**Detection:** Temporal analysis. Compare modification timestamps across the implementation relationship.

---

### 3. Orphan Chains

Links exist but hierarchy is broken. Code claims to implement S-042. S-042 exists. But no outcome's `specifies:` includes S-042. The spec floats, disconnected from goals.

**Example:**
```
Code → S-042 ✓
S-042 → ??? (not in any outcome)
```

**Detection:** Graph traversal. Every spec must be reachable from an outcome. Every outcome from a goal.

---

### 4. Coverage Theater

Decorators added mechanically to satisfy tooling, not because developers read specs.

**Signals:**
- Suspiciously uniform distribution (every function has exactly one `@jig.implements`)
- Decorator-only commits (adding links without touching implementation)
- Decorators added months after code stabilized

**Detection:** Statistical analysis of decorator patterns. Real intent is lumpy.

---

### 5. Retrofitted Intent

Spec created after code. "Intent" reverse-engineered from implementation rather than driving it.

**Example:** Code written March 2025. Spec S-055 created September 2025 with `@jig.implements` added same day.

**Detection:** Git archaeology. Compare spec creation date to first code commit.

---

### 6. Phantom References

Outcome claims `specifies: [S-099]` but S-099 doesn't exist. Perhaps deleted, perhaps typo.

**Detection:** Graph validation. All references must resolve.

---

## Drift Signals

### Automatable (High Confidence)

| Signal | Computation | Threshold | Severity |
|--------|-------------|-----------|----------|
| **Modification divergence** | `max(code_modified) - max(spec_modified)` | >90 days | WARN |
| **Orphan spec (upward)** | Spec not in any outcome's `specifies:` | Any | ERROR |
| **Phantom reference (downward)** | `specifies:` references non-existent spec | Any | ERROR |
| **Broken goal chain** | Outcome not in any goal's support chain | Any | ERROR |
| **Uniform distribution** | stddev(implementations per spec) | <0.5 | INFO |
| **Retrofitted spec** | spec_created - first_code_commit | >30 days | WARN |
| **Decorator-only commits** | Commits touching only decorators | >3 recent | INFO |
| **Stale decorator** | Decorator unchanged, implementing code churns | >20 changes | WARN |

### Requires Sampling (Human/LLM Review)

| Signal | Method | Trigger |
|--------|--------|---------|
| **Semantic accuracy** | Read spec, read code, compare | High modification divergence |
| **Behavioral match** | Does code do what spec says? | Random sampling |
| **Decorator validity** | Did author read spec? | Decorator-only commits |
| **Spec currency** | Does spec describe current or historical? | Stale spec flagged |

---

## Drift Audit Output

```
DRIFT AUDIT
===========

STRUCTURAL DRIFT (automated, blocks CI)
---------------------------------------
[ERROR] S-067: Orphan spec - not in any outcome's specifies: field
[ERROR] O-015: Phantom reference - specifies: contains S-099 (does not exist)
[ERROR] O-022: Broken chain - not reachable from any goal

TEMPORAL DRIFT (automated, advisory)
------------------------------------
[WARN] S-042: 187 days since spec modified, 43 code commits since
[WARN] S-023: 134 days since spec modified, 28 code commits since
[WARN] S-055: Retrofitted - spec created 2025-09-15, code dates to 2025-03-01
[INFO] 7 decorator-only commits in past 90 days

DISTRIBUTION ANALYSIS
---------------------
[INFO] Implementations per spec: mean=2.3, stddev=0.4
       Low variance suggests mechanical decoration. Review for coverage theater.

SEMANTIC REVIEW CANDIDATES
--------------------------
Priority specs for manual review (ranked by modification divergence × code churn):
  1. S-042 Token Expiration (score: 8041)
  2. S-023 Session Persistence (score: 3752)
  3. S-011 Password Validation (score: 1862)

Run with --sample 5 to generate review prompts.
```

---

## Semantic Sampling Protocol

For high-priority drift candidates, generate structured review prompts:

```markdown
## Drift Review: S-042 Token Expiration

### Spec States (jig/specifications/S-042_Token_Expiration.md)
> Tokens MUST expire after 15 minutes of inactivity.
> Expiration is measured from last API call, not from token creation.

### Implementing Code (src/auth/token.py:89-102)
@jig.implements("S-042")
def create_token(user_id: str) -> Token:
    return Token(
        user_id=user_id,
        expires_at=datetime.now() + timedelta(hours=1)  # Fixed 1 hour
    )

### Temporal Context
- Spec last modified: 2025-03-15
- Code last modified: 2026-01-02
- Code commits since spec: 43

### Review Questions
1. Does the code behavior match the spec?
2. If not, which is authoritative?
   [ ] Spec is correct → fix code
   [ ] Code is correct → update spec
   [ ] Both wrong → escalate
3. Is the spec still relevant or should it be retired?

### Reviewer: _______________  Date: _______________
```

---

# Part II: Coherence

_When artifacts fail to illuminate_

---

## Dimensions of Coherence

### 1. Granularity Consistency

**Question:** Are specs at comparable abstraction levels?

| State | Description |
|-------|-------------|
| **Too coarse** | S-001 covers 40 functions across 8 modules. It's an outcome masquerading as a spec. Agents can't reason about it—it's everything and nothing. |
| **Too fine** | S-089 specifies "trim whitespace from username input." This is an implementation detail, not observable behavior. Agents drown in noise. |
| **Balanced** | Specs describe coherent capabilities mapping to recognizable code units. An agent can understand a spec, find its code, and reason about the boundary. |

**Metric:** Implementations per spec (count), LOC per spec (sum of implementing function sizes).

**Signal:** High variance indicates inconsistent granularity.

```
Granularity Analysis:
  Implementations per spec: [1, 2, 3, 2, 23, 1, 45, 2, 1]
  Mean: 8.9, Stddev: 15.2

  Outliers (>2σ):
    S-001: 45 implementations → Too coarse? Consider decomposition.
    S-007: 23 implementations → Too coarse? Consider decomposition.

  Outliers (<0.5σ):
    S-089, S-091, S-092: 1 implementation each → Too fine? Consider merging.
```

---

### 2. Outcome Cohesion

**Question:** Do specs within an outcome belong together?

| State | Description |
|-------|-------------|
| **Grab-bag** | O-015 contains "Token Refresh," "Log Rotation," and "Button Styling." No shared concern. The outcome is a dumping ground. |
| **Cohesive** | O-015's specs collectively deliver one user-visible capability. Reading them together tells a complete story. |

**Metric:** For specs in same outcome, measure implementation overlap (shared modules, shared callers, shared imports).

**Signal:** Low overlap within outcome = arbitrary grouping.

```
Outcome Cohesion Analysis:
  O-015 "Authentication Flow"
    Specs: S-042, S-043, S-044, S-045
    Implementation overlap: 0.73 [HIGH] ✓
    All specs share auth/ module dependencies

  O-019 "System Utilities"
    Specs: S-067, S-068, S-069
    Implementation overlap: 0.08 [LOW] ✗
    S-067 → logging/, S-068 → cache/, S-069 → metrics/
    No shared implementation. Consider splitting outcome.
```

---

### 3. Outcome Coupling

**Question:** Can outcomes be understood independently?

| State | Description |
|-------|-------------|
| **High coupling** | Understanding O-015 requires reading O-016, O-017, and O-022. They're actually one outcome split arbitrarily, or their boundaries are wrong. |
| **Low coupling** | Each outcome is self-contained. Cross-references are explicit, intentional, and rare. An agent can load one outcome and reason about it. |

**Metric:** Cross-outcome implementation dependencies. If code implementing S-042 (in O-015) imports from code implementing S-067 (in O-016), that's coupling.

**Signal:** High cross-outcome coupling = poorly drawn boundaries.

```
Outcome Coupling Matrix:
              O-015  O-016  O-017  O-019
    O-015       -     0.45   0.12   0.03
    O-016     0.45      -    0.67   0.08
    O-017     0.12    0.67     -    0.02
    O-019     0.03    0.08   0.02     -

[WARN] O-016 ↔ O-017: Coupling 0.67
       These outcomes share significant implementation.
       Consider: merge into single outcome, or redraw boundaries.
```

---

### 4. Coverage Balance

**Question:** Is intent documentation proportional to code complexity?

| State | Description |
|-------|-------------|
| **Lumpy** | Auth subsystem (500 LOC) has 15 specs. Payment subsystem (2000 LOC, higher risk) has 2. The important parts are under-specified. |
| **Balanced** | Spec density correlates with complexity and risk. Critical paths have rich intent. Utility code has light coverage. |

**Metric:** Specs per brick, normalized by LOC or cyclomatic complexity.

**Signal:** High variance = coverage driven by accident, not design.

```
Coverage Balance by Brick:
  Brick          LOC    Specs   Density
  B-auth         523      15     0.029    [HIGH]
  B-api         1847       8     0.004    [MEDIUM]
  B-payment     2103       2     0.001    [LOW] ✗
  B-cache        412       7     0.017    [HIGH]
  B-utils        891       1     0.001    [LOW]

[WARN] B-payment: High LOC, low spec density
       Critical subsystem may be under-specified.

[INFO] B-utils: Low density acceptable for utility code.
```

---

### 5. Hierarchy Shape

**Question:** Is the goal→outcome→spec tree balanced?

| State | Description |
|-------|-------------|
| **Lopsided** | G-001 has 18 outcomes. G-005 has 1. Either goals represent unequal concerns, or decomposition was uneven. Agents see one goal as "the whole system" and others as afterthoughts. |
| **Balanced** | Goals represent roughly equal strategic concerns. Outcomes distribute proportionally. The hierarchy is navigable. |

**Metric:** Outcomes per goal, specs per outcome. Compute Gini coefficient.

**Signal:** High Gini = lopsided tree.

```
Hierarchy Shape:
  Goals → Outcomes:
    G-001: 18 outcomes (69%)
    G-002:  4 outcomes (15%)
    G-003:  2 outcomes (8%)
    G-004:  1 outcome  (4%)
    G-005:  1 outcome  (4%)
    Gini: 0.72 [HIGH] ✗

  Outcomes → Specs:
    Mean: 3.5 specs/outcome
    Stddev: 4.2
    Range: 1-15
    Gini: 0.48 [MODERATE]

[WARN] Goal hierarchy is lopsided.
       G-001 dominates. Consider:
       - Is G-001 actually multiple goals?
       - Are G-004/G-005 too narrow?
```

---

### 6. Spec-to-Code Scatter

**Question:** Do specs map to cohesive code units?

| State | Description |
|-------|-------------|
| **Scattered** | S-042 is implemented by functions in auth/, api/, utils/, db/, and cache/. The "spec" doesn't correspond to any architectural unit. It's a concern smeared across the codebase. |
| **Focused** | S-042 maps to one module or one brick. The spec is the code's intent, localized. Agents can find it, understand it, modify it. |

**Metric:** Bricks per spec, modules per spec.

**Signal:** High values = scattered implementation.

```
Spec Scatter Analysis:
  Spec      Bricks  Modules  Assessment
  S-042        5       12    [SCATTERED] ✗
  S-023        4        8    [SCATTERED] ✗
  S-067        1        2    [FOCUSED] ✓
  S-011        2        3    [MODERATE]

[WARN] S-042: Implemented across 5 bricks
       This spec may be too broad, or represents a cross-cutting concern.
       Consider: decompose along brick boundaries, or document as cross-cutting.
```

---

### 7. Code-to-Spec Scatter (Inverse)

**Question:** Does code have coherent intent?

| State | Description |
|-------|-------------|
| **Fragmented** | `auth/session.py` implements parts of S-012, S-034, S-045, S-067, and S-089. The module has no single purpose—it's a grab-bag of unrelated capabilities. |
| **Coherent** | Module implements one or two related specs. Clear responsibility. Agents know what this code is for. |

**Metric:** Specs per module.

**Signal:** High values = fragmented code responsibility.

```
Code Responsibility Analysis:
  Module                    Specs  Assessment
  auth/session.py              5   [FRAGMENTED] ✗
  auth/token.py                2   [COHERENT] ✓
  api/handlers.py              7   [FRAGMENTED] ✗
  utils/crypto.py              1   [COHERENT] ✓

[WARN] auth/session.py: Implements 5 unrelated specs
       Module may have too many responsibilities.
       Consider refactoring along spec boundaries.
```

---

### 8. Naming Consistency

**Question:** Do titles follow predictable patterns?

| State | Description |
|-------|-------------|
| **Chaotic** | "User Auth," "the token thing," "S-045 Improvements," "NewCache_v2." Titles are ad-hoc, temporal, implementation-focused. Agents can't predict what a spec covers from its name. |
| **Consistent** | Noun phrases describing capabilities. No temporal words, no implementation details, no versions. Titles are evergreen. |

**Anti-patterns:**
- Temporal: "new," "old," "improved," "v2," "legacy"
- Implementation: "Redis Cache," "JWT Handler," "SQL Query"
- Task-oriented: "Fix Auth Bug," "Refactor Login"
- Articles: "The Main Config," "A Better Parser"
- Vague: "Miscellaneous," "Utilities," "Helpers"

**Metric:** Pattern match against anti-patterns. Count violations.

```
Naming Analysis:
  Violations: 4
    S-045: "Improved Token Handling" → temporal "Improved"
    S-078: "New Session Manager" → temporal "New"
    S-089: "Fix Auth Race Condition" → task "Fix"
    S-091: "Redis Cache Layer" → implementation "Redis"

  Recommendations:
    S-045 → "Token Lifecycle Management"
    S-078 → "Session State Persistence"
    S-089 → "Authentication Concurrency Safety"
    S-091 → "Response Caching"
```

---

### 9. Architectural Alignment

**Question:** Do intent boundaries mirror code boundaries?

| State | Description |
|-------|-------------|
| **Misaligned** | Outcome O-015 cuts across B-auth, B-api, B-cache, and B-db. The intent structure has no correspondence to the code structure. Agents can't map between them. |
| **Aligned** | Outcomes roughly correspond to bricks or towers. Specs correspond to modules within bricks. Intent structure mirrors implementation structure. Agents can navigate both together. |

**Metric:** For each outcome, count distinct bricks implementing it.

**Signal:** High brick count per outcome = misalignment.

```
Architectural Alignment:
  Outcome      Bricks  Alignment
  O-015           4    [MISALIGNED] ✗
  O-016           2    [MODERATE]
  O-017           1    [ALIGNED] ✓
  O-019           5    [MISALIGNED] ✗

[WARN] O-015: Spans 4 bricks (B-auth, B-api, B-cache, B-db)
       Intent boundary doesn't match architectural boundary.
       Consider: split into brick-aligned outcomes, or document as cross-cutting.
```

---

### 10. Narrative Legibility

**Question:** Does reading outcomes tell a coherent story?

| State | Description |
|-------|-------------|
| **Laundry list** | Outcomes read like random capabilities. A new developer reading them learns facts but not structure. The system's shape remains opaque. |
| **Coherent narrative** | Outcomes form a "table of contents" for the system. Reading them in order builds understanding. The system's architecture emerges from the intent graph. |

**Metric:** Qualitative, or: semantic clustering of outcome titles. Random distribution = no narrative.

**Assessment method:** Read outcome titles in sequence. Do they tell a story? Could a new developer sketch the system architecture from outcomes alone?

---

## Coherence Signals Summary

| Dimension | Metric | Signal | Threshold |
|-----------|--------|--------|-----------|
| Granularity | stddev(impl per spec) | High variance | >5.0 |
| Outcome cohesion | avg implementation overlap | Low overlap | <0.2 |
| Outcome coupling | cross-outcome import ratio | High coupling | >0.4 |
| Coverage balance | Gini(specs per brick, normalized) | Imbalanced | >0.5 |
| Hierarchy shape | Gini(outcomes per goal) | Lopsided | >0.4 |
| Spec scatter | avg(bricks per spec) | Scattered | >2.0 |
| Code scatter | avg(specs per module) | Fragmented | >3.0 |
| Naming | anti-pattern count | Inconsistent | >0 |
| Arch alignment | avg(bricks per outcome) | Misaligned | >2.5 |

---

## Coherence Audit Output

```
COHERENCE AUDIT
===============

GRANULARITY
-----------
Implementations per spec: mean=4.2, stddev=8.7 [HIGH VARIANCE]
  Coarse outliers (>15 impl):
    S-001: 45 implementations
    S-007: 23 implementations
  Fine outliers (=1 impl):
    S-089, S-091, S-092

OUTCOME STRUCTURE
-----------------
Cohesion:
  O-019 "System Utilities": overlap=0.08 [LOW] - grab-bag?

Coupling:
  O-016 ↔ O-017: 0.67 [HIGH] - merge or redraw?

COVERAGE
--------
Gini coefficient: 0.58 [IMBALANCED]
  Under-covered: B-payment (2103 LOC, 2 specs)
  Over-covered: B-auth (523 LOC, 15 specs)

HIERARCHY
---------
Goal distribution Gini: 0.72 [LOPSIDED]
  G-001: 18 outcomes (69%)
  G-002-G-005: 8 outcomes combined (31%)

SCATTER
-------
Specs crossing brick boundaries:
  S-042: 5 bricks [HIGH]
  S-023: 4 bricks [HIGH]

Modules with fragmented responsibility:
  auth/session.py: 5 specs [HIGH]
  api/handlers.py: 7 specs [HIGH]

NAMING
------
Anti-pattern violations: 4
  S-045: "Improved" (temporal)
  S-078: "New" (temporal)
  S-089: "Fix" (task)
  S-091: "Redis" (implementation)

ARCHITECTURAL ALIGNMENT
-----------------------
Outcomes misaligned with bricks:
  O-015: spans 4 bricks
  O-019: spans 5 bricks

NARRATIVE ASSESSMENT
--------------------
[Manual review required]
Question: Do outcome titles form a coherent table of contents?
Run with --narrative to output outcome list for review.
```

---

# Part III: Unified Audit

---

## Combined Command

```bash
jigy audit [OPTIONS]

# Subcommands
jigy audit drift      # Drift analysis only
jigy audit coherence  # Coherence analysis only
jigy audit full       # Both (default)
```

### Options

```
--format text|json|markdown   Output format (default: text)
--strict                      Exit non-zero on any error/warning
--ci                          CI mode: errors only, no advisory
--threshold-days N            Modification divergence threshold (default: 90)
--sample N                    Generate N semantic review prompts
--narrative                   Output outcome titles for narrative review
--json-report PATH            Write full report to JSON file
```

### Exit Codes

```
0  - No errors, no warnings
1  - Errors detected (structural drift, broken chains)
2  - Warnings only (temporal drift, coherence issues)
```

---

## Full Audit Report Structure

```
ALIGNMENT INTEGRITY AUDIT
=========================
Project: jig-dev
Date: 2026-01-07
Artifacts: 5 goals, 26 outcomes, 91 specs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DRIFT (Do artifacts match reality?)
───────────────────────────────────
Structural: 2 errors, 0 warnings
Temporal: 0 errors, 5 warnings
Distribution: 1 info

COHERENCE (Do artifacts illuminate reality?)
────────────────────────────────────────────
Granularity: 1 warning (high variance)
Structure: 2 warnings (low cohesion, high coupling)
Coverage: 1 warning (imbalanced)
Hierarchy: 1 warning (lopsided)
Scatter: 2 warnings (spec scatter, code fragmentation)
Naming: 4 violations
Alignment: 2 warnings (outcomes span multiple bricks)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY
───────
Integrity Score: 62/100
  Drift:      85/100 (accurate but temporally stale)
  Coherence:  45/100 (structurally weak)

Priority Actions:
  1. [ERROR] Fix orphan specs: S-067
  2. [ERROR] Fix phantom refs: O-015 → S-099
  3. [WARN] Review stale specs: S-042, S-023, S-011
  4. [WARN] Decompose coarse specs: S-001, S-007
  5. [WARN] Split grab-bag outcome: O-019

Run `jigy audit --sample 5` for semantic review prompts.
Run `jigy audit --narrative` for narrative assessment.
```

---

## CI Integration

```yaml
# .github/workflows/jig.yml
jobs:
  jig-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: JIG Integrity Audit
        run: |
          jigy audit --ci --strict
        # --ci: Only structural errors (blocks merge)
        # --strict: Exit non-zero on any error

      - name: JIG Advisory Report
        if: always()
        run: |
          jigy audit --format markdown > jig-audit.md

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: jig-audit-report
          path: jig-audit.md
```

**CI Philosophy:**
- **Block on:** Structural drift (orphans, phantoms, broken chains)
- **Warn on:** Temporal drift, coherence issues
- **Report on:** Everything, for human review

---

## Periodic Ritual

**Weekly (automated):**
```bash
jigy audit --json-report jig-audit-$(date +%Y%m%d).json
```

Track integrity score over time. Alert on regression.

**Sprint (human):**
```bash
jigy audit --sample 5
```

Assign 5 semantic reviews to rotating team member. Track in sprint.

**Quarterly (team):**
```bash
jigy audit --narrative
```

Read outcomes as a team. Assess: Does this tell our system's story?
Refactor intent structure as needed.

---

## Remediation Patterns

### Drift Remediation

| Problem | Action |
|---------|--------|
| Orphan spec | Add to appropriate outcome's `specifies:` or delete |
| Phantom reference | Remove from outcome or create missing spec |
| Stale spec | Review: update spec or fix code |
| Retrofitted spec | Acceptable if accurate; flag for semantic review |
| Coverage theater | Review decorator validity; remove mechanical links |

### Coherence Remediation

| Problem | Action |
|---------|--------|
| Coarse spec | Decompose into multiple focused specs |
| Fine spec | Merge into parent spec or delete |
| Grab-bag outcome | Split by concern or regroup specs |
| High outcome coupling | Merge outcomes or redraw boundaries |
| Coverage imbalance | Add specs to under-covered areas |
| Lopsided hierarchy | Split large goals or merge small ones |
| Scattered spec | Decompose along brick boundaries |
| Fragmented module | Refactor code along spec boundaries |
| Naming violation | Rename to capability-focused title |
| Arch misalignment | Align outcomes to bricks/towers |

---

## Non-Goals

- **Automated semantic verification** — Determining if prose matches behavior requires understanding both. LLMs can assist triage but not replace judgment.

- **Auto-fixing** — Detection only. Humans decide whether spec or code is authoritative, how to restructure, what to rename.

- **Blame assignment** — Report facts, not fault. "S-042 is stale" not "Alice let S-042 drift."

- **Perfection** — Some incoherence is acceptable. Utility code doesn't need rich specs. Cross-cutting concerns will span bricks. The goal is visibility, not zero warnings.

---

## Success Criteria

1. `jigy audit` completes in <10s for typical project (<100 specs)
2. Zero false negatives on structural drift (orphans, phantoms, broken chains)
3. Temporal drift signals identify 80%+ of semantically stale specs
4. Coherence metrics correlate with developer-perceived quality (validate via survey)
5. Integrity score is reproducible and comparable across time
6. CI integration prevents new structural drift from merging
7. Periodic ritual is sustainable (not burdensome)

---

## Open Questions

1. **Threshold calibration:** Are defaults (90 days, Gini 0.5, etc.) right? Need empirical tuning on real projects.

2. **Weighting:** How to combine drift and coherence into single integrity score? Equal weight? Risk-adjusted?

3. **LLM integration:** Should `--sample` invoke LLM directly for triage, or generate prompts for external use?

4. **Historical tracking:** Persist audit results for trend analysis? Schema for `jig/generated/audit-history.ndjson`?

5. **Coherence subjectivity:** Some dimensions (narrative legibility) resist quantification. How to handle?

6. **Cross-cutting concerns:** Specs that legitimately span bricks (logging, auth, caching) will always show as scattered. How to mark as intentional?

7. **Incremental audit:** Can we audit only changed artifacts? Or must full audit run for accurate coupling/distribution metrics?

---

## Related

- [[A-001_JIG_Core_Architecture]] — Defines the hierarchy being audited
- [[A-004_Validation_Architecture]] — Structural validation (complements integrity audit)
- [[O-015_Completeness_Validation_for_Intent_Graph]] — Existing completeness checks
- [[O-027_Discoverable_Intent_Document_Naming]] — Naming conventions (relates to naming coherence)

---

## Next Steps

1. **Validate concept** — Does this framing resonate? Are dimensions complete?
2. **Prioritize dimensions** — Which coherence metrics are most valuable?
3. **Prototype drift detection** — Temporal analysis is automatable today
4. **Define O-028?** — Is this a new outcome or extension of A-004?
5. **Spec decomposition** — Break into implementable specs (S-093+?)

---

## Appendix: Integrity Score Calculation

Proposed formula (weights TBD):

```
drift_score = (
  0.4 × structural_clean     # No orphans, phantoms, broken chains (binary)
  + 0.3 × temporal_health    # % specs within modification threshold
  + 0.2 × distribution_ok    # Decorator distribution not suspicious
  + 0.1 × no_retrofits       # % specs created before implementing code
)

coherence_score = (
  0.15 × granularity_consistency  # 1 - normalized(stddev)
  + 0.15 × outcome_cohesion       # avg overlap
  + 0.10 × outcome_decoupling     # 1 - avg coupling
  + 0.15 × coverage_balance       # 1 - Gini
  + 0.10 × hierarchy_balance      # 1 - Gini
  + 0.10 × spec_focus             # 1 - normalized(avg bricks per spec)
  + 0.10 × code_focus             # 1 - normalized(avg specs per module)
  + 0.05 × naming_clean           # 1 - violation_rate
  + 0.10 × arch_alignment         # 1 - normalized(avg bricks per outcome)
)

integrity_score = 0.5 × drift_score + 0.5 × coherence_score
```

All components normalized to 0-1 range, final score 0-100.
