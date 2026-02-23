---
type: exploration
title: "Go Core With Subprocess Language Analyzers"
status: active
created: 1740355200
created_human: "2026-02-23"
parent: null
children: []
---

# Go Core With Subprocess Language Analyzers

## Summary

Rewrite JIG's core tooling in Go for a fast, zero-install, single-binary CLI. Language-specific analysis
(extracting code structure, decorators, and test annotations) is handled by external subprocess analyzers
that speak a common NDJSON protocol. The Go core orchestrates everything else: intent graph generation,
validation, query engine, mend, MCP server, and the CLI. This enables JIG to grow from Python-only to
Python + C + Swift + Kotlin + others without touching the core binary.

---

## Context and Motivation

### The Current State

JIG is a Python project that analyzes Python projects. The CLI (`jigy`) requires:

- Python 3.10+ installed on the host
- A virtualenv activated (`source .venv/bin/activate`)
- Dependencies installed (`pip install -e ".[dev]"`)
- ~200ms startup time on every invocation

For a tool that agents and CI pipelines call dozens of times per session, this overhead is real. More
importantly, Python-as-runtime couples the tool's own language to the languages it analyzes, which
becomes a problem as JIG expands to multi-language projects.

### What the User Wants

> "I want this program to run on the command line, be very fast, and not have any dependencies."
> "I want to grow JIG to work on other languages — C and Swift and Kotlin are likely to come next."

These two requirements together motivate a two-part answer:

1. The **core** (intent graph, validation, query, CLI, MCP) moves to Go: single binary, ~5ms startup,
   zero runtime dependencies.
2. The **language analyzers** (code structure extraction, decorator scanning) remain language-specific
   subprocesses, connected via a lightweight NDJSON protocol.

### Why Go Over Rust or TypeScript

| Language | Startup | Binary | Dev effort | Verdict |
|----------|---------|--------|------------|---------|
| Python (current) | ~200ms | needs venv | current baseline | too slow, too fragile |
| Go | ~5ms | ~10MB static | moderate | **correct choice** |
| Rust | ~3ms | ~5MB | high | overkill for I/O-bound tool |
| TypeScript/Deno | ~30ms | ~50MB | moderate | still needs a runtime |

Go was designed for CLI tooling and server programs. Its standard library covers everything JIG needs:
JSON, YAML (via `gopkg.in/yaml.v3`), filesystem traversal, subprocess execution, regex, and HTTP.
The `encoding/json` streaming decoder handles NDJSON natively. Cobra is the industry-standard CLI
framework. Single-binary compilation with `GOOS=darwin GOARCH=arm64 go build` is straightforward.

---

## The Key Architectural Insight

The NDJSON graph files are the natural seam between JIG's subsystems:

```
Generators (jigy rebuild)   →  intent.ndjson, impl.ndjson, verify.ndjson  →  Consumers (jigy validate, jigy context)
```

This seam already exists. It is well-defined and stable. Python and Go can both read and write the same
NDJSON format. This enables incremental conversion (strangler fig) without a flag day, and it defines
the protocol that subprocess analyzers must speak.

---

## Architecture: Go Core + Subprocess Analyzers

```
jigy (Go binary, ~10MB)
│
├── config/          Parse jig.toml, discover project root
├── intent_graph/    Parse Markdown frontmatter → intent.ndjson
├── verify_graph/    Scan test files for annotations → verify.ndjson
├── impl_graph/      Orchestrate analyzer subprocesses → impl.ndjson
│    └── (calls language analyzers via subprocess protocol)
├── validation/      17 rule types, brick/layer/tower logic
├── query/           BFS traversal, identifier resolution, text search
├── mend/            YAML frontmatter editing, auto-fix engine
├── mcp/             MCP server (stdio, model context protocol)
├── staleness/       Git-based change detection
└── cli/             Cobra commands: rebuild, validate, context, mend, mcp, init
```

```
Language Analyzers (subprocesses — separate binaries or scripts)
│
├── jigy-analyzer-python    Python script; uses stdlib ast; ships with jigy
├── jigy-analyzer-swift     Swift binary or Go binary; future
├── jigy-analyzer-c         libclang wrapper or Go C parser; future
└── jigy-analyzer-kotlin    JVM tool or Go; future
```

The Go core never imports a Python module. It does not contain a Python parser, a Swift parser, or a
C parser. It contains exactly one interface: the subprocess protocol.

---

## The Subprocess Analyzer Protocol

Each language analyzer is a subprocess. The contract is minimal and stable:

### Input (stdin or args)

```
# Option A: file list on stdin (one path per line)
/path/to/src/mymodule.py
/path/to/src/other.py

# Option B: JSON array via stdin
["/path/to/src/mymodule.py", "/path/to/src/other.py"]
```

The Go core passes file paths to analyze. Configuration (project root, spec IDs) is passed via
environment variables or a JSON config blob on stdin before the file list.

### Output (stdout)

NDJSON, identical schema to the existing `impl.ndjson` format:

```json
{"_meta": {"analyzer": "python", "version": "1.0", "file_count": 2}}
{"id": "F-jig.cli.main.validate", "type": "function", "module": "jig.cli.main", "class": null, "file": "src/jig/cli/main.py", "line": 45, "language": "python", "hash": "sha256:abc..."}
{"id": "F-jig.cli.main.rebuild", "type": "function", "module": "jig.cli.main", "class": null, "file": "src/jig/cli/main.py", "line": 89, "language": "python", "hash": "sha256:def..."}
{"source": "F-jig.cli.main.validate", "target": "S-026", "type": "implements"}
```

Edges, nodes, and metadata — same as today. The Go core reads this stream and writes it into
`impl.ndjson`. No schema change is required.

### Stderr

Errors, warnings, and progress messages. Non-zero exit code = analyzer failure. The Go core
logs stderr and reports to the user.

### Environment Variables Passed to Analyzer

```
JIG_PROJECT_ROOT=/path/to/project
JIG_SPECS_DIR=/path/to/jig/specifications
JIG_LANGUAGE=python
JIG_LOG_LEVEL=info
```

### Analyzer Discovery

The Go core discovers analyzers in this priority order:

1. Explicit path in `jig.toml` `[analyzers]` section
2. `jigy-analyzer-{language}` in the same directory as the `jigy` binary
3. `jigy-analyzer-{language}` on PATH

```toml
# jig.toml
[analyzers]
python = "jigy-analyzer-python"       # bundled, same dir as jigy binary
swift  = "/usr/local/bin/jigy-analyzer-swift"
c      = "jigy-analyzer-c"
kotlin = "jigy-analyzer-kotlin"
```

If no analyzer is found for a language, `jigy rebuild impl` warns and skips that language. It does not
fail — a project may not yet have a configured analyzer for all its languages.

---

## What the Python Analyzer Becomes

The Python analyzer (`src/jig/impl_graph/analyzers/python.py` + `python_visitor.py`, ~960 LoC) is
extracted into a standalone script:

```
jigy-analyzer-python (Python script)
├── Entry point: main() reads file list from stdin, writes NDJSON to stdout
├── Uses Python's ast module (correct — best Python parser available)
├── Zero new dependencies (ast, json, sys are all stdlib)
├── Ships alongside the jigy binary in the distribution
└── Works on any Python 3.8+
```

This is correct. The Python analyzer uses Python's own AST module because that is the most accurate
way to parse Python. This is not a dependency problem — it is the appropriate tool. When a user runs
JIG on a Python project, they have Python installed. The analyzer runs as a subprocess of `jigy rebuild
impl --language python`.

The Python analyzer is the **reference implementation** for what all future language analyzers must
produce. Its output schema defines the protocol.

Similarly, the verification graph (test annotation scanning) gets a Python component for Python test
files:

```
jigy-verifier-python (Python script)
├── Scans for @jig.verifies("S-###") decorators in test files
├── Same subprocess protocol as analyzers
└── Ships alongside jigy binary
```

---

## What Stays in Go (No Subprocess)

Everything that is not language-specific lives in Go natively:

| Subsystem | Why Go, Not Subprocess |
|-----------|----------------------|
| Intent graph | Parses Markdown frontmatter (language-agnostic; same format for all projects) |
| Validation engine | All 17 rule types operate on NDJSON graph data, not source code |
| Query engine | BFS traversal over NDJSON; no language knowledge needed |
| Mend / auto-fix | Edits YAML frontmatter in intent documents; language-agnostic |
| Staleness detection | Calls `git hash-object` via `exec.Command` |
| MCP server | Wraps the query layer; language-agnostic |
| CLI | Command routing, output formatting |
| Config | Reads jig.toml / pyproject.toml |

The impl_graph **orchestrator** lives in Go. It discovers source files by language (via extensions or
explicit config), groups them, invokes the appropriate subprocess analyzer, streams the NDJSON output,
and writes the final `impl.ndjson`. The orchestrator owns no language-specific parsing logic.

