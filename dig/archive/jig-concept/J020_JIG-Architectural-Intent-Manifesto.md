---
title: "The Architectural Intent Manifesto"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1764980842
created_human: "2025-12-05 18:27 CST"
parent: "[[J017_JIG-Concept-v9]]"
children: []
---
# The Architectural Intent Manifesto

## Software as a Constraint Satisfaction Problem

**Version:** 1.0  
**Date:** December 2025  
**Authors:** Jim & Claude  
**Status:** Philosophy Document

---

## I. The Central Thesis

**Software development is not primarily about writing code. It is about maintaining alignment between what we intend and what exists.**

Code is easy. Alignment is hard.

We can generate code effortlessly—AI makes this trivial. But code without intent is chaos. Code that drifts from intent is decay. Code that contradicts intent is failure.

**JIG exists to make intent explicit, alignment measurable, and drift visible.**

---

## II. The Two Domains of Intent

Software has two irreducible domains of intent:

### Functional Intent: What the System Should DO

*"The system shall authenticate users with JWT tokens that expire after 15 minutes of inactivity."*

This is a specification. It declares behavior. It makes a promise about what the system does.

### Architectural Intent: How the System Should BE ORGANIZED

*"Authentication is a cohesive subsystem. It depends on cryptographic primitives but nothing depends on it except the API layer."*

This is structure. It declares boundaries. It makes a promise about how the system is organized.

**Both forms of intent are declarations. Neither executes. Both constrain.**

---

## III. Declarations Do Not Execute

A specification does not authenticate users. Code authenticates users.

A brick definition does not enforce boundaries. The compiler (sometimes) and discipline (always) enforce boundaries.

A layer declaration does not prevent cycles. Developers prevent cycles.

**Declarations are inert. They are statements of will, frozen in text.**

So why write them?

Because declarations create the possibility of **misalignment**. And misalignment creates **tension**. And tension is a **signal**.

---

## IV. The Tension Principle

> **When declared intent and actual reality diverge, tension emerges. Tension is not a bug. Tension is the signal that drives correction.**

Consider a physical jig—the woodworking tool that holds pieces in place. The jig doesn't cut wood. The jig doesn't shape wood. The jig creates **constraint**. When the wood doesn't fit the jig, you feel resistance. That resistance tells you: something must change.

Software intent works the same way:

| Declaration | Reality | Tension |
|-------------|---------|---------|
| Spec S-001 exists | No function implements S-001 | "Unimplemented specification" |
| Function F claims to implement S-001 | No test verifies S-001 | "Unverified specification" |
| Test T claims to verify S-001 | T doesn't execute F | "False verification claim" |
| Brick B-auth at layer 1 | B-auth calls B-api at layer 2 | "Upward dependency violation" |
| Brick B-auth exports 3 functions | 47 functions are called externally | "Boundary violation" |

**Each tension is a signal. Each signal demands response.**

The response might be:
- Fix the code to match the intent
- Fix the intent to match the code
- Acknowledge the tension as acceptable technical debt

But the tension cannot be ignored. It persists until resolved.

---

## V. The S-F-T Triangle: Functional Alignment

The Specification-Function-Test triangle is the irreducible core of functional intent:

```
         S (Specification)
        ╱ ╲
       ╱   ╲
      ╱     ╲
implements  verifies
    ╱         ╲
   ╱           ╲
  F ──covers──► T
(Function)    (Test)
```

**Three nodes. Three edges. Three potential tensions.**

| Edge | Meaning | Tension When Missing |
|------|---------|---------------------|
| F → S | "This function implements this spec" | Unimplemented intent |
| T → S | "This test verifies this spec" | Unverified intent |
| T → F | "This test executes this function" | False verification |

The triangle is a constraint system. Perfect alignment means all three edges exist and are consistent. Any missing or inconsistent edge creates tension.

**The triangle does not make code correct. The triangle makes incorrectness visible.**

---

## VI. Bricks and Layers: Architectural Alignment

The Brick-Layer system is the irreducible core of architectural intent:

### Bricks: Horizontal Partitioning

A brick is a declaration: *"These functions belong together. They share secrets. They form a cohesive unit with a defined boundary."*

