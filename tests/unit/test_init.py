"""Tests for JIG project initialization.

Verifies the core init_project() function creates proper directory structure
and handles idempotent behavior correctly.
"""

import tomllib
from dataclasses import fields
from pathlib import Path

import yaml

import jig


class TestInitResult:
    """Tests for InitResult dataclass structure."""

    @jig.verifies("S-096")
    def test_init_result_is_dataclass(self):
        """InitResult should be a dataclass."""
        from jig.init import InitResult

        # Check it has expected dataclass fields
        field_names = {f.name for f in fields(InitResult)}
        assert "success" in field_names
        assert "paths_created" in field_names
        assert "error" in field_names

    @jig.verifies("S-096")
    def test_init_result_has_correct_types(self):
        """InitResult fields have correct types."""
        from jig.init import InitResult

        result = InitResult(success=True, paths_created=[Path("test")], error=None)
        assert isinstance(result.success, bool)
        assert isinstance(result.paths_created, list)
        assert result.error is None

        result_error = InitResult(success=False, paths_created=[], error="test error")
        assert isinstance(result_error.error, str)


class TestInitProjectDirectoryStructure:
    """Tests for S-096: init_project() creates correct directory structure."""

    @jig.verifies("S-096")
    def test_creates_jig_toml(self, tmp_path: Path):
        """init_project creates jig.toml at project root."""
        from jig.init import init_project

        result = init_project(tmp_path)

        assert result.success
        assert (tmp_path / "jig.toml").exists()
        assert (tmp_path / "jig.toml") in result.paths_created

    @jig.verifies("S-096")
    def test_creates_jig_directory(self, tmp_path: Path):
        """init_project creates jig/ directory."""
        from jig.init import init_project

        result = init_project(tmp_path)

        assert result.success
        assert (tmp_path / "jig").is_dir()

    @jig.verifies("S-096", "S-098")
    def test_creates_charter_with_correct_naming(self, tmp_path: Path):
        """init_project creates Charter_<project>.md with correct naming."""
        from jig.init import init_project

        # Use explicit project name
        result = init_project(tmp_path, project_name="my_project")

        assert result.success
        charter_path = tmp_path / "jig" / "Charter_my_project.md"
        assert charter_path.exists()
        assert charter_path in result.paths_created

    @jig.verifies("S-096", "S-098")
    def test_charter_uses_parent_directory_name_when_no_project_name(
        self, tmp_path: Path
    ):
        """init_project uses parent directory name when --project not provided."""
        from jig.init import init_project

        # tmp_path has a unique name like /tmp/pytest-xyz
        result = init_project(tmp_path)

        assert result.success
        # Charter should use tmp_path's name
        expected_name = f"Charter_{tmp_path.name}.md"
        charter_path = tmp_path / "jig" / expected_name
        assert charter_path.exists()

    @jig.verifies("S-096")
    def test_creates_specifications_directory(self, tmp_path: Path):
        """init_project creates jig/specifications/ directory."""
        from jig.init import init_project

        result = init_project(tmp_path)

        assert result.success
        assert (tmp_path / "jig" / "specifications").is_dir()

    @jig.verifies("S-096")
    def test_creates_outcomes_directory(self, tmp_path: Path):
        """init_project creates jig/outcomes/ directory."""
        from jig.init import init_project

        result = init_project(tmp_path)

        assert result.success
        assert (tmp_path / "jig" / "outcomes").is_dir()

    @jig.verifies("S-096")
    def test_creates_architecture_directory(self, tmp_path: Path):
        """init_project creates jig/architecture/ directory."""
        from jig.init import init_project

        result = init_project(tmp_path)

        assert result.success
        assert (tmp_path / "jig" / "architecture").is_dir()

    @jig.verifies("S-096", "S-099")
    def test_creates_bricks_yaml(self, tmp_path: Path):
        """init_project creates jig/bricks.yaml scaffold."""
        from jig.init import init_project

        result = init_project(tmp_path)

        assert result.success
        bricks_path = tmp_path / "jig" / "bricks.yaml"
        assert bricks_path.exists()
        assert bricks_path in result.paths_created

        # Verify content is valid YAML with bricks: []
        content = bricks_path.read_text()
        parsed = yaml.safe_load(content)
        assert parsed["bricks"] == []


