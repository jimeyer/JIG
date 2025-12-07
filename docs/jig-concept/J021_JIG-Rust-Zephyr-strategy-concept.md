# J021: Firmware Development with Rust, JIG, and Zephyr

_A Strategy for nRF54-Class Hardware_

**Status:** Draft Concept
**Date:** 2025-12

---

## 1. Introduction

Firmware development today faces four converging pressures:

1. **Reducing bugs** — especially memory, concurrency, and edge-case defects
2. **Predictability** — ensuring implementation matches intended behavior
3. **Better documentation** — keeping intent, implementation, and verification aligned
4. **Leveraging AI tools** — using AI agents safely and effectively

This paper outlines a strategy for embedded firmware on Zephyr for nRF54-class hardware using three mutually reinforcing elements:

- **Rust** for correctness and memory safety
- **JIG** for architectural alignment and documentation
- **Zephyr + Nordic SDK** as the hardware substrate
- **AI-assisted development** operating safely inside this structured environment

The goal is to show how these pieces interlock—not to dictate a product design, but to provide a conceptual architecture strategy for any embedded system built on a large C-based dependency.

---

## 2. C vs. Rust in the Context of JIG and AI

### 2.1 Quick Comparison

**C:**
- Maximum control, minimal abstraction
- Undefined behavior is always possible
- Requires high discipline to avoid memory and concurrency bugs

**Rust:**
- Modern systems language eliminating entire bug classes (memory safety, data races)
- Strong types and ownership rules guide both humans and AI
- Produces deterministic, zero-cost code suitable for bare-metal work

### 2.2 Why JIG + Rust is Stronger Than JIG + C

JIG's model—specification → implementation → verification—relies on code that is predictable, structured, and analyzable.

| Dimension | C + JIG | Rust + JIG |
|-----------|---------|------------|
| Memory Safety | Weak; JIG cannot prevent C bugs | Strong; most defects eliminated in safe code |
| Architectural Boundaries | Hard to enforce; headers leak | Crates/modules/visibility align with Bricks/Layers |
| Predictability | High variance; UB possible | Compiler-enforced invariants |
| LLM Behavior | AI reproduces legacy unsafe patterns | AI guided by type system into safer patterns |
| Documentation | Comments & headers drift | Types, enums, traits encode intent in code |

Rust multiplies the effectiveness of JIG and AI agents because:

- The type system prevents entire categories of misalignment
- Crates map cleanly to Bricks
- `pub` and `pub(crate)` enforce architectural boundaries
- Build-graph dependencies mirror JIG Layers
- The compiler does much of the verification work

C works, but Rust + JIG creates a *self-correcting architecture* where drift is harder to introduce and easier to detect.

---

## 3. The Dependency Problem

Zephyr and the Nordic nRF54 SDK are written in C. They provide:

- BLE stack
- Drivers
- RTOS primitives
- Power management
- Board support packages

We treat this as a large, external dependency—a "foreign world" where JIG has no influence and Rust has limited leverage.

This raises a question: How do we let Rust and JIG operate in a structured, safe way while still relying on a large C ecosystem?

The answer is to use JIG's layer system, with Layer 0 serving as the containment boundary for all C interop.

---

## 4. The Architecture

```
┌─────────────────────────────────────────────┐
│  EXTERNAL: Zephyr + Nordic SDK              │
│  - Not JIG-managed                          │
│  - Treated as opaque C dependency           │
│  - Accessed only through Layer 0            │
└─────────────────────────────────────────────┘
                    ▲
                    │ FFI calls
                    │
┌─────────────────────────────────────────────┐
│  LAYER 0: FFI Boundary                      │
│  - The "narrow waist"                       │
│  - Only place unsafe is permitted           │
│  - Containment zone for C interop           │
│  - B-hal-ffi, B-board-config                │
├─────────────────────────────────────────────┤
│  LAYER 1: Platform Services                 │
│  - Pure Rust, no unsafe                     │
│  - B-radio, B-storage, B-power              │
├─────────────────────────────────────────────┤
│  LAYER 2: Domain Logic                      │
│  - B-state-machine, B-sync-protocol         │
├─────────────────────────────────────────────┤
│  LAYER 3: Application                       │
│  - B-main-app, B-control-loop               │
└─────────────────────────────────────────────┘
```

### 4.1 External: Zephyr + SDK

We take a "When in Rome" approach:

- Zephyr is not rewritten
- Zephyr is not JIG-managed
- Zephyr's APIs and behavior are treated as external facts

JIG observes *what we do with Zephyr*, not Zephyr itself. Rust avoids most of Zephyr's internal complexity by treating it as a library behind a safe API.

### 4.2 Layer 0: The FFI Boundary

Layer 0 has a unique role: it's the containment zone for all C interop.

Rules:

- Layer 0 Bricks (e.g., `B-hal-ffi`) are the *only* Bricks permitted to call C
- Explicit FFI functions, each tied to a JIG specification
- All types `#[repr(C)]` and simple POD structures
- Ownership rules explicit and documented
- `unsafe` isolated here and nowhere else

> Layer 0 is a hazardous materials containment zone. It should be small, explicit, versioned, and extremely well-tested.

Design principles:

1. **Minimize surface area** — fewer, coarser APIs are safer
2. **Treat every FFI call like a syscall** — define and test semantics
3. **Do not share mutable memory** — pass values across the seam, not references
4. **Document alignment with JIG specs** — preconditions, invariants, lifetimes
5. **Test aggressively** — mocked tests, fuzzing, property tests, hardware loopbacks

This layer turns Zephyr into a predictable substrate.

### 4.3 Layers 1+: Pure Rust Application Code

Everything above Layer 0 is pure safe Rust, fully JIG-managed.

Characteristics:

- No `unsafe` — that's confined to Layer 0
- Heavily annotated with JIG decorators
- Organized into Bricks with strict Layer rules
- Every behavior mapped to a specification
- Zero drift tolerated

This is the "true" firmware logic: state machines, radio logic, data transforms, protocol behavior, power decisions.

AI agents operate confidently here—Rust's rules plus JIG's alignment structure prevent most model-induced errors.

---

## 5. Brick and Layer Mapping

Rust's native structure maps elegantly onto JIG:

- Crates = Bricks
- Crate dependencies = Layers
- Module visibility = Boundary enforcement

### Example Layering

**Layer 0: Foundation (FFI Boundary)**
- `B-hal-ffi` (FFI bridge to Zephyr)
- `B-board-config`

**Layer 1: Platform Services**
- `B-radio` (BLE, packetization)
- `B-storage`
- `B-logging`
- `B-power`

**Layer 2: Domain Logic**
- `B-state-machine`
- `B-sync-protocol`
- `B-sensor-process`

**Layer 3: Application**
- `B-main-app`
- `B-control-loop`

JIG continuously validates:

- Correct dependencies (Layer N only depends on layers < N)
- Boundary restrictions (only Layer 0 touches C)
- Specs implemented and verified
- Functions actually tested for what they claim to verify
- Drift in intent vs. implementation

This creates predictable evolution—critical for AI-assisted code.

---

## 6. Testing Strategy

Testing must reflect architectural risk. Layer 0 carries the most risk; higher layers are progressively safer.

### 6.1 Layer 0 Tests (High Risk)

- Mocked Zephyr functions
- Validate argument mapping, errors, and state
- Validate FFI protocol invariants
- Fuzz testing—target `unsafe` code aggressively
- Verify no panics, no undefined behavior

### 6.2 Layers 1+ Tests (Lower Risk)

- Pure unit tests
- Property-based tests
- JIG-aligned verification tests
- No hardware required
- Fast CI, low cost

### 6.3 Hardware-in-the-Loop Tests

- BLE advertising and scan tests
- Flash read/write tests
- Timer/interrupt behavior
- Power measurement tests

### 6.4 JIG Alignment Checks

- Are specs → functions → tests aligned?
- Are Bricks respecting Layers?
- Is Layer 0 the only layer with `unsafe`?
- Are coverage relationships correct?

Testing is not just about correctness—it maintains alignment and ensures predictability.

---

## 7. AI Agents in the Stack

AI-assisted development is a major motivator. The challenge: LLMs generate unpredictable output unless the environment constrains them.

This stack constrains them well:

- **Rust** constrains semantics (ownership + types)
- **JIG** constrains architecture (Bricks + Layers + S/F/T triangle)
- **Zephyr** provides stable external APIs
- **Layer 0** gives a deliberately tiny escape hatch to C

AI agents generating Rust in Layers 1+ produce:

- Fewer bugs
- More consistent structure
- Easily aligned code
- Automated tracing from spec → implementation → test

AI agents modifying Layer 0 do so under tight constraints and heavy testing. The layer boundary makes it clear when an agent is entering dangerous territory.

---

## 8. Summary

This framework provides:

**Predictability:** Rust's type system and JIG's alignment rules combine to create a self-correcting architecture.

**Bug Reduction:** Memory safety, data race elimination, and structured layering drastically reduce defect classes.

**Better Documentation:** Specs, implementations, and tests stay connected and measurable through JIG.

**AI Acceleration:** Agents generate Rust inside a safe architectural sandbox. Drift is detected immediately. Layer 0 isolates unsafe interactions.

**Large Dependency Integration:** Zephyr remains the solid C-based substrate. Rust logic stays clean and aligned. Layer 0 provides a narrow, well-controlled bridge.

The triad—Rust + JIG + Zephyr—offers a resilient approach to embedded firmware development, especially as AI-assisted workflows become standard.

---

## References

- **J017:** JIG Concept v9 (Alignment Graph with Architectural Layers)
- **JIG-When-In-Rome:** Strategy for adopting JIG in existing ecosystems
