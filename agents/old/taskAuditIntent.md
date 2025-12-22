# Task: Outcome-Specification Graph Audit

## Objective

Audit the Outcome-Specification (O→S) graph structure to ensure design intent is clearly expressed through complete, coherent, and traceable relationships between business value (Outcomes) and behavioral requirements (Specifications).

## Context

The jig graph expresses design intent through two primary node types:
- **Outcomes** (O-XXX): Describe business value and WHY the system behaves a certain way
- **Specifications** (S-XXX): Define HOW the system behaves through observable contracts

**Together**, these nodes form the design intent graph. Outcomes decompose into Specifications via the `specifies: [S-XXX, ...]` frontmatter field.

This audit focuses on the **graph structure and relationships**, not individual node quality (which is covered by S008-O-S-Conformance-Audit). Specifically:

**Graph Topology:**
- Are all Outcomes linked to at least one Specification?
- Are all Specifications claimed by at least one Outcome?
- Are the links correctly bidirectional (Outcome→Spec and Spec→Outcome)?

**Completeness:**
- Do the Specifications collectively satisfy their parent Outcome's acceptance criteria?
- Are there obvious gaps in the specification set?
- Is the decomposition at the right granularity?

**Traceability:**
- Can you trace from business value (Outcome) to behavior (Specification) to code?
- Does the `@jig.implements("S-XXX")` and `@jig.verifies("S-XXX")` trail exist?
- Are all links mechanically verifiable?

**Coherence:**
- Do Specifications meaningfully decompose their parent Outcome?
- Is the abstraction level appropriate (Outcome=WHY, Spec=WHAT/HOW)?
- Are there misclassified nodes (Outcomes that are really Specs, or vice versa)?

## Inputs

**Outcome Files:**
- **Location**: `jig/outcomes/*.md`
- **Count**: Use `find jig/outcomes -name "*.md" | wc -l`
- **Key Fields**: `id`, `specifies: [S-XXX, ...]`

**Specification Files:**
- **Location**: `jig/specifications/*.md`
- **Count**: Use `find jig/specifications -name "*.md" | wc -l`
- **Key Fields**: `id`, `implements: [O-XXX, ...]` (or similar parent linkage)

**Graph Index (if exists):**
- **Location**: `jig/graph-index.yaml` or similar
- **Purpose**: Cross-reference for validation

**Reference Materials:**
- `docs/architecture/O-S-Writing-Guide.md`: Defines O/S node principles
- `agents/S008-O-S-Conformance-Audit.md`: Example of node-level audit (this task focuses on graph-level)

## Process

### 1. Discovery Phase

**Build Graph Topology:**
```bash
# Count nodes
OUTCOME_COUNT=$(find jig/outcomes -name "*.md" | wc -l)
SPEC_COUNT=$(find jig/specifications -name "*.md" | wc -l)

# Extract all O→S links
for f in jig/outcomes/*.md; do
  grep "^specifies:" "$f"  # Extract specification lists
done

# Extract all S→O links (if they exist)
for f in jig/specifications/*.md; do
  grep "^implements:" "$f"  # Or similar parent linkage field
done
```

**Data Collection:**
- List of all Outcome IDs with their `specifies: [...]` arrays
- List of all Specification IDs with their parent Outcome references
- Build adjacency matrix: O-XXX → [S-YYY, S-ZZZ, ...]

### 2. Critical Issue Detection

**CRITICAL-1: Orphaned Outcomes**

Find Outcomes with `specifies: []` (empty specification list):
```bash
for f in jig/outcomes/*.md; do
  if grep -q "^specifies: \[\]" "$f"; then
    echo "Orphaned: $f"
  fi
done
```

**Impact**: Outcome describes business value but has no behavioral requirements to satisfy it. Cannot implement or verify.

**Exception**: Check if Outcome body mentions specifications in "Related" section - if so, this is a frontmatter bug (critical fix: add to `specifies`). If no specs mentioned anywhere, this is a decomposition gap (critical fix: create specifications).

