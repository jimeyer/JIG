---
id: S-087
title: Tower Value Format
type: specification
outcome: O-026
outcomes: [O-026]
architecture: [A-001, A-004]
---

# Tower Value Format

## Constraints

1. **tower MUST be kebab-case if present**
   - Lowercase letters, numbers, and hyphens only
   - Must start with a letter
   - Must not end with a hyphen
   - Regex: `^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$`

2. **Tower names MUST be descriptive**
   - Represent logical component boundaries
   - Examples: backend, frontend, shared, data-pipeline

3. **Reserved tower names**
   - "default" is reserved for bricks without explicit tower
   - Using "default" explicitly is not recommended

## Examples

Valid tower names:
- backend
- frontend
- data-pipeline
- api-v2
- ml

Invalid tower names:
- Backend (uppercase)
- data_pipeline (underscore)
- -backend (starts with hyphen)
- backend- (ends with hyphen)
- 2fast (starts with number)

## Validation Rules

- `jigy validate` MUST check tower format when field is present
- Invalid tower format triggers validation error
- Valid format is prerequisite for tower isolation checking

## Rationale

Kebab-case is consistent with common naming conventions and prevents issues with case-sensitive file systems. The format is simple to validate and read.

