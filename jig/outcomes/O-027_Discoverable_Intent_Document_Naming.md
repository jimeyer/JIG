---
id: O-027
title: Discoverable Intent Document Naming
type: outcome
theme: [Validation]
supports_goals: [G-001, G-004]
specifies: [S-092]
---

# Discoverable Intent Document Naming

**Value:** Intent document filenames include meaningful titles, enabling developers and agents to understand document purpose without opening files.

**Acceptance:** Developers can locate relevant specifications, outcomes, and architectures by scanning filenames alone; title guidance prevents git noise from unnecessary renames.

## AI Agent Benefit

Agents creating new intent documents receive title selection guidance via CLAUDE.md and Charter before creating files. This prevents poor title choices that would cause file renames later. Title stability reduces git history noise and merge conflicts.

## Rationale

Files like `S-047.md` reveal nothing about content—developers must open each file to find what they need. Files like `S-047_Response_Caching.md` are immediately scannable. However, title quality cannot be validated deterministically (requires semantic judgment), so guidance must reach agents before file creation, not after via validation warnings.

## Success Criteria

1. All intent document filenames include title in snake_case
2. Title guidance is available in agent context (CLAUDE.md, Charter)
3. Validation checks structural consistency (filename↔frontmatter↔H1 match)
4. Title quality is NOT checked by validation (semantic judgment required)

## Specified By

This outcome is delivered through:
- **S-092**: Intent Document Title Requirements - documents title selection guidance for agents
