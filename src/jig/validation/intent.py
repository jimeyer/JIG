"""
Intent validation: specifications, outcomes, and decorators.

Validates human-authored intent artifacts before graph generation.
"""

import ast
import re
from pathlib import Path
from typing import Optional

import yaml

import jig
from jig.validation.models import ValidationError, ValidationResult


# ============================================================================
# Filename Format Validation Helpers (S-018, S-019, S-076)
# ============================================================================


@jig.implements("S-018", "S-019", "S-076")
def to_snake_case(title: str) -> str:
    """
    Convert title to snake_case for filename matching.

    Rules:
    - Replace spaces with underscores
    - Remove punctuation (except hyphens in compound words)
    - Preserve capitalization (Title_Case)
    - Preserve acronyms

    Examples:
        "Python Code Structure" -> "Python_Code_Structure"
        "CLI Show Commands" -> "CLI_Show_Commands"
        "YAML Frontmatter Parsing" -> "YAML_Frontmatter_Parsing"
        "What's New?" -> "Whats_New"
        "Cross-Tower Isolation" -> "Cross-Tower_Isolation"
    """
    # Remove punctuation except hyphens and spaces
    # Keep hyphens that are between letters (compound words)
    result = []
    for char in title:
        if char.isalnum() or char == ' ':
            result.append(char)
        elif char == '-':
            # Keep hyphens between letters (compound words)
            result.append(char)
        # else: drop other punctuation (apostrophes, question marks, etc.)

    # Join and replace spaces with underscores
    cleaned = ''.join(result)
    return cleaned.replace(' ', '_')


@jig.implements("S-018", "S-019", "S-076")
def validate_filename_format(
    file_path: Path,
    frontmatter: dict,
    type_prefix: str,
) -> list[str]:
    """
    Validate that filename matches expected pattern and frontmatter title.

    Pattern: {TYPE}-{NNN}_{Title_Snake_Case}.md

    Args:
        file_path: Path to the intent document file
        frontmatter: Parsed YAML frontmatter dictionary
        type_prefix: Expected prefix (S, O, or A)

    Returns:
        List of error messages (empty if valid).
    """
    errors = []

    # Get frontmatter values
    doc_id = frontmatter.get("id", "")
    title = frontmatter.get("title", "")

    if not title:
        # Missing title is caught by required field validation
        return errors

    # Expected filename format
    expected_snake = to_snake_case(title)
    expected_filename = f"{doc_id}_{expected_snake}.md"

    # Check if filename matches expected format
    actual_filename = file_path.name

    if actual_filename != expected_filename:
        errors.append(
            f"Invalid filename format\n"
            f"  File: {file_path}\n"
            f"  Expected: {expected_filename}\n"
            f"  Actual: {actual_filename}\n"
            f"  Rule: Filename must be {{TYPE}}-{{NNN}}_{{Title_Snake_Case}}.md"
        )

    return errors


@jig.implements("S-018", "S-019", "S-076")
def validate_h1_matches_title(file_path: Path, frontmatter: dict) -> list[str]:
    """
    Validate that first H1 in document body matches frontmatter title exactly.

    The H1 must NOT include an ID prefix (e.g., "# A-001: Title" is invalid).

    Returns:
        List of error messages (empty if valid).
    """
    errors = []

    title = frontmatter.get("title", "")
    if not title:
        # Missing title is caught by required field validation
        return errors

    try:
        content = file_path.read_text()

        # Skip frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2]
            else:
                body = content
        else:
            body = content

        # Find first H1 header
        h1_pattern = re.compile(r"^#\s+(.+)$", re.MULTILINE)
        match = h1_pattern.search(body)

        if not match:
            errors.append(
                f"Missing H1 header\n"
                f"  File: {file_path}\n"
                f"  Rule: Document must have at least one H1 (# Title) header"
            )
            return errors

        h1_content = match.group(1).strip()

        # Check if H1 matches title exactly
        if h1_content != title:
            errors.append(
                f"H1 does not match title\n"
                f"  File: {file_path}\n"
                f"  Frontmatter title: \"{title}\"\n"
                f"  First H1: \"# {h1_content}\"\n"
                f"  Rule: First H1 must exactly match frontmatter title"
            )

        # Check if H1 contains ID prefix (e.g., "A-001: Title")
        id_prefix_pattern = re.compile(r"^[AOS]-\d{3}:\s*")
        if id_prefix_pattern.match(h1_content):
            errors.append(
                f"H1 contains ID prefix\n"
                f"  File: {file_path}\n"
                f"  First H1: \"# {h1_content}\"\n"
                f"  Rule: H1 must NOT include ID prefix (use title only)"
            )

    except Exception:
        # File reading errors are caught elsewhere
        pass

    return errors


