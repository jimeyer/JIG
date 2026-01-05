---
id: S-075
title: Goal ID Format
type: specification
outcome: O-023
---

# Goal ID Format

## Constraints

1. **Goal IDs MUST match `G-{number}` pattern**
   - Uppercase G followed by hyphen
   - Followed by one or more digits
   - Regex: `^G-\d+$`

2. **Goal numbers are NOT zero-padded**
   - Valid: G-1, G-5, G-100
   - Invalid: G-001, G-01

3. **Goal IDs MUST be unique within Charter**
   - No duplicate goal numbers allowed

## Reference Validation

All references to goals in other artifacts MUST use this exact format:
- Architecture supports_goals arrays
- Outcome supports_goals arrays

## Examples

Valid goal IDs:
- G-1
- G-5
- G-100

Invalid goal IDs:
- G-001 (zero-padded)
- g-1 (lowercase)
- G1 (missing hyphen)
- G- (missing number)

## Validation Rules

- `jigy validate` MUST verify goal ID format in Charter
- `jigy validate` MUST verify all goal references match defined goals

## Rationale

Simple, unpadded goal IDs are more readable and avoid sorting confusion. The format mirrors the established O-{NNN} and S-{NNN} patterns but omits padding since projects typically have fewer than 10 goals.

