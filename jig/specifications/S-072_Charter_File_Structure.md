---
id: S-072
title: Charter File Structure
type: specification
outcome: O-023
outcomes: [O-023]
architecture: [A-001, A-004]
---

# Charter File Structure

## Constraints

1. **Charter MUST be a single file at jig/Charter.md**
   - Exactly one Charter file per project
   - Located at the root of the jig directory
   - Named `Charter.md` (case-sensitive)

2. **Charter MUST have valid YAML frontmatter**
   - Frontmatter delimited by `---` lines
   - Contains required fields: id, type, defines_goals

3. **Charter id MUST be "Charter"**
   - Literal string, not a pattern
   - Case-sensitive

4. **Charter type MUST be "charter"**
   - Lowercase string
   - Enables node type identification in intent graph

## Validation Rules

- `jigy validate` MUST fail if Charter.md does not exist
- `jigy validate` MUST fail if Charter.md has invalid frontmatter
- `jigy validate` MUST fail if multiple Charter files detected

## Rationale

The Charter is the root of the intent hierarchy. A single, predictable location ensures all downstream artifacts can reference goals consistently. The id and type fields enable machine processing while the body contains human-readable content.

