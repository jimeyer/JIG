# ABOUTME: Foundation types for the rules engine: Rule protocol, Violation, Fix, Artifact.
# ABOUTME: Implements S-108 (error ID stability) and S-109 (rule spec traceability).
"""
Foundation types for the JIG rules engine.

Defines:
- Rule: Protocol for validation rules
- Violation: Detected validation error
- Fix: Repair action template
- Artifact: JIG artifact (spec, outcome, architecture, etc.)
- compute_error_id: Stable error ID computation (S-108)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

import jig

if TYPE_CHECKING:
    from jig.rules.context import MendContext, ValidationContext


@dataclass
class Violation:
    """Represents a single validation error detected by a rule.

    Attributes:
        rule_code: Unique code identifying the rule that detected this violation.
        artifact_id: ID of the artifact containing the violation (e.g., "S-001").
        file: Path to the file containing the violation.
        line: Line number of the violation, or None if not applicable.
        message: Human-readable description of the violation.
        context: Error-specific context for ID computation and fix generation.
    """

    rule_code: str
    artifact_id: str
    file: str
    line: int | None
    message: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class Fix:
    """Represents a repair action template for a violation.

    Attributes:
        action: The type of fix action (e.g., "set_field", "rename_file").
        target: Path to the file to be modified.
        params: Parameters for the fix action.
        auto: Whether this fix can be applied automatically.
        suggestions: Optional suggestions for manual fixes.
    """

    action: str
    target: str
    params: dict[str, Any] = field(default_factory=dict)
    auto: bool = False
    suggestions: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "action": self.action,
            "target": self.target,
            "params": self.params,
            "auto": self.auto,
        }
        if self.suggestions is not None:
            result["suggestions"] = self.suggestions
        return result


@dataclass
class Artifact:
    """Represents a JIG artifact (spec, outcome, architecture, goal, charter).

    Attributes:
        id: Unique identifier (e.g., "S-001", "O-001").
        file: Path to the artifact file.
        frontmatter: Parsed YAML frontmatter as dict.
    """

    id: str
    file: str
    frontmatter: dict[str, Any]

    @property
    def kind(self) -> str:
        """Return the artifact type from frontmatter."""
        return self.frontmatter.get("type", "unknown")


@runtime_checkable
class Rule(Protocol):
    """Protocol defining the interface for validation rules.

    A rule knows how to:
    - Detect violations in a ValidationContext
    - Generate fix templates for violations
    - Apply fixes via MendContext

    Each rule is associated with a specification (spec) for traceability (S-109).
    """

    @property
    def code(self) -> str:
        """Unique identifier for this rule (e.g., 'REQUIRED_FIELD')."""
        ...

    @property
    def spec(self) -> str:
        """Specification ID this rule enforces (e.g., 'S-018')."""
        ...

    def violations(self, ctx: ValidationContext) -> list[Violation]:
        """Detect all violations of this rule in the given context."""
        ...

    def fix_for(self, violation: Violation) -> Fix | None:
        """Generate a fix template for the given violation, or None if unfixable."""
        ...

    def apply(self, fix: Fix, ctx: MendContext) -> None:
        """Apply the fix using the MendContext."""
        ...


@jig.implements("S-108")
def compute_error_id(
    rule_code: str, artifact_id: str, context: dict[str, Any]
) -> str:
    """Compute a stable, deterministic error ID.

    The ID is a 12-character hex string computed from:
    - rule_code: The rule that detected the error
    - artifact_id: The artifact containing the error
    - context: Error-specific context (canonicalized as sorted JSON)

    This ensures the same logical error produces the same ID across runs,
    enabling reliable error tracking (S-108).

    Args:
        rule_code: Unique rule identifier.
        artifact_id: Artifact identifier (e.g., "S-001").
        context: Error-specific context dict.

    Returns:
        12-character lowercase hex string.
    """
    # Canonical JSON with sorted keys for determinism
    canonical_context = json.dumps(context, sort_keys=True, separators=(",", ":"))
    input_str = f"{rule_code}:{artifact_id}:{canonical_context}"
    hash_bytes = hashlib.sha256(input_str.encode("utf-8")).digest()
    return hash_bytes.hex()[:12]
