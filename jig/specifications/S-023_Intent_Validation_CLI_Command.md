---
id: S-023
title: Intent Validation CLI Command
type: specification
---

# Intent Validation CLI Command

Provide `jigy validate intent` command to validate specifications, outcomes, and decorators WITHOUT requiring graphs.

**Acceptance Criteria**:
- Command `jigy validate intent` runs all Phase 1 validators
- Validates specification files (S-018)
- Validates outcome files (S-019)
- Validates decorator references (S-020)
- Runs without requiring any graph files to exist
- Exit code 0 on success, 1 on validation failures, 2 on errors
- Output grouped by validation phase (specs, outcomes, decorators)
- Shows count of files/items validated per phase
- Support granular subcommands: `jigy validate intent specs`, `jigy validate intent outcomes`, `jigy validate intent decorators`

**Rationale**: Intent validation can run early in development before any graphs exist. Enables fail-fast workflow.

**References**: AG026 §2.1 (Phase 1: Validate Intent)
