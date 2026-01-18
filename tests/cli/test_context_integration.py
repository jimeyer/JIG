# ABOUTME: Integration tests for context command against real JIG project graphs.
# ABOUTME: Verifies SCOPE use case: "jigy context traverses graph, gives list of related nodes"

"""Integration tests for jigy context command (S-110, S-111, S-112, S-113).

These tests run against the real JIG project graphs to verify the SCOPE use case:
"jigy context <identifier> traverses the graph and gives you a list of related nodes"
"""

import json
from pathlib import Path

import pytest

import jig
from click.testing import CliRunner
from jig.cli.main import cli


# Skip all tests if graphs don't exist (fresh clone without rebuild)
GRAPHS_EXIST = (
    Path("jig/generated/intent-graph.ndjson").exists()
    and Path("jig/generated/implementation-graph.ndjson").exists()
    and Path("jig/generated/verification-graph.ndjson").exists()
)


@pytest.mark.skipif(not GRAPHS_EXIST, reason="Requires generated graphs")
class TestContextIntegration:
    """Integration tests for context command against real project."""

    @jig.verifies("S-110")
    def test_context_goal_returns_ancestors_and_descendants(self):
        """jigy context G-001 returns Charter as ancestor, outcomes/specs as descendants."""
        runner = CliRunner()
        result = runner.invoke(cli, ["context", "G-001", "-j"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        data = json.loads(result.output)

        # Root should be G-001
        assert data["root"] == "G-001"

        # Should have nodes
        assert len(data["nodes"]) > 0

        # Charter should be an ancestor (depth < 0)
        charter_nodes = [n for n in data["nodes"] if n["id"] == "Charter"]
        assert len(charter_nodes) == 1, "Charter should be in ancestors"
        assert charter_nodes[0]["depth"] < 0, "Charter should have negative depth (ancestor)"

        # Should have some descendants (outcomes, specs)
        descendants = [n for n in data["nodes"] if n["depth"] > 0]
        assert len(descendants) > 0, "Should have descendants"

        # Descendants should include outcomes or architecture
        descendant_types = {n["type"] for n in descendants}
        assert descendant_types & {"outcome", "architecture"}, "Should have outcome/arch descendants"

    @jig.verifies("S-110", "S-113")
    def test_context_spec_shows_parent_outcome(self):
        """jigy context S-110 returns O-030 as parent with correct depth."""
        runner = CliRunner()
        result = runner.invoke(cli, ["context", "S-110", "-j"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        data = json.loads(result.output)

        # Root should be S-110
        assert data["root"] == "S-110"

        # O-030 should be an ancestor (depth -1)
        o030_nodes = [n for n in data["nodes"] if n["id"] == "O-030"]
        assert len(o030_nodes) == 1, "O-030 should be in ancestors"
        assert o030_nodes[0]["depth"] == -1, "O-030 should be immediate parent (depth -1)"

        # Charter should be ancestor with negative depth
        charter_nodes = [n for n in data["nodes"] if n["id"] == "Charter"]
        assert len(charter_nodes) == 1, "Charter should be reachable"
        assert charter_nodes[0]["depth"] < 0, "Charter should have negative depth"

    @jig.verifies("S-110", "S-112")
    def test_context_max_limits_budget(self):
        """--max N flag limits returned nodes and reports truncation count."""
        runner = CliRunner()
        result = runner.invoke(cli, ["context", "Charter", "--max", "5", "-j"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        data = json.loads(result.output)

        # Should have at most 5 nodes
        assert len(data["nodes"]) <= 5, f"Expected <= 5 nodes, got {len(data['nodes'])}"

        # Should report truncation via 'more' field
        assert "more" in data, "Response should have 'more' field"
        assert data["more"] > 0, "Should indicate more nodes were truncated"

    @jig.verifies("S-110", "S-111")
    def test_context_invalid_identifier_shows_patterns(self):
        """Invalid identifier produces helpful error with valid patterns."""
        runner = CliRunner()
        result = runner.invoke(cli, ["context", "INVALID"])

        assert result.exit_code == 1, "Should fail with exit code 1"

        # Error should list valid patterns
        assert "S-###" in result.output, "Should mention S-### pattern"
        assert "O-###" in result.output, "Should mention O-### pattern"
        assert "G-###" in result.output, "Should mention G-### pattern"
        assert "Charter" in result.output, "Should mention Charter pattern"

    @jig.verifies("S-110")
    def test_context_default_human_readable_output(self):
        """Default output (no flags) is human-readable, not JSON."""
        runner = CliRunner()
        result = runner.invoke(cli, ["context", "Charter"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Should NOT be JSON
        try:
            json.loads(result.output)
            pytest.fail("Default output should not be JSON")
        except json.JSONDecodeError:
            pass  # Expected - not JSON

        # Should contain readable output with Charter
        assert "Charter" in result.output

    @jig.verifies("S-110")
    def test_context_markdown_flag(self):
        """jigy context -m produces markdown output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["context", "G-001", "-m"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Markdown should have header
        assert "# Context:" in result.output

        # Should have table structure
        assert "|" in result.output

    @jig.verifies("S-110", "S-112")
    def test_context_more_zero_for_small_neighborhood(self):
        """more = 0 when entire neighborhood fits in budget."""
        runner = CliRunner()
        # Use high budget to get complete neighborhood
        result = runner.invoke(cli, ["context", "S-110", "--max", "1000", "-j"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        data = json.loads(result.output)

        # With large budget, should have complete neighborhood
        # S-110 has limited descendants so more should be 0
        assert data["more"] == 0, f"Expected more=0 for complete neighborhood, got {data['more']}"

    @jig.verifies("S-110", "S-113")
    def test_context_nodes_have_required_fields(self):
        """Each node in response has id, type, file, edge, depth."""
        runner = CliRunner()
        result = runner.invoke(cli, ["context", "G-001", "-j"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        data = json.loads(result.output)

        for node in data["nodes"]:
            assert "id" in node, f"Node missing id: {node}"
            assert "type" in node, f"Node missing type: {node}"
            assert "file" in node, f"Node missing file: {node}"
            assert "edge" in node, f"Node missing edge: {node}"
            assert "depth" in node, f"Node missing depth: {node}"

    @jig.verifies("S-110", "S-113")
    def test_context_nodes_sorted_by_depth(self):
        """Nodes are sorted by depth (ancestors first, then descendants)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["context", "S-110", "-j"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        data = json.loads(result.output)
        nodes = data["nodes"]

        # Verify depth ordering
        depths = [n["depth"] for n in nodes]
        assert depths == sorted(depths), f"Nodes should be sorted by depth: {depths}"
