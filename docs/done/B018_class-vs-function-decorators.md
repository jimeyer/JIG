# B018: Class vs Function Decorators

**Status:** Reference
**Date:** 2025-12-10

---

## Summary

Decorate **functions and methods**, not classes. The S-F-T alignment model measures relationships between Functions (F) and Specifications (S), not Classes (C) and Specifications.

---

## The S-F-T Triangle

From J017 and A001, alignment is measured between three node types:

```
         S (Specification)
        / \
       /   \
implements  verifies
     /       \
    F --------> T
      covers
```

- **F → S** (implements): Functions implement specifications
- **T → S** (verifies): Tests verify specifications
- **T → F** (covers): Tests execute functions

The fundamental unit is the **Function** (F), not the class.

---

## What Happens When You Decorate a Class

```python
@jig.implements("S-001")
class TokenValidator:
    def validate(self): ...
    def refresh(self): ...
```

| Artifact | Result |
|----------|--------|
| Class node | `C-module.TokenValidator` with `implements: ["S-001"]` |
| Method nodes | `F-module.TokenValidator.validate` with `implements: []` |
| | `F-module.TokenValidator.refresh` with `implements: []` |
| Alignment queries | Look for **F → S** edges, find none |
| Validation | Class decorators are **not validated** for reference integrity |

**Result:** The decorator is captured but has no effect on alignment measurement.

---

## What Happens When You Decorate Methods

```python
class TokenValidator:
    @jig.implements("S-001")
    def validate(self): ...

    @jig.implements("S-001")
    def refresh(self): ...
```

| Artifact | Result |
|----------|--------|
| Method nodes | `F-module.TokenValidator.validate` with `implements: ["S-001"]` |
| | `F-module.TokenValidator.refresh` with `implements: ["S-001"]` |
| Alignment queries | Find **F → S** edges, report spec as implemented |
| Validation | Decorator references are validated |

**Result:** Alignment is measured correctly.

---

## Recommendation

### For `@jig.implements`

Decorate the specific functions/methods that implement a specification:

```python
# GOOD - explicit, validated, measured
class TokenValidator:
    @jig.implements("S-001")
    def validate(self, token: str) -> bool:
        """Validate token format and expiration."""
        ...

    @jig.implements("S-002")
    def refresh(self, token: str) -> str:
        """Refresh an expiring token."""
        ...
```

### For `@jig.verifies`

Decorate the specific test methods that verify a specification:

```python
# GOOD - explicit, validated, measured
class TestTokenValidation:
    @jig.verifies("S-001")
    def test_expired_token_rejected(self):
        """Verify expired tokens are rejected."""
        ...

    @jig.verifies("S-001")
    def test_valid_token_accepted(self):
        """Verify valid tokens are accepted."""
        ...
```

---

## Why Not Classes?

1. **Semantic ambiguity**: Does `@jig.implements("S-001")` on a class mean all methods implement it? Some methods? The class as a concept?

2. **Granularity mismatch**: Different methods often implement different specifications. A `TokenValidator` class might have `validate()` implementing S-001 and `refresh()` implementing S-002.

3. **Alignment measurement**: The graph queries look for F → S edges. Class decorators create C → S edges that aren't queried.

4. **Validation gap**: Function decorators are validated for reference integrity. Class decorators are not.

---

## References

- **A001:** Core Artifacts Contract (defines S-F-T triangle)
- **J017:** JIG Concept v9 (alignment model)
