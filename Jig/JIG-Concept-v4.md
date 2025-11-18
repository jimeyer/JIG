# JIG: Jig Intent Graph v4.0
**Jig Intent Graph**
**An Alignment-Based Development System with Practical Implementation**
**Date:** 2025-11-12
**Status:** Architecture Proposal

---

## Executive Summary

JIG (Jig Intent Graph) represents a fundamental reimagining of software development as a **constraint-satisfaction and alignment problem** rather than a linear construction process.

The name "JIG" embodies the system's philosophy:
- **Jig** (noun): A template or guide that ensures components align correctly during construction
- **Intent Graph**: The explicit network of relationships between why we build (Outcomes), what we build (Specifications), how we verify (Tests), and how we implement (Code)

Instead of "writing code," development becomes:
1. **Expressing intent** in structured documentation (Outcomes and Specifications)
2. **Annotating reality** with lightweight decorators in tests and code
3. **Detecting misalignment** when changes create inconsistencies across the graph
4. **Restoring equilibrium** through AI-assisted repair operations
5. **Maintaining coherence** between business purpose and running systems

> "JIG doesn't build software forward or reverse—it maintains alignment across all representations of system meaning."

---

## 1. Core Philosophy: Alignment as First Principle

### 1.1 The Traditional Problem

Traditional development follows directional flows:
- **Forward**: Requirements → Design → Code → Tests
- **Reverse**: Code → Tests → Documentation → Intent

Problems:
- Assumes unidirectional causality
- Creates drift between artifacts
- Lacks unified model of "correctness"
- Manual synchronization burden
- Documentation becomes redundant and stale

### 1.2 The JIG Solution

JIG treats software as a **constraint network** seeking equilibrium, but recognizes a fundamental distinction:

**Intent vs Reality**
- **Intent** (Outcomes, Specifications): Lives in documentation files - these are conceptual and have no code equivalent
- **Reality** (Tests, Code): Lives in actual implementation - these are self-documenting and need only relational metadata

```
┌─────────────────────────────────────────────┐
│         Jig Intent Graph (JIG)              │
│                                             │
│  Intent Layer (Documentation):             │
│  ┌──────────┐       ┌──────────┐          │
│  │ Outcomes │──────→│  Specs   │          │
│  └──────────┘       └──────────┘          │
│       WHY               WHAT               │
│                                             │
│  Reality Layer (Annotations):              │
│  ┌──────────┐       ┌──────────┐          │
│  │  Tests   │──────→│   Code   │          │
│  └──────────┘       └──────────┘          │
│      VERIFY             HOW                │
│                                             │
└─────────────────────────────────────────────┘
         ↓                ↓
   ┌──────────┐    ┌──────────────┐
   │Constraint│    │  Alignment   │
   │   Rules  │───→│    Engine    │
   └──────────┘    └──────────────┘
                          ↓
              ┌──────────────────────┐
              │   Repair Operators   │
              │ (AI Agent Workflows) │
              └──────────────────────┘
```

**Core Principle**: Any change to any artifact introduces potential misalignment. JIG's role is to detect, localize, and repair until the graph is consistent again.

### 1.3 The Pragmatic Insight

**Don't Document What Already Documents Itself**

When you write:
```python
def validate_expense(amount, category):
    """
    Validate expense data before storage.

    Args:
        amount: Dollar amount (must be positive)
        category: Expense category (must be in VALID_CATEGORIES)
    """
    if amount <= 0:
        raise ValueError("Amount must be positive")
    # ...
```

This code **already describes what it does**. Creating a separate documentation file for this function is pure redundancy.

**JIG adds only relational metadata:**
```python
# @jig C-001 implements:S-001,S-002
def validate_expense(amount, category):
    """..."""
```

The annotation answers: "What specification does this implement?" Everything else is already in the code.

---

## 2. The OSTC Model in JIG

### 2.1 Four Types of Truth

JIG embodies four distinct epistemologies:

| Element | Type of Truth | Question Answered | Storage Method | Owner/Perspective |
|---------|--------------|-------------------|----------------|-------------------|
| **Outcome (O)** | Narrative truth | Why are we doing this? What value are we seeking? | `.jig/outcomes/O-XXX.md` | Product, business, users |
| **Specification (S)** | Logical truth | What must exist to fulfill the Outcome? | `.jig/specifications/S-XXX.md` | Design, product, architecture |
| **Test (T)** | Empirical truth | How do we know it's true? | `@jig` annotation in test files | QA, data, automation |
| **Code (C)** | Operational truth | How is it made real? | `@jig` annotation in source files | Engineering |

### 2.2 Why This Split?

**Intent Layers (O, S) = Separate Files**
- No code equivalent exists
- Purely conceptual
- Describes the "why" and "what"
- Maintained by humans manually
- Changes infrequently (business strategy, requirements)

**Reality Layers (T, C) = Annotations**
- Actual runnable code/tests already exist
- Self-documenting through docstrings, comments, and implementation
- JIG adds only relational metadata (implements what? validates what?)
- Changes frequently (implementation details)
- Stays synchronized automatically through scanning

### 2.3 The Chain of Evidence

JIG creates an explicit chain from human value to engineering proof:

```
Outcome (why) ──satisfies──> Specification (what) ──validates──> Test (verify) ──covers──> Code (how)
```

Each link in the chain must be maintained:
- **O ↔ S**: Ensures every Specification traces back to a declared Outcome (no specs without purpose)
- **S ↔ T**: Ensures every Specification has measurable verification
- **T ↔ C**: Ensures every passing Test links to code that implements that behavior

---

## 3. File Structure and Organization

### 3.1 Project Structure

```
project/
├── src/
│   └── myapp.py                    # Source code with @jig annotations
├── tests/
│   └── test_myapp.py               # Test code with @jig annotations
├── .jig/
│   ├── outcomes/
│   │   ├── O-001.md               # Manual: Business goals
│   │   └── O-002.md
│   ├── specifications/
│   │   ├── S-001.md               # Manual: Requirements
│   │   └── S-002.md
│   ├── generated/                  # Generated by jigy CLI
│   │   ├── code_index.json        # From source annotations
│   │   ├── test_index.json        # From test annotations
│   │   └── graph.json             # All relationships
│   └── README.md                   # Overview
├── .jig.toml                       # Configuration (optional)
└── README.md                       # Project README
```

**Manual files**: O-*.md, S-*.md (the "why" and "what")
**Generated files**: Everything in `generated/` (derived from code annotations)

### 3.2 Outcome File Template

**File**: `.jig/outcomes/O-XXX.md`

