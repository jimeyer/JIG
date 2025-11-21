# Task: Find and Repair Orphaned Nodes in Graph Index

## Objective

Identify nodes in the jig graph structure that are orphaned (unreferenced or have broken relationships) and either repair their connections or document them for manual review, ensuring graph integrity.

## Context

The jig project maintains a graph of Intent nodes (Outcomes, Specifications, Work Units, Design Rules, and Technical Components) in `jig/graph-index.yaml`. Over time, nodes can become orphaned through:
- References to node IDs that don't exist in the index
- Nodes that exist but are never referenced by any other node
- Malformed relationship structures (e.g., missing required fields)
- Nodes referenced in subsystem definitions but absent from the main index

Graph integrity is critical for the OSTC framework to function correctly. Orphaned nodes indicate incomplete modeling or data consistency issues.

## Inputs

- **Primary Location**: `jig/graph-index.yaml`
- **Secondary Location**: `jig/subsystems.yaml` (for cross-referencing subsystem-declared nodes)
- **Format**: YAML files following the OSTC node structure
- **Expected Structure**:
  - Each node has an `id` field (e.g., `O-JIG-001`)
  - Nodes may have `implements`, `specifies`, `contributes_to`, `depends_on` relationship fields
  - Relationships reference other node IDs as strings or lists

## Process

1. **Load and Parse Graph Data**
   - Parse `jig/graph-index.yaml` into memory
   - Parse `jig/subsystems.yaml` for any node references
   - Build a registry of all declared node IDs

2. **Identify Orphans - Type 1: Dangling References**
   - For each node, iterate through all relationship fields
   - Check if referenced node IDs exist in the registry
   - Record any references to non-existent nodes

3. **Identify Orphans - Type 2: Unreferenced Nodes**
   - Build a reverse index of all node IDs that are referenced
   - Identify nodes in the registry that appear in zero relationship fields
   - Exclude root-level nodes that are expected to have no incoming references (e.g., top-level Outcomes without parent systems)

4. **Categorize Findings**
   - **Broken References**: Node A references Node B, but B doesn't exist
   - **Isolated Nodes**: Node exists but nothing references it
   - **Malformed Structures**: Relationship fields exist but are empty/null/malformed

5. **Generate Repair Report**
   - Create a structured output listing all orphaned nodes by category
   - For each issue, suggest repair actions:
     - Broken reference → "Create missing node or remove reference"
     - Isolated node → "Add relationship to parent concept or remove if obsolete"
     - Malformed → "Fix structure or remove field"

## Outputs

- **Format**: Markdown report
- **Location**: `docs/reports/orphaned-nodes-YYYYMMDD.md` (use current date)
- **Naming**: `orphaned-nodes-{YYYYMMDD}.md`
- **Structure**:
  ```markdown
  # Orphaned Nodes Report

  **Generated**: [ISO timestamp]
  **Total Nodes Analyzed**: [count]

  ## Summary
  - Broken References: [count]
  - Isolated Nodes: [count]
  - Malformed Structures: [count]

  ## Broken References

  ### Node: [ID]
  - **Type**: [Outcome/Specification/etc.]
  - **Issue**: References non-existent node `[missing-id]` in field `[field-name]`
  - **Suggested Fix**: [action]

  ## Isolated Nodes

  ### Node: [ID]
  - **Type**: [type]
  - **Issue**: Exists but is never referenced
  - **Context**: [description from node if available]
  - **Suggested Fix**: [action]

  ## Malformed Structures
  [Same pattern as above]

  ## Recommended Actions
  1. [Prioritized list of fixes]
  ```

## Success Criteria

- [ ] All nodes in `jig/graph-index.yaml` are parsed without errors
- [ ] Report identifies every node reference that points to a non-existent ID
- [ ] Report identifies every node that has zero incoming references (excluding expected root nodes)
- [ ] Each identified issue includes a specific suggested fix
- [ ] Report is saved to the correct location with proper timestamp
- [ ] If zero issues found, report explicitly states "No orphaned nodes detected"
- [ ] Output is valid markdown that renders correctly

## Constraints

- **DO NOT**: Automatically modify `jig/graph-index.yaml` without explicit confirmation
- **DO NOT**: Remove nodes that appear isolated but may be intentional root nodes (check context)
- **DO NOT**: Fail silently—if parsing errors occur, report them clearly
- **MUST**: Preserve all original node data when analyzing (read-only by default)
- **MUST**: Handle missing files gracefully (report if index doesn't exist)
- **PREFER**: Conservative repair suggestions (recommend manual review for ambiguous cases)

## Examples

### Example 1: Broken Reference

**Input** (in `graph-index.yaml`):
```yaml
- id: S-JIG-001
  type: Specification
  specifies: O-JIG-999  # This Outcome doesn't exist
```

**Expected Output** (in report):
```markdown
### Node: S-JIG-001
- **Type**: Specification
- **Issue**: References non-existent node `O-JIG-999` in field `specifies`
- **Suggested Fix**: Either create Outcome O-JIG-999 or update reference to existing Outcome
```

### Example 2: Isolated Node

**Input** (in `graph-index.yaml`):
```yaml
- id: T-JIG-042
  type: Technical Component
  description: "Legacy validation module"
  # No other nodes reference T-JIG-042
```

**Expected Output**:
```markdown
### Node: T-JIG-042
- **Type**: Technical Component
- **Issue**: Exists but is never referenced by any other node
- **Context**: Legacy validation module
- **Suggested Fix**: Review if still needed; if obsolete, remove. If active, link to relevant Work Unit or Specification
```

### Example 3: Clean Graph

**Output when no issues**:
```markdown
# Orphaned Nodes Report

**Generated**: 2025-11-21T10:30:00Z
**Total Nodes Analyzed**: 42

## Summary
No orphaned nodes detected. Graph integrity verified.
```

## Edge Cases

- **Empty Graph**: If no nodes exist, report "Empty graph—no nodes to analyze"
- **Circular References**: Don't count circular references as orphans (A→B→A is valid)
- **Self-References**: Flag as unusual but don't categorize as broken unless the node doesn't exist
- **List vs String Fields**: Handle both `specifies: "O-001"` and `specifies: ["O-001", "O-002"]`
- **Null/None Values**: Empty relationship fields are valid—only flag if they contain invalid references

## Verification Steps

After generating the report:
1. Manually verify at least 2 items from each category in the actual YAML files
2. Confirm total node count matches the count in graph-index.yaml
3. Check that report filename follows the date format convention
4. Ensure markdown syntax is valid (no unclosed code blocks, headers render correctly)

---

**Version**: 1.0
**Last Updated**: 2025-11-21
