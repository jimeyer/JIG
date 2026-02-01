---
id: S-086
title: Brick Tower Field Optional
type: specification
outcome: O-026
outcomes: [O-026]
architecture: [A-001, A-004]
---

# Brick Tower Field Optional

## Constraints

1. **Bricks MAY have optional tower field in bricks.yaml**
   - Field name: tower
   - Field is optional (not required)
   - When omitted, brick belongs to implicit single-tower

2. **Single-tower projects SHOULD omit tower field**
   - Omitting tower field indicates cohesive, single-component project
   - Cross-tower validation is skipped when no towers declared
   - This is the default for most projects

3. **Tower field presence enables multi-tower mode**
   - At least one brick with tower field activates tower validation
   - All bricks with tower field are grouped by tower value
   - Bricks without tower field belong to "default" tower

## Example (Single-Tower - Recommended for JIG)

```yaml
- id: B-decorators
  name: JIG Core Decorators
  layer: 0
  # tower field omitted - single-tower project
  units:
    - M-jig.__init__
```

## Example (Multi-Tower)

```yaml
- id: B-api
  name: API Layer
  layer: 1
  tower: backend
  units:
    - M-ase.api

- id: B-ui
  name: UI Components
  layer: 1
  tower: frontend
  units:
    - M-ase.ui
```

## Rationale

Tower partitioning is opt-in. Projects that don't need vertical isolation (like JIG itself) simply don't use towers. This keeps the common case simple while enabling advanced architectural patterns when needed.

