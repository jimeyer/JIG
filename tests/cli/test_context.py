# ABOUTME: Tests for context module - identifier resolution (S-111) and graph traversal (S-112).
# ABOUTME: TDD tests verifying resolve_identifier and traverse_graph functions.

"""Tests for context module (S-111, S-112).

S-111: Context Identifier Resolution - pattern matching for IDs and file paths
S-112: Context Graph Traversal - ancestor/descendant navigation with budget
"""

import json

import pytest

import jig


class TestResolveIdentifier:
    """Tests for resolve_identifier function (S-111)."""

    @jig.verifies("S-111")
    def test_resolves_specification_id(self, sample_graphs):
        """S-### pattern resolves to specification nodes."""
        from jig.cli.context import resolve_identifier

        result = resolve_identifier("S-001", sample_graphs)
        assert result is not None
        assert result["id"] == "S-001"
        assert result["type"] == "specification"

    @jig.verifies("S-111")
    def test_resolves_outcome_id(self, sample_graphs):
        """O-### pattern resolves to outcome nodes."""
        from jig.cli.context import resolve_identifier

        result = resolve_identifier("O-001", sample_graphs)
        assert result is not None
        assert result["id"] == "O-001"
        assert result["type"] == "outcome"

    @jig.verifies("S-111")
    def test_resolves_goal_id(self, sample_graphs):
        """G-### pattern resolves to goal nodes."""
        from jig.cli.context import resolve_identifier

        result = resolve_identifier("G-001", sample_graphs)
        assert result is not None
        assert result["id"] == "G-001"
        assert result["type"] == "goal"

    @jig.verifies("S-111")
    def test_resolves_architecture_id(self, sample_graphs):
        """A-### pattern resolves to architecture nodes."""
        from jig.cli.context import resolve_identifier

        result = resolve_identifier("A-001", sample_graphs)
        assert result is not None
        assert result["id"] == "A-001"
        assert result["type"] == "architecture"

    @jig.verifies("S-111")
    def test_resolves_brick_id(self, sample_graphs):
        """B-* pattern resolves to brick nodes."""
        from jig.cli.context import resolve_identifier

        result = resolve_identifier("B-cli", sample_graphs)
        assert result is not None
        assert result["id"] == "B-cli"
        assert result["type"] == "brick"

    @jig.verifies("S-111")
    def test_resolves_function_id(self, sample_graphs):
        """F-* pattern resolves to function nodes in impl graph."""
        from jig.cli.context import resolve_identifier

        result = resolve_identifier("F-jig.cli.main.run", sample_graphs)
        assert result is not None
        assert result["id"] == "F-jig.cli.main.run"
        assert result["type"] == "function"

    @jig.verifies("S-111")
    def test_resolves_test_id(self, sample_graphs):
        """T-* pattern resolves to test nodes in verify graph."""
        from jig.cli.context import resolve_identifier

        result = resolve_identifier("T-test_cli.test_validate", sample_graphs)
        assert result is not None
        assert result["id"] == "T-test_cli.test_validate"
        assert result["type"] == "test"

    @jig.verifies("S-111")
    def test_resolves_charter(self, sample_graphs):
        """Charter literal resolves to charter node."""
        from jig.cli.context import resolve_identifier

        result = resolve_identifier("Charter", sample_graphs)
        assert result is not None
        assert result["id"] == "Charter"
        assert result["type"] == "charter"

    @jig.verifies("S-111")
    def test_resolves_file_path(self, sample_graphs):
        """File paths resolve to functions in that file."""
        from jig.cli.context import resolve_identifier

        # Create a temp file to simulate existing file
        result = resolve_identifier("src/jig/cli/main.py", sample_graphs)
        # Returns list of function nodes in that file
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(node["file"] == "src/jig/cli/main.py" for node in result)

    @jig.verifies("S-111")
    def test_invalid_identifier_raises_error(self, sample_graphs):
        """Invalid identifiers raise clear error with valid patterns."""
        from jig.cli.context import IdentifierError, resolve_identifier

        with pytest.raises(IdentifierError) as exc_info:
            resolve_identifier("invalid-thing", sample_graphs)

        error_msg = str(exc_info.value)
        # Should mention valid patterns
        assert "S-###" in error_msg or "valid patterns" in error_msg.lower()

    @jig.verifies("S-111")
    def test_nonexistent_id_raises_error(self, sample_graphs):
        """Valid pattern but nonexistent ID raises clear error."""
        from jig.cli.context import IdentifierError, resolve_identifier

        with pytest.raises(IdentifierError) as exc_info:
            resolve_identifier("S-999", sample_graphs)

        error_msg = str(exc_info.value)
        assert "S-999" in error_msg or "not found" in error_msg.lower()