class TestInitGeneratedDirectory:
    """Tests for S-100: init_project() manages generated directory."""

    @jig.verifies("S-100")
    def test_creates_generated_directory(self, tmp_path: Path):
        """init_project creates jig/generated/ directory."""
        from jig.init import init_project

        result = init_project(tmp_path)

        assert result.success
        assert (tmp_path / "jig" / "generated").is_dir()

    @jig.verifies("S-100")
    def test_creates_gitignore_if_not_exists(self, tmp_path: Path):
        """init_project creates .gitignore with jig/generated/ if it doesn't exist."""
        from jig.init import init_project

        result = init_project(tmp_path)

        assert result.success
        gitignore_path = tmp_path / ".gitignore"
        assert gitignore_path.exists()
        content = gitignore_path.read_text()
        assert "jig/generated/" in content

    @jig.verifies("S-100")
    def test_appends_to_existing_gitignore(self, tmp_path: Path):
        """init_project appends jig/generated/ to existing .gitignore."""
        from jig.init import init_project

        # Create existing .gitignore with some content
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("node_modules/\n.env\n")

        result = init_project(tmp_path)

        assert result.success
        content = gitignore_path.read_text()
        # Should preserve existing content
        assert "node_modules/" in content
        assert ".env" in content
        # Should have added jig/generated/
        assert "jig/generated/" in content

    @jig.verifies("S-100")
    def test_does_not_duplicate_gitignore_entry(self, tmp_path: Path):
        """init_project does not add jig/generated/ if already present."""
        from jig.init import init_project

        # Create .gitignore that already has the entry
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("jig/generated/\n")

        result = init_project(tmp_path)

        assert result.success
        content = gitignore_path.read_text()
        # Should only appear once
        assert content.count("jig/generated/") == 1

    @jig.verifies("S-100")
    def test_adds_newline_before_entry_if_needed(self, tmp_path: Path):
        """init_project adds newline before jig/generated/ if file doesn't end with one."""
        from jig.init import init_project

        # Create .gitignore without trailing newline
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("node_modules/")  # No trailing newline

        result = init_project(tmp_path)

        assert result.success
        content = gitignore_path.read_text()
        # Should have proper formatting
        assert "node_modules/\njig/generated/" in content or "node_modules/\n\njig/generated/" in content


