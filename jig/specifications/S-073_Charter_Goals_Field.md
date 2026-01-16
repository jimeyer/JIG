---
id: S-073
title: Charter Goals Field
type: specification
outcomes: [O-023]
architecture: [A-001, A-004]
---

# Charter Goals Field

## Constraints

1. **Charter MUST have goals array in frontmatter**
   - Array of goal IDs
   - Non-empty (at least one goal required)
   - Each element matches G-{number} pattern

2. **goals array MUST match goal headers in body**
   - Every goal ID in array MUST have corresponding header
   - Every goal header in body MUST be listed in array
   - Mismatch triggers validation error

3. **Goal IDs MUST be unique within Charter**
   - No duplicate entries in goals array
   - Duplicate triggers validation error

## Example

```yaml
---
id: Charter
type: charter
goals: [G-001, G-002, G-003, G-004, G-005]
---
```

## Validation Rules

- `jigy validate` MUST fail if goals is missing
- `jigy validate` MUST fail if goals is empty
- `jigy validate` MUST fail if goals contains duplicates
- `jigy validate` MUST fail if goal headers don't match array

## Rationale

The goals array serves as a machine-readable index of goals while the body headers provide human-readable descriptions. Requiring correspondence between the two ensures consistency and enables reliable goal reference validation.