class TestTraverseGraph:
    """Tests for traverse_graph function (S-112)."""

    @jig.verifies("S-112")
    def test_returns_all_ancestors(self, sample_graphs):
        """All ancestors from node to Charter are included."""
        from jig.cli.context import traverse_graph

        # Start from a spec, should get outcome, goal, charter
        result = traverse_graph("S-001", sample_graphs, max_nodes=100)

        ancestors = result["ancestors"]
        ancestor_ids = {n["id"] for n in ancestors}

        # Spec should have outcome as parent
        assert "O-001" in ancestor_ids
        # Outcome should have goal as parent
        assert "G-001" in ancestor_ids
        # Goal should have charter as parent
        assert "Charter" in ancestor_ids

    @jig.verifies("S-112")
    def test_returns_immediate_children(self, sample_graphs):
        """Immediate children (depth 1) are always included."""
        from jig.cli.context import traverse_graph

        # Start from outcome, should get spec children
        result = traverse_graph("O-001", sample_graphs, max_nodes=100)

        children = result["children"]
        assert len(children) > 0
        # O-001 specifies S-001
        child_ids = {n["id"] for n in children}
        assert "S-001" in child_ids

    @jig.verifies("S-112")
    def test_fills_descendants_breadth_first(self, sample_graphs):
        """Deeper descendants are added breadth-first by depth layer."""
        from jig.cli.context import traverse_graph

        # Start from Charter with limited budget
        result = traverse_graph("Charter", sample_graphs, max_nodes=20)

        # Immediate children should be goals (depth 1)
        children = result["children"]
        assert len(children) > 0
        # Charter's immediate children are goals
        assert all(c["type"] == "goal" for c in children)

        # Deeper descendants (depth 2+) should be outcomes/arch then specs
        descendants = result["descendants"]
        if descendants:
            # First deeper descendants are outcomes/arch (depth 2 from Charter)
            first_descendant = descendants[0]
            assert first_descendant["type"] in ("outcome", "architecture")

    @jig.verifies("S-112")
    def test_respects_max_budget(self, sample_graphs):
        """Total nodes in response ≤ max_nodes."""
        from jig.cli.context import traverse_graph

        max_budget = 10
        result = traverse_graph("Charter", sample_graphs, max_nodes=max_budget)

        total_nodes = (
            1  # root node
            + len(result.get("ancestors", []))
            + len(result.get("children", []))
            + len(result.get("descendants", []))
        )
        assert total_nodes <= max_budget

    @jig.verifies("S-112")
    def test_more_count_for_truncated_results(self, sample_graphs):
        """When budget exhausted, 'more' reports omitted descendant count."""
        from jig.cli.context import traverse_graph

        # Use very small budget to force truncation
        result = traverse_graph("Charter", sample_graphs, max_nodes=5)

        # Should have 'more' field indicating truncation
        assert "more" in result
        # If truncated, more > 0
        if result.get("descendants"):
            # We know Charter has many descendants
            assert result["more"] >= 0

    @jig.verifies("S-112")
    def test_more_zero_for_complete_neighborhood(self, sample_graphs):
        """more = 0 means complete neighborhood (no truncation)."""
        from jig.cli.context import traverse_graph

        # Use large budget for small subtree
        result = traverse_graph("S-001", sample_graphs, max_nodes=1000)

        # Should be complete with more=0
        assert result["more"] == 0

    @jig.verifies("S-112")
    def test_ancestors_always_included(self, sample_graphs):
        """Ancestors consume budget first but are always included."""
        from jig.cli.context import traverse_graph

        # Even with tight budget, ancestors should be present
        result = traverse_graph("S-001", sample_graphs, max_nodes=5)

        # Should have ancestors even with small budget
        assert "ancestors" in result
        ancestor_ids = {n["id"] for n in result["ancestors"]}
        # Charter should be reachable
        assert "Charter" in ancestor_ids

    @jig.verifies("S-112")
    def test_root_node_included(self, sample_graphs):
        """The root node itself is included in response."""
        from jig.cli.context import traverse_graph

        result = traverse_graph("S-001", sample_graphs, max_nodes=100)

        assert "root" in result
        assert result["root"]["id"] == "S-001"


