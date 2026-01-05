---
title: "Intent Discovery Workflow"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1764019099
created_human: "2025-11-24 15:18 CST"
parent: "[[AG001_Alignment-Graph-Bricks]]"
children: []
---
# Intent Discovery Workflow

_Bootstrapping Outcomes and Specifications from Brick Analysis_

**Date:** 2025-11-24
**Status:** Methodology Definition
**Author:** Claude + Jim Meyer
**Prerequisite:** AG010_Brick-Discovery-Workflow.md (completed)

---

## Purpose

This document defines a repeatable workflow for **discovering Intent nodes (Outcomes and Specifications)** from existing Bricks when applying JIG to a codebase that doesn't yet have Intent documentation.

**Starting Point:** Completed Brick discovery (AG010), producing `bricks/*.brick.yaml` files.

**Goal:** Produce complete Intent nodes (O-*.md, S-*.md) with high confidence, using user input to resolve ambiguous cases.

---

## The Intent Discovery Problem

When applying JIG to an existing codebase:

1. **Code exists** - We can observe what was built
2. **Tests exist** - We can observe what is verified
3. **Intent is implicit** - We don't know *why* it was built this way

Some Intent can be inferred:
- Tests with clear names reveal specifications: `test_token_expires_after_24_hours` → S: "Tokens expire after 24 hours"
- Docstrings explain purpose: `"""Validates JWT tokens for multi-device auth"""` → O: "Multi-device authentication"
- Code structure implies constraints: Rate limiter class → S: "Rate limiting required"

Some Intent cannot be inferred:
- Business rationale: *Why* 24 hours? Why not 1 hour or 1 week?
- Priority and importance: Is this a core feature or nice-to-have?
- Future direction: Should this capability expand or stay limited?
- Edge cases: What should happen in error conditions?

This workflow separates **high-confidence inferences** from **questions requiring human input**.

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Code & Test Evidence Extraction                    │
│  Input: bricks/*.brick.yaml                                 │
│  Output: intent-discovery/01-evidence.yaml                  │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│  Step 2: Intent Inference (High Confidence)                 │
│  Input: 01-evidence.yaml                                    │
│  Output: intent-discovery/02-inferred-intent.yaml           │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│  Step 3: Gap Analysis & Question Generation                 │
│  Input: 02-inferred-intent.yaml, bricks/*.brick.yaml       │
│  Output: intent-discovery/03-questions.md                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ ← USER INPUT (answers questions in 03-questions.md)
                 │
┌────────────────▼────────────────────────────────────────────┐
│  Step 4: Answer Integration                                 │
│  Input: 02-inferred-intent.yaml, 03-questions.md (answered)│
│  Output: intent-discovery/04-complete-intent.yaml           │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│  Step 5: Intent Node Generation                             │
│  Input: 04-complete-intent.yaml                             │
│  Output: jig/outcomes/O-*.md, jig/specifications/S-*.md     │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│  Step 6: Brick Linkage & Validation                         │
│  Input: jig/outcomes/*, jig/specifications/*, bricks/*     │
│  Output: Updated bricks/*.brick.yaml, validation report     │
└─────────────────────────────────────────────────────────────┘
```

**Key Properties:**
- ✅ Each step produces a file artifact
- ✅ Context can be cleared between steps
- ✅ User input happens at a defined checkpoint (Step 3→4)
- ✅ Steps can be re-run with different parameters
- ✅ All decisions are traceable

---

## Directory Structure

```
project/
├── bricks/                          # From AG010 workflow
│   ├── foundation-utilities.brick.yaml
│   ├── graph-core.brick.yaml
│   └── ...
├── intent-discovery/                # Working artifacts
│   ├── 01-evidence.yaml
│   ├── 02-inferred-intent.yaml
│   ├── 03-questions.md              # ← User edits this
│   ├── 04-complete-intent.yaml
│   └── 05-generation-log.yaml
├── jig/                             # Final Intent nodes
│   ├── outcomes/
│   │   ├── O-AUTH-001.md
│   │   └── ...
│   ├── specifications/
│   │   ├── S-AUTH-001.md
│   │   └── ...
│   └── graph-index.yaml
└── analysis/                        # From AG010
    └── ...
```

---

## Step 1: Code & Test Evidence Extraction

### Objective
Extract observable evidence from code and tests that reveals implicit Intent.

### Tasks

1. **Extract from code**
   - Module and class docstrings
   - Function docstrings and signatures
   - Type annotations and contracts
   - Error messages and exception types
   - Configuration constants and defaults
   - Comments marked with TODO, FIXME, NOTE
   - Public API surface (what's exported)

2. **Extract from tests**
   - Test function names (often describe behavior)
   - Test docstrings
   - Assertion messages
   - Test fixtures (reveal expected states)
   - Parameterized test values (reveal edge cases)
   - Integration test scenarios

3. **Extract from Brick definitions**
   - Responsibility statements
   - Interface contracts
   - Dependency rationales
   - Health concerns

4. **Categorize evidence by type**
   - **Behavioral:** What the code does
   - **Constraint:** Limits and boundaries
   - **Rationale:** Why (if documented)
   - **Quality:** Non-functional requirements

### Output Artifact: `intent-discovery/01-evidence.yaml`

```yaml
metadata:
  source_artifacts:
    - "bricks/*.brick.yaml"
    - "src/**/*.py"
    - "tests/**/*.py"
  extraction_date: "2025-11-24T10:00:00Z"
  total_bricks_analyzed: 10

