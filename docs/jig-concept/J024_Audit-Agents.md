# J024: Audit Agents

**Status:** Proposal
**Date:** 2025-12-06
**Builds On:** J022 (Alignment Change Detection), J023 (Audit Strategies and Mechanisms)

---

## Context

J022 introduced hash-based change detection to identify *when* alignment needs re-verification. J023 defined the output format and query patterns for audit results. This document addresses *how* to perform audits efficiently and *how* to evaluate audit strategies.

### The Core Question

Auditing alignment between specifications (S), implementations (F), and tests (T) requires judgment. Some judgment is mechanical (does the decorator exist?), some requires understanding (does the implementation fulfill the spec?).

**The naive approach:** Throw a large LLM at each audit. This works but is expensive, slow, and wasteful when simpler methods suffice.

**The challenge:** Not all audit tasks require the same intelligence level. How do we match audit depth to actual need?

### Design Goals

1. **Minimize LLM usage** without sacrificing audit quality
2. **Use the right tool** for each audit sub-task
3. **Leverage change detection** (J022) to avoid redundant work
4. **Produce machine-readable output** (J023) for aggregation
5. **Enable empirical evaluation** of strategy effectiveness

---

## Part I: The Audit Intelligence Spectrum

Audit tasks exist on a spectrum from fully deterministic to deeply semantic:

```
┌─────────────────────────────────────────────────────────────────┐
│                 AUDIT INTELLIGENCE SPECTRUM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DETERMINISTIC          STRUCTURED           SEMANTIC           │
│  (no LLM)               (small LLM)          (large LLM)        │
│                                                                 │
│  ├── File exists?       ├── Extract criteria  ├── Does impl     │
│  ├── Frontmatter valid? ├── Map func→criteria │   fulfill spec? │
│  ├── Decorator present? ├── Map test→criteria ├── Quality       │
│  ├── Reference valid?   ├── Yes/No/Partial    │   assessment    │
│  ├── Coverage data      │   classification    ├── Gap analysis  │
│  └── Hash comparison    └── Name similarity   └── Cross-cutting │
│                                                                 │
│  Cost: $0               Cost: ~$0.001         Cost: ~$0.05      │
│  Speed: <100ms          Speed: ~500ms         Speed: ~10s       │
│  Accuracy: 100%         Accuracy: ~85-90%     Accuracy: ~95%    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part II: Audit Agent Strategies

The following strategies are **hypotheses** to be validated empirically. Each represents a different approach to balancing cost, speed, and accuracy.

### Strategy 1: Tiered Audit Depths

**Hypothesis:** Define discrete audit levels; not every change needs every level.

#### Level 0: Structural (Deterministic)
```
Cost: $0
Time: <100ms
Trigger: Any change

Checks:
✓ Spec file exists with valid YAML frontmatter
✓ @jig.implements decorator present and syntactically valid
✓ @jig.verifies decorator present and syntactically valid
✓ All references resolve (spec ID exists, outcome ID exists)
✓ Brick/layer assignment is valid
✓ Hash recorded for change detection
```

#### Level 1: Coverage (Deterministic + Test Execution)
```
Cost: Test runtime only
Time: Varies by test suite
Trigger: Implementation or test changed

Checks:
✓ Run pytest with coverage
✓ Verify T→F edges (test covers implementing function)
✓ Calculate coverage percentage
✓ Identify coverage gaps
```

#### Level 2: Criteria Mapping (Small LLM)
```
Cost: ~$0.001 per spec
Time: ~500ms
Trigger: Spec or implementation changed

Checks:
✓ Extract acceptance criteria from spec text
✓ For each function: "Does this address criterion N?" [Yes/No/Partial]
✓ For each test: "Does this validate criterion N?" [Yes/No/Partial]
✓ Build criteria coverage matrix
```

#### Level 3: Semantic Shallow (Small/Medium LLM)
```
Cost: ~$0.01 per spec
Time: ~2s
Trigger: Level 2 score below threshold

