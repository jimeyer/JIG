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

**Recommended: Using Make (Linux/macOS)**

```bash
# Clone the repository
git clone https://github.com/yourorg/jig.git
cd jig

# One-command setup with dev dependencies
make dev-setup

# Activate the virtual environment
source .venv/bin/activate

# Verify installation
jigy --version
```

**Alternative: Manual Installation (All platforms)**

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

> **Note**: For production use, run `make install` or `pip install -e .` (without dev dependencies)

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
  --subsystem identity.auth

# Create a Specification node
jigy node create --type specification \
  --id S-AUTH-001 \
  --title "JWT tokens with 24-hour expiration" \
  --subsystem identity.auth

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
- **Modularity**: Newman-Girvan score (target: >0.7)
- **Module depth**: LOC / exports (target: >100:1)

### Nested Subsystems

Organize large projects hierarchically with nested subsystems:

```yaml
# graph-index.yaml
subsystems:
  identity:
    description: "User identity management"
    subsystems:
      auth:
        description: "Authentication"
        nodes: [O-AUTH-001, S-AUTH-001]
      profile:
        description: "User profiles"
        nodes: [O-USER-001, S-USER-001]

  commerce:
    description: "E-commerce features"
    subsystems:
      catalog:
        nodes: [O-CATALOG-001]
      cart:
        nodes: [O-CART-001]
```

**Benefits:**
- Scales to 20+ subsystems without clutter
- Multi-level analysis (parent + leaf metrics)
- Better coupling ratios (sibling edges internal to parent)
- Reflects real system architecture

**Commands:**
```bash
# View hierarchical tree
jigy status

# Query subtree recursively
jigy graph list --subsystem identity --recursive

# Analyze subsystem metrics
jigy decompose metrics --subsystem identity
```

See [Nested Subsystems Guide](docs/user-guide/NESTED_SUBSYSTEMS.md) for details.

### Deltas: Temporal Work Artifacts

Deltas capture the narrative of change, tied to git branches:

- Active deltas: `jig/deltas/active/{branch}/`
- Archived deltas: `jig/deltas/archive/{branch}/`
- Harvest markers: `#DISCOVERY`, `#LEARNED`, `#DECISION`

## Development

### Run Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file (activate venv first)
pytest tests/unit/test_config.py -v
```

### Code Quality

```bash
# Run linter
make lint

# Format code
make format

# Type checking
make typecheck

# Run all checks (lint + typecheck + test)
make validate
```

### Available Make Commands

Run `make help` to see all available commands:
- `make install` - Basic installation
- `make install-dev` - Install with dev dependencies
- `make dev-setup` - Full development setup
- `make test` - Run tests
- `make lint` - Run linter
- `make format` - Format code
- `make typecheck` - Type checking
- `make validate` - Run all checks
- `make clean` - Remove venv and artifacts

## Requirements

- Python 3.11 or higher
- No external services required for core functionality
- Optional: API keys for `jigy ai-*` commands

## Project Status

**Current version**: 0.3.0-dev (Phase 1 Completion)
**Status**: Active development - Phase 1: Decomposability & Nested Subsystems

**Completed:**
- ✅ Slice 0: Bootstrap Infrastructure
- ✅ Slice 1-2: Status & Graph Commands
- ✅ Slice 3: Decomposability Analysis (WU9 complete)
- ✅ Slice 5: Nested Subsystems (WU20-22 complete)

**In Progress:**
- 🔄 WU23: Documentation & Migration guides
- 📋 Remaining: WU10-15 (Community detection, boundary violations, additional decompose commands)

See `docs/wip/S009_PLAN_phase_1_completion.md` for current roadmap.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Setting up your development environment
- Running tests and code quality checks
- Submitting pull requests
- Code style and conventions

## License

MIT

## Documentation

Full documentation available in `docs/`:

- **Concepts**: `docs/jig-concept/JIG-Concept-v7.md` - OSTCX model
- **User Guides**:
  - `docs/user-guide/NESTED_SUBSYSTEMS.md` - Hierarchical subsystems
  - `docs/user-guide/MIGRATION_NESTED.md` - Flat to nested migration
- **Tutorials**: `docs/tutorials/NESTED_SUBSYSTEMS_TUTORIAL.md` - Hands-on example
- **Architecture**:
  - `docs/architecture/DATA_FORMATS.md` - File formats
  - `docs/architecture/GRAPH_SUBSYSTEM.md` - Subsystem implementation
- **Plans**: `docs/wip/S009_PLAN_phase_1_completion.md` - Current development

## Authors

Jim Meyer & Claude

---

*"Intent documented. Deltas harvested. Boundaries preserved. Alignment maintained."*
