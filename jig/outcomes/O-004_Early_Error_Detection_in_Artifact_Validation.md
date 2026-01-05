---
id: O-004
title: Early Error Detection in Artifact Validation
type: outcome
theme: [Validation]
supports_goals: [G-003]
specifies: [S-023, S-024, S-025, S-027]
---

# Early Error Detection in Artifact Validation

**Value:** Fail-fast feedback loop catches malformed artifacts at validation time rather than during expensive graph generation or cryptic runtime failures.

**Acceptance:** Validation errors are detected and reported before any graph generation attempts.

## AI Agent Benefit

Agents discover errors immediately after writing artifacts rather than minutes later during graph generation. Early detection enables rapid iteration - agents can fix errors and retry without losing context. Without early detection, agents waste compute on failed graph builds and face harder-to-parse runtime errors.

## Rationale

Graph generation is expensive - it parses source code, builds dependency graphs, and writes NDJSON output. If an artifact (spec, outcome, or brick definition) is malformed, this work is wasted. The graph generator may produce cryptic errors or silently skip the malformed artifact.

Early error detection inverts this cost structure. Validation runs first, checking artifact format before any graph work begins. A missing frontmatter field or malformed YAML is caught in milliseconds, not after seconds of graph generation.

This fail-fast pattern is especially valuable in CI pipelines where graph generation cost accumulates across many builds. Catching errors early in the pipeline saves compute and provides faster feedback to developers.

For developers, early detection means errors appear at the point of introduction - not hours later when the CI build fails. The mental context is fresh, and the fix is obvious.

## Success Criteria

The validation system must:
1. Detect malformed artifacts before graph generation begins
2. Run validation independently via `jigy validate`
3. Integrate validation into rebuild commands automatically
4. Report errors within 1 second for typical projects
5. Provide clear error messages for all validation failures

## Specified By

This outcome is delivered through:
- **S-023**: Specification File Validation - validates spec markdown format
- **S-024**: Outcome File Validation - validates outcome markdown format
- **S-025**: Brick Definition Validation - validates bricks.yaml format
- **S-027**: Pre-Generation Validation Gate - blocks graph generation on errors

## Constitution Linkage

This outcome serves: **Part III: Validation** - Early Detection
Enables: Fail-fast feedback, reduced wasted compute, clear error attribution
Without this: Errors surface late in expensive operations; agents waste context on failed builds
