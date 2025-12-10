"""TOML configuration file parsing for JIG.

Implements S-063: TOML Configuration Parsing
"""

from pathlib import Path
from typing import Any

import jig

# Try tomllib (Python 3.11+), fall back to tomli
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found, no-redef]


class ConfigError(Exception):
    """Error raised when configuration parsing fails."""

    pass


@jig.implements("S-063")
def parse_config_file(config_path: Path) -> dict[str, Any]:
    """Parse a JIG configuration file.

    For jig.toml and .jig.toml:
        - Returns the entire parsed content
        - If [jig] section exists, returns full structure
        - If no [jig] section, returns root level as config

    For pyproject.toml:
        - Extracts only the [tool.jig] section
        - Raises ConfigError if [tool.jig] section doesn't exist

    Args:
        config_path: Path to the configuration file.

    Returns:
        Parsed configuration as a dictionary.

    Raises:
        ConfigError: If file doesn't exist, has invalid TOML syntax,
                    or pyproject.toml lacks [tool.jig] section.
    """
    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(
            f"Invalid TOML syntax in {config_path.name}: {e}"
        ) from e

    # Handle pyproject.toml specially - extract [tool.jig] section
    if config_path.name == "pyproject.toml":
        return _extract_tool_jig_section(data, config_path)

    # For jig.toml and .jig.toml, return as-is
    return data


def _extract_tool_jig_section(data: dict[str, Any], config_path: Path) -> dict[str, Any]:
    """Extract [tool.jig] section from pyproject.toml data.

    Args:
        data: Parsed pyproject.toml content.
        config_path: Path to the file (for error messages).

    Returns:
        Contents of [tool.jig] section.

    Raises:
        ConfigError: If [tool.jig] section doesn't exist.
    """
    tool = data.get("tool", {})
    jig_config = tool.get("jig")

    if jig_config is None:
        raise ConfigError(
            f"pyproject.toml at {config_path} does not contain [tool.jig] section"
        )

    return jig_config