Checks:
✓ Function name/docstring alignment with spec keywords
✓ Test name/assertions alignment with spec
✓ Embedding similarity scoring
✓ Basic semantic validation
```

#### Level 4: Semantic Deep (Large LLM)
```
Cost: ~$0.05 per spec
Time: ~10s
Trigger: Manual request, periodic sampling, or flagged by lower levels

Checks:
✓ Full semantic review of implementation vs spec
✓ Logic gap analysis
✓ Quality assessment of tests
✓ Cross-cutting outcome analysis
✓ Actionable recommendations
```

---

### Strategy 2: Change-Triggered Escalation

**Hypothesis:** Use J022 hash changes to determine minimum required audit depth.

```
┌──────────────────────────────────────────────────────────────────┐
│              CHANGE TYPE → AUDIT DEPTH MAPPING                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Change Detected              Minimum Audit Response             │
│  ───────────────              ──────────────────────             │
│                                                                  │
│  No change                 →  Skip (use cached result)           │
│                                                                  │
│  Spec hash changed,        →  Level 0-2 required                 │
│  impl hash unchanged          Flag for Level 3-4 review         │
│                                                                  │
│  Impl hash changed,        →  Level 0-2 required                 │
│  spec hash unchanged          Level 3-4 optional                 │
│                                                                  │
│  Both hashes changed       →  Full audit (Level 0-4)             │
│                                                                  │
│  New alignment pair        →  Full audit (Level 0-4)             │
│                                                                  │
│  Alignment removed         →  Cleanup only (archive old result)  │
│                                                                  │
│  Periodic (configurable)   →  Sample N% for Level 4              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Rationale:** Spec changes are more likely to require semantic re-review than implementation changes. A spec change may invalidate the entire implementation; an implementation change may just be refactoring.

---

### Strategy 3: Structured Prompts for Small Models

**Hypothesis:** Constrained questions with constrained outputs enable reliable use of small models (Haiku).

#### Criteria Extraction Prompt
```
Given this specification:
---
{spec_content}
---

Extract the acceptance criteria as a JSON array.
Each criterion should be a single testable requirement.
Number them to match the spec if numbered.

Output ONLY valid JSON:
{"criteria": ["criterion 1 text", "criterion 2 text", ...]}
```

#### Criteria Classification Prompt
```
Specification criterion: "{criterion_text}"

Function code:
```python
{function_code}
```

Does this function address this criterion?
Answer with ONLY one word: YES, NO, or PARTIAL
```

#### Test Coverage Classification Prompt
```
Test function:
```python
{test_code}
```

Which of these criteria does this test validate?
{numbered_criteria_list}

Answer with ONLY the criterion numbers, comma-separated.
Example: 1, 3, 5
If none, answer: NONE
```

**Why this works:**
- Constrained outputs (YES/NO/PARTIAL, numbers only) are easy to validate
- No reasoning required—just classification
- Small models excel at pattern matching with clear instructions
- Can run many queries in parallel
- Failures are detectable (invalid output format)

---

### Strategy 4: Confidence-Based Escalation

**Hypothesis:** Deterministic signals can predict when LLM review is needed.

```python
def compute_audit_confidence(spec: Spec, impl: Function, test: Test) -> float:
    """
    Compute confidence that alignment is correct (0.0-1.0).
    Higher confidence = less likely to need deep review.
    """
    signals = []

    # Strong positive signals (deterministic)
    if decorator_references_correct_spec(impl, spec):
        signals.append(1.0)

    if test_covers_implementation(test, impl):  # From coverage data
        signals.append(1.0)

    # Medium signals (heuristic)
    if function_name_contains_spec_keywords(impl, spec):
        signals.append(0.7)

    if docstring_mentions_spec_id(impl, spec):
        signals.append(0.8)

    if test_name_relates_to_spec(test, spec):
        signals.append(0.6)

    # Negative signals
    if spec_has_many_criteria(spec, threshold=5):
        signals.append(0.3)  # Complex specs need more review

    if impl_is_very_short(impl, lines=5):
        signals.append(0.4)  # May be incomplete

    return sum(signals) / len(signals) if signals else 0.0


def determine_audit_depth(confidence: float) -> int:
    """Map confidence to audit depth."""
    if confidence >= 0.85:
        return 1  # Structural + coverage sufficient
    elif confidence >= 0.65:
        return 2  # Add criteria mapping
    elif confidence >= 0.45:
        return 3  # Add shallow semantic
    else:
        return 4  # Full deep review needed
```

