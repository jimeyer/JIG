# ABOUTME: UniquenessRule detects duplicate values in a collection.
# ABOUTME: No auto-fix - duplicates require manual resolution.
"""UniquenessRule - validates uniqueness within a collection."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-018", "S-019")
@dataclass
class UniquenessRule:
    """Rule that validates uniqueness of values within a collection.

    Detects duplicates. No auto-fix since resolution requires human decision.

    Attributes:
        key_extractor: Function to extract the key from each artifact.
        artifact_filter: Optional filter to limit which artifacts to check.
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    key_extractor: Callable[[Any], str | None]
    artifact_filter: Callable[[Any], bool] | None = None
    _code: str = "UNIQUENESS"
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
        """Detect duplicate keys in artifacts."""
        # Build key -> list of artifacts mapping
        key_to_artifacts: dict[str, list[Any]] = defaultdict(list)

        for artifact in ctx.all_artifacts:
            # Apply filter if provided
            if self.artifact_filter and not self.artifact_filter(artifact):
                continue

            key = self.key_extractor(artifact)
            if key is not None:
                key_to_artifacts[key].append(artifact)

        # Find duplicates
        result = []
        for key, artifacts in key_to_artifacts.items():
            if len(artifacts) > 1:
                # Report violation for all but the first occurrence
                first_file = artifacts[0].file
                for artifact in artifacts[1:]:
                    result.append(
                        Violation(
                            rule_code=self.code,
                            artifact_id=artifact.id,
                            file=artifact.file,
                            line=None,
                            message=f"Duplicate ID '{key}' (also in {first_file})",
                            context={"duplicate_key": key, "first_file": first_file},
                        )
                    )
        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Duplicates require manual resolution - no auto-fix."""
        return Fix(
            action="resolve_duplicate",
            target=violation.file,
            params={"duplicate_key": violation.context.get("duplicate_key")},
            auto=False,
            suggestions=[
                "Rename one of the duplicates to a unique ID",
                "Delete the duplicate file",
                "Merge the duplicate content",
            ],
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Duplicates cannot be auto-applied."""
        raise NotImplementedError("UniquenessRule fixes require manual resolution")
