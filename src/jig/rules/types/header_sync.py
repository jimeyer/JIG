# ABOUTME: HeaderSyncRule validates H1 heading matches frontmatter title.
# ABOUTME: Generates sync_title fix for auto-repair.
"""HeaderSyncRule - validates H1 matches frontmatter title."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-018", "S-019", "S-076")
@dataclass
class HeaderSyncRule:
    """Rule that validates first H1 heading matches frontmatter title.

    The H1 must exactly match the frontmatter title.
    The H1 must NOT include an ID prefix (e.g., "# A-001: Title" is invalid).

    Attributes:
        artifact_filter: Optional filter to limit which artifacts to check.
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    artifact_filter: Callable[[Any], bool] | None = None
    _code: str = "HEADER_SYNC"
    _spec: str = "S-018"

    @property
    def code(self) -> str:
        """Unique identifier for this rule."""
        return self._code

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces."""
        return self._spec

    def _extract_h1(self, file_path: str, project_root: Path) -> str | None:
        """Extract first H1 header from document body."""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = project_root / path

            content = path.read_text()

            # Skip frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    body = parts[2]
                else:
                    body = content
            else:
                body = content

            # Find first H1 header
            h1_pattern = re.compile(r"^#\s+(.+)$", re.MULTILINE)
            match = h1_pattern.search(body)

            if match:
                return match.group(1).strip()
            return None
        except Exception:
            return None

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect H1 headers that don't match frontmatter title."""
        result = []
        for artifact in ctx.all_artifacts:
            # Apply filter if provided
            if self.artifact_filter and not self.artifact_filter(artifact):
                continue

            title = artifact.frontmatter.get("title", "")
            if not title:
                # Missing title is handled by RequiredFieldRule
                continue

            h1 = self._extract_h1(artifact.file, ctx.project_root)

            if h1 is None:
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=artifact.id,
                        file=artifact.file,
                        line=None,
                        message="Missing H1 header",
                        context={"title": title, "h1": None, "missing": True},
                    )
                )
            elif h1 != title:
                # Check if H1 has ID prefix
                id_prefix_pattern = re.compile(r"^[AOSGH]-\d{1,3}:\s*")
                has_prefix = id_prefix_pattern.match(h1) is not None

                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=artifact.id,
                        file=artifact.file,
                        line=None,
                        message=f"H1 does not match title: '{h1}' != '{title}'",
                        context={
                            "title": title,
                            "h1": h1,
                            "has_id_prefix": has_prefix,
                        },
                    )
                )
        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Generate a sync_title fix."""
        title = violation.context.get("title", "")
        return Fix(
            action="sync_title",
            target=violation.file,
            params={"title": title},
            auto=True,
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """sync_title action is handled by mend engine."""
        raise NotImplementedError("sync_title action is handled by mend engine")
