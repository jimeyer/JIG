---
id: S-049
title: Git Blob Optimization
type: specification
outcomes: [O-017]
---

# Git Blob Optimization

JIG optionally uses git blob hashes to skip recomputing content hashes for unchanged files.

**Acceptance Criteria:**
- `git_blob` field is optional on all graph nodes
- If file's git blob hash unchanged since last rebuild, content hash reused
- Non-git environments omit `git_blob` field entirely
- All JIG functionality works correctly without `git_blob`
- Git blob hash truncated to 12 hex chars for consistency

**Rationale:** Performance optimization. Git already hashes every file; if blob unchanged, file bytes are identical, so content hash is also unchanged.
