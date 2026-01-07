---
title: "JIG & DIG CLI Design Manifesto: The Dual-Audience Interface"
type: exploration
status: active
created: 1736100000
created_human: "2026-01-05 12:00 CST"
parent: null
children: ["[[DJ002_SCOPE_CLI_Recommendations]]"]
---
# JIG & DIG CLI Design Manifesto: The Dual-Audience Interface

**Version:** 1.1
**Date:** 2026-01-05
**Applies to:** JIG, DIG, and future companion tools

---

## Preamble

Developer tools serve two audiences that think differently:

1. **Humans** — who scan, interpret context, and appreciate aesthetics
2. **Agents** — who parse, query, and optimize for token efficiency

A CLI that serves only humans wastes agent context on formatting. A CLI that serves only agents alienates the humans who configure, debug, and trust it.

This manifesto establishes principles for CLIs that serve both audiences excellently, drawing from the Unix tradition for humans and emerging AI agent research for machines.

---

## Part I: Core Philosophy

### 1. One Command, Three Modes

Every command can express its output in three formats:

| Mode | Flag | Audience | Optimized For |
|------|------|----------|---------------|
| Default | (none) | Human | Terminal reading |
| JSON | `--json` / `-j` | Agent | Parsing and acting |
| Markdown | `--markdown` / `-m` | LLM | Context injection and reasoning |

```bash
# Human mode (default) — rich terminal formatting
$ jigy context
JIG CONTEXT: my-project
════════════════════════
PROJECT STATE
  Specs: 91 total | 78 implemented
  Gaps: 3 unimplemented, 13 unverified

# JSON mode — structured for parsing
$ jigy context --json
{"specs":{"total":91,"implemented":78},"gaps":{"unimplemented":3,"unverified":13}}

# Markdown mode — optimized for LLM context
$ jigy context --markdown
# JIG Context: my-project

## Project State
- **Specs:** 91 total | 78 implemented
- **Gaps:** 3 unimplemented, 13 unverified
```

**All three modes are always available.** The command decides how to best represent itself in each format.

### 2. Verb-First Commands

Commands describe **actions users take**, not objects in the system:

```bash
# CORRECT: What can I do?
jigy rebuild impl
jigy validate bricks
digy new exploration "Title"

# WRONG: What objects exist?
jigy impl rebuild
digy exploration new "Title"
```

Verb-first answers "What can I do?" immediately. Noun subcommands narrow scope.

### 3. Progressive Disclosure

Basic usage requires zero knowledge:

```bash
jigy align    # Does everything useful
digy validate # Checks everything
```

Advanced usage narrows scope:

```bash
jigy rebuild impl     # Just implementation graph
jigy validate bricks  # Just brick validation
digy validate dig/wip/D017_PLAN.md  # Just one file
```

### 4. Radical Flag Minimalism

**Global flags are sacred.** Each project has exactly three:

| Flag | Purpose |
|------|---------|
| `--help` / `-h` | Show help for any command |
| `--version` | Show version (root only) |
| `--no-rebuild` | Skip automatic graph rebuild |

All other flags are **per-command** but **universally supported** across all commands.

### 5. Fail Fast, Fail Clearly

No silent failures. No warnings that should be errors. No `--strict` flag because strict is the only mode.

```bash
$ jigy validate
Error: INVALID_REFERENCE
  File: jig/specifications/S-042.md:7
  Reference: O-999 (does not exist)

  Tip: Run `jigy show outcomes` to see valid outcome IDs
```

Errors include:
- **What** went wrong (error code)
- **Where** it happened (file:line)
- **How to fix it** (actionable tip)

---

## Part II: Designing for Humans

### The Unix Tradition (Adapted)

Humans have 50 years of muscle memory. Respect it—but adapt for trust and discoverability.

| Principle | Application |
|-----------|-------------|
| **Minimal feedback on success** | `validate` with no errors = one-line summary with metrics |
| **Errors to stderr** | Parsing stdout never polluted by errors |
| **Exit codes matter** | 0 = success, non-zero = failure |
| **Pipelines work** | Output can be piped, grepped, redirected |

**Why not pure silence?** New tools need to earn trust. Feedback like "Validated 91 specs, 11 bricks" confirms the command ran and teaches users what the tool does.

### The Git Model

Git is the gold standard for developer CLIs:

