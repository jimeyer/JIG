"""File I/O utilities for JIG (Jig Intent Graph).

This module provides safe, type-checked file operations with clear error handling.
"""

# @jig C-UTIL-001 implements:S-JIG-002 subsystem:core interface:internal

from pathlib import Path


def read_file(path: Path) -> str:
    """Read file contents, raise clear error if missing.

    Args:
        path: Path to file to read

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file does not exist (with helpful message)
        PermissionError: If file cannot be read due to permissions
        OSError: For other I/O errors

    Example:
        >>> content = read_file(Path("jig/outcomes/O-JIG-001.md"))
    """
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"File not found: {path}\n"
            f"Please check that the path exists and is spelled correctly."
        ) from e
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied reading file: {path}\n"
            f"Please check file permissions."
        ) from e


def write_file(path: Path, content: str) -> None:
    """Write file, create parent dirs if needed.

    Args:
        path: Path to file to write
        content: String content to write

    Raises:
        PermissionError: If file or directory cannot be written due to permissions
        OSError: For other I/O errors

    Example:
        >>> write_file(Path("jig/outcomes/O-TEST-001.md"), "# Test\\n")
    """
    try:
        # Ensure parent directory exists
        ensure_dir(path.parent)
        path.write_text(content, encoding="utf-8")
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied writing file: {path}\n"
            f"Please check file and directory permissions."
        ) from e


def ensure_dir(path: Path) -> None:
    """Create directory and parents if they don't exist.

    Args:
        path: Path to directory to create

    Raises:
        PermissionError: If directory cannot be created due to permissions
        OSError: For other I/O errors

    Example:
        >>> ensure_dir(Path("jig/outcomes"))
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied creating directory: {path}\n"
            f"Please check parent directory permissions."
        ) from e
