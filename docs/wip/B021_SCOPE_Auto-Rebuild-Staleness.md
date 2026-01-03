# B021: Auto-Rebuild with Staleness Detection

## Summary

Add automatic graph rebuild before `jigy validate`, `jigy show`, and `jigy audit` commands, with fast staleness detection to avoid unnecessary rebuilds.

## Problem

Currently, users must manually run `jigy rebuild` before other commands to ensure graphs are current. This creates two issues:

1. **Stale data**: Users forget to rebuild, then validate/show/audit operate on outdated graphs
2. **Wasted time**: If we naively auto-rebuild, every command adds ~2 seconds even when nothing changed

## Solution

Implement **per-graph staleness detection** using Git status + HEAD SHA. Only rebuild graphs whose source files have changed.

## Approach: Git Status + HEAD SHA

### Per-Graph Detection

Each graph has independent input directories (configurable via `jig.toml`):

| Graph | Config Key | Default | Input Patterns |
|-------|------------|---------|----------------|
| impl | `paths.source` | `src/` | `**/*.py`, `**/*.pyx` |
| verify | `paths.tests` | `test/` | `**/test_*.py`, `**/*_test.py` |
| intent | `paths.specifications` | `jig/specifications/` | `S-*.md` |
| intent | `paths.outcomes` | `jig/outcomes/` | `O-*.md` |
| intent | `paths.bricks` | `jig/bricks.yaml` | single file |

### Staleness Algorithm

For each graph, store in `_meta`:
```json
{
  "_meta": {
    "git_head": "abc123def456",
    "git_tree_hashes": {
      "src/": "aaa111",
      "tests/": "bbb222"
    },
    "git_dirty_files": []
  }
}
```

Check staleness:
```python
def is_stale(graph_type: str, config: JigConfig) -> bool:
    """Return True if graph needs rebuilding."""
    meta = load_graph_meta(graph_type)
    if meta is None:
        return True  # No graph exists

    input_dirs = get_input_dirs(graph_type, config)

    # Check 1: Has HEAD moved?
    current_head = git_rev_parse("HEAD")
    if current_head != meta.get("git_head"):
        # HEAD changed - check if relevant trees changed
        for dir in input_dirs:
            old_tree = meta.get("git_tree_hashes", {}).get(dir)
            new_tree = git_tree_hash(dir)
            if old_tree != new_tree:
                return True

    # Check 2: Any uncommitted changes in input dirs?
    dirty_files = git_status_porcelain(input_dirs)
    if dirty_files != meta.get("git_dirty_files", []):
        return True

    return False
```

### Performance Target

| Scenario | Time |
|----------|------|
| Nothing changed | ~50-100ms (git subprocess calls) |
| One graph stale | ~0.7s (rebuild one graph) |
| All graphs stale | ~2s (full rebuild) |

## Work Units

### WU1: Staleness Detection Module
**File:** `src/jig/staleness.py`

Create module with:
- `is_stale(graph_type: str, config: JigConfig) -> bool`
- `get_staleness_status(config: JigConfig) -> dict[str, bool]`
- Git helper functions: `git_rev_parse()`, `git_tree_hash()`, `git_status_porcelain()`
- Handle non-git projects: always return `True` (always rebuild)

### WU2: Update Graph Metadata
**Files:** `src/jig/impl_graph/ndjson_writer.py`, `src/jig/verification_graph/builder.py`, `src/jig/intent_graph/generator.py`

Extend `_meta` block to include:
- `git_head`: Current HEAD SHA
- `git_tree_hashes`: Dict of input_dir -> tree hash
- `git_dirty_files`: List of uncommitted files in input dirs

### WU3: Add Auto-Rebuild to Commands
**File:** `src/jig/cli/main.py` (or new `src/jig/cli/auto_rebuild.py`)

Create decorator or helper:
```python
def ensure_graphs_current(graph_types: list[str]):
    """Rebuild stale graphs before command execution."""
    ...
```

Apply to:
- `jigy validate` (all graphs)
- `jigy validate intent` (intent graph only)
- `jigy validate bricks` (impl + intent graphs)
- `jigy show` (all graphs)
- `jigy show layers` (impl + intent graphs)
- `jigy show bricks` (impl + intent graphs)
- `jigy audit coverage` (impl + verify graphs)

### WU4: Add `--no-rebuild` Flag
**File:** `src/jig/cli/main.py`

Add global flag to skip auto-rebuild:
```bash
jigy --no-rebuild validate  # Use existing graphs, don't check staleness
```

### WU5: Tests
**File:** `tests/cli/test_staleness.py`

Test cases:
- Fresh project (no graphs) -> rebuilds all
- Nothing changed -> no rebuild
- Source file modified -> only impl rebuilds
- Test file modified -> only verify rebuilds
- Spec file modified -> only intent rebuilds
- New uncommitted file -> detects as dirty
- Non-git project -> always rebuilds

## CLI Output

When auto-rebuild triggers:
```
$ jigy validate
Graphs stale, rebuilding...
  impl: 423 nodes, 671 edges
  verify: up to date
  intent: up to date
Validating...
  ...
```

When nothing changed:
```
$ jigy validate
Validating...
  ...
```

With `--no-rebuild`:
```
$ jigy --no-rebuild validate
Validating...
  ...
```

## Edge Cases

1. **Non-git projects**: Always rebuild (can't detect changes efficiently)
2. **Submodules**: Use tree hash of submodule, not contents
3. **Ignored files**: Git status respects `.gitignore`
4. **Missing graph file**: Always rebuild that graph
5. **Corrupted meta**: Rebuild if meta can't be parsed

## Future Considerations (Out of Scope)

- Incremental rebuild (only re-analyze changed files) - separate effort
- File watcher for continuous rebuild
- Parallel graph rebuilds

## Dependencies

- Existing `jigy rebuild` infrastructure
- Git must be available for optimal performance (graceful degradation without)

## Acceptance Criteria

1. `jigy validate` auto-rebuilds stale graphs before validating
2. `jigy show` auto-rebuilds stale graphs before displaying
3. `jigy audit coverage` auto-rebuilds stale impl+verify graphs
4. When nothing changed, commands complete in <200ms (no rebuild)
5. `--no-rebuild` flag skips staleness check entirely
6. Works with custom paths from `jig.toml`
7. Gracefully handles non-git projects
