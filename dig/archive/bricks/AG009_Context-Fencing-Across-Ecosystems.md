---
title: "Context Fencing Across Ecosystems"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1764019099
created_human: "2025-11-24 15:18 CST"
parent: "[[AG001_Alignment-Graph-Bricks]]"
children: []
---
# Context Fencing Across Ecosystems

_How Software Architectures Manage Cognitive Boundaries—And Why Bricks Are Different_

**Date:** 2025-11-24
**Status:** Analysis
**Author:** Claude + Jim Meyer

---

## Executive Summary

**Context fencing**—the practice of creating bounded, comprehensible units of work—is not new. It appears across every mature software ecosystem under different names:

- **Rust**: Workspaces and crates
- **Go**: Modules and packages
- **Java**: Multi-module Maven/Gradle projects
- **JavaScript/TypeScript**: Nx libraries and monorepo tooling
- **Domain-Driven Design**: Bounded contexts
- **Microservices**: Service boundaries

Each emerged from **real pain**: build times, dependency hell, team coordination, cognitive overload.

**What's novel about Bricks:** They're the first architectural pattern explicitly designed for **human-AI collaboration**. Other patterns optimize for human teams or build systems. Bricks optimize for **dual cognition**—both human architects and AI agents working within the same bounded contexts.

This document:
1. Analyzes context fencing motivations across ecosystems
2. Compares enforcement mechanisms and trade-offs
3. Identifies what makes Bricks unique
4. Extracts lessons for the Alignment Graph

**Key Finding:** Context fencing has evolved through four eras:
1. **1970s-80s**: Modularity for human understanding (Parnas, modularity)
2. **1990s-2000s**: Packaging for distribution (libraries, packages)
3. **2010s**: Build efficiency and team scaling (monorepos, microservices)
4. **2020s**: **AI agent safety and token budgets** ← We are here

---

## 1. The Universal Problem: Cognitive Complexity

### 1.1 The Human Limit

Humans can hold ~7 items in working memory (Miller, 1956). Complex software has thousands to millions of elements.

**The cognitive gap:**
- Small program: 500 lines, 10 functions → Comprehensible
- Medium program: 5,000 lines, 100 functions → Challenging
- Large program: 500,000 lines, 10,000 functions → **Incomprehensible without structure**

**Solution:** Create **bounded contexts** that fit in human working memory.

### 1.2 The AI Limit

LLMs have context windows (100K-1M tokens). Complex software repositories exceed this.

**The token gap:**
- Small project: 5K LOC ≈ 100K tokens → Fits in context
- Medium project: 50K LOC ≈ 1M tokens → Marginal
- Large project: 500K LOC ≈ 10M tokens → **Impossible to load fully**

Additionally:
- **Attention degradation**: Quality drops with context length
- **Hallucination risk**: More noise → more fabrication
- **Latency cost**: Larger context → slower inference
- **Relevance ratio**: 95% of codebase irrelevant to any given task

**Solution:** Create **context boundaries** that fit in token budgets.

### 1.3 The Shared Challenge

Both humans and AI need:
1. **Selective visibility** - See only what's relevant
2. **Clear boundaries** - Know what's in/out of scope
3. **Explicit interfaces** - Understand dependencies without seeing implementations
4. **Cognitive anchors** - Stable structures to reason about
5. **Compositional thinking** - Build understanding from parts to wholes

**Context fencing is the solution to cognitive limits.**

---

## 2. Context Fencing Across Ecosystems

### 2.1 Rust: Workspaces and Crates

**Structure:**
```
my-project/
├── Cargo.toml              # Workspace manifest
└── crates/
    ├── core/
    │   ├── Cargo.toml      # Crate manifest
    │   ├── src/
    │   └── tests/
    ├── api/
    │   ├── Cargo.toml
    │   ├── src/
    │   └── tests/
    └── cli/
        ├── Cargo.toml
        ├── src/
        └── tests/
```

**What is the boundary unit?**
The **crate** - a compilation unit with explicit dependencies.

**What motivated it?**
1. **Compilation speed** - Large projects (rustc, Servo) had 30+ minute builds
2. **Incremental builds** - Only recompile changed crates
3. **Semantic versioning** - Each crate can have independent versions
4. **Code reuse** - Crates can be libraries for multiple projects

**How is it enforced?**
- **Compiler:** Type system enforces crate boundaries
- **Module system:** `pub` visibility controls exports
- **Cargo.toml:** Explicit dependency declarations
- **Ownership:** Borrow checker prevents invalid cross-crate access

**What can you see inside a crate boundary?**
- All source files in the crate
- Type signatures of dependencies
- Public interfaces only (no private implementation)

**Strengths:**
- ✅ **Compile-time enforcement** - Impossible to violate boundaries
- ✅ **Type safety** - Incorrect usage won't compile
- ✅ **Incremental builds** - Fast iteration
- ✅ **Clear semantics** - Ownership rules extend to crates

