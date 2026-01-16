---
id: S-095
title: Bidirectional Reference Consistency
type: specification
outcomes: [O-004, O-025]
architecture: [A-004]
---

# Bidirectional Reference Consistency

Specification back-references must be consistent with forward-references from outcomes and architecture.

## Acceptance Criteria

### Outcome-to-Specification Consistency
- If outcome O.specifications contains spec S, then S.outcomes MUST contain O
- If spec S.outcomes contains outcome O, then O.specifications MUST contain S
- Missing back-reference from spec to outcome is reported as error
- Missing forward-reference from outcome to spec is reported as error

### Architecture-to-Specification Consistency
- If architecture A.specifications contains spec S, then S.architecture MUST contain A
- If spec S.architecture contains architecture A, then A.specifications MUST contain S
- Missing back-reference from spec to architecture is reported as error
- Missing forward-reference from architecture to spec is reported as error

### Error Reporting
- Error messages identify which document has the missing reference
- Error messages include both IDs (source and target of inconsistency)
- Clear guidance on which direction is missing

## Algorithm

```
1. Build forward index from outcomes:
   forward_outcome_to_spec = {O-id: [S-ids from O.specifications]}

2. Build forward index from architecture:
   forward_arch_to_spec = {A-id: [S-ids from A.specifications]}

3. Build back index from specifications:
   back_spec_to_outcomes = {S-id: [O-ids from S.outcomes]}
   back_spec_to_arch = {S-id: [A-ids from S.architecture]}

4. For each outcome O:
   For each spec S in O.specifications:
     If O not in back_spec_to_outcomes[S]:
       ERROR: O references S but S doesn't reference O

5. For each spec S with outcomes:
   For each outcome O in S.outcomes:
     If S not in forward_outcome_to_spec[O]:
       ERROR: S references O but O doesn't reference S

6. Repeat steps 4-5 for architecture/spec relationships
```

## Examples

**Valid bidirectional references:**
```yaml
# O-001.md
specifications: [S-042, S-043]

# S-042.md
outcomes: [O-001, O-015]  # Includes O-001

# S-043.md
outcomes: [O-001]  # Includes O-001
```

**Invalid - missing back-reference:**
```yaml
# O-001.md
specifications: [S-042]

# S-042.md
outcomes: []  # ERROR: O-001 references S-042 but S-042 doesn't reference O-001
```

**Invalid - missing forward-reference:**
```yaml
# O-001.md
specifications: []

# S-042.md
outcomes: [O-001]  # ERROR: S-042 references O-001 but O-001 doesn't reference S-042
```

## Rationale

Bidirectional consistency ensures the intent graph accurately reflects relationships between outcomes, architecture, and specifications. Inconsistent references create a corrupted graph where traversal from outcome to spec differs from traversal from spec to outcome. This validation catches data entry errors and ensures graph integrity.

## References

- O-004: Early Error Detection in Artifact Validation
- O-025: Intent Graph Captures Full Hierarchy