@pytest.fixture
def sample_graphs(tmp_path):
    """Create sample graph files for testing."""
    # Intent graph with Charter -> Goal -> Outcome -> Spec hierarchy
    intent_nodes = [
        {"_meta": {"version": "2.0"}},
        {"id": "Charter", "type": "charter", "file": "jig/Charter.md", "goals": ["G-001"]},
        {"id": "G-001", "type": "goal", "title": "Test Goal", "file": "jig/Charter.md"},
        {
            "id": "A-001",
            "type": "architecture",
            "title": "Test Arch",
            "file": "jig/architecture/A-001.md",
            "goals": ["G-001"],
            "specifications": ["S-001"],
        },
        {
            "id": "O-001",
            "type": "outcome",
            "title": "Test Outcome",
            "file": "jig/outcomes/O-001.md",
            "goals": ["G-001"],
            "specifications": ["S-001"],
        },
        {"id": "S-001", "type": "specification", "file": "jig/specifications/S-001.md"},
        {"id": "B-cli", "type": "brick", "name": "CLI", "layer": 1, "file": "jig/bricks.yaml"},
    ]
    # Edges
    intent_edges = [
        {"source": "Charter", "target": "G-001", "type": "defines_goal"},
        {"source": "O-001", "target": "G-001", "type": "supports_goal"},
        {"source": "O-001", "target": "S-001", "type": "specifies"},
        {"source": "A-001", "target": "G-001", "type": "supports_goal"},
        {"source": "A-001", "target": "S-001", "type": "specifications"},
    ]

    intent_path = tmp_path / "intent-graph.ndjson"
    with open(intent_path, "w") as f:
        for item in intent_nodes + intent_edges:
            f.write(json.dumps(item) + "\n")

    # Implementation graph with functions
    impl_nodes = [
        {"_meta": {"version": "1.0"}},
        {
            "id": "F-jig.cli.main.run",
            "type": "function",
            "file": "src/jig/cli/main.py",
            "name": "run",
            "implements": ["S-001"],
        },
        {
            "id": "F-jig.cli.main.validate",
            "type": "function",
            "file": "src/jig/cli/main.py",
            "name": "validate",
        },
    ]
    impl_edges = [
        {"source": "F-jig.cli.main.run", "target": "S-001", "type": "implements"},
    ]

    impl_path = tmp_path / "implementation-graph.ndjson"
    with open(impl_path, "w") as f:
        for item in impl_nodes + impl_edges:
            f.write(json.dumps(item) + "\n")

    # Verification graph with tests
    verify_nodes = [
        {"_meta": {"version": "1.0"}},
        {
            "id": "T-test_cli.test_validate",
            "type": "test",
            "file": "tests/cli/test_cli.py",
            "verifies": ["S-001"],
        },
    ]
    verify_edges = [
        {"source": "T-test_cli.test_validate", "target": "S-001", "type": "verifies"},
    ]

    verify_path = tmp_path / "verification-graph.ndjson"
    with open(verify_path, "w") as f:
        for item in verify_nodes + verify_edges:
            f.write(json.dumps(item) + "\n")

    return {
        "intent": intent_path,
        "impl": impl_path,
        "verify": verify_path,
        "project_root": tmp_path,
    }


