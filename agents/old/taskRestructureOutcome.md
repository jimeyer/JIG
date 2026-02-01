# Task: Restructure Outcome to B025 Format

**Version:** 1.0.0
**Audience:** Sub-agent (Sonnet)
**Purpose:** Restructure a single JIG outcome from legacy format to B025 compliance

---

## Overview

You are restructuring a JIG outcome document to comply with the B025 format specification. Your job is to:
1. Read the existing outcome
2. Extract and preserve all existing content
3. Reorganize into B025 structure
4. Write the restructured file back

**Critical:** Do NOT lose or discard existing content. Restructure and rephrase, but preserve intent.

---

## Input

You receive:
- Path to an outcome file (e.g., `jig/outcomes/O-012.md`)

---

## B025 Target Format

The restructured outcome MUST have this structure:

```markdown
---
id: O-XXX
title: [Noun Phrase Describing Value]
type: outcome
specifies: [S-001, S-002, ...]
---

# [Same as title - NO ID prefix]

**Value:** [One sentence: WHO can do WHAT without PAIN]

**Acceptance:** [One sentence with measurable criterion]

## Why This Matters

[2-3 paragraphs from agent perspective]
[First paragraph: What capability this enables]
[Second paragraph: What problems it solves]
[Third paragraph (optional): Broader impact]

## Rationale

[3-5 paragraphs with problem→solution arc]
[Explain the "why" behind this outcome]
[What alternatives were considered]
[Why this approach was chosen]

## Success Criteria

1. [Action verb] [measurable outcome]
2. [Action verb] [measurable outcome]
3. [Action verb] [measurable outcome]
...
(3-8 numbered items, each starting with action verb)

## Specified By

- **S-XXX** - [Brief description of what this spec covers]
- **S-YYY** - [Brief description of what this spec covers]

## Constitution Linkage

**Serves:** [Which constitution principle this serves]
**Enables:** [What capability this enables for agents]
**Without this:** [What would be missing/broken]
```

---

## Restructuring Process

### Step 1: Read and Extract

Read the existing outcome and identify:
- Current title (may have ID prefix - remove it)
- Value proposition / what it delivers
- Business impact / why it matters
- Acceptance criteria (may be checkboxes)
- Related specifications
- Any rationale or context

### Step 2: Map Legacy → B025

| Legacy Section | B025 Section |
|----------------|--------------|
| Value Proposition | **Value:** statement |
| Business Impact | ## Why This Matters |
| Acceptance Criteria (checkboxes) | ## Success Criteria (numbered, action verbs) |
| Related Specifications | ## Specified By (with descriptions) |
| (often missing) | ## Rationale |
| (often missing) | ## Constitution Linkage |
| (often missing) | **Acceptance:** statement |

### Step 3: Generate Missing Sections

If sections are missing, generate them based on context:

**Acceptance:** (if missing)
- Create a single measurable criterion from the acceptance criteria
- Example: "Validation completes in under 500ms for projects with 10,000 files"

**Rationale:** (if missing)
- Explain WHY this outcome matters
- What problem does it solve?
- What alternatives exist and why weren't they chosen?

**Constitution Linkage:** (if missing)
- **Serves:** Infer from content (e.g., "Developer productivity", "Code quality", "System reliability")
- **Enables:** What agents can do because of this
- **Without this:** What would break or be missing

### Step 4: Transform Content

**Title:**
- Remove any ID prefix ("O-012: Something" → "Something")
- Ensure it's a noun phrase describing VALUE delivered
- NOT an imperative verb ("Add...", "Implement...")

**Value statement:**
- One sentence
- Pattern: "[WHO] can [DO WHAT] without [PAIN/FRICTION]"
- Example: "Developers can validate their entire project in seconds without waiting for slow checks"

**Acceptance statement:**
- One sentence with a measurable criterion
- Include a number, time, or percentage
- Example: "Project validation completes in under 2 seconds for codebases up to 50,000 lines"

**Success Criteria:**
- Convert checkboxes to numbered list
- Each item starts with action verb (Verify, Confirm, Demonstrate, Validate, etc.)
- Each item is measurable/observable
- Remove checkbox syntax `[ ]` or `- [ ]`

