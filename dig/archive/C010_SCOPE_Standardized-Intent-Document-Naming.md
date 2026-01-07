---
title: "SCOPE: Standardized Intent Document Naming"
type: scope
status: implemented
decision: completed
created: 1767550000
created_human: "2026-01-04 12:00 CST"
parent: null
children: ['[[C011_JIGPLAN_Standardized-Intent-Document-Naming]]']
---
# SCOPE: Standardized Intent Document Naming

**ID:** C010
**Status:** Draft
**Date:** 2026-01-04
**Implements:** (standalone enhancement)

---

## Executive Summary

This scope document defines the work required to standardize the naming convention for all JIG intent documents (Specifications, Outcomes, and Architectures) to include the title in the filename.

**Current State:**
- Architecture files: `A-{NNN}_{Title_Snake_Case}.md` (already compliant)
- Outcome files: `O-{NNN}.md` (title NOT in filename)
- Specification files: `S-{NNN}.md` (title NOT in filename)

**Target State:**
- All intent files: `{A/O/S}-{NNN}_{Title_Snake_Case}.md`
- Title required in frontmatter
- First H1 in body must match frontmatter title exactly
- Decorators unchanged (still reference by ID: `S-001`, `O-015`, etc.)

---

## Motivation

### Problem

1. **Discoverability**: Files like `S-047.md` reveal nothing about content without opening
2. **Navigation**: Developers must memorize IDs or constantly open files to find relevant specs
3. **Consistency**: Architecture documents already use the full naming convention; others don't
4. **Human readability**: File listings are opaque without descriptive names

### Solution

Standardize all intent document filenames to include the title in snake_case, matching the pattern already used for Architecture documents.

**Example transformation:**
```
Before: jig/specifications/S-001.md
After:  jig/specifications/S-001_Python_Code_Structure_Extraction.md

Before: jig/outcomes/O-001.md
After:  jig/outcomes/O-001_Discoverable_Implementation_Structure.md
```

---

## Current State Analysis

### File Naming Patterns

| Type | Current Pattern | Files | Compliant? |
|------|-----------------|-------|------------|
| Architecture | `A-{NNN}_{Title_Snake_Case}.md` | 1 | YES |
| Outcome | `O-{NNN}.md` | 22 | NO |
| Specification | `S-{NNN}.md` | 74 | NO |

### Frontmatter Requirements

| Type | `title` in frontmatter? | H1 in body? |
|------|-------------------------|-------------|
| Architecture | Required | `# A-001: {Title}` |
| Outcome | Required | `# {Title}` |
| Specification | Required | `# {Title}` |

### Current Discovery Patterns (Code)

```python
# src/jig/validation/intent.py
spec_files = sorted(spec_dir.glob("S-*.md"))       # Line 32
outcome_files = sorted(outcome_dir.glob("O-*.md")) # Line 151
arch_files = sorted(architecture_dir.glob("A-*.md")) # Line 884

# src/jig/intent_graph/generator.py
spec_dir.glob("S-*.md")       # Line 272
outcome_dir.glob("O-*.md")    # Line 314
architecture_dir.glob("A-*.md") # Line 223
```

**Key insight**: Current glob patterns (`S-*.md`, `O-*.md`, `A-*.md`) will continue to work with the new naming convention. The ID is extracted from frontmatter, not the filename.

---

## Target State

### Naming Convention (All Types)

```
{TYPE}-{NNN}_{Title_Snake_Case}.md
```

Where:
- `{TYPE}` = `A`, `O`, or `S`
- `{NNN}` = Zero-padded 3-digit number (e.g., `001`, `047`, `091`)
- `{Title_Snake_Case}` = Frontmatter title converted to snake_case

### Snake Case Rules

1. Replace spaces with underscores
2. Remove punctuation except hyphens within compound words
3. Capitalize each word (Title_Case, not title_case)
4. Preserve acronyms (e.g., `CLI`, `API`, `YAML`)

