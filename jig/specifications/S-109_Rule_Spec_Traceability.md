---
id: S-109
title: Rule Spec Traceability
type: specification
outcomes: [O-029, O-005]
architecture: [A-004]
---

# Rule Spec Traceability

Each validation rule references the specification it enforces, enabling error-to-requirement traceability.

**Acceptance Criteria**:
- Each validation error includes a `spec` field in JSON output
- The `spec` field contains the S-### ID of the specification being enforced
- Rules that enforce multiple specs list the primary spec (most specific)
- The spec reference is available in both JSON and human-readable output
- Running `jigy validate` with human-readable output shows spec IDs for each error

**Rationale**: Spec traceability enables:
- Humans to understand why a validation rule exists (read the spec)
- Agents to prioritize errors based on spec importance
- Reports showing which specs have active violations
- Debugging why a particular error is being raised

**Example Output**:
```
ERROR [S-018]: Missing required field 'outcomes' in jig/specifications/S-099.md
```
