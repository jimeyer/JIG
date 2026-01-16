---
id: S-078
title: Architecture Goals Required
type: specification
outcomes: [O-024]
architecture: [A-001, A-004]
---

# Architecture Goals Required

## Constraints

1. **Architecture MUST have non-empty goals array**
   - Field is required in frontmatter
   - Array must contain at least one goal ID
   - All goal IDs must reference valid Charter goals

2. **Each goal ID MUST match G-{number} format**
   - Same format as Charter goal definitions
   - Cross-referenced against Charter.goals

3. **Invalid goal references MUST trigger validation error**
   - Reference to non-existent goal is an error
   - Validation cannot proceed with dangling references

## Example

```yaml
---
id: A-001
type: architecture
title: JIG Core Architecture
goals: [G-001, G-003, G-004, G-005]
---
```

## Validation Rules

- `jigy validate` MUST fail if goals is missing
- `jigy validate` MUST fail if goals is empty
- `jigy validate` MUST fail if any goal reference is invalid

## Rationale

Architecture documents exist to achieve project goals. Requiring explicit goal linkage ensures architectural decisions are traceable to purpose and enables queries like "which architecture supports G-003?"