**Examples:**
```
title: "Python Code Structure Extraction"
filename: S-001_Python_Code_Structure_Extraction.md

title: "CLI Show Commands"
filename: S-072_CLI_Show_Commands.md

title: "YAML Frontmatter Parsing"
filename: S-015_YAML_Frontmatter_Parsing.md
```

### Consistency Requirements

1. **Frontmatter `title` field**: REQUIRED for all types
2. **Filename title**: MUST match frontmatter `title` (after snake_case conversion)
3. **Body H1**: MUST match frontmatter `title` exactly
4. **ID in frontmatter**: MUST match filename ID (e.g., `S-001`)

### H1 Format Standardization

**Proposed (uniform across all types):**
```markdown
# {Title}
```

**Current state (inconsistent):**
- Architecture: `# A-001: JIG Core Architecture` (ID + Title)
- Outcome: `# Discoverable Implementation Structure` (Title only)
- Specification: `# Python Code Structure Extraction` (Title only)

**Decision**: Standardize to title-only H1 for all types. The ID is in frontmatter and filename; duplicating it in H1 adds noise.

**Migration for Architecture:**
```markdown
# Before
# A-001: JIG Core Architecture

# After
# JIG Core Architecture
```

---

## PART A: Validation Code Changes

**File:** `src/jig/validation/intent.py`

### A.1 New Validation Function: Filename Format

```python
def validate_filename_format(file_path: Path, frontmatter: dict, type_prefix: str) -> List[str]:
    """Validate that filename matches expected pattern and frontmatter title.

    Pattern: {TYPE}-{NNN}_{Title_Snake_Case}.md

    Returns list of error messages (empty if valid).
    """
```

**Validation rules:**
1. Filename must match regex: `^{TYPE}-\d{3}_[A-Z][A-Za-z0-9_]+\.md$`
2. ID extracted from filename must match frontmatter `id`
3. Title extracted from filename must match `to_snake_case(frontmatter['title'])`

### A.2 New Validation Function: H1 Matches Title

```python
def validate_h1_matches_title(file_path: Path, frontmatter: dict) -> List[str]:
    """Validate that first H1 in document body matches frontmatter title.

    Returns list of error messages (empty if valid).
    """
```

**Validation rules:**
1. Document body must contain at least one H1 (`# ...`)
2. First H1 content must exactly match frontmatter `title`
3. H1 must not include ID prefix (e.g., `# A-001: Title` is invalid)

### A.3 Helper Function: Snake Case Conversion

```python
def to_snake_case(title: str) -> str:
    """Convert title to snake_case for filename matching.

    Rules:
    - Replace spaces with underscores
    - Remove punctuation (except hyphens in compound words)
    - Preserve capitalization (Title_Case)
    - Preserve acronyms

    Examples:
        "Python Code Structure" -> "Python_Code_Structure"
        "CLI Show Commands" -> "CLI_Show_Commands"
        "YAML Frontmatter Parsing" -> "YAML_Frontmatter_Parsing"
    """
```

### A.4 Update Existing Validation Functions

**`validate_specification_files()`** (lines 18-133):
- Add call to `validate_filename_format(spec_file, frontmatter, "S")`
- Add call to `validate_h1_matches_title(spec_file, frontmatter)`

**`validate_outcome_files()`** (lines 136-262):
- Add call to `validate_filename_format(outcome_file, frontmatter, "O")`
- Add call to `validate_h1_matches_title(outcome_file, frontmatter)`

**`validate_architecture_files()`** (lines 859-1056):
- Add call to `validate_filename_format(arch_file, frontmatter, "A")`
- Add call to `validate_h1_matches_title(arch_file, frontmatter)`
- Remove existing H1 format check that allows `# A-001: Title` pattern

### A.5 Error Message Format

