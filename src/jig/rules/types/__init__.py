# ABOUTME: Rule type classes implementing the Rule protocol.
# ABOUTME: Each rule type knows how to detect violations, describe repairs, and execute fixes.
"""
Rule type classes for the JIG validation engine.

Provides 15 rule types that implement the Rule protocol:
- RequiredFieldRule: Detects missing required fields
- IdFormatRule: Validates ID patterns
- UniquenessRule: Detects duplicates
- FilenameSyncRule: Validates filename/frontmatter consistency
- HeaderSyncRule: Validates H1/title consistency
- ExcludedFieldRule: Detects forbidden fields
- FieldTypeRule: Validates field types
- FieldValueRule: Validates field values against predicates
- ReferenceValidityRule: Validates references exist
- BidirectionalLinkRule: Validates A<->B consistency
- CoverageRule: Validates every item is covered
- PartitionRule: Validates partition property (no gaps, no overlaps)
- DAGRule: Validates acyclic graph
- LayerConstraintRule: Validates layer hierarchy
- IsolationRule: Validates no cross-boundary dependencies
"""

import re

# Helper functions for normalization


def to_snake_case(title: str) -> str:
    """Convert title to snake_case for filename matching.

    Rules:
    - Replace spaces with underscores
    - Remove punctuation (except hyphens in compound words)
    - Preserve capitalization (Title_Case)
    - Preserve acronyms

    Examples:
        "Python Code Structure" -> "Python_Code_Structure"
        "CLI Show Commands" -> "CLI_Show_Commands"
        "What's New?" -> "Whats_New"
        "Cross-Tower Isolation" -> "Cross-Tower_Isolation"
    """
    result = []
    for char in title:
        if char.isalnum() or char == " ":
            result.append(char)
        elif char == "-":
            result.append(char)
    cleaned = "".join(result)
    return cleaned.replace(" ", "_")


def normalize_spec_id(raw: str) -> str:
    """Normalize a spec ID to canonical form.

    Converts variations like "s-1", "S-1", "s-001" to "S-001".
    Returns the input unchanged if it doesn't match spec pattern.

    Examples:
        "s-1" -> "S-001"
        "S-1" -> "S-001"
        "S-001" -> "S-001"
        "S-99" -> "S-099"
        "invalid" -> "invalid"
    """
    pattern = re.compile(r"^[sS]-(\d+)$")
    match = pattern.match(raw)
    if not match:
        return raw
    num = int(match.group(1))
    return f"S-{num:03d}"


def normalize_outcome_id(raw: str) -> str:
    """Normalize an outcome ID to canonical form.

    Converts variations like "o-1", "O-1", "o-001" to "O-001".

    Examples:
        "o-1" -> "O-001"
        "O-1" -> "O-001"
        "O-001" -> "O-001"
    """
    pattern = re.compile(r"^[oO]-(\d+)$")
    match = pattern.match(raw)
    if not match:
        return raw
    num = int(match.group(1))
    return f"O-{num:03d}"


def normalize_architecture_id(raw: str) -> str:
    """Normalize an architecture ID to canonical form.

    Converts variations like "a-1", "A-1", "a-001" to "A-001".

    Examples:
        "a-1" -> "A-001"
        "A-1" -> "A-001"
        "A-001" -> "A-001"
    """
    pattern = re.compile(r"^[aA]-(\d+)$")
    match = pattern.match(raw)
    if not match:
        return raw
    num = int(match.group(1))
    return f"A-{num:03d}"


def normalize_goal_id(raw: str) -> str:
    """Normalize a goal ID to canonical form.

    Converts variations like "g-1", "G-1", "g-001" to "G-001".

    Examples:
        "g-1" -> "G-001"
        "G-1" -> "G-001"
        "G-001" -> "G-001"
    """
    pattern = re.compile(r"^[gG]-(\d+)$")
    match = pattern.match(raw)
    if not match:
        return raw
    num = int(match.group(1))
    return f"G-{num:03d}"


def normalize_brick_id(raw: str) -> str:
    """Normalize a brick ID to canonical form.

    Brick IDs must be kebab-case starting with B-.
    This function lowercases and ensures proper format.

    Examples:
        "B-Auth" -> "B-auth"
        "b-core-utils" -> "B-core-utils"
        "B-core-utils" -> "B-core-utils"
    """
    if not raw.startswith(("B-", "b-")):
        return raw
    # Lowercase everything after B-
    return "B-" + raw[2:].lower()


# Export rule types (must be at module end due to helper function definitions above)
from jig.rules.types.bidirectional_link import BidirectionalLinkRule  # noqa: E402
from jig.rules.types.coverage import CoverageRule  # noqa: E402
from jig.rules.types.dag import DAGRule  # noqa: E402
from jig.rules.types.excluded_field import ExcludedFieldRule  # noqa: E402
from jig.rules.types.field_type import FieldTypeRule  # noqa: E402
from jig.rules.types.field_value import FieldValueRule  # noqa: E402
from jig.rules.types.filename_sync import FilenameSyncRule  # noqa: E402
from jig.rules.types.header_sync import HeaderSyncRule  # noqa: E402
from jig.rules.types.id_format import IdFormatRule  # noqa: E402
from jig.rules.types.isolation import IsolationRule  # noqa: E402
from jig.rules.types.layer_constraint import LayerConstraintRule  # noqa: E402
from jig.rules.types.partition import PartitionRule  # noqa: E402
from jig.rules.types.reference_validity import ReferenceValidityRule  # noqa: E402
from jig.rules.types.required_field import RequiredFieldRule  # noqa: E402
from jig.rules.types.uniqueness import UniquenessRule  # noqa: E402

__all__ = [
    # Helper functions
    "to_snake_case",
    "normalize_spec_id",
    "normalize_outcome_id",
    "normalize_architecture_id",
    "normalize_goal_id",
    "normalize_brick_id",
    # Rule types
    "RequiredFieldRule",
    "IdFormatRule",
    "UniquenessRule",
    "FilenameSyncRule",
    "HeaderSyncRule",
    "ExcludedFieldRule",
    "FieldTypeRule",
    "FieldValueRule",
    "ReferenceValidityRule",
    "BidirectionalLinkRule",
    "CoverageRule",
    "PartitionRule",
    "DAGRule",
    "LayerConstraintRule",
    "IsolationRule",
]
