---
id: S-108
title: Validation Error ID Stability
type: specification
outcomes: [O-029, O-005]
architecture: [A-004]
---

# Validation Error ID Stability

Validation errors have stable, deterministic IDs computed from the error's semantic identity, enabling reliable error tracking across validation runs.

**Acceptance Criteria**:
- Each validation error has an `id` field in JSON output
- The ID is a 12-character hexadecimal string
- The same logical error produces the same ID across validation runs
- Different errors produce different IDs
- The ID is computed from: rule code, artifact identifier, and error-specific context
- Changing artifact content that doesn't affect the error (e.g., adding comments) does not change the ID
- Changing content that does affect the error (e.g., fixing the issue) removes the error

**Rationale**: Stable error IDs enable:
- Agents to track which errors persist across fix attempts
- CI systems to detect new vs. existing errors
- Humans to reference specific errors in discussions
- Mend command to correlate fixes with their target errors

**Non-goals**: The ID format is not guaranteed to be human-memorable. Use the `message` field for human communication.