**Weaknesses:**
- ⚠️ Compilation-focused, not cognitive-focused
- ⚠️ No intent modeling (no "why" for crate structure)
- ⚠️ Crate granularity can be too coarse (or too fine)

**Context fencing grade: A**
Strong technical enforcement, clear boundaries, but no architectural intent layer.

---

### 2.2 Go: Modules and Packages

**Structure:**
```
my-project/
├── go.mod                  # Module manifest
├── graph/
│   ├── graph.go
│   ├── graph_test.go
│   └── relationships.go
├── parser/
│   ├── parser.go
│   └── parser_test.go
└── cli/
    ├── main.go
    └── commands_test.go
```

**What is the boundary unit?**
The **package** - a directory of `.go` files with a single package declaration.

**What motivated it?**
1. **Dependency hell** - Pre-Go modules had no version management
2. **Simplicity** - Python/JS packaging is complex, Go wanted better
3. **Build reproducibility** - `go.mod` locks dependencies
4. **Import clarity** - Full import paths make dependencies obvious

**How is it enforced?**
- **go.mod file:** Declares dependencies and versions
- **Import paths:** Explicit, verifiable references
- **Package names:** Single namespace per directory
- **Visibility:** Capitalized = public, lowercase = private

**What can you see inside a package boundary?**
- All files in the package (including private functions)
- Exported symbols from dependency packages
- Tests live *next to* code (`_test.go` suffix)

**Strengths:**
- ✅ **Extreme simplicity** - One directory = one package
- ✅ **Co-located tests** - No cognitive distance
- ✅ **Clear imports** - Full paths, no ambiguity
- ✅ **Fast builds** - Packages are small compilation units

**Weaknesses:**
- ⚠️ No architectural layer above packages
- ⚠️ No explicit interfaces (structural typing only)
- ⚠️ Package granularity debates (big vs small)
- ⚠️ No subsystem or brick-like concept

**Context fencing grade: B+**
Simple, clear, but lacks higher-order architectural structures.

---

### 2.3 Java: Maven Multi-Module Projects

**Structure:**
```
my-project/
├── pom.xml                 # Parent POM
├── core/
│   ├── pom.xml             # Module POM
│   └── src/
│       ├── main/java/
│       └── test/java/
├── api/
│   ├── pom.xml
│   └── src/
│       ├── main/java/
│       └── test/java/
└── cli/
    ├── pom.xml
    └── src/
        ├── main/java/
        └── test/java/
```

**What is the boundary unit?**
The **module** - a Maven/Gradle subproject with its own build lifecycle.

**What motivated it?**
1. **Enterprise scale** - Large organizations with 100+ module projects
2. **Team coordination** - Different teams own different modules
3. **Release independence** - Modules can have different release cycles
4. **Dependency management** - Maven Central, transitive dependencies
5. **Build lifecycle control** - Each module can have different build steps

**How is it enforced?**
- **POM files:** Explicit dependency declarations
- **Java module system (JPMS):** Module-info.java declares exports
- **Maven reactor:** Builds modules in dependency order
- **Classpath isolation:** Modules don't see each other unless declared

**What can you see inside a module boundary?**
- All source in `src/main/java`
- All tests in `src/test/java`
- Public classes from dependency modules
- No internal implementation details of dependencies

**Strengths:**
- ✅ **Mature tooling** - Maven/Gradle widely understood
- ✅ **Enterprise proven** - Scales to very large orgs
- ✅ **Lifecycle control** - Each module can have custom build
- ✅ **Clear ownership** - Modules map to teams

**Weaknesses:**
- ⚠️ **Complexity** - POMs are verbose, inheritance is confusing
- ⚠️ **Slow builds** - JVM startup overhead per module
- ⚠️ **Circular dependencies** - Easy to create accidentally
- ⚠️ No intent modeling (modules are technical, not semantic)

**Context fencing grade: B**
Strong for enterprise coordination, but heavy and complex.

---

### 2.4 Nx Monorepo (TypeScript/JavaScript)

**Structure:**
```
my-project/
├── nx.json                 # Nx configuration
├── apps/
│   └── cli/
│       └── src/
└── libs/
    ├── graph/
    │   ├── src/
    │   ├── test/
    │   └── project.json    # Lib configuration
    ├── parser/
    │   ├── src/
    │   ├── test/
    │   └── project.json
    └── utils/
        ├── src/
        ├── test/
        └── project.json
```

**What is the boundary unit?**
The **library** - an Nx project with its own build/test/lint configuration.

**What motivated it?**
1. **Code reuse without duplication** - Share code across apps
2. **Affected tests** - Only test what changed (dependency graph analysis)
3. **Computational caching** - Cache build/test results per library
4. **Monorepo management** - Large monorepos (Google, Facebook) need tooling
5. **Build optimization** - Parallel builds, incremental builds

