---
id: S-047
title: Test Hashing via AST
type: specification
---

# Test Hashing via AST

Tests with `@jig.verifies` are hashed using the same AST-normalized representation as functions (S-046).

**Acceptance Criteria:**
- Same hashing algorithm as S-046 applied to test functions
- Test name, parameters, body included
- Decorators excluded from hash
- Formatting changes do not affect hash

**Rationale:** Tests are code. When test logic changes, the hash changes to signal potential re-verification needed.
