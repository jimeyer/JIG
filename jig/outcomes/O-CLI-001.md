---
id: O-CLI-001
type: outcome
title: Users can safely run jigy init multiple times
subsystem: cli
created: 2025-11-21
---

# O-CLI-001: Users can safely run jigy init multiple times

## Value Proposition

Developers expect `jigy init` to follow standard CLI idioms where initialization commands are idempotent. Running init multiple times should verify the setup rather than error out.

## User Impact

- **Current State**: Running `jigy init` in an initialized directory produces an error, forcing users to manually delete `jig/` directory to reinitialize
- **Desired State**: Running `jigy init` in an initialized directory verifies structure and repairs any missing components
- **Benefit**: Reduces friction, follows principle of least surprise, enables self-healing workflows

## Acceptance Criteria

- [ ] `jigy init` can be run multiple times in the same directory without error
- [ ] Second and subsequent runs verify the JIG structure is complete
- [ ] Users receive clear feedback about what was verified vs repaired
- [ ] Behavior matches standard tools like `git init`, `npm init`, `terraform init`

## Constraints

- Must not overwrite existing user data (config files, node files)
- Must preserve existing `jig.toml` configuration
- Must maintain backwards compatibility with existing JIG projects

## Related Nodes

- Implements: (user need, not derived from other nodes)
- Supports: S-CLI-003, S-CLI-004, S-CLI-005