---

## Multi-Language Projects

JIG can analyze a project with mixed languages by running multiple analyzers:

```toml
# jig.toml for a C + Python project
[source]
languages = ["c", "python"]

[analyzers]
c      = "jigy-analyzer-c"
python = "jigy-analyzer-python"
```

```
jigy rebuild impl
  → discover .c files  → spawn jigy-analyzer-c  → collect NDJSON
  → discover .py files → spawn jigy-analyzer-python → collect NDJSON
  → merge into impl.ndjson
  → write metadata line
```

All edges from all languages merge into a single `impl.ndjson`. The validation engine, query engine,
and mend system see a unified graph — they don't know or care which language produced which nodes.

This is a significant capability improvement over the current Python-only system.

---

## Test Annotation Strategy Per Language

The `@jig.verifies("S-###")` pattern is Python-specific syntax. Each language needs its own convention:

| Language | Test annotation convention |
|----------|--------------------------|
| Python | `@jig.verifies("S-001")` decorator (current) |
| Go | `// jig:verifies S-001` comment above test function |
| C | `/* jig:verifies S-001 */` comment above test function |
| Swift | `// jig:verifies S-001` comment above test function |
| Kotlin | `@JigVerifies("S-001")` annotation or `// jig:verifies S-001` comment |

The comment-based conventions are the lowest common denominator and work in every language without
requiring a runtime library. The verifier subprocess for each language scans test files for the
appropriate pattern and emits verification edges in NDJSON.

The Go core's verification graph orchestrator works identically to the impl graph orchestrator: it
discovers test files by language, invokes `jigy-verifier-{language}`, and merges the output.

---

## Strangler Fig Migration Strategy

The strangler fig works because the NDJSON files are the interface between all JIG subsystems.
Python and Go can share this interface without modification.

### Phase 1: Go Consumers (NDJSON readers)

Build the Go binary reading the NDJSON files that Python still generates. No Python output changes.
Users get a faster `jigy validate`, `jigy context`, and `jigy show` immediately.

```
Python jigy rebuild →  *.ndjson  ← Go jigy validate
                               ← Go jigy context
                               ← Go jigy mcp
```

Risk: zero. Go reads files Python wrote. Python is unchanged.

### Phase 2: Go Intent Graph and Verify Graph

Go takes over `jigy rebuild intent` and `jigy rebuild verify`. These subsystems parse Markdown
frontmatter and scan test annotations — no language-specific code analysis.

```
Go jigy rebuild intent → intent.ndjson
Go jigy rebuild verify → verify.ndjson
Python jigy rebuild impl → impl.ndjson
```

Risk: low. Frontmatter parsing is straightforward. Output schema is already tested.

### Phase 3: Go Impl Graph Orchestrator + Python Analyzer Subprocess

Go takes over `jigy rebuild impl` as the orchestrator. The Python analyzer is extracted from the
Python codebase into a standalone `jigy-analyzer-python` script. The Go orchestrator calls it as a
subprocess.

This is the critical structural change: the Python analyzer is no longer a Python module imported
by a Python CLI — it is a subprocess called by a Go binary. Externally, behavior is identical.
Internally, the architecture is now language-agnostic.

```
Go jigy rebuild impl
  → spawn jigy-analyzer-python
  → collect NDJSON via stdout pipe
  → write impl.ndjson
```

### Phase 4: Distribution

The distribution artifact is:
- `jigy` (Go binary, ~10MB)
- `jigy-analyzer-python` (Python script, ~50 lines at the entry point)
- `jigy-verifier-python` (Python script, ~30 lines at the entry point)

Users install via homebrew, `go install`, or download a release. The Python scripts are either
bundled in the binary (via `//go:embed`) or installed alongside it.

```bash
# Installation
brew install jigy
# or
go install github.com/youorg/jig/cmd/jigy@latest
```

No virtualenv. No `pip install`. No `source .venv/bin/activate`. Just `jigy validate`.

### Phase 5: Additional Language Analyzers

Add analyzers for C, Swift, Kotlin as separate projects or as part of the JIG repository:

```
cmd/jigy/                 Go CLI binary
cmd/jigy-analyzer-python/ Python script (bundled)
cmd/jigy-analyzer-c/      C/Go analyzer
cmd/jigy-analyzer-swift/  Swift analyzer
cmd/jigy-analyzer-kotlin/ Kotlin analyzer
```

---

## Test Suite Strategy

