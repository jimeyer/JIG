# ABOUTME: ReferenceValidityRule validates that references point to existing artifacts.
# ABOUTME: Checks that IDs referenced in fields actually exist.
"""ReferenceValidityRule - validates references exist."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-020", "S-075", "S-079")
@dataclass
class ReferenceValidityRule:
    """Rule that validates references point to existing artifacts.

    Attributes:
        field: Name of the field containing references.
        valid_ids_fn: Function to get set of valid IDs from context.
        artifact_filter: Optional filter to limit which artifacts to check.
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    field: str
    valid_ids_fn: Callable[[Any], set[str]]
    artifact_filter: Callable[[Any], bool] | None = None
    _code: str = "REFERENCE_VALIDITY"
    _spec: str = "S-020"

    @property
    def code(self) -> str:
        """Unique identifier for this rule."""
        return self._code

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces."""
        return self._spec

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect references to non-existent artifacts."""
        valid_ids = self.valid_ids_fn(ctx)
        result = []

        for artifact in ctx.all_artifacts:
            # Apply filter if provided
            if self.artifact_filter and not self.artifact_filter(artifact):
                continue

            refs = artifact.frontmatter.get(self.field)
            if refs is None:
                continue

            # Handle both single ref and list of refs
            if isinstance(refs, str):
                refs = [refs]
            elif not isinstance(refs, list):
                continue

            for ref in refs:
                if ref not in valid_ids:
                    result.append(
                        Violation(
                            rule_code=self.code,
                            artifact_id=artifact.id,
                            file=artifact.file,
                            line=None,
                            message=f"Invalid reference in '{self.field}': '{ref}' does not exist",
                            context={
                                "field": self.field,
                                "invalid_ref": ref,
                            },
                        )
                    )
        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Invalid references require manual fix."""
        invalid_ref = violation.context.get("invalid_ref", "")
        return Fix(
            action="remove_field_value",
            target=violation.file,
            params={"field": self.field, "value": invalid_ref},
            auto=False,
            suggestions=[
                f"Create the missing artifact '{invalid_ref}'",
                f"Remove '{invalid_ref}' from {self.field}",
                f"Update '{invalid_ref}' to reference a valid artifact",
            ],
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Apply the fix using MendContext."""
        ctx.remove_field_value(fix.target, fix.params["field"], fix.params["value"])
