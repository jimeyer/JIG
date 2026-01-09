---
id: O-016
title: CI and Tooling Integration
type: outcome
theme: [Continuity]
supports_goals: [G-003]
specifies: [S-026, S-093, S-094]
---

# CI and Tooling Integration

**Value:** Validation integrates seamlessly into CI pipelines and editor tooling via machine-parseable output, enabling automated quality gates and real-time feedback.

**Acceptance:** `jigy validate --format json` produces structured, parseable output with error codes, file locations, and severity levels that CI systems and editors can consume programmatically.

## AI Agent Benefit

Agents parse JSON validation output for automated remediation. Structured error codes enable agents to categorize errors and apply appropriate fixes without natural language parsing. Without JSON output, agents must parse human-readable text - a fragile, error-prone approach that breaks when format changes.

## Rationale

Human-readable terminal output is excellent for interactive development but inadequate for automation. CI systems need structured data to:
- Parse validation results programmatically
- Create inline code comments on PRs
- Block merges when validation fails
- Track validation metrics over time

Editor integrations need structured output to:
- Show inline error squiggles at specific lines
- Provide quick-fix suggestions
- Display validation status in real-time

By providing a machine-parseable JSON format alongside human-readable output, we enable the jig ecosystem to extend beyond CLI usage into automated workflows and IDE integrations.

## Success Criteria

The CI integration must:
1. Provide `--format json` flag on all validate commands
2. Output valid, parseable JSON with no syntax errors
3. Include structured error codes for programmatic handling (e.g., `MISSING_REQUIRED_FIELD`, `INVALID_SPEC_REFERENCE`)
4. Include file paths, line numbers, error messages, and severity for each error
5. Include summary statistics: `total_errors`, `total_warnings`, validation status per phase
6. Maintain schema consistency across all validation commands
7. Default to human-readable format (no breaking changes to existing workflows)
8. Complete with same performance as human-readable format

## Specified By

This outcome is delivered through:
- **S-026**: JSON output format for CI integration with structured error codes and consistent schema

## Constitution Linkage

This outcome serves: **Part IV: Continuity** - CI and Tooling Integration
Enables: CI quality gates, editor integration, automated remediation
Without this: Validation results are human-only; automation requires fragile text parsing