class TestIdempotentInit:
    """Tests for S-102: init_project() idempotent behavior."""

    @jig.verifies("S-102")
    def test_second_run_creates_nothing_new(self, tmp_path: Path):
        """Running init twice creates nothing new on second run."""
        from jig.init import init_project

        # First run
        result1 = init_project(tmp_path)
        assert result1.success
        assert len(result1.paths_created) > 0  # First run creates paths

        # Second run
        result2 = init_project(tmp_path)
        assert result2.success
        # Should have no new paths created
        assert len(result2.paths_created) == 0

    @jig.verifies("S-102")
    def test_second_run_returns_success(self, tmp_path: Path):
        """Second run on initialized project returns success."""
        from jig.init import init_project

        init_project(tmp_path)
        result = init_project(tmp_path)

        assert result.success
        assert result.error is None

    @jig.verifies("S-102")
    def test_never_overwrites_charter(self, tmp_path: Path):
        """init_project never overwrites existing Charter file."""
        from jig.init import init_project

        # First init
        init_project(tmp_path, project_name="test_proj")

        # Modify charter content
        charter_path = tmp_path / "jig" / "Charter_test_proj.md"
        charter_path.write_text("# My Custom Charter\n\nCustom content.")

        # Second init
        result = init_project(tmp_path, project_name="test_proj")

        assert result.success
        # Charter should still have custom content
        content = charter_path.read_text()
        assert "My Custom Charter" in content
        assert "Custom content" in content

    @jig.verifies("S-102")
    def test_never_overwrites_charter_even_with_force(self, tmp_path: Path):
        """init_project never overwrites Charter even with force=True."""
        from jig.init import init_project

        # First init
        init_project(tmp_path, project_name="test_proj")

        # Modify charter
        charter_path = tmp_path / "jig" / "Charter_test_proj.md"
        charter_path.write_text("# Custom Charter")

        # Second init with force
        result = init_project(tmp_path, project_name="test_proj", force=True)

        assert result.success
        content = charter_path.read_text()
        assert "Custom Charter" in content

    @jig.verifies("S-102")
    def test_never_overwrites_bricks_yaml(self, tmp_path: Path):
        """init_project never overwrites existing bricks.yaml."""
        from jig.init import init_project

        # First init
        init_project(tmp_path)

        # Modify bricks.yaml
        bricks_path = tmp_path / "jig" / "bricks.yaml"
        bricks_path.write_text("bricks:\n  - id: B-custom\n    name: Custom\n    layer: 0\n")

        # Second init
        result = init_project(tmp_path)

        assert result.success
        content = bricks_path.read_text()
        assert "B-custom" in content

    @jig.verifies("S-102")
    def test_never_overwrites_bricks_yaml_even_with_force(self, tmp_path: Path):
        """init_project never overwrites bricks.yaml even with force=True."""
        from jig.init import init_project

        # First init
        init_project(tmp_path)

        # Modify bricks.yaml
        bricks_path = tmp_path / "jig" / "bricks.yaml"
        bricks_path.write_text("bricks:\n  - id: B-custom\n")

        # Second init with force
        result = init_project(tmp_path, force=True)

        assert result.success
        content = bricks_path.read_text()
        assert "B-custom" in content

    @jig.verifies("S-102")
    def test_always_ensures_generated_directory_exists(self, tmp_path: Path):
        """init_project always ensures jig/generated/ exists (may be wiped by rebuild)."""
        from jig.init import init_project

        # First init
        init_project(tmp_path)

        # Simulate rebuild wiping generated/
        generated_dir = tmp_path / "jig" / "generated"
        generated_dir.rmdir()
        assert not generated_dir.exists()

        # Second init should recreate it
        result = init_project(tmp_path)

        assert result.success
        assert generated_dir.is_dir()

    @jig.verifies("S-102")
    def test_force_allows_overwriting_jig_toml(self, tmp_path: Path):
        """force=True allows overwriting jig.toml."""
        from jig.init import init_project

        # First init
        init_project(tmp_path)

        # Modify jig.toml
        toml_path = tmp_path / "jig.toml"
        toml_path.write_text("[custom]\nkey = 'value'\n")

        # Second init without force - should not overwrite
        result = init_project(tmp_path)
        assert result.success
        content = toml_path.read_text()
        assert "custom" in content

        # Now with force - should overwrite
        result = init_project(tmp_path, force=True)
        assert result.success
        content = toml_path.read_text()
        assert "[integration]" in content


class TestDigDetection:
    """Tests for S-097: dig detection for include_dig setting."""

    @jig.verifies("S-097")
    def test_include_dig_true_when_dig_directory_exists(self, tmp_path: Path):
        """include_dig is true in jig.toml when dig/ directory exists."""
        from jig.init import init_project

        # Create dig/ directory before init
        (tmp_path / "dig").mkdir()

        result = init_project(tmp_path)

        assert result.success
        content = (tmp_path / "jig.toml").read_text()
        parsed = tomllib.loads(content)
        assert parsed["integration"]["include_dig"] is True

    @jig.verifies("S-097")
    def test_include_dig_true_when_dig_toml_exists(self, tmp_path: Path):
        """include_dig is true in jig.toml when dig.toml exists."""
        from jig.init import init_project

        # Create dig.toml before init
        (tmp_path / "dig.toml").write_text("[dig]\n")

        result = init_project(tmp_path)

        assert result.success
        content = (tmp_path / "jig.toml").read_text()
        parsed = tomllib.loads(content)
        assert parsed["integration"]["include_dig"] is True

    @jig.verifies("S-097")
    def test_include_dig_false_when_no_dig(self, tmp_path: Path):
        """include_dig is false in jig.toml when no dig/ or dig.toml."""
        from jig.init import init_project

        result = init_project(tmp_path)

        assert result.success
        content = (tmp_path / "jig.toml").read_text()
        parsed = tomllib.loads(content)
        assert parsed["integration"]["include_dig"] is False


