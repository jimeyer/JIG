# ABOUTME: Registry of all validation rules with lookup indexes.
# ABOUTME: Provides RULES list, RULES_BY_CODE, and RULES_BY_SPEC for S-104 and S-109.
"""
Registry of validation rules.

Provides:
- RULES: List of all rule instances
- RULES_BY_CODE: Dict mapping rule code to rule instance
- RULES_BY_SPEC: Dict mapping spec ID to list of rules enforcing it
"""

from __future__ import annotations

from collections import defaultdict

import jig
from jig.rules.base import Artifact
from jig.rules.types import (
    BidirectionalLinkRule,
    CoverageRule,
    DAGRule,
    FilenameSyncRule,
    HeaderSyncRule,
    IdFormatRule,
    IsolationRule,
    LayerConstraintRule,
    PartitionRule,
    ReferenceValidityRule,
    RequiredFieldRule,
    UniquenessRule,
    normalize_outcome_id,
    normalize_spec_id,
)

# =============================================================================
# ARTIFACT FILTERS - predicates for filtering artifacts by type
# =============================================================================
# NOTE: Filters use ID pattern matching rather than frontmatter 'type' field
# because we need to validate artifacts that may be missing the 'type' field.
# Artifacts are already loaded by directory location in ValidationContext.


def is_specification(a: Artifact) -> bool:
    """Filter for specification artifacts.

    Uses ID pattern (S-###) for normal artifacts, or file path for orphans.
    """
    if a.id:
        return a.id.startswith("S-")
    # For orphans (missing ID), check if file path indicates specification
    return "specifications" in a.file


def is_outcome(a: Artifact) -> bool:
    """Filter for outcome artifacts.

    Uses ID pattern (O-###) for normal artifacts, or file path for orphans.
    """
    if a.id:
        return a.id.startswith("O-")
    # For orphans (missing ID), check if file path indicates outcome
    return "outcomes" in a.file


def is_architecture(a: Artifact) -> bool:
    """Filter for architecture artifacts.

    Uses ID pattern (A-###) since type field may be missing.
    """
    return a.id.startswith("A-")


def is_goal(a: Artifact) -> bool:
    """Filter for goal artifacts.

    Uses ID pattern (G-###) since type field may be missing.
    """
    return a.id.startswith("G-")


def is_charter(a: Artifact) -> bool:
    """Filter for charter artifacts."""
    return a.id == "Charter"


# =============================================================================
# CONTEXT HELPER FUNCTIONS - for extracting IDs and references from context
# =============================================================================


def get_spec_ids(ctx):
    """Get set of all spec IDs from context."""
    return set(ctx.specifications.keys())


def get_outcome_ids(ctx):
    """Get set of all outcome IDs from context."""
    return set(ctx.outcomes.keys())


def get_architecture_ids(ctx):
    """Get set of all architecture IDs from context."""
    return set(ctx.architectures.keys())


def get_goal_ids(ctx):
    """Get set of all goal IDs from context.

    Goals are defined inline in Charter's goals array, not as separate files.
    """
    # First try goals directory (for projects with separate goal files)
    if ctx.goals:
        return set(ctx.goals.keys())
    # Fall back to Charter's goals array
    if ctx.charter:
        goals = ctx.charter.frontmatter.get("goals", [])
        if isinstance(goals, list):
            return set(goals)
    return set()


def get_all_spec_refs_from_outcomes(ctx):
    """Get all spec IDs referenced in outcomes' specifications field."""
    refs = set()
    for outcome in ctx.outcomes.values():
        spec_refs = outcome.frontmatter.get("specifications", [])
        if isinstance(spec_refs, str):
            spec_refs = [spec_refs]
        if isinstance(spec_refs, list):
            refs.update(spec_refs)
    return refs


# =============================================================================
# RULE INSTANCES - instantiate all rules for validation
# =============================================================================


# --- SPECIFICATION RULES (S-018) ---

