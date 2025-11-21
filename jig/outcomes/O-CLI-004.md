---
id: O-CLI-004
type: outcome
title: "Actionable Error Messages"
subsystem: cli
created: 2025-11-21
---

# Outcome: Actionable Error Messages

Every error message includes a suggested action. Users can resolve >90% of issues without consulting documentation.

## Value

Error messages that only describe the problem without suggesting a solution create frustration and slow down development. When `validate` reports "subsystem not specified", the user must figure out what to do. When it says "Unassigned nodes (3): O-PERF-001, S-API-001, C-PERF-001" followed by "• Assign nodes to subsystems (add 'subsystem: <name>' to frontmatter)", the user knows exactly what to do.

Actionable error messages enable:
- **Self-service problem solving**: Users fix issues without asking for help
- **Faster iteration**: No need to search docs or wait for answers
- **Better onboarding**: New users learn by doing, not by reading
- **Reduced support burden**: Fewer "how do I fix this?" questions

## Success Metrics

- 100% of warnings include suggested action in Suggestions section
- >90% of users resolve validation errors without consulting docs
- <10% of GitHub issues are "how do I fix error X?"
- User feedback: "Error messages tell me what to do" in >90% of surveys

## Acceptance Criteria

- All warnings paired with actionable suggestions:
  - Warning: "⚠ Orphaned nodes (12): ..."
  - Suggestion: "• Add relationships to 12 orphaned nodes (use 'implements:', 'verifies:', or 'depends_on:')"
- All suggestions are copy-paste ready where possible:
  - Bad: "Add subsystem field"
  - Good: "Add 'subsystem: <name>' to frontmatter"
- All suggestions include specific commands when applicable:
  - "Run 'jigy validate' to check graph consistency"
  - "Use 'jigy graph show O-CLI-001' to inspect node"
- Warnings and Suggestions clearly separated:
  - Warnings section: Problems that exist
  - Suggestions section: Actions to take

## Related

- implements: S-CLI-008 (Validate Command Output Format - suggestions section)
- related: O-CLI-003 (Consistent CLI Output Formatting)
- subsystem: cli

## History

- 2025-11-21: Created during WU0 (known constraint from S011_SUMMARY_cli_output_alignment.md)