class TestJigTomlContent:
    """Tests for jig.toml content validity."""

    @jig.verifies("S-097")
    def test_jig_toml_is_valid_toml(self, tmp_path: Path):
        """Generated jig.toml is valid TOML."""
        from jig.init import init_project

        init_project(tmp_path)

        content = (tmp_path / "jig.toml").read_text()
        # Should parse without error
        parsed = tomllib.loads(content)
        assert isinstance(parsed, dict)

    @jig.verifies("S-097")
    def test_jig_toml_has_scan_ignore(self, tmp_path: Path):
        """Generated jig.toml has [scan].ignore list."""
        from jig.init import init_project

        init_project(tmp_path)

        content = (tmp_path / "jig.toml").read_text()
        parsed = tomllib.loads(content)
        assert "scan" in parsed
        assert "ignore" in parsed["scan"]
        assert isinstance(parsed["scan"]["ignore"], list)

    @jig.verifies("S-097")
    def test_jig_toml_has_name_field(self, tmp_path: Path):
        """Generated jig.toml has top-level name field."""
        from jig.init import init_project

        init_project(tmp_path, project_name="myproject")

        content = (tmp_path / "jig.toml").read_text()
        parsed = tomllib.loads(content)
        assert "name" in parsed
        assert parsed["name"] == "myproject"


class TestProjectNameFromToml:
    """Tests for reading project name from existing jig.toml."""

    @jig.verifies("S-097")
    def test_reads_project_name_from_existing_jig_toml(self, tmp_path: Path):
        """init_project reads project name from existing jig.toml."""
        from jig.init import init_project

        # Create jig.toml with name before init
        (tmp_path / "jig.toml").write_text('name = "existing-project"\n')

        result = init_project(tmp_path)

        assert result.success
        # Charter should use name from jig.toml
        charter_path = tmp_path / "jig" / "Charter_existing-project.md"
        assert charter_path.exists()

    @jig.verifies("S-097")
    def test_cli_project_name_overrides_jig_toml(self, tmp_path: Path):
        """CLI --project flag takes precedence over jig.toml name."""
        from jig.init import init_project

        # Create jig.toml with name
        (tmp_path / "jig.toml").write_text('name = "toml-name"\n')

        # But pass different name via project_name parameter
        result = init_project(tmp_path, project_name="cli-name")

        assert result.success
        # Charter should use CLI name
        charter_path = tmp_path / "jig" / "Charter_cli-name.md"
        assert charter_path.exists()
        # Should NOT create Charter_toml-name.md
        assert not (tmp_path / "jig" / "Charter_toml-name.md").exists()