class TestContextCommand:
    """Tests for context_command function (S-110)."""

    @jig.verifies("S-110")
    def test_context_command_returns_exit_code_and_output(self, context_project):
        """context_command returns (exit_code, output) tuple."""
        from jig.cli.context import context_command

        exit_code, output = context_command(
            identifier="S-001",
            project_root=context_project,
            max_nodes=50,
            output_format="human",
        )

        assert exit_code == 0
        assert isinstance(output, str)
        assert "S-001" in output

    @jig.verifies("S-110")
    def test_context_command_max_controls_budget(self, context_project):
        """--max N flag controls node budget."""
        from jig.cli.context import context_command

        # With small max, should still work
        exit_code, output = context_command(
            identifier="Charter",
            project_root=context_project,
            max_nodes=5,
            output_format="json",
        )

        assert exit_code == 0
        result = json.loads(output)
        assert "root" in result
        assert "nodes" in result

    @jig.verifies("S-110", "S-111")
    def test_context_command_invalid_identifier_returns_overview_with_note(self, context_project_full):
        """Invalid identifier returns overview + note (graceful fallback per S-111)."""
        from jig.cli.context import context_command

        exit_code, output = context_command(
            identifier="invalid-thing",
            project_root=context_project_full,
            max_nodes=50,
            output_format="human",
            skip_rebuild=True,
        )

        # Graceful fallback: returns 0 with overview + note
        assert exit_code == 0
        assert "Note:" in output
        assert "invalid-thing" in output
        # Should still show overview content
        assert "Goals:" in output or "Specs:" in output

    @jig.verifies("S-110")
    def test_context_command_bare_returns_overview(self, context_project_full):
        """Bare context command (no identifier) returns project overview."""
        from jig.cli.context import context_command

        exit_code, output = context_command(
            identifier=None,
            project_root=context_project_full,
            max_nodes=50,
            output_format="human",
            skip_rebuild=True,
        )

        assert exit_code == 0
        # Should have overview content
        assert "JIG:" in output or "Goals:" in output
        # Should not have traversal content
        assert "Context for:" not in output

    @jig.verifies("S-110", "S-111")
    def test_context_command_nonexistent_spec_returns_overview_with_note(self, context_project_full):
        """Non-existent spec ID returns overview + 'not found' note."""
        from jig.cli.context import context_command

        exit_code, output = context_command(
            identifier="S-999",
            project_root=context_project_full,
            max_nodes=50,
            output_format="human",
            skip_rebuild=True,
        )

        assert exit_code == 0
        assert "Note:" in output
        assert "S-999" in output
        assert "not found" in output.lower()

    @jig.verifies("S-110")
    def test_context_command_json_output(self, context_project):
        """JSON output format produces valid JSON."""
        from jig.cli.context import context_command

        exit_code, output = context_command(
            identifier="S-001",
            project_root=context_project,
            max_nodes=50,
            output_format="json",
        )

        assert exit_code == 0
        result = json.loads(output)
        assert "root" in result
        assert result["root"] == "S-001"

    @jig.verifies("S-110")
    def test_context_command_markdown_output(self, context_project):
        """Markdown output format produces readable markdown."""
        from jig.cli.context import context_command

        exit_code, output = context_command(
            identifier="S-001",
            project_root=context_project,
            max_nodes=50,
            output_format="markdown",
        )

        assert exit_code == 0
        assert "# Context:" in output
        # Should have markdown table headers
        assert "|" in output


