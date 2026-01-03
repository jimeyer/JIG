# B007: Unified Rebuild Command

**Status:** ✅ Complete
**Author:** AI Assistant
**Date:** 2025-12-03
**Completed:** 2025-12-03

## Problem Statement

Developers currently run four separate commands to rebuild and validate the entire JIG system:

```bash
jigy validate
jigy impl rebuild
jigy intent rebuild
jigy layers
```

This is repetitive and error-prone. Users want a single command that runs the complete workflow.

## Goal

Create a new top-level CLI command `jigy rebuild` that orchestrates all four workflow commands in sequence with proper error handling and progress output.

## Proposed Solution

### Command Name

**`jigy rebuild`** - Clear, matches the two main "rebuild" subcommands it orchestrates

### Command Behavior

```bash
jigy rebuild [--project-root PATH] [--verbose]
```

**Workflow Steps:**
1. Validate all JIG artifacts (`validate_full_command`)
2. Rebuild implementation graph (`build_graph`)
3. Rebuild intent graph (`generate_intent_graph`)
4. Display layer structure (`layers_command`)

**Error Handling:**
- Exit immediately if any step fails
- Display clear error message indicating which step failed
- Return appropriate exit code

**Output:**
- Show progress messages between steps
- Display output from each command as it runs
- Show summary at completion

### Implementation Overview

**File:** `src/jig/cli/main.py`

**Changes Required:**

1. **Add new command function** (~50-80 lines):
```python
@cli.command()
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Root directory of the project (default: current directory)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def rebuild(project_root: Path, verbose: bool) -> None:
    """Run complete JIG rebuild workflow.

    Executes all standard JIG commands in sequence:
    1. Validate artifacts
    2. Rebuild implementation graph
    3. Rebuild intent graph
    4. Display layer structure

    Example:
        jigy rebuild
        jigy rebuild --verbose
    """
    # Implementation here
```

2. **Orchestrate existing functions:**
   - Import from `jig.cli.validate`: `validate_full_command`
   - Import from `jig.impl_graph.builder`: `build_graph`
   - Import from `jig.intent_graph.generator`: `generate_intent_graph`
   - Import from `jig.cli.layers`: `layers_command`

3. **Error handling pattern:**
```python
# Step 1: Validate
click.echo("=" * 60)
click.echo("Step 1/4: Validating JIG artifacts...")
click.echo("=" * 60)
exit_code = validate_full_command(project_root, "human")
if exit_code != 0:
    click.echo("\n✗ Validation failed. Stopping rebuild.", err=True)
    sys.exit(exit_code)

# Step 2: Implementation graph
click.echo("\n" + "=" * 60)
click.echo("Step 2/4: Rebuilding implementation graph...")
click.echo("=" * 60)
try:
    # Call build_graph with appropriate parameters
    # Handle success/failure
except Exception as e:
    click.echo(f"\n✗ Implementation rebuild failed: {e}", err=True)
    sys.exit(1)

# ... repeat for steps 3 and 4
```

4. **Configuration management:**
   - Reuse default paths from individual commands
   - Pass `verbose` flag where applicable
   - Use consistent output formatting

## Work Unit Breakdown

### WU0: Create Intent (if needed)
- **Skip** - This is a tooling feature, no specifications needed
- OR create minimal spec if desired for completeness

### WU1: Implement `jigy rebuild` command
**Effort:** 30-45 minutes
**Status:** ✅ Complete

**Tasks:**
- [x] Add `rebuild()` function to `src/jig/cli/main.py`
- [x] Add required imports
- [x] Implement step 1: validate
- [x] Implement step 2: impl rebuild
- [x] Implement step 3: intent rebuild
- [x] Implement step 4: layers
- [x] Add progress messages between steps
- [x] Test manually: `jigy rebuild`

**Acceptance:**
- [x] Command runs all 4 steps in order
- [x] Stops on first error
- [x] Shows clear progress output
- [x] Returns appropriate exit codes

**Implementation Notes:**
- Added 94-line `rebuild()` function at line 39 in `src/jig/cli/main.py`
- Function orchestrates all four workflow commands with clear step separators
- Proper error handling with early exit on any failure
- Shows success summary at completion

### WU2: Add integration test
**Effort:** 15-20 minutes
**Status:** ✅ Complete

**Tasks:**
- [x] Add test in `tests/integration/test_cli.py`
- [x] Test successful execution path
- [x] Test early exit on validation failure
- [x] Verify all four commands are called

**Test Coverage:**
- `test_cli_rebuild_success` - Full workflow execution with all steps
- `test_cli_rebuild_with_verbose` - Verbose flag functionality
- `test_cli_rebuild_stops_on_validation_error` - Early exit on error
- `test_cli_rebuild_help` - Help documentation
- Added `full_project` fixture for complete test project setup

## Implementation Details

### Function Signatures to Reuse

From existing code at `src/jig/cli/main.py`:

1. **Validation** (line 58):
```python
validate_full_command(project_root: Path, output_format: str) -> int
```

2. **Implementation rebuild** (lines 146-166):
```python
graph = build_graph(
    project_root=project_root,
    source_dir=None,  # Uses default
    output_path=None,  # Uses default
    exclude_patterns=None,
    verbose=verbose,
    strict=True,
    include_timestamp=True,
)
```

3. **Intent rebuild** (lines 206-215):
```python
output_path, node_count, edge_count = generate_intent_graph(
    project_root=project_root,
    output_path=None,  # Uses default
    include_timestamp=True,
)
```

