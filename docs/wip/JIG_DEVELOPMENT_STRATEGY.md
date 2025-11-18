# JIG Development Strategy
**Date:** 2025-11-18
**Status:** Development Plan
**Version:** 1.0

> "Building JIG using JIG principles: simple, fast, composable, local-first"

---

## Executive Summary

This document outlines the development strategy for building **JIG (Jig Intent Graph)** - a version control system for software intent. The strategy follows JIG's own philosophy: we will build JIG by practicing alignment-based development, using Deltas to narrate our work and harvesting insights into Intent as we go.

**Core Challenge:** Build a system that is itself an example of nearly decomposable architecture.

**Key Insight:** JIG tools fall into two natural subsystems:
1. **Deterministic Core** - Fast, reliable, grep-based operations (plumbing)
2. **Intelligence Layer** - LLM-assisted synthesis and analysis (porcelain)

---

## Part 1: Project Structure

### 1.1 Directory Layout

```
jig/
├── agents/                        # Agent instruction files (prompts)
│   ├── taskPLAN.md               # PLAN workflow for AI agents
│   ├── taskREVIEW.md             # Code review workflow
│   ├── taskREFACTOR.md           # Refactoring workflow
│   └── taskDOCUMENT.md           # Documentation workflow
│
├── jig/                           # JIG's own Intent Graph (dogfooding)
│   ├── outcomes/                  # Business outcomes for JIG
│   ├── specifications/            # Technical specs
│   ├── graph-index.yaml          # Master graph index
│   └── subsystems.yaml           # Subsystem definitions
│
├── src/
│   └── jig/                       # Main package
│       ├── __init__.py
│       ├── cli/                   # Command-line interface (porcelain)
│       │   ├── __init__.py
│       │   ├── main.py           # Entry point (jigy command)
│       │   ├── extract.py        # Extract command
│       │   ├── synthesize.py     # Synthesize command
│       │   ├── integrate.py      # Integrate command
│       │   ├── distill.py        # Distill command (high-level)
│       │   ├── status.py         # Status command
│       │   ├── validate.py       # Validate command
│       │   ├── delta.py          # Delta management
│       │   ├── graph.py          # Graph visualization
│       │   └── decompose.py      # Decomposability analysis
│       │
│       ├── core/                  # Core abstractions (plumbing)
│       │   ├── __init__.py
│       │   ├── extractor.py      # Marker extraction engine
│       │   ├── parser.py         # YAML/Markdown parsing
│       │   ├── graph.py          # Graph data structure
│       │   ├── validator.py      # Reference validation
│       │   ├── integrator.py     # OSTC file updates
│       │   └── config.py         # .jig.toml handling
│       │
│       ├── delta/                 # Delta management subsystem
│       │   ├── __init__.py
│       │   ├── lifecycle.py      # Branch binding, archiving
│       │   ├── templates.py      # Delta templates
│       │   ├── markers.py        # Marker definitions
│       │   └── harvest.py        # Harvest report generation
│       │
│       ├── synthesis/             # LLM synthesis subsystem
│       │   ├── __init__.py
│       │   ├── synthesizer.py    # Main LLM orchestration
│       │   ├── prompts.py        # Prompt templates
│       │   ├── conflict.py       # Conflict detection
│       │   └── patterns.py       # Pattern recognition
│       │
│       ├── decompose/             # Decomposability analysis
│       │   ├── __init__.py
│       │   ├── detector.py       # Subsystem detection
│       │   ├── metrics.py        # Modularity, coupling calculations
│       │   ├── visualization.py  # Graph rendering
│       │   └── analyzer.py       # Community detection algorithms
│       │
│       ├── git_integration/       # Git hooks and helpers
│       │   ├── __init__.py
│       │   ├── hooks.py          # Git hook management
│       │   ├── branch.py         # Branch-Delta binding
│       │   └── commit.py         # Commit message parsing
│       │
│       └── utils/                 # Shared utilities
│           ├── __init__.py
│           ├── io.py             # File operations
│           ├── yaml_utils.py     # YAML helpers
│           ├── markdown.py       # Markdown parsing
│           └── text.py           # Text processing
│
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests (per subsystem)
│   │   ├── test_extractor.py
│   │   ├── test_parser.py
│   │   ├── test_graph.py
│   │   ├── test_synthesizer.py
│   │   └── ...
│   ├── integration/               # Integration tests
│   │   ├── test_harvest_pipeline.py
│   │   ├── test_delta_lifecycle.py
│   │   └── test_git_integration.py
│   ├── fixtures/                  # Test data
│   │   ├── sample_deltas/
│   │   ├── sample_ostc/
│   │   └── sample_repos/
│   └── e2e/                       # End-to-end tests
│       └── test_full_workflow.py
│
├── jig/                           # (continued)
│   ├── deltas/                   # JIG's own Deltas
│   │   ├── active/               # Current work
│   │   └── archive/              # Completed work
│
├── docs/
│   ├── jig-concept/              # Conceptual documentation (existing)
│   ├── wip/                      # Work in progress docs
│   ├── architecture/             # Architecture docs
│   │   ├── SUBSYSTEMS.md        # Subsystem descriptions
│   │   ├── DATA_FORMATS.md      # YAML schema definitions
│   │   └── PATTERNS.md          # Design patterns
│   └── user-guide/               # User documentation
│       ├── QUICKSTART.md
│       ├── COMMANDS.md
│       └── MARKERS.md
│
├── agents/                       # (see above for agent instructions)
│
├── templates/                     # Delta templates
│   ├── PLAN_TEMPLATE.md
│   ├── RETROSPECTIVE_TEMPLATE.md
│   ├── ANALYSIS_TEMPLATE.md
│   └── ...
│
├── pyproject.toml                # Python packaging (PEP 621)
├── jig.toml                      # JIG configuration (dogfooding)
├── .gitignore
└── README.md
```