class TestFormatResponse:
    """Tests for format_response function (S-113)."""

    @jig.verifies("S-113")
    def test_format_response_has_required_fields(self, sample_graphs):
        """JSON response has root, nodes, more fields."""
        from jig.cli.context import format_response, traverse_graph, _load_all_graphs

        traversal_result = traverse_graph("S-001", sample_graphs, max_nodes=100)
        _, all_edges = _load_all_graphs(sample_graphs)
        response = format_response(traversal_result, all_edges)

        assert "root" in response
        assert "nodes" in response
        assert "more" in response

    @jig.verifies("S-113")
    def test_format_response_root_is_identifier(self, sample_graphs):
        """root field is the queried identifier."""
        from jig.cli.context import format_response, traverse_graph, _load_all_graphs

        traversal_result = traverse_graph("O-001", sample_graphs, max_nodes=100)
        _, all_edges = _load_all_graphs(sample_graphs)
        response = format_response(traversal_result, all_edges)

        assert response["root"] == "O-001"

    @jig.verifies("S-113")
    def test_format_response_nodes_have_required_fields(self, sample_graphs):
        """Each node has id, type, file, edge, depth fields."""
        from jig.cli.context import format_response, traverse_graph, _load_all_graphs

        traversal_result = traverse_graph("S-001", sample_graphs, max_nodes=100)
        _, all_edges = _load_all_graphs(sample_graphs)
        response = format_response(traversal_result, all_edges)

        for node in response["nodes"]:
            assert "id" in node
            assert "type" in node
            assert "file" in node
            assert "edge" in node
            assert "depth" in node

    @jig.verifies("S-113")
    def test_format_response_depth_negative_for_ancestors(self, sample_graphs):
        """Ancestor nodes have negative depth."""
        from jig.cli.context import format_response, traverse_graph, _load_all_graphs

        traversal_result = traverse_graph("S-001", sample_graphs, max_nodes=100)
        _, all_edges = _load_all_graphs(sample_graphs)
        response = format_response(traversal_result, all_edges)

        # S-001's ancestors (O-001, G-001, Charter) should have negative depth
        ancestor_ids = {"O-001", "G-001", "Charter"}
        for node in response["nodes"]:
            if node["id"] in ancestor_ids:
                assert node["depth"] < 0, f"{node['id']} should have negative depth"

    @jig.verifies("S-113")
    def test_format_response_depth_positive_for_descendants(self, sample_graphs):
        """Descendant nodes have positive depth."""
        from jig.cli.context import format_response, traverse_graph, _load_all_graphs

        traversal_result = traverse_graph("O-001", sample_graphs, max_nodes=100)
        _, all_edges = _load_all_graphs(sample_graphs)
        response = format_response(traversal_result, all_edges)

        # O-001's descendants (S-001) should have positive depth
        for node in response["nodes"]:
            if node["id"] == "S-001":
                assert node["depth"] > 0, "S-001 should have positive depth"

    @jig.verifies("S-113")
    def test_format_response_nodes_sorted_by_depth_then_id(self, sample_graphs):
        """Nodes are sorted by depth (ancestors first), then by ID."""
        from jig.cli.context import format_response, traverse_graph, _load_all_graphs

        traversal_result = traverse_graph("S-001", sample_graphs, max_nodes=100)
        _, all_edges = _load_all_graphs(sample_graphs)
        response = format_response(traversal_result, all_edges)

        nodes = response["nodes"]
        # Check sorting: depth ascending, then id ascending
        for i in range(len(nodes) - 1):
            curr = nodes[i]
            next_node = nodes[i + 1]
            if curr["depth"] == next_node["depth"]:
                assert curr["id"] <= next_node["id"], f"Nodes at same depth should be sorted by ID"
            else:
                assert curr["depth"] < next_node["depth"], f"Nodes should be sorted by depth"

    @jig.verifies("S-113")
    def test_format_response_more_zero_when_complete(self, sample_graphs):
        """more = 0 when neighborhood is complete."""
        from jig.cli.context import format_response, traverse_graph, _load_all_graphs

        traversal_result = traverse_graph("S-001", sample_graphs, max_nodes=1000)
        _, all_edges = _load_all_graphs(sample_graphs)
        response = format_response(traversal_result, all_edges)

        assert response["more"] == 0

    @jig.verifies("S-113")
    def test_format_response_edge_type_from_graph(self, sample_graphs):
        """Edge field uses raw edge type from graph."""
        from jig.cli.context import format_response, traverse_graph, _load_all_graphs

        # Start from S-001, check that function child has "implements" edge
        traversal_result = traverse_graph("S-001", sample_graphs, max_nodes=100)
        _, all_edges = _load_all_graphs(sample_graphs)
        response = format_response(traversal_result, all_edges)

        # F-jig.cli.main.run implements S-001
        for node in response["nodes"]:
            if node["id"] == "F-jig.cli.main.run":
                assert node["edge"] == "implements"


