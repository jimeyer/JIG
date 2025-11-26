# Implementation and Verification Graphs

_Completing the Alignment Graph: Dependency and Test Layers_

**Date:** 2025-11-25
**Status:** Proposal
**Related:** AG002 (Alignment Graph Whitepaper), AG010 (Brick Discovery Workflow)

---

## Abstract

The Alignment Graph model (AG002) defines four layers: Intent, Dependency (Implementation), Test (Verification), and Brick. Currently, only the Intent layer is captured in `graph-index.json`. This document proposes two additional graph files to complete the model:

1. **`graph-implementation.json`** - The Dependency Layer (observed code structure)
2. **`graph-verification.json`** - The Test Layer (observed verification)

Each graph is machine-generated from codebase analysis, queryable, and includes maintenance commands (`rebuild`, `status`) mirroring the existing Intent graph workflow.

---

## Motivation

### The Current State

**`graph-index.json`** stores:
- Intent nodes: Outcomes (O-*), Specifications (S-*)
- Code stub nodes: High-level file references with `implements` relationships
- Subsystem groupings

This captures **what we intend** but provides minimal information about:
- **What actually exists** in the implementation (modules, classes, functions, dependencies)
- **What is verified** through tests (coverage, verification relationships)
- **How aligned** intent, code, and tests are

### The Problem

Without explicit Implementation and Verification graphs:
- Drift detection is manual (comparing annotations to actual structure)
- Dependency analysis requires running separate tools (AST parsers, coverage runners)
- Alignment queries are impossible ("Which specs lack implementing code?", "Which code lacks tests?")
- Brick boundary violations cannot be automatically detected
- Agent context generation lacks structural detail

### The Solution

Two additional graph files, generated from observable facts:

1. **`graph-implementation.json`**: Captures the actual code structure (modules, classes, functions, imports, calls, Brick assignments)
2. **`graph-verification.json`**: Captures actual verification (tests, coverage edges, verification relationships, drift indicators)

Together with `graph-index.json`, these form the complete Alignment Graph enabling:
- Automatic drift detection via graph queries
- Brick boundary enforcement
- Rich context for agent work
- Alignment health metrics

---

## graph-implementation.json Format

### Overview

The Implementation Graph represents the **Dependency Layer** from AG002: the actual code structure and relationships discovered through static analysis.

### Schema

