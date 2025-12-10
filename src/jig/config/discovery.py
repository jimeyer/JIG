"""Configuration file discovery for JIG.

Implements S-062: Configuration File Discovery
"""

from pathlib import Path
from typing import Optional

import jig

# Try tomllib (Python 3.11+), fall back to tomli
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found, no-redef]


# Search order for config files (first found wins)
CONFIG_FILE_NAMES = [
    "jig.toml",      # Dedicated JIG config (recommended)
    ".jig.toml",     # Hidden file variant
    "pyproject.toml",  # Python project config with [tool.jig]
]


@jig.implements("S-062")
def find_config_file(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Find JIG configuration file by searching up from start_dir.

    Search order (first found wins):
    1. jig.toml
    2. .jig.toml
    3. pyproject.toml (only if [tool.jig] section exists)

    Args:
        start_dir: Directory to start search from. Defaults to current working directory.

    Returns:
        Path to configuration file, or None if not found.
    """
    if start_dir is None:
        start_dir = Path.cwd()

    current = start_dir.resolve()

    # Walk up the directory tree
    while True:
        # Check each config file name in priority order
        for filename in CONFIG_FILE_NAMES:
            config_path = current / filename

            if config_path.is_file():
                # For pyproject.toml, verify [tool.jig] section exists
                if filename == "pyproject.toml":
                    if _has_tool_jig_section(config_path):
                        return config_path
                    # pyproject.toml without [tool.jig] - continue searching
                else:
                    return config_path

        # Move to parent directory
        parent = current.parent
        if parent == current:
            # Reached filesystem root
            break
        current = parent

    return None


def _has_tool_jig_section(pyproject_path: Path) -> bool:
    """Check if pyproject.toml has a [tool.jig] section.

    Args:
        pyproject_path: Path to pyproject.toml file.

    Returns:
        True if [tool.jig] section exists, False otherwise.
    """
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return "tool" in data and "jig" in data.get("tool", {})
    except Exception:
        # If we can't parse it, treat as not having [tool.jig]
        return False
