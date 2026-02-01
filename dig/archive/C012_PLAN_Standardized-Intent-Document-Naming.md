---
title: "PLAN: Standardized Intent Document Naming"
type: plan
status: implemented
decision: "All work units completed, S/O files renamed to new convention"
created: 1767636000
created_human: "2026-01-05 12:00 CST"
parent: "[[C011_JIGPLAN_Standardized-Intent-Document-Naming]]"
children: []
---
# PLAN: Standardized Intent Document Naming

- **SCOPE**: dig/wip/C010_SCOPE_Standardized-Intent-Document-Naming.md
- **JIGPLAN**: dig/wip/C011_JIGPLAN_Standardized-Intent-Document-Naming.md
- **Start**: 2026-01-05
- **Status**: Draft
- **Branch**: feature/standardized-intent-naming

---

## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- B-decorators (layer 0) — Core decorator definitions
- B-impl-graph (layer 0) — Implementation graph generation
- B-intent-graph (layer 0) — Intent graph generation
- B-config (layer 0) — Configuration loading

**Layer Constraints:**
- B-validation at layer 0
- B-validation has no dependencies on other JIG bricks
- Changes isolated to validation module only

**Clean Break:**
- No backwards compatibility shims
- No feature flags
- Migration provides clean transition

---

## Work Unit Checklist

- [x] WU1: Validation Functions — tests ✓ / code ✓ / docs ✓
- [x] WU2: Validation Tests — tests ✓ / code ✓ / docs ✓
- [x] WU3: Migration Script — tests ✓ / code ✓ / docs ✓
- [x] WU4: Run Migration — tests ✓ / code ✓ / docs ✓
- [x] WU5: Intent Documents + Agent Context — tests ✓ / code ✓ / docs ✓
- [x] WU6: Validation — SCOPE verified ✓

---

## Work Units

### Work Unit 1: Validation Functions

**Goal**: Add filename format validation and H1 matching to specification, outcome, and architecture file validators.

**Specs Addressed**: S-018 (update), S-019 (update), S-076 (update)

**Acceptance Criteria**:
- [ ] `to_snake_case(title)` helper converts titles correctly (preserves acronyms, removes punctuation)
- [ ] `validate_filename_format()` checks `{TYPE}-{NNN}_{Title_Snake_Case}.md` pattern
- [ ] `validate_h1_matches_title()` verifies first H1 matches frontmatter title exactly
- [ ] `validate_specification_files()` calls new validation functions
- [ ] `validate_outcome_files()` calls new validation functions
- [ ] `validate_architecture_files()` calls new validation functions
- [ ] H1 must NOT include ID prefix (e.g., `# A-001: Title` is invalid)
- [ ] Error messages include file path, expected format, and actual value
- [ ] Code with @jig.implements decorators referencing S-018, S-019, S-076

**Success Gates** (all must pass):
- [ ] Python syntax valid: `python -m py_compile src/jig/validation/intent.py`
- [ ] No new linting/type errors: `ruff check src/jig/validation/intent.py`
- [ ] No modifications to FORBIDDEN bricks

**Escalation Triggers** (stop and ask human if):
- Implementation approach must deviate from JIGPLAN
- FORBIDDEN brick modification needed
- Ambiguity in snake_case conversion rules
- Existing validation structure incompatible with new checks

**Implementation Notes**:
- Files: `src/jig/validation/intent.py` (modify)
- Add helper function `to_snake_case()` near top of file
- Add `validate_filename_format(file_path, frontmatter, type_prefix)` function
- Add `validate_h1_matches_title(file_path, frontmatter)` function
- Integrate calls into existing `validate_specification_files()` (after frontmatter parsing)
- Integrate calls into existing `validate_outcome_files()` (after frontmatter parsing)
- Integrate calls into existing `validate_architecture_files()` (after frontmatter parsing)
- For architecture: remove existing H1 check that allows `# A-001: Title` pattern
- Decorators: functions already have `@jig.implements("S-018")` etc., extend behavior

**Human Verification**:
```bash
python -m py_compile src/jig/validation/intent.py
ruff check src/jig/validation/intent.py
```

**Note**: After this WU, `jigy validate` will FAIL on existing files. This is expected—WU4 (migration) fixes them.

---

### Work Unit 2: Validation Tests

**Goal**: Add comprehensive tests for filename format and H1 validation functions.

**Specs Addressed**: S-018 (verifies), S-019 (verifies), S-076 (verifies)