SPEC_REQUIRED_OUTCOMES = RequiredFieldRule(
    field="outcomes",
    artifact_filter=is_specification,
    default_value=[],
    auto_fix=False,  # Need human to decide which outcomes
    _code="SPEC_REQUIRED_OUTCOMES",
    _spec="S-018",
)

SPEC_REQUIRED_TITLE = RequiredFieldRule(
    field="title",
    artifact_filter=is_specification,
    default_value="",
    auto_fix=False,
    _code="SPEC_REQUIRED_TITLE",
    _spec="S-018",
)

SPEC_REQUIRED_TYPE = RequiredFieldRule(
    field="type",
    artifact_filter=is_specification,
    default_value="specification",
    auto_fix=True,
    _code="SPEC_REQUIRED_TYPE",
    _spec="S-018",
)

SPEC_REQUIRED_ID = RequiredFieldRule(
    field="id",
    artifact_filter=is_specification,
    default_value="",
    auto_fix=False,  # ID must be manually assigned
    _code="SPEC_REQUIRED_ID",
    _spec="S-018",
)

SPEC_ID_FORMAT = IdFormatRule(
    pattern=r"^S-\d{3}$",
    normalizer=normalize_spec_id,
    artifact_filter=is_specification,
    _code="SPEC_ID_FORMAT",
    _spec="S-018",
)

SPEC_UNIQUENESS = UniquenessRule(
    key_extractor=lambda a: a.id if is_specification(a) else None,
    artifact_filter=is_specification,
    _code="SPEC_UNIQUENESS",
    _spec="S-018",
)

SPEC_FILENAME_SYNC = FilenameSyncRule(
    artifact_filter=is_specification,
    _code="SPEC_FILENAME_SYNC",
    _spec="S-018",
)

SPEC_HEADER_SYNC = HeaderSyncRule(
    artifact_filter=is_specification,
    _code="SPEC_HEADER_SYNC",
    _spec="S-018",
)


# --- OUTCOME RULES (S-019) ---

OUTCOME_REQUIRED_TITLE = RequiredFieldRule(
    field="title",
    artifact_filter=is_outcome,
    default_value="",
    auto_fix=False,
    _code="OUTCOME_REQUIRED_TITLE",
    _spec="S-019",
)

OUTCOME_REQUIRED_TYPE = RequiredFieldRule(
    field="type",
    artifact_filter=is_outcome,
    default_value="outcome",
    auto_fix=True,
    _code="OUTCOME_REQUIRED_TYPE",
    _spec="S-019",
)

# Note: S-019 does NOT require goals/supports_goals field on outcomes.
# Goal references are validated via S-079 if present.

OUTCOME_ID_FORMAT = IdFormatRule(
    pattern=r"^O-\d{3}$",
    normalizer=normalize_outcome_id,
    artifact_filter=is_outcome,
    _code="OUTCOME_ID_FORMAT",
    _spec="S-019",
)

OUTCOME_UNIQUENESS = UniquenessRule(
    key_extractor=lambda a: a.id if is_outcome(a) else None,
    artifact_filter=is_outcome,
    _code="OUTCOME_UNIQUENESS",
    _spec="S-019",
)

OUTCOME_FILENAME_SYNC = FilenameSyncRule(
    artifact_filter=is_outcome,
    _code="OUTCOME_FILENAME_SYNC",
    _spec="S-019",
)

OUTCOME_HEADER_SYNC = HeaderSyncRule(
    artifact_filter=is_outcome,
    _code="OUTCOME_HEADER_SYNC",
    _spec="S-019",
)


# --- CHARTER RULES (S-072) ---

CHARTER_REQUIRED_GOALS = RequiredFieldRule(
    field="goals",
    artifact_filter=is_charter,
    default_value=[],
    auto_fix=False,  # Need human to define goals
    _code="CHARTER_REQUIRED_GOALS",
    _spec="S-072",
)


# --- REFERENCE VALIDITY RULES (S-020, S-075, S-079) ---

