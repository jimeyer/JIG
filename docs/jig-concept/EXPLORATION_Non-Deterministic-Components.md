---
type: exploration
title: "Non-Deterministic Components in JIG: The Agent Task Problem"
branch: explore-agent-ostc
created: 2025-11-21
status: active
participants: [Jim, Claude]
---

# EXPLORATION: Non-Deterministic Components in JIG

## Problem Statement

**Context:** JIG currently models software as OSTC alignment (Outcomes, Specifications, Tests, Code) where Tests verify Specifications and Code implements Specifications. This model assumes deterministic execution.

**The Gap:** Agent task documents (e.g., `taskCleanBreak-v1.md`) are effectively "code" that gets "executed" by LLM interpreters. But:
- They have no formal tests (evals)
- They produce probabilistic outcomes (non-deterministic)
- They represent an increasingly common pattern in AI-native software

**The Question:** How should JIG handle non-deterministic components while maintaining its core principles of alignment, traceability, and nearly decomposable architecture?

#DISCOVERY "Agent tasks are untested code being shipped"
If we treat task documents as documentation, we're lying to ourselves. They're executable artifacts that change behavior. They need tests.

#DISCOVERY "Non-determinism is not a bug, it's the future"
More software will have LLMs inside. If JIG can't model this, it's a toy for legacy codebases only.

---

## Current State Analysis

### What We Have

```
Agent Task Documents (5 files):
├── taskCleanBreak-v1.md
├── taskDebug-v1.md  
├── taskPlan-v1.md
├── taskTestRepair-v1.md
└── [others]

Properties:
- Human-readable markdown
- Versioned (v1, v2, ...)
- Executed by agents (interpreted as instructions)
- No formal tests
- Stored in docs/tasks/ (outside jig/)
```

### The OSTC Mapping Problem

| OSTC Layer | Traditional Software | Agent Tasks | Status |
|------------|---------------------|-------------|--------|
| **Outcome** | Business value | âœ… Same (agents deliver value) | Clear |
| **Specification** | Technical requirements | âœ… Same (what agent must do) | Clear |
| **Test** | Unit/integration tests | â" Evals? | **Missing** |
| **Code** | Source files | â" Task documents? | **Unclear** |

#LEARNED "The abstraction fits, but execution model differs"
The OSTC layers map conceptually, but verification changes:
- Traditional: Binary pass/fail (deterministic)
- Agent-powered: Success rate distribution (probabilistic)

---

## Solution Space: Five Approaches

### Approach 1: Probabilistic OSTC (Statistical Extension)

**Core Idea:** Extend OSTC to handle probability distributions instead of binary pass/fail.

#### Model Extensions

```yaml
# Traditional Test Node
T-AUTH-001:
  type: test
  file: tests/test_auth.py
  pass_fail: binary  # deterministic

# Probabilistic Test Node  
T-AGENT-CLEAN-001:
  type: test
  file: evals/eval_clean_break.py
  execution_type: probabilistic
  success_rate: 0.87        # historical average
  threshold: 0.85           # required minimum
  sample_size: 20           # eval runs per test
```

#### Validation Changes

```bash
jig validate --check-alignment

# Output for probabilistic tests:
âœ" S-AGENT-CLEAN-001 verified by T-AGENT-CLEAN-001 (87% > 85% threshold)
âš  S-AGENT-REFACTOR-002 verified by T-AGENT-REFACTOR-001 (81% < 85% threshold)
   Suggestion: Improve prompt or lower threshold
```

#### Example: Eval as Test

```python
# evals/eval_clean_break.py
# @jig T-AGENT-CLEAN-001 verifies:S-AGENT-CLEAN-001 subsystem:agent-interface confidence:0.87

def eval_clean_break_no_feature_flags():
    """Verify agent doesn't create feature-flagged code"""
    results = []
    
    for scenario in clean_break_scenarios(n=20):
        result = run_agent_task(
            task="taskCleanBreak-v1.md",
            context=scenario.context
        )
        has_feature_flags = detect_feature_flags(result.code)
        results.append(not has_feature_flags)
    
    success_rate = sum(results) / len(results)
    record_eval_result("T-AGENT-CLEAN-001", success_rate)
    
    assert success_rate >= 0.85, f"Below threshold: {success_rate}"
```

