"""
Tests for validate CLI commands.
"""

import json
from pathlib import Path

from click.testing import CliRunner

import jig
from jig.cli.main import cli


def _create_valid_spec_with_outcome(base_path: Path = None):
    """Helper to create a valid spec with a covering outcome."""
    base = base_path or Path(".")
    spec_dir = base / "jig/specifications"
    spec_dir.mkdir(parents=True, exist_ok=True)
    outcome_dir = base / "jig/outcomes"
    outcome_dir.mkdir(parents=True, exist_ok=True)

    (spec_dir / "S-001_Test_Specification.md").write_text(
        """---
id: S-001
type: specification
title: Test Specification
outcomes: [O-001]
---

# Test Specification
"""
    )

    (outcome_dir / "O-001_Test_Outcome.md").write_text(
        """---
id: O-001
type: outcome
title: Test Outcome
specifications: [S-001]
---

# Test Outcome
"""
    )


@jig.verifies("S-023")
@jig.verifies("S-061")
def test_validate_intent_success():
    """jigy validate intent passes with valid artifacts."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _create_valid_spec_with_outcome()

        result = runner.invoke(cli, ["validate", "intent"])
        assert result.exit_code == 0
        # New engine outputs "Validation passed." on success
        assert "passed" in result.output.lower() or "validation" in result.output.lower()


@jig.verifies("S-023")
@jig.verifies("S-061")
def test_validate_intent_failure():
    """jigy validate intent fails with invalid artifacts."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create invalid spec (missing id)
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
type: specification
---

# Test
"""
        )

        result = runner.invoke(cli, ["validate", "intent"])
        assert result.exit_code == 1  # Validation failure
        assert "error" in result.output.lower() or "✗" in result.output


@jig.verifies("S-023")
@jig.verifies("S-061")
def test_validate_intent_exit_codes():
    """jigy validate intent uses correct exit codes."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _create_valid_spec_with_outcome()

        result = runner.invoke(cli, ["validate", "intent"])
        assert result.exit_code == 0


@jig.verifies("S-024")
@jig.verifies("S-061")
def test_validate_bricks_success():
    """jigy validate bricks passes with valid bricks."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "M-test", "type": "module"}) + "\n"
            + json.dumps({"id": "F-test.func", "type": "function"}) + "\n"
        )

        # Create valid bricks
        (Path("jig") / "bricks.yaml").write_text(
            """bricks:
  - id: B-test
    name: Test
    layer: 0
    units:
      - M-test
