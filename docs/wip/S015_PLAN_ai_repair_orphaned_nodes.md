---
delta_type: plan
branch: feat/ai-repair-orphaned-nodes
status: Draft
---

# PLAN: AI-Powered Orphaned Node Repair

- **SCOPE:** `docs/wip/S014_SCOPE_ai_repair_orphaned_nodes.md`
- **Start:** 2025-11-21
- **Owner:** Jim Meyer
- **Status:** Draft
- **Subsystem:** jig-graph

## Known Intent (Created Before Coding)

### Outcomes Created (Why we build this)

- **O-JIG-006**: "Developers identify and repair orphaned nodes efficiently" (`jig/outcomes/O-JIG-006.md`)
  - Value: Maintains graph integrity without manual YAML inspection
  - Acceptance: Can find and fix orphaned nodes in <5 minutes vs 30+ minutes manual

- **O-JIG-007**: "Graph integrity issues detected before they cause problems" (`jig/outcomes/O-JIG-007.md`)
  - Value: Prevents downstream failures from broken references
  - Acceptance: Zero production incidents from orphaned nodes

- **O-JIG-008**: "AI analysis provides actionable repair context" (`jig/outcomes/O-JIG-008.md`)
  - Value: Human understands *why* a node is orphaned and *how* to fix it
  - Acceptance: 90%+ of suggestions are directly applicable

- **O-JIG-009**: "API credentials stored securely per industry standards" (`jig/outcomes/O-JIG-009.md`)
  - Value: No credential leaks, audit-compliant, CI/CD friendly
  - Acceptance: Zero credential exposure in logs, git, or error messages

### Specifications Created (What we build)

- **S-JIG-012**: "Deterministic orphan detection" (`jig/specifications/S-JIG-012.md`)
  - Detects: Dangling references, unreferenced nodes, malformed structures
  - Performance: <100ms for graphs up to 1000 nodes
  - Output: Structured JSON with node context
  - Note: S-JIG-005/006 were already assigned to other features

- **S-JIG-013**: "Claude API client with cost management" (`jig/specifications/S-JIG-013.md`)
  - Features: Retry logic (3 attempts, exponential backoff), token estimation
  - Accuracy: Cost estimates within 20% of actual usage
  - Models: Support Sonnet (default) and Opus

- **S-JIG-007**: "Multi-source credential resolution" (`jig/specifications/S-JIG-007.md`)
  - Sources (priority order): CLI flag > env var > config file > keyring
  - Validation: Check permissions, test authentication
  - Error handling: Clear setup instructions on missing credentials

- **S-JIG-008**: "CLI with user consent workflow" (`jig/specifications/S-JIG-008.md`)
  - Modes: Full (AI), dry-run (estimate only), skip-ai (deterministic only)
  - Confirmation: Required if estimated cost >$0.10
  - Output: Markdown report with severity levels and action priorities

- **S-JIG-009**: "Secure credential storage" (`jig/specifications/S-JIG-009.md`)
  - Config file: 0600 permissions (user-only read/write)
  - Warnings: Alert if permissions too broad
  - Validation: `jigy config validate-credentials` command

- **S-JIG-010**: "Zero credential exposure" (`jig/specifications/S-JIG-010.md`)
  - Logging: Never log full API keys (show `sk-ant-...xyz` only)
  - Errors: No credentials in exception messages or stack traces
  - Display: Redact middle of keys in all output

- **S-JIG-011**: "Accurate cost estimation" (`jig/specifications/S-JIG-011.md`)
  - Estimation: Token counts within 20% of actual
  - Tracking: Log actual usage after API calls
  - Reporting: Display input/output tokens and USD cost

### Rationale

These constraints were known from SCOPE S014. The analysis in S013 identified the deterministic/AI split and security requirements. Creating Intent upfront enables O→S→TDD flow and establishes clear acceptance criteria.

---

## Work Unit Checklist