evidence_by_brick:
  "BRICK-GRAPH":
    brick_file: "bricks/graph-core.brick.yaml"

    code_evidence:
      docstrings:
        - location: "src/core/graph.py:1"
          type: "module"
          content: "Core graph data structures for the Alignment Graph."

        - location: "src/core/graph.py:45"
          type: "class"
          entity: "Graph"
          content: "Represents the full Alignment Graph with OSTC nodes and edges."

        - location: "src/core/graph.py:78"
          type: "method"
          entity: "Graph.load_from_dir"
          content: "Load graph from a directory of Intent files."
          signature: "load_from_dir(intent_dir: Path) -> Graph"

      type_annotations:
        - location: "src/core/graph.py:92"
          entity: "Graph.nodes"
          annotation: "dict[str, OSTCNode]"
          implies: "Nodes indexed by string ID"

      constants:
        - location: "src/core/graph.py:12"
          name: "MAX_GRAPH_DEPTH"
          value: 100
          implies: "Graph traversal has depth limit"

      error_types:
        - location: "src/core/graph.py:156"
          exception: "CircularDependencyError"
          message: "Circular dependency detected: {cycle}"
          implies: "Circular dependencies are invalid"

      comments:
        - location: "src/core/graph.py:203"
          type: "NOTE"
          content: "Performance degrades above 10k nodes"
          implies: "Scalability constraint"

    test_evidence:
      test_names:
        - location: "tests/unit/test_graph.py:45"
          name: "test_graph_loads_all_node_types"
          implies: "Graph must load O, S, T, C nodes"
          confidence: "high"

        - location: "tests/unit/test_graph.py:67"
          name: "test_graph_detects_circular_dependencies"
          implies: "Circular dependency detection required"
          confidence: "high"

        - location: "tests/unit/test_graph.py:89"
          name: "test_graph_query_finds_path"
          implies: "Path finding between nodes required"
          confidence: "high"

        - location: "tests/unit/test_graph.py:112"
          name: "test_graph_handles_empty_directory"
          implies: "Empty input is valid (returns empty graph)"
          confidence: "medium"

      test_docstrings:
        - location: "tests/unit/test_graph.py:67"
          content: "Verify that circular dependencies raise an error with the full cycle path."
          implies: "Error messages must include cycle details"
          confidence: "high"

      parameterized_tests:
        - location: "tests/unit/test_graph.py:134"
          name: "test_graph_query_performance"
          parameters: [100, 1000, 5000]
          implies: "Performance tested up to 5000 nodes"
          confidence: "medium"

      assertion_messages:
        - location: "tests/unit/test_graph.py:78"
          message: "Graph should contain exactly 4 nodes"
          implies: "Graph tracks node count"

    brick_evidence:
      responsibility: "Central domain model for graph data structures and operations."
      stability: "stable"
      concerns:
        - "Large Brick (892 LOC) - monitor for splitting"

    summary:
      total_evidence_items: 23
      high_confidence_items: 12
      medium_confidence_items: 8
      low_confidence_items: 3

  "BRICK-VALIDATOR":
    brick_file: "bricks/intent-validator.brick.yaml"

    code_evidence:
      docstrings:
        - location: "src/core/validator.py:1"
          type: "module"
          content: "Validates Intent graph structure and relationships."

        - location: "src/core/validator.py:34"
          type: "class"
          entity: "IntentValidator"
          content: "Validates OSTC nodes and their relationships."

      error_types:
        - location: "src/core/validator.py:89"
          exception: "OrphanedNodeError"
          message: "Node {id} has no connections"
          implies: "Orphaned nodes are invalid"

        - location: "src/core/validator.py:95"
          exception: "MissingReferenceError"
          message: "Node {id} references non-existent node {ref}"
          implies: "Dangling references are invalid"

    test_evidence:
      test_names:
        - location: "tests/unit/test_validator.py:23"
          name: "test_validates_node_id_format"
          implies: "Node IDs must follow specific format"
          confidence: "high"

        - location: "tests/unit/test_validator.py:45"
          name: "test_validates_required_fields"
          implies: "Nodes have required fields"
          confidence: "high"

        - location: "tests/unit/test_validator.py:67"
          name: "test_detects_orphaned_specifications"
          implies: "Specifications must link to Outcomes"
          confidence: "high"

        - location: "tests/unit/test_validator.py:89"
          name: "test_validates_subsystem_assignment"
          implies: "All nodes must have subsystem"
          confidence: "medium"

    summary:
      total_evidence_items: 18
      high_confidence_items: 10
      medium_confidence_items: 5
      low_confidence_items: 3

  # ... more bricks ...

evidence_summary:
  total_evidence_items: 156
  by_confidence:
    high: 78
    medium: 52
    low: 26
  by_type:
    behavioral: 89
    constraint: 34
    rationale: 12
    quality: 21
```

### Success Criteria
- [ ] All Bricks have evidence extracted
- [ ] Code docstrings captured
- [ ] Test names and docstrings captured
- [ ] Evidence categorized by confidence
- [ ] Summary statistics computed

---

## Step 2: Intent Inference (High Confidence)

### Objective
Generate draft Intent nodes from high-confidence evidence.

### Inference Rules

**Rule 1: Test Name → Specification**
```
test_X_does_Y → S: "X does Y"
Confidence: HIGH if test passes, MEDIUM if test exists but status unknown
```

**Rule 2: Exception Type → Specification (Constraint)**
```
XError("message") → S: "X is invalid" or "X must not occur"
Confidence: HIGH (code explicitly rejects this condition)
```

**Rule 3: Constant with Limit → Specification (Constraint)**
```
MAX_X = N → S: "X must not exceed N"
Confidence: MEDIUM (may be implementation detail, not requirement)
```

**Rule 4: Class Docstring → Outcome (if describes value)**
```
"""Enables users to X""" → O: "Users can X"
Confidence: MEDIUM (docstrings may be outdated)
```

**Rule 5: Integration Test → Outcome (if describes scenario)**
```
test_user_can_authenticate_and_access_dashboard → O: "Users authenticate and access dashboard"
Confidence: HIGH (integration tests often map to user stories)
```

**Rule 6: Public API Method → Specification (Capability)**
```
def do_something(x: T) -> R → S: "System can do something with T, returning R"
Confidence: LOW (method existence doesn't imply it's a requirement)
```

### Tasks

1. **Apply inference rules to evidence**
   - Match evidence patterns to rules
   - Generate draft Intent statements
   - Assign confidence levels

2. **Cluster related inferences**
   - Group specifications that serve same outcome
   - Identify outcome candidates from spec clusters
   - Link inferred specs to inferred outcomes

3. **Assign tentative IDs**
   - Use Brick name as prefix: `O-{BRICK}-001`
   - Sequential numbering within Brick

4. **Flag low-confidence items for questions**
   - Mark items needing human validation
   - Note what additional info would raise confidence

### Output Artifact: `intent-discovery/02-inferred-intent.yaml`

```yaml
metadata:
  source_artifact: "intent-discovery/01-evidence.yaml"
  inference_date: "2025-11-24T10:30:00Z"
  inference_rules_version: "1.0"

