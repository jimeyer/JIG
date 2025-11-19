"""Core functionality for JIG: config, parsing, validation."""

from jig.core.config import JigConfig, load_config
from jig.core.parser import OSTCNode, parse_ostc_node

__all__ = ["JigConfig", "load_config", "OSTCNode", "parse_ostc_node"]