```
ERROR: Invalid filename format
  File: jig/specifications/S-001.md
  Expected: S-001_Python_Code_Structure_Extraction.md
  Rule: Filename must be {TYPE}-{NNN}_{Title_Snake_Case}.md

ERROR: Filename title mismatch
  File: jig/specifications/S-001_Python_Code.md
  Frontmatter title: "Python Code Structure Extraction"
  Filename title: "Python_Code"
  Rule: Filename title must match frontmatter title

ERROR: H1 does not match title
  File: jig/specifications/S-001_Python_Code_Structure_Extraction.md
  Frontmatter title: "Python Code Structure Extraction"
  First H1: "# S-001: Python Code Structure"
  Rule: First H1 must exactly match frontmatter title

ERROR: Missing H1 header
  File: jig/specifications/S-001_Python_Code_Structure_Extraction.md
  Rule: Document must have at least one H1 (# Title) header
```

---

## PART B: Test Coverage

**New test file:** `test/validation/test_filename_validation.py`

### B.1 Test Cases: Filename Format

```python
def test_valid_spec_filename():
    """S-001_Valid_Title.md passes validation."""

def test_valid_outcome_filename():
    """O-015_Valid_Title.md passes validation."""

def test_valid_architecture_filename():
    """A-001_Valid_Title.md passes validation."""

def test_invalid_spec_filename_no_title():
    """S-001.md fails validation with clear error."""

def test_invalid_spec_filename_wrong_format():
    """S-1_Title.md fails (non-zero-padded ID)."""

def test_filename_title_mismatch():
    """Filename title differs from frontmatter title."""

def test_special_characters_in_title():
    """Titles with punctuation convert correctly to snake_case."""
```

### B.2 Test Cases: H1 Validation

```python
def test_h1_matches_title():
    """First H1 matches frontmatter title."""

def test_h1_mismatch():
    """First H1 differs from frontmatter title."""

def test_h1_with_id_prefix_fails():
    """H1 like '# A-001: Title' fails validation."""

def test_missing_h1():
    """Document without H1 fails validation."""

def test_multiple_h1_uses_first():
    """Only first H1 is checked for title match."""
```

### B.3 Test Cases: Snake Case Conversion

```python
def test_simple_title():
    """'Simple Title' -> 'Simple_Title'"""

def test_acronym_preserved():
    """'CLI Commands' -> 'CLI_Commands'"""

def test_punctuation_removed():
    """'What's New?' -> 'Whats_New'"""

def test_hyphenated_words():
    """'Cross-Tower Isolation' -> 'Cross-Tower_Isolation'"""
```

---

## PART C: Discovery and Loading Code Changes

**Files affected:**
- `src/jig/intent_graph/generator.py`
- `src/jig/validation/intent.py`
- `src/jig/cli/show.py`
- `src/jig/cli/rebuild.py`

### C.1 Glob Patterns (No Change Required)

Current glob patterns continue to work:
```python
spec_dir.glob("S-*.md")       # Matches S-001_Title.md
outcome_dir.glob("O-*.md")    # Matches O-015_Title.md
architecture_dir.glob("A-*.md") # Matches A-001_Title.md
```

**Verification**: Write test confirming glob patterns match new filenames.

### C.2 ID Extraction (No Change Required)

ID is extracted from frontmatter, not filename:
```python
frontmatter = _parse_frontmatter(spec_file)
spec_id = frontmatter["id"]  # "S-001"
```

**Verification**: Confirm no code extracts ID from filename stem.

### C.3 File Path in Graph Nodes

Current graph nodes include `file` field with relative path:
```json
{"id":"S-001","type":"specification","title":"...","file":"jig/specifications/S-001.md"}
```

**After change:**
```json
{"id":"S-001","type":"specification","title":"...","file":"jig/specifications/S-001_Python_Code_Structure_Extraction.md"}
```

**No code changes needed** - file path is derived from actual file on disk.

---

## PART D: Graph Schema Changes

### D.1 Node Schema (Optional Enhancement)

Consider adding `slug` field to nodes for programmatic access to snake_case title:

