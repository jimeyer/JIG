# ABOUTME: Context classes for validation and mending: ValidationContext and MendContext.
# ABOUTME: ValidationContext loads artifacts; MendContext batches and commits repairs.
"""
Context classes for the JIG rules engine.

Provides:
- ValidationContext: Loads all artifacts into a queryable structure for rule execution.
- MendContext: Batches modifications and commits them atomically.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

import jig
from jig.rules.base import Artifact


def _parse_frontmatter(file_path: Path) -> dict[str, Any] | None:
    """Parse YAML frontmatter from a markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Frontmatter dict, or None if parsing fails.
    """
    try:
        content = file_path.read_text()
        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        return yaml.safe_load(parts[1])
    except Exception:
        return None


def _load_artifacts_from_dir(
    directory: Path, pattern: str, project_root: Path
) -> tuple[dict[str, Artifact], dict[str, Artifact]]:
    """Load artifacts from a directory matching a glob pattern.

    Args:
        directory: Directory to search.
        pattern: Glob pattern (e.g., "S-*.md").
        project_root: Project root for relative path computation.

    Returns:
        Tuple of (artifacts_by_id, orphan_artifacts_by_path).
        Orphan artifacts are those with missing or empty IDs.
    """
    artifacts: dict[str, Artifact] = {}
    orphans: dict[str, Artifact] = {}
    if not directory.exists():
        return artifacts, orphans

    for file_path in sorted(directory.glob(pattern)):
        frontmatter = _parse_frontmatter(file_path)
        if frontmatter is None:
            continue

        artifact_id = frontmatter.get("id")
        relative_path = str(file_path.relative_to(project_root))

        if not artifact_id:
            # Store as orphan with file path as key
            orphans[relative_path] = Artifact(
                id="",  # Empty ID
                file=relative_path,
                frontmatter=frontmatter,
            )
            continue
        artifacts[artifact_id] = Artifact(
            id=artifact_id,
            file=relative_path,
            frontmatter=frontmatter,
        )

    return artifacts, orphans


@jig.implements("S-109")
@dataclass
class ValidationContext:
    """Context for rule validation, providing access to all JIG artifacts.

    Loads specifications, outcomes, architectures, goals, charter, bricks,
    and implementation graph data from the JIG directory structure.

    Attributes:
        project_root: Root directory of the JIG project.
        specifications: Dict mapping spec ID to Artifact.
        outcomes: Dict mapping outcome ID to Artifact.
        architectures: Dict mapping architecture ID to Artifact.
        goals: Dict mapping goal ID to Artifact.
        charter: The Charter artifact, or None if not present.
        bricks: List of brick definitions from bricks.yaml.
        impl_graph_nodes: List of nodes from implementation graph.
        impl_graph_edges: List of call edges from implementation graph.
    """

    project_root: Path
    specifications: dict[str, Artifact] = field(default_factory=dict)
    outcomes: dict[str, Artifact] = field(default_factory=dict)
    architectures: dict[str, Artifact] = field(default_factory=dict)
    goals: dict[str, Artifact] = field(default_factory=dict)
    charter: Artifact | None = None
    bricks: list[dict[str, Any]] = field(default_factory=list)
    impl_graph_nodes: list[dict[str, Any]] = field(default_factory=list)
    impl_graph_edges: list[dict[str, Any]] = field(default_factory=list)
    # Files with missing or invalid IDs, keyed by file path
    orphan_artifacts: dict[str, Artifact] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Load all artifacts after initialization."""
        jig_dir = self.project_root / "jig"
        all_orphans: dict[str, Artifact] = {}

        # Load specifications
        self.specifications, spec_orphans = _load_artifacts_from_dir(
            jig_dir / "specifications", "S-*.md", self.project_root
        )
        all_orphans.update(spec_orphans)

        # Load outcomes
        self.outcomes, outcome_orphans = _load_artifacts_from_dir(
            jig_dir / "outcomes", "O-*.md", self.project_root
        )
        all_orphans.update(outcome_orphans)

        # Load architectures
        self.architectures, arch_orphans = _load_artifacts_from_dir(
            jig_dir / "architecture", "A-*.md", self.project_root
        )
        all_orphans.update(arch_orphans)

        # Store all orphans
        self.orphan_artifacts = all_orphans

        # Load goals (ignore orphans for goals - goals are usually defined in Charter)
        self.goals, _ = _load_artifacts_from_dir(
            jig_dir / "goals", "G-*.md", self.project_root
        )

        # Load charter - try Charter.md first, then any Charter_*.md
        self.charter = None
        charter_path = jig_dir / "Charter.md"
        if charter_path.exists():
            frontmatter = _parse_frontmatter(charter_path)
            if frontmatter is not None and frontmatter.get("id") == "Charter":
                self.charter = Artifact(
                    id="Charter",
                    file=str(charter_path.relative_to(self.project_root)),
                    frontmatter=frontmatter,
                )
        # Try Charter_*.md pattern if Charter.md not found
        if self.charter is None:
            for charter_candidate in sorted(jig_dir.glob("Charter_*.md")):
                frontmatter = _parse_frontmatter(charter_candidate)
                if frontmatter is not None and frontmatter.get("id") == "Charter":
                    self.charter = Artifact(
                        id="Charter",
                        file=str(charter_candidate.relative_to(self.project_root)),
                        frontmatter=frontmatter,
                    )
                    break

        # Load bricks
        bricks_path = jig_dir / "bricks.yaml"
        if bricks_path.exists():
            try:
                bricks_data = yaml.safe_load(bricks_path.read_text())
                if bricks_data and "bricks" in bricks_data:
                    self.bricks = bricks_data["bricks"]
            except Exception:
                pass

        # Load implementation graph
        impl_graph_path = jig_dir / "generated" / "implementation-graph.ndjson"
        if impl_graph_path.exists():
            try:
                with impl_graph_path.open() as f:
                    for line in f:
                        item = json.loads(line)
                        if item.get("type") == "calls":
                            self.impl_graph_edges.append(item)
                        elif "id" in item and "type" in item:
                            self.impl_graph_nodes.append(item)
            except Exception:
                pass

    def get(self, artifact_id: str) -> Artifact | None:
        """Get an artifact by ID.

        Searches specifications, outcomes, architectures, goals, and charter.

        Args:
            artifact_id: The artifact ID (e.g., "S-001", "O-001").

        Returns:
            The Artifact if found, None otherwise.
        """
        if artifact_id in self.specifications:
            return self.specifications[artifact_id]
        if artifact_id in self.outcomes:
            return self.outcomes[artifact_id]
        if artifact_id in self.architectures:
            return self.architectures[artifact_id]
        if artifact_id in self.goals:
            return self.goals[artifact_id]
        if artifact_id == "Charter" and self.charter:
            return self.charter
        return None

    @property
    def all_artifacts(self) -> list[Artifact]:
        """Return all loaded artifacts as a list, including orphans."""
        result = list(self.specifications.values())
        result.extend(self.outcomes.values())
        result.extend(self.architectures.values())
        result.extend(self.goals.values())
        if self.charter:
            result.append(self.charter)
        # Include orphan artifacts so rules can detect missing IDs
        result.extend(self.orphan_artifacts.values())
        return result

    # =========================================================================
    # Brick Validation Helpers
    # =========================================================================

    def get_function_ids(self) -> set[str]:
        """Get all function IDs from implementation graph."""
        return {
            node["id"]
            for node in self.impl_graph_nodes
            if node.get("type") == "function"
        }

    def get_brick_to_functions(self) -> dict[str, list[str]]:
        """Get mapping from brick ID to list of function IDs it contains.

        Module units (M-) expand to all functions in that module.
        Class units (C-) expand to all methods of that class.
        Function units (F-) are direct function references.
        """
        brick_to_funcs: dict[str, list[str]] = {}

        for brick in self.bricks:
            brick_id = brick.get("id", "unknown")
            units = brick.get("units", [])
            expanded = self._expand_units_to_functions(units)
            brick_to_funcs[brick_id] = list(expanded)

        return brick_to_funcs

    def _expand_units_to_functions(self, units: list[str]) -> set[str]:
        """Expand module/class/function units to function IDs."""
        expanded: set[str] = set()

        for unit in units:
            if unit.startswith("M-"):
                # Module: expand to all functions in that module
                module_path = unit[2:]  # Remove "M-" prefix
                for node in self.impl_graph_nodes:
                    if node.get("type") == "function":
                        func_id = node["id"]
                        # F-auth.session.login matches M-auth.session
                        if func_id.startswith(f"F-{module_path}."):
                            expanded.add(func_id)
            elif unit.startswith("C-"):
                # Class: expand to all methods
                class_path = unit[2:]  # Remove "C-" prefix
                for node in self.impl_graph_nodes:
                    if node.get("type") == "function":
                        func_id = node["id"]
                        # F-auth.Token.__init__ matches C-auth.Token
                        if func_id.startswith(f"F-{class_path}."):
                            expanded.add(func_id)
            elif unit.startswith("F-"):
                # Function: direct reference
                expanded.add(unit)

        return expanded

    def get_brick_layers(self) -> dict[str, int]:
        """Get mapping from brick ID to layer number."""
        return {
            brick["id"]: brick["layer"]
            for brick in self.bricks
            if "id" in brick and "layer" in brick and isinstance(brick["layer"], int)
        }

    def get_brick_towers(self) -> dict[str, str | None]:
        """Get mapping from brick ID to tower name (None if no tower)."""
        return {
            brick["id"]: brick.get("tower")
            for brick in self.bricks
            if "id" in brick
        }

    def get_brick_dependency_edges(self) -> list[tuple[str, str]]:
        """Get brick dependency edges derived from function call edges.

        Returns list of (source_brick, target_brick) tuples.
        Only includes cross-brick dependencies.
        """
        # Build function -> brick mapping
        func_to_brick: dict[str, str] = {}
        for brick in self.bricks:
            brick_id = brick.get("id", "unknown")
            units = brick.get("units", [])
            expanded = self._expand_units_to_functions(units)
            for func_id in expanded:
                func_to_brick[func_id] = brick_id

        # Extract brick dependencies from call edges
        edges: list[tuple[str, str]] = []
        for edge in self.impl_graph_edges:
            source_func = edge.get("source")
            target_func = edge.get("target")

            if not source_func or not target_func:
                continue

            source_brick = func_to_brick.get(source_func)
            target_brick = func_to_brick.get(target_func)

            # Both functions must be in bricks
            if not source_brick or not target_brick:
                continue

            # Skip self-dependencies (same brick)
            if source_brick == target_brick:
                continue

            edges.append((source_brick, target_brick))

        return edges

    def get_brick_dependency_graph(self) -> dict[str, set[str]]:
        """Get brick dependency graph as adjacency list.

        Returns dict mapping brick ID to set of brick IDs it depends on.
        """
        graph: dict[str, set[str]] = defaultdict(set)
        for source, target in self.get_brick_dependency_edges():
            graph[source].add(target)
        return dict(graph)