@jig.implements("S-018")
def validate_specification_files(spec_dir: Path) -> ValidationResult:
    """
    Validate specification files against A001 contract.

    Checks:
    - Required fields: id, title, type
    - ID format: S-{number}
    - ID uniqueness
    - Filename matches ID
    - No excluded fields: brick, depends_on, content
    """
    result = ValidationResult(passed=True, phase_name="specifications")

    spec_files = sorted(spec_dir.glob("S-*.md"))
    result.items_checked = len(spec_files)

    seen_ids = {}
    spec_pattern = re.compile(r"^S-\d+$")

    for spec_file in spec_files:
        # Parse YAML frontmatter
        frontmatter = _parse_frontmatter(spec_file)
        if frontmatter is None:
            result.add_error(
                ValidationError(
                    file=str(spec_file),
                    message="Missing or invalid YAML frontmatter",
                    code="INVALID_FRONTMATTER",
                )
            )
            continue

        # Check required fields
        if "id" not in frontmatter:
            result.add_error(
                ValidationError(
                    file=str(spec_file),
                    message="Missing required field: 'id'",
                    code="MISSING_REQUIRED_FIELD",
                    field="id",
                )
            )
            continue

        if "type" not in frontmatter:
            result.add_error(
                ValidationError(
                    file=str(spec_file),
                    message="Missing required field: 'type'",
                    code="MISSING_REQUIRED_FIELD",
                    field="type",
                )
            )

        if "title" not in frontmatter:
            result.add_error(
                ValidationError(
                    file=str(spec_file),
                    message="Missing required field: 'title'. Per A001, specifications must have a title field in frontmatter.",
                    code="MISSING_REQUIRED_FIELD",
                    field="title",
                )
            )

        spec_id = frontmatter.get("id")

        # Check ID format
        if not spec_pattern.match(spec_id):
            result.add_error(
                ValidationError(
                    file=str(spec_file),
                    message=f"Invalid ID format: '{spec_id}' (expected S-NNN pattern)",
                    code="INVALID_ID_FORMAT",
                    field="id",
                )
            )

        # Check filename format: {ID}_{Title_Snake_Case}.md
        filename_errors = validate_filename_format(spec_file, frontmatter, "S")
        for err_msg in filename_errors:
            result.add_error(
                ValidationError(
                    file=str(spec_file),
                    message=err_msg,
                    code="INVALID_FILENAME_FORMAT",
                )
            )

        # Check H1 matches frontmatter title
        h1_errors = validate_h1_matches_title(spec_file, frontmatter)
        for err_msg in h1_errors:
            result.add_error(
                ValidationError(
                    file=str(spec_file),
                    message=err_msg,
                    code="H1_TITLE_MISMATCH",
                )
            )

        # Check ID uniqueness
        if spec_id in seen_ids:
            result.add_error(
                ValidationError(
                    file=str(spec_file),
                    message=f"Duplicate ID '{spec_id}' (also in {seen_ids[spec_id]})",
                    code="DUPLICATE_ID",
                    field="id",
                )
            )
        else:
            seen_ids[spec_id] = spec_file.name

        # Check excluded fields
        excluded_fields = ["brick", "depends_on", "content", "implements"]
        for field in excluded_fields:
            if field in frontmatter:
                result.add_error(
                    ValidationError(
                        file=str(spec_file),
                        message=f"Excluded field '{field}' must not be present in specifications",
                        code="EXCLUDED_FIELD_PRESENT",
                        field=field,
                    )
                )

    return result


@jig.implements("S-019")
def validate_outcome_files(outcome_dir: Path) -> ValidationResult:
    """
    Validate outcome files against A001 contract.

    Outcomes are optional artifacts.

    Checks:
    - Required fields: id, title, type, specifications
    - ID format: O-{number}
    - ID uniqueness
    - No excluded fields: brick
    """
    result = ValidationResult(passed=True, phase_name="outcomes")

    outcome_files = sorted(outcome_dir.glob("O-*.md"))
    result.items_checked = len(outcome_files)

    # Outcomes are optional, so no files is valid
    if len(outcome_files) == 0:
        return result

    seen_ids = {}
    outcome_pattern = re.compile(r"^O-\d+$")
    total_spec_references = 0

    for outcome_file in outcome_files:
        # Parse YAML frontmatter
        frontmatter = _parse_frontmatter(outcome_file)
        if frontmatter is None:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message="Missing or invalid YAML frontmatter",
                    code="INVALID_FRONTMATTER",
                )
            )
            continue

        # Check required fields
        if "id" not in frontmatter:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message="Missing required field: 'id'",
                    code="MISSING_REQUIRED_FIELD",
                    field="id",
                )
            )
            continue

        if "type" not in frontmatter:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message="Missing required field: 'type'",
                    code="MISSING_REQUIRED_FIELD",
                    field="type",
                )
            )

        if "specifications" not in frontmatter:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message="Missing required field: 'specifications'",
                    code="MISSING_REQUIRED_FIELD",
                    field="specifications",
                )
            )

        if "title" not in frontmatter:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message="Missing required field: 'title'. Per A001, outcomes must have a title field in frontmatter.",
                    code="MISSING_REQUIRED_FIELD",
                    field="title",
                )
            )

        outcome_id = frontmatter.get("id")

        # Check ID format
        if not outcome_pattern.match(outcome_id):
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message=f"Invalid ID format: '{outcome_id}' (expected O-NNN pattern)",
                    code="INVALID_ID_FORMAT",
                    field="id",
                )
            )

        # Check filename format: {ID}_{Title_Snake_Case}.md
        filename_errors = validate_filename_format(outcome_file, frontmatter, "O")
        for err_msg in filename_errors:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message=err_msg,
                    code="INVALID_FILENAME_FORMAT",
                )
            )

        # Check H1 matches frontmatter title
        h1_errors = validate_h1_matches_title(outcome_file, frontmatter)
        for err_msg in h1_errors:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message=err_msg,
                    code="H1_TITLE_MISMATCH",
                )
            )

        # Check ID uniqueness
        if outcome_id in seen_ids:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message=f"Duplicate ID '{outcome_id}' (also in {seen_ids[outcome_id]})",
                    code="DUPLICATE_ID",
                    field="id",
                )
            )
        else:
            seen_ids[outcome_id] = outcome_file.name

        # Check excluded fields
        if "brick" in frontmatter:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message="Excluded field 'brick' must not be present in outcomes",
                    code="EXCLUDED_FIELD_PRESENT",
                    field="brick",
                )
            )

        # Count spec references
        specifications = frontmatter.get("specifications", [])
        if isinstance(specifications, list):
            total_spec_references += len(specifications)

    # Set detail for display
    result.detail = f"{len(outcome_files)} files, {total_spec_references} spec references"

    return result