```markdown
---
id: O-XXX
type: outcome
title: <Short description of business goal>
created: <ISO 8601 timestamp>
modified: <ISO 8601 timestamp>
status: active
tags: [<relevant>, <tags>]
priority: high | medium | low
---

# <Title>

## Business Value
<Why this outcome matters - who benefits and how>

## Success Criteria
<How we know this outcome is achieved>
- Measurable criterion 1
- Measurable criterion 2

## Metrics
- **Metric Name**: Target value
  - Current: <current value>
  - Status: <on-track | at-risk | achieved>

## User Story (Optional)
As a <user type>, I want <capability> so that <benefit>.

## Stakeholders
- **Role**: Concern or responsibility

## Related Outcomes
<Links to parent/child outcomes if hierarchical>
```

### 3.3 Specification File Template

**File**: `.jig/specifications/S-XXX.md`

```markdown
---
id: S-XXX
type: specification
title: <Technical requirement or design decision>
created: <ISO 8601 timestamp>
modified: <ISO 8601 timestamp>
status: active
tags: [<relevant>, <tags>]
satisfies: [O-XXX, O-YYY]
---

# <Title>

## Description
<Clear technical description of what must be true>

## Requirements
<Specific, testable requirements>
- Requirement 1
- Requirement 2
- Requirement 3

## Scenarios
<Concrete scenarios that define behavior>
- **When**: <triggering condition>
  - **Then**: <expected system response>

## Invariants
<Properties that must always hold>
- Invariant 1
- Invariant 2

## Constraints
<Technical constraints or limitations>
- Performance: <requirement>
- Security: <requirement>
- Compliance: <requirement>

## Acceptance Criteria
<How to verify this spec is met>
- [ ] Criterion 1
- [ ] Criterion 2

## Implementation Status
<!-- Auto-updated by jigy scan --update-specs -->
- **Implemented by**: C-001, C-003
- **Validated by**: T-001, T-002, T-005
- **Coverage**: 3/5 tests passing
- **Last updated**: 2025-11-12T10:00:00Z

## Design Decisions
<Key technical choices made>

## Examples
<Concrete examples showing the spec in action>
```

### 3.4 Code Annotations

**In source code files** - Add single-line annotations above functions/classes:

```python
# expense_tracker.py

# @jig C-001 implements:S-001,S-002
def validate_expense(amount, category):
    """
    Validate expense data before storage.

    Args:
        amount: Dollar amount (must be positive)
        category: Expense category (must be in VALID_CATEGORIES)

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if category not in VALID_CATEGORIES:
        raise ValueError("Invalid category")
    return True


# @jig C-002 implements:S-003 depends:C-001
class ExpenseTracker:
    """Track and manage personal expenses."""

    def __init__(self):
        self.expenses = []

    # @jig C-003 implements:S-003 depends:C-001
    def add_expense(self, amount, category):
        """Add validated expense to tracker."""
        validate_expense(amount, category)
        self.expenses.append({"amount": amount, "category": category})
```

**Annotation Format**:
```
# @jig <node-id> implements:<spec-ids> depends:<code-ids>
```

**Keys**:
- `implements:` (required) - Comma-separated specification IDs this code implements
- `depends:` (optional) - Comma-separated code IDs this code depends on

### 3.5 Test Annotations

**In test files** - Add single-line annotations above test functions:

```python
# test_expense_tracker.py

import pytest
from expense_tracker import validate_expense, ExpenseTracker

# @jig T-001 validates:S-001 covers:C-001
def test_valid_expense_accepted():
    """Test that valid expense passes validation."""
    # Given
    amount = 50.00
    category = "food"

    # When
    result = validate_expense(amount, category)

    # Then
    assert result is True


# @jig T-002 validates:S-001 covers:C-001
def test_negative_amount_rejected():
    """Test that negative amount raises ValueError."""
    # Given
    amount = -10.00
    category = "food"

    # When/Then
    with pytest.raises(ValueError, match="Amount must be positive"):
        validate_expense(amount, category)


# @jig T-003 validates:S-001,S-002 covers:C-001
def test_invalid_category_rejected():
    """Test that invalid category raises ValueError."""
    # Given
    amount = 50.00
    category = "invalid"

    # When/Then
    with pytest.raises(ValueError, match="Invalid category"):
        validate_expense(amount, category)


# @jig T-004 validates:S-003 covers:C-002,C-003
def test_add_expense_to_tracker():
    """Test adding expense to tracker after validation."""
    # Given
    tracker = ExpenseTracker()

    # When
    tracker.add_expense(50.00, "food")

    # Then
    assert len(tracker.expenses) == 1
    assert tracker.expenses[0]["amount"] == 50.00
```

**Annotation Format**:
```
# @jig <node-id> validates:<spec-ids> covers:<code-ids>
```

**Keys**:
- `validates:` (required) - Comma-separated specification IDs this test validates
- `covers:` (required) - Comma-separated code IDs this test exercises

### 3.6 Generated Indices

**File**: `.jig/generated/code_index.json`

```json
{
  "metadata": {
    "generated_at": "2025-11-12T10:00:00Z",
    "tool_version": "jigy 1.0.0",
    "source_directories": ["src/"]
  },
  "code_nodes": [
    {
      "id": "C-001",
      "title": "validate_expense",
      "location": {
        "file": "src/expense_tracker.py",
        "line": 4,
        "symbol": "validate_expense",
        "type": "function"
      },
      "docstring": "Validate expense data before storage.",
      "implements": ["S-001", "S-002"],
      "depends_on": [],
      "signature": "validate_expense(amount, category)",
      "language": "python"
    },
    {
      "id": "C-003",
      "title": "ExpenseTracker.add_expense",
      "location": {
        "file": "src/expense_tracker.py",
        "line": 33,
        "symbol": "ExpenseTracker.add_expense",
        "type": "method"
      },
      "docstring": "Add validated expense to tracker.",
      "implements": ["S-003"],
      "depends_on": ["C-001"],
      "signature": "add_expense(self, amount, category)",
      "language": "python"
    }
  ]
}
```

**File**: `.jig/generated/test_index.json`