Bricks partition the function space horizontally—within a layer, bricks create boundaries that limit what can see what.

**Bricks are not native modules.** Native modules are discovered from code. Bricks are declared as intent. A brick might map 1:1 to a native module, or it might group several, or it might subdivide one. The mapping is not the point. The declaration of intent is the point.

### Layers: Vertical Ordering

A layer is a declaration: *"These bricks are at this level of abstraction. They may only depend on lower layers."*

Layers partition the brick space vertically—across the system, layers create ordering that constrains what can depend on what.

**Layers are not derived from code.** Yes, you can compute layers from a dependency graph. But computed layers describe what IS. Declared layers describe what SHOULD BE. The tension between them is the signal.

### The Two-Dimensional Constraint

Together, bricks and layers create a two-dimensional constraint system:

```
Layer 2: [B-cli] [B-gui]
              ↓       ↓
Layer 1: [B-auth] [B-billing] [B-inventory]
              ↓       ↓            ↓
Layer 0: [B-crypto] [B-logging] [B-config]
```

**Vertical constraint (layers):** Dependencies flow downward only.
**Horizontal constraint (bricks):** Only exports cross boundaries.

| Violation | Tension |
|-----------|---------|
| B-auth calls B-cli | Upward dependency (layer violation) |
| B-auth calls B-billing internals | Boundary breach (brick violation) |
| B-auth has 2:1 coupling ratio | Weak cohesion (nearly-decomposable violation) |

**Every violation is tension. Every tension is a signal.**

---

## VII. The Flow of Intent

Intent flows through declarations into constraints:

```
┌─────────────────┐
│  Human Intent   │  "Users should authenticate securely"
└────────┬────────┘
         ▼
┌─────────────────┐
│  Specification  │  S-AUTH-001: JWT tokens, 15-minute expiry
└────────┬────────┘
         ▼
┌─────────────────┐
│   Decoration    │  @implements("S-AUTH-001") on function
└────────┬────────┘
         ▼
┌─────────────────┐
│   Alignment     │  Graph edge: F-authenticate → S-AUTH-001
│     Graph       │  
└────────┬────────┘
         ▼
┌─────────────────┐
│    Tension      │  Missing T → S edge: "S-AUTH-001 unverified"
│    Detection    │
└────────┬────────┘
         ▼
┌─────────────────┐
│     Signal      │  CI fails, dashboard shows gap, agent notices
└────────┬────────┘
         ▼
┌─────────────────┐
│   Correction    │  Human or agent writes test, restores alignment
└─────────────────┘
```

The same flow applies to architectural intent:

```
┌─────────────────┐
│  Human Intent   │  "Auth should be isolated, depend only on crypto"
└────────┬────────┘
         ▼
┌─────────────────┐
│ Brick + Layer   │  B-auth at layer 1, depends on B-crypto at layer 0
│  Declaration    │
└────────┬────────┘
         ▼
┌─────────────────┐
│   Validation    │  Check: Does code match declaration?
└────────┬────────┘
         ▼
┌─────────────────┐
│    Tension      │  B-auth imports from B-api (layer 2): violation
│    Detection    │
└────────┬────────┘
         ▼
┌─────────────────┐
│     Signal      │  Layer validation fails, diagram shows red edge
└────────┬────────┘
         ▼
┌─────────────────┐
│   Correction    │  Human or agent removes dependency, restores alignment
└─────────────────┘
```

**Intent → Declaration → Validation → Tension → Signal → Correction**

This is the JIG loop. It runs continuously. It never ends.

---

## VIII. Why AI Agents Need Intent

AI agents can generate unlimited code. They cannot generate intent.

Intent comes from humans—from business needs, user stories, regulatory requirements, architectural decisions. Agents are powerful executors but they need constraints.

**Without declared intent, agents optimize for the wrong things:**
- Code that compiles but doesn't meet requirements
- Tests that pass but don't verify specifications  
- Modules that work but violate architectural boundaries
- Changes that fix one thing but break three others

**With declared intent, agents have guardrails:**
- Specs tell agents what to build
- Tests tell agents what to verify
- Bricks tell agents what context to consider
- Layers tell agents what dependencies are legal

The alignment graph is not just documentation. It is the **constraint system within which agents operate**.

