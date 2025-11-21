---
id: S-JIG-011
type: Specification
title: Accurate Cost Estimation
subsystem: jig-ai
implements:
  - O-JIG-008
created: 2025-11-21
status: active
---

# Specification: Accurate Cost Estimation

## Purpose

Provide reliable token usage and cost estimates before API calls to enable informed user consent and budget management.

## Requirements

### Estimation Accuracy

- **Target**: Estimates within 20% of actual usage
- **Validation**: Integration test with real API call compares estimate to actual
- **Metrics**:
  - Input tokens: Estimate vs. actual (% error)
  - Output tokens: Estimate vs. actual (% error)
  - Total cost: Estimate vs. actual (% error)

### Estimation Components

1. **Input Token Estimation**
   ```python
   input_tokens = (
       len(json.dumps(findings)) / 4          # Findings JSON
       + len(prompt_template) / 4             # Prompt structure
       + sum(len(node.get('description', '')) / 4
             for node in context_nodes)       # Node context
       + 100                                  # System message overhead
   )
   ```

   **Factors:**
   - JSON serialization overhead (~10-15%)
   - Markdown formatting in prompt
   - Node context (descriptions, types, relationships)
   - System message and instructions

2. **Output Token Estimation**
   ```python
   # Base estimate
   output_tokens = 1500  # Typical report length

   # Adjust for finding count
   output_tokens += len(findings['dangling_references']) * 50
   output_tokens += len(findings['unreferenced_nodes']) * 50
   output_tokens += len(findings['malformed_structures']) * 40

   # Complexity adjustment
   if total_findings > 20:
       output_tokens *= 1.2  # More detailed analysis
   ```

3. **Cost Calculation**
   ```python
   # Pricing as of 2025-11 (update if prices change)
   PRICING = {
       'claude-sonnet-4-5': {
           'input': 3.00 / 1_000_000,   # $3 per million tokens
           'output': 15.00 / 1_000_000  # $15 per million tokens
       },
       'claude-opus-4': {
           'input': 15.00 / 1_000_000,
           'output': 75.00 / 1_000_000
       }
   }

   cost_usd = (
       input_tokens * PRICING[model]['input']
       + output_tokens * PRICING[model]['output']
   )
   ```

### Display Format

**Before API call:**
```
💰 Estimated cost: $0.0375
   Input tokens: ~5000
   Output tokens: ~1500
   Model: claude-sonnet-4-5
```

**After API call:**
```
📈 Actual usage:
   Input tokens: 4823 (estimate: 5000, error: -3.5%)
   Output tokens: 1654 (estimate: 1500, error: +10.3%)
   Cost: $0.0393 (estimate: $0.0375, error: +4.8%)
```

### Estimation Method

```python
def estimate_token_cost(
    findings: Dict[str, Any],
    model: str = "claude-sonnet-4-5"
) -> Dict[str, Union[int, float]]:
    """
    Estimate token usage and cost before API call.

    Args:
        findings: Detection results from deterministic analysis
        model: Claude model to use

    Returns:
        {
            "input_tokens": 5000,
            "output_tokens": 1500,
            "est_cost_usd": 0.0375,
            "model": "claude-sonnet-4-5"
        }
    """
    # Input estimation
    findings_json = json.dumps(findings)
    prompt_len = len(ORPHANED_NODES_PROMPT_TEMPLATE)

    input_tokens = (
        len(findings_json) / 4
        + prompt_len / 4
        + 100  # System overhead
    )

    # Output estimation
    total_findings = (
        len(findings['findings']['dangling_references'])
        + len(findings['findings']['unreferenced_nodes'])
        + len(findings['findings']['malformed_structures'])
    )

    output_tokens = 1500  # Base
    output_tokens += total_findings * 50  # Per-finding analysis

    # Complexity adjustment
    if total_findings > 20:
        output_tokens = int(output_tokens * 1.2)

    # Cost calculation
    pricing = PRICING[model]
    cost_usd = (
        input_tokens * pricing['input']
        + output_tokens * pricing['output']
    )

    return {
        'input_tokens': int(input_tokens),
        'output_tokens': int(output_tokens),
        'est_cost_usd': round(cost_usd, 4),
        'model': model
    }
```

### Tracking Actual Usage

```python
class ClaudeClient:
    def __init__(self, api_key: str):
        self.client = anthropic.Client(api_key=api_key)
        self.last_usage = None

    def analyze_orphaned_nodes(self, findings, graph_data, model):
        response = self.client.messages.create(
            model=model,
            messages=[...],
            max_tokens=4096
        )

        # Track actual usage
        self.last_usage = {
            'input_tokens': response.usage.input_tokens,
            'output_tokens': response.usage.output_tokens,
            'cost_usd': self._calculate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens,
                model
            )
        }

        return response.content[0].text
```

## Validation Strategy

### Integration Test

```python
@pytest.mark.integration
def test_cost_estimation_accuracy(real_api_client):
    """Verify cost estimates are within 20% of actual."""
    # Use real findings from test fixture
    findings = load_fixture('graph_orphans_sample.json')

    # Get estimate
    estimate = real_api_client.estimate_token_cost(findings)

    # Make actual API call
    report = real_api_client.analyze_orphaned_nodes(
        findings,
        graph_data=[],
        model='claude-sonnet-4-5'
    )

    # Compare
    actual = real_api_client.last_usage

    input_error = abs(estimate['input_tokens'] - actual['input_tokens']) / actual['input_tokens']
    output_error = abs(estimate['output_tokens'] - actual['output_tokens']) / actual['output_tokens']
    cost_error = abs(estimate['est_cost_usd'] - actual['cost_usd']) / actual['cost_usd']

    assert input_error < 0.20, f"Input token error: {input_error:.1%}"
    assert output_error < 0.20, f"Output token error: {output_error:.1%}"
    assert cost_error < 0.20, f"Cost error: {cost_error:.1%}"
```

### Calibration

If estimates consistently over/under by >20%:
1. Collect actual usage data from 10+ real runs
2. Calculate average error: `(estimate - actual) / actual`
3. Add calibration factor:
   ```python
   # If estimates average 15% too high
   CALIBRATION_FACTOR = 0.85
   input_tokens = int(input_tokens * CALIBRATION_FACTOR)
   ```

## Rationale

**Why estimate tokens:**
- Users need cost visibility before charges
- Prevents "bill shock" from unexpected API usage
- Enables budget controls (confirm if >$0.10)

**Why 20% accuracy target:**
- Exact prediction impossible (LLM output variability)
- 20% is "good enough" for user decision-making
- Tighter bounds require complex modeling (diminishing returns)

**Why display actual usage:**
- Builds trust (users verify estimate quality)
- Enables cost tracking over time
- Helps calibrate estimation algorithm

**Why track errors:**
- Monitors estimation quality
- Triggers recalibration if drift detected
- Provides data for algorithm improvements

## Future Enhancements

1. **Historical Tracking**
   - Log estimates vs. actuals to SQLite
   - Analyze patterns: "Finding type X consistently underestimated"
   - Auto-adjust estimation based on history

2. **Budget Controls**
   - `--max-cost 0.50` flag to cap spending
   - Abort if estimate exceeds budget

3. **Batch Optimization**
   - For large graphs, estimate cost per batch
   - Help user decide batch size vs. cost tradeoff

## References

- Anthropic pricing: https://www.anthropic.com/pricing
- Token counting: https://docs.anthropic.com/claude/docs/models-overview#token-counting
- SCOPE: `docs/wip/S014_SCOPE_ai_repair_orphaned_nodes.md` (WU2)
