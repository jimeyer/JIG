# SCOPE: AI-Powered Orphaned Node Repair

**Status**: Draft
**Created**: 2025-11-21
**Related**: `docs/wip/S013_deterministic-orphan-detection-analysis.md`

## Objective

Implement `jigy ai-repair-orphaned-nodes` command that combines deterministic graph integrity detection with AI-powered contextual analysis and repair suggestions.

## Context

Per the analysis in S013, orphaned node detection is 80% deterministic (set operations, schema validation) and 20% judgment-based (categorization, repair strategy). This implementation creates a hybrid tool where:

1. **Deterministic layer**: Python performs fast, reliable detection
2. **AI layer**: Claude API provides contextual judgment and repair suggestions

This establishes a reusable pattern for future AI-augmented commands.

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│  jigy ai-repair-orphaned-nodes          │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 1. Deterministic Detection      │   │
│  │    - Load graph YAML            │   │
│  │    - Find dangling refs         │   │
│  │    - Find unreferenced nodes    │   │
│  │    - Detect malformed structs   │   │
│  │    → Output: findings.json      │   │
│  └─────────────────────────────────┘   │
│              ↓                          │
│  ┌─────────────────────────────────┐   │
│  │ 2. AI Analysis (Claude API)     │   │
│  │    - Read findings + node data  │   │
│  │    - Categorize issues          │   │
│  │    - Suggest repairs            │   │
│  │    - Prioritize actions         │   │
│  │    → Output: repair-report.md   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## Work Units

### WU1: Deterministic Detection Module
**File**: `jig/tools/graph_integrity.py` (or integrate into existing modules)

**Responsibilities**:
- Load `jig/graph-index.yaml` and `jig/subsystems.yaml`
- Build node registry and relationship index
- Detect three issue types:
  1. Dangling references (refs to non-existent nodes)
  2. Unreferenced nodes (isolated nodes)
  3. Malformed structures (null/invalid fields)
- Output structured JSON per schema in S013:299-348

**Interface**:
```python
def check_graph_integrity(
    graph_path: Path,
    subsystems_path: Path,
    include_node_context: bool = True
) -> Dict[str, Any]:
    """
    Returns:
    {
        "timestamp": "2025-11-21T...",
        "graph_file": "jig/graph-index.yaml",
        "total_nodes": 42,
        "findings": {
            "dangling_references": [...],
            "unreferenced_nodes": [...],
            "malformed_structures": [...]
        },
        "statistics": {...}
    }
    """
```

**Edge Cases**:
- Empty graph → Return zero findings with appropriate message
- Missing files → Raise clear error with path
- Circular references → Don't flag as orphans
- Self-references → Flag as unusual but separate category
- Mixed list/string relationship fields → Normalize to list

**Testing**:
- Unit tests for each detection function
- Fixtures with known orphan patterns
- Edge case validation

---

### WU2: Claude API Client Module
**File**: `jig/ai/claude_client.py`

**Responsibilities**:
- Manage Claude API authentication
- Construct prompts from structured findings
- Handle API calls with retry logic
- Parse responses
- Manage token usage/costs

**Interface**:
```python
class ClaudeClient:
    """Client for Claude API with credential management."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize client. API key resolution order:
        1. Explicit `api_key` parameter
        2. Environment variable: ANTHROPIC_API_KEY
        3. Config file: ~/.config/jig/credentials.yaml
        4. System keyring (if available)

        Raises CredentialError if no key found.
        """

    def analyze_orphaned_nodes(
        self,
        findings: Dict[str, Any],
        graph_data: List[Dict],
        model: str = "claude-sonnet-4-5"
    ) -> str:
        """
        Send findings to Claude for contextual analysis.

        Returns: Markdown report with categorization and repair suggestions
        """

    def estimate_token_cost(self, findings: Dict) -> Dict[str, int]:
        """
        Estimate token usage before making call.

        Returns: {"input_tokens": ~X, "output_tokens": ~Y, "est_cost_usd": Z}
        """
```

**Error Handling**:
- Network failures → Retry with exponential backoff (max 3 attempts)
- Rate limits → Wait and retry with 429 status
- Authentication errors → Clear message directing to credential setup
- Token limit exceeded → Suggest breaking into batches

**Token Management**:
- Default to smallest model that handles task (Sonnet)
- Allow model override via `--model` flag
- Log token usage to stderr
- Support `--dry-run` to show cost estimate without API call

---

### WU3: Credential Management System
**File**: `jig/config/credentials.py`

**Responsibilities**:
- Securely load API credentials
- Support multiple credential sources
- Provide clear setup instructions
- Never log or display credentials

**Credential Resolution Order**:

1. **Explicit parameter** (highest priority)
   ```bash
   jigy ai-repair-orphaned-nodes --api-key sk-ant-...
   ```

2. **Environment variable**
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   jigy ai-repair-orphaned-nodes
   ```

3. **Config file** (user home directory)
   ```yaml
   # ~/.config/jig/credentials.yaml
   anthropic:
     api_key: sk-ant-...
   ```
   - File must have 0600 permissions (user-only read/write)
   - Warning if permissions too broad
   - **CRITICAL**: Add `credentials.yaml` to `.gitignore`

4. **System keyring** (optional, if `keyring` library installed)
   ```python
   import keyring
   api_key = keyring.get_password("jig", "anthropic_api_key")
   ```

**Setup Command**:
```bash
# Interactive setup
jigy config set-credential anthropic

# Prompts:
# > Enter Anthropic API key: [hidden input]
# > Store in: [1] Config file, [2] Keyring: 1
# ✓ Credential saved to ~/.config/jig/credentials.yaml
# ⚠ WARNING: Keep this file secure. Do not commit to version control.
```

**Validation**:
```bash
jigy config validate-credentials
# Output:
# ✓ Anthropic API key found (source: config file)
# ✓ Successfully authenticated with Claude API
```

**Security Best Practices**:
- Never print full API key (show `sk-ant-...abc123` with middle redacted)
- Warn if config file permissions are too permissive
- Don't include credentials in error messages
- Don't send credentials to logs
- Provide clear documentation on security implications

**CI/CD Support**:
```bash
# For automated environments, use env var
export ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }}
jigy ai-repair-orphaned-nodes --no-interactive
```

---

### WU4: CLI Command Implementation
**File**: `jig/cli/commands/ai_repair_orphaned_nodes.py`

**Command Interface**:
```bash
jigy ai-repair-orphaned-nodes [OPTIONS]

Options:
  --graph PATH              Path to graph-index.yaml [default: jig/graph-index.yaml]
  --subsystems PATH         Path to subsystems.yaml [default: jig/subsystems.yaml]
  --output PATH             Output report path [default: docs/reports/orphaned-nodes-{date}.md]
  --model TEXT              Claude model to use [default: claude-sonnet-4-5]
                            Options: claude-sonnet-4-5, claude-opus-4
  --api-key TEXT            Anthropic API key (overrides other sources)
  --dry-run                 Show findings and cost estimate without calling AI
  --format TEXT             Output format [default: markdown]
                            Options: markdown, json
  --skip-ai                 Only run deterministic detection (no AI analysis)
  --help                    Show this message and exit

Examples:
  # Standard usage (reads credentials from config)
  jigy ai-repair-orphaned-nodes

  # Dry run to see findings and cost
  jigy ai-repair-orphaned-nodes --dry-run

  # Use specific API key
  jigy ai-repair-orphaned-nodes --api-key sk-ant-...

  # Only deterministic detection
  jigy ai-repair-orphaned-nodes --skip-ai --format json
```

**Execution Flow**:
```python
def ai_repair_orphaned_nodes(
    graph: Path,
    subsystems: Path,
    output: Path,
    model: str,
    api_key: Optional[str],
    dry_run: bool,
    format: str,
    skip_ai: bool
) -> None:
    # 1. Run deterministic detection
    print("🔍 Analyzing graph integrity...")
    findings = check_graph_integrity(graph, subsystems)

    if findings['findings']['dangling_references'] == [] and \
       findings['findings']['unreferenced_nodes'] == [] and \
       findings['findings']['malformed_structures'] == []:
        print("✓ No orphaned nodes detected. Graph integrity verified.")
        return

    # 2. Display findings summary
    print(f"\n📊 Findings:")
    print(f"  - Dangling references: {len(findings['findings']['dangling_references'])}")
    print(f"  - Unreferenced nodes: {len(findings['findings']['unreferenced_nodes'])}")
    print(f"  - Malformed structures: {len(findings['findings']['malformed_structures'])}")

    if skip_ai:
        # Output raw findings
        if format == "json":
            print(json.dumps(findings, indent=2))
        else:
            # Generate basic markdown report
            write_basic_report(findings, output)
        return

    # 3. Initialize Claude client
    try:
        client = ClaudeClient(api_key=api_key)
    except CredentialError as e:
        print(f"❌ Credential error: {e}")
        print("\n💡 To set up credentials, run:")
        print("   jigy config set-credential anthropic")
        sys.exit(1)

    # 4. Estimate cost
    cost = client.estimate_token_cost(findings)
    print(f"\n💰 Estimated cost: ${cost['est_cost_usd']:.4f}")
    print(f"   Input tokens: ~{cost['input_tokens']}")
    print(f"   Output tokens: ~{cost['output_tokens']}")

    if dry_run:
        print("\n(Dry run - not calling API)")
        return

    # 5. Confirm if cost is high
    if cost['est_cost_usd'] > 0.10:  # More than 10 cents
        if not click.confirm(f"\nProceed with API call?"):
            print("Cancelled.")
            return

    # 6. Call Claude API
    print("\n🤖 Analyzing with Claude...")
    graph_data = yaml.safe_load(open(graph))
    report = client.analyze_orphaned_nodes(findings, graph_data, model=model)

    # 7. Write report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report)
    print(f"\n✓ Report written to: {output}")

    # 8. Display usage
    actual_usage = client.last_usage  # Track actual tokens used
    print(f"\n📈 Actual usage:")
    print(f"   Input tokens: {actual_usage['input_tokens']}")
    print(f"   Output tokens: {actual_usage['output_tokens']}")
    print(f"   Cost: ${actual_usage['cost_usd']:.4f}")