inferred_outcomes:
  - id: "O-GRAPH-001"
    brick: "BRICK-GRAPH"
    title: "Graph represents system alignment"
    description: |
      The Alignment Graph provides a unified view of Intent, Implementation,
      and Verification as a queryable structure.
    confidence: "high"
    evidence:
      - source: "brick_responsibility"
        content: "Central domain model for graph data structures and operations."
      - source: "docstring:src/core/graph.py:1"
        content: "Core graph data structures for the Alignment Graph."
    inferred_by_rule: "Rule 4: Class Docstring → Outcome"
    needs_validation:
      - "Is this the primary purpose or just implementation detail?"
      - "Should we distinguish 'alignment' from general 'graph'?"

  - id: "O-GRAPH-002"
    brick: "BRICK-GRAPH"
    title: "Graph enables dependency tracking"
    description: |
      Users can query the graph to find dependencies and dependents
      of any node, enabling impact analysis.
    confidence: "high"
    evidence:
      - source: "test:tests/unit/test_graph.py:89"
        content: "test_graph_query_finds_path"
      - source: "method:src/core/graph.py:get_dependencies"
        content: "Get all nodes this node depends on"
    inferred_by_rule: "Rule 5: Integration Test → Outcome"
    needs_validation: []

  - id: "O-VALIDATOR-001"
    brick: "BRICK-VALIDATOR"
    title: "Graph integrity is enforced"
    description: |
      The system validates that the Intent graph is structurally correct,
      with no orphans, dangling references, or invalid relationships.
    confidence: "high"
    evidence:
      - source: "exception:OrphanedNodeError"
        content: "Node {id} has no connections"
      - source: "exception:MissingReferenceError"
        content: "Node {id} references non-existent node {ref}"
      - source: "test:test_detects_orphaned_specifications"
        content: "Specifications must link to Outcomes"
    inferred_by_rule: "Rule 2: Exception Type → Specification"
    needs_validation:
      - "What level of validation is required? Strict or permissive?"

inferred_specifications:
  - id: "S-GRAPH-001"
    brick: "BRICK-GRAPH"
    title: "Graph loads all OSTC node types"
    description: "Graph.load_from_dir() must load Outcome, Specification, Test, and Code nodes."
    confidence: "high"
    implements_outcomes: ["O-GRAPH-001"]
    evidence:
      - source: "test:tests/unit/test_graph.py:45"
        content: "test_graph_loads_all_node_types"
    inferred_by_rule: "Rule 1: Test Name → Specification"
    needs_validation: []

  - id: "S-GRAPH-002"
    brick: "BRICK-GRAPH"
    title: "Circular dependencies are detected and rejected"
    description: "Graph must detect circular dependencies and raise CircularDependencyError with cycle path."
    confidence: "high"
    implements_outcomes: ["O-VALIDATOR-001"]
    evidence:
      - source: "test:tests/unit/test_graph.py:67"
        content: "test_graph_detects_circular_dependencies"
      - source: "exception:CircularDependencyError"
        content: "Circular dependency detected: {cycle}"
      - source: "test_docstring"
        content: "Error messages must include cycle details"
    inferred_by_rule: "Rule 1 + Rule 2"
    needs_validation: []

  - id: "S-GRAPH-003"
    brick: "BRICK-GRAPH"
    title: "Graph supports path queries"
    description: "Graph must support finding paths between any two nodes."
    confidence: "high"
    implements_outcomes: ["O-GRAPH-002"]
    evidence:
      - source: "test:tests/unit/test_graph.py:89"
        content: "test_graph_query_finds_path"
    inferred_by_rule: "Rule 1: Test Name → Specification"
    needs_validation: []

  - id: "S-GRAPH-004"
    brick: "BRICK-GRAPH"
    title: "Graph depth limited to 100 levels"
    description: "Graph traversal operations are limited to 100 levels of depth."
    confidence: "medium"
    implements_outcomes: ["O-GRAPH-002"]
    evidence:
      - source: "constant:MAX_GRAPH_DEPTH"
        content: "MAX_GRAPH_DEPTH = 100"
    inferred_by_rule: "Rule 3: Constant with Limit → Specification"
    needs_validation:
      - "Is 100 a requirement or arbitrary implementation choice?"
      - "What should happen when limit is exceeded?"

  - id: "S-GRAPH-005"
    brick: "BRICK-GRAPH"
    title: "Graph handles empty directories gracefully"
    description: "Loading from empty directory returns empty graph (not error)."
    confidence: "medium"
    implements_outcomes: ["O-GRAPH-001"]
    evidence:
      - source: "test:tests/unit/test_graph.py:112"
        content: "test_graph_handles_empty_directory"
    inferred_by_rule: "Rule 1: Test Name → Specification"
    needs_validation:
      - "Is empty graph valid, or should it warn/error?"

  - id: "S-VALIDATOR-001"
    brick: "BRICK-VALIDATOR"
    title: "Node IDs must follow format convention"
    description: "All node IDs must match the pattern {TYPE}-{SUBSYSTEM}-{NUMBER}."
    confidence: "high"
    implements_outcomes: ["O-VALIDATOR-001"]
    evidence:
      - source: "test:tests/unit/test_validator.py:23"
        content: "test_validates_node_id_format"
    inferred_by_rule: "Rule 1: Test Name → Specification"
    needs_validation:
      - "What is the exact format? Need to inspect test for regex."

  - id: "S-VALIDATOR-002"
    brick: "BRICK-VALIDATOR"
    title: "Specifications must link to Outcomes"
    description: "Every Specification node must reference at least one Outcome."
    confidence: "high"
    implements_outcomes: ["O-VALIDATOR-001"]
    evidence:
      - source: "test:tests/unit/test_validator.py:67"
        content: "test_detects_orphaned_specifications"
    inferred_by_rule: "Rule 1: Test Name → Specification"
    needs_validation: []

  - id: "S-VALIDATOR-003"
    brick: "BRICK-VALIDATOR"
    title: "All nodes must have subsystem assignment"
    description: "Every node must be assigned to exactly one subsystem."
    confidence: "medium"
    implements_outcomes: ["O-VALIDATOR-001"]
    evidence:
      - source: "test:tests/unit/test_validator.py:89"
        content: "test_validates_subsystem_assignment"
    inferred_by_rule: "Rule 1: Test Name → Specification"
    needs_validation:
      - "Is subsystem required, or can nodes be 'unassigned'?"
      - "Can a node belong to multiple subsystems?"

  # ... more specifications ...

gaps_identified:
  missing_outcomes:
    - brick: "BRICK-UTILS"
      observation: "No clear business outcome for utility functions"
      possible_outcome: "System has reliable file I/O operations"
      confidence: "low"
      question_needed: true

    - brick: "BRICK-CONFIG"
      observation: "Configuration loading exists but no stated purpose"
      possible_outcome: "System behavior is configurable"
      confidence: "medium"
      question_needed: true

  missing_specifications:
    - brick: "BRICK-GRAPH"
      gap: "Performance requirements unclear"
      evidence: "Comment mentions '10k nodes' but no test"
      question_needed: true

    - brick: "BRICK-VALIDATOR"
      gap: "Error recovery behavior undefined"
      evidence: "Exceptions thrown but recovery not specified"
      question_needed: true

inference_summary:
  total_outcomes: 8
  total_specifications: 24
  by_confidence:
    high: 18
    medium: 10
    low: 4
  items_needing_validation: 12
  gaps_requiring_questions: 6
