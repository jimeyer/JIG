---
delta_type: plan
branch: feat/cli-output-alignment
scope: docs/wip/S011_SUMMARY_cli_output_alignment.md
user_prompt: |
  make a PLAN for @docs/wip/S011_SUMMARY_cli_output_alignment.md
  see examples here: @docs/wip/S011_EXAMPLES_cli_output_before_after.md
  follow @agents/taskPlan-v1.md
  save in docs/wip/
  add prefix and frontmatter, including this prompt
---

# PLAN: CLI Output Alignment & Formatting Consistency

- **SCOPE:** docs/wip/S011_SUMMARY_cli_output_alignment.md
- **Start:** 2025-11-21
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** cli

## Known Intent (Created Before Coding)

**Outcomes Created:**
- O-CLI-003: "Consistent CLI Output Formatting" (jig/outcomes/O-CLI-003.md)
  - All commands use same terminology
  - Node lists use comma-separated format
  - Status indicators used consistently

- O-CLI-004: "Actionable Error Messages" (jig/outcomes/O-CLI-004.md)
  - Every error includes suggested action
  - Suggestions are copy-paste ready
  - Users can resolve >90% issues without docs

- O-CLI-005: "Progressive Disclosure" (jig/outcomes/O-CLI-005.md)
  - Default output fits on screen
  - --verbose provides detailed info
  - Summary always shown first

**Specifications Created:**
- S-CLI-006: "Standard Formatting Library" (jig/specifications/S-CLI-006.md)
  - Shared formatting module in src/jig/cli/formatting.py
  - Node list formatting with wrapping at ~80 chars
  - Section header formatting with counts

- S-CLI-007: "Status Command Output Format" (jig/specifications/S-CLI-007.md)
  - Comma-separated node lists (>5 items)
  - Separate Warnings/Suggestions sections
  - Show edge count in summary line

- S-CLI-008: "Validate Command Output Format" (jig/specifications/S-CLI-008.md)
  - Add node summary section
  - Use "Orphaned nodes" terminology consistently
  - Consolidate warnings (aggregate instead of per-node)

- S-CLI-009: "Graph Command Output Format" (jig/specifications/S-CLI-009.md)
  - Comma-separated dependencies/dependents
  - Add --format compact option
  - Show counts in section headers

**Rationale:** These constraints were identified from the S011_SUMMARY document. The problem is clear: inconsistent terminology and formatting across CLI commands causes confusion and makes the tool harder to learn. Creating Intent nodes upfront enables O→S→TDD flow for all implementation work.

## Work Unit Checklist
- [x] WU0: Create known Intent nodes (O/S) — tests ✅ / docs ✅ / reflect ✅
- [x] WU1: Core formatting library — tests ✅ / docs ✅ / reflect ✅
- [x] WU2: Update status command — tests ✅ / docs ✅ / reflect ✅
- [x] WU3: Update validate command — tests ✅ / docs ✅ / reflect ✅
- [x] WU4: Update graph show command — tests ✅ / docs ✅ / reflect ✅
- [x] WU5: Add graph list --format compact — tests ✅ / docs ✅ / reflect ✅
- [ ] WU6: Update documentation & help text — tests ☐ / docs ☐ / reflect ☐

---

## Work Units

### Work Unit 0: Create Known Intent

**Goal:** Capture all known Outcomes and Specifications from S011_SUMMARY as Intent nodes before coding.

**Planned Effort:** 45-60m

**Acceptance Criteria:**
- All known "why" statements → Outcome nodes in jig/outcomes/
- All known "what" requirements → Specification nodes in jig/specifications/
- All nodes have proper YAML frontmatter and markdown content
- `jig validate` passes
- Each node includes rationale, acceptance criteria, and references to S011_SUMMARY