**Escalation flow:**
```
Start with Level 0 (deterministic)
    ↓
Compute confidence score
    ↓
confidence >= 0.85? → Done (Level 1)
    ↓ no
Run Level 2 (Haiku criteria mapping)
    ↓
confidence >= 0.65? → Done (Level 2)
    ↓ no
Run Level 3 or 4 depending on remaining confidence
```

---

### Strategy 5: Layered Agent Architecture

**Hypothesis:** A modular architecture enables mixing and matching strategies.

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUDIT AGENT ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Orchestrator (Python, no LLM)               │   │
│  │  • Loads spec, impl, test from files                    │   │
│  │  • Checks J022 hashes for changes                       │   │
│  │  • Retrieves cached results if unchanged                │   │
│  │  • Determines required audit depth                      │   │
│  │  • Dispatches to appropriate layer                      │   │
│  │  • Aggregates results into J023 format                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│         ┌──────────────────┼──────────────────┐                │
│         ▼                  ▼                  ▼                │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐           │
│  │Deterministic│    │   Small    │    │   Large    │           │
│  │   Layer    │    │ LLM Layer  │    │ LLM Layer  │           │
│  ├────────────┤    ├────────────┤    ├────────────┤           │
│  │File checks │    │ Haiku      │    │ Sonnet or  │           │
│  │Graph query │    │            │    │ Opus       │           │
│  │AST parsing │    │ Extract    │    │            │           │
│  │Coverage    │    │ criteria   │    │ Semantic   │           │
│  │Hash compare│    │ Classify   │    │ review     │           │
│  │Heuristics  │    │ Y/N/P      │    │ Quality    │           │
│  └────────────┘    └────────────┘    └────────────┘           │
│         │                  │                  │                │
│         └──────────────────┼──────────────────┘                │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Result Aggregator                       │   │
│  │  • Combines results from all layers                     │   │
│  │  • Computes final alignment score                       │   │
│  │  • Determines status (PERFECT, UNVERIFIED, etc.)        │   │
│  │  • Collects issues with severity                        │   │
│  │  • Outputs J023-compliant NDJSON                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- Each layer is independently testable
- Can swap LLM providers without changing architecture
- Deterministic layer provides baseline at zero cost
- Results are traceable (which layer produced which finding)

---

### Strategy 6: Audit-by-Committee (Consensus)

**Hypothesis:** Multiple small model runs with consensus voting outperforms single run.

```python
async def audit_with_consensus(
    question: str,
    context: str,
    n_runs: int = 3
) -> tuple[str, float]:
    """
    Run question through multiple small models.
    Return consensus answer and confidence.
    """
    # Run N queries in parallel
    responses = await asyncio.gather(*[
        haiku_query(question, context)
        for _ in range(n_runs)
    ])

    # Count votes
    from collections import Counter
    votes = Counter(responses)
    winner, count = votes.most_common(1)[0]

    # Compute confidence
    confidence = count / n_runs

    if confidence >= 0.67:  # Majority agrees
        return winner, confidence
    else:
        return None, confidence  # No consensus, escalate


# Usage
answer, confidence = await audit_with_consensus(
    "Does this function handle token expiration? [YES/NO/PARTIAL]",
    function_code,
    n_runs=3
)

if answer is None:
    # Escalate to larger model
    answer = await sonnet_query(detailed_prompt, function_code)
```

