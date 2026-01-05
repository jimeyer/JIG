---
id: S-067
title: Coverage Record Format
type: specification
---

# Coverage Record Format

Coverage audit results are persisted in a grep-able, diff-able record file
that supports staleness detection.

**Acceptance Criteria:**
- Record written to `jig/audits/records/coverage-YYYY-MM-DD.ndjson`
- Each line is a valid JSON object representing one T→F edge
- Edge records contain: edge type, from (test ID + jig_hash), to (function ID + jig_hash), result
- Lines sorted by test ID, then function ID
- Grep for test ID returns all functions that test covers
- Grep for function ID returns all tests that cover that function

**Rationale:** Line-oriented JSON enables standard Unix tools for querying and
comparing coverage across runs. Content hashes enable staleness detection.
