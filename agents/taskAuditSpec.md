# Task: Audit Specification

**Version:** 1.0.0
**Audience:** Sub-agent (Sonnet)
**Purpose:** First-pass compliance audit of a single JIG specification

---

## Overview

You are auditing a JIG specification document for compliance with the format specification (B025). Your goal is a quick, accurate first-pass assessment: does this spec look legit or not?

**Time budget:** ~30 seconds per spec. Be efficient.

---

## Input

You receive:
- Path to a specification file (e.g., `jig/specifications/S-042.md`)
- Reference to format spec: `docs/wip/B025_Outcome-Format-Specification.md`

---

## Compliance Checklist

Check each item. Mark as PASS, FAIL, or WARN.

### Frontmatter (Required)

| Check | Requirement |
|-------|-------------|
| FM-1 | Has YAML frontmatter with `---` delimiters |
| FM-2 | Has `id` field matching filename (e.g., `S-042`) |
| FM-3 | Has `title` field (non-empty string) |
| FM-4 | Has `type: specification` |

### Title Quality

| Check | Requirement |
|-------|-------------|
| TQ-1 | H1 heading matches frontmatter `title` exactly |
| TQ-2 | Title is a noun phrase (not imperative verb) |
| TQ-3 | Title describes observable behavior/capability |
| TQ-4 | Title does not include ID (e.g., NOT "S-042: Something") |

**Title anti-patterns (FAIL):**
- Starts with verb: "Validate...", "Check...", "Make..."
- Too vague: "Authentication", "Validation"
- Includes ID: "S-042: Layer Validation"

**Title good patterns (PASS):**
- "Token Expiration"
- "Layer Constraint Validation"
- "Decorator Link Extraction"

### Content Quality

| Check | Requirement |
|-------|-------------|
| CQ-1 | Has acceptance criteria (explicit or clear behavioral requirements) |
| CQ-2 | Criteria are testable (could write `@jig.verifies` test for them) |
| CQ-3 | No project-speak (avoids "we added", "this sprint", "TODO") |
| CQ-4 | Present tense (describes what IS, not what WILL BE) |
| CQ-5 | Describes behavior, not value (WHAT not WHY) |

### Format

| Check | Requirement |
|-------|-------------|
| FT-1 | Code/commands in backticks |
| FT-2 | No trailing whitespace issues |
| FT-3 | Readable structure (headers, lists) |

---

## Verdict Criteria

### PASS
- All FM checks pass
- All TQ checks pass (or WARN with minor issues)
- At least 3/5 CQ checks pass
- No major format issues

### WARN
- FM checks pass
- 1-2 TQ issues (fixable)
- 2-3 CQ issues
- Generally compliant but needs polish

### FAIL
- Any FM check fails
- Title is imperative verb (TQ-2 fail)
- Title includes ID (TQ-4 fail)
- <3 CQ checks pass
- Contains TODO/WIP/stub content

---

## Output Format

Return a structured report:

```markdown
## Audit: S-XXX

**File:** `jig/specifications/S-XXX.md`
**Verdict:** PASS | WARN | FAIL

### Checklist Results

| Check | Result | Notes |
|-------|--------|-------|
| FM-1 | PASS/FAIL | |
| FM-2 | PASS/FAIL | |
| FM-3 | PASS/FAIL | |
| FM-4 | PASS/FAIL | |
| TQ-1 | PASS/FAIL | |
| TQ-2 | PASS/FAIL | |
| TQ-3 | PASS/FAIL | |
| TQ-4 | PASS/FAIL | |
| CQ-1 | PASS/FAIL/WARN | |
| CQ-2 | PASS/FAIL/WARN | |
| CQ-3 | PASS/FAIL/WARN | |
| CQ-4 | PASS/FAIL/WARN | |
| CQ-5 | PASS/FAIL/WARN | |
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

- **DO NOT** rewrite the spec
- **DO NOT** suggest content changes beyond format compliance
- **DO NOT** spend more than ~30 seconds analyzing
- **DO** be specific about what's wrong
- **DO** give actionable fix suggestions

---

## Example Audit

**Input:** `jig/specifications/S-027.md` containing:

```markdown
---
id: S-027
title: Validate Layer Constraints
type: specification
---

# S-027: Validate Layer Constraints

We need to check that layers don't have upward deps...
```

**Output:**

```markdown
## Audit: S-027

**File:** `jig/specifications/S-027.md`
**Verdict:** FAIL

### Checklist Results

| Check | Result | Notes |
|-------|--------|-------|
| FM-1 | PASS | |
| FM-2 | PASS | |
| FM-3 | PASS | |
| FM-4 | PASS | |
| TQ-1 | FAIL | H1 includes ID prefix |
| TQ-2 | FAIL | "Validate" is imperative verb |
| TQ-3 | WARN | Could describe behavior better |
| TQ-4 | FAIL | H1 includes "S-027:" |
| CQ-1 | FAIL | No acceptance criteria |
| CQ-2 | N/A | |
| CQ-3 | FAIL | "We need to" is project-speak |
| CQ-4 | PASS | |
| CQ-5 | WARN | |
| FT-1 | PASS | |
| FT-2 | PASS | |
| FT-3 | WARN | Minimal structure |

### Issues Found

1. Title uses imperative verb "Validate" - should be noun phrase
2. H1 includes ID prefix "S-027:" - redundant with frontmatter
3. Content uses "We need to" - project-speak, not evergreen
4. No acceptance criteria defined

### Suggested Fixes

1. Change title to "Layer Constraint Validation"
2. Change H1 to match: "# Layer Constraint Validation"
3. Rewrite as "The validator detects..." (present tense, active voice)
4. Add explicit acceptance criteria section
```

---

## Notes

- This is a first-pass audit. Human review follows for WARN/FAIL items.
- Focus on structural compliance, not content quality.
- When in doubt, mark WARN (not FAIL) for subjective issues.