- [x] WU0: Create known Intent nodes (O/S) — done ✅
- [ ] WU1: Deterministic detection module — tests ☐ / docs ☐ / reflect ☐
- [ ] WU2: Credential management system — tests ☐ / docs ☐ / reflect ☐
- [ ] WU3: Claude API client — tests ☐ / docs ☐ / reflect ☐
- [ ] WU4: AI prompt engineering — tests ☐ / docs ☐ / reflect ☐
- [ ] WU5: CLI command integration — tests ☐ / docs ☐ / reflect ☐
- [ ] WU6: Documentation & security audit — tests ☐ / docs ☐ / reflect ☐

---

## Work Units

### Work Unit 0: Create Known Intent

**Goal:** Capture all known Outcomes and Specifications from SCOPE as Intent nodes before coding.

**Acceptance Criteria:**
- [x] 4 Outcome nodes created in `jig/outcomes/` (O-JIG-006 through O-JIG-009)
- [x] 7 Specification nodes created in `jig/specifications/` (S-JIG-007 through S-JIG-013, skipping 005/006 which were already assigned)
- [x] All nodes have proper YAML frontmatter and markdown content
- [x] Each Specification links to implementing Outcomes via `implements:` field
- [x] `jig validate` passes
- [x] Committed to git with Intent commit message

**Created Nodes:**

**Outcomes:**
- `jig/outcomes/O-JIG-006.md` - Efficient orphaned node identification
- `jig/outcomes/O-JIG-007.md` - Proactive graph integrity detection
- `jig/outcomes/O-JIG-008.md` - Actionable AI-powered repair suggestions
- `jig/outcomes/O-JIG-009.md` - Secure credential management

**Specifications:**
- `jig/specifications/S-JIG-012.md` - Deterministic detection (implements O-JIG-006, O-JIG-007)
- `jig/specifications/S-JIG-013.md` - Claude API client (implements O-JIG-008)
- `jig/specifications/S-JIG-007.md` - Multi-source credentials (implements O-JIG-009)
- `jig/specifications/S-JIG-008.md` - CLI with consent (implements O-JIG-006, O-JIG-008)
- `jig/specifications/S-JIG-009.md` - Secure storage (implements O-JIG-009)
- `jig/specifications/S-JIG-010.md` - Zero exposure (implements O-JIG-009)
- `jig/specifications/S-JIG-011.md` - Cost estimation (implements O-JIG-008)

**Reflect:**
- What was clear from SCOPE:
  - Clean separation between deterministic detection (80%) and AI judgment (20%)
  - Security requirements well-defined (S013 analysis was thorough)
  - Phased implementation approach makes incremental delivery possible
- What was ambiguous:
  - Exact format of JSON output schema (will discover during WU1 implementation)
  - Prompt template effectiveness (will iterate in WU4 based on actual results)
  - Optimal batch size for large graphs (need to test with real data)
  - Whether keyring integration adds enough value vs complexity

---

### Work Unit 1: Deterministic Detection Module

**Goal:** Implement fast, reliable graph integrity detection that finds all three orphan types and outputs structured JSON.

**Planned Effort:** 90 minutes

**Implements:** S-JIG-012

**Acceptance Criteria:**
- [ ] Function `check_graph_integrity(graph_path, subsystems_path)` exists (S-JIG-012)
- [ ] Detects dangling references (references to non-existent node IDs)
- [ ] Detects unreferenced nodes (isolated nodes with no incoming refs)
- [ ] Detects malformed structures (null/invalid relationship fields)
- [ ] Handles edge cases: empty graph, circular refs, self-refs, mixed list/string fields
- [ ] Returns structured JSON per schema (see SCOPE S014:299-348)
- [ ] Performance: <100ms for 100-node graph (measured with pytest-benchmark)
- [ ] All tests pass with 100% coverage of detection logic

**Implementation Notes:**
- Module: `jig/tools/graph_integrity.py` or integrate into `jig/core/graph.py`
- Algorithm approach:
  1. Load YAML with error handling (file not found, parse errors)
  2. Build node registry: `{node_id: node_data}`
  3. Build reference index: `{referenced_id: [referrer_ids]}`
  4. Find dangling: set membership check for each reference
  5. Find unreferenced: set difference (all_ids - referenced_ids)
  6. Find malformed: null checks, type validation on relationship fields
- Relationship fields to scan: `['implements', 'specifies', 'contributes_to', 'depends_on']`
- Output includes node context (description, type) for AI consumption

