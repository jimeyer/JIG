# JIG System: Brick Summary

Quick reference for the 10 architectural Bricks identified in the JIG system.

---

## The 10 Bricks

### Layer 1: Foundation (No Internal Dependencies)

#### 🧱 BRICK-UTILS: Foundation Utilities
- **Files:** `utils/io.py`, `utils/yaml_utils.py`
- **LOC:** 173
- **Purpose:** Pure file I/O and YAML operations
- **Coupling:** ∞:1 (foundation layer)
- **Health:** ✅ Excellent

#### 🧱 BRICK-CONFIG: Configuration & Filtering
- **Files:** `core/config.py`, `core/ignore_filter.py`
- **LOC:** 219
- **Purpose:** Load config, manage .jigignore patterns
- **Coupling:** ~30:1
- **Health:** ✅ Excellent

---

### Layer 2: Domain Core (Intent & Graph)

#### 🧱 BRICK-PARSER: Intent Parser
- **Files:** `core/parser.py`
- **LOC:** 129
- **Purpose:** Parse OSTC nodes (YAML + Markdown)
- **Deps:** Utils
- **Coupling:** ~15:1
- **Health:** ✅ Excellent

#### 🧱 BRICK-VALIDATOR: Intent Validator
- **Files:** `core/validator.py`, `core/validation.py`
- **LOC:** 528
- **Purpose:** Validate nodes and graph consistency
- **Deps:** Parser, Graph
- **Coupling:** ~8:1
- **Health:** ✅ Good

#### 🧱 BRICK-GRAPH: Graph Core
- **Files:** `core/graph.py`, `core/relationships.py`
- **LOC:** 696
- **Purpose:** Graph structures, queries, traversal
- **Deps:** Parser, Utils
- **Coupling:** ~12:1
- **Health:** ⚠️ Fair (large, consider split)

---

### Layer 3: Analysis & Discovery

#### 🧱 BRICK-SCANNER: Annotation Scanner
- **Files:** `core/scanner.py`
- **LOC:** 301
- **Purpose:** Scan @jig annotations in source
- **Deps:** Config
- **Coupling:** ~15:1
- **Health:** ✅ Excellent

#### 🧱 BRICK-ANNOT-VALIDATOR: Annotation Validator
- **Files:** `core/annotation_validator.py`
- **LOC:** 368
- **Purpose:** Validate annotations against graph
- **Deps:** Scanner, Graph
- **Coupling:** ~8:1
- **Health:** ✅ Good

#### 🧱 BRICK-INDEX: Index Builder
- **Files:** `core/index_builder.py`
- **LOC:** 530
- **Purpose:** Build graph-index.json from sources
- **Deps:** Parser, Scanner, Graph
- **Coupling:** ~6:1
- **Health:** ✅ Good

#### 🧱 BRICK-DECOMPOSE: Decomposition Analysis
- **Files:** `decompose/metrics.py`
- **LOC:** 246
- **Purpose:** Calculate modularity, coupling metrics
- **Deps:** Graph
- **Coupling:** ~20:1
- **Health:** ✅ Excellent

---

### Layer 4: Interface (Orchestration)

#### 🧱 BRICK-CLI: CLI Commands
- **Files:** All `cli/*.py` (9 files)
- **LOC:** 2,338
- **Purpose:** Command-line interface, user interaction
- **Deps:** ALL (orchestration layer)
- **Coupling:** ~2:1 (expected for orchestrator)
- **Health:** ⚠️ Fair (large, consider split by command group)

---

## Metrics Summary

| Metric | Value |
|--------|-------|
| **Total Bricks** | 10 |
| **Total LOC** | ~5,600 |
| **Total Tests** | 320 (40 files) |
| **Avg LOC per Brick** | ~560 |
| **Smallest Brick** | Parser (129 LOC) |
| **Largest Brick** | CLI (2,338 LOC) |
| **Avg Coupling Ratio** | ~13:1 |
| **Foundation Bricks** | 2 (no internal deps) |
| **Domain Bricks** | 3 |
| **Analysis Bricks** | 4 |
| **Interface Bricks** | 1 |

---

## Dependency Flow

```
Foundation Layer (no deps)
  ↓
Domain Core (parser → validator → graph)
  ↓
Analysis & Discovery (scanner → index, decompose)
  ↓
Interface (CLI orchestrates all)
```

---

## Health Assessment

| Health | Count | Bricks |
|--------|-------|--------|
| ✅ Excellent | 6 | Utils, Config, Parser, Scanner, Decompose, Annot-Validator |
| ✅ Good | 2 | Validator, Index |
| ⚠️ Fair | 2 | Graph (large), CLI (large) |
| ❌ Poor | 0 | None |

**Overall Health:** ✅ Good

---

## Next Actions

1. **Review** this analysis with architect
2. **Create** formal Brick definition files (.brick.yaml)
3. **Split** Graph and CLI if complexity grows
4. **Add** Intent nodes for infrastructure Bricks
5. **Document** public interfaces in code
6. **Implement** Brick boundary enforcement

---

## Visual Map

```
┌─────────────────────────────────────────┐
│         BRICK-CLI (Interface)           │  2,338 LOC
│      ┌─────────────────────┐           │
│      │ All CLI Commands    │           │
│      └─────────────────────┘           │
└──────────┬──────────────────────────────┘
           │ (orchestrates all)
    ┌──────┴─────┬─────────┬─────────┐
    │            │         │         │
┌───▼────┐  ┌───▼─────┐ ┌─▼──────┐ ┌▼────────┐
│ BRICK- │  │ BRICK-  │ │ BRICK- │ │ BRICK-  │
│ INDEX  │  │ SCANNER │ │ ANNOT  │ │DECOMPOSE│
│Builder │  │         │ │Validate│ │         │
│530 LOC │  │ 301 LOC │ │368 LOC │ │ 246 LOC │
└───┬────┘  └────┬────┘ └────┬───┘ └────┬────┘
    │            │           │          │
    └────────┬───┴──────┬────┴──────────┘
             │          │
        ┌────▼──────────▼─────┐
        │   BRICK-GRAPH       │  696 LOC
        │  (Domain Core)      │
        └──────┬──────────────┘
               │
    ┌──────────▼──────────┐
    │  BRICK-VALIDATOR    │  528 LOC
    └──────┬──────────────┘
           │
    ┌──────▼──────────┐
    │  BRICK-PARSER   │  129 LOC
    └──────┬──────────┘
           │
    ┌──────▼──────┬──────────┐
    │ BRICK-      │ BRICK-   │
    │ CONFIG      │ UTILS    │
    │ 219 LOC     │ 173 LOC  │
    └─────────────┴──────────┘
       (Foundation Layer)
```

---

**For full analysis, see:** `Brick-Analysis-JIG-System.md`