### 1.2 Subsystem Boundaries

Following JIG's own philosophy, we define clear subsystems:

| Subsystem | Purpose | Exports | Dependencies |
|-----------|---------|---------|--------------|
| **core** | Graph data structures, validation | `Graph`, `Node`, `Validator` | utils |
| **delta** | Delta lifecycle management | `DeltaManager`, `HarvestReport` | core, utils |
| **synthesis** | LLM-based intelligence | `Synthesizer`, `SynthesisProposal` | core, delta |
| **decompose** | Architecture analysis | `MetricsCalculator`, `Detector` | core |
| **git_integration** | Git hooks and branch binding | `GitHooks`, `BranchManager` | delta, core |
| **cli** | User-facing commands | `jigy` command | all subsystems |

**Expected Metrics:**
- Coupling ratio: >10:1 (internal:external edges)
- Modularity score: >0.7
- Module depth: >100:1 (LOC per export)

---

## Part 2: Build Order (Vertical Slices)

### Philosophy: Build Vertical Slices, Not Layers

Rather than building "all parsers, then all extractors, then all commands," we build **complete workflows** end-to-end. This allows us to:
- Test real usage immediately
- Discover interface mismatches early
- Deliver value incrementally
- Practice JIG on JIG

### 2.1 Slice 0: Bootstrap (Week 1)

**Goal:** Minimal infrastructure to start dogfooding.

**Deliverables:**
```python
# Can create basic OSTC nodes manually
jig init                          # Create jig/ structure
jig node create --type spec      # Create S-001.md from template
jig validate                      # Basic YAML validation
```

**Implementation:**
- `src/jig/core/config.py` - Load jig.toml
- `src/jig/core/parser.py` - Parse YAML frontmatter
- `src/jig/core/validator.py` - Basic schema validation
- `src/jig/cli/main.py` - CLI skeleton
- `src/jig/cli/validate.py` - Validate command
- `jig.toml` - JIG's own config (start dogfooding!)

**Test:**
```bash
cd jig/
jig init
jig node create --type outcome --id O-JIG-001 --title "JIG tools run in <1s"
jig validate
```

**Delta:** `jig/deltas/active/bootstrap/PLAN_bootstrap.md`

---

### 2.2 Slice 1: Deterministic Extraction (Week 2)

**Goal:** Extract markers from Deltas, generate harvest reports.

**Deliverables:**
```bash
# Can extract markers from Delta documents
jig extract --branch bootstrap --output harvest-001.yaml
cat harvest-001.yaml  # See structured marker data
```