class TestExistingCharterDetection:
    """Tests for detecting existing Charter files."""

    @jig.verifies("S-102")
    def test_skips_charter_creation_when_legacy_charter_exists(self, tmp_path: Path):
        """init_project skips Charter creation when Charter.md exists."""
        from jig.init import init_project

        # Create jig/ with legacy Charter.md
        jig_dir = tmp_path / "jig"
        jig_dir.mkdir()
        legacy_charter = jig_dir / "Charter.md"
        legacy_charter.write_text("# My Legacy Charter\n")

        result = init_project(tmp_path, project_name="newproj")

        assert result.success
        # Should NOT create Charter_newproj.md
        assert not (jig_dir / "Charter_newproj.md").exists()
        # Legacy charter should be untouched
        assert legacy_charter.read_text() == "# My Legacy Charter\n"

    @jig.verifies("S-102")
    def test_skips_charter_creation_when_named_charter_exists(self, tmp_path: Path):
        """init_project skips Charter creation when Charter_*.md exists."""
        from jig.init import init_project

        # Create jig/ with existing named charter
        jig_dir = tmp_path / "jig"
        jig_dir.mkdir()
        existing_charter = jig_dir / "Charter_oldname.md"
        existing_charter.write_text("# Old Charter\n")

        result = init_project(tmp_path, project_name="newname")

        assert result.success
        # Should NOT create Charter_newname.md
        assert not (jig_dir / "Charter_newname.md").exists()
        # Existing charter should be untouched
        assert existing_charter.read_text() == "# Old Charter\n"

    @jig.verifies("S-102")
    def test_creates_charter_when_no_charter_exists(self, tmp_path: Path):
        """init_project creates Charter when none exists."""
        from jig.init import init_project

        result = init_project(tmp_path, project_name="newproj")

        assert result.success
        charter_path = tmp_path / "jig" / "Charter_newproj.md"
        assert charter_path.exists()


class TestInstallSkillsLocalInstallation:
    """Tests for S-101: install_skills() creates local skill files."""

    @jig.verifies("S-101")
    def test_creates_skill_md_file(self, tmp_path: Path):
        """install_skills creates .claude/skills/jig/SKILL.md."""
        from jig.init import install_skills

        result = install_skills(tmp_path)

        skill_path = tmp_path / ".claude" / "skills" / "jig" / "SKILL.md"
        assert skill_path.exists()
        assert skill_path in result

    @jig.verifies("S-101")
    def test_creates_context_jig_md_file(self, tmp_path: Path):
        """install_skills creates .claude/skills/jig/contextJIG.md."""
        from jig.init import install_skills

        result = install_skills(tmp_path)

        context_path = tmp_path / ".claude" / "skills" / "jig" / "contextJIG.md"
        assert context_path.exists()
        assert context_path in result

    @jig.verifies("S-101")
    def test_returns_list_of_created_paths(self, tmp_path: Path):
        """install_skills returns list of created paths."""
        from jig.init import install_skills

        result = install_skills(tmp_path)

        assert isinstance(result, list)
        # 2 (jig/) + 2 (jig-context/) + 3 (jigplan/) + 3 (plan/) + 3 (do-plan/) = 13
        assert len(result) == 13
        # jig/ skill paths should be in the result
        skill_path = tmp_path / ".claude" / "skills" / "jig" / "SKILL.md"
        context_path = tmp_path / ".claude" / "skills" / "jig" / "contextJIG.md"
        assert skill_path in result
        assert context_path in result

    @jig.verifies("S-101")
    def test_skill_file_has_correct_content(self, tmp_path: Path):
        """SKILL.md contains the expected template content."""
        from jig.init import install_skills
        from jig.templates import SKILL_MD_TEMPLATE

        install_skills(tmp_path)

        skill_path = tmp_path / ".claude" / "skills" / "jig" / "SKILL.md"
        content = skill_path.read_text()
        assert content == SKILL_MD_TEMPLATE

    @jig.verifies("S-101")
    def test_context_file_has_correct_content(self, tmp_path: Path):
        """contextJIG.md contains the expected template content."""
        from jig.init import install_skills
        from jig.templates import CONTEXT_JIG_MD_TEMPLATE

        install_skills(tmp_path)

        context_path = tmp_path / ".claude" / "skills" / "jig" / "contextJIG.md"
        content = context_path.read_text()
        assert content == CONTEXT_JIG_MD_TEMPLATE

    @jig.verifies("S-101")
    def test_creates_necessary_directories(self, tmp_path: Path):
        """install_skills creates .claude/skills/jig/ directory structure."""
        from jig.init import install_skills

        install_skills(tmp_path)

        assert (tmp_path / ".claude").is_dir()
        assert (tmp_path / ".claude" / "skills").is_dir()
        assert (tmp_path / ".claude" / "skills" / "jig").is_dir()


