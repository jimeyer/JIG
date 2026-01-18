---
id: S-106
title: Mend Command Apply Mode
type: specification
outcomes: [O-029]
architecture: [A-004]
---

# Mend Command Apply Mode

The `jigy mend --apply fixes.json` command applies explicit fixes from a JSON file.

**Acceptance Criteria**:
- Command `jigy mend --apply <file>` reads fixes from the specified JSON file
- The JSON file format matches the `errors` array from `jigy validate -j`
- Each fix is applied regardless of `auto` value (explicit user approval)
- Missing or malformed fixes in the JSON file cause validation errors, not silent skips
- Fixes can be combined: `jigy mend --auto --apply fixes.json`
- The `--dry-run` flag shows what would change without modifying files
- The `-j` flag outputs results as JSON
- Exit code 0 on success, 1 on partial failure, 2 on error

**Rationale**: Apply mode enables human-curated repairs. Agents can generate fix files for human review, or humans can edit the JSON to customize repairs before applying.

**Example Workflow**:
```bash
# Generate fix templates
jigy validate -j > fixes.json

# Human reviews and edits fixes.json

# Apply curated fixes
jigy mend --apply fixes.json
```