**How is it enforced?**
- **Nx tooling:** Understands project.json and dependency graph
- **Lint rules:** Can enforce module boundaries via ESLint
- **Import restrictions:** Tags + eslint rules restrict imports
- **Dependency graph:** Nx builds and visualizes the graph

**What can you see inside a library boundary?**
- All source in the library
- All tests in the library
- Public exports from dependency libraries
- Nx generates barrel files (`index.ts`) to control exports

**Strengths:**
- ✅ **Dependency graph analysis** - First-class concern
- ✅ **Affected detection** - Only test changed code
- ✅ **Caching** - Reuse build results across CI runs
- ✅ **Visualization** - `nx graph` shows dependencies
- ✅ **Lint enforcement** - Can block boundary violations

**Weaknesses:**
- ⚠️ **Tooling dependency** - Must use Nx (vendor lock-in)
- ⚠️ **JavaScript/TypeScript only** - Not cross-language
- ⚠️ No intent layer (libraries are technical units)
- ⚠️ Module boundaries are conventions, not hard rules

**Context fencing grade: A-**
Excellent tooling and DX, but JavaScript-specific and no architectural intent.

---

### 2.5 Domain-Driven Design: Bounded Contexts

**Structure:**
```
(Conceptual, not file-based)

Contexts:
├── Catalog Context
│   ├── Product (entity)
│   ├── Category (entity)
│   └── Search (service)
│
├── Ordering Context
│   ├── Order (entity)
│   ├── LineItem (value object)
│   └── Checkout (aggregate root)
│
└── Shipping Context
    ├── Shipment (entity)
    ├── Carrier (entity)
    └── Tracking (service)

Context Map:
  Catalog --[Conformist]--> Ordering
  Ordering --[Anti-corruption]--> Shipping
```

**What is the boundary unit?**
The **bounded context** - a semantic boundary where domain terms have specific meanings.

**What motivated it?**
1. **Domain complexity** - Enterprise software models complex real-world domains
2. **Linguistic ambiguity** - Same word means different things in different parts of business
3. **Team autonomy** - Different teams need different models
4. **Model integrity** - Prevent model pollution across contexts
5. **Evolution** - Contexts can evolve independently

**How is it enforced?**
- **Ubiquitous language** - Each context has its own vocabulary
- **Context maps** - Explicit relationships between contexts
- **Anti-corruption layers** - Translation layers at boundaries
- **Aggregate boundaries** - Transactions stay within aggregates
- **Separate schemas** - Different databases per context (often)

**What can you see inside a bounded context boundary?**
- All entities, value objects, aggregates in the context
- Domain events published by the context
- Services within the context
- **Only interfaces** of other contexts (via anti-corruption layers)

**Strengths:**
- ✅ **Semantic clarity** - Terms have precise meanings
- ✅ **Model integrity** - No pollution across contexts
- ✅ **Team autonomy** - Contexts owned by teams
- ✅ **Evolution** - Contexts can change independently
- ✅ **Linguistic boundaries** - Prevents conceptual drift

**Weaknesses:**
- ⚠️ **Not technical** - DDD is a pattern, not a tool
- ⚠️ **Hard to enforce** - Relies on discipline, not automation
- ⚠️ **Ambiguous boundaries** - Where does one context end?
- ⚠️ **Translation overhead** - Anti-corruption layers add complexity

**Context fencing grade: A (conceptual), C (practical)**
Brilliant conceptually, but hard to enforce without tooling.

---

### 2.6 Microservices: Service Boundaries

**Structure:**
```
(Distributed system)

Services:
├── product-catalog-service
│   ├── API (REST/gRPC)
│   ├── Database (PostgreSQL)
│   └── Codebase (independent repo)
│
├── order-service
│   ├── API (REST/gRPC)
│   ├── Database (MongoDB)
│   └── Codebase (independent repo)
│
└── shipping-service
    ├── API (REST/gRPC)
    ├── Database (MySQL)
    └── Codebase (independent repo)

Network boundaries enforce separation
```

**What is the boundary unit?**
The **service** - an independently deployable process with its own codebase and data.

**What motivated it?**
1. **Independent deployment** - Change one service without redeploying others
2. **Team autonomy** - Teams own entire services (code, data, infrastructure)
3. **Technology diversity** - Each service can use different tech stack
4. **Scalability** - Scale services independently
5. **Fault isolation** - One service failure doesn't crash others

**How is it enforced?**
- **Network boundaries** - Physical separation via network
- **API contracts** - REST/gRPC/GraphQL interfaces
- **Separate deployments** - Each service deployed independently
- **Database per service** - No shared databases
- **Service mesh** - Infrastructure enforces boundaries (Istio, Linkerd)

**What can you see inside a service boundary?**
- All code in the service
- Service's private database
- API definitions of other services
- **No implementation** of other services

