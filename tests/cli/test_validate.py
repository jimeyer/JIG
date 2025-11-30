"""
Tests for validate CLI commands.
"""

import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

import jig
from jig.cli.main import cli


@jig.verifies("S-023")
def test_validate_intent_success():
    """jigy validate intent passes with valid artifacts."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid spec
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        result = runner.invoke(cli, ["validate", "intent", "--project-root", "."])
        assert result.exit_code == 0
        assert "specifications" in result.output.lower()


@jig.verifies("S-023")
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

        result = runner.invoke(cli, ["validate", "intent", "--project-root", "."])
        assert result.exit_code == 1  # Validation failure
        assert "error" in result.output.lower() or "✗" in result.output


@jig.verifies("S-023")
def test_validate_intent_exit_codes():
    """jigy validate intent uses correct exit codes."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)

        # Success: exit code 0
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        result = runner.invoke(cli, ["validate", "intent", "--project-root", "."])
        assert result.exit_code == 0


@jig.verifies("S-024")
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
            """
- id: B-001
  name: Test
  units:
    - M-test
"""
        )

        result = runner.invoke(cli, ["validate", "bricks", "--project-root", "."])
        assert result.exit_code == 0
        assert "brick" in result.output.lower()


@jig.verifies("S-024")
def test_validate_bricks_missing_graph():
    """jigy validate bricks errors if implementation graph missing."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create bricks but no graph
        Path("jig").mkdir()
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-001
  name: Test
  units:
    - M-test
"""
        )

        result = runner.invoke(cli, ["validate", "bricks", "--project-root", "."])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "missing" in result.output.lower()


@jig.verifies("S-024")
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
            """- id: B-001
  name: Empty
  units: []
"""
        )

        result = runner.invoke(cli, ["validate", "bricks", "--project-root", "."])
        assert result.exit_code == 1
        assert "gap" in result.output.lower() or "0 bricks" in result.output.lower()


@jig.verifies("S-025")
def test_validate_full_success():
    """jigy validate runs both intent and brick validation."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid spec
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-test.func", "type": "function"}) + "\n"
        )

        # Create valid bricks
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-001
  name: Test
  units:
    - F-test.func
"""
        )

        result = runner.invoke(cli, ["validate", "--project-root", "."])
        assert result.exit_code == 0
        # Should run both validations
        assert "intent" in result.output.lower() or "specification" in result.output.lower()
        assert "brick" in result.output.lower()


@jig.verifies("S-025")
def test_validate_full_skips_bricks_if_no_graph():
    """jigy validate gracefully skips brick validation if no graph."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid spec only (no graph)
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        result = runner.invoke(cli, ["validate", "--project-root", "."])
        # Should succeed (intent validation passes, brick validation skipped)
        assert result.exit_code == 0


@jig.verifies("S-025")
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

        result = runner.invoke(cli, ["validate", "--project-root", "."])
        assert result.exit_code == 1


@jig.verifies("S-027")
def test_impl_rebuild_auto_validates():
    """jigy impl rebuild auto-validates decorators before building."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create invalid decorator (references non-existent spec)
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)

        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "module.py").write_text(
            '''import jig

@jig.implements("S-999")  # Non-existent spec
def my_function():
    pass
'''
        )

        result = runner.invoke(cli, ["impl", "rebuild", "--project-root", "."])
        # Should fail validation before building graph
        assert result.exit_code == 1
        assert "S-999" in result.output or "validation" in result.output.lower()


@jig.verifies("S-027")
def test_impl_rebuild_skip_validation():
    """jigy impl rebuild --skip-validation bypasses validation."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create invalid decorator
        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "module.py").write_text(
            '''import jig

@jig.implements("S-999")  # Non-existent spec
def my_function():
    pass
'''
        )

        result = runner.invoke(cli, ["impl", "rebuild", "--skip-validation", "--project-root", "."])
        # Should succeed (validation skipped)
        assert result.exit_code == 0 or "successfully" in result.output.lower()


@jig.verifies("S-027")
def test_impl_rebuild_validates_only_decorators():
    """jigy impl rebuild validates decorators, not all intent."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create invalid spec file (but valid decorators)
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
type: specification
---

# Missing id - invalid spec!
"""
        )

        # Create valid code with valid decorator
        (spec_dir / "S-002.md").write_text(
            """---
id: S-002
type: specification
---

# Valid
"""
        )

        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "module.py").write_text(
            '''import jig

@jig.implements("S-002")  # Valid decorator
def my_function():
    pass
'''
        )

        result = runner.invoke(cli, ["impl", "rebuild", "--project-root", "."])
        # Should succeed (only validates decorators, not spec files)
        assert result.exit_code == 0


@jig.verifies("S-026")
def test_validate_intent_json_format():
    """jigy validate intent --format json produces valid JSON."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create valid spec
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
id: S-001
type: specification
---

# Test
"""
        )

        result = runner.invoke(cli, ["validate", "intent", "--project-root", ".", "--format", "json"])
        assert result.exit_code == 0

        # Should be valid JSON
        data = json.loads(result.output)
        assert "status" in data
        assert "summary" in data
        assert data["status"] == "passed"


@jig.verifies("S-026")
def test_validate_bricks_json_format():
    """jigy validate bricks --format json produces valid JSON."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create implementation graph
        graph_dir = Path("jig/generated")
        graph_dir.mkdir(parents=True)
        graph_file = graph_dir / "implementation-graph.ndjson"
        graph_file.write_text(
            json.dumps({"id": "F-test.func", "type": "function"}) + "\n"
        )

        # Create valid bricks
        (Path("jig") / "bricks.yaml").write_text(
            """- id: B-001
  name: Test
  units:
    - F-test.func
"""
        )

        result = runner.invoke(cli, ["validate", "bricks", "--project-root", ".", "--format", "json"])
        assert result.exit_code == 0

        # Should be valid JSON
        data = json.loads(result.output)
        assert "status" in data
        assert data["status"] == "passed"


@jig.verifies("S-026")
def test_validate_json_format_with_errors():
    """jigy validate --format json includes structured errors."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create invalid spec
        spec_dir = Path("jig/specifications")
        spec_dir.mkdir(parents=True)
        (spec_dir / "S-001.md").write_text(
            """---
type: specification
---

# Missing id
"""
        )

        result = runner.invoke(cli, ["validate", "intent", "--project-root", ".", "--format", "json"])
        assert result.exit_code == 1

        # Should be valid JSON with errors
        data = json.loads(result.output)
        assert data["status"] == "failed"
        assert data["summary"]["total_errors"] > 0
        # Should have error details
        assert len(data["intent"]["errors"]) > 0
        error = data["intent"]["errors"][0]
        assert "code" in error
        assert "message" in error
        assert "file" in error
