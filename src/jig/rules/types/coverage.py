# ABOUTME: CoverageRule validates every item in a collection is covered.
# ABOUTME: Checks that all items are referenced at least once.
"""CoverageRule - validates complete coverage."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-042", "S-043")
@dataclass
class CoverageRule:
    """Rule that validates every item in a collection is covered.

    Checks that all items are referenced at least once by another set.

    Attributes:
        items_fn: Function to get items that need coverage.
        references_fn: Function to get all references from covering artifacts.
        message_template: Template for error message (use {item_id}).
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    items_fn: Callable[[Any], dict[str, Any]]
    references_fn: Callable[[Any], set[str]]
    message_template: str = "Item '{item_id}' is not covered by any reference"
    _code: str = "COVERAGE"
    _spec: str = "S-043"

    @property
    def code(self) -> str:
        """Unique identifier for this rule."""
        return self._code

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces."""
        return self._spec

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect items that are not covered by any reference."""
        items = self.items_fn(ctx)
        references = self.references_fn(ctx)
        result = []

        for item_id, artifact in items.items():
            if item_id not in references:
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=item_id,
                        file=artifact.file,
                        line=None,
                        message=self.message_template.format(item_id=item_id),
                        context={"item_id": item_id},
                    )
                )

        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Coverage gaps require manual fix."""
        item_id = violation.context.get("item_id", "")
        return Fix(
            action="add_reference",
            target=violation.file,
            params={"item_id": item_id},
            auto=False,
            suggestions=[
                f"Add '{item_id}' to a covering artifact's reference list",
                f"Create a new covering artifact that references '{item_id}'",
            ],
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Coverage fixes require manual resolution."""
        raise NotImplementedError("CoverageRule fixes require manual resolution")
