"""Tests for TOML configuration parsing (S-063)."""

from pathlib import Path

import pytest

import jig
from jig.config.parser import parse_config_file, ConfigError


@jig.verifies("S-063")
def test_parses_valid_jig_toml(tmp_path: Path) -> None:
    """Valid jig.toml is parsed correctly."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
[jig]
version = "1"

[jig.paths]
source = "lib"
tests = "tests"
''')

    result = parse_config_file(config_file)

    assert result["jig"]["version"] == "1"
    assert result["jig"]["paths"]["source"] == "lib"
    assert result["jig"]["paths"]["tests"] == "tests"


@jig.verifies("S-063")
def test_parses_jig_toml_without_jig_section(tmp_path: Path) -> None:
    """jig.toml without [jig] section uses root as config."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
version = "1"

[paths]
source = "src"
''')

    result = parse_config_file(config_file)

    # Root level becomes the config
    assert result["version"] == "1"
    assert result["paths"]["source"] == "src"


@jig.verifies("S-063")
def test_parses_hidden_jig_toml(tmp_path: Path) -> None:
    """Hidden .jig.toml is parsed correctly."""
    config_file = tmp_path / ".jig.toml"
    config_file.write_text('''
[jig]
version = "1"
''')

    result = parse_config_file(config_file)

    assert result["jig"]["version"] == "1"


@jig.verifies("S-063")
def test_extracts_tool_jig_from_pyproject(tmp_path: Path) -> None:
    """pyproject.toml extracts only [tool.jig] section."""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text('''
[project]
name = "myproject"
version = "1.0.0"

[tool.black]
line-length = 88

[tool.jig]
version = "1"

[tool.jig.paths]
tests = "tests"
''')

    result = parse_config_file(config_file)

    # Only tool.jig section is returned
    assert result["version"] == "1"
    assert result["paths"]["tests"] == "tests"
    # Other sections are not included
    assert "project" not in result
    assert "tool" not in result
    assert "black" not in result


@jig.verifies("S-063")
def test_invalid_toml_raises_config_error(tmp_path: Path) -> None:
    """Invalid TOML syntax raises ConfigError with details."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
[jig
version = "1"
''')

    with pytest.raises(ConfigError) as exc_info:
        parse_config_file(config_file)

    error = exc_info.value
    assert "jig.toml" in str(error)
    # Should mention it's a parse error
    assert "parse" in str(error).lower() or "invalid" in str(error).lower() or "toml" in str(error).lower()


@jig.verifies("S-063")
def test_empty_file_returns_empty_dict(tmp_path: Path) -> None:
    """Empty config file returns empty dict."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text("")

    result = parse_config_file(config_file)

    assert result == {}


@jig.verifies("S-063")
def test_file_not_found_raises_config_error(tmp_path: Path) -> None:
    """Non-existent file raises ConfigError."""
    config_file = tmp_path / "nonexistent.toml"

    with pytest.raises(ConfigError) as exc_info:
        parse_config_file(config_file)

    assert "nonexistent.toml" in str(exc_info.value)


@jig.verifies("S-063")
def test_pyproject_without_tool_jig_raises_config_error(tmp_path: Path) -> None:
    """pyproject.toml without [tool.jig] raises ConfigError."""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text('''
[project]
name = "myproject"

[tool.black]
line-length = 88
''')

    with pytest.raises(ConfigError) as exc_info:
        parse_config_file(config_file)

    assert "tool.jig" in str(exc_info.value).lower()


@jig.verifies("S-063")
def test_unknown_keys_in_config(tmp_path: Path) -> None:
    """Unknown keys are preserved (validation happens later)."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
[jig]
version = "1"
unknown_key = "value"

[jig.unknown_section]
foo = "bar"
''')

    result = parse_config_file(config_file)

    # Unknown keys are preserved at parse time
    # Validation of known keys happens in schema layer (WU3)
    assert result["jig"]["unknown_key"] == "value"
    assert result["jig"]["unknown_section"]["foo"] == "bar"


@jig.verifies("S-063")
def test_preserves_all_value_types(tmp_path: Path) -> None:
    """All TOML value types are preserved correctly."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text('''
[jig]
version = "1"
count = 42
enabled = true
ratio = 3.14
items = ["a", "b", "c"]
''')

    result = parse_config_file(config_file)

    assert result["jig"]["version"] == "1"
    assert result["jig"]["count"] == 42
    assert result["jig"]["enabled"] is True
    assert result["jig"]["ratio"] == 3.14
    assert result["jig"]["items"] == ["a", "b", "c"]
