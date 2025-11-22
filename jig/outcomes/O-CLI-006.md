---
id: O-CLI-006
type: outcome
title: "Developers understand graph health with single command"
subsystem: cli
created: 2025-11-22
---

# Outcome: Developers understand graph health with single command

Status should be the one-stop command for "is my graph ready to commit?"

## Value

Splitting graph health checking across two commands (`jigy status` for metrics, `jigy validate` for semantics) creates cognitive overhead and confusion. Developers must remember to run both commands before committing, leading to:
- **Missed validations**: Forgetting to run validate after status
- **Redundant work**: Running two commands when one should suffice
- **Mental model complexity**: Which command checks what?

A unified status command that shows both metrics AND validation enables:
- **Single command workflow**: `jigy index rebuild` → `jigy status` → commit
- **Complete picture**: See both "what's in the graph" and "is it valid" at once
- **Clear decision point**: Exit code tells you immediately if you can commit
- **Better developer experience**: Less to remember, faster workflow

## Success Metrics

- Developers run `jigy status` and know immediately if they can commit
- <10% of commits have validation errors (down from current rate)
- Zero questions in issues about "do I need to run validate?"
- CI pipelines use single command for health checks

## Acceptance Criteria

- `jigy status` shows both metrics (node counts, subsystem breakdown) and validation results (semantic checks, errors, warnings)
- Exit code reflects validation state: 0 for valid, 1 for errors
- Output clearly separates metrics from validation
- Performance: Combined command completes in <2s (minimal overhead)
- Migration path: Users who run `validate` separately can switch to `status` only

## Related

- implements: S-CLI-022 (Status validates semantics and shows metrics)
- related: O-CLI-007 (Consistent CI validation strategy)
- related: O-CLI-005 (Progressive disclosure)
- subsystem: cli

## History

- 2025-11-22: Created during WU0 (known constraint from S030_PLAN)