#### Pros/Cons

**Pros:**
- Minimal model extension (add probability, keep OSTC)
- Statistical rigor (track confidence over time)
- Clear thresholds for CI/CD gates

**Cons:**
- Requires eval infrastructure (sampling, measurement)
- Statistical tracking adds complexity
- Need to define "good enough" thresholds per domain

#LEARNED "Probability is a property, not a special case"
This treats non-determinism as a property of execution, not a fundamental difference. Tests still verify specs, just probabilistically.

---

### Approach 2: Dual-Track Subsystems (Deterministic vs Probabilistic)

**Core Idea:** Some subsystems are pure code (deterministic), others are agent-powered (probabilistic). Different validation rules for each track.

#### Configuration

```toml
# jig/config.toml

[subsystems.core]
type = "deterministic"
min_test_coverage = 0.80
validation = "strict"           # Tests must pass 100%

[subsystems.agent-interface]
type = "probabilistic"
min_eval_confidence = 0.85
validation = "statistical"      # Tests must pass >85%
eval_sample_size = 20

[subsystems.extraction]
type = "deterministic"

[subsystems.synthesis]
type = "probabilistic"
```

#### Coupling Constraints

```toml
[decomposability]
# Deterministic subsystems depend on deterministic only
# Probabilistic can depend on both
# Prevents non-determinism from leaking

[subsystems.core]
type = "deterministic"
allowed_dependencies = ["extraction", "validation"]

[subsystems.synthesis]
type = "probabilistic"
allowed_dependencies = ["core", "extraction", "agent-interface"]
```

#### Subsystem Boundaries

```
Deterministic World          Probabilistic World
┌───────────────┐           ┌──────────────────┐
│ core          │           │ agent-interface  │
│ extraction    │◄──────────│ synthesis        │
│ validation    │           │                  │
└───────────────┘           └──────────────────┘
     strict                      statistical
     100% pass                   >85% success
```

#### Pros/Cons

**Pros:**
- Clean separation of concerns
- Prevents probabilistic contamination
- Different teams can use different validation strategies

**Cons:**
- Two validation systems to maintain
- Boundary decisions may be contentious
- Cross-boundary dependencies need careful design

#DECISION "Architectural boundaries should match execution model boundaries"
If you're mixing deterministic and probabilistic, make the boundary explicit. Don't pretend they're the same thing.

---

### Approach 3: Prompt Versioning + Eval Co-Evolution

**Core Idea:** Treat prompt documents exactly like source code. Version them, test them, track their evolution.

#### Directory Structure

```
jig/
├── specifications/
│   └── S-AGENT-CLEAN-001.md
├── prompts/                    # NEW: prompts are code
│   ├── taskCleanBreak-v1.md   # @jig C-AGENT-CLEAN-001
│   ├── taskCleanBreak-v2.md   # @jig C-AGENT-CLEAN-002
│   └── taskDebug-v1.md        # @jig C-AGENT-DEBUG-001
├── evals/                      # NEW: evals are tests
│   ├── eval_clean_break.py    # @jig T-AGENT-CLEAN-001
│   └── eval_debug.py          # @jig T-AGENT-DEBUG-001
└── deltas/
    └── active/
        └── improve-clean-break/
            ├── PLAN.md
            └── RETRO.md
```

#### Prompt as Code

