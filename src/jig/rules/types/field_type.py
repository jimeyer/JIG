# ABOUTME: FieldTypeRule validates field values are of expected type.
# ABOUTME: Generates coercion fix if type conversion is possible.
"""FieldTypeRule - validates field type constraints."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-018", "S-019", "S-037")
@dataclass
class FieldTypeRule:
    """Rule that validates field values are of expected type.

    Attributes:
        field: Name of the field to check.
        expected_type: Expected Python type (e.g., list, int, str).
        coercer: Optional function to coerce to correct type.
        artifact_filter: Optional filter to limit which artifacts to check.
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    field: str
    expected_type: type
    coercer: Callable[[Any], Any] | None = None
    artifact_filter: Callable[[Any], bool] | None = None
    _code: str = "FIELD_TYPE"
    _spec: str = "S-018"

    @property
    def code(self) -> str:
        """Unique identifier for this rule."""
        return self._code

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces."""
        return self._spec

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect fields with incorrect type."""
        result = []
        for artifact in ctx.all_artifacts:
            # Apply filter if provided
            if self.artifact_filter and not self.artifact_filter(artifact):
                continue

            if self.field not in artifact.frontmatter:
                # Missing field is handled by RequiredFieldRule
                continue

            value = artifact.frontmatter[self.field]
            if not isinstance(value, self.expected_type):
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=artifact.id,
                        file=artifact.file,
                        line=None,
                        message=f"Field '{self.field}' must be {self.expected_type.__name__}, got {type(value).__name__}",
                        context={
                            "field": self.field,
                            "expected_type": self.expected_type.__name__,
                            "actual_type": type(value).__name__,
                            "value": value,
                        },
                    )
                )
        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Generate a coercion fix if coercer is available."""
        if self.coercer is None:
            return Fix(
                action="set_field",
                target=violation.file,
                params={"field": self.field, "value": None},
                auto=False,
                suggestions=[
                    f"Change '{self.field}' to type {violation.context.get('expected_type')}"
                ],
            )

        try:
            original_value = violation.context.get("value")
            coerced = self.coercer(original_value)
            return Fix(
                action="set_field",
                target=violation.file,
                params={"field": self.field, "value": coerced},
                auto=True,
            )
        except Exception:
            return Fix(
                action="set_field",
                target=violation.file,
                params={"field": self.field, "value": None},
                auto=False,
                suggestions=[f"Cannot coerce value to {violation.context.get('expected_type')}"],
            )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Apply the fix using MendContext."""
        ctx.set_field(fix.target, fix.params["field"], fix.params["value"])