```json
{
  "metadata": {
    "generated_at": "2025-11-12T10:00:00Z",
    "tool_version": "jigy 1.0.0",
    "test_directories": ["tests/"]
  },
  "test_nodes": [
    {
      "id": "T-001",
      "title": "test_valid_expense_accepted",
      "location": {
        "file": "tests/test_expense_tracker.py",
        "line": 6,
        "symbol": "test_valid_expense_accepted"
      },
      "docstring": "Test that valid expense passes validation.",
      "validates": ["S-001"],
      "covers": ["C-001"],
      "status": "passing",
      "test_type": "unit",
      "last_run": "2025-11-12T10:00:00Z"
    },
    {
      "id": "T-002",
      "title": "test_negative_amount_rejected",
      "location": {
        "file": "tests/test_expense_tracker.py",
        "line": 19,
        "symbol": "test_negative_amount_rejected"
      },
      "docstring": "Test that negative amount raises ValueError.",
      "validates": ["S-001"],
      "covers": ["C-001"],
      "status": "passing",
      "test_type": "unit",
      "last_run": "2025-11-12T10:00:00Z"
    }
  ]
}
```

**File**: `.jig/generated/graph.json`

```json
{
  "metadata": {
    "generated_at": "2025-11-12T10:00:00Z",
    "tool_version": "jigy 1.0.0",
    "project_name": "Expense Tracker",
    "code_index": "code_index.json",
    "test_index": "test_index.json",
    "outcomes_dir": "../outcomes/",
    "specifications_dir": "../specifications/"
  },
  "nodes": {
    "outcomes": ["O-001", "O-002"],
    "specifications": ["S-001", "S-002", "S-003"],
    "tests": ["T-001", "T-002", "T-003", "T-004"],
    "code": ["C-001", "C-002", "C-003"]
  },
  "edges": [
    {
      "id": "E-001",
      "type": "satisfies",
      "source": "S-001",
      "target": "O-001",
      "source_file": ".jig/specifications/S-001.md",
      "confidence": 1.0,
      "rationale": "Data validation ensures accurate expense tracking"
    },
    {
      "id": "E-002",
      "type": "implements",
      "source": "C-001",
      "target": "S-001",
      "source_annotation": "src/expense_tracker.py:4",
      "confidence": 1.0,
      "rationale": "validate_expense() implements the validation rules"
    },
    {
      "id": "E-003",
      "type": "validates",
      "source": "T-001",
      "target": "S-001",
      "source_annotation": "tests/test_expense_tracker.py:6",
      "confidence": 1.0,
      "rationale": "Test verifies positive amount requirement"
    },
    {
      "id": "E-004",
      "type": "covers",
      "source": "T-001",
      "target": "C-001",
      "source_annotation": "tests/test_expense_tracker.py:6",
      "confidence": 1.0,
      "rationale": "Test directly exercises validation function"
    },
    {
      "id": "E-005",
      "type": "depends",
      "source": "C-003",
      "target": "C-001",
      "source_annotation": "src/expense_tracker.py:33",
      "confidence": 1.0,
      "rationale": "add_expense calls validate_expense"
    }
  ],
  "alignment_metrics": {
    "alignment_index": 0.94,
    "drift_rate": 0.002,
    "alignment_debt": 3,
    "confidence": 0.89,
    "coverage": {
      "outcomes_with_specs": 1.0,
      "specs_with_tests": 0.98,
      "tests_with_code": 0.96,
      "code_with_tests": 0.91
    },
    "edge_health": {
      "outcome_spec": 0.95,
      "spec_test": 0.92,
      "test_code": 0.94
    }
  }
}
```

---

## 4. The Alignment System

### 4.1 Alignment as First Principle

**Definition**: Alignment is the degree to which Outcomes, Specifications, Tests, and Code tell the same story and deliver on the same promise.

**Alignment is**:
- A **technical condition**: structural graph integrity
- A **semantic condition**: meaning coherence
- A **cultural condition**: shared understanding across teams

### 4.2 States of Alignment

| State | Description | System Response |
|-------|-------------|-----------------|
| **Aligned** | All nodes connected; constraints satisfied | Monitor for drift |
| **Mostly Aligned** | Minor gaps within tolerance | Advisory notices |
| **Misaligned** | Clear inconsistencies detected | Propose repairs |
| **Unaligned** | Orphaned artifacts with no traceability | Highlight gaps, suggest mapping |
| **Drifting** | Alignment degrading over time | Increase monitoring frequency |
| **Pending Alignment** | Known change awaiting repair | Queue repair operations |

### 4.3 Alignment Constraints

Declarative rules define what "aligned" means:

```yaml
constraints:
  - id: C1
    rule: "Every Outcome MUST have ≥1 Specification"
    violation_severity: critical

  - id: C2
    rule: "Every Specification MUST have ≥1 Test"
    violation_severity: critical

  - id: C3
    rule: "Every Test MUST have ≥1 Code node"
    violation_severity: critical

  - id: C4
    rule: "Test assertions MUST verify their Specification's scenarios"
    violation_severity: high

  - id: C5
    rule: "Code telemetry MUST demonstrate Outcome metrics are met"
    violation_severity: high

  - id: C6
    rule: "Specifications MUST NOT introduce behaviors outside their Outcome scope"
    violation_severity: medium

  - id: C7
    rule: "Tests MUST NOT verify behaviors outside their Specification"
    violation_severity: medium

  - id: C8
    rule: "Code MUST NOT implement behaviors outside its Test scope"
    violation_severity: medium

  - id: C9
    rule: "All Tests MUST have determinable pass/fail status"
    violation_severity: high

  - id: C10
    rule: "Code without Tests MUST be flagged as unverified"
    violation_severity: medium
```

### 4.4 Alignment Metrics

```yaml
alignment_index: 0.94        # Overall coherence score (0-1)
drift_rate: 0.002            # Daily degradation rate
alignment_debt: 3            # Count of unresolved violations
confidence: 0.89             # Certainty in current links

coverage:
  outcomes_with_specs: 100%
  specs_with_tests: 98%
  tests_with_code: 96%
  code_with_tests: 91%

edge_health:
  outcome_spec: 0.95         # O↔S alignment
  spec_test: 0.92            # S↔T alignment
  test_code: 0.94            # T↔C alignment
```

---

## 5. Detecting Misalignment

### 5.1 Misalignment Categories

| Pattern | Description | Detection Method |
|---------|-------------|------------------|
| **Orphaned Outcome** | Outcome with no Specifications | Graph traversal (O with no S edges) |
| **Unspecified Behavior** | Specification with no Tests | Graph traversal (S with no T edges) |
| **Unverified Code** | Code with no Tests | Coverage analysis (C with no T edges) |
| **Test-Spec Divergence** | Test assertions don't match Spec scenarios | Semantic similarity analysis |
| **Code-Test Divergence** | Code behavior doesn't match Test expectations | Test failure + semantic analysis |
| **Outcome Drift** | Metrics show Outcome not being achieved | Telemetry analysis vs Outcome targets |
| **Specification Creep** | Spec defines behavior outside Outcome scope | Semantic boundary analysis |
| **Test Gap** | Missing tests for critical Spec scenarios | Scenario coverage analysis |
| **Dead Code** | Code not referenced by any Test | Static analysis + coverage |
| **Failing Tests** | Tests exist but currently fail | CI/test runner status |
| **Broken References** | Annotation references non-existent node | Validation during scan |