**Test Plan:**

Unit tests in `tests/tools/test_graph_integrity.py`:
- [x] `test_load_empty_graph()` - Returns zero findings
- [x] `test_dangling_reference_single()` - Detects one missing ref
- [x] `test_dangling_reference_list()` - Handles list of refs
- [x] `test_unreferenced_node()` - Finds isolated node
- [x] `test_circular_references_ok()` - A→B→A not flagged as orphan
- [x] `test_self_reference_flagged()` - Node references itself (unusual but valid)
- [x] `test_malformed_null_field()` - Null in relationship field
- [x] `test_malformed_invalid_type()` - Integer instead of string ID
- [x] `test_mixed_string_list_normalized()` - Both formats handled
- [x] `test_missing_file_raises()` - Clear error on missing graph
- [x] `test_performance_100_nodes()` - Benchmark <100ms

Fixture: `tests/fixtures/graph_orphans.yaml` with known orphan patterns

**Docs to Update:**
- Docstrings with type hints for `check_graph_integrity()`
- Add example usage in module docstring

**Reflect (≤5 bullets; keep crisp):**

*[To be filled after implementation]*

**Links:**
- MR/PR: [TBD]
- Commit(s): [TBD]

**Human Validation:**
- Commands:
  ```bash
  pytest tests/tools/test_graph_integrity.py -v --cov
  python -m jig.tools.graph_integrity  # Should print JSON to stdout
  jig validate
  ```
- Look for: All tests pass, coverage >95%, JSON output well-formed

---

### Work Unit 2: Credential Management System

**Goal:** Implement secure, multi-source credential resolution with validation and setup commands.

**Planned Effort:** 90 minutes

**Implements:** S-JIG-007, S-JIG-009, S-JIG-010

**Acceptance Criteria:**
- [ ] Function `load_credential(service: str)` with 4-source resolution (flag > env > config > keyring)
- [ ] Config file at `~/.config/jig/credentials.yaml` with 0600 permissions enforced
- [ ] Warning displayed if config file permissions too broad (not 0600)
- [ ] API keys never logged in full (redaction function `redact_key()`)
- [ ] CLI command: `jigy config set-credential anthropic` (interactive)
- [ ] CLI command: `jigy config validate-credentials` (test auth)
- [ ] Setup creates config directory if missing
- [ ] All tests pass with mocked file I/O

**Implementation Notes:**
- Module: `jig/config/credentials.py`
- Resolution function:
  ```python
  def load_credential(service: str, explicit_key: Optional[str] = None) -> str:
      # 1. Explicit parameter
      if explicit_key:
          return explicit_key
      # 2. Environment variable
      env_var = f"{service.upper()}_API_KEY"
      if env_var in os.environ:
          return os.environ[env_var]
      # 3. Config file
      config_path = Path.home() / ".config" / "jig" / "credentials.yaml"
      if config_path.exists():
          check_permissions(config_path)  # Warn if not 0600
          creds = yaml.safe_load(config_path.read_text())
          if service in creds:
              return creds[service]['api_key']
      # 4. Keyring (optional)
      try:
          import keyring
          key = keyring.get_password("jig", f"{service}_api_key")
          if key:
              return key
      except ImportError:
          pass  # Keyring not installed, skip
      # None found
      raise CredentialError(f"No credential found for {service}. Run: jigy config set-credential {service}")
  ```
- Permission check: `stat.S_IMODE(path.stat().st_mode) == 0o600`
- Redaction: Show first 7 chars + "..." + last 4 chars

**Test Plan:**

Unit tests in `tests/config/test_credentials.py`:
- [x] `test_explicit_key_highest_priority()` - Ignores other sources
- [x] `test_env_var_second_priority()` - Falls back to env
- [x] `test_config_file_third_priority()` - Reads from YAML
- [x] `test_keyring_fourth_priority()` - Tries keyring if available
- [x] `test_no_credential_raises()` - Clear error message
- [x] `test_permission_warning()` - Warns on 0644 file
- [x] `test_redact_key()` - Shows `sk-ant-...abc123` format
- [x] `test_set_credential_creates_config()` - Interactive setup
- [x] `test_validate_credentials()` - Test API call (mocked)

