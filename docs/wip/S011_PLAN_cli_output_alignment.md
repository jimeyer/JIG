# CLI Output Formatting Alignment

**Status**: Planning  
**Created**: 2025-11-21  
**Context**: Align output formatting and terminology across all CLI commands

## Problem Statement

The JIG CLI commands (`status`, `validate`, `graph`, etc.) currently use inconsistent formatting and terminology when displaying similar information. This creates a fragmented user experience and makes the tool harder to learn and use.

### Current Inconsistencies

#### 1. Orphaned Nodes Display

**`jigy status` (current):**
```
⚠ Orphaned nodes:
  12 node(s) have no relationships:
    - C-PERF-001
    - O-CLI-001
    - O-CLI-002
    - O-JIG-004
    ...
```

**`jigy validate` (current):**
```
Warnings:
  ⚠ Nodes not referenced in graph index: C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-001, ...
```

**Issues:**
- Different terminology: "Orphaned nodes" vs "Nodes not referenced in graph index"
- Different formatting: newline-separated list vs comma-separated list
- Different message structure: explanatory text vs direct list

#### 2. Node Count Display

**`jigy status`:**
```
✓ Total nodes: 20

Node counts by type:
  constraint: 1
  outcome: 9
  specification: 10
```

**`jigy validate`:**
```
✓ All 20 nodes valid
```

**Issues:**
- `validate` doesn't show breakdown by type
- Different structural approach to presenting the same count

#### 3. Subsystem Display

**`jigy status`:**
```
Subsystems:
  core (9 nodes)
```

**`jigy graph list --subsystem core`:**
```
ID                   Type            Subsystem            Title
------------------------------------------------------------------------------------------
O-JIG-001            outcome         core                 JIG tools run in <1 second...
```

**Issues:**
- Status shows hierarchical tree with counts
- Graph list shows tabular format
- No consistent way to visualize subsystem membership

#### 4. Warning/Error Presentation

**`jigy validate`:**
```
Warnings:
  ⚠ Node O-PERF-001: subsystem not specified
  ⚠ Node S-API-001: subsystem not specified
  ⚠ Nodes not referenced in graph index: C-PERF-001, O-CLI-001, ...
```

**`jigy status`:**
```
Suggestions:
  • 12 node(s) need relationships (add 'implements', 'verifies', or 'depends_on' edges)
  • 3 node(s) need subsystem assignment (add 'subsystem: <name>' to frontmatter)
```

**Issues:**
- `validate` uses "Warnings" for validation issues
- `status` uses "Suggestions" for actionable items
- Both overlap in purpose but different presentation

## Proposed Solution

### Core Principles

1. **Consistency First**: Use the same terminology and formatting across all commands
2. **Scannable Output**: Prefer comma-separated lists for large collections of items
3. **Clear Hierarchy**: Use consistent indentation and symbols (✓, ✗, ⚠, •)
4. **Actionable Language**: Distinguish between errors, warnings, and suggestions
5. **Progressive Disclosure**: Show summary first, details on demand (with --verbose)

### Terminology Standards

| Concept | Standard Term | Notes |
|---------|--------------|-------|
| Nodes without edges | **Orphaned nodes** | Used consistently across all commands |
| Nodes missing subsystem | **Unassigned nodes** | Clear action implied |
| Node counts | **Node summary** | Always show type breakdown |
| Edge types | **implements**, **verifies**, **depends_on** | Lowercase, verb form |
| Relationship direction | **Dependencies** (what this depends on), **Dependents** (what depends on this) | Clear directionality |

### Formatting Standards

#### 1. Node Lists

**For small lists (≤5 items):**
```
⚠ Missing subsystem:
  • O-PERF-001, S-API-001, C-PERF-001
```

**For large lists (>5 items):**
```
⚠ Orphaned nodes (12):
  • C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004, O-PERF-001, O-TEST-001,
    S-API-001, S-CLI-003, S-CLI-004, S-CLI-005, S-JIG-005, S-JIG-006
```

**Rationale:**
- Comma-separated is more scannable for large lists
- Wrapping at reasonable line length (~80 chars) maintains readability
- Count in parentheses provides quick overview

#### 2. Status Indicators

