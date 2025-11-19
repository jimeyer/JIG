"""Unit tests for jig.utils.io module."""

# @jig T-UTIL-001 verifies:S-JIG-002 subsystem:core
# @jig T-UTIL-002 verifies:S-JIG-002 subsystem:core

from pathlib import Path

import pytest

from jig.utils.io import ensure_dir, read_file, write_file


def test_read_file_success(tmp_path: Path) -> None:
    """Verify read_file loads file contents correctly."""
    # Arrange
    test_file = tmp_path / "test.txt"
    expected_content = "Hello, JIG!\nThis is a test file.\n"
    test_file.write_text(expected_content, encoding="utf-8")

    # Act
    content = read_file(test_file)

    # Assert
    assert content == expected_content


def test_read_file_missing(tmp_path: Path) -> None:
    """Verify read_file raises FileNotFoundError with clear message."""
    # Arrange
    nonexistent_file = tmp_path / "does_not_exist.txt"

    # Act & Assert
    with pytest.raises(FileNotFoundError) as exc_info:
        read_file(nonexistent_file)

    # Verify error message is helpful
    error_msg = str(exc_info.value)
    assert "File not found" in error_msg
    assert str(nonexistent_file) in error_msg
    assert "check that the path exists" in error_msg


def test_read_file_empty(tmp_path: Path) -> None:
    """Verify read_file handles empty files correctly."""
    # Arrange
    test_file = tmp_path / "empty.txt"
    test_file.write_text("", encoding="utf-8")

    # Act
    content = read_file(test_file)

    # Assert
    assert content == ""


def test_write_file_success(tmp_path: Path) -> None:
    """Verify write_file creates file with correct content."""
    # Arrange
    test_file = tmp_path / "output.txt"
    expected_content = "Written by JIG\n"

    # Act
    write_file(test_file, expected_content)

    # Assert
    assert test_file.exists()
    assert test_file.read_text(encoding="utf-8") == expected_content


def test_write_file_creates_parent_dirs(tmp_path: Path) -> None:
    """Verify write_file creates parent directories if needed."""
    # Arrange
    test_file = tmp_path / "nested" / "dirs" / "file.txt"
    content = "Test content\n"

    # Act
    write_file(test_file, content)

    # Assert
    assert test_file.exists()
    assert test_file.read_text(encoding="utf-8") == content
    assert test_file.parent.exists()


def test_write_file_overwrites_existing(tmp_path: Path) -> None:
    """Verify write_file overwrites existing file."""
    # Arrange
    test_file = tmp_path / "overwrite.txt"
    test_file.write_text("Old content\n", encoding="utf-8")
    new_content = "New content\n"

    # Act
    write_file(test_file, new_content)

    # Assert
    assert test_file.read_text(encoding="utf-8") == new_content


def test_ensure_dir_creates_directory(tmp_path: Path) -> None:
    """Verify ensure_dir creates directory."""
    # Arrange
    test_dir = tmp_path / "new_directory"

    # Act
    ensure_dir(test_dir)

    # Assert
    assert test_dir.exists()
    assert test_dir.is_dir()


def test_ensure_dir_creates_nested_directories(tmp_path: Path) -> None:
    """Verify ensure_dir creates nested directories."""
    # Arrange
    test_dir = tmp_path / "level1" / "level2" / "level3"

    # Act
    ensure_dir(test_dir)

    # Assert
    assert test_dir.exists()
    assert test_dir.is_dir()


def test_ensure_dir_idempotent(tmp_path: Path) -> None:
    """Verify ensure_dir is idempotent (safe to call multiple times)."""
    # Arrange
    test_dir = tmp_path / "existing"
    test_dir.mkdir()

    # Act - Call twice
    ensure_dir(test_dir)
    ensure_dir(test_dir)

    # Assert - Should not raise error
    assert test_dir.exists()
    assert test_dir.is_dir()


def test_read_file_preserves_unicode(tmp_path: Path) -> None:
    """Verify read_file preserves unicode characters."""
    # Arrange
    test_file = tmp_path / "unicode.txt"
    unicode_content = "Hello 世界! Здравствуй мир! 🎉\n"
    test_file.write_text(unicode_content, encoding="utf-8")

    # Act
    content = read_file(test_file)

    # Assert
    assert content == unicode_content


def test_write_file_preserves_unicode(tmp_path: Path) -> None:
    """Verify write_file preserves unicode characters."""
    # Arrange
    test_file = tmp_path / "unicode_out.txt"
    unicode_content = "Bonjour! Привет! こんにちは! 🚀\n"

    # Act
    write_file(test_file, unicode_content)

    # Assert
    assert test_file.read_text(encoding="utf-8") == unicode_content
