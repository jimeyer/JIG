# Architecture Report: JIG Core vs JIG AI

**Date:** 2025-11-16
**Status:** Design Proposal
**Question:** How should JIG distinguish between deterministic operations and AI-augmented operations?

---

## Executive Summary

**The Core Insight:**

JIG should have a **bright line** between deterministic core operations (fast, correct, stable) and AI-augmented operations (slow, evolving, customizable).

**Recommended Architecture:**

1. **JIG Core**: All deterministic operations, git-like philosophy
2. **AI Namespace**: `jigy ai-*` commands for AI operations, clearly distinct
3. **Plugin System**: Future extensibility for multiple AI backends and user customization
4. **Clear Contracts**: Structured data formats (YAML/JSON) as interface between layers

**Key Principle:**

> "JIG Core is like git. JIG AI is like GitHub Copilot. The core is stable and deterministic. The AI is evolving and optional."

---

## 1. The Philosophical Question

### 1.1 Two Types of Operations

JIG will have operations with fundamentally different characteristics:

| Aspect | Deterministic Ops | AI Ops |
|--------|------------------|--------|
| **Speed** | <1 second | 30-60 seconds |
| **Correctness** | Provably correct | Probabilistically useful |
| **Stability** | Stable contract | Evolving prompts |
| **Versioning** | Semantic versioning | Model-dependent |
| **Customization** | Config files | Prompt engineering |
| **Offline** | Always works | Requires API/model |
| **Trust** | Deterministic | Requires validation |

**Example:**

```bash
# Deterministic: Find all #DISCOVERY markers in Deltas
jigy extract --branch bike-relay
# Output: Always finds exact same markers
# Speed: <1s for 1000 files
# Correctness: 100% (regex match)

# AI: Synthesize markers into OSTC proposals
jigy synthesize --harvest report.yaml
# Output: Varies by model, prompts, temperature
# Speed: 30-60s
# Correctness: Requires human review
```

### 1.2 The Problem

**If we don't make this distinction clear:**
- Users won't know which operations are fast/slow
- Developers won't know which code is stable/evolving
- AI improvements will require core changes
- Can't swap AI backends easily
- Can't skip AI operations when needed

**Git's example:**
Git has NO non-deterministic operations. Every command is fast and deterministic. This is part of why it's trusted.

**JIG's challenge:**
We WANT AI assistance, but we need to preserve the git-like trust in the core.

---

## 2. Architectural Options

### 2.1 Option 1: AI-Prefixed Commands (RECOMMENDED)

```bash
# Core JIG (deterministic)
jigy extract       # Find markers
jigy validate      # Check OSTC graph
jigy integrate     # Update OSTC files
jigy status        # Show alignment status
jigy graph         # Generate graph visualization

# AI JIG (non-deterministic)
jigy ai-synthesize # LLM synthesis
jigy ai-distill    # Full pipeline with AI
jigy ai-suggest    # Suggest OSTC improvements
jigy ai-explain    # Explain alignment violations
```

**Pros:**
- **Crystal clear** what uses AI
- Easy to grep: `jigy ai-*`
- Mental model: "ai-" = slow, requires review
- Can document separately
- Users can skip entire `ai-*` namespace

**Cons:**
- Verbose (6 extra characters)
- Namespace collision if we add other prefixes

**Verdict:** Best balance of clarity and simplicity.

### 2.2 Option 2: Plugin Architecture

```bash
# Core JIG
jigy extract
jigy integrate
jigy validate

# Plugins
jigy plugin:ai synthesize
jigy plugin:gpt4 synthesize
jigy plugin:claude synthesize
jigy plugin:local-llama synthesize

# Plugin management
jigy plugin list
jigy plugin install jigy-ai-claude
jigy plugin configure ai
```

**Pros:**
- Maximum extensibility
- Multiple AI backends
- Users can write custom plugins
- Complete separation
- Can ship AI as optional package

**Cons:**
- More complex architecture
- Plugin system overhead
- Discoverability harder

**Verdict:** Good for future, but over-engineered for v1.

### 2.3 Option 3: Separate Binary

```bash
# Core binary: jigy
jigy extract
jigy validate
jigy integrate

# AI binary: jigy-ai (separate package)
jigy-ai synthesize
jigy-ai distill
jigy-ai suggest

# Optional: symlink for convenience
jigy ai synthesize  # → jigy-ai synthesize
```

