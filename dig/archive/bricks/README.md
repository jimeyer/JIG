---
title: "Alignment Graph & Bricks - Documentation"
type: exploration
status: implemented
decision: "Superseded by newer deliberation"
created: 1763934216
created_human: "2025-11-23 15:43 CST"
parent: null
children: ['[[AG001_Alignment-Graph-Bricks]]']
---
# Alignment Graph & Bricks - Documentation

This directory contains documentation and analysis for the **Alignment Graph** and **Bricks** architectural model for JIG.

---

## Documents

### 1. Conceptual Foundation

#### [Alignment-Graph-Bricks.md](Alignment-Graph-Bricks.md)
**The core concept document.**

Defines:
- What the Alignment Graph is
- What Bricks are
- How Bricks enforce architectural boundaries
- Architecture Mode vs. Implementation Mode
- Drift detection and alignment measurement

**Start here** to understand the theoretical foundation.

---

### 2. Enforcement Mechanism

#### [Brick-Context-Enforcement-Proposal.md](Brick-Context-Enforcement-Proposal.md)
**How to constrain AI agents to work within Brick boundaries.**

Comprehensive proposal covering:
- The Brick Context Contract (what agents can/cannot see)
- 4-layer enforcement strategy (definitions, context loading, tool wrappers, validation)
- Practical workflow for Claude Code today
- Brick definition file format (.brick.yaml)
- Validation and compliance checking
- Implementation phases

**Read this** to understand how to actually enforce Brick boundaries.

#### [Enforcement-Quick-Reference.md](Enforcement-Quick-Reference.md)
**Quick reference card for Brick Mode workflow.**

One-page guide:
- Quick workflow steps
- What goes in .brick.yaml
- Validation checks
- Example session
- Key commands

**Use this** as a cheat sheet when working in Brick Mode.

---

### 3. Shared Artifacts

#### [Shared-Artifacts-And-Bricks.md](Shared-Artifacts-And-Bricks.md)
**How shared files like graph-index.json fit into the Brick model.**

Addresses:
- Shared artifacts as interface contracts
- Single writer, multiple readers pattern
- Schema versioning and ownership
- Repository pattern for artifacts
- How different Bricks see the same artifact

**Read this** to understand how Bricks share data without violating boundaries.

---

### 4. Clean Breaks & Refactoring

#### [Clean-Breaks-And-Cross-Brick-Refactoring.md](Clean-Breaks-And-Cross-Brick-Refactoring.md)
**How to make breaking changes across Brick boundaries during active development.**

Comprehensive guide covering:
- Development Mode vs. Production Mode
- Why Bricks HELP with clean breaks
- Cross-Brick refactoring workflow
- No compatibility layers in dev mode
- Integration with taskCleanBreak protocol
- Practical commands and validation

**Read this** to understand how to "burn the ships" safely with Bricks.

#### [Clean-Breaks-Quick-Reference.md](Clean-Breaks-Quick-Reference.md)
**One-page cheat sheet for clean break workflow.**

Quick guide:
- 6-step workflow
- Commands reference
- Do's and don'ts
- Example commit format

**Use this** when making breaking changes in dev mode.

---

### 5. JIG System Analysis

#### [Brick-Analysis-JIG-System.md](Brick-Analysis-JIG-System.md)
**Comprehensive architectural analysis of the JIG codebase.**

Contains:
- **10 identified Bricks** with detailed specifications
- Dependency analysis and coupling ratios
- Test coverage mapping
- Intent node alignment
- Brick definition format proposal
- Recommendations for implementation

**This is the main deliverable** - a complete Brick architecture for JIG.

---

#### [Brick-Summary.md](Brick-Summary.md)
**Quick reference card for the 10 Bricks.**

Provides:
- One-page overview of all Bricks
- Size and health metrics
- Dependency flow diagram
- Visual architecture map

**Use this** for quick lookups and orientation.

---

### 3. Background Reading

#### [Understanding_Alignment_and_Bricks.md](Understanding_Alignment_and_Bricks.md)
**Earlier exploration notes** on the Alignment Graph concept.

Background material on:
- Intent-Code-Test alignment
- Drift detection mechanisms
- Architectural integrity concepts

---

## Quick Navigation

### For Architects
1. Read: `Alignment-Graph-Bricks.md` (concept)
2. Read: `Brick-Analysis-JIG-System.md` (JIG architecture)
3. Read: `Brick-Context-Enforcement-Proposal.md` (how to enforce)
4. Review: Brick definitions and recommendations
5. Decide: Accept/modify proposed Bricks

### For Developers
1. Skim: `Brick-Summary.md` (quick overview)
2. Reference: `Brick-Analysis-JIG-System.md` (find your Brick)
3. Read: `Enforcement-Quick-Reference.md` (how to work in Brick Mode)
4. Check: Brick interfaces and boundaries
5. Follow: Brick Context Contract when coding with AI

### For AI Agents
1. Load: Context file from `jigy brick load BRICK-ID`
2. Understand: Brick boundaries from context file
3. Work: Only within allowed files and interfaces
4. Verify: Agent should suggest running `jigy brick validate` when done

