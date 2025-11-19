# @jig T-CORE-001 verifies:S-JIG-002 subsystem:core
"""Unit tests for config loading and management."""

from pathlib import Path

import pytest
import toml

from jig.core.config import JigConfig, load_config


def test_load_config_valid(tmp_path: Path) -> None:
    """Verify config loads from valid jig.toml."""
    config_file = tmp_path / "jig.toml"
    config_data = {
        "project": {
            "name": "test-project",
            "intent_dir": "custom/intent",
            "delta_dir": "custom/deltas",
            "templates_dir": "custom/templates",
            "graph_index_file": "custom/graph.yaml",
            "subsystems_file": "custom/subsystems.yaml",
        }
    }
    config_file.write_text(toml.dumps(config_data))

    config = load_config(config_file)

    assert config.project_name == "test-project"
    assert config.intent_dir == Path("custom/intent")
    assert config.delta_dir == Path("custom/deltas")
    assert config.templates_dir == Path("custom/templates")
    assert config.graph_index_file == Path("custom/graph.yaml")
    assert config.subsystems_file == Path("custom/subsystems.yaml")


# @jig T-CORE-002 verifies:S-JIG-002 subsystem:core
def test_load_config_defaults(tmp_path: Path) -> None:
    """Verify defaults used when jig.toml missing."""
    config_file = tmp_path / "nonexistent.toml"

    config = load_config(config_file)

    assert config.project_name == "default"
    assert config.intent_dir == Path("jig")
    assert config.delta_dir == Path("jig/deltas")
    assert config.templates_dir == Path("templates")
    assert config.graph_index_file == Path("jig/graph-index.yaml")
    assert config.subsystems_file == Path("jig/subsystems.yaml")


def test_load_config_partial(tmp_path: Path) -> None:
    """Verify partial config uses defaults for missing fields."""
    config_file = tmp_path / "jig.toml"
    config_data = {
        "project": {
            "name": "partial-project",
            "intent_dir": "custom/intent",
            # Other fields missing - should use defaults
        }
    }
    config_file.write_text(toml.dumps(config_data))

    config = load_config(config_file)

    assert config.project_name == "partial-project"
    assert config.intent_dir == Path("custom/intent")
    assert config.delta_dir == Path("jig/deltas")  # Default
    assert config.templates_dir == Path("templates")  # Default


def test_load_config_empty_project_section(tmp_path: Path) -> None:
    """Verify empty project section uses all defaults."""
    config_file = tmp_path / "jig.toml"
    config_data = {"project": {}}
    config_file.write_text(toml.dumps(config_data))

    config = load_config(config_file)

    assert config.project_name == "default"
    assert config.intent_dir == Path("jig")
    assert config.delta_dir == Path("jig/deltas")


def test_load_config_invalid_toml(tmp_path: Path) -> None:
    """Verify error on malformed TOML."""
    config_file = tmp_path / "jig.toml"
    config_file.write_text("invalid toml syntax [[[")

    with pytest.raises(ValueError, match="Invalid TOML syntax"):
        load_config(config_file)


def test_load_config_no_project_section(tmp_path: Path) -> None:
    """Verify config with no project section uses defaults."""
    config_file = tmp_path / "jig.toml"
    config_data = {"other": {"key": "value"}}
    config_file.write_text(toml.dumps(config_data))

    config = load_config(config_file)

    assert config.project_name == "default"
    assert config.intent_dir == Path("jig")


def test_jig_config_dataclass() -> None:
    """Verify JigConfig dataclass can be instantiated correctly."""
    config = JigConfig(
        project_name="test",
        intent_dir=Path("jig"),
        delta_dir=Path("jig/deltas"),
        templates_dir=Path("templates"),
        graph_index_file=Path("jig/graph-index.yaml"),
        subsystems_file=Path("jig/subsystems.yaml"),
    )

    assert config.project_name == "test"
    assert isinstance(config.intent_dir, Path)
    assert isinstance(config.delta_dir, Path)