@dataclass
class _PendingChange:
    """Represents a pending change to a file."""

    action: str
    file: str
    params: dict[str, Any]


@jig.implements("S-105", "S-106")
@dataclass
class MendContext:
    """Context for applying fixes, with batched modifications.

    Changes are batched until commit() is called, allowing rollback
    if something goes wrong.

    Attributes:
        project_root: Root directory of the JIG project.
        pending_changes: List of pending changes to apply on commit.
    """

    project_root: Path
    pending_changes: list[_PendingChange] = field(default_factory=list)

    def set_field(self, file: str, field_name: str, value: Any) -> None:
        """Set a frontmatter field to a value.

        Args:
            file: Path to the file (relative or absolute).
            field_name: Name of the field to set.
            value: Value to set.
        """
        self.pending_changes.append(
            _PendingChange(
                action="set_field",
                file=file,
                params={"field": field_name, "value": value},
            )
        )

    def add_field_value(self, file: str, field_name: str, value: Any) -> None:
        """Append a value to an array field.

        Args:
            file: Path to the file.
            field_name: Name of the array field.
            value: Value to append.
        """
        self.pending_changes.append(
            _PendingChange(
                action="add_field_value",
                file=file,
                params={"field": field_name, "value": value},
            )
        )

    def remove_field_value(self, file: str, field_name: str, value: Any) -> None:
        """Remove a value from an array field.

        Args:
            file: Path to the file.
            field_name: Name of the array field.
            value: Value to remove.
        """
        self.pending_changes.append(
            _PendingChange(
                action="remove_field_value",
                file=file,
                params={"field": field_name, "value": value},
            )
        )

    def delete_field(self, file: str, field_name: str) -> None:
        """Delete a field from frontmatter.

        Args:
            file: Path to the file.
            field_name: Name of the field to delete.
        """
        self.pending_changes.append(
            _PendingChange(
                action="delete_field",
                file=file,
                params={"field": field_name},
            )
        )

    def rename_file(self, old_path: str, new_path: str) -> None:
        """Rename a file to a new path.

        Args:
            old_path: Current file path.
            new_path: New file path.
        """
        self.pending_changes.append(
            _PendingChange(
                action="rename_file",
                file=old_path,
                params={"new_path": new_path},
            )
        )

    def sync_title(
        self, file: str, direction: Literal["to_h1", "to_frontmatter"]
    ) -> None:
        """Sync H1 heading and frontmatter title.

        Args:
            file: Path to the file.
            direction: Direction of sync:
                - "to_h1": Copy frontmatter title to H1 heading
                - "to_frontmatter": Copy H1 heading to frontmatter title
        """
        self.pending_changes.append(
            _PendingChange(
                action="sync_title",
                file=file,
                params={"direction": direction},
            )
        )

    def set_h1(self, file: str, heading: str) -> None:
        """Set the H1 heading.

        Args:
            file: Path to the file.
            heading: New H1 heading text.
        """
        self.pending_changes.append(
            _PendingChange(
                action="set_h1",
                file=file,
                params={"heading": heading},
            )
        )

    def rollback(self) -> None:
        """Discard all pending changes."""
        self.pending_changes.clear()

    def commit(self) -> None:
        """Apply all pending changes to files.

        Applies changes in order using the mend actions module.
        """
        for change in self.pending_changes:
            self._apply_change(change)

        # Clear pending changes
        self.pending_changes.clear()

    def _apply_change(self, change: _PendingChange) -> None:
        """Apply a single change using mend actions.

        Args:
            change: The change to apply.
        """
        # Import here to avoid circular imports
        from jig.mend.actions import (
            apply_add_field_value,
            apply_delete_field,
            apply_remove_field_value,
            apply_rename_file,
            apply_set_field,
            apply_set_h1,
            apply_sync_title,
        )

        file_path = Path(change.file)
        if not file_path.is_absolute():
            file_path = self.project_root / file_path

        if change.action == "set_field":
            apply_set_field(file_path, change.params["field"], change.params["value"])
        elif change.action == "add_field_value":
            apply_add_field_value(
                file_path, change.params["field"], change.params["value"]
            )
        elif change.action == "remove_field_value":
            apply_remove_field_value(
                file_path, change.params["field"], change.params["value"]
            )
        elif change.action == "delete_field":
            apply_delete_field(file_path, change.params["field"])
        elif change.action == "rename_file":
            new_path = Path(change.params["new_path"])
            if not new_path.is_absolute():
                new_path = self.project_root / new_path
            apply_rename_file(file_path, new_path)
        elif change.action == "sync_title":
            apply_sync_title(file_path, change.params["direction"])
        elif change.action == "set_h1":
            apply_set_h1(file_path, change.params["heading"])
