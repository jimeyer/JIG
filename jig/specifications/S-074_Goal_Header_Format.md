---
id: S-074
title: Goal Header Format
type: specification
outcome: O-023
outcomes: [O-023]
architecture: [A-001, A-004]
---

# Goal Header Format

## Constraints

1. **Goals MUST have `### G-{number}:` headers in Charter body**
   - Level 3 markdown header (three #)
   - Goal ID followed by colon
   - Format: `### G-{number}: {Title}`

2. **Goal number is positive integer without zero-padding**
   - Valid: G-1, G-5, G-100
   - Invalid: G-001, G-01, G-0

3. **Goal title MUST follow the colon**
   - At least one character after `: `
   - Title is free-form text

## Examples

Valid:
```markdown
### G-001: Grounding in Reality
### G-002: Continuity Across Sessions
```

Invalid:
```markdown
## G-001: Wrong header level
### G001: Missing hyphen
### G-001 Missing colon
```

## Validation Rules

- `jigy validate` MUST detect goal headers in Charter body
- `jigy validate` MUST fail if header format is invalid
- `jigy validate` MUST extract goal ID from each valid header

## Rationale

Consistent header format enables reliable parsing while remaining human-readable. The level 3 header places goals below the document title and section headers in the markdown hierarchy.