Integration test in `tests/cli/test_config_commands.py`:
- [x] `test_set_credential_interactive()` - Full flow with Click testing

**Docs to Update:**
- `jig/config/README.md` - Credential setup guide
- `.gitignore` - Add `credentials.yaml`, `.credentials.yaml`, `**/credentials.yaml`

**Reflect (≤5 bullets; keep crisp):**

*[To be filled after implementation]*

**Links:**
- MR/PR: [TBD]
- Commit(s): [TBD]

**Human Validation:**
- Commands:
  ```bash
  pytest tests/config/test_credentials.py -v
  jigy config set-credential anthropic  # Interactive test (use test key)
  jigy config validate-credentials
  jig validate
  ```
- Look for:
  - Config file created at `~/.config/jig/credentials.yaml` with 0600 perms
  - Warning if you manually `chmod 644` the file
  - API key never printed in full

---

### Work Unit 3: Claude API Client

**Goal:** Implement Claude API client with retry logic, cost estimation, and usage tracking.

**Planned Effort:** 90 minutes

**Implements:** S-JIG-013, S-JIG-011

**Acceptance Criteria:**
- [ ] Class `ClaudeClient` with `__init__(api_key: Optional[str])` using credential resolution (S-JIG-013)
- [ ] Method `analyze_orphaned_nodes(findings, graph_data, model)` returns markdown report
- [ ] Method `estimate_token_cost(findings)` returns `{input_tokens, output_tokens, est_cost_usd}` (S-JIG-011)
- [ ] Retry logic: 3 attempts with exponential backoff on network errors
- [ ] Rate limit handling: Wait and retry on 429 status
- [ ] Token tracking: Store `last_usage` with actual token counts and cost
- [ ] Cost estimation accuracy: Within 20% of actual (tested with real API call)
- [ ] All tests pass with mocked Anthropic SDK

**Implementation Notes:**
- Module: `jig/ai/claude_client.py`
- Dependency: `anthropic` library (add to `pyproject.toml`)
- Estimation heuristic:
  - Input tokens ≈ JSON length / 4 + graph context
  - Output tokens ≈ 1500 (typical report length)
  - Costs (as of 2025-11): Sonnet input $3/MTok, output $15/MTok
- Retry decorator:
  ```python
  @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
  def _make_api_call(...):
  ```
- Rate limit: Check response status, sleep if 429

**Test Plan:**

Unit tests in `tests/ai/test_claude_client.py`:
- [x] `test_init_with_explicit_key()` - Uses provided key
- [x] `test_init_without_key_loads_credential()` - Falls back to credential system
- [x] `test_estimate_token_cost()` - Returns dict with expected keys
- [x] `test_analyze_orphaned_nodes_success()` - Mocked API call returns markdown
- [x] `test_retry_on_network_error()` - Retries 3 times, then fails
- [x] `test_rate_limit_handling()` - Sleeps on 429, retries
- [x] `test_last_usage_tracked()` - Stores actual token counts
- [x] `test_model_parameter()` - Supports sonnet and opus

Integration test (requires real API key, marked `@pytest.mark.integration`):
- [x] `test_real_api_call()` - Call with small findings, verify cost within 20%

**Docs to Update:**
- Docstrings for all public methods
- `jig/ai/README.md` - Usage examples

**Reflect (≤5 bullets; keep crisp):**

*[To be filled after implementation]*

**Links:**
- MR/PR: [TBD]
- Commit(s): [TBD]

**Human Validation:**
- Commands:
  ```bash
  pytest tests/ai/test_claude_client.py -v -m "not integration"
  pytest tests/ai/test_claude_client.py -v -m integration  # Requires API key
  ```
- Look for:
  - Mocked tests pass without API key
  - Integration test confirms cost estimation accuracy
  - Retry logic logs retry attempts

---

### Work Unit 4: AI Prompt Engineering

**Goal:** Design and implement effective prompt template for orphaned node analysis with structured output.

**Planned Effort:** 60 minutes

**Implements:** S-JIG-008 (output quality)

