# ABOUTME: IsolationRule validates no cross-boundary dependencies.
# ABOUTME: Used for tower isolation and other partition-based constraints.
"""IsolationRule - validates no cross-boundary dependencies."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-088", "S-089")
@dataclass
class IsolationRule:
    """Rule that validates no cross-boundary dependencies.

    Ensures nodes in different partitions (e.g., towers) don't depend on each other.

    Attributes:
        partition_fn: Function to get node -> partition mapping.
        edges_fn: Function to get dependency edges as (source, target) pairs.
        skip_if_single: If True, skip validation when only one partition exists.
        node_label: Label for nodes in error messages.
        partition_label: Label for partitions in error messages.
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    partition_fn: Callable[[Any], dict[str, str | None]]
    edges_fn: Callable[[Any], list[tuple[str, str]]]
    skip_if_single: bool = True
    node_label: str = "brick"
    partition_label: str = "tower"
    _code: str = "ISOLATION"
    _spec: str = "S-088"

    @property
    def code(self) -> str:
        """Unique identifier for this rule."""
        return self._code

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces."""
        return self._spec

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect cross-boundary dependencies."""
        partitions = self.partition_fn(ctx)
        edges = self.edges_fn(ctx)

        # Check if we should skip (single partition)
        if self.skip_if_single:
            unique_partitions = {p for p in partitions.values() if p is not None}
            if len(unique_partitions) <= 1:
                return []

        result = []

        for source, target in edges:
            source_partition = partitions.get(source)
            target_partition = partitions.get(target)

            # Treat None as "default" partition
            source_partition = source_partition or "default"
            target_partition = target_partition or "default"

            if source_partition != target_partition:
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=source,
                        file="",  # Isolation violations are cross-file
                        line=None,
                        message=f"Cross-{self.partition_label} dependency: {source} ({self.partition_label}: {source_partition}) depends on {target} ({self.partition_label}: {target_partition})",
                        context={
                            "source": source,
                            "target": target,
                            "source_partition": source_partition,
                            "target_partition": target_partition,
                        },
                    )
                )

        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Isolation violations require manual resolution."""
        source = violation.context.get("source", "")
        target = violation.context.get("target", "")
        return Fix(
            action="resolve_isolation_violation",
            target="",
            params={
                "source": source,
                "target": target,
            },
            auto=False,
            suggestions=[
                f"Move '{source}' and '{target}' to the same {self.partition_label}",
                f"Remove the dependency from '{source}' to '{target}'",
                "Use intent specifications instead of direct code imports",
            ],
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Isolation fixes require manual resolution."""
        raise NotImplementedError("IsolationRule fixes require manual resolution")