```

### Success Criteria
- [ ] All high-confidence evidence produces draft Intent
- [ ] Outcomes and Specifications are linked
- [ ] Confidence levels assigned
- [ ] Gaps and uncertainties documented
- [ ] Items needing questions flagged

---

## Step 3: Gap Analysis & Question Generation

### Objective
Generate a structured Questions document for user input on uncertain Intent.

### Question Categories

1. **Validation Questions** - Confirm inferred Intent is correct
2. **Clarification Questions** - Resolve ambiguity in evidence
3. **Gap Questions** - Fill in missing Intent
4. **Priority Questions** - Understand relative importance
5. **Scope Questions** - Define boundaries

### Question Format

Each question includes:
- Context (what we observed)
- The question itself
- Why we're asking
- Default assumption (if user doesn't answer)
- Answer space

### Output Artifact: `intent-discovery/03-questions.md`

```markdown
# Intent Discovery Questions

**Project:** [Project Name]
**Generated:** 2025-11-24
**Status:** AWAITING USER INPUT

---

## Instructions

This document contains questions about Intent that could not be confidently
inferred from code and tests. Please answer each question to help complete
the Intent documentation.

**How to answer:**
1. Read the context and question
2. Write your answer in the `### Your Answer` section
3. If you don't know, leave the default assumption
4. Add any additional context in `### Notes`

**When complete:** Save this file and re-run Step 4 of the workflow.

---

## Section 1: Outcome Validation

These questions confirm whether inferred Outcomes are correct.

---

### Q1: Graph Purpose Confirmation

**Brick:** BRICK-GRAPH

**What we observed:**
- Module docstring: "Core graph data structures for the Alignment Graph"
- Class docstring: "Represents the full Alignment Graph with OSTC nodes and edges"
- Tests verify loading, querying, and traversal

**Inferred Outcome:**
> O-GRAPH-001: "Graph represents system alignment"
> The Alignment Graph provides a unified view of Intent, Implementation,
> and Verification as a queryable structure.

**Question:**
Is this the correct framing of the Graph's purpose? Should we emphasize
different aspects (e.g., "enables impact analysis" vs "maintains alignment")?

**Default assumption:** The inferred outcome is correct.

### Your Answer

[Write your answer here]

### Notes

[Any additional context]

---

### Q2: Validation Strictness

**Brick:** BRICK-VALIDATOR

**What we observed:**
- Validator throws errors for orphaned nodes, missing references
- Tests check for specific error conditions
- No "warning" mode observed in code

**Inferred Outcome:**
> O-VALIDATOR-001: "Graph integrity is enforced"
> The system validates that the Intent graph is structurally correct,
> with no orphans, dangling references, or invalid relationships.

**Question:**
Should validation be strict (errors stop processing) or permissive
(warnings allow continuation)? The code appears strict, but is that
intentional?

**Options:**
- [ ] Strict: Invalid graphs should fail validation
- [ ] Permissive: Warnings for issues, but allow continuation
- [ ] Configurable: User chooses strictness level
- [ ] Other: [explain]

**Default assumption:** Strict validation is intentional.

### Your Answer

[Select an option or write your answer]

### Notes

[Any additional context]

---

## Section 2: Specification Clarification

These questions clarify ambiguous specifications.

---

### Q3: Graph Depth Limit

**Brick:** BRICK-GRAPH

**What we observed:**
- Constant: `MAX_GRAPH_DEPTH = 100`
- No test explicitly validates this limit
- Comment: "Performance degrades above 10k nodes"

**Inferred Specification:**
> S-GRAPH-004: "Graph depth limited to 100 levels"
> Graph traversal operations are limited to 100 levels of depth.

**Questions:**
1. Is the 100-level limit a hard requirement, or an arbitrary choice?
2. What should happen when the limit is exceeded?
   - Raise error?
   - Return partial result?
   - Warn and continue?
3. Is this related to the "10k nodes" performance concern?

**Default assumption:** 100 is arbitrary; can be changed. Exceeding raises error.

### Your Answer

[Write your answers to each question]

### Notes

[Any additional context]

---

### Q4: Node ID Format

**Brick:** BRICK-VALIDATOR

**What we observed:**
- Test: `test_validates_node_id_format`
- Test checks format but regex not visible in evidence

**Inferred Specification:**
> S-VALIDATOR-001: "Node IDs must follow format convention"
> All node IDs must match the pattern {TYPE}-{SUBSYSTEM}-{NUMBER}.

**Question:**
What is the exact node ID format? Please provide:
1. The regex pattern (if known)
2. Examples of valid IDs
3. Examples of invalid IDs

**Default assumption:** Pattern is `{TYPE}-{SUBSYSTEM}-{NUMBER}` where TYPE is O/S/T/C.

### Your Answer

[Write the format specification]

### Notes

[Any additional context]

---

### Q5: Empty Graph Behavior

**Brick:** BRICK-GRAPH

**What we observed:**
- Test: `test_graph_handles_empty_directory`
- Implies empty input returns empty graph (not error)

**Inferred Specification:**
> S-GRAPH-005: "Graph handles empty directories gracefully"
> Loading from empty directory returns empty graph (not error).

**Question:**
Is an empty graph a valid state? Should the system:
- Accept empty graphs silently
- Warn that graph is empty
- Require at least one node

**Default assumption:** Empty graphs are valid, no warning needed.

### Your Answer

[Select or explain]

### Notes

[Any additional context]

---

## Section 3: Gap Filling

These questions address missing Intent that couldn't be inferred.

---

### Q6: Utility Functions Purpose

**Brick:** BRICK-UTILS

**What we observed:**
- File I/O functions: read_file, write_file, ensure_dir
- YAML utilities: load_yaml, dump_yaml
- No clear business outcome stated

**Gap:**
No Outcome exists for BRICK-UTILS. It's a foundation layer, but why does
it exist? What value does it provide?

**Possible Outcomes:**
- "System has reliable file I/O operations"
- "File operations are abstracted for testability"
- "YAML is the standard data format"

**Question:**
What is the business/technical value that BRICK-UTILS provides? Or should
foundation utilities not have explicit Outcomes (implicit requirement)?

**Default assumption:** Foundation utilities don't need explicit Outcomes.

### Your Answer

[Write your answer]

### Notes

[Any additional context]

---

### Q7: Configuration Purpose

**Brick:** BRICK-CONFIG

**What we observed:**
- Configuration loading from TOML files
- Default values defined in code
- No explicit outcome for configurability

**Question:**
What aspects of the system should be configurable? Examples:
- Performance tuning parameters
- Validation strictness
- Output formats
- External service connections

**Default assumption:** Configuration exists but scope is implementation detail.