### 5.2 Detection Engine Architecture

```yaml
detection_pipeline:
  - stage: structural_analysis
    checks:
      - missing_edges        # O-S, S-T, T-C connections
      - orphaned_nodes       # Isolated elements
      - dead_code_paths      # Unreachable code
      - broken_references    # Invalid node IDs in annotations

  - stage: semantic_analysis
    checks:
      - intent_drift         # O vs S semantic distance
      - behavior_drift       # S vs T semantic distance
      - implementation_drift # T vs C semantic distance

  - stage: empirical_analysis
    checks:
      - test_failures        # T status != pass
      - metric_deviation     # Telemetry vs Outcome targets
      - coverage_gaps        # Untested code paths

  - stage: temporal_analysis
    checks:
      - drift_rate           # Alignment degradation velocity
      - stale_artifacts      # No updates in >90 days
      - version_skew         # Dependent versions mismatched
```

### 5.3 Example Misalignment Report

```yaml
misalignment_report:
  timestamp: "2025-11-12T10:30:00Z"
  alignment_index: 0.87

  violations:
    - id: V001
      type: "missing_tests"
      severity: critical
      description: "Specification S-002 has no associated Tests"
      affected_nodes:
        - spec: S-002
      suggested_repair: "Generate test suite from specification scenarios"

    - id: V002
      type: "test_failure"
      severity: high
      description: "Test T-005 failing since 2025-11-10"
      affected_nodes:
        - test: T-005
        - code: C-003
      suggested_repair: "Code change broke test; propose code rollback or test update"

    - id: V003
      type: "broken_reference"
      severity: critical
      description: "Code C-007 references non-existent specification S-999"
      affected_nodes:
        - code: C-007
      suggested_repair: "Update annotation to reference valid specification or create S-999"

    - id: V004
      type: "outcome_drift"
      severity: medium
      description: "Outcome 'Fast Response Time' target 120ms, actual p95 is 187ms"
      affected_nodes:
        - outcome: O-003
      suggested_repair: "Performance optimization or adjust target"
```

---

## 6. Repairing Misalignment

### 6.1 Repair Philosophy

JIG doesn't prescribe a single direction for repairs. Depending on context, alignment can be restored by:
- **Updating downstream** (changing Tests or Code to match Specs)
- **Updating upstream** (revising Specs or Outcomes to match reality)
- **Bidirectional adjustment** (meeting in the middle)

The repair engine proposes options; humans choose direction based on business context.

### 6.2 Repair Operations

| Operation | Direction | When to Use | Example |
|-----------|-----------|-------------|---------|
| **Spec Generation** | O → S | New Outcome needs formalization | Generate Specification from Outcome description |
| **Test Generation** | S → T | Specification lacks verification | Generate test suite from Spec scenarios |
| **Code Generation** | T → C | Tests exist but no implementation | Generate code that passes Tests |
| **Spec Update** | T → S | Tests reveal Spec is incomplete | Update Specification based on Test coverage |
| **Outcome Realignment** | S → O | Specifications drifted from original intent | Propose Outcome revision or new Outcome |
| **Test Update** | S → T | Specification changed | Update Tests to match new Spec |
| **Code Refactor** | T → C | Code fails Tests | Refactor code to pass Tests |
| **Annotation Fix** | Any → Any | Broken reference in annotation | Update annotation to reference valid node |
| **Evidence Linking** | C → T → S → O | Existing artifacts need connection | Establish traceability links |

### 6.3 AI-Assisted Repair Agents

| Agent | Responsibility | Autonomy Level | Human Loop |
|-------|----------------|----------------|------------|
| **Spec Drafter** | Generate Specifications from Outcomes | Semi-autonomous | Review before commit |
| **Test Generator** | Generate test suites from Specifications | Semi-autonomous | Review before integration |
| **Test Updater** | Update Tests when Specs change | Advisory | Approval required |
| **Code Suggester** | Propose code changes to pass Tests | Advisory | Approval required |
| **Annotation Fixer** | Fix broken references in annotations | Semi-autonomous | Review changes |
| **Evidence Linker** | Connect artifacts via semantic analysis | Autonomous | Post-hoc review |
| **Drift Monitor** | Detect alignment degradation | Autonomous | Alert only |
| **Metric Collector** | Gather telemetry for Outcome validation | Autonomous | Background operation |

---

## 7. The jigy CLI

### 7.1 Command Overview

```bash
jigy [COMMAND] [OPTIONS]
```

### 7.2 Core Commands

#### jigy init

Initialize a new JIG project structure.

```bash
jigy init [OPTIONS]

Options:
  --path PATH           Project directory (default: current directory)
  --template TEMPLATE   Use template (basic, python, javascript, etc.)
  --no-examples         Skip example files
```

Creates:
- `.jig/` directory structure
- `.jig.toml` configuration file
- Example outcome and specification files (unless --no-examples)
- `.jig/README.md` with getting started instructions

#### jigy scan

Scan source and test files to extract JIG annotations and generate indices.

```bash
jigy scan [OPTIONS]

Options:
  --source PATH       Directory containing source code (default: src/)
  --tests PATH        Directory containing test files (default: tests/)
  --output PATH       Directory for generated files (default: .jig/generated/)
  --validate          Check for broken references and inconsistencies
  --update-specs      Update "Implementation Status" in specification files
  --watch             Watch mode - automatically rescan on file changes
  --language LANG     Programming language (auto-detected if not specified)
```

**What it does**:
1. Scans all source files for `@jig` annotations
2. Extracts docstrings, line numbers, signatures
3. Generates `code_index.json` and `test_index.json`
4. Reads O-*.md and S-*.md frontmatter
5. Generates `graph.json` with all edges
6. Computes alignment metrics
7. Optionally updates S-*.md files with current implementation status

**Example**:
```bash
jigy scan --source src/ --tests tests/ --update-specs --validate
```

#### jigy validate

Check consistency, completeness, and alignment health.

```bash
jigy validate [OPTIONS]

Options:
  --strict            Fail on any warnings
  --check-coverage    Ensure all specs have tests/code
  --min-alignment N   Minimum alignment index required (0.0-1.0)
  --report FORMAT     Output format (text, json, html)
```

