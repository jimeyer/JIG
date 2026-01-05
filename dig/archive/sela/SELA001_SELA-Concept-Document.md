---
title: "SELA Concept Document"
type: exploration
status: parked
created: 1763493911
created_human: "2025-11-18 13:25 CST"
parent: null
children: ['[[SELA002_SELA-Concept-v2]]']
---
# SELA Concept Document  
**Structured English Language Abstraction (SELA)**  
**Version:** 0.1  
**Date:** 2025-11-06  

---

## 1. Overview  

**SELA** (Structured English Language Abstraction) is a new programming abstraction layer designed for the age of AI-assisted software development.  
It moves the primary act of programming from writing syntax in a programming language to writing **structured English definitions of intent** that AI agents can compile deterministically into code, tests, and documentation.  

Just as:
- Assembly abstracted away machine code, and  
- C abstracted away Assembly,  

**SELA abstracts away implementation**, allowing humans to design **meaning and behavior** directly.  

SELA’s goal is to make English a *structured, auditable, and executable source of truth* — precise enough for machines, expressive enough for humans.

---

## 2. Manifesto  

SELA represents the next step in programming abstraction.  
It enables engineers to express *intent* rather than implementation, replacing code as the central artifact with structured English that defines purpose, behavior, and constraints.  

> “Just as C freed programmers from assembly, SELA frees creators from syntax.”  

SELA formalizes English into an **engineering-grade medium**:  
structured enough for deterministic parsing,  
traceable enough for version control,  
and expressive enough to capture human reasoning.  

---

## 3. Functional Characteristics  

| Category | Characteristic | Description |
|-----------|----------------|-------------|
| **Structure** | Deterministic schema | Standard sections (`PURPOSE`, `INPUTS`, `OUTPUTS`, `INVARIANTS`, `EXAMPLES`). Enables parsing and diffing. |
| | Hierarchical nesting | Modules can contain functions, subsystems, and behaviors. |
| **Constraint** | Controlled English | Restricted vocabulary using modal verbs (`MUST`, `SHOULD`, `ENSURE`, `WHEN`). |
| | Shared ontology | Common glossary prevents synonym drift. |
| **Composability** | Modular design | SELA files can import or reference other SELA modules. |
| **Traceability** | Round-trip determinism | Regenerating from SELA produces equivalent code and tests. |
| | Semantic diffs | Diffs report *meaning changes* not text deltas. |
| **Executable semantics** | Embedded examples | Human-written examples become runnable tests. |
| | Runtime verification | Generated code can self-report conformance. |
| **Governance** | Versioned schema | SELA has its own spec and grammar versioning. |
| **Accessibility** | Human-readable, machine-parseable | Markdown structure with embedded metadata headers. |

---

## 4. Artifacts  

### 4.1 Repository Structure  

sela/
├── README.md
├── manifesto.md
├── spec/
│   ├── sela_language_spec.md
│   ├── sela_grammar.yaml
│   ├── sela_schema.json
│   ├── keywords.md
│   └── conventions.md
├── examples/
│   ├── function_example.sela.md
│   ├── subsystem_example.sela.md
│   └── test_example.sela.md
├── compiler/
│   ├── sela_parser.py
│   ├── sela_validator.py
│   ├── sela_diff.py
│   ├── sela_cli.py
│   └── prompts/
│       ├── validate_prompt.txt
│       ├── compile_prompt.txt
│       ├── testgen_prompt.txt
│       ├── diff_prompt.txt
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
├── language_reference.md
├── design_principles.md
├── style_guide.md
└── faq.md

### 4.2 Key Artifact Types  

| Artifact | Purpose |
|-----------|----------|
| **Spec files** | Define SELA grammar, schema, and keywords. |
| **Prompts** | Define how AI agents interpret SELA. |
| **Examples** | Demonstrate usage and code generation. |
| **Validator** | Ensures SELA docs conform to spec. |
| **CLI tools** | Enable validate/compile/diff operations. |
| **Tests** | Verify SELA compiler determinism. |

---

## 5. Workflows  

### 5.1 Core SELA Workflows

| Phase | Human Role | Agent Role | Goal |
|--------|-------------|-------------|------|
| **Intent Capture** | Write SELA doc | Validate structure and vocabulary | Capture precise, testable intent |
| **Compilation** | Trigger build | Generate code/tests | Create executable realization of intent |
| **Review & Audit** | Inspect diffs | Explain mapping | Validate fidelity between intent and code |
| **Execution** | Run tests | Verify conformance | Confirm behavioral correctness |
| **Refactor & Evolve** | Update SELA | Suggest diffs | Maintain intent over time |
| **Explain & Educate** | Ask questions | Answer from SELA corpus | Make intent transparent |

### 5.2 TDD Workflow  

SELA is inherently **test-driven**.  
The SELA doc defines examples and invariants; the agent generates failing tests first, then code to make them pass.

1️⃣ validate_prompt
2️⃣ testgen_prompt
3️⃣ run_tests (fail)
4️⃣ compile_prompt
5️⃣ run_tests (pass)
6️⃣ check_prompt
7️⃣ refactor_prompt

Tests are not derived from code; **code is derived from tests**.  

---

## 6. Agent Prompts  

### 6.1 Core Prompts  