### For Understanding Shared Data
1. Question: "How does graph-index.json work with Bricks?"
2. Read: `Shared-Artifacts-And-Bricks.md`
3. Understand: Single writer, multiple readers pattern
4. Apply: To other shared artifacts

### For Making Breaking Changes
1. Question: "How do I refactor across Brick boundaries?"
2. Read: `Clean-Breaks-Quick-Reference.md` (workflow)
3. Read: `Clean-Breaks-And-Cross-Brick-Refactoring.md` (full guide)
4. Use: `jigy brick validate --check-dependents` to see impact
5. Fix: All dependent Bricks shown by validation
6. Integrate: With `taskCleanBreak.md` protocol

---

## Analysis Artifacts

The following scripts were created to analyze the JIG codebase:

**In project root:**
- `analyze_imports.py` - Module dependency analysis
- `analyze_cohesion.py` - Semantic responsibility analysis
- `analyze_test_coverage.py` - Test-to-source mapping

**To run:**
```bash
python analyze_imports.py
python analyze_cohesion.py
python analyze_test_coverage.py
```

These scripts can be used to:
- Verify Brick boundaries remain clean
- Detect architectural drift
- Update coupling metrics
- Re-run analysis after refactoring

---

## Key Findings

### JIG Has Natural Brick Boundaries ✅

The analysis revealed 10 cohesive architectural units:

**Foundation Layer (2 Bricks)**
1. Foundation Utilities (173 LOC)
2. Configuration & Filtering (219 LOC)

**Domain Core Layer (3 Bricks)**
3. Intent Parser (129 LOC)
4. Intent Validator (528 LOC)
5. Graph Core (696 LOC) ⚠️ _large_

**Analysis & Discovery Layer (4 Bricks)**
6. Annotation Scanner (301 LOC)
7. Annotation Validator (368 LOC)
8. Index Builder (530 LOC)
9. Decomposition Analysis (246 LOC)

**Interface Layer (1 Brick)**
10. CLI Commands (2,338 LOC) ⚠️ _large, orchestrator_

---

### Metrics

- **Average Coupling Ratio:** ~13:1 (internal:external)
- **Test Coverage:** 320 tests across 40 files
- **Health Score:** 8/10 Bricks rated Good or Excellent
- **Layering:** Clear foundation → domain → analysis → interface
- **Largest Brick:** CLI (2,338 LOC) - orchestration layer
- **Smallest Brick:** Parser (129 LOC) - focused responsibility

---

### Recommendations

1. ✅ **Adopt** the 10 identified Bricks as initial architecture
2. ⚠️ **Monitor** Graph Core and CLI for potential splits
3. 📝 **Create** formal Brick definition files (.brick.yaml)
4. 📚 **Add** Intent nodes for infrastructure Bricks
5. 🔍 **Implement** Brick boundary enforcement tools
6. 📊 **Add** Brick metrics to `jigy status` command

---

## Next Steps

### Phase 1: Formalization
- [ ] Review analysis with human architect
- [ ] Create Brick definition schema
- [ ] Write .brick.yaml files for all 10 Bricks
- [ ] Document public interfaces in code
- [ ] Add missing Intent nodes (O/S)

### Phase 2: Enforcement
- [ ] Implement Brick Context Contract validator
- [ ] Add `jigy bricks` command group
- [ ] Detect Brick boundary violations
- [ ] Add Brick-level metrics to status
- [ ] Visualize Brick dependency graph

### Phase 3: Agent Integration
- [ ] Implement Architecture Mode (Brick-level context)
- [ ] Implement Implementation Mode (single-Brick scope)
- [ ] Build Alignment Graph for JIG itself
- [ ] Use Bricks to constrain agent context windows
- [ ] Measure drift using Alignment Graph

---

## Contributing

When modifying this documentation:

1. **Concepts** → Update `Alignment-Graph-Bricks.md`
2. **JIG Analysis** → Update `Brick-Analysis-JIG-System.md`
3. **Quick Reference** → Update `Brick-Summary.md`
4. **Keep in sync** - summary should match full analysis

When refactoring code:

1. **Check Brick boundaries** - run analysis scripts
2. **Update Brick definitions** if responsibilities change
3. **Maintain coupling ratios** - avoid increasing inter-Brick calls
4. **Preserve test boundaries** - keep tests aligned with Bricks

---

## References

### External Influences
- Parnas information hiding (1972)
- DDD bounded contexts
- Clean Architecture boundary rules
- Nearly Decomposable Systems (Herbert Simon)
- Microservice autonomy patterns

### JIG Documentation
- `README.md` - System overview
- `docs/jig-concept/JIG-Concept-v7.md` - OSTCX model
- `docs/architecture/` - Technical architecture
- `jig/subsystems.yaml` - Current subsystem definitions

---

## Questions?

For conceptual questions about Alignment Graphs and Bricks:
- See: `Alignment-Graph-Bricks.md`
- Discuss: With architect

For specific JIG Brick questions:
- See: `Brick-Analysis-JIG-System.md`
- Check: Brick definition for your module
- Ask: In code reviews

For implementation questions:
- Run: Analysis scripts to verify boundaries
- Check: Test coverage by Brick
- Review: Coupling ratios and dependencies

---

**Last Updated:** 2025-11-22
**Analysis Version:** 1.0
**JIG Version:** 0.3.0-dev