```json
{
  "version": "1.0",
  "generated": "2025-11-25T12:00:00Z",
  "metadata": {
    "project_root": "/Users/jmeyer/Code/jig",
    "total_modules": 87,
    "total_classes": 124,
    "total_functions": 456,
    "total_loc": 12141,
    "analysis_tools": {
      "parser": "ast + rope",
      "version": "1.0.0"
    },
    "scan_exclusions": [
      "tests/",
      ".venv/",
      "__pycache__/"
    ]
  },

  "nodes": [
    {
      "id": "M-jig.core.graph",
      "type": "module",
      "name": "jig.core.graph",
      "file": "/Users/jmeyer/Code/jig/src/jig/core/graph.py",
      "loc": 892,
      "brick": "BRICK-GRAPH",
      "subsystem": "core",
      "imports": [
        "M-jig.core.parser",
        "M-jig.utils.io",
        "M-networkx"
      ],
      "exports": [
        "C-jig.core.graph.Graph",
        "C-jig.core.graph.Edge",
        "F-jig.core.graph.load_graph"
      ],
      "implements": [
        "S-GRAPH-002"
      ]
    },
    {
      "id": "C-jig.core.graph.Graph",
      "type": "class",
      "name": "Graph",
      "module": "M-jig.core.graph",
      "file": "/Users/jmeyer/Code/jig/src/jig/core/graph.py",
      "line": 45,
      "loc": 523,
      "brick": "BRICK-GRAPH",
      "methods": [
        "F-jig.core.graph.Graph.load_from_dir",
        "F-jig.core.graph.Graph.get_dependencies",
        "F-jig.core.graph.Graph.get_dependents",
        "F-jig.core.graph.Graph.find_path"
      ],
      "implements": [
        "S-GRAPH-002"
      ],
      "metrics": {
        "cyclomatic_complexity": 18,
        "method_count": 24,
        "public_methods": 12,
        "private_methods": 12
      }
    },
    {
      "id": "F-jig.core.graph.Graph.load_from_dir",
      "type": "function",
      "name": "load_from_dir",
      "parent": "C-jig.core.graph.Graph",
      "file": "/Users/jmeyer/Code/jig/src/jig/core/graph.py",
      "line": 89,
      "loc": 67,
      "brick": "BRICK-GRAPH",
      "signature": "load_from_dir(cls, intent_dir: Path) -> Graph",
      "calls": [
        "F-jig.utils.io.read_file",
        "F-jig.core.parser.parse_frontmatter"
      ],
      "implements": [
        "S-GRAPH-002"
      ],
      "metrics": {
        "cyclomatic_complexity": 8,
        "parameter_count": 2,
        "return_points": 1
      }
    },
    {
      "id": "M-networkx",
      "type": "external_module",
      "name": "networkx",
      "package": "networkx",
      "version": "3.1",
      "used_by": [
        "M-jig.core.graph",
        "M-jig.decompose.metrics"
      ]
    }
  ],

  "edges": [
    {
      "source": "M-jig.core.graph",
      "target": "M-jig.core.parser",
      "type": "import",
      "symbols": ["parse_frontmatter", "OSTCNode"],
      "line": 8
    },
    {
      "source": "M-jig.core.graph",
      "target": "M-jig.utils.io",
      "type": "import",
      "symbols": ["read_file", "write_file"],
      "line": 9
    },
    {
      "source": "F-jig.core.graph.Graph.load_from_dir",
      "target": "F-jig.utils.io.read_file",
      "type": "call",
      "line": 102,
      "context": "reading YAML files"
    },
    {
      "source": "F-jig.core.graph.Graph.load_from_dir",
      "target": "F-jig.core.parser.parse_frontmatter",
      "type": "call",
      "line": 105,
      "context": "parsing OSTC nodes"
    },
    {
      "source": "C-jig.core.graph.Graph",
      "target": "F-jig.core.graph.Graph.load_from_dir",
      "type": "contains",
      "visibility": "public"
    }
  ],

  "bricks": {
    "BRICK-UTILS": {
      "modules": [
        "M-jig.utils.io",
        "M-jig.utils.yaml_utils"
      ],
      "classes": [],
      "functions": [
        "F-jig.utils.io.read_file",
        "F-jig.utils.io.write_file",
        "F-jig.utils.io.ensure_dir",
        "F-jig.utils.yaml_utils.load_yaml",
        "F-jig.utils.yaml_utils.dump_yaml"
      ],
      "total_loc": 173,
      "dependency_count": 0,
      "dependent_count": 4,
      "public_api": [
        "F-jig.utils.io.read_file",
        "F-jig.utils.io.write_file",
        "F-jig.utils.io.ensure_dir",
        "F-jig.utils.yaml_utils.load_yaml",
        "F-jig.utils.yaml_utils.dump_yaml"
      ]
    },
    "BRICK-GRAPH": {
      "modules": [
        "M-jig.core.graph",
        "M-jig.core.relationships",
        "M-jig.core.subsystem"
      ],
      "classes": [
        "C-jig.core.graph.Graph",
        "C-jig.core.graph.Edge",
        "C-jig.core.subsystem.Subsystem"
      ],
      "functions": [
        "F-jig.core.relationships.extract_relationships"
      ],
      "total_loc": 892,
      "dependency_count": 2,
      "dependent_count": 4,
      "public_api": [
        "C-jig.core.graph.Graph",
        "C-jig.core.graph.Edge",
        "F-jig.core.graph.load_graph"
      ],
      "dependencies": [
        "BRICK-PARSER",
        "BRICK-UTILS"
      ],
      "external_dependencies": [
        "networkx",
        "json"
      ]
    }
  },

  "metrics": {
    "modularity": {
      "foundation_layer": {
        "modules": 6,
        "loc": 346,
        "internal_dependencies": 0,
        "external_dependencies": 2
      },
      "domain_layer": {
        "modules": 12,
        "loc": 3245,
        "internal_dependencies": 8,
        "external_dependencies": 3
      },
      "application_layer": {
        "modules": 8,
        "loc": 2550,
        "internal_dependencies": 15,
        "external_dependencies": 5
      }
    },
    "coupling": {
      "average_fan_in": 3.2,
      "average_fan_out": 2.8,
      "max_fan_in": 15,
      "max_fan_out": 12,
      "highly_coupled": [
        "M-jig.core.graph"
      ]
    },
    "complexity": {
      "average_cyclomatic": 5.2,
      "max_cyclomatic": 24,
      "complex_functions": [
        "F-jig.core.validator.validate_graph"
      ]
    }
  },

  "boundary_violations": [
    {
      "source": "F-jig.cli.status.show_health",
      "target": "F-jig.core.graph._internal_helper",
      "brick_source": "BRICK-CLI",
      "brick_target": "BRICK-GRAPH",
      "violation": "calling private function outside brick",
      "severity": "error",
      "file": "/Users/jmeyer/Code/jig/src/jig/cli/status.py",
      "line": 67
    }
  ]
}
```

### Key Features

**Node Types:**
- `module`: Python module (`.py` file)
- `class`: Class definition
- `function`: Function or method
- `external_module`: Third-party dependency

**Edge Types:**
- `import`: Module imports another module
- `call`: Function calls another function
- `contains`: Class contains method, module contains class

**Brick Metadata:**
- Brick assignments for all code nodes
- Public API declarations
- Dependency relationships (Brick → Brick)
- Boundary violation detection

**Metrics:**
- LOC, cyclomatic complexity, fan-in/fan-out
- Modularity by layer
- Coupling and complexity aggregates

---

## graph-verification.json Format

### Overview

The Verification Graph represents the **Test Layer** from AG002: actual test coverage, verification relationships, and drift indicators.

### Schema