SPEC_OUTCOME_REFS_VALID = ReferenceValidityRule(
    field="outcomes",
    valid_ids_fn=get_outcome_ids,
    artifact_filter=is_specification,
    _code="SPEC_OUTCOME_REFS_VALID",
    _spec="S-020",
)

OUTCOME_GOAL_REFS_VALID = ReferenceValidityRule(
    field="goals",  # Field name used in existing outcomes
    valid_ids_fn=get_goal_ids,
    artifact_filter=is_outcome,
    _code="OUTCOME_GOAL_REFS_VALID",
    _spec="S-079",
)


# --- BIDIRECTIONAL CONSISTENCY (S-095) ---

SPEC_OUTCOME_BIDIRECTIONAL = BidirectionalLinkRule(
    forward_field="outcomes",
    back_field="specifications",
    source_filter=is_specification,
    target_filter=is_outcome,
    _code="SPEC_OUTCOME_BIDIRECTIONAL",
    _spec="S-095",
)


# --- COVERAGE RULES (S-042, S-043) ---

# S-043: Every spec must be listed by at least one outcome
SPEC_COVERAGE = CoverageRule(
    items_fn=lambda ctx: ctx.specifications,
    references_fn=get_all_spec_refs_from_outcomes,
    message_template="Specification '{item_id}' is not referenced by any outcome",
    _code="SPEC_COVERAGE",
    _spec="S-043",
)


# =============================================================================
# BRICK VALIDATION RULES (S-022, S-038, S-039, S-087, S-088, S-089)
# =============================================================================


# --- TOWER FORMAT RULE (S-087) ---

import re as _re
from jig.rules.base import Fix, Violation


class TowerFormatRule:
    """Rule that validates tower field values are kebab-case.

    Per S-087, tower values must be kebab-case:
    - Lowercase letters, numbers, and hyphens only
    - Must start with a letter
    - Must not end with a hyphen
    """

    _code: str = "TOWER_FORMAT"
    _spec: str = "S-087"

    # Regex per S-087: ^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$
    _TOWER_PATTERN = _re.compile(r"^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$")

    @property
    def code(self) -> str:
        return self._code

    @property
    def spec(self) -> str:
        return self._spec

    def violations(self, ctx) -> list[Violation]:
        """Detect bricks with invalid tower format."""
        result = []
        for brick in ctx.bricks:
            tower = brick.get("tower")
            if tower is None:
                continue  # tower is optional

            if not self._TOWER_PATTERN.match(tower):
                brick_id = brick.get("id", "unknown")
                result.append(
                    Violation(
                        rule_code=self.code,
                        artifact_id=brick_id,
                        file="jig/bricks.yaml",
                        line=None,
                        message=f"Tower '{tower}' in brick '{brick_id}' must be kebab-case",
                        context={"brick_id": brick_id, "tower": tower},
                    )
                )
        return result

    def fix_for(self, violation: Violation) -> Fix | None:
        """Tower format violations require manual fix."""
        tower = violation.context.get("tower", "")
        # Suggest converting to kebab-case
        suggested = tower.lower().replace("_", "-")
        return Fix(
            action="manual_review",
            target=violation.file,
            params={"tower": tower},
            auto=False,
            suggestions=[
                f"Change tower to kebab-case (e.g., '{suggested}')",
                "Tower must: start with letter, use only lowercase/numbers/hyphens",
            ],
        )

    def apply(self, fix: Fix, ctx) -> None:
        """Tower format fixes require manual editing of bricks.yaml."""
        pass  # Manual fix required


TOWER_FORMAT = TowerFormatRule()


# Context helper functions for brick rules

def get_all_function_ids(ctx):
    """Get set of all function IDs from implementation graph."""
    return ctx.get_function_ids()


def get_brick_to_functions(ctx):
    """Get dict mapping brick_id -> list of function IDs it contains."""
    return ctx.get_brick_to_functions()


def get_brick_layers(ctx):
    """Get dict mapping brick_id -> layer number."""
    return ctx.get_brick_layers()


