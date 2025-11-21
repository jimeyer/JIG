# @jig C-JIGY-010 implements:S-JIGY-010 subsystem:jigy-tool interface:public
"""Annotation validator - validate @jig annotations against Intent graph.

Validates that code annotations reference valid Intent nodes, have correct
relationships, and maintain consistency with the Intent graph. Detects:
- Broken references (annotation targets don't exist)
- Invalid edge types (code verify instead of implement)
- Duplicate annotations
- Orphaned Intent nodes (specs without implementations)

Performance target: <1 second for 1000 annotations.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from jig.core.graph import Graph
from jig.core.scanner import Annotation, AnnotationScanner


@dataclass
class ValidationResult:
    """Result of annotation validation.

    Attributes:
        valid: True if validation passed with no errors
        errors: List of error messages (broken references, invalid types)
        warnings: List of warning messages (orphaned nodes, missing tests)
        annotations_checked: Number of annotations validated
        coverage: Optional coverage metrics dictionary
    """

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    annotations_checked: int = 0
    coverage: dict[str, float] = field(default_factory=dict)


class AnnotationValidator:
    """Validates @jig annotations against the Intent graph.

    Example:
        >>> validator = AnnotationValidator(Path("/path/to/project"))
        >>> result = validator.validate()
        >>> if not result.valid:
        ...     for error in result.errors:
        ...         print(f"Error: {error}")
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize annotation validator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.intent_dir = project_root / "jig"
        self.src_dirs = [project_root / "src", project_root / "test", project_root / "tests"]

    def validate(self, strict: bool = False) -> ValidationResult:
        """Validate all annotations against Intent graph.

        Args:
            strict: If True, warnings become errors

        Returns:
            ValidationResult with errors, warnings, and metrics
        """
        errors: list[str] = []
        warnings: list[str] = []

        # 1. Load Intent graph
        graph = self._load_intent_graph()

        # 2. Scan for annotations
        annotations = self._scan_annotations()

        # 3. Validate each annotation
        errors.extend(self._validate_node_ids(annotations))
        errors.extend(self._validate_relationships(annotations, graph))
        errors.extend(self._validate_edge_types(annotations, graph))
        errors.extend(self._detect_duplicates(annotations))

        # 4. Check for orphaned Intent nodes
        warnings.extend(self._find_orphaned_specs(graph, annotations))

        # 5. Calculate coverage metrics
        coverage = self._calculate_coverage(graph, annotations)

        # Determine success
        valid = len(errors) == 0 and (not strict or len(warnings) == 0)

        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            annotations_checked=len(annotations),
            coverage=coverage,
        )

    def _load_intent_graph(self) -> Graph:
        """Load Intent graph from jig/ directory.

        Returns:
            Graph object with O/S/C nodes
        """
        if not self.intent_dir.exists():
            # No Intent graph - return empty graph
            return Graph()

        try:
            graph = Graph.load_from_dir(self.intent_dir)
            return graph
        except Exception:
            # Failed to load - return empty graph
            return Graph()

    def _scan_annotations(self) -> list[Annotation]:
        """Scan source directories for @jig annotations.

        Returns:
            List of discovered annotations
        """
        scanner = AnnotationScanner()
        existing_dirs = [d for d in self.src_dirs if d.exists()]

        if not existing_dirs:
            return []

        annotations = scanner.scan(existing_dirs)
        return annotations

    def _validate_node_ids(self, annotations: list[Annotation]) -> list[str]:
        """Validate node ID format for all annotations.

        Args:
            annotations: List of annotations to check

        Returns:
            List of error messages for invalid IDs
        """
        errors: list[str] = []

        # Pattern: [CT]-[A-Z]+-\d+
        pattern = re.compile(r'^[CT]-[A-Z]+-\d+$')

        for annotation in annotations:
            if not pattern.match(annotation.id):
                errors.append(
                    f"Invalid node ID format '{annotation.id}' at {annotation.file}:{annotation.line}"
                )

        return errors

    def _validate_relationships(self, annotations: list[Annotation], graph: Graph) -> list[str]:
        """Validate that all relationship targets exist in graph.

        Args:
            annotations: List of annotations to check
            graph: Intent graph

        Returns:
            List of error messages for broken references
        """
        errors: list[str] = []

        for annotation in annotations:
            for rel_type, targets in annotation.relationships.items():
                for target in targets:
                    if target not in graph.nodes:
                        errors.append(
                            f"{annotation.id} {rel_type}:{target} - target doesn't exist "
                            f"(at {annotation.file}:{annotation.line})"
                        )

        return errors

    def _validate_edge_types(self, annotations: list[Annotation], graph: Graph) -> list[str]:
        """Validate edge type semantics (code implements, test verifies).

        Args:
            annotations: List of annotations to check
            graph: Intent graph

        Returns:
            List of error messages for invalid edge types
        """
        errors: list[str] = []

        for annotation in annotations:
            for rel_type, targets in annotation.relationships.items():
                # Check semantic validity
                if annotation.type == "code":
                    # Code nodes should implement or depend, not verify
                    if rel_type in ["verifies", "satisfies"]:
                        errors.append(
                            f"{annotation.id} uses '{rel_type}' but code nodes should 'implement' "
                            f"(at {annotation.file}:{annotation.line})"
                        )

                elif annotation.type == "test":
                    # Test nodes should verify, not implement
                    if rel_type in ["implements", "satisfies"]:
                        errors.append(
                            f"{annotation.id} uses '{rel_type}' but test nodes should 'verify' "
                            f"(at {annotation.file}:{annotation.line})"
                        )

                # Validate target node type (if target exists)
                for target in targets:
                    if target in graph.nodes:
                        target_node = graph.nodes[target]
                        
                        # Code can implement specs, tests can verify specs/outcomes
                        if annotation.type == "code" and rel_type == "implements":
                            if target_node.type not in ["specification", "outcome"]:
                                errors.append(
                                    f"{annotation.id} implements {target} but {target} is "
                                    f"type '{target_node.type}', expected specification"
                                )
                        
                        elif annotation.type == "test" and rel_type == "verifies":
                            if target_node.type not in ["specification", "outcome"]:
                                errors.append(
                                    f"{annotation.id} verifies {target} but {target} is "
                                    f"type '{target_node.type}', expected specification"
                                )

        return errors

    def _detect_duplicates(self, annotations: list[Annotation]) -> list[str]:
        """Detect duplicate annotation IDs across files.

        Args:
            annotations: List of annotations to check

        Returns:
            List of error messages for duplicates
        """
        errors: list[str] = []

        # Track seen annotations by ID
        seen: dict[str, Annotation] = {}

        for annotation in annotations:
            if annotation.id in seen:
                existing = seen[annotation.id]
                # Same file and line is not a duplicate (same annotation scanned twice)
                if existing.file != annotation.file or existing.line != annotation.line:
                    errors.append(
                        f"Duplicate annotation ID '{annotation.id}' found in "
                        f"{annotation.file}:{annotation.line} and "
                        f"{existing.file}:{existing.line}"
                    )
            else:
                seen[annotation.id] = annotation

        return errors

    def _find_orphaned_specs(self, graph: Graph, annotations: list[Annotation]) -> list[str]:
        """Find specification nodes without implementations or tests.

        Args:
            graph: Intent graph
            annotations: List of discovered annotations

        Returns:
            List of warning messages for orphaned specs
        """
        warnings: list[str] = []

        # Build index of what each spec has
        spec_implementations: dict[str, list[str]] = {}
        spec_verifications: dict[str, list[str]] = {}

        for annotation in annotations:
            for rel_type, targets in annotation.relationships.items():
                for target in targets:
                    if rel_type == "implements":
                        if target not in spec_implementations:
                            spec_implementations[target] = []
                        spec_implementations[target].append(annotation.id)
                    elif rel_type == "verifies":
                        if target not in spec_verifications:
                            spec_verifications[target] = []
                        spec_verifications[target].append(annotation.id)

        # Check each specification
        for node_id, node in graph.nodes.items():
            if node.type != "specification":
                continue

            # Skip non-active specs
            if node.status and node.status not in ["active", None]:
                continue

            # Check for implementation
            if node_id not in spec_implementations:
                warnings.append(f"{node_id} has no code implementation")

            # Check for verification
            if node_id not in spec_verifications:
                warnings.append(f"{node_id} has no test verification")

        return warnings

    def _calculate_coverage(self, graph: Graph, annotations: list[Annotation]) -> dict[str, float]:
        """Calculate coverage metrics.

        Args:
            graph: Intent graph
            annotations: List of discovered annotations

        Returns:
            Dictionary with coverage percentages
        """
        coverage: dict[str, float] = {}

        # Count active specs
        active_specs = [
            n for n in graph.nodes.values()
            if n.type == "specification" and n.status in ["active", None]
        ]

        if len(active_specs) == 0:
            return coverage

        # Count implemented specs
        implemented_specs = set()
        verified_specs = set()

        for annotation in annotations:
            for rel_type, targets in annotation.relationships.items():
                for target in targets:
                    if target in graph.nodes and graph.nodes[target].type == "specification":
                        if rel_type == "implements":
                            implemented_specs.add(target)
                        elif rel_type == "verifies":
                            verified_specs.add(target)

        # Calculate percentages
        total = len(active_specs)
        coverage['implementation'] = (len(implemented_specs) / total) * 100 if total > 0 else 0.0
        coverage['verification'] = (len(verified_specs) / total) * 100 if total > 0 else 0.0

        return coverage


def validate_annotations(project_root: Path, strict: bool = False) -> ValidationResult:
    """Convenience function to validate annotations.

    Args:
        project_root: Root directory of the project
        strict: If True, warnings become errors

    Returns:
        ValidationResult with errors and warnings

    Example:
        >>> result = validate_annotations(Path("/path/to/project"))
        >>> if not result.valid:
        ...     print(f"Found {len(result.errors)} errors")
    """
    validator = AnnotationValidator(project_root)
    return validator.validate(strict=strict)

