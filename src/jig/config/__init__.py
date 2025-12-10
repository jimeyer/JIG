"""JIG configuration module."""

from jig.config.discovery import find_config_file
from jig.config.parser import parse_config_file, ConfigError
from jig.config.schema import load_config, JigConfig, PathsConfig

__all__ = [
    "find_config_file",
    "parse_config_file",
    "ConfigError",
    "load_config",
    "JigConfig",
    "PathsConfig",
]