```markdown
<!-- jig/prompts/taskCleanBreak-v1.md -->
<!-- @jig C-AGENT-CLEAN-001 implements:S-AGENT-CLEAN-001 subsystem:agent-interface version:1 -->

# taskCleanBreak: Clean Break Protocol

**Purpose:** Execute clean breaks from old implementations...

[... rest of task document ...]

<!-- Metadata for tracking -->
<!-- eval_suite: evals/eval_clean_break.py -->
<!-- success_rate: 0.87 (last 20 runs) -->
<!-- last_tested: 2025-11-21 -->
```

#### Development Workflow

```bash
# Making changes to a prompt (like refactoring code)
git checkout -b improve-clean-break
mkdir jig/deltas/active/improve-clean-break

# Edit prompt
cp jig/prompts/taskCleanBreak-v1.md jig/prompts/taskCleanBreak-v2.md
vim jig/prompts/taskCleanBreak-v2.md

# Run evals (like running tests)
jig eval --prompt jig/prompts/taskCleanBreak-v2.md --baseline v1

# Output:
Baseline (v1):     87% success (20 samples)
Candidate (v2):    92% success (20 samples)
Improvement:       +5% ✓
Statistical sig:   p < 0.05 ✓

# Commit with discovery markers
git add jig/prompts/taskCleanBreak-v2.md
git commit -m "improve(agent): add anti-pattern examples

#LEARNED \"Explicit negative examples improve compliance\"
Success rate improved from 87% to 92% by adding ❌/✅ comparisons.

Closes: O-AGENT-RELIABILITY-001"
```

#### Version Lineage Tracking

```yaml
# jig/graph-index.yaml

nodes:
  C-AGENT-CLEAN-001:
    type: code
    file: jig/prompts/taskCleanBreak-v1.md
    language: markdown-prompt
    version: 1
    success_rate: 0.87
    
  C-AGENT-CLEAN-002:
    type: code
    file: jig/prompts/taskCleanBreak-v2.md
    language: markdown-prompt
    version: 2
    success_rate: 0.92
    supersedes: C-AGENT-CLEAN-001   # version lineage

  T-AGENT-CLEAN-001:
    type: test
    file: evals/eval_clean_break.py
    tests_versions: [1, 2]          # which versions this eval covers
```

#### Pros/Cons

**Pros:**
- Conceptually simple (prompts = code)
- Standard versioning workflow
- Clear evolution tracking
- No special handling needed

**Cons:**
- Doesn't explicitly model non-determinism
- Version explosion possible (v1, v2, v3...)
- Eval suite must handle multiple versions

#LEARNED "Explicit versioning beats implicit evolution"
Seeing v1 → v2 → v3 with success rates tells a story. Git history alone obscures this.

---

### Approach 4: Agent Interface Layer (Fifth Node Type)

**Core Idea:** Add new node type `I` (Interface) that sits between deterministic and probabilistic subsystems. Contract-based boundary.

#### Extended Model: OSTCI

```
Deterministic World:
O → S → T + C

Agent World:
O → S → I → T + C
         ↑
    (contract layer)
```

#### Interface Node Example

```yaml
# jig/interfaces/I-AGENT-CLEAN-001.md
---
id: I-AGENT-CLEAN-001
type: interface
title: "Clean break execution contract"
subsystem: agent-interface
---

# Interface: Agent Clean Break Contract

**Input Schema:**
```json
{
  "task": "clean-break",
  "context": {
    "old_implementation": "path/to/old/",
    "new_implementation": "path/to/new/",
    "subsystem": "auth"
  }
}
```

**Output Schema:**
```json
{
  "changes": [...],
  "validation": {
    "has_feature_flags": false,
    "updated_graph_index": true,
    "added_error_handling": true
  }
}
```

**Contract Guarantees:**
- No feature flags in output
- Graph index updated if @jig annotations deleted
- Error handling for unimplemented features

## Related
- implements: S-AGENT-CLEAN-001
- implemented_by: C-AGENT-CLEAN-001, C-AGENT-CLEAN-002
- verified_by: T-AGENT-CLEAN-001
```

#### Graph Relationships

