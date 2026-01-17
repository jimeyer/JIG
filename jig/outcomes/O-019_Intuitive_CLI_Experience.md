---
id: O-019
title: Intuitive CLI Experience
type: outcome
theme: [Experience]
goals: [G-002]
specifications: [S-057, S-058, S-059, S-060, S-061]
---

# Intuitive CLI Experience

**Value:** Users interact with JIG through a memorable, verb-first command structure requiring zero configuration to start.

**Acceptance:** `jigy validate`, `jigy layers`, `jigy align` work from any project subdirectory with no flags or setup required.

## AI Agent Benefit

Agents can execute JIG commands without parsing configuration files or remembering complex flag combinations. Simple, predictable CLI patterns reduce agent errors and enable reliable automation. Without intuitive CLI, agents waste context on command syntax and fail on edge cases.

## Rationale

Developer tools succeed or fail based on friction. Complex CLIs with mandatory flags, configuration requirements, and inconsistent patterns create friction that discourages use. JIG must be used frequently to provide value - a tool that's hard to invoke is a tool that's not invoked.

The verb-first pattern (`jigy validate`, `jigy rebuild`, `jigy layers`) reads like English and is memorable. Users don't need to remember whether it's `jigy --validate` or `validate-jigy` or `jigy run validate`. The pattern is consistent and predictable.

Zero-configuration startup is essential for adoption. Projects can run `jigy validate` immediately after installing JIG - no `jigy init`, no config file creation, no directory restructuring. Sensible defaults handle typical projects; configuration is available but optional.

Auto-discovery of project root eliminates `--project-dir` flags. Users run commands from any subdirectory; JIG walks up to find `jig/` or `jig.yaml`. This matches user mental models - "I'm in my project, run JIG" - without requiring users to track where they are.

## Success Criteria

The CLI must:
1. Auto-discover project root by walking up directories
2. Use verb-first command pattern: `jigy {verb} [target]`
3. Require no configuration for projects with standard layout
4. Limit global flags to: `--help`, `--version`, `--no-rebuild`, plus universal output flags (`-j`, `-m`, `-v`)
5. Provide consistent error messages with actionable guidance
6. Complete command dispatch in <100ms before actual work begins

## Specified By

This outcome is delivered through:
- **S-057**: Project Root Auto-Discovery - walks up directories to find project
- **S-058**: Verb-First Rebuild Commands - consistent `jigy rebuild {target}` structure
- **S-059**: Align Command - single command for full workflow
- **S-060**: Show Command Structure - `jigy show` for structural queries
- **S-061**: Minimal Global Options - only `--help` and `--version` globally

## Constitution Linkage

This outcome serves: **Part V: Developer Experience**
Enables: Friction-free JIG usage, frequent validation, CI integration
Without this: Users avoid running JIG due to complexity; validation happens too rarely