| Git Pattern | Application |
|-------------|-------------|
| Bare command shows help | `jigy` → usage and commands |
| Auto-discovery | Find project root by walking up |
| Sensible defaults | Works with zero configuration |
| Designed for terminals | Color, formatting, counts, summaries |

### Output by Command Type

Different commands have different default output behaviors:

| Command Type | Default Behavior | Examples |
|--------------|------------------|----------|
| **Validation** | One-line summary with metrics | `jigy validate` → "Validated 91 specs, 11 bricks." |
| **Rebuild** | One-line summary with metrics | `jigy rebuild` → "Rebuilt 3 graphs." |
| **Creation** | Minimal confirmation | `jigy new spec` → "Created S-094: Title" |
| **Query/Display** | Full output | `jigy context`, `jigy show`, `jigy audit` |

```bash
# Validation: one-line confirmation with metrics
$ jigy validate
Validated 91 specs, 11 bricks.

# With auto-rebuild: combined feedback
$ jigy validate
Rebuilt 3 graphs. Validated 91 specs, 11 bricks.

# Creation: confirm what was created
$ jigy new spec "Token Refresh"
Created S-094: Token Refresh
  File: jig/specifications/S-094_Token_Refresh.md

# Query: output is the product
$ jigy audit gaps
COVERAGE GAPS
═════════════
UNIMPLEMENTED (3)
  S-044  CRDT Conflict Resolution      (O-012)
  ...
```

### Human Output Principles

1. **Scan, don't read** — Bold headers, visual hierarchy, whitespace
2. **Counts and summaries** — "91 specs | 78 implemented | 13 gaps"
3. **Show the path** — "File: jig/specifications/S-042.md:7"
4. **Progressive detail** — Summary first, details on request (`-v`)

### Markdown is an Export Format

`--markdown` is for **export and LLM injection**, not terminal reading.

Markdown in a terminal shows raw syntax (`**bold**`) that doesn't render. Humans in terminals want rich formatting: box drawing, color, alignment.

**When humans use `--markdown`:**
- Piping to a file: `jigy context --markdown > context.md`
- Copying to documentation
- Feeding to another tool that expects markdown

---

## Part III: Designing for Agents

### The Agent Reality

AI agents (Claude, GPT-4, Gemini) have specific constraints:

1. **Context is precious** — Every token of output consumes reasoning capacity
2. **Parsing is fallible** — Unstructured text requires interpretation
3. **State is external** — Agents can't remember across sessions
4. **Tools replace reasoning** — A good tool call saves 100 tokens of deduction

### Two Agent Modes: Acting vs Reasoning

Agents need different formats for different purposes:

| Purpose | Format | Flag | When to Use |
|---------|--------|------|-------------|
| **Acting** (parse & branch) | JSON | `--json` | Tool responses that feed into logic |
| **Reasoning** (understand & plan) | Markdown | `--markdown` | Context injection for comprehension |

**JSON is for tool calls:**
```python
# Agent parses and acts
result = call_tool("jigy validate --json")
if result["valid"]:
    proceed()
else:
    for error in result["errors"]:
        fix(error["file"], error["code"])
```

**Markdown is for context injection:**
```
<system>
You are working on a JIG project. Current state:

# JIG Context: my-project

## Project State
- **Specs:** 91 total | 78 implemented
- **Top Gap:** S-044 CRDT Conflict Resolution
</system>
```

**Why the split?** LLMs reason better with prose than JSON. Markdown is often more token-efficient for context (fewer structural characters), while JSON is essential for deterministic parsing.

### JSON Output Principles

JSON output is:
- **Single-line** (no pretty-print — saves tokens)
- **Complete** (all data needed, no follow-up queries)
- **Typed** (numbers are numbers, not "91 specs")
- **Actionable** (includes error codes and suggested next steps)

```json
{"valid":false,"errors":[{"code":"INVALID_REFERENCE","file":"S-042.md","line":7,"tip":"Run jigy show outcomes"}]}
```

### Markdown Output Principles

Markdown output is:
- **Readable** (headers, bullets, emphasis)
- **Semantic** (structure conveys meaning)
- **Dense** (information-rich without verbosity)
- **Complete** (stands alone as context)