```yaml
edges:
  # Spec layer
  - from: I-AGENT-CLEAN-001
    to: S-AGENT-CLEAN-001
    type: implements

  # Multiple implementations of same interface
  - from: C-AGENT-CLEAN-001  # v1 prompt
    to: I-AGENT-CLEAN-001
    type: implements
    
  - from: C-AGENT-CLEAN-002  # v2 prompt
    to: I-AGENT-CLEAN-001
    type: implements

  # Eval verifies interface contract, not implementation
  - from: T-AGENT-CLEAN-001
    to: I-AGENT-CLEAN-001
    type: verifies
```

#### Why Interface Layer?

**Isolation:** Deterministic subsystems depend on `I`, not `C`
- Core doesn't care which prompt version
- Core only cares about contract compliance
- Prompts can evolve independently

**Substitution:** Multiple implementations can satisfy same interface
- v1 prompt: 87% success
- v2 prompt: 92% success
- Both implement same I-AGENT-CLEAN-001 contract

#### Pros/Cons

**Pros:**
- Clean architectural boundary
- Enables A/B testing (multiple C for same I)
- Deterministic code insulated from probabilistic
- Contract-first design

**Cons:**
- New node type (OSTCI is more complex than OSTC)
- More overhead (write Interface + Code)
- May be overkill for simple cases

#DISCOVERY "Interface layer enables experimentation"
With I as contract, we can try multiple prompt implementations without changing dependent code. Like dependency injection for agents.

---

### Approach 5: Bootstrap JIG-on-JIG (Meta-Dogfooding)

**Core Idea:** Use JIG to track JIG's own agent interface as the reference implementation. Eat our own dog food.

#### Full OSTC for Agent Tasks

```
jig/
├── outcomes/
│   └── O-AGENT-001.md            # "Agents execute tasks reliably"
├── specifications/
│   ├── S-AGENT-CLEAN-001.md      # "Clean break protocol spec"
│   └── S-AGENT-DEBUG-001.md      # "Debug workflow spec"
├── prompts/                       # Code layer
│   ├── taskCleanBreak-v1.md      # @jig C-AGENT-CLEAN-001
│   ├── taskDebug-v1.md           # @jig C-AGENT-DEBUG-001
│   └── taskPlan-v1.md            # @jig C-AGENT-PLAN-001
├── evals/                         # Test layer
│   ├── eval_clean_break.py       # @jig T-AGENT-CLEAN-001
│   ├── eval_debug.py             # @jig T-AGENT-DEBUG-001
│   └── eval_plan.py              # @jig T-AGENT-PLAN-001
└── deltas/
    └── active/
        └── improve-agent-reliability/
            ├── PLAN.md
            └── RETRO.md
```

#### Configuration

```toml
# jig/config.toml

[subsystems.agent-interface]
type = "probabilistic"
min_eval_confidence = 0.85
eval_sample_size = 20

[subsystems.agent-interface.prompts]
location = "jig/prompts/"
annotation_pattern = "@jig C-AGENT-"

[subsystems.agent-interface.evals]
location = "evals/"
annotation_pattern = "@jig T-AGENT-"
```

#### Validation Example

```bash
jig validate --subsystem agent-interface

# Output:
âœ" O-AGENT-001 has specifications: S-AGENT-CLEAN-001, S-AGENT-DEBUG-001, S-AGENT-PLAN-001
âœ" S-AGENT-CLEAN-001 has prompts: C-AGENT-CLEAN-001
âœ" S-AGENT-CLEAN-001 has evals: T-AGENT-CLEAN-001 (87% > 85%)
âœ" S-AGENT-DEBUG-001 has prompts: C-AGENT-DEBUG-001
âš  S-AGENT-DEBUG-001 has no evals (test coverage gap!)
âœ" S-AGENT-PLAN-001 has prompts: C-AGENT-PLAN-001
âš  S-AGENT-PLAN-001 has no evals (test coverage gap!)

Coverage: 33% (1/3 specs have evals)
Target: 80%
Action: Write evals for debug and plan tasks
```

