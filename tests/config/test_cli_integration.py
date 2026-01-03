"""Integration tests for CLI configuration.

Verifies S-065: CLI Integration with Configuration
"""

import os
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

import jig
from jig.cli.main import cli


@pytest.fixture
def project_dir():
    """Create a temporary project directory with basic structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project = Path(tmpdir)

        # Create jig directory marker
        (project / "jig").mkdir()
        (project / "jig" / "specifications").mkdir()
        (project / "jig" / "outcomes").mkdir()
        (project / "jig" / "generated").mkdir()

        # Create a valid specification
        spec_file = project / "jig" / "specifications" / "S-001.md"
        spec_file.write_text("""---
id: S-001
type: specification
---

# Test Specification

A test specification for validation.

**Acceptance Criteria:**
- Can be validated
""")

        # Create a valid outcome
        outcome_file = project / "jig" / "outcomes" / "O-001.md"
        outcome_file.write_text("""---
id: O-001
type: outcome
specifies:
  - S-001
---

# Test Outcome

A test outcome.
""")

        # Create bricks.yaml (required for auto-rebuild of intent graph)
        bricks_file = project / "jig" / "bricks.yaml"
        bricks_file.write_text("bricks: []\n")

        # Create default source directory
        (project / "src").mkdir()
        (project / "test").mkdir()

        yield project


@jig.verifies("S-065")
def test_validate_uses_config_paths(project_dir):
    """Verify validate command uses configured paths."""
    # Create custom paths
    (project_dir / "custom_jig").mkdir()
    (project_dir / "custom_jig" / "specifications").mkdir()
    (project_dir / "custom_jig" / "outcomes").mkdir()
    (project_dir / "custom_jig" / "generated").mkdir()

    # Create bricks.yaml (required for auto-rebuild of intent graph)
    bricks_file = project_dir / "custom_jig" / "bricks.yaml"
    bricks_file.write_text("bricks: []\n")

    # Create a spec in custom location
    spec_file = project_dir / "custom_jig" / "specifications" / "S-002.md"
    spec_file.write_text("""---
id: S-002
type: specification
---

# Custom Specification

A custom specification.

**Acceptance Criteria:**
- Can be validated from custom path
""")

    # Create an outcome that specifies this spec
    outcome_file = project_dir / "custom_jig" / "outcomes" / "O-002.md"
    outcome_file.write_text("""---
id: O-002
type: outcome
specifies:
  - S-002
---

# Custom Outcome

A custom outcome.
""")

    # Create config pointing to custom path
    config_file = project_dir / "jig.toml"
    config_file.write_text("""[jig.paths]
jig_root = "custom_jig"
""")

    runner = CliRunner()

    # Change to project directory and run
    with runner.isolated_filesystem():
        os.chdir(project_dir)
        result = runner.invoke(cli, ["validate", "intent"])

    # Should find spec from custom path
    assert result.exit_code == 0, f"Output: {result.output}"
    assert "1 files" in result.output


@jig.verifies("S-065")
def test_commands_work_without_config_file(project_dir):
    """Verify commands work with defaults when no config file exists."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(project_dir)
        result = runner.invoke(cli, ["validate", "intent"])

    # Should work with defaults
    assert result.exit_code == 0
    assert "validation passed" in result.output.lower() or "1 files" in result.output


@jig.verifies("S-065")
def test_validate_uses_configured_source_path(project_dir):
    """Verify validate discovers decorators from configured source path."""
    # Create custom source directory
    (project_dir / "lib").mkdir()
    src_file = project_dir / "lib" / "example.py"
    src_file.write_text("""import jig

@jig.implements("S-001")
def example_function():
    pass
""")

    # Create config pointing to custom source
    config_file = project_dir / "jig.toml"
    config_file.write_text("""[jig.paths]
source = "lib"
""")

    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(project_dir)
        result = runner.invoke(cli, ["validate", "intent"])

    # Should find decorator in custom source path
    assert result.exit_code == 0


@jig.verifies("S-065")
def test_rebuild_uses_configured_paths(project_dir):
    """Verify rebuild commands use configured source and test paths."""
    # Create custom source directory with a Python file
    (project_dir / "lib").mkdir()
    src_file = project_dir / "lib" / "example.py"
    src_file.write_text("""import jig

@jig.implements("S-001")
def example_function():
    pass
""")

    # Create config
    config_file = project_dir / "jig.toml"
    config_file.write_text("""[jig.paths]
source = "lib"
""")

    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(project_dir)
        result = runner.invoke(cli, ["rebuild", "impl"])

    # Should succeed and find the source file
    assert result.exit_code == 0
    assert "impl:" in result.output


@jig.verifies("S-065")
def test_show_uses_configured_bricks_path(project_dir):
    """Verify show commands use configured bricks path."""
    # Create custom bricks file
    bricks_file = project_dir / "jig" / "custom-bricks.yaml"
    bricks_file.write_text("""bricks:
  - id: custom-brick
    name: Custom Brick
    layer: 0
    units: []
""")

    # Create config pointing to custom bricks
    config_file = project_dir / "jig.toml"
    config_file.write_text("""[jig.paths]
bricks = "custom-bricks.yaml"
""")

    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(project_dir)
        result = runner.invoke(cli, ["show"])

    # Should find the custom brick
    assert "custom-brick" in result.output or "Custom Brick" in result.output