"""
        )

        # Use --no-rebuild to skip auto-rebuild (we have mock graphs)
        result = runner.invoke(cli, ["--no-rebuild", "validate", "bricks"])
        assert result.exit_code == 0
        # New engine outputs "Validation passed." on success
        assert "passed" in result.output.lower()


@jig.verifies("S-024")
@jig.verifies("S-061")
def test_validate_bricks_missing_graph():
    """jigy validate bricks errors if implementation graph missing."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create bricks but no graph
        Path("jig").mkdir()
        (Path("jig") / "bricks.yaml").write_text(
            """bricks:
  - id: B-test
    name: Test
    layer: 0
    units:
      - M-test
"""
        )

        # Use --no-rebuild to prevent auto-rebuild from creating the graph
        result = runner.invoke(cli, ["--no-rebuild", "validate", "bricks"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()


@jig.verifies("S-024")
@jig.verifies("S-061")
def test_validate_bricks_partition_gap():
    """jigy validate bricks detects partition gaps."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph with function
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-test.func", "type": "function"}) + "\n"
        )

        # Create bricks that don't include the function (gap)
        (Path("jig") / "bricks.yaml").write_text(
            """bricks:
  - id: B-empty
    name: Empty
    layer: 0
    units: []
"""
        )

        # Use --no-rebuild to skip auto-rebuild (we have mock graphs)
        result = runner.invoke(cli, ["--no-rebuild", "validate", "bricks"])
        assert result.exit_code == 1
        assert "gap" in result.output.lower() or "0 bricks" in result.output.lower()


@jig.verifies("S-025")
@jig.verifies("S-061")
def test_validate_full_success():
    """jigy validate runs both intent and brick validation."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid spec with outcome
        _create_valid_spec_with_outcome()

        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-test.func", "type": "function"}) + "\n"
        )

        # Create valid bricks
        (Path("jig") / "bricks.yaml").write_text(
            """bricks:
  - id: B-test
    name: Test
    layer: 0
    units:
      - F-test.func
"""
        )

        # Use --no-rebuild to skip auto-rebuild (we have mock graphs)
        result = runner.invoke(cli, ["--no-rebuild", "validate"])
        assert result.exit_code == 0
        # Per S-025, full validation outputs "Validated X specs, Y outcomes, Z bricks."
        assert "validated" in result.output.lower()
        assert "specs" in result.output.lower()
        assert "outcomes" in result.output.lower()
        assert "bricks" in result.output.lower()


@jig.verifies("S-025")
@jig.verifies("S-061")
def test_validate_full_skips_bricks_if_no_graph():
    """jigy validate gracefully skips brick validation if no graph."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid spec with outcome (no impl graph)
        _create_valid_spec_with_outcome()

        # Use --no-rebuild to skip auto-rebuild (testing graph-less behavior)
        result = runner.invoke(cli, ["--no-rebuild", "validate"])
        # Should succeed (intent validation passes, brick validation skipped)
        assert result.exit_code == 0


@jig.verifies("S-025")
@jig.verifies("S-061")
def test_validate_full_fails_on_intent_error():
    """jigy validate fails if intent validation fails."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create invalid spec
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
type: specification
---

# Test (missing id)
"""
        )

        result = runner.invoke(cli, ["validate"])
        assert result.exit_code == 1


@jig.verifies("S-061")
def test_validate_no_project_root_option():
    """jigy validate commands reject --project-root option."""
    runner = CliRunner()

    result = runner.invoke(cli, ["validate", "--project-root", "."])
    assert result.exit_code != 0
    assert "no such option" in result.output.lower()

    result = runner.invoke(cli, ["validate", "intent", "--project-root", "."])
    assert result.exit_code != 0
    assert "no such option" in result.output.lower()

    result = runner.invoke(cli, ["validate", "bricks", "--project-root", "."])
    assert result.exit_code != 0
    assert "no such option" in result.output.lower()


@jig.verifies("S-061")
def test_validate_no_format_option():
    """jigy validate commands reject --format option."""
    runner = CliRunner()

    result = runner.invoke(cli, ["validate", "--format", "json"])
    assert result.exit_code != 0
    assert "no such option" in result.output.lower()

    result = runner.invoke(cli, ["validate", "intent", "--format", "json"])
    assert result.exit_code != 0
    assert "no such option" in result.output.lower()


@jig.verifies("S-061")
def test_validate_not_in_project():
    """jigy validate fails with clear error when not in JIG project."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # No jig/ directory

        result = runner.invoke(cli, ["validate"])
        assert result.exit_code != 0
        assert "Not in a JIG project" in result.output or "jig/ directory" in result.output


@jig.verifies("S-061")
def test_validate_human_output_only():
    """jigy validate produces human-readable output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _create_valid_spec_with_outcome()

        result = runner.invoke(cli, ["validate", "intent"])
        assert result.exit_code == 0

        # Should be human-readable (contains "passed" or "Validation"), not JSON
        assert "passed" in result.output.lower() or "validation" in result.output.lower()
        # Should NOT be parseable as JSON
        try:
            json.loads(result.output)
            assert False, "Output should not be JSON"
        except json.JSONDecodeError:
            pass  # Expected


# ============================================================================
# Output Format Flag Tests (S-026, S-093)
# ============================================================================


def _setup_valid_project(runner):
    """Helper to set up a valid JIG project for output format tests."""
    # Create valid spec with outcome
    _create_valid_spec_with_outcome()

    # Create implementation graph
    graph_dir = Path("jig/generated")
    graph_dir.mkdir(parents=True)
    graph_file = graph_dir / "implementation-graph.ndjson"
    graph_file.write_text(
        json.dumps({"id": "F-test.func", "type": "function"}) + "\n"
    )

    # Create valid bricks
    (Path("jig") / "bricks.yaml").write_text(
        """bricks:
  - id: B-test
    name: Test
    layer: 0
    units:
      - F-test.func
"""
    )


def _setup_invalid_project(runner):
    """Helper to set up an invalid JIG project for error output tests."""
    spec_dir = Path("jig/specifications")
    spec_dir.mkdir(parents=True)
    # Invalid spec: missing id
    (spec_dir / "S-001_Bad.md").write_text(
        """---
type: specification
---

# Test
"""
    )


@jig.verifies("S-026", "S-093")
def test_validate_json_flag():
    """jigy validate -j produces JSON output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "-j"])
        assert result.exit_code == 0

        # Output must be valid JSON with new schema
        data = json.loads(result.output)
        assert "valid" in data
        assert data["valid"] is True
        assert "summary" in data
        assert "errors" in data


