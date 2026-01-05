---
id: S-092
title: Intent Document Title Requirements
type: specification
---

# Intent Document Title Requirements

This specification documents title selection guidance for intent documents (Specifications, Outcomes, Architectures). Title quality is enforced via agent context (CLAUDE.md, Charter), not via deterministic validation.

## Guidance

### Title Selection Principles

1. Title MUST describe behavior or capability, not implementation details
2. Title MUST NOT contain version numbers, dates, or temporal words
3. Title MUST NOT start with articles (The, A, An)
4. Title MUST be specific enough to distinguish from other documents of same type
5. Title SHOULD complete the phrase "This [spec|outcome|architecture] defines..."

### Title Stability

6. Title changes SHOULD be avoided unless scope genuinely changed
7. Title renames cause file renames, which create git history noise
8. When title change is necessary, use separate commit with justification

### Anti-Patterns

Avoid these title patterns:

| Pattern | Problem | Example |
|---------|---------|---------|
| Temporal words | Becomes stale | `New_Authentication`, `Old_Parser` |
| Version numbers | Becomes stale | `User_Model_v2`, `Auth_2024` |
| Implementation details | Ties to solution | `Redis_Cache_Layer` |
| Vague comparatives | Meaningless | `Better_Error_Handling` |
| Task descriptions | Not a capability | `Fix_Login_Bug` |
| Leading articles | Unnecessary | `The_Main_Config` |

## Rationale

Title quality requires semantic judgment that deterministic validation cannot provide. Regex-based pattern matching produces false positives (e.g., `A_Record_Parser` flagged by `^A_` rule) and misses most actual problems (e.g., `Redis_Cache_Layer` is implementation-specific but passes all regex checks).

Agent context (CLAUDE.md, Charter "For AI Agents" section, skills) ensures guidance reaches the point of decision—before file creation—rather than after via post-hoc validation warnings.

## Enforcement

- **NOT enforced by `jigy validate`** — validation checks structural correctness only
- **Enforced by agent context** — CLAUDE.md, Charter, skills see guidance before creating files
- **Reference documentation** — this spec provides authoritative guidance for edge cases

## See Also

- CLAUDE.md "Creating JIG Intent Documents" section
- Charter "For AI Agents" section
- C010_SCOPE_Standardized-Intent-Document-Naming.md (PART J)
