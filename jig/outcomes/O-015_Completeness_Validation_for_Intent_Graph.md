---
id: O-015
title: Completeness Validation for Intent Graph
type: outcome
theme: [Validation]
goals: [G-004, G-003]
specifications: [S-042, S-043]
---

# Completeness Validation for Intent Graph

**Value:** Developers discover incomplete intent definitions (orphaned outcomes or specifications) before they cause confusion or misalignment.

**Acceptance:** `jigy validate intent` detects and reports outcomes without specifications and specifications without outcomes, completing in <1s for typical projects.

## AI Agent Benefit

Agents can trust that all specs have business justification (outcome linkage) and all outcomes have concrete requirements (spec linkage). Without completeness validation, agents work on orphaned specs with unclear value or orphaned outcomes with undefined scope. Completeness validation ensures every node in the intent graph is meaningful.

## Rationale

Incomplete intent graphs degrade traceability and alignment measurement. Two categories of incompleteness undermine the system:

1. **Orphaned outcomes**: Outcomes with empty `specifies` arrays provide no concrete requirements to implement. They capture WHY without defining WHAT, making them impossible to verify or implement. This violates the principle that outcomes decompose into actionable specifications.

2. **Orphaned specifications**: Specifications not referenced by any outcome define WHAT to build without explaining WHY it matters. They lack business justification and cannot be prioritized or evaluated for value delivery. This violates the principle that all specifications should deliver measurable value.

Detecting orphans early prevents:
- Wasted effort implementing specifications with unclear value
- Confusion about how to verify outcomes with no concrete requirements
- Drift between intent and implementation as orphaned nodes accumulate
- Incomplete alignment measurement (orphaned nodes appear unimplemented even if they're irrelevant)

By requiring bidirectional completeness (outcomes → specs, specs ← outcomes), we ensure that every intent node contributes to measurable value delivery.

## Success Criteria

The validation system must:
1. Detect outcomes where `specifies` array is empty `[]`
2. Detect specifications not referenced in any outcome's `specifies` array
3. Report clear error messages identifying which nodes are orphaned
4. Provide actionable guidance on how to fix (add specs to outcome, create outcome for spec)
5. Complete validation in under 1 second for typical projects (10-50 outcomes, 50-200 specs)
6. Integrate into existing `jigy validate intent` command

## Specified By

This outcome is delivered through:
- **S-042**: Validate outcomes specify at least one specification
- **S-043**: Validate specifications are specified by at least one outcome

## Constitution Linkage

This outcome serves: **Part III: Validation** - Completeness
Enables: Bidirectional O↔S linkage, meaningful intent graph
Without this: Orphaned nodes accumulate; intent graph becomes unreliable
