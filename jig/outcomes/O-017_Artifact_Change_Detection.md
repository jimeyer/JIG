---
id: O-017
title: Artifact Change Detection
type: outcome
theme: [Continuity]
supports_goals: [G-002, G-001]
specifies: [S-044, S-045, S-046, S-047, S-048, S-049, S-050]
---

# Artifact Change Detection

**Value:** Enables automated detection of specification, implementation, or test changes, eliminating manual tracking and enabling CI/CD drift detection.

**Acceptance:** Changes to any JIG artifact are detected via content hashing with <200ms staleness check when nothing changed.

## AI Agent Benefit

Agents can determine what changed since their last session by querying artifact hashes. This prevents redundant analysis of unchanged code and enables incremental work. Without change detection, agents must re-analyze entire codebases each session, wasting context and compute.

## Rationale

Software systems accumulate drift between intent (specifications), reality (implementation), and verification (tests). Without automated change detection, this drift is invisible until it causes failures.

Manual tracking of "what changed" is error-prone and incomplete. Developers forget to update specs when code changes. Tests drift from implementations they claim to verify. The gap between documentation and reality widens silently.

Content hashing provides objective, tamper-evident change detection. A hash change means content changed - no false positives or negatives. This enables CI pipelines to flag misalignment automatically rather than relying on human vigilance.

JIG's change detection enables three key workflows: (1) staleness detection before commands, (2) CI gates that block merges when specs and code diverge, and (3) agent session continuity where work resumes from last known state.

## Success Criteria

The change detection system must:
1. Hash all artifacts using SHA-256 truncated to 12 hex characters
2. Detect changes to specification files within 1 second
3. Detect changes to implementation files within 2 seconds for 10K LOC
4. Detect changes to test files within 1 second
5. Complete staleness check in <200ms when no files changed
6. Persist hashes to enable cross-session comparison

## Specified By

This outcome is delivered through:
- **S-044**: Content Hash Format - defines SHA-256 truncated hash standard
- **S-045**: Specification File Hashing - hashes spec markdown files
- **S-046**: Implementation File Hashing - hashes source code files
- **S-047**: Test File Hashing - hashes test files
- **S-048**: Hash Persistence - stores hashes for comparison
- **S-049**: Change Detection Query - API to check what changed
- **S-050**: Staleness Check Performance - ensures fast unchanged checks

## Constitution Linkage

This outcome serves: **Part IV: Continuity** - Change Detection
Enables: Drift detection, CI integration, agent session continuity
Without this: Agents cannot determine what changed between sessions; manual tracking fails at scale
