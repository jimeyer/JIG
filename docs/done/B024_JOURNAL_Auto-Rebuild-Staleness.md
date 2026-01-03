# Execution Journal: Auto-Rebuild with Staleness Detection

**PLAN:** docs/wip/B023_PLAN_Auto-Rebuild-Staleness.md
**Started:** 2025-12-22 
**Status:** In Progress

---

## Entries

### Entry 1 | 2025-12-22 | Pre-Execution

```yaml
type: observation
wu: null
```

Starting execution of B023 PLAN. This is an additive feature (no legacy code to delete).
Key constraints:
- FORBIDDEN bricks: B-decorators, B-validation, B-config, B-hashing, B-languages, B-audit
- B-staleness at layer 0, B-cli at layer 1
- No backwards compatibility shims needed

Codebase exploration complete. Understood existing patterns:
- NDJSONWriter has `_meta` block with version, node_count, edge_count, generated timestamp
- CLI commands use Click, pass JigConfig from context
- Graph builders use similar patterns (impl_graph, verification_graph, intent_graph)

Ready to execute WU1: Staleness Detection Module.

---

### Entry 2 | 2025-12-22 | WU1 Complete

```yaml
type: outcome
wu: WU1
spec: S-069
```

**Status:** COMPLETE

**Gates:** 4/4 passed
- ✓ Tests: 17/17 passed (`pytest tests/unit/test_staleness.py`)
- ✓ jigy rebuild && jigy validate: PASS
- ✓ FORBIDDEN bricks: untouched
- ✓ Linting: no new errors

**Files Created/Modified:**
- `src/jig/staleness.py` (new) - staleness detection module
- `tests/unit/test_staleness.py` (new) - 17 unit tests
- `jig/bricks.yaml` - added B-staleness brick at layer 0

**Notable:**
- Bug found in `git_status_porcelain` - `.strip()` on stdout was removing leading spaces from git output format. Fixed by using `.rstrip("\n")` instead.
- Git subprocess calls work reliably; timeout of 5s is adequate.

**Commit:** d460515

---

### Entry 3 | 2025-12-22 | WU2 Complete

```yaml
type: outcome
wu: WU2
spec: S-068
```

**Status:** COMPLETE

**Gates:** 4/4 passed
- ✓ Tests: 8/8 passed (`pytest tests/unit/test_graph_metadata.py`)
- ✓ jigy rebuild && jigy validate: PASS
- ✓ FORBIDDEN bricks: untouched
- ✓ Linting: no new errors

**Files Modified:**
- `src/jig/impl_graph/ndjson_writer.py` - added git_metadata to NDJSONWriter
- `src/jig/impl_graph/builder.py` - pass git_metadata through
- `src/jig/intent_graph/generator.py` - added git_metadata to _generate_metadata
- `src/jig/verification_graph/builder.py` - added git_metadata parameter
- `src/jig/cli/rebuild.py` - collect and pass git_metadata for each graph type
- `tests/unit/test_graph_metadata.py` (new) - 8 unit tests

**Notable:**
- Clean separation: collect_git_metadata() in staleness.py, metadata writing in each builder
- Intent graph includes tree hashes for jig/, jig/outcomes/, jig/specifications/

**Commit:** b224cfc

---

### Entry 4 | 2025-12-22 | WU3 Complete

```yaml
type: outcome
wu: WU3
spec: S-070
```

**Status:** COMPLETE

**Gates:** 4/4 passed
- ✓ Tests: 11/11 passed (`pytest tests/cli/test_auto_rebuild.py`)
- ✓ jigy rebuild && jigy validate: PASS
- ✓ FORBIDDEN bricks: untouched
- ✓ Linting: no new errors

**Files Created/Modified:**
- `src/jig/cli/auto_rebuild.py` (new) - ensure_graphs_current() and helpers
- `src/jig/cli/validate.py` - added auto-rebuild to validate commands
- `src/jig/cli/show.py` - added auto-rebuild to show commands
- `src/jig/cli/audit.py` - added auto-rebuild to coverage command
- `jig/bricks.yaml` - added M-jig.cli.auto_rebuild to B-cli
- `tests/cli/test_auto_rebuild.py` (new) - 11 unit tests

**Notable:**
- Used mocks for testing to avoid full graph rebuilds in tests
- validate_full passes skip_rebuild=True to sub-commands to avoid double rebuild

**Commit:** f85f5c9

---

### Entry 5 | 2025-12-22 | WU4 Complete

```yaml
type: outcome
wu: WU4
spec: S-071
```

**Status:** COMPLETE

**Gates:** 4/4 passed
- ✓ Tests: 10/10 passed (`pytest tests/cli/test_no_rebuild_flag.py`)
- ✓ jigy rebuild && jigy validate: PASS
- ✓ FORBIDDEN bricks: untouched
- ✓ Linting: no new errors

**Files Modified:**
- `src/jig/cli/main.py` - added --no-rebuild global option and get_no_rebuild()
- `tests/cli/test_no_rebuild_flag.py` (new) - 10 unit tests

**Notable:**
- Flag is positioned before subcommand: `jigy --no-rebuild validate`
- All CLI command wrappers updated to pass skip_rebuild parameter

**Commit:** 9e007ef

---

### Entry 6 | 2025-12-22 | WU5 Complete

```yaml
type: outcome
wu: WU5
spec: S-068, S-069, S-070, S-071
```

**Status:** COMPLETE

**Gates:** All passed
- ✓ Integration tests: 12/12 passed (`pytest tests/integration/test_auto_rebuild_e2e.py`)
- ✓ Full test suite: 487/487 passed
- ✓ jigy rebuild && jigy validate: PASS

**Files Created/Modified:**
- `tests/integration/test_auto_rebuild_e2e.py` (new) - 12 integration tests
- `src/jig/cli/auto_rebuild.py` - added error handling for rebuild failures
- `tests/config/test_cli_integration.py` - added bricks.yaml to fixtures
- `tests/audit/test_coverage_integration.py` - added skip_rebuild=True to tests
- `tests/cli/test_validate.py` - added --no-rebuild flag to tests

**SCOPE Validation:**
- ✓ Commands operate on current data without manual rebuild
- ✓ Staleness check is fast (<100ms verified in test)
- ✓ Only affected graphs rebuild when files change
- ✓ --no-rebuild provides escape hatch

**Notable:**
- Some existing tests needed updates to work with auto-rebuild
- Added bricks.yaml to test fixtures where missing
- Used --no-rebuild or skip_rebuild=True in tests that mock graph files

---

## Synthesis

### Patterns
- Git subprocess calls are fast and reliable for staleness detection
- The `collect_git_metadata` / `is_stale` pattern cleanly separates recording and comparison
- Error handling in auto_rebuild prevents rebuild failures from blocking commands

### Friction Summary
- Existing tests required updates when auto-rebuild was introduced
- Need to ensure bricks.yaml exists for intent graph generation

### Suggestions
- Consider adding `--verbose` flag to show staleness check details
- Could cache git state across multiple staleness checks for slight speedup

### Wins
- Clean separation between staleness module (layer 0) and CLI integration (layer 1)
- Minimal invasive changes to existing code - mostly additive
- Performance target (<100ms) easily achieved