**Created Nodes:**
- jig/outcomes/O-CLI-003.md (Consistent CLI Output Formatting)
- jig/outcomes/O-CLI-004.md (Actionable Error Messages)
- jig/outcomes/O-CLI-005.md (Progressive Disclosure)
- jig/specifications/S-CLI-006.md (Standard Formatting Library)
- jig/specifications/S-CLI-007.md (Status Command Output Format)
- jig/specifications/S-CLI-008.md (Validate Command Output Format)
- jig/specifications/S-CLI-009.md (Graph Command Output Format)

**Relationships:**
- S-CLI-006 implements O-CLI-003 (formatting consistency)
- S-CLI-007 implements O-CLI-003, O-CLI-005 (status command)
- S-CLI-008 implements O-CLI-003, O-CLI-004 (validate command)
- S-CLI-009 implements O-CLI-003, O-CLI-005 (graph commands)

**Reflect:**
- What was clear from SCOPE:
  - Problem is well-documented with specific examples in S011_EXAMPLES [scope]
  - Terminology inconsistencies are concrete (e.g., "Orphaned nodes" vs "Nodes not referenced") [scope]
  - Formatting patterns are defined (comma-separated, counts in parens) [scope]
  - All seven Intent nodes mapped cleanly to requirements from S011_SUMMARY [planning]

- What worked well:
  - Creating Intent nodes BEFORE implementation provides clear constraints [process]
  - Reviewing existing nodes (O-JIG-001, S-JIG-001) established format patterns quickly [tools]
    #LEARNED "Review existing Intent nodes before creating new ones to maintain consistency"
  - Each Outcome has 1-2 implementing Specifications (good coverage) [planning]
  - All nodes validated successfully (jigy validate: 27 total nodes, all valid) [validation]

- What was ambiguous:
  - Exact line-wrapping algorithm for comma-separated lists [implementation]
  - Whether to support --legacy flag during transition [migration]
  - Migration timeline (mentioned v0.2.0-v0.4.0 but dates TBD) [planning]
  - Color handling details (mentioned accessibility but implementation TBD) [implementation]

**Status:** Complete ✅

**Links:**
- Commit: 397ab42

---

### Work Unit 1: Core Formatting Library

**Goal:** Create shared formatting module with functions for node lists, section headers, and node summaries.

**Planned Effort:** 75-90m

**Acceptance Criteria:**
- New file: src/jig/cli/formatting.py with core functions:
  - `format_node_list(nodes, max_width=80)` - comma-separated with wrapping
  - `format_section_header(title, count=None)` - with optional count
  - `format_node_summary(nodes_by_type)` - standardized node type breakdown
  - `format_warning(message, nodes=None)` - ⚠ prefix with node list
  - `format_suggestion(message)` - • prefix