---

**CRITICAL-2: Orphaned Specifications**

Find Specifications not claimed by any Outcome:
1. Extract all Specification IDs from `jig/specifications/*.md`
2. Extract all `specifies: [...]` arrays from `jig/outcomes/*.md`
3. Find S-XXX IDs that never appear in any Outcome's `specifies` list

**Impact**: Specification has no parent - unclear what business value it serves. Cannot trace to higher-level goals.

**Fix**: Either link to existing Outcome or create new Outcome to justify the Specification's existence.

---

**CRITICAL-3: Broken Links**

Find references that point to non-existent nodes:
- Outcome specifies S-XXX, but `jig/specifications/S-XXX.md` doesn't exist
- Specification implements O-XXX, but `jig/outcomes/O-XXX.md` doesn't exist

**Impact**: Graph is malformed. Tooling will fail. Traceability broken.

**Fix**: Either create missing node or remove broken reference.

---

**CRITICAL-4: Bidirectional Link Mismatch**

If Specifications have an `implements: O-XXX` field (or similar):
- O-012 specifies [S-024, S-025]
- S-024 implements [O-012] ✓ CONSISTENT
- S-025 implements [O-014] ✗ INCONSISTENT (should be O-012)

**Impact**: Graph is contradictory. Unclear which Outcome "owns" the Specification.

**Fix**: Ensure forward (O→S) and backward (S→O) links agree.

### 3. Moderate Issue Detection

**MODERATE-1: Under-Specified Outcomes**

Find Outcomes with only 1 Specification:
```bash
# Pattern: specifies: [S-XXX]  (single element)
```

**Concern**: Most Outcomes decompose into 2-5 Specifications. Single-spec Outcomes might be:
- Over-decomposed (Outcome and Spec are nearly identical - merge them?)
- Under-specified (need more Specs to satisfy Outcome acceptance criteria)

**Analysis Required**: Read Outcome acceptance criteria. Can 1 Spec really satisfy all criteria? If not, identify gaps.

---

**MODERATE-2: Over-Decomposed Outcomes**

Find Outcomes with >10 Specifications:
```bash
# Pattern: specifies: [S-001, S-002, ..., S-012]  (many elements)
```

**Concern**: Very large spec lists might indicate:
- Outcome is too broad (should be split into multiple Outcomes)
- Specifications are too granular (should be merged)
- Outcome is actually a "meta-outcome" (collection of related outcomes)

**Analysis Required**: Check if specifications cluster into semantic groups that could be separate Outcomes.

---

**MODERATE-3: Specification Sharing**

Find Specifications claimed by multiple Outcomes:
- O-008 specifies [S-015, S-016, S-017]
- O-009 specifies [S-015, S-018]  ← S-015 is shared

**Analysis**: Is this intentional (Spec supports multiple Outcomes) or a modeling issue?
- **Valid**: Shared infrastructure (e.g., S-015: "Logging system captures errors" supports multiple Outcomes)
- **Concern**: If Specs are tightly coupled to one Outcome, sharing might indicate unclear decomposition

---

**MODERATE-4: Completeness Gaps**

For each Outcome:
1. Read Outcome's "Acceptance Criteria" section
2. Read all linked Specifications
3. Check: Do Specifications collectively cover all acceptance criteria?

**Example Issue**:
```markdown
# O-042: Data Validation Ensures Integrity

**Acceptance Criteria:**
- All user inputs are validated before processing
- Invalid data triggers clear error messages  ← NO SPEC COVERS THIS
- Validation rules are centrally defined

**Specifies:** [S-120, S-121]
- S-120: Input validation uses schema-based rules
- S-121: Validation rules defined in YAML config
```

**Gap**: No Specification describes error message behavior.

**Fix**: Either create S-122 for error handling or expand S-120 to include it.

