# S034: Orphaned Nodes Fix Plan

## Summary

JIG graph currently has **17 orphaned nodes** (nodes with no edges). Analysis reveals these fall into two categories:

1. **Test fixtures** (3 nodes) - Intentionally orphaned, used for testing/documentation
2. **Real nodes** (14 nodes) - Have relationship information in "Related" sections but NOT in YAML frontmatter

## Root Cause

The graph parser only reads relationships from YAML frontmatter, not from markdown "Related" sections. Many nodes document their relationships in prose at the bottom of the file, but the parser cannot extract this information.

**Example of the problem:**

```yaml
---
id: O-CLI-003
type: outcome
title: "Consistent CLI Output Formatting"
subsystem: cli
# Missing: implements field here!
---

# ... markdown content ...

## Related

- implements: S-CLI-006 (Standard Formatting Library)
- implements: S-CLI-007 (Status Command Output Format)
- implements: S-CLI-008 (Validate Command Output Format)
- implements: S-CLI-009 (Graph Command Output Format)
```

The "Related" section is human-readable but not machine-readable. The parser needs:

```yaml
---
id: O-CLI-003
type: outcome
title: "Consistent CLI Output Formatting"
subsystem: cli
implements:
  - S-CLI-006
  - S-CLI-007
  - S-CLI-008
  - S-CLI-009
---
```

## Orphaned Nodes Breakdown

### Category 1: Test Fixtures (Intentionally Orphaned)

These nodes exist solely for testing and documentation. They can remain orphaned OR be linked in a test fixture network.

| Node ID    | Title                                                | Location                         |
| ---------- | ---------------------------------------------------- | -------------------------------- |
| S-AUTH-001 | JWT token authentication (test fixture)              | jig/specifications/S-AUTH-001.md |
| S-AUTH-002 | JWT token refresh mechanism (test fixture)           | jig/specifications/S-AUTH-002.md |
| S-TEST-001 | Generic test specification for fixtures and examples | jig/specifications/S-TEST-001.md |

**Decision needed:** Should test fixtures remain orphaned, or should they be connected to each other or to testing-related outcomes?

**Recommendation:** Mark these as `status: test-fixture` in frontmatter (already done) and exclude from orphan warnings in validation logic.

---

### Category 2: Real Nodes (Need Frontmatter Fixes)

#### CLI Outcomes (5 nodes)

**O-CLI-003** - Consistent CLI Output Formatting
- File: `jig/outcomes/O-CLI-003.md`
- Related section says: implements S-CLI-006, S-CLI-007, S-CLI-008, S-CLI-009
- **Fix:** Add to frontmatter:
  ```yaml
  implements:
    - S-CLI-006
    - S-CLI-007
    - S-CLI-008
    - S-CLI-009
  ```

**O-CLI-004** - Actionable Error Messages
- File: `jig/outcomes/O-CLI-004.md`
- Needs analysis: No Related section found
- **Action:** Read file to determine appropriate relationships

**O-CLI-005** - Progressive Disclosure of Information
- File: `jig/outcomes/O-CLI-005.md`
- Needs analysis: No Related section found
- **Action:** Read file to determine appropriate relationships

#### Core Outcomes (5 nodes)

**O-JIG-001** - JIG tools run in <1 second for most operations
- File: `jig/outcomes/O-JIG-001.md`
- Related section says: specs: S-JIG-001
- **Fix:** Change "specs:" to proper relationship. Outcomes don't implement specs; specs implement outcomes.
- **Analysis needed:** This is backwards. S-JIG-001 should implement O-JIG-001, not the other way around.
- **Action:** Check if S-JIG-001 already has `implements: O-JIG-001` in its frontmatter. If yes, O-JIG-001 is orphaned but correctly so. If no, add it to S-JIG-001.

**O-JIG-002** - JIG uses simple text formats (YAML + Markdown)
- File: `jig/outcomes/O-JIG-002.md`
- **Action:** Read file to determine relationships

**O-JIG-003** - JIG is composable (pipes work)
- File: `jig/outcomes/O-JIG-003.md`
- **Action:** Read file to determine relationships

**O-JIG-004** - JIG requires no external services
- File: `jig/outcomes/O-JIG-004.md`
- **Action:** Read file to determine relationships

**O-JIG-005** - JIG demonstrates modularity >0.7
- File: `jig/outcomes/O-JIG-005.md`
- **Action:** Read file to determine relationships

#### Core Specifications (6 nodes)