**Checks**:
- All node IDs are unique
- All referenced nodes exist (no dangling references)
- All specifications have at least one implementing code node
- All specifications have at least one validating test
- All code nodes reference valid specification IDs
- File paths in indices actually exist
- Line numbers are reasonable
- Alignment index meets threshold

**Example**:
```bash
jigy validate --strict --check-coverage --min-alignment 0.85
```

#### jigy graph

Generate visual representations of the intent graph.

```bash
jigy graph [OPTIONS]

Options:
  --format FORMAT     Output format (html, svg, dot, mermaid)
  --output FILE       Output file path
  --from NODE         Trace from specific node
  --to NODE           Trace to specific node
  --layer LAYER       Show only specific layer (O, S, T, C)
  --interactive       Generate interactive HTML visualization
```

**Example**:
```bash
jigy graph --format html --output graph.html --interactive
jigy graph --from O-001 --to C-003 --format svg --output trace.svg
```

#### jigy align

Check and restore alignment across the graph.

```bash
jigy align [OPTIONS]

Options:
  --detect            Detect misalignments only (no repairs)
  --propose           Propose repairs without applying
  --auto-fix          Automatically apply safe repairs
  --repair-type TYPE  Focus on specific repair type
  --min-confidence N  Minimum confidence for auto-repairs (0.0-1.0)
```

**Example**:
```bash
jigy align --detect
jigy align --propose
jigy align --auto-fix --min-confidence 0.9
```

#### jigy new

Create a new node (outcome or specification).

```bash
jigy new [TYPE] [OPTIONS]

Types:
  outcome      Create new outcome file
  spec         Create new specification file

Options:
  --id ID             Node ID (auto-generated if not specified)
  --title TITLE       Node title
  --template FILE     Use custom template
  --edit              Open in editor after creation
```

**Example**:
```bash
jigy new outcome --title "Track user expenses" --edit
jigy new spec --title "Expense validation rules" --edit
```

#### jigy show

Display information about nodes and their relationships.

```bash
jigy show [NODE_ID] [OPTIONS]

Options:
  --full              Show full details including content
  --edges             Show all connected edges
  --trace             Show full trace to/from this node
  --format FORMAT     Output format (text, json, markdown)
```

**Example**:
```bash
jigy show S-001
jigy show C-003 --edges
jigy show O-001 --trace --format markdown
```

#### jigy coverage

Generate coverage reports showing alignment completeness.

```bash
jigy coverage [OPTIONS]

Options:
  --type TYPE         Coverage type (specs, tests, code, all)
  --format FORMAT     Output format (text, html, json)
  --output FILE       Output file path
  --threshold N       Minimum coverage threshold (0-100)
```

**Example**:
```bash
jigy coverage --type all --format html --output coverage.html
jigy coverage --type specs --threshold 90
```

#### jigy bootstrap

Bootstrap JIG from existing codebase (reverse engineering).

```bash
jigy bootstrap [OPTIONS]

Options:
  --source PATH       Source code directory
  --tests PATH        Test directory
  --interactive       Interactive mode with prompts
  --confidence N      Minimum confidence for auto-linking (0.0-1.0)
```

**What it does**:
1. Analyzes existing code and tests
2. Infers specifications from implementation
3. Prompts for outcome articulation
4. Generates draft O and S files
5. Creates initial annotations
6. Generates graph

**Example**:
```bash
jigy bootstrap --source src/ --tests tests/ --interactive
```

### 7.3 Configuration File

**File**: `.jig.toml` (in project root)

```toml
[jig]
version = "4.0"
project_name = "My Project"

[paths]
source = ["src/", "lib/"]
tests = ["tests/"]
outcomes = ".jig/outcomes/"
specifications = ".jig/specifications/"
generated = ".jig/generated/"

[annotation]
format = "python"  # python, javascript, java, rust, go, etc.
marker = "@jig"
comment_style = "#"  # #, //, /*, etc.

[validation]
require_tests = true          # All specs must have tests
require_implementation = true # All specs must have code
allow_orphans = false        # No disconnected nodes
min_alignment_index = 0.85   # Minimum alignment score

[generation]
auto_update_specs = true     # Update "Implementation Status" in S-*.md
include_rationale = true     # Generate rationale for edges
timestamp_format = "iso8601"
compute_metrics = true       # Compute alignment metrics

[alignment]
drift_threshold = 0.01       # Alert if drift rate exceeds this
max_alignment_debt = 10      # Maximum unresolved violations
auto_repair_confidence = 0.9 # Confidence threshold for auto-repairs

[testing]
test_runner = "pytest"       # Test framework to use
coverage_tool = "coverage"   # Coverage tool to use
```

---

## 8. Workflows and Usage Patterns

### 8.1 Top-Down Development (New Feature)

**Scenario**: Building a new feature from scratch

```bash
# 1. Create outcome
jigy new outcome --title "Enable expense categorization" --edit

# 2. Create specifications
jigy new spec --title "Category validation rules" --edit
jigy new spec --title "Category persistence" --edit

# 3. Write tests (TDD)
# In test file:
# @jig T-010 validates:S-005 covers:C-008
def test_category_validation():
    # ...

# 4. Implement code
# In source file:
# @jig C-008 implements:S-005
def validate_category(category):
    # ...

# 5. Scan and validate
jigy scan --source src/ --tests tests/ --update-specs
jigy validate --check-coverage

# 6. Verify alignment
jigy align --detect
jigy coverage --type all
```

### 8.2 Bottom-Up Development (Existing Codebase)

**Scenario**: Adding JIG to legacy code

```bash
# 1. Initialize JIG structure
jigy init --path .

# 2. Bootstrap from existing code
jigy bootstrap --source src/ --tests tests/ --interactive

# This will:
# - Analyze code and tests
# - Generate draft O and S files
# - Prompt you to refine them
# - Create initial annotations

# 3. Review and refine generated outcomes/specs
# Edit .jig/outcomes/O-*.md files
# Edit .jig/specifications/S-*.md files

# 4. Rescan with human-refined docs
jigy scan --source src/ --tests tests/ --validate

# 5. Fix any misalignments
jigy align --propose
jigy align --auto-fix --min-confidence 0.9

# 6. Generate report
jigy coverage --format html --output coverage.html
```

### 8.3 Test-Driven Development (TDD)

**Scenario**: Classic TDD workflow