```json
{
  "id": "S-001",
  "type": "specification",
  "title": "Python Code Structure Extraction",
  "slug": "Python_Code_Structure_Extraction",
  "file": "jig/specifications/S-001_Python_Code_Structure_Extraction.md"
}
```

**Rationale**:
- `slug` is derived from title via `to_snake_case()`
- Useful for generating links, anchors, or cross-references
- Ensures consistency between filename and programmatic identifier

**Decision**: OPTIONAL - implement if graph consumers need it.

### D.2 Metadata Update

No version bump required - this is a policy change, not a schema change.

---

## PART E: Migration of Existing Documents

### E.1 Files Requiring Rename

| Type | Count | Example Before | Example After |
|------|-------|----------------|---------------|
| Specification | 74 | `S-001.md` | `S-001_Python_Code_Structure_Extraction.md` |
| Outcome | 22 | `O-001.md` | `O-001_Discoverable_Implementation_Structure.md` |
| Architecture | 0 | (already compliant) | (no change) |

**Total files to rename:** 96

### E.2 Architecture H1 Update

The single architecture file needs H1 format change:
```markdown
# Before
# A-001: JIG Core Architecture

# After
# JIG Core Architecture
```

### E.3 Migration Script

Create `scripts/migrate_intent_filenames.py`:

```python
"""Migrate intent document filenames to include title.

Usage:
    python scripts/migrate_intent_filenames.py --dry-run  # Preview changes
    python scripts/migrate_intent_filenames.py            # Apply changes
"""
```

**Migration steps per file:**
1. Parse frontmatter to get `id` and `title`
2. Convert title to snake_case
3. Construct new filename: `{id}_{snake_case_title}.md`
4. Rename file (git mv for version control)
5. Update H1 if it contains ID prefix

### E.4 Migration Verification

After migration, run:
```bash
jigy validate
# Should pass with 0 errors

git status
# Should show 96 file renames
```

---

## PART F: Cross-Project Compatibility

### F.1 New Projects

New JIG projects automatically follow the new convention:
- Validation enforces filename format
- Documentation shows correct examples
- `jigy init` scaffolds compliant files

### F.2 Existing Projects

Existing projects using JIG must:
1. Run migration script on their intent documents
2. Ensure `jigy validate` passes
3. Update any external references to old filenames

### F.3 Decorator Behavior (No Change)

Decorators continue to reference by ID only:
```python
@jig.implements("S-001")  # ID only, not filename
@jig.verifies("O-015")    # ID only, not filename
```

**No code changes to decorator handling required.**

---

## PART G: Work Units

### WU-1: Validation Functions

**Scope:**
- Add `to_snake_case()` helper function
- Add `validate_filename_format()` function
- Add `validate_h1_matches_title()` function
- Integrate into existing validation functions

**Files:** `src/jig/validation/intent.py`

**Acceptance Criteria:**
- [ ] `to_snake_case()` converts titles correctly
- [ ] `validate_filename_format()` detects invalid filenames
- [ ] `validate_h1_matches_title()` detects mismatched H1
- [ ] Error messages are clear and actionable

---

### WU-2: Validation Tests

**Scope:**
- Create `test/validation/test_filename_validation.py`
- Test valid and invalid filename patterns
- Test H1 validation
- Test snake_case conversion edge cases

**Files:** `test/validation/test_filename_validation.py`

**Acceptance Criteria:**
- [ ] All test cases pass
- [ ] Edge cases covered (acronyms, punctuation, hyphens)
- [ ] Error messages verified in tests

---

### WU-3: Migration Script

**Scope:**
- Create `scripts/migrate_intent_filenames.py`
- Support `--dry-run` flag
- Use `git mv` for renames
- Handle H1 updates for architecture files

**Files:** `scripts/migrate_intent_filenames.py`

