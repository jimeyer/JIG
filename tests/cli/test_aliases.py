# ABOUTME: Tests for CLI command aliases (S-115).
# ABOUTME: Verifies that hallucinated command names map to core commands.

"""Tests for CLI command aliases (S-115).

S-115: CLI Command Aliases - commonly hallucinated commands map to useful outputs.
"""

import json

import pytest
from click.testing import CliRunner

import jig
from jig.cli.main import cli


class TestGraphAlias:
    """Tests for graph alias → context."""

    @jig.verifies("S-115")
    def test_graph_alias_exists(self):
        """jigy graph command exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ["graph", "--help"])

        assert result.exit_code == 0
        assert "alias" in result.output.lower()

    @jig.verifies("S-115")
    def test_graph_bare_returns_overview(self, alias_project):
        """jigy graph (bare) returns project overview."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--no-rebuild", "graph"], obj={})

        assert result.exit_code == 0
        # Should have overview content
        assert "Goals:" in result.output or "JIG:" in result.output

    @jig.verifies("S-115")
    def test_graph_with_identifier(self, alias_project):
        """jigy graph <id> invokes context with identifier."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--no-rebuild", "graph", "Charter"], obj={})

        assert result.exit_code == 0
        assert "Charter" in result.output


class TestListAlias:
    """Tests for list alias → context."""

    @jig.verifies("S-115")
    def test_list_alias_exists(self):
        """jigy list command exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ["list", "--help"])

        assert result.exit_code == 0
        assert "alias" in result.output.lower()

    @jig.verifies("S-115")
    def test_list_bare_returns_overview(self, alias_project):
        """jigy list (bare) returns project overview."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--no-rebuild", "list"], obj={})

        assert result.exit_code == 0
        assert "Goals:" in result.output or "JIG:" in result.output


class TestShowAlias:
    """Tests for show alias → context."""

    @jig.verifies("S-115")
    def test_show_alias_exists(self):
        """jigy show command exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ["show", "--help"])

        assert result.exit_code == 0
        assert "alias" in result.output.lower()

    @jig.verifies("S-115")
    def test_show_bare_returns_overview(self, alias_project):
        """jigy show (bare) returns project overview."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--no-rebuild", "show"], obj={})

        assert result.exit_code == 0
        assert "Goals:" in result.output or "JIG:" in result.output

    @jig.verifies("S-115")
    def test_show_with_identifier(self, alias_project):
        """jigy show <id> invokes context with identifier."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--no-rebuild", "show", "Charter"], obj={})

        assert result.exit_code == 0
        assert "Charter" in result.output


class TestBricksAlias:
    """Tests for bricks alias → context (bare only)."""

    @jig.verifies("S-115")
    def test_bricks_alias_exists(self):
        """jigy bricks command exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ["bricks", "--help"])

        assert result.exit_code == 0
        assert "alias" in result.output.lower()

    @jig.verifies("S-115")
    def test_bricks_returns_overview(self, alias_project):
        """jigy bricks returns project overview (bare only)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--no-rebuild", "bricks"], obj={})

        assert result.exit_code == 0
        # Should have overview content with bricks
        assert "Bricks" in result.output or "Layer" in result.output


class TestLayersAlias:
    """Tests for layers alias → context (bare only)."""

    @jig.verifies("S-115")
    def test_layers_alias_exists(self):
        """jigy layers command exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ["layers", "--help"])

        assert result.exit_code == 0
        assert "alias" in result.output.lower()

    @jig.verifies("S-115")
    def test_layers_returns_overview(self, alias_project):
        """jigy layers returns project overview (bare only)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--no-rebuild", "layers"], obj={})

        assert result.exit_code == 0
        assert "Layer" in result.output or "Bricks" in result.output


class TestTowersAlias:
    """Tests for towers alias → context (bare only)."""

    @jig.verifies("S-115")
    def test_towers_alias_exists(self):
        """jigy towers command exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ["towers", "--help"])

        assert result.exit_code == 0
        assert "alias" in result.output.lower()

    @jig.verifies("S-115")
    def test_towers_returns_overview(self, alias_project):
        """jigy towers returns project overview (bare only)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--no-rebuild", "towers"], obj={})

        assert result.exit_code == 0
        # Single tower projects show overview
        assert "JIG:" in result.output or "Goals:" in result.output


class TestFixAlias:
    """Tests for fix alias → mend."""

    @jig.verifies("S-115")
    def test_fix_alias_exists(self):
        """jigy fix command exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ["fix", "--help"])

        assert result.exit_code == 0
        assert "alias" in result.output.lower()

    @jig.verifies("S-115")
    def test_fix_supports_dry_run(self, alias_project):
        """jigy fix --dry-run works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["fix", "--dry-run"], obj={})

        # Should succeed (even if nothing to fix)
        assert result.exit_code == 0
        assert "dry" in result.output.lower() or "fixes" in result.output.lower() or "apply" in result.output.lower()

    @jig.verifies("S-115")
    def test_fix_supports_json_output(self, alias_project):
        """jigy fix -j produces JSON."""
        runner = CliRunner()
        result = runner.invoke(cli, ["fix", "--dry-run", "-j"], obj={})

        assert result.exit_code == 0
        # Should be valid JSON
        parsed = json.loads(result.output)
        assert isinstance(parsed, dict)


class TestAliasesInHelp:
    """Tests for alias visibility in help."""

    @jig.verifies("S-115")
    def test_aliases_appear_in_main_help(self):
        """Aliases appear in jigy --help with (alias) marker."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "(alias)" in result.output
        assert "graph" in result.output
        assert "list" in result.output
        assert "bricks" in result.output
        assert "layers" in result.output
        assert "towers" in result.output
        assert "fix" in result.output


@pytest.fixture
def alias_project(tmp_path, monkeypatch):
    """Create a minimal JIG project for alias testing."""
    import os

    # Change to tmp_path
    monkeypatch.chdir(tmp_path)

    jig_dir = tmp_path / "jig"
    generated_dir = jig_dir / "generated"
    specs_dir = jig_dir / "specifications"

    os.makedirs(generated_dir, exist_ok=True)
    os.makedirs(specs_dir, exist_ok=True)

    # jig.toml
    (tmp_path / "jig.toml").write_text('[jig]\nversion = "0.1.0"\n')

    # Charter
    (jig_dir / "Charter_Test.md").write_text("""---
id: Charter
type: charter
goals: [G-001]
---

# Test Project

## G-001: Test Goal

A test goal.
""")

    # bricks.yaml
    (jig_dir / "bricks.yaml").write_text("""bricks:
  - id: B-core
    name: Core
    layer: 0
    units:
      - M-core.utils
""")

    # Intent graph
    intent_content = [
        '{"_meta": {"version": "2.0"}}',
        '{"id": "Charter", "type": "charter", "file": "jig/Charter_Test.md"}',
        '{"id": "G-001", "type": "goal", "title": "Test Goal"}',
        '{"source": "Charter", "target": "G-001", "type": "defines_goal"}',
    ]
    with open(generated_dir / "intent-graph.ndjson", "w") as f:
        f.write("\n".join(intent_content) + "\n")

    # Implementation graph
    with open(generated_dir / "implementation-graph.ndjson", "w") as f:
        f.write('{"_meta": {"version": "1.0"}}\n')

    # Verification graph
    with open(generated_dir / "verification-graph.ndjson", "w") as f:
        f.write('{"_meta": {"version": "1.0"}}\n')

    return tmp_path
