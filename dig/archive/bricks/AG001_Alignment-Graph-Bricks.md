---
title: "Alignment Graph & Bricks"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1763934216
created_human: "2025-11-23 15:43 CST"
parent: null
children: ['[[AG002_Alignment_Graph_Whitepaper]]', '[[AG002_Understanding_Alignment_and_Bricks]]']
---
# Alignment Graph & Bricks

_A Unified Architectural Model for Human–Agent Software Development_

---

## Overview

Modern software systems suffer from three chronic structural problems:

1. **Intent drift** — What we _meant_ to build doesn't match what got built.
2. **Architecture erosion** — Code and tests slowly decay away from any original design.
3. **Agent unpredictability** — AI assistants see too much, get distracted, and modify things outside their intended scope.

The **Alignment Graph** and **Bricks** directly address these issues.

Together they provide:
- a unified model of **Intent**, **Implementation**, and **Verification**
- enforceable architectural boundaries
- safe context scopes for agent work
- a reusable system-level structure that keeps human design aligned with agent execution

This document defines:
- What the Alignment Graph is
- What Bricks are
- How Bricks connect intent ↔ code ↔ tests
- How agents operate safely inside Bricks
- How architects design Bricks without implementation noise
- Drift detection and architectural integrity

---

## 1. The Alignment Graph

The **Alignment Graph (AG)** is a machine-generated, machine-readable, and human-inspectable **semantic graph** that represents a software system across three layers:

1. **Intent Layer** – what should exist and why
2. **Dependency Layer** – what actually exists in code
3. **Test Layer** – what is actually verified
4. **Brick Layer** – the architectural units binding the three together

The AG is generated automatically from:
- JIG Intent nodes
- source code
- dependency analysis
- coverage/test analysis
- Brick definition files

The AG allows both humans and agents to see the _truth_ of the system, not assumptions.

### 1.1 The Three Observable Layers

#### Intent Layer (Declared)

This layer contains:
- **Outcome nodes (O)** — Why we're building something
- **Specification nodes (S)** — What constraints it must satisfy
- **Brick nodes (B)** — High-level architectural units
- **Subsystem nodes** — Groupings of Bricks

Intent nodes are human-authored, durable, and design-oriented. They represent the **desired architecture and behavior**.

#### Dependency Layer (Observed)

This layer contains:
- code nodes (functions, classes, modules)
- observed import/call graph edges
- inferred Brick membership
- structural relationships within the implementation

This is the **real implementation**, not what we hoped it looked like.

#### Test Layer (Observed)

This contains:
- test nodes (pytest functions, integration tests, fixtures)
- test coverage → code mapping
- test → intent verification mapping
- test drift and coverage gaps

This layer represents **what we actually verify**, not what we assume is tested.

### 1.2 Why the Alignment Graph Exists

The AG exists because traditional software representation is fractured:
- Intent lives in docs
- Code lives in repos
- Tests live in test folders
- Architecture lives in diagrams
- Drift lives everywhere

The AG unifies these into a **single version of truth** that:
- shows alignment
- reveals drift
- powers agent reasoning
- enables architecture enforcement
- makes system design and evolution tangible

---

## 2. Bricks

A **Brick** is the fundamental architectural unit of the system.

It is a **context boundary**, a **clean room**, and a **design element**.

### 2.1 What a Brick Is

Formally:

> **A Brick is a cohesive architectural unit that groups intent, code, and tests into a single, enforceable context boundary.**

Practically:
- a Brick is a _ring-fence of context_
- agents operate inside one Brick at a time
- Bricks define the stable architectural shape of the system
- Bricks represent human design decisions, not files or packages

Bricks are like modular Lego blocks:
- they snap together cleanly
- each has a clear responsibility
- each has a clear interface
- each encloses internal complexity
- each resists unwanted coupling

Bricks are the **join point** tying Intent → Implementation → Tests together.

### 2.2 What Bricks Contain

Every Brick includes:
- **Brick Definition File** (responsibilities, boundaries, interfaces)
- **Outcome nodes** belonging to the Brick
- **Specification nodes** the Brick must satisfy
- **Assigned code nodes** (implementation)
- **Assigned test nodes** (verification)
- **Interface contracts** (public APIs only)
- **Declared Brick dependencies** (allowed neighbors)

This is a complete architectural slice.

### 2.3 What Bricks Explicitly Exclude

Bricks do **not** include:
- other Bricks' code
- other Bricks' tests
- global project structure
- internal details of adjacent Bricks
- implementation noise

This isolation is **mandatory**. It is enforced by the AG and by the Brick Context Contract.

---

## 3. The Brick Context Contract

The Brick Context Contract defines what an agent can and cannot do inside a Brick.

### 3.1 Allowed Inside a Brick

- Brick definition file
- Brick-level Intent nodes
- Brick-level code nodes
- Brick-level test nodes
- Public interfaces of adjacent Bricks
- Brick dependency graph slice

### 3.2 Forbidden Inside a Brick

- any code outside the Brick
- any tests outside the Brick
- internal details of other Bricks
- any global call graphs
- any repo-level filesystem structure
- any details not explicitly exposed via Brick interfaces