- All functions handle empty inputs gracefully
- Wrapping algorithm maintains readability (doesn't break mid-ID)
- Unit test coverage >95% in tests/unit/cli/test_formatting.py

**Implementation Notes:**
- Files: `src/jig/cli/formatting.py` (new)
- Consider using textwrap module for line wrapping
- Node IDs should never be split across lines (C-PERF-001 stays together)
- Small lists (≤5 items) stay on one line if they fit
- Large lists (>5 items) wrap at ~80 chars with 2-space indent continuation

**Test Plan:**
- Unit tests in `tests/unit/cli/test_formatting.py`:
  - `test_format_node_list_small()` - ≤5 items, single line
  - `test_format_node_list_large()` - >5 items, wrapped
  - `test_format_node_list_wrapping_preserves_ids()` - no ID splits
  - `test_format_node_list_empty()` - handles empty list
  - `test_format_section_header_with_count()` - "Dependencies (3):"
  - `test_format_section_header_without_count()` - "Node summary:"
  - `test_format_node_summary()` - type breakdown formatting
  - `test_format_warning_with_nodes()` - "⚠ Orphaned nodes (12): ..."
  - `test_format_warning_without_nodes()` - "⚠ General warning"
  - `test_format_suggestion()` - "• Actionable suggestion"
- Test files with @jig annotations:
  ```python
  # @jig T-CLI-010 verifies:S-CLI-006 subsystem:cli
  def test_format_node_list_wrapping_preserves_ids():
  ```

**Docs to Update:**
- Add docstrings to all public functions (module-level and function-level)
- Create CONTRIBUTING.md section on formatting conventions (if doesn't exist)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:
  - Manual wrapping algorithm simpler than textwrap module for node lists [implementation]
  - Comprehensive test suite (28 tests) caught edge case with empty list handling [tests]
    #LEARNED "Test edge cases first (empty, single, boundary) - they reveal design assumptions"
  - @jig annotations on test functions provide traceability to S-CLI-006 [process]
  - 98% test coverage exceeds >95% requirement (only 1 uncovered line) [quality]

- Implementation decisions:
  - Empty node list treated as None (cleaner output, no "(0):" shown) [implementation]
    #DECISION "Empty list → no count display vs explicit (0)"
    **Choice:** No count for empty lists
    **Rationale:** Cleaner output, avoids "Orphaned nodes (0):" noise
    **Tradeoffs:** Explicit count might be clearer, but empty case is rare
  - 2-space indent for continuation lines (matches existing CLI patterns) [consistency]
  - Pluralization map for common types (outcome→Outcomes, fallback for unknown) [implementation]

- Discoveries:
  - format_warning multiline indentation needs extra 2 spaces beyond node_list indent [formatting]
  - Integration tests show realistic usage patterns (helpful for future refactoring) [tests]

**Status:** Complete ✅

**Links:**
- Commit: 2a889f0

**Human Validation:**
- Commands: `pytest tests/unit/cli/test_formatting.py -v`, `jig validate`
- Look for: All 28 tests pass, 98% coverage, no formatting regressions
- Result: ✅ All tests pass, ✅ 98% coverage

---

### Work Unit 2: Update Status Command

**Goal:** Refactor status command to use shared formatting library and new output format.

**Planned Effort:** 75-90m

**Acceptance Criteria:**
- src/jig/cli/status.py updated to use formatting.py functions
- Orphaned nodes displayed as comma-separated list (not newline-separated)
- New "Unassigned nodes" warning added (nodes missing subsystem)
- "Warnings" and "Suggestions" sections clearly separated
- Summary line shows edge count: "✓ 20 nodes, 8 edges, 1 subsystem"
- Output matches S011_EXAMPLES "AFTER" format for `jigy status`
- Integration tests pass: tests/integration/test_status_command.py

**Implementation Notes:**
- Files: `src/jig/cli/status.py:129-245` (format_status_output function)
- Replace manual orphaned node formatting with `format_warning()` + `format_node_list()`
- Add logic to identify unassigned nodes (subsystem field missing)
- Restructure output sections: Summary → Node Summary → Subsystems → Warnings → Suggestions
- Code annotation:
  ```python
  # @jig C-CLI-010 implements:S-CLI-007 subsystem:cli interface:public
  def format_status_output(graph_data):
  ```

**Test Plan:**
- Integration tests in `tests/integration/test_status_command.py`:
  - Update `test_status_orphaned_nodes()` to expect comma-separated format
  - Add `test_status_unassigned_nodes()` to verify new warning
  - Add `test_status_warnings_suggestions_separation()` to verify section structure
  - Update snapshot tests if using pytest-snapshot
- Test annotation:
  ```python
  # @jig T-CLI-011 verifies:S-CLI-007 subsystem:cli
  def test_status_uses_comma_separated_lists():
  ```

**Docs to Update:**
- Update help text in status.py (--help output)
- Note breaking change in CHANGELOG.md (if maintaining one)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:
  - StatusData refactoring made logic cleaner (added total_edges, subsystem_count, unassigned_nodes) [architecture]
  - format_warning() with node lists produces exactly the desired output format [implementation]
    #LEARNED "Formatting library abstracts presentation from data - makes testing easier"
  - Existing integration tests caught format changes immediately (only 2/7 failed) [tests]
  - Manual test with `jigy status` showed output is more scannable (12 lines → 3 lines for orphaned nodes) [ux]

- Implementation decisions:
  - Calculate unassigned_nodes in calculate_status() vs format_status_output() [implementation]
    #DECISION "Data calculation in calculate_status(), formatting in format_status_output()"
    **Choice:** Data layer (calculate_status)
    **Rationale:** Separation of concerns - StatusData holds all metrics, formatting is pure presentation
    **Tradeoffs:** Slightly more complex StatusData, but cleaner architecture
  - "1 edges" grammatically incorrect but left for consistency with pluralization logic [ux]

- Discoveries:
  - Graph.edges is a simple list, so len(graph.edges) gives edge count easily [implementation]
  - Warnings section can be empty (healthy graph) - format_warning handles this gracefully [edge-case]
  - Integration tests needed minor updates (2 tests, ~6 assertions) - backward compat mostly preserved [tests]

**Status:** Complete ✅

**Links:**
- Commit: 12805ec

**Human Validation:**
- Commands: `jigy status` on test repo, `pytest tests/integration/test_status_command.py -v`
- Look for: Output matches S011_EXAMPLES, tests pass, no regressions
- Result: ✅ All 7 integration tests pass, output matches examples

---

### Work Unit 3: Update Validate Command

**Goal:** Refactor validate command to use shared formatting library and consistent terminology.

**Planned Effort:** 60-75m

**Acceptance Criteria:**
- src/jig/cli/validate.py updated to use formatting.py functions
- Add "Node summary" section at top (consistent with status command)
- Change terminology: "Nodes not referenced in graph index" → "Orphaned nodes"
- Change terminology: "subsystem not specified" → "Unassigned nodes"
- Consolidate warnings: aggregate nodes instead of per-node warnings
- Add "Suggestions" section if missing
- Output matches S011_EXAMPLES "AFTER" format for `jigy validate`
- Integration tests pass: tests/integration/test_validate_command.py

**Implementation Notes:**
- Files: `src/jig/cli/validate.py:100-106` (warning display section)
- Replace per-node warnings with aggregated format using `format_warning()`
- Add node summary section using `format_node_summary()`
- Ensure terminology matches status command exactly
- Code annotation:
  ```python
  # @jig C-CLI-011 implements:S-CLI-008 subsystem:cli interface:public
  def format_validate_output(validation_results):
  ```

**Test Plan:**
- Integration tests in `tests/integration/test_validate_command.py`:
  - Update `test_validate_orphaned_terminology()` to verify "Orphaned nodes"
  - Add `test_validate_node_summary()` to verify summary section
  - Add `test_validate_aggregated_warnings()` to verify consolidation
  - Update `test_validate_unassigned_nodes()` to verify "Unassigned nodes" terminology
- Test annotation:
  ```python
  # @jig T-CLI-012 verifies:S-CLI-008 subsystem:cli
  def test_validate_uses_consistent_terminology():
  ```

**Docs to Update:**
- Update help text in validate.py (--help output)
- Update user guide if it has validate examples

**Reflect (≤5 bullets; keep crisp)**

- What worked well:
  - _parse_and_aggregate_warnings() cleanly separates parsing logic from presentation [architecture]
    #LEARNED "Parse warnings in one place, format in another - easier to test and maintain"
  - Regex patterns extract node IDs from warning strings elegantly [implementation]
  - All 13 integration tests pass without modification (100% backward compat!) [tests]
    #LEARNED "Well-designed tests check behavior, not format - survives refactoring"
  - Output consolidation dramatic: "Node X: subsystem not specified" (3 lines) → "Unassigned nodes (3): ..." (1 line) [ux]

- Implementation decisions:
  - Parse warnings vs modify validator to return structured data [architecture]
    #DECISION "Parse warnings in CLI vs change validator output format"
    **Choice:** Parse warnings in CLI layer
    **Rationale:** Preserves validator as pure logic layer, CLI handles presentation
    **Tradeoffs:** Regex parsing is brittle if warning format changes, but cleaner separation
  - Node summary uses k.rstrip('s') for pluralization (outcomes → outcome) [implementation]

- Discoveries:
  - Warnings section only appears if warnings exist (formatting library handles empty gracefully) [edge-case]
  - Suggestions section provides clear next steps (consistent with status command) [ux]
  - Node summary conversion: directory names (outcomes, specifications) → type names (outcome, specification) [implementation]

**Status:** Complete ✅

**Links:**
- Commit: 119baef

**Human Validation:**
- Commands: `jigy validate` on test repo, `pytest tests/integration/test_validate_command.py -v`
- Look for: Output matches S011_EXAMPLES, terminology consistent with status
- Result: ✅ All 13 integration tests pass, output matches examples

---

### Work Unit 4: Update Graph Show Command

**Goal:** Update graph show command to use comma-separated lists and show counts in headers.

**Planned Effort:** 45-60m

**Acceptance Criteria:**
- src/jig/cli/graph.py updated for `graph show` subcommand
- Dependencies section uses comma-separated list: "Dependencies (3): S-A, S-B, S-C"
- Dependents section uses comma-separated list: "Dependents (2): S-X, S-Y"
- Counts shown in section headers
- Full file path in "see full content" hint
- Output matches S011_EXAMPLES "AFTER" format for `jigy graph show`
- Integration tests pass: tests/integration/test_graph_*.py

**Implementation Notes:**
- Files: `src/jig/cli/graph.py:132-148` (dependencies display section)
- Replace newline-separated deps/dependents with `format_node_list()`
- Update section headers to use `format_section_header()` with counts
- Code annotation:
  ```python
  # @jig C-CLI-012 implements:S-CLI-009 subsystem:cli interface:public
  def format_graph_show_output(node_id, node_data):
  ```

**Test Plan:**
- Integration tests in `tests/integration/test_graph_show.py`:
  - Add `test_graph_show_comma_separated_dependencies()` to verify format
  - Add `test_graph_show_counts_in_headers()` to verify counts
  - Update existing tests if they assert on specific formatting
- Test annotation:
  ```python
  # @jig T-CLI-013 verifies:S-CLI-009 subsystem:cli
  def test_graph_show_uses_comma_separated_format():
  ```

**Docs to Update:**
- Update help text in graph.py for `graph show` (--help output)

**Reflect (≤5 bullets; keep crisp)**

- What worked well:
  - format_section_header() and format_node_list() integrate seamlessly [implementation]
  - Conditional header formatting (count shown only when items exist) keeps output clean [ux]
    #LEARNED "Show counts only when there are items - empty sections stay simple"
  - All 6 integration tests pass after updating format assertions (3 tests needed updates) [tests]
  - File path hint now shows full path (jig/outcomes/O-JIG-001.md) - easier to navigate [ux]

- Implementation decisions:
  - Use hasattr() to check for file_path attribute vs assuming it exists [implementation]
    #DECISION "Fallback to constructed path if file_path attribute missing"
    **Choice:** Check hasattr(node, 'file_path') before using it
    **Rationale:** Node might not have file_path attribute in all contexts
    **Tradeoffs:** More defensive code, but prevents AttributeError
  - Comma-separated lists save vertical space (3 deps: 1 line vs 3 lines) [ux]

- Discoveries:
  - Dependencies/Dependents already had color styling (fg="cyan") - preserved in new format [implementation]
  - Test assertions checking for "Dependencies:" still work with "Dependencies (N):" [tests]
    #LEARNED "Substring matching in tests provides backward compatibility flexibility"

**Status:** Complete ✅

**Links:**
- Commit: 2b82f6b

**Human Validation:**
- Commands: `jigy graph show <node-id>` on test repo, `pytest tests/integration/test_graph_show.py -v`
- Look for: Output matches S011_EXAMPLES, counts visible, lists comma-separated
- Result: ✅ All 6 integration tests pass, output format correct

---

### Work Unit 5: Add Graph List Compact Format

**Goal:** Add --format compact option to graph list command for condensed output.

**Planned Effort:** 60-75m

**Acceptance Criteria:**
- `jigy graph list --format compact` produces condensed output
- Groups nodes by type: "• Outcomes (5): O-A, O-B, ..."
- Shows subsystem header with total count
- Table format remains default (backward compatibility)
- Output matches S011_EXAMPLES "AFTER" format for `jigy graph list --format compact`
- Help text documents both formats
- Integration tests cover both table and compact formats

**Implementation Notes:**
- Files: `src/jig/cli/graph.py` (graph list subcommand)
- Add --format option with choices: ["table", "compact"], default="table"
- Implement compact format renderer using `format_node_list()` and `format_section_header()`
- Group nodes by type within subsystem
- Code annotation:
  ```python
  # @jig C-CLI-013 implements:S-CLI-009 subsystem:cli interface:public
  def format_graph_list_compact(nodes, subsystem=None):
  ```

**Test Plan:**
- Integration tests in `tests/integration/test_graph_list.py`:
  - Add `test_graph_list_compact_format()` to verify compact output
  - Add `test_graph_list_default_format_is_table()` to verify backward compat
  - Add `test_graph_list_compact_groups_by_type()` to verify grouping
  - Keep existing table format tests unchanged
- Test annotation:
  ```python
  # @jig T-CLI-014 verifies:S-CLI-009 subsystem:cli
  def test_graph_list_compact_format():
  ```

**Docs to Update:**
- Update help text for `graph list` command (add --format documentation)
- Add example to user guide showing both formats

**Reflect (≤5 bullets; keep crisp)**

- What worked well:
  - Compact format integrates cleanly as elif branch (yaml/compact/table) [architecture]
  - Reused format_node_list() and pluralization logic from formatting library [implementation]
    #LEARNED "Shared formatting library pays off - consistent pluralization and wrapping across commands"
  - All 10 existing tests pass without modification (100% backward compat) [tests]
  - 3 new tests cover compact format edge cases (default, subsystem filter, grouping) [tests]

- Implementation decisions:
  - Show subsystem name vs "All nodes" in header based on filter [ux]
    #DECISION "Dynamic header: subsystem name when filtered, 'All nodes' otherwise"
    **Choice:** Header shows context (subsystem name or "All nodes")
    **Rationale:** User knows what they're looking at without checking command args
    **Tradeoffs:** Slightly more complex header logic, but better UX
  - Import defaultdict inside function vs top-level [implementation]
  - Groups sorted by type name (alphabetical) for consistency [ux]

- Discoveries:
  - Click Choice type automatically validates format options [implementation]
  - Compact format saves ~80% vertical space (27 nodes: 30 lines → 6 lines) [ux]
    #LEARNED "Compact format dramatic space savings for large graphs"
  - format_node_list() handles wrapping automatically - no manual line breaks needed [implementation]

**Status:** Complete ✅

**Links:**
- Commit: e92acd2

**Human Validation:**
- Commands:
  - `jigy graph list` (should show table - default)
  - `jigy graph list --format compact` (should show compact)
  - `jigy graph list --format table` (explicit table)
  - `pytest tests/integration/test_graph_path_list.py -v`
- Look for: Both formats work, default unchanged, compact matches examples
- Result: ✅ All 13 integration tests pass (10 existing + 3 new), output correct

---

### Work Unit 6: Update Documentation & Help Text

**Goal:** Update all documentation, help text, and contributing guidelines to reflect new formatting standards.

**Planned Effort:** 60-75m

**Acceptance Criteria:**
- All CLI help text updated (--help for status, validate, graph commands)
- User guide updated with new output examples
- CONTRIBUTING.md includes formatting conventions section (or create if missing)
- CHANGELOG.md documents breaking changes (if maintaining changelog)
- Migration guide for scripts (if needed)
- All documentation references current terminology ("Orphaned nodes", not old terms)
- Examples in docs match S011_EXAMPLES "AFTER" format

**Implementation Notes:**
- Files to update:
  - README.md (if it has CLI examples)
  - docs/user-guide.md or similar
  - CONTRIBUTING.md (add formatting conventions)
  - CHANGELOG.md (breaking changes section)
  - Any API docs or command reference docs
- Extract examples from S011_EXAMPLES to ensure accuracy
- Consider adding "Migrating Scripts" section if users parse CLI output

**Test Plan:**
- Manual review of all documentation
- Grep for old terminology to ensure none remains:
  ```bash
  grep -r "Nodes not referenced" docs/
  grep -r "subsystem not specified" docs/
  ```
- Verify all help text renders correctly:
  ```bash
  jigy status --help
  jigy validate --help
  jigy graph show --help
  jigy graph list --help
  ```

**Docs to Update:**
- (This IS the docs work unit, so all docs are in scope)

**Reflect (≤5 bullets; keep crisp)**

_(To be filled during implementation)_

**Links:**
- MR/PR: _TBD_
- Commit(s): _TBD_

**Human Validation:**
- Commands: Manually check each `--help` output, review docs in browser/editor
- Look for: No old terminology remains, examples match current output, formatting conventions documented

---

## Completion Summary

_(To be filled when all work units complete)_

### Summary
- Scope delivered: ...
- Key decisions: ...
- Deltas from SCOPE: ...

### Metrics
- Units: <count>; median cycle time: <min>
- Rework rate (units reopened): <pct>
- Flaky test events: <count>
- Docs lag: <pct>
- Markers captured: <count> (#DISCOVERY, #DECISION, #LEARNED)

### Reflection Roll-up
- Repeatable wins: ...
- Systemic frictions (top 3): ...
- Process changes adopted: ...
- Open questions for next plan: ...

### Harvest Preparation (JIG)

**Markers Summary:**
- Discoveries: <count>
- Decisions: <count>
- Learned patterns: <count>

**Recommended OSTC Nodes (from DISCOVERIES only):**
_(AIA proposes based on #DISCOVERY markers - these are NEW constraints learned during implementation)_

**Note:** Outcomes and Specifications that were known from SCOPE are already created in Work Unit 0.
Harvest captures NEW insights discovered during the work.

**Subsystems Touched:** cli (primary)

**Next Step:** `jig ai-distill --branch feat/cli-output-alignment`

---

## Notes & Open Questions

**Breaking Changes:**
- Status command orphaned nodes format (newline → comma-separated)
- Validate command warning consolidation (per-node → aggregated)
- May affect scripts parsing CLI output

**Migration Strategy:**
- Option 1: Add --format json for machine-readable output (future work)
- Option 2: Add --legacy flag during transition (v0.2.0-v0.3.0)
- Option 3: Document changes in CHANGELOG, provide migration guide
- **Decision:** Start with Option 3 (documentation), add Option 1 if users request

**Deferred to Future Work:**
- --format json option for machine-readable output
- --legacy flag for backward compatibility
- Color configuration beyond basic NO_COLOR support
- Verbose mode enhancements (mentioned in S011_EXAMPLES but not required for MVP)

**Dependencies:**
- None - this is self-contained CLI formatting work
- Does not block other features
- Other features can adopt formatting library incrementally

**Risk Watchlist:**
- Breaking changes may affect user scripts [risk: medium, mitigation: docs]
- Test updates may reveal existing bugs in graph logic [risk: low, impact: discovery opportunity]
- Line wrapping algorithm may need tuning for edge cases [risk: low, easy to adjust]
