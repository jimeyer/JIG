# PLAN: Auto-Rebuild with Staleness Detection

- **SCOPE**: docs/wip/B021_SCOPE_Auto-Rebuild-Staleness.md
- **JIGPLAN**: docs/wip/B022_JIGPLAN_Auto-Rebuild-Staleness.md
- **Start**: 2025-12-22
- **Status**: Draft
- **Branch**: feature/auto-rebuild-staleness

---

## Constraints from JIGPLAN

**FORBIDDEN Bricks** (do not modify):
- B-decorators (layer 0)
- B-validation (layer 0)
- B-config (layer 0)
- B-hashing (layer 0)
- B-languages (layer 0)
- B-audit (layer 1)

**Layer Constraints:**
- B-staleness at layer 0 (foundation)
- B-cli at layer 1 (may depend on B-staleness)
- No upward dependencies (layer 0 cannot import from layer 1)

**Clean Break:**
- Additive feature, no legacy code to delete
- No backwards compatibility shims needed

---

## Work Unit Checklist

- [ ] WU1: Staleness Detection Module — tests ☐ / code ☐ / docs ☐
- [ ] WU2: Graph Metadata for Staleness — tests ☐ / code ☐ / docs ☐
- [ ] WU3: Auto-Rebuild Integration — tests ☐ / code ☐ / docs ☐
- [ ] WU4: --no-rebuild Flag — tests ☐ / code ☐ / docs ☐
- [ ] WU5: Validation — SCOPE verified ☐

---

## Work Units

### Work Unit 1: Staleness Detection Module

**Goal**: Create staleness detection module with git-based change detection.

**Specs Addressed**: S-069

**Acceptance Criteria**:
- [ ] `is_stale(graph_type: str, config: JigConfig) -> bool` implemented
- [ ] `get_staleness_status(config: JigConfig) -> dict[str, bool]` implemented
- [ ] Git helpers: `git_rev_parse()`, `git_tree_hash()`, `git_status_porcelain()`
- [ ] Returns True when: graph missing, metadata corrupt, HEAD changed with tree changes, dirty files differ
- [ ] Returns False when git state matches recorded metadata
- [ ] Non-git projects: always returns True (graceful degradation)
- [ ] Staleness check for all graphs completes in <100ms
- [ ] Tests with @jig.verifies("S-069") decorators
- [ ] Code with @jig.implements("S-069") decorators
- [ ] Add B-staleness brick to bricks.yaml with M-jig.staleness
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/unit/test_staleness.py -v`
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Git subprocess calls behave unexpectedly
- Performance target (<100ms) not achievable
- FORBIDDEN brick modification needed
- Layer constraint violation detected

**Implementation Notes**:
- Files: `src/jig/staleness.py` (new), `tests/unit/test_staleness.py` (new)
- Add to bricks.yaml: B-staleness with unit M-jig.staleness
- Use subprocess for git calls (git rev-parse HEAD, git ls-tree, git status --porcelain)
- Handle CalledProcessError for non-git directories
- Input directories per graph type:
  - impl: config.paths.source
  - verify: config.paths.tests
  - intent: config.paths.specifications, config.paths.outcomes, config.paths.bricks
- Decorators to add: @jig.implements("S-069") on is_stale(), get_staleness_status()

**Human Verification**:
```bash
pytest tests/unit/test_staleness.py -v
jigy rebuild && jigy validate
```

---

### Work Unit 2: Graph Metadata for Staleness

**Goal**: Extend graph `_meta` blocks to include git state for staleness detection.

**Specs Addressed**: S-068

**Acceptance Criteria**:
- [ ] Implementation graph includes `git_head`, `git_tree_hashes`, `git_dirty_files` in `_meta`
- [ ] Verification graph includes same metadata in `_meta`
- [ ] Intent graph includes same metadata in `_meta`
- [ ] Metadata recorded at generation time using git subprocess calls
- [ ] Non-git projects: metadata fields are null/empty
- [ ] Tests verify metadata presence in generated graphs
- [ ] Tests with @jig.verifies("S-068") decorators
- [ ] Code with @jig.implements("S-068") decorators
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/unit/test_graph_metadata.py -v`
- [ ] jigy rebuild && jigy validate passes
- [ ] Generated graphs contain git metadata in _meta block
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Graph format changes break existing consumers
- FORBIDDEN brick modification needed
- Unclear how to integrate with existing _meta structure