**Cost analysis:**
```
3x Haiku:     ~$0.003
1x Sonnet:    ~$0.03
Escalation rate (est.): ~20%

Expected cost per audit:
  0.80 × $0.003 + 0.20 × $0.033 = $0.009

vs always-Sonnet: $0.03

Savings: ~70%
```

**When consensus helps:**
- Ambiguous inputs where model might guess differently
- Classification tasks with clear categories
- Reduces variance from model randomness

**When consensus doesn't help:**
- Systematically hard questions (all runs fail the same way)
- Tasks requiring reasoning (not just classification)

---

### Strategy 7: Self-Improving Rules

**Hypothesis:** LLM-discovered patterns can become deterministic rules, reducing future LLM usage.

```python
# When LLM identifies an issue pattern
llm_finding = {
    "issue_type": "MISSING_ERROR_HANDLING",
    "spec_pattern": "MUST handle.*error|SHALL.*exception",
    "impl_indicator": "no try/except block",
    "confidence": 0.95
}

# Extract as deterministic rule
new_rule = Rule(
    id="rule-error-handling-001",
    name="error_handling_required",
    description="Specs requiring error handling should have try/except",

    # When does this rule apply?
    spec_trigger=re.compile(r"MUST handle.*error|SHALL.*exception", re.I),

    # What to check in implementation?
    impl_check=lambda ast_node: has_try_except_block(ast_node),

    # What to report if check fails?
    issue=Issue(
        type="MISSING_ERROR_HANDLING",
        severity="HIGH",
        message="Spec requires error handling but function has no try/except"
    )
)

# Add to rule registry
rules_registry.add(new_rule)

# Future audits check rule first (no LLM needed)
def apply_rules(spec: Spec, impl: Function) -> list[Issue]:
    issues = []
    for rule in rules_registry.all():
        if rule.spec_trigger.search(spec.content):
            if not rule.impl_check(impl.ast_node):
                issues.append(rule.issue)
    return issues
```

**Flywheel effect:**
1. LLM audits find issues
2. Issues with clear patterns become rules
3. Rules catch issues without LLM
4. LLM focuses on novel/complex issues
5. Over time, LLM usage decreases

**Rule sources:**
- Manual (expert encodes known patterns)
- LLM-extracted (from audit findings)
- Community (shared rule libraries)

---

### Strategy 8: Risk-Based Sampling

**Hypothesis:** Not all specs need equal audit attention. Prioritize by risk.

```python
def compute_audit_priority(spec_id: str, context: AuditContext) -> float:
    """
    Higher priority = audit more frequently and/or more deeply.
    """
    priority = 0.0

    # Architectural risk: foundation code is highest risk
    brick = context.get_brick_for_spec(spec_id)
    layer_weight = {0: 2.0, 1: 1.5, 2: 1.0, 3: 0.5}
    priority += layer_weight.get(brick.layer, 0.5)

    # Complexity risk: more implementations = more risk
    impl_count = len(context.get_implementations(spec_id))
    priority += min(impl_count * 0.3, 1.5)

    # Recency risk: recent changes need attention
    days_since_change = context.days_since_hash_change(spec_id)
    if days_since_change < 7:
        priority += 1.5
    elif days_since_change < 30:
        priority += 0.5

    # History risk: previous issues predict future issues
    if context.has_previous_issues(spec_id):
        priority += 1.0

    # Coverage risk: low coverage = higher risk
    coverage = context.get_coverage_percentage(spec_id)
    if coverage < 50:
        priority += 1.0
    elif coverage < 80:
        priority += 0.5

    return priority


def select_for_deep_audit(
    all_specs: list[str],
    context: AuditContext,
    sample_rate: float = 0.1
) -> list[str]:
    """Select top N% by priority for deep audit."""
    scored = [(s, compute_audit_priority(s, context)) for s in all_specs]
    scored.sort(key=lambda x: x[1], reverse=True)

    n = max(1, int(len(all_specs) * sample_rate))
    return [s for s, _ in scored[:n]]
```

