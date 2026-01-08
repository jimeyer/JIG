---
type: concept
title: "JIG Alignment Inspector Agent"
status: active
created: 1736387200
created_human: "2026-01-08 16:00 PST"
updated: 1736402400
updated_human: "2026-01-08 20:20 PST"
parent: "[[C021_CONCEPT_Alignment_Triangle_Metrics]]"
children: []
prompt: |
  Inspector agent for qualitative alignment review in JIG workflows.
  Integrated with Five Stage Audit as Stage 5 implementation.
  Explains WHY metrics are low, not just WHAT is wrong.
  Generates actionable remediation plans from audit findings.
---

# JIG Alignment Inspector Agent

_Qualitative alignment review integrated with quantitative audit_

---

## Core Insight

The Five Stage Audit ([[C023_PLAN_Five_Stage_Alignment_Audit]]) produces **measurements**:
- Triangle closure: 87.7%
- Verification gaps: 9
- Cohesion: 83.1%

But measurements don't explain themselves. A 0.0 closure score tells you something is wrong—not what's wrong, why it matters, or how to fix it.

**The Inspector produces understanding and action.**

| Audit | Inspector |
|-------|-----------|
| Finds WHAT | Explains WHY |
| Computes metrics | Interprets meaning |
| Flags items | Clusters into work |
| Reports numbers | Generates plans |

The audit is the diagnostic scan. The inspector is the doctor explaining the results.

---

## What Inspector Is (and Isn't)

### Not a Test Runner

TDD requires tight feedback loops. Inserting a separate agent to run tests breaks the loop with latency at each iteration. The orchestrator already verifies test execution independently.

### A Reviewer

Inspector reads artifacts and judges alignment quality:

| Artifact | What Inspector Checks |
|----------|----------------------|
| Spec | Are acceptance criteria testable? Is this behavior or implementation? |
| Tests | Does each criterion have a verifying assertion? Are edge cases covered? |
| Code | Does implementation match spec semantics? Are concerns properly bounded? |
| Triangle | Why is closure low? Missing tests or wrong tests? |

---

## Integration with Five Stage Audit

```
                    AUDIT + INSPECTOR INTEGRATION
                    ═════════════════════════════

    ┌─────────────┐
    │  STAGE 1    │──→ Checkpoint: complexity outliers
    │  CODE       │    "Why is show_towers at 55 CC?"
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  STAGE 2    │──→ Checkpoint: orphan review
    │  TEST       │    "Is __main__.py intentionally untested?"
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  STAGE 3    │──→ FULL INSPECTION (if score <70)
    │  SPEC       │    Semantic analysis of every gap
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  STAGE 4    │──→ Checkpoint: hierarchy anomalies
    │  HIERARCHY  │    "Should O-026 be split?"
    └──────┬──────┘
           │
    ┌──────▼──────────────────────────────────┐
    │  STAGE 5: INSPECTOR SYNTHESIS           │
    │  ─────────────────────────────────────  │
    │  • Explain all flagged items            │
    │  • Challenge false positives            │
    │  • Cluster related findings             │
    │  • Generate remediation WUs             │
    └──────┬──────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────────┐
    │  AUDIT_REPORT.md + REMEDIATION_PLAN.md  │
    └─────────────────────────────────────────┘
```

### Stage 5 as Inspector Protocol

The audit's Stage 5 "SEMANTIC" was underspecified. Inspector provides concrete methodology:

```
Stage 5 (Inspector Protocol)
├── Input: All items flagged in Stages 1-4
│   ├── Verification gaps (Stage 3)
│   ├── Orphan specs (Stage 3)
│   ├── Complexity outliers (Stage 1)
│   ├── Grab-bag outcomes (Stage 4)
│   └── Low-closure specs (Stage 3)
│
├── For each flagged item:
│   ├── Read relevant artifacts (spec, code, tests)
│   ├── Apply appropriate protocol (see below)
│   └── Produce structured finding
│
└── Synthesis:
    ├── Challenge false positives
    ├── Cluster related findings into WUs
    ├── Prioritize by impact
    └── Generate remediation plan
```

### Score-Based Inspection Tiering

Don't inspect everything. Use Stage 1-4 scores to allocate inspection budget:

| Stage Score | Inspection Level | Rationale |
|-------------|------------------|-----------|
| >85 | Skip | Metrics suggest health; trust them |
| 70-85 | Spot-check | Sample review to validate metrics |
| <70 | Full | Metrics suggest problems; understand each |

