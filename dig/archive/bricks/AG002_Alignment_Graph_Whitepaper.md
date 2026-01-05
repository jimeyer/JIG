---
title: "The Alignment Graph and Bricks"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1764019099
created_human: "2025-11-24 15:18 CST"
parent: "[[AG001_Alignment-Graph-Bricks]]"
children: []
---
# The Alignment Graph and Bricks

_A Hypothesis for Maintaining Architectural Integrity in Agent-Assisted Development_

---

## Abstract

Software systems exhibit a persistent three-way divergence: what we intend to build drifts from what we actually build, which drifts from what we actually verify. This alignment crisis intensifies as AI agents take on more implementation work, operating in codebases where architectural boundaries are implicit, context is unbounded, and design intent exists only in stale documentation.

We propose the **Alignment Graph** and **Bricks** as a unified architectural model that makes this three-way relationship explicit, measurable, and enforceable. The Alignment Graph is a machine-generated semantic graph representing intent, implementation, and verification as a single queryable structure. Bricks are architectural units that provide bounded contexts for both human design and agent execution.

This is not a proven solution. It is a hypothesis about how we might preserve architectural integrity as development becomes increasingly agent-assisted. This paper presents the model in sufficient detail that practitioners can evaluate, critique, and potentially test these ideas in their own contexts.

---

## 1. The Persistent Tension

### 1.1 The Three-Body Problem

Software development operates simultaneously in three realities:

**The World of Intention**
What we're trying to accomplish. The problems we're solving. The constraints we must satisfy. This lives in requirements documents, architectural diagrams, tickets, commit messages, and the collective memory of the team.

**The World of Implementation**
The actual code we write. The dependencies we create. The structure that emerges from thousands of incremental decisions. This lives in source files, call graphs, import relationships, and module boundaries.

**The World of Verification**
What we actually test. What coverage we achieve. What confidence we earn. This lives in test suites, CI pipelines, coverage reports, and QA processes.

Traditional development treats these as separate concerns, managed by separate tools, living in separate locations. The problem is that **these three realities drift apart constantly.**

You intend to build feature X with architectural property Y. You actually build something that's 80% of X, introduces unintended coupling Z, and happens to satisfy property Y only by accident. Your tests verify 60% of what you built and 40% of what you intended. Six months later, nobody knows what was meant, what exists, or what's actually verified.

### 1.2 Why This Matters More Now

This alignment crisis has always existed, but three trends make it more acute:

1. **Increased system complexity** - Modern systems have more dependencies, more layers, more emergent behavior
2. **Faster evolution cycles** - Changes happen more frequently, leaving less time for architectural review
3. **Agent-assisted implementation** - AI tools can write significant code quickly, but struggle to maintain architectural coherence

That third point deserves elaboration. When an AI agent works on a codebase, it faces an impossible choice:
- **See everything** → get overwhelmed, distracted, make unintended changes across boundaries
- **See too little** → miss critical context, break dependencies, create subtle bugs

Current tools offer the agent the entire codebase or nothing. There's no architectural middle ground. No principled way to say "here is the boundary of what you should concern yourself with."

### 1.3 What If We Could Unify These Realities?

What if we could make all three realities—intention, implementation, verification—visible in a single structure? Not as documentation that drifts, but as continuously generated ground truth?

What if we could define architectural boundaries that are machine-enforceable, providing both human designers and AI agents with the right level of context?

What if drift between intent, code, and tests became objectively measurable rather than a matter of opinion?

This is the hypothesis behind the Alignment Graph and Bricks.

---

## 2. The Alignment Graph: A Unified Semantic Model

### 2.1 Core Definition

The **Alignment Graph (AG)** is a machine-generated, machine-readable, and human-inspectable semantic graph representing a software system across four layers:

1. **Intent Layer** – what should exist and why
2. **Dependency Layer** – what actually exists in code
3. **Test Layer** – what is actually verified
4. **Brick Layer** – the architectural units binding the three together

The AG is generated automatically from observable facts:
- JIG Intent nodes (Outcomes and Specifications)
- Source code structure and dependencies
- Static analysis (call graphs, import relationships)
- Test discovery and coverage analysis
- Brick definition files