```json
{
  "version": "1.0",
  "generated": "2025-11-25T12:00:00Z",
  "metadata": {
    "project_root": "/Users/jmeyer/Code/jig",
    "total_tests": 320,
    "total_test_files": 42,
    "total_test_loc": 4219,
    "overall_coverage": 81.4,
    "test_framework": "pytest",
    "coverage_tool": "pytest-cov",
    "test_run_date": "2025-11-25T11:45:00Z"
  },

  "test_nodes": [
    {
      "id": "T-test_io.test_read_file",
      "type": "test_function",
      "name": "test_read_file",
      "file": "/Users/jmeyer/Code/jig/tests/unit/test_io.py",
      "line": 12,
      "loc": 18,
      "test_type": "unit",
      "brick": "BRICK-UTILS",
      "verifies": [
        "S-JIG-002"
      ],
      "covers": [
        "F-jig.utils.io.read_file"
      ],
      "fixtures": [
        "tmp_path"
      ],
      "assertions": 3
    },
    {
      "id": "T-test_io.test_read_file_missing",
      "type": "test_function",
      "name": "test_read_file_missing",
      "file": "/Users/jmeyer/Code/jig/tests/unit/test_io.py",
      "line": 31,
      "loc": 12,
      "test_type": "unit",
      "brick": "BRICK-UTILS",
      "verifies": [
        "S-JIG-002"
      ],
      "covers": [
        "F-jig.utils.io.read_file"
      ],
      "tests_error_handling": true,
      "assertions": 1
    },
    {
      "id": "T-test_graph_loading.test_load_full_graph",
      "type": "test_function",
      "name": "test_load_full_graph",
      "file": "/Users/jmeyer/Code/jig/tests/integration/test_graph_loading.py",
      "line": 45,
      "loc": 67,
      "test_type": "integration",
      "bricks": [
        "BRICK-GRAPH",
        "BRICK-PARSER",
        "BRICK-UTILS"
      ],
      "verifies": [
        "S-GRAPH-002",
        "O-JIGY-001"
      ],
      "covers": [
        "F-jig.core.graph.Graph.load_from_dir",
        "F-jig.core.parser.parse_frontmatter",
        "F-jig.utils.io.read_file"
      ],
      "fixtures": [
        "sample_intent_dir",
        "tmp_path"
      ],
      "assertions": 8
    },
    {
      "id": "T-test_validator.TestGraphValidator",
      "type": "test_class",
      "name": "TestGraphValidator",
      "file": "/Users/jmeyer/Code/jig/tests/unit/test_validator.py",
      "line": 23,
      "loc": 145,
      "test_type": "unit",
      "brick": "BRICK-VALIDATOR",
      "test_methods": [
        "T-test_validator.TestGraphValidator.test_valid_graph",
        "T-test_validator.TestGraphValidator.test_missing_outcome",
        "T-test_validator.TestGraphValidator.test_circular_deps"
      ]
    }
  ],

  "coverage_edges": [
    {
      "test": "T-test_io.test_read_file",
      "code": "F-jig.utils.io.read_file",
      "coverage_type": "line",
      "lines_covered": 18,
      "lines_total": 18,
      "coverage_percent": 100.0,
      "branches_covered": 2,
      "branches_total": 3,
      "branch_percent": 66.7
    },
    {
      "test": "T-test_io.test_read_file_missing",
      "code": "F-jig.utils.io.read_file",
      "coverage_type": "line",
      "lines_covered": 8,
      "lines_total": 18,
      "coverage_percent": 44.4,
      "branches_covered": 1,
      "branches_total": 3,
      "branch_percent": 33.3
    }
  ],

  "verification_edges": [
    {
      "test": "T-test_io.test_read_file",
      "intent": "S-JIG-002",
      "intent_type": "specification",
      "verification_type": "direct",
      "rationale": "Tests YAML file reading requirement"
    },
    {
      "test": "T-test_graph_loading.test_load_full_graph",
      "intent": "O-JIGY-001",
      "intent_type": "outcome",
      "verification_type": "integration",
      "rationale": "Tests graph accurately reflects OSTC relationships"
    },
    {
      "test": "T-test_graph_loading.test_load_full_graph",
      "intent": "S-GRAPH-002",
      "intent_type": "specification",
      "verification_type": "integration",
      "rationale": "Tests core graph data structures"
    }
  ],

  "code_coverage": {
    "by_brick": {
      "BRICK-UTILS": {
        "total_lines": 173,
        "covered_lines": 165,
        "missing_lines": 8,
        "coverage_percent": 95.4,
        "total_branches": 24,
        "covered_branches": 22,
        "branch_percent": 91.7,
        "test_count": 16,
        "test_ratio": 1.66
      },
      "BRICK-GRAPH": {
        "total_lines": 892,
        "covered_lines": 695,
        "missing_lines": 197,
        "coverage_percent": 77.9,
        "total_branches": 124,
        "covered_branches": 97,
        "branch_percent": 78.2,
        "test_count": 52,
        "test_ratio": 1.15
      }
    },
    "by_module": {
      "M-jig.utils.io": {
        "total_lines": 89,
        "covered_lines": 85,
        "missing_lines": 4,
        "coverage_percent": 95.5,
        "uncovered_lines": [67, 68, 89, 90]
      }
    },
    "by_function": {
      "F-jig.utils.io.read_file": {
        "total_lines": 18,
        "covered_lines": 18,
        "missing_lines": 0,
        "coverage_percent": 100.0,
        "total_branches": 3,
        "covered_branches": 3,
        "branch_percent": 100.0,
        "tests": [
          "T-test_io.test_read_file",
          "T-test_io.test_read_file_missing",
          "T-test_graph_loading.test_load_full_graph"
        ]
      }
    }
  },

  "drift_indicators": {
    "untested_code": [
      {
        "code": "F-jig.core.experimental_feature.new_algo",
        "type": "function",
        "brick": "BRICK-GRAPH",
        "loc": 87,
        "coverage_percent": 0.0,
        "severity": "warning",
        "recommendation": "Add unit tests or mark as experimental"
      }
    ],
    "unverified_specs": [
      {
        "spec": "S-GRAPH-004",
        "title": "Graph serialization format",
        "subsystem": "core",
        "tests": [],
        "severity": "error",
        "recommendation": "Add verification tests for S-GRAPH-004"
      }
    ],
    "orphaned_tests": [
      {
        "test": "T-test_old_api.test_deprecated_function",
        "covers": [],
        "verifies": [],
        "severity": "warning",
        "recommendation": "Remove test or link to Intent"
      }
    ],
    "partial_coverage": [
      {
        "code": "F-jig.core.validator.validate_graph",
        "coverage_percent": 42.3,
        "branch_percent": 28.1,
        "missing_branches": 18,
        "severity": "warning",
        "tests": [
          "T-test_validator.test_valid_graph"
        ],
        "recommendation": "Add tests for error paths and edge cases"
      }
    ],
    "cross_brick_tests": [
      {
        "test": "T-test_graph_loading.test_load_full_graph",
        "bricks": [
          "BRICK-GRAPH",
          "BRICK-PARSER",
          "BRICK-UTILS"
        ],
        "test_type": "integration",
        "rationale": "Legitimate integration test across brick boundaries"
      }
    ]
  },

  "test_organization": {
    "by_type": {
      "unit": {
        "count": 256,
        "test_files": 28,
        "loc": 3120
      },
      "integration": {
        "count": 48,
        "test_files": 12,
        "loc": 987
      },
      "contract": {
        "count": 16,
        "test_files": 2,
        "loc": 112
      }
    },
    "by_brick": {
      "BRICK-UTILS": {
        "unit_tests": 16,
        "integration_tests": 0,
        "contract_tests": 0
      },
      "BRICK-GRAPH": {
        "unit_tests": 42,
        "integration_tests": 10,
        "contract_tests": 0
      }
    }
  },

  "alignment_metrics": {
    "intent_coverage": {
      "total_outcomes": 15,
      "verified_outcomes": 12,
      "unverified_outcomes": 3,
      "coverage_percent": 80.0
    },
    "spec_coverage": {
      "total_specs": 45,
      "verified_specs": 38,
      "unverified_specs": 7,
      "coverage_percent": 84.4
    },
    "code_coverage": {
      "total_functions": 456,
      "tested_functions": 389,
      "untested_functions": 67,
      "coverage_percent": 85.3
    }
  }
}
```