**Acceptance Criteria:**
- [ ] Prompt template in `jig/ai/prompts/orphaned_nodes.py`
- [ ] Includes OSTC context rules (O-* nodes may be root-level, deprecated nodes preserved)
- [ ] Requests specific output format: severity, root cause, repair action, impact
- [ ] Requests executive summary and prioritized action list (top 5)
- [ ] Handles context window limits (batching strategy if >100 findings)
- [ ] Template variables: `{total_nodes}`, `{dangling_details}`, etc.
- [ ] Manual validation: Generate report for jig's actual graph, verify actionability

**Implementation Notes:**
- Module: `jig/ai/prompts/orphaned_nodes.py`
- Template structure (see SCOPE S014:360-407):
  ```python
  ORPHANED_NODES_PROMPT = """
  You are analyzing a graph of Intent nodes from the OSTC framework.

  # Graph Context
  Total nodes: {total_nodes}
  Node types: {node_types}

  # Detected Issues (Deterministic Analysis)
  [Formatted findings JSON]

  # Your Task
  For each issue:
  1. Categorize severity (Critical, Warning, Info)
  2. Determine root cause (deprecated? intentional? data error?)
  3. Suggest specific repair action (create node X, link to Y, remove Z)
  4. Estimate impact (affects N downstream nodes?)

  # Output Format
  [Markdown structure with executive summary, issues by category, action list]

  # Context Rules
  - Outcome nodes (O-*) may intentionally have no incoming refs
  - Technical Components (T-*) without outgoing refs might be leaf implementations
  - Deprecated nodes should be linked to docs, not deleted
  - Be specific: "Update S-JIG-001.specifies to O-JIG-003" not "fix the reference"
  """
  ```
- Context window management:
  - Max findings per call: 100
  - If more, batch by severity (Critical first)

**Test Plan:**

Unit tests in `tests/ai/test_prompts.py`:
- [x] `test_prompt_template_variables()` - All variables resolved
- [x] `test_prompt_includes_ostc_context()` - Rules present
- [x] `test_batch_findings()` - Splits >100 findings

Manual validation:
- [ ] Generate report for `jig/graph-index.yaml` (current graph)
- [ ] Review output for:
  - Clear severity labels
  - Specific repair actions (not vague)
  - Rationale provided
  - Actionable prioritization

**Docs to Update:**
- Prompt template docstring with example output

**Reflect (≤5 bullets; keep crisp):**

*[To be filled after implementation]*

**Links:**
- MR/PR: [TBD]
- Commit(s): [TBD]

**Human Validation:**
- Commands:
  ```bash
  pytest tests/ai/test_prompts.py -v
  # Manual test: Run full command on real graph
  jigy ai-repair-orphaned-nodes --dry-run
  ```
- Look for: Prompt is clear, structured, includes all necessary context

---

### Work Unit 5: CLI Command Integration

**Goal:** Wire together all components into working `jigy ai-repair-orphaned-nodes` command with full workflow.

**Planned Effort:** 90 minutes

**Implements:** S-JIG-008, O-JIG-006

**Acceptance Criteria:**
- [ ] Command registered: `jigy ai-repair-orphaned-nodes`
- [ ] All CLI flags work: `--graph`, `--subsystems`, `--output`, `--model`, `--api-key`, `--dry-run`, `--format`, `--skip-ai`
- [ ] Workflow steps execute in order (see SCOPE S014:269-347):
  1. Run deterministic detection
  2. Display findings summary
  3. Initialize Claude client (handle credential errors gracefully)
  4. Estimate cost, display to user
  5. Confirm if cost >$0.10 (skip in `--dry-run`)
  6. Call Claude API
  7. Write report to output path
  8. Display actual usage
- [ ] Error handling: Missing credentials → helpful message + setup instructions
- [ ] Exit codes: 0 (success/no orphans), 1 (errors), 2 (user cancelled)
- [ ] `--skip-ai` mode outputs basic markdown report without API call
- [ ] All integration tests pass

**Implementation Notes:**
- Module: `jig/cli/commands/ai_repair_orphaned_nodes.py`
- Click command decorator:
  ```python
  @click.command("ai-repair-orphaned-nodes")
  @click.option("--graph", type=click.Path(exists=True), ...)
  @click.option("--dry-run", is_flag=True, ...)
  def ai_repair_orphaned_nodes(graph, subsystems, output, model, api_key, dry_run, format, skip_ai):
  ```
