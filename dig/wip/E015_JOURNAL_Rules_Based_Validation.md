---
title: JOURNAL Rules-Based Validation
type: journal
status: active
created: 1737252000
created_human: 2026-01-18 21:00 CST
parent: "[[E014_PLAN_Rules_Based_Validation]]"
children: []
---

# JOURNAL Rules-Based Validation

**PLAN:** dig/wip/E014_PLAN_Rules_Based_Validation.md
**JIGPLAN:** dig/wip/E013_JIGPLAN_Rules_Based_Validation.md
**Started:** 2026-01-18 21:00 CST
**Status:** Complete

---

## Entries

### Entry 1 | 2026-01-18 21:00 | Pre-Execution

```yaml
type: observation
wu: null
```

Beginning PLAN execution. Branch is `rules-validate-mend` (clean).

Initial state:
- `jigy validate` passes (86 specs, 24 outcomes, 13 bricks)
- No `src/jig/rules/` module exists yet
- New specs S-104 through S-109 need to be created (JIGPLAN marked as "(created)" but files don't exist)
- O-029 (Automated Validation Repair) needs to be created

Will create missing O/S nodes before starting WU1, as JIGPLAN phase should have produced these.

---

### Entry 2 | 2026-01-18 21:15 | WU1 Complete

```yaml
type: outcome
wu: WU1
spec: S-108, S-109
```

**Status:** COMPLETE (all 4 gates passed)

Sub-agent successfully created rules infrastructure:
- Rule protocol with code, spec, violations(), fix_for(), apply() methods
- Violation dataclass with stable error ID computation (S-108)
- Fix dataclass with action/target/params/auto/suggestions
- ValidationContext loading specs, outcomes, architecture, charter, bricks
- MendContext with batched change support

**Results:**
- 37 tests pass (21 in test_base.py, 16 in test_context.py)
- jigy validate passes (92 specs, 25 outcomes, 14 bricks)
- B-rules brick added to bricks.yaml (layer 0)
- No FORBIDDEN bricks touched

**Notable:**
- Pre-existing test failure in `test_v2_schema.py::test_charter_node_has_goals_field` unrelated to this work
- Used `@runtime_checkable` on Rule protocol for isinstance() checks
- TYPE_CHECKING guard used to avoid circular imports

**Commit:** 0ed52ee

---

### Entry 3 | 2026-01-18 22:00 | WU2 Complete

```yaml
type: outcome
wu: WU2
spec: S-018, S-019, S-020, S-022, S-035, S-037, S-038, S-039, S-042, S-043, S-072, S-073, S-075, S-076, S-079, S-086, S-087, S-088, S-089, S-095
```

**Status:** COMPLETE (all 4 gates passed)

Sub-agent successfully implemented all 15 rule type classes:

**Field Rules (5):**
- `RequiredFieldRule` - detects missing fields, generates set_field fix
- `IdFormatRule` - validates ID patterns, generates normalized fix when normalizer provided
- `ExcludedFieldRule` - detects forbidden fields, generates delete_field fix
- `FieldTypeRule` - validates field types, generates coercion fix if possible
- `FieldValueRule` - validates field values against predicate

**Sync Rules (2):**
- `FilenameSyncRule` - validates filename matches frontmatter, generates rename_file fix
- `HeaderSyncRule` - validates H1 matches title, generates sync_title fix

**Uniqueness Rule (1):**
- `UniquenessRule` - detects duplicates, no auto-fix (requires manual resolution)

**Reference Rules (2):**
- `ReferenceValidityRule` - validates references exist
- `BidirectionalLinkRule` - validates A<->B consistency, generates add_field_value fix

**Graph Rules (5):**
- `CoverageRule` - validates every item covered
- `PartitionRule` - validates partition property (no gaps, no overlaps)
- `DAGRule` - validates acyclic graph
- `LayerConstraintRule` - validates layer hierarchy
- `IsolationRule` - validates no cross-boundary dependencies (tower isolation)

**Helper Functions:**
- `to_snake_case()` - converts title to snake_case for filename matching
- `normalize_spec_id()`, `normalize_outcome_id()`, `normalize_architecture_id()`, `normalize_goal_id()` - normalizes artifact IDs to canonical form
- `normalize_brick_id()` - normalizes brick IDs to kebab-case

**Results:**
- 37 new tests pass in test_types/test_all_rules.py
- 330 total unit tests pass
- jigy validate passes (92 specs, 25 outcomes, 14 bricks)
- B-rules brick updated with 16 new module units
- No FORBIDDEN bricks touched
- All @jig.implements and @jig.verifies decorators in place

**Notable:**
- Each rule is a @dataclass implementing the Rule protocol
- Filters via Callable allow limiting which artifacts rules apply to
- Graph rules (DAG, Layer, Isolation, Partition) work with mock contexts since they don't need artifact files
- Pre-existing test failure in `test_v2_schema.py::test_charter_node_has_goals_field` confirmed unrelated

---

### Entry 4 | 2026-01-18 22:30 | WU3 Complete

```yaml
type: outcome
wu: WU3
spec: S-105, S-106, S-107 (infrastructure)
```

**Status:** COMPLETE (all 4 gates passed)

Sub-agent successfully implemented mend infrastructure:

**Fix Actions (7):**
- `apply_set_field` - sets frontmatter field value
- `apply_add_field_value` - appends to array field
- `apply_remove_field_value` - removes from array field
- `apply_delete_field` - removes field entirely
- `apply_rename_file` - renames file using shutil.move
- `apply_sync_title` - syncs H1 and frontmatter title
- `apply_set_h1` - sets H1 heading

**YAML Editor:**
- `FrontmatterFile` dataclass for clean manipulation
- `parse_frontmatter_file()` / `write_frontmatter_file()` helpers
- PyYAML-based parsing (accepts minor reformatting)

**Results:**
- 32 tests pass (18 in test_actions.py, 14 in test_yaml_editor.py)
- jigy validate passes (92 specs, 25 outcomes, 15 bricks)
- B-mend brick added (layer 0, depends on B-rules)
- MendContext refactored to use mend actions module
- No FORBIDDEN bricks touched

**Commit:** 8a59f5e

---

### Entry 5 | 2026-01-18 23:00 | WU4 Complete

```yaml
type: outcome
wu: WU4
spec: S-104, S-108, S-109
```

**Status:** COMPLETE (all 4 gates passed)

Sub-agent created validation engine:

**Registry (17 rules):**
- RULES list with all rule instances
- RULES_BY_CODE index for code-based lookup
- RULES_BY_SPEC index for spec-based lookup
- Artifact filters (is_specification, is_outcome, etc.)

**Rule Instances:**
- Spec: required outcomes/title/type, ID format, uniqueness, filename sync, H1 sync
- Outcome: required title/type, ID format, uniqueness, filename sync, H1 sync
- References: spec outcome refs, outcome goal refs
- Bidirectional: spec<->outcome consistency
- Coverage: all specs covered by outcomes

**Engine:**
- `validate(project_root)` runs all rules, returns structured output
- Each error has: id (12-char hex), spec, fix (action template), file, line, message
- Summary: total, auto_fixable, manual counts

**Results:**
- 32 tests pass (17 registry, 15 engine)
- jigy validate passes (92 specs, 25 outcomes, 15 bricks)
- No FORBIDDEN bricks touched

**Notable:**
- CLI wiring deferred to cleanup phase (old validation remains active)
- New engine available via `from jig.validation.engine import validate`
- Enhanced charter loading to support `Charter_*.md` pattern

**Commit:** f599fed

---

### Entry 6 | 2026-01-18 23:30 | WU5 Complete

```yaml
type: outcome
wu: WU5
spec: S-105, S-106, S-107
```

**Status:** COMPLETE (all 5 gates passed)

Sub-agent implemented mend command:

**Mend Engine:**
- `mend_auto()` - applies all fixes where auto=true
- `mend_apply()` - applies fixes from JSON file
- `mend_combined()` - combines both modes
- Fixed-point iteration (max 3) until no new errors

**CLI Command:**
- `jigy mend --auto` - auto-fix mode
- `jigy mend --apply fixes.json` - explicit fix mode
- `--dry-run` - preview without changes
- `-j` - JSON output
- Exit codes: 0=success, 1=partial, 2=error

**Results:**
- 23 tests pass
- jigy validate passes (92 specs, 25 outcomes, 15 bricks)
- No FORBIDDEN bricks touched

**Commit:** fb9a4d5

---

### Entry 7 | 2026-01-18 23:45 | WU6 Complete

```yaml
type: outcome
wu: WU6
spec: S-104, S-105, S-106, S-107, S-108, S-109
escalated: false
```

**Status:** COMPLETE (all 6 gates passed)

Integration tests verify the SCOPE claim: "A rule knows how to detect violations, describe repairs, and execute fixes."

**Tests (13):**
- validate -> mend --auto -> validate cycle converges
- validate -> mend --apply -> validate cycle
- Same rule produces both error and fix (rule unity)
- Mend actually resolves errors
- Error ID stability (S-108)
- Spec traceability (S-109)
- Complete end-to-end workflow

**Fix Applied:**
Changed artifact filters from `a.kind == "specification"` to `a.id.startswith("S-")`.
This enables detection of artifacts with missing type fields.

**Results:**
- 13 integration tests pass
- jigy validate passes
- No FORBIDDEN bricks touched

**Commit:** 539ffeb

---

### Entry 8 | 2026-01-19 00:30 | WU7 Complete

```yaml
type: outcome
wu: WU7
spec: null
escalated: true
```

**Status:** COMPLETE (all gates passed after brick rules added)

**Escalation:** Sub-agent discovered brick rules weren't registered. Human approved adding them before cleanup.

**Changes:**
- Deleted `src/jig/validation/intent.py` and `bricks.py` (clean break)
- Deleted obsolete tests (test_intent.py, test_bricks*.py)
- Wired CLI validate.py to use rules engine
- Added missing rules: BRICK_PARTITION, BRICK_DAG, BRICK_LAYER_CONSTRAINT, TOWER_ISOLATION, TOWER_FORMAT, CHARTER_REQUIRED_GOALS
- Updated A-004 and A-002 architecture docs
- Updated CLI tests for new output format

**Results:**
- 1038 tests pass (1 pre-existing failure unrelated to this work)
- jigy validate passes
- 7489 lines deleted, 866 lines added

**Commit:** 37a2ba6

---

## Synthesis

### Patterns
- TDD approach worked consistently across all WUs
- Sub-agents with clear WU scope and success gates produced reliable results
- Clean break is easier than maintaining compatibility shims
- Rules-based architecture provides better extensibility than procedural functions

### Friction Summary
- WU4 didn't register brick rules (discovered in WU7) - gap in coverage parity verification
- Artifact filters initially used `a.kind` which requires `type` field - fixed to use ID patterns
- Pre-existing test failure (`test_charter_node_has_goals_field`) caused confusion about whether it was related

### Suggestions
- JIGPLAN should explicitly list all rule instances needed, not just rule types
- Integration tests should verify coverage parity between old and new systems before cleanup WU
- Consider adding Charter node to intent graph (addresses pre-existing test failure)

### Wins
- Clean break achieved: 7489 lines of procedural code deleted
- Rules engine extensible: adding new validation is just instantiating rule types
- Mend command works: validate->mend->validate cycle converges
- Architecture docs updated to reflect new model
- All specs S-104 through S-109 implemented and verified