**Acceptance Criteria:**
- [ ] Dry run shows all planned renames
- [ ] Actual run renames files correctly
- [ ] Git history preserved via `git mv`
- [ ] Architecture H1 updated correctly

---

### WU-4: Run Migration on JIG

**Scope:**
- Run migration script on `jig/specifications/` (74 files)
- Run migration script on `jig/outcomes/` (22 files)
- Update `jig/architecture/A-001*.md` H1 format
- Verify `jigy validate` passes

**Acceptance Criteria:**
- [ ] All 96 files renamed
- [ ] All H1 headers match frontmatter titles
- [ ] `jigy validate` passes
- [ ] `jigy rebuild && jigy validate` passes

---

### WU-5: Documentation Update

**Scope:**
- Update any documentation referencing old filenames
- Update examples in README or contributing guides
- Add note about naming convention

**Files:** Documentation files (if any reference specific filenames)

**Acceptance Criteria:**
- [ ] No stale filename references in docs
- [ ] Naming convention documented

---

### WU-6: Agent Context for Title Guidance

**Scope:**
- Add title selection guidance to `CLAUDE.md`
- Add title guidance to Charter "For AI Agents" section
- Create S-092 specification as reference documentation
- Optionally: create `/create-spec` skill with title validation

**Files:**
- `CLAUDE.md`
- `jig/Charter.md`
- `jig/specifications/S-092_Intent_Document_Title_Requirements.md`

**Acceptance Criteria:**
- [ ] `CLAUDE.md` contains title selection guidance (see J.5.1)
- [ ] Charter "For AI Agents" section includes title guidance (see J.5.2)
- [ ] S-092 exists as reference documentation
- [ ] Agent creating new spec sees guidance before creating file

**Rationale:**
Title quality cannot be enforced by deterministic validation (requires semantic judgment).
Guidance must reach agents BEFORE file creation, not after via validation warnings.

---

## PART H: Success Criteria

### H.1 Validation Criteria

1. `jigy validate` reports errors for non-compliant filenames
2. `jigy validate` reports errors for H1/title mismatches
3. Error messages include expected filename format
4. Existing tests continue to pass

### H.2 Migration Criteria

1. All 74 specification files renamed with title
2. All 22 outcome files renamed with title
3. Architecture H1 updated to title-only format
4. Git history shows proper renames (not delete+add)
5. `jigy rebuild && jigy validate` passes

### H.3 Cross-Project Criteria

1. Decorators continue to work with ID references
2. Intent graph generation produces correct `file` paths
3. CLI commands continue to find and display intent documents

### H.4 Agent Context Criteria

1. `CLAUDE.md` contains title selection guidance
2. Charter "For AI Agents" section includes title guidance
3. S-092 specification exists as reference documentation
4. Title quality is NOT checked by `jigy validate` (deterministic only)

---

## PART I: Risks and Mitigations

### I.1 Risk: External References Break

**Risk:** External tools or scripts reference old filenames directly.

**Mitigation:**
- Search codebase for hardcoded filename references before migration
- Grep for patterns like `S-\d{3}\.md` and `O-\d{3}\.md`
- Update any matches before migration

### I.2 Risk: Merge Conflicts During Migration

**Risk:** Open PRs referencing old filenames will conflict.

**Mitigation:**
- Coordinate migration timing with team
- Complete migration in single commit
- Provide instructions for rebasing open PRs

### I.3 Risk: Snake Case Edge Cases

**Risk:** Some titles may produce unexpected snake_case results.

**Mitigation:**
- Test conversion function thoroughly
- Review migration dry-run output
- Allow manual override in migration script if needed

### I.4 Risk: Performance with Many Files

**Risk:** Validation slower with filename checks.

**Mitigation:**
- Filename format check is O(1) per file
- No additional file reads required
- Impact negligible

---

## PART J: Title Selection Guidance

Since titles are now embedded in filenames, title quality directly impacts discoverability and git history cleanliness. This section defines how to choose good titles and when (not) to change them.

### J.1 Principles for Good Titles

