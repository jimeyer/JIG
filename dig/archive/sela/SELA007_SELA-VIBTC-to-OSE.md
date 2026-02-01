---
title: "SELA Model Transition: From VIBTC → OSE"
type: exploration
status: parked
created: 1763493911
created_human: "2025-11-18 13:25 CST"
parent: "[[SELA001_SELA-Concept-Document]]"
children: []
---
# SELA Model Transition: From VIBTC → OSE  
**Version:** 0.1  
**Date:** 2025-11-07  
**Status:** Draft  

---

## 1. Purpose

This document formalizes the transition of SELA’s semantic model from **VIBTC** (Values, Intents, Behaviors, Tests, Code) to a simplified and more communicative triad: **OSE** — *Outcomes, Specifications, Executions.*

The OSE model retains all the expressive power of VIBTC while improving clarity, usability, and alignment between business and engineering. It provides a single shared vocabulary for product managers, designers, and developers to describe the full lifecycle of a product idea—from purpose to proof.

---

## 2. Background

The original SELA semantic graph used five primary nodes:

| Node | Description |
|------|--------------|
| **Value (V)** | The business or user value a feature delivers. |
| **Intent (I)** | The specific purpose or problem the feature aims to solve. |
| **Behavior (B)** | Observable, testable system actions that fulfill the intent. |
| **Tests (T)** | Verification artifacts ensuring the behavior is correct. |
| **Code (C)** | The actual implementation of the behavior. |

This **VIBTC** structure worked well for formal traceability but proved heavy in daily use. In conversation, business leaders spoke in *values* and *outcomes*, engineers spoke in *specs* and *code*, and few people naturally separated *intent* from *value* or *tests* from *code*.  
The structure also produced high graph churn—too many nodes for each logical concept—and made “alignment” discussions more cumbersome.

---

## 3. The Shift to OSE

SELA now models the system as a triad:

| Element | Description | Legacy Mapping |
|----------|--------------|----------------|
| **Outcome (O)** | The *why*—the business value and user intent, unified into a single expression of purpose and success criteria. | `Value + Intent` |
| **Specification (S)** | The *what*—the formal description of observable behavior and constraints that realize the outcome. | `Behavior` |
| **Execution (E)** | The *how*—the running system and all artifacts that prove it works: code, tests, telemetry, and evidence. | `Tests + Code` |

OSE collapses five related ideas into three interdependent layers that mirror how teams naturally think and talk:

> *Outcome describes the promise.*  
> *Specification defines what fulfills that promise.*  
> *Execution makes it real.*

---

## 4. Motivations for Change

| Goal | VIBTC Limitation | OSE Solution |
|------|------------------|---------------|
| **Improve human alignment** | Too many abstract terms; unclear boundaries between Value and Intent. | Merge into **Outcome**, the shared business+product anchor. |
| **Simplify reasoning** | Graph traversal and balancing required five linked nodes. | Three-node triad enables faster and clearer alignment logic. |
| **Unify language** | Business spoke “value,” engineers spoke “behavior/tests.” | “Outcome, Specification, Execution” is shared vocabulary. |
| **Reduce graph churn** | Every feature generated multiple nodes. | OSE maintains nesting within nodes rather than multiplying them. |
| **Enable richer nesting** | VIBTC flattened semantics. | OSE supports layered subgraphs (nested Outcomes, nested Executions). |
| **Support organizational adoption** | VIBTC sounded academic. | OSE reads as everyday product language—usable in meetings and reports. |

---

## 5. Alignment Model (OSE)

SELA’s alignment engine ensures coherence across **Outcome**, **Specification**, and **Execution.**

### Alignment Rules
1. **Outcome ↔ Specification**  
   - Every Outcome MUST be specified by at least one Specification.  
   - Each Specification MUST reference the Outcome it fulfills.  
   - Misalignment = promises without specs, or specs detached from business purpose.

2. **Specification ↔ Execution**  
   - Every Specification MUST have one or more Executions (tests or implementations).  
   - Executions MUST not introduce behavior outside the Specification.  
   - Misalignment = failing tests, orphaned code, or unverified behaviors.

3. **Outcome ↔ Execution**  
   - Executions MUST demonstrate that the intended Outcome is achieved (via metrics, telemetry, acceptance tests).  
   - Misalignment = system delivers but not on the stated Outcome (e.g., feature works but no user impact).

---

## 6. Example OSE Structure

```yaml
id: OSE-ShiftDeterminism
outcome:
  name: "Predictable Shifting"
  description: "Riders experience consistent, reliable gear changes that build confidence."
  metrics:
    - name: "Shift success rate"
      target: "99.9%"
    - name: "Latency (p95)"
      target: "≤120 ms"
specification:
  name: "Single Press Shift Behavior"
  scenarios:
    - when: "rear shift button pressed"
      then: "exactly one gear change occurs"
  invariants:
    - "No multiple shifts from a single press"
    - "Engagement latency ≤120 ms"
execution:
  tests:
    - file: tests/test_single_press.yaml
      status: pass
  code:
    - module: src/shift_controller.py
      version: 1.4.2
  telemetry:
    - metric: shift_latency_ms_p95
      current: 117.4