### Your Answer

[List what should be configurable and why]

### Notes

[Any additional context]

---

### Q8: Performance Requirements

**Brick:** BRICK-GRAPH

**What we observed:**
- Comment: "Performance degrades above 10k nodes"
- Parameterized test with [100, 1000, 5000] nodes
- No explicit performance specification

**Gap:**
Performance requirements are not documented. What are the targets?

**Questions:**
1. What is the expected maximum graph size? (nodes, edges)
2. What are acceptable response times for common operations?
   - Load graph: _____ ms
   - Query single node: _____ ms
   - Find path: _____ ms
3. Are there memory constraints?

**Default assumption:** Performance is best-effort, no hard requirements.

### Your Answer

[Provide performance requirements]

### Notes

[Any additional context]

---

## Section 4: Priority Questions

These questions help understand relative importance.

---

### Q9: Critical vs Nice-to-Have

**Question:**
Of the Bricks analyzed, which represent **critical** functionality
(system doesn't work without them) vs **nice-to-have** (useful but
optional)?

**Bricks to classify:**
- [ ] BRICK-GRAPH: ☐ Critical  ☐ Nice-to-have
- [ ] BRICK-VALIDATOR: ☐ Critical  ☐ Nice-to-have
- [ ] BRICK-PARSER: ☐ Critical  ☐ Nice-to-have
- [ ] BRICK-INDEX: ☐ Critical  ☐ Nice-to-have
- [ ] BRICK-SCANNER: ☐ Critical  ☐ Nice-to-have
- [ ] BRICK-CLI: ☐ Critical  ☐ Nice-to-have
- [ ] BRICK-DECOMPOSE: ☐ Critical  ☐ Nice-to-have

**Default assumption:** All Bricks are equally important.

### Your Answer

[Check boxes or explain priority]

### Notes

[Any additional context]

---

### Q10: Future Direction

**Question:**
Are there capabilities that should be:
1. **Expanded** in future versions?
2. **Deprecated** or removed?
3. **Added** (not currently present)?

This helps prioritize which Intent to document thoroughly.

**Default assumption:** Current capabilities are stable.

### Your Answer

[Describe future direction]

### Notes

[Any additional context]

---

## Section 5: Scope Questions

These questions define boundaries.

---

### Q11: Error Handling Philosophy

**What we observed:**
- Various exception types defined
- Tests check that errors are raised
- No error recovery or retry logic observed

**Question:**
What is the error handling philosophy?
- Fail fast: Any error stops processing
- Graceful degradation: Continue with partial results
- Retry logic: Transient errors are retried
- User choice: Configurable behavior

**Default assumption:** Fail fast for structural errors.

### Your Answer

[Describe error handling philosophy]

### Notes

[Any additional context]

---

### Q12: Integration Boundaries

**Question:**
What external systems does this integrate with?
- File system (already observed)
- Git (if any)
- External APIs (if any)
- Databases (if any)
- Other tools (if any)

For each integration, what are the assumptions/requirements?

**Default assumption:** File system only, no external integrations.

### Your Answer

[List integrations and requirements]

### Notes

[Any additional context]

---

## Completion Checklist

Before saving this file, please confirm:

- [ ] All questions in Section 1 (Validation) answered
- [ ] All questions in Section 2 (Clarification) answered
- [ ] All questions in Section 3 (Gap Filling) answered
- [ ] At least reviewed Section 4 (Priority) - answers optional
- [ ] At least reviewed Section 5 (Scope) - answers optional

**Save this file and run Step 4 to continue.**

---

**Generated by:** Intent Discovery Workflow Step 3
**Questions derived from:** intent-discovery/02-inferred-intent.yaml
```

### Success Criteria
- [ ] All gaps from Step 2 have questions
- [ ] All low/medium confidence items have validation questions
- [ ] Questions are clear and actionable
- [ ] Default assumptions provided
- [ ] User can answer without additional context

---

## Step 4: Answer Integration

### Objective
Integrate user answers into complete Intent definitions.

### Input
- `intent-discovery/02-inferred-intent.yaml` (draft Intent)
- `intent-discovery/03-questions.md` (with user answers)

### Tasks

1. **Parse user answers**
   - Extract answers from markdown
   - Handle missing answers (use defaults)
   - Validate answer format

2. **Update Intent definitions**
   - Incorporate answers into descriptions
   - Adjust confidence based on validation
   - Resolve ambiguities

3. **Create new Intent from gap answers**
   - Generate Outcomes from Q6, Q7
   - Generate Specifications from Q3-Q5, Q8

4. **Apply priority information**
   - Tag critical vs nice-to-have
   - Note future direction

5. **Final consistency check**
   - All Specs link to Outcomes
   - No orphaned Intent
   - IDs are unique

### Output Artifact: `intent-discovery/04-complete-intent.yaml`

```yaml
metadata:
  source_artifacts:
    - "intent-discovery/02-inferred-intent.yaml"
    - "intent-discovery/03-questions.md"
  integration_date: "2025-11-24T14:00:00Z"
  user_answers_provided: 10
  user_answers_missing: 2

outcomes:
  - id: "O-GRAPH-001"
    brick: "BRICK-GRAPH"
    title: "Graph represents system alignment"
    description: |
      The Alignment Graph provides a unified view of Intent, Implementation,
      and Verification as a queryable structure. It is the central domain
      model for understanding system architecture and detecting drift.
    status: "validated"
    confidence: "high"
    priority: "critical"
    evidence:
      - "brick_responsibility"
      - "module_docstring"
      - "user_validation:Q1"
    user_input:
      question: "Q1"
      answer: "Confirmed. Emphasis should be on 'detecting drift' aspect."
      applied: true

  - id: "O-GRAPH-002"
    brick: "BRICK-GRAPH"
    title: "Graph enables impact analysis"
    description: |
      Users can query the graph to understand dependencies, find paths
      between nodes, and assess the impact of proposed changes.
    status: "validated"
    confidence: "high"
    priority: "critical"
    evidence:
      - "test:test_graph_query_finds_path"
      - "method:get_dependencies"

  - id: "O-VALIDATOR-001"
    brick: "BRICK-VALIDATOR"
    title: "Graph integrity is strictly enforced"
    description: |
      The system validates that the Intent graph is structurally correct.
      Validation is strict: invalid graphs fail with clear error messages.
      This prevents silent corruption and ensures reliable analysis.
    status: "validated"
    confidence: "high"
    priority: "critical"
    user_input:
      question: "Q2"
      answer: "Strict validation is intentional and required."
      applied: true

  - id: "O-CONFIG-001"
    brick: "BRICK-CONFIG"
    title: "System behavior is configurable"
    description: |
      Key operational parameters can be configured via TOML files,
      allowing customization without code changes. Configurable aspects
      include validation strictness and performance tuning.
    status: "created_from_user_input"
    confidence: "high"
    priority: "nice-to-have"
    user_input:
      question: "Q7"
      answer: "Validation strictness and performance tuning should be configurable."
      applied: true

