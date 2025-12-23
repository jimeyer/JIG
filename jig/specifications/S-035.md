---
id: S-035
title: Brick ID Format Validation
type: specification
---

# Brick ID Format Validation

Brick IDs SHALL match the pattern `B-[a-z0-9-]+` (kebab-case format).

**Acceptance Criteria**:
- Validation function checks all brick IDs in bricks.yaml
- IDs must start with `B-` prefix
- After prefix, only lowercase letters (a-z), digits (0-9), and hyphens (-) are allowed
- Invalid IDs are reported with clear error messages indicating the problem
- Error message shows the invalid ID and suggests correct format

**Rationale**: Semantic kebab-case IDs provide immediate meaning at a glance. B-auth indicates authentication, while B-001 provides no context. This enforces A001 Section 4 ID format requirements.

**Valid Examples**:
- `B-auth`
- `B-core-utils`
- `B-rest-api`
- `B-cli-interface`
- `B-user-management`

**Invalid Examples**:
- `B-001` (old sequential format)
- `B-Auth` (uppercase letter)
- `B-core_utils` (underscore instead of hyphen)
- `B-` (missing name)
- `auth` (missing B- prefix)

**References**:
- A001 Section 4: Brick Definitions
- A001 Section 7: ID Format Contract
- A001 Section 10: Validation Contract (rule #2)
