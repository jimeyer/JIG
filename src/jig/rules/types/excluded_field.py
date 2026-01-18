# ABOUTME: ExcludedFieldRule detects forbidden fields in artifacts.
# ABOUTME: Generates delete_field fix for auto-repair.
"""ExcludedFieldRule - validates excluded fields are not present."""

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
class ExcludedFieldRule:
    """Rule that validates excluded fields are not present in artifacts.

    Attributes:
        field: Name of the forbidden field.
        artifact_filter: Optional filter to limit which artifacts to check.
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    field: str
    artifact_filter: Callable[[Any], bool] | None = None
    _code: str = "EXCLUDED_FIELD"
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
        """Detect excluded fields that are present in artifacts."""
        result = []
        for artifact in ctx.all_artifacts:
            # Apply filter if provided
            if self.artifact_filter and not self.artifact_filter(artifact):
                continue

            if self.field in artifact.frontmatter:
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=artifact.id,
                        file=artifact.file,
                        line=None,
                        message=f"Excluded field '{self.field}' must not be present",
                        context={"field": self.field},
                    )
                )
        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Generate a delete_field fix."""
        return Fix(
            action="delete_field",
            target=violation.file,
            params={"field": self.field},
            auto=True,
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Apply the fix using MendContext."""
        ctx.delete_field(fix.target, fix.params["field"])
