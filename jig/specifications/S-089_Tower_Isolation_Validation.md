---
id: S-089
title: Tower Isolation Validation
type: specification
outcome: O-026
outcomes: [O-026]
architecture: [A-004]
---

# Tower Isolation Validation

## Constraints

1. **jigy validate MUST check for cross-tower dependencies**
   - Scans implementation graph for function calls
   - Identifies source and target brick for each call
   - Flags calls where source.tower != target.tower

2. **Validation is skipped for single-tower projects**
   - If no bricks have tower field, skip tower isolation checks
   - Single-tower message shown: "single-tower project, isolation check skipped"

3. **Validation output MUST be actionable**
   - Report: which function, in which brick/tower
   - Report: calls which function, in which brick/tower
   - Enable developer to locate and fix violation

## Output Format

```
Tower isolation violations:
  B-api (tower: backend) → B-ui (tower: frontend)
    F-ase.api.handler.render() calls F-ase.ui.components.Button()
```

## Validation Rules

- `jigy validate` MUST include tower isolation in validation suite
- Violations are errors, not warnings
- All violations reported (not just first)

## Rationale

Automated enforcement catches cross-tower dependencies before they accumulate. Early detection prevents architectural drift and maintains component independence.