**Acceptance Criteria**:
- [ ] Test valid specification filename passes (`S-001_Valid_Title.md`)
- [ ] Test valid outcome filename passes (`O-015_Valid_Title.md`)
- [ ] Test valid architecture filename passes (`A-001_Valid_Title.md`)
- [ ] Test invalid filename without title fails (`S-001.md`)
- [ ] Test invalid filename non-zero-padded fails (`S-1_Title.md`)
- [ ] Test filename title mismatch fails
- [ ] Test H1 matches title passes
- [ ] Test H1 mismatch fails
- [ ] Test H1 with ID prefix fails (`# A-001: Title`)
- [ ] Test missing H1 fails
- [ ] Test snake_case: simple title → `Simple_Title`
- [ ] Test snake_case: acronym preserved → `CLI_Commands`
- [ ] Test snake_case: punctuation removed → `Whats_New`
- [ ] Test snake_case: hyphens preserved → `Cross-Tower_Isolation`
- [ ] Tests with @jig.verifies decorators

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/validation/test_filename_validation.py -v`
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors

**Escalation Triggers** (stop and ask human if):
- Test fixtures cannot replicate validation scenarios
- Discovered edge case not covered in SCOPE
- Test failures persist after 2 retry attempts

**Implementation Notes**:
- Files: `tests/validation/test_filename_validation.py` (new)
- Use `tmp_path` fixture for creating test files
- Create minimal valid frontmatter for each test case
- Test the helper functions directly (`to_snake_case()`)
- Test the validation functions with mock file paths
- Decorators to add: `@jig.verifies("S-018")`, `@jig.verifies("S-019")`, `@jig.verifies("S-076")`

**Human Verification**:
```bash
pytest tests/validation/test_filename_validation.py -v
```

---

### Work Unit 3: Migration Script

**Goal**: Create a script to rename all specification and outcome files to include title.

**Specs Addressed**: (none — tooling support)

**Acceptance Criteria**:
- [ ] Script at `scripts/migrate_intent_filenames.py`
- [ ] `--dry-run` flag shows planned renames without executing
- [ ] Uses `git mv` for renames to preserve history
- [ ] Handles all 75 specification files
- [ ] Handles all 23 outcome files
- [ ] Updates architecture H1 format (removes ID prefix)
- [ ] Script is idempotent (safe to run multiple times)
- [ ] Graceful error handling for edge cases

**Success Gates** (all must pass):
- [ ] Script runs without error: `python scripts/migrate_intent_filenames.py --dry-run`
- [ ] Dry run output shows correct renames
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors

**Escalation Triggers** (stop and ask human if):
- Some files have missing frontmatter or title
- Title produces invalid filename characters
- Duplicate filenames would result from migration
- Discovered files not matching expected patterns

**Implementation Notes**:
- Files: `scripts/migrate_intent_filenames.py` (new)
- Parse frontmatter with same logic as validation
- Use `to_snake_case()` function (import from jig.validation.intent or duplicate)
- For architecture: only update H1, filename already correct
- Print summary at end: files renamed, errors encountered
- Exit with non-zero code if any errors

**Human Verification**:
```bash
python scripts/migrate_intent_filenames.py --dry-run
# Review output for correctness
```

---

### Work Unit 4: Run Migration

**Goal**: Execute migration script to rename all intent document files.

**Specs Addressed**: (none — migration execution)

**Acceptance Criteria**:
- [ ] All 75 specification files renamed to `S-{NNN}_{Title}.md`
- [ ] All 23 outcome files renamed to `O-{NNN}_{Title}.md`
- [ ] Architecture H1 updated (remove ID prefix)
- [ ] Git shows proper renames (not delete+add)
- [ ] `jigy rebuild && jigy validate` passes
- [ ] Intent graph regenerates with new file paths

**Success Gates** (all must pass):
- [ ] Migration script completes without errors
- [ ] `jigy rebuild && jigy validate` passes
- [ ] `git status` shows renames, not deletions
- [ ] No modifications to FORBIDDEN bricks

**Escalation Triggers** (stop and ask human if):
- Migration script fails
- Validation fails after migration
- Git history appears broken
- Any file not successfully renamed

**Implementation Notes**:
- Run: `python scripts/migrate_intent_filenames.py`
- Verify with: `git status` (should show 98 renames: 75 specs + 23 outcomes)
- Run: `jigy rebuild && jigy validate`
- Commit migration separately from code changes

**Human Verification**:
```bash
python scripts/migrate_intent_filenames.py
git status
jigy rebuild && jigy validate
git diff --stat HEAD~1  # Should show renames
```

---

### Work Unit 5: Intent Documents + Agent Context

**Goal**: Create new outcome O-027 and specification S-092, plus add title guidance to agent context.

**Specs Addressed**: O-027 (create), S-092 (create)

**Acceptance Criteria**:
- [ ] `jig/outcomes/O-027_Discoverable_Intent_Document_Naming.md` created
- [ ] `jig/specifications/S-092_Intent_Document_Title_Requirements.md` created
- [ ] S-092 linked to O-027 via `implements` field
- [ ] Both files use new naming format (title in filename)
- [ ] Both files have H1 matching frontmatter title exactly
- [ ] `CLAUDE.md` created with title selection guidance
- [ ] Charter "For AI Agents" section includes title guidance
- [ ] `jigy rebuild && jigy validate` passes

**Success Gates** (all must pass):
- [ ] `jigy rebuild && jigy validate` passes
- [ ] New files follow correct format
- [ ] No modifications to FORBIDDEN bricks

**Escalation Triggers** (stop and ask human if):
- O-027 or S-092 ID conflicts with existing
- Validation fails on new files
- Unsure about CLAUDE.md location or format

**Implementation Notes**:
- Files:
  - `jig/outcomes/O-027_Discoverable_Intent_Document_Naming.md` (new)
  - `jig/specifications/S-092_Intent_Document_Title_Requirements.md` (new)
  - `CLAUDE.md` (new, project root)
  - `jig/Charter.md` (modify)

**O-027 content** (frontmatter):
```yaml
---
id: O-027
type: outcome
title: Discoverable Intent Document Naming
---
```

**S-092 content** (frontmatter):
```yaml
---
id: S-092
type: specification
title: Intent Document Title Requirements
implements: O-027
---
```

**CLAUDE.md guidance** (from SCOPE J.5.1):
```markdown
## Creating JIG Intent Documents

