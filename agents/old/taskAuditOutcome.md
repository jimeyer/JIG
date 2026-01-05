# Task: Audit Outcome

**Version:** 1.0.0
**Audience:** Sub-agent (Sonnet)
**Purpose:** First-pass compliance audit of a single JIG outcome

---

## Overview

You are auditing a JIG outcome document for compliance with the format specification (B025). Your goal is a quick, accurate first-pass assessment: does this outcome look legit or not?

**Time budget:** ~45 seconds per outcome. Be efficient.

---

## Input

You receive:
- Path to an outcome file (e.g., `jig/outcomes/O-012.md`)
- Reference to format spec: `docs/wip/B025_Outcome-Format-Specification.md`

---

## Compliance Checklist

Check each item. Mark as PASS, FAIL, or WARN.

### Frontmatter (Required)

| Check | Requirement |
|-------|-------------|
| FM-1 | Has YAML frontmatter with `---` delimiters |
| FM-2 | Has `id` field matching filename (e.g., `O-012`) |
| FM-3 | Has `title` field (non-empty string) |
| FM-4 | Has `type: outcome` |
| FM-5 | Has `specifies` array (list of S-XXX IDs) |

### Title Quality

| Check | Requirement |
|-------|-------------|
| TQ-1 | H1 heading matches frontmatter `title` exactly |
| TQ-2 | Title is a noun phrase (not imperative verb) |
| TQ-3 | Title describes delivered VALUE (not behavior or activity) |
| TQ-4 | Title does not include ID (e.g., NOT "O-012: Something") |

**Title anti-patterns (FAIL):**
- Starts with verb: "Discover...", "Implement...", "Add..."
- Describes work: "Make graphs work faster"
- Includes ID: "O-012: Layer Architecture"
- Too technical: "AST Parser Implementation"

**Title good patterns (PASS):**
- "Implementation Structure Discovery"
- "Automated Code-to-Specification Traceability"
- "Layer Architecture Enforcement"
- "Fast Project Validation"

### Required Sections

| Check | Requirement |
|-------|-------------|
| RS-1 | Has **Value:** statement after H1 |
| RS-2 | Has **Acceptance:** statement after Value |
| RS-3 | Has "## Why This Matters" section |
| RS-4 | Has "## Rationale" section |
| RS-5 | Has "## Success Criteria" section |
| RS-6 | Has "## Specified By" section |
| RS-7 | Has "## Constitution Linkage" section |

### Section Quality

| Check | Requirement |
|-------|-------------|
| SQ-1 | Value statement is one sentence (who can do what without pain) |
| SQ-2 | Acceptance has measurable criterion (number, time, percentage) |
| SQ-3 | "Why This Matters" leads with agent perspective |
| SQ-4 | "Why This Matters" has 2-3 paragraphs |
| SQ-5 | Rationale has 3-5 paragraphs with problem→solution arc |
| SQ-6 | Success Criteria has 3-8 numbered, measurable items |
| SQ-7 | Success Criteria items start with action verbs |
| SQ-8 | "Specified By" has descriptions (not just IDs) |
| SQ-9 | Constitution Linkage has Serves/Enables/Without structure |

### Content Quality

| Check | Requirement |
|-------|-------------|
| CQ-1 | Evergreen content (no project-speak: "we added", "this sprint") |
| CQ-2 | Present tense (describes what IS, not WILL BE or WAS) |
| CQ-3 | Active voice (names the actor) |
| CQ-4 | Agent-first framing (agent benefit explicit, not implied) |
| CQ-5 | Concrete over abstract (specific commands, real metrics) |
| CQ-6 | No TODO/WIP/stub content |

### Format

| Check | Requirement |
|-------|-------------|
| FT-1 | Code/commands in backticks |
| FT-2 | Specs/Outcomes in bold (e.g., **S-001**) |
| FT-3 | Readable structure (proper section hierarchy) |

---

## Verdict Criteria

### PASS
- All FM checks pass
- All TQ checks pass (or WARN with minor issues)
- All RS checks pass
- At least 6/9 SQ checks pass
- At least 4/6 CQ checks pass
- No major format issues

### WARN
- FM checks pass
- 1-2 TQ issues (fixable)
- 1-2 RS sections missing or minimal
- 4-5 SQ checks pass
- 3-4 CQ checks pass
- Generally compliant but needs polish

### FAIL
- Any FM check fails (especially FM-5: specifies)
- Title is imperative verb (TQ-2 fail)
- Title includes ID (TQ-4 fail)
- 3+ RS sections missing
- <4 SQ checks pass
- Contains TODO/WIP/stub content

---

## Output Format

Return a structured report:

