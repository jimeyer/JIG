# ABOUTME: BidirectionalLinkRule validates A<->B link consistency.
# ABOUTME: Checks that if A references B, then B references A.
"""BidirectionalLinkRule - validates bidirectional link consistency."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-095")
@dataclass
class BidirectionalLinkRule:
    """Rule that validates bidirectional link consistency.

    If artifact A's forward_field contains B, then B's back_field must contain A.

    Attributes:
        forward_field: Field on A containing references to B.
        back_field: Field on B that should reference back to A.
        source_filter: Filter for source artifacts (A).
        target_filter: Filter for target artifacts (B).
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    forward_field: str
    back_field: str
    source_filter: Callable[[Any], bool] | None = None
    target_filter: Callable[[Any], bool] | None = None
    _code: str = "BIDIRECTIONAL_LINK"
    _spec: str = "S-095"

    @property
    def code(self) -> str:
        """Unique identifier for this rule."""
        return self._code

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces."""
        return self._spec

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect bidirectional link inconsistencies."""
        result = []

        # Build index of target artifacts
        target_index: dict[str, Any] = {}
        for artifact in ctx.all_artifacts:
            if self.target_filter and not self.target_filter(artifact):
                continue
            target_index[artifact.id] = artifact

        # Check forward references
        for source in ctx.all_artifacts:
            if self.source_filter and not self.source_filter(source):
                continue

            forward_refs = source.frontmatter.get(self.forward_field)
            if forward_refs is None:
                continue

            if isinstance(forward_refs, str):
                forward_refs = [forward_refs]
            elif not isinstance(forward_refs, list):
                continue

            for target_id in forward_refs:
                target = target_index.get(target_id)
                if target is None:
                    # Missing target is handled by ReferenceValidityRule
                    continue

                back_refs = target.frontmatter.get(self.back_field)
                if back_refs is None:
                    back_refs = []
                elif isinstance(back_refs, str):
                    back_refs = [back_refs]
                elif not isinstance(back_refs, list):
                    continue

                if source.id not in back_refs:
                    result.append(
                        Violation(
                            rule_code=self.code,
                            artifact_id=target_id,
                            file=target.file,
                            line=None,
                            message=(
                                f"Bidirectional inconsistency: '{source.id}' references "
                                f"'{target_id}' in {self.forward_field}, but '{target_id}' "
                                f"does not list '{source.id}' in {self.back_field}"
                            ),
                            context={
                                "source_id": source.id,
                                "target_id": target_id,
                                "forward_field": self.forward_field,
                                "back_field": self.back_field,
                                "missing_back_ref": source.id,
                            },
                        )
                    )

        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Generate an add_field_value fix to restore bidirectional link."""
        missing_ref = violation.context.get("missing_back_ref", "")
        back_field = violation.context.get("back_field", self.back_field)

        return Fix(
            action="add_field_value",
            target=violation.file,
            params={"field": back_field, "value": missing_ref},
            auto=True,
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Apply the fix using MendContext."""
        ctx.add_field_value(fix.target, fix.params["field"], fix.params["value"])