**Pros:**
- Complete separation
- AI is optional dependency
- Can version independently
- Clear what requires API keys

**Cons:**
- Two tools to install
- Path management
- Users might not realize they're separate

**Verdict:** Interesting, but violates "single tool" simplicity.

### 2.4 Option 4: Explicit Flags

```bash
jigy synthesize --manual        # Template-based (deterministic)
jigy synthesize --ai            # LLM-based (non-deterministic)
jigy synthesize --ai-model=claude-sonnet-4.5

jigy distill --manual           # Extract + manual review
jigy distill --ai               # Extract + AI synthesis
```

**Pros:**
- Single command, multiple modes
- Flexible

**Cons:**
- Not obvious without `--help`
- Harder to maintain radically different implementations
- Flag fatigue

**Verdict:** Not clear enough about AI usage.

---

## 3. Recommended Architecture: Layered with AI Namespace

### 3.1 The Two-Layer Model

```
┌─────────────────────────────────────────────────────────┐
│                    JIG Architecture                      │
└─────────────────────────────────────────────────────────┘

Layer 1: JIG CORE (Deterministic, Stable)
┌──────────────────────────────────────────┐
│ Commands:                                │
│  - jigy extract                          │
│  - jigy validate                         │
│  - jigy integrate                        │
│  - jigy status                           │
│  - jigy graph                            │
│  - jigy delta (new/archive)              │
│  - jigy decompose (metrics)              │
│                                          │
│ Characteristics:                         │
│  - Fast (<1s)                            │
│  - Deterministic (same input = output)   │
│  - No network required                   │
│  - Stable contracts                      │
│  - Core JIG philosophy                   │
└──────────────────────────────────────────┘

Layer 2: JIG AI (Non-deterministic, Evolving)
┌──────────────────────────────────────────┐
│ Commands:                                │
│  - jigy ai-synthesize                    │
│  - jigy ai-distill                       │
│  - jigy ai-suggest                       │
│  - jigy ai-explain                       │
│  - jigy ai-review                        │
│                                          │
│ Characteristics:                         │
│  - Slow (30-60s)                         │
│  - Non-deterministic (varies)            │
│  - Requires LLM API or model             │
│  - Evolving prompts                      │
│  - User-customizable                     │
└──────────────────────────────────────────┘

Interface: Structured Data (YAML/JSON)
┌──────────────────────────────────────────┐
│ - HarvestReport (extract → ai-synthesize)│
│ - SynthesisProposal (ai-synthesize → int)│
│ - ValidationReport (validate → ai-explain)│
│ - OSTCGraph (graph → ai-suggest)         │
└──────────────────────────────────────────┘
```

### 3.2 Command Catalog

**JIG Core (Deterministic):**

```bash
# Extraction (parsing, regex)
jigy extract --branch bike-relay --output harvest.yaml

# Validation (graph algorithms, schema checking)
jigy validate --check-all
jigy validate --check-references
jigy validate --check-boundaries

# Integration (file I/O, YAML updates)
jigy integrate --synthesis synthesis.yaml --approve all

# Status (fast queries)
jigy status                    # Overall alignment status
jigy status --subsystem auth   # Subsystem-specific

# Graph (graph generation, deterministic layout)
jigy graph --mode subsystem
jigy graph --output graph.dot

# Delta management
jigy delta new --type plan
jigy delta archive --branch bike-relay

# Decomposability (metrics calculation)
jigy decompose --detect
jigy decompose --metrics
```

**JIG AI (Non-deterministic):**

```bash
# Synthesis (LLM-powered understanding)
jigy ai-synthesize --harvest harvest.yaml --output synthesis.yaml

# Distillation (full pipeline with AI)
jigy ai-distill --branch bike-relay

# Suggestion (AI-powered recommendations)
jigy ai-suggest --subsystem auth
jigy ai-suggest --improve-modularity

# Explanation (AI narrative generation)
jigy ai-explain --violation V-042
jigy ai-explain --why "S-AUTH-001 missing test"

# Review (AI-assisted code review)
jigy ai-review --branch bike-relay
jigy ai-review --focus decomposability
```

### 3.3 The Contract: Structured Data

**Core produces data, AI consumes data:**