@jig.implements("S-042")
def validate_outcome_completeness(outcome_dir: Path) -> ValidationResult:
    """
    Validate that outcomes have non-empty specifications arrays.

    Per S-042: All outcomes SHALL specify at least one specification.
    Empty specifications arrays are incomplete and prevent O→S→TDD workflow.

    Checks:
    - Each outcome has 'specifications' field (checked by validate_outcome_files)
    - 'specifications' array is non-empty (has at least one spec ID)
    """
    result = ValidationResult(passed=True, phase_name="outcome completeness")

    outcome_files = sorted(outcome_dir.glob("O-*.md"))
    result.items_checked = len(outcome_files)

    # Outcomes are optional, so no files is valid
    if len(outcome_files) == 0:
        return result

    for outcome_file in outcome_files:
        # Parse YAML frontmatter
        frontmatter = _parse_frontmatter(outcome_file)
        if frontmatter is None:
            # Malformed frontmatter is caught by validate_outcome_files
            continue

        outcome_id = frontmatter.get("id")
        specifications = frontmatter.get("specifications", [])

        # Check if specifications array is empty
        if isinstance(specifications, list) and len(specifications) == 0:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message=f"Outcome completeness: Outcome '{outcome_id}' has empty specifications array. Outcomes must decompose into at least one concrete specification.",
                    code="EMPTY_SPECIFICATIONS",
                    field="specifications",
                )
            )

    return result


@jig.implements("S-043")
def validate_specification_coverage(spec_dir: Path, outcome_dir: Path) -> ValidationResult:
    """
    Validate that all specifications are referenced by at least one outcome.

    Per S-043: All specifications SHALL be specified by at least one outcome.
    Specifications without outcomes lack business justification.

    Algorithm:
    1. Load all outcomes and build reverse index: spec_id → [outcome_ids]
    2. Load all specifications
    3. Report specifications with empty reverse index (no outcomes point to them)

    Checks:
    - Each spec is referenced in at least one outcome's 'specifications' array
    """
    result = ValidationResult(passed=True, phase_name="specification coverage")

    spec_files = sorted(spec_dir.glob("S-*.md"))
    result.items_checked = len(spec_files)

    # If no specs, validation passes (specs are not optional, but empty is valid during setup)
    if len(spec_files) == 0:
        return result

    # Build reverse index: spec_id → list of outcomes that specify it
    spec_to_outcomes = {}
    for outcome_file in sorted(outcome_dir.glob("O-*.md")):
        frontmatter = _parse_frontmatter(outcome_file)
        if frontmatter is None:
            continue

        outcome_id = frontmatter.get("id")
        specifications = frontmatter.get("specifications", [])

        if isinstance(specifications, list):
            for spec_id in specifications:
                if spec_id not in spec_to_outcomes:
                    spec_to_outcomes[spec_id] = []
                spec_to_outcomes[spec_id].append(outcome_id)

    # Check each specification
    covered_count = 0
    orphaned_count = 0

    for spec_file in spec_files:
        frontmatter = _parse_frontmatter(spec_file)
        if frontmatter is None:
            # Malformed frontmatter is caught by validate_specification_files
            continue

        spec_id = frontmatter.get("id")

        # Check if spec is referenced by any outcome
        if spec_id not in spec_to_outcomes or len(spec_to_outcomes[spec_id]) == 0:
            orphaned_count += 1
            result.add_error(
                ValidationError(
                    file=str(spec_file),
                    message=f"Specification coverage: Specification '{spec_id}' is not specified by any outcome. All specifications must deliver value via at least one outcome.",
                    code="ORPHANED_SPECIFICATION",
                    field="specifications",
                )
            )
        else:
            covered_count += 1

    # Set detail for display
    result.detail = f"{len(spec_files)} specs: {covered_count} covered, {orphaned_count} orphaned"

    return result