**DO:**
| Principle | Rationale |
|-----------|-----------|
| Describe **behavior or capability** | Titles should answer "what does this enable?" |
| Use **noun phrases** | Complete the sentence "This spec defines..." |
| Be **specific enough** to distinguish | Avoid generic titles that could apply to many specs |
| Be **stable** | Choose titles that won't change as implementation evolves |
| Use **domain language** | Prefer problem-space terms over solution-space terms |

**DON'T:**
| Anti-Pattern | Why It's Bad | Example |
|--------------|--------------|---------|
| Version numbers | Temporal, will become stale | `User_Auth_v2` |
| Implementation details | Ties title to solution | `Redis_Cache_Layer` |
| Vague comparatives | Meaningless without context | `Better_Error_Handling` |
| Temporal references | Becomes confusing over time | `New_Login_Flow` |
| Task descriptions | Specs define capabilities, not tasks | `Fix_Session_Bug` |
| Leading articles | Wastes space, adds nothing | `The_User_Model` |

### J.2 Title Examples

| Bad Title | Problem | Good Title |
|-----------|---------|------------|
| `New_Authentication` | "New" is temporal | `User_Authentication` |
| `Fix_Login_Bug` | Task, not capability | `Session_Persistence` |
| `Redis_Cache_Layer` | Implementation-specific | `Response_Caching` |
| `Better_Error_Handling` | Vague comparative | `Structured_Error_Responses` |
| `Update_User_Model_v2` | Version in title | `User_Profile_Schema` |
| `The_Main_Config` | Leading article | `Configuration_Loading` |
| `Misc_Utilities` | Too vague | `String_Sanitization_Helpers` |
| `API_Stuff` | Lazy, uninformative | `REST_Endpoint_Routing` |

### J.3 Title Stability Policy

**Titles are semi-permanent.** Changing a title causes:
- File rename → appears as delete + add in some git tools
- Git history fragmentation for that file
- Broken external references (bookmarks, documentation links, search indexes)
- Potential merge conflicts in open PRs

#### When to Rename (Acceptable)

| Reason | Example |
|--------|---------|
| Original title was **genuinely wrong** | `Cache_Validation` actually defines `Cache_Invalidation` |
| Scope **significantly changed** | Spec expanded from `User_Login` to `User_Authentication` |
| **Consolidating** multiple specs | Merging `Email_Send` and `Email_Queue` into `Email_Delivery` |
| **Splitting** a spec | Breaking `User_Management` into `User_Creation` and `User_Deletion` |

#### When NOT to Rename (Git Noise)

| Reason | Why It's Bad |
|--------|--------------|
| Minor wording preference | "Auth" vs "Authentication" — not worth the churn |
| Making it "sound better" | Subjective improvement ≠ necessary change |
| Matching new style guide | Apply to new specs only; don't retrofit |
| Fixing capitalization | `Cli_Commands` → `CLI_Commands` is noise unless egregious |

### J.4 Validation Scope (Deterministic Only)

Validation (`jigy validate`) checks **structural correctness only**:

| Check | Type | Rationale |
|-------|------|-----------|
| Filename matches `{TYPE}-{NNN}_{Title}.md` | Error | Structural requirement |
| Filename title matches frontmatter title | Error | Consistency requirement |
| H1 matches frontmatter title | Error | Consistency requirement |
| Frontmatter has required fields | Error | Schema requirement |

**Validation does NOT check title quality.** Reasons:

1. **Semantic judgment requires LLM** — regex patterns are brittle and miss most bad titles
2. **Deterministic commands must stay deterministic** — no LLM calls in `jigy validate`
3. **Post-hoc warnings are ineffective** — by the time validation runs, the bad title is in git
4. **False positives annoy users** — `A_Record_Parser` is fine, but `^A_` regex would flag it

Title quality is enforced **before file creation** via agent context, not after via validation.

### J.5 Discoverability: Agent Context (Primary)