```

---

### WU5: AI Prompt Engineering
**File**: `jig/ai/prompts/orphaned_nodes.py`

**Responsibilities**:
- Construct effective prompts for Claude
- Include relevant context from graph
- Request structured output
- Handle large graphs (context window limits)

**Prompt Template**:
```python
ORPHANED_NODES_PROMPT = """
You are analyzing a graph of Intent nodes from the OSTC (Outcome-Specification-Technical-Component) framework.

# Graph Context
Total nodes: {total_nodes}
Node types: {node_types}

# Detected Issues (Deterministic Analysis)

## Dangling References ({dangling_count})
{dangling_details}

## Unreferenced Nodes ({unreferenced_count})
{unreferenced_details}

## Malformed Structures ({malformed_count})
{malformed_details}

# Your Task
For each issue:
1. **Categorize** the severity (Critical, Warning, Info)
2. **Determine root cause** (deprecated?, intentional isolation?, data entry error?)
3. **Suggest specific repair action** (create node X, link to Y, remove Z)
4. **Estimate impact** (affects how many downstream nodes?)

# Output Format
Provide a markdown report with:
- Executive summary (2-3 sentences)
- Issues by category (Critical first, then Warning, then Info)
- For each issue:
  - Node ID and type
  - Problem description
  - Contextual analysis (why is this an issue?)
  - Recommended action (specific, actionable)
  - Rationale (why this fix?)
- Prioritized action list (top 5 fixes to do first)

# Important Context Rules
- Outcome nodes (O-*) at the top level may intentionally have no incoming refs
- Technical Components (T-*) without outgoing refs might be leaf implementations
- Deprecated nodes should be linked to historical documentation, not deleted
- If a node description mentions "legacy" or "deprecated", preserve but isolate

Be specific. Instead of "fix the reference", say "Update S-JIG-001.specifies to reference O-JIG-003 instead of missing O-JIG-999".
"""
```

**Context Window Management**:
- If findings > 100 items, batch into multiple API calls
- Prioritize critical issues first
- Provide node context only for nodes involved in issues (not entire graph)

---

### WU6: Documentation
**Files**:
- `README.md` (update with new command)
- `docs/CLI-REFERENCE.md` (new section)
- `docs/AI-INTEGRATION.md` (new guide)
- `.gitignore` (add credential paths)

**Content**:

#### README.md Addition
```markdown
### AI-Powered Commands

Jig includes experimental AI-powered analysis commands using Claude:

- `jigy ai-repair-orphaned-nodes`: Detect and suggest repairs for orphaned graph nodes

These commands require an Anthropic API key. See [AI Integration Guide](docs/AI-INTEGRATION.md).
```

#### AI-INTEGRATION.md (new file)
```markdown
# AI Integration Guide

## Overview
Jig provides hybrid AI/deterministic commands that combine fast, reliable
local analysis with AI-powered contextual reasoning.

## Setup
1. Get an API key from https://console.anthropic.com/
2. Set up credentials:
   ```bash
   jigy config set-credential anthropic
   ```
3. Verify:
   ```bash
   jigy config validate-credentials
   ```

## Security
- API keys are never logged or displayed in full
- Store keys in `~/.config/jig/credentials.yaml` (user-only permissions)
- Never commit `credentials.yaml` to version control
- For CI/CD, use environment variable `ANTHROPIC_API_KEY`

## Cost Management
- Commands show cost estimates before calling API
- Typical cost: $0.01-0.05 per analysis
- Use `--dry-run` to see estimates without charges
- Use `--skip-ai` to run only deterministic checks (free)

