---
id: O-JIG-004
type: outcome
title: "JIG requires no external services"
subsystem: core
created: 2025-11-18
---

# Outcome: No External Dependencies

JIG core functionality works without network, databases, or external services. Everything runs locally from files.

## Value

Developers can use JIG:
- On airplanes (offline)
- In secure environments (no internet)
- Without setting up databases
- Without API keys (for core features)

Reduces friction to adoption. Clone repo, run commands. No infrastructure required.

## Success Metrics

- Core commands (`extract`, `validate`, `graph`, `decompose`, `integrate`) work offline
- No database installation required
- No mandatory API keys for plumbing commands
- All data stored in git-tracked files

## Acceptance Criteria

- Disconnect network, core commands still work
- Fresh clone requires zero additional setup
- Optional AI features clearly marked with `ai-` prefix
- API keys only needed for `jig ai-*` commands

## Related

- specs: All core specs (S-JIG-001 through S-JIG-004)
- subsystem: core

## History

- 2025-11-18: Created during WU0 bootstrap (known constraint from SCOPE)
