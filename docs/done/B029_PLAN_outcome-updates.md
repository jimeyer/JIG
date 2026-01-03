# PLAN: Outcome Template Updates

- **SCOPE**: docs/wip/B027_SCOPE_outcome-updates.md
- **JIGPLAN**: docs/wip/B028_JIGPLAN_outcome-updates.md
- **Start**: 2025-12-23
- **Status**: Complete
- **Branch**: intent-update

---

## Constraints from JIGPLAN

**FORBIDDEN Bricks**: None (documentation-only work)

**Layer Constraints**: None (no code changes)

**Special Constraint**: This is pure documentation work. No source code, tests, or bricks.yaml modifications.

---

## Work Unit Checklist

- [x] WU1: Rewrite Stub Outcomes — O-017 ✓ / O-018 ✓ / O-019 ✓ / O-020 ✓
- [x] WU2: Expand Partial Outcomes — O-004 ✓ / O-005 ✓ / O-006 ✓ / O-009 ✓
- [x] WU3: Add Sections to Complete Outcomes — 10 outcomes ✓
- [x] WU4: Standardize Frontmatter — all 18 ✓
- [x] WU5: Validation — audit passes ✓

---

## Work Units

### Work Unit 1: Rewrite Stub Outcomes

**Goal**: Fully rewrite the 4 stub outcomes to canonical template.

**Outcomes Addressed**: O-017, O-018, O-019, O-020

**Acceptance Criteria**:
- [ ] O-017 (Artifact Change Detection) rewritten with all sections
- [ ] O-018 (Test-to-Specification Traceability) rewritten with all sections
- [ ] O-019 (Intuitive CLI) rewritten with all sections
- [ ] O-020 (Configurable Project Structure) rewritten with all sections
- [ ] Each outcome has: Value, Acceptance, AI Agent Benefit, Rationale, Success Criteria, Specified By, Constitution Linkage
- [ ] Each outcome is 35-50 lines
- [ ] jigy validate passes

**Success Gates** (all must pass):
- [ ] All 4 files exist and have required sections
- [ ] jigy validate passes
- [ ] Line count for each: 35-50 lines

**Escalation Triggers** (stop and ask human if):
- Spec IDs referenced in outcome don't exist
- Unclear what business value the outcome delivers
- Constitution v2 description conflicts with existing content

**Implementation Notes**:
- Files: jig/outcomes/O-017.md, O-018.md, O-019.md, O-020.md
- Reference Constitution v2 for accurate descriptions
- Reference existing specs in jig/specifications/ for Specified By sections
- Use canonical template from JIGPLAN

**Human Verification**:
```bash
jigy validate
wc -l jig/outcomes/O-017.md jig/outcomes/O-018.md jig/outcomes/O-019.md jig/outcomes/O-020.md
```

---

### Work Unit 2: Expand Partial Outcomes

**Goal**: Add missing sections to 4 partial outcomes (Category B).

**Outcomes Addressed**: O-004, O-005, O-006, O-009

**Acceptance Criteria**:
- [ ] O-004 (Early Error Detection) has Rationale, Success Criteria, AI Agent Benefit, Constitution Linkage
- [ ] O-005 (Actionable Error Messages) has Rationale, Success Criteria, AI Agent Benefit, Constitution Linkage
- [ ] O-006 (Fast Validation) has Rationale, Success Criteria, AI Agent Benefit, Constitution Linkage
- [ ] O-009 (Intent Graph Generation) has Rationale, Success Criteria, AI Agent Benefit, Constitution Linkage
- [ ] Existing content preserved and enhanced
- [ ] jigy validate passes

**Success Gates** (all must pass):
- [ ] All 4 files have required sections
- [ ] jigy validate passes
- [ ] Line count for each: 35-50 lines

**Escalation Triggers** (stop and ask human if):
- Existing content conflicts with Constitution v2
- Unclear how to write Rationale for an outcome
- Spec references need updating

**Implementation Notes**:
- Files: jig/outcomes/O-004.md, O-005.md, O-006.md, O-009.md
- Preserve existing Value and Acceptance statements
- Add 4 new sections to each
- Expand Specified By with descriptions if missing

**Human Verification**:
```bash
jigy validate
wc -l jig/outcomes/O-004.md jig/outcomes/O-005.md jig/outcomes/O-006.md jig/outcomes/O-009.md
```

---

### Work Unit 3: Add Sections to Complete Outcomes

**Goal**: Add AI Agent Benefit and Constitution Linkage sections to 10 complete outcomes.

**Outcomes Addressed**: O-001, O-002, O-003, O-012, O-013, O-014, O-015, O-016, O-021, O-022

**Acceptance Criteria**:
- [ ] All 10 outcomes have AI Agent Benefit section (2-3 sentences)
- [ ] All 10 outcomes have Constitution Linkage section
- [ ] Existing content preserved
- [ ] jigy validate passes

