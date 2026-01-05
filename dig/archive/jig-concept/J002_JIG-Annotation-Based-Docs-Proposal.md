---
title: "JIG Annotation-Based Documentation Proposal"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1763493911
created_human: "2025-11-18 13:25 CST"
parent: "[[J001_JIG-Concept-v4]]"
children: []
---
# JIG Annotation-Based Documentation Proposal
**Natural Documents with Embedded Intent Annotations**
**Date:** 2025-11-12
**Status:** Design Proposal
**Builds on:** JIG v4.0

---

## Executive Summary

This proposal extends JIG v4.0 to support **annotation-based documentation**, allowing developers to embed Outcomes and Specifications directly into natural documents (PRDs, RFCs, design docs) using lightweight annotations, just like we do with code and tests.

**Core Insight**: Humans don't write in isolated fragments. They write coherent documents with narrative flow, examples, diagrams, and context. JIG should extract structure from these natural documents, not force authors into rigid templates.

**Key Change**: Instead of:
```
.jig/outcomes/O-001.md
.jig/outcomes/O-002.md
.jig/specifications/S-001.md
.jig/specifications/S-002.md
```

Authors write:
```
docs/expense-tracking-feature.md  (contains both O and S nodes)
docs/architecture-decisions.md    (contains S nodes)
product/2025-q4-roadmap.md        (contains O nodes)
```

---

## 1. The Problem with Separate Files

### 1.1 Current JIG v4.0 Structure

```
.jig/
├── outcomes/
│   ├── O-001.md
│   ├── O-002.md
│   ├── O-003.md
│   ├── O-004.md
│   └── O-005.md
└── specifications/
    ├── S-001.md
    ├── S-002.md
    ├── S-003.md
    └── S-004.md
```

**Issues**:
1. **Cognitive fragmentation**: Related content split across many files
2. **Context loss**: Can't see the narrative arc from Outcome → Spec
3. **Not how humans write**: PRDs, RFCs, design docs are unified documents
4. **Rigid structure**: Forces template compliance before content creation
5. **Collaboration friction**: Hard to review/comment on 20 separate files
6. **Migration burden**: Existing docs can't be adopted without full rewrite

### 1.2 How Humans Actually Write

**Product Requirements Document**:
```markdown
# Expense Tracking Feature Proposal

## Background
Our users struggle to manage personal finances...

## Goals
We want to enable accurate expense tracking so users can...

## Requirements
### Data Validation
Expenses must be validated before storage:
- Amounts must be positive
- Categories must be from approved list
- Maximum expense: $10,000

### Persistence
Validated expenses must be stored reliably...

## Success Metrics
- 95% of users successfully track expenses
- <1% data validation errors
```

This is **one coherent document** with multiple embedded Outcomes and Specifications. Breaking it into 10 separate files destroys readability.

---

## 2. The Annotation-Based Solution

### 2.1 Core Principle

> **Intent lives in documents, not files. JIG extracts structure through annotations.**

Authors write natural documents. JIG annotations mark sections as Outcomes or Specifications. The scanner extracts these into the graph while preserving document context.

### 2.2 Annotation Syntax

**Lightweight HTML-style comments** (invisible in rendered Markdown):

```markdown
<!-- @jig outcome O-001 -->
## Enable Accurate Expense Tracking

We want to help users track expenses so they can manage their finances effectively.

**Success Criteria**:
- 95% of users successfully track expenses
- <1% data validation errors
<!-- @jig end -->

Some explanatory text that's not part of the outcome...

<!-- @jig spec S-001 satisfies:O-001 -->
### Expense Validation Rules

Expenses must be validated before storage:
- Amount must be positive decimal
- Category must be from approved list
- Maximum amount: $10,000
<!-- @jig end -->
```

**Why HTML comments?**
- Invisible when rendered (GitHub, GitLab, Notion, etc.)
- Standard Markdown syntax
- Won't confuse existing tools
- Easy to search/replace

### 2.3 Auto-Generated IDs (Optional)

Authors can omit IDs on first write:

```markdown
<!-- @jig outcome -->
## Enable Accurate Expense Tracking
...
<!-- @jig end -->

<!-- @jig spec satisfies:^ -->
### Expense Validation Rules
...
<!-- @jig end -->
```

**How it works**:
1. Run `jigy scan --annotate-docs docs/`
2. JIG generates stable IDs based on heading text + content hash
3. Updates annotations in place:
   ```markdown
   <!-- @jig outcome O-001 -->
   ## Enable Accurate Expense Tracking
   ```
