---
title: "Outcome Audit and Alignment Agent Prompt"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1765657742
created_human: "2025-12-13 14:29 CST"
parent: "[[B019_SCOPE_Coverage-Audit-Record]]"
children: []
---
---
title: Agent Prompt - Outcome Audit and Alignment
version: 1.0
purpose: Instruction set for AI agents to audit and align JIG outcome documents
usage: Provide this entire document as context when asking an agent to audit outcomes
---

# Outcome Audit and Alignment Agent Prompt

You are auditing outcome documents in the JIG system to ensure consistency, completeness, and constitutional alignment.

## Context: What is JIG?

JIG is an architecture and intent alignment system built specifically to enable AI coding agents to work effectively on complex codebases. Read `jig/JIG.md` (the constitution) before starting your audit to understand:

- The 4 core themes (Grounding in Reality, Continuity Across Sessions, Enforcing Constraints, Intent Alignment)
- Why JIG exists (to solve fundamental AI agent limitations)
- The hierarchy: Constitution → Outcomes → Specifications → Tests → Functions

## Your Task

Analyze all files matching `jig/outcomes/O-*.md` and produce an audit report that evaluates structural consistency, completeness, and alignment with the constitution's purpose.

---

## Audit Criteria

For each outcome file, verify the following:

### 1. Structural Completeness ✅

Every outcome must have:

- [ ] **Frontmatter** with all required fields:
  ```yaml
  id: O-XXX
  type: outcome
  theme: [Theme1, Theme2]  # References constitutional themes
  specifies: [S-XXX, ...]   # List of spec IDs this outcome delivers
  ```

- [ ] **Value statement** (bold, one sentence)
  - Format: `**Value:** [pain solved for AI agents and humans]`
  - Must answer: "What pain does this solve?"

- [ ] **Acceptance criterion** (bold, one measurable statement)
  - Format: `**Acceptance:** [one measurable criterion]`
  - Must be quantifiable (times, percentages, counts)