class TestInstallSkillsGlobalInstallation:
    """Tests for S-101: install_skills() with global_install option."""

    @jig.verifies("S-101")
    def test_global_install_uses_home_directory(self, tmp_path: Path, monkeypatch):
        """--global-skills installs to ~/.claude/skills/ instead."""
        from jig.init import install_skills

        # Use tmp_path as fake home directory
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        result = install_skills(tmp_path / "project", global_install=True)

        # Should install to home directory, not project directory
        skill_path = tmp_path / ".claude" / "skills" / "jig" / "SKILL.md"
        context_path = tmp_path / ".claude" / "skills" / "jig" / "contextJIG.md"
        assert skill_path.exists()
        assert context_path.exists()
        assert skill_path in result
        assert context_path in result

    @jig.verifies("S-101")
    def test_global_install_does_not_create_local_files(
        self, tmp_path: Path, monkeypatch
    ):
        """--global-skills does not create files in project directory."""
        from jig.init import install_skills

        # Create project directory
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()

        # Use tmp_path as fake home directory
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        install_skills(project_dir, global_install=True)

        # Should NOT have local skills
        local_skill_path = project_dir / ".claude" / "skills" / "jig" / "SKILL.md"
        assert not local_skill_path.exists()


class TestInstallSkillsOverwriteBehavior:
    """Tests for S-101: Skills always overwrite existing files."""

    @jig.verifies("S-101")
    def test_skills_always_overwrite(self, tmp_path: Path):
        """Skills are always overwritten (they are templates, not user content)."""
        from jig.init import install_skills

        # First install
        install_skills(tmp_path)

        # Modify the skill file
        skill_path = tmp_path / ".claude" / "skills" / "jig" / "SKILL.md"
        skill_path.write_text("# Modified content")

        # Second install should overwrite
        result = install_skills(tmp_path)

        content = skill_path.read_text()
        assert "Modified content" not in content
        assert skill_path in result

    @jig.verifies("S-101")
    def test_context_always_overwrites(self, tmp_path: Path):
        """contextJIG.md is always overwritten."""
        from jig.init import install_skills

        # First install
        install_skills(tmp_path)

        # Modify the context file
        context_path = tmp_path / ".claude" / "skills" / "jig" / "contextJIG.md"
        context_path.write_text("# Modified context")

        # Second install should overwrite
        result = install_skills(tmp_path)

        content = context_path.read_text()
        assert "Modified context" not in content
        assert context_path in result


class TestInstallSkillsIndependence:
    """Tests for S-101: Skill installation works independently of jig/ structure."""

    @jig.verifies("S-101")
    def test_works_without_jig_directory(self, tmp_path: Path):
        """install_skills works even when jig/ directory doesn't exist."""
        from jig.init import install_skills

        # Don't create jig/ directory
        assert not (tmp_path / "jig").exists()

        # Should still work
        result = install_skills(tmp_path)

        skill_path = tmp_path / ".claude" / "skills" / "jig" / "SKILL.md"
        assert skill_path.exists()
        assert len(result) == 13

    @jig.verifies("S-101")
    def test_works_without_jig_toml(self, tmp_path: Path):
        """install_skills works even when jig.toml doesn't exist."""
        from jig.init import install_skills

        # Don't create jig.toml
        assert not (tmp_path / "jig.toml").exists()

        # Should still work
        result = install_skills(tmp_path)

        skill_path = tmp_path / ".claude" / "skills" / "jig" / "SKILL.md"
        assert skill_path.exists()
        assert len(result) == 13


