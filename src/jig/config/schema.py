"""Configuration schema and loading for JIG.

Implements S-064: Path Configuration with Defaults
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import jig
from jig.config.discovery import find_config_file
from jig.config.parser import parse_config_file


# Default path values
DEFAULT_SOURCE = "src"
DEFAULT_TESTS = "test"
DEFAULT_JIG_ROOT = "jig"
DEFAULT_SPECIFICATIONS = "specifications"
DEFAULT_OUTCOMES = "outcomes"
DEFAULT_BRICKS = "bricks.yaml"
DEFAULT_GENERATED = "generated"


@dataclass
class PathsConfig:
    """Configuration for all JIG-related paths.

    All paths are resolved to absolute paths relative to project_root.
    """

    source: Path
    tests: Path
    jig_root: Path
    specifications: Path
    outcomes: Path
    bricks: Path
    generated: Path


@dataclass
class JigConfig:
    """Complete JIG configuration.

    Attributes:
        paths: All path configurations, resolved to absolute paths.
        project_root: The root directory of the project.
        config_file_path: Path to the config file used, or None if using defaults.
        has_config_file: True if a config file was found and loaded.
    """

    paths: PathsConfig
    project_root: Path
    config_file_path: Optional[Path]
    has_config_file: bool


@jig.implements("S-064")
def load_config(project_root: Optional[Path] = None) -> JigConfig:
    """Load JIG configuration with defaults.

    Searches for configuration in the project root directory and merges
    with default values. All paths are resolved to absolute paths.

    Args:
        project_root: The root directory of the project. If None, uses
                     current working directory.

    Returns:
        Complete JigConfig with all paths resolved.
    """
    if project_root is None:
        project_root = Path.cwd()

    project_root = project_root.resolve()

    # Find and parse config file
    config_file = find_config_file(start_dir=project_root)
    raw_config: dict[str, Any] = {}

    if config_file is not None:
        raw_config = parse_config_file(config_file)

    # Extract paths configuration
    paths_config = _extract_paths_config(raw_config, project_root)

    return JigConfig(
        paths=paths_config,
        project_root=project_root,
        config_file_path=config_file,
        has_config_file=config_file is not None,
    )


def _extract_paths_config(raw_config: dict[str, Any], project_root: Path) -> PathsConfig:
    """Extract and resolve paths configuration from raw config.

    Args:
        raw_config: Parsed configuration dictionary.
        project_root: Project root for resolving relative paths.

    Returns:
        PathsConfig with all paths resolved to absolute.
    """
    # Navigate to paths section (may be nested under "jig")
    paths_dict = _get_paths_dict(raw_config)

    # Get jig_root first as other paths may be relative to it
    jig_root_str = paths_dict.get("jig_root", DEFAULT_JIG_ROOT)
    jig_root = project_root / jig_root_str

    # Source and tests are relative to project_root
    source = project_root / paths_dict.get("source", DEFAULT_SOURCE)
    tests = project_root / paths_dict.get("tests", DEFAULT_TESTS)

    # These are relative to jig_root
    specifications = jig_root / paths_dict.get("specifications", DEFAULT_SPECIFICATIONS)
    outcomes = jig_root / paths_dict.get("outcomes", DEFAULT_OUTCOMES)
    bricks = jig_root / paths_dict.get("bricks", DEFAULT_BRICKS)
    generated = jig_root / paths_dict.get("generated", DEFAULT_GENERATED)

    return PathsConfig(
        source=source,
        tests=tests,
        jig_root=jig_root,
        specifications=specifications,
        outcomes=outcomes,
        bricks=bricks,
        generated=generated,
    )


def _get_paths_dict(raw_config: dict[str, Any]) -> dict[str, Any]:
    """Extract paths dictionary from raw config.

    Handles both structures:
    - jig.toml: {"jig": {"paths": {...}}} or {"paths": {...}}
    - pyproject.toml [tool.jig]: {"paths": {...}}

    Args:
        raw_config: Parsed configuration dictionary.

    Returns:
        The paths dictionary, or empty dict if not found.
    """
    # Check for nested structure: {"jig": {"paths": {...}}}
    if "jig" in raw_config:
        jig_section = raw_config["jig"]
        if isinstance(jig_section, dict):
            return jig_section.get("paths", {})

    # Check for flat structure: {"paths": {...}}
    if "paths" in raw_config:
        return raw_config["paths"]

    return {}
