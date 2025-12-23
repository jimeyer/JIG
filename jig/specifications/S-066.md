---
id: S-066
title: T→F Edge Collection via Coverage
type: specification
---

# T→F Edge Collection via Coverage

The coverage audit determines which tests execute which functions by running
the test suite with coverage instrumentation.

**Acceptance Criteria:**
- Running `jigy audit coverage` executes tests with line-level coverage tracking
- For each test, the system identifies which functions had lines executed
- A T→F edge exists when test T executed at least one line of function F
- Edge data includes test ID, function ID, and coverage result

**Rationale:** T→F relationships are objective facts determined by execution,
unlike F→S and T→S which require semantic judgment.
