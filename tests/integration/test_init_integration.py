"""Integration tests for jigy init command.

Verifies the SCOPE problem is solved at system boundary:
"jigy init bootstraps a project with idempotent directory/file creation.
One skill (/jig) bootstraps agent awareness"

These tests exercise the full init -> validate cycle as a user would.
"""

import json
import subprocess
import tomllib
from pathlib import Path

import yaml

import jig

# ========================================================================
# End-to-End Integration Tests
# ========================================================================


class TestInitFullCycle:
    """Tests for complete init -> validate cycle."""

    @jig.verifies("S-096", "S-097", "S-098", "S-099", "S-100", "S-101", "S-102", "S-103")
    def test_init_creates_complete_structure(self, tmp_path: Path):
        """jigy init creates complete project structure.

        Verifies the full SCOPE requirement:
        - Directory structure created
        - Configuration files valid
        - Skills installed
        - jigy validate passes
        """
        # Run init command in temp directory
        result = subprocess.run(
            ["jigy", "init", "--project", "testproj"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Init failed: {result.stderr}"

        # Verify directory structure
        assert (tmp_path / "jig").is_dir()
        assert (tmp_path / "jig" / "specifications").is_dir()
        assert (tmp_path / "jig" / "outcomes").is_dir()
        assert (tmp_path / "jig" / "architecture").is_dir()
        assert (tmp_path / "jig" / "generated").is_dir()

        # Verify files exist
        assert (tmp_path / "jig.toml").exists()
        assert (tmp_path / "jig" / "Charter_testproj.md").exists()
        assert (tmp_path / "jig" / "bricks.yaml").exists()
        assert (tmp_path / ".gitignore").exists()

        # Verify skills installed
        assert (tmp_path / ".agent" / "skills" / "jig" / "SKILL.md").exists()
        assert (tmp_path / ".agent" / "skills" / "jig" / "contextJIG.md").exists()

    @jig.verifies("S-097")
    def test_jig_toml_has_correct_sections(self, tmp_path: Path):
        """jig.toml has [integration] and [scan] sections."""
        subprocess.run(
            ["jigy", "init", "--project", "configtest"],
            cwd=tmp_path,
            capture_output=True,
        )

        content = (tmp_path / "jig.toml").read_text()
        parsed = tomllib.loads(content)

        # Verify [integration] section
        assert "integration" in parsed
        assert "include_dig" in parsed["integration"]
        assert isinstance(parsed["integration"]["include_dig"], bool)

        # Verify [scan] section
        assert "scan" in parsed
        assert "ignore" in parsed["scan"]
        assert isinstance(parsed["scan"]["ignore"], list)

    @jig.verifies("S-098")
    def test_charter_has_g1_placeholder(self, tmp_path: Path):
        """Charter has G-1 placeholder as specified in SCOPE."""
        subprocess.run(
            ["jigy", "init", "--project", "chartertest"],
            cwd=tmp_path,
            capture_output=True,
        )

        content = (tmp_path / "jig" / "Charter_chartertest.md").read_text()

        # Charter should have G-1 placeholder
        assert "G-1" in content

    @jig.verifies("S-099")
    def test_bricks_yaml_scaffold(self, tmp_path: Path):
        """bricks.yaml is valid YAML with bricks: []."""
        subprocess.run(
            ["jigy", "init", "--project", "brickstest"],
            cwd=tmp_path,
            capture_output=True,
        )

        content = (tmp_path / "jig" / "bricks.yaml").read_text()
        parsed = yaml.safe_load(content)

        assert "bricks" in parsed
        assert parsed["bricks"] == []


class TestInitValidateCycle:
    """Tests for init followed by validate."""

    @jig.verifies("S-096", "S-102")
    def test_fresh_project_validates_successfully(self, tmp_path: Path):
        """jigy rebuild && jigy validate passes on fresh project.

        This is critical for SCOPE: new projects must be immediately usable.
        """
        # Run init
        init_result = subprocess.run(
            ["jigy", "init", "--project", "validatetest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert init_result.returncode == 0, f"Init failed: {init_result.stderr}"

        # Run rebuild
        rebuild_result = subprocess.run(
            ["jigy", "rebuild"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert rebuild_result.returncode == 0, f"Rebuild failed: {rebuild_result.stderr}"

        # Run validate
        validate_result = subprocess.run(
            ["jigy", "validate"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert validate_result.returncode == 0, f"Validate failed: {validate_result.stderr}"


class TestIdempotentBehavior:
    """Tests for idempotent init behavior."""

    @jig.verifies("S-102")
    def test_second_run_succeeds_with_no_new_files(self, tmp_path: Path):
        """Running jigy init twice succeeds with no new jig/ files on second run."""
        # First run
        result1 = subprocess.run(
            ["jigy", "init", "-j", "--project", "idemtest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert result1.returncode == 0
        output1 = json.loads(result1.stdout)
        assert len(output1["paths_created"]) > 0

        # Second run
        result2 = subprocess.run(
            ["jigy", "init", "-j", "--project", "idemtest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert result2.returncode == 0
        output2 = json.loads(result2.stdout)
        assert output2["success"] is True
        assert len(output2["paths_created"]) == 0, "Second run should create nothing new"

    @jig.verifies("S-102")
    def test_second_run_preserves_user_content(self, tmp_path: Path):
        """Running jigy init twice preserves Charter and bricks.yaml modifications."""
        # First run
        subprocess.run(
            ["jigy", "init", "--project", "preservetest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Modify Charter
        charter_path = tmp_path / "jig" / "Charter_preservetest.md"
        charter_path.write_text("# My Custom Charter\n\nCustom content here.")

        # Modify bricks.yaml
        bricks_path = tmp_path / "jig" / "bricks.yaml"
        bricks_path.write_text("bricks:\n  - id: B-custom\n    name: Custom Brick\n    layer: 0\n")

        # Second run
        result = subprocess.run(
            ["jigy", "init", "--project", "preservetest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )
        assert result.returncode == 0

        # Verify content preserved
        assert "Custom content" in charter_path.read_text()
        assert "B-custom" in bricks_path.read_text()


class TestSkillsInstallation:
    """Tests for skill installation behavior."""

    @jig.verifies("S-101")
    def test_skills_installed_by_default(self, tmp_path: Path):
        """jigy init installs skills by default."""
        subprocess.run(
            ["jigy", "init", "--project", "skillstest"],
            cwd=tmp_path,
            capture_output=True,
        )

        skill_path = tmp_path / ".agent" / "skills" / "jig" / "SKILL.md"
        context_path = tmp_path / ".agent" / "skills" / "jig" / "contextJIG.md"

        assert skill_path.exists()
        assert context_path.exists()

    @jig.verifies("S-101", "S-103")
    def test_no_skills_flag_skips_installation(self, tmp_path: Path):
        """--no-skills flag prevents skill installation."""
        subprocess.run(
            ["jigy", "init", "--project", "noskillstest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )

        # jig/ should exist
        assert (tmp_path / "jig").is_dir()
        # Skills should NOT exist
        assert not (tmp_path / ".agent" / "skills" / "jig").exists()

    @jig.verifies("S-101", "S-103")
    def test_skills_only_flag(self, tmp_path: Path):
        """--skills-only installs only skills, not jig/ structure."""
        subprocess.run(
            ["jigy", "init", "--skills-only"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Skills should exist
        assert (tmp_path / ".agent" / "skills" / "jig" / "SKILL.md").exists()
        # jig/ should NOT exist
        assert not (tmp_path / "jig").exists()
        assert not (tmp_path / "jig.toml").exists()

    @jig.verifies("S-101")
    def test_skills_always_overwritten(self, tmp_path: Path):
        """Skills are always overwritten on re-init."""
        from jig.templates import SKILL_MD_TEMPLATE

        # First install
        subprocess.run(
            ["jigy", "init", "--skills-only"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Modify skill
        skill_path = tmp_path / ".agent" / "skills" / "jig" / "SKILL.md"
        skill_path.write_text("# Modified content")

        # Second install
        subprocess.run(
            ["jigy", "init", "--skills-only"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Should be restored to template
        content = skill_path.read_text()
        assert content == SKILL_MD_TEMPLATE


class TestCLIFlags:
    """Tests for CLI flag behavior."""

    @jig.verifies("S-103")
    def test_project_flag_sets_charter_name(self, tmp_path: Path):
        """--project sets the Charter filename."""
        subprocess.run(
            ["jigy", "init", "--project", "myproject", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )

        assert (tmp_path / "jig" / "Charter_myproject.md").exists()

    @jig.verifies("S-103")
    def test_default_project_name_from_directory(self, tmp_path: Path):
        """Without --project, uses directory name."""
        subprocess.run(
            ["jigy", "init", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Find charter with directory name
        expected_charter = tmp_path / "jig" / f"Charter_{tmp_path.name}.md"
        assert expected_charter.exists()

    @jig.verifies("S-103")
    def test_force_flag_overwrites_jig_toml(self, tmp_path: Path):
        """--force allows overwriting jig.toml."""
        # First init
        subprocess.run(
            ["jigy", "init", "--project", "forcetest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Modify jig.toml
        toml_path = tmp_path / "jig.toml"
        toml_path.write_text("[custom]\nkey = 'value'\n")

        # Second init without force - should not overwrite
        subprocess.run(
            ["jigy", "init", "--project", "forcetest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )
        assert "custom" in toml_path.read_text()

        # With force - should overwrite
        subprocess.run(
            ["jigy", "init", "--project", "forcetest", "--no-skills", "--force"],
            cwd=tmp_path,
            capture_output=True,
        )
        content = toml_path.read_text()
        assert "[integration]" in content
        assert "custom" not in content

    @jig.verifies("S-103")
    def test_json_output_format(self, tmp_path: Path):
        """-j flag produces valid JSON output."""
        result = subprocess.run(
            ["jigy", "init", "-j", "--project", "jsontest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["success"] is True
        assert "paths_created" in output
        assert isinstance(output["paths_created"], list)

    @jig.verifies("S-103")
    def test_mutually_exclusive_flags(self, tmp_path: Path):
        """--no-skills and --skills-only are mutually exclusive."""
        result = subprocess.run(
            ["jigy", "init", "--no-skills", "--skills-only"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "mutually exclusive" in result.stderr.lower()


class TestGlobalSkillsInstallation:
    """Tests for global skills installation."""

    @jig.verifies("S-101", "S-103")
    def test_global_skills_flag(self, tmp_path: Path, monkeypatch):
        """--global-skills installs to ~/.agent/skills/ instead of project-local.

        Note: Uses Click test runner with monkeypatch to avoid subprocess
        environment issues with HOME variable.
        """
        from click.testing import CliRunner

        from jig.cli.main import cli

        # Create a fake home directory
        fake_home = tmp_path / "fakehome"
        fake_home.mkdir()

        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Monkeypatch Path.home() for this test
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=project_dir):
            result = runner.invoke(cli, ["init", "--global-skills", "--skills-only"])

            assert result.exit_code == 0, f"Failed: {result.output}"

            # Skills should be in global location (fake home)
            global_skills = fake_home / ".agent" / "skills" / "jig"
            assert (global_skills / "SKILL.md").exists()
            assert (global_skills / "contextJIG.md").exists()


class TestGitignoreManagement:
    """Tests for .gitignore management."""

    @jig.verifies("S-100")
    def test_creates_gitignore_with_generated_entry(self, tmp_path: Path):
        """jigy init creates .gitignore with jig/generated/ entry."""
        subprocess.run(
            ["jigy", "init", "--project", "gitignoretest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )

        gitignore = tmp_path / ".gitignore"
        assert gitignore.exists()
        assert "jig/generated/" in gitignore.read_text()

    @jig.verifies("S-100")
    def test_appends_to_existing_gitignore(self, tmp_path: Path):
        """jigy init appends to existing .gitignore without duplicating."""
        # Create existing .gitignore
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n.env\n")

        subprocess.run(
            ["jigy", "init", "--project", "appendtest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )

        content = gitignore.read_text()
        # Should preserve existing and add new
        assert "node_modules/" in content
        assert ".env" in content
        assert "jig/generated/" in content

    @jig.verifies("S-100")
    def test_no_duplicate_gitignore_entry(self, tmp_path: Path):
        """jigy init does not duplicate jig/generated/ entry."""
        # Create .gitignore with entry already
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("jig/generated/\n")

        subprocess.run(
            ["jigy", "init", "--project", "nodupetest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )

        content = gitignore.read_text()
        assert content.count("jig/generated/") == 1


class TestDigDetection:
    """Tests for DIG detection in jig.toml."""

    @jig.verifies("S-097")
    def test_include_dig_true_when_dig_exists(self, tmp_path: Path):
        """include_dig is true when dig/ directory exists."""
        # Create dig/ before init
        (tmp_path / "dig").mkdir()

        subprocess.run(
            ["jigy", "init", "--project", "digtest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )

        content = (tmp_path / "jig.toml").read_text()
        parsed = tomllib.loads(content)
        assert parsed["integration"]["include_dig"] is True

    @jig.verifies("S-097")
    def test_include_dig_false_when_no_dig(self, tmp_path: Path):
        """include_dig is false when no dig/ or dig.toml exists."""
        subprocess.run(
            ["jigy", "init", "--project", "nodigtest", "--no-skills"],
            cwd=tmp_path,
            capture_output=True,
        )

        content = (tmp_path / "jig.toml").read_text()
        parsed = tomllib.loads(content)
        assert parsed["integration"]["include_dig"] is False