**Sampling schedule:**
```
Daily CI:        Level 0 all, Level 1 changed
Weekly:          Level 2 all changed, Level 4 top 10%
Monthly:         Level 4 top 25%
Release:         Level 4 all layer 0 specs
```

---

## Part III: Evaluation Framework

All strategies above are hypotheses. Rigorous evaluation is required before production use.

### The Evaluation Challenge

Agent evaluation is hard because:

1. **Ground truth is expensive** — requires expert labeling
2. **Subjectivity exists** — "does this fulfill the spec?" involves judgment
3. **Compound errors cascade** — bad extraction → bad mapping → bad score
4. **Distribution shift** — lab evals may not match production
5. **Evaluation cost** — running N strategies × M examples is expensive

### Evaluation Layers

#### Layer 1: Component Evaluation

Test each pipeline stage independently:

| Component | Metric | Ground Truth Source |
|-----------|--------|---------------------|
| Criteria Extraction | F1 score vs human | Human-labeled criteria |
| Criteria Mapping (Y/N/P) | Accuracy | Human-labeled mappings |
| Coverage Gap Detection | Precision/Recall | Actual coverage data |
| Issue Detection | Precision/Recall | Human-labeled issues |
| Final Score | Pearson correlation | Human scores |

#### Layer 2: End-to-End Evaluation

Test the complete pipeline:

| Metric | Definition | Target |
|--------|------------|--------|
| Status Accuracy | % matching human label | >90% |
| Score Correlation | Pearson r with human | >0.85 |
| Issue Precision | Found issues that are real | >80% |
| Issue Recall | Found all real issues | >70% |
| Recommendation Quality | Human rating 1-5 | >3.5 |

#### Layer 3: Efficiency Evaluation

Test cost/speed tradeoffs:

| Metric | Definition |
|--------|------------|
| Cost per audit | Total API spend |
| Latency | Wall-clock time |
| Accuracy/$ | Quality per dollar spent |
| Pareto efficiency | No cheaper strategy with same accuracy? |

---

### Ground Truth Acquisition

#### Option A: Expert Labeling (Gold Standard)

```
Process:
1. Select 50-100 diverse (spec, impl, test) triples
2. Two experts independently audit each
3. Measure inter-rater agreement (Cohen's κ)
4. Resolve disagreements through discussion
5. Final labels become ground truth

Cost: 2-4 hours per triple
Quality: High
Limitation: Expert availability, potential bias
```

#### Option B: Synthetic Ground Truth

```
Process:
1. Write specs with known characteristics
2. Write implementations with intentional gaps
3. Write tests with intentional coverage gaps
4. Ground truth is known by construction

Example triple:
  Spec: "Function MUST validate input is positive"
  Impl A: has_validation=True → ALIGNED
  Impl B: has_validation=False → MISALIGNED
  Impl C: validates_wrong_thing=True → PARTIAL

Cost: ~30 min per example
Quality: Medium (may miss real-world complexity)
Limitation: Tests what we think to test
```

#### Option C: Bootstrapped from Production

```
Process:
1. Run multiple strategies on real data
2. When strategies agree → pseudo-label as correct
3. When strategies disagree → human reviews
4. Labeled set grows incrementally

Cost: Amortized over time
Quality: Improves over time
Limitation: Initial strategy quality influences labels
```

#### Option D: Comparative (Pairwise)

```
Process:
1. Run Strategy A and B on same inputs
2. Human judges: "Which audit is better?"
3. Compute Elo ratings or Bradley-Terry scores
4. Rank strategies by relative quality

Cost: Cheaper than absolute labeling
Quality: Good for ranking, not absolute measurement
Limitation: No absolute quality metric
```

---

### Hypotheses to Test

Each strategy implies testable hypotheses:

