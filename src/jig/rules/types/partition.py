# ABOUTME: PartitionRule validates partition property (no gaps, no overlaps).
# ABOUTME: Ensures every item belongs to exactly one container.
"""PartitionRule - validates partition property."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-022")
@dataclass
class PartitionRule:
    """Rule that validates partition property (no gaps, no overlaps).

    Every item must belong to exactly one container.

    Attributes:
        items_fn: Function to get all items that need partitioning.
        containers_fn: Function to get containers with their item lists.
        item_label: Label for items in error messages (e.g., "function").
        container_label: Label for containers (e.g., "brick").
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    items_fn: Callable[[Any], set[str]]
    containers_fn: Callable[[Any], dict[str, list[str]]]
    item_label: str = "item"
    container_label: str = "container"
    _code: str = "PARTITION"
    _spec: str = "S-022"

    @property
    def code(self) -> str:
        """Unique identifier for this rule."""
        return self._code

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces."""
        return self._spec

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect partition violations (gaps and overlaps)."""
        items = self.items_fn(ctx)
        containers = self.containers_fn(ctx)
        result = []

        # Build item -> containers mapping
        item_to_containers: dict[str, list[str]] = defaultdict(list)
        for container_id, container_items in containers.items():
            for item_id in container_items:
                item_to_containers[item_id].append(container_id)

        # Detect gaps (items in 0 containers)
        for item_id in items:
            container_count = len(item_to_containers.get(item_id, []))
            if container_count == 0:
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=item_id,
                        file="",  # Partition violations are cross-file
                        line=None,
                        message=f"Partition gap: {self.item_label} '{item_id}' belongs to 0 {self.container_label}s",
                        context={
                            "item_id": item_id,
                            "violation_type": "gap",
                        },
                    )
                )
            elif container_count > 1:
                # Detect overlaps (items in 2+ containers)
                container_ids = item_to_containers[item_id]
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=item_id,
                        file="",  # Partition violations are cross-file
                        line=None,
                        message=f"Partition overlap: {self.item_label} '{item_id}' belongs to multiple {self.container_label}s: {', '.join(container_ids)}",
                        context={
                            "item_id": item_id,
                            "container_ids": container_ids,
                            "violation_type": "overlap",
                        },
                    )
                )

        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Partition violations require manual fix."""
        violation_type = violation.context.get("violation_type", "gap")
        item_id = violation.context.get("item_id", "")

        if violation_type == "gap":
            return Fix(
                action="add_to_container",
                target="",
                params={"item_id": item_id},
                auto=False,
                suggestions=[
                    f"Add '{item_id}' to an existing {self.container_label}",
                    f"Create a new {self.container_label} containing '{item_id}'",
                ],
            )
        else:  # overlap
            container_ids = violation.context.get("container_ids", [])
            return Fix(
                action="resolve_overlap",
                target="",
                params={"item_id": item_id, "container_ids": container_ids},
                auto=False,
                suggestions=[
                    f"Remove '{item_id}' from all but one {self.container_label}",
                    f"Choose which {self.container_label} should own '{item_id}'",
                ],
            )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Partition fixes require manual resolution."""
        raise NotImplementedError("PartitionRule fixes require manual resolution")