### Key Features

**Test Node Types:**
- `test_function`: Individual test function
- `test_class`: Test class (with methods)
- `test_method`: Method within test class

**Edge Types:**
- `coverage`: Test covers code (with line/branch metrics)
- `verification`: Test verifies Intent node (Outcome or Spec)

**Coverage Metrics:**
- Line coverage (covered/total)
- Branch coverage (covered/total)
- Per-brick, per-module, per-function granularity

**Drift Indicators:**
- Untested code (functions with 0% coverage)
- Unverified specs (specs with no tests)
- Orphaned tests (tests covering no code or intent)
- Partial coverage (functions below threshold)
- Cross-brick tests (legitimate integration tests)

**Alignment Metrics:**
- Intent coverage: % of Outcomes/Specs verified
- Code coverage: % of functions tested
- Test organization by type and brick

---

## Maintenance Commands

### Implementation Graph Commands

#### `jigy impl rebuild`

**Purpose:** Regenerate `graph-implementation.json` from codebase static analysis.

**Algorithm:**
1. Scan project root for Python files (excluding test dirs, venv, cache)
2. Parse each file with AST to extract:
   - Module declarations
   - Class definitions
   - Function/method definitions
   - Import statements
   - Function calls (where statically determinable)
3. Load brick definitions (if available) to assign nodes to bricks
4. Calculate metrics (LOC, complexity, coupling)
5. Detect boundary violations (calls crossing brick boundaries)
6. Write `graph-implementation.json`

**Options:**
```bash
jigy impl rebuild [OPTIONS]

Options:
  --project-root PATH    Project root directory (default: current dir)
  --exclude PATTERN      Exclude patterns (default: tests/*, .venv/*, __pycache__/*)
  --bricks PATH          Path to brick definitions (default: bricks/*.brick.yaml)
  --output PATH          Output file (default: jig/graph-implementation.json)
  --analyze-calls        Include call graph analysis (slower, default: false)
  --verbose              Show detailed progress
```

**Example:**
```bash
$ jigy impl rebuild --project-root ~/Code/jig --analyze-calls

Scanning codebase...
  Found 87 Python files
  Excluded 42 test files

Parsing modules...
  Parsed 87 modules
  Extracted 124 classes
  Extracted 456 functions

Analyzing dependencies...
  Found 598 import edges
  Analyzed 1247 function calls

Loading brick definitions...
  Loaded 10 bricks
  Assigned 87 modules to bricks

Detecting boundary violations...
  Found 2 violations

Calculating metrics...
  Modularity: 0.73
  Average coupling: 3.2

Writing graph-implementation.json...
Done. Generated 87 nodes, 1845 edges in 2.3s
```

