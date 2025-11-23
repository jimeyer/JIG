# Understanding Alignment Graphs and Bricks

_A personal re-explanation of the core concepts_

---

## The Fundamental Problem

Software development has a **three-body problem**.

We operate simultaneously in three different realities:

1. **The world of intention** - what we're trying to accomplish, the problems we're solving, the constraints we must satisfy
2. **The world of implementation** - the actual code we write, the dependencies we create, the structure that emerges
3. **The world of verification** - what we actually test, what coverage we achieve, what confidence we earn

Traditional development treats these as separate concerns:
- Intentions live in documents, tickets, and minds
- Implementation lives in source files and repositories
- Verification lives in test suites and CI pipelines

The problem? **These three realities drift apart constantly.**

You intend to build feature X. You actually build something that's 80% of X plus unintended side effect Y. Your tests verify 60% of what you built and 40% of what you intended. Six months later, nobody knows what was meant, what exists, or what's actually verified.

This is the **alignment crisis** at the heart of software evolution.

---

## The Alignment Graph: A Unified Reality

The **Alignment Graph** is a radical proposal: **make all three realities visible in a single, queryable structure.**

It's not a diagram. It's not documentation. It's a **living semantic graph** that represents:

- **What you said you wanted** (Intent Layer: Outcomes, Specifications, architectural Bricks)
- **What you actually built** (Dependency Layer: functions, classes, modules, call graphs, import relationships)
- **What you actually verify** (Test Layer: test functions, coverage maps, verification traces)

The graph is **machine-generated** from observable facts:
- Intent nodes from JIG declarations
- Code nodes from static analysis and dependency extraction
- Test nodes from pytest discovery and coverage analysis
- Brick assignments from architectural definitions

The graph is **machine-readable** so tools can query it:
- "Which Intent nodes have no implementation?"
- "Which code calls across Brick boundaries illegally?"
- "Which Specifications lack test coverage?"

The graph is **human-inspectable** so architects can see truth:
- "Where is the system drifting from design?"
- "What unintended dependencies have emerged?"
- "Which tests are orphaned from Intent?"

### Why This Matters

The Alignment Graph makes **drift visible and measurable** instead of invisible and assumed.

It answers questions that are currently hard or impossible:
- "Does our implementation actually match our design?"
- "Are we testing what matters?"
- "Where is technical debt accumulating?"
- "What will break if I change this?"

It does this not through documentation (which lies) but through **observation of ground truth.**

---

## Bricks: The Architectural Quantum

If the Alignment Graph is the measurement system, **Bricks** are the units of measure.

A Brick is:

**An architectural unit that encloses intention, implementation, and verification in a single boundary.**

Think of it this way: files are too small, subsystems are too big, and packages are implementation artifacts. We need something that:
- Corresponds to how humans think about design
- Provides a natural scope for agent work
- Enforces meaningful boundaries
- Ties together "why", "what", and "how"

That's a Brick.

### What Makes a Good Brick?

A Brick is like a **cell membrane** - it has a clear inside, a clear outside, and controlled exchange between them.

**Inside the Brick:**
- The Intent nodes this Brick is responsible for
- The code implementing those intentions
- The tests verifying those implementations
- The internal dependencies and relationships

**Outside the Brick:**
- Other Bricks (only their public interfaces visible)
- The broader system context
- Global concerns and infrastructure

**The Membrane:**
- Explicit interface contracts (what this Brick exposes)
- Declared dependencies (which other Bricks this one may use)
- Responsibility boundaries (what's in scope, what's not)

### Bricks as Context Boundaries

Here's where it gets interesting for **agent-based development**.

When an AI agent works on a system, it faces an impossible choice:
- See everything → get overwhelmed, distracted, make unintended changes
- See too little → miss critical context, break dependencies, create bugs

Bricks solve this by providing **the right-sized context**.

When an agent works inside a Brick, it sees:
- Everything inside this Brick (Intent, code, tests)
- The interfaces of neighboring Bricks (public contracts only)
- Nothing else (no internals of other Bricks, no global noise)

This creates a **clean room** where the agent can reason locally, implement confidently, and test thoroughly - without accidentally refactoring half the codebase.

### Two Operating Modes

The Brick model enables two distinct modes of work:

**1. Architecture Mode** - designing the system structure
- See: all Brick definitions, interfaces, Intent, dependency relationships
- Don't see: any implementation details, code, tests, file structure
- Purpose: design and reshape architectural boundaries without implementation noise

**2. Implementation Mode** - building inside a Brick
- See: this Brick's Intent, code, tests, neighbor interfaces
- Don't see: anything outside this Brick's boundary
- Purpose: implement safely within architectural constraints

This separation is powerful. You can redesign architecture without drowning in code details. You can implement features without accidentally violating architectural boundaries.

---

## Alignment Checking: The Health Monitor

With the Alignment Graph and Bricks in place, you can now **measure alignment** across three dimensions:

### Intent ↔ Code Alignment
- Does every Intent node have implementing code?
- Does every Brick's code serve its declared Intent?
- Is there "orphan code" unrelated to any Intent?

### Intent ↔ Test Alignment
- Is every Specification verified by tests?
- Does every Outcome have test coverage?
- Are there Intent nodes we assume work but never verify?

### Code ↔ Architecture Alignment
- Does code stay within Brick boundaries?
- Are there illegal dependencies crossing boundaries?
- Do actual call graphs match intended architecture?

When these alignments break down, you have **drift**:
- **Intent drift** - we're building something other than what we planned
- **Architecture drift** - structure is eroding from design
- **Test drift** - verification doesn't match Intent or implementation

The Alignment Graph makes drift **objectively detectable**, not a matter of opinion.

---

## Why This Approach Works

### For Humans
Bricks operate at the **right level of abstraction**:
- Bigger than thinking about individual functions
- Smaller than thinking about entire subsystems
- Aligned with how we naturally partition responsibility
- Make architectural decisions explicit and visible

### For Agents
Bricks provide the **right constraints**:
- Confined, deterministic context (reduces hallucination)
- Clear responsibilities (reduces scope confusion)
- Enforced boundaries (prevents architectural erosion)
- Intent + Tests present (enables verification)

### For the System
The Alignment Graph provides **continuous truth**:
- No documentation can drift from reality (it IS reality)
- Drift is detected automatically
- Architectural integrity is enforced by tooling
- Evolution is guided by measured alignment

---

## The Deeper Insight

Here's what I think is most profound about this model:

**Traditional architecture is descriptive.** You draw boxes and lines, write documents, explain patterns. But the code evolves independently. The architecture becomes a beautiful lie.

**Alignment Graph + Bricks make architecture prescriptive and verifiable.**

The architecture isn't separate from the system - it's **derived from** and **enforced within** the system. The graph observes what exists. The Bricks define what should exist. The alignment check reveals where reality deviates from design.

This shifts architecture from **aspiration** to **mechanism**.

You're not documenting the design you hope exists. You're defining boundaries that are enforced, checking alignments that are measured, and detecting drift that is quantified.

---

## Historical Context

This isn't entirely new. It inherits ideas from:
- **Information hiding** (Parnas, 1972) - modules with clear boundaries
- **Domain-Driven Design** - bounded contexts with explicit relationships
- **Clean Architecture** - dependency rules and boundary enforcement
- **Microservices** - independent deployable units with API contracts

But Bricks + Alignment Graph add critical innovations:

1. **Machine enforcement** - boundaries aren't guidelines, they're validated
2. **Tri-fold binding** - Intent, Implementation, and Verification bound together
3. **Agent context fencing** - explicit scoping for AI development
4. **Continuous drift detection** - alignment measured constantly, not assumed
5. **Operational at code level** - works inside a codebase, not just at service boundaries

This makes architectural integrity **achievable at scale**, even with AI agents doing much of the implementation work.

---

## Summary

**The Alignment Graph** sees the system as it truly is - what we intended, what we built, what we verified - in a single unified structure.

**Bricks** are the architectural units that group these three realities into bounded, enforceable, human-meaningful chunks.

Together, they solve the alignment crisis by:
- Making drift visible
- Enforcing boundaries
- Providing the right context for both human designers and AI implementers
- Keeping architecture alive and true as code evolves

This is architecture for the age of agent-assisted development.

A way to preserve human design intent while leveraging AI execution capability.

A way to know - not hope, but **know** - that what you built matches what you meant, and what you verified covers what matters.

---

_This is my understanding. The original document contains more precise definitions, formal contracts, and implementation details. This is the conceptual core as I understand it._
