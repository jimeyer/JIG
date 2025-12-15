"""
Data models for validation results and errors.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidationError:
    """Represents a single validation error."""

    file: str
    message: str
    line: Optional[int] = None
    code: Optional[str] = None
    severity: str = "error"
    field: Optional[str] = None

    def __str__(self) -> str:
        location = self.file
        if self.line is not None:
            location = f"{self.file}:{self.line}"
        return f"ERROR: {location}\n  - {self.message}"


@dataclass
class ValidationResult:
    """Represents the result of a validation phase."""

    passed: bool
    errors: list[ValidationError] = field(default_factory=list)
    phase_name: str = ""
    items_checked: int = 0
    detail: Optional[str] = None  # Optional additional detail for display

    def add_error(self, error: ValidationError) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.passed = False

    def __str__(self) -> str:
        # Build the display string
        if self.detail:
            display = f"{self.detail}"
        else:
            display = f"{self.items_checked} files"

        if self.passed:
            return f"✓ Validating {self.phase_name} ({display})"
        else:
            return f"✗ Validating {self.phase_name} ({display})"