**Output:** `jig/graph-implementation.json` (updated)

---

#### `jigy impl status`

**Purpose:** Show health metrics and boundary violations for the implementation graph.

**Algorithm:**
1. Load `graph-implementation.json`
2. Calculate health metrics:
   - Modularity score
   - Coupling metrics (fan-in, fan-out)
   - Complexity metrics (avg/max cyclomatic)
   - Brick boundary violations
3. Display summary and issues

**Options:**
```bash
jigy impl status [OPTIONS]

Options:
  --brick BRICK_ID       Show status for specific brick
  --violations-only      Only show boundary violations
  --format {text,json}   Output format (default: text)
  --detailed             Show detailed metrics per module
```

**Example:**
```bash
$ jigy impl status

Implementation Graph Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: 2025-11-25 12:00:00
Modules: 87 | Classes: 124 | Functions: 456 | LOC: 12,141

Modularity Metrics
  Foundation Layer: 6 modules, 346 LOC, 0 internal deps
  Domain Layer:     12 modules, 3,245 LOC, 8 internal deps
  Application Layer: 8 modules, 2,550 LOC, 15 internal deps

  Overall Modularity: 0.73 (good)

Coupling Metrics
  Average fan-in:  3.2
  Average fan-out: 2.8
  Highly coupled:  M-jig.core.graph (fan-in: 15)

Complexity Metrics
  Average cyclomatic: 5.2
  Max cyclomatic:     24 (F-jig.core.validator.validate_graph)
  Complex functions:  3

Brick Boundaries
  ✓ BRICK-UTILS: No violations
  ✓ BRICK-PARSER: No violations
  ✗ BRICK-CLI: 2 violations
  ✓ BRICK-GRAPH: No violations

Boundary Violations (2)
  1. BRICK-CLI → BRICK-GRAPH
     src/jig/cli/status.py:67
     F-jig.cli.status.show_health calls private F-jig.core.graph._internal_helper
     Severity: error

  2. BRICK-VALIDATOR → BRICK-GRAPH
     src/jig/core/validator.py:245
     F-jig.core.validator.check_cycles imports internal M-jig.core.graph._utils
     Severity: warning

Health: 92/100 (excellent) - 2 violations need fixing
```

**Example (brick-specific):**
```bash
$ jigy impl status --brick BRICK-UTILS

BRICK-UTILS Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Modules: 2 | Functions: 5 | LOC: 173

Dependencies
  Bricks:   0 (foundation layer)
  External: 2 (pathlib, yaml)

Dependents
  Bricks: 4 (BRICK-PARSER, BRICK-GRAPH, BRICK-INDEX, BRICK-CLI)

Public API (5 functions)
  ✓ F-jig.utils.io.read_file
  ✓ F-jig.utils.io.write_file
  ✓ F-jig.utils.io.ensure_dir
  ✓ F-jig.utils.yaml_utils.load_yaml
  ✓ F-jig.utils.yaml_utils.dump_yaml

Metrics
  Coupling ratio: ∞:1 (no dependencies)
  Fan-in:  4
  Fan-out: 0
  Average cyclomatic: 2.3
  Max cyclomatic:     8

Boundary Violations: 0

Health: 100/100 (excellent)
```

---

### Verification Graph Commands

#### `jigy verify rebuild`

**Purpose:** Regenerate `graph-verification.json` from test discovery and coverage analysis.

**Algorithm:**
1. Discover tests (using pytest test discovery)
2. Run coverage analysis (pytest-cov or coverage.py)
3. Parse test files to extract:
   - Test functions/classes
   - Test types (unit, integration, contract)
   - `@jig` annotations for verification relationships
4. Map coverage data to code nodes (from `graph-implementation.json`)
5. Identify drift indicators:
   - Untested code (0% coverage)
   - Unverified specs (specs with no tests)
   - Orphaned tests (no coverage or verification edges)
6. Calculate alignment metrics
7. Write `graph-verification.json`

**Options:**
```bash
jigy verify rebuild [OPTIONS]

Options:
  --project-root PATH      Project root directory (default: current dir)
  --test-dir PATH          Test directory (default: tests/)
  --coverage-threshold INT Minimum coverage % (default: 80)
  --run-tests              Run tests before analysis (default: false)
  --impl-graph PATH        Path to implementation graph (default: jig/graph-implementation.json)
  --intent-graph PATH      Path to intent graph (default: jig/graph-index.json)
  --output PATH            Output file (default: jig/graph-verification.json)
  --verbose                Show detailed progress
```

