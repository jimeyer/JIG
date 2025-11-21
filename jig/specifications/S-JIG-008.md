---
id: S-JIG-008
type: Specification
title: CLI with User Consent Workflow
subsystem: jig-cli
implements:
  - O-JIG-006
  - O-JIG-008
created: 2025-11-21
status: active
---

# Specification: CLI with User Consent Workflow

## Purpose

Provide a command-line interface for orphaned node repair that respects user consent, provides cost transparency, and supports multiple execution modes.

## Requirements

### Command Interface

```bash
jigy ai-repair-orphaned-nodes [OPTIONS]
```

### Options

- `--graph PATH`: Path to graph-index.yaml (default: `jig/graph-index.yaml`)
- `--subsystems PATH`: Path to subsystems.yaml (default: `jig/subsystems.yaml`)
- `--output PATH`: Output report path (default: `docs/reports/orphaned-nodes-{YYYYMMDD}.md`)
- `--model TEXT`: Claude model (default: `claude-sonnet-4-5`, options: `claude-opus-4`)
- `--api-key TEXT`: Explicit API key (overrides credential resolution)
- `--dry-run`: Show findings and cost estimate, do not call API
- `--format TEXT`: Output format (default: `markdown`, options: `json`)
- `--skip-ai`: Run deterministic detection only, no AI analysis
- `--help`: Show help message

### Execution Flow

1. **Deterministic Detection**
   - Run `check_graph_integrity()` (S-JIG-005)
   - Display: "🔍 Analyzing graph integrity..."
   - If zero findings: "✓ No orphaned nodes detected. Graph integrity verified." (exit 0)

2. **Findings Summary**
   - Display counts:
     ```
     📊 Findings:
       - Dangling references: 3
       - Unreferenced nodes: 5
       - Malformed structures: 1
     ```

3. **Mode Branching**

   **If `--skip-ai`:**
   - Generate basic markdown/JSON report from deterministic findings
   - Skip steps 4-7
   - Exit 0

   **If `--dry-run`:**
   - Continue to step 4 (credential check)
   - Continue to step 5 (cost estimation)
   - Display: "(Dry run - not calling API)"
   - Exit 0

   **Otherwise (full mode):**
   - Continue to step 4

4. **Credential Resolution**
   - Initialize `ClaudeClient(api_key=api_key)`
   - If `CredentialError`:
     ```
     ❌ Credential error: No API key found for 'anthropic'

     💡 To set up credentials, run:
        jigy config set-credential anthropic
     ```
     Exit 1

5. **Cost Estimation**
   - Call `client.estimate_token_cost(findings)`
   - Display:
     ```
     💰 Estimated cost: $0.0375
        Input tokens: ~5000
        Output tokens: ~1500
     ```

6. **User Confirmation** (if not `--dry-run`)
   - If estimated cost >$0.10:
     - Prompt: "Proceed with API call? [y/N]"
     - If "N": Display "Cancelled." (exit 0)

7. **AI Analysis**
   - Display: "🤖 Analyzing with Claude..."
   - Call `client.analyze_orphaned_nodes(findings, graph_data, model)`
   - Handle errors gracefully (network, rate limit, token limit)

8. **Write Report**
   - Create output directory if needed
   - Write markdown report to output path
   - Display: "✓ Report written to: {output_path}"

9. **Usage Display**
   - Show actual usage:
     ```
     📈 Actual usage:
        Input tokens: 4823
        Output tokens: 1654
        Cost: $0.0393
     ```

### Exit Codes

- `0`: Success (no orphans found OR analysis complete)
- `1`: Error (credential error, file not found, API failure)
- `2`: User cancelled (declined cost confirmation)

## Output Formats

### Markdown (default)

```markdown
# Orphaned Nodes Report

**Generated**: 2025-11-21T10:30:00Z
**Total Nodes Analyzed**: 42

## Executive Summary
[AI-generated 2-3 sentence summary]

## Critical Issues

### Node: S-JIG-001
- **Type**: Specification
- **Issue**: References non-existent node O-JIG-999
- **Analysis**: [AI contextual analysis]
- **Recommended Action**: Create Outcome O-JIG-999 or update reference to O-JIG-003
- **Rationale**: [Why this fix]
- **Impact**: Affects 3 downstream Work Units

## Priority Actions
1. [Top priority fix]
2. [Second priority fix]
...
```

### JSON (`--format json`)

```json
{
  "timestamp": "2025-11-21T10:30:00Z",
  "findings": { /* raw deterministic findings */ },
  "ai_analysis": {
    "executive_summary": "...",
    "categorized_issues": [ /* ... */ ],
    "priority_actions": [ /* ... */ ]
  },
  "usage": {
    "input_tokens": 4823,
    "output_tokens": 1654,
    "cost_usd": 0.0393
  }
}
```

## Examples

```bash
# Standard usage
jigy ai-repair-orphaned-nodes

# Preview without API call
jigy ai-repair-orphaned-nodes --dry-run

# Deterministic only (free)
jigy ai-repair-orphaned-nodes --skip-ai --format json

# Use specific API key
jigy ai-repair-orphaned-nodes --api-key sk-ant-...

# Use Opus model
jigy ai-repair-orphaned-nodes --model claude-opus-4
```

## Rationale

**User consent:**
- Cost transparency before API calls respects user budgets
- Confirmation for >$0.10 prevents accidental expensive operations

**Multiple modes:**
- `--dry-run`: Safe exploration without charges
- `--skip-ai`: Fast, free deterministic checks for CI/CD
- Full mode: Complete analysis with AI suggestions

**Clear feedback:**
- Emoji markers (🔍 🤖 ✓) provide visual progress cues
- Token/cost display enables cost monitoring

## Dependencies

- Click for CLI framework
- ClaudeClient (S-JIG-006)
- Credential system (S-JIG-007)
- Detection module (S-JIG-005)

## Testing

- Integration tests with mocked API (all modes)
- Test credential error handling
- Test user cancellation (mock `click.confirm`)
- Test all exit codes

## References

- SCOPE: `docs/wip/S014_SCOPE_ai_repair_orphaned_nodes.md` (WU4, WU5)