@jig.implements("S-020")
def validate_decorator_files(
    source_dir: Path,
    spec_dir: Path,
    outcome_dir: Optional[Path] = None,
    test_dir: Optional[Path] = None,
) -> ValidationResult:
    """
    Validate @jig.implements and @jig.verifies decorators reference valid IDs.

    Checks:
    - Decorator arguments are string literals
    - References point to existing spec/outcome IDs
    - Multiple specs in single decorator are all valid
    """
    result = ValidationResult(passed=True, phase_name="decorators")

    # Load valid spec and outcome IDs
    valid_spec_ids = _load_spec_ids(spec_dir)
    valid_outcome_ids = _load_outcome_ids(outcome_dir) if outcome_dir else set()
    valid_ids = valid_spec_ids | valid_outcome_ids

    # Find all Python files in source directory
    python_files = list(source_dir.rglob("*.py"))

    # Also find Python files in test directory if it exists
    # Exclude fixture directories
    test_python_files = []
    if test_dir and test_dir.exists():
        test_python_files = [
            f for f in test_dir.rglob("*.py")
            if "fixtures" not in f.parts and "fixture" not in f.parts
        ]

    result.items_checked = len(python_files) + len(test_python_files)

    # Track decorated function counts
    function_count = 0
    test_count = 0

    # Process source files
    for py_file in python_files:
        try:
            source = py_file.read_text()
            tree = ast.parse(source, filename=str(py_file))

            # Visit all function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    has_jig_decorator = _validate_function_decorators(node, py_file, valid_ids, result)
                    if has_jig_decorator:
                        function_count += 1

        except SyntaxError as e:
            result.add_error(
                ValidationError(
                    file=str(py_file),
                    line=e.lineno,
                    message=f"Python syntax error: {e.msg}",
                    code="SYNTAX_ERROR",
                )
            )
        except Exception as e:
            result.add_error(
                ValidationError(
                    file=str(py_file),
                    message=f"Error parsing file: {e}",
                    code="PARSE_ERROR",
                )
            )

    # Process test files
    for py_file in test_python_files:
        try:
            source = py_file.read_text()
            tree = ast.parse(source, filename=str(py_file))

            # Visit all function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    has_jig_decorator = _validate_function_decorators(node, py_file, valid_ids, result)
                    if has_jig_decorator:
                        test_count += 1

        except SyntaxError as e:
            result.add_error(
                ValidationError(
                    file=str(py_file),
                    line=e.lineno,
                    message=f"Python syntax error: {e.msg}",
                    code="SYNTAX_ERROR",
                )
            )
        except Exception as e:
            result.add_error(
                ValidationError(
                    file=str(py_file),
                    message=f"Error parsing file: {e}",
                    code="PARSE_ERROR",
                )
            )

    # Set detail for display
    total_files = len(python_files) + len(test_python_files)
    result.detail = f"{total_files} files: {function_count} functions, {test_count} tests"

    return result


def _parse_frontmatter(file_path: Path) -> Optional[dict]:
    """Parse YAML frontmatter from markdown file."""
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


def _load_spec_ids(spec_dir: Path) -> set[str]:
    """Load all valid specification IDs."""
    ids = set()
    for spec_file in spec_dir.glob("S-*.md"):
        frontmatter = _parse_frontmatter(spec_file)
        if frontmatter and "id" in frontmatter:
            ids.add(frontmatter["id"])
    return ids


def _load_outcome_ids(outcome_dir: Path) -> set[str]:
    """Load all valid outcome IDs."""
    ids = set()
    for outcome_file in outcome_dir.glob("O-*.md"):
        frontmatter = _parse_frontmatter(outcome_file)
        if frontmatter and "id" in frontmatter:
            ids.add(frontmatter["id"])
    return ids


def _validate_function_decorators(
    func_node: ast.FunctionDef,
    file_path: Path,
    valid_ids: set[str],
    result: ValidationResult,
) -> bool:
    """
    Validate decorators on a function definition.

    Returns True if the function has any jig decorators, False otherwise.
    """
    has_jig_decorator = False

    for decorator in func_node.decorator_list:
        # Check for @jig.implements and @jig.verifies
        if isinstance(decorator, ast.Call):
            if _is_jig_decorator(decorator, "implements") or _is_jig_decorator(decorator, "verifies"):
                has_jig_decorator = True
                # Check all arguments are string literals
                for arg in decorator.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        ref_id = arg.value
                        # Check if ID exists
                        if ref_id not in valid_ids:
                            decorator_name = _get_decorator_name(decorator)
                            result.add_error(
                                ValidationError(
                                    file=str(file_path),
                                    line=decorator.lineno,
                                    message=f"@{decorator_name}(\"{ref_id}\"): ID does not exist",
                                    code="INVALID_REFERENCE",
                                )
                            )
                    else:
                        # Non-string argument
                        decorator_name = _get_decorator_name(decorator)
                        result.add_error(
                            ValidationError(
                                file=str(file_path),
                                line=decorator.lineno,
                                message=f"@{decorator_name}: arguments must be string literals, not variables or expressions",
                                code="INVALID_DECORATOR_ARGUMENT",
                            )
                        )

    return has_jig_decorator


