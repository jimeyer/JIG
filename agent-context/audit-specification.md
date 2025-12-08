# Audit Specification Alignment

You are auditing the alignment of a JIG specification. Your goal is to verify that the specification is properly connected through the S-F-T triangle (Specification → Function → Test).

## Input

You will be given a specification ID (e.g., `S-001`) to audit.

## Audit Checklist

### 1. Specification Quality

Read the specification file at `jig/specifications/{spec-id}.md` and verify:

- [ ] **ID Format**: ID matches `S-NNN` pattern in frontmatter
- [ ] **Required Fields**: Has `id` and `type: specification` in YAML frontmatter
- [ ] **Clear Intent**: The specification clearly describes WHAT should be built
- [ ] **Testable Criteria**: Acceptance criteria are concrete and verifiable
- [ ] **No Ambiguity**: Requirements use precise language (MUST, SHALL, MAY per RFC 2119)

### 2. Outcome Alignment (O → S edges)

Check if this specification is linked to an upstream outcome and verify the alignment:

```bash
# Find outcomes that reference this spec
grep -rn 'specifies:.*{spec-id}' jig/outcomes/
```

For each referencing outcome, verify:

- [ ] **Outcome Exists**: If spec is referenced, the outcome file exists and is valid
- [ ] **Bidirectional Consistency**: Outcome's `specifies` list includes this spec
- [ ] **Semantic Contribution**: This spec meaningfully contributes to achieving the outcome's goal
- [ ] **Scope Alignment**: The spec is neither too broad nor too narrow for the outcome
- [ ] **Complete Decomposition**: Together with sibling specs, the outcome is fully addressed

If NO outcome references this spec:

- [ ] **Orphan Assessment**: Is this spec standalone, or should it be linked to an outcome?
- [ ] **Outcome Candidate**: Should a new outcome be created to group related specs?

Report:
- List all outcomes that reference this spec
- For each outcome, list sibling specs (other specs in the same outcome)
- Assess whether the outcome is fully decomposed into testable specs
- Flag any semantic misalignment between spec and outcome intent

**Outcome Alignment States:**

| State | Assessment |
|-------|------------|
| ALIGNED | Spec contributes meaningfully to outcome goal |
| PARTIAL | Spec addresses outcome but incompletely |
| MISALIGNED | Spec doesn't support the outcome's stated goal |
| ORPHAN | Spec has no upstream outcome (may be intentional) |

### 3. Implementation Coverage (F → S edges)

Search for `@jig.implements("{spec-id}")` decorators in the codebase:

```bash
grep -r '@jig.implements.*{spec-id}' src/
```

For each implementing function, verify:

- [ ] **Functions Exist**: At least one function implements this spec
- [ ] **Correct Decorator**: Decorator syntax is valid
- [ ] **Semantic Match**: The function's behavior actually fulfills the spec's intent
- [ ] **Complete Implementation**: All acceptance criteria are addressed by implementations
- [ ] **Brick Assignment**: Implementing functions belong to defined bricks

Report:
- List all implementing functions with file paths and line numbers
- Flag any acceptance criteria without corresponding implementation

### 4. Verification Coverage (T → S edges)

Search for `@jig.verifies("{spec-id}")` decorators in test files:

```bash
grep -r '@jig.verifies.*{spec-id}' tests/
```

For each verifying test, verify:

- [ ] **Tests Exist**: At least one test verifies this spec
- [ ] **Correct Decorator**: Decorator syntax is valid
- [ ] **Semantic Match**: The test actually validates the spec's requirements
- [ ] **Criteria Coverage**: Each acceptance criterion has a corresponding test assertion
- [ ] **Test Quality**: Tests are meaningful, not just structural

Report:
- List all verifying tests with file paths and line numbers
- Flag any acceptance criteria without corresponding test coverage

### 5. Execution Coverage (T → F edges)

For each (implementing function, verifying test) pair:

- [ ] **Dynamic Coverage**: The test actually executes the implementing function
- [ ] **Path Coverage**: Critical code paths in the implementation are exercised

To verify, run tests with coverage:
```bash
pytest --cov=src --cov-report=term-missing tests/test_file.py::test_name
```

Report:
- Confirm which implementing functions are covered by which tests
- Flag any "verification gaps" where T → S and F → S exist but T does not cover F

### 6. Triangle Completeness

Assess the overall alignment state:

| State | F → S | T → S | T → F | Assessment |
|-------|-------|-------|-------|------------|
| PERFECT | ✓ | ✓ | ✓ | Fully aligned |
| UNVERIFIED | ✓ | ✗ | - | Needs tests |
| UNTESTED | ✓ | ✓ | ✗ | Tests don't cover impl |
| UNIMPLEMENTED | ✗ | ? | - | Needs implementation |