**S-JIG-001** - Marker extraction processes 1000 files in <1s
- File: `jig/specifications/S-JIG-001.md`
- Related section says: implements: O-JIG-001
- **Fix:** Add to frontmatter:
  ```yaml
  implements:
    - O-JIG-001
  ```

**S-JIG-003** - Commands output valid YAML
- File: `jig/specifications/S-JIG-003.md`
- **Action:** Read file to determine relationships (likely implements O-JIG-002)

**S-JIG-004** - Subsystems export <5 interfaces
- File: `jig/specifications/S-JIG-004.md`
- **Action:** Read file to determine relationships (likely implements O-JIG-005)

**S-JIG-005** - Test nodes discovered via @jig annotations
- File: `jig/specifications/S-JIG-005.md`
- **Action:** Read file to determine relationships

**S-JIG-006** - Graph loads O/S/X markdown nodes only
- File: `jig/specifications/S-JIG-006.md`
- **Action:** Read file to determine relationships

**S-NESTED-006** - Constraint scopes with nested subsystem paths
- File: `jig/specifications/S-NESTED-006.md`
- Related section says: "Related: S-NESTED-002 (path resolution), Constraint system (future spec)"
- **Fix:** Add to frontmatter:
  ```yaml
  depends_on:
    - S-NESTED-002
  ```

## Fix Strategy

### Phase 1: Analysis (Read All Files)

Read all 14 real orphaned nodes to extract relationship information from:
1. "Related" sections
2. "Implements" references in body text
3. "References" sections
4. Logical connections based on titles and content

### Phase 2: Create Relationship Mapping

Document for each node:
- Current frontmatter
- Relationships found in markdown
- Proposed frontmatter additions
- Justification

### Phase 3: Systematic Frontmatter Updates

For each node:
1. Add appropriate relationship fields to frontmatter
2. Keep "Related" sections for human readers (they provide context)
3. Ensure consistency between frontmatter and prose

### Phase 4: Rebuild Index

```bash
jigy index
```

### Phase 5: Verification

```bash
jigy status
```

Expected result: 0 orphaned nodes (or only 3 test fixtures if we exclude them from warnings)

## Relationship Field Reference

Nodes can use these frontmatter fields:

```yaml
implements:      # S/C nodes → O nodes (specs/code implement outcomes)
  - O-XYZ-001

verifies:        # T nodes → S/O nodes (tests verify specs/outcomes)
  - S-XYZ-001

depends_on:      # Any node → any node (dependency relationship)
  - S-OTHER-001
```

**Key rules:**
- Specifications implement Outcomes
- Code implements Specifications (and sometimes Outcomes)
- Tests verify Specifications or Outcomes
- Outcomes generally do NOT implement other nodes (they are goals, not implementations)
- Use `depends_on:` for non-hierarchical relationships

## Edge Cases to Consider

1. **Outcomes that are too high-level:** Some outcomes might be strategic goals with no direct implementing specs yet. These could legitimately be orphaned until specs are created.

2. **Deprecated nodes:** Some orphaned nodes might be obsolete. Check git history before adding relationships.

3. **Future features:** Some specs might be placeholders for future work. Determine if they should connect to existing outcomes or remain orphaned as "planned work."

## Validation Rule Improvement

Consider updating `jigy status` to:
1. Exclude `status: test-fixture` nodes from orphan warnings
2. Add flag `--include-fixtures` to show them if needed
3. Categorize orphans: "Real nodes (X)", "Test fixtures (Y)"

## Timeline Estimate

- Phase 1 (Read files): 15 minutes
- Phase 2 (Document mappings): 20 minutes
- Phase 3 (Update frontmatter): 20 minutes
- Phase 4 (Rebuild + verify): 5 minutes

**Total: ~60 minutes**

## Success Criteria

- [ ] All 14 real orphaned nodes have at least one edge
- [ ] Test fixture nodes remain orphaned but are excluded from warnings
- [ ] `jigy status` shows 0 orphaned warnings
- [ ] All relationship fields are in frontmatter (not just prose)
- [ ] Index rebuilds successfully
- [ ] No new validation errors introduced

## References

- Current graph status: 95 nodes, 65 edges, 17 orphaned
- Graph index: `jig/graph-index.json`
- Example working node: `jig/specifications/S-CLI-003.md` (has proper frontmatter)
- Example broken node: `jig/outcomes/O-CLI-003.md` (relationships only in prose)

## Next Steps

1. Review this plan for accuracy
2. Proceed with Phase 1 (read all 14 nodes)
3. Create detailed relationship mapping in spreadsheet or table
4. Execute Phase 3 (frontmatter updates)
5. Verify success with `jigy status`