class TestCliIntegration:
    """Integration tests for jigy context CLI command."""

    @jig.verifies("S-110")
    def test_cli_context_help_shows_usage(self, sample_project):
        """jigy context --help shows usage information."""
        from click.testing import CliRunner
        from jig.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["context", "--help"])

        assert result.exit_code == 0
        assert "IDENTIFIER" in result.output
        assert "--max" in result.output

    @jig.verifies("S-110")
    def test_cli_context_with_valid_identifier(self, sample_project):
        """jigy context <identifier> succeeds with valid ID."""
        from click.testing import CliRunner
        from jig.cli.main import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create minimal project structure
            import os
            os.makedirs("jig/generated", exist_ok=True)

            # Create sample graphs
            intent_content = [
                '{"_meta": {"version": "2.0"}}',
                '{"id": "Charter", "type": "charter", "file": "jig/Charter.md"}',
                '{"id": "G-001", "type": "goal", "file": "jig/Charter.md"}',
                '{"id": "S-001", "type": "specification", "file": "jig/specifications/S-001.md"}',
                '{"source": "Charter", "target": "G-001", "type": "defines_goal"}',
            ]
            with open("jig/generated/intent-graph.ndjson", "w") as f:
                f.write("\n".join(intent_content))
            with open("jig/generated/implementation-graph.ndjson", "w") as f:
                f.write('{"_meta": {"version": "1.0"}}\n')
            with open("jig/generated/verification-graph.ndjson", "w") as f:
                f.write('{"_meta": {"version": "1.0"}}\n')

            result = runner.invoke(cli, ["context", "Charter"])

            assert result.exit_code == 0
            assert "Charter" in result.output

    @jig.verifies("S-110")
    def test_cli_context_json_flag(self, sample_project):
        """jigy context -j produces JSON output."""
        from click.testing import CliRunner
        from jig.cli.main import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            import os
            os.makedirs("jig/generated", exist_ok=True)

            intent_content = [
                '{"_meta": {"version": "2.0"}}',
                '{"id": "Charter", "type": "charter", "file": "jig/Charter.md"}',
            ]
            with open("jig/generated/intent-graph.ndjson", "w") as f:
                f.write("\n".join(intent_content))
            with open("jig/generated/implementation-graph.ndjson", "w") as f:
                f.write('{"_meta": {"version": "1.0"}}\n')
            with open("jig/generated/verification-graph.ndjson", "w") as f:
                f.write('{"_meta": {"version": "1.0"}}\n')

            result = runner.invoke(cli, ["--no-rebuild", "context", "Charter", "-j"])

            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["root"] == "Charter"

    @jig.verifies("S-110")
    def test_cli_context_markdown_flag(self, sample_project):
        """jigy context -m produces markdown output."""
        from click.testing import CliRunner
        from jig.cli.main import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            import os
            os.makedirs("jig/generated", exist_ok=True)

            intent_content = [
                '{"_meta": {"version": "2.0"}}',
                '{"id": "Charter", "type": "charter", "file": "jig/Charter.md"}',
            ]
            with open("jig/generated/intent-graph.ndjson", "w") as f:
                f.write("\n".join(intent_content))
            with open("jig/generated/implementation-graph.ndjson", "w") as f:
                f.write('{"_meta": {"version": "1.0"}}\n')
            with open("jig/generated/verification-graph.ndjson", "w") as f:
                f.write('{"_meta": {"version": "1.0"}}\n')

            result = runner.invoke(cli, ["context", "Charter", "-m"])

            assert result.exit_code == 0
            assert "# Context:" in result.output

    @jig.verifies("S-110", "S-111")
    def test_cli_context_invalid_identifier_returns_overview_with_note(self):
        """Invalid identifier returns overview with note (graceful fallback per S-111)."""
        from click.testing import CliRunner
        from jig.cli.main import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            import os
            os.makedirs("jig/generated", exist_ok=True)
            os.makedirs("jig/specifications", exist_ok=True)

            # Create minimal files for overview
            with open("jig.toml", "w") as f:
                f.write('[jig]\nversion = "0.1.0"\n')
            with open("jig/bricks.yaml", "w") as f:
                f.write("bricks: []\n")
            with open("jig/generated/intent-graph.ndjson", "w") as f:
                f.write('{"_meta": {"version": "2.0"}}\n')
            with open("jig/generated/implementation-graph.ndjson", "w") as f:
                f.write('{"_meta": {"version": "1.0"}}\n')
            with open("jig/generated/verification-graph.ndjson", "w") as f:
                f.write('{"_meta": {"version": "1.0"}}\n')

            result = runner.invoke(cli, ["--no-rebuild", "context", "invalid-thing"])

            # Graceful fallback: exit 0 with overview + note
            assert result.exit_code == 0
            assert "Note:" in result.output
            assert "invalid-thing" in result.output


