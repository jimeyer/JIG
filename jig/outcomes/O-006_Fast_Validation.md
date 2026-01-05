---
id: O-006
title: Fast Validation
type: outcome
theme: [Validation]
supports_goals: [G-003]
specifies: [S-023, S-024, S-025]
---

# Fast Validation

**Value:** Full project validation completes in under 5 seconds, making it practical to run frequently during development.

**Acceptance:** `jigy validate` completes in <5 seconds for projects with up to 100 specs and 10K LOC.

## AI Agent Benefit

Agents can validate after every change without significant latency cost. Fast validation enables tight feedback loops - agents write, validate, fix, repeat without waiting. Slow validation forces agents to batch changes, increasing error accumulation and debugging complexity.

## Rationale

Validation that's slow is validation that's skipped. A 30-second validation discourages frequent use - developers batch changes and validate less often. Errors accumulate, and when validation finally runs, the developer faces multiple issues with forgotten context.

Fast validation inverts this dynamic. A 2-second validation can run after every save, in pre-commit hooks, and in watch mode. Errors surface immediately while context is fresh. The cost of validation is negligible compared to the cost of delayed error discovery.

Performance comes from smart architecture: validate intent artifacts (specs, outcomes, bricks) without full graph generation. YAML and markdown parsing is fast; the expensive graph building only runs when explicitly requested via `jigy rebuild`.

For CI pipelines, fast validation means short feedback loops. A 2-second validation step doesn't bottleneck the pipeline. This enables validation as a required check on every PR without developer complaints about slow builds.

## Success Criteria

The validation system must:
1. Complete full validation in <5 seconds for typical projects
2. Run intent validation without graph generation
3. Scale linearly with artifact count (not quadratically)
4. Enable pre-commit hook integration without friction
5. Support watch mode for continuous validation

## Specified By

This outcome is delivered through:
- **S-023**: Intent Validation CLI Command - fast validation without graph generation
- **S-024**: Brick Validation CLI Command - validates bricks against implementation graph
- **S-025**: Full Validation CLI Command - intelligent combined validation

## Constitution Linkage

This outcome serves: **Part III: Validation** - Fast Feedback
Enables: Frequent validation, pre-commit hooks, watch mode, CI integration
Without this: Validation is slow and avoided; errors accumulate undetected
