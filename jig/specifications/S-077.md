---
id: S-077
title: Architecture ID Format
type: specification
outcome: O-024
---

# Architecture ID Format

## Constraints

1. **Architecture IDs MUST match `A-{NNN}` pattern**
   - Uppercase A followed by hyphen
   - Three-digit zero-padded number
   - Regex: `^A-\d{3}$`

2. **Architecture IDs MUST be unique**
   - No duplicate IDs across architecture files
   - First file with ID wins; duplicate triggers error

3. **ID MUST appear in frontmatter**
   - Field name: id
   - Value: A-{NNN} format

## Examples

Valid architecture IDs:
- A-001
- A-042
- A-999

Invalid architecture IDs:
- A-1 (not zero-padded)
- A-0001 (too many digits)
- a-001 (lowercase)
- Arch-001 (wrong prefix)

## Validation Rules

- `jigy validate` MUST verify architecture ID format
- `jigy validate` MUST detect duplicate architecture IDs
- `jigy validate` MUST verify ID matches file name

## Rationale

Zero-padded three-digit format ensures consistent sorting and allows for up to 999 architecture documents. The A- prefix distinguishes architecture IDs from other artifact types (O-, S-, G-).

