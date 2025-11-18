---
id: O-JIG-005
type: outcome
title: "JIG demonstrates modularity >0.7"
subsystem: core
created: 2025-11-18
---

# Outcome: High Modularity (Decomposability)

JIG codebase should exemplify nearly decomposable architecture with modularity score >0.7 (Newman-Girvan metric).

## Value

JIG teaches by example. The tool that enforces modularity should embody it. This:
- Validates the approach works in practice
- Provides reference implementation
- Enables parallel development
- Makes JIG easier to extend and maintain

"Eat your own dog food" - if JIG can't achieve high modularity, why would users trust it?

## Success Metrics

- Overall modularity score >0.7 (Newman-Girvan)
- Each subsystem has coupling ratio >10:1 (internal/external edges)
- Subsystems export <5 interfaces each
- Circular dependencies = 0

## Acceptance Criteria

- Run `jig decompose --metrics` on JIG itself
- All subsystems meet coupling targets
- Module depth (LOC/exports) >100:1
- Clear subsystem boundaries in code organization

## Subsystems Expected

- core: Config, parser, validator
- cli: Command-line interface
- graph: Graph building and analysis
- harvest: Marker extraction and integration
- metrics: Decomposability calculations

## Related

- specs: S-JIG-004
- subsystem: core

## History

- 2025-11-18: Created during WU0 bootstrap (known constraint from SCOPE)
