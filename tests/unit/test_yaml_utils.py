"""Unit tests for jig.utils.yaml_utils module."""

# @jig T-UTIL-003 verifies:S-JIG-002 subsystem:core
# @jig T-UTIL-004 verifies:S-JIG-002 subsystem:core

from pathlib import Path

import pytest
import yaml

from jig.utils.yaml_utils import dump_yaml, load_yaml


def test_load_yaml_valid(tmp_path: Path) -> None:
    """Verify YAML parsing of valid frontmatter."""
    # Arrange
    yaml_file = tmp_path / "valid.yaml"
    yaml_content = """
id: O-JIG-001
type: outcome
title: JIG tools run fast
status: active
"""
    yaml_file.write_text(yaml_content, encoding="utf-8")

    # Act
    data = load_yaml(yaml_file)

    # Assert
    assert data["id"] == "O-JIG-001"
    assert data["type"] == "outcome"
    assert data["title"] == "JIG tools run fast"
    assert data["status"] == "active"


def test_load_yaml_invalid(tmp_path: Path) -> None:
    """Verify helpful error on malformed YAML."""
    # Arrange
    yaml_file = tmp_path / "invalid.yaml"
    # Invalid YAML: inconsistent indentation
    yaml_content = """
key1: value1
  key2: value2
"""
    yaml_file.write_text(yaml_content, encoding="utf-8")

    # Act & Assert
    with pytest.raises(yaml.YAMLError) as exc_info:
        load_yaml(yaml_file)

    # Verify error message is helpful
    error_msg = str(exc_info.value)
    assert "Failed to parse YAML file" in error_msg
    assert str(yaml_file) in error_msg
    assert "check YAML syntax" in error_msg


def test_load_yaml_empty_file(tmp_path: Path) -> None:
    """Verify empty YAML file returns empty dict."""
    # Arrange
    yaml_file = tmp_path / "empty.yaml"
    yaml_file.write_text("", encoding="utf-8")

    # Act
    data = load_yaml(yaml_file)

    # Assert
    assert data == {}


def test_load_yaml_nested_structure(tmp_path: Path) -> None:
    """Verify loading of nested YAML structure."""
    # Arrange
    yaml_file = tmp_path / "nested.yaml"
    yaml_content = """
project:
  name: JIG
  version: 0.1.0
  metadata:
    author: Jim Meyer
    tags:
      - constraint-driven
      - tdd
"""
    yaml_file.write_text(yaml_content, encoding="utf-8")

    # Act
    data = load_yaml(yaml_file)

    # Assert
    assert data["project"]["name"] == "JIG"
    assert data["project"]["version"] == "0.1.0"
    assert data["project"]["metadata"]["author"] == "Jim Meyer"
    assert "constraint-driven" in data["project"]["metadata"]["tags"]


def test_load_yaml_non_dict_root(tmp_path: Path) -> None:
    """Verify error when YAML root is not a dictionary."""
    # Arrange
    yaml_file = tmp_path / "list_root.yaml"
    # Root is a list, not a dict
    yaml_content = """
- item1
- item2
- item3
"""
    yaml_file.write_text(yaml_content, encoding="utf-8")

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        load_yaml(yaml_file)

    # Verify error message explains the issue
    error_msg = str(exc_info.value)
    assert "must contain a dictionary at root level" in error_msg
    assert "list" in error_msg.lower()


def test_load_yaml_missing_file(tmp_path: Path) -> None:
    """Verify FileNotFoundError for missing file."""
    # Arrange
    nonexistent_file = tmp_path / "missing.yaml"

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        load_yaml(nonexistent_file)


def test_dump_yaml_simple_dict(tmp_path: Path) -> None:
    """Verify dumping simple dictionary to YAML."""
    # Arrange
    yaml_file = tmp_path / "output.yaml"
    data = {
        "id": "S-JIG-001",
        "type": "specification",
        "title": "Fast marker extraction",
    }

    # Act
    dump_yaml(data, yaml_file)

    # Assert
    assert yaml_file.exists()
    loaded_data = load_yaml(yaml_file)
    assert loaded_data == data


