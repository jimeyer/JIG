---
id: O-JIG-003
type: outcome
title: "JIG is composable (pipes work)"
subsystem: core
created: 2025-11-18
---

# Outcome: Unix Composability

JIG commands follow Unix philosophy: do one thing well, compose via pipes, output structured data.

## Value

Composable tools integrate into existing workflows. Developers can:
- Chain JIG commands with Unix tools
- Process JIG output with jq, grep, awk
- Integrate into CI/CD pipelines
- Build custom workflows without forking JIG

## Success Metrics

- All commands support `--output yaml|json` format option
- Commands exit with meaningful codes (0=success, non-zero=failure)
- Commands accept stdin where appropriate
- No interactive prompts in default mode (use flags for automation)

## Acceptance Criteria

- `jig validate | jq '.errors'` works
- `jig graph --output yaml | yq '.nodes'` works
- Exit codes: 0 (success), 1 (validation errors), 2 (usage errors)
- STDOUT for data, STDERR for diagnostics
- `--quiet` flag suppresses human-friendly output

## Related

- specs: S-JIG-003
- subsystem: core

## History

- 2025-11-18: Created during WU0 bootstrap (known constraint from SCOPE)
