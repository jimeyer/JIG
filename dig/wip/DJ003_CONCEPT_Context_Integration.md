---
title: JIG/DIG Context Integration
type: exploration
status: active
created: 1736200000
created_human: 2026-01-06 10:00 CST
parent: "[[DJ002_SCOPE_CLI_Recommendations]]"
children:
  - "[[DJ004_CONCEPT_Strategy]]"
  - "[[DJ005_SCOPE_CLI_Implementation]]"
---
# JIG/DIG Context Integration


## Overview

The `context` command is the primary interface for AI agents and humans to understand the state of a project. When JIG and DIG are used together, context from both tools should be available seamlessly.

This document describes the design for cross-tool context integration, including graph traversal depth, content selection, verbose mode behavior, and measurement strategies.

---

## Research Foundation

This design draws from current best practices in AI agent context engineering:

### The Guiding Principle

> "Find the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."
> — [Anthropic: Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### Key Research Findings

**Context Rot:** As token count increases, model accuracy degrades. This stems from n² attention relationships that stretch the model's attention budget thin. Smaller, focused contexts often outperform massive contexts for targeted tasks.

**Avoid Context Dumping:** Early agent implementations fall into the "context dumping" trap—placing large payloads directly into context. This creates a permanent tax on the session.

**Just-in-Time Retrieval:** Rather than pre-loading everything, maintain lightweight identifiers and dynamically load data using tools when needed. This is the approach used by Claude Code with glob/grep.

**Observation Masking vs Summarization:** [JetBrains research](https://blog.jetbrains.com/research/2025/12/efficient-context-management/) found that observation masking (replacing older outputs with placeholders) cut costs by 52% while improving solve rates by 2.6% compared to LLM summarization.

**Optimal Chunk Size:** [RAG research](https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025) consistently finds 256-512 tokens per semantic chunk with 10-20% overlap provides optimal retrieval precision.

### Implications for JIG/DIG

1. **Bounded depth** — Don't traverse the entire graph; stop at relevance boundaries
2. **High-signal selection** — Include identity, status, and relationships; exclude full content
3. **Hierarchical structure** — Preserve document structure in output
4. **Token budget awareness** — Target specific token ranges per artifact

---

## Goals

### G1: Seamless Cross-Tool Context

A single `context` command should return everything relevant, regardless of which tool owns the data.

```bash
jigy context S-004
# Returns: JIG context for S-004 + DIG deliberations that produced S-004
```

The user shouldn't need to know which tool to query or use special flags.

### G2: Loose Coupling

Each tool owns its own data and logic. JIG doesn't need to understand DIG's graph format, and vice versa. Integration happens through a simple subprocess call interface.

### G3: Graceful Degradation

If only one tool is installed, or if peer integration is disabled, commands work normally without errors. Missing peer context is simply omitted.

### G4: Transparent Configuration

Integration is controlled by explicit config that users can see and modify. No hidden magic.

### G5: Consistent Interface

Both tools use the same pattern. Learning one teaches you the other.

### G6: Token Efficiency

Context output should be dense with high-signal information. Target 300-800 tokens for default mode, 800-2000 tokens for verbose mode. Never exceed 5000 tokens for a single context query.

---

## Graph Traversal Depth

### The Depth Model

Graph traversal uses a bounded depth model where relevance decays with each hop:

| Depth | Relationship | Default | Verbose |
|-------|--------------|---------|---------|
| 0 | Target artifact itself | ✓ Full | ✓ Full |
| 1 | Direct relationships | ✓ Summary | ✓ Detail |
| 2 | One hop further | ✗ Count only | ✓ Summary |
| 3+ | Distant relationships | ✗ Omitted | ✗ Count only |

### JIG Depth Examples

**`jigy context S-004` (default):**

```
Depth 0: S-004 itself
         → title, status, type, outcome

Depth 1: Direct relationships
         → implementations (F-xxx): ID + file:line
         → tests (T-xxx): ID + file:line
         → outcome (O-xxx): ID + title
         → brick: ID only

Depth 2: One hop further
         → sibling specs (same outcome): count only ("3 related specs")
         → deliberation: ID only (if present)
```

**`jigy context S-004 -v` (verbose):**

```
Depth 0: S-004 itself
         → title, status, type, outcome, full description

Depth 1: Direct relationships
         → implementations: ID + file:line + function signature
         → tests: ID + file:line + test name
         → outcome: ID + title + goal
         → brick: ID + layer + dependencies

Depth 2: One hop further
         → sibling specs: ID + title + status for each
         → deliberation: ID + title + status
         → goal (via outcome): ID + title

Depth 3: Distant
         → Charter goal count only
```

### DIG Depth Examples

**`digy context D017` (default):**

```
Depth 0: D017 itself
         → title, type, status, created date

Depth 1: Direct relationships
         → parent: ID + title
         → children: ID + title for each
         → produces: JIG spec IDs only

Depth 2: One hop further
         → siblings (same parent): count only
         → grandchildren: count only
```

**`digy context D017 -v` (verbose):**

```
Depth 0: D017 itself
         → title, type, status, created, decision summary

Depth 1: Direct relationships
         → parent: ID + title + type + status
         → children: ID + title + type + status for each
         → produces: JIG spec ID + title + status for each

Depth 2: One hop further
         → siblings: ID + title + type for each
         → full deliberation chain (ancestors to root)
```

### Why Bounded Depth?

1. **Relevance decay** — Each hop away from target reduces relevance
2. **Token budget** — Unbounded traversal explodes token count
3. **Context rot** — LLMs struggle with information buried in large contexts
4. **Actionability** — Agents need focused context to make decisions

### Depth Configuration

Default depths are tuned for typical agent tasks. Future versions may allow configuration:

```toml
[context]
default_depth = 1
verbose_depth = 2
max_depth = 3
```

---

## Content Selection

### What Gets Returned

For each artifact at each depth level, specific fields are selected:

#### JIG Specification (Depth 0 - Target)

| Mode | Fields Included |
|------|-----------------|
| Default | `id`, `title`, `status`, `outcome`, `brick` |
| Verbose | + `description`, `acceptance_criteria`, `created`, `updated` |

#### JIG Specification (Depth 1 - Related)

| Mode | Fields Included |
|------|-----------------|
| Default | `id`, `title`, `status` |
| Verbose | + `outcome`, `brick` |

#### JIG Implementation (Depth 1)

| Mode | Fields Included |
|------|-----------------|
| Default | `function_id`, `file:line` |
| Verbose | + `signature`, `docstring` (first line only) |

#### JIG Test (Depth 1)

| Mode | Fields Included |
|------|-----------------|
| Default | `test_id`, `file:line` |
| Verbose | + `test_name`, `verifies` (spec list) |

#### DIG Document (Depth 0 - Target)

| Mode | Fields Included |
|------|-----------------|
| Default | `filename`, `title`, `type`, `status`, `parent`, `children` |
| Verbose | + `decision`, `created`, `produces`, first 200 chars of content |

#### DIG Document (Depth 1 - Related)

| Mode | Fields Included |
|------|-----------------|
| Default | `filename`, `title`, `type` |
| Verbose | + `status`, `decision` |

### What Gets Excluded

**Always excluded from context output:**

- Full document/file content (use `show` command instead)
- Full code bodies (context provides pointers, not code)
- Historical versions or changelog
- Validation errors (use `validate` command)
- Build/test output logs

**Rationale:** Context is for orientation, not exhaustive detail. Agents can use other tools (`show`, `Read`, `grep`) to retrieve full content when needed.

### Token Budget Guidelines

Based on [RAG chunking research](https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025) and Anthropic's guidance:

| Context Type | Default Target | Verbose Target | Hard Maximum |
|--------------|----------------|----------------|--------------|
| Single spec | 200-400 tokens | 500-1000 tokens | 2000 tokens |
| Project overview | 400-800 tokens | 1000-2000 tokens | 4000 tokens |
| Cross-tool combined | 500-1000 tokens | 1200-2500 tokens | 5000 tokens |

**Why these limits?**

- Fits comfortably in typical tool response expectations
- Leaves room for agent reasoning in context window
- Avoids "lost in the middle" problem with medium-length contexts
- Aligns with optimal RAG chunk sizes (256-512 tokens per semantic unit)

---

## Verbose Mode (`-v`)

### What Verbose Adds

The `-v` flag increases both depth and detail:

| Aspect | Default | Verbose |
|--------|---------|---------|
| Traversal depth | 1 hop | 2 hops |
| Fields per artifact | Core identity | Extended metadata |
| Relationship detail | Counts/IDs | IDs + titles + status |
| Cross-references | ID only | ID + summary |

### Verbose Output Example

**`jigy context S-004` (default, ~300 tokens):**

```
JIG CONTEXT: S-004 Minimal Success Feedback
═══════════════════════════════════════════
Status: Implemented, Verified
Outcome: O-015
Brick: B-cli

IMPLEMENTATIONS (2):
  F-jig.cli.output.format_success    src/jig/cli/output.py:45
  F-jig.cli.output.format_metrics    src/jig/cli/output.py:78

TESTS (3):
  T-test_output.test_format_success  tests/test_output.py:23
  T-test_output.test_format_metrics  tests/test_output.py:45
  T-test_output.test_combined        tests/test_output.py:67

Related: 2 sibling specs (same outcome)
```

**`jigy context S-004 -v` (verbose, ~800 tokens):**

```
JIG CONTEXT: S-004 Minimal Success Feedback
═══════════════════════════════════════════
Status: Implemented, Verified
Type: specification
Created: 2026-01-05
Outcome: O-015 (CLI Output Design)
  Goal: G-002 (Continuity Across Sessions)
Brick: B-cli (Layer: interface)
Deliberation: D017 (CLI Output Unification)

DESCRIPTION:
Commands provide one-line feedback with metrics on success,
building trust and aiding discoverability.

IMPLEMENTATIONS (2):
  F-jig.cli.output.format_success
    src/jig/cli/output.py:45
    def format_success(command: str, metrics: dict) -> str

  F-jig.cli.output.format_metrics
    src/jig/cli/output.py:78
    def format_metrics(counts: dict) -> str

TESTS (3):
  T-test_output.test_format_success  tests/test_output.py:23
  T-test_output.test_format_metrics  tests/test_output.py:45
  T-test_output.test_combined        tests/test_output.py:67

SIBLING SPECS (same outcome):
  S-003  JSON Output Format           implemented
  S-005  Verbose Flag                 implemented
```

### When to Use Verbose

| Use Case | Recommended Mode |
|----------|------------------|
| Quick orientation | Default |
| Agent tool call (parsing) | Default + JSON |
| Understanding relationships | Verbose |
| Debugging/investigation | Verbose |
| LLM context injection | Default (token-efficient) |
| Documentation/export | Verbose + Markdown |

---

## The Integration Pattern

### How It Works

When `jigy context <id>` is called:

1. **JIG builds its own context** for `<id>` (spec details, implementations, tests, etc.)
2. **If `include_dig=true` in `jig.toml`:**
   - JIG calls `digy context <id> -m` as a subprocess
   - DIG returns whatever context it has for `<id>`
   - JIG appends DIG's output to its own
3. **Return combined result**

The same pattern works in reverse for `digy context <id>`.

### The Key Insight

Each tool decides what context it has for any given identifier:

| Tool receives | Tool's logic |
|---------------|--------------|
| `digy context D017` | D017 is a DIG doc → return its context |
| `digy context S-004` | S-004 is not a DIG doc → search for DIG docs that reference S-004 |
| `jigy context S-004` | S-004 is a JIG spec → return its context |
| `jigy context D017` | D017 is not a JIG artifact → search for JIG specs that reference D017 |

The calling tool doesn't need to know how the peer tool will interpret the identifier. It just passes it through and gets back relevant context (or nothing).

---

## Identifier Resolution

### DIG: Resolving Non-DIG Identifiers

When DIG receives an identifier that isn't a DIG document (e.g., `S-004`), it should search its graph for related deliberations.

**Primary mechanism:** Search the `produces` frontmatter field.

```yaml
# In DIG document D017_JIGPLAN_CLI_Output.md
---
title: CLI Output Unification
type: jigplan
produces: [S-004, S-005, S-007]
---
```

When `digy context S-004` is called:
1. Search all DIG documents for `produces` containing `S-004`
2. Return context for matching documents (D017 in this case)
3. If no matches, return empty/minimal response

**Additional search strategies** (implementation can evolve):
- Full-text search for the identifier in document content
- Search `related` or other frontmatter fields
- Search by topic/tag similarity

### JIG: Resolving Non-JIG Identifiers

When JIG receives an identifier that isn't a JIG artifact (e.g., `D017`), it should search its graph for related specs.

**Primary mechanism:** Search the `deliberation` frontmatter field (if present).

```yaml
# In JIG spec S-004_Minimal_Success_Feedback.md
---
id: S-004
title: Minimal Success Feedback
deliberation: D017
---
```

When `jigy context D017` is called:
1. Search all JIG specs for `deliberation` containing `D017`
2. Return context for matching specs
3. If no matches, return empty/minimal response

---

## Frontmatter Convention

### DIG Documents

| Field | Type | Purpose |
|-------|------|---------|
| `produces` | list | JIG spec IDs this deliberation produced |

```yaml
---
title: CLI Output Unification
type: jigplan
status: implemented
produces: [S-004, S-005, S-007]
---
```

**Notes:**
- `produces` is optional but enables cross-tool discovery
- Values should be valid JIG spec IDs
- Validation can verify referenced specs exist

### JIG Documents

| Field | Type | Purpose |
|-------|------|---------|
| `deliberation` | string | DIG document that produced this spec |

```yaml
---
id: S-004
title: Minimal Success Feedback
type: specification
deliberation: D017
---
```

**Notes:**
- `deliberation` is optional (many specs won't have tracked deliberation)
- Value should be a valid DIG document identifier
- Validation can verify referenced doc exists

---

## Output Composition

### Combined Context Output

When peer context is included, outputs are concatenated with clear separation:

**Default (human) mode:**
```
JIG CONTEXT: S-004 Minimal Success Feedback
═══════════════════════════════════════════
STATUS: Implemented, Verified
OUTCOME: O-015 (CLI Output Design)
IMPLEMENTATIONS (2):
  F-jig.cli.output.format_success    src/jig/cli/output.py:45
  ...

───────────────────────────────────────────
DIG CONTEXT: Related Deliberations
───────────────────────────────────────────
D017 JIGPLAN: CLI Output Unification
  Status: implemented
  Produced: S-004, S-005, S-007
```

**Markdown mode (`-m`):**
```markdown
# JIG Context: S-004 Minimal Success Feedback

## Status
Implemented, Verified

## Outcome
O-015 (CLI Output Design)

## Implementations
- `F-jig.cli.output.format_success` in `src/jig/cli/output.py:45`

---

# DIG Context: Related Deliberations

## D017 JIGPLAN: CLI Output Unification
- **Status:** implemented
- **Produced:** S-004, S-005, S-007
```

**JSON mode (`-j`):**
```json
{
  "jig": {
    "id": "S-004",
    "title": "Minimal Success Feedback",
    "status": "implemented",
    "outcome": "O-015",
    "implementations": [...]
  },
  "dig": {
    "related": [
      {
        "id": "D017",
        "type": "jigplan",
        "title": "CLI Output Unification",
        "produces": ["S-004", "S-005", "S-007"]
      }
    ]
  }
}
```

### No Peer Context

When peer tool returns nothing (no related context found), simply omit that section:

```
JIG CONTEXT: S-004 Minimal Success Feedback
═══════════════════════════════════════════
STATUS: Implemented, Verified
...
```

No "DIG CONTEXT" section appears. No error, no "nothing found" message.

---

## Configuration

### Config Files

Both tools read their config from the project root:

```
project/
├── jig.toml          # JIG config
├── dig.toml          # DIG config
├── jig/
└── dig/
```

### Integration Settings

**jig.toml:**
```toml
[integration]
include_dig = true   # Call digy for cross-tool context
```

**dig.toml:**
```toml
[integration]
include_jig = true   # Call jigy for cross-tool context
```

### Behavior Matrix

| `include_dig` | `digy` installed | `dig/` exists | Behavior |
|---------------|------------------|---------------|----------|
| true | yes | yes | Call digy, include response |
| true | yes | no | Call digy, likely empty response |
| true | no | — | Skip (graceful degradation) |
| false | — | — | Skip (disabled by config) |

---

## Subprocess Interface

### Calling Convention

The calling tool invokes the peer tool with:

```bash
<peer-tool> context <id> -m
```

- Always request markdown mode (`-m`) for the peer response
- The peer tool returns its context as markdown on stdout
- Exit code 0 = success (even if no context found)
- Non-zero exit code = error (logged, but calling tool continues)

### Why Markdown?

Markdown is the common interchange format because:
- Human-readable if inspected
- Easy to concatenate
- LLM-friendly for context injection
- Avoids JSON parsing complexity for simple concatenation

For JSON mode output, the calling tool parses the peer's markdown and structures it appropriately (or calls with `-j` and parses JSON).

### Timeout and Error Handling

- Subprocess call should have a reasonable timeout (e.g., 5 seconds)
- If peer tool times out or errors, log warning and continue without peer context
- Never fail the primary command due to peer integration issues

---

## Implementation Considerations

### Graph Search Efficiency

When searching for references to an unknown identifier:

**Naive approach:** Parse every document's frontmatter on each query.

**Better approach:** Maintain a reverse index during graph build.

```
# dig/generated/produces_index.json
{
  "S-004": ["D017"],
  "S-005": ["D017"],
  "S-007": ["D017", "D022"]
}
```

This index is regenerated on `digy rebuild`. Queries become O(1) lookups.

### Caching

For frequently queried identifiers, consider caching peer responses briefly. However, since context can change, keep cache lifetime short or invalidate on rebuild.

### Circular Call Prevention

If JIG calls DIG and DIG's integration config says to call JIG back, we could get infinite recursion.

**Solution:** When a tool is called as a subprocess for integration, it should NOT call back to the peer. This can be signaled via:
- Environment variable: `JIG_PEER_CALL=1`
- Command flag: `--no-peer` (internal, not user-facing)

```bash
# JIG calls DIG
JIG_PEER_CALL=1 digy context S-004 -m

# DIG sees JIG_PEER_CALL=1, skips calling jigy back
```

---

## Measuring Success

### The Core Question

How do we know if the context system is working? Per [Anthropic's guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), evaluation should be task-dependent and iterative:

> "Start by maximizing recall to ensure your compaction prompt captures every relevant piece of information... Test minimal prompts with top-tier models first, then iteratively add guidance based on failure modes."

### Quantitative Metrics

#### Token Efficiency

| Metric | Target | Measurement |
|--------|--------|-------------|
| Default context size | 300-800 tokens | Count tokens in output |
| Verbose context size | 800-2000 tokens | Count tokens in output |
| Cross-tool overhead | < 200 tokens | Difference with/without peer |
| Token per artifact | 50-150 tokens | Total / artifact count |

**How to measure:** Run context commands and count tokens using a tokenizer (e.g., `tiktoken` for OpenAI, Claude's tokenizer for Anthropic models).

#### Latency

| Metric | Target | Measurement |
|--------|--------|-------------|
| Single-tool context | < 200ms | Time from invocation to output |
| Cross-tool context | < 500ms | Time including subprocess call |
| Graph search | < 50ms | Index lookup time |

**How to measure:** Instrument commands with timing, run benchmarks across project sizes.

#### Completeness

| Metric | Target | Measurement |
|--------|--------|-------------|
| Direct relationship coverage | 100% | All depth-1 relationships included |
| Cross-reference accuracy | 100% | All `produces`/`deliberation` refs resolved |
| No dangling references | 0 errors | Validation catches broken links |

### Qualitative Metrics

#### Agent Task Success

The ultimate test: can an agent complete tasks using this context?

**Test scenarios:**

1. **Spec understanding:** Given `jigy context S-004`, can the agent correctly describe what the spec does?

2. **Implementation location:** Given context, can the agent find and modify the right file?

3. **Relationship navigation:** Given a spec, can the agent identify related specs and their purpose?

4. **Cross-tool tracing:** Given a JIG spec, can the agent find the deliberation that produced it?

**Evaluation method:**
- Create a test suite of 20-30 agent tasks
- Run with and without JIG/DIG context
- Measure: task completion rate, accuracy, token usage, time to completion

#### Information Sufficiency

| Question | Desired Answer |
|----------|----------------|
| Does the agent ask for more info it should have? | Rarely |
| Does the agent hallucinate specs/functions? | Never |
| Does the agent make incorrect assumptions? | Rarely |
| Does one context call suffice for the task? | Usually |

**Evaluation method:**
- Review agent session logs
- Count follow-up queries for information present in context
- Count hallucinations (invented IDs, wrong file paths)

#### Human Usability

| Question | Desired Answer |
|----------|----------------|
| Can a developer orient quickly? | < 30 seconds |
| Is the output scannable? | Yes (clear hierarchy) |
| Is verbose mode actually more useful? | Yes (for complex tasks) |
| Does cross-tool context add value? | Yes (connects why to what) |

**Evaluation method:**
- User studies with developers
- Time-to-understanding measurements
- Preference surveys (default vs verbose)

### Benchmark Suite

#### Minimal Benchmark (Quick Validation)

```bash
# 1. Token count check
jigy context S-001 -m | wc -w  # Should be 200-600 words (~300-800 tokens)

# 2. Latency check
time jigy context S-001  # Should be < 200ms

# 3. Cross-tool check
time jigy context S-001  # With include_dig=true, should be < 500ms

# 4. Completeness check
jigy context S-001 -j | jq '.implementations | length'  # Should match known count
```

#### Full Benchmark (Periodic Evaluation)

1. **Coverage test:** For each spec, verify context includes all implementations and tests
2. **Cross-reference test:** For each `produces` entry, verify reverse lookup works
3. **Token budget test:** No single context exceeds 5000 tokens
4. **Latency distribution:** P50, P95, P99 latencies across all artifacts
5. **Agent task suite:** Run standardized agent tasks, measure success rate

### Failure Modes to Watch

| Failure Mode | Symptom | Mitigation |
|--------------|---------|------------|
| Context too sparse | Agent asks for info that should be included | Increase depth or fields |
| Context too verbose | Token budget exceeded, agent confused | Reduce depth, prune fields |
| Missing relationships | Agent can't find related specs | Check graph build, add indexes |
| Stale cross-references | Broken `produces`/`deliberation` links | Run validation, rebuild graphs |
| Peer timeout | Cross-tool context missing | Increase timeout, check peer health |
| Circular calls | Infinite recursion | Verify JIG_PEER_CALL flag works |

### Iterative Tuning Process

Based on [Anthropic's recommendation](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents):

1. **Start minimal:** Begin with core identity fields only
2. **Test with agents:** Run common tasks, observe failures
3. **Add based on failures:** When agents fail, identify missing context
4. **Measure token impact:** Each addition should justify its token cost
5. **Repeat:** Continue until task success plateaus

**Do NOT:**
- Add fields "just in case"
- Include full content when summaries suffice
- Exceed token budgets without evidence of benefit

---

## Success Criteria

### Functional

1. `jigy context S-004` returns JIG context + related DIG deliberations
2. `digy context D017` returns DIG context + related JIG specs
3. Unknown identifiers return relevant cross-references (if any exist)
4. Missing peer tool doesn't cause errors
5. Disabled integration (`include_dig=false`) is respected
6. Depth boundaries are respected (no unbounded traversal)
7. Verbose mode adds exactly one depth level and extended fields

### Performance

1. Single-tool context < 200ms latency
2. Cross-tool context < 500ms latency
3. Graph search uses index (O(1) lookup)
4. Subprocess timeout (5s) prevents hangs
5. Default output < 1000 tokens
6. Verbose output < 2500 tokens

### User Experience

1. No special flags needed for cross-tool context
2. Output clearly separates JIG and DIG sections
3. Empty peer context is silently omitted
4. Config is discoverable and documented
5. Output is scannable (clear visual hierarchy)
6. Token counts are predictable and bounded

### Agent Experience

1. Single context call provides sufficient orientation
2. Agents don't hallucinate specs/functions after reading context
3. Agents can locate files from context pointers
4. Agents can navigate relationships from context
5. Task completion rate improves vs. no context baseline

---

## Future Considerations

### Deeper Integration

The subprocess call pattern is simple but limited. Future versions might:
- Share a common graph database
- Use IPC instead of subprocess
- Provide real-time cross-tool validation

### Additional Cross-References

Beyond `produces` and `deliberation`, tools might link via:
- `related`: general cross-references
- `supersedes`: replacement chains
- `blocks` / `blocked_by`: dependency tracking

### Multi-Project Support

If JIG and DIG directories are in different locations, config could specify paths:

```toml
[integration]
include_dig = true
dig_path = "../other-project/dig"
```

---

## Summary

The context integration design prioritizes both simplicity and effectiveness:

### Architecture

1. **Each tool owns its logic** — no shared data formats
2. **Subprocess call interface** — loosely coupled
3. **Frontmatter is the link** — `produces` and `deliberation` fields
4. **Graceful degradation** — missing peer is not an error
5. **Transparent config** — users see and control integration

### Graph Traversal

1. **Bounded depth** — Default: 1 hop, Verbose: 2 hops, Max: 3 hops
2. **Relevance decay** — More detail for closer relationships
3. **Selective fields** — Each depth level has specific field inclusions
4. **Token awareness** — Budgets prevent context bloat

### Content Philosophy

> "Find the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."

1. **Orientation, not exhaustion** — Pointers to content, not content itself
2. **Identity first** — ID, title, status, type before details
3. **Relationships matter** — Show connections, not just entities
4. **Actionable output** — File:line references agents can use

### Measurement

1. **Token budgets** — 300-800 default, 800-2000 verbose, 5000 max
2. **Latency targets** — 200ms single-tool, 500ms cross-tool
3. **Agent success** — Can agents complete tasks with this context?
4. **Iterative tuning** — Add based on observed failures, not speculation

---

## References

- [Anthropic: Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic: Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [JetBrains: Efficient Context Management for LLM-Powered Agents](https://blog.jetbrains.com/research/2025/12/efficient-context-management/)
- [Firecrawl: Best Chunking Strategies for RAG 2025](https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025)
- [Qodo: Understanding Context Windows](https://www.qodo.ai/blog/context-windows/)

---

*This document is maintained alongside JIG_DIG_CLI_Recommendations.md. When context behavior changes, update both.*
