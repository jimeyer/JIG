"""Tests for path configuration with defaults (S-064)."""

from pathlib import Path

import pytest

import jig
from jig.config.schema import load_config, JigConfig, PathsConfig


@jig.verifies("S-064")
def test_default_paths_when_no_config(tmp_path: Path) -> None:
    """All paths use defaults when no config file exists."""
    config = load_config(project_root=tmp_path)

    assert config.paths.source == tmp_path / "src"
    assert config.paths.tests == tmp_path / "test"
    assert config.paths.jig_root == tmp_path / "jig"
    assert config.paths.specifications == tmp_path / "jig" / "specifications"
    assert config.paths.outcomes == tmp_path / "jig" / "outcomes"
    assert config.paths.bricks == tmp_path / "jig" / "bricks.yaml"
    assert config.paths.generated == tmp_path / "jig" / "generated"


@jig.verifies("S-064")
def test_override_tests_path(tmp_path: Path) -> None:
    """paths.tests can be overridden while others use defaults."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
[jig]
version = "1"

[jig.paths]
tests = "tests"
''')

    config = load_config(project_root=tmp_path)

    assert config.paths.tests == tmp_path / "tests"
    # Others remain default
    assert config.paths.source == tmp_path / "src"
    assert config.paths.jig_root == tmp_path / "jig"


@jig.verifies("S-064")
def test_override_source_path(tmp_path: Path) -> None:
    """paths.source can be overridden."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
[jig]
version = "1"

[jig.paths]
source = "lib"
''')

    config = load_config(project_root=tmp_path)

    assert config.paths.source == tmp_path / "lib"
    assert config.paths.tests == tmp_path / "test"  # default


@jig.verifies("S-064")
def test_override_jig_root_affects_nested_paths(tmp_path: Path) -> None:
    """Changing jig_root affects specifications, outcomes, bricks, generated."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
[jig]
version = "1"

[jig.paths]
jig_root = ".jig"
''')

    config = load_config(project_root=tmp_path)

    assert config.paths.jig_root == tmp_path / ".jig"
    assert config.paths.specifications == tmp_path / ".jig" / "specifications"
    assert config.paths.outcomes == tmp_path / ".jig" / "outcomes"
    assert config.paths.bricks == tmp_path / ".jig" / "bricks.yaml"
    assert config.paths.generated == tmp_path / ".jig" / "generated"


@jig.verifies("S-064")
def test_override_nested_path_independently(tmp_path: Path) -> None:
    """Nested paths can be overridden independently of jig_root."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
[jig]
version = "1"

[jig.paths]
specifications = "specs"
bricks = "architecture/bricks.yaml"
''')

    config = load_config(project_root=tmp_path)

    # Overridden paths (relative to jig_root)
    assert config.paths.specifications == tmp_path / "jig" / "specs"
    assert config.paths.bricks == tmp_path / "jig" / "architecture" / "bricks.yaml"
    # Default jig_root and others
    assert config.paths.jig_root == tmp_path / "jig"
    assert config.paths.outcomes == tmp_path / "jig" / "outcomes"


@jig.verifies("S-064")
def test_partial_config_merges_with_defaults(tmp_path: Path) -> None:
    """Partial configuration merges correctly with defaults."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
[jig]
version = "1"

[jig.paths]
source = "src/main"
tests = "src/test"
''')

    config = load_config(project_root=tmp_path)

    # Overridden
    assert config.paths.source == tmp_path / "src" / "main"
    assert config.paths.tests == tmp_path / "src" / "test"
    # Defaults
    assert config.paths.jig_root == tmp_path / "jig"
    assert config.paths.specifications == tmp_path / "jig" / "specifications"


@jig.verifies("S-064")
def test_paths_are_absolute(tmp_path: Path) -> None:
    """All resolved paths are absolute."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
[jig]
version = "1"

[jig.paths]
source = "lib"
''')

    config = load_config(project_root=tmp_path)

    assert config.paths.source.is_absolute()
    assert config.paths.tests.is_absolute()
    assert config.paths.jig_root.is_absolute()
    assert config.paths.specifications.is_absolute()
    assert config.paths.outcomes.is_absolute()
    assert config.paths.bricks.is_absolute()
    assert config.paths.generated.is_absolute()


@jig.verifies("S-064")
def test_config_from_pyproject_toml(tmp_path: Path) -> None:
    """Configuration loads correctly from pyproject.toml."""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text('''
[project]
name = "myproject"

[tool.jig]
version = "1"

[tool.jig.paths]
tests = "tests"
''')

    config = load_config(project_root=tmp_path)

    assert config.paths.tests == tmp_path / "tests"
    assert config.paths.source == tmp_path / "src"  # default


@jig.verifies("S-064")
def test_config_has_metadata(tmp_path: Path) -> None:
    """Config object includes metadata about config file."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
[jig]
version = "1"
''')

    config = load_config(project_root=tmp_path)

    assert config.project_root == tmp_path
    assert config.config_file_path == config_file
    assert config.has_config_file is True


@jig.verifies("S-064")
def test_config_without_file_has_metadata(tmp_path: Path) -> None:
    """Config object metadata when no config file exists."""
    config = load_config(project_root=tmp_path)

    assert config.project_root == tmp_path
    assert config.config_file_path is None
    assert config.has_config_file is False


@jig.verifies("S-064")
def test_loads_hidden_jig_toml(tmp_path: Path) -> None:
    """Configuration loads from .jig.toml."""
    config_file = tmp_path / ".jig.toml"
    config_file.write_text('''
[jig]
version = "1"

[jig.paths]
tests = "test_suite"
''')

    config = load_config(project_root=tmp_path)

    assert config.paths.tests == tmp_path / "test_suite"
    assert config.config_file_path == config_file


@jig.verifies("S-064")
def test_jig_toml_takes_priority(tmp_path: Path) -> None:
    """jig.toml takes priority over .jig.toml and pyproject.toml."""
    # Create all three
    (tmp_path / "jig.toml").write_text('''
[jig]
version = "1"

[jig.paths]
tests = "from_jig_toml"
''')
    (tmp_path / ".jig.toml").write_text('''
[jig]
version = "1"

[jig.paths]
tests = "from_hidden"
''')
    (tmp_path / "pyproject.toml").write_text('''
[tool.jig]
version = "1"

[tool.jig.paths]
tests = "from_pyproject"
''')

    config = load_config(project_root=tmp_path)

    assert config.paths.tests == tmp_path / "from_jig_toml"
