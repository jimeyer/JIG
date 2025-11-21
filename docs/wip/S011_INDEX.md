# S011: CLI Output Alignment

**Status**: Proposed  
**Created**: 2025-11-21  
**Issue**: Inconsistent formatting and terminology across CLI commands

## Documents in This Series

### 📋 [S011_SUMMARY_cli_output_alignment.md](./S011_SUMMARY_cli_output_alignment.md)
**Start here** - Executive summary with key changes and quick reference card.

- Problem statement
- Core changes (5 key improvements)
- Before/after side-by-side
- Standard terminology table
- Quick reference card
- Next actions

**Best for**: Getting overview, making decisions, quick reference

---

### 📐 [S011_PLAN_cli_output_alignment.md](./S011_PLAN_cli_output_alignment.md)
**Complete specification** - Detailed planning, implementation strategy, and requirements.

- Current state analysis
- Proposed solution with rationale
- Formatting standards specification
- Command-specific proposals
- Implementation phases (4 sprints)
- Proposed outcomes & specs (O-CLI-003 through O-CLI-005, S-CLI-006 through S-CLI-009)
- Testing strategy
- Migration notes
- Open questions

**Best for**: Implementation, detailed requirements, architecture decisions

---

### 👀 [S011_EXAMPLES_cli_output_before_after.md](./S011_EXAMPLES_cli_output_before_after.md)
**Visual guide** - Side-by-side examples of current vs proposed output.

- `jigy status` before/after
- `jigy validate` before/after
- `jigy graph show` before/after
- `jigy graph list --format compact` (new feature)
- Terminology comparison table
- Formatting patterns reference
- Verbose mode examples
- Implementation checklist

**Best for**: Understanding changes visually, UX review, documentation examples

---

## Quick Links

### For Reviewers
1. Read **SUMMARY** for overview
2. Review **EXAMPLES** to see visual changes
3. Check **PLAN** for implementation details

### For Implementers
1. Read **PLAN** for requirements
2. Use **EXAMPLES** as reference during coding
3. Check **SUMMARY** for quick terminology lookup

### For Users
1. Read **SUMMARY** for what's changing
2. Use **EXAMPLES** to see before/after
3. Check **SUMMARY** "Migration" section if you have scripts

---

## Key Changes Summary

| Change | Commands Affected | Impact |
|--------|------------------|--------|
| Use "Orphaned nodes" terminology | status, validate | Consistency |
| Comma-separated node lists | status, validate, graph show | Scannability |
| Add "Unassigned nodes" section | status, validate | Clarity |
| Separate Warnings/Suggestions | status, validate | Structure |
| Add node summary to all | validate, graph | Consistency |
| Show counts in parentheses | All | Quick scanning |

---

## Proposed New Outcomes

- **O-CLI-003**: Consistent CLI Output Formatting
- **O-CLI-004**: Actionable Error Messages  
- **O-CLI-005**: Progressive Disclosure in Output

## Proposed New Specifications

- **S-CLI-006**: Standard Formatting Library
- **S-CLI-007**: Status Command Output Format
- **S-CLI-008**: Validate Command Output Format
- **S-CLI-009**: Graph Command Output Format

---

## Implementation Timeline

- **Phase 1** (Week 1): Core formatting library
- **Phase 2** (Week 2): Update status & validate
- **Phase 3** (Week 3): Update graph commands
- **Phase 4** (Week 4): Documentation & migration

---

## Current CLI Output Examples

### `jigy status` (as of 2025-11-21)

```
JIG Graph Status

✓ Total nodes: 20

Node counts by type:
  constraint: 1
  outcome: 9
  specification: 10

Subsystems:
  core (9 nodes)

⚠ Orphaned nodes:
  12 node(s) have no relationships:
    - C-PERF-001
    - O-CLI-001
    - O-CLI-002
    [... 9 more ...]
```

### `jigy validate` (as of 2025-11-21)

```
Validating JIG graph...
✓ All 20 nodes valid

Warnings:
  ⚠ Node O-PERF-001: subsystem not specified
  ⚠ Node S-API-001: subsystem not specified
  ⚠ Node C-PERF-001: subsystem not specified
  ⚠ Nodes not referenced in graph index: C-PERF-001, O-CLI-001, ...
```

**Issues identified**:
- ❌ Different terminology ("Orphaned nodes" vs "Nodes not referenced")
- ❌ Different formatting (newlines vs commas)
- ❌ Repetitive warnings (3 lines for subsystem, could be 1)
- ❌ Validate missing node summary

---

## Related Files

### Implementation
- `/src/jig/cli/status.py` - Status command
- `/src/jig/cli/validate.py` - Validate command
- `/src/jig/cli/graph.py` - Graph commands
- `/src/jig/cli/formatting.py` - **TO CREATE** (shared formatting)

### Tests
- `/tests/integration/test_status_command.py`
- `/tests/integration/test_validate_command.py`
- `/tests/integration/test_graph_*.py`
- `/tests/unit/test_cli_formatting.py` - **TO CREATE**

### Documentation
- `/docs/user-guide/` - User-facing docs
- `/CONTRIBUTING.md` - Contributor guidelines

---

## Decision Log

### 2025-11-21: Initial Proposal
- **Decision**: Use comma-separated lists for >5 items
- **Rationale**: More scannable, less vertical space, matches validate's current approach
- **Alternative considered**: Keep newline lists
- **Rejected because**: Takes too much space for large lists (12+ items)

### 2025-11-21: Terminology Choice
- **Decision**: "Orphaned nodes" (not "Nodes not referenced in graph index")
- **Rationale**: Shorter, clearer, already used by status command
- **Alternative considered**: "Unreferenced nodes"
- **Rejected because**: Less clear, doesn't convey lack of relationships

### 2025-11-21: Warning Aggregation
- **Decision**: Aggregate per-node warnings into single list
- **Rationale**: Reduces noise, matches other warning formats
- **Example**: "Unassigned nodes (3): O-PERF-001, S-API-001, C-PERF-001"
- **Alternative considered**: Keep per-node warnings
- **Rejected because**: Too verbose for large projects

---

## Open Questions

1. **Should we support machine-readable output (JSON/YAML)?**
   - Discussion in PLAN, Section "Open Questions"
   - Proposal: Add in Phase 2 (`--format json`)

2. **Should we enforce 80-char line length or detect terminal width?**
   - Discussion in PLAN, Section "Open Questions"  
   - Proposal: Start with 80 chars, add dynamic detection in Phase 3

3. **Should orphaned nodes show which relationship type they need?**
   - Discussion in PLAN, Section "Open Questions"
   - Proposal: Add to --verbose mode in Phase 3

---

## Feedback Welcome

Please review and provide feedback on:

1. **Terminology**: Are "Orphaned nodes" and "Unassigned nodes" clear?
2. **Formatting**: Is comma-separated better than newline-separated?
3. **Breaking changes**: Is the migration plan acceptable?
4. **Proposed outcomes/specs**: Do they capture requirements?
5. **Timeline**: Is 4-week implementation realistic?

---

**Last Updated**: 2025-11-21  
**Author**: Analysis based on current CLI implementation  
**Status**: Awaiting review and feedback

