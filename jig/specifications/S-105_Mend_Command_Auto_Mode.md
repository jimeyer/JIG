---
id: S-105
title: Mend Command Auto Mode
type: specification
outcomes: [O-029]
architecture: [A-004]
---

# Mend Command Auto Mode

The `jigy mend --auto` command applies all fixes where `auto: true` from validation errors.

**Acceptance Criteria**:
- Command `jigy mend --auto` runs validation and applies all auto-fixable errors
- Only fixes with `auto: true` are applied; manual fixes are skipped
- Each applied fix is reported to stdout with file and action
- Skipped fixes (manual) are listed with reason
- The `--dry-run` flag shows what would change without modifying files
- The `-j` flag outputs results as JSON
- Exit code 0 on success (all auto-fixes applied), 1 on partial success (some fixes skipped), 2 on error
- Files are modified in place; YAML formatting is preserved where possible

**Rationale**: Auto mode enables one-command repair of mechanical validation errors. Agents and CI pipelines can run `jigy mend --auto` to fix common issues without human intervention.

**Example Usage**:
```bash
# Fix all auto-fixable errors
jigy mend --auto

# Preview what would be fixed
jigy mend --auto --dry-run

# Fix and output JSON results
jigy mend --auto -j
```
