# @jig T-CLAUDE-001 verifies:S-JIG-013,S-JIG-011 subsystem:jig-ai
"""Tests for Claude API client module."""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from jig.ai.claude_client import APIError, ClaudeClient, TokenLimitError
from jig.config.credentials import CredentialError


# Fixtures
@pytest.fixture
def mock_anthropic(monkeypatch):
    """Mock Anthropic client."""
    import sys

    # Create mock Anthropic module and class
    mock_anthropic_module = MagicMock()
    mock_anthropic_class = MagicMock()
    mock_client = MagicMock()

    # Setup mock hierarchy
    mock_anthropic_module.Anthropic = mock_anthropic_class
    mock_anthropic_class.return_value = mock_client

    # Add exception classes needed by tests
    mock_anthropic_module.APIError = type("APIError", (Exception,), {})
    mock_anthropic_module.RateLimitError = type("RateLimitError", (Exception,), {})

    # Inject into sys.modules before any imports
    monkeypatch.setitem(sys.modules, "anthropic", mock_anthropic_module)

    yield mock_client


@pytest.fixture
def mock_credential(monkeypatch):
    """Mock credential loading."""
    mock_load = Mock(return_value="test-api-key-123")
    monkeypatch.setattr("jig.ai.claude_client.load_credential", mock_load)
    return mock_load


@pytest.fixture
def sample_findings():
    """Sample findings from graph integrity check."""
    return {
        "timestamp": "2025-11-21T10:00:00Z",
        "total_nodes": 10,
        "findings": {
            "dangling_references": [
                {
                    "node_id": "S-TEST-001",
                    "node_type": "specification",
                    "field": "implements",
                    "missing_reference": "O-TEST-999",
                }
            ],
            "unreferenced_nodes": [
                {
                    "node_id": "S-TEST-002",
                    "node_type": "specification",
                    "potential_reason": "isolated",
                }
            ],
            "malformed_structures": [],
        },
        "statistics": {
            "total_relationships": 15,
            "relationship_density": 1.5,
            "node_type_distribution": {"outcome": 3, "specification": 7},
        },
    }


@pytest.fixture
def mock_api_response():
    """Mock successful API response."""
    response = MagicMock()
    response.content = [MagicMock(text="# Orphaned Nodes Report\n\nTest report")]
    response.usage = MagicMock(input_tokens=1000, output_tokens=500)
    return response


# Tests for initialization


def test_init_with_explicit_key(mock_anthropic):
    """Initializes with explicit API key."""
    client = ClaudeClient(api_key="explicit-key-123")

    # Should not call credential loading (uses explicit key)
    assert client.api_key == "explicit-key-123"


def test_init_without_key_loads_credential(mock_credential, mock_anthropic):
    """Initializes without key loads from credential system."""
    client = ClaudeClient()

    mock_credential.assert_called_once_with("anthropic", explicit_key=None)
    assert client.api_key == "test-api-key-123"


def test_init_missing_credential_raises(monkeypatch):
    """Raises CredentialError if no key found."""
    import sys

    # Mock anthropic module
    mock_anthropic_module = MagicMock()
    monkeypatch.setitem(sys.modules, "anthropic", mock_anthropic_module)

    # Mock credential loading to fail
    monkeypatch.setattr(
        "jig.ai.claude_client.load_credential",
        Mock(side_effect=CredentialError("No key found")),
    )

    with pytest.raises(CredentialError, match="No key found"):
        ClaudeClient()