**Strengths:**
- ✅ **Strongest enforcement** - Network boundaries are hard
- ✅ **True independence** - Services can be in different languages
- ✅ **Clear ownership** - Services map to teams
- ✅ **Scalability** - Independent scaling

**Weaknesses:**
- ⚠️ **Operational complexity** - Distributed systems are hard
- ⚠️ **Network latency** - Cross-service calls are slow
- ⚠️ **Data consistency** - Eventual consistency challenges
- ⚠️ **Debugging** - Distributed tracing required
- ⚠️ **Overhead** - Too fine-grained = too many services

**Context fencing grade: A+ (enforcement), C (complexity)**
Strongest boundaries, but at the cost of massive operational complexity.

---

## 3. Comparison Matrix

| Pattern | Boundary Unit | Primary Motivation | Enforcement | Cognitive Focus | Agent-Aware |
|---------|--------------|-------------------|-------------|----------------|-------------|
| **Rust Crates** | Crate | Build speed, type safety | Compiler (strong) | Low (technical) | No |
| **Go Packages** | Package | Simplicity, versioning | Import system (medium) | Medium (simple) | No |
| **Java Modules** | Module | Enterprise scale, teams | Maven/POM (medium) | Low (technical) | No |
| **Nx Libraries** | Library | Build caching, affected tests | Tooling + lint (medium) | Medium (tooling) | No |
| **DDD Contexts** | Bounded Context | Domain complexity, semantics | Discipline (weak) | **High (semantic)** | No |
| **Microservices** | Service | Deployment independence | Network (strongest) | Medium (distributed) | No |
| **Bricks** | **Brick** | **AI safety + human clarity** | **Intent graph + tooling** | **High (semantic + technical)** | **Yes** |

**Key observations:**

1. **Technical vs. Semantic:**
   - Most patterns are **technical** (crates, modules, packages)
   - DDD is **semantic** (domain-driven)
   - **Bricks are both** (semantic intent + technical enforcement)

2. **Enforcement strength:**
   - Compile-time (Rust) > Runtime (Microservices) > Tooling (Nx) > Discipline (DDD)
   - **Bricks use multiple layers** (intent graph + validation + social contracts)

3. **Cognitive focus:**
   - Most optimize for **build systems** or **team coordination**
   - DDD optimizes for **domain understanding**
   - **Bricks optimize for dual cognition** (humans + AI)

4. **Agent awareness:**
   - **Zero existing patterns designed for AI agents**
   - Bricks are the first to explicitly consider token budgets and hallucination risk

---

## 4. What Makes Bricks Unique

### 4.1 Dual Audience: Humans AND Agents

**Traditional patterns:**
- Designed for human developers
- Compilers/build tools are means to an end
- Agent usage is incidental

**Bricks:**
- **Explicitly designed for human-AI collaboration**
- Agents are first-class citizens
- Context boundaries serve both audiences

**Why this matters:**

| Concern | Human Need | Agent Need | Brick Solution |
|---------|-----------|-----------|----------------|
| **Scope** | Manageable cognitive load | Token budget | Brick = ~500 LOC context |
| **Clarity** | Understand responsibility | Reduce hallucination | Explicit intent nodes (O/S) |
| **Safety** | Prevent accidental coupling | Prevent scope creep | Boundary enforcement |
| **Focus** | Work on one thing at a time | Relevant context only | Brick Context Contract |
| **Verification** | Know what to test | Alignment checking | Intent ↔ Code ↔ Test graph |

**Bricks serve both audiences with the same structure.**

---

### 4.2 Intent as First-Class Citizen

**Traditional patterns:**
- Intent lives in docs, comments, conversations
- Code and intent drift apart over time
- No machine-readable representation

**Bricks:**
- Every Brick has **explicit intent nodes** (Outcomes, Specifications)
- Intent is **machine-readable** (YAML frontmatter + Markdown)
- Intent ↔ Code alignment is **computed and verified**

**Example:**

```yaml
# Traditional (Go package)
package graph

// Graph provides efficient graph data structures and queries
type Graph struct { ... }

# Brick (Alignment Graph)
Brick: BRICK-GRAPH
Intent:
  - O-GRAPH-001: "Fast graph queries (<100ms for 10K nodes)"
  - S-GRAPH-001: "Use NetworkX for graph algorithms"
  - S-GRAPH-002: "Support nested subsystems"

Code: src/jig/core/graph.py
Tests: tests/unit/test_graph*.py

Alignment: intent → code → tests (verified)
```

**Why this matters:**
- **Drift detection:** Can measure when code diverges from intent
- **Agent guidance:** Agent sees WHY it's building something
- **Verification:** Tests explicitly tied to specs
- **Architecture visibility:** Intent graph shows system design

---

### 4.3 Multi-Layer Context Boundaries

**Traditional patterns:**
- Single enforcement mechanism (compiler, imports, network)