```markdown
## Audit: O-XXX

**File:** `jig/outcomes/O-XXX.md`
**Verdict:** PASS | WARN | FAIL

### Checklist Results

| Check | Result | Notes |
|-------|--------|-------|
| FM-1 | PASS/FAIL | |
| FM-2 | PASS/FAIL | |
| FM-3 | PASS/FAIL | |
| FM-4 | PASS/FAIL | |
| FM-5 | PASS/FAIL | |
| TQ-1 | PASS/FAIL | |
| TQ-2 | PASS/FAIL | |
| TQ-3 | PASS/FAIL | |
| TQ-4 | PASS/FAIL | |
| RS-1 | PASS/FAIL | |
| RS-2 | PASS/FAIL | |
| RS-3 | PASS/FAIL | |
| RS-4 | PASS/FAIL | |
| RS-5 | PASS/FAIL | |
| RS-6 | PASS/FAIL | |
| RS-7 | PASS/FAIL | |
| SQ-1 | PASS/FAIL/WARN | |
| SQ-2 | PASS/FAIL/WARN | |
| SQ-3 | PASS/FAIL/WARN | |
| SQ-4 | PASS/FAIL/WARN | |
| SQ-5 | PASS/FAIL/WARN | |
| SQ-6 | PASS/FAIL/WARN | |
| SQ-7 | PASS/FAIL/WARN | |
| SQ-8 | PASS/FAIL/WARN | |
| SQ-9 | PASS/FAIL/WARN | |
| CQ-1 | PASS/FAIL/WARN | |
| CQ-2 | PASS/FAIL/WARN | |
| CQ-3 | PASS/FAIL/WARN | |
| CQ-4 | PASS/FAIL/WARN | |
| CQ-5 | PASS/FAIL/WARN | |
| CQ-6 | PASS/FAIL | |
| FT-1 | PASS/FAIL | |
| FT-2 | PASS/FAIL | |
| FT-3 | PASS/FAIL | |

### Issues Found

1. [Issue description - what's wrong and why]
2. [Issue description]

### Suggested Fixes

1. [Specific fix for issue 1]
2. [Specific fix for issue 2]
```

---

## Constraints

- **DO NOT** rewrite the outcome
- **DO NOT** suggest content changes beyond format compliance
- **DO NOT** spend more than ~45 seconds analyzing
- **DO** be specific about what's wrong
- **DO** give actionable fix suggestions

---

## Example Audit

**Input:** `jig/outcomes/O-013.md` containing:

```markdown
---
id: O-013
title: Add Layer Validation
type: outcome
---

# O-013: Add Layer Validation

We're adding layer validation to prevent bad dependencies.

## What It Does

Checks layers.
```

**Output:**

```markdown
## Audit: O-013

**File:** `jig/outcomes/O-013.md`
**Verdict:** FAIL

### Checklist Results

| Check | Result | Notes |
|-------|--------|-------|
| FM-1 | PASS | |
| FM-2 | PASS | |
| FM-3 | PASS | |
| FM-4 | PASS | |
| FM-5 | FAIL | Missing specifies array |
| TQ-1 | FAIL | H1 includes ID prefix |
| TQ-2 | FAIL | "Add" is imperative verb |
| TQ-3 | WARN | Describes activity, not value |
| TQ-4 | FAIL | H1 includes "O-013:" |
| RS-1 | FAIL | No Value statement |
| RS-2 | FAIL | No Acceptance statement |
| RS-3 | FAIL | No "Why This Matters" section |
| RS-4 | FAIL | No "Rationale" section |
| RS-5 | FAIL | No "Success Criteria" section |
| RS-6 | FAIL | No "Specified By" section |
| RS-7 | FAIL | No "Constitution Linkage" section |
| SQ-* | N/A | Sections missing |
| CQ-1 | FAIL | "We're adding" is project-speak |
| CQ-2 | FAIL | Future tense |
| CQ-3 | WARN | |
| CQ-4 | FAIL | No agent perspective |
| CQ-5 | FAIL | "Checks layers" is abstract |
| CQ-6 | PASS | No TODO markers |
| FT-1 | PASS | |
| FT-2 | N/A | |
| FT-3 | FAIL | Missing required structure |

### Issues Found

1. Missing `specifies` array in frontmatter
2. Title uses imperative verb "Add" - should be noun phrase describing value
3. H1 includes ID prefix "O-013:" - redundant with frontmatter
4. Missing all required sections (Value, Acceptance, Why This Matters, etc.)
5. Content uses project-speak ("We're adding")
6. No agent-first perspective

### Suggested Fixes

1. Add `specifies: [S-027, S-028]` to frontmatter (list actual specs)
2. Change title to "Layer Architecture Enforcement"
3. Change H1 to match: "# Layer Architecture Enforcement"
4. Add all required sections per B025 format spec
5. Rewrite content in present tense, evergreen style
6. Lead "Why This Matters" with agent perspective
```

---

## Notes

- Outcomes have more required structure than specifications
- This is a first-pass audit. Human review follows for WARN/FAIL items.
- Focus on structural compliance and section presence first
- When in doubt on subjective quality (SQ checks), mark WARN
