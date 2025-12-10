"""JIG configuration module."""

from jig.config.discovery import find_config_file
from jig.config.parser import parse_config_file, ConfigError

__all__ = ["find_config_file", "parse_config_file", "ConfigError"]