#### H1: Deterministic Baseline Value
```
Claim: Level 0 catches >50% of structural issues with 100% precision
Test: Run Level 0 on labeled dataset
Metric: Recall for structural issues, Precision
Pass: Recall > 0.5, Precision = 1.0
```

#### H2: Small Model Criteria Extraction
```
Claim: Haiku extracts acceptance criteria with >80% F1
Test: 50 specs with human-labeled criteria
Metric: Precision, Recall, F1
Pass: F1 > 0.80
```

#### H3: Small Model Classification
```
Claim: Haiku Y/N/P classification achieves >85% accuracy
Test: 100 (function, criterion) pairs with human labels
Metric: Accuracy, confusion matrix
Pass: Accuracy > 0.85
```

#### H4: Consensus Improves Accuracy
```
Claim: 3x Haiku consensus beats 1x Haiku at <2x cost
Test: Same 100 pairs, compare 1x vs 3x
Metric: Accuracy, total cost
Pass: Consensus accuracy > 1x accuracy, cost < 2x
```

#### H5: Confidence Calibration
```
Claim: Confidence scores predict error rate (calibrated)
Test: Bin predictions by confidence, measure accuracy per bin
Metric: Calibration curve, ECE (expected calibration error)
Pass: Accuracy increases monotonically with confidence
```

#### H6: Tiered Strategy Efficiency
```
Claim: Tiered audit achieves >90% of full audit quality at <30% cost
Test: Run full (always Level 4) vs tiered on same dataset
Metric: Agreement rate with full, cost ratio
Pass: Agreement > 0.90, cost < 0.30x
```

#### H7: Change Detection Precision
```
Claim: J022 hash changes correctly identify re-audit needs
Test: Historical data with known changes and outcomes
Metric: Precision/Recall for "needs re-audit"
Pass: Recall > 0.95 (don't miss important changes)
```

#### H8: Risk-Based Sampling Coverage
```
Claim: Top 10% by risk priority catches >50% of issues
Test: Deep audit all, measure issue distribution by priority
Metric: % of issues in top 10% by priority
Pass: Issue concentration > 50% in top 10%
```

---

### Evaluation Dataset Schema

```yaml
# eval/dataset/example-001.yaml
id: example-001
category: token-expiration
difficulty: medium
created: 2025-12-06
labeled_by: expert-1
reviewed_by: expert-2

spec:
  id: S-EVAL-001
  content: |
    # Token Expiration
    Authentication tokens MUST expire after 15 minutes of inactivity.

    **Acceptance Criteria:**
    1. Token created with expires_at = now() + 15 minutes
    2. Any operation updates last_activity timestamp
    3. Token rejected if now() > last_activity + 15 minutes

  # Ground truth: human-labeled criteria
  criteria:
    - {id: 1, text: "Token created with expires_at = now() + 15 minutes"}
    - {id: 2, text: "Any operation updates last_activity timestamp"}
    - {id: 3, text: "Token rejected if now() > last_activity + 15 minutes"}

implementation:
  id: F-eval-auth.create_token
  file: eval/code/auth.py
  code: |
    def create_token(user_id: str) -> Token:
        return Token(
            user_id=user_id,
            expires_at=datetime.now() + timedelta(minutes=15),
            last_activity=datetime.now()
        )

  # Ground truth: human-labeled criteria mapping
  criteria_mapping:
    1: YES      # Creates with expires_at
    2: PARTIAL  # Creates last_activity but doesn't update on operations
    3: NO       # Doesn't implement rejection logic

test:
  id: T-eval-auth.test_token_creation
  file: eval/tests/test_auth.py
  code: |
    def test_token_creation():
        token = create_token("user1")
        assert token.expires_at > datetime.now()
        assert token.user_id == "user1"

  # Ground truth: criteria coverage
  criteria_coverage: [1]  # Only validates criterion 1

# Ground truth: overall audit result
ground_truth:
  alignment_status: UNTESTED
  outcome_alignment: ORPHAN
  score: 45

  issues:
    - type: COVERAGE_GAP
      severity: HIGH
      description: "Test doesn't verify expiration rejection"
      affected_criteria: [3]

    - type: PARTIAL_IMPLEMENTATION
      severity: MEDIUM
      description: "last_activity created but never updated"
      affected_criteria: [2]

metadata:
  inter_rater_agreement: true
  labeling_time_minutes: 18
  notes: "Criterion 2 was ambiguous - discussed and clarified"
```