**Example:**
```bash
$ jigy verify rebuild --run-tests --coverage-threshold 80

Running tests with coverage...
  pytest --cov=jig --cov-report=json
  ===== 320 passed in 4.2s =====

Analyzing coverage data...
  Coverage: 81.4% (12,141 lines, 9,883 covered)
  Branch coverage: 78.2%

Discovering tests...
  Found 42 test files
  Extracted 320 test functions
  Identified 256 unit tests, 48 integration tests, 16 contract tests

Mapping tests to code...
  Created 1,247 coverage edges

Loading intent graph...
  Loaded 60 Intent nodes (15 Outcomes, 45 Specs)

Extracting verification relationships...
  Found 89 @jig.verifies annotations
  Created 89 verification edges

Detecting drift...
  Untested code:       67 functions (14.7%)
  Unverified specs:    7 specs (15.6%)
  Orphaned tests:      3 tests
  Partial coverage:    23 functions (< 80%)

Calculating alignment metrics...
  Intent coverage:     84.4%
  Code coverage:       85.3%
  Overall alignment:   81.2%

Writing graph-verification.json...
Done. Generated 320 test nodes, 1,336 edges in 6.8s
```

**Output:** `jig/graph-verification.json` (updated)

---

#### `jigy verify status`

**Purpose:** Show test coverage, verification relationships, and drift indicators.

**Algorithm:**
1. Load `graph-verification.json`
2. Calculate and display:
   - Coverage summary (overall, by brick, by type)
   - Drift indicators (untested code, unverified specs, orphaned tests)
   - Alignment metrics
3. Highlight issues and recommendations

**Options:**
```bash
jigy verify status [OPTIONS]

Options:
  --brick BRICK_ID       Show status for specific brick
  --drift-only           Only show drift indicators
  --format {text,json}   Output format (default: text)
  --detailed             Show detailed coverage per module
  --threshold INT        Coverage threshold for warnings (default: 80)
```

**Example:**
```bash
$ jigy verify status

Verification Graph Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: 2025-11-25 12:00:00 (from test run: 2025-11-25 11:45:00)
Tests: 320 (256 unit, 48 integration, 16 contract)
Test LOC: 4,219

Coverage Summary
  Overall:        81.4% line, 78.2% branch
  Functions:      389/456 tested (85.3%)
  Specifications: 38/45 verified (84.4%)
  Outcomes:       12/15 verified (80.0%)

Coverage by Brick
  BRICK-UTILS:     95.4% (excellent)
  BRICK-PARSER:    89.2% (good)
  BRICK-GRAPH:     77.9% (fair)
  BRICK-VALIDATOR: 82.1% (good)
  BRICK-CLI:       45.9% (poor)

Drift Indicators (33 total)

  Untested Code (67 functions)
    ! F-jig.core.experimental_feature.new_algo (0% coverage)
      Location: src/jig/core/experimental_feature.py:45
      Recommendation: Add unit tests or mark as experimental

    ! F-jig.cli.commands.deprecated_command (0% coverage)
      Location: src/jig/cli/commands.py:234
      Recommendation: Remove or add tests

    ... 65 more

  Unverified Specifications (7)
    ✗ S-GRAPH-004: Graph serialization format
      No tests found
      Recommendation: Add verification tests for S-GRAPH-004

    ✗ S-CLI-010: Error handling in CLI
      No tests found
      Recommendation: Add verification tests for S-CLI-010

    ... 5 more

  Orphaned Tests (3)
    ? T-test_old_api.test_deprecated_function
      Covers no code, verifies no intent
      Recommendation: Remove test or link to Intent

    ... 2 more

  Partial Coverage (23 functions < 80%)
    ⚠ F-jig.core.validator.validate_graph: 42.3% line, 28.1% branch
      Missing 18 branches (error paths untested)
      Tests: T-test_validator.test_valid_graph
      Recommendation: Add tests for error paths and edge cases

    ... 22 more

Alignment Health: 81/100 (good) - 33 drift issues
Recommendation: Address unverified specs and untested code
```

**Example (brick-specific):**
```bash
$ jigy verify status --brick BRICK-UTILS

BRICK-UTILS Verification Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Coverage: 95.4% line, 91.7% branch
Tests: 16 unit, 0 integration, 0 contract
Test Ratio: 1.66:1 (287 test LOC / 173 source LOC)

Functions (5 total)
  ✓ F-jig.utils.io.read_file         100% (3 tests)
  ✓ F-jig.utils.io.write_file        100% (2 tests)
  ✓ F-jig.utils.io.ensure_dir        100% (1 test)
  ✓ F-jig.utils.yaml_utils.load_yaml  92% (4 tests)
  ✓ F-jig.utils.yaml_utils.dump_yaml  88% (3 tests)

Specifications Verified
  ✓ S-JIG-002: YAML frontmatter + Markdown (16 tests)

Uncovered Lines (8)
  src/jig/utils/yaml_utils.py:67-68 (error handling)
  src/jig/utils/io.py:89-90 (edge case)

Drift Indicators: 0
Health: 95/100 (excellent)
```

---

## Integration with Existing Commands

### Enhanced `jigy status`

The existing `jigy status` command currently shows Intent graph health. With Implementation and Verification graphs available, it should be enhanced to show **alignment across all three graphs**.

