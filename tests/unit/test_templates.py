"""Tests for JIG scaffold templates.

Verifies that all template constants are valid and parseable.
These templates are used by `jigy init` to scaffold new JIG projects.
"""

import tomllib

import yaml

import jig
from jig.templates import (
    BRICKS_YAML_TEMPLATE,
    CHARTER_MD_TEMPLATE,
    CONTEXT_JIG_MD_TEMPLATE,
    JIG_TOML_TEMPLATE,
    SKILL_MD_TEMPLATE,
)


class TestJigTomlTemplate:
    """Tests for S-097: jig.toml template structure."""

    @jig.verifies("S-097")
    def test_valid_toml_syntax(self):
        """Template parses as valid TOML."""
        parsed = tomllib.loads(JIG_TOML_TEMPLATE)
        assert isinstance(parsed, dict)

    @jig.verifies("S-097")
    def test_has_integration_section(self):
        """Template contains [integration] section."""
        parsed = tomllib.loads(JIG_TOML_TEMPLATE)
        assert "integration" in parsed
        assert isinstance(parsed["integration"], dict)

    @jig.verifies("S-097")
    def test_has_scan_section(self):
        """Template contains [scan] section."""
        parsed = tomllib.loads(JIG_TOML_TEMPLATE)
        assert "scan" in parsed
        assert isinstance(parsed["scan"], dict)

    @jig.verifies("S-097")
    def test_scan_has_ignore_list(self):
        """Scan section has ignore list with common directories."""
        parsed = tomllib.loads(JIG_TOML_TEMPLATE)
        ignore_list = parsed["scan"]["ignore"]
        assert isinstance(ignore_list, list)
        # Should include common ignore patterns
        assert ".venv/" in ignore_list
        assert "__pycache__/" in ignore_list


class TestCharterMdTemplate:
    """Tests for S-098: Charter.md template structure."""

    @jig.verifies("S-098")
    def test_has_yaml_frontmatter(self):
        """Template contains valid YAML frontmatter."""
        # Extract frontmatter between --- markers
        lines = CHARTER_MD_TEMPLATE.strip().split("\n")
        assert lines[0] == "---"

        # Find closing ---
        end_idx = None
        for i, line in enumerate(lines[1:], 1):
            if line == "---":
                end_idx = i
                break

        assert end_idx is not None, "No closing --- found"
        frontmatter = "\n".join(lines[1:end_idx])
        parsed = yaml.safe_load(frontmatter)
        assert isinstance(parsed, dict)

    @jig.verifies("S-098")
    def test_frontmatter_has_required_fields(self):
        """Frontmatter has id, type, and goals fields."""
        lines = CHARTER_MD_TEMPLATE.strip().split("\n")
        end_idx = next(i for i, line in enumerate(lines[1:], 1) if line == "---")
        frontmatter = "\n".join(lines[1:end_idx])
        parsed = yaml.safe_load(frontmatter)

        assert parsed["id"] == "Charter"
        assert parsed["type"] == "charter"
        assert "goals" in parsed
        assert "G-1" in parsed["goals"]

    @jig.verifies("S-098")
    def test_has_h1_charter_heading(self):
        """Template has # Charter heading."""
        assert "# Charter" in CHARTER_MD_TEMPLATE

    @jig.verifies("S-098")
    def test_has_g1_placeholder(self):
        """Template has G-1 goal placeholder section."""
        assert "G-1" in CHARTER_MD_TEMPLATE


class TestBricksYamlTemplate:
    """Tests for S-099: bricks.yaml template structure."""

    @jig.verifies("S-099")
    def test_valid_yaml_syntax(self):
        """Template parses as valid YAML."""
        parsed = yaml.safe_load(BRICKS_YAML_TEMPLATE)
        assert isinstance(parsed, dict)

    @jig.verifies("S-099")
    def test_has_bricks_key(self):
        """Template has 'bricks' key."""
        parsed = yaml.safe_load(BRICKS_YAML_TEMPLATE)
        assert "bricks" in parsed

    @jig.verifies("S-099")
    def test_bricks_is_empty_list(self):
        """Bricks value is empty list."""
        parsed = yaml.safe_load(BRICKS_YAML_TEMPLATE)
        assert parsed["bricks"] == []


class TestSkillMdTemplate:
    """Tests for S-101: SKILL.md template structure."""

    @jig.verifies("S-101")
    def test_has_yaml_frontmatter(self):
        """Template contains valid YAML frontmatter."""
        lines = SKILL_MD_TEMPLATE.strip().split("\n")
        assert lines[0] == "---"

        end_idx = next(i for i, line in enumerate(lines[1:], 1) if line == "---")
        frontmatter = "\n".join(lines[1:end_idx])
        parsed = yaml.safe_load(frontmatter)
        assert isinstance(parsed, dict)

    @jig.verifies("S-101")
    def test_frontmatter_has_name_and_description(self):
        """Frontmatter has name and description fields."""
        lines = SKILL_MD_TEMPLATE.strip().split("\n")
        end_idx = next(i for i, line in enumerate(lines[1:], 1) if line == "---")
        frontmatter = "\n".join(lines[1:end_idx])
        parsed = yaml.safe_load(frontmatter)

        assert parsed["name"] == "jig"
        assert "description" in parsed
        assert isinstance(parsed["description"], str)

    @jig.verifies("S-101")
    def test_has_jig_heading(self):
        """Template has # jig heading."""
        assert "# jig" in SKILL_MD_TEMPLATE

    @jig.verifies("S-101")
    def test_has_bootstrap_section(self):
        """Template has Bootstrap section."""
        assert "## Bootstrap" in SKILL_MD_TEMPLATE

    @jig.verifies("S-101")
    def test_has_cli_commands_section(self):
        """Template has CLI Commands section."""
        assert "## CLI Commands" in SKILL_MD_TEMPLATE

    @jig.verifies("S-101")
    def test_has_workflows_section(self):
        """Template has Workflows section."""
        assert "## Workflows" in SKILL_MD_TEMPLATE

    @jig.verifies("S-101")
    def test_references_contextjig(self):
        """Template references contextJIG.md."""
        assert "contextJIG.md" in SKILL_MD_TEMPLATE


class TestContextJigMdTemplate:
    """Tests for contextJIG.md template content."""

    @jig.verifies("S-097")
    def test_is_non_empty(self):
        """Template is non-empty string."""
        assert isinstance(CONTEXT_JIG_MD_TEMPLATE, str)
        assert len(CONTEXT_JIG_MD_TEMPLATE) > 100

    @jig.verifies("S-097")
    def test_has_jig_context_heading(self):
        """Template has JIG Context heading."""
        assert "# JIG Context" in CONTEXT_JIG_MD_TEMPLATE

    @jig.verifies("S-097")
    def test_has_gaosct_pyramid(self):
        """Template explains the G-A-O-S-C-T pyramid."""
        assert "G-A-O-S-C-T" in CONTEXT_JIG_MD_TEMPLATE

    @jig.verifies("S-097")
    def test_has_decorator_syntax(self):
        """Template shows decorator syntax."""
        assert "@jig.implements" in CONTEXT_JIG_MD_TEMPLATE
        assert "@jig.verifies" in CONTEXT_JIG_MD_TEMPLATE

    @jig.verifies("S-097")
    def test_has_brick_layer_model(self):
        """Template explains bricks and layers."""
        assert "Layer" in CONTEXT_JIG_MD_TEMPLATE
        assert "Brick" in CONTEXT_JIG_MD_TEMPLATE