def test_init_without_anthropic_library(mock_credential, monkeypatch):
    """Raises clear error if anthropic library not installed."""
    # Mock import failure
    import builtins

    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "anthropic":
            raise ImportError("No module named 'anthropic'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    with pytest.raises(ImportError, match="Anthropic library not installed"):
        ClaudeClient()


# Tests for analyze_orphaned_nodes


def test_analyze_success(
    mock_credential, mock_anthropic, sample_findings, mock_api_response
):
    """Successfully analyzes findings and returns report."""
    mock_anthropic.messages.create.return_value = mock_api_response

    client = ClaudeClient()
    report = client.analyze_orphaned_nodes(sample_findings, graph_data=[])

    # Should return report text
    assert "Orphaned Nodes Report" in report

    # Should track usage
    assert client.last_usage is not None
    assert client.last_usage["input_tokens"] == 1000
    assert client.last_usage["output_tokens"] == 500
    assert "cost_usd" in client.last_usage


def test_analyze_calls_api_with_correct_params(
    mock_credential, mock_anthropic, sample_findings, mock_api_response
):
    """API called with correct parameters."""
    mock_anthropic.messages.create.return_value = mock_api_response

    client = ClaudeClient()
    client.analyze_orphaned_nodes(sample_findings, graph_data=[], model="claude-opus-4")

    # Check API call
    mock_anthropic.messages.create.assert_called_once()
    call_args = mock_anthropic.messages.create.call_args

    assert call_args.kwargs["model"] == "claude-opus-4"
    assert call_args.kwargs["max_tokens"] == 4096
    assert len(call_args.kwargs["messages"]) == 1
    assert call_args.kwargs["messages"][0]["role"] == "user"


def test_analyze_with_large_input_raises_token_limit(
    mock_credential, mock_anthropic, sample_findings
):
    """Raises TokenLimitError if input too large."""
    # Create huge findings that would exceed token limit
    huge_findings = sample_findings.copy()
    huge_findings["findings"]["dangling_references"] = [
        {"node_id": f"S-TEST-{i}", "field": "implements", "missing_reference": "O-999"}
        for i in range(50000)  # Massive list
    ]

    client = ClaudeClient()

    with pytest.raises(TokenLimitError, match="Input too large"):
        client.analyze_orphaned_nodes(huge_findings, graph_data=[])


# Tests for retry logic


def test_retry_on_api_error(
    mock_credential, mock_anthropic, sample_findings, mock_api_response
):
    """Retries on API errors."""
    from anthropic import APIError as AnthropicAPIError

    # Fail twice, then succeed
    mock_anthropic.messages.create.side_effect = [
        AnthropicAPIError("Network error"),
        AnthropicAPIError("Network error"),
        mock_api_response,
    ]

    client = ClaudeClient()

    with patch("time.sleep"):  # Don't actually sleep in tests
        report = client.analyze_orphaned_nodes(sample_findings, graph_data=[])

    # Should succeed after retries
    assert "Orphaned Nodes Report" in report
    assert mock_anthropic.messages.create.call_count == 3


def test_retry_fails_after_max_attempts(
    mock_credential, mock_anthropic, sample_findings
):
    """Raises APIError after max retries."""
    from anthropic import APIError as AnthropicAPIError

    # Always fail
    mock_anthropic.messages.create.side_effect = AnthropicAPIError("Persistent error")

    client = ClaudeClient()

    with patch("time.sleep"):  # Don't actually sleep
        with pytest.raises(APIError, match="failed after 3 attempts"):
            client.analyze_orphaned_nodes(sample_findings, graph_data=[])

    assert mock_anthropic.messages.create.call_count == 3


def test_rate_limit_handling(
    mock_credential, mock_anthropic, sample_findings, mock_api_response
):
    """Handles rate limits (429) with retry."""
    from anthropic import RateLimitError

    # Rate limit once, then succeed
    rate_limit_error = RateLimitError("Rate limited")
    rate_limit_error.retry_after = 2

    mock_anthropic.messages.create.side_effect = [rate_limit_error, mock_api_response]

    client = ClaudeClient()

    with patch("time.sleep") as mock_sleep:
        report = client.analyze_orphaned_nodes(sample_findings, graph_data=[])

    # Should succeed
    assert "Orphaned Nodes Report" in report

    # Should have slept for retry_after duration
    mock_sleep.assert_called_with(2)


# Tests for cost estimation


def test_estimate_token_cost_structure(mock_credential, mock_anthropic):
    """Cost estimation returns expected structure."""
    client = ClaudeClient()

    findings = {
        "findings": {
            "dangling_references": [{"node_id": "S-001"}],
            "unreferenced_nodes": [{"node_id": "S-002"}],
            "malformed_structures": [],
        }
    }

    estimate = client.estimate_token_cost(findings)

    # Check structure
    assert "input_tokens" in estimate
    assert "output_tokens" in estimate
    assert "est_cost_usd" in estimate
    assert "model" in estimate

    # Check types
    assert isinstance(estimate["input_tokens"], int)
    assert isinstance(estimate["output_tokens"], int)
    assert isinstance(estimate["est_cost_usd"], float)


def test_estimate_scales_with_findings(mock_credential, mock_anthropic):
    """Cost estimation scales with number of findings."""
    client = ClaudeClient()

    # Few findings
    small_findings = {
        "findings": {
            "dangling_references": [{"node_id": "S-001"}],
            "unreferenced_nodes": [],
            "malformed_structures": [],
        }
    }

    # Many findings
    large_findings = {
        "findings": {
            "dangling_references": [{"node_id": f"S-{i:03d}"} for i in range(50)],
            "unreferenced_nodes": [{"node_id": f"O-{i:03d}"} for i in range(50)],
            "malformed_structures": [],
        }
    }

    small_estimate = client.estimate_token_cost(small_findings)
    large_estimate = client.estimate_token_cost(large_findings)

    # Large should have more output tokens
    assert large_estimate["output_tokens"] > small_estimate["output_tokens"]
    assert large_estimate["est_cost_usd"] > small_estimate["est_cost_usd"]


def test_estimate_complexity_adjustment(mock_credential, mock_anthropic):
    """Applies complexity adjustment for >20 findings."""
    client = ClaudeClient()

    # 25 findings (>20 threshold)
    findings = {
        "findings": {
            "dangling_references": [{"node_id": f"S-{i:03d}"} for i in range(25)],
            "unreferenced_nodes": [],
            "malformed_structures": [],
        }
    }

    estimate = client.estimate_token_cost(findings)

    # Base: 1500 + (25 * 50) = 2750
    # With 1.2x adjustment: 3300
    expected_output = int((1500 + 25 * 50) * 1.2)
    assert estimate["output_tokens"] == expected_output


# Tests for usage tracking


def test_last_usage_tracked(
    mock_credential, mock_anthropic, sample_findings, mock_api_response
):
    """Tracks actual token usage after API call."""
    mock_anthropic.messages.create.return_value = mock_api_response

    client = ClaudeClient()

    # Before call
    assert client.last_usage is None

    # After call
    client.analyze_orphaned_nodes(sample_findings, graph_data=[])

    assert client.last_usage["input_tokens"] == 1000
    assert client.last_usage["output_tokens"] == 500
    assert client.last_usage["cost_usd"] > 0


def test_cost_calculation_sonnet(mock_credential, mock_anthropic):
    """Cost calculation uses correct Sonnet pricing."""
    client = ClaudeClient()

    # Sonnet: $3/MTok input, $15/MTok output
    cost = client._calculate_cost(1000, 500, "claude-sonnet-4-5")

    expected = (1000 * 3.00 / 1_000_000) + (500 * 15.00 / 1_000_000)
    assert cost == pytest.approx(expected)


def test_cost_calculation_opus(mock_credential, mock_anthropic):
    """Cost calculation uses correct Opus pricing."""
    client = ClaudeClient()

    # Opus: $15/MTok input, $75/MTok output
    cost = client._calculate_cost(1000, 500, "claude-opus-4")

    expected = (1000 * 15.00 / 1_000_000) + (500 * 75.00 / 1_000_000)
    assert cost == pytest.approx(expected)


# Tests for prompt building


def test_prompt_includes_findings(
    mock_credential, mock_anthropic, sample_findings, mock_api_response
):
    """Prompt includes all findings data."""
    mock_anthropic.messages.create.return_value = mock_api_response

    client = ClaudeClient()
    client.analyze_orphaned_nodes(sample_findings, graph_data=[])

    # Get the prompt that was sent
    call_args = mock_anthropic.messages.create.call_args
    prompt = call_args.kwargs["messages"][0]["content"]

    # Check prompt contains key information
    assert "Total nodes: 10" in prompt
    assert "Dangling References (1)" in prompt
    assert "Unreferenced Nodes (1)" in prompt
    assert "S-TEST-001" in prompt
    assert "O-TEST-999" in prompt


def test_prompt_includes_context_rules(
    mock_credential, mock_anthropic, sample_findings, mock_api_response
):
    """Prompt includes OSTC context rules."""
    mock_anthropic.messages.create.return_value = mock_api_response

    client = ClaudeClient()
    client.analyze_orphaned_nodes(sample_findings, graph_data=[])

    call_args = mock_anthropic.messages.create.call_args
    prompt = call_args.kwargs["messages"][0]["content"]

    # Check context rules are present
    assert "Outcome nodes (O-*)" in prompt
    assert "deprecated" in prompt.lower()
    assert "intentional" in prompt.lower()


# Tests for model selection


def test_supports_multiple_models(
    mock_credential, mock_anthropic, sample_findings, mock_api_response
):
    """Supports Sonnet and Opus models."""
    mock_anthropic.messages.create.return_value = mock_api_response

    client = ClaudeClient()

    # Test Sonnet
    client.analyze_orphaned_nodes(
        sample_findings, graph_data=[], model="claude-sonnet-4-5"
    )
    assert mock_anthropic.messages.create.call_args.kwargs["model"] == "claude-sonnet-4-5"

    # Test Opus
    mock_anthropic.messages.create.reset_mock()
    client.analyze_orphaned_nodes(sample_findings, graph_data=[], model="claude-opus-4")
    assert mock_anthropic.messages.create.call_args.kwargs["model"] == "claude-opus-4"


# Integration-style test (requires real API key)
@pytest.mark.integration
@pytest.mark.skipif(
    True, reason="Requires real API key - run manually with: pytest -m integration"
)
def test_real_api_call():
    """Integration test with real Claude API (manually run only)."""
    # This test requires:
    # 1. Real Anthropic API key in env/config
    # 2. pytest -m integration to run
    client = ClaudeClient()

    findings = {
        "total_nodes": 5,
        "findings": {
            "dangling_references": [
                {
                    "node_id": "S-TEST-001",
                    "field": "implements",
                    "missing_reference": "O-TEST-999",
                }
            ],
            "unreferenced_nodes": [],
            "malformed_structures": [],
        },
        "statistics": {"node_type_distribution": {"specification": 5}},
    }

    # Get estimate
    estimate = client.estimate_token_cost(findings)

    # Make real call
    report = client.analyze_orphaned_nodes(findings, graph_data=[])

    # Check report
    assert len(report) > 100  # Should be substantial
    assert "S-TEST-001" in report  # Should mention the issue

    # Check cost accuracy (within 20%)
    actual = client.last_usage
    input_error = abs(estimate["input_tokens"] - actual["input_tokens"]) / actual[
        "input_tokens"
    ]
    output_error = abs(estimate["output_tokens"] - actual["output_tokens"]) / actual[
        "output_tokens"
    ]

    assert input_error < 0.20, f"Input token error: {input_error:.1%}"
    assert output_error < 0.20, f"Output token error: {output_error:.1%}"