```
✓  Success / Valid state
✗  Error / Invalid state  
⚠  Warning / Needs attention
•  List item / Suggestion
→  Dependency / Forward relationship
←  Dependent / Reverse relationship
```

#### 3. Section Structure

Standard hierarchy for all commands:

```
[COMMAND NAME]

[SUCCESS/ERROR INDICATOR] [Summary line]

[Detail Section 1]:
  [Content with 2-space indent]

[Detail Section 2]:
  [Content with 2-space indent]

[Errors]: (if any)
  ✗ [Error message]

[Warnings]: (if any)
  ⚠ [Warning message]

[Suggestions]: (if any)
  • [Actionable suggestion]
```

### Command-Specific Proposals

#### `jigy status` (Revised)

```
JIG Graph Status

✓ 20 nodes, 8 edges, 1 subsystem

Node summary:
  • Outcomes: 9
  • Specifications: 10
  • Constraints: 1

Subsystems:
  • core (9 nodes)

Warnings:
  ⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004,
    O-PERF-001, O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005,
    S-JIG-005, S-JIG-006
  ⚠ Unassigned nodes (3): O-PERF-001, S-API-001, C-PERF-001

Suggestions:
  • Add relationships to 12 orphaned nodes (use 'implements:', 'verifies:', 
    or 'depends_on:')
  • Assign 3 nodes to subsystems (add 'subsystem: <name>' to frontmatter)
  • Run 'jigy validate' to check graph consistency
```

**Changes:**
- Combined summary line shows total nodes, edges, subsystems
- Node lists use comma-separated format with wrapping
- Clear distinction between "Warnings" (problems) and "Suggestions" (actions)
- Consistent use of "Orphaned nodes" and "Unassigned nodes" terminology
- Node type plurals (Outcomes, Specifications, Constraints)

#### `jigy validate` (Revised)

```
Validating JIG graph...
✓ All 20 nodes valid

Node summary:
  • Outcomes: 9
  • Specifications: 10  
  • Constraints: 1

Warnings:
  ⚠ Unassigned nodes (3): O-PERF-001, S-API-001, C-PERF-001
  ⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, O-CLI-002, O-JIG-004,
    O-PERF-001, O-TEST-001, S-API-001, S-CLI-003, S-CLI-004, S-CLI-005,
    S-JIG-005, S-JIG-006

Suggestions:
  • Run 'jigy status' for detailed graph health metrics
```

**Changes:**
- Added node summary (consistency with status)
- Changed "Nodes not referenced in graph index" → "Orphaned nodes"
- Changed "subsystem not specified" → "Unassigned nodes" with comma list
- Removed redundant per-node warnings, consolidated into single list
- Added suggestion to run status for details

#### `jigy graph show` (Revised)

```
O-JIG-001
Type: outcome
Title: JIG tools run in <1 second for most operations  
Subsystem: core
Status: active

Body:
[First 10 lines of content...]
... (use 'cat jig/outcomes/O-JIG-001.md' for full content)

Dependencies (3):
  → S-JIG-001, S-JIG-002, S-GRAPH-001

Dependents (2):
  ← S-CLI-001, T-JIG-001
```

**Changes:**
- Consistent metadata display order
- Comma-separated lists for dependencies/dependents
- Show counts in section headers
- Clearer file path in truncation message

#### `jigy graph list` (Revised)

Default table format remains unchanged for backward compatibility:

```
jigy graph list --subsystem core

ID                   Type            Subsystem            Title
------------------------------------------------------------------------------------------
O-JIG-001            outcome         core                 JIG tools run in <1 second...
[9 rows shown]
```

Add new `--format compact` option:

```
jigy graph list --subsystem core --format compact

Core subsystem (9 nodes):
  • Outcomes (5): O-JIG-001, O-JIG-002, O-JIG-003, O-JIG-004, O-JIG-005
  • Specifications (4): S-JIG-001, S-JIG-002, S-JIG-003, S-JIG-004
```

#### `jigy graph deps` / `jigy graph impact` (No Change)

Tree format is appropriate for hierarchical dependency visualization:

```
Dependency tree for S-JIG-001:

S-JIG-001
├── O-JIG-001
│   └── S-GRAPH-001
└── O-JIG-002
```

### Verbose Mode Standards