This creates a **clean-room environment** where the agent:
- cannot leak dependencies
- cannot accidentally refactor outside the Brick
- cannot hallucinate cross-boundary behavior
- cannot erode architecture

This is how we get consistency and containment.

---

## 4. Architecture Mode

**Architecture Mode** is the agent's environment for _designing the system of Bricks_.

In this mode, the agent sees:
- all Brick definitions
- all subsystem definitions
- interfaces (signatures only)
- Intent (O + S nodes)
- the Brick-level dependency graph

The agent **does not** see:
- any code
- any tests
- any implementation detail
- any file names

This allows the agent to:
- design new Bricks
- reshape existing Bricks
- propose boundaries
- design interfaces
- suggest Brick-to-Brick relationships
- propose new architectural views

Architecture Mode **thinks with shapes, flows, and semantics, not syntax**.

---

## 5. Implementation Mode

Implementation Mode is the agent's environment for _building_ inside a Brick.

In this mode, the agent sees:
- Brick definition
- Brick intent
- Brick code
- Brick tests
- Brick interface neighbors
- Brick-local dependency graph slice

The agent sees **nothing else**.

This ensures:
- local reasoning
- implementation safety
- lack of distraction
- architectural correctness

The agent builds _inside_ the Brick, and the AG ensures correctness.

---

## 6. Alignment Between Intent, Code, and Tests

The AG (Alignment Graph) allows us to compute alignment and drift.

### 6.1 Brick → Intent Alignment

Questions the AG checks:
- Does every Intent node belong to a Brick?
- Does every Brick implement the Intent it claims?
- Are there Intent nodes with no implementation?
- Are there Intent nodes with no tests?

### 6.2 Brick → Code Alignment

Checks include:
- Does the code of the Brick actually implement the Intent?
- Are there code nodes assigned to the Brick but unrelated to its responsibilities?
- Does code inside this Brick call internal code of other Bricks? (violation)
- Does code escape Brick boundaries?

### 6.3 Brick → Test Alignment

Checks include:
- Are all Intent nodes verified by tests?
- Are all code nodes covered by tests?
- Do tests from this Brick leak into other Bricks?
- Are there tests with no Brick? (orphan tests)

This forms Brick-level "health scores."

---

## 7. Drift Detection

Using the Alignment Graph, we automatically detect:

### Architectural Drift
Brick boundaries violated, interfaces ignored, coupling increased.

### Intent Drift
Specs not implemented; Outcomes not achieved.

### Test Drift
Tests misaligned with Intent or code.

### Dependency Drift
Unexpected edges in the call graph.

Drift becomes objectively measurable, not guesswork.

---

## 8. Why Bricks Work (Human Side)

Humans think at the level of:
- responsibility
- abstraction
- architecture
- boundaries

Bricks give humans a **clear, manageable unit** to reason about:
- bigger than a file
- smaller than a subsystem
- meaningful
- composable
- intentional

They act as the **cognitive scaffolding** for both design and evolution.

---

## 9. Why Bricks Work (Agent Side)

Agents work best with:
- confined context windows
- deterministic boundaries
- clear responsibilities
- unambiguous constraints

Bricks give the agent exactly that.

A Brick:
- declares its own context
- loads only what it needs
- forbids all else
- provides clear Intent and tests
- enforces local correctness

This drastically improves:
- predictability
- quality
- alignment
- test coverage
- architectural integrity

Bricks are the missing abstraction layer for AI-based software development.

---

## 10. Historical Lineage

Bricks inherit ideas from:
- **Parnas information hiding (1972)**
- **DDD bounded contexts**
- **Microservice autonomy & API contracts**
- **Component-and-connector architectures**
- **Clean Architecture boundary rules**
- **Nearly Decomposable Systems (Herbert Simon)**

But Bricks go further by:
- being **machine-enforced** via the Alignment Graph
- coupling intent → code → tests in a single structure
- providing explicit context fences for LLM agents
- being small enough to work inside a codebase
- supporting automated drift detection

Bricks transform architecture from documentation to **live reality**.

---

## 11. Benefits

### For Humans
- clarity of design
- explicit boundaries
- clean mental models
- simple collaboration
- reduced cognitive load

### For Agents
- less noise
- fewer hallucinations
- safer edits
- fewer unintended side-effects
- simpler state spaces
- easier verification

### For the System
- reduced drift
- higher reliability
- meaningful tests
- self-healing architecture
- explicit traceability (Intent → Implementation → Verification)

---

## 12. Final Summary

**The Alignment Graph** is the unified structure that ties together:
- _what we want_ (Intent)
- _what we built_ (Code)
- _what we tested_ (Verification)
- _how it's shaped_ (Bricks)

**Bricks** are the architectural units that:
- give humans the right level of design abstraction
- give agents the right size of context
- enforce correctness and boundaries
- preserve architecture over time

Together, they create the world's first truly **agent-compatible software architecture model**.

A model that can evolve with intent, maintain alignment, and stay understandable — even as code grows and agents do more of the implementation work.