def _is_jig_decorator(call_node: ast.Call, decorator_name: str) -> bool:
    """Check if a Call node is @jig.<decorator_name>."""
    if isinstance(call_node.func, ast.Attribute):
        if isinstance(call_node.func.value, ast.Name):
            return call_node.func.value.id == "jig" and call_node.func.attr == decorator_name
    return False


def _get_decorator_name(call_node: ast.Call) -> str:
    """Get the decorator name from a Call node."""
    if isinstance(call_node.func, ast.Attribute):
        return f"jig.{call_node.func.attr}"
    return "unknown"


# ============================================================================
# Charter and Goal Validation (S-072, S-073, S-074, S-075)
# ============================================================================


@jig.implements("S-072", "S-073", "S-074", "S-075")
def validate_charter_file(charter_path: Path) -> ValidationResult:
    """
    Validate Charter.md against S-072, S-073, S-074, S-075 specifications.

    Checks:
    - Charter file exists at jig/Charter.md (S-072)
    - Charter has valid YAML frontmatter
    - Charter has id: Charter, type: charter
    - Charter has goals array (S-073)
    - Goal headers match goals array (S-074)
    - Goal IDs match G-{number} format (S-075)
    """
    result = ValidationResult(passed=True, phase_name="charter")
    result.items_checked = 1

    # S-072: Check file exists
    if not charter_path.exists():
        result.add_error(
            ValidationError(
                file=str(charter_path),
                message="Charter file not found. Charter must be a single file at jig/Charter.md",
                code="FILE_NOT_FOUND",
            )
        )
        return result

    # Parse frontmatter
    frontmatter = _parse_frontmatter(charter_path)
    if frontmatter is None:
        result.add_error(
            ValidationError(
                file=str(charter_path),
                message="Missing or invalid YAML frontmatter",
                code="INVALID_FRONTMATTER",
            )
        )
        return result

    # Check id field
    if frontmatter.get("id") != "Charter":
        result.add_error(
            ValidationError(
                file=str(charter_path),
                message=f"Invalid id: '{frontmatter.get('id')}' (must be exactly 'Charter')",
                code="INVALID_ID",
                field="id",
            )
        )

    # Check type field
    if frontmatter.get("type") != "charter":
        result.add_error(
            ValidationError(
                file=str(charter_path),
                message=f"Invalid type: '{frontmatter.get('type')}' (must be exactly 'charter')",
                code="INVALID_TYPE",
                field="type",
            )
        )

    # S-073: Check goals array
    goals = frontmatter.get("goals")
    if not goals:
        result.add_error(
            ValidationError(
                file=str(charter_path),
                message="Missing required field: 'goals'. Charter must define at least one goal.",
                code="MISSING_REQUIRED_FIELD",
                field="goals",
            )
        )
        return result

    if not isinstance(goals, list):
        result.add_error(
            ValidationError(
                file=str(charter_path),
                message=f"goals must be an array, not {type(goals).__name__}",
                code="INVALID_FIELD_TYPE",
                field="goals",
            )
        )
        return result

    if len(goals) == 0:
        result.add_error(
            ValidationError(
                file=str(charter_path),
                message="goals array is empty. Charter must define at least one goal.",
                code="EMPTY_GOALS",
                field="goals",
            )
        )
        return result

    # S-075: Check goal ID format
    goal_pattern = re.compile(r"^G-\d+$")
    for goal_id in goals:
        if not goal_pattern.match(goal_id):
            result.add_error(
                ValidationError(
                    file=str(charter_path),
                    message=f"Invalid goal ID format: '{goal_id}' (must match G-{{number}} pattern, e.g., G-001)",
                    code="INVALID_GOAL_ID_FORMAT",
                    field="goals",
                )
            )

    # Check for duplicates
    if len(goals) != len(set(goals)):
        result.add_error(
            ValidationError(
                file=str(charter_path),
                message="goals contains duplicate goal IDs",
                code="DUPLICATE_GOAL_ID",
                field="goals",
            )
        )

    # S-074: Extract goal headers from body and verify they match
    body_goals = _extract_goal_headers(charter_path)
    body_goal_ids = set(body_goals.keys())
    frontmatter_goal_ids = set(goals)

    # Goals in frontmatter but not in body
    missing_in_body = frontmatter_goal_ids - body_goal_ids
    for goal_id in missing_in_body:
        result.add_error(
            ValidationError(
                file=str(charter_path),
                message=f"Goal '{goal_id}' in goals but no matching '### {goal_id}:' header in body",
                code="MISSING_GOAL_HEADER",
                field="goals",
            )
        )

    # Goals in body but not in frontmatter
    missing_in_frontmatter = body_goal_ids - frontmatter_goal_ids
    for goal_id in missing_in_frontmatter:
        result.add_error(
            ValidationError(
                file=str(charter_path),
                message=f"Goal header '### {goal_id}:' in body but not listed in goals",
                code="UNDECLARED_GOAL_HEADER",
            )
        )

    result.detail = f"1 file, {len(goals)} goals defined"
    return result