All commands should support `--verbose` flag for detailed output:

```
jigy status --verbose
```

**Verbose additions:**
- Show individual node IDs under subsystems
- Show edge details (edge type, source, target)
- Show full paths to node files
- Show additional metadata (created date, last modified, etc.)

### Implementation Strategy

#### Phase 1: Core Formatting Functions (Sprint 1)

Create shared formatting utilities:

```python
# src/jig/cli/formatting.py

def format_node_list(nodes: list[str], max_line_length: int = 80) -> str:
    """Format node list as comma-separated with wrapping."""
    
def format_section_header(title: str, icon: str, color: str) -> str:
    """Format consistent section headers."""
    
def format_node_summary(node_counts: dict[str, int]) -> list[str]:
    """Format node counts by type."""

def format_orphaned_nodes(nodes: list[str]) -> list[str]:
    """Format orphaned nodes with standard terminology."""
    
def format_unassigned_nodes(nodes: list[str]) -> list[str]:
    """Format nodes missing subsystems."""
```

#### Phase 2: Update Status Command (Sprint 1)

- Refactor `format_status_output()` to use shared formatting
- Update orphaned nodes from newline list to comma list
- Add "Unassigned nodes" section
- Distinguish "Warnings" from "Suggestions"

#### Phase 3: Update Validate Command (Sprint 2)

- Add node summary section
- Change terminology: "Nodes not referenced" → "Orphaned nodes"
- Consolidate per-node warnings into aggregate lists
- Use shared formatting functions

#### Phase 4: Update Graph Commands (Sprint 2)

- Update `graph show` to use comma-separated lists
- Add `--format compact` to `graph list`
- Ensure consistent metadata display order

#### Phase 5: Documentation & Tests (Sprint 3)

- Update all CLI help text
- Update user guide with examples
- Add integration tests for output format validation
- Update CONTRIBUTING.md with formatting standards

## Related Outcomes & Specifications

### Proposed Outcomes

#### O-CLI-003: Consistent CLI Output Formatting

```yaml
id: O-CLI-003
type: outcome
title: CLI commands use consistent output formatting
status: proposed
priority: high
subsystem: cli
```

**Verification:**
- All commands use same terminology for equivalent concepts
- Node lists use comma-separated format when >5 items
- Section structure follows standard hierarchy
- Status indicators (✓, ✗, ⚠, •) used consistently

**Constraints:**
- Output is parseable by standard text processing tools (grep, awk)
- Maintains backward compatibility with existing scripts where possible
- Follows accessibility best practices (color is supplemental, not required)

#### O-CLI-004: Actionable Error Messages

```yaml
id: O-CLI-004
type: outcome
title: CLI errors provide clear next steps
status: proposed
priority: high
subsystem: cli
```

**Verification:**
- Every error message includes suggested action
- Suggestions reference specific commands or file paths
- Users can resolve >90% of issues without consulting docs

**Constraints:**
- Error messages are <100 characters when possible
- Suggestions are command-line ready (copy-paste ready)

#### O-CLI-005: Progressive Disclosure in Output

```yaml
id: O-CLI-005
type: outcome  
title: CLI output uses progressive disclosure
status: proposed
priority: medium
subsystem: cli
```

**Verification:**
- Default output fits on single screen (<50 lines) for typical projects
- `--verbose` flag available on all commands
- Summary information always shown first
- Detail information available on demand

**Constraints:**
- Default output useful for quick status checks
- Verbose output provides debugging-level detail

### Proposed Specifications

#### S-CLI-006: Standard Formatting Library

```yaml
id: S-CLI-006
type: specification
title: Shared CLI formatting utilities
status: proposed
priority: high
subsystem: cli
implements:
  - O-CLI-003
  - O-CLI-004
  - O-CLI-005
```

**Requirements:**
1. Create `src/jig/cli/formatting.py` module
2. Implement node list formatter with wrapping logic
3. Implement section header formatter
4. Implement status indicator constants
5. Add type hints for all functions
6. Test output with various terminal widths (80, 120, 160 cols)