- [ ] **AI Agent Benefit section** (## heading, 2-3 sentences)
  - Explains why this outcome matters specifically for AI agent workflows
  - Includes examples of agent failure modes prevented
  - NOT just developer benefits reframed

- [ ] **Rationale section** (## heading, 3-5 paragraphs)
  - Explains what problem exists without this outcome
  - Explains why current workarounds fail (for agents and humans)
  - Explains how this outcome solves it
  - Describes downstream benefits that emerge

- [ ] **Success Criteria section** (## heading, 3-8 numbered items)
  - Each criterion is measurable and testable
  - Each has quantifiable metrics (times, counts, percentages)
  - Lists what the system/validation/CLI/graph MUST do

- [ ] **Specified By section** (## heading)
  - Lists all specs from frontmatter `specifies` field
  - Includes one-sentence description per spec
  - Format: `- **S-XXX**: [what this spec contributes to outcome]`

- [ ] **Constitution Linkage section** (## heading)
  - Explicitly references which constitutional theme(s) this serves
  - Explains contribution to JIG's purpose
  - Shows what breaks for agents without this outcome

### 2. Constitution Alignment 🎯

- [ ] **Theme linkage**: Frontmatter `theme` field references at least one of:
  - `Grounding in Reality`
  - `Continuity Across Sessions`
  - `Enforcing Constraints`
  - `Intent Alignment`

- [ ] **AI-first framing**: "AI Agent Benefit" section leads with agent perspective, not human perspective

- [ ] **Purpose alignment**: Outcome clearly contributes to enabling AI agents (per constitution's stated purpose)

- [ ] **Bidirectional linkage**: Both constitution → outcome (in JIG.md) and outcome → constitution (in outcome file) exist

### 3. Content Quality 📊

- [ ] **Value statement quality**:
  - One sentence only
  - Answers "what pain does this solve?" not "what does this do?"
  - Mentions both AI agents and humans (or just agents)

- [ ] **Acceptance criterion quality**:
  - One measurable statement
  - Has quantifiable metrics (e.g., "<2s for 10K LOC", "detects all violations with function-level detail")
  - Represents minimum bar for "done"

- [ ] **Rationale quality**:
  - Answers three questions: (1) What breaks without this? (2) Why can't we work around it? (3) What becomes possible?
  - 3-5 paragraphs (not one paragraph, not ten paragraphs)
  - Includes specific examples or scenarios

- [ ] **Success criteria quality**:
  - 3-8 numbered items (not 1-2, not 15)
  - Every item is testable (could write automated validation)
  - Every item has quantifiable metrics
  - No vague terms ("fast" → "<5s", "most" → "80%+")

- [ ] **Specified By quality**:
  - Every spec ID from frontmatter appears in this section
  - Every spec has a one-sentence description (not just ID)
  - Descriptions explain contribution to outcome, not full spec scope

### 4. Consistency Checks ⚖️

- [ ] **Length**: 35-50 lines (comprehensive template range)
  - Too short (<20 lines) = likely missing sections
  - Too long (>60 lines) = may need splitting or editing

- [ ] **Section headers**: Uses exact same headers as template:
  - `# [Outcome Title]` (H1)
  - `## AI Agent Benefit` (H2)
  - `## Rationale` (H2)
  - `## Success Criteria` (H2)
  - `## Specified By` (H2)
  - `## Constitution Linkage` (H2)

- [ ] **Voice and style**:
  - Consistent with peer outcomes
  - Uses active voice ("Agents can query..." not "Queries can be made...")
  - Professional tone (no marketing fluff, no excessive enthusiasm)

- [ ] **No redundancy**: Acceptance criterion and Success Criteria #1 are not identical

---

## Audit Process

Follow these steps in order:

### Step 1: Preparation

1. Read the constitution (`jig/JIG.md`) fully
   - Understand the 4 core themes
   - Understand JIG's purpose for AI agents
   - Note how outcomes are referenced in constitution

2. Read the canonical template (`jig/docs/outcome-template.md` if it exists)
   - If template doesn't exist, infer from best-quality outcomes
   - Document which outcomes exemplify best practices

### Step 2: Individual Outcome Analysis

For each outcome file (O-001.md through O-020.md):

1. **Completeness scoring**: Check all items in "Structural Completeness" criteria
   - Count which sections are present vs missing
   - Classify as: Complete (8/8 sections), Partial (4-7/8 sections), or Stub (<4/8 sections)

2. **Constitution alignment**: Check all items in "Constitution Alignment" criteria
   - Verify theme tags exist and are valid
   - Verify AI agent framing exists and is agent-first
   - Verify bidirectional linkage to constitution

3. **Content quality**: Check all items in "Content Quality" criteria
   - Score each section (Value, Acceptance, Rationale, Success Criteria, etc.)
   - Note specific weaknesses (vague metrics, missing rationale, etc.)

4. **Consistency**: Check all items in "Consistency Checks" criteria
   - Measure line count
   - Verify section header consistency
   - Compare voice/style to peer outcomes

5. **Document findings**:
   - List strengths (what's done well)
   - List weaknesses (what's missing or weak)
   - Recommend concrete actions to improve

### Step 3: Aggregate Metrics

Calculate system-wide metrics:

1. **Completeness distribution**:
   - Count: Complete outcomes, Partial outcomes, Stub outcomes
   - Percentage of total for each category

2. **Component presence**:
   - For each template section, count how many outcomes have it
   - Create table showing: Component | Present | Missing

3. **Length distribution**:
   - Calculate: min, max, mean, median, quartiles
   - Identify outliers (too short or too long)

4. **Theme coverage**:
   - Count outcomes per theme
   - Identify which themes are over/under-represented

5. **Specification coverage**:
   - Count specs referenced per outcome
   - Identify outcomes with many specs but no descriptions

### Step 4: Report Generation

Produce a comprehensive audit report with these sections:

#### 1. Executive Summary
- Audit metadata (date, auditor, scope)
- Key findings (top 3-5 critical issues)
- Overall assessment with status indicators (✅ Good, ⚠️ Moderate, ❌ Poor) for:
  - Structural Integrity
  - Completeness
  - Constitution Alignment
  - AI Agent Readiness

#### 2. Detailed Findings by Outcome
- One subsection per outcome (O-001 through O-020)
- For each: Length, Template type, Completeness status, Strengths, Weaknesses, Recommended actions

#### 3. Metrics Summary
- Tables showing completeness distribution, component presence, length distribution
- Charts/tables showing theme coverage and spec coverage

#### 4. Constitution Alignment Analysis
- Theme coverage table (which outcomes serve which themes)
- Gap analysis (missing AI agent framing, missing linkages)

#### 5. Recommendations
- Priority 1 (Critical - must fix before next release)
- Priority 2 (Important - improves consistency)
- Priority 3 (Enhancement - long-term quality)
- Each with specific actionable items

#### 6. Template Recommendation
- Show the canonical template in full
- Explain why this template is recommended
- Provide examples of outcomes that follow it well

---

## Key Quality Signals

### Good Outcome Indicators ✅

An outcome is high-quality when it:

- **Starts with AI agent benefit**, not developer benefit
  - Good: "Agents can query actual structure instead of hallucinating APIs"
  - Bad: "Developers can understand the codebase faster"

- **Every claim has a number**
  - Good: "Completes in <5s for typical projects"
  - Bad: "Fast validation enables frequent use"

- **Rationale explains failure modes**, not just features
  - Good: "Without this, agents hallucinate function signatures, causing runtime errors"
  - Bad: "This feature provides code structure discovery"

- **Success criteria are testable**
  - Good: "Extract all @jig.implements() decorators with 99%+ accuracy"
  - Bad: "Properly extract decorator information"

- **Links bidirectionally**
  - Constitution references outcome
  - Outcome references constitution
  - Specs reference outcome
  - Outcome references specs with descriptions

### Poor Outcome Indicators ❌

An outcome is low-quality when it:

- **No mention of AI agents** (despite constitution stating this is JIG's core purpose)
- **Vague acceptance criteria** ("improves performance" vs "<5s", "most cases" vs "90%+")
- **Missing rationale** (no explanation of what problem this solves)
- **Spec IDs without descriptions** (lists S-001, S-002, S-003 but doesn't explain what each contributes)
- **No constitution linkage** (can't trace this outcome back to JIG's purpose)
- **Too short** (<20 lines = likely missing critical sections)
- **Redundancy** (Acceptance and Success Criteria #1 are identical)

---

## Specific Patterns to Check

### Pattern 1: Stub Outcomes

**Symptoms:**
- <20 lines total
- No Rationale section
- No Success Criteria section (only Acceptance)
- Spec IDs in frontmatter but no "Specified By" section

**Action:** Flag as Priority 1 (Critical) - these must be completed before release

---

### Pattern 2: Human-Only Framing

**Symptoms:**
- All benefits described from developer perspective
- No "AI Agent Benefit" section
- Language like "Users interact with..." instead of "Agents query..."

**Action:** Flag as Priority 1 (Critical) - violates constitutional purpose

---

### Pattern 3: Missing Quantification

**Symptoms:**
- Acceptance uses words like "fast", "efficient", "most", "many"
- Success criteria have no numbers, times, or percentages
- Claims like "enables frequent use" without defining "frequent"

**Action:** Flag as Priority 2 (Important) - reduces testability

---

### Pattern 4: Orphaned from Constitution

**Symptoms:**
- No `theme` field in frontmatter
- No "Constitution Linkage" section
- Can't determine which of the 4 themes this serves

**Action:** Flag as Priority 1 (Critical) - breaks hierarchy

---

## Output Requirements

### File Location
Save your audit report as: `jig/docs/outcome-audit-YYYY-MM-DD.md`

### Report Structure
Your report must include:

1. ✅ Executive Summary (with overall assessment scores)
2. ✅ Detailed Findings by Outcome (one section per O-XXX file)
3. ✅ Metrics Summary (tables with counts and percentages)
4. ✅ Constitution Alignment Analysis (theme coverage, gaps)
5. ✅ Recommendations (Priority 1/2/3 with specific actions)
6. ✅ Template Recommendation (show canonical template in full)

### Tone and Style

- **Be rigorous**: The outcomes are the foundation of the entire JIG hierarchy
- **Be specific**: Don't say "improve quality", say "add Rationale section explaining failure modes"
- **Be actionable**: Every weakness should have a concrete recommended action
- **Be quantitative**: Count everything, measure everything, table everything

### Critical Directive

**When in doubt, flag it.**

Better to over-report gaps than to miss structural defects. Incomplete or inconsistent outcomes cascade failures down to specifications, tests, and function implementations.

The outcome layer is the load-bearing wall of the JIG system. If it's weak, everything collapses.

---

## Example Finding Entry

Here's an example of a well-structured finding for one outcome:

```markdown
### O-017: Artifact Change Detection

**Length:** 11 lines
**Template:** Stub
**Completeness:** ❌ Incomplete

**Strengths:**
- Clear value statement
- Important capability for drift detection

**Weaknesses:**
- No acceptance criteria beyond title
- No Rationale section (doesn't explain why change detection matters)
- No Success Criteria section (doesn't define what "detects changes" means technically)
- No "Specified By" section (references S-044 through S-050 but provides zero context for 7 specs)
- No AI Agent Benefit section (doesn't explain how agents use change detection)
- No Constitution Linkage section (can't trace to themes)

**Recommended Actions:**
1. **URGENT (P1)**: Add Rationale section explaining drift detection problem
2. **URGENT (P1)**: Add Success Criteria defining "change detection" technically (hash-based? timestamp-based? content diff?)
3. **URGENT (P1)**: Add "Specified By" section with one-sentence description per spec (7 specs total)
4. **URGENT (P1)**: Add AI Agent Benefit explaining how agents use this for session continuity
5. **URGENT (P1)**: Add Constitution Linkage to "Continuity Across Sessions" theme
6. Target length: 35-40 lines (currently 11)
```

---

## Final Checklist

Before submitting your audit report, verify:

- [ ] I read JIG.md (constitution) completely
- [ ] I analyzed all 20 outcome files (O-001 through O-020)
- [ ] I scored each outcome against all 4 criteria categories
- [ ] I generated all required metrics tables
- [ ] I provided specific recommended actions for each weakness
- [ ] I prioritized recommendations (P1/P2/P3)
- [ ] I included the canonical template in full
- [ ] I saved report as `jig/docs/outcome-audit-YYYY-MM-DD.md`
- [ ] My report is actionable (someone can fix issues from my recommendations)

---

## Remember

JIG exists to enable AI agents to work on complex codebases. If the outcomes don't clearly explain how they serve this purpose, the system has failed its constitutional mandate.

Your audit is not just checking boxes—it's verifying that the foundation of the JIG hierarchy is solid enough to support specifications, tests, and implementations that will guide real agent work.

Be thorough. Be critical. Be specific.