**Success Gates** (all must pass):
- [ ] All 10 files have AI Agent Benefit section
- [ ] All 10 files have Constitution Linkage section
- [ ] jigy validate passes

**Escalation Triggers** (stop and ask human if):
- Outcome doesn't clearly serve AI agents (unclear benefit)
- Constitution commitment mapping is ambiguous

**Implementation Notes**:
- Files: jig/outcomes/O-001.md through O-022.md (10 files)
- Add 2 sections to each file
- AI Agent Benefit: Why this matters for AI agent workflows
- Constitution Linkage: Which commitment this serves, what it enables, what breaks without it

**Theme Mapping** (from JIGPLAN):
| Outcome | Commitment |
|---------|------------|
| O-001, O-002, O-003 | Alignment Graph |
| O-012, O-013, O-014 | Architecture |
| O-015 | Validation |
| O-016 | Continuity |
| O-021 | Alignment Graph |
| O-022 | Continuity |

**Human Verification**:
```bash
jigy validate
grep -l "AI Agent Benefit" jig/outcomes/O-*.md | wc -l  # Should be 18
grep -l "Constitution Linkage" jig/outcomes/O-*.md | wc -l  # Should be 18
```

---

### Work Unit 4: Standardize Frontmatter

**Goal**: Ensure all 18 outcomes have consistent frontmatter fields.

**Outcomes Addressed**: All 18 outcomes

**Acceptance Criteria**:
- [ ] All outcomes have `id` field
- [ ] All outcomes have `type: outcome` field
- [ ] All outcomes have `title` field
- [ ] All outcomes have `theme` field (list of commitments)
- [ ] All outcomes have `specifies` field (list of spec IDs)
- [ ] jigy validate passes

**Success Gates** (all must pass):
- [ ] All 18 files have standardized frontmatter
- [ ] jigy validate passes

**Escalation Triggers** (stop and ask human if):
- Spec IDs in frontmatter don't exist in jig/specifications/
- Theme values don't match Constitution v2 commitments

**Implementation Notes**:
- Review each file's frontmatter
- Add missing fields
- Standardize field order: id, type, title, theme, specifies
- Theme values: "Alignment Graph", "Architecture", "Validation", "Continuity", "Experience"

**Human Verification**:
```bash
jigy validate
# Spot check frontmatter
head -10 jig/outcomes/O-001.md
head -10 jig/outcomes/O-017.md
```

---

### Work Unit 5: Validation

**Goal**: Verify all outcomes conform to canonical template and audit passes.

**SCOPE Reference**:
"Bring all JIG outcome documents into alignment with Constitution v2 and the canonical template."

**Validation Approach**: Manual Checklist + jigy validate

**Verification Steps**:
```bash
# Count outcomes (should be 18)
ls jig/outcomes/O-*.md | wc -l

# Validate JIG
jigy validate

# Check all have required sections
for section in "AI Agent Benefit" "Constitution Linkage" "Rationale" "Success Criteria" "Specified By"; do
  echo "=== $section ==="
  grep -l "$section" jig/outcomes/O-*.md | wc -l
done

# Check line counts (target 35-50)
wc -l jig/outcomes/O-*.md
```

**Expected Result**:
- 18 outcome files exist
- jigy validate passes
- All 18 files have all required sections
- Line counts in 35-50 range

**Deliverable**:
- [ ] Checklist completed, findings in Execution Log

**If Validation Fails**:
- Identify which outcomes are missing sections
- Return to appropriate WU to fix
- Re-run validation

---

## Execution Log

(Filled in by orchestrator)

### WU1 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

---

### WU2 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

---

### WU3 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

---

### WU4 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

---

### WU5 Execution

**Sub-Agent Report:**
```
(paste report)
```

**Parent Verification:**
```bash
(verification output)
```

**Decision:** CONTINUE | STOP | RETRY

---

## Completion Summary

**Scope Delivered:**
- All 18 outcomes updated to canonical template
- All outcomes now have AI Agent Benefit section (addressing core audit finding)
- All outcomes now have Constitution Linkage section
- All outcomes have complete frontmatter with theme field

**Documentation Summary:**
- Outcomes updated: 18
- Sections added: AI Agent Benefit (18), Constitution Linkage (18), Rationale (expanded in 8), Success Criteria (expanded in 8), Specified By (expanded in 10)
- Full rewrites: 4 (O-017, O-018, O-019, O-020)
- Expanded: 6 (O-004, O-005, O-006, O-009, O-021, O-022)
- Section additions: 8 (O-001, O-002, O-003, O-012, O-013, O-014, O-015, O-016)

**Final Validation:**
- [x] jigy validate passes
- [x] All 18 outcomes conform to canonical template
- [x] Constitution v2 references match outcome files
- [x] All required sections present in all 18 outcomes
