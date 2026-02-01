---
title: "Related Work"
type: exploration
status: parked
created: 1763493911
created_human: "2025-11-18 13:25 CST"
parent: "[[SELA001_SELA-Concept-Document]]"
children: []
---
# Related Work  
**Structured English Language Abstraction (SELA)**  
**Version:** 0.1  
**Date:** 2025-11-06  

## Introduction  
SELA proposes a new layer of software abstraction: structured English definitions of intent, behaviors, invariants and examples that drive generation of code and tests via AI agents, with integrated traceability and semantic mappings (Value → Intent → Behavior → Test → Code).  
This “intent-first” layer builds upon and interacts with prior work in controlled natural languages, executable specification languages, model-driven development, and BDD/ATDD practices. This document surveys existing frameworks and positions SELA relative to them.

---

## Existing frameworks & languages

### Attempto Controlled English (ACE)  
- A controlled natural language (CNL) developed at the University of Zurich since 1995. It is a formally defined subset of English with deterministic semantics (first-order logic) designed for knowledge representation, requirements specification, querying and reasoning.  [oai_citation:0‡Wikipedia](https://en.wikipedia.org/wiki/Attempto_Controlled_English?utm_source=chatgpt.com)  
- Example usage: “Every woman is a human.” → unambiguous formal interpretation.  [oai_citation:1‡Wikipedia](https://en.wikipedia.org/wiki/Attempto_Controlled_English?utm_source=chatgpt.com)  
- Strengths: human-readable while machine‐processable, fits domain experts who are not logicians.  
- Limitations relative to SELA: ACE emphasizes formal logic mapping (KR) rather than driving code/test generation; it lacks the TDD workflow, behavior→test→code chain and trace graph of Values → Intents → Behaviors → Tests → Code.

### Semantics of Business Vocabulary & Rules (SBVR)  
- An OMG standard that defines vocabularies and business rules in structured English (or other notations) using a formal metamodel.  [oai_citation:2‡OMG](https://www.omg.org/spec/SBVR/1.3/?utm_source=chatgpt.com)  
- It allows business-domain experts to define terms (nouns), fact types (verbs), rules (modal operators, quantifiers) in a way that can be processed by tools.  [oai_citation:3‡KDM Analytics](https://www.kdmanalytics.com/sbvr/sbvr_intro_2.html?utm_source=chatgpt.com)  
- Strengths: strong alignment with business vocabularies, tool-interchange modelling, semantics for rules and domain facts.  
- Gaps relative to SELA: SBVR focuses on business rule modelling rather than full lifecycle from intent→test→code; it doesn’t prescribe test generation, TDD workflows or semantic trace mapping to implementation code.

### Behaviour-Driven Development (BDD) / Executable Specification Tools  
- Tools like Cucumber/Gherkin allow plain-text “Given/When/Then” stories that execute as tests.  
- Tools like Robot Framework and FitNesse allow tabular or wiki-based specifications as acceptance tests.  
- Strengths: direct link between spec-text and runnable tests; encourages collaboration among stakeholders.  
- Limitations: While they treat spec-text as code/test, they do *not* usually define a structured English *language* layer for intent and invariants, nor do they map systematically to a semantic graph of Values→Intents→Behaviors or generate code from spec automatically (most require manual step-implementations).  
- SELA’s differentiator: the spec (‘SELA document’) is the primary artifact; test generation and code generation are integral; semantic trace and abstraction layering are first-class.

### Model-Driven & Formal Specification Languages  
- Languages & tools such as TLA+, Alloy, and executable UML (fUML/ALF) allow high-level modeling of system behavior, invariants, and formal verification.  
- Strengths: rigorous, powerful for correctness, abstraction from low-level code.  
- Weaknesses relative to SELA: they require expertise in formal methods, do not leverage everyday English for intent, often lack integrated test-first code generation, and don’t necessarily center on the business/product-intent layer (Values → Intent) or trace mapping to tests and code.  
- SELA aims to borrow the abstraction and formal semantics ideas but embed them into a discipline of structured English, test-driven code generation, and a semantic trace network.

### Specification → Code / Schema-Driven Code Generation  
- Schemes like CUE (constraint language/tooling), OpenAPI + codegen, and other schema → stub/SDK frameworks treat spec as source of code/test/stub generation.  
- Benefits: strong toolchain discipline, deterministic generation of artifacts from spec.  
- Limitations: usually the spec is a formal schema or interface definition (not structured English “intent”); they typically don’t include the human-meaning layer (Values/Intent), do not embed invariants/tests automatically, and often don’t maintain a full trace graph from business value → code.  
- SELA’s goal: deliver the same discipline of spec→artifacts but raise the abstraction layer to “intent in structured English” and integrate tests and semantic graphs as first-class.

---

## Comparison Table  

| Framework / Tool | Primary Focus | English-readability | Code/Test generation | Trace Value→Intent→Behavior→Test→Code | TDD-first workflow |
|-------------------|-------------|----------------------|------------------------|----------------------------------------|--------------------|
| ACE                | Controlled English for logic & KR | ✅ strong             | Limited                 | Partial *(domain concepts)*             | ❌                 |
| SBVR               | Business vocabulary & rules       | ✅ good               | Limited                 | Partial *(business facts)*              | ❌                 |
| BDD (Gherkin/Robot) | Executable specs/tests            | ✅ good               | Semi-manual            | Limited                                 | ✅ (acceptance test)|
| TLA+/Alloy         | Formal behavior/specification     | ❌ low                | Manual/Proof            | Minimal                                  | ❌                 |
| Schema→Code (OpenAPI/CUE) | Spec→artifacts              | ❌ (technical spec)    | ✅ yes                 | Limited                                  | Partial            |
| **SELA (this work)**| Intent→Tests→Code via structured English + graph | ✅ explicit             | ✅ planned             | ✅ full mapping                          | ✅ core principle |

---

## Positioning SELA  
SELA sits at a unique intersection:  
- It **elevates natural language** (English) into a disciplined authoring medium (controlled English) rather than pure specification schemas.  
- It embeds **TDD** at the core: examples/invariants in the spec yield failing tests which drive code generation.  
- It builds a **semantic trace graph** from business value → product intent → behaviors → tests → implementation, enabling auditability, refactorability and tool-driven traversal.  
- It aims to integrate **human-readable intent**, **AI agent pipelines**, and **deterministic structure** rather than purely manual or purely model-driven approaches.  
- It lowers reliance on heavy formal methods by borrowing their rigor (structured semantics, invariants) but delivering usability for product engineers and cross-functional teams rather than formal-logic specialists.  
- It addresses legacy and forward-development alike: via reverse workflows (code → tests → intent) and forward workflows (intent → tests → code).  

---

## Gaps & Opportunities  
While related work supplies many of the pieces (controlled English, spec→code, executable tests, business rule modelling, formal semantics), SELA contributes the *combined system* of structured-English intent + TDD pipeline + semantic mapping + trace from business value to code. Some opportunities to refine include:  
- How to standardize the **ontology** (Values / Intents / Behaviors) across domains.  
- Tooling for **semantic graph traversal**, versioning, diffing and visualization (beyond what prior work builds).  
- The role of AI agents in bridging human spec and machine code: prompts, pipelines, error handling, drift detection.  
- Adoption by product-engineer teams (rather than logic specialists) and integration into CI/CD/dev workflows.  

---

## References  
1. Fuchs, N. E., Schwitter, R. “Attempto Controlled English (ACE).” 1996.  [oai_citation:4‡arXiv](https://arxiv.org/abs/cmp-lg/9603003?utm_source=chatgpt.com)  
2. “Attempto Controlled English.” Wikipedia.  [oai_citation:5‡Wikipedia](https://en.wikipedia.org/wiki/Attempto_Controlled_English?utm_source=chatgpt.com)  
3. Object Management Group. *Semantics of Business Vocabulary and Business Rules (SBVR) v1.3.*  [oai_citation:6‡OMG](https://www.omg.org/spec/SBVR/1.3/?utm_source=chatgpt.com)  
4. Brillant Feuto Njonko, P., Cardey, S., Greenfield, P., El Abed, W. “RuleCNL: A Controlled Natural Language for Business Rule Specifications.” 2014.  [oai_citation:7‡arXiv](https://arxiv.org/abs/1406.2096?utm_source=chatgpt.com)  

---

## Summary  
While no existing framework fully delivers all of SELA’s ambitions, many provide strong precedent in one or more dimensions: controlled natural English, executable specifications, semantic modelling, spec-to-artifact generation. SELA’s innovation is in **combining** those dimensions into a coherent developer-and-agent workflow, complete with traceability from strategy (Values) to implementation (Code).  
This positioning helps justify SELA as both novel and grounded in proven concepts.