Critically, **the AG is not documentation**. It doesn't describe what we hope exists. It observes and represents what demonstrably exists, then measures alignment against what was intended.

### 2.2 Layer 1: Intent (Declared)

The Intent Layer contains the explicit declarations of what we're building and why:

**Outcome Nodes (O)**
Why we're building something. The value proposition, the problem being solved, the user need being addressed.

```yaml
id: O-AUTH-001
type: Outcome
content: "Users can authenticate securely without managing passwords"
rationale: "Reduce support burden and security risk from password reuse"
```

**Specification Nodes (S)**
What constraints the implementation must satisfy. These are testable, verifiable requirements.

```yaml
id: S-AUTH-002
type: Specification
content: "Authentication tokens expire after 15 minutes of inactivity"
verifiable: true
related_outcomes: [O-AUTH-001]
```

**Brick Nodes (B)**
High-level architectural units (defined in Section 3).

**Subsystem Nodes**
Groupings of related Bricks for higher-level organization.

Intent nodes are human-authored, durable, and design-oriented. They represent the **desired architecture and behavior**, not what accidentally emerged.

### 2.3 Layer 2: Dependency (Observed)

The Dependency Layer represents the actual implementation structure:

- **Code nodes**: functions, classes, modules discovered through static analysis
- **Import edges**: which modules depend on which
- **Call edges**: which functions call which
- **Brick membership**: which code nodes are assigned to which Bricks
- **Structural relationships**: inheritance, composition, interfaces

This layer is generated automatically from the codebase. It represents **what actually exists**, not what we assume exists or what documentation claims.

Example nodes:
```
Function: authenticate_user (src/auth/session.py:45)
Class: TokenValidator (src/auth/tokens.py:12)
Module: auth.session
Import: auth.session → auth.tokens
Call: authenticate_user() → TokenValidator.validate()
```

### 2.4 Layer 3: Test (Observed)

The Test Layer represents actual verification:

- **Test nodes**: test functions, integration tests, fixtures
- **Coverage edges**: which tests execute which code
- **Verification edges**: which tests verify which Intent nodes
- **Coverage metrics**: line coverage, branch coverage, mutation scores
- **Drift indicators**: tests orphaned from Intent, Intent lacking tests

This is generated from test discovery (pytest, unittest, etc.) and coverage analysis. It shows **what we actually verify**, not what we assume is tested.

Example:
```
Test: test_token_expiration (tests/test_auth.py:89)
Covers: TokenValidator.validate() (87% branch coverage)
Verifies: S-AUTH-002 (token expiration spec)
```

### 2.5 Layer 4: Brick (Architectural)

The Brick Layer defines architectural boundaries and groupings:

- **Brick definitions**: responsibility statements, interfaces, constraints
- **Brick assignments**: which Intent, code, and tests belong to each Brick
- **Brick dependencies**: which Bricks may depend on which others
- **Interface contracts**: public APIs exposed between Bricks

This layer bridges the gap between abstract intent and concrete implementation. It's the organizational schema that groups the other three layers into coherent architectural units.

### 2.6 Why the Alignment Graph Exists

Traditional software representation is fractured:
- Intent lives in docs (often stale)
- Code lives in repos (always changing)
- Tests live in test folders (sometimes orphaned)
- Architecture lives in diagrams (frequently aspirational)
- Drift lives everywhere (usually invisible)

The AG unifies these into a **single version of truth** that:
- Shows alignment between what was intended and what exists
- Reveals drift objectively through graph queries
- Powers agent reasoning with structured context
- Enables architecture enforcement through boundary validation
- Makes system design and evolution tangible and measurable

The graph answers questions that are currently hard or impossible:
- "Does our implementation actually match our design?"
- "Which specifications lack test coverage?"
- "Where is technical debt accumulating?"
- "What will break if I change this interface?"
- "Which code serves no documented intent?"

It does this not through documentation (which lies) but through **observation of ground truth**.

---

## 3. Bricks: The Architectural Quantum