Example from jig-dev audit (76 overall):
- Stage 1 (75): Spot-check top 5 complexity outliers
- Stage 2 (84): Skip (coverage healthy)
- Stage 3 (68): **Full inspection** of all 9 verification gaps
- Stage 4 (80): Spot-check the 1 grab-bag outcome

This economizes LLM tokens where problems likely exist.

### Stage Checkpoints

Run micro-inspections after each stage, not just at the end:

**After Stage 1 (CODE):**
```
Inspector reviews: Complexity outliers >40 CC

show_towers_command (55 CC):
  "Function conflates 5 concerns:
   - Tower data loading
   - Filtering by criteria
   - Sorting logic
   - Display formatting
   - Output mode selection

   Recommendation: Extract tower_filter(), tower_sort(),
   format_tower_row(). Each becomes testable unit."
```

**After Stage 2 (TEST):**
```
Inspector reviews: Orphan files with 0% coverage

impl_graph/analyzers/__main__.py (0%):
  "This is a CLI entry point (3 lines). Entry points
   conventionally untested in unit suite.

   Verify: integration tests exercise `python -m jig.impl_graph.analyzers`
   Action: Mark as acceptable non-coverage in audit config."
```

**After Stage 3 (SPEC):**
```
Inspector reviews: All 9 verification gaps

Clustering analysis:
  Cluster A (6 specs): S-080 through S-085
    All in intent_graph/generator.py
    All describe intent graph hierarchy nodes/edges
    Single cohesive concern

  Cluster B (1 spec): S-027
    Isolated in cli/validate.py
    Auto-validation trigger

  Cluster C (2 specs): S-028, S-086
    May be false positives (see challenge protocol)
```

**After Stage 4 (HIERARCHY):**
```
Inspector reviews: Grab-bag outcomes (cohesion <50%)

O-026 "Towers Enforce Component Isolation" (44% cohesion):
  "Specs scatter across validation, intent_graph, cli bricks.

   Analysis:
   - S-086, S-087, S-088, S-089: Schema/validation concerns
   - S-090, S-091: Display concerns (jigy towers, jigy matrix)

   Recommendation: Split into:
   - O-026a 'Tower Schema Validation' (validation brick)
   - O-026b 'Tower Visibility Commands' (cli brick)"
```

---

## Inspector Protocols

### Protocol 1: Triangle Explanation

For specs with low closure, explain semantically:

```
INPUT: S-080 "Charter Node In Intent Graph" - closure: 0.0

SPEC CONTENT:
  "Intent graph SHALL include node with type=CHARTER containing:
   - title from Charter.md frontmatter
   - defines_goals edges to each G-### listed in charter"

IMPLEMENTATION FOUND:
  generator.py:_load_charter_node() lines 180-210
  - Reads Charter.md via _parse_frontmatter()
  - Creates node dict with type="CHARTER"
  - Iterates charter["defines_goals"], creates edges

TESTS FOUND:
  None with @jig.verifies("S-080")

ACCEPTANCE CRITERIA MAPPING:
  - [ ] "Node type=CHARTER exists" → NO TEST
  - [ ] "Node contains charter title" → NO TEST
  - [ ] "defines_goals edges present" → NO TEST
  - [ ] "Edge targets match charter goals" → NO TEST

IMPACT ASSESSMENT:
  Charter node is root of intent hierarchy. If broken,
  entire goal→outcome→spec traceability fails silently.
  High-value test target.

RECOMMENDED TESTS:
  1. test_charter_node_exists()
     Assert: intent graph contains exactly one CHARTER node

  2. test_charter_node_title()
     Assert: CHARTER node title matches Charter.md title

  3. test_charter_defines_goals_edges()
     Assert: CHARTER has defines_goals edge for each G-### in charter

  4. test_charter_goal_references_valid()
     Assert: Each edge target exists as GOAL node in graph

VERDICT: Genuine gap. Recommend WU to add tests.
```

### Protocol 2: Challenge (Adversarial Review)

Inspector attempts to **invalidate** audit findings:

```
INPUT: S-086 "Brick Tower Field Optional" - closure: 0.0

AUDIT CLAIM: "Verification gap - has implementation, no tests"

CHALLENGE:
  Implementation: validation/bricks.py:validate_brick_definitions()
    Lines 45-52 handle optional tower field

  Related tests:
    test_tower_value_format - exercises tower when present
    test_brick_without_tower - exercises tower when absent
    test_cross_tower_isolation - exercises tower constraint

  These tests DO exercise the optional tower path.
  They lack @jig.verifies("S-086") decorator.

VERDICT: False positive. Coverage exists, decorator missing.

RECOMMENDATION:
  Add @jig.verifies("S-086") to test_brick_without_tower
  No new test code needed.
```

```
INPUT: S-028 "CLI Command to Generate Intent Graph" - closure: 0.0

AUDIT CLAIM: "Verification gap - has implementation, no tests"

CHALLENGE:
  Implementation: intent_graph/generator.py:generate_intent_graph()

  This is invoked by: jigy rebuild intent

  Integration tests exist:
    tests/integration/test_rebuild_e2e.py exercises full rebuild

  Unit testing CLI commands directly is unusual.
  The command is a thin wrapper around generator.

VERDICT: Likely acceptable. Integration coverage exists.

RECOMMENDATION:
  Document as "integration-tested, unit test optional"
  Or add focused test for generator.generate_intent_graph()
```

### Protocol 3: Remediation Generation

Cluster findings into actionable work units:

```
INPUT: 9 verification gaps from Stage 3

CLUSTERING ANALYSIS:

Cluster A: Intent Graph Hierarchy (6 specs)
  Specs: S-080, S-081, S-082, S-083, S-084, S-085
  Location: src/jig/intent_graph/generator.py
  Concern: Charter/Goal/Architecture nodes and edges

  All specs describe related graph structure.
  Single test file can verify all.

  → WU-1: Add intent graph hierarchy tests
    New file: tests/jig/intent_graph/test_hierarchy_nodes.py
    Tests: ~8-10 covering all 6 specs
    Effort: Medium (1-2 hours)

Cluster B: False Positives (2 specs)
  Specs: S-028, S-086

  Per challenge protocol, these have implicit coverage.

  → WU-2: Decorator hygiene
    Add @jig.verifies decorators to existing tests
    Effort: Trivial (15 minutes)

Cluster C: Isolated Gap (1 spec)
  Spec: S-027 "Auto-Validation in Rebuild Commands"
  Location: src/jig/cli/validate.py:_run_auto_validation

  Standalone concern, needs dedicated test.

  → WU-3: Add auto-validation trigger test
    File: tests/cli/test_rebuild.py (extend)
    Tests: 2 (trigger fires, --no-validate suppresses)
    Effort: Low (30 minutes)

REMEDIATION PLAN:
  WU-1: Intent graph hierarchy tests [MEDIUM]
  WU-2: Decorator hygiene [TRIVIAL]
  WU-3: Auto-validation test [LOW]

  Total estimated effort: 2-3 hours
  Expected closure improvement: 9 gaps → 0 gaps
```

### Protocol 4: Spec Quality Review

For specs flagged by naming violations or staleness:

```
INPUT: S-045 "Improved Token Handling" (naming violation: temporal)

ANALYSIS:
  Title contains "Improved" - temporal language.
  Suggests this was a refactoring task, not evergreen behavior.

  Spec content:
    "Token handling SHALL use the new TokenManager class..."

  This reads like implementation instructions, not requirements.

RECOMMENDATION:
  Rewrite as behavior spec:
    "Token Lifecycle Management"
    "Tokens SHALL be created with configurable expiry..."

  Or: Mark as SUPERSEDED if original behavior spec exists.
```

---

## Output Artifacts

### Stage 5 JSON

```json
{
  "stage": 5,
  "name": "INSPECTOR",
  "timestamp": "2026-01-08T19:30:00Z",
  "inspection_mode": "tiered",
  "items_reviewed": 15,
  "findings": [
    {
      "item": "S-080",
      "type": "verification_gap",
      "verdict": "genuine",
      "explanation": "Charter node tests missing...",
      "cluster": "intent-hierarchy",
      "recommended_tests": ["test_charter_node_exists", "..."]
    },
    {
      "item": "S-086",
      "type": "verification_gap",
      "verdict": "false_positive",
      "explanation": "Implicit coverage via test_brick_without_tower",
      "recommendation": "Add decorator"
    }
  ],
  "clusters": [
    {
      "id": "intent-hierarchy",
      "specs": ["S-080", "S-081", "S-082", "S-083", "S-084", "S-085"],
      "wu_recommendation": "WU-1"
    }
  ],
  "health_score": 82,
  "false_positive_count": 2,
  "genuine_gap_count": 7
}
```

