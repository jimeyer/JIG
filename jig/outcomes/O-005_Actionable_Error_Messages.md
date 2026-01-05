---
id: O-005
title: Actionable Error Messages
type: outcome
theme: [Validation]
supports_goals: [G-002, G-003]
specifies: [S-018, S-019, S-020, S-021, S-022]
---

# Actionable Error Messages

**Value:** Error messages include file paths, line numbers, and specific remediation steps, enabling developers to fix issues without reading documentation.

**Acceptance:** Developers resolve 80%+ of validation issues from error messages alone without external lookups.

## AI Agent Benefit

Agents can parse structured error messages to auto-fix common issues. File paths and line numbers enable precise edits; remediation guidance eliminates guesswork. Without actionable errors, agents must guess at fixes or escalate to humans, breaking autonomous workflows.

## Rationale

Error messages are communication. A cryptic error like "validation failed" communicates nothing useful. The developer must investigate, read documentation, and experiment to find the problem. This friction discourages validation use.

Actionable error messages front-load the investigation. They answer: What file? What line? What's wrong? How to fix it? A message like "jig/specifications/S-001.md:3 - frontmatter missing required field 'id'" is immediately actionable - no documentation lookup required.

File paths must be absolute or project-relative so developers can navigate directly. Line numbers must be accurate so developers see the problem immediately. Remediation hints must be specific - not "fix the error" but "add 'id: S-001' to frontmatter."

For AI agents, this structure is even more valuable. Agents can parse the error, locate the file and line, understand the problem, and apply the fix - all without human intervention. Unstructured error messages break this automation loop.

## Success Criteria

The error reporting system must:
1. Include file path for every file-related error
2. Include line number when the error location is determinable
3. Describe what's wrong in plain language
4. Suggest how to fix the error when the remedy is clear
5. Group errors by validation phase for scannability
6. Provide summary counts for quick assessment

## Specified By

This outcome is delivered through:
- **S-018**: Error Message File Paths - includes paths in all file errors
- **S-019**: Error Message Line Numbers - includes line numbers when determinable
- **S-020**: Error Description Clarity - plain language problem descriptions
- **S-021**: Remediation Suggestions - actionable fix guidance
- **S-022**: Error Grouping and Summary - organized error presentation

## Constitution Linkage

This outcome serves: **Part III: Validation** - Actionable Errors
Enables: Self-serve error resolution, AI agent auto-fixing, reduced documentation lookups
Without this: Users cannot fix errors without investigation; agents cannot auto-remediate