```yaml
# HarvestReport (extract → ai-synthesize)
# Produced by: jigy extract
# Consumed by: jigy ai-synthesize

metadata:
  timestamp: 2025-11-16T14:32:00Z
  branch: bike-echoform-relay
  marker_count: 47

markers:
  - file: docs/deltas/active/bike-relay/PLAN.md
    line: 234
    type: DISCOVERY
    text: "OR-Set requires hashable elements"
```

```yaml
# SynthesisProposal (ai-synthesize → integrate)
# Produced by: jigy ai-synthesize
# Consumed by: jigy integrate

synthesis:
  new_nodes:
    - id: S-CRDT-042
      type: specification
      title: "CRDT operations validate input types"
      content: |
        All CRDT operations MUST validate input types.
```

**This means:**
- Core doesn't care HOW synthesis happens (AI, manual, template)
- AI doesn't care HOW extraction happens (regex, AST parsing)
- Both can evolve independently
- Users can skip AI and manually create SynthesisProposal

---

## 4. Evolution Strategy

### 4.1 Phase 1: Core First (Months 1-2)

**Ship JIG Core without AI:**

```bash
# Working commands
jigy extract        # ✓ Deterministic extraction
jigy validate       # ✓ Graph validation
jigy integrate      # ✓ OSTC updates
jigy status         # ✓ Alignment status
jigy graph          # ✓ Visualization

# Manual workflow (no AI)
jigy extract --branch bike-relay --output harvest.yaml
# Human manually reviews harvest.yaml
# Human manually creates synthesis.yaml
jigy integrate --synthesis synthesis.yaml --review
```

**Benefits:**
- Core is stable and useful without AI
- Users can adopt incrementally
- Proves value of deterministic tools
- Establishes contracts

### 4.2 Phase 2: Basic AI (Months 3-4)

**Add AI synthesis with Claude:**

```bash
# New commands
jigy ai-synthesize --harvest harvest.yaml --output synthesis.yaml
jigy ai-distill --branch bike-relay

# Workflow with AI
jigy extract --branch bike-relay --output harvest.yaml
jigy ai-synthesize --harvest harvest.yaml --output synthesis.yaml
jigy integrate --synthesis synthesis.yaml --review
```

**Implementation:**
- Hardcode Claude Sonnet 4.5 prompts
- Simple prompt templates
- No customization yet

### 4.3 Phase 3: Customization (Months 5-6)

**Add prompt customization:**

```bash
# Custom prompts
jigy ai-synthesize --prompt-file my-prompts.yaml

# Custom model
jigy ai-synthesize --model gpt-4

# Configuration
~/.jig/ai-config.yaml:
  model: claude-sonnet-4.5
  temperature: 0.1
  prompts:
    synthesis: custom-synthesis-prompt.txt
```

### 4.4 Phase 4: Plugin System (Months 7+)

**Add plugin architecture:**

```bash
# Multiple AI backends
jigy plugin install jigy-ai-claude
jigy plugin install jigy-ai-gpt4
jigy plugin install jigy-ai-local

# Plugin commands
jigy ai-synthesize --backend claude
jigy ai-synthesize --backend gpt4
jigy ai-synthesize --backend local

# User plugins
jigy plugin install my-custom-ai
jigy ai-synthesize --backend my-custom
```

**Plugin API:**

```python
# jigy/plugins/base.py
class AIPlugin:
    def synthesize(self, harvest: HarvestReport) -> SynthesisProposal:
        """Must return valid SynthesisProposal"""
        raise NotImplementedError

# User plugin
class MyCustomAI(AIPlugin):
    def synthesize(self, harvest):
        # Custom logic here
        return SynthesisProposal(...)
```

---

## 5. User Experience

### 5.1 Discoverability

```bash
# Help clearly distinguishes
jigy --help

JIG: Jig Intent Graph v6.0

Core Commands (deterministic, <1s):
  extract        Extract markers from Deltas
  validate       Validate OSTC graph integrity
  integrate      Integrate synthesis into OSTC
  status         Show alignment status
  graph          Generate graph visualization
  delta          Manage Delta documents
  decompose      Analyze decomposability

AI Commands (requires LLM, 30-60s):
  ai-synthesize  Synthesize harvest into OSTC proposals
  ai-distill     Full distillation pipeline with AI
  ai-suggest     Get AI suggestions for improvements
  ai-explain     AI explanation of violations
  ai-review      AI-assisted code review

Run 'jigy <command> --help' for more information.
```