### 4. Traceability Analysis

**Check Implementation Trail:**

For each Specification:
1. Search codebase for `@jig.implements("S-XXX")` annotations
2. Search codebase for `@jig.verifies("S-XXX")` annotations (tests)
3. Report coverage:
   - Specifications with implementations found
   - Specifications with tests found
   - Specifications with neither (gap)

**Output Example**:
```
Traceability Report:
- 45/81 Specifications have @jig.implements annotations (55%)
- 38/81 Specifications have @jig.verifies tests (47%)
- 23/81 Specifications have BOTH (28%)
- 18/81 Specifications have NEITHER (22%) ← GAPS
```

**Critical Traceability Gaps**: Specifications without ANY code references cannot be verified.

### 5. Coherence Analysis

**Abstraction Level Check:**

For each Outcome→Specification link, verify:
- **Outcome describes WHY/WHAT-VALUE**: Business value, architectural decision, user need
- **Specification describes HOW/WHAT-BEHAVIOR**: Observable system behavior, contracts, invariants

**Anti-Pattern Examples:**

**Outcome misclassified as Specification:**
```markdown
# O-XXX: User authentication validates JWT tokens
```
↑ This is too specific/behavioral for an Outcome. Should be a Specification under a broader Outcome like "Secure API Access."

**Specification misclassified as Outcome:**
```markdown
# S-XXX: System provides secure user authentication
```
↑ This is too broad/value-focused for a Specification. Should be an Outcome with child Specs like "JWT validation," "Session management," etc.

**Check**: Does the node title match its type? Outcomes should emphasize value/goals, Specs should emphasize behavior/contracts.

---

**Semantic Coherence Check:**

For each Outcome, read all child Specifications and ask:
- Do these Specs collectively satisfy the Outcome?
- Is there a clear logical relationship (decomposition, not just loose association)?
- Could you implement the Outcome by implementing all its Specs?

**Incoherent Example:**
```markdown
# O-015: Message Ordering Guarantees

**Specifies:**
- S-042: Lamport clocks track causality  ✓ RELATED
- S-043: Messages serialize to Protocol Buffers  ? UNRELATED
- S-044: Causal delivery preserves happened-before  ✓ RELATED
```

S-043 is about serialization format, not ordering - likely mislinked.

## Outputs

### Format: Markdown Report

**File Name**: `agents/S00X-O-S-Graph-Audit.md` (where X is next available number)