**Bricks:**
- **Layer 1:** Brick definitions (declare boundaries)
- **Layer 2:** Context loaders (pre-load allowed context)
- **Layer 3:** Tool wrappers (runtime enforcement, future)
- **Layer 4:** Validation (post-work verification)

**Why multiple layers?**
- No single layer is perfect
- Social + technical + validation = strongest fencing
- Gradual enforcement (can start with just definitions)

---

### 4.4 Alignment Graph Integration

**Traditional patterns:**
- Boundaries exist in code/build systems
- No unified view of intent ↔ implementation ↔ verification

**Bricks:**
- Part of the **Alignment Graph**
- Graph shows: intent layer, dependency layer, test layer, **brick layer**
- Can query: "Which bricks implement O-GRAPH-001?" "Which tests verify this brick?"

**The Alignment Graph enables:**
- Automated drift detection
- Cross-brick impact analysis
- Architectural health metrics
- Intent traceability

**This is novel.** No other ecosystem has unified intent + code + tests + architecture in a single graph.

---

### 4.5 Cognitive Safety for Agents

**The AI-specific problem:**

Traditional codebases overwhelm agents:
- 10,000+ files in context → confusion
- See irrelevant code → hallucinations
- No clear boundaries → scope creep
- No explicit constraints → architectural violations

**Brick solution:**

```
Agent Context (Brick Mode):
├── Brick definition          ~50 lines   (what/why)
├── Intent nodes              ~200 lines  (requirements)
├── Brick source code         ~500 lines  (implementation)
├── Brick tests               ~300 lines  (verification)
└── Dependency interfaces     ~100 lines  (what I can use)
                              ─────────
Total context:                ~1,150 lines (~30K tokens)

Compare to full repo:         ~50,000 lines (~1.2M tokens)
```

**The agent sees:**
- 2% of the codebase
- 100% of what it needs
- 0% of what it shouldn't touch

**Result:**
- ✅ Focused reasoning
- ✅ Lower hallucination rate
- ✅ Faster inference
- ✅ Better quality output
- ✅ Architectural safety

**No other pattern optimizes for this.**

---

## 5. Lessons from Other Ecosystems

### 5.1 From Rust: Compile-Time Enforcement

**Rust lesson:** The compiler catches violations before runtime.

**Applied to Bricks:**
- **Intent graph validation** is like type checking
- Brick boundaries can be validated statically
- `jigy brick validate` = "compile-time" check
- CI fails if boundaries violated

**Takeaway:** Static checks > runtime checks > no checks.

---

### 5.2 From Go: Radical Simplicity

**Go lesson:** Simple patterns win. One directory = one package. No cleverness.

**Applied to Bricks:**
- Brick definition should be **simple** (.brick.yaml, not complex DSL)
- One brick = one logical unit (not fractal, not nested)
- Clear naming (BRICK-GRAPH, not abstract IDs)
- Tools should be obvious (`jigy brick load`, not arcane commands)

**Takeaway:** Complexity is the enemy. Keep Bricks simple.

---

### 5.3 From Java: Explicit Metadata

**Java lesson:** Explicit declarations (POMs) beat implicit conventions.