When an agent's change creates tension (breaks a spec, violates a boundary, creates a cycle), the tension is a signal—to the agent itself—that correction is needed.

**JIG turns architectural intent into agent constraints.**

---

## IX. The Economics of Tension

Tension has a cost. Maintaining alignment has a cost. Why pay it?

Because the cost of invisible drift is catastrophic.

| Drift Type | Without JIG | With JIG |
|------------|-------------|----------|
| Spec drift | Discovered in production ($$$$) | Discovered in CI ($) |
| Test drift | Discovered when bugs ship ($$$$) | Discovered in validation ($) |
| Boundary drift | Discovered when refactoring is impossible ($$$$$) | Discovered at PR time ($) |
| Layer drift | Discovered when cycles block builds ($$$) | Discovered immediately ($) |

**The tension signal converts expensive late-stage failures into cheap early-stage corrections.**

Every tension caught early is a crisis prevented later.

---

## X. The Nature of the Graph

The alignment graph is not a model OF the system. It is a model of our INTENT for the system, overlaid with the reality of what exists.

```
Intent Layer:     [S-001] ←── [S-002] ←── [S-003]
                     ↑            ↑            ↑
                  declares     declares     declares
                     ↓            ↓            ↓
Reality Layer:    [F-auth] ─── [F-sess] ─── [F-token]
                     ↑            ↑            ↑
                  verifies     verifies     (missing!)
                     ↓            ↓            ↓
Verification:     [T-auth] ─── [T-sess] ─── ???
```

The graph shows both what should be and what is. The gaps are tension. The tensions are signals.

**The graph is not descriptive. It is normative.**

It doesn't just say "here's how the code is organized." It says "here's how it SHOULD be organized, here's how it IS organized, and here are the differences."

---

## XI. The Manifesto

We declare:

1. **Intent must be explicit.** Implicit intent is lost intent. We write specifications. We declare bricks. We define layers. We make our will concrete.

2. **Alignment must be measurable.** What cannot be measured cannot be managed. We build graphs. We count edges. We compute ratios. We quantify alignment.

3. **Tension is a feature, not a bug.** When intent and reality diverge, we want to know. Tension is the signal. We do not hide tension. We surface it.

4. **Signals demand response.** Tension that is ignored becomes drift. Drift that is ignored becomes decay. Decay that is ignored becomes failure. We respond to signals.

5. **Humans declare intent. Machines detect tension. Both restore alignment.** The loop is collaborative. Humans set direction. Machines amplify awareness. Both take action.

6. **The cost of early tension is low. The cost of late drift is high.** We pay the small cost of maintaining alignment to avoid the catastrophic cost of discovering misalignment in production.

7. **Architecture is intent, not accident.** The structure of a system should reflect deliberate design, not accumulated happenstance. We declare our architectural will and hold ourselves to it.

---

## XII. The Promise

JIG promises:

**For specifications:** You will know which are implemented, which are verified, and which are orphaned. No specification will silently drift from reality.

**For functions:** You will know which specifications they implement, which tests verify them, and whether the verification is real. No function will silently lose its purpose.

**For tests:** You will know which specifications they verify, which functions they cover, and whether they're actually testing what they claim. No test will silently become theater.

**For bricks:** You will know their boundaries, their dependencies, their coupling ratios. No brick will silently become a god module.

**For layers:** You will know the ordering, the violations, the cycles. No layer will silently become spaghetti.

**For the system:** You will know its alignment—functional and architectural. You will see the tensions. You will have the signals.

**What you do with the signals is up to you.**

---

## XIII. Conclusion

Software is intent made manifest in code.

The tragedy of software is that intent fades while code persists. We forget why we built what we built. We lose track of what verifies what. We let boundaries erode and dependencies tangle.

JIG is a system for making intent persist.

Not by freezing code—code must change.
Not by preventing evolution—systems must grow.

But by making intent explicit, alignment measurable, and drift visible.

**The jig holds the pieces in place. When they slip, you feel the tension. The tension is the signal. The signal drives correction.**

This is the Architectural Intent Manifesto.

This is why we build JIG.

---

*"Intent declared. Alignment measured. Tension surfaced. Drift prevented."*

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**License:** Proprietary

