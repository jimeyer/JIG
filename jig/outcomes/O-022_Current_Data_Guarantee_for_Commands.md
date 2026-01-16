---
id: O-022
title: Current Data Guarantee for Commands
type: outcome
theme: [Continuity]
goals: [G-002, G-001]
specifications: [S-068, S-069, S-070, S-071]
---

# Current Data Guarantee for Commands

**Value:** JIG commands operate on up-to-date graph data without requiring manual rebuild invocation.

**Acceptance:** Commands automatically rebuild stale graphs before executing; staleness check completes in <200ms when nothing changed.

## AI Agent Benefit

Agents always work with current data without needing to remember `jigy rebuild`. When an agent queries alignment or runs validation, results reflect the actual current state. Without auto-rebuild, agents risk acting on stale analysis - a subtle bug that's hard to detect and debug.

## Rationale

Stale graphs lead to false confidence. Validation passes against old code. Alignment queries return outdated results. Developers (and agents) make decisions based on information that's no longer true. This class of bug is subtle - everything appears to work, but the data is wrong.

Manual rebuild before every command adds friction and is easily forgotten. Developers run `jigy validate`, see it pass, and assume their code is correct - not realizing the graphs are stale. The fix seems simple ("just run rebuild first") but human memory is unreliable.

Naive auto-rebuild on every command wastes ~2 seconds when nothing changed. This friction discourages frequent use. The solution is smart staleness detection: check if source files changed since last rebuild, and only rebuild when necessary.

Git provides efficient change detection via diff. For non-git projects, a graceful fallback (always rebuild, or timestamp comparison) maintains correctness at the cost of speed. The `--no-rebuild` flag provides an escape hatch when users know graphs are current.

## Success Criteria

The staleness detection system must:
1. Detect source file changes since last graph generation
2. Trigger automatic rebuild when files changed
3. Complete staleness check in <200ms when nothing changed
4. Support git-based detection for git repositories
5. Fall back gracefully for non-git projects
6. Provide `--no-rebuild` flag to skip auto-rebuild when needed

## Specified By

This outcome is delivered through:
- **S-068**: Staleness Detection - determines if graphs need rebuild
- **S-069**: Git-Based Change Detection - uses git diff for efficiency
- **S-070**: Auto-Rebuild Integration - triggers rebuild before commands
- **S-071**: No-Rebuild Flag - allows skipping auto-rebuild

## Constitution Linkage

This outcome serves: **Part IV: Continuity** - Current Data
Enables: Always-current analysis, eliminated stale data bugs
Without this: Commands silently use outdated graphs; false results