### Remediation Plan (Markdown)

```markdown
# Remediation Plan

Generated: 2026-01-08
Audit Score: 76/100 → Projected: 85/100

## Work Units

### WU-1: Intent Graph Hierarchy Tests [PRIORITY: HIGH]

**Specs Covered:** S-080, S-081, S-082, S-083, S-084, S-085

**Location:**
- Implementation: src/jig/intent_graph/generator.py
- Tests: tests/jig/intent_graph/test_hierarchy_nodes.py (new)

**Acceptance Criteria to Verify:**
- Charter node exists with type=CHARTER
- Goal nodes created for each G-###
- Architecture nodes created for each A-###
- defines_goals edges from charter to goals
- supports_goals edges from architecture to goals
- constrains edges from architecture to specs

**Estimated Effort:** 1-2 hours

---

### WU-2: Decorator Hygiene [PRIORITY: LOW]

**Specs Covered:** S-028, S-086

**Action:** Add @jig.verifies decorators to existing tests

| Spec | Add Decorator To |
|------|------------------|
| S-086 | test_brick_without_tower |
| S-028 | test_rebuild_intent_e2e |

**Estimated Effort:** 15 minutes

---

### WU-3: Auto-Validation Trigger Test [PRIORITY: MEDIUM]

**Spec Covered:** S-027

**Location:**
- Implementation: src/jig/cli/validate.py:_run_auto_validation
- Tests: tests/cli/test_rebuild.py (extend)

**Tests to Add:**
1. test_rebuild_triggers_validation
2. test_rebuild_no_validate_flag_skips

**Estimated Effort:** 30 minutes
```

---

## Live Mode: Alignment Oracle

Beyond periodic audit, inspector can serve as always-available advisor during development:

```
Developer: "About to implement S-147. What should tests cover?"

Inspector (live):
  "S-147 'Subscription Callback Protocol' has 3 acceptance criteria:

   1. Register observer for key changes
   2. Callback receives (key, old_value, new_value)
   3. Re-subscription is idempotent

   Minimum test set:
   - test_subscribe_registers_observer
   - test_callback_receives_change_tuple
   - test_resubscribe_idempotent

   Edge cases (inferred from spec language):
   - Subscribe to non-existent key
   - Callback that raises exception
   - Unsubscribe without prior subscribe

   Related specs: S-148 (unsubscribe) - coordinate fixtures."
```

```
Developer: "I just wrote these tests for S-042. Did I miss anything?"

Inspector (live):
  "S-042 'Outcomes Must Specify Specifications' requires:

   1. Outcomes have specifies: field
   2. References are valid S-### IDs
   3. Each referenced spec exists

   Your tests cover:
   [x] test_outcome_requires_specifies - criterion 1
   [x] test_outcome_invalid_spec_ref - criterion 2
   [ ] test_outcome_dangling_spec_ref - criterion 3 MISSING

   Add test verifying error when specifies: ['S-999']
   and S-999 doesn't exist."
```

This shifts inspector from post-hoc review to proactive guidance.

---

## Invocation Triggers

### During Audit

| Trigger | Action |
|---------|--------|
| Stage score <70 | Full inspection of that stage's findings |
| Stage score 70-85 | Spot-check sample of findings |
| Stage score >85 | Skip inspection for that stage |
| End of audit | Synthesis and remediation generation |

### During Development (Live Mode)

| Trigger | Action |
|---------|--------|
| `jigy inspect S-###` | Full inspection of single spec |
| Pre-commit hook | Quick check of changed specs |
| WU completion | Review alignment of completed work |
| PLAN completion | Comprehensive review before declaring done |

### Configuration

```yaml
# jig.toml
[inspector]
mode = "selective"  # always | selective | never

[inspector.triggers]
stage_threshold = 70  # Full inspection below this
spot_check_sample = 3  # Items to check in 70-85 range
live_mode = true      # Enable jigy inspect command

[inspector.protocols]
challenge = true      # Run adversarial review
remediation = true    # Generate WU plan
```

---

## Cost/Benefit Analysis

### Benefits

