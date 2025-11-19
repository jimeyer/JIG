# @jig C-CORE-001 implements:S-JIG-002 subsystem:core interface:internal
"""Configuration loading and management for JIG."""

from dataclasses import dataclass
from pathlib import Path

import toml


@dataclass
class JigConfig:
    """JIG project configuration.

    Attributes:
        project_name: Name of the project using JIG
        intent_dir: Directory containing OSTC nodes (outcomes, specifications, tests, constraints)
        delta_dir: Directory containing work deltas (plans, commits)
        templates_dir: Directory containing node templates
        graph_index_file: Path to graph-index.yaml
        subsystems_file: Path to subsystems.yaml
    """

    project_name: str
    intent_dir: Path
    delta_dir: Path
    templates_dir: Path
    graph_index_file: Path
    subsystems_file: Path


def load_config(path: Path = Path("jig.toml")) -> JigConfig:
    """Load JIG configuration from jig.toml file.

    Args:
        path: Path to jig.toml file (default: jig.toml in current directory)

    Returns:
        JigConfig object with project configuration

    Raises:
        ValueError: If config file has invalid TOML syntax or required fields are invalid

    Note:
        If jig.toml is missing, returns default configuration with:
        - project_name: "default"
        - intent_dir: jig/
        - delta_dir: jig/deltas/
        - templates_dir: templates/
        - graph_index_file: jig/graph-index.yaml
        - subsystems_file: jig/subsystems.yaml
    """
    # Return defaults if config file doesn't exist
    if not path.exists():
        return _default_config()

    try:
        config_data = toml.load(path)
    except toml.TomlDecodeError as e:
        raise ValueError(f"Invalid TOML syntax in {path}: {e}") from e

    # Extract project section (optional, use defaults if missing)
    project_data = config_data.get("project", {})

    return JigConfig(
        project_name=project_data.get("name", "default"),
        intent_dir=Path(project_data.get("intent_dir", "jig")),
        delta_dir=Path(project_data.get("delta_dir", "jig/deltas")),
        templates_dir=Path(project_data.get("templates_dir", "templates")),
        graph_index_file=Path(project_data.get("graph_index_file", "jig/graph-index.yaml")),
        subsystems_file=Path(project_data.get("subsystems_file", "jig/subsystems.yaml")),
    )


def _default_config() -> JigConfig:
    """Return default JIG configuration.

    Returns:
        JigConfig with default values for all fields
    """
    return JigConfig(
        project_name="default",
        intent_dir=Path("jig"),
        delta_dir=Path("jig/deltas"),
        templates_dir=Path("templates"),
        graph_index_file=Path("jig/graph-index.yaml"),
        subsystems_file=Path("jig/subsystems.yaml"),
    )
