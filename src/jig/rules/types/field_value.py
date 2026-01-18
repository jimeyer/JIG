# ABOUTME: FieldValueRule validates field values against a predicate.
# ABOUTME: Reports violations when predicate returns False.
"""FieldValueRule - validates field values against predicates."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-037", "S-072", "S-073")
@dataclass
class FieldValueRule:
    """Rule that validates field values against a predicate.

    Attributes:
        field: Name of the field to check.
        predicate: Function returning True if value is valid.
        message_fn: Function to generate error message from value.
        artifact_filter: Optional filter to limit which artifacts to check.
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    field: str
    predicate: Callable[[Any], bool]
    message_fn: Callable[[Any], str] | None = None
    artifact_filter: Callable[[Any], bool] | None = None
    _code: str = "FIELD_VALUE"
    _spec: str = "S-037"

    @property
    def code(self) -> str:
        """Unique identifier for this rule."""
        return self._code

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces."""
        return self._spec

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect fields with invalid values."""
        result = []
        for artifact in ctx.all_artifacts:
            # Apply filter if provided
            if self.artifact_filter and not self.artifact_filter(artifact):
                continue

            if self.field not in artifact.frontmatter:
                # Missing field is handled by RequiredFieldRule
                continue

            value = artifact.frontmatter[self.field]
            if not self.predicate(value):
                if self.message_fn:
                    message = self.message_fn(value)
                else:
                    message = f"Field '{self.field}' has invalid value: {value}"

                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=artifact.id,
                        file=artifact.file,
                        line=None,
                        message=message,
                        context={"field": self.field, "value": value},
                    )
                )
        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Field value violations typically require manual fix."""
        return Fix(
            action="set_field",
            target=violation.file,
            params={"field": self.field, "value": None},
            auto=False,
            suggestions=[f"Update '{self.field}' to a valid value"],
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Apply the fix using MendContext."""
        ctx.set_field(fix.target, fix.params["field"], fix.params["value"])