1. **Explains measurements** - audit says 68%, inspector says why
2. **Catches false positives** - not every low score is a real problem
3. **Generates action** - findings become concrete work units
4. **Fresh perspective** - second opinion on spec interpretation
5. **Systematic rigor** - same checklist applied to every item

### Costs

1. **Latency** - additional LLM calls per reviewed item
2. **Tokens** - inspector reads spec + tests + code per item
3. **False positives** - inspector may flag acceptable approaches
4. **Complexity** - another agent to coordinate

### ROI by Context

| Context | Inspector Value |
|---------|-----------------|
| Healthy codebase (>85 audit) | Low - metrics sufficient |
| Problem area (<70 audit) | High - explains what's wrong |
| New specs being implemented | High - catches misunderstandings early |
| Refactoring existing code | Medium - verifies behavior preserved |
| Greenfield project | High - establishes patterns |

---

## Relation to Other Concepts

**[[C020_CONCEPT_Alignment_Integrity]]** - Defines drift and coherence. Inspector detects semantic drift that metrics miss.

**[[C021_CONCEPT_Alignment_Triangle_Metrics]]** - Provides quantitative triangle metrics. Inspector provides qualitative interpretation.

**[[C022_CONCEPT_Stratified_Alignment_Verification]]** - Staged verification approach. Inspector is Stage 5 implementation.

**[[C023_PLAN_Five_Stage_Alignment_Audit]]** - Audit procedure. Inspector integrates as final stage and checkpoint system.

**taskDoPLAN / taskDoWU** - Execution workflow. Inspector can review WU output before orchestrator continues.

---

## Implementation Notes

### Inspector Prompt Template

```
You are the JIG Alignment Inspector reviewing {item_type} {item_id}.

## Context
{audit_findings_for_item}

## Artifacts

### Spec Content
{spec_markdown}

### Implementation
{code_with_line_numbers}

### Tests
{test_code_with_line_numbers}

## Your Task

Apply the {protocol} protocol:

{protocol_instructions}

## Output Format

Return structured JSON:
{
  "item": "{item_id}",
  "verdict": "genuine_gap | false_positive | acceptable",
  "explanation": "...",
  "acceptance_criteria_mapping": [...],
  "recommended_actions": [...],
  "confidence": 0.0-1.0
}
```

### Orchestration

```python
async def run_stage_5_inspector(audit_results):
    findings = []

    # Collect items to inspect based on scores
    items = select_items_for_inspection(audit_results)

    # Run appropriate protocol for each item
    for item in items:
        if item.type == "verification_gap":
            finding = await run_protocol(
                "triangle_explanation", item
            )
            # Then challenge it
            challenge = await run_protocol(
                "challenge", item, finding
            )
            finding.challenge_result = challenge

        elif item.type == "complexity_outlier":
            finding = await run_protocol(
                "complexity_review", item
            )

        findings.append(finding)

    # Cluster and generate remediation
    clusters = cluster_findings(findings)
    plan = generate_remediation_plan(clusters)

    return InspectorReport(
        findings=findings,
        clusters=clusters,
        remediation_plan=plan
    )
```

---

## Integration with PLAN Execution Workflow

The Inspector integrates with taskDoPLAN (orchestrator) and taskDoWU (worker) to provide alignment quality gates during active development, not just periodic audits.

### Current Flow (Without Inspector)

```
taskDoPLAN (Orchestrator)
│
├─→ For each WU:
│     ├─→ Launch taskDoWU sub-agent
│     │     ├── TDD: tests → code → verify
│     │     └── Return structured report
│     │
│     ├─→ Independent verification
│     │     ├── pytest
│     │     └── jigy validate
│     │
│     ├─→ Decision: CONTINUE | STOP | RETRY
│     ├─→ Journal entry
│     └─→ Commit
│
├─→ Validation WU
├─→ Cleanup WU
├─→ Delete deprecated O/S nodes
└─→ JIG Summary Report
```

### Proposed Flow (With Inspector)

