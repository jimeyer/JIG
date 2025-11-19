"""YAML processing utilities for JIG (Jig Intent Graph).

This module provides safe YAML loading and dumping with consistent formatting.
"""

# @jig C-UTIL-002 implements:S-JIG-002 subsystem:core interface:internal

from pathlib import Path
from typing import Any

import yaml

from jig.utils.io import read_file, write_file


def load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML file, raise on parse errors.

    Args:
        path: Path to YAML file to load

    Returns:
        Parsed YAML as dictionary

    Raises:
        FileNotFoundError: If file does not exist
        yaml.YAMLError: If YAML is malformed (with helpful message)
        ValueError: If YAML root is not a dictionary

    Example:
        >>> config = load_yaml(Path("jig.toml"))
    """
    content = read_file(path)

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(
            f"Failed to parse YAML file: {path}\n"
            f"Error: {e}\n"
            f"Please check YAML syntax (indentation, colons, quotes)."
        ) from e

    if data is None:
        # Empty file is treated as empty dict
        return {}

    if not isinstance(data, dict):
        raise ValueError(
            f"YAML file must contain a dictionary at root level: {path}\n"
            f"Found: {type(data).__name__}"
        )

    return data


def dump_yaml(data: dict[str, Any], path: Path) -> None:
    """Write YAML with consistent formatting.

    Args:
        data: Dictionary to write as YAML
        path: Path to YAML file to write

    Raises:
        PermissionError: If file cannot be written
        yaml.YAMLError: If data cannot be serialized to YAML

    Example:
        >>> dump_yaml({"version": "1.0", "nodes": []}, Path("jig/graph-index.yaml"))
    """
    try:
        # Use default_flow_style=False for block style (more readable)
        # Use sort_keys=False to preserve insertion order (Python 3.7+)
        # Use allow_unicode=True to avoid escaping unicode characters
        content = yaml.safe_dump(
            data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            indent=2,
        )
        write_file(path, content)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(
            f"Failed to serialize data to YAML: {e}\n"
            f"Please check that all values are YAML-serializable."
        ) from e