Title guidance must reach agents **before** they create files, not after. The primary mechanisms are:

#### 1. CLAUDE.md (Session Start)

Add to project's `CLAUDE.md`:

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

#### 2. Charter "For AI Agents" Section

The Charter already has agent instructions. Add title guidance there:

```markdown
## For AI Agents

### Creating Intent Documents

When creating new specifications, outcomes, or architecture documents,
select titles that describe the CAPABILITY being defined, not the
implementation approach. Titles appear in filenames and are semi-permanent.

Good: "Response Caching", "User Authentication", "Session Persistence"
Bad: "New Cache", "Redis Layer", "Fix Login Bug", "Auth v2"
```

#### 3. Skills (If Available)

If the project has a `/create-spec` or similar skill:

```markdown
# Skill: create-spec

Before creating the file, validate the title:
1. Does it describe a capability (not implementation)?
2. Does it avoid temporal words (New, Old, Updated)?
3. Does it avoid version numbers?
4. Could this title still make sense in 2 years?

If any check fails, suggest a better title before proceeding.
```

#### 4. Hooks (Reminder, Not Enforcement)

A `user-prompt-submit` hook could remind about title guidance when creating intent files, but should not block or validate — that's the agent's job.

### J.6 Discoverability: Documentation (Secondary)

For human reference and edge cases, title guidance also lives in:

#### This SCOPE Document

Sections J.1-J.3 provide comprehensive guidance for humans reviewing or establishing conventions.

#### Specification S-092 (Reference Only)

Create `jig/specifications/S-092_Intent_Document_Title_Requirements.md` as **documentation**, not as something validation enforces:

```yaml
---
id: S-092
type: specification
title: Intent Document Title Requirements
---

# Intent Document Title Requirements

This specification documents title selection guidance. Title quality
is enforced via agent context (CLAUDE.md, Charter, skills), not via
deterministic validation.

## Guidance

1. Title MUST describe behavior or capability, not implementation details
2. Title MUST NOT contain version numbers, dates, or temporal words
3. Title MUST NOT start with articles (The, A, An)
4. Title MUST be specific enough to distinguish from other specs of same type
5. Title SHOULD complete the phrase "This [spec|outcome|architecture] defines..."
6. Title changes SHOULD be avoided unless scope genuinely changed

## Rationale

Title quality requires semantic judgment that deterministic validation
cannot provide. Regex-based pattern matching produces false positives
and misses most actual problems. Agent context ensures guidance reaches
the point of decision (before file creation) rather than after (validation).
```

**Note:** S-092 is not decorated with `@jig.implements` in validation code because validation does not enforce title quality.

### J.7 Title Change Workflow

When a title change is necessary:

1. **Justify** in commit message why the rename is needed
2. **Separate commit** for title-only changes (don't mix with content changes)
3. **Update references** in same commit (documentation, links)
4. **Commit message format:**
   ```
   Rename S-047: Cache_Implementation → Response_Caching

   The original title described implementation (caching mechanism)
   rather than capability (caching responses). Updated to reflect
   what the spec actually defines.
   ```

### J.8 Summary: Where Title Guidance Lives

| Location | When Seen | Purpose |
|----------|-----------|---------|
| `CLAUDE.md` | Session start | Primary agent guidance |
| Charter "For AI Agents" | Reading project context | Reinforcement |
| Skills (`/create-spec`) | Invoking skill | Point-of-use validation |
| S-092 specification | Searching specs | Reference documentation |
| This SCOPE (J.1-J.3) | Process review | Comprehensive guidance |

**Key principle:** Guide agents BEFORE they create files. Don't rely on validation to catch bad titles AFTER they're in git.

---

## References

- C003_SCOPE_Extended-Intent-Hierarchy-and-Towers.md (established Architecture naming pattern)
- Current validation implementation: `src/jig/validation/intent.py`
- Current intent graph generation: `src/jig/intent_graph/generator.py`
