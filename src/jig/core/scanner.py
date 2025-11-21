# @jig C-JIGY-008 implements:S-JIGY-008 subsystem:jigy-tool interface:public
"""Fast scanner for @jig annotations in source files.

Scans source and test directories for @jig annotations that mark Code (C-*)
and Test (T-*) nodes. Extracts node metadata, relationships, and file locations.

Performance target: <2 seconds for 10,000 files.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Annotation:
    """Represents a discovered @jig annotation in source code.

    Attributes:
        id: Node ID (e.g., C-AUTH-001, T-AUTH-001)
        type: Node type (code or test, inferred from C-/T- prefix)
        file: File path where annotation was found
        line: Line number where annotation appears
        relationships: Dictionary of relationship types to target node IDs
        metadata: Dictionary of metadata key-value pairs
    """

    id: str
    type: str
    file: str
    line: int
    relationships: dict[str, list[str]] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)


def parse_annotation_line(line: str) -> Annotation | None:
    """Parse a single line containing a @jig annotation.

    Expected format:
        # @jig <NODE-ID> <RELATIONS> <METADATA>

    Where:
        - NODE-ID: [CT]-[A-Z]+-\\d+ (e.g., C-AUTH-001, T-AUTH-001)
        - RELATIONS: key:value[,value] pairs (e.g., implements:S-001,S-002)
        - METADATA: key:value pairs (e.g., subsystem:auth interface:public)

    Args:
        line: Source code line potentially containing annotation

    Returns:
        Annotation object if line matches format, None otherwise

    Example:
        >>> line = "# @jig C-AUTH-001 implements:S-AUTH-001 subsystem:auth"
        >>> annotation = parse_annotation_line(line)
        >>> annotation.id
        'C-AUTH-001'
        >>> annotation.relationships
        {'implements': ['S-AUTH-001']}
    """
    # Pattern matches: # @jig <NODE-ID> <rest>
    # NODE-ID format: [CT]-[A-Z]+-\d+
    pattern = re.compile(
        r'^\s*#\s*@jig\s+([CT]-[A-Z]+-\d+)\s+(.*)$'
    )
    
    match = pattern.match(line)
    if not match:
        return None
    
    node_id = match.group(1)
    rest = match.group(2).strip()
    
    # Infer type from prefix
    node_type = "code" if node_id.startswith("C-") else "test"
    
    # Parse relationships and metadata
    relationships: dict[str, list[str]] = {}
    metadata: dict[str, str] = {}
    
    # Relationship keys (have list values)
    relation_keys = {"implements", "verifies", "satisfies", "depends", "depends_on"}
    
    # Split rest into key:value pairs
    parts = rest.split()
    for part in parts:
        if ":" not in part:
            continue
        
        key, value = part.split(":", 1)
        key = key.strip()
        value = value.strip()
        
        if key in relation_keys:
            # Relationship: split comma-separated values
            targets = [v.strip() for v in value.split(",")]
            relationships[key] = targets
        else:
            # Metadata: single value
            metadata[key] = value
    
    return Annotation(
        id=node_id,
        type=node_type,
        file="",  # Will be set by scanner
        line=0,   # Will be set by scanner
        relationships=relationships,
        metadata=metadata,
    )


class AnnotationScanner:
    """Fast scanner for @jig annotations in source files.

    Scans Python files in source and test directories to discover @jig
    annotations marking Code and Test nodes.

    Performance: <2 seconds for 10,000 files using pure Python implementation.

    Example:
        >>> scanner = AnnotationScanner()
        >>> annotations = scanner.scan([Path("src"), Path("test")])
        >>> len(annotations)
        42
        >>> annotations[0].id
        'C-AUTH-001'
    """

    def __init__(self) -> None:
        """Initialize annotation scanner."""
        self.file_extensions = [".py"]  # Supported file extensions

    def scan_file(self, file_path: Path) -> list[Annotation]:
        """Scan a single file for @jig annotations.

        Args:
            file_path: Path to file to scan

        Returns:
            List of annotations found in the file

        Example:
            >>> scanner = AnnotationScanner()
            >>> annotations = scanner.scan_file(Path("src/auth.py"))
        """
        annotations: list[Annotation] = []

        if not file_path.exists():
            return annotations

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    annotation = parse_annotation_line(line)
                    if annotation:
                        # Set file and line info
                        annotation.file = str(file_path)
                        annotation.line = line_num
                        annotations.append(annotation)
        except (OSError, UnicodeDecodeError):
            # Skip files we can't read (binary, permission errors, etc.)
            pass

        return annotations

    def scan_directory(self, directory: Path) -> list[Annotation]:
        """Scan a directory recursively for @jig annotations.

        Only processes files with supported extensions (.py by default).

        Args:
            directory: Root directory to scan

        Returns:
            List of all annotations found in directory tree

        Example:
            >>> scanner = AnnotationScanner()
            >>> annotations = scanner.scan_directory(Path("src"))
        """
        annotations: list[Annotation] = []

        if not directory.exists() or not directory.is_dir():
            return annotations

        # Recursively find all Python files
        for ext in self.file_extensions:
            for file_path in directory.rglob(f"*{ext}"):
                if file_path.is_file():
                    file_annotations = self.scan_file(file_path)
                    annotations.extend(file_annotations)

        return annotations

    def scan(self, directories: list[Path]) -> list[Annotation]:
        """Scan multiple directories for @jig annotations.

        Args:
            directories: List of directory paths to scan

        Returns:
            Combined list of annotations from all directories

        Example:
            >>> scanner = AnnotationScanner()
            >>> annotations = scanner.scan([Path("src"), Path("test")])
        """
        all_annotations: list[Annotation] = []

        for directory in directories:
            annotations = self.scan_directory(directory)
            all_annotations.extend(annotations)

        return all_annotations

    def find_duplicates(self, annotations: list[Annotation]) -> dict[str, list[Annotation]]:
        """Find duplicate annotation IDs.

        Args:
            annotations: List of annotations to check

        Returns:
            Dictionary mapping duplicate IDs to list of annotations with that ID.
            Empty dict if no duplicates found.

        Example:
            >>> scanner = AnnotationScanner()
            >>> annotations = scanner.scan([Path("src")])
            >>> duplicates = scanner.find_duplicates(annotations)
            >>> if duplicates:
            ...     print(f"Found duplicate: {list(duplicates.keys())[0]}")
        """
        # Group annotations by ID
        by_id: dict[str, list[Annotation]] = {}
        for annotation in annotations:
            if annotation.id not in by_id:
                by_id[annotation.id] = []
            by_id[annotation.id].append(annotation)

        # Filter to only duplicates (ID appears more than once)
        duplicates = {
            node_id: anns
            for node_id, anns in by_id.items()
            if len(anns) > 1
        }

        return duplicates