**Interface:**
```python
def format_node_list(
    nodes: list[str], 
    max_line_length: int = 80,
    indent: int = 2
) -> str:
    """Format node IDs as wrapped comma-separated list."""

def format_section(
    title: str,
    content: list[str],
    icon: str = "•",
    color: str | None = None
) -> str:
    """Format a standard output section."""
```

#### S-CLI-007: Status Command Output Format

```yaml
id: S-CLI-007  
type: specification
title: Status command output specification
status: proposed
priority: high
subsystem: cli
implements:
  - O-CLI-003
depends_on:
  - S-CLI-006
```

**Requirements:**
1. Use comma-separated lists for orphaned nodes
2. Add "Unassigned nodes" section
3. Show edge count in summary line
4. Separate "Warnings" and "Suggestions" sections
5. Support `--verbose` for detailed node lists
6. Node type labels use plural form

**Example Output:**
```
JIG Graph Status

✓ 20 nodes, 8 edges, 1 subsystem

Node summary:
  • Outcomes: 9
  • Specifications: 10
  • Constraints: 1

Warnings:
  ⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, ...

Suggestions:
  • Add relationships to 12 orphaned nodes
  • Run 'jigy validate' to check graph consistency
```

#### S-CLI-008: Validate Command Output Format

```yaml
id: S-CLI-008
type: specification
title: Validate command output specification
status: proposed
priority: high
subsystem: cli
implements:
  - O-CLI-003
depends_on:
  - S-CLI-006
```

**Requirements:**
1. Add node summary section
2. Use "Orphaned nodes" terminology (not "Nodes not referenced")
3. Use "Unassigned nodes" terminology (not "subsystem not specified")
4. Consolidate warnings into aggregate lists
5. Use comma-separated format for node lists
6. Support `--verbose` for per-file validation results

**Example Output:**
```
Validating JIG graph...
✓ All 20 nodes valid

Node summary:
  • Outcomes: 9
  • Specifications: 10
  • Constraints: 1

Warnings:
  ⚠ Orphaned nodes (12): C-PERF-001, O-CLI-001, ...
  ⚠ Unassigned nodes (3): O-PERF-001, S-API-001, C-PERF-001
```

#### S-CLI-009: Graph Command Output Format

```yaml
id: S-CLI-009
type: specification
title: Graph command output specification
status: proposed
priority: medium
subsystem: cli
implements:
  - O-CLI-003
depends_on:
  - S-CLI-006
```

**Requirements:**
1. `graph show`: Use comma-separated lists for dependencies/dependents
2. `graph show`: Show relationship counts in section headers
3. `graph list`: Add `--format compact` option for comma-separated output
4. `graph deps/impact`: Keep tree format (appropriate for hierarchy)
5. Consistent metadata display order: ID → Type → Title → Subsystem → Status

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_cli_formatting.py

def test_format_node_list_small():
    """Small lists stay on one line."""
    nodes = ["O-JIG-001", "O-JIG-002", "S-JIG-001"]
    result = format_node_list(nodes)
    assert result == "O-JIG-001, O-JIG-002, S-JIG-001"

def test_format_node_list_wrapping():
    """Large lists wrap at max_line_length."""
    nodes = [f"O-JIG-{i:03d}" for i in range(20)]
    result = format_node_list(nodes, max_line_length=80)
    lines = result.split("\n")
    assert all(len(line) <= 80 for line in lines)
    assert len(lines) > 1

def test_format_orphaned_nodes_terminology():
    """Uses 'Orphaned nodes' terminology."""
    nodes = ["O-JIG-001", "S-JIG-001"]
    result = format_orphaned_nodes(nodes)
    assert "Orphaned nodes" in result
    assert "not referenced" not in result.lower()
```

### Integration Tests

```python
# tests/integration/test_cli_output_alignment.py

def test_status_uses_comma_separated_lists(tmp_path):
    """Status command uses comma-separated node lists."""
    # Setup graph with orphaned nodes
    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    # Should have comma-separated list, not newline list
    assert re.search(r"O-[A-Z]+-\d+, O-[A-Z]+-\d+", result.output)

def test_validate_uses_orphaned_terminology(tmp_path):
    """Validate command uses 'Orphaned nodes' terminology."""
    result = runner.invoke(cli, ["validate"])
    assert result.exit_code == 0
    if "orphaned" in result.output.lower():
        assert "Orphaned nodes" in result.output
        assert "not referenced" not in result.output.lower()