specifications:
  - id: "S-GRAPH-001"
    brick: "BRICK-GRAPH"
    title: "Graph loads all OSTC node types"
    description: |
      Graph.load_from_dir() must load all four node types:
      Outcome (O), Specification (S), Test (T), and Code (C).
    implements: ["O-GRAPH-001"]
    verified_by: []  # To be filled by test mapping
    status: "validated"
    confidence: "high"

  - id: "S-GRAPH-002"
    brick: "BRICK-GRAPH"
    title: "Circular dependencies are detected and rejected"
    description: |
      Graph must detect circular dependencies during loading or validation.
      When detected, raise CircularDependencyError with the full cycle path
      in the error message.
    implements: ["O-VALIDATOR-001"]
    verified_by: []
    status: "validated"
    confidence: "high"

  - id: "S-GRAPH-003"
    brick: "BRICK-GRAPH"
    title: "Graph supports path queries"
    description: |
      Graph must support finding the shortest path between any two nodes.
      If no path exists, return None (not error).
    implements: ["O-GRAPH-002"]
    verified_by: []
    status: "validated"
    confidence: "high"

  - id: "S-GRAPH-004"
    brick: "BRICK-GRAPH"
    title: "Graph traversal depth is configurable with 100-level default"
    description: |
      Graph traversal operations have a configurable depth limit.
      Default is 100 levels. Exceeding the limit raises DepthLimitError.
      This prevents runaway traversals in large or cyclic-ish graphs.
    implements: ["O-GRAPH-002", "O-CONFIG-001"]
    verified_by: []
    status: "updated_from_user_input"
    confidence: "high"
    user_input:
      question: "Q3"
      answer: |
        100 is a reasonable default but should be configurable.
        Exceeding should raise error, not silently truncate.
      applied: true

  - id: "S-GRAPH-005"
    brick: "BRICK-GRAPH"
    title: "Empty directories produce empty graphs"
    description: |
      Loading from an empty directory returns an empty Graph object.
      This is valid state (not an error). No warning is emitted.
    implements: ["O-GRAPH-001"]
    verified_by: []
    status: "validated"
    confidence: "high"
    user_input:
      question: "Q5"
      answer: "Empty graphs are valid. No warning needed."
      applied: true

  - id: "S-GRAPH-006"
    brick: "BRICK-GRAPH"
    title: "Graph operations complete within performance targets"
    description: |
      Performance requirements:
      - Maximum supported graph size: 10,000 nodes
      - Load graph: < 2 seconds
      - Query single node: < 10 ms
      - Find path: < 100 ms
    implements: ["O-GRAPH-001"]
    verified_by: []
    status: "created_from_user_input"
    confidence: "high"
    priority: "nice-to-have"
    user_input:
      question: "Q8"
      answer: |
        Max 10k nodes. Load < 2s. Query < 10ms. Path < 100ms.
      applied: true

  - id: "S-VALIDATOR-001"
    brick: "BRICK-VALIDATOR"
    title: "Node IDs follow {TYPE}-{SUBSYSTEM}-{NNN} format"
    description: |
      All node IDs must match the pattern: {TYPE}-{SUBSYSTEM}-{NUMBER}
      - TYPE: O, S, T, or C
      - SUBSYSTEM: uppercase alphanumeric, 2-10 chars
      - NUMBER: 3-digit zero-padded number (001-999)

      Examples:
      - Valid: O-GRAPH-001, S-AUTH-042, T-UTILS-001
      - Invalid: graph-001, O-graph-001, O-G-1
    implements: ["O-VALIDATOR-001"]
    verified_by: []
    status: "updated_from_user_input"
    confidence: "high"
    user_input:
      question: "Q4"
      answer: |
        Pattern: {TYPE}-{SUBSYSTEM}-{NUMBER}
        TYPE: O/S/T/C
        SUBSYSTEM: 2-10 uppercase alphanumeric
        NUMBER: 3 digits zero-padded
      applied: true

  - id: "S-VALIDATOR-002"
    brick: "BRICK-VALIDATOR"
    title: "Specifications must reference at least one Outcome"
    description: |
      Every Specification node must include at least one reference to
      an Outcome node via the 'implements' field. Orphaned Specifications
      are validation errors.
    implements: ["O-VALIDATOR-001"]
    verified_by: []
    status: "validated"
    confidence: "high"

  # ... more specifications ...

unmapped_intent:
  # Intent that doesn't map to a Brick (cross-cutting)
  - id: "O-SYSTEM-001"
    title: "System fails fast on errors"
    description: |
      The system follows a fail-fast philosophy. Structural errors
      stop processing immediately with clear error messages.
      No silent failures or partial results on error.
    status: "created_from_user_input"
    user_input:
      question: "Q11"
      answer: "Fail fast for structural errors."

future_direction:
  expand:
    - "Performance optimization for larger graphs"
    - "Visualization capabilities"
  deprecate: []
  add:
    - "Real-time drift detection"
    - "Git integration for history"
  source: "Q10"

integration_notes:
  - "All critical Bricks have Outcomes"
  - "BRICK-UTILS remains without explicit Outcome (foundation layer)"
  - "Performance specs added based on user input"
  - "Node ID format now fully specified"
```

### Success Criteria
- [ ] All user answers parsed and integrated
- [ ] Default assumptions applied where answers missing
- [ ] New Intent created from gap-filling answers
- [ ] All Intent has confidence level
- [ ] Priority information captured
- [ ] Consistency verified

---

## Step 5: Intent Node Generation

### Objective
Generate final Intent files in JIG format.

### Tasks

1. **Create Outcome files**
   - Generate `jig/outcomes/O-*.md` for each Outcome
   - Use JIG v6.1 format (YAML frontmatter + Markdown body)
   - Include source traceability

2. **Create Specification files**
   - Generate `jig/specifications/S-*.md` for each Specification
   - Link to Outcomes via `implements` field
   - Include source evidence

3. **Update graph-index.yaml**
   - Add all new nodes to index
   - Create edges for relationships
   - Update subsystem mappings

4. **Generate creation log**
   - Track what was created
   - Note sources and confidence

### Output Artifacts

**jig/outcomes/O-GRAPH-001.md:**
```yaml
---
id: O-GRAPH-001
type: outcome
title: "Graph represents system alignment"
subsystem: graph
created: 2025-11-24
source_discovery: intent-discovery/04-complete-intent.yaml
confidence: high
priority: critical
---