**Structure**:
```markdown
# Outcome-Specification Graph Audit Report

**Date:** [YYYY-MM-DD]
**Scope:** [X Outcomes, Y Specifications]
**Purpose:** Validate design intent graph structure, completeness, and traceability

---

## Executive Summary

**Graph Statistics:**
- Outcomes: [X total]
- Specifications: [Y total]
- O→S Links: [Z total edges]
- Average Specs per Outcome: [Z/X]

**Critical Issues:**
- [N] orphaned Outcomes (no Specifications)
- [M] orphaned Specifications (no parent Outcome)
- [P] broken links (references to non-existent nodes)
- [Q] bidirectional mismatches

**Moderate Issues:**
- [A] under-specified Outcomes (only 1 Spec)
- [B] over-decomposed Outcomes (>10 Specs)
- [C] completeness gaps (Outcome criteria not covered by Specs)

**Traceability:**
- [D]% of Specifications have code implementations
- [E]% of Specifications have test coverage
- [F]% have both

---

## Critical Findings

### Orphaned Outcomes (No Specifications)

| Outcome | Title | Issue |
|---------|-------|-------|
| O-XXX | [Title] | `specifies: []` - no behavioral requirements |
| O-YYY | [Title] | `specifies: []` - specs mentioned in body but not frontmatter |

**Impact**: Cannot implement or verify these Outcomes.

**Fix Strategy**:
- O-XXX: Create specifications S-AAA, S-BBB to decompose acceptance criteria
- O-YYY: Add `specifies: [S-CCC, S-DDD]` to frontmatter (specs already exist)

---

### Orphaned Specifications (No Parent Outcome)

| Specification | Title | Issue |
|---------------|-------|-------|
| S-XXX | [Title] | Not claimed by any Outcome |
| S-YYY | [Title] | Not claimed by any Outcome |

**Impact**: Unclear why these Specifications exist. No traceability to business value.

**Fix Strategy**:
- S-XXX: Link to existing O-AAA (already describes this behavior's value)
- S-YYY: Create new Outcome O-BBB to justify this Specification

---

### Broken Links

| Source | Target | Issue |
|--------|--------|-------|
| O-XXX | S-999 | O-XXX specifies S-999, but S-999.md doesn't exist |
| S-AAA | O-888 | S-AAA implements O-888, but O-888.md doesn't exist |

**Fix Strategy**: [Create missing node or remove broken reference]

---

### Bidirectional Link Mismatches

| Outcome | Specification | Forward Link | Backward Link | Issue |
|---------|---------------|--------------|---------------|-------|
| O-012 | S-025 | O-012 specifies S-025 | S-025 implements O-014 | Mismatch |

**Fix Strategy**: Decide which is correct and fix the other.

---

## Moderate Findings

### Under-Specified Outcomes (Single Specification)

| Outcome | Spec Count | Analysis |
|---------|------------|----------|
| O-XXX | 1 | Acceptance criteria has 4 points, but only 1 Spec - gaps likely |
| O-YYY | 1 | Outcome and Spec nearly identical - consider merging |

---

### Over-Decomposed Outcomes (>10 Specifications)

| Outcome | Spec Count | Analysis |
|---------|------------|----------|
| O-XXX | 15 | Specifications cluster into 3 semantic groups - consider splitting Outcome |

---

### Completeness Gaps

| Outcome | Missing Coverage |
|---------|------------------|
| O-XXX | Acceptance criterion "error messages are clear" - no Spec covers error handling |
| O-YYY | Acceptance criterion "performance <100ms" - no Spec defines latency requirements |

**Fix Strategy**: Create new Specifications or expand existing ones to cover gaps.

---

## Traceability Report

### Implementation Coverage

**Specifications WITH `@jig.implements` annotations (X/Y):**
- S-001, S-002, S-005, ...

**Specifications WITHOUT implementations ([Y-X] gaps):**
- S-XXX: [Title] - no code found
- S-YYY: [Title] - no code found

---

### Test Coverage

**Specifications WITH `@jig.verifies` tests (X/Y):**
- S-001, S-003, S-007, ...

**Specifications WITHOUT tests ([Y-X] gaps):**
- S-XXX: [Title] - no tests found
- S-YYY: [Title] - no tests found

---

### Complete Traceability Chain

**Specifications with BOTH implementation AND tests ([X] nodes):**
- S-001: Outcome → Spec → Code → Test ✓
- S-005: Outcome → Spec → Code → Test ✓

**Gold Standard**: These Specifications have complete traceability.

---

## Coherence Analysis

### Abstraction Level Violations

**Outcomes that should be Specifications:**
- O-XXX: "[Title]" - too behavioral, should be Spec under broader Outcome

**Specifications that should be Outcomes:**
- S-XXX: "[Title]" - too broad/value-focused, should be Outcome with child Specs

---

### Semantic Incoherence

**Questionable O→S Relationships:**

| Outcome | Specification | Issue |
|---------|---------------|-------|
| O-015: Message Ordering | S-043: Protobuf Serialization | Spec is about format, not ordering - mislinked? |

---

## Graph Visualization

```
Outcome Distribution by Specification Count:

0 Specs: ██████ (6 outcomes) ← ORPHANED
1 Spec:  ████ (4 outcomes) ← UNDER-SPECIFIED
2-5 Specs: ████████████████████ (20 outcomes) ← NORMAL
6-10 Specs: ████ (4 outcomes) ← NORMAL
>10 Specs: ██ (2 outcomes) ← OVER-DECOMPOSED