## Output Format

Produce a structured audit report:

```markdown
# Specification Audit: {spec-id}

## Summary
- **Specification**: {title}
- **Alignment Status**: {PERFECT | UNVERIFIED | UNTESTED | UNIMPLEMENTED}
- **Outcome Alignment**: {ALIGNED | PARTIAL | MISALIGNED | ORPHAN}
- **Upstream Outcome**: {outcome-id or "None"}
- **Implementing Functions**: {count}
- **Verifying Tests**: {count}

## Specification Review
{Quality assessment notes}

## Outcome Alignment
- **Linked Outcome**: {outcome-id} - {outcome title}
- **Outcome Goal**: {brief description of what the outcome aims to achieve}
- **Sibling Specs**: {list of other specs under same outcome}
- **Contribution Assessment**: {how this spec contributes to the outcome}

| Sibling Spec | Title | Status | Contributes To Outcome |
|--------------|-------|--------|------------------------|
| ... | ... | ... | ... |

### Outcome Coverage Analysis
{Assessment of whether the outcome is fully decomposed into specs}
{Flag any gaps where the outcome goal is not addressed by any spec}

## Implementation Analysis
| Function | File | Line | Covers Criteria |
|----------|------|------|-----------------|
| ... | ... | ... | ... |

### Missing Implementation
{List any acceptance criteria without implementation}

## Verification Analysis
| Test | File | Line | Validates Criteria |
|------|------|------|--------------------|
| ... | ... | ... | ... |

### Missing Verification
{List any acceptance criteria without tests}

## Coverage Analysis
| Test | Covers Function | Execution Verified |
|------|-----------------|-------------------|
| ... | ... | ✓/✗ |

### Verification Gaps
{Cases where test claims to verify spec but doesn't execute implementing code}

## Recommendations
1. {Specific actionable items to improve alignment}
2. ...

## Alignment Score
- Outcome Alignment: {ALIGNED | PARTIAL | MISALIGNED | ORPHAN}
- Implementation: {n}/{total} criteria covered
- Verification: {n}/{total} criteria tested
- Execution: {n}/{total} test-function pairs verified
- **Overall**: {percentage}%
```

## Commands to Use

```bash
# Find specification
cat jig/specifications/{spec-id}.md

# Find upstream outcomes that reference this spec
grep -rln 'specifies:' jig/outcomes/ | xargs grep -l '{spec-id}'

# Read outcome to see all sibling specs
cat jig/outcomes/{outcome-id}.md

# Find implementations
grep -rn '@jig.implements.*{spec-id}' src/

# Find verifying tests
grep -rn '@jig.verifies.*{spec-id}' tests/

# Check brick assignment
grep -A5 'units:' jig/bricks.yaml

# Run targeted coverage
pytest --cov=src --cov-report=term-missing -k "test_name"
```

## Key Questions to Answer

1. **Is the spec linked to an outcome?** Does an outcome's `specifies` list include this spec?
2. **Does the spec support the outcome?** Does this spec meaningfully contribute to achieving the outcome's goal?
3. **Is the outcome fully decomposed?** Do all sibling specs together fully address the outcome?
4. **Is the spec implemented?** Are there functions with `@jig.implements("{spec-id}")`?
5. **Is the spec verified?** Are there tests with `@jig.verifies("{spec-id}")`?
6. **Do tests cover implementations?** When verifying tests run, do they execute implementing functions?
7. **Is there semantic alignment?** Do implementations actually fulfill the spec? Do tests actually validate the requirements?
8. **What's missing?** What specific gaps need to be addressed?

## Failure Modes to Detect

### Outcome-Level Failures
- **Orphan Spec**: Spec has no upstream outcome when it logically should belong to one
- **Misaligned Spec**: Spec is listed in outcome but doesn't actually contribute to the outcome's goal
- **Incomplete Decomposition**: Outcome's goal is not fully addressed by its listed specs
- **Outcome Drift**: Outcome was modified but specs weren't updated to match new goal
- **Duplicate Coverage**: Multiple specs under same outcome address identical concerns

### Implementation-Level Failures
- **Orphan Implementation**: Function claims to implement spec that doesn't exist
- **Orphan Verification**: Test claims to verify spec that doesn't exist
- **Hollow Implementation**: Decorator present but function doesn't actually implement the requirement
- **Hollow Verification**: Test has decorator but doesn't actually test the requirement
- **Coverage Gap**: Test verifies spec, function implements spec, but test never calls function
- **Stale Decorator**: Spec was modified but implementation/tests weren't updated