```bash
# 1. Document intent (O and S files already exist)

# 2. Write failing test
# @jig T-015 validates:S-007 covers:C-012
def test_new_feature():
    assert new_feature() == expected_result

# 3. Run tests (red)
pytest

# 4. Scan to update graph
jigy scan --source src/ --tests tests/

# 5. Check alignment (will show C-012 missing)
jigy align --detect
# Warning: T-015 references missing code node C-012

# 6. Implement code
# @jig C-012 implements:S-007
def new_feature():
    # implementation

# 7. Run tests (green)
pytest

# 8. Rescan and validate alignment
jigy scan --source src/ --tests tests/
jigy validate --check-coverage

# 9. Refactor (refactor)
# Update implementation
# Tests should still pass

# 10. Final validation
jigy align --detect
jigy coverage --type all
```

### 8.4 Continuous Integration

**Scenario**: Integrate JIG into CI/CD pipeline

```yaml
# .github/workflows/jig-validation.yml
name: JIG Alignment Check

on: [push, pull_request]

jobs:
  alignment:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install jigy
        run: pip install jigy

      - name: Scan codebase
        run: jigy scan --source src/ --tests tests/ --validate

      - name: Validate alignment
        run: jigy validate --strict --check-coverage --min-alignment 0.85

      - name: Check for drift
        run: jigy align --detect

      - name: Generate coverage report
        run: jigy coverage --format html --output coverage.html

      - name: Upload coverage
        uses: actions/upload-artifact@v2
        with:
          name: jig-coverage
          path: coverage.html
```

### 8.5 Daily Developer Workflow

**Morning**: Check alignment status
```bash
jigy validate
jigy align --detect
```

**During Development**: Watch mode for live feedback
```bash
jigy scan --watch --source src/ --tests tests/
```

**Before Commit**: Validate changes
```bash
jigy scan --source src/ --tests tests/ --validate
jigy align --detect
jigy coverage --type all
```

**Code Review**: Show traceability
```bash
jigy show C-015 --trace --format markdown > trace.md
```

---

## 9. Bootstrapping from Existing Codebases

### 9.1 The Bootstrap Challenge