Specification Distribution by Outcome Count:

0 Outcomes: ████ (4 specs) ← ORPHANED
1 Outcome:  ████████████████████████ (60 specs) ← NORMAL
2+ Outcomes: ████ (8 specs) ← SHARED
```

---

## Recommendations

### Immediate Action (Critical)

1. **Fix orphaned Outcomes**: Add specification links to O-XXX, O-YYY frontmatter OR create missing Specifications
2. **Fix orphaned Specifications**: Link S-AAA, S-BBB to parent Outcomes OR create justifying Outcomes
3. **Repair broken links**: Create missing nodes or remove invalid references
4. **Resolve bidirectional mismatches**: Fix conflicting O→S and S→O links

### Short-Term (Moderate)

5. **Address completeness gaps**: Create Specifications to cover missing acceptance criteria
6. **Review under-specified Outcomes**: Either add more Specs or merge with single Spec
7. **Review over-decomposed Outcomes**: Consider splitting into multiple Outcomes

### Long-Term (Quality)

8. **Improve traceability**: Add `@jig.implements` and `@jig.verifies` annotations to codebase
9. **Validate coherence**: Review flagged abstraction level violations
10. **Automate graph validation**: Add `jigy graph validate` command to CI

---

## Success Metrics

**Graph Integrity:**
- ✓ PASS: 0 broken links
- ✓ PASS: 0 bidirectional mismatches
- ✗ FAIL: 6 orphaned Outcomes, 4 orphaned Specifications

**Completeness:**
- ⚠ WARNING: 12 Outcomes have completeness gaps (criteria not covered by Specs)

**Traceability:**
- ⚠ WARNING: Only 55% of Specifications have code implementations
- ⚠ WARNING: Only 47% of Specifications have test coverage

---

## Conclusion

**Overall Assessment:** [Summary paragraph on graph health]

**Strengths:**
- Most Outcomes properly decompose into 2-5 Specifications
- No broken links or malformed references
- Core protocol stack (O-001 to O-010) has excellent traceability

**Weaknesses:**
- 6 orphaned Outcomes need Specifications created
- 4 orphaned Specifications need parent Outcomes
- Traceability coverage is incomplete (only 28% have both code and tests)

**Action Priority:**
1. Fix critical graph topology issues (orphans, broken links) - 2 hours
2. Address completeness gaps in high-priority Outcomes - 4 hours
3. Add missing `@jig.implements` annotations to codebase - ongoing

---

**Audit Completed:** [YYYY-MM-DD]
**Graph Version:** [Commit SHA or date]
**Nodes Reviewed:** [X Outcomes + Y Specifications]
**Tooling Used:** `grep`, `find`, manual analysis
```

## Success Criteria

- [ ] All Outcome files in `jig/outcomes/` have been analyzed
- [ ] All Specification files in `jig/specifications/` have been analyzed
- [ ] Graph topology has been validated (O→S links, S→O links)
- [ ] All orphaned Outcomes identified with specific file names
- [ ] All orphaned Specifications identified with specific file names
- [ ] All broken links identified and categorized
- [ ] Completeness analysis done for at least 10 representative Outcomes
- [ ] Traceability report includes implementation and test coverage percentages
- [ ] At least 3 coherence issues flagged with specific examples
- [ ] Recommendations are prioritized (Immediate/Short-Term/Long-Term)
- [ ] Report is saved in `agents/` directory

## Constraints

**DO NOT:**
- Modify any Outcome or Specification files (read-only analysis)
- Audit individual node quality (that's S008's job - focus on graph structure)
- Make subjective judgments about decomposition without clear criteria
- Flag shared Specifications as errors without analyzing if sharing is intentional

