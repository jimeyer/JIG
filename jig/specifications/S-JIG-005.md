---
id: S-JIG-005
type: specification
title: "Test nodes discovered via @jig annotations"
subsystem: core
created: 2025-11-20
---

# Specification: Test nodes discovered via @jig annotations

Test nodes (T-XXX) represent executable tests that verify outcomes and specifications. In the OSTCX model, T nodes exist in the intent graph but are discovered from `@jig` annotations in test code, not from markdown files.

## Requirements

### Functional Requirements
- Test nodes (T-XXX) are discovered by scanning test code for `@jig T-XXX` annotations
- Test nodes contain `verifies:` relations to connect to outcomes/specifications
- Test nodes capture metadata: test name, file path, line number, verification targets
- Test annotations follow standard format: `@jig T-XXX verifies: O-XXX, S-XXX`

### Non-Functional Requirements
- Discovery: Fast annotation scanning (target: <100ms for 1000 test files)
- Storage: No markdown files in jig/tests/ directory
- Source of truth: The test implementation code, not documentation

### Implementation Approach
- Parser scans test files for `@jig T-XXX` comments/decorators
- Extracted test nodes added to graph during load
- Relations parsed from `verifies:` clause
- Future feature: `jig sync` command to discover and update test nodes

## Rationale

Tests are code, not intent documents. The OSTCX model separates:
- **Markdown nodes (O/S/X)**: Timeless intent and system properties
- **Annotation nodes (T/C)**: Executable reality tied to code

Test nodes represent "Empirical truth (verify)" and must stay close to the implementation. Storing tests as markdown files creates drift risk and maintenance burden. Annotations keep the source of truth in the test code itself.

This aligns with JIG v7 architecture principle: Tests are discovered, not declared.

## Acceptance Criteria

- No `type: test` validation in validator.py
- No test_template.md in templates/
- No jig/tests/ directory for markdown files
- Future `jig sync` discovers test annotations correctly
- Test nodes appear in graph with proper relations to O/S nodes

## Related

- implements: O-JIG-002 (JIG v7 OSTCX model implemented)
- subsystem: core

## History

- 2025-11-20: Created during WU0 (S008 PLAN, remove-tests-directory branch)

