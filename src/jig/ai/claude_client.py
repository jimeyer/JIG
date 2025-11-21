# @jig C-CLAUDE-001 implements:S-JIG-013,S-JIG-011 subsystem:jig-ai interface:public
"""Claude API client with cost management and retry logic.

This module provides a robust client for Claude API interactions with:
- Credential resolution via jig.config.credentials
- Retry logic with exponential backoff
- Token cost estimation and tracking
- Rate limit handling
"""

import json
import time
from typing import Any, Optional

from jig.config.credentials import CredentialError, load_credential


class APIError(Exception):
    """Raised when API call fails after retries."""

    pass


class TokenLimitError(Exception):
    """Raised when input exceeds model context window."""

    pass


class ClaudeClient:
    """Client for Claude API with credential management and cost tracking.

    Examples:
        >>> client = ClaudeClient()  # Uses credential resolution
        >>> findings = {"findings": {...}}
        >>> report = client.analyze_orphaned_nodes(findings, graph_data=[])
    """

    # Model pricing (as of 2025-11, per million tokens)
    PRICING = {
        "claude-sonnet-4-5": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
        "claude-opus-4": {"input": 15.00 / 1_000_000, "output": 75.00 / 1_000_000},
    }

    # Context window sizes (tokens)
    CONTEXT_WINDOWS = {
        "claude-sonnet-4-5": 200_000,
        "claude-opus-4": 200_000,
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize client with credential resolution.

        Args:
            api_key: Optional explicit API key (overrides other sources)

        Raises:
            CredentialError: If no API key found via any source
        """
        try:
            self.api_key = load_credential("anthropic", explicit_key=api_key)
        except CredentialError as e:
            raise CredentialError(
                f"{e}\n\n"
                f"The Claude API client requires an Anthropic API key.\n"
                f"Get one at: https://console.anthropic.com/"
            ) from e

        # Initialize Anthropic client
        try:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=self.api_key)
        except ImportError as e:
            raise ImportError(
                "Anthropic library not installed. Install with: pip install anthropic"
            ) from e

        # Track last API call usage
        self._last_usage: Optional[dict[str, Any]] = None

    def analyze_orphaned_nodes(
        self,
        findings: dict[str, Any],
        graph_data: list[dict[str, Any]],
        model: str = "claude-sonnet-4-5",
    ) -> str:
        """Analyze orphaned node findings and generate repair report.

        Args:
            findings: Structured detection results from graph_integrity.check_graph_integrity()
            graph_data: Full graph nodes for context (optional, for detailed analysis)
            model: Claude model to use (default: claude-sonnet-4-5)

        Returns:
            Markdown report with categorized issues and repair suggestions

        Raises:
            APIError: On API call failures after retries
            TokenLimitError: If input exceeds model context window
        """
        # Build prompt
        prompt = self._build_prompt(findings, graph_data)

        # Check token limits (rough estimate)
        estimated_input_tokens = len(prompt) // 4
        if estimated_input_tokens > self.CONTEXT_WINDOWS.get(model, 200_000):
            raise TokenLimitError(
                f"Input too large: ~{estimated_input_tokens} tokens exceeds "
                f"{self.CONTEXT_WINDOWS[model]} token limit for {model}"
            )

        # Call API with retry logic
        response = self._call_api_with_retry(prompt, model)

        # Extract response text
        report = response.content[0].text

        # Track usage
        self._last_usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "cost_usd": self._calculate_cost(
                response.usage.input_tokens, response.usage.output_tokens, model
            ),
        }

        return report

    def estimate_token_cost(self, findings: dict[str, Any]) -> dict[str, Any]:
        """Estimate token usage and cost before API call.

        Args:
            findings: Detection results to analyze

        Returns:
            Dictionary with estimated usage:
            {
                "input_tokens": ~5000,
                "output_tokens": ~1500,
                "est_cost_usd": 0.0375,
                "model": "claude-sonnet-4-5"
            }
        """
        # Estimate input tokens
        findings_json = json.dumps(findings)
        prompt_length = len(findings_json) + 1500  # Findings + prompt template

        input_tokens = prompt_length // 4  # Rough heuristic: 4 chars per token

        # Estimate output tokens based on finding count
        total_findings = (
            len(findings.get("findings", {}).get("dangling_references", []))
            + len(findings.get("findings", {}).get("unreferenced_nodes", []))
            + len(findings.get("findings", {}).get("malformed_structures", []))
        )

        # Base estimate: 1500 tokens for report structure
        output_tokens = 1500

        # Add tokens per finding (50 tokens per issue for analysis)
        output_tokens += total_findings * 50

        # Complexity adjustment for large graphs
        if total_findings > 20:
            output_tokens = int(output_tokens * 1.2)

        # Calculate cost (using Sonnet pricing as default)
        model = "claude-sonnet-4-5"
        cost_usd = self._calculate_cost(input_tokens, output_tokens, model)

        return {
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
            "est_cost_usd": round(cost_usd, 4),
            "model": model,
        }

    @property
    def last_usage(self) -> Optional[dict[str, Any]]:
        """Get actual usage from last API call.

        Returns:
            Dictionary with actual usage or None if no calls made:
            {
                "input_tokens": 4823,
                "output_tokens": 1654,
                "cost_usd": 0.0393
            }
        """
        return self._last_usage

    def _build_prompt(
        self, findings: dict[str, Any], graph_data: list[dict[str, Any]]
    ) -> str:
        """Build prompt for orphaned node analysis."""
        # Format findings for prompt
        dangling = findings.get("findings", {}).get("dangling_references", [])
        unreferenced = findings.get("findings", {}).get("unreferenced_nodes", [])
        malformed = findings.get("findings", {}).get("malformed_structures", [])

        prompt = f"""You are analyzing a graph of Intent nodes from the OSTC (Outcome-Specification-Technical-Component) framework.

# Graph Context
Total nodes: {findings.get('total_nodes', 0)}
Node types: {json.dumps(findings.get('statistics', {}).get('node_type_distribution', {}))}

# Detected Issues (Deterministic Analysis)

## Dangling References ({len(dangling)})
{json.dumps(dangling, indent=2) if dangling else "None"}

## Unreferenced Nodes ({len(unreferenced)})
{json.dumps(unreferenced, indent=2) if unreferenced else "None"}

## Malformed Structures ({len(malformed)})
{json.dumps(malformed, indent=2) if malformed else "None"}

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
        return prompt

    def _call_api_with_retry(self, prompt: str, model: str, max_retries: int = 3):
        """Call API with exponential backoff retry logic."""
        from anthropic import APIError as AnthropicAPIError
        from anthropic import RateLimitError

        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response

            except RateLimitError as e:
                # Handle 429 rate limits
                retry_after = getattr(e, "retry_after", None) or (2 ** attempt)
                print(
                    f"⚠ Rate limit hit, waiting {retry_after}s before retry {attempt + 1}/{max_retries}..."
                )
                time.sleep(retry_after)
                last_error = e

            except AnthropicAPIError as e:
                # Network/API errors
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(
                        f"⚠ API error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(wait_time)
                    last_error = e
                else:
                    last_error = e

        # All retries failed
        raise APIError(
            f"API call failed after {max_retries} attempts: {last_error}"
        ) from last_error

    def _calculate_cost(
        self, input_tokens: int, output_tokens: int, model: str
    ) -> float:
        """Calculate cost in USD for token usage."""
        pricing = self.PRICING.get(model, self.PRICING["claude-sonnet-4-5"])
        cost = input_tokens * pricing["input"] + output_tokens * pricing["output"]
        return cost
