---
title: "JOURNAL: Standardized Intent Document Naming"
type: journal
status: complete
created: 1767654400
created_human: "2026-01-05 17:00 CST"
parent: "[[C012_PLAN_Standardized-Intent-Document-Naming]]"
children: []
---
# Execution Journal: Standardized Intent Document Naming

**PLAN:** dig/wip/C012_PLAN_Standardized-Intent-Document-Naming.md
**Started:** 2026-01-05 17:00 CST
**Completed:** 2026-01-05 18:20 CST
**Status:** Complete
**Branch:** feature/standardized-intent-naming

---

## Entries

### Entry 1 | 2026-01-05 17:00 | Pre-Execution

```yaml
type: observation
wu: null
```

Pre-execution observations:
- Branch created: `feature/standardized-intent-naming`
- S-092 and O-027 already exist (created during JIGPLAN phase)
- 75 specification files currently named `S-{NNN}.md` (need rename to include title)
- 23 outcome files currently named `O-{NNN}.md` (need rename to include title)
- Architecture file A-001 has H1 with ID prefix (`# A-001: JIG Core Architecture`) - needs update
- Current validation in `src/jig/validation/intent.py` checks filename matches `{id}.md` pattern
- This validation will need to change to `{id}_{title}.md` pattern

FORBIDDEN bricks confirmed:
- B-decorators (layer 0)
- B-impl-graph (layer 0)
- B-intent-graph (layer 0)
- B-config (layer 0)

Target brick: B-validation (layer 0, no dependencies on other JIG bricks)

---

### Entry 2 | 2026-01-05 17:10 | WU1 Complete

```yaml
type: outcome
wu: WU1
spec: S-018, S-019, S-076
```

Added three new validation functions to `src/jig/validation/intent.py`:
- `to_snake_case()` - converts titles to filename-safe format
- `validate_filename_format()` - checks `{TYPE}-{NNN}_{Title}.md` pattern
- `validate_h1_matches_title()` - ensures H1 matches frontmatter title

Integrated into `validate_specification_files()`, `validate_outcome_files()`, and `validate_architecture_files()`.

All functions have `@jig.implements("S-018", "S-019", "S-076")` decorators.

---

### Entry 3 | 2026-01-05 17:15 | WU2 Complete

```yaml
type: outcome
wu: WU2
spec: S-018, S-019, S-076
```

Created `tests/validation/test_filename_validation.py` with 20 tests covering:
- Snake case conversion (7 tests)
- Filename format validation (6 tests)
- H1 matching validation (7 tests)

All tests pass. Tests have `@jig.verifies` decorators.

---

### Entry 4 | 2026-01-05 17:20 | WU3 Complete

```yaml
type: outcome
wu: WU3
```

Created `scripts/migrate_intent_filenames.py` with:
- `--dry-run` flag for preview
- Uses `git mv` to preserve history
- Handles spec rename, outcome rename, architecture H1 update

Dry run shows 99 operations (75 specs + 23 outcomes + 1 arch H1 update).

---

### Entry 5 | 2026-01-05 17:25 | WU4 Complete

```yaml
type: outcome
wu: WU4
```

Migration executed successfully:
- 75 specification files renamed
- 23 outcome files renamed
- 1 architecture H1 updated (removed ID prefix)

Git shows proper `R` (rename) status for all 98 files.
`jigy rebuild && jigy validate` passes.

---

### Entry 6 | 2026-01-05 17:30 | WU5 Complete

```yaml
type: outcome
wu: WU5
```

Agent context updates:
- Created `CLAUDE.md` with filename format and title selection guidance
- Updated `jig/Charter.md` "For AI Agents" section with item 8 (title stability)
- Confirmed S-092 and O-027 exist with correct content

---

### Entry 7 | 2026-01-05 17:35 | WU6 Complete

```yaml
type: outcome
wu: WU6
```

Validation checklist verified:
1. ✓ `ls jig/specifications/` shows descriptive names
2. ✓ `ls jig/outcomes/` shows descriptive names
3. ✓ Keyword search works (e.g., `grep -i validation`)
4. ✓ `jigy rebuild && jigy validate` passes
5. ✓ Intent graph has correct file paths

---

### Entry 8 | 2026-01-05 17:40 | Test Fixture Updates

```yaml
type: friction
wu: null
```

Many existing test fixtures needed updates to use new filename format:
- `tests/cli/test_validate.py` - 6 fixtures updated
- `tests/config/test_cli_integration.py` - 4 fixtures updated
- `tests/cli/test_align.py` - 2 fixtures updated
- `tests/validation/test_intent.py` - 2 fixtures updated

This was expected - clean break means old format no longer valid.

---

## Synthesis

### Patterns

- Migration script with `--dry-run` essential for safe bulk renames
- Using `git mv` preserves history as intended
- Validation functions are well-isolated in B-validation brick
- Test fixtures mirror production code patterns closely

### Friction Summary

- Test fixtures across multiple files needed updating for new format
- Some sandbox restrictions prevented git-dependent test execution (not a code issue)

### Suggestions

- Consider a pre-commit hook to validate filename format on new files
- Future validation rules should consider test fixture update burden

### Wins

- Clean migration: 98 file renames with zero errors
- Immediate discoverability: `ls jig/specifications/ | grep validation` now works
- Agent guidance in place before file creation (CLAUDE.md + Charter)