@pytest.fixture
def sample_project(tmp_path):
    """Create a minimal JIG project for CLI tests."""
    # Just return tmp_path, actual setup done in each test
    return tmp_path


@pytest.fixture
def context_project(tmp_path):
    """Create a JIG project with graphs in jig/generated/ for context_command tests."""
    import os

    generated_dir = tmp_path / "jig" / "generated"
    os.makedirs(generated_dir, exist_ok=True)

    # Intent graph with Charter -> Goal -> Outcome -> Spec hierarchy
    intent_nodes = [
        {"_meta": {"version": "2.0"}},
        {"id": "Charter", "type": "charter", "file": "jig/Charter.md", "goals": ["G-001"]},
        {"id": "G-001", "type": "goal", "title": "Test Goal", "file": "jig/Charter.md"},
        {
            "id": "A-001",
            "type": "architecture",
            "title": "Test Arch",
            "file": "jig/architecture/A-001.md",
            "goals": ["G-001"],
            "specifications": ["S-001"],
        },
        {
            "id": "O-001",
            "type": "outcome",
            "title": "Test Outcome",
            "file": "jig/outcomes/O-001.md",
            "goals": ["G-001"],
            "specifications": ["S-001"],
        },
        {"id": "S-001", "type": "specification", "file": "jig/specifications/S-001.md"},
        {"id": "B-cli", "type": "brick", "name": "CLI", "layer": 1, "file": "jig/bricks.yaml"},
    ]
    intent_edges = [
        {"source": "Charter", "target": "G-001", "type": "defines_goal"},
        {"source": "O-001", "target": "G-001", "type": "supports_goal"},
        {"source": "O-001", "target": "S-001", "type": "specifies"},
        {"source": "A-001", "target": "G-001", "type": "supports_goal"},
        {"source": "A-001", "target": "S-001", "type": "specifications"},
    ]

    with open(generated_dir / "intent-graph.ndjson", "w") as f:
        for item in intent_nodes + intent_edges:
            f.write(json.dumps(item) + "\n")

    # Implementation graph with functions
    impl_nodes = [
        {"_meta": {"version": "1.0"}},
        {
            "id": "F-jig.cli.main.run",
            "type": "function",
            "file": "src/jig/cli/main.py",
            "name": "run",
            "implements": ["S-001"],
        },
    ]
    impl_edges = [
        {"source": "F-jig.cli.main.run", "target": "S-001", "type": "implements"},
    ]

    with open(generated_dir / "implementation-graph.ndjson", "w") as f:
        for item in impl_nodes + impl_edges:
            f.write(json.dumps(item) + "\n")

    # Verification graph
    with open(generated_dir / "verification-graph.ndjson", "w") as f:
        f.write('{"_meta": {"version": "1.0"}}\n')

    return tmp_path


