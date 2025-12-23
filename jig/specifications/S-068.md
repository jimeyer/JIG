---
id: S-068
title: Graph Metadata for Staleness Detection
type: specification
---

# Graph Metadata for Staleness Detection

Graph NDJSON files include git state metadata enabling efficient staleness detection.

**Acceptance Criteria:**
- Graph `_meta` block includes `git_head`: current HEAD SHA at build time
- Graph `_meta` block includes `git_tree_hashes`: dict mapping input directories to tree hashes
- Graph `_meta` block includes `git_dirty_files`: list of uncommitted files in input directories
- Metadata recorded during graph generation (impl, verify, intent)
- Non-git projects: metadata fields are null/empty (graceful degradation)

**Input Directory Mapping:**

| Graph | Input Directories (from config) |
|-------|--------------------------------|
| impl | `paths.source` |
| verify | `paths.tests` |
| intent | `paths.specifications`, `paths.outcomes`, `paths.bricks` |

**Example `_meta` Block:**
```json
{
  "_meta": {
    "generated_at": "2025-12-22T10:00:00Z",
    "git_head": "abc123def456789",
    "git_tree_hashes": {
      "src/": "aaa111bbb222"
    },
    "git_dirty_files": []
  }
}
```

**Rationale:** Storing git state at build time enables comparing against current state
to detect staleness without re-analyzing source files.