- Progress indicators: Use `click.echo()` with emoji for user feedback
- Confirmation: `click.confirm("Proceed with API call?")`
- Default output path: `docs/reports/orphaned-nodes-{date}.md` where date is YYYYMMDD

**Test Plan:**

Integration tests in `tests/cli/test_ai_repair_command.py`:
- [x] `test_no_orphans_found()` - Clean graph exits successfully
- [x] `test_dry_run_mode()` - Shows estimate, no API call
- [x] `test_skip_ai_mode()` - Outputs basic report only
- [x] `test_full_workflow()` - End-to-end with mocked Claude API
- [x] `test_missing_credentials()` - Error message + setup instructions
- [x] `test_user_cancels_confirmation()` - Exits cleanly
- [x] `test_cost_threshold_confirmation()` - Prompts if >$0.10
- [x] `test_actual_usage_displayed()` - Shows token counts after API call

**Docs to Update:**
- CLI help text (built into command decorators)
- Add examples to command docstring

**Reflect (≤5 bullets; keep crisp):**

*[To be filled after implementation]*

**Links:**
- MR/PR: [TBD]
- Commit(s): [TBD]

**Human Validation:**
- Commands:
  ```bash
  pytest tests/cli/test_ai_repair_command.py -v

  # Manual end-to-end tests:
  jigy ai-repair-orphaned-nodes --help
  jigy ai-repair-orphaned-nodes --dry-run
  jigy ai-repair-orphaned-nodes --skip-ai --format json
  jigy ai-repair-orphaned-nodes  # Full run with real API

  jig validate
  ```
- Look for:
  - Help text is clear
  - Dry run shows cost estimate
  - Skip-ai produces basic report
  - Full run produces actionable markdown report
  - Exit codes correct

---

### Work Unit 6: Documentation & Security Audit

**Goal:** Complete user documentation, security review, and verify all success criteria met.

**Planned Effort:** 60 minutes

**Implements:** O-JIG-009 (security docs), S-JIG-010 (audit)

**Acceptance Criteria:**
- [ ] `README.md` updated with AI-powered commands section
- [ ] `docs/AI-INTEGRATION.md` created (see SCOPE S014:436-469)
- [ ] `.gitignore` updated with credential paths
- [ ] Security checklist complete (SCOPE S014:537-544):
  - [x] `credentials.yaml` in `.gitignore`
  - [x] Config file permissions checked (warn if >0600)
  - [x] API keys never in logs
  - [x] Clear error messages for missing credentials
  - [x] Documentation warns about security
  - [x] No keys in exception stack traces
  - [x] Support for secret managers (keyring)
- [ ] All success criteria from SCOPE met (S014:588-598)
- [ ] Manual security test: Attempt to trigger key disclosure (none found)

**Implementation Notes:**
- Review all modules for potential credential leaks
- Check logger statements: `grep -r "api_key" jig/` → verify redaction
- Test error paths: Try to crash with bad inputs, check stack traces
- Verify .gitignore patterns catch all credential files

**Test Plan:**

Security tests in `tests/security/test_credential_security.py`:
- [x] `test_no_keys_in_logs()` - Enable logging, verify redaction
- [x] `test_no_keys_in_exceptions()` - Trigger errors, check messages
- [x] `test_gitignore_patterns()` - Verify credential files excluded
- [x] `test_permission_warnings()` - chmod 644, verify warning displayed

Manual audit:
- [ ] Review all error messages for credential leaks
- [ ] Test with invalid API key, verify no key in output
- [ ] Test with broad config permissions, verify warning
- [ ] Grep codebase for hardcoded keys or debug statements

**Docs to Update:**
- `README.md` - Add "AI-Powered Commands" section
- `docs/AI-INTEGRATION.md` - Complete setup and security guide
- `.gitignore` - Add credential file patterns
- `CONTRIBUTING.md` - Add note about AI command development pattern

**Reflect (≤5 bullets; keep crisp):**

*[To be filled after implementation]*

**Links:**
- MR/PR: [TBD]
- Commit(s): [TBD]