## Available Commands
- `jigy ai-repair-orphaned-nodes`: Graph integrity analysis
```

#### .gitignore Addition
```gitignore
# API credentials (NEVER commit these)
credentials.yaml
.credentials.yaml
**/credentials.yaml
.anthropic_api_key
```

---

## Implementation Phases

### Phase 1: Core Infrastructure (WU1, WU3)
- Implement deterministic detection
- Implement credential management
- Test with fixtures
- Can be used standalone without AI

**Deliverable**: `jigy graph check-integrity --format json`

### Phase 2: AI Integration (WU2, WU5)
- Implement Claude API client
- Develop prompt template
- Test with real API (small graphs)
- Add cost estimation

**Deliverable**: Working AI analysis in isolation

### Phase 3: Command Integration (WU4)
- Implement full CLI command
- Wire deterministic + AI layers
- Add interactive confirmations
- Error handling polish

**Deliverable**: `jigy ai-repair-orphaned-nodes` fully functional

### Phase 4: Documentation & Polish (WU6)
- Write user guides
- Add examples
- Update main docs
- Security audit

**Deliverable**: Production-ready command

---

## API Key Management: Best Practices Summary

### ✓ Do
- Use environment variables for CI/CD
- Store in config file with 0600 permissions
- Provide multiple credential sources
- Show cost estimates before API calls
- Redact keys in logs/output (show `sk-ant-...xyz`)
- Document security implications clearly
- Support `--dry-run` for cost estimation

### ✗ Don't
- Hardcode API keys
- Commit keys to version control
- Log full API keys
- Display keys in error messages
- Auto-retry expensive operations without confirmation
- Assume credentials exist (fail gracefully)

### Security Checklist
- [ ] `credentials.yaml` in `.gitignore`
- [ ] Config file permissions checked (warn if > 0600)
- [ ] API keys never in logs
- [ ] Clear error messages for missing credentials
- [ ] Documentation warns about security
- [ ] No keys in exception stack traces
- [ ] Support for secret managers (keyring)

---

## Testing Strategy

### Unit Tests
- `test_graph_integrity.py`: All detection functions
- `test_credential_loading.py`: All credential sources
- `test_claude_client.py`: API client (mocked responses)

### Integration Tests
- `test_ai_repair_command.py`: Full command flow with mocked API
- Test credential resolution priority
- Test error handling paths

### Manual Testing
- Run on actual jig graph
- Test with missing credentials (verify error messages)
- Test with invalid API key (verify auth error handling)
- Test dry-run mode
- Test skip-ai mode
- Verify cost estimates are reasonable

### Security Testing
- Verify no keys in logs
- Test file permission warnings
- Attempt to trigger key disclosure in errors
- Verify .gitignore patterns

---

## Future Enhancements

1. **Batch Processing**: Support multiple graphs in one command
2. **Interactive Repair**: `--interactive` flag to apply suggested fixes with confirmation
3. **History Tracking**: Log API usage over time
4. **Cost Budgets**: `--max-cost 0.10` to cap spending
5. **Offline Mode**: Cache Claude responses for repeated analysis
6. **Multi-Model Support**: Compare suggestions from different models
7. **Custom Prompts**: Allow user-provided prompt templates

---

## Success Criteria

- [ ] Command successfully detects all three orphan types
- [ ] Credential resolution works in all four modes
- [ ] API client handles errors gracefully
- [ ] Cost estimates within 20% of actual usage
- [ ] Report output is actionable and well-formatted
- [ ] Security audit passes (no credential leaks)
- [ ] Documentation is clear and complete
- [ ] Zero API calls made without explicit user consent
- [ ] Works in CI/CD with environment variables

---

## Open Questions

1. **Model Selection**: Default to Sonnet or allow Haiku for simpler cases?
   - **Recommendation**: Sonnet default, allow override via `--model`

2. **Cost Threshold**: When to require confirmation?
   - **Recommendation**: Confirm if > $0.10 (10 cents)

3. **Batch Size**: How many findings per API call?
   - **Recommendation**: 100 findings max, batch if more

4. **Caching**: Should we cache API responses?
   - **Recommendation**: Not in MVP, add later if needed

5. **Credential Storage**: Require keyring library or make optional?
   - **Recommendation**: Optional. Config file is sufficient.

---

## Related Documents
- `docs/wip/S013_deterministic-orphan-detection-analysis.md` - Analysis and rationale
- `agents/taskRepairOrphanedNodes.md` - Original agent task
- `agents/AI-Agent-Task-Crafting-Guide.md` - Task design principles

---

**Next Steps**:
1. Review this SCOPE for completeness
2. Decide on credential management approach (confirm keyring optional?)
3. Begin Phase 1 implementation (deterministic detection)
