---
id: S-019
title: Outcome File Validation
type: specification
outcomes: [O-005]
---

# Outcome File Validation

Validate outcome files against contract requirements.

## Acceptance Criteria

### Frontmatter Validation
- Parse YAML frontmatter from outcome markdown files
- Required fields validated: `id`, `type`, `title`
- ID format validated: must match `O-{NNN}` pattern (zero-padded 3 digits)
- ID uniqueness validated: no duplicate outcome IDs across all files
- Excluded fields rejected: `brick` must NOT be present
- Validation works when no outcome files present (outcomes are optional)

### Filename Validation
- Filename MUST follow pattern: `O-{NNN}_{Title_Snake_Case}.md`
- Filename ID MUST match frontmatter `id` field
- Filename title MUST match frontmatter `title` field (after snake_case conversion)
- Snake_case conversion: spaces to underscores, preserve capitalization

### Body Validation
- First H1 header in document body MUST match frontmatter `title` exactly
- H1 MUST NOT include ID prefix (e.g., `# O-001: Title` is invalid)

### Error Reporting
- Error messages include file path and specific field violations
- Expected filename shown when filename format is invalid
- Clear guidance for remediation

## Examples

**Valid:**
```
Filename: O-001_Discoverable_Implementation_Structure.md
Frontmatter: id: O-001, title: Discoverable Implementation Structure
H1: # Discoverable Implementation Structure
```

**Invalid:**
- `O-001.md` (missing title in filename)
- `O-1_Title.md` (ID not zero-padded)
- H1: `# O-001: Discoverable Structure` (ID prefix in H1)

## Rationale

Consistent naming enables file discoverability without opening files. Title in filename aids navigation and search. H1 matching frontmatter ensures document consistency. Outcomes remain optional artifacts.

**References**: A001 §10 (Validation Rules)
