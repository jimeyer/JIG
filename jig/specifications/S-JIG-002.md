---
id: S-JIG-002
type: specification
title: "OSTC nodes use YAML frontmatter + Markdown"
subsystem: core
implements:
  - O-JIG-002
  - O-JIG-004
created: 2025-11-18
---

# Specification: OSTC Node Format

All Intent nodes (Outcome, Specification, Test, Constraint) use YAML frontmatter + Markdown body.

## Format Specification

### File Structure
```markdown
---
id: O-XXX-NNN
type: outcome|specification|test|constraint
title: "Human-readable title"
subsystem: subsystem-name
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft|active|deprecated
---

# Markdown Title

Markdown content here...

## Sections

More content...
```

### Required Fields (YAML frontmatter)
- `id`: Node identifier (format: `[OSTC]-[A-Z0-9]+-\d{3}`)
- `type`: One of: outcome, specification, test, constraint
- `title`: Human-readable title (quoted string)

### Optional Fields
- `subsystem`: Subsystem name (lowercase, hyphenated)
- `created`: Creation date (YYYY-MM-DD)
- `updated`: Last update date (YYYY-MM-DD)
- `status`: draft | active | deprecated
- `source_delta`: Path to delta file that created this (for traceability)
- `source_commit`: Git commit SHA
- `source_branch`: Git branch name

### ID Format Rules
- Outcome: `O-{PROJECT}-{NNN}` (e.g., O-JIG-001)
- Specification: `S-{PROJECT}-{NNN}` (e.g., S-JIG-001)
- Test: `T-{PROJECT}-{NNN}` (e.g., T-JIG-001)
- Constraint: `C-{PROJECT}-{NNN}` (e.g., C-JIG-001)

Where:
- `{PROJECT}`: Uppercase project abbreviation (e.g., JIG, AUTH)
- `{NNN}`: Zero-padded 3-digit number (001-999)

### Markdown Body
- Free-form markdown content
- Recommended sections (not enforced):
  - Value / Rationale
  - Acceptance Criteria / Requirements
  - Related (links to other nodes)
  - History (changelog)

## Parsing

Use `python-frontmatter` library for parsing:
```python
import frontmatter

with open('jig/outcomes/O-JIG-001.md') as f:
    post = frontmatter.load(f)
    metadata = post.metadata  # YAML as dict
    content = post.content    # Markdown as string
```

## Rationale

YAML frontmatter + Markdown is:
- Human-readable (cat/less work)
- Well-supported (many parsers available)
- Git-friendly (meaningful diffs)
- Standard (used by Jekyll, Hugo, many SSGs)
- Simple (no custom format)

## Acceptance Criteria

- Parser handles all valid OSTC nodes
- Parser validates required fields
- Parser rejects invalid ID formats
- Generated nodes follow format exactly

## Related

- implements: O-JIG-002 (simple text formats)
- subsystem: core

## History

- 2025-11-18: Created during WU0 bootstrap (known constraint from SCOPE)