@jig.verifies("S-026", "S-093")
def test_validate_intent_json_flag():
    """jigy validate intent -j produces JSON output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "intent", "-j"])
        assert result.exit_code == 0

        # Output must be valid JSON with new schema
        data = json.loads(result.output)
        assert "valid" in data
        assert data["valid"] is True
        assert "summary" in data


@jig.verifies("S-026", "S-093")
def test_validate_bricks_json_flag():
    """jigy validate bricks -j produces JSON output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "bricks", "-j"])
        assert result.exit_code == 0

        # Output must be valid JSON with new schema
        data = json.loads(result.output)
        assert "valid" in data
        assert data["valid"] is True
        assert "summary" in data


@jig.verifies("S-093", "S-094")
def test_validate_markdown_flag():
    """jigy validate -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "-m"])
        assert result.exit_code == 0

        # Output should be markdown with new format
        assert "# JIG Validation:" in result.output
        assert "**Specs:**" in result.output


@jig.verifies("S-093", "S-094")
def test_validate_intent_markdown_flag():
    """jigy validate intent -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "intent", "-m"])
        assert result.exit_code == 0

        # Output should be markdown with new format
        assert "# JIG Validation:" in result.output
        assert "**Specs:**" in result.output


@jig.verifies("S-093", "S-094")
def test_validate_bricks_markdown_flag():
    """jigy validate bricks -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "bricks", "-m"])
        assert result.exit_code == 0

        # Output should be markdown with new format
        assert "# JIG Validation:" in result.output
        assert "**Specs:**" in result.output


@jig.verifies("S-093")
def test_validate_verbose_flag():
    """jigy validate -v produces verbose output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "-v"])
        assert result.exit_code == 0

        # Verbose human output - more detail than non-verbose
        # Just verify it runs without error (verbose mode is format-dependent)


@jig.verifies("S-026", "S-093")
def test_validate_json_verbose_flag():
    """jigy validate -j -v produces verbose JSON output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "-j", "-v"])
        assert result.exit_code == 0

        # Output must be valid JSON with new schema
        data = json.loads(result.output)
        assert "valid" in data


@jig.verifies("S-093", "S-094")
def test_validate_markdown_verbose_flag():
    """jigy validate -m -v produces verbose markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "-m", "-v"])
        assert result.exit_code == 0

        # Verbose markdown should have details section
        assert "# JIG Validation:" in result.output
        assert "## Details" in result.output


@jig.verifies("S-093")
def test_validate_json_markdown_mutual_exclusion():
    """jigy validate -j -m produces clear error message."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "-j", "-m"])
        assert result.exit_code != 0

        # Error message should mention mutual exclusivity
        assert "mutually exclusive" in result.output.lower()


@jig.verifies("S-093")
def test_validate_intent_json_markdown_mutual_exclusion():
    """jigy validate intent -j -m produces clear error message."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "intent", "-j", "-m"])
        assert result.exit_code != 0
        assert "mutually exclusive" in result.output.lower()


@jig.verifies("S-093")
def test_validate_bricks_json_markdown_mutual_exclusion():
    """jigy validate bricks -j -m produces clear error message."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "bricks", "-j", "-m"])
        assert result.exit_code != 0
        assert "mutually exclusive" in result.output.lower()


@jig.verifies("S-026", "S-093")
def test_validate_json_output_is_single_line():
    """jigy validate -j produces single-line JSON (not pretty-printed)."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "-j"])
        assert result.exit_code == 0

        # Output should be single line (no embedded newlines in JSON)
        # Strip trailing newline and check
        output = result.output.strip()
        assert "\n" not in output, "JSON output should be single-line"


@jig.verifies("S-026", "S-093")
def test_validate_json_with_errors():
    """jigy validate -j includes error details in JSON output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_invalid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "intent", "-j"])
        assert result.exit_code == 1

        # Output must be valid JSON with error details
        data = json.loads(result.output)
        assert data["valid"] is False
        assert "errors" in data
        assert len(data["errors"]) > 0


@jig.verifies("S-093", "S-094")
def test_validate_markdown_with_errors():
    """jigy validate -m includes error details in markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_invalid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "intent", "-m"])
        assert result.exit_code == 1

        # Markdown should have errors section
        assert "# JIG Validation: FAILED" in result.output
        assert "## Errors" in result.output


@jig.verifies("S-026", "S-093")
def test_validate_full_json_flag():
    """jigy validate full -j produces JSON output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "full", "-j"])
        assert result.exit_code == 0

        # Output must be valid JSON with new schema
        data = json.loads(result.output)
        assert "valid" in data


@jig.verifies("S-093", "S-094")
def test_validate_full_markdown_flag():
    """jigy validate full -m produces markdown output."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _setup_valid_project(runner)

        result = runner.invoke(cli, ["--no-rebuild", "validate", "full", "-m"])
        assert result.exit_code == 0

        # Output should be markdown with new format
        assert "# JIG Validation:" in result.output