# Outcome: Graph represents system alignment

The Alignment Graph provides a unified view of Intent, Implementation,
and Verification as a queryable structure. It is the central domain
model for understanding system architecture and detecting drift.

## Value

Enables:
- Understanding what was intended vs. what was built
- Tracking verification coverage
- Detecting architectural drift over time
- Impact analysis for proposed changes

## Acceptance Criteria

- Graph loads all four OSTC node types
- Graph supports dependency and path queries
- Graph detects structural issues (cycles, orphans)

## Related

- specs: S-GRAPH-001, S-GRAPH-002, S-GRAPH-003, S-GRAPH-004, S-GRAPH-005
- brick: BRICK-GRAPH

## Discovery Source

Inferred from:
- Module docstring: "Core graph data structures for the Alignment Graph"
- Brick responsibility: "Central domain model for graph data structures"
- User validation: Q1 response confirmed framing
```

**jig/specifications/S-GRAPH-002.md:**
```yaml
---
id: S-GRAPH-002
type: specification
title: "Circular dependencies are detected and rejected"
subsystem: graph
created: 2025-11-24
source_discovery: intent-discovery/04-complete-intent.yaml
confidence: high
---

# Specification: Circular dependencies are detected and rejected

Graph must detect circular dependencies during loading or validation.
When detected, raise CircularDependencyError with the full cycle path
in the error message.

## Rationale

Circular dependencies indicate structural problems in the Intent graph.
Failing fast with clear error messages helps identify the issue quickly.

## Verification

- Test: test_graph_detects_circular_dependencies
- Error includes full cycle path

## Related

- implements: O-VALIDATOR-001
- tested_by: T-GRAPH-002 (to be mapped)
- brick: BRICK-GRAPH

## Discovery Source

Inferred from:
- Test name: test_graph_detects_circular_dependencies
- Exception type: CircularDependencyError
- Test docstring: "Error messages must include cycle details"
```

**intent-discovery/05-generation-log.yaml:**
```yaml
metadata:
  source_artifact: "intent-discovery/04-complete-intent.yaml"
  generation_date: "2025-11-24T15:00:00Z"

generated_files:
  outcomes:
    - file: "jig/outcomes/O-GRAPH-001.md"
      id: "O-GRAPH-001"
      title: "Graph represents system alignment"

    - file: "jig/outcomes/O-GRAPH-002.md"
      id: "O-GRAPH-002"
      title: "Graph enables impact analysis"

    - file: "jig/outcomes/O-VALIDATOR-001.md"
      id: "O-VALIDATOR-001"
      title: "Graph integrity is strictly enforced"

    - file: "jig/outcomes/O-CONFIG-001.md"
      id: "O-CONFIG-001"
      title: "System behavior is configurable"

  specifications:
    - file: "jig/specifications/S-GRAPH-001.md"
      id: "S-GRAPH-001"
      title: "Graph loads all OSTC node types"

    # ... all specifications ...

  updated:
    - file: "jig/graph-index.yaml"
      changes: "Added 4 Outcomes, 12 Specifications"

summary:
  outcomes_created: 4
  specifications_created: 12
  total_nodes: 16

  by_confidence:
    high: 14
    medium: 2
    low: 0

  by_source:
    inferred_and_validated: 10
    created_from_user_input: 4
    inferred_default_used: 2
```

### Success Criteria
- [ ] All Intent nodes have files created
- [ ] Files follow JIG v6.1 format
- [ ] Source traceability included
- [ ] Graph index updated
- [ ] Generation log complete

---

## Step 6: Brick Linkage & Validation

### Objective
Update Brick files with Intent mappings and validate consistency.

### Tasks

1. **Update Brick files**
   - Add `intent_mapping.outcomes` list
   - Add `intent_mapping.specifications` list
   - Update any notes

2. **Validate linkage**
   - Every Brick has at least one Outcome (except foundation)
   - Every Specification links to an Outcome
   - All referenced IDs exist

3. **Run JIG validation**
   - Check graph consistency
   - Verify no orphaned nodes
   - Confirm relationships valid

4. **Generate validation report**
   - Coverage statistics
   - Any remaining gaps
   - Recommendations

### Output: Updated Brick Files and Validation Report

**Updated bricks/graph-core.brick.yaml (partial):**
```yaml
# ... existing content ...

intent_mapping:
  outcomes:
    - id: "O-GRAPH-001"
      title: "Graph represents system alignment"
      status: "active"

    - id: "O-GRAPH-002"
      title: "Graph enables impact analysis"
      status: "active"

  specifications:
    - id: "S-GRAPH-001"
      title: "Graph loads all OSTC node types"
      status: "active"

    - id: "S-GRAPH-002"
      title: "Circular dependencies are detected and rejected"
      status: "active"

    - id: "S-GRAPH-003"
      title: "Graph supports path queries"
      status: "active"

    - id: "S-GRAPH-004"
      title: "Graph traversal depth is configurable"
      status: "active"

    - id: "S-GRAPH-005"
      title: "Empty directories produce empty graphs"
      status: "active"

    - id: "S-GRAPH-006"
      title: "Graph operations complete within performance targets"
      status: "active"

  coverage:
    outcomes: 2
    specifications: 6

  notes: |
    Intent discovered via AG012 workflow on 2025-11-24.
    All specifications inferred from code/tests and validated by user.
```

**intent-discovery/06-validation-report.yaml:**
```yaml
metadata:
  validation_date: "2025-11-24T16:00:00Z"
  workflow_version: "AG012 v1.0"

validation_results:
  status: "PASSED"

  checks:
    - check: "All Outcomes exist"
      status: "pass"
      count: 4

    - check: "All Specifications exist"
      status: "pass"
      count: 12

    - check: "All Specs link to Outcomes"
      status: "pass"
      orphaned: 0

    - check: "All Bricks have Intent (except foundation)"
      status: "pass"
      bricks_with_intent: 8
      foundation_bricks: 2

    - check: "No dangling references"
      status: "pass"

    - check: "ID format valid"
      status: "pass"

coverage_summary:
  by_brick:
    "BRICK-GRAPH":
      outcomes: 2
      specifications: 6
      coverage: "complete"

    "BRICK-VALIDATOR":
      outcomes: 1
      specifications: 3
      coverage: "complete"

    "BRICK-CONFIG":
      outcomes: 1
      specifications: 2
      coverage: "complete"

    "BRICK-UTILS":
      outcomes: 0
      specifications: 0
      coverage: "none (foundation layer - acceptable)"

    # ... other bricks ...

  overall:
    total_outcomes: 4
    total_specifications: 12
    bricks_with_full_coverage: 8
    bricks_partial_coverage: 0
    bricks_no_coverage: 2  # Foundation layer