#### Harvest Example

```markdown
# jig/deltas/active/improve-agent-reliability/RETRO.md

## What We Built

Added explicit anti-pattern examples to taskCleanBreak.

#LEARNED "Negative examples matter more than positive ones"
v1 (positive examples only): 87% success
v2 (positive + negative): 92% success
Agents need to see what NOT to do.

## Evals as Tests

Created eval_clean_break.py with 20 test scenarios.

#DISCOVERY "Evals reveal edge cases prompts miss"
Scenario 12 (circular dependency): 45% success
Prompt v1 had no guidance on circular refs
Added section → 88% success on scenario 12

## Harvest Targets

- O-AGENT-001: Updated success metric (87% → 92%)
- S-AGENT-CLEAN-001: Add circular dependency guidance
- C-AGENT-CLEAN-002: New version with anti-patterns
- T-AGENT-CLEAN-001: Extended to cover circular deps
```

#### Dogfooding Benefits

1. **Validation of model:** If JIG can't track its own agent tasks, model is wrong
2. **Reference implementation:** Other projects can copy pattern
3. **Forces rigor:** Can't ship without evals (we'd fail our own standards)
4. **Documentation by example:** JIG's agent-interface subsystem IS the guide

#### Pros/Cons

**Pros:**
- Validates the model (if it works for us, it works)
- Creates reference implementation
- Forces us to build eval infrastructure
- Demonstrates pattern for others

