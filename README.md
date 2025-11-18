# JIG: Jig Intent Graph

**Git-native constraint-driven development for nearly decomposable systems**

JIG treats software development as maintaining alignment across four representations of truth:

- **Outcome (O)**: What business value we deliver
- **Specification (S)**: What technical requirements we satisfy
- **Test (T)**: How we verify correctness
- **Code (C)**: What actually runs

## Philosophy

Like git transformed version control by being fast, simple, text-based, and distributed, JIG transforms Intent management with the same principles:

- **Fast**: grep-speed extraction (<1s for 10k files)
- **Simple**: YAML + Markdown, no databases
- **Git-native**: Branch-scoped deltas, content-addressed nodes
- **Powerful**: Decomposability analysis, harvest pipeline

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourorg/jig.git
cd jig

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Verify installation
jigy --version
```

### Initialize a Project

```bash
# Initialize JIG in your project
jigy init

# This creates:
# jig/
# ├── outcomes/         # Business outcomes (O nodes)
# ├── specifications/   # Technical specs (S nodes)
# ├── constraints/      # Design constraints (C nodes)
# ├── graph-index.yaml  # Node and edge registry
# └── subsystems.yaml   # Subsystem definitions
```

### Create Intent Nodes

```bash
# Create an Outcome node
jigy node create --type outcome \
  --id O-AUTH-001 \
  --title "Users authenticate securely" \
  --subsystem auth

# Create a Specification node
jigy node create --type specification \
  --id S-AUTH-001 \
  --title "JWT tokens with 24-hour expiration" \
  --subsystem auth

# Validate your Intent graph
jigy validate
```

## Core Concepts

### OSTC Model

- **Outcome**: Narrative truth (why) - lives in `jig/outcomes/`
- **Specification**: Logical truth (what) - lives in `jig/specifications/`
- **Test**: Empirical truth (verify) - marked with `@jig` annotations in test code
- **Code**: Operational truth (how) - marked with `@jig` annotations in source

### Nearly Decomposable Systems

JIG helps measure and maintain architectural boundaries:

- **Coupling ratio**: Internal edges / external edges (target: >10:1)
- **Modularity**: Newman-Girvan score (target: >0.5)
- **Module depth**: LOC / exports (target: >100:1)

### Deltas: Temporal Work Artifacts

Deltas capture the narrative of change, tied to git branches:

- Active deltas: `jig/deltas/active/{branch}/`
- Archived deltas: `jig/deltas/archive/{branch}/`
- Harvest markers: `#DISCOVERY`, `#LEARNED`, `#DECISION`

## Development

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/jig --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_config.py -v
```

### Code Quality

```bash
# Run linter
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Type checking
mypy src/
```

## Requirements

- Python 3.11 or higher
- No external services required for core functionality
- Optional: API keys for `jigy ai-*` commands

## Project Status

**Current version**: 0.1.0-bootstrap
**Status**: Active development - Slice 0 (Bootstrap Infrastructure)

See `docs/wip/PLAN_slice_0_bootstrap.md` for current roadmap.

## License

MIT

## Documentation

Full documentation available in `docs/`:

- Architecture: `docs/jig-concept/JIG-Concept-v6.1.md`
- Implementation Plan: `docs/wip/PLAN_slice_0_bootstrap.md`
- Data Formats: (coming in WU10)

## Authors

Jim Meyer & Claude

---

*"Intent documented. Deltas harvested. Boundaries preserved. Alignment maintained."*
