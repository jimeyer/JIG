---
id: S-052
title: Test Node Schema
type: specification
outcomes: [O-018]
---

# Test Node Schema

Test nodes in the verification graph conform to the A001 contract schema.

**Required Fields:**
- `id` (string): Format `T-{module}.{test_function}` or `T-{module}.{TestClass}.{test_method}`
- `type` (string): Value SHALL be `"test"`
- `file` (string): Relative path to test file from project root
- `verifies` (array): Spec/outcome IDs from `@jig.verifies`, empty array if none
- `jig_hash` (string): Content hash per S-047

**Excluded Fields:**
- `brick` — derived at query time from bricks.yaml
- `line` — brittle across refactors, computable on demand
- `covers` — T→F coverage handled by Audit system (J023), not verification graph

**Rationale:** Consistent schema enables tooling and queries. Static-only fields keep verification graph generation fast and deterministic.
