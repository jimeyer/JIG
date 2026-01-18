# ABOUTME: RequiredFieldRule detects missing required fields in artifacts.
# ABOUTME: Generates set_field fix for auto-repair of missing fields.
"""RequiredFieldRule - validates required fields are present."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-018", "S-019")
@dataclass
class RequiredFieldRule:
    """Rule that validates required fields are present in artifacts.

    Attributes:
        _code: Unique rule code.
        _spec: Specification this rule enforces.
        field: Name of the required field.
        artifact_filter: Optional filter function to limit which artifacts to check.
        default_value: Default value to use in fix (if auto-fixable).
        auto_fix: Whether this can be auto-fixed.
    """

    field: str
    artifact_filter: Callable[[Any], bool] | None = None
    default_value: Any = None
    auto_fix: bool = True
    _code: str = "REQUIRED_FIELD"
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
        """Detect missing required fields in artifacts."""
        result = []
        for artifact in ctx.all_artifacts:
            # Apply filter if provided
            if self.artifact_filter and not self.artifact_filter(artifact):
                continue

            if self.field not in artifact.frontmatter:
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=artifact.id,
                        file=artifact.file,
                        line=None,
                        message=f"Missing required field '{self.field}'",
                        context={"field": self.field},
                    )
                )
        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Generate a set_field fix for missing field."""
        if not self.auto_fix:
            return Fix(
                action="set_field",
                target=violation.file,
                params={"field": self.field, "value": None},
                auto=False,
                suggestions=[f"Add '{self.field}' field to frontmatter"],
            )
        return Fix(
            action="set_field",
            target=violation.file,
            params={"field": self.field, "value": self.default_value},
            auto=True,
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Apply the fix using MendContext."""
        ctx.set_field(fix.target, fix.params["field"], fix.params["value"])
