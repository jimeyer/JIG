# ABOUTME: Rules engine module for JIG validation and mending.
# ABOUTME: Exports Rule protocol, Violation, Fix, Artifact, and context classes.
"""
Rules engine for JIG validation.

This module provides:
- Rule protocol: interface for validation rules
- Violation: represents a detected validation error
- Fix: represents a repair action template
- Artifact: represents a JIG artifact (spec, outcome, etc.)
- ValidationContext: loads artifacts for rule execution
- MendContext: batches and commits repairs
"""

from jig.rules.base import Artifact, Fix, Rule, Violation, compute_error_id
from jig.rules.context import MendContext, ValidationContext

__all__ = [
    "Artifact",
    "Fix",
    "MendContext",
    "Rule",
    "ValidationContext",
    "Violation",
    "compute_error_id",
]