The Python test suite does not port line-for-line. It gets replaced with Go table-driven tests that
verify the same specs (S-###).

### During Transition

- **Keep Python tests running** throughout the transition. They protect the Python implementation.
- **Write Go tests** for each Go subsystem as it is built, referencing the same S-### specs.
- **Integration tests survive nearly unchanged**: they test CLI output (JSON or text). A Go binary
  produces the same output as Python for the same inputs. Integration tests can drive either binary
  via `exec.Command`.

### Go Test Conventions

Instead of Python decorators, Go tests use structured comments:

```go
// TestValidateIDFormat verifies S-018 S-019
// jig:verifies S-018 S-019
func TestValidateIDFormat(t *testing.T) {
    cases := []struct {
        id      string
        wantErr bool
    }{
        {"S-001", false},
        {"S-999", false},
        {"s-001", true},  // lowercase not allowed
        {"S-1",   true},  // not zero-padded
    }
    for _, c := range cases {
        err := validateIDFormat(c.id)
        if (err != nil) != c.wantErr {
            t.Errorf("validateIDFormat(%q) error=%v, wantErr=%v", c.id, err, c.wantErr)
        }
    }
}
```

The `jigy-verifier-go` (or the Go impl_graph analyzer) scans for `// jig:verifies S-###` comments in
`_test.go` files.

### What to Test Thoroughly in Go

| Module | Test approach |
|--------|--------------|
| intent_graph | Fixtures: synthetic spec/outcome/charter MD files → compare NDJSON output |
| validation rules | Table-driven unit tests per rule type (17 rules × multiple cases each) |
| query engine | Synthetic NDJSON graphs → verify traversal and identifier resolution |
| mend engine | Synthetic validation errors → verify YAML edits applied correctly |
| analyzer protocol | Mock subprocess → verify Go orchestrator handles NDJSON stream |
| CLI integration | `exec.Command("jigy", ...)` against test fixtures → compare stdout |

### The Spec Is The Ground Truth

Every Go test that replaces a Python test should `// jig:verifies S-###` the same spec the Python
test verified. The JIG spec hierarchy (S-###) defines what the system must do, independent of
implementation language. Tests in Go verify the same contracts as tests in Python.

---

## Go External Dependencies

Minimizing external dependencies is a goal. The Go standard library handles most of what JIG needs:

| Need | Approach |
|------|---------|
| JSON / NDJSON | `encoding/json` (stdlib streaming decoder) |
| TOML | `github.com/BurntSushi/toml` (single dependency, minimal, widely used) |
| YAML | `gopkg.in/yaml.v3` (single dependency, stable) |
| Markdown frontmatter | Custom parser (~50 lines) using stdlib `bufio` and `strings` |
| CLI framework | `github.com/spf13/cobra` (industry standard for Go CLIs) |
| MCP server | `github.com/mark3labs/mcp-go` or implement the stdio JSON-RPC protocol directly (~200 lines) |
| Git operations | `exec.Command("git", ...)` — no Go git library needed |
| File watching | `github.com/fsnotify/fsnotify` if auto-rebuild is needed; otherwise skip |

Total: 3-4 external dependencies. Far fewer than the current Python setup.

The frontmatter parser deserves a note: `python-frontmatter` is 1,000 lines of Python. A Go
frontmatter parser for JIG's specific subset (YAML between `---` fences) is ~50 lines using
stdlib `bufio` + `gopkg.in/yaml.v3`. No external frontmatter library is needed.

---

## Scope Inventory by Effort

### Low Effort (direct port, well-understood logic)

| Module | Python LoC | Notes |
|--------|-----------|-------|
| Config system | 324 | TOML/YAML, path resolution |
| Hashing / staleness | 451 | `exec.Command("git", ...)` |
| Templates / init | 663 | `text/template` |
| MCP server wrapper | 100 | Thin layer over query functions |
| Validation reporting | 181 | String formatting |
| CLI output formatting | ~150 | JSON/Markdown/text modes |

### Medium Effort (non-trivial logic, well-scoped)

| Module | Python LoC | Notes |
|--------|-----------|-------|
| Intent graph generator | 707 | Frontmatter parsing, NDJSON emission |
| Verification graph | 400 | Test file discovery, annotation scanning |
| Query engine | 1,000 | BFS traversal, identifier resolution |
| Mend engine | 667 | YAML editing, fixed-point iteration |
| CLI commands | 2,658 | Cobra instead of Click; mostly routing |
| Analyzer orchestrator | ~200 | Subprocess management, NDJSON streaming |

### High Effort (complex logic, many edge cases)

| Module | Python LoC | Notes |
|--------|-----------|-------|
| Validation rule context | 555 | Complex state: specs, outcomes, bricks, layers |
| Validation rule registry | 622 | 17 rule types, registration system |
| Validation rule types | 1,500+ | 17 individual rule implementations |

### Stays Python (not ported to Go)

| Module | Python LoC | Notes |
|--------|-----------|-------|
| Python AST analyzer | 960 | Uses Python's own ast module; correct tool |
| Coverage audit | 310 | Requires pytest integration; stays Python |

Total Go work: ~9,000-11,000 LoC of Go (smaller than Python due to Go's verbosity trade-offs being
offset by eliminating framework boilerplate and test infrastructure).

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Core language | Go | Fast startup, single binary, excellent stdlib, designed for CLI tooling |
| Analyzer architecture | Subprocess + NDJSON protocol | Language-agnostic; already have the NDJSON format; proven pattern (LSP, SCIP) |
| Python analyzer | Stays Python | Correct tool for the job; Python is installed on Python projects |
| Analyzer discovery | Same dir as binary → PATH → jig.toml config | Bundled gets first pick; user can override |
| NDJSON format | Unchanged | Zero migration cost; existing graphs remain valid |
| Test annotation | `// jig:verifies S-###` comment | Works in every language; no runtime library dependency |
| Migration strategy | Strangler fig via NDJSON seam | No flag day; Go and Python can coexist; verify parity before cutover |
| Test suite | Replace Python tests with Go table-driven tests | Same specs, new language; Python tests run until Go counterpart is verified |
| External Go dependencies | 3-4 total | toml, yaml.v3, cobra, mcp-go (optional) |
| Frontmatter parsing | Custom ~50 lines | JIG's frontmatter subset is simple; no library needed |
| CLI framework | Cobra | Industry standard; similar paradigm to Click but Go-native |
| Audit subsystem | Defer or keep Python | pytest integration is deeply Python-specific; low priority for Go port |

---

## What JIG Looks Like After Conversion

A new user on a project with Python + Swift code:

```bash
# Install once
brew install jigy

# In any JIG-enabled project — no setup, no venv
jigy validate          # ~10ms startup, 0 dependencies
jigy context S-042     # instant
jigy rebuild           # Go handles intent/verify; Python script handles .py; Swift analyzer handles .swift
```

The MCP server starts in milliseconds. CI pipelines run `jigy validate` without activating a virtualenv.
Agents call `jigy context` without worrying about the Python runtime.

For Python project analysis, `jigy` ships with `jigy-analyzer-python` bundled (either as an embedded
resource or as a companion script). Users on Python projects already have Python — the analyzer just
works.

---

## Success Criteria

- [ ] `jigy validate` runs in <50ms on a cold start (no venv, no Python)
- [ ] Single binary installation: `brew install jigy` or `go install`
- [ ] `jigy rebuild intent`, `jigy rebuild verify` work in Go
- [ ] `jigy rebuild impl` calls `jigy-analyzer-python` as a subprocess and produces identical `impl.ndjson`
- [ ] All 17 validation rules produce identical output as Python implementation on same fixtures
- [ ] `jigy context`, `jigy validate`, `jigy mcp` produce identical output to Python versions
- [ ] Go test suite covers same S-### specs as Python test suite (verified via `jigy validate`)
- [ ] A project with mixed languages (e.g., Python + C) runs `jigy rebuild` successfully
- [ ] `jig.toml` `[analyzers]` section allows user-specified analyzer paths
- [ ] Missing language analyzer produces a warning, not a failure

---

## Out of Scope for This Proposal

- Specific Go package structure / module layout (belongs in JIGPLAN)
- Analyzer implementations for C, Swift, Kotlin (separate scopes)
- Changes to the NDJSON schema or validation rules
- `jigy audit coverage` (pytest-specific; defer; keep Python)
- Changes to the `digy` tool (separate concern)

---

## Related Documents

- `jig/Charter_JIG.md` — G-001 through G-005 (this supports all five, primarily G-002 and G-003)
- `dig/archive/C001_PROPOSAL_JIG-Core-Artifacts-Contract.md` — NDJSON schema this proposal relies on
- `dig/archive/AG015_Implementation-Graph-Feasibility.md` — Original feasibility analysis for impl graph
- `dig/wip/E030_SCOPE_MCP_Server.md` — MCP scope; the Go MCP server inherits this design

---

**End of Proposal**
