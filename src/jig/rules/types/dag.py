# ABOUTME: DAGRule validates that a graph is acyclic.
# ABOUTME: Detects and reports cycles in dependency graphs.
"""DAGRule - validates directed acyclic graph property."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jig
from jig.rules.base import Fix, Violation

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@jig.implements("S-039")
@dataclass
class DAGRule:
    """Rule that validates a graph is acyclic (DAG property).

    Attributes:
        graph_fn: Function to get adjacency list from context.
        node_label: Label for nodes in error messages (e.g., "brick").
        _code: Unique rule code.
        _spec: Specification this rule enforces.
    """

    graph_fn: Callable[[Any], dict[str, set[str]]]
    node_label: str = "node"
    _code: str = "DAG"
    _spec: str = "S-039"

    @property
    def code(self) -> str:
        """Unique identifier for this rule."""
        return self._code

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces."""
        return self._spec

    def _detect_cycles(self, graph: dict[str, set[str]]) -> list[list[str]]:
        """Detect all cycles in directed graph using DFS."""
        visited: set[str] = set()
        rec_stack: set[str] = set()
        rec_stack_list: list[str] = []
        cycles: list[list[str]] = []
        cycles_set: set[tuple[str, ...]] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            rec_stack_list.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start_idx = rec_stack_list.index(neighbor)
                    cycle = rec_stack_list[cycle_start_idx:] + [neighbor]
                    # Normalize cycle to avoid duplicates
                    normalized = self._normalize_cycle(cycle[:-1])
                    cycle_key = tuple(normalized)
                    if cycle_key not in cycles_set:
                        cycles_set.add(cycle_key)
                        cycles.append(normalized)

            rec_stack_list.pop()
            rec_stack.remove(node)

        # Get all nodes
        all_nodes = set(graph.keys())
        for neighbor_set in graph.values():
            all_nodes.update(neighbor_set)

        for node in all_nodes:
            if node not in visited:
                dfs(node)

        return cycles

    def _normalize_cycle(self, cycle: list[str]) -> list[str]:
        """Normalize cycle to start from lexicographically smallest node."""
        if not cycle:
            return cycle
        min_idx = cycle.index(min(cycle))
        return cycle[min_idx:] + cycle[:min_idx]

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect cycles in the graph."""
        graph = self.graph_fn(ctx)
        cycles = self._detect_cycles(graph)
        result = []

        for cycle in cycles:
            cycle_path = " -> ".join(cycle) + f" -> {cycle[0]}"
            result.append(
                Violation(
                    rule_code=self.code,
                    artifact_id=cycle[0],  # Use first node in cycle as artifact ID
                    file="",  # Cycles are cross-file
                    line=None,
                    message=f"Circular dependency detected: {cycle_path}",
                    context={"cycle": cycle},
                )
            )

        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Cycles require manual resolution."""
        cycle = violation.context.get("cycle", [])
        return Fix(
            action="break_cycle",
            target="",
            params={"cycle": cycle},
            auto=False,
            suggestions=[
                "Remove one of the dependencies in the cycle",
                "Extract shared functionality to break the cycle",
                f"Reconsider the {self.node_label} structure",
            ],
        )

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Cycle fixes require manual resolution."""
        raise NotImplementedError("DAGRule fixes require manual resolution")
