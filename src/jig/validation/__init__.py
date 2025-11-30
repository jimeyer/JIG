"""
Validation module for JIG artifacts.

This module provides validation for:
- Intent artifacts (specifications, outcomes, decorators)
- Brick definitions and partition constraints
"""

from jig.validation.models import ValidationError, ValidationResult

__all__ = ["ValidationError", "ValidationResult"]