4. `satisfies:^` means "satisfies the closest preceding outcome"

**Stable ID generation**:
```python
def generate_id(type, title, content):
    # Hash based on title + first paragraph (stable across edits)
    hash = sha256(f"{title}:{first_paragraph(content)}").hexdigest()[:8]
    return f"{type[0].upper()}-{hash}"
```

---

## 3. Document Structure Patterns

### 3.1 Single-Purpose Documents

**One Outcome, Multiple Specs**:

```markdown
# User Authentication Feature

<!-- @jig outcome O-auth-001 priority:high -->
## Secure User Authentication

Enable secure login so users can access their accounts safely.

**Success Metrics**:
- <0.1% account compromises
- 99.9% uptime for auth service
<!-- @jig end -->

## Technical Approach

<!-- @jig spec S-auth-001 satisfies:O-auth-001 -->
### Password Requirements
- Minimum 12 characters
- Must include uppercase, lowercase, number, symbol
- Cannot be in common password database
<!-- @jig end -->

<!-- @jig spec S-auth-002 satisfies:O-auth-001 -->
### Multi-Factor Authentication
- Support TOTP (Time-based One-Time Password)
- Support SMS backup codes
- Force MFA for admin accounts
<!-- @jig end -->
```

### 3.2 Multi-Purpose Documents

**PRD with Multiple Outcomes**:

```markdown
# 2025 Q4 Product Roadmap

## Strategic Initiatives

<!-- @jig outcome O-q4-001 priority:critical -->
### Improve User Retention
Increase 30-day retention from 60% to 75%.
<!-- @jig end -->

<!-- @jig outcome O-q4-002 priority:high -->
### Expand Payment Options
Support international payment methods to increase conversion.
<!-- @jig end -->

## Feature Details

<!-- @jig spec S-payments-001 satisfies:O-q4-002 -->
### Stripe Integration
- Support credit cards, ACH, PayPal
- Handle currency conversion
- Comply with PCI-DSS
<!-- @jig end -->
```

### 3.3 Existing Documents (Retrofitting)

**Adding JIG to existing PRD**:

```markdown
# Expense Tracker PRD (Existing Document)

Written by: Product Team
Last updated: 2025-10-01

## Vision
We want to build the best expense tracking app...

<!-- @jig outcome -->
## Goal: Help Users Track Spending
Our research shows users struggle to track expenses manually.
We want to automate this so they save time and improve financial health.
<!-- @jig end -->

## Requirements (from stakeholder interviews)

Some background context that's not a spec...

<!-- @jig spec satisfies:^ -->
### Requirement 1: Validate Expense Data
All expense inputs must be validated:
- Amount > 0
- Category in approved list
- Receipt photo < 10MB
<!-- @jig end -->
```

**Key**: Authors don't need to restructure. Just wrap relevant sections.

---

## 4. Scanning and Extraction

### 4.1 Document Scanning Process

```bash
jigy scan --docs docs/ product/ design/
```

**What happens**:

1. **Find documents**: Glob for `*.md` files in specified directories
2. **Parse Markdown**: Extract structure (headings, paragraphs, lists)
3. **Identify annotations**: Find `<!-- @jig ... -->` blocks
4. **Extract content**: Grab everything between start and end tags
5. **Generate IDs**: If missing, create stable IDs
6. **Update files**: Write IDs back to documents (if `--annotate-docs`)
7. **Build index**: Create `.jig/generated/docs_index.json`
8. **Merge graph**: Combine with code/test indices into `graph.json`

### 4.2 Generated Index Structure

**File**: `.jig/generated/docs_index.json`

```json
{
  "metadata": {
    "generated_at": "2025-11-12T10:00:00Z",
    "tool_version": "jigy 1.0.0",
    "document_directories": ["docs/", "product/"]
  },
  "outcome_nodes": [
    {
      "id": "O-001",
      "title": "Enable Accurate Expense Tracking",
      "content": "We want to help users track expenses...",
      "location": {
        "file": "docs/expense-tracking.md",
        "line_start": 15,
        "line_end": 23,
        "heading": "## Enable Accurate Expense Tracking"
      },
      "metadata": {
        "priority": "high",
        "status": "active",
        "created": "2025-11-01T10:00:00Z",
        "modified": "2025-11-12T10:00:00Z"
      },
      "context": {
        "preceding_text": "## Background\nOur users struggle...",
        "following_text": "Some explanatory text..."
      }
    }
  ],
  "specification_nodes": [
    {
      "id": "S-001",
      "title": "Expense Validation Rules",
      "content": "Expenses must be validated...",
      "location": {
        "file": "docs/expense-tracking.md",
        "line_start": 30,
        "line_end": 40,
        "heading": "### Expense Validation Rules"
      },
      "satisfies": ["O-001"],
      "metadata": {
        "status": "active"
      }
    }
  ]
}
```