**Applied to Bricks:**
- **Declare dependencies** (don't infer)
- **Declare interfaces** (don't guess)
- **Declare intent** (don't assume)
- Make everything explicit in `.brick.yaml`

**Takeaway:** Explicit is better than implicit.

---

### 5.4 From Nx: Dependency Graph as First-Class Citizen

**Nx lesson:** Visualizing the graph matters. Affected detection matters.

**Applied to Bricks:**
- **Alignment Graph** should be visualizable
- `jigy graph show --bricks` should render brick dependencies
- "What bricks are affected by this change?" is a first-class query
- Brick health should be tracked over time

**Takeaway:** Make the graph visible and queryable.

---

### 5.5 From DDD: Semantic Boundaries Matter

**DDD lesson:** Technical boundaries aren't enough. Semantic boundaries (bounded contexts) prevent model pollution.

**Applied to Bricks:**
- Bricks should have **semantic cohesion** (not just technical grouping)
- Each brick has a **responsibility** (like DDD contexts have ubiquitous language)
- Intent nodes provide semantic meaning
- Brick != package (bricks are architectural, packages are technical)

**Takeaway:** Semantics > syntax. Bricks are meaning, not just files.

---

### 5.6 From Microservices: Strong Boundaries Have Costs

**Microservices lesson:** Network boundaries are the strongest, but operational complexity is crushing.

**Applied to Bricks:**
- **Don't over-fence** - Bricks aren't microservices
- Bricks live in one codebase (monorepo)
- Shared language runtime (Python)
- No network latency, no distributed debugging
- **Just-enough boundaries** for clarity, not for deployment

**Takeaway:** Strong boundaries have costs. Optimize for development clarity, not deployment independence.

---

## 6. The Evolution of Context Fencing

### 6.1 Four Eras

| Era | Primary Concern | Pattern | Enforcement | Example |
|-----|----------------|---------|-------------|---------|
| **1970s-80s** | Human understanding | Modules, information hiding | Discipline | Parnas (1972) |
| **1990s-2000s** | Code distribution | Packages, libraries | Import systems | PyPI, Maven Central |
| **2010s** | Build efficiency & teams | Monorepos, microservices | Tooling / network | Nx, Kubernetes |
| **2020s** | **AI collaboration** | **Bricks** | **Intent graph** | **JIG Alignment Graph** |

### 6.2 What Changed in Each Era

**Era 1: Information Hiding (1972)**
- **Problem:** Growing programs becoming incomprehensible
- **Solution:** Modules with defined interfaces (Parnas)
- **Insight:** Hide design decisions behind interfaces
- **Limitation:** Discipline-based, no tooling

**Era 2: Package Distribution (1990s)**
- **Problem:** Code reuse across projects
- **Solution:** Package managers (CPAN, PyPI, npm)
- **Insight:** Versioning + namespaces + distribution
- **Limitation:** No intra-project structure

**Era 3: Build Optimization (2010s)**
- **Problem:** Large monorepos with slow builds
- **Solution:** Incremental builds, affected tests, caching (Bazel, Nx)
- **Insight:** Dependency graphs enable smart builds
- **Limitation:** Focused on machines (build systems), not humans

**Era 4: AI Collaboration (2020s)**
- **Problem:** AI agents overwhelmed by codebases, hallucinate, violate architecture
- **Solution:** **Bricks with intent graphs and context boundaries**
- **Insight:** Cognitive limits apply to both humans AND agents
- **Novel:** Intent as first-class, dual-audience design

---

## 7. Why Context Fencing Matters More Now

### 7.1 The Shift to Agent-Augmented Development

**2020s trend:** AI agents (Claude Code, Copilot, Cursor) write significant portions of code.

**Traditional assumptions broken:**
- "Developers understand the full system" → Agents don't
- "Code review catches violations" → Too late for agents
- "Docs explain architecture" → Agents don't read docs well
- "Good judgment prevents bad changes" → Agents lack judgment

**New reality:**
- Agents need **explicit constraints**, not implicit knowledge
- Architecture must be **machine-readable**, not just human-readable
- Boundaries must be **enforced**, not suggested
- Intent must be **explicit**, not inferred

**Bricks provide this.**

---

### 7.2 The Token Budget Crisis

**Context windows are finite:**
- GPT-4: ~128K tokens
- Claude 3.5 Sonnet: ~200K tokens
- Gemini 1.5: ~1M tokens (but attention degrades)

**A medium Python project:**
- 50K LOC ≈ 1M tokens (with docs, tests, etc.)
- **Can't fit in any current context window**

**Traditional approach:** Load everything, hope agent figures it out.
**Result:** Noise, distraction, hallucination, slow inference.

**Brick approach:** Load only the relevant brick (~1K LOC, ~30K tokens).
**Result:** Focused, fast, accurate.

**Token budgets force better architecture.**

---

### 7.3 The Alignment Problem

**Software alignment problem:**
- Intent → Implementation → Verification should align
- In practice, they drift apart
- Docs go stale, tests become obsolete, code evolves

**Traditional solution:** Discipline, code review, documentation.
**Problem:** Doesn't scale, isn't verified.

**Brick solution:**
- Intent nodes are **machine-readable**
- Alignment Graph **computes** alignment
- Drift is **measured** (not guessed)
- CI **fails** if alignment breaks

**This is a paradigm shift:**
- From documentation to **data**
- From review to **verification**
- From implicit to **explicit**

---

## 8. What Bricks Don't Try to Be

### 8.1 Not a Deployment Boundary (Unlike Microservices)

Bricks are **development-time boundaries**, not runtime boundaries.

**They don't provide:**
- Independent deployment
- Network isolation
- Separate databases
- Fault isolation

**Why not?**
- Too much operational complexity
- Not necessary for development clarity
- Monorepo benefits (refactoring, consistency, single build)

**Bricks = cognitive boundaries, not deployment boundaries.**

---

### 8.2 Not a Package Manager (Unlike Cargo/Maven)

Bricks are **not** about distributing reusable libraries.

**They don't provide:**
- Versioned packages
- Public registries
- Transitive dependency resolution
- SemVer compatibility checking

**Why not?**
- Solves a different problem (distribution vs. clarity)
- Most projects don't publish all internal modules
- Overhead not worth it for internal structure

**Bricks = architectural units, not packages.**

---

### 8.3 Not a Domain Model (Unlike DDD Bounded Contexts)

Bricks can be **informed by** DDD, but aren't replacements.

**They don't provide:**
- Ubiquitous language enforcement
- Domain event modeling
- Aggregate design
- Strategic design patterns

**Why not?**
- Bricks are more granular (code-level, not domain-level)
- Bricks are technical + semantic, DDD is purely semantic
- Bricks have tooling, DDD is a pattern

**Bricks complement DDD, don't replace it.**

---

### 8.4 Not a Build System (Unlike Bazel/Nx)

Bricks leverage build systems, but aren't one.

**They don't provide:**
- Incremental compilation
- Distributed caching
- Build parallelization
- Target definitions

**Why not?**
- Build systems already exist (pytest, mypy, ruff)
- Bricks focus on **what to build**, not **how to build**
- Orthogonal concerns

**Bricks = architectural structure, build systems = compilation.**

---

## 9. The Brick Philosophy

### 9.1 Core Principles

**1. Cognitive Fidelity**
Physical structure should match mental models.

**2. Explicit Over Implicit**
Declare intent, dependencies, interfaces—don't infer.

**3. Verifiable Alignment**
Intent ↔ Code ↔ Tests should be computable, not assumed.

**4. Dual-Audience Design**
Serve humans AND agents equally.

**5. Just-Enough Boundaries**
Strong enough to matter, light enough to use.

**6. Semantic + Technical**
Combine meaning (intent) with mechanism (code).

**7. Evolve With Intent**
Architecture should be durable but adaptable.

---

### 9.2 When Bricks Work Best

**Strong fit:**
- ✅ AI-augmented development
- ✅ Architectural clarity is valuable
- ✅ Medium to large codebases (5K-500K LOC)
- ✅ Intent-driven design
- ✅ Need to manage drift
- ✅ Agent safety matters

**Weak fit:**
- ⚠️ Tiny projects (<1K LOC)
- ⚠️ Rapid prototyping (unknown architecture)
- ⚠️ No agent usage
- ⚠️ Purely exploratory code

---

## 10. Open Questions and Future Research

### 10.1 Cross-Language Bricks?

**Question:** Can Bricks work in polyglot codebases?

**Challenge:**
- Import systems differ (Python vs. Rust vs. Go)
- Type systems differ (static vs. dynamic)
- Build systems differ (cargo vs. npm vs. maven)

**Hypothesis:**
- Brick **definitions** are language-agnostic (YAML)
- Brick **validation** needs language-specific parsers
- Alignment Graph can unify across languages

**Research needed:** Implement bricks in multi-language monorepo.

---

### 10.2 Dynamic Brick Boundaries?

**Question:** Should bricks be static or dynamic?

**Current:** Bricks defined in `.brick.yaml`, static.

**Alternative:** Bricks inferred from code structure, updated automatically.

**Trade-offs:**
- Static = explicit, stable, human-authored
- Dynamic = adaptive, reflects reality, machine-generated

**Hypothesis:** Hybrid—human defines intent, tooling validates/suggests refinements.

---

### 10.3 Brick Maturity Levels?

**Question:** Should bricks have maturity levels (experimental, stable, deprecated)?

**Analogy:** Kubernetes API groups (alpha, beta, stable)

**Use case:**
- New brick = experimental (interfaces may change)
- Mature brick = stable (SemVer compatibility)
- Old brick = deprecated (migration path needed)

**Research needed:** Define maturity criteria, lifecycle management.

---

### 10.4 Brick Composition Patterns?

**Question:** Can bricks compose into higher-order structures?

**Example:**
- Subsystem = collection of bricks
- Feature = cross-cutting slice of multiple bricks
- Layer = horizontal grouping (foundation, domain, interface)

**Challenge:** Avoid fractal complexity (bricks all the way down).

**Hypothesis:** Flat structure with metadata-based grouping.

---

### 10.5 Bricks for Non-Code Artifacts?

**Question:** Should bricks include docs, infrastructure, data schemas?

**Current:** Bricks = code + tests + intent.

**Extension:** Bricks = code + tests + intent + infrastructure + schemas?

**Trade-offs:**
- Broader scope = more complete context
- Broader scope = more complexity

**Research needed:** Experiment with "full-stack bricks."

---

## 11. Recommendations for JIG

### 11.1 Adopt the Best Practices

**From Rust: Static validation**
- Implement `jigy brick validate` early
- Make validation fast (<1 second)
- Integrate into CI

**From Go: Radical simplicity**
- Keep `.brick.yaml` minimal
- Avoid abstraction layers
- One brick = one clear responsibility

**From Nx: Dependency graph visualization**
- Implement `jigy graph show --bricks`
- Show brick dependencies, not just node dependencies
- Enable "affected bricks" queries

**From DDD: Semantic cohesion**
- Bricks should have meaningful responsibilities
- Use natural language in intent nodes
- Group by domain concepts, not technical layers

**From Microservices: Cautious boundaries**
- Don't over-brick (10 bricks is good, 100 is too many)
- Merge bricks that are tightly coupled
- Split bricks that grow too large (>1K LOC)

---

### 11.2 Avoid the Pitfalls

**Rust pitfall: Over-engineered type systems**
→ Don't make brick definitions too complex.

**Java pitfall: XML/YAML hell**
→ Keep `.brick.yaml` files simple and readable.

**Microservices pitfall: Too fine-grained**
→ Bricks should be human-scale (~500 LOC), not function-scale.

**DDD pitfall: Unclear boundaries**
→ Make brick membership explicit, not inferred.

**Nx pitfall: Tooling lock-in**
→ Brick concepts should be tool-agnostic (even if JIG is the current implementation).

---

### 11.3 Unique Brick Strengths to Leverage

**1. Intent as data**
→ Build tools that query intent (e.g., "Which bricks satisfy O-PERF-001?").

**2. Alignment verification**
→ Make alignment a first-class metric (dashboards, trends).

**3. Agent-first design**
→ Use bricks for all agent interactions, measure quality improvement.

**4. Multi-layer enforcement**
→ Start with simple (definitions + validation), add runtime enforcement later.

**5. Gradual adoption**
→ Define bricks for existing codebases without restructuring files (hybrid approach).

---

## 12. Conclusion

### 12.1 Context Fencing is Universal

Every mature ecosystem has discovered the need for bounded contexts:
- Rust: Crates
- Go: Packages
- Java: Modules
- JavaScript: Libraries
- DDD: Bounded Contexts
- Microservices: Services

**The pattern is universal because the problem is universal:**
Human and machine cognition have finite capacity.

---

### 12.2 Bricks Are the Next Evolution

**What makes Bricks different:**
1. **Dual-audience design** - Humans AND AI agents
2. **Intent as first-class** - Machine-readable requirements
3. **Alignment verification** - Computable drift detection
4. **Multi-layer enforcement** - Social + technical + validation
5. **Semantic + technical** - Meaning AND mechanism

**Bricks are the first architectural pattern explicitly designed for the age of AI-augmented development.**

---

### 12.3 Lessons Learned

**From 50 years of context fencing:**

✅ **Explicit boundaries beat implicit conventions**
✅ **Enforcement matters** (discipline alone fails)
✅ **Simplicity wins** (complex patterns don't get adopted)
✅ **Visibility matters** (graphs, visualization, querying)
✅ **Semantics > syntax** (meaning beats technical grouping)
✅ **Trade-offs exist** (strong boundaries have costs)

**Bricks incorporate these lessons while adding novel capabilities for AI collaboration.**

---

### 12.4 The Future of Software Architecture

**Past:** Architecture as documentation (diagrams, wikis).
**Present:** Architecture as code (infrastructure-as-code).
**Future:** **Architecture as graph** (intent + code + tests + boundaries, queryable and verifiable).

**Bricks + Alignment Graph = Architecture as Graph**

This enables:
- Automated drift detection
- Agent-safe development
- Intent traceability
- Architectural evolution
- Human-AI collaboration

**Context fencing has always been about managing complexity.**
**Bricks are about managing complexity in the age of AI.**

---

## References

### Academic
- Parnas, D. L. (1972). "On the Criteria To Be Used in Decomposing Systems into Modules"
- Simon, H. A. (1962). "The Architecture of Complexity"
- Miller, G. A. (1956). "The Magical Number Seven, Plus or Minus Two"
- Conway, M. E. (1968). "How Do Committees Invent?"

### Industry Patterns
- Evans, E. (2003). _Domain-Driven Design: Tackling Complexity in the Heart of Software_
- Martin, R. C. (2017). _Clean Architecture_
- Newman, S. (2015). _Building Microservices_
- Kleppmann, M. (2017). _Designing Data-Intensive Applications_

### Ecosystem Documentation
- Rust Book: https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html
- Go Modules: https://go.dev/blog/using-go-modules
- Nx Documentation: https://nx.dev/concepts/more-concepts/applications-and-libraries
- Maven Multi-Module: https://maven.apache.org/guides/mini/guide-multiple-modules.html

### Related Work
- Bazel: https://bazel.build/
- Module Federation: https://webpack.js.org/concepts/module-federation/
- JPMS (Java Platform Module System): https://openjdk.org/projects/jigsaw/

---

**Document Status:** Deep analysis for architectural decision-making.

**Next Steps:**
1. Review with architect
2. Validate Brick design decisions against ecosystem lessons
3. Implement Brick validation tooling informed by Rust/Nx practices
4. Measure agent quality improvement with Brick boundaries
5. Publish Brick pattern for broader community feedback

---

**Acknowledgments:** This analysis synthesizes patterns from decades of software engineering practice across multiple ecosystems. The insights belong to the communities that created Rust, Go, Java, JavaScript, DDD, and microservices. Bricks stand on the shoulders of giants.
