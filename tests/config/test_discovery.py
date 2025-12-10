"""Tests for configuration file discovery (S-062)."""

import tempfile
from pathlib import Path

import pytest

import jig
from jig.config.discovery import find_config_file


@jig.verifies("S-062")
def test_finds_jig_toml_in_current_directory(tmp_path: Path) -> None:
    """jig.toml in current directory is found."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('[jig]\nversion = "1"\n')

    result = find_config_file(start_dir=tmp_path)

    assert result == config_file


@jig.verifies("S-062")
def test_finds_hidden_jig_toml(tmp_path: Path) -> None:
    """Hidden .jig.toml is found when jig.toml doesn't exist."""
    config_file = tmp_path / ".jig.toml"
    config_file.write_text('[jig]\nversion = "1"\n')

    result = find_config_file(start_dir=tmp_path)

    assert result == config_file


@jig.verifies("S-062")
def test_finds_pyproject_toml_with_tool_jig(tmp_path: Path) -> None:
    """pyproject.toml with [tool.jig] section is found."""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text('[tool.jig]\nversion = "1"\n')

    result = find_config_file(start_dir=tmp_path)

    assert result == config_file


@jig.verifies("S-062")
def test_ignores_pyproject_without_tool_jig(tmp_path: Path) -> None:
    """pyproject.toml without [tool.jig] section is ignored."""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text('[tool.black]\nline-length = 88\n')

    result = find_config_file(start_dir=tmp_path)

    assert result is None


@jig.verifies("S-062")
def test_returns_none_when_no_config(tmp_path: Path) -> None:
    """Returns None when no configuration file exists."""
    result = find_config_file(start_dir=tmp_path)

    assert result is None


@jig.verifies("S-062")
def test_jig_toml_takes_priority_over_hidden(tmp_path: Path) -> None:
    """jig.toml takes priority over .jig.toml."""
    jig_toml = tmp_path / "jig.toml"
    jig_toml.write_text('[jig]\nversion = "1"\n')
    hidden_toml = tmp_path / ".jig.toml"
    hidden_toml.write_text('[jig]\nversion = "1"\n')

    result = find_config_file(start_dir=tmp_path)

    assert result == jig_toml


@jig.verifies("S-062")
def test_jig_toml_takes_priority_over_pyproject(tmp_path: Path) -> None:
    """jig.toml takes priority over pyproject.toml."""
    jig_toml = tmp_path / "jig.toml"
    jig_toml.write_text('[jig]\nversion = "1"\n')
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.jig]\nversion = "1"\n')

    result = find_config_file(start_dir=tmp_path)

    assert result == jig_toml


@jig.verifies("S-062")
def test_hidden_jig_toml_takes_priority_over_pyproject(tmp_path: Path) -> None:
    """.jig.toml takes priority over pyproject.toml."""
    hidden_toml = tmp_path / ".jig.toml"
    hidden_toml.write_text('[jig]\nversion = "1"\n')
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.jig]\nversion = "1"\n')

    result = find_config_file(start_dir=tmp_path)

    assert result == hidden_toml


@jig.verifies("S-062")
def test_searches_parent_directories(tmp_path: Path) -> None:
    """Searches parent directories for config file."""
    # Create config in parent
    config_file = tmp_path / "jig.toml"
    config_file.write_text('[jig]\nversion = "1"\n')

    # Create nested subdirectory
    nested = tmp_path / "src" / "module"
    nested.mkdir(parents=True)

    result = find_config_file(start_dir=nested)

    assert result == config_file


@jig.verifies("S-062")
def test_stops_at_filesystem_root(tmp_path: Path) -> None:
    """Search stops at filesystem root without infinite loop."""
    # This test verifies the function terminates properly
    # when no config file exists anywhere in the path
    result = find_config_file(start_dir=tmp_path)

    # Should return None, not raise or loop forever
    assert result is None


@jig.verifies("S-062")
def test_uses_cwd_as_default_start_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Uses current working directory when start_dir not specified."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('[jig]\nversion = "1"\n')

    monkeypatch.chdir(tmp_path)

    result = find_config_file()

    assert result == config_file