@pytest.fixture
def context_project_full(tmp_path):
    """Create a full JIG project with actual files for overview testing."""
    import os

    jig_dir = tmp_path / "jig"
    generated_dir = jig_dir / "generated"
    specs_dir = jig_dir / "specifications"
    outcomes_dir = jig_dir / "outcomes"

    os.makedirs(generated_dir, exist_ok=True)
    os.makedirs(specs_dir, exist_ok=True)
    os.makedirs(outcomes_dir, exist_ok=True)

    # Create jig.toml
    (tmp_path / "jig.toml").write_text('[jig]\nversion = "0.1.0"\n')

    # Create Charter
    (jig_dir / "Charter_Test.md").write_text("""---
id: Charter
type: charter
goals: [G-001]
---

# Test Project

## G-001: Test Goal

A test goal.
""")

    # Create spec
    (specs_dir / "S-001_Test_Spec.md").write_text("""---
id: S-001
title: Test Spec
type: specification
outcomes: [O-001]
---

# Test Spec
""")

    # Create outcome
    (outcomes_dir / "O-001_Test_Outcome.md").write_text("""---
id: O-001
title: Test Outcome
type: outcome
goals: [G-001]
specifications: [S-001]
---

# Test Outcome
""")

    # Create bricks.yaml
    (jig_dir / "bricks.yaml").write_text("""bricks:
  - id: B-core
    name: Core
    layer: 0
    units:
      - M-core.utils
""")

    # Intent graph
    intent_nodes = [
        {"_meta": {"version": "2.0"}},
        {"id": "Charter", "type": "charter", "file": "jig/Charter_Test.md"},
        {"id": "G-001", "type": "goal", "title": "Test Goal"},
        {"id": "O-001", "type": "outcome", "title": "Test Outcome"},
        {"id": "S-001", "type": "specification", "title": "Test Spec"},
    ]
    intent_edges = [
        {"source": "Charter", "target": "G-001", "type": "defines_goal"},
        {"source": "O-001", "target": "G-001", "type": "supports_goal"},
        {"source": "O-001", "target": "S-001", "type": "specifies"},
    ]

    with open(generated_dir / "intent-graph.ndjson", "w") as f:
        for item in intent_nodes + intent_edges:
            f.write(json.dumps(item) + "\n")

    # Implementation graph
    impl_items = [
        {"_meta": {"version": "1.0"}},
        {"id": "F-core.utils.helper", "type": "function"},
        {"source": "F-core.utils.helper", "target": "S-001", "type": "implements"},
    ]
    with open(generated_dir / "implementation-graph.ndjson", "w") as f:
        for item in impl_items:
            f.write(json.dumps(item) + "\n")

    # Verification graph
    verify_items = [
        {"_meta": {"version": "1.0"}},
        {"id": "T-test.test_helper", "type": "test"},
        {"source": "T-test.test_helper", "target": "S-001", "type": "verifies"},
    ]
    with open(generated_dir / "verification-graph.ndjson", "w") as f:
        for item in verify_items:
            f.write(json.dumps(item) + "\n")

    return tmp_path