def _extract_goal_headers(charter_path: Path) -> dict[str, str]:
    """
    Extract goal headers from Charter.md body.

    Returns dict of goal_id -> title from headers matching '### G-{number}: {Title}'
    """
    goals = {}
    goal_header_pattern = re.compile(r"^###\s+(G-\d+):\s*(.*)$", re.MULTILINE)

    try:
        content = charter_path.read_text()
        # Skip frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]

        for match in goal_header_pattern.finditer(content):
            goal_id = match.group(1)
            title = match.group(2).strip()
            goals[goal_id] = title

    except Exception:
        pass

    return goals


@jig.implements("S-075")
def validate_goal_references(
    charter_path: Path,
    outcome_dir: Path,
    architecture_dir: Optional[Path] = None,
) -> ValidationResult:
    """
    Validate that all goal references point to valid Charter goals.

    Checks:
    - Outcome goals reference valid goals (if present)
    - Architecture goals reference valid goals (if present)
    """
    result = ValidationResult(passed=True, phase_name="goal references")

    # Load valid goals from Charter
    valid_goals = set()
    if charter_path.exists():
        frontmatter = _parse_frontmatter(charter_path)
        if frontmatter and "goals" in frontmatter:
            valid_goals = set(frontmatter["goals"])

    if not valid_goals:
        # No goals defined, skip reference validation
        result.detail = "0 goal references (no charter goals defined)"
        return result

    total_references = 0
    invalid_references = 0

    # Check outcomes
    for outcome_file in sorted(outcome_dir.glob("O-*.md")):
        frontmatter = _parse_frontmatter(outcome_file)
        if frontmatter is None:
            continue

        outcome_goals = frontmatter.get("goals", [])
        if isinstance(outcome_goals, list):
            for goal_id in outcome_goals:
                total_references += 1
                if goal_id not in valid_goals:
                    invalid_references += 1
                    result.add_error(
                        ValidationError(
                            file=str(outcome_file),
                            message=f"Invalid goal reference: '{goal_id}' not defined in Charter",
                            code="INVALID_GOAL_REFERENCE",
                            field="goals",
                        )
                    )

    # Check architectures
    if architecture_dir and architecture_dir.exists():
        for arch_file in sorted(architecture_dir.glob("A-*.md")):
            frontmatter = _parse_frontmatter(arch_file)
            if frontmatter is None:
                continue

            arch_goals = frontmatter.get("goals", [])
            if isinstance(arch_goals, list):
                for goal_id in arch_goals:
                    total_references += 1
                    if goal_id not in valid_goals:
                        invalid_references += 1
                        result.add_error(
                            ValidationError(
                                file=str(arch_file),
                                message=f"Invalid goal reference: '{goal_id}' not defined in Charter",
                                code="INVALID_GOAL_REFERENCE",
                                field="goals",
                            )
                        )

    result.items_checked = total_references
    result.detail = f"{total_references} goal references ({invalid_references} invalid)"
    return result


# ============================================================================
# Architecture Validation (S-076, S-077, S-078, S-079)
# ============================================================================