| Name | Function |
|------|-----------|
| **validate_prompt** | Ensure structure and controlled language compliance. |
| **testgen_prompt** | Generate failing tests from SELA examples/invariants. |
| **compile_prompt** | Generate code to pass tests. |
| **check_prompt** | Review results, identify missing coverage. |
| **diff_prompt** | Show semantic changes between SELA versions. |
| **refactor_prompt** | Suggest code/intent alignment improvements. |
| **explain_prompt** | Map code → SELA meaning. |

### 6.2 Example: `compile_prompt.txt`

You are a SELA Implementation Generator.
Goal: produce minimal deterministic code that passes provided tests and satisfies SELA intent.
	1.	Read SELA PURPOSE, INPUTS, INVARIANTS.
	2.	Implement only what is tested and described.
	3.	Include docstrings referencing SELA version and test IDs.
	4.	Never add behavior not explicitly specified.

---

## 7. Reverse-SELA Workflow  

Many developers will apply SELA to **existing codebases**.  
Reverse-SELA recovers meaning from code back up the abstraction stack.

| Phase | Input | Output | Agent Prompt |
|--------|--------|---------|---------------|
| **Discover** | Source code | Structural map | `analyze_code_prompt.txt` |
| **Extract Tests** | Code + comments | Behavioral tests | `generate_tests_prompt.txt` |
| **Validate Tests** | Human review | Passing baseline | — |
| **Abstract Intent** | Code + tests | SELA doc | `abstract_intent_prompt.txt` |
| **Roundtrip Verify** | Code + regenerated code | Semantic diff | `verify_roundtrip_prompt.txt` |

Reverse-SELA turns implicit knowledge in legacy systems into explicit, structured SELA documents.

---

## 8. Semantic Mapping Model  

SELA and VIB content interlink through a **Semantic Graph** structure, not flat mappings.

### 8.1 Core Node Types  

| Node | Example | Description |
|-------|----------|-------------|
| **Value** | Rider Confidence | Strategic, qualitative anchor |
| **Intent** | Intuitive Control | Describes goal or purpose |
| **Behavior** | Deterministic Shift | Observable system behavior |
| **Test** | Shift_Determinism_Test | Verifies a behavior |
| **Code** | shift_controller.py | Implementation artifact |

### 8.2 Edge Types  

| Edge | Relationship |
|------|---------------|
| `REALIZES` | Intent → Value |
| `SPECIFIES` | Behavior → Intent |
| `VERIFIES` | Test → Behavior |
| `IMPLEMENTS` | Code → Behavior |
| `EVIDENCES` | Test Result → Intent/Behavior |

### 8.3 Representation Example (YAML)

```yaml
nodes:
  - id: V001
    type: Value
    name: Rider Confidence
  - id: I012
    type: Intent
    name: Intuitive Control
  - id: B033
    type: Behavior
    name: Deterministic Shift
edges:
  - from: I012
    to: V001
    type: REALIZES
  - from: B033
    to: I012
    type: SPECIFIES

This structure can be expressed as JSON-LD, GraphQL, or stored in a graph database like Neo4j.
It is queryable, diffable, and versionable.

⸻

9. PDCA Loop for SELA Evolution

Phase	Objective	Activities	Output
PLAN	Identify workflow friction	Observe AI runs, collect issues	SELA Improvement Proposal (SIP)
DO	Implement experiment	Modify grammar/prompts	Branch implementation
CHECK	Measure results	Run determinism and usability tests	Validation data
ACT	Propagate or revert	Merge or tag release	Updated SELA version

SELA evolves continuously as a living language.

⸻

10. Human + Agent Roles

Role	Human Responsibility	Agent Responsibility
Author	Define intent, examples, invariants	Validate grammar
Engineer	Interpret SELA diffs, approve code	Compile code/tests
Reviewer	Ensure alignment with business value	Explain traceability
Maintainer	Manage spec versioning	Auto-generate schema updates


⸻

11. SELA in Practice

11.1 Forward Development

Humans write SELA docs → AI generates tests → code passes tests → SELA is source of truth.

11.2 Reverse Engineering

AI reads code → generates tests and SELA docs → humans validate recovered intent.

11.3 Unified Graph

All SELA docs, tests, and code connect through a semantic graph — traversable, auditable, and explainable.

⸻

12. Areas of Future Exploration

Theme	Description
Semantic Graph Tooling	Build lightweight deterministic graph libraries for SELA traversal (YAML/JSON).
CRDT Collaboration	Enable multi-agent, concurrent SELA editing using CRDT graphs.
Ontology Definition	Formalize shared vocabulary for Values, Intents, and Behaviors.
Roundtrip Fidelity Metrics	Develop metrics for how closely regenerated code matches original.
Visualization Tools	Create graph/diagram renderers for SELA networks.
Prompt Evolution	Version prompts like compilers; explore fine-tuned, smaller models for deterministic SELA compilation.
AST Integration	Represent SELA as Intent Syntax Trees (ISTs) compatible with tree-sitter or ast-grep.
LLM Minimization	Shift as much as possible to deterministic traversal and parsing; LLMs only used for text–to–structure translation.
Governance Framework	Create SELA Improvement Proposals (SIPs) as community-driven governance.


⸻

13. Summary

SELA defines a structured English layer that lets humans express software meaning with precision and traceability.
It treats intent, not syntax, as the primary unit of engineering.
AI agents become compilers that generate implementation and verification from human meaning.
The result is a new, collaborative development model where code and behavior evolve under the governance of structured human thought.

“Readable as prose, processable as data, executable as intent.”

⸻