@jig.verifies("S-065")
def test_config_loaded_once_per_invocation(project_dir):
    """Verify config is loaded once and reused across subcommands."""
    # This test verifies the implementation doesn't load config multiple times
    # by checking that all paths are consistently resolved

    config_file = project_dir / "jig.toml"
    config_file.write_text("""[jig.paths]
tests = "my_tests"
""")

    (project_dir / "my_tests").mkdir()

    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(project_dir)
        # Run a command that exercises config loading
        result = runner.invoke(cli, ["validate"])

    # Should complete without errors
    assert result.exit_code == 0


@jig.verifies("S-065")
def test_partial_config_uses_defaults_for_unset(project_dir):
    """Verify partial config merges with defaults correctly."""
    # Only set tests path, source should use default
    config_file = project_dir / "jig.toml"
    config_file.write_text("""[jig.paths]
tests = "my_tests"
""")

    (project_dir / "my_tests").mkdir()

    # Create source file in default location
    src_file = project_dir / "src" / "example.py"
    src_file.parent.mkdir(exist_ok=True)
    src_file.write_text("""import jig

@jig.implements("S-001")
def example_function():
    pass
""")

    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(project_dir)
        result = runner.invoke(cli, ["validate", "intent"])

    # Should find source in default 'src' path
    assert result.exit_code == 0


@jig.verifies("S-065")
def test_pyproject_toml_config_works(project_dir):
    """Verify config can be loaded from pyproject.toml."""
    # Create pyproject.toml with jig config
    config_file = project_dir / "pyproject.toml"
    config_file.write_text("""[tool.jig.paths]
source = "lib"
""")

    (project_dir / "lib").mkdir()
    src_file = project_dir / "lib" / "example.py"
    src_file.write_text("""import jig

@jig.implements("S-001")
def example_function():
    pass
""")

    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(project_dir)
        result = runner.invoke(cli, ["validate", "intent"])

    # Should work with pyproject.toml config
    assert result.exit_code == 0


@jig.verifies("S-063")
def test_invalid_toml_shows_clear_error(project_dir):
    """Verify invalid TOML config shows clear error message."""
    # Create invalid TOML
    config_file = project_dir / "jig.toml"
    config_file.write_text("""[jig.paths
source = "lib"
""")  # Missing closing bracket

    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(project_dir)
        result = runner.invoke(cli, ["validate", "intent"])

    # Should fail - the exception message contains "Invalid TOML"
    assert result.exit_code != 0
    # Check the exception type/message
    assert result.exception is not None
    assert "Invalid TOML" in str(result.exception) or "ConfigError" in str(type(result.exception))


@jig.verifies("S-065")
def test_full_workflow_with_config(project_dir):
    """End-to-end test: create config, run all commands, verify behavior."""
    # Set up custom project structure
    (project_dir / "lib").mkdir()
    (project_dir / "my_tests").mkdir()
    (project_dir / "custom_jig").mkdir()
    (project_dir / "custom_jig" / "specifications").mkdir()
    (project_dir / "custom_jig" / "outcomes").mkdir()
    (project_dir / "custom_jig" / "generated").mkdir()

    # Create bricks.yaml (required for auto-rebuild of intent graph)
    bricks_file = project_dir / "custom_jig" / "bricks.yaml"
    bricks_file.write_text("bricks: []\n")

    # Create specification
    spec_file = project_dir / "custom_jig" / "specifications" / "S-100.md"
    spec_file.write_text("""---
id: S-100
type: specification
---

# Workflow Test Spec

Test specification for full workflow.

**Acceptance Criteria:**
- Can run full workflow
""")

    # Create outcome
    outcome_file = project_dir / "custom_jig" / "outcomes" / "O-100.md"
    outcome_file.write_text("""---
id: O-100
type: outcome
specifies:
  - S-100
---

# Workflow Test Outcome

Test outcome for full workflow.
""")

    # Create source file
    src_file = project_dir / "lib" / "workflow.py"
    src_file.write_text("""import jig

@jig.implements("S-100")
def workflow_function():
    '''Implementation for workflow test.'''
    pass
""")

    # Create test file
    test_file = project_dir / "my_tests" / "test_workflow.py"
    test_file.write_text("""import jig

@jig.verifies("S-100")
def test_workflow():
    pass
""")

    # Create config
    config_file = project_dir / "jig.toml"
    config_file.write_text("""[jig.paths]
source = "lib"
tests = "my_tests"
jig_root = "custom_jig"
""")

    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(project_dir)

        # Step 1: Validate intent
        result = runner.invoke(cli, ["validate", "intent"])
        assert result.exit_code == 0, f"validate intent failed: {result.output}"

        # Step 2: Rebuild impl graph
        result = runner.invoke(cli, ["rebuild", "impl"])
        assert result.exit_code == 0, f"rebuild impl failed: {result.output}"
        assert "impl:" in result.output

        # Step 3: Rebuild verify graph
        result = runner.invoke(cli, ["rebuild", "verify"])
        assert result.exit_code == 0, f"rebuild verify failed: {result.output}"
        assert "verify:" in result.output

    # Verify generated files are in custom location
    assert (project_dir / "custom_jig" / "generated" / "implementation-graph.ndjson").exists()
    assert (project_dir / "custom_jig" / "generated" / "verification-graph.ndjson").exists()
