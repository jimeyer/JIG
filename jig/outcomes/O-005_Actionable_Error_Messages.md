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
- **S-018**: Specification File Validation - validates spec files with actionable error messages
- **S-019**: Outcome File Validation - validates outcome files with actionable error messages
- **S-020**: Decorator Reference Validation - validates decorators with file/line reporting
- **S-021**: Brick Definition Validation - validates bricks with clear error messages
- **S-022**: Brick Partition Validation - reports partition violations with function-level detail

## Constitution Linkage

This outcome serves: **Part III: Validation** - Actionable Errors
Enables: Self-serve error resolution, AI agent auto-fixing, reduced documentation lookups
Without this: Users cannot fix errors without investigation; agents cannot auto-remediate
