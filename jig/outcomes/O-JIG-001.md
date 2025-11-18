---
id: O-JIG-001
type: outcome
title: "JIG tools run in <1 second for most operations"
subsystem: core
created: 2025-11-18
---

# Outcome: Performance - Sub-second Operations

JIG tools should feel as responsive as git commands. Most operations complete in under 1 second.

## Value

Developer flow depends on fast feedback. If tools take seconds to run, they break concentration and discourage frequent use. Git-like speed (<1s for most operations) enables tight iteration loops.

## Success Metrics

- Marker extraction: Process 1000 files in <1 second
- Validation: Check 100 nodes in <1 second
- Graph generation: Build index for 100 nodes in <2 seconds
- Node creation: Create new OSTC node in <200ms

## Acceptance Criteria

- 95% of common operations complete in <1 second
- Performance tests in CI catch regressions
- Performance metrics visible in test output
- No blocking network calls in core operations

## Related

- specs: S-JIG-001
- subsystem: core

## History

- 2025-11-18: Created during WU0 bootstrap (known constraint from SCOPE)
