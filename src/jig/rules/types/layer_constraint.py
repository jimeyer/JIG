# ABOUTME: LayerConstraintRule validates layer hierarchy constraints.
# ABOUTME: Ensures layer N only depends on layers < N (or layer 0 on layer 0).
"""LayerConstraintRule - validates layer hierarchy."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-038")
@dataclass
class LayerConstraintRule:
    """Rule that validates layer hierarchy constraints.

    Layer N can only depend on layers < N.
    Layer 0 can depend on layer 0 (same-layer dependencies allowed at foundation).

    Attributes:
        layers_fn: Function to get node -> layer mapping.
        edges_fn: Function to get dependency edges as (source, target) pairs.
        node_label: Label for nodes in error messages.
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    layers_fn: Callable[[Any], dict[str, int]]
    edges_fn: Callable[[Any], list[tuple[str, str]]]
    node_label: str = "brick"
    _code: str = "LAYER_CONSTRAINT"
    _spec: str = "S-038"

    @property
    def code(self) -> str:
        """Unique identifier for this rule."""
        return self._code

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces."""
        return self._spec

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect layer constraint violations."""
        layers = self.layers_fn(ctx)
        edges = self.edges_fn(ctx)
        result = []

        for source, target in edges:
            source_layer = layers.get(source)
            target_layer = layers.get(target)

            if source_layer is None or target_layer is None:
                # Missing layer info is handled elsewhere
                continue

            violation = False
            reason = ""

            if source_layer == 0:
                # Layer 0 can only depend on layer 0
                if target_layer != 0:
                    violation = True
                    reason = f"Layer 0 {self.node_label}s can only depend on other layer 0 {self.node_label}s, not layer {target_layer}"
            else:
                # Layer N (N > 0) can only depend on layer < N
                if target_layer >= source_layer:
                    violation = True
                    if target_layer == source_layer:
                        reason = f"Same-layer dependencies are only allowed at layer 0, not layer {source_layer}"
                    else:
                        reason = f"Layer {source_layer} cannot depend on layer {target_layer} (upward dependency)"

            if violation:
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=source,
                        file="",  # Layer violations are cross-file
                        line=None,
                        message=f"Layer constraint violation: {source} (layer {source_layer}) depends on {target} (layer {target_layer}). {reason}",
                        context={
                            "source": source,
                            "target": target,
                            "source_layer": source_layer,
                            "target_layer": target_layer,
                            "reason": reason,
                        },
                    )
                )

        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Layer violations require manual resolution."""
        source = violation.context.get("source", "")
        target = violation.context.get("target", "")
        return Fix(
            action="resolve_layer_violation",
            target="",
            params={
                "source": source,
                "target": target,
            },
            auto=False,
            suggestions=[
                f"Move '{source}' to a higher layer",
                f"Move '{target}' to a lower layer",
                f"Remove the dependency from '{source}' to '{target}'",
            ],
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Layer fixes require manual resolution."""
        raise NotImplementedError("LayerConstraintRule fixes require manual resolution")