```
taskDoPLAN (Orchestrator)
│
├─→ For each WU:
│     │
│     ├─→ Launch taskDoWU sub-agent
│     │     ├── TDD: tests → code → verify
│     │     └── Return report + Alignment Confidence
│     │
│     ├─→ Independent verification
│     │     ├── pytest
│     │     └── jigy validate
│     │
│     ├─→ [NEW] Selective Inspector (if triggered)
│     │     ├── Trigger: NEW spec in JIGPLAN
│     │     ├── Trigger: Notable field has "friction"
│     │     ├── Trigger: Alignment Confidence = LOW
│     │     ├── Trigger: WU touched >3 specs
│     │     └── Returns: LGTM | FINDINGS
│     │
│     ├─→ Decision: CONTINUE | STOP | RETRY | REMEDIATE
│     ├─→ Journal entry (include Inspector findings)
│     └─→ Commit
│
├─→ Validation WU (verifies SCOPE is solved)
│
├─→ [NEW] Pre-Cleanup Inspector Review (MANDATORY)
│     ├─→ Run on ALL specs touched by this PLAN
│     │     ├── Triangle explanation for each
│     │     ├── Challenge any gaps found
│     │     └── Cluster findings into remediation WUs
│     │
│     ├─→ If FINDINGS with GENUINE gaps:
│     │     ├── Generate remediation WUs
│     │     ├── Execute remediation WUs
│     │     └── Re-run Inspector (loop until clean)
│     │
│     └─→ If LGTM or only FALSE_POSITIVES:
│           └── Continue to Cleanup
│
├─→ Cleanup WU
├─→ Delete deprecated O/S nodes
└─→ JIG Summary Report (includes Inspector summary)
```

### Per-WU Selective Inspection

Inspector doesn't run on every WU—only when risk signals are present.

**Trigger conditions:**

| Condition | Inspection Level |
|-----------|------------------|
| WU implements CREATE spec (new in JIGPLAN) | Full |
| Worker report has friction in Notable field | Quick |
| Worker sets Alignment Confidence = LOW | Full |
| Worker explicitly requests review | Full |
| WU touches >3 specs | Quick |
| None of the above | Skip |

**Quick vs Full inspection:**
- **Quick:** Acceptance criteria audit only (~30 seconds)
- **Full:** Triangle explanation + acceptance criteria + challenge (~2 minutes)

**Sequence diagram:**

```
Orchestrator                    Worker (taskDoWU)              Inspector
    │                                │                              │
    ├─── "Execute WU3" ─────────────→│                              │
    │                                │                              │
    │                                ├── TDD cycle                  │
    │                                ├── Write report               │
    │                                │                              │
    │←── Structured Report ──────────┤                              │
    │    Status: COMPLETE            │                              │
    │    Alignment Confidence: LOW   │                              │
    │    Notable: "S-147 wording     │                              │
    │     confusing"                 │                              │
    │                                                               │
    ├── Independent verify                                          │
    │   ├── pytest ✓                                                │
    │   └── jigy validate ✓                                         │
    │                                                               │
    ├── Check triggers:                                             │
    │   • NEW spec? No                                              │
    │   • Notable friction? YES ◄───────────────────────────────────┤
    │   • Confidence LOW? YES                                       │
    │                                                               │
    ├─── "Review S-147 alignment" ─────────────────────────────────→│
    │                                                               │
    │                                                               ├── Read spec
    │                                                               ├── Read tests
    │                                                               ├── Read impl
    │                                                               │
    │←── Inspector Report ──────────────────────────────────────────┤
    │    Verdict: GENUINE_GAP                                       │
    │    Missing: Criterion 3 test                                  │
    │    Recommendation: Add test                                   │
    │                                                               │
    ├── Decision: REMEDIATE                                         │
    │                                                               │
    ├─── "Execute remediation" ─────→│                              │
    │                                ├── Add missing test           │
    │←── Complete ───────────────────┤                              │
    │                                                               │
    ├─── "Re-review S-147" ────────────────────────────────────────→│
    │←── LGTM ──────────────────────────────────────────────────────┤
    │                                                               │
    └── CONTINUE to next WU
```

### Pre-Cleanup Inspector Review

**Mandatory** checkpoint after Validation WU, before Cleanup WU.

**Purpose:** Catch any alignment gaps before declaring the PLAN complete.

**Scope:** All specs from JIGPLAN (CREATE and UPDATE actions).

**Process:**