### 5.2 Configuration

```yaml
# ~/.jig/config.yaml

[core]
version = "6.0"

[ai]
enabled = true
backend = "claude"  # claude, gpt4, local
model = "claude-sonnet-4.5"
temperature = 0.1
api_key_env = "ANTHROPIC_API_KEY"

[ai.prompts]
synthesis = "~/.jig/prompts/synthesis.txt"
suggest = "~/.jig/prompts/suggest.txt"

[ai.cost]
warn_threshold_usd = 1.00  # Warn if operation > $1
monthly_limit_usd = 50.00
```

### 5.3 Opt-Out

```bash
# Users can completely skip AI
jigy extract --branch bike-relay --output harvest.yaml

# Manual synthesis (template-based)
jigy synthesize --manual --harvest harvest.yaml
# Opens editor with template for human to fill

jigy integrate --synthesis synthesis.yaml
```

---

## 6. Implementation Architecture

### 6.1 Directory Structure

```
jigy/
├── core/                   # Deterministic operations
│   ├── extract.py          # Marker extraction
│   ├── validate.py         # Graph validation
│   ├── integrate.py        # OSTC updates
│   ├── graph.py            # Graph algorithms
│   └── models.py           # Data models (HarvestReport, etc.)
│
├── ai/                     # AI operations (optional)
│   ├── synthesize.py       # LLM synthesis
│   ├── suggest.py          # AI suggestions
│   ├── explain.py          # AI explanations
│   ├── backends/           # AI backend implementations
│   │   ├── claude.py
│   │   ├── gpt4.py
│   │   └── local.py
│   └── prompts/            # Prompt templates
│       ├── synthesis.txt
│       └── suggest.txt
│
├── cli/                    # Command-line interface
│   ├── core_commands.py    # extract, validate, integrate
│   ├── ai_commands.py      # ai-*, clearly separated
│   └── main.py             # Dispatcher
│
├── plugins/                # Plugin system (future)
│   ├── base.py             # Plugin interface
│   └── loader.py           # Plugin discovery
│
└── tests/
    ├── core/               # Fast, deterministic tests
    └── ai/                 # Slow, requires API keys
```

### 6.2 Dependency Management

```toml
# pyproject.toml

[project]
name = "jigy"
dependencies = [
    "pyyaml",
    "networkx",       # Graph algorithms
    "rich",           # Terminal UI
]

[project.optional-dependencies]
ai = [
    "anthropic",      # Claude API
    "openai",         # GPT API
    "transformers",   # Local models
]

# Install core only
pip install jigy

# Install with AI
pip install jigy[ai]
```

### 6.3 Testing Strategy

```python
# tests/core/test_extract.py (fast, no mocks)
def test_extract_discovery_markers():
    """Deterministic: always finds exact markers"""
    delta = "docs/deltas/test.md"
    report = extract(delta)
    assert len(report.discoveries) == 3
    assert report.discoveries[0].text == "OR-Set requires hashable"

# tests/ai/test_synthesize.py (slow, mocked by default)
@pytest.mark.ai
@pytest.mark.slow
def test_synthesize_creates_spec():
    """AI: creates reasonable OSTC proposal"""
    harvest = HarvestReport.load("test-harvest.yaml")
    proposal = ai_synthesize(harvest)
    assert len(proposal.new_nodes) > 0
    assert proposal.new_nodes[0].type == "specification"
```

```bash
# Fast tests only (CI)
pytest tests/core/

# All tests including AI (requires API keys)
pytest tests/ --run-ai
```

---

## 7. AI Backend Abstraction

### 7.1 Backend Interface

```python
# jigy/ai/backends/base.py

from abc import ABC, abstractmethod
from jigy.core.models import HarvestReport, SynthesisProposal

class AIBackend(ABC):
    """Abstract interface for AI backends"""

    @abstractmethod
    def synthesize(
        self,
        harvest: HarvestReport,
        intent_context: str
    ) -> SynthesisProposal:
        """Synthesize harvest into OSTC proposals"""
        pass

    @abstractmethod
    def suggest(
        self,
        graph: OSTCGraph,
        focus: str
    ) -> List[Suggestion]:
        """Suggest improvements to OSTC graph"""
        pass

    @abstractmethod
    def explain(
        self,
        violation: Violation
    ) -> str:
        """Explain an alignment violation"""
        pass
```

