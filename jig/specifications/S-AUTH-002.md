---
id: S-AUTH-002
type: specification
title: JWT token refresh mechanism (test fixture)
subsystem: test-fixtures
status: test-fixture
created: 2025-11-21
---

# Specification: JWT Token Refresh (Test Fixture)

## Purpose

This is a test fixture specification used in annotation parsing examples. It demonstrates multi-relationship annotations (code implementing multiple specifications).

## Context

Referenced in annotation scanner unit tests as an example of:
- Multiple `implements:` targets in a single annotation
- Comma-separated relationship syntax
- Metadata field combinations

**This is a documentation/testing artifact, not a production specification.**

## Example Usage

From test fixtures:

```python
# @jig C-AUTH-002 implements:S-AUTH-001,S-AUTH-002 subsystem:auth
def validate_token(self, token: str) -> Claims:
    """Validates JWT and extracts claims"""
```

Demonstrates a single code node implementing multiple specifications.

## References

- Tests: `tests/unit/test_annotation_scanner.py` (lines 31-39)
- Documentation: JIG-Concept-v6.1.md annotation examples
- Related: S-AUTH-001 (companion example)