When creating specifications, outcomes, or architecture documents:

**Title Selection:**
- Describe BEHAVIOR or CAPABILITY, not implementation
- Use noun phrases that complete "This spec defines..."
- Avoid: version numbers, temporal words (New, Old), implementation details
- Titles are semi-permanent — choose carefully, renames cause git noise

**Examples:**
| Bad | Problem | Good |
|-----|---------|------|
| `New_Redis_Cache` | Temporal + implementation | `Response_Caching` |
| `Fix_Auth_Bug` | Task description | `Session_Persistence` |
| `User_Model_v2` | Version in title | `User_Profile_Schema` |

**Filename Format:** `{S/O/A}-{NNN}_{Title_In_Snake_Case}.md`
```

**Charter addition** (to "For AI Agents" section):
```markdown
8. **Choose stable titles**: When creating intent documents, select titles that describe capabilities, not implementations. Titles appear in filenames and are semi-permanent. Good: "Response Caching", "User Authentication". Bad: "New Cache", "Redis Layer", "Fix Login Bug".
```

**Human Verification**:
```bash
jigy rebuild && jigy validate
cat CLAUDE.md
cat jig/Charter.md
```

---

### Work Unit 6: Validation

**Goal**: Verify SCOPE problem is solved at system boundary.

**SCOPE Reference**:
> "Files like `S-047.md` reveal nothing about content without opening. Developers must memorize IDs or constantly open files to find relevant specs."

**Validation Approach**: Manual Checklist

**Reason Integration Test Not Feasible**: The core value is human discoverability—seeing meaningful filenames in `ls` output. This is a UX improvement, not programmatic behavior.

**Verification Steps**:
```bash
# 1. List specification files - should show descriptive names
ls jig/specifications/ | head -20

# 2. List outcome files - should show descriptive names  
ls jig/outcomes/ | head -10

# 3. File search should work with content keywords
ls jig/specifications/ | grep -i "validation"
ls jig/specifications/ | grep -i "graph"

# 4. Validation should pass
jigy rebuild && jigy validate

# 5. Intent graph should have correct file paths
head -5 jig/generated/intent-graph.ndjson
```

**Expected Result**:
- File listings immediately communicate what each spec/outcome defines
- Searching by keyword finds relevant files without opening them
- All validation passes with new format enforced
- Generated graphs reference new filenames

**Deliverable**:
- [ ] Checklist completed, findings in Execution Log below

**If Validation Fails**:
- Investigate which files don't follow format
- Check migration script for bugs
- Fix issues and re-run validation

**Human Verification**:
```bash
# Quick sanity check
ls jig/specifications/ | wc -l  # Should be 76 (75 + S-092)
ls jig/outcomes/ | wc -l        # Should be 24 (23 + O-027)
jigy rebuild && jigy validate
```

---

## Execution Log

(Filled in by orchestrator during execution)

### WU1 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

**Commit:** <hash>

---

### WU2 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

**Commit:** <hash>

---

### WU3 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

**Commit:** <hash>

---

### WU4 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

**Commit:** <hash>

---

### WU5 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

**Commit:** <hash>

---

### WU6 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

**Commit:** <hash>

---

## Completion Summary

**Scope Delivered:**
- All intent document filenames now include descriptive titles in snake_case
- Validation enforces filename format `{TYPE}-{NNN}_{Title_Snake_Case}.md`
- Validation enforces H1 matches frontmatter title exactly
- Agent guidance added to CLAUDE.md and Charter
- Migration script available for future use

**JIG Summary:**
- Specs updated: S-018, S-019, S-076 (validation now checks filename format and H1)
- Specs created: S-092 (existed prior, confirmed in place)
- Outcomes created: O-027 (existed prior, confirmed in place)
- Bricks modified: B-validation (added to_snake_case, validate_filename_format, validate_h1_matches_title)

**Clean Break Actions:**
- [x] All 98 intent files renamed (75 specs + 23 outcomes)
- [x] Architecture H1 format updated (removed ID prefix from A-001)
- [x] CLAUDE.md created with title guidance
- [x] Charter updated with title guidance (item 8 added)
- [x] Final `jigy rebuild && jigy validate` passed

**Reflection Roll-Up:**
- Repeatable wins: Migration script with --dry-run proved essential for safe execution
- Systemic frictions: Test fixtures needed bulk updates for new filename format
- Open questions: None - scope fully delivered