**Cons:**
- Requires commitment to evals (can't skip tests)
- Meta-complexity (using tool to track tool)
- Needs time to build properly

#DECISION "Bootstrap approach has highest leverage"
If we do this right, JIG becomes the example for AI-native development. We're not just building a tool—we're demonstrating a pattern.

---

## Comparison Matrix

| Dimension | Approach 1:<br>Probabilistic | Approach 2:<br>Dual-Track | Approach 3:<br>Versioning | Approach 4:<br>Interface | Approach 5:<br>Bootstrap |
|-----------|------------|-----------|------------|-------------|------------|
| **Model Complexity** | Medium | Medium | Low | High | Medium |
| **Implementation Effort** | Medium | High | Low | High | Medium |
| **Eval Infrastructure** | Required | Required | Required | Required | Required |
| **Conceptual Clarity** | Good | Excellent | Good | Good | Excellent |
| **Scalability** | High | High | Medium | High | High |
| **Traceability** | Excellent | Good | Excellent | Excellent | Excellent |
| **Backwards Compat** | High | High | High | Low | High |
| **Dogfooding** | No | No | No | No | Yes |

**Key Insights:**

- All approaches require eval infrastructure (no way around it)
- Approaches 1, 3, 5 are compatible (can combine)
- Approach 4 is most invasive (new node type)
- Approach 5 has highest learning value (forces us to use what we build)

---

## Open Questions

### Q1: What makes a good eval?

**Dimensions:**
- Coverage (how many scenarios?)
- Realism (synthetic vs real-world contexts?)
- Speed (can we run 20 samples in <5 minutes?)
- Stability (do results vary run-to-run?)

**Need to explore:**
- Eval scenario design patterns
- Minimum sample size for statistical confidence
- How to detect eval drift (eval gets stale as models improve)

### Q2: Where do evals live in the codebase?

**Options:**
1. `evals/` at repo root (separate from tests/)
2. `tests/evals/` (group with unit tests)
3. `jig/evals/` (colocate with JIG artifacts)

**Tradeoffs:**
- Separation: Clear boundary, but another top-level directory
- Tests: Familiar location, but conflates deterministic/probabilistic
- JIG: Keeps JIG artifacts together, but may feel "meta"

#LEARNED "Evals are not unit tests"
Unit tests check deterministic code. Evals measure probabilistic behavior. Different mental model, should have different location?

### Q3: How to handle eval cost?

**Problem:** LLM calls cost money. Running 20 scenarios × 5 tasks = 100 calls.

**Strategies:**
- Cache results (trade storage for API costs)
- Sample intelligently (not every commit needs full suite)
- CI budget (X calls per PR, full suite on main)
- Synthetic evaluation (cheaper than real LLM calls?)

### Q4: Version explosion problem?

**Concern:** If every prompt change creates new version (v1, v2, v3...), do we get clutter?

**Mitigation options:**
- Only version on success rate improvements >5%
- Prune old versions after N releases
- Keep only baseline + current
- Accept the clutter (git log is also "cluttered" with history)

### Q5: Probabilistic subsystem boundaries?

**Question:** Which JIG subsystems should be probabilistic?

**Current guess:**
- `synthesis`: LLM-powered (probabilistic)
- `agent-interface`: LLM-powered (probabilistic)
- `extraction`: ripgrep-based (deterministic)
- `validation`: rule-based (deterministic)
- `core`: pure logic (deterministic)

**Need to validate:** Does this boundary make sense architecturally?

---

## Preliminary Recommendation

**Combine Approaches 1, 3, and 5:**

### Phase 1: Add Eval Infrastructure (Weeks 1-2)
- Create `evals/` directory
- Write 3 initial evals (clean-break, debug, plan)
- Establish baseline success rates
- Document eval pattern

### Phase 2: Track Prompts as Code (Week 3)
- Move task docs to `jig/prompts/`
- Add `@jig C-AGENT-*` annotations
- Link prompts ↔ evals in graph-index
- Version prompts (v1, v2, ...)

### Phase 3: Extend Validation (Week 4)
- Modify `jig validate` to handle probabilistic tests
- Add success rate tracking over time
- Warn on degradation below threshold
- CI/CD integration

### Phase 4: Document Pattern (Week 5)
- Write guide: "Using JIG with Non-Deterministic Components"
- JIG's agent-interface subsystem is reference implementation
- Extract lessons learned
- Ship it

**Why this combination?**
- Minimal model changes (add probability property)
- Leverages existing OSTC structure
- Dogfooding validates design
- Creates reusable pattern for others

---

## Success Criteria

**We'll know this works when:**

1. **Coverage:** All agent tasks have evals (100%)
2. **Validation:** `jig validate --subsystem agent-interface` passes in CI
3. **Visibility:** Success rates tracked over time
4. **Improvement:** Can A/B test prompt changes with confidence
5. **Documentation:** Other projects can replicate pattern
6. **Dogfooding:** JIG uses JIG to track its agent interface

**We'll know this failed when:**
- Evals are too slow to run regularly
- Success rates are too noisy to be useful
- Model feels forced/unnatural
- Overhead exceeds value

---

## Next Steps

1. **Decide:** Which approach(es) to pursue
2. **Spike:** Build one eval end-to-end (clean-break)
3. **Measure:** Run 20 samples, measure time/cost/stability
4. **Document:** Write eval creation guide
5. **Iterate:** Add 2 more evals, refine pattern
6. **Ship:** Integrate into jig validate

**Time estimate:** 4-5 weeks to fully implement and document

**Effort:** ~20-30 hours of focused work

**Risk:** Medium (unproven pattern, but clear path forward)

---

## References

**External:**
- OpenAI Evals: https://github.com/openai/evals
- Anthropic Constitutional AI: https://www.anthropic.com/index/constitutional-ai-harmlessness-from-ai-feedback
- LangChain Evaluation: https://python.langchain.com/docs/guides/evaluation

**Internal (JIG):**
- JIG Concept v6.1: Core OSTC model
- taskCleanBreak-v1.md: Example prompt artifact
- Nearly Decomposable Systems: Herbert Simon (theoretical foundation)

---

**Status:** Open for discussion
**Next Review:** After spike (eval prototype complete)
**Owner:** Jim