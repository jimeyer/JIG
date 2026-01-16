---
id: S-076
title: Architecture File Location
type: specification
outcome: O-024
outcomes: [O-024]
architecture: [A-001, A-004]
---

# Architecture File Location

## Constraints

1. **Architecture files MUST be in jig/architecture/ directory**
   - Directory must exist if any architecture documents exist
   - All architecture files reside in this single directory

2. **Architecture files MUST follow naming pattern: A-{NNN}_{Title}.md**
   - A- prefix (uppercase)
   - Three-digit zero-padded number
   - Underscore separator
   - Title in Title_Case with underscores
   - .md extension

3. **Architecture file name MUST match internal id and title**
   - File A-001_Core_Architecture.md MUST have id: A-001 in frontmatter
   - Filename title MUST match frontmatter `title` field (after snake_case conversion)
   - Mismatch triggers validation error

4. **First H1 header MUST match frontmatter title**
   - H1 MUST be exactly the frontmatter `title` value
   - H1 MUST NOT include ID prefix (e.g., `# A-001: Title` is invalid)

## Examples

Valid:
```
Filename: A-001_JIG_Core_Architecture.md
Frontmatter: id: A-001, title: JIG Core Architecture
H1: # JIG Core Architecture
```

Invalid:
- `jig/architecture/A-1_Core.md` (not zero-padded)
- `jig/architecture/arch-001.md` (wrong prefix)
- `jig/A-001.md` (wrong directory)
- H1: `# A-001: JIG Core Architecture` (ID prefix in H1)

## Validation Rules

- `jigy validate` MUST verify architecture files are in correct directory
- `jigy validate` MUST verify file name follows pattern
- `jigy validate` MUST verify file name matches internal id
- `jigy validate` MUST verify filename title matches frontmatter title
- `jigy validate` MUST verify first H1 matches frontmatter title

## Rationale

Consistent location and naming enables reliable discovery and establishes clear distinction from other artifact types. Zero-padding ensures correct alphabetical sorting. H1 matching frontmatter ensures document consistency across all intent document types.