**Implementation Notes**:
- Files to modify:
  - `src/jig/impl_graph/ndjson_writer.py` (B-impl-graph)
  - `src/jig/intent_graph/generator.py` (B-intent-graph)
  - `src/jig/verification_graph/builder.py` (B-verification-graph)
- New test file: `tests/unit/test_graph_metadata.py`
- Reuse git helper functions from staleness.py (import from jig.staleness)
- Each graph builder needs to know its input directories (from config)
- Decorators: @jig.implements("S-068") on metadata writing functions

**Human Verification**:
```bash
pytest tests/unit/test_graph_metadata.py -v
jigy rebuild
grep -A5 '"_meta"' jig/generated/implementation-graph.ndjson | head -20
```

---

### Work Unit 3: Auto-Rebuild Integration

**Goal**: Add automatic rebuild of stale graphs before validate, show, and audit commands.

**Specs Addressed**: S-070

**Acceptance Criteria**:
- [ ] `jigy validate` rebuilds all stale graphs before validating
- [ ] `jigy validate intent` rebuilds stale intent graph only
- [ ] `jigy validate bricks` rebuilds stale impl + intent graphs
- [ ] `jigy show` rebuilds all stale graphs before displaying
- [ ] `jigy show layers` rebuilds stale impl + intent graphs
- [ ] `jigy show bricks` rebuilds stale impl + intent graphs
- [ ] `jigy audit coverage` rebuilds stale impl + verify graphs
- [ ] Output shows "Graphs stale, rebuilding..." when rebuilding
- [ ] Output shows nothing extra when graphs current
- [ ] Tests with @jig.verifies("S-070") decorators
- [ ] Code with @jig.implements("S-070") decorators
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/cli/test_auto_rebuild.py -v`
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Auto-rebuild creates infinite loop
- Performance significantly degraded (>500ms overhead when nothing stale)
- FORBIDDEN brick modification needed
- Layer constraint violation detected

**Implementation Notes**:
- Files to modify:
  - `src/jig/cli/validate.py` (B-cli)
  - `src/jig/cli/show.py` (B-cli)
  - `src/jig/cli/audit.py` (B-cli)
- New test file: `tests/cli/test_auto_rebuild.py`
- Create helper function `ensure_graphs_current(graph_types: list[str], config: JigConfig)`
- Import from jig.staleness for detection
- Import from jig.cli.rebuild for actual rebuild
- Graph type mapping:
  - validate (bare): ["impl", "verify", "intent"]
  - validate intent: ["intent"]
  - validate bricks: ["impl", "intent"]
  - show (bare): ["impl", "verify", "intent"]
  - show layers: ["impl", "intent"]
  - show bricks: ["impl", "intent"]
  - audit coverage: ["impl", "verify"]
- Decorators: @jig.implements("S-070") on ensure_graphs_current and command wrappers

**Human Verification**:
```bash
pytest tests/cli/test_auto_rebuild.py -v
# Test auto-rebuild by modifying a source file and running validate
touch src/jig/__init__.py
jigy validate  # Should show "Graphs stale, rebuilding..."
jigy validate  # Should NOT show rebuilding message
```

---

### Work Unit 4: --no-rebuild Flag

**Goal**: Add global --no-rebuild flag to skip staleness detection.

**Specs Addressed**: S-071

**Acceptance Criteria**:
- [ ] `jigy --no-rebuild validate` skips staleness check
- [ ] `jigy --no-rebuild show` skips staleness check
- [ ] `jigy --no-rebuild audit coverage` skips staleness check
- [ ] Flag is global (before subcommand)
- [ ] No rebuild message shown when flag used
- [ ] Tests with @jig.verifies("S-071") decorators
- [ ] Code with @jig.implements("S-071") decorators
- [ ] jigy rebuild && jigy validate passes

**Success Gates** (all must pass):
- [ ] All tests pass: `pytest tests/cli/test_no_rebuild_flag.py -v`
- [ ] jigy rebuild && jigy validate passes
- [ ] No modifications to FORBIDDEN bricks
- [ ] No new linting/type errors

**Escalation Triggers** (stop and ask human if):
- Test failures persist after 2 retry attempts
- Click/Typer global option pattern unclear
- FORBIDDEN brick modification needed

**Implementation Notes**:
- Files to modify: `src/jig/cli/main.py` (B-cli)
- New test file: `tests/cli/test_no_rebuild_flag.py`
- Use Click callback or context to pass flag to subcommands
- The ensure_graphs_current helper should check this flag
- Decorators: @jig.implements("S-071") on flag handling

**Human Verification**:
```bash
pytest tests/cli/test_no_rebuild_flag.py -v
# Modify source and test --no-rebuild skips check
touch src/jig/__init__.py
jigy --no-rebuild validate  # Should NOT show rebuild message
jigy validate  # Should show rebuild message
```

---

### Work Unit 5: Validation

**Goal**: Verify SCOPE problem is solved at system boundary.

**SCOPE Reference**:
"Currently, users must manually run `jigy rebuild` before other commands to ensure graphs are current. This creates two issues: 1. Stale data: Users forget to rebuild, 2. Wasted time: If we naively auto-rebuild, every command adds ~2 seconds even when nothing changed"

**Validation Approach**: Integration Test (preferred)

**Verification Steps**:
```bash
# Test 1: Nothing changed - should be fast (<200ms)
jigy rebuild  # Ensure current
time jigy validate  # Should complete quickly, no rebuild