### 7.2 Claude Backend

```python
# jigy/ai/backends/claude.py

from anthropic import Anthropic
from .base import AIBackend

class ClaudeBackend(AIBackend):
    def __init__(self, model="claude-sonnet-4.5", temperature=0.1):
        self.client = Anthropic()
        self.model = model
        self.temperature = temperature

    def synthesize(self, harvest, intent_context):
        prompt = self._build_synthesis_prompt(harvest, intent_context)

        response = self.client.messages.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_synthesis_response(response.content)

    def _build_synthesis_prompt(self, harvest, context):
        # Load template
        template = load_prompt_template("synthesis.txt")
        return template.format(
            harvest=harvest.to_yaml(),
            context=context
        )
```

### 7.3 User Custom Backend

```python
# ~/.jigy/plugins/my_backend.py

from jigy.ai.backends.base import AIBackend

class MyCustomBackend(AIBackend):
    """My company's custom LLM integration"""

    def synthesize(self, harvest, intent_context):
        # Call internal API
        result = my_company_llm.synthesize(
            data=harvest.to_yaml(),
            context=intent_context,
            style="formal"
        )

        # Parse into SynthesisProposal
        return SynthesisProposal.from_dict(result)
```

```bash
# Register plugin
jigy plugin register ~/.jigy/plugins/my_backend.py

# Use it
jigy ai-synthesize --backend my-custom
```

---

## 8. Cost and Performance Transparency

### 8.1 Cost Warnings

```bash
# Before expensive operation
jigy ai-distill --branch bike-relay

⚠ This operation will make ~5 LLM API calls
Estimated cost: $0.75 USD
Continue? [y/N]: y

Processing...
✓ Synthesis complete (47 markers → 12 OSTC nodes)
Actual cost: $0.68 USD
```

### 8.2 Performance Reporting

```bash
jigy status --verbose

JIG Status:
  Core operations:
    - Extract: 0.84s (1,234 files)
    - Validate: 0.12s (89 nodes, 234 edges)

  AI operations (last 7 days):
    - ai-synthesize: 3 runs, avg 42s
    - ai-distill: 1 run, 58s
    - Total cost: $2.34 USD
```

---

## 9. Migration and Compatibility

### 9.1 Backward Compatibility

**Promise:** Core commands never break.

```bash
# JIG v6.0
jigy extract --branch bike-relay

# JIG v7.0 (future)
jigy extract --branch bike-relay
# Still works exactly the same
```

### 9.2 AI Evolution

**AI commands can change rapidly:**

```bash
# JIG v6.0
jigy ai-synthesize --harvest report.yaml
# Uses claude-sonnet-4.5

# JIG v6.1
jigy ai-synthesize --harvest report.yaml
# Uses claude-sonnet-5.0 (better prompts, different output)
# But SynthesisProposal format is stable
```

### 9.3 Deprecation Policy

**Core:** Semantic versioning, 1-year deprecation notice
**AI:** Can change anytime, documented in release notes

---

## 10. Recommended Decisions

### 10.1 CLI Namespace: `jigy ai-*`

**Decision:** Use `ai-` prefix for all AI operations.

**Rationale:**
- Crystal clear what uses AI
- Easy to grep and document
- Users can skip entire namespace
- Aligns with git philosophy (clear, explicit)

**Alternative considered:** Plugin system
**Why not:** Over-engineered for v1, can add later

### 10.2 Core-First Development

**Decision:** Ship core without AI, add AI later.

**Rationale:**
- Validates deterministic tools are useful
- Core is stable foundation
- Users can adopt incrementally
- Reduces initial complexity

### 10.3 Structured Data Contracts

**Decision:** YAML/JSON interfaces between core and AI.

**Rationale:**
- Loose coupling
- Swappable AI backends
- Can skip AI entirely
- Testable independently

### 10.4 Optional AI Dependency

**Decision:** AI features require `pip install jigy[ai]`.

**Rationale:**
- Core has no LLM dependencies
- Faster install for core-only users
- Clear what requires API keys
- Reduces attack surface

---

## 11. Example Workflows