Most organizations won't start with a perfect JIG graph. They have:
- Working code (often well-structured)
- Partial test coverage (60-90%)
- Scattered documentation (outdated, unstructured)
- Implicit outcomes (in people's heads, old tickets, folklore)

JIG must **extract structure from reality** rather than impose structure from scratch.

### 9.2 Bootstrap Principle

> _JIG doesn't rewrite the system; it reveals its structure of truth._

The codebase already contains most of the graph—just in implicit, fragmented form. JIG's mission is to **extract**, **structure**, and **align** those implicit truths into an explicit graph.

### 9.3 Three-Phase Bootstrap Process

#### Phase 1: Discovery — Build the "T-C Backbone"

Start from what's most reliable: Code and Tests.

| Input | Method | Output Artifact |
|-------|--------|-----------------|
| Source files | Static analysis (AST / dependency graph / docstrings / signatures) | **Code Nodes (C)** — functions, classes, modules |
| Test suite | Parse test names, assertions, fixtures, coverage reports | **Test Nodes (T)** — linked to code via imports/coverage |
| Coverage reports | Cross-map code ↔ tests | Edge links T ↔ C + confidence score |
| Build system / CI logs | Detect active vs dead code paths | Execution frequency; activity heatmap |

**Result**: The **bottom half** of the graph with solid T ↔ C edges.

#### Phase 2: Inference — Reconstruct the "S Layer"

Once the backbone is built, infer **Specifications** from the Test-Code relationships.

| Input | Method | Output |
|-------|--------|--------|
| Test names, assertions | LLM summarization + pattern mining | Candidate **Specifications** |
| Docstrings & comments | Extract behavior statements | Supplement to inferred specs |
| API specs / type hints / schemas | Deterministic rules | Structured input-output definitions |
| Commit messages | Semantic clustering | Evolution history of specs |

**Result**: A set of **draft Specifications**, each linked to Tests and Code:

```markdown
---
id: S-001
type: specification
title: Expense validation rules
inferred_from: [test_expense_validation.py, validate.py]
confidence: 0.82
status: draft
---

# Expense validation rules

## Requirements (Inferred)
- Amount must be positive decimal number
- Category must be in valid categories list
- Maximum amount: $10,000

## Needs Review
- [ ] Confirm requirements are complete
- [ ] Add constraints
- [ ] Link to outcome
```

#### Phase 3: Elicitation — Capture "O Layer"

No tool can read Outcomes from code—they live in human memory.

| Method | Purpose | Example |
|--------|---------|---------|
| **Spec clustering** | Group related specs | "These 12 specs relate to user identity—what Outcome?" |
| **Goal inference from KPIs** | Suggest Outcome candidates | "'Expense accuracy' metric → O: 'Accurate Financial Records'" |
| **Product doc mining** | NLP pass over README, tickets, OKRs | Extract value statements |
| **Alignment Interview** | Structured Q&A with PM/lead | "Which specs matter most to business?" |

**Result**: Outcomes linked to Specifications with confidence scores.

### 9.4 Bootstrap Command Flow

```bash
# Start interactive bootstrap
jigy bootstrap --source src/ --tests tests/ --interactive

# Phase 1: Discovery (automatic)
# Scanning source files...
# Found 45 functions, 12 classes
# Scanning test files...
# Found 89 tests
# Cross-referencing with coverage...
# Created 57 code nodes, 89 test nodes

# Phase 2: Inference (semi-automatic)
# Analyzing test-code relationships...
# Inferred 23 specification candidates
#
# Review inferred specification S-001:
# Title: Expense validation rules
# Confidence: 0.82
# Linked to: T-001, T-002, T-003, C-001
#
# [E]dit / [A]ccept / [S]kip / [Q]uit? a

# Phase 3: Elicitation (interactive)
# Specifications grouped into 5 clusters.
#
# Cluster 1 (8 specs related to expense tracking):
# Suggested outcome: "Enable accurate expense tracking"
#
# [E]dit / [A]ccept / [C]ustom / [S]kip? a

# Bootstrap complete!
# Created:
# - 5 outcome files
# - 23 specification files
# - 146 annotations added to code
#
# Next steps:
# 1. Review and refine .jig/outcomes/*.md
# 2. Review and refine .jig/specifications/*.md
# 3. Run: jigy scan --validate
# 4. Run: jigy align --detect
```

---

## 10. Benefits of JIG

### 10.1 Eliminates Redundancy

| Traditional Approach | JIG Approach |
|---------------------|--------------|
| Write function | Write function |
| Write separate doc describing function ❌ | Add one-line annotation ✅ |
| Write test | Write test |
| Write separate doc describing test ❌ | Add one-line annotation ✅ |
| Manually maintain documentation ❌ | Auto-generate graph ✅ |
| Documentation drifts ❌ | Always in sync ✅ |

### 10.2 Single Source of Truth

- **Implementation details**: In the actual code (docstrings, comments, logic)
- **JIG metadata**: In annotations (which spec? which test?)
- **Business intent**: In O/S markdown files (why? what?)
- **Relationships**: In generated graph (auto-updated)

### 10.3 Developer-Friendly

```python
# Minimal annotation - just relationship metadata
# @jig C-002 implements:S-001,S-003

# Everything else is what you'd write anyway:
def save_expense(amount, category, description):
    """
    Save expense to database after validation.

    Args:
        amount: Dollar amount (positive decimal)
        category: Expense category
        description: Optional description

    Returns:
        Expense ID if successful

    Raises:
        ValueError: If validation fails
        DatabaseError: If save fails
    """
    # Implementation...
```

### 10.4 Automatic Synchronization

```bash
# After any code change:
jigy scan --watch

# Automatically:
# - Updates code_index.json
# - Updates test_index.json
# - Regenerates graph.json
# - Computes alignment metrics
# - Validates all references
# - Detects misalignments
```

### 10.5 Tool-Enabled Workflows

- **IDE integration**: Jump from spec to implementation
- **Coverage reports**: Which specs lack tests?
- **Impact analysis**: What breaks if I change this spec?
- **Onboarding**: New dev reads O/S docs, tools show implementation
- **Compliance**: Automated traceability for audits
- **AI assistance**: Context-aware code generation

### 10.6 Cultural Transformation

JIG creates a **shared language** across roles:

- **Product**: "Let's ensure O-003 is properly specified"
- **QA**: "S-005 needs more test coverage"
- **Engineering**: "This PR implements S-007 and S-008"
- **Management**: "Our alignment index is 0.94, up from 0.87"

---

## 11. Theoretical Foundations

### 11.1 Formal Methods Inspirations

JIG draws from proven formal methods:

| Technique | Source Domain | Application in JIG |
|-----------|---------------|-------------------|
| **Bidirectional Transformations (BX)** | Programming languages, databases | OSTC elements are projections of one system meaning; changes propagate bidirectionally |
| **Triple Graph Grammars (TGG)** | Model-Driven Engineering | Correspondence links between O, S, T, C with sync rules |
| **Truth Maintenance Systems (TMS)** | AI reasoning | Nodes are beliefs; edges are justifications; changes propagate consequences |
| **Constraint Solving (SMT/MaxSAT)** | Formal verification | Alignment as satisfiability; repairs as minimal edit sets |
| **Reactive Dataflow** | Spreadsheets, build systems | Changes invalidate dependent subgraphs; incremental recomputation |

### 11.2 The JIG as a Jig

A physical **jig** in manufacturing:
- Holds components in place
- Ensures alignment during assembly
- Guides tools to the right position
- Enables repeatable, accurate production
- Makes quality systematic, not accidental

The **Jig Intent Graph**:
- Holds artifacts (O, S, T, C) in alignment
- Ensures coherence during development
- Guides changes to maintain consistency
- Enables repeatable, traceable development
- Makes quality systematic, not accidental

---

## 12. Governance and Policy

### 12.1 Alignment Policies

Organizations can configure JIG behavior through `.jig.toml`:

```toml
[alignment]
strictness = "medium"  # low | medium | high

[auto_repair]
spec_generation = false      # Require human review
test_generation = true       # Can run autonomously
code_generation = false      # Advisory only
link_inference = true        # Can run autonomously
annotation_fixes = true      # Can fix broken references

[thresholds]
minimum_alignment_index = 0.85
maximum_alignment_debt = 10
test_coverage_requirement = 80
min_confidence_auto_repair = 0.9

[notifications]
alignment_drift = "team_channel"
test_failures = "owner_email"
critical_violations = "pager_duty"

[exemptions]
patterns = [
    "experimental/*",    # R&D code, alignment optional
    "vendor/*",          # Third-party code, JIG not applicable
    "scripts/*"          # Utility scripts
]
```

### 12.2 Roles and Responsibilities

| Role | JIG Responsibilities | CLI Usage |
|------|---------------------|-----------|
| **Product Manager** | Define and refine Outcomes; prioritize features | `jigy new outcome`, `jigy coverage` |
| **Designer/Architect** | Draft and maintain Specifications | `jigy new spec`, `jigy graph` |
| **QA Engineer** | Write and maintain Tests; validate coverage | `jigy validate --check-coverage` |
| **Software Engineer** | Write Code; ensure Tests pass; add annotations | `jigy scan --watch` |
| **DevOps/SRE** | Integrate JIG with CI/CD; monitor health | `jigy align --detect` in CI |
| **Engineering Manager** | Oversee alignment health; manage debt | `jigy coverage --format html` |

---

## 13. Success Metrics

### 13.1 Technical Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Alignment Index** | ≥0.90 | High coherence without perfection burden |
| **Mean Time to Realign (MTTR)** | <2 hours | Fast repair cycles |
| **Repair Approval Rate** | ≥85% | AI proposals are high-quality |
| **Constraint Violation Rate** | <5% | Preventive health |
| **Test-Spec Coverage** | ≥95% | All Specs have verification |
| **Code-Test Coverage** | ≥90% | All Code has tests |
| **Edge Confidence** | ≥0.85 | Reliable traceability |

### 13.2 Human Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Developer Satisfaction** | ≥4/5 | Tool is helpful, not burdensome |
| **Cross-Team Alignment Understanding** | ≥80% agreement | Shared mental model |
| **Time Spent on Manual Sync** | -50% vs baseline | Efficiency gain |
| **Onboarding Time** | -30% vs baseline | Graph accelerates understanding |
| **Communication Quality** | ≥4/5 | Shared language improves collaboration |

### 13.3 Business Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Feature-to-Intent Traceability** | 100% | Auditability and compliance |
| **Misalignment-Caused Bugs** | -40% | Better semantic checks catch errors early |
| **Strategy-Execution Lag** | -25% | Faster propagation of business changes |
| **Time from Outcome to Deployed Code** | -20% | Streamlined workflow |
| **Documentation Staleness** | -60% | Living graph replaces static docs |

---

## 14. Future Directions

### 14.1 Tooling Enhancements

- **IDE Plugins**: VSCode, IntelliJ, Vim extensions
- **Visual Graph Editor**: Drag-and-drop OSTC construction
- **Natural Language Interface**: "Show me all outcomes without tests"
- **Real-Time Collaboration**: Multi-user JIG editing
- **Mobile Dashboard**: View alignment metrics on mobile

### 14.2 AI & Automation

- **Fine-Tuned Models**: JIG-specific smaller models (reduce cost)
- **Reinforcement Learning**: Agents learn repair preferences
- **Multi-Agent Negotiation**: Competing repair proposals
- **Predictive Drift Detection**: ML predicts misalignment before it occurs
- **Auto-Documentation**: Generate O/S drafts from code analysis

### 14.3 Domain Extensions

- **Compliance Mapping**: Link to SOC2, GDPR, HIPAA requirements
- **Safety-Critical Systems**: Enhanced verification for medical/automotive
- **Design-to-Code**: Figma/Sketch plugins generate Specifications
- **Multi-Repository JIG**: Distributed graphs across microservices
- **Real-Time Systems**: Timing constraints and performance profiles

### 14.4 Language Support

**Current**: Python (primary focus)

**Planned**:
- JavaScript/TypeScript
- Java
- Go
- Rust
- C#
- Ruby
- PHP

---

## 15. FAQ

### Q: Why "JIG"?

**A**: A jig is a manufacturing tool that holds components in alignment during assembly. The Jig Intent Graph does the same for software artifacts—it maintains alignment between intent (Outcomes, Specifications) and reality (Tests, Code).

### Q: Why "jigy" instead of "jig" for the CLI?

**A**: To avoid namespace collisions with existing tools and make it more unique/searchable. The 'y' makes it friendly and distinctive.

### Q: How is JIG different from existing documentation tools?

**A**:
- **Not just documentation**: JIG is an alignment system, not a doc generator
- **No redundancy**: Tests and code self-document; we add only relational metadata
- **Active synchronization**: Automatic updates when code changes
- **Constraint-based**: Explicit alignment rules and violations
- **AI-assisted**: Repair agents help maintain coherence

### Q: How much overhead does JIG add?

**A**: Minimal:
- One-line annotations for code and tests
- Outcome/spec files you'd write anyway (as docs or tickets)
- `jigy scan` runs in seconds for typical projects
- Most developers spend <5% additional time on JIG maintenance

### Q: Can I adopt JIG incrementally?

**A**: Yes! Bootstrap from existing code, start with one module, gradually expand coverage.

### Q: What if my tests don't follow a standard pattern?

**A**: JIG works with any test framework. Annotations are language-agnostic. Configure test runner in `.jig.toml`.

### Q: How does JIG handle legacy code with no tests?

**A**: Bootstrap identifies untested code, generates test stubs with annotations, highlights gaps in coverage reports.

### Q: Can I use JIG with microservices?

**A**: Yes. Each service has its own `.jig/` directory. Future versions will support cross-repository graphs.

### Q: Is JIG open source?

**A**: [To be determined - specify license]

---

## 16. Conclusion

JIG (Jig Intent Graph) transforms software development from a construction process into an **alignment maintenance discipline**.

**Key Innovations**:
1. **OSTC Model**: Four clear layers of truth (Narrative, Logical, Empirical, Operational)
2. **Intent vs Reality Split**: Documentation for concepts, annotations for implementation
3. **Zero Redundancy**: Don't document what already documents itself
4. **Alignment Engine**: Treats development as constraint satisfaction
5. **Omnidirectional Workflows**: No forward or reverse—just continuous equilibrium
6. **AI as Repair Operators**: Structured, bounded AI use
7. **Bootstrap Capability**: Works with legacy code and greenfield projects
8. **Chain of Evidence**: Explicit O→S→T→C traceability
9. **Developer-First Design**: Minimal overhead, maximum value

**The Vision**:
> Developers express intent in structured documentation.
> Developers annotate reality with lightweight metadata.
> AI maintains alignment between business goals and running systems.
> Teams share a living, traceable graph from strategy to implementation.
> Tests prove that Code fulfills Specifications that deliver Outcomes.

**What JIG Provides**:
- **For Product**: Clear traceability from business value to implementation
- **For QA**: Comprehensive verification that specs are tested
- **For Engineering**: Context-aware development with clear requirements
- **For Management**: Quantified alignment metrics and health dashboards
- **For Compliance**: Automated audit trails and evidence chains

**The Metaphor**:
Like a jig in manufacturing, JIG holds your software artifacts in alignment during development, ensuring that intent and implementation tell the same story, deliver on the same promise, and maintain coherence across changes.

**Next Steps**:
1. Install jigy: `pip install jigy`
2. Initialize your project: `jigy init`
3. Bootstrap existing code: `jigy bootstrap --interactive`
4. Or start fresh: Create O and S files, add annotations
5. Scan and validate: `jigy scan --validate`
6. Monitor alignment: `jigy align --detect`

---

## 17. References & Acknowledgments

### 17.1 Theoretical Foundations

1. **Bidirectional Transformations (BX)**
   - Czarnecki et al., "Feature-based survey of model transformation approaches" (2006)
   - Foster et al., "Combinators for bidirectional tree transformations" (2005)

2. **Triple Graph Grammars (TGG)**
   - Schürr, "Specification of graph translators with triple graph grammars" (1994)
   - Leblebici et al., "A comparison of incremental triple graph grammar tools" (2014)

3. **Truth Maintenance Systems (TMS)**
   - Doyle, "A truth maintenance system" (1979)
   - de Kleer, "An assumption-based TMS" (1986)

4. **Constraint Solving**
   - Nieuwenhuis et al., "Solving SAT and SAT Modulo Theories" (2006)

### 17.2 Related Practices

5. **Behavior-Driven Development (BDD)**
   - North, "Introducing BDD" (2006)
   - Cucumber/Gherkin documentation

6. **Test-Driven Development (TDD)**
   - Beck, "Test-Driven Development: By Example" (2002)

7. **Model-Driven Engineering (MDE)**
   - Brambilla et al., "Model-Driven Software Engineering in Practice" (2012)

### 17.3 Inspirations

- **SELA System**: Alignment-based development philosophy
- **GOSTC**: Annotation-driven documentation approach
- **Living Documentation**: Documentation that stays synchronized with code
- **Literate Programming**: Code and documentation as unified artifact

---

**Document Version**: 4.0.0
**Last Updated**: 2025-11-12
**Status**: Architecture Proposal
**Authors**: [To be filled]
**License**: [To be determined]

---

*"JIG: The alignment template for software development."*
*"Intent documented. Reality annotated. Alignment maintained."*