def test_commands_use_consistent_node_summary(tmp_path):
    """Status and validate show same node summary format."""
    status_result = runner.invoke(cli, ["status"])
    validate_result = runner.invoke(cli, ["validate"])
    
    # Both should show "Outcomes: N" format
    assert re.search(r"Outcomes: \d+", status_result.output)
    assert re.search(r"Outcomes: \d+", validate_result.output)
```

### Acceptance Criteria

- [ ] All proposed formatting functions implemented in `formatting.py`
- [ ] Status command updated with comma-separated lists
- [ ] Status command distinguishes Warnings vs Suggestions
- [ ] Validate command uses "Orphaned nodes" terminology
- [ ] Validate command uses "Unassigned nodes" terminology
- [ ] Validate command shows node summary
- [ ] Graph show command uses comma-separated dependencies
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Documentation updated with examples
- [ ] User guide includes output formatting conventions

## Migration Notes

### Breaking Changes

**Minimal breaking changes expected:**

1. **Status command**: Orphaned nodes change from newline list to comma list
   - **Impact**: Scripts parsing orphaned node list line-by-line will break
   - **Mitigation**: Add `--format` flag to support both formats during transition
   
2. **Validate command**: Warning messages consolidated
   - **Impact**: Scripts counting warning lines will get different counts
   - **Mitigation**: Add machine-readable `--format json` output

### Backward Compatibility

**Maintain compatibility where possible:**

1. Keep `graph list` table format as default
2. Add new formats (`compact`, `json`) as opt-in
3. Preserve exit codes (0=success, 1=errors, 3=not initialized)
4. Keep `--verbose` flag behavior consistent

### Deprecation Timeline

**Phase 1 (v0.2.0)**: Introduce new formatting
- Add new formatting alongside old
- Warnings for deprecated formats
- Update documentation

**Phase 2 (v0.3.0)**: Default to new formatting
- New formatting is default
- Old formatting available via `--legacy` flag
- Update all examples

**Phase 3 (v0.4.0)**: Remove legacy formatting
- Remove `--legacy` flag
- Remove old formatting code
- Clean up tests

## Open Questions

1. **Should we support machine-readable output (JSON/YAML)?**
   - Pros: Makes scripting easier, avoids parsing text
   - Cons: Adds complexity, duplicates formatting logic
   - **Proposal**: Add `--format json` to status/validate commands in Phase 2

2. **Should orphaned nodes show relationship type needed?**
   - Example: "O-JIG-001 (needs implements:)"
   - Pros: More actionable
   - Cons: More complex logic, longer output
   - **Proposal**: Defer to Phase 3, add to --verbose mode first

3. **Should we enforce line length limits?**
   - Current proposal: 80 chars with wrapping
   - Alternative: Detect terminal width dynamically
   - **Proposal**: Start with 80 chars, add dynamic in Phase 3

4. **Should subsystem display be hierarchical or flat?**
   - Status currently supports both (`--flat` flag)
   - Validate doesn't show subsystems at all
   - **Proposal**: Hierarchical by default, keep --flat for compatibility

## Success Metrics

### Qualitative
- User feedback indicates output is "clear" and "consistent"
- New contributors can understand output without asking questions
- Documentation examples are copy-paste ready

### Quantitative
- 100% of CLI commands use shared formatting library
- <5% of output lines exceed 80 characters (excluding tables)
- 0 terminology inconsistencies across commands
- >95% test coverage for formatting functions

## References

- Current `status.py` implementation: `/src/jig/cli/status.py` (lines 129-245)
- Current `validate.py` implementation: `/src/jig/cli/validate.py`
- Current `graph.py` implementation: `/src/jig/cli/graph.py`
- Related outcomes: O-CLI-001 (performance), O-CLI-002 (formats)
- Related specs: S-CLI-003, S-CLI-004, S-CLI-005

## Next Steps

1. **Review & Refine**: Get feedback on this proposal from maintainers
2. **Create Tickets**: Break down into implementable tasks
3. **Implement Phase 1**: Core formatting library
4. **Iterate**: Gather user feedback, adjust as needed
5. **Document**: Update user guide with formatting conventions