### 3.1 Formal Definition

A **Brick** is a cohesive architectural unit that groups intent, code, and tests into a single, enforceable context boundary.

More precisely:

> **A Brick B is a 4-tuple (I, C, T, B) where:**
> - **I** is a set of Intent nodes (Outcomes and Specifications)
> - **C** is a set of code nodes (functions, classes, modules)
> - **T** is a set of test nodes verifying C and I
> - **D** is a set of declared Brick dependencies (B → B' edges)
>
> **Subject to constraints:**
> - Every Intent node in I must be addressed by some code in C
> - Every Specification node in I must be verified by some test in T
> - Code in C may only call code in C or in the public interface of Bricks in D
> - Tests in T may only verify code in C
> - B must be acyclic (no circular Brick dependencies)

This is the formal model. Practically, think of a Brick as a **cell membrane** with a clear inside, clear outside, and controlled exchange between them.

### 3.2 What Bricks Contain

Every Brick includes:

1. **Brick Definition File** (`brick.yaml`)
   - Unique identifier and name
   - Responsibility statement (why this Brick exists)
   - Public interface contracts (what it exposes)
   - Declared dependencies (which Bricks it may use)
   - Constraints and invariants

2. **Intent Nodes** belonging to the Brick
   - Outcome nodes explaining the "why"
   - Specification nodes defining the "what"

3. **Code Nodes** assigned to the Brick
   - Implementation of the Intent
   - Internal helpers and utilities
   - Data structures and algorithms

4. **Test Nodes** verifying the Brick
   - Unit tests for internal code
   - Integration tests for interface contracts
   - Verification tests for Specifications

5. **Interface Contracts**
   - Public functions and classes
   - Type signatures and protocols
   - Behavioral contracts and preconditions

6. **Dependency Declarations**
   - Which other Bricks this one may use
   - Which interfaces it consumes

This is a complete architectural slice: intent → implementation → verification, bounded and explicit.

### 3.3 What Bricks Explicitly Exclude

Bricks do **not** include:
- Other Bricks' code (even if in the same subsystem)
- Other Bricks' tests
- Internal details of adjacent Bricks
- Global project structure and scaffolding
- Build systems and tooling (unless that's the Brick's responsibility)

This isolation is **mandatory**. It's enforced by the Alignment Graph through dependency validation and by the Brick Context Contract (Section 4).

### 3.4 Why This Unit of Abstraction?

Files are too small. Entire subsystems are too big. Packages are implementation artifacts, not design decisions.

Bricks are sized to match how humans naturally think about architecture:
- Bigger than "I need to edit this function"
- Smaller than "I need to understand this entire service"
- Aligned with responsibility and cohesion
- Composable and reusable
- Understandable in a single context load

They also provide the right scope for agent work:
- Large enough to accomplish meaningful tasks
- Small enough to fit in context windows
- Bounded enough to prevent architectural violations
- Complete enough to include Intent and verification

Bricks are the missing abstraction layer between "code files" and "architecture diagrams."

---

## 4. The Brick Context Contract

The Brick Context Contract defines what an agent (or human) can and cannot access when working inside a Brick. This is how we enforce architectural boundaries.

### 4.1 Allowed Inside a Brick Context

When operating inside Brick B, you have access to:

1. **The Brick definition file** for B
2. **All Intent nodes** assigned to B (Outcomes and Specifications)
3. **All code nodes** assigned to B (full implementation)
4. **All test nodes** assigned to B (full test suite)
5. **Public interfaces** of Bricks in D (B's declared dependencies)
6. **Brick-local dependency graph** (how B's internals relate)

This is everything needed to understand, modify, and verify the Brick—and nothing more.

### 4.2 Forbidden Inside a Brick Context

When operating inside Brick B, you **cannot** access:

1. Any code outside B (even within the same subsystem)
2. Any tests outside B
3. Internal implementation details of other Bricks
4. Global call graphs or import maps
5. Repository-level filesystem structure (beyond B's assigned files)
6. Any dependencies not explicitly declared in D

This creates a **clean-room environment** where:
- You cannot accidentally introduce illegal dependencies
- You cannot refactor code outside the Brick's responsibility
- You cannot hallucinate cross-boundary behavior
- You cannot erode architectural boundaries through convenience

### 4.3 Why This Contract Matters

Without enforced boundaries, agents (and humans) take the path of least resistance:
- Import from anywhere because it's easier than dependency injection
- Modify shared code because it's faster than proper interfaces
- Test through internals because it's simpler than proper mocking

The Brick Context Contract makes the path of least resistance **the architecturally correct path**. You literally cannot see code you shouldn't depend on. You cannot import modules outside your declared dependencies.

This is architecture enforcement through information hiding, not through code review alone.

---

## 5. Two Modes of Operation

The Brick model enables two distinct operating modes with different visibility and purposes.

### 5.1 Architecture Mode: Designing the System

**What you see:**
- All Brick definitions and responsibilities
- All Subsystem groupings
- All Intent nodes (Outcomes and Specifications)
- All public interfaces (signatures only, no implementations)
- The Brick-level dependency graph (which Bricks depend on which)

**What you don't see:**
- Any implementation code
- Any test code
- Any internal details
- Any file names or directory structure
- Any low-level dependencies

**Purpose:**
Design and reshape the system's architectural structure without drowning in implementation noise.

**Example tasks:**
- "We need to split the Authentication Brick—session management and token validation have different responsibilities"
- "Which Bricks would be affected if we introduce a rate-limiting layer?"
- "This Brick has too many dependencies—what interfaces could we introduce to decouple it?"

Architecture Mode lets you **think with shapes, flows, and semantics**, not syntax.

### 5.2 Implementation Mode: Building Inside a Brick

**What you see:**
- This Brick's definition and responsibilities
- This Brick's Intent nodes
- This Brick's full code (implementation details)
- This Brick's full tests
- Public interfaces of neighboring Bricks (declared dependencies)
- This Brick's local dependency graph

**What you don't see:**
- Anything outside this Brick's boundary
- Internal details of other Bricks
- Global system structure

**Purpose:**
Implement features and fix bugs within architectural constraints, safely and locally.

**Example tasks:**
- "Implement the token expiration logic required by S-AUTH-002"
- "Add test coverage for the edge case identified in the last incident"
- "Refactor this module for better testability without changing the interface"

Implementation Mode ensures **local reasoning, safety, and architectural correctness** by limiting context to what's relevant.

### 5.3 Why This Separation Is Powerful

Traditional development mixes architectural thinking and implementation thinking constantly. You're reading code trying to understand system design. You're designing interfaces while worrying about implementation complexity.

Separating these modes allows:
- **Clearer architectural decisions** without premature implementation concerns
- **Safer implementation work** without accidentally violating architectural intent
- **Better tool support** (IDEs, agents, linters) tailored to the task at hand
- **Reduced cognitive load** from context switching

An agent in Architecture Mode can't accidentally refactor internals while redesigning interfaces. An agent in Implementation Mode can't introduce cross-boundary dependencies because they're not visible.

---

## 6. Alignment Checking and Drift Detection

With the Alignment Graph and Bricks in place, alignment and drift become objectively measurable.

### 6.1 Intent ↔ Code Alignment

Questions the AG can answer:

**Completeness:**
- Does every Intent node belong to a Brick?
- Does every Brick have code implementing its Intent?
- Are there Intent nodes with no implementing code? (unimplemented features)

**Coherence:**
- Does the code in Brick B actually serve the Intent assigned to B?
- Is there code in B unrelated to any Intent node in B? (orphan code)
- Are there functions serving Intent from multiple Bricks? (boundary violations)

**Query example:**
```
MATCH (intent:Outcome)-[:ASSIGNED_TO]->(brick:Brick)
WHERE NOT EXISTS {
  MATCH (brick)-[:CONTAINS]->(code:Function)
  WHERE (code)-[:IMPLEMENTS]->(intent)
}
RETURN intent.id, brick.id
// Returns Outcomes assigned to Bricks with no implementing code
```

### 6.2 Intent ↔ Test Alignment

Questions the AG can answer:

**Verification:**
- Is every Specification verified by at least one test?
- Does every Outcome have test coverage?
- Are there Intent nodes we assume work but never actually verify?

**Coverage:**
- Which Specifications have only partial test coverage?
- Which tests verify multiple Specifications? (coupling in tests)
- Which tests are orphaned from Intent? (testing implementation details only)

**Query example:**
```
MATCH (spec:Specification)-[:ASSIGNED_TO]->(brick:Brick)
WHERE NOT EXISTS {
  MATCH (brick)-[:CONTAINS]->(test:Test)
  WHERE (test)-[:VERIFIES]->(spec)
}
RETURN spec.id, spec.content
// Returns Specifications lacking test verification
```

### 6.3 Code ↔ Architecture Alignment

Questions the AG can answer:

**Boundary integrity:**
- Does code in Brick B only call code in B or B's declared dependencies?
- Are there illegal dependencies crossing Brick boundaries?
- Do actual import relationships match declared Brick dependencies?

**Structural correctness:**
- Does the call graph match intended architectural flow?
- Are there unexpected coupling patterns?
- Has circular dependency crept into previously acyclic structure?

**Query example:**
```
MATCH (brick1:Brick)-[:CONTAINS]->(code1:Function)
MATCH (code1)-[:CALLS]->(code2:Function)
MATCH (brick2:Brick)-[:CONTAINS]->(code2)
WHERE brick1 <> brick2
  AND NOT EXISTS {
    MATCH (brick1)-[:DEPENDS_ON]->(brick2)
  }
RETURN brick1.id, brick2.id, code1.name, code2.name
// Returns illegal cross-Brick calls
```

### 6.4 Types of Drift

When these alignments break down, you have measurable drift:

**Intent Drift**
What we built doesn't match what we said we'd build.
- Unimplemented Specifications
- Unverified Outcomes
- Code solving problems not in any Intent node

**Architecture Drift**
Structure is eroding from design.
- Boundary violations (illegal dependencies)
- Increased coupling (more cross-Brick calls)
- Interface erosion (internal details leaking)

**Test Drift**
Verification doesn't match Intent or implementation.
- Specifications lacking tests
- Tests orphaned from Intent
- Coverage gaps in critical code

The Alignment Graph makes drift **objectively detectable** through graph queries, not subjective code review opinions.

---

## 7. Why This Might Work

### 7.1 For Human Designers

Bricks operate at the **right level of abstraction**:
- Bigger than individual functions (avoids micro-management)
- Smaller than entire subsystems (maintains comprehensibility)
- Aligned with how we naturally partition responsibility
- Explicit about boundaries (reduces assumptions and miscommunication)

The separation of Architecture Mode and Implementation Mode matches how humans naturally think:
- Sometimes you need to think about system design without implementation details
- Sometimes you need to focus on implementation without architectural distractions
- Mixing these contexts creates cognitive load and poor decisions

Explicit Intent nodes make design decisions **durable and visible**:
- Why decisions were made doesn't get lost in code comments
- Specifications remain attached to implementations
- Refactoring can preserve intent even when changing structure

### 7.2 For AI Agents

Bricks provide the **right constraints** for productive agent work:

**Confined context:**
Agents see only what's relevant, reducing hallucination and distraction.

**Clear responsibilities:**
The Brick definition and Intent nodes give explicit goals, not vague instructions.

**Enforced boundaries:**
Agents cannot violate architectural boundaries because invisible code cannot be called.

**Verification built-in:**
Tests and Specifications are present in the same context, enabling test-driven development.

**Deterministic scope:**
The agent knows exactly what it's responsible for and what it's not.

This addresses the core problem of agent-assisted development: how to give the agent enough context to be useful without so much context that it gets lost or makes harmful changes.

### 7.3 For System Evolution

The Alignment Graph provides **continuous truth**:

**No documentation drift:**
The AG is generated from observable facts, not maintained docs.

**Automated drift detection:**
Graph queries run continuously, catching problems early.

**Architectural enforcement:**
Boundary violations fail validation, not just code review.

**Guided evolution:**
Alignment metrics show where attention is needed.

**Objective technical debt measurement:**
Drift scores quantify how far reality has diverged from intent.

This shifts architecture from aspiration to mechanism. You're not documenting the design you hope exists—you're defining boundaries that are enforced, checking alignments that are measured, and detecting drift that is quantified.

---

## 8. Historical Context and Influences

This model doesn't emerge from vacuum. It inherits ideas from several architectural traditions:

**Parnas, Information Hiding (1972)**
Modules with clear interfaces and hidden implementations. Bricks formalize this with machine-enforced boundaries.

**Domain-Driven Design (Evans, 2003)**
Bounded contexts with explicit relationships. Bricks are bounded contexts at code-level granularity.

**Clean Architecture (Martin, 2012)**
Dependency rules and boundary enforcement through layers. Bricks enforce boundaries horizontally (between architectural units), not just vertically (between layers).

**Microservices Architecture**
Independent deployable units with API contracts. Bricks bring this pattern inside the monolith, making boundaries enforceable even without network boundaries.

**Simon, Nearly Decomposable Systems (1962)**
Systems structured as semi-independent subsystems with limited interaction. Bricks operationalize this theory with explicit dependency graphs and interface contracts.

**What's novel:**

1. **Tri-fold binding** – Intent, Implementation, and Verification bound together in a single architectural unit
2. **Machine enforcement** – Boundaries validated automatically through the Alignment Graph, not just in code review
3. **Agent context fencing** – Explicit scoping designed for AI development, not just human modularity
4. **Continuous drift measurement** – Alignment checked constantly, not assumed until problems emerge
5. **Operational at code level** – Works inside a codebase, not just at service or package boundaries

The synthesis of these ideas into a unified model is the contribution here.

---

## 9. Open Questions and Limitations

### 9.1 This Is a Hypothesis

We need to be clear: **this model is untested at scale.**

It represents a coherent theory about how to maintain architectural integrity in agent-assisted development, but it remains to be proven whether:
- The overhead of defining and maintaining Bricks is worth the architectural benefits
- The Alignment Graph can scale to large codebases (10M+ lines)
- Real developers will adopt Architecture Mode vs Implementation Mode in practice
- Agents will actually stay within Brick boundaries or find ways to hallucinate cross-boundary behavior
- The alignment metrics actually correlate with system quality and maintainability

### 9.2 Practical Challenges

**Bootstrapping:**
How do you introduce Bricks into an existing codebase? Does it require wholesale restructuring, or can Bricks be adopted incrementally?

**Granularity:**
What's the right size for a Brick? Too small and you have too many boundaries. Too large and you lose the benefits of context confinement.

**Tooling:**
This model requires sophisticated tooling for:
- Generating the Alignment Graph from code
- Enforcing Brick Context Contracts in IDEs and agents
- Visualizing alignment and drift
- Running graph queries efficiently

**Evolution:**
How do Bricks change over time? What happens when a Brick needs to split or merge? How is this coordinated with existing code?

**Human factors:**
Will developers actually write Intent nodes, or will this feel like bureaucratic overhead? How do we make Intent authoring feel valuable rather than burdensome?

### 9.3 Questions for Experimentation

To validate (or refute) this hypothesis, we need experiments that measure:

1. **Agent predictability:** Do agents operating within Brick boundaries make fewer architectural mistakes than agents with full codebase access?

2. **Maintenance burden:** Is the cost of defining and maintaining Bricks offset by reduced debugging and refactoring effort?

3. **Drift detection efficacy:** Do alignment metrics give early warning of problems, or do they just measure what we already know?

4. **Architectural integrity:** Do systems structured with Bricks maintain better separation of concerns over time compared to traditional approaches?

5. **Developer adoption:** Do human developers find Bricks helpful for understanding and navigating codebases, or do they work around them?

These are empirical questions. The model is only useful if the answers are favorable.

---

## 10. Paths Forward

### 10.1 Minimal Viable Implementation

To test these ideas, we don't need a complete implementation. A minimal version could:

1. **Define a small Brick taxonomy** for one subsystem
2. **Generate a basic Alignment Graph** from static analysis
3. **Implement simple boundary checking** (detect illegal dependencies)
4. **Measure one alignment metric** (e.g., Specifications without tests)
5. **Run one agent experiment** (compare agent work with/without Brick context boundaries)

This would be sufficient to validate or refute core hypotheses.

### 10.2 Tool Ecosystem

If the model proves viable, a mature implementation would require:

**Graph generation:**
- Static analysis pipeline (AST parsing, dependency extraction)
- Test discovery and coverage mapping
- Intent node extraction from structured comments or separate files
- Brick definition parsing and validation

**Graph storage and querying:**
- Graph database (Neo4j, or embedded graph lib)
- Query API for alignment checks
- Incremental update on code changes

**Developer tooling:**
- IDE plugins for Brick-aware navigation
- Linters that enforce Brick Context Contracts
- Visualizations of Bricks, dependencies, and alignment

**Agent integration:**
- Context generation for Bricks (what the agent sees)
- Boundary enforcement in agent code generation
- Intent-aware code suggestions

### 10.3 Research Questions

Beyond implementation, this model opens research directions:

**Formal verification:**
Can we formally verify that code satisfies Specifications using the AG structure?

**Automated refactoring:**
Can we use alignment metrics to automatically suggest architectural improvements?

**Learning from drift patterns:**
Do certain drift patterns predict bugs or outages?

**Optimal Brick sizing:**
Is there a mathematical model for optimal Brick granularity based on cognitive load and coupling metrics?

**Intent mining:**
Can we automatically extract Intent from existing code, docs, and commit history to bootstrap the AG?

---

## 11. Conclusion

Software development faces an alignment crisis: what we intend diverges from what we build, which diverges from what we verify. This crisis intensifies as AI agents take on more implementation work, lacking the architectural context and boundaries that human developers implicitly understand.

The **Alignment Graph** and **Bricks** are a hypothesis for addressing this crisis:

- The Alignment Graph unifies intent, implementation, and verification into a single queryable structure, making drift visible and measurable.
- Bricks provide bounded architectural units that give both humans and agents the right level of context—large enough to be meaningful, small enough to be comprehensible.
- The Brick Context Contract enforces boundaries, preventing the architectural erosion that plagues long-lived systems.
- Alignment checking transforms architecture from documentation to mechanism, from aspiration to enforcement.

This is not a proven solution. It's a model that deserves experimentation, critique, and refinement.

The goal isn't to over-promise a silver bullet for software complexity. The goal is to present a coherent architectural framework that:
- Makes implicit architectural decisions explicit
- Makes invisible drift visible
- Provides structure for agent-assisted development
- Enables objective measurement of architectural health

If these ideas resonate—if the problems described feel real and the proposed solutions feel promising—then the next step is implementation and measurement. Build a minimal AG. Define Bricks for one subsystem. Run an agent experiment. Measure the outcomes.

Architecture should be more than aspiration. It should be observable, measurable, and enforceable.

That's the hypothesis. Let's test it.

---

## References and Further Reading

**Foundational concepts:**
- Parnas, D.L. (1972). "On the Criteria To Be Used in Decomposing Systems into Modules"
- Simon, H.A. (1962). "The Architecture of Complexity"
- Evans, E. (2003). *Domain-Driven Design*
- Martin, R.C. (2012). *Clean Architecture*

**Related work on architectural enforcement:**
- Murphy, G. et al. (2001). "Software Reflexion Models: Bridging the Gap between Design and Implementation"
- Terra, R. et al. (2015). "Dependency Constraint Language: A Language for Architectural Constraint Specification"

**Agent-based development challenges:**
- Barke, S. et al. (2023). "Grounded Copilot: How Programmers Interact with Code-Generating Models"
- Hou, X. et al. (2023). "Large Language Models for Software Engineering: Survey and Open Problems"

---

_This whitepaper presents a hypothesis, not a conclusion. The ideas are offered for evaluation, experimentation, and critique by the software engineering community._