```markdown
# Validation Result

**Status:** Invalid (2 errors)

## Errors

1. **INVALID_REFERENCE** in `S-042.md:7`
   - Reference: `O-999` does not exist
   - Tip: Run `jigy show outcomes`
```

### Context Density

One rich query beats five narrow queries:

```bash
# BAD: Agent needs 5 calls
jigy show spec S-042 --json
jigy show spec S-041 --json
jigy show brick B-crdt --json
jigy show outcome O-012 --json

# GOOD: Agent needs 1 call
jigy context spec S-042 --json
# Returns spec + related specs + brick + outcome + gaps + next steps
```

### The `context` Command

Both JIG and DIG have a first-class `context` command that synthesizes orientation:

| `show` | `context` |
|--------|-----------|
| Static artifact display | Dynamic synthesis |
| Single item | Item + neighborhood |
| What exists | What matters now |
| For checking details | For getting oriented |

The `context` command is particularly useful with both output modes:
- `--json` — When agent needs to parse project state and decide what to do
- `--markdown` — When output goes into system prompt for orientation

---

## Part IV: The Flag System

### Output Format Flags

Three flags control output format. **All are universally supported** on every command.

| Flag | Short | Purpose |
|------|-------|---------|
| `--json` | `-j` | Machine-parseable JSON |
| `--markdown` | `-m` | LLM-optimized markdown |
| `--verbose` | `-v` | More detail in any format |

### Flag Combinations

| Combination | Behavior |
|-------------|----------|
| (none) | Default human output |
| `-v` | Verbose human output |
| `-j` | Compact JSON |
| `-j -v` | Verbose JSON (more fields) |
| `-m` | Compact markdown |
| `-m -v` | Verbose markdown (more detail) |
| `-j -m` | **Error:** mutually exclusive |

### Success Output Semantics

**All modes provide feedback on success.** The format differs by output mode:

```bash
# Default: one-line summary with metrics
$ jigy validate
Validated 91 specs, 11 bricks.

# JSON: structured data for parsing
$ jigy validate --json
{"valid":true,"errors":[],"checked":{"specs":91,"bricks":11}}

# Markdown: human-readable confirmation
$ jigy validate --markdown
Validation passed. Checked 91 specs, 11 bricks.
```

**Rationale:** Feedback builds trust and aids discoverability. Users learn what the tool did, not just that it succeeded.

### Universal Applicability

All flags work on all commands. No exceptions. No errors for "unsupported."

| Command | `-j` | `-m` | `-v` |
|---------|------|------|------|
| `validate` | ✓ | ✓ | ✓ |
| `rebuild` | ✓ | ✓ | ✓ |
| `context` | ✓ | ✓ | ✓ |
| `show` | ✓ | ✓ | ✓ |
| `audit` | ✓ | ✓ | ✓ |
| `new` | ✓ | ✓ | ✓ |
| `init` | ✓ | ✓ | ✓ |

Each command decides how to best represent itself in each format. Some markdown is rich (context), some is simple (new). But the flag always works.

### Flag Scope

| Type | Flags | Scope |
|------|-------|-------|
| Global | `--help`, `--version`, `--no-rebuild` | Defined once, work everywhere |
| Output | `-j`, `-m`, `-v` | Per-command, but universal |

---

## Part V: Cross-Project Alignment

### DIG and JIG: Parallel Universes

DIG and JIG are complementary:

| Aspect | DIG | JIG |
|--------|-----|-----|
| **Purpose** | Why decisions were made | What should be true |
| **Lifecycle** | Archival (fades) | Evergreen (updated) |
| **Command** | `digy` | `jigy` |
| **Root** | `dig/` | `jig/` |

Their CLIs are **parallel in structure** so learning one teaches you the other.

### Shared Command Patterns

| Pattern | DIG | JIG |
|---------|-----|-----|
| Initialize | `digy init` | `jigy init` |
| Validate | `digy validate` | `jigy validate` |
| Create | `digy new <type> "Title"` | `jigy new <type> "Title"` |
| Context | `digy context [target]` | `jigy context [target]` |
| Show | `digy show <artifact>` | `jigy show <artifact>` |
| Rebuild | `digy graph` | `jigy rebuild` |

### Shared Flag Semantics