def get_brick_dependency_edges(ctx):
    """Get list of (source_brick, target_brick) dependency edges."""
    return ctx.get_brick_dependency_edges()


def get_brick_dependency_graph(ctx):
    """Get adjacency list: brick_id -> set of brick_ids it depends on."""
    return ctx.get_brick_dependency_graph()


def get_brick_towers(ctx):
    """Get dict mapping brick_id -> tower name (or None)."""
    return ctx.get_brick_towers()


# --- BRICK PARTITION RULES (S-022) ---

BRICK_PARTITION = PartitionRule(
    items_fn=get_all_function_ids,
    containers_fn=get_brick_to_functions,
    item_label="function",
    container_label="brick",
    _code="BRICK_PARTITION",
    _spec="S-022",
)


# --- BRICK DAG RULE (S-039) ---

BRICK_DAG = DAGRule(
    graph_fn=get_brick_dependency_graph,
    node_label="brick",
    _code="BRICK_DAG",
    _spec="S-039",
)


# --- BRICK LAYER CONSTRAINTS (S-038) ---

BRICK_LAYER_CONSTRAINT = LayerConstraintRule(
    layers_fn=get_brick_layers,
    edges_fn=get_brick_dependency_edges,
    node_label="brick",
    _code="BRICK_LAYER_CONSTRAINT",
    _spec="S-038",
)


# --- TOWER ISOLATION RULES (S-088, S-089) ---

TOWER_ISOLATION = IsolationRule(
    partition_fn=get_brick_towers,
    edges_fn=get_brick_dependency_edges,
    skip_if_single=True,  # S-089: skip if single tower
    node_label="brick",
    partition_label="tower",
    _code="TOWER_ISOLATION",
    _spec="S-088",
)


# =============================================================================
# RULES REGISTRY - the main list and indexes
# =============================================================================


@jig.implements("S-109")
def _build_rules_list() -> list:
    """Build the list of all rule instances."""
    return [
        # Spec rules (S-018)
        SPEC_REQUIRED_ID,
        SPEC_REQUIRED_OUTCOMES,
        SPEC_REQUIRED_TITLE,
        SPEC_REQUIRED_TYPE,
        SPEC_ID_FORMAT,
        SPEC_UNIQUENESS,
        SPEC_FILENAME_SYNC,
        SPEC_HEADER_SYNC,
        # Outcome rules (S-019)
        OUTCOME_REQUIRED_TITLE,
        OUTCOME_REQUIRED_TYPE,
        OUTCOME_ID_FORMAT,
        OUTCOME_UNIQUENESS,
        OUTCOME_FILENAME_SYNC,
        OUTCOME_HEADER_SYNC,
        # Charter rules (S-072)
        CHARTER_REQUIRED_GOALS,
        # Reference validity (S-020, S-079)
        SPEC_OUTCOME_REFS_VALID,
        OUTCOME_GOAL_REFS_VALID,
        # Bidirectional consistency (S-095)
        SPEC_OUTCOME_BIDIRECTIONAL,
        # Coverage (S-043)
        SPEC_COVERAGE,
        # Brick rules (S-022, S-038, S-039, S-087, S-088, S-089)
        BRICK_PARTITION,
        BRICK_DAG,
        BRICK_LAYER_CONSTRAINT,
        TOWER_FORMAT,
        TOWER_ISOLATION,
    ]


def _build_rules_by_code(rules: list) -> dict:
    """Build code -> rule mapping."""
    return {rule.code: rule for rule in rules}


def _build_rules_by_spec(rules: list) -> dict:
    """Build spec -> [rules] mapping."""
    index = defaultdict(list)
    for rule in rules:
        index[rule.spec].append(rule)
    return dict(index)


# Initialize the registry
RULES: list = _build_rules_list()
RULES_BY_CODE: dict = _build_rules_by_code(RULES)
RULES_BY_SPEC: dict = _build_rules_by_spec(RULES)