**Proposed output:**
```bash
$ jigy status

JIG Alignment Graph Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project: ~/Code/jig
Generated: 2025-11-25 12:00:00

Intent Graph (graph-index.json)
  Nodes: 60 (15 Outcomes, 45 Specifications)
  Subsystems: 5
  Health: 94/100 (excellent)

Implementation Graph (graph-implementation.json)
  Nodes: 667 (87 modules, 124 classes, 456 functions)
  LOC: 12,141
  Bricks: 10
  Boundary violations: 2
  Health: 92/100 (excellent)

Verification Graph (graph-verification.json)
  Tests: 320 (256 unit, 48 integration, 16 contract)
  Coverage: 81.4% line, 78.2% branch
  Drift indicators: 33
  Health: 81/100 (good)

Alignment Metrics
  Intent → Implementation: 95.6% (43/45 specs implemented)
  Intent → Verification:   84.4% (38/45 specs verified)
  Implementation → Verification: 85.3% (389/456 functions tested)

  Overall Alignment: 85.1% (good)

Critical Issues (4)
  1. S-GRAPH-004 not verified (no tests)
  2. BRICK-CLI boundary violation (status.py:67)
  3. F-jig.core.validator.validate_graph low coverage (42%)
  4. 67 untested functions

Recommendation: Run `jigy verify rebuild` to update test coverage
```

---

## Workflow Integration

### Typical Development Workflow

**1. Initial Setup**
```bash
# Initialize JIG structure
jigy init

# Build all three graphs
jigy index           # Intent graph
jigy impl rebuild    # Implementation graph
jigy verify rebuild --run-tests  # Verification graph

# Check alignment
jigy status
```

**2. After Code Changes**
```bash
# Rebuild implementation graph
jigy impl rebuild

# Check for boundary violations
jigy impl status --violations-only
```

**3. After Adding Tests**
```bash
# Rebuild verification graph
jigy verify rebuild --run-tests

# Check coverage and drift
jigy verify status --drift-only
```

**4. Before Commit**
```bash
# Full alignment check
jigy status

# Ensure no critical issues
jigy impl status --violations-only
jigy verify status --threshold 80
```

**5. CI Pipeline**
```bash
# In CI, fail on violations or low coverage
jigy impl rebuild
jigy impl status --violations-only --format json | jq '.boundary_violations | length' | grep -q '^0$' || exit 1

jigy verify rebuild --run-tests
jigy verify status --threshold 80 --format json | jq '.metrics.overall_coverage' | awk '{if($1<80) exit 1}'
```

---

## Implementation Plan

### Phase 1: Implementation Graph (Week 1-2)

**Week 1: Core Implementation**
- [ ] Implement AST-based code scanner
- [ ] Extract modules, classes, functions, imports
- [ ] Build import graph
- [ ] Assign nodes to bricks (if brick definitions exist)
- [ ] Generate `graph-implementation.json`

**Week 2: Metrics & Commands**
- [ ] Calculate metrics (LOC, complexity, coupling)
- [ ] Implement boundary violation detection
- [ ] Build `jigy impl rebuild` command
- [ ] Build `jigy impl status` command
- [ ] Write unit tests

**Deliverables:**
- `src/jig/core/impl_graph_builder.py`
- `src/jig/cli/impl.py` (CLI commands)
- `graph-implementation.json` schema validator
- Unit tests (>80% coverage)

---

### Phase 2: Verification Graph (Week 3-4)

**Week 3: Core Implementation**
- [ ] Implement test discovery (pytest integration)
- [ ] Run coverage analysis (pytest-cov integration)
- [ ] Parse test files and extract test nodes
- [ ] Map coverage data to code nodes
- [ ] Extract verification relationships from `@jig` annotations
- [ ] Generate `graph-verification.json`

**Week 4: Drift Detection & Commands**
- [ ] Implement drift indicator detection
  - Untested code
  - Unverified specs
  - Orphaned tests
  - Partial coverage
- [ ] Calculate alignment metrics
- [ ] Build `jigy verify rebuild` command
- [ ] Build `jigy verify status` command
- [ ] Write unit tests

**Deliverables:**
- `src/jig/core/verify_graph_builder.py`
- `src/jig/cli/verify.py` (CLI commands)
- `graph-verification.json` schema validator
- Unit tests (>80% coverage)

---

### Phase 3: Integration & Enhancement (Week 5)

**Integration:**
- [ ] Enhance `jigy status` to show all three graphs
- [ ] Add alignment queries (e.g., "Which specs lack tests?")
- [ ] Integrate with existing `jigy index` workflow
- [ ] Add CI documentation and examples

**Enhancement:**
- [ ] Add graph query API for custom alignment checks
- [ ] Add Mermaid/Graphviz export for visualization
- [ ] Add `jigy align check` command for specific alignment queries
- [ ] Performance optimization for large codebases

**Deliverables:**
- Enhanced `jigy status` command
- Graph query API
- CI integration guide
- Documentation updates

---

## Alignment Query Examples

With all three graphs in place, we can answer powerful alignment queries:

### Query 1: Which specifications lack implementing code?

```bash
# Using graph query API
jigy align check --query "unimplemented-specs"

# Output:
Unimplemented Specifications (2)
  S-GRAPH-005: Real-time graph updates
    No implementing code found
    Recommendation: Implement or mark as future work

  S-CLI-011: Plugin system
    No implementing code found
    Recommendation: Implement or mark as future work
```

**Graph traversal:**
1. Load Intent graph → get all Specification nodes
2. For each Spec, check Implementation graph for `implements` edges
3. Return Specs with no implementing code

---

### Query 2: Which code serves no documented intent?