@jig.implements("S-076", "S-077", "S-078", "S-079")
def validate_architecture_files(
    architecture_dir: Path,
    charter_goals: set[str],
    spec_ids: set[str],
) -> ValidationResult:
    """
    Validate architecture files against S-076, S-077, S-078, S-079 specifications.

    Checks:
    - Files are in jig/architecture/ directory (S-076)
    - Files follow A-{NNN}_{Title}.md naming pattern (S-076)
    - ID format: A-{NNN} zero-padded (S-077)
    - Required fields: id, type, title, goals (S-078)
    - goals references valid Charter goals (S-078)
    - specifications references valid spec IDs (S-079) - optional
    """
    result = ValidationResult(passed=True, phase_name="architecture")

    # Architecture directory is optional
    if not architecture_dir.exists():
        result.detail = "0 files (no architecture directory)"
        return result

    arch_files = sorted(architecture_dir.glob("A-*.md"))
    result.items_checked = len(arch_files)

    if len(arch_files) == 0:
        result.detail = "0 files"
        return result

    seen_ids = {}
    arch_id_pattern = re.compile(r"^A-\d{3}$")

    for arch_file in arch_files:
        # Parse frontmatter
        frontmatter = _parse_frontmatter(arch_file)
        if frontmatter is None:
            result.add_error(
                ValidationError(
                    file=str(arch_file),
                    message="Missing or invalid YAML frontmatter",
                    code="INVALID_FRONTMATTER",
                )
            )
            continue

        # Check required fields
        arch_id = frontmatter.get("id")
        if not arch_id:
            result.add_error(
                ValidationError(
                    file=str(arch_file),
                    message="Missing required field: 'id'",
                    code="MISSING_REQUIRED_FIELD",
                    field="id",
                )
            )
            continue

        # S-077: Check ID format
        if not arch_id_pattern.match(arch_id):
            result.add_error(
                ValidationError(
                    file=str(arch_file),
                    message=f"Invalid ID format: '{arch_id}' (must match A-NNN pattern, e.g., A-001)",
                    code="INVALID_ID_FORMAT",
                    field="id",
                )
            )

        # Check ID uniqueness
        if arch_id in seen_ids:
            result.add_error(
                ValidationError(
                    file=str(arch_file),
                    message=f"Duplicate ID '{arch_id}' (also in {seen_ids[arch_id]})",
                    code="DUPLICATE_ID",
                    field="id",
                )
            )
        else:
            seen_ids[arch_id] = arch_file.name

        # Check type field
        if frontmatter.get("type") != "architecture":
            result.add_error(
                ValidationError(
                    file=str(arch_file),
                    message=f"Invalid type: '{frontmatter.get('type')}' (must be 'architecture')",
                    code="INVALID_TYPE",
                    field="type",
                )
            )

        # Check title field
        if "title" not in frontmatter:
            result.add_error(
                ValidationError(
                    file=str(arch_file),
                    message="Missing required field: 'title'",
                    code="MISSING_REQUIRED_FIELD",
                    field="title",
                )
            )

        # Check filename format: {ID}_{Title_Snake_Case}.md
        filename_errors = validate_filename_format(arch_file, frontmatter, "A")
        for err_msg in filename_errors:
            result.add_error(
                ValidationError(
                    file=str(arch_file),
                    message=err_msg,
                    code="INVALID_FILENAME_FORMAT",
                )
            )

        # Check H1 matches frontmatter title
        h1_errors = validate_h1_matches_title(arch_file, frontmatter)
        for err_msg in h1_errors:
            result.add_error(
                ValidationError(
                    file=str(arch_file),
                    message=err_msg,
                    code="H1_TITLE_MISMATCH",
                )
            )

        # S-078: Check goals field (V2 schema - was supports_goals)
        arch_goals = frontmatter.get("goals")
        if not arch_goals:
            result.add_error(
                ValidationError(
                    file=str(arch_file),
                    message="Missing required field: 'goals'. Architecture must support at least one goal.",
                    code="MISSING_REQUIRED_FIELD",
                    field="goals",
                )
            )
        elif not isinstance(arch_goals, list):
            result.add_error(
                ValidationError(
                    file=str(arch_file),
                    message=f"goals must be an array, not {type(arch_goals).__name__}",
                    code="INVALID_FIELD_TYPE",
                    field="goals",
                )
            )
        elif len(arch_goals) == 0:
            result.add_error(
                ValidationError(
                    file=str(arch_file),
                    message="goals array is empty. Architecture must support at least one goal.",
                    code="EMPTY_GOALS",
                    field="goals",
                )
            )
        else:
            # Validate goal references
            for goal_id in arch_goals:
                if goal_id not in charter_goals:
                    result.add_error(
                        ValidationError(
                            file=str(arch_file),
                            message=f"Invalid goal reference: '{goal_id}' not defined in Charter",
                            code="INVALID_GOAL_REFERENCE",
                            field="goals",
                        )
                    )

        # S-079: Check specifications field (optional, V2 schema - was constrains)
        specifications = frontmatter.get("specifications")
        if specifications is not None:
            if not isinstance(specifications, list):
                result.add_error(
                    ValidationError(
                        file=str(arch_file),
                        message=f"specifications must be an array, not {type(specifications).__name__}",
                        code="INVALID_FIELD_TYPE",
                        field="specifications",
                    )
                )
            else:
                # Validate spec references
                for spec_id in specifications:
                    if spec_id not in spec_ids:
                        result.add_error(
                            ValidationError(
                                file=str(arch_file),
                                message=f"Invalid spec reference in specifications: '{spec_id}' does not exist",
                                code="INVALID_SPEC_REFERENCE",
                                field="specifications",
                            )
                        )

    result.detail = f"{len(arch_files)} files"
    return result


# ============================================================================
# Bidirectional Reference Consistency Validation (S-095)
# ============================================================================


