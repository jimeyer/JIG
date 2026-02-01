# ABOUTME: FilenameSyncRule validates filename matches frontmatter ID and title.
# ABOUTME: Generates rename_file fix for auto-repair.
"""FilenameSyncRule - validates filename matches frontmatter."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation
from jig.rules.types import to_snake_case

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-018", "S-019", "S-076")
@dataclass
class FilenameSyncRule:
    """Rule that validates filename matches frontmatter ID and title.

    Expected format: {ID}_{Title_In_Snake_Case}.md

    Attributes:
        artifact_filter: Optional filter to limit which artifacts to check.
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    artifact_filter: Callable[[Any], bool] | None = None
    _code: str = "FILENAME_SYNC"
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
        """Detect filenames that don't match frontmatter."""
        result = []
        for artifact in ctx.all_artifacts:
            # Apply filter if provided
            if self.artifact_filter and not self.artifact_filter(artifact):
                continue

            # Skip Charter - different naming convention
            if artifact.id == "Charter":
                continue

            doc_id = artifact.frontmatter.get("id", "")
            title = artifact.frontmatter.get("title", "")

            if not title:
                # Missing title is handled by RequiredFieldRule
                continue

            expected_snake = to_snake_case(title)
            expected_filename = f"{doc_id}_{expected_snake}.md"
            actual_filename = Path(artifact.file).name

            if actual_filename != expected_filename:
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=artifact.id,
                        file=artifact.file,
                        line=None,
                        message=f"Filename mismatch: expected '{expected_filename}', got '{actual_filename}'",
                        context={
                            "expected": expected_filename,
                            "actual": actual_filename,
                            "doc_id": doc_id,
                            "title": title,
                        },
                    )
                )
        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Generate a rename_file fix."""
        expected = violation.context.get("expected", "")
        current_path = Path(violation.file)
        new_path = current_path.parent / expected

        return Fix(
            action="rename_file",
            target=violation.file,
            params={"new_path": str(new_path)},
            auto=True,
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Rename file is handled by mend engine, not MendContext directly."""
        # File renames are a special action handled externally
        raise NotImplementedError("rename_file action is handled by mend engine")