def test_dump_yaml_nested_structure(tmp_path: Path) -> None:
    """Verify dumping nested structure to YAML."""
    # Arrange
    yaml_file = tmp_path / "nested_output.yaml"
    data = {
        "graph": {
            "version": "1.0",
            "nodes": [
                {"id": "O-JIG-001", "type": "outcome"},
                {"id": "S-JIG-001", "type": "specification"},
            ],
        }
    }

    # Act
    dump_yaml(data, yaml_file)

    # Assert
    loaded_data = load_yaml(yaml_file)
    assert loaded_data == data


def test_dump_yaml_preserves_order(tmp_path: Path) -> None:
    """Verify YAML dump preserves insertion order (Python 3.7+)."""
    # Arrange
    yaml_file = tmp_path / "ordered.yaml"
    data = {
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
    }

    # Act
    dump_yaml(data, yaml_file)

    # Assert
    content = yaml_file.read_text(encoding="utf-8")
    # Check that keys appear in order in the file
    first_pos = content.index("first:")
    second_pos = content.index("second:")
    third_pos = content.index("third:")
    fourth_pos = content.index("fourth:")
    assert first_pos < second_pos < third_pos < fourth_pos


def test_dump_yaml_unicode_characters(tmp_path: Path) -> None:
    """Verify YAML dump preserves unicode characters."""
    # Arrange
    yaml_file = tmp_path / "unicode.yaml"
    data = {
        "title": "世界你好",
        "greeting": "Привет мир",
        "emoji": "🎉🚀",
    }

    # Act
    dump_yaml(data, yaml_file)

    # Assert
    loaded_data = load_yaml(yaml_file)
    assert loaded_data == data
    # Verify unicode is not escaped in the file
    content = yaml_file.read_text(encoding="utf-8")
    assert "世界你好" in content
    assert "Привет мир" in content


def test_dump_yaml_creates_parent_dirs(tmp_path: Path) -> None:
    """Verify dump_yaml creates parent directories if needed."""
    # Arrange
    yaml_file = tmp_path / "nested" / "dirs" / "config.yaml"
    data = {"version": "1.0"}

    # Act
    dump_yaml(data, yaml_file)

    # Assert
    assert yaml_file.exists()
    assert load_yaml(yaml_file) == data


def test_dump_yaml_block_style(tmp_path: Path) -> None:
    """Verify YAML dump uses block style (not flow style)."""
    # Arrange
    yaml_file = tmp_path / "block.yaml"
    data = {
        "items": ["one", "two", "three"],
        "nested": {"key1": "value1", "key2": "value2"},
    }

    # Act
    dump_yaml(data, yaml_file)

    # Assert
    content = yaml_file.read_text(encoding="utf-8")
    # Block style uses newlines and indentation, not inline {}/[]
    assert "{" not in content  # No flow-style dicts
    assert "[" not in content  # No flow-style lists
    # Verify it's valid and round-trips correctly
    loaded_data = load_yaml(yaml_file)
    assert loaded_data == data


def test_load_yaml_with_special_types(tmp_path: Path) -> None:
    """Verify loading YAML with various data types."""
    # Arrange
    yaml_file = tmp_path / "types.yaml"
    yaml_content = """
string_value: hello
int_value: 42
float_value: 3.14
bool_true: true
bool_false: false
null_value: null
list_value:
  - one
  - two
"""
    yaml_file.write_text(yaml_content, encoding="utf-8")

    # Act
    data = load_yaml(yaml_file)

    # Assert
    assert data["string_value"] == "hello"
    assert data["int_value"] == 42
    assert data["float_value"] == 3.14
    assert data["bool_true"] is True
    assert data["bool_false"] is False
    assert data["null_value"] is None
    assert data["list_value"] == ["one", "two"]