4. **Layers display** (line 343):
```python
layers_command(project_root: Path, summary: bool, verbose: bool) -> int
```

### Default Parameters

Use consistent defaults matching individual commands:
- `output_format="human"` for validation
- `source_dir=None` (auto-detect)
- `output_path=None` (use defaults)
- `exclude_patterns=None`
- `strict=True`
- `include_timestamp=True`
- `summary=False` for layers
- `skip_validation=False` for impl rebuild

### Output Format Example

```
==============================================================
Step 1/4: Validating JIG artifacts...
==============================================================
✓ Intent validation passed
✓ Brick validation passed

==============================================================
Step 2/4: Rebuilding implementation graph...
==============================================================
Generating implementation graph for /Users/jmeyer/Code/jig

✓ Implementation graph generated successfully:
  - Nodes: 142
  - Edges: 256
  - Output: jig/generated/implementation-graph.ndjson

==============================================================
Step 3/4: Rebuilding intent graph...
==============================================================
Generating intent graph for /Users/jmeyer/Code/jig

✓ Intent graph generated successfully:
  - Nodes: 23
  - Edges: 18
  - Output: jig/generated/intent-graph.ndjson

==============================================================
Step 4/4: Displaying layer structure...
==============================================================

Layer 0 (Foundation)
└── B-graph (graph-index, subsystems)
    2 functions

Layer 1 (Core)
└── B-core (validation, impl_graph, intent_graph)
    84 functions

==============================================================
✓ Complete! All JIG artifacts rebuilt successfully.
==============================================================
```

## Testing Strategy

### Manual Testing
```bash
# Test successful execution
jigy rebuild

# Test with verbose flag
jigy rebuild --verbose

# Test with custom project root
jigy rebuild --project-root ~/other-project

# Test early exit (introduce validation error first)
# Edit jig/bricks.yaml to create error
jigy rebuild
# Should stop after step 1 with error message
```

### Integration Test (if implemented)
```python
def test_rebuild_command_success(tmp_project):
    """Test that rebuild runs all four steps."""
    runner = CliRunner()
    result = runner.invoke(cli, ['rebuild', '--project-root', str(tmp_project)])

    assert result.exit_code == 0
    assert "Step 1/4: Validating" in result.output
    assert "Step 2/4: Rebuilding implementation" in result.output
    assert "Step 3/4: Rebuilding intent" in result.output
    assert "Step 4/4: Displaying layer" in result.output
    assert "Complete!" in result.output

def test_rebuild_stops_on_validation_error(tmp_project):
    """Test that rebuild stops on validation failure."""
    # Create invalid artifact
    # Run rebuild
    # Verify it stops at step 1
```

## Documentation Updates

### Update CLI Help Text

The command will automatically appear in `jigy --help` output:

```
Commands:
  impl      Implementation graph commands.
  intent    Intent graph commands.
  layers    Visualize and manage brick layer structure.
  rebuild   Run complete JIG rebuild workflow.
  validate  Validate JIG artifacts.
```

### Update agents/contextJIG.md (line 146)

Add to CLI Commands section:
```markdown
## CLI Commands

```bash
jigy rebuild        # Run complete workflow (validate + rebuild all + layers)
jigy impl rebuild   # Generate implementation graph from code
jigy intent rebuild # Generate intent graph from JIG artifacts
jigy validate       # Check references, partition, layers
jigy layers         # Show layer structure
```
```

## Risks and Considerations

### Low Risk
- Very straightforward implementation
- Reuses existing, tested functions
- No new functionality, just orchestration

### Potential Issues
1. **Long runtime**: All four commands might take time on large projects
   - Mitigation: Show progress between steps

2. **Verbose output handling**: Some commands use click.echo, others logging
   - Mitigation: Accept mixed output styles, they're already working

3. **Exit code consistency**: Ensure all commands return proper codes
   - Mitigation: Check existing implementations (already done)

## Alternatives Considered

### Alternative Names
- `jigy build` - Too generic, doesn't convey "rebuild everything"
- `jigy refresh` - Less clear than rebuild
- `jigy run-all` - Too verbose
- `jigy workflow` - Doesn't convey rebuilding

**Decision:** Stick with `jigy rebuild` - clear and matches existing vocabulary

### Alternative: Shell Script
Could create `scripts/rebuild.sh` instead of CLI command.

**Rejected because:**
- Users expect native CLI commands
- Harder to maintain (two languages)
- Loses click's argument parsing and help text
- CLI command is more discoverable

### Alternative: Configuration File
Could add config to run multiple commands.

**Rejected because:**
- Over-engineering for this simple use case
- Users want one command, not configuration

## Completion Criteria

- [ ] `jigy rebuild` command exists and is callable
- [ ] All four workflow steps execute in order
- [ ] Clear progress messages between steps
- [ ] Proper error handling and early exit on failure
- [ ] Appropriate exit codes returned
- [ ] Manual testing confirms expected behavior
- [ ] Documentation updated (contextJIG.md)
- [ ] Command appears in `jigy --help`

## Estimated Effort

**Total:** 45-65 minutes
- Implementation: 30-45 minutes
- Testing: 10-15 minutes
- Documentation: 5 minutes

## Next Steps

1. Review this plan with user
2. Implement WU1 (main command)
3. Test manually
4. Update documentation
5. Optional: Add integration test (WU2)