**MUST:**
- Read frontmatter from ALL Outcome and Specification files
- Build complete graph topology (adjacency lists)
- Quote specific frontmatter when identifying issues
- Provide file:line references for all findings
- Include counts and percentages in statistics

**PREFER:**
- Mechanical validation over subjective assessment
- Graph-theoretic analysis (orphans, connectivity, coverage)
- Concrete examples of topology issues
- Actionable fixes ("add S-XXX to O-YYY.specifies") over vague suggestions

## Edge Cases to Handle

**If Specifications don't have parent linkage field:**
- Rely solely on Outcome→Specification forward links
- Note this as a schema limitation in report
- Recommend adding `implements: O-XXX` to Specification frontmatter

**If multiple Outcomes claim the same Specification (shared):**
- Check if this is intentional (infrastructure/utility Spec)
- Flag if Spec is tightly coupled to one Outcome but claimed by multiple
- Document shared Specifications in a separate section

**If Outcome has no acceptance criteria:**
- Cannot perform completeness analysis for that Outcome
- Flag as documentation gap (separate from graph topology issue)

**If specification count seems wrong:**
- Cross-reference with graph index (if exists)
- Double-check file naming conventions (S-XXX.md vs S-XXX-something.md)
- Report discrepancies

## Examples

### Example 1: Orphaned Outcome (Critical)

```yaml
# jig/outcomes/O-042.md
id: O-042
title: Data Validation Ensures Integrity
specifies: []
status: active
```

**Issue**: Outcome exists but has no Specifications to implement its acceptance criteria.

**Fix**: Create Specifications:
- S-120: Schema-based input validation
- S-121: Clear error messages for invalid data
- S-122: Centralized validation rule definitions

Then update frontmatter: `specifies: [S-120, S-121, S-122]`

---

### Example 2: Orphaned Specification (Critical)

S-057 exists in `jig/specifications/S-057.md` but does not appear in ANY Outcome's `specifies` list.

**Issue**: No traceability to business value. Why does this Specification exist?

**Fix Option 1**: Link to existing Outcome O-019 if S-057 relates to its goals.
**Fix Option 2**: Create new Outcome O-028 to justify S-057's existence.

---

### Example 3: Completeness Gap (Moderate)

```markdown
# O-015: Reliable Message Delivery

**Acceptance Criteria:**
- Messages are delivered exactly once
- Network failures trigger automatic retry
- Delivery confirmation is tracked

**Specifies:** [S-042, S-043]
- S-042: Message acknowledgment protocol
- S-043: Idempotent message processing
```

**Gap**: No Specification covers "network failures trigger automatic retry."

**Fix**: Create S-044: "Retry Logic for Failed Deliveries" or expand S-042 to include retry behavior.

---

### Example 4: Abstraction Level Violation (Coherence Issue)

```markdown
# O-XXX: JWT Token Validation

JWT tokens are validated using RS256 signature verification.
```

**Issue**: This is too specific/behavioral for an Outcome. It's a Specification masquerading as an Outcome.

**Fix**:
- Rename to Specification S-XXX
- Create broader Outcome O-XXX: "Secure API Access" with acceptance criteria about authentication, authorization, and session management
- Make S-XXX one of several Specifications under O-XXX

## Verification Steps

After generating the report:

1. **Completeness Check**: Verify all O-XXX and S-XXX files were processed
2. **Link Validation**: Spot-check 5 Outcomes - verify their `specifies` arrays are correctly reported
3. **Orphan Detection**: Manually verify at least 2 orphaned nodes are truly orphaned
4. **Statistics Accuracy**: Recalculate one percentage to confirm math is correct
5. **Fix Feasibility**: Ensure recommended fixes are specific and actionable

---

**Version:** 1.0
**Last Updated:** 2025-12-02
**Guide Reference:** docs/architecture/O-S-Writing-Guide.md
**Related:** agents/S008-O-S-Conformance-Audit.md (node quality audit)