### 11.1 Core-Only Workflow (No AI)

```bash
# Extract markers
jigy extract --branch bike-relay --output harvest.yaml

# Review harvest manually
cat harvest.yaml

# Create synthesis manually (template-based)
jigy synthesize --manual --harvest harvest.yaml --output synthesis.yaml
# Opens editor with template:
# synthesis:
#   new_nodes:
#     - id: S-???
#       type: specification
#       title: ???

# Integrate
jigy integrate --synthesis synthesis.yaml --review
```

### 11.2 AI-Assisted Workflow

```bash
# Extract (deterministic)
jigy extract --branch bike-relay --output harvest.yaml

# Synthesize with AI (non-deterministic)
jigy ai-synthesize --harvest harvest.yaml --output synthesis.yaml

# Review AI proposal
cat synthesis.yaml

# Integrate (deterministic)
jigy integrate --synthesis synthesis.yaml --approve all
```

### 11.3 Convenience Workflow

```bash
# One command (includes AI)
jigy ai-distill --branch bike-relay

# What it does:
# 1. jigy extract (fast)
# 2. jigy ai-synthesize (slow)
# 3. jigy integrate --review (interactive)
```

---

## 12. Open Questions

### 12.1 Should AI commands fail gracefully without API keys?

**Option A:** Error immediately
```bash
jigy ai-synthesize
Error: AI backend not configured. Run 'jigy ai-setup'
```

**Option B:** Fall back to manual
```bash
jigy ai-synthesize
Warning: No AI backend configured, falling back to manual
Opening editor...
```

**Recommendation:** Option A (explicit better than implicit)

### 12.2 Should core commands have AI hooks?

**Option A:** Separate commands only
```bash
jigy extract    # Never calls AI
jigy validate   # Never calls AI
```

**Option B:** Optional AI enhancement
```bash
jigy validate --ai-explain  # Explains violations with AI
jigy status --ai-suggest    # Suggests fixes with AI
```

**Recommendation:** Option B for convenience, but clearly documented

### 12.3 Should we support local models?

**Yes, but later:**
```bash
# Phase 4+
jigy ai-synthesize --backend local --model llama-3
```

Requires:
- More prompt engineering (local models less capable)
- Different performance characteristics
- Different cost model

---

## 13. Conclusion

### 13.1 The Bright Line

JIG must maintain a **bright line** between:

**Deterministic Core:**
- Fast (<1s)
- Correct (provably)
- Stable (semantic versioning)
- Offline (no network)
- Trustworthy (like git)

**AI Augmentation:**
- Slow (30-60s)
- Useful (probabilistically)
- Evolving (rapid iteration)
- Online (requires API)
- Assistive (requires review)

### 13.2 The Architecture

**Recommended:**
1. CLI namespace: `jigy ai-*` for all AI operations
2. Core-first development: Ship without AI, add later
3. Structured contracts: YAML/JSON between layers
4. Optional dependency: `pip install jigy[ai]`
5. Backend abstraction: Support multiple AI providers

### 13.3 The Philosophy

> "JIG Core is git for Intent. JIG AI is Copilot for alignment."

Git never tries to be smart—it's fast, correct, and trustworthy.
Copilot is smart but requires review.

JIG should follow the same model:
- Core operations: Trust by default
- AI operations: Verify always

### 13.4 The Evolution Path

**Phase 1 (Months 1-2):** Core only, no AI
**Phase 2 (Months 3-4):** Add `jigy ai-*` commands with Claude
**Phase 3 (Months 5-6):** Add customization (prompts, models)
**Phase 4 (Months 7+):** Add plugin system for multiple backends

---

## 14. Recommended Next Steps

1. **Adopt `jigy ai-*` namespace** for all AI operations
2. **Ship JIG Core v6.0** without AI (deterministic only)
3. **Define structured data contracts** (HarvestReport, SynthesisProposal)
4. **Plan AI integration** for v6.1 with Claude backend
5. **Design plugin API** for future extensibility

---

**Status:** Proposal
**Decision Required:** CLI namespace for AI operations
**Recommendation:** `jigy ai-*` prefix with future plugin system
**Reading Time:** ~20 minutes

---

*"The core must be rock-solid and deterministic, like git. The AI layer is helpful but optional, like Copilot. Make the distinction obvious."*