**Implementation:**
- `src/jig/core/extractor.py` - Regex-based marker extraction
- `src/jig/delta/markers.py` - Marker definitions (#VIB, #OSTC, etc.)
- `src/jig/delta/harvest.py` - HarvestReport generation
- `src/jig/cli/extract.py` - Extract command
- `tests/unit/test_extractor.py` - Test suite

**Test Data:**
Create `jig/deltas/active/bootstrap/PLAN_bootstrap.md` with markers:
```markdown
#OSTC:Outcome "Extraction completes in <1 second for 1000 files"
#DISCOVERY:001 "Regex faster than AST parsing for markers"
#DECISION:001 "Use ripgrep for file scanning"
```

**Success Criteria:**
- Extracts all marker types (VIB, OSTC, DISCOVERY, DECISION, LEARNED)
- Runs in <1s for 100 files
- Generates valid YAML harvest report
- Test coverage >80%

---

### 2.3 Slice 2: Integration (Week 3)

**Goal:** Update OSTC files from harvest reports.

**Deliverables:**
```bash
# Can integrate harvest into Intent Graph
jig integrate --harvest harvest-001.yaml --approve all
jig validate  # Verify graph consistency
```

**Implementation:**
- `src/jig/core/integrator.py` - Update OSTC files
- `src/jig/core/graph.py` - Graph index management
- `src/jig/cli/integrate.py` - Integrate command
- `tests/integration/test_extract_integrate.py` - Round-trip test

**Test:**
```bash
# Extract markers → Integrate → Validate graph consistency
jig extract --branch bootstrap > harvest.yaml
jig integrate --harvest harvest.yaml --dry-run
jig integrate --harvest harvest.yaml --approve all
jig validate --check-all
```

**Success Criteria:**
- Creates new OSTC nodes from markers
- Updates existing nodes with references
- Maintains graph-index.yaml consistency
- Handles conflicts gracefully (human review)

---

### 2.4 Slice 3: Status & Validation (Week 4)

**Goal:** Git-like status command showing alignment health.

**Deliverables:**
```bash
jig status
# Shows:
# - Unharvested deltas
# - Alignment violations
# - Graph health
# - Recent changes
```

**Implementation:**
- `src/jig/cli/status.py` - Status command
- `src/jig/core/validator.py` - Extend validation
- `src/jig/utils/text.py` - Terminal formatting
- `tests/e2e/test_status_workflow.py`

**Success Criteria:**
- Runs in <100ms
- Clear, actionable output
- Shows delta harvest status
- Highlights violations

---

### 2.5 Slice 4: LLM Synthesis (Week 5-6)

**Goal:** LLM-assisted synthesis of harvest into Intent proposals.

**Deliverables:**
```bash
jig ai-synthesize --harvest harvest.yaml --output synthesis.yaml
cat synthesis.yaml  # See LLM-proposed OSTC nodes
```

**Implementation:**
- `src/jig/synthesis/synthesizer.py` - LLM orchestration
- `src/jig/synthesis/prompts.py` - Prompt engineering
- `src/jig/synthesis/conflict.py` - Conflict detection
- `src/jig/cli/ai_synthesize.py` - AI Synthesize command
- `tests/unit/test_synthesizer.py` - Mock LLM tests

**LLM Provider:**
- Start with Claude Sonnet 4.5 (Anthropic API)
- Make provider pluggable for future alternatives

**Test:**
```bash
# Mock LLM for tests
export JIG_LLM_MOCK=true
jig ai-synthesize --harvest harvest.yaml

# Real LLM
export ANTHROPIC_API_KEY=sk-...
jig ai-synthesize --harvest harvest.yaml
```

**Success Criteria:**
- Generates valid SynthesisProposal YAML
- Detects semantic conflicts
- Proposes reasonable abstractions
- Includes source traceability

---

### 2.6 Slice 5: Distill (High-Level) (Week 7)

**Goal:** One-command harvest workflow.

**Deliverables:**
```bash
jig ai-distill --branch bootstrap
# Runs: extract → ai-synthesize → ai-integrate (with review)
```

**Implementation:**
- `src/jig/cli/ai_distill.py` - Orchestrate pipeline
- Terminal UI for human review (approve/reject)
- `tests/e2e/test_full_distill.py`

**Success Criteria:**
- Single command completes full harvest
- Interactive approval for synthesis proposals
- Generates changelog automatically
- Links Deltas to OSTC nodes

---

### 2.7 Slice 6: Delta Lifecycle (Week 8)

**Goal:** Branch-bound Delta management.

**Deliverables:**
```bash
git checkout -b feature/new-work
jig delta new --type plan
# Edit jig/deltas/active/new-work/PLAN_new_work.md

git merge feature/new-work
jig delta archive --branch new-work --retention long-term
# Moves to jig/deltas/archive/
```

**Implementation:**
- `src/jig/delta/lifecycle.py` - Branch binding
- `src/jig/delta/templates.py` - Delta templates
- `src/jig/git_integration/branch.py` - Git integration
- `src/jig/cli/delta.py` - Delta commands

**Success Criteria:**
- Deltas tied to git branches
- Auto-archive on merge (optional hook)
- Template-based Delta creation
- Retention tier support

---

### 2.8 Slice 7: Decomposability Analysis (Week 9-10)

**Goal:** Measure and visualize subsystem boundaries.

**Deliverables:**
```bash
jig decompose --detect      # Auto-detect subsystems
jig decompose --metrics     # Calculate health scores
```

**Implementation:**
- `src/jig/decompose/detector.py` - Community detection
- `src/jig/decompose/metrics.py` - Modularity, coupling
- `src/jig/cli/decompose.py` - Decompose commands

**Algorithms:**
- Louvain method for community detection
- Newman modularity score
- Coupling ratio analysis

**Success Criteria:**
- Detects subsystems automatically
- Calculates modularity >0.5
- Runs in <5s for 10k LOC project

**Note:** Visualization (graph rendering) can be added later as a plugin/add-on.

---

### 2.9 Slice 8: Git Integration (Week 11)

**Goal:** Git hooks for harvest reminders.

**Deliverables:**
```bash
jig git install-hooks
# Installs pre-push hook that checks for unharvested deltas
```

**Implementation:**
- `src/jig/git_integration/hooks.py` - Hook installation
- `src/jig/git_integration/commit.py` - Commit parsing
- Git hook scripts in `.git/hooks/`

**Hooks:**
- `pre-push` - Warn if unharvested Deltas exist
- `post-merge` - Suggest archiving Deltas
- `commit-msg` - Parse OSTC references

---

### 2.10 Slice 9: Polish & Documentation (Week 12)

**Goal:** Production-ready v1.0.

**Deliverables:**
- Comprehensive user guide
- API documentation
- Performance benchmarks
- Packaging for PyPI

**Tasks:**
- Write docs/user-guide/QUICKSTART.md
- Generate API docs (Sphinx)
- Run benchmarks (extraction, validation, synthesis)
- Create PyPI package: `pip install jig-cli`

---

## Part 3: Technical Architecture

### 3.1 Data Formats

**HarvestReport (YAML):**
```yaml
metadata:
  timestamp: 2025-11-18T10:30:00Z
  branch: bootstrap
  base_commit: abc123
  delta_count: 3
  marker_count: 47

markers:
  - file: jig/deltas/active/bootstrap/PLAN.md
    line: 234
    type: VIB
    subtype: Value
    text: "Extraction must complete in <1s"

  - file: jig/deltas/active/bootstrap/PLAN.md
    line: 267
    type: OSTC
    subtype: Outcome
    id: O-JIG-001
    text: "Fast deterministic operations"

decisions:
  - id: D-001
    file: jig/deltas/active/bootstrap/PLAN.md
    line: 145
    title: "Regex vs AST for marker extraction"
    choice: regex
    rationale: "10x faster, simpler"
```

**SynthesisProposal (YAML):**
```yaml
synthesis:
  new_nodes:
    - id: S-JIG-001
      type: specification
      title: "Marker extraction runs in <1s for 1000 files"
      content: |
        The extractor MUST process 1000 Delta files in <1 second.
        Use ripgrep for file scanning, regex for marker parsing.
      source_deltas:
        - file: jig/deltas/active/bootstrap/PLAN.md
          line: 234
          marker: OSTC:Outcome
      subsystem: core

  conflicts:
    - existing_node: S-JIG-002
      proposed_node: S-JIG-001
      conflict_type: performance_threshold_mismatch
      resolution_needed: human_review
```

**OSTC Node (Markdown with YAML):**
```markdown
---
id: S-JIG-001
type: specification
title: "Marker extraction runs in <1s for 1000 files"
subsystem: core
---

The extractor MUST process 1000 Delta files in <1 second.

## Rationale
Fast feedback enables developers to harvest frequently without friction.

## Implementation
- Use ripgrep for file scanning
- Regex for marker parsing
- Parallel processing for large repos

## References
- Implements: O-JIG-001
- Tested by: T-JIG-005
- Source: jig/deltas/archive/bootstrap/PLAN.md:234
```

### 3.2 Key Algorithms

**Marker Extraction (Deterministic):**
```python
def extract_markers(delta_files: list[Path]) -> HarvestReport:
    """Extract all markers from Delta files using regex."""
    markers = []

    # Use ripgrep for fast file scanning
    result = subprocess.run(
        ["rg", r"#(VIB|OSTC|DISCOVERY|DECISION|LEARNED):", ...],
        capture_output=True
    )

    # Parse matches into structured data
    for line in result.stdout.splitlines():
        marker = parse_marker_line(line)
        markers.append(marker)

    return HarvestReport(markers=markers, ...)
```

**LLM Synthesis (Creative):**
```python
def synthesize(harvest: HarvestReport, graph: Graph) -> SynthesisProposal:
    """Use LLM to propose OSTC nodes from harvest."""

    prompt = build_synthesis_prompt(harvest, graph)

    response = anthropic_client.messages.create(
        model="claude-sonnet-4.5-20250929",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    proposal = parse_synthesis_response(response.content)
    return proposal
```

**Community Detection (Graph Analysis):**
```python
def detect_subsystems(graph: Graph) -> dict[str, Subsystem]:
    """Use Louvain method to detect subsystems."""
    import networkx as nx
    from networkx.algorithms import community

    G = graph.to_networkx()
    communities = community.louvain_communities(G)

    subsystems = {}
    for i, nodes in enumerate(communities):
        subsystems[f"subsystem_{i}"] = Subsystem(nodes=nodes)

    return subsystems
```

### 3.3 Performance Targets

| Operation | Target | Rationale |
|-----------|--------|-----------|
| `jig status` | <100ms | Must be instant (like `git status`) |
| `jig extract` | <1s | Deterministic, should be fast |
| `jig validate` | <1s | Runs frequently, must be fast |
| `jig integrate` | <1s | File I/O bound, should be quick |
| `jig ai-synthesize` | 30-60s | LLM call, inherently slow (acceptable) |
| `jig decompose` | <10s | Complex analysis, rare use |

---

## Part 4: Dogfooding Strategy

### 4.1 JIG Develops JIG Using JIG

**Principle:** Use JIG to build JIG from Day 1.

**How:**
1. **Initialize Intent Graph early** (Slice 0)
   - Create `jig/` with initial Outcomes
   - Example: `O-JIG-001: "Fast deterministic operations"`

2. **Write Deltas for each slice**
   - `jig/deltas/active/slice-1-extraction/PLAN_extraction.md`
   - Capture decisions, discoveries, learnings

3. **Harvest insights incrementally**
   - After each slice, run `jig ai-distill`
   - Update `jig/` with new specs and tests

4. **Measure decomposability continuously**
   - Run `jig decompose --metrics` weekly
   - Ensure coupling ratio >10:1

5. **Archive Deltas on slice completion**
   - Move to `jig/deltas/archive/` when done

### 4.2 Initial OSTC Nodes

**Outcomes:**
- `O-JIG-001`: "JIG tools run in <1 second for most operations"
- `O-JIG-002`: "JIG uses simple text formats (YAML + Markdown)"
- `O-JIG-003`: "JIG is composable (pipes work)"
- `O-JIG-004`: "JIG requires no external services (local-first)"
- `O-JIG-005`: "JIG demonstrates modularity >0.7"

**Specifications:**
- `S-JIG-001`: "Marker extraction processes 1000 files in <1s"
- `S-JIG-002`: "OSTC nodes use YAML frontmatter + Markdown"
- `S-JIG-003`: "Commands output valid YAML for piping"
- `S-JIG-004`: "Subsystems export <5 public interfaces each"

**Tests:**
- `T-JIG-001`: "test_extract_1000_files_under_1s"
- `T-JIG-002`: "test_yaml_frontmatter_parsing"
- `T-JIG-003`: "test_command_output_pipeable"

---

## Part 5: Technology Stack

### 5.1 Core Technologies

**Language:** Python 3.11+
- Reason: Rapid development, rich ecosystem, familiar to developers
- Alternatives considered: Rust (too slow to prototype), Go (less LLM library support)

**CLI Framework:** Click or Typer
- Reason: Composable, generates help automatically, testing support
- Start with Click (simpler), migrate to Typer if types become valuable

**YAML/Markdown:** PyYAML + python-frontmatter
- Reason: Standard libraries, battle-tested

**Graph Analysis:** NetworkX
- Reason: Community detection algorithms built-in
- Alternative: graph-tool (faster, but harder to install)

**LLM Integration:** Anthropic Python SDK
- Reason: Native Claude support, streaming, async
- Make pluggable for future OpenAI/local models

**Testing:** pytest + pytest-cov
- Reason: Industry standard, plugin ecosystem

**Packaging:** PEP 621 (pyproject.toml) + Poetry or Hatch
- Reason: Modern Python packaging, dependency management

### 5.2 Development Tools

**Linting/Formatting:**
- ruff (fast linter/formatter)
- mypy (type checking)

**Testing:**
- pytest (unit, integration, e2e)
- pytest-benchmark (performance tests)
- pytest-mock (mocking)

**Documentation:**
- Sphinx (API docs)
- MkDocs (user guide)

**CI/CD:**
- GitHub Actions (free, integrated)
- Run tests on Python 3.11, 3.12, 3.13

---

## Part 6: Development Principles

### 6.1 Build Philosophy

**1. Vertical Slices Over Horizontal Layers**
- Build complete workflows (extract → integrate) before adding features
- Delivers value early, tests real usage

**2. Dogfood Relentlessly**
- Use JIG to build JIG from Week 1
- Deltas for every slice, harvest regularly

**3. Simple > Clever**
- Regex over AST parsing
- YAML over SQL
- Grep over indexing

**4. Fast > Feature-Rich**
- Deterministic operations <1s
- Defer LLM synthesis (it's slow, that's OK)

**5. Explicit > Implicit**
- No magic: developers write markers
- No hidden state: everything in git

**6. Test Before Scale**
- Unit tests for algorithms
- Integration tests for workflows
- E2E tests for user journeys

### 6.2 Decision-Making Framework

When choosing between alternatives:

1. **Speed**: Will this slow down developers?
2. **Simplicity**: Can it be explained in one sentence?
3. **Composability**: Can it be piped/chained?
4. **Debuggability**: Can developers inspect state easily?
5. **Alignment**: Does this match JIG philosophy?

---

## Part 7: Risk Management

### 7.1 Known Risks

| Risk | Mitigation |
|------|------------|
| **LLM synthesis quality** | Human review always required; start with conservative prompts |
| **Performance degrades with scale** | Benchmark continuously; use ripgrep, parallel processing |
| **Marker syntax too verbose** | Start minimal, add features based on user feedback |
| **Graph complexity explodes** | Enforce subsystem boundaries; detect violations early |
| **Dependencies conflict** | Pin versions; minimal dependency tree |

### 7.2 Validation Checkpoints

**After Each Slice:**
- [ ] All tests pass (>80% coverage)
- [ ] Performance targets met
- [ ] Dogfooding successful (used on JIG itself)
- [ ] Documentation updated
- [ ] Delta harvested into `.jig/`

**Before v1.0 Release:**
- [ ] Full e2e workflow tested on 3+ real projects
- [ ] Decomposability metrics >0.7 for JIG itself
- [ ] User guide complete
- [ ] PyPI package published
- [ ] Performance benchmarks documented

---

## Part 8: Success Criteria

### 8.1 Technical Success

**Functionality:**
- [ ] Extract markers from Deltas (all types)
- [ ] Integrate harvest into OSTC graph
- [ ] LLM synthesis generates valid proposals
- [ ] Status shows alignment health
- [ ] Decomposability analysis detects subsystems
- [ ] Git integration works (hooks, archiving)

**Performance:**
- [ ] `jigy status` <100ms
- [ ] `jigy extract` <1s for 1000 files
- [ ] `jigy validate` <1s for 1000 nodes
- [ ] `jigy decompose` <10s for 10k LOC

**Quality:**
- [ ] Test coverage >80%
- [ ] Type hints throughout (mypy clean)
- [ ] Passes ruff linting
- [ ] Zero critical bugs

### 8.2 Dogfooding Success

**JIG building JIG:**
- [ ] `jig/` contains 50+ OSTC nodes
- [ ] 10+ Deltas written and harvested
- [ ] Modularity score >0.7 for JIG codebase
- [ ] Coupling ratio >10:1 for all subsystems
- [ ] All development decisions captured in Deltas

### 8.3 User Success

**Adoption:**
- [ ] 3+ external projects pilot JIG
- [ ] User guide tested by non-authors
- [ ] Installation <5 minutes
- [ ] First harvest <10 minutes

**Note:** Visualization features are intentionally deferred as they can be added later as plugins/add-ons, allowing focus on core functionality first.

---

## Part 9: Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Slice 0: Bootstrap** | Week 1 | `jig init`, `jig validate` |
| **Slice 1: Extraction** | Week 2 | `jig extract`, HarvestReport |
| **Slice 2: Integration** | Week 3 | `jig integrate`, graph updates |
| **Slice 3: Status** | Week 4 | `jig status`, alignment health |
| **Slice 4: Synthesis** | Weeks 5-6 | `jig ai-synthesize`, LLM integration |
| **Slice 5: Distill** | Week 7 | `jig ai-distill`, full pipeline |
| **Slice 6: Delta Lifecycle** | Week 8 | Delta management, archiving |
| **Slice 7: Decompose** | Weeks 9-10 | Subsystem detection, metrics |
| **Slice 8: Git Integration** | Week 11 | Hooks, branch binding |
| **Slice 9: Polish** | Week 12 | Docs, packaging, v1.0 release |

**Total:** 12 weeks to v1.0 (assuming 1 developer, part-time)

---

## Part 10: Next Steps

### Immediate Actions (This Week)

1. **Set up project structure**
   ```bash
   mkdir -p src/jig/{cli,core,delta,synthesis,decompose,git_integration,utils}
   touch src/jig/__init__.py
   touch src/jig/cli/main.py
   ```

2. **Create pyproject.toml**
   ```toml
   [project]
   name = "jig-cli"
   version = "0.1.0"
   dependencies = ["click", "pyyaml", "python-frontmatter", "networkx"]
   ```

3. **Initialize jig/ (dogfooding)**
   ```bash
   mkdir -p jig/{outcomes,specifications,tests}
   # Create O-JIG-001, S-JIG-001, etc.
   ```

4. **Create first Delta**
   ```bash
   mkdir -p jig/deltas/active/bootstrap/
   # Write PLAN_bootstrap.md
   ```

5. **Write first test**
   ```bash
   mkdir -p tests/unit
   # Write test_extractor.py (TDD style)
   ```

### First Development Cycle (Slice 0)

**Branch:** `feature/bootstrap`

**Delta:** `jig/deltas/active/bootstrap/PLAN_bootstrap.md`

**Commits:**
1. "Project structure scaffolding"
2. "Add pyproject.toml and dependencies"
3. "Implement jigy init command"
4. "Implement jigy validate command"
5. "Add tests for init and validate"
6. "Harvest bootstrap insights"

**Expected Duration:** 3-5 days

---

## Conclusion

This strategy builds JIG using JIG's own principles:

1. **Nearly decomposable architecture** - Clear subsystem boundaries
2. **Vertical slices** - Complete workflows, not layers
3. **Dogfooding** - JIG builds JIG using Deltas and Intent
4. **Simple, fast, composable** - Following git's philosophy
5. **Explicit over magic** - Developers control everything

**The ultimate validation:** If JIG can build JIG, it proves the concept works.

---

**Status:** Ready to begin Slice 0
**Next:** Create project structure and start dogfooding