```bash
jigy align check --query "orphan-code"

# Output:
Orphan Code (12 functions)
  F-jig.core.experimental_feature.new_algo
    No Intent nodes reference this function
    Recommendation: Add Intent or remove code

  ... 11 more
```

**Graph traversal:**
1. Load Implementation graph → get all function nodes
2. For each function, check for `implements` edges to Intent graph
3. Return functions with no Intent relationships

---

### Query 3: Which tests verify multiple specifications? (test coupling)

```bash
jigy align check --query "coupled-tests"

# Output:
Coupled Tests (5 tests verify >3 specs each)
  T-test_full_pipeline.test_end_to_end
    Verifies 8 specifications:
      S-GRAPH-001, S-GRAPH-002, S-PARSER-001, S-CLI-007, ...
    Recommendation: Split into smaller tests

  ... 4 more
```

**Graph traversal:**
1. Load Verification graph → get all test nodes
2. For each test, count `verifies` edges
3. Return tests with >3 verification edges (threshold configurable)

---

### Query 4: What will break if I change this interface?

```bash
jigy align check --query "impact-analysis" --target "F-jig.utils.io.read_file"

# Output:
Impact Analysis: F-jig.utils.io.read_file
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Direct Callers (12 functions in 3 bricks)
  F-jig.core.parser.parse_frontmatter (BRICK-PARSER)
  F-jig.core.graph.Graph.load_from_dir (BRICK-GRAPH)
  F-jig.cli.init.load_template (BRICK-CLI)
  ... 9 more

Indirect Impact (48 functions via call chain)
  BRICK-PARSER → 18 functions
  BRICK-GRAPH → 22 functions
  BRICK-CLI → 8 functions

Affected Tests (23 tests will need updates)
  T-test_parser.test_parse_outcome
  T-test_graph_loading.test_load_full_graph
  ... 21 more

Affected Specifications (5 specs rely on this function)
  S-JIG-002: YAML frontmatter
  S-GRAPH-002: Graph loading
  ... 3 more

Recommendation: Breaking changes require major version bump
```

**Graph traversal:**
1. Implementation graph: find all `call` edges pointing to target function
2. Recursively follow call edges to find indirect callers
3. Verification graph: find all tests covering callers
4. Intent graph: find all specs implemented by callers
5. Aggregate and display

---

## Future Extensions

### Graph Versioning

Track how graphs change over time:
```bash
jigy impl diff --from v1.0 --to v2.0

# Output:
Implementation Graph Diff (v1.0 → v2.0)
  Added modules:    3
  Removed modules:  1
  Modified modules: 8

  Added functions:  12
  Removed functions: 5

  Boundary violations: 2 → 0 (fixed)
  Modularity: 0.71 → 0.73 (improved)
```

---

### Automated Refactoring Suggestions

Use alignment metrics to suggest improvements:
```bash
jigy align suggest

# Output:
Refactoring Suggestions

  1. Split BRICK-CLI (2,338 LOC)
     Current: Very large, high coupling
     Suggested: Split into BRICK-CLI-CORE, BRICK-CLI-COMMANDS
     Impact: Reduces coupling ratio from 2:1 to 8:1

  2. Add tests for BRICK-VALIDATOR complex functions
     Current: 3 functions with cyclomatic complexity > 20, coverage < 50%
     Suggested: Add unit tests for error paths
     Impact: Raises coverage from 67% → 85%

  3. Remove orphaned code
     Current: 12 functions with no Intent
     Suggested: Remove or document Intent
     Impact: Reduces LOC by 340, improves alignment
```

---

### Real-time Monitoring

Watch mode for continuous alignment checking:
```bash
jigy align watch

# Output (updates every 5s):
Watching for changes...

12:34:56 - File changed: src/jig/core/graph.py
12:34:57 - Rebuilding implementation graph...
12:34:58 - New boundary violation detected!
           BRICK-GRAPH → BRICK-PARSER
           F-jig.core.graph.helper calls internal F-jig.core.parser._parse

12:35:02 - File changed: tests/unit/test_graph.py
12:35:03 - Rebuilding verification graph...
12:35:05 - Coverage improved: 77.9% → 79.2%
```

---

## Conclusion

Adding `graph-implementation.json` and `graph-verification.json` completes the Alignment Graph model, enabling:

1. **Automatic drift detection** - Compare Intent, Implementation, and Verification objectively
2. **Brick boundary enforcement** - Detect violations through static analysis
3. **Rich agent context** - Provide detailed structural information for AI-assisted development
4. **Alignment health metrics** - Quantify architectural integrity over time
5. **Powerful queries** - Answer questions that are currently impossible

These graphs transform architecture from aspiration to mechanism, making the invisible visible and the unmeasurable measurable.

**Next Steps:**
1. Review and refine schemas
2. Implement Phase 1 (Implementation Graph)
3. Implement Phase 2 (Verification Graph)
4. Integrate with existing `jigy` workflow
5. Dogfood on JIG itself
6. Apply to ASE project

The hypothesis from AG002 can now be tested empirically.

---

## References

- **AG002** - Alignment Graph and Bricks Whitepaper
- **AG010** - Brick Discovery Workflow
- **ASE Brick Analysis** - ~/Code/ASE/jig-wip (17 bricks, real-world validation)
- Current `graph-index.json` - jig/graph-index.json (Intent graph schema)