---

### Evaluation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVALUATION PIPELINE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. LOAD                                                        │
│     eval/dataset/*.yaml → examples[]                           │
│                                                                 │
│  2. RUN STRATEGIES                                              │
│     for strategy in [opus_full, tiered, haiku_only,            │
│                      haiku_consensus, escalation]:             │
│         for example in examples:                                │
│             results[strategy][example] = run(strategy, example)│
│                                                                 │
│  3. COMPUTE METRICS                                             │
│     for strategy in strategies:                                 │
│         metrics[strategy] = {                                   │
│             accuracy: compare(results, ground_truth),          │
│             cost: sum(api_costs),                              │
│             latency: sum(times),                               │
│             precision: tp / (tp + fp),                         │
│             recall: tp / (tp + fn),                            │
│         }                                                       │
│                                                                 │
│  4. STATISTICAL TESTS                                           │
│     - Confidence intervals (bootstrap)                         │
│     - Significance tests (McNemar for accuracy)                │
│     - Effect sizes (Cohen's d)                                 │
│                                                                 │
│  5. GENERATE REPORT                                             │
│     eval/reports/eval-{timestamp}.md                           │
│     - Strategy comparison table                                 │
│     - Hypothesis test results                                   │
│     - Error analysis                                            │
│     - Recommendations                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Evaluation CLI

```bash
# Run full evaluation
jigy eval run --dataset eval/dataset --strategies all
# Output: eval/results/run-2025-12-06T14:30:00/

# Compare strategies
jigy eval compare --run eval/results/run-2025-12-06T14:30:00
# Output:
# Strategy          Accuracy  Precision  Recall  Cost    Latency
# opus-full         0.94      0.91       0.89    $1.20   180s
# tiered            0.91      0.88       0.85    $0.35   45s
# haiku-only        0.72      0.78       0.65    $0.08   12s
# haiku-consensus   0.81      0.82       0.74    $0.18   18s
# escalation        0.89      0.86       0.82    $0.28   35s

# Test specific hypothesis
jigy eval hypothesis H3 --dataset eval/dataset
# Output:
# H3: Haiku Y/N/P Classification
# ─────────────────────────────
# Accuracy: 0.87 (95% CI: 0.82-0.92)
#
# Confusion Matrix:
#          Pred
#          YES  NO   PARTIAL
# True YES  45   2    3
#      NO    1  28    1
#      PARTIAL 3  2   15
#
# Result: PASS (threshold: 0.85, observed: 0.87)

# Analyze where strategies disagree
jigy eval disagreements --run eval/results/run-2025-12-06T14:30:00
# Output: Examples where strategies disagree, for human review

# Add new labeled example
jigy eval label --interactive
# Guided process to create ground truth for new example

# Component-level evaluation
jigy eval component criteria-extraction --dataset eval/dataset --model haiku
# Tests just the criteria extraction component
```

---

### Practical Evaluation Plan

#### Phase 1: Minimum Viable Dataset (2 days)

```
Goal: 20 high-quality labeled examples

Distribution:
├── Perfect alignment (4 examples)
├── Missing implementation (3 examples)
├── Missing tests (3 examples)
├── Coverage gaps (3 examples)
├── Partial implementation (3 examples)
├── Outcome misalignment (2 examples)
└── Edge cases (2 examples)

Source: JIG's own specs (dogfooding)
Method: Two reviewers, resolve disagreements
```

#### Phase 2: Component Validation (1 day)

```
Goal: Validate H2, H3 (small model capabilities)

Tests:
1. Criteria extraction: 20 specs → Haiku → compare to human
2. Y/N/P classification: 60 pairs → Haiku → compare to human

Decision gate: If F1 < 0.75 or Accuracy < 0.80,
              small model strategy is not viable
```

#### Phase 3: Strategy Comparison (2 days)

```
Goal: Rank strategies by efficiency frontier

Tests:
1. Run all strategies on 20 examples
2. Compute metrics table
3. Plot accuracy vs cost (Pareto frontier)
4. Statistical significance tests

Output: Recommended strategy with confidence bounds
```

#### Phase 4: Expand and Iterate (Ongoing)

```
Actions:
1. Add examples where strategies disagree (hard cases)
2. Add examples from real audit requests (distribution shift)
3. Track metrics over time (regression detection)
4. Refine strategies based on error analysis
```

---

## Part IV: Integration

### With J022 (Change Detection)

```
J022 provides:
  - Hash for each spec, impl, test
  - Detection of which pairs changed
  - Audit log of previous decisions

J024 uses:
  - Hash changes to determine audit depth
  - Previous audit results as cache
  - Audit log to track strategy decisions
```

### With J023 (Audit Output)

```
J023 defines:
  - NDJSON output format
  - Index aggregation schema
  - Query patterns

J024 produces:
  - Audit results in J023 format
  - Strategy metadata in _meta record
  - Evaluation metrics for analysis
```

### CLI Commands

```bash
# Audit commands (production)
jigy audit S-001                    # Audit single spec (auto depth)
jigy audit S-001 --depth 4          # Force full depth
jigy audit --all --depth 0          # Structural check all
jigy audit --changed --depth 2      # Criteria mapping for changed

# Evaluation commands (development)
jigy eval run --dataset DIR         # Run evaluation
jigy eval compare --run DIR         # Compare strategies
jigy eval hypothesis H3             # Test specific hypothesis

# Strategy configuration
jigy config audit.default_strategy tiered
jigy config audit.escalation_threshold 0.65
jigy config audit.sampling_rate 0.1
```

---

## Open Questions

1. **What is the human ceiling?** If experts disagree 15% of the time, is 85% accuracy the maximum achievable?

2. **How much labeled data is enough?** 20 examples for initial validation, but how many for reliable strategy comparison?

3. **How to handle distribution shift?** Lab examples may not reflect production audit requests.

4. **Should strategies be spec-specific?** Different spec types (security, performance, UI) may need different approaches.

5. **How to measure recommendation quality?** Accuracy on classification is measurable; "good advice" is subjective.

6. **When to retrain/recalibrate?** As codebase evolves, do confidence thresholds need adjustment?

---

## References

- **J022:** Alignment Change Detection (hash-based change tracking)
- **J023:** Audit Strategies and Mechanisms (output format, query patterns)
- **J017:** JIG Concept v9 (S-F-T triangle, alignment measurement)
- **A001:** Core Artifacts Contract (artifact schemas)

---

## Appendix: Strategy Comparison Summary

| Strategy | Cost | Latency | Expected Accuracy | Best For |
|----------|------|---------|-------------------|----------|
| Opus Full | $$$ | Slow | Highest | Final review, critical specs |
| Tiered | $$ | Medium | High | Default production use |
| Haiku Only | $ | Fast | Medium | Quick checks, CI |
| Consensus | $$ | Medium | Medium-High | Uncertain classifications |
| Escalation | $$ | Variable | High | Cost-sensitive production |
| Deterministic | Free | Instant | Limited | Structural validation |
| Risk Sampling | $$ | Variable | High (targeted) | Large codebases |
| Self-Improving | Decreasing | Improving | Improving | Long-term deployment |

**Recommendation:** Start with Tiered strategy, validate with evaluation framework, adjust based on measured accuracy/cost tradeoffs.

---

_All strategies are hypotheses until validated empirically._
