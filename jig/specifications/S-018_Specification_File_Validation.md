---
id: S-018
title: Specification File Validation
type: specification
outcomes: [O-005]
architecture: [A-004]
---

# Specification File Validation

Validate specification files against contract requirements.

## Acceptance Criteria

### Frontmatter Validation
- Parse YAML frontmatter from specification markdown files
- Required fields validated: `id`, `type`, `title`
- ID format validated: must match `S-{NNN}` pattern (zero-padded 3 digits)
- ID uniqueness validated: no duplicate spec IDs across all files
- Excluded fields rejected: `brick`, `depends_on`, `content` must NOT be present

### Filename Validation
- Filename MUST follow pattern: `S-{NNN}_{Title_Snake_Case}.md`
- Filename ID MUST match frontmatter `id` field
- Filename title MUST match frontmatter `title` field (after snake_case conversion)
- Snake_case conversion: spaces to underscores, preserve capitalization

### Body Validation
- First H1 header in document body MUST match frontmatter `title` exactly
- H1 MUST NOT include ID prefix (e.g., `# S-001: Title` is invalid)

### Error Reporting
- Error messages include file path and specific field violations
- Expected filename shown when filename format is invalid
- Clear guidance for remediation

## Examples

**Valid:**
```
Filename: S-001_Python_Code_Structure_Extraction.md
Frontmatter: id: S-001, title: Python Code Structure Extraction
H1: # Python Code Structure Extraction
```

**Invalid:**
- `S-001.md` (missing title in filename)
- `S-1_Title.md` (ID not zero-padded)
- H1: `# S-001: Python Code Structure` (ID prefix in H1)

## Rationale

Consistent naming enables file discoverability without opening files. Title in filename aids navigation and search. H1 matching frontmatter ensures document consistency.

**References**: A001 §10 (Validation Rules)
