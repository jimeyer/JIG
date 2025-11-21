---
id: S-JIG-013
type: Specification
title: Claude API Client with Cost Management
subsystem: jig-ai
implements:
  - O-JIG-008
created: 2025-11-21
status: active
---

# Specification: Claude API Client with Cost Management

## Purpose

Provide a robust client for Claude API interactions with retry logic, cost estimation, and usage tracking.

## Requirements

### Core Functionality

1. **Authentication**
   - Use credential resolution system (S-JIG-007)
   - Support explicit API key parameter override
   - Raise clear `CredentialError` if no key found

2. **API Interaction**
   - Model support: `claude-sonnet-4-5` (default), `claude-opus-4`
   - Send findings + graph context to Claude
   - Receive markdown report with repair suggestions
   - Method: `analyze_orphaned_nodes(findings, graph_data, model)`

3. **Cost Estimation**
   - Pre-call token estimation
   - Calculate: input tokens, output tokens, USD cost
   - Method: `estimate_token_cost(findings) -> Dict[str, int]`
   - Accuracy requirement: Within 20% of actual usage

4. **Usage Tracking**
   - Track actual token counts after API call
   - Store in `last_usage` attribute
   - Include: input_tokens, output_tokens, cost_usd

### Reliability

1. **Retry Logic**
   - Retry on network errors: 3 attempts max
   - Exponential backoff: 2s, 4s, 8s
   - Use `tenacity` library or Anthropic SDK built-in retry

2. **Rate Limiting**
   - Detect 429 status codes
   - Wait per Retry-After header
   - Retry after waiting

3. **Error Handling**
   - Network failures: Retry then fail with clear message
   - Auth errors: Direct user to `jigy config set-credential`
   - Token limit exceeded: Suggest batching strategy

## Interface

```python
class ClaudeClient:
    """Client for Claude API with credential management and cost tracking."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize client with credential resolution.

        Args:
            api_key: Optional explicit API key (overrides other sources)

        Raises:
            CredentialError: If no API key found via any source
        """

    def analyze_orphaned_nodes(
        self,
        findings: Dict[str, Any],
        graph_data: List[Dict],
        model: str = "claude-sonnet-4-5"
    ) -> str:
        """
        Analyze orphaned node findings and generate repair report.

        Args:
            findings: Structured detection results from S-JIG-012
            graph_data: Full graph nodes for context
            model: Claude model to use

        Returns:
            Markdown report with categorized issues and repair suggestions

        Raises:
            APIError: On API call failures after retries
            TokenLimitError: If input exceeds model context window
        """

    def estimate_token_cost(self, findings: Dict) -> Dict[str, int]:
        """
        Estimate token usage and cost before API call.

        Args:
            findings: Detection results to analyze

        Returns:
            {
                "input_tokens": ~5000,
                "output_tokens": ~1500,
                "est_cost_usd": 0.0375
            }
        """

    @property
    def last_usage(self) -> Dict[str, Union[int, float]]:
        """
        Get actual usage from last API call.

        Returns:
            {
                "input_tokens": 4823,
                "output_tokens": 1654,
                "cost_usd": 0.0393
            }
        """
```

## Cost Estimation Algorithm

**Input tokens:**
```python
input_tokens = (
    len(json.dumps(findings)) / 4  # JSON payload
    + len(prompt_template) / 4      # Prompt structure
    + sum(len(node['description']) / 4 for node in context_nodes)  # Node context
)
```

**Output tokens:**
- Estimate: 1500 tokens (typical report length)
- Adjust based on finding count: +50 tokens per finding

**Pricing (as of 2025-11):**
- Sonnet: $3/MTok input, $15/MTok output
- Opus: $15/MTok input, $75/MTok output

**Accuracy validation:**
- Integration test: Compare estimate to actual usage
- Pass if error <20%

## Rationale

- **Retry logic**: Network failures are transient; retries improve reliability
- **Cost estimation**: Users need visibility into spending before API calls
- **Model selection**: Sonnet balances quality and cost; Opus available for complex cases
- **Token tracking**: Enables cost monitoring and optimization

## Dependencies

- `anthropic` Python SDK (official)
- Credential system (S-JIG-007)
- Prompt templates (S-JIG-008)

## Testing

- Unit tests with mocked Anthropic client
- Integration test with real API (marked `@pytest.mark.integration`)
- Retry logic test (simulate network failures)
- Cost estimation accuracy test (compare estimate to actual)

## Security

- Never log full API keys (redaction via S-JIG-010)
- No credentials in error messages or stack traces
- Validate inputs to prevent prompt injection

## References

- SCOPE: `docs/wip/S014_SCOPE_ai_repair_orphaned_nodes.md` (WU2)
- Anthropic API docs: https://docs.anthropic.com/