| Flag | Short | Meaning (both tools) |
|------|-------|----------------------|
| `--json` | `-j` | Machine-parseable JSON output |
| `--markdown` | `-m` | LLM-optimized markdown |
| `--verbose` | `-v` | Show progress and details |
| `--help` | `-h` | Show help |
| `--version` | | Show version |

### Integration Points

1. **Cross-References** — DIG documents can link to JIG specs they produced
2. **Shared Conventions** — Same filename patterns, same frontmatter fields
3. **Unified Tooling** — Obsidian works on both, Dataview queries both
4. **Parallel Workflows** — `digy validate && jigy validate`

---

## Part VI: Implementation Checklist

### For New Commands

- [ ] Verb-first naming (`do-thing`, not `thing-do`)
- [ ] Human output by default (rich terminal formatting)
- [ ] `-j` produces single-line JSON
- [ ] `-m` produces clean markdown
- [ ] `-v` adds detail to any format
- [ ] Errors to stderr with codes and tips
- [ ] Exit code 0 on success, non-zero on failure
- [ ] Documented before implemented

### For Output Formats

**Default (Human):**
- [ ] Box drawing, alignment, color (respects `NO_COLOR`)
- [ ] Counts and summaries
- [ ] One-line feedback with metrics (for validation/rebuild commands)
- [ ] Minimal confirmation (for creation commands)

**JSON (`-j`):**
- [ ] Single-line (no pretty-print)
- [ ] Complete (no follow-up needed)
- [ ] Typed (numbers, booleans, not strings)
- [ ] Error codes included
- [ ] Suggested next actions included
- [ ] Includes metrics for discoverability

**Markdown (`-m`):**
- [ ] Headers and structure
- [ ] Emphasis for key data
- [ ] Code blocks for paths/commands
- [ ] Includes metrics for discoverability

### For Error Messages

- [ ] Error code (INVALID_REFERENCE, not "error")
- [ ] Location (file:line)
- [ ] What went wrong (clear description)
- [ ] How to fix (actionable tip)
- [ ] Relevant command suggestion

---

## Part VII: Anti-Patterns

### Don't Do This

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| `--output-format json` | Use `--json` (shorter, clearer) |
| `--format=yaml` | Support one machine format, not many |
| `--quiet` | Default output is already minimal; redirect if needed |
| `--strict` | Strict is the only mode |
| `--lenient` | Silent failures hide bugs |
| `--project-dir` | Auto-discovery handles this |
| `--config-file` | Convention over configuration |
| Silent success | Feedback builds trust and discoverability |
| Warnings on success | Either it's an error or it's fine |
| Pretty-printed JSON | Wastes agent tokens |
| Prose errors | Unparseable by agents |
| Selective flag support | All flags work on all commands |

### Exceptions

| Exception | When Allowed |
|-----------|--------------|
| `--no-color` | When `NO_COLOR` env isn't enough |
| `--dry-run` | For destructive operations only |
| `--force` | When safety prompt is needed |

---

## Part VIII: Quick Reference

### The Three Modes

```bash
command           # Human: rich terminal output
command -j        # Agent: JSON for parsing
command -m        # LLM: Markdown for context
```

### Adding Detail

```bash
command -v        # Verbose human output
command -j -v     # Verbose JSON (more fields)
command -m -v     # Verbose markdown (more detail)
```

### The Mental Model

```
Who's reading?     What are they doing?     Use:
─────────────────────────────────────────────────
Human in terminal  Interacting              (default)
Human exporting    Saving/copying           -m
Agent tool call    Parsing → acting         -j
Agent context      Understanding → reasoning -m
```

---

## Conclusion

A great CLI is invisible. It does what you expect, fails when it should, and stays out of the way.

For humans: follow Unix and Git. Minimal feedback builds trust. Errors are clear. Commands are verbs.

For agents: JSON for tools, markdown for context. Error codes are parseable. One call beats five.

Build CLIs that serve both, and you build tools that last.

---

## References

- The Unix Philosophy (Doug McIlroy, 1978)
- Git CLI Design (Junio Hamano, Git project)
- Anthropic Tool Use Best Practices (2024-2025)
- OpenAI Function Calling Guide (2024-2025)
- Google Gemini Tool Use Documentation (2025)
- JIG A-002: CLI Command Architecture
- DIG D017: CLI Output Unification

---

*This manifesto is evergreen. When principles conflict with practice, update the manifesto or fix the practice.*
