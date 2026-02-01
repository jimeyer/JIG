---
id: S-045
title: Intent Artifact Hashing
type: specification
outcomes: [O-017]
---

# Intent Artifact Hashing

Specifications and Outcomes are hashed using canonical JSON representation of frontmatter plus normalized body.

**Acceptance Criteria:**
- YAML frontmatter parsed and included in hash input
- Body text stripped of leading/trailing whitespace
- Line endings normalized to LF before hashing
- JSON canonicalized with sorted keys and minimal separators
- Trailing whitespace changes do not affect hash
- CRLF vs LF differences do not affect hash

**Rationale:** Captures semantic content changes while ignoring formatting noise.