class TestInstallSkillsNewSkills:
    """Tests for S-101: new skill directories installed by install_skills()."""

    @jig.verifies("S-101")
    def test_jig_context_skill_installed(self, tmp_path: Path):
        """install_skills creates .claude/skills/jig-context/ with SKILL.md and contextJIG.md."""
        from jig.init import install_skills

        install_skills(tmp_path)

        base = tmp_path / ".claude" / "skills" / "jig-context"
        assert (base / "SKILL.md").exists()
        assert (base / "contextJIG.md").exists()

    @jig.verifies("S-101")
    def test_jig_context_skill_has_user_invocable_false(self, tmp_path: Path):
        """jig-context SKILL.md has user-invocable: false."""
        from jig.init import install_skills

        install_skills(tmp_path)

        content = (tmp_path / ".claude" / "skills" / "jig-context" / "SKILL.md").read_text()
        assert "user-invocable: false" in content

    @jig.verifies("S-101")
    def test_jigplan_skill_installed(self, tmp_path: Path):
        """install_skills creates .claude/skills/jigplan/ with SKILL.md, instructions.md, contextJIG.md."""
        from jig.init import install_skills

        install_skills(tmp_path)

        base = tmp_path / ".claude" / "skills" / "jigplan"
        assert (base / "SKILL.md").exists()
        assert (base / "instructions.md").exists()
        assert (base / "contextJIG.md").exists()

    @jig.verifies("S-101")
    def test_jigplan_skill_has_disable_model_invocation(self, tmp_path: Path):
        """jigplan SKILL.md has disable-model-invocation: true."""
        from jig.init import install_skills

        install_skills(tmp_path)

        content = (tmp_path / ".claude" / "skills" / "jigplan" / "SKILL.md").read_text()
        assert "disable-model-invocation: true" in content

    @jig.verifies("S-101")
    def test_plan_skill_installed(self, tmp_path: Path):
        """install_skills creates .claude/skills/plan/ with SKILL.md, instructions.md, contextJIG.md."""
        from jig.init import install_skills

        install_skills(tmp_path)

        base = tmp_path / ".claude" / "skills" / "plan"
        assert (base / "SKILL.md").exists()
        assert (base / "instructions.md").exists()
        assert (base / "contextJIG.md").exists()

    @jig.verifies("S-101")
    def test_plan_skill_has_disable_model_invocation(self, tmp_path: Path):
        """plan SKILL.md has disable-model-invocation: true."""
        from jig.init import install_skills

        install_skills(tmp_path)

        content = (tmp_path / ".claude" / "skills" / "plan" / "SKILL.md").read_text()
        assert "disable-model-invocation: true" in content

    @jig.verifies("S-101")
    def test_do_plan_skill_installed(self, tmp_path: Path):
        """install_skills creates .claude/skills/do-plan/ with SKILL.md, instructions.md, do-wu.md."""
        from jig.init import install_skills

        install_skills(tmp_path)

        base = tmp_path / ".claude" / "skills" / "do-plan"
        assert (base / "SKILL.md").exists()
        assert (base / "instructions.md").exists()
        assert (base / "do-wu.md").exists()

    @jig.verifies("S-101")
    def test_do_plan_skill_has_disable_model_invocation(self, tmp_path: Path):
        """do-plan SKILL.md has disable-model-invocation: true."""
        from jig.init import install_skills

        install_skills(tmp_path)

        content = (tmp_path / ".claude" / "skills" / "do-plan" / "SKILL.md").read_text()
        assert "disable-model-invocation: true" in content

    @jig.verifies("S-101")
    def test_all_skill_dirs_created(self, tmp_path: Path):
        """install_skills creates all five skill directories."""
        from jig.init import install_skills

        install_skills(tmp_path)

        skills_root = tmp_path / ".claude" / "skills"
        for skill_dir in ["jig", "jig-context", "jigplan", "plan", "do-plan"]:
            assert (skills_root / skill_dir).is_dir(), f"{skill_dir}/ not created"

    @jig.verifies("S-101")
    def test_global_install_creates_new_skills_in_home(self, tmp_path: Path, monkeypatch):
        """--global-skills installs all skill dirs under ~/.claude/skills/."""
        from jig.init import install_skills

        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        install_skills(tmp_path / "project", global_install=True)

        skills_root = tmp_path / ".claude" / "skills"
        for skill_dir in ["jig", "jig-context", "jigplan", "plan", "do-plan"]:
            assert (skills_root / skill_dir).is_dir(), f"global {skill_dir}/ not created"
