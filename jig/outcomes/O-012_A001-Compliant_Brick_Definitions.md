---
id: O-012
title: A001-Compliant Brick Definitions
type: outcome
theme: [Architecture, Validation]
goals: [G-003]
specifications: [S-035, S-036, S-037]
---

# A001-Compliant Brick Definitions

**Value:** Developers receive immediate feedback when brick definitions violate A001 contracts, preventing malformed architecture metadata from entering the codebase.

**Acceptance:** `jigy validate bricks` detects and reports ID format violations, missing layer fields, and invalid layer values in <1s for typical projects (5-50 bricks).

## AI Agent Benefit

Agents can trust brick ID format for reliable queries - `B-auth-core` always means the same thing. Without format validation, agents encounter malformed IDs (`B-001`, `B-Auth`) that break queries or create ambiguous references. Validated bricks provide a stable namespace for agent navigation.

## Rationale

A001 establishes strict contracts for brick definitions (Section 4). These contracts ensure that brick metadata is machine-readable, semantically meaningful, and architecturally sound. Without validation, three categories of errors accumulate:

1. **Format violations**: Non-kebab-case brick IDs (B-001, B-Auth, B-core_utils) obscure architectural intent and break tooling assumptions
2. **Missing required fields**: Bricks without `layer` fields break layer-based analysis and visualization
3. **Invalid values**: Non-integer or negative layer values create nonsensical architectural positions

Validating these contracts early prevents confusion about brick identity and architecture structure. Clear error messages with examples reduce debugging time and guide developers toward correct formats.

## Success Criteria

The validation system must:
1. Detect brick IDs that don't match `B-[a-z0-9-]+` pattern and suggest correct format with examples
2. Flag all bricks missing the `layer` field as errors (per A001 Section 4)
3. Reject non-integer layer values (strings, floats, null, arrays)
4. Reject negative layer values (layer numbers must be >= 0)
5. Complete validation in under 1 second for typical projects
6. Provide actionable error messages that show the invalid value and explain the fix

## Specified By

This outcome is delivered through:
- **S-035**: Brick ID format validation using regex pattern `^B-[a-z0-9-]+$` with clear examples of valid/invalid IDs
- **S-036**: Layer field presence validation ensuring all bricks have the required `layer` field
- **S-037**: Layer value validation checking that layer values are non-negative integers (>= 0)

## Constitution Linkage

This outcome serves: **Part II: Architectural Boundaries** - Bricks
Enables: Reliable brick queries, consistent architectural vocabulary
Without this: Malformed bricks create confusion and break tooling