@jig.implements("S-095")
def validate_bidirectional_consistency(
    spec_dir: Path,
    outcome_dir: Path,
    architecture_dir: Path,
) -> ValidationResult:
    """
    Validate bidirectional consistency between specifications and outcomes/architecture.

    Per S-095: Specification back-references must be consistent with forward-references
    from outcomes and architecture.

    Checks:
    - If O.specifications contains S, then S.outcomes must contain O
    - If S.outcomes contains O, then O.specifications must contain S
    - If A.specifications contains S, then S.architecture must contain A
    - If S.architecture contains A, then A.specifications must contain S

    Algorithm:
    1. Build forward index from outcomes: O-id -> [S-ids]
    2. Build forward index from architecture: A-id -> [S-ids]
    3. Build back index from specifications: S-id -> {outcomes: [O-ids], architecture: [A-ids]}
    4. Check forward -> back consistency (outcomes/arch reference specs)
    5. Check back -> forward consistency (specs reference outcomes/arch)
    """
    result = ValidationResult(passed=True, phase_name="bidirectional consistency")

    # Load specification back-references
    spec_back_refs: dict[str, dict[str, list[str]]] = {}
    spec_files = sorted(spec_dir.glob("S-*.md"))

    for spec_file in spec_files:
        frontmatter = _parse_frontmatter(spec_file)
        if frontmatter is None:
            continue

        spec_id = frontmatter.get("id")
        if not spec_id:
            continue

        outcomes = frontmatter.get("outcomes", [])
        architecture = frontmatter.get("architecture", [])

        spec_back_refs[spec_id] = {
            "outcomes": outcomes if isinstance(outcomes, list) else [],
            "architecture": architecture if isinstance(architecture, list) else [],
            "file": str(spec_file),
        }

    result.items_checked = len(spec_files)

    # If no specs, validation passes
    if len(spec_files) == 0:
        return result

    # Build forward index from outcomes
    outcome_forward_refs: dict[str, list[str]] = {}
    outcome_files: dict[str, str] = {}

    for outcome_file in sorted(outcome_dir.glob("O-*.md")):
        frontmatter = _parse_frontmatter(outcome_file)
        if frontmatter is None:
            continue

        outcome_id = frontmatter.get("id")
        if not outcome_id:
            continue

        specifications = frontmatter.get("specifications", [])
        outcome_forward_refs[outcome_id] = specifications if isinstance(specifications, list) else []
        outcome_files[outcome_id] = str(outcome_file)

    # Build forward index from architecture
    arch_forward_refs: dict[str, list[str]] = {}
    arch_files: dict[str, str] = {}

    if architecture_dir.exists():
        for arch_file in sorted(architecture_dir.glob("A-*.md")):
            frontmatter = _parse_frontmatter(arch_file)
            if frontmatter is None:
                continue

            arch_id = frontmatter.get("id")
            if not arch_id:
                continue

            specifications = frontmatter.get("specifications", [])
            arch_forward_refs[arch_id] = specifications if isinstance(specifications, list) else []
            arch_files[arch_id] = str(arch_file)

    # Check: Outcome -> Spec (forward) must have Spec -> Outcome (back)
    for outcome_id, spec_ids in outcome_forward_refs.items():
        for spec_id in spec_ids:
            if spec_id in spec_back_refs:
                spec_outcomes = spec_back_refs[spec_id].get("outcomes", [])
                if outcome_id not in spec_outcomes:
                    result.add_error(
                        ValidationError(
                            file=outcome_files.get(outcome_id, "unknown"),
                            message=(
                                f"Bidirectional inconsistency: Outcome '{outcome_id}' references "
                                f"specification '{spec_id}' in its specifications array, but "
                                f"'{spec_id}' does not include '{outcome_id}' in its outcomes array. "
                                f"Add '{outcome_id}' to {spec_id}'s outcomes field."
                            ),
                            code="MISSING_BACK_REFERENCE",
                        )
                    )

    # Check: Spec -> Outcome (back) must have Outcome -> Spec (forward)
    for spec_id, refs in spec_back_refs.items():
        for outcome_id in refs.get("outcomes", []):
            if outcome_id in outcome_forward_refs:
                outcome_specs = outcome_forward_refs[outcome_id]
                if spec_id not in outcome_specs:
                    result.add_error(
                        ValidationError(
                            file=refs.get("file", "unknown"),
                            message=(
                                f"Bidirectional inconsistency: Specification '{spec_id}' references "
                                f"outcome '{outcome_id}' in its outcomes array, but "
                                f"'{outcome_id}' does not include '{spec_id}' in its specifications array. "
                                f"Add '{spec_id}' to {outcome_id}'s specifications field."
                            ),
                            code="MISSING_FORWARD_REFERENCE",
                        )
                    )

    # Check: Architecture -> Spec (forward) must have Spec -> Architecture (back)
    for arch_id, spec_ids in arch_forward_refs.items():
        for spec_id in spec_ids:
            if spec_id in spec_back_refs:
                spec_arch = spec_back_refs[spec_id].get("architecture", [])
                if arch_id not in spec_arch:
                    result.add_error(
                        ValidationError(
                            file=arch_files.get(arch_id, "unknown"),
                            message=(
                                f"Bidirectional inconsistency: Architecture '{arch_id}' references "
                                f"specification '{spec_id}' in its specifications array, but "
                                f"'{spec_id}' does not include '{arch_id}' in its architecture array. "
                                f"Add '{arch_id}' to {spec_id}'s architecture field."
                            ),
                            code="MISSING_BACK_REFERENCE",
                        )
                    )

    # Check: Spec -> Architecture (back) must have Architecture -> Spec (forward)
    for spec_id, refs in spec_back_refs.items():
        for arch_id in refs.get("architecture", []):
            if arch_id in arch_forward_refs:
                arch_specs = arch_forward_refs[arch_id]
                if spec_id not in arch_specs:
                    result.add_error(
                        ValidationError(
                            file=refs.get("file", "unknown"),
                            message=(
                                f"Bidirectional inconsistency: Specification '{spec_id}' references "
                                f"architecture '{arch_id}' in its architecture array, but "
                                f"'{arch_id}' does not include '{spec_id}' in its specifications array. "
                                f"Add '{spec_id}' to {arch_id}'s specifications field."
                            ),
                            code="MISSING_FORWARD_REFERENCE",
                        )
                    )

    # Set detail
    outcome_count = len(outcome_forward_refs)
    arch_count = len(arch_forward_refs)
    error_count = len(result.errors)
    result.detail = f"{len(spec_files)} specs, {outcome_count} outcomes, {arch_count} architectures, {error_count} inconsistencies"

    return result
