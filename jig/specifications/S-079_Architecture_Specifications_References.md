---
id: S-079
title: Architecture Specifications References
type: specification
outcomes: [O-024]
architecture: [A-001, A-004]
---

# Architecture Specifications References

## Constraints

1. **specifications field MUST reference existing spec IDs (if present)**
   - Field is optional
   - When present, must be an array of spec IDs
   - Each spec ID must match S-{NNN} format

2. **All referenced specs MUST exist**
   - Cross-referenced against specification files
   - Dangling references trigger validation error

3. **Empty specifications array is allowed but not required**
   - Architecture may exist without specifying any specs
   - Omitting the field entirely is preferred over empty array

## Example

```yaml
---
id: A-001
type: architecture
title: JIG Core Architecture
goals: [G-001, G-003]
specifications: [S-072, S-073, S-074, S-075, S-086, S-087, S-088]
---
```

## Validation Rules

- `jigy validate` MUST verify specifications references if present
- `jigy validate` MUST fail if any spec reference is invalid
- `jigy validate` MAY skip specifications validation if field is absent

## Rationale

The specifications relationship captures which specifications are governed by an architecture document. This enables impact analysis when architecture changes - all related specs may need review.

