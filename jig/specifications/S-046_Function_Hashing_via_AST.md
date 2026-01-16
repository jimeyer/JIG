---
id: S-046
title: Function Hashing via AST
type: specification
outcomes: [O-017]
---

# Function Hashing via AST

Functions with `@jig.implements` are hashed using AST-normalized representation excluding decorators.

**Acceptance Criteria:**
- Function name included in hash
- Parameters and type annotations included in hash
- Return type annotation included in hash
- Function body (all statements) included in hash
- Decorators EXCLUDED from hash
- Comments excluded (not preserved in AST)
- Whitespace/formatting excluded (normalized by AST)

**Rationale:** Logic changes are detected; formatting changes and decorator changes are ignored. Decorator targets tracked separately in `implements` field.