```
1. Collect all specs from JIGPLAN
   └── CREATE: S-200, S-201
   └── UPDATE: S-147, S-148, S-149

2. Launch Inspector (full review, all specs)

3. Process findings:
   │
   ├── All LGTM?
   │   └── Continue to Cleanup WU
   │
   ├── GENUINE gaps found?
   │   ├── Generate remediation WUs
   │   ├── Execute remediation WUs (via taskDoWU)
   │   ├── Re-run Inspector
   │   └── Loop (max 3 iterations, then escalate)
   │
   └── Only FALSE_POSITIVES?
       └── Add decorator hygiene tasks to Cleanup WU

4. Inspector sign-off: "All specs LGTM"

5. Continue to Cleanup WU
```

### New Decision: REMEDIATE

Add to taskDoPLAN decision framework:

| Decision | When to Use |
|----------|-------------|
| CONTINUE | All gates pass, Inspector LGTM or skipped |
| STOP | Escalation trigger, need human input |
| RETRY | Transient failure, sub-agent can fix |
| **REMEDIATE** | Inspector found fixable gaps |

**REMEDIATE conditions:**
- Inspector verdict = GENUINE_GAP
- Gap is test coverage issue (missing test, weak assertion)
- Gap is decorator issue (missing @jig.verifies)
- No architectural decisions required
- No spec clarification needed

**REMEDIATE sequence:**
1. Generate remediation micro-WU from Inspector recommendation
2. Execute micro-WU (focused, single concern)
3. Re-run Inspector on affected spec
4. If LGTM → CONTINUE
5. If still GENUINE → STOP (escalate)

### Changes to taskDoWU Report Format

Add new fields to worker report:

```markdown
**Status**: COMPLETE | BLOCKED | FAILED

**Gates**: X/Y passed
[existing fields]

**Alignment Confidence**: HIGH | MEDIUM | LOW
- HIGH: Spec clear, all criteria obviously tested
- MEDIUM: Some interpretation required, believe coverage complete
- LOW: Significant interpretation, recommend Inspector review

**Request Inspector Review**: YES | NO
- If YES, explain what to review:
  "S-147 criterion 3 - is this test sufficient for idempotency?"

**Notable** (enhanced):
- Friction keywords trigger inspection: "confusing", "unclear",
  "ambiguous", "interpreted", "assumed", "guessed"
- Example: "Spec S-147 acceptance criteria were ambiguous"

[rest of report]
```

### Changes to taskDoPLAN

**New section: Inspector Integration**

```markdown
## Inspector Integration

### Per-WU Inspection (Selective)

After independent verification, check Inspector triggers:

| Trigger | Action |
|---------|--------|
| WU implements CREATE spec | Full Inspector review |
| Notable field has friction keywords | Quick Inspector review |
| Alignment Confidence = LOW | Full Inspector review |
| Worker requests review | Full Inspector review |
| WU touches >3 specs | Quick Inspector review |
| None | Skip inspection |

If Inspector returns FINDINGS:
- GENUINE gaps → REMEDIATE decision
- FALSE_POSITIVE → Note for Cleanup WU decorator hygiene

### Pre-Cleanup Inspection (Mandatory)

After Validation WU, before Cleanup WU:

1. Collect all specs from JIGPLAN (CREATE + UPDATE)
2. Launch Inspector with full review scope
3. Process findings:
   - GENUINE → Generate and execute remediation WUs
   - FALSE_POSITIVE → Add to Cleanup WU
   - LGTM → Continue
4. Loop until all specs LGTM (max 3 iterations)
5. Escalate if loop exhausted

### Modified JIG Summary Report

Add Inspector summary section:

| Spec | Review Result | Notes |
|------|---------------|-------|
| S-147 | LGTM | All criteria verified |
| S-148 | FALSE_POSITIVE | Decorator added |
| S-200 | REMEDIATED | Added edge case test |

Remediation WUs executed: N
Final state: All specs LGTM
```

### Complete Workflow Sequence

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PLAN EXECUTION WITH INSPECTOR                         │
└─────────────────────────────────────────────────────────────────────────┘

1. PRE-EXECUTION
   ├── Create branch
   ├── Verify JIGPLAN approved
   ├── Create JOURNAL file
   └── Note which specs are CREATE vs UPDATE