**Why This Matters:**
- Write from agent perspective
- Lead with what capability this enables
- 2-3 paragraphs
- Evergreen language (no project-speak)

**Specified By:**
- List each specification with a brief description
- Format: `**S-XXX** - [what it specifies]`
- If descriptions unknown, use the spec title

---

## Example Transformation

### Before (Legacy)

```markdown
---
id: O-012
title: O-012: Fast Validation
type: outcome
---

# O-012: Fast Validation

## Value Proposition

Fast validation helps developers iterate quickly.

## Business Impact

Without fast validation, developers waste time waiting.

## Acceptance Criteria

- [ ] Validation runs in under 5 seconds
- [ ] Works on large projects
- [ ] No false positives

## Related Specifications

S-027, S-028
```

### After (B025)

```markdown
---
id: O-012
title: Fast Project Validation
type: outcome
specifies: [S-027, S-028]
---

# Fast Project Validation

**Value:** Developers can validate their entire project in seconds without waiting for slow, blocking checks.

**Acceptance:** Full project validation completes in under 5 seconds for codebases with up to 50,000 lines of code.

## Why This Matters

Fast validation transforms the development workflow. When validation is instant, developers run it constantly—after every change, before every commit. This catches issues immediately while context is fresh, rather than discovering problems hours later in CI.

Slow validation creates friction that discourages use. Developers skip checks, batch up changes, and lose the tight feedback loop that makes validation valuable. Speed isn't just convenience; it's the difference between a tool that gets used and one that gets bypassed.

## Rationale

Validation speed depends on algorithmic efficiency and caching strategy. A naive implementation that re-validates everything on each run would be too slow for interactive use. Instead, the system tracks file modification times and only re-validates changed files and their dependents.

The 5-second target was chosen based on user research showing that delays beyond this threshold cause developers to context-switch away from the validation task. Sub-second validation for incremental changes keeps developers in flow state.

Alternative approaches considered included background validation (rejected due to complexity) and sampling-based validation (rejected due to potential missed issues).

## Success Criteria

1. Validate a 50,000-line project in under 5 seconds on first run
2. Validate incremental changes in under 500ms
3. Report zero false positives in validation results
4. Scale linearly with project size (not exponentially)
5. Provide progress feedback for long-running validations

## Specified By

- **S-027** - Incremental validation algorithm and caching
- **S-028** - Validation performance benchmarks and targets

## Constitution Linkage

**Serves:** Developer productivity and iteration speed
**Enables:** Agents to validate changes instantly before committing, catching issues early
**Without this:** Developers would skip validation due to slowness, leading to broken code reaching production
```

---

## Output

After restructuring, write the file back to the same path.

Return a brief summary:

```markdown
## Restructured: O-XXX

**Title:** [new title]
**Changes:**
- Removed ID from H1
- Converted 3 checkbox criteria to numbered Success Criteria
- Added Rationale section (was missing)
- Added Constitution Linkage section (was missing)
- Rewrote Value Proposition as Value statement

**Preserved:** All original acceptance criteria, spec references
```

---

## Constraints

### DO
- Preserve all existing content intent
- Generate missing sections based on context
- Use present tense, evergreen language
- Make Success Criteria measurable with action verbs
- Include Constitution Linkage (often missing)

### DO NOT
- Lose or discard existing content
- Use project-speak ("we added", "this sprint")
- Use future tense ("will be", "going to")
- Leave checkbox syntax in Success Criteria
- Skip the Constitution Linkage section

---

## Quality Checks Before Writing

Before writing the file, verify:
- [ ] Title is noun phrase (no ID, no imperative verb)
- [ ] H1 matches title exactly
- [ ] Value statement is one sentence with who/what/without pattern
- [ ] Acceptance statement has measurable criterion
- [ ] Why This Matters has 2-3 paragraphs
- [ ] Rationale has 3-5 paragraphs
- [ ] Success Criteria has 3-8 numbered items with action verbs
- [ ] Specified By has descriptions for each spec
- [ ] Constitution Linkage has Serves/Enables/Without structure
- [ ] No checkbox syntax remains
- [ ] No project-speak or temporal references