remaining_gaps:
  - brick: "BRICK-UTILS"
    gap: "No Intent nodes"
    acceptable: true
    reason: "Foundation layer - implicit requirements"

  - brick: "BRICK-INDEX"
    gap: "Specifications exist but no Outcome"
    acceptable: false
    recommendation: "Create O-INDEX-001 for index purpose"

recommendations:
  - priority: "medium"
    action: "Create O-INDEX-001 for BRICK-INDEX"
    rationale: "Index builder needs explicit business outcome"

  - priority: "low"
    action: "Add more Specifications to BRICK-CLI"
    rationale: "CLI has Outcomes but few Specifications"

next_steps:
  - "Run `jig validate` to verify graph consistency"
  - "Address medium-priority recommendations"
  - "Map Tests to Specifications (T nodes)"
  - "Map Code to Specifications (C nodes via @jig annotations)"
```

### Success Criteria
- [ ] All Brick files updated with Intent mappings
- [ ] Validation passes
- [ ] Coverage statistics calculated
- [ ] Remaining gaps documented
- [ ] Recommendations prioritized

---

## Execution Guidelines

### Context Management

Between steps:
1. **Complete step** - Ensure output artifact is saved
2. **Clear context** - Start fresh conversation (optional but recommended)
3. **Load inputs** - Read required input artifacts
4. **Execute** - Run the step's tasks
5. **Validate** - Check success criteria

### Iteration Points

**Step 2 can iterate:**
- Adjust inference rules
- Change confidence thresholds
- Re-cluster evidence

**Step 3 can iterate:**
- Refine questions based on feedback
- Add more context
- Adjust default assumptions

**Step 4 can iterate:**
- User provides additional answers
- Clarify ambiguous responses
- Request more detail

### Error Recovery

**If Step 4 fails (answers unclear):**
1. Generate follow-up questions
2. Append to `03-questions.md` as "Section 6: Follow-up Questions"
3. Have user answer follow-ups
4. Re-run Step 4

**If Step 6 validation fails:**
1. Review validation errors
2. Go back to Step 4 or Step 5 to fix issues
3. Re-run validation

### Tooling Recommendations

| Step | Recommended Approach |
|------|---------------------|
| Step 1 | Python AST parsing + regex for evidence extraction |
| Step 2 | LLM for semantic inference + rule-based confidence |
| Step 3 | LLM for question generation from gaps |
| Step 4 | LLM for answer parsing + structured integration |
| Step 5 | Template-based file generation |
| Step 6 | Deterministic validation (jig validate) |

---

## Appendix A: Inference Rule Reference

### High-Confidence Rules (0.8+)

| Pattern | Inference | Example |
|---------|-----------|---------|
| `test_X_does_Y` | S: "X does Y" | test_graph_loads_nodes → "Graph loads nodes" |
| `XError("msg")` | S: "X is invalid" | CircularDependencyError → "Circular deps invalid" |
| Integration test scenario | O: scenario as outcome | test_user_authenticates → "Users authenticate" |
| Exception + test | S: constraint | Error thrown + test passes → Hard requirement |

### Medium-Confidence Rules (0.5-0.8)

| Pattern | Inference | Example |
|---------|-----------|---------|
| `MAX_X = N` | S: "X ≤ N" | MAX_DEPTH=100 → "Depth ≤ 100" |
| Docstring describes value | O: value statement | "Enables X" → O: "Users can X" |
| Test with default | S: default behavior | test_handles_empty → "Empty is valid" |

### Low-Confidence Rules (< 0.5)

| Pattern | Inference | Example |
|---------|-----------|---------|
| Public method exists | S: capability | do_something() → "Can do something" |
| Import exists | S: dependency | import X → "Requires X" |

---

## Appendix B: Question Templates

### Validation Template
```markdown
### Q{N}: {Topic} Validation

**Brick:** {BRICK-ID}

**What we observed:**
{Evidence list}

**Inferred Intent:**
> {ID}: "{Title}"
> {Description}

**Question:**
{Specific question about correctness}

**Default assumption:** {What we'll use if no answer}

### Your Answer
[Write your answer here]

### Notes
[Any additional context]
```

### Gap-Filling Template
```markdown
### Q{N}: {Topic}

**Brick:** {BRICK-ID}

**What we observed:**
{Evidence that suggests a gap}

**Gap:**
{What's missing}

**Question:**
{What we need to know}

**Default assumption:** {Fallback}

### Your Answer
[Write your answer here]

### Notes
[Any additional context]
```

---

## Appendix C: Complete Workflow Checklist

```markdown
## Intent Discovery Workflow Checklist

### Preparation
- [ ] AG010 Brick Discovery complete
- [ ] `bricks/*.brick.yaml` files exist
- [ ] `intent-discovery/` directory created

### Step 1: Evidence Extraction
- [ ] Code evidence extracted (docstrings, types, errors)
- [ ] Test evidence extracted (names, assertions)
- [ ] Brick evidence incorporated
- [ ] Output: `intent-discovery/01-evidence.yaml`

### Step 2: Intent Inference
- [ ] Inference rules applied
- [ ] Draft Outcomes created
- [ ] Draft Specifications created
- [ ] Gaps identified
- [ ] Output: `intent-discovery/02-inferred-intent.yaml`

### Step 3: Question Generation
- [ ] Validation questions for medium/low confidence
- [ ] Gap-filling questions for missing Intent
- [ ] Default assumptions documented
- [ ] Output: `intent-discovery/03-questions.md`

### Step 4: Answer Integration (USER INPUT)
- [ ] User answered questions in 03-questions.md
- [ ] Answers parsed and integrated
- [ ] New Intent created from answers
- [ ] Consistency verified
- [ ] Output: `intent-discovery/04-complete-intent.yaml`

### Step 5: Node Generation
- [ ] Outcome files created (`jig/outcomes/O-*.md`)
- [ ] Specification files created (`jig/specifications/S-*.md`)
- [ ] Graph index updated
- [ ] Output: `intent-discovery/05-generation-log.yaml`

### Step 6: Linkage & Validation
- [ ] Brick files updated with intent_mapping
- [ ] Validation passed
- [ ] Coverage calculated
- [ ] Output: `intent-discovery/06-validation-report.yaml`

### Completion
- [ ] All outputs saved and committed
- [ ] Remaining gaps documented
- [ ] Next steps identified
```

---

## References

- **AG010** - Brick Discovery Workflow (prerequisite)
- **AG002** - Alignment Graph Whitepaper (conceptual foundation)
- **JIG-Concept-v6.1** - Intent file format specification

---

**Next Step:** Execute Step 1 on a project with completed Brick analysis.
