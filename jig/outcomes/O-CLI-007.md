---
id: O-CLI-007
type: outcome
title: "CI pipelines use consistent validation strategy"
subsystem: cli
created: 2025-11-22
---

# Outcome: CI pipelines use consistent validation strategy

One command for CI reduces configuration complexity and ensures consistent validation across environments.

## Value

CI pipelines that must run multiple JIG commands to validate graph health create unnecessary complexity:
- **Configuration overhead**: Must remember to run `rebuild`, `status`, AND `validate`
- **Inconsistency risk**: Some pipelines forget `validate` step
- **Maintenance burden**: Three commands to update when flags change
- **Unclear failure points**: Which command failed? What does exit code mean?

A single validation command for CI enables:
- **Simple pipelines**: `jigy index rebuild && jigy status` is complete workflow
- **Consistent enforcement**: Every CI run uses same validation strategy
- **Clear exit codes**: Status exit code determines CI pass/fail
- **Better error messages**: One command output to debug
- **Easier onboarding**: New projects copy simple CI config

## Success Metrics

- All example CI configs use `jigy status` only (not `validate`)
- Zero CI examples in docs show multi-command validation
- <5% of users run both `status` and `validate` in CI
- CI pipeline examples in README show 2-command workflow (rebuild + status)

## Acceptance Criteria

- CI documentation shows single-command validation: `jigy status`
- Status command provides all validation needed for CI gates
- Exit codes support CI requirements:
  - Default: Fail on errors, pass on warnings
  - `--strict`: Fail on errors OR warnings (quality gate)
  - `--warn-only`: Always pass (preview mode)
- Performance suitable for CI: <2s for typical graphs
- Clear error output for CI logs (structured, parseable)

## Related

- implements: S-CLI-022 (Status validates semantics)
- implements: S-CLI-023 (Configurable exit codes)
- related: O-CLI-006 (Single command for graph health)
- subsystem: cli

## History

- 2025-11-22: Created during WU0 (known constraint from S030_PLAN)
