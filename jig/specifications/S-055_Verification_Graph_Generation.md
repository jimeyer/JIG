---
id: S-055
title: Verification Graph Generation
type: specification
outcomes: [O-018]
---

# Verification Graph Generation

The verification graph is generated as NDJSON from test analysis.

**Output Location:** `jig/generated/verification-graph.ndjson`

**Acceptance Criteria:**
- Output format is NDJSON (one JSON object per line)
- First line is metadata: `{"_meta": {"version": "1.0", "node_count": N, "edge_count": M, ...}}`
- Test nodes (T) sorted alphabetically by ID
- Verifies edges (T→S) sorted by (source, target, type)
- Output is deterministic for same input (reproducible builds)
- Includes all discovered tests, even those without `@jig.verifies`

**Edge Types:**
- `verifies`: T→S edge from `@jig.verifies` decorator

**Not Included:**
- `covers`: T→F edges are recorded in audit-log.ndjson per J023

**Rationale:** NDJSON enables clean git diffs and streaming processing. Determinism enables CI caching and change detection.