# Test 2: Source changed - should auto-rebuild impl only
echo "# comment" >> src/jig/__init__.py
jigy validate  # Should show "impl" rebuilding, not verify/intent
git checkout src/jig/__init__.py

# Test 3: Test file changed - should auto-rebuild verify only
echo "# comment" >> tests/__init__.py
jigy validate  # Should show "verify" rebuilding
git checkout tests/__init__.py

# Test 4: --no-rebuild skips check
echo "# comment" >> src/jig/__init__.py
jigy --no-rebuild validate  # Should NOT rebuild
git checkout src/jig/__init__.py
```

**Expected Result**:
- Commands operate on current data without manual rebuild
- When nothing changed, staleness check < 200ms
- When graphs stale, only affected graphs rebuild
- --no-rebuild flag provides escape hatch

**Deliverable**:
- [ ] Integration test added: `tests/integration/test_auto_rebuild_e2e.py`

**If Validation Fails**:
- Investigate which scenario fails (stale detection, selective rebuild, performance)
- Fix the issue
- Add regression test
- Re-run validation

**Implementation Notes**:
- Test file: `tests/integration/test_auto_rebuild_e2e.py`
- Use pytest fixtures to create temp git repos for testing
- Test scenarios from SCOPE WU5 test cases

**Human Verification**:
```bash
pytest tests/integration/test_auto_rebuild_e2e.py -v
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

## Completion Summary

**Scope Delivered:**
- <to be filled>

**JIG Summary:**
- <to be filled>

**Clean Break Actions:**
- [N/A] No deprecated O/S nodes to delete (additive feature)
- [N/A] No legacy code modules to delete
- [ ] Final jigy rebuild && jigy validate passed

**Reflection Roll-Up:**
- Repeatable wins: <patterns that worked>
- Systemic frictions: <process issues>
- Open questions: <items for future work>