**Human Validation:**
- Commands:
  ```bash
  pytest tests/security/test_credential_security.py -v

  # Manual checks:
  grep -r "api_key" jig/ | grep -v "test_" | grep -v ".pyc"
  git status  # Verify credentials.yaml not tracked

  # Test credential error path:
  unset ANTHROPIC_API_KEY
  jigy ai-repair-orphaned-nodes  # Should show helpful setup message

  jig validate
  ```
- Look for:
  - No API keys in code or logs
  - `.gitignore` catches all credential files
  - Error messages are helpful, not revealing
  - Documentation is clear and complete

---

## Completion Summary

*[To be filled after all work units complete]*

### Summary
- Scope delivered: …
- Key decisions: …
- Deltas from SCOPE: …

### Metrics
- Units: 6 (plus WU0); median cycle time: <TBD>
- Rework rate (units reopened): <TBD>
- Flaky test events: <TBD>
- Docs lag: <TBD>
- Markers captured: <TBD> (#DISCOVERY, #DECISION, #LEARNED)

### Reflection Roll-up
- Repeatable wins: …
- Systemic frictions (top 3): …
- Process changes adopted: …
- Open questions for next plan: …

### Harvest Preparation (JIG)

**Markers Summary:**
- Discoveries: <count>
- Decisions: <count>
- Learned patterns: <count>

**Recommended OSTC Nodes (from DISCOVERIES only):**

*Note: Outcomes O-JIG-006 through O-JIG-009 and Specifications S-JIG-005 through S-JIG-011 were known from SCOPE and already created in WU0. List only NEW constraints discovered during implementation here.*

Example format:
- [ ] S-JIG-012: "Prompt token estimation must account for JSON formatting overhead" (NEW - discovered actual usage 30% higher than naive char/4 estimate)
- [ ] S-JIG-006: Update with actual retry timing values (UPDATE - exponential backoff tuning from production testing)

**Subsystems Touched:** jig-graph (primary), jig-config (new), jig-ai (new)

**Next Step:** `jig ai-distill --branch feat/ai-repair-orphaned-nodes`

---

## Notes

### Open Questions (to resolve during implementation)

1. **Keyring integration**: Optional dependency or required?
   - **Recommendation from SCOPE**: Optional. Config file sufficient for MVP.
   - **Decision point**: WU2 implementation

2. **Batch size**: How many findings per API call?
   - **Recommendation from SCOPE**: 100 findings max
   - **Validation point**: WU4 manual testing with large graphs

3. **Cost threshold**: Confirm when to require user confirmation?
   - **Recommendation from SCOPE**: $0.10 (10 cents)
   - **May adjust**: After testing with real usage patterns

4. **Model selection**: Sonnet vs Haiku for simple cases?
   - **Recommendation from SCOPE**: Sonnet default, allow override
   - **Future enhancement**: Auto-select based on finding complexity

### Risks

- **Risk**: Prompt template may need iteration based on actual output quality
  - **Mitigation**: Manual validation in WU4 with real jig graph
  - **Fallback**: Provide examples in prompt, adjust based on feedback

- **Risk**: Cost estimation accuracy depends on token counting heuristics
  - **Mitigation**: Integration test with real API call validates 20% threshold
  - **Fallback**: Add safety margin to estimates (e.g., 1.3x multiplier)

- **Risk**: Credential system may not work on all platforms (Windows paths differ)
  - **Mitigation**: Use `Path.home()` for cross-platform compatibility
  - **Validation**: Test on macOS, Linux (Windows testing in future)

- **Risk**: Large graphs (>1000 nodes) may exceed context window
  - **Mitigation**: Batching strategy in prompt template (WU4)
  - **Future**: Add pagination support if needed

### Dependencies

- **External libraries to add**:
  - `anthropic` (Claude API SDK)
  - `tenacity` (retry logic) or use built-in retry in anthropic SDK
  - `keyring` (optional, for system keystore integration)

- **Configuration**:
  - Add to `pyproject.toml` dependencies
  - Mark `keyring` as optional extra

---

**Status:** Ready for execution
**Next Action:** Execute Work Unit 0 (create Intent node files)
