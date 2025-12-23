---
id: S-050
title: Graph Schema Hash Fields
type: specification
---

# Graph Schema Hash Fields

Graph nodes include `jig_hash` field for content identity.

**Acceptance Criteria:**
- Specification nodes: `jig_hash` REQUIRED
- Outcome nodes: `jig_hash` REQUIRED
- Brick nodes: `jig_hash` REQUIRED
- Function nodes with `implements`: `jig_hash` REQUIRED
- Test nodes with `verifies`: `jig_hash` REQUIRED
- `git_blob` OPTIONAL on all node types
- Nodes without alignment tracking (no implements/verifies) MAY omit hash fields

**Rationale:** Content identity stored in graph enables change detection by comparing current hashes to audit records.