### 4.3 Bi-Directional Sync

**Challenge**: How do we update documents when implementation changes?

**Solution**: Auto-generated status sections

```markdown
<!-- @jig spec S-001 satisfies:O-001 -->
### Expense Validation Rules

Expenses must be validated before storage:
- Amount must be positive decimal
- Category must be from approved list

<!-- @jig status:auto-generated -->
**Implementation Status** (auto-updated by `jigy scan --update-docs`):
- ✅ Implemented by: `validate_expense()` (C-001)
- ✅ Tested by: 3 tests (T-001, T-002, T-003)
- ✅ Coverage: 100%
- ⚠️ Test T-002 failing since 2025-11-10
- Last verified: 2025-11-12T10:00:00Z
<!-- @jig end-status -->

<!-- @jig end -->
```

**Rules**:
1. Status block is auto-generated (don't edit manually)
2. Located before `<!-- @jig end -->`
3. Updated by `jigy scan --update-docs`
4. Shows alignment health for this node

---

## 5. Annotation Reference Syntax

### 5.1 Full Syntax

```markdown
<!-- @jig TYPE [ID] [key:value ...] -->
CONTENT
<!-- @jig end -->
```

**Parameters**:
- `TYPE`: `outcome` | `spec`
- `ID`: Optional; auto-generated if omitted
- `key:value`: Metadata pairs

### 5.2 Outcome Annotations

```markdown
<!-- @jig outcome [ID] [priority:LEVEL] [status:STATUS] [tags:TAG1,TAG2] -->
## Heading
Content describing the business outcome...
<!-- @jig end -->
```

**Keys**:
- `priority`: `critical` | `high` | `medium` | `low`
- `status`: `active` | `draft` | `deprecated` | `achieved`
- `tags`: Comma-separated tags

**Examples**:
```markdown
<!-- @jig outcome priority:high tags:q4,revenue -->
<!-- @jig outcome O-2025-q4-retention status:active -->
<!-- @jig outcome -->
```

### 5.3 Specification Annotations

```markdown
<!-- @jig spec [ID] satisfies:O-XXX[,O-YYY] [status:STATUS] [tags:TAG1,TAG2] -->
### Heading
Content describing technical requirements...
<!-- @jig end -->
```

**Keys**:
- `satisfies`: Comma-separated outcome IDs (required)
- `status`: `active` | `draft` | `deprecated` | `implemented`
- `tags`: Comma-separated tags

**Special satisfies values**:
- `satisfies:^` → "closest preceding outcome in this document"
- `satisfies:O-001` → explicit ID
- `satisfies:O-001,O-002` → multiple outcomes

**Examples**:
```markdown
<!-- @jig spec satisfies:^ -->
<!-- @jig spec S-auth-001 satisfies:O-auth-001 status:implemented -->
<!-- @jig spec satisfies:O-001,O-002 tags:security,compliance -->
```

### 5.4 Reference Resolution

**Relative references** (`^`, `^^`):
- `^`: Closest preceding outcome in same document
- `^^`: Second closest preceding outcome
- Resolved during scan

**Example**:
```markdown
<!-- @jig outcome O-001 -->
## Outcome A
<!-- @jig end -->

<!-- @jig outcome O-002 -->
## Outcome B
<!-- @jig end -->

<!-- @jig spec satisfies:^ -->
### Spec for Outcome B
<!-- @jig end -->

<!-- @jig spec satisfies:^^ -->
### Spec for Outcome A
<!-- @jig end -->
```

---

## 6. Workflow Examples

### 6.1 Starting from Scratch

**Step 1**: Write natural document

```markdown
# New Feature Proposal

## Problem
Users can't export their data.

## Solution
We'll add CSV export functionality.

### Export Format
CSV files with columns: date, amount, category, description.

### Export Limits
- Maximum 10,000 rows per export
- Data from last 2 years only
```

**Step 2**: Add annotations

```markdown
# New Feature Proposal

<!-- @jig outcome -->
## Problem
Users can't export their data. We want to enable data export so users can analyze in Excel.
<!-- @jig end -->

<!-- @jig spec satisfies:^ -->
### Export Format
CSV files with columns: date, amount, category, description.
<!-- @jig end -->

<!-- @jig spec satisfies:^ -->
### Export Limits
- Maximum 10,000 rows per export
- Data from last 2 years only
<!-- @jig end -->
```

**Step 3**: Scan and generate IDs

```bash
jigy scan --docs docs/ --annotate-docs
```

**Result** (file updated in place):

```markdown
<!-- @jig outcome O-f3a8b1c2 -->
## Problem
Users can't export their data...
<!-- @jig end -->

<!-- @jig spec S-9d4e2f1a satisfies:O-f3a8b1c2 -->
### Export Format
...
<!-- @jig end -->
```

### 6.2 Retrofitting Existing PRD

**Before**:
```markdown
# Q3 Roadmap

## Initiative 1: Improve Onboarding
Research shows 40% of users drop off during signup.

Requirements:
1. Reduce signup form to 3 fields
2. Add social login options
3. Send welcome email with tutorial video
```

**After** (minimal changes):
```markdown
# Q3 Roadmap

<!-- @jig outcome priority:critical -->
## Initiative 1: Improve Onboarding
Research shows 40% of users drop off during signup.
Target: Reduce drop-off to 20%.
<!-- @jig end -->

<!-- @jig spec satisfies:^ -->
Requirements:
1. Reduce signup form to 3 fields
2. Add social login options (Google, GitHub)
3. Send welcome email with tutorial video
<!-- @jig end -->
```

**Scan**:
```bash
jigy scan --docs product/ --annotate-docs
jigy validate --check-coverage
```

### 6.3 Linking to Code and Tests

**Document**:
```markdown
<!-- @jig spec S-001 satisfies:O-001 -->
### Expense Validation Rules
- Amount must be positive
- Category must be valid
<!-- @jig end -->
```

**Test**:
```python
# @jig T-001 validates:S-001 covers:C-001
def test_expense_validation():
    """Test expense validation rules."""
    assert validate_expense(50.00, "food") == True
```

**Code**:
```python
# @jig C-001 implements:S-001
def validate_expense(amount, category):
    """Validate expense data."""
    if amount <= 0:
        raise ValueError("Amount must be positive")
    # ...
```

**Full Chain**:
```
O-001 (docs/prd.md)
  ← S-001 (docs/prd.md)
    ← T-001 (tests/test_expenses.py)
      ← C-001 (src/expenses.py)
```

---

## 7. CLI Integration

### 7.1 New Commands

#### `jigy scan --docs`

Scan documentation files for annotations.

```bash
jigy scan --docs PATHS [OPTIONS]

Options:
  --annotate-docs     Generate missing IDs and write back to files
  --update-docs       Update auto-generated status sections
  --validate          Check for broken references
  --watch             Watch mode - rescan on file changes

Examples:
  jigy scan --docs docs/ product/
  jigy scan --docs docs/ --annotate-docs
  jigy scan --docs docs/ --update-docs --validate
```

#### `jigy new doc`

Create a new document from template.

```bash
jigy new doc [OPTIONS]

Options:
  --title TITLE       Document title
  --type TYPE         Document type (prd, rfc, design, architecture)
  --template FILE     Custom template
  --edit              Open in editor after creation

Examples:
  jigy new doc --title "Export Feature" --type prd --edit
  jigy new doc --title "API Design" --type rfc
```

**Creates**:
```markdown
# Export Feature

<!-- @jig outcome priority:medium -->
## [Describe business goal]

**Success Criteria**:
- [Measurable criterion 1]
- [Measurable criterion 2]
<!-- @jig end -->

## Technical Approach

<!-- @jig spec satisfies:^ -->
### [Requirement name]

[Requirement details]
<!-- @jig end -->
```

#### `jigy docs validate`

Validate documentation structure and references.

```bash
jigy docs validate [OPTIONS]

Options:
  --strict            Fail on warnings
  --check-links       Verify all satisfies references exist
  --check-orphans     Find outcomes without specs

Examples:
  jigy docs validate --strict
  jigy docs validate --check-links --check-orphans
```

### 7.2 Updated Existing Commands

#### `jigy scan` (enhanced)

Now scans both code and docs:

```bash
jigy scan [OPTIONS]

Options:
  --source PATH       Source code directories (default: src/)
  --tests PATH        Test directories (default: tests/)
  --docs PATH         Documentation directories (default: docs/)
  --all               Scan source, tests, and docs
  --annotate-docs     Generate missing IDs in docs
  --update-docs       Update status sections in docs
  --update-specs      [DEPRECATED - use --update-docs]

Examples:
  jigy scan --all
  jigy scan --source src/ --tests tests/ --docs docs/ product/
  jigy scan --all --annotate-docs --update-docs
```

#### `jigy validate` (enhanced)

Now validates documents:

```bash
jigy validate [OPTIONS]

Checks:
  - All outcome/spec IDs are unique
  - All satisfies references exist
  - All specs link to at least one outcome
  - All code/test annotations reference valid specs
  - Documents are parseable

Examples:
  jigy validate --strict --check-coverage
```

### 7.3 Configuration

**File**: `.jig.toml`

```toml
[paths]
source = ["src/", "lib/"]
tests = ["tests/"]
docs = ["docs/", "product/", "design/"]  # NEW

[annotation]
format = "python"
marker = "@jig"
comment_style = "#"

[docs]  # NEW SECTION
annotation_style = "html-comment"  # html-comment | frontmatter
auto_generate_ids = true
id_algorithm = "content-hash"      # content-hash | sequential
update_status_blocks = true
status_block_position = "before-end"  # before-end | after-start

[validation]
require_tests = true
require_implementation = true
allow_orphans = false
min_alignment_index = 0.85
docs_must_have_ids = false  # NEW: Allow docs without IDs initially
```

---

## 8. Migration Path

### 8.1 From JIG v4.0 (Separate Files)

**Scenario**: Existing project with `.jig/outcomes/` and `.jig/specifications/`

```bash
# Step 1: Convert to annotation-based
jigy docs migrate --from separate-files --to annotated --output docs/

# This creates:
# docs/outcomes.md (all outcomes)
# docs/specifications.md (all specs grouped by outcome)

# Step 2: Review generated documents
# Edit for narrative flow, add context, merge related sections

# Step 3: Rescan
jigy scan --docs docs/ --validate

# Step 4: (Optional) Remove old structure
rm -rf .jig/outcomes/ .jig/specifications/
```

**Result**:
```markdown
# Outcomes and Specifications

<!-- @jig outcome O-001 priority:high -->
## Enable Accurate Expense Tracking
[Original content from O-001.md]
<!-- @jig end -->

<!-- @jig spec S-001 satisfies:O-001 -->
### Expense Validation Rules
[Original content from S-001.md]
<!-- @jig end -->

<!-- @jig spec S-002 satisfies:O-001 -->
### Expense Persistence
[Original content from S-002.md]
<!-- @jig end -->
```

### 8.2 From Unstructured Docs

**Scenario**: Existing docs with no JIG structure

```bash
# Step 1: Scan for outcome/spec candidates
jigy docs infer --input docs/ --interactive

# This uses LLM to:
# - Identify potential outcomes (goal statements, success criteria)
# - Identify potential specs (requirements, constraints)
# - Suggest where to add annotations

# Step 2: Review suggestions
# CLI shows:
#
# Found potential outcome at docs/prd.md:15
# "We want to help users track expenses..."
# [A]nnotate / [S]kip / [E]dit? a

# Step 3: Annotations added to files
jigy scan --docs docs/ --annotate-docs --validate
```

---

## 9. Advanced Features

### 9.1 Cross-Document References

**Problem**: Outcome in one doc, specs in another

**Solution**: Explicit references

```markdown
<!-- File: product/roadmap.md -->
<!-- @jig outcome O-q4-retention -->
## Improve User Retention
...
<!-- @jig end -->
```

```markdown
<!-- File: design/onboarding-redesign.md -->
<!-- @jig spec satisfies:O-q4-retention -->
### Simplified Signup Flow
...
<!-- @jig end -->
```

### 9.2 Nested Specifications

**Problem**: Hierarchical requirements

**Solution**: Parent references

```markdown
<!-- @jig spec S-001 satisfies:O-001 -->
### User Authentication
High-level authentication requirements.
<!-- @jig end -->

<!-- @jig spec S-002 satisfies:O-001 parent:S-001 -->
#### Password Requirements
Specific password rules (child of S-001).
<!-- @jig end -->

<!-- @jig spec S-003 satisfies:O-001 parent:S-001 -->
#### MFA Requirements
Multi-factor auth rules (child of S-001).
<!-- @jig end -->
```

### 9.3 Document Templates

**Product Requirements Template**:

```markdown
# [Feature Name]

## Context
[Background and motivation]

<!-- @jig outcome priority:medium -->
## Goal
[What business outcome are we seeking?]

**Success Criteria**:
- [Measurable criterion 1]
- [Measurable criterion 2]
<!-- @jig end -->

## User Stories
[Optional user stories for context]

## Requirements

<!-- @jig spec satisfies:^ -->
### Functional Requirement 1
[Detailed requirement description]
<!-- @jig end -->

<!-- @jig spec satisfies:^ -->
### Functional Requirement 2
[Detailed requirement description]
<!-- @jig end -->

## Non-Functional Requirements

<!-- @jig spec satisfies:^ tags:performance -->
### Performance
- Response time < 200ms
- Support 10,000 concurrent users
<!-- @jig end -->

<!-- @jig spec satisfies:^ tags:security -->
### Security
- Encrypt data at rest
- HTTPS only
<!-- @jig end -->

## Out of Scope
[What we're NOT doing]

## Open Questions
[Unresolved issues]
```

**RFC Template**:

```markdown
# RFC: [Title]

**Author**: [Name]
**Status**: Draft | In Review | Accepted | Rejected
**Created**: [Date]

## Summary
[One-paragraph overview]

<!-- @jig outcome priority:medium tags:architecture -->
## Problem
[What problem does this solve?]
<!-- @jig end -->

## Proposed Solution

<!-- @jig spec satisfies:^ -->
### Approach
[High-level approach]
<!-- @jig end -->

<!-- @jig spec satisfies:^ -->
### API Design
[Specific API details]
<!-- @jig end -->

## Alternatives Considered
[Other approaches and why they weren't chosen]

## Implementation Plan
[Phased rollout, milestones]

## Risks and Mitigations
[What could go wrong?]
```

### 9.4 Document Validation Rules

Custom validation beyond defaults:

```toml
# .jig.toml
[docs.validation]
# Require every outcome to have success criteria
require_success_criteria = true

# Require every spec to have acceptance criteria
require_acceptance_criteria = true

# Enforce heading level conventions
outcome_heading_level = 2  # ## Outcomes
spec_heading_level = 3     # ### Specs

# Require minimum content length
min_outcome_words = 20
min_spec_words = 10

# Enforce naming conventions
outcome_heading_pattern = "^(Enable|Improve|Reduce|Increase).*"
spec_heading_pattern = "^[A-Z].*"
```

---

## 10. Comparison: Before and After

### 10.1 Before (JIG v4.0)

**File structure**:
```
.jig/
├── outcomes/
│   ├── O-001.md (63 lines)
│   ├── O-002.md (71 lines)
│   ├── O-003.md (54 lines)
│   └── O-004.md (68 lines)
└── specifications/
    ├── S-001.md (89 lines)
    ├── S-002.md (76 lines)
    ├── S-003.md (82 lines)
    ├── S-004.md (71 lines)
    ├── S-005.md (64 lines)
    └── S-006.md (78 lines)
```

**Total**: 10 files, ~700 lines

**To read entire feature**: Open 7 files (1 outcome + 6 specs)

**To add new spec**: Create new file, copy template, fill in, update outcome's spec list

### 10.2 After (Annotation-Based)

**File structure**:
```
docs/
└── expense-tracking-feature.md (400 lines - includes narrative, diagrams, examples)
```

**Total**: 1 file, 400 lines (but much richer content due to narrative flow)

**To read entire feature**: Open 1 file, read top to bottom

**To add new spec**: Add section with annotation

**Example file**:
```markdown
# Expense Tracking Feature

## Background
[Rich context, user research, competitive analysis - 100 lines]

<!-- @jig outcome O-001 priority:high -->
## Goal: Enable Accurate Expense Tracking
[Business value, success criteria - 30 lines]
<!-- @jig end -->

## Design Exploration
[Mockups, user flows - 80 lines]

## Technical Requirements

<!-- @jig spec S-001 satisfies:O-001 -->
### Data Validation
[Requirements - 25 lines]
<!-- @jig end -->

<!-- @jig spec S-002 satisfies:O-001 -->
### Persistence Layer
[Requirements - 30 lines]
<!-- @jig end -->

[More specs...]

## Implementation Notes
[Architecture diagrams, dependencies - 60 lines]

## Rollout Plan
[Phased deployment strategy - 40 lines]

## Appendix
[Related research, links - 35 lines]
```

**Key differences**:
- ✅ Single coherent document
- ✅ Rich context preserved
- ✅ Natural reading flow
- ✅ Easy to review/comment
- ✅ Works with existing docs
- ✅ Diagrams and examples integrated

---

## 11. Implementation Considerations

### 11.1 Backward Compatibility

**Support both approaches**:

```toml
# .jig.toml
[docs]
style = "annotated"  # annotated | separate-files | hybrid
```

- `annotated`: Scan for annotations in docs
- `separate-files`: Use `.jig/outcomes/`, `.jig/specifications/`
- `hybrid`: Support both

### 11.2 ID Stability

**Challenge**: Content changes → hash changes → broken references

**Solution**: Use title + first sentence for hash (stable)

```python
def generate_stable_id(type, heading_text, content):
    # Extract first sentence or first 100 chars
    first_sentence = extract_first_sentence(content)

    # Create hash from heading + first sentence
    # This stays stable even if middle content changes
    stable_text = f"{heading_text}:{first_sentence}"
    hash = sha256(stable_text).hexdigest()[:8]

    return f"{type[0].upper()}-{hash}"
```

**Alternatively**: Manual IDs + migration warnings

```bash
jigy scan --docs docs/ --check-id-stability

# Warning: Content hash changed for O-abc123def
# Old hash: abc123def (from "Enable expense tracking: Users need...")
# New hash: xyz789ghi (from "Enable expense tracking: Research shows...")
#
# Recommendation: Keep existing ID O-abc123def
# Or use manual ID to avoid future changes:
#   <!-- @jig outcome O-expense-tracking -->
```

### 11.3 Parsing Edge Cases

**Multi-paragraph content**:
```markdown
<!-- @jig spec S-001 satisfies:O-001 -->
### Requirement A

First paragraph.

Second paragraph.

- List item 1
- List item 2

Some code:
\`\`\`python
def foo():
    pass
\`\`\`

More text.
<!-- @jig end -->
```

**Solution**: Extract everything between start and end tags

**Nested annotations** (not supported):
```markdown
<!-- @jig outcome O-001 -->
## Outcome

<!-- @jig spec S-001 satisfies:^ -->  ❌ ERROR: Nested annotations
### Spec
<!-- @jig end -->

<!-- @jig end -->
```

**Solution**: Keep flat structure, use document sections

### 11.4 Tool Integration

**Markdown editors**:
- Annotations render as invisible
- No special plugin needed

**GitHub/GitLab**:
- Comments don't render
- Diffs show annotation changes clearly

**Notion/Confluence**:
- Export to Markdown preserves comments
- Import annotations work

**Obsidian/Roam**:
- Annotations visible but harmless
- Can hide with CSS: `<!-- --> { display: none; }`

---

## 12. Benefits Analysis

### 12.1 For Authors

| Aspect | Separate Files | Annotation-Based | Winner |
|--------|----------------|------------------|--------|
| **Initial writing** | Must follow rigid template | Write naturally, annotate later | ✅ Annotated |
| **Reading flow** | Jump between 10 files | Single document, top-to-bottom | ✅ Annotated |
| **Context preservation** | Fragmented | Rich narrative | ✅ Annotated |
| **Collaboration** | Hard to review 10 files | Easy to review 1 file | ✅ Annotated |
| **Adding content** | Create new file | Add section | ✅ Annotated |
| **Diagrams/examples** | Where do they go? | Embedded naturally | ✅ Annotated |
| **Existing docs** | Must rewrite completely | Add annotations | ✅ Annotated |

### 12.2 For Readers

| Aspect | Separate Files | Annotation-Based | Winner |
|--------|----------------|------------------|--------|
| **Discoverability** | Must know file names | Browse documents | ✅ Annotated |
| **Understanding** | Fragmented context | Full narrative | ✅ Annotated |
| **Onboarding** | 10+ files to read | 1-2 docs to read | ✅ Annotated |
| **Traceability** | Same (via graph) | Same (via graph) | 🤝 Tie |

### 12.3 For Tools

| Aspect | Separate Files | Annotation-Based | Winner |
|--------|----------------|------------------|--------|
| **Parsing** | Simple (frontmatter) | Moderate (markdown parsing) | ✅ Separate |
| **Validation** | File = node | Must parse annotations | ✅ Separate |
| **ID management** | Filename = ID | Must generate/track IDs | ✅ Separate |
| **Flexibility** | Rigid | Very flexible | ✅ Annotated |
| **Graph construction** | Same | Same | 🤝 Tie |

**Verdict**: Annotation-based wins for humans, requires slightly more tooling complexity (acceptable trade-off).

---

## 13. Risks and Mitigations

### 13.1 Risk: ID Stability

**Risk**: Content changes break IDs → broken references

**Mitigations**:
1. Hash based on stable elements (heading + first sentence)
2. Manual ID override: `<!-- @jig outcome O-my-stable-id -->`
3. Migration warnings when hash changes
4. `jigy docs fix-refs` command to update broken references

### 13.2 Risk: Parsing Complexity

**Risk**: Markdown parsing is harder than file-per-node

**Mitigations**:
1. Use well-tested Markdown library (mistletoe, markdown-it)
2. Clear error messages for malformed annotations
3. Strict validation: `jigy docs validate --strict`
4. Comprehensive test suite

### 13.3 Risk: Tooling Fragmentation

**Risk**: Some tools don't preserve HTML comments

**Mitigations**:
1. Test with common tools (GitHub, Notion, Confluence)
2. Fallback: frontmatter style (YAML blocks)
3. Document tool compatibility
4. Provide conversion tools

### 13.4 Risk: Adoption Confusion

**Risk**: Teams confused by two approaches

**Mitigations**:
1. Clear migration guide
2. Default to annotation-based for new projects
3. Support hybrid mode during transition
4. Good documentation and examples

---

## 14. Recommended Rollout

### Phase 1: Core Implementation (MVP)
- [ ] Markdown parser with annotation extraction
- [ ] `jigy scan --docs` command
- [ ] ID generation (manual only)
- [ ] Basic validation
- [ ] Graph integration
- [ ] Documentation and examples

### Phase 2: Auto-ID Generation
- [ ] Content-hash based ID generation
- [ ] `--annotate-docs` flag
- [ ] ID stability checking
- [ ] Migration warnings

### Phase 3: Status Blocks
- [ ] Auto-generated status sections
- [ ] `--update-docs` flag
- [ ] Bi-directional sync

### Phase 4: Advanced Features
- [ ] `jigy docs infer` (LLM-based annotation suggestions)
- [ ] `jigy docs migrate` (separate-files → annotated)
- [ ] Cross-document references
- [ ] Nested specifications
- [ ] Custom validation rules

### Phase 5: Tooling Ecosystem
- [ ] VSCode extension
- [ ] GitHub Action
- [ ] Template library
- [ ] Interactive web viewer

---

## 15. Conclusion

### Key Innovations

1. **Natural documentation**: Write like humans, extract structure via annotations
2. **Zero redundancy**: One document, multiple extracted nodes
3. **Retrofitting support**: Add JIG to existing docs without rewriting
4. **Preserved context**: Rich narrative flow, diagrams, examples
5. **Flexible structure**: From rigid templates to freeform docs with tags

### The Core Trade-off

| Approach | Developer Experience | Parsing Complexity |
|----------|---------------------|-------------------|
| Separate files | ❌ Fragmented | ✅ Simple |
| Annotation-based | ✅ Natural | ⚠️ Moderate |

**Recommendation**: Prioritize developer experience. Parsing complexity is one-time implementation cost. Developer friction is ongoing.

### The Vision

```markdown
<!-- @jig outcome priority:critical -->
## Make expense tracking effortless

Enable users to track expenses without manual data entry,
reducing time spent on bookkeeping from 2 hours/week to 10 minutes/week.

**Success Metrics**:
- 90% of users actively tracking expenses after 30 days
- Average time per expense entry < 30 seconds
- 99% accuracy on automatic categorization
<!-- @jig end -->

## Research Insights
[User interviews, competitive analysis, behavioral data...]

## Design Exploration
[Mockups, prototypes, user testing results...]

<!-- @jig spec satisfies:^ -->
### Automatic Expense Detection
Monitor linked bank accounts and credit cards for new transactions.
Present detected expenses for user confirmation.

**Requirements**:
- Real-time transaction monitoring via Plaid API
- Confidence score for auto-categorization
- One-tap confirmation UI
- Manual override for miscategorized items
<!-- @jig end -->

[Implementation details, diagrams, API specs...]
```

This is a **real document** a human would write.
JIG extracts structure without destroying readability.
Intent stays visible. Reality stays traceable.
Alignment maintained.

---

**Status**: Proposal Ready for Review
**Next Steps**:
1. Gather feedback on syntax and workflow
2. Validate parsing complexity assumptions
3. Prototype MVP (Phase 1)
4. User testing with real documents

**Questions for Discussion**:
1. HTML comments vs. alternative syntax?
2. Auto-ID generation: content-hash vs. sequential vs. manual-only?
3. Support separate-files as legacy mode?
4. Priority: MVP features vs. advanced features?