2. PER-WU LOOP
   │
   ├── Launch taskDoWU sub-agent
   │     ├── TDD cycle
   │     └── Return report with Notable + Alignment Confidence
   │
   ├── Independent verification
   │     ├── pytest
   │     └── jigy validate
   │
   ├── Check Inspector triggers
   │     ├── CREATE spec? ──────────────────→ Full Inspector
   │     ├── Notable has friction? ─────────→ Quick Inspector
   │     ├── Alignment Confidence LOW? ─────→ Full Inspector
   │     ├── Worker requests review? ───────→ Full Inspector
   │     └── None ──────────────────────────→ Skip
   │
   ├── If Inspector ran:
   │     ├── LGTM ──────────────────────────→ CONTINUE
   │     ├── FALSE_POSITIVE ────────────────→ Note, CONTINUE
   │     ├── GENUINE (fixable) ─────────────→ REMEDIATE
   │     └── GENUINE (complex) ─────────────→ STOP
   │
   ├── Journal entry (include Inspector findings)
   │
   └── Commit

3. VALIDATION WU
   ├── Execute Validation WU (verifies SCOPE is solved)
   └── If fails: investigate, fix, re-validate

4. PRE-CLEANUP INSPECTOR REVIEW (MANDATORY)
   │
   ├── Collect all specs from JIGPLAN
   │
   ├── Launch Inspector (full review, all specs)
   │
   ├── Process findings:
   │     │
   │     ├── All LGTM? ─────────────────────→ Continue to Cleanup
   │     │
   │     ├── GENUINE gaps?
   │     │     ├── Generate remediation WUs
   │     │     ├── Execute via taskDoWU
   │     │     ├── Re-run Inspector
   │     │     └── Loop (max 3, then escalate)
   │     │
   │     └── Only FALSE_POSITIVES?
   │           └── Add decorator tasks to Cleanup
   │
   └── Inspector sign-off required before Cleanup

5. CLEANUP WU
   ├── Delete deprecated code
   ├── Fix decorator hygiene (from Inspector)
   └── Final refactoring

6. POST-EXECUTION
   ├── Delete deprecated O/S nodes
   ├── jigy rebuild && jigy validate
   ├── JIG Summary (with Inspector summary)
   ├── Journal synthesis
   └── Final commit
```

### Friction Keywords

Words in Notable field that trigger Inspector review:

| Category | Keywords |
|----------|----------|
| Ambiguity | confusing, unclear, ambiguous, vague |
| Interpretation | interpreted, assumed, guessed, inferred |
| Gaps | missing, incomplete, not specified, edge case |
| Uncertainty | unsure, uncertain, might be wrong |

**Example Notable entries that trigger:**
- "Spec S-147 wording was confusing - took 3 reads"
- "Had to assume idempotency means re-subscribe returns same observer"
- "Edge case for empty input not specified in acceptance criteria"
- "Uncertain if null check is required by spec"

**Example Notable entries that don't trigger:**
- "Test setup took longer than expected"
- "Found useful pattern in existing code"
- "Refactored for clarity while keeping behavior"

---

## Open Questions

1. **Inspector calibration** - How do we measure inspector accuracy? Need ground truth from human review.

2. **Iterative inspection** - If inspector finds gaps during WU execution, should worker fix and re-inspect, or escalate?

3. **Challenge reliability** - How often does challenge protocol correctly identify false positives vs incorrectly dismiss real gaps?

4. **Remediation accuracy** - Do generated WUs accurately scope the work? Need feedback loop.

5. **Live mode latency** - Is inspector fast enough for interactive use, or only batch audit?

---

## Status

**Concept:** Documented with two integration points:
1. Five Stage Audit (Stage 5 implementation)
2. PLAN Execution Workflow (taskDoPLAN/taskDoWU integration)

**Implementation:** Not yet built.

**Next Steps:**
1. Prototype Stage 5 inspector on jig-dev audit results
2. Measure: How many of 9 gaps does inspector correctly classify?
3. Measure: Does generated remediation plan match human judgment?
4. If valuable, implement as `jigy audit --with-inspector`
5. Update taskDoPLAN.md and taskDoWU.md with Inspector integration sections
6. Prototype per-WU selective inspection in orchestrated execution

---

## References

- [[C020_CONCEPT_Alignment_Integrity]] - Drift definitions
- [[C021_CONCEPT_Alignment_Triangle_Metrics]] - Triangle metrics
- [[C022_CONCEPT_Stratified_Alignment_Verification]] - Staged verification
- [[C023_PLAN_Five_Stage_Alignment_Audit]] - Audit procedure
- taskDoPLAN.md - Orchestrator workflow
- taskDoWU.md - Worker workflow
