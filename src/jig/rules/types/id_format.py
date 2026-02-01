# ABOUTME: IdFormatRule validates ID fields match expected patterns.
# ABOUTME: Generates normalized ID fix when pattern is recoverable.
"""IdFormatRule - validates ID format patterns."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-018", "S-019", "S-035")
@dataclass
class IdFormatRule:
    """Rule that validates ID fields match expected patterns.

    Attributes:
        pattern: Regex pattern the ID must match.
        normalizer: Optional function to normalize malformed IDs.
        artifact_filter: Optional filter to limit which artifacts to check.
        field_name: Name of the ID field (default: "id").
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    pattern: str
    normalizer: Callable[[str], str] | None = None
    artifact_filter: Callable[[Any], bool] | None = None
    field_name: str = "id"
    _code: str = "ID_FORMAT"
    _spec: str = "S-018"
    _compiled_pattern: re.Pattern = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Compile the regex pattern."""
        self._compiled_pattern = re.compile(self.pattern)

    @property
    def code(self) -> str:
        """Unique identifier for this rule."""
        return self._code

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces."""
        return self._spec

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect IDs that don't match the expected pattern."""
        result = []
        for artifact in ctx.all_artifacts:
            # Apply filter if provided
            if self.artifact_filter and not self.artifact_filter(artifact):
                continue

            id_value = artifact.frontmatter.get(self.field_name)
            if id_value is None:
                # Missing ID is handled by RequiredFieldRule
                continue

            if not self._compiled_pattern.match(str(id_value)):
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=artifact.id,
                        file=artifact.file,
                        line=None,
                        message=f"Invalid ID format: '{id_value}' (expected pattern: {self.pattern})",
                        context={
                            "field": self.field_name,
                            "value": id_value,
                            "pattern": self.pattern,
                        },
                    )
                )
        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Generate a normalized ID fix if normalizer is available."""
        if self.normalizer is None:
            return Fix(
                action="set_field",
                target=violation.file,
                params={"field": self.field_name, "value": None},
                auto=False,
                suggestions=[f"Update '{self.field_name}' to match pattern: {self.pattern}"],
            )

        raw_value = violation.context.get("value", "")
        normalized = self.normalizer(str(raw_value))

        # Check if normalized value matches pattern
        if not self._compiled_pattern.match(normalized):
            return Fix(
                action="set_field",
                target=violation.file,
                params={"field": self.field_name, "value": None},
                auto=False,
                suggestions=[f"Cannot normalize '{raw_value}' to valid format"],
            )

        return Fix(
            action="set_field",
            target=violation.file,
            params={"field": self.field_name, "value": normalized},
            auto=True,
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Apply the fix using MendContext."""
        ctx.set_field(fix.target, fix.params["field"], fix.params["value"])
