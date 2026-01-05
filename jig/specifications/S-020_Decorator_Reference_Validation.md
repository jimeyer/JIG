---
id: S-020
title: Decorator Reference Validation
type: specification
---

# Decorator Reference Validation

Validate `@jig.implements` and `@jig.verifies` decorators reference valid specification and outcome IDs.

**Acceptance Criteria**:
- Parse Python source files using AST to find @jig decorators
- Validate `@jig.implements("S-XXX")` references existing specification IDs
- Validate `@jig.verifies("S-XXX")` and `@jig.verifies("O-XXX")` reference existing IDs
- Validate decorator arguments are string literals (not variables or expressions)
- Support multiple specs in single decorator: `@jig.implements("S-001", "S-002")`
- Error messages include file path, line number, and invalid reference
- Report decorator syntax errors (invalid arguments, non-string references)

**Rationale**: Prevents broken references that would cause graph generation failures. Catches typos and stale references early.

**References**: A001 §10 (Validation Rules), AG026 (Linter Proposal)
