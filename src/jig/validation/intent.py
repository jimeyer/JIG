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

        # Check filename matches ID
        expected_filename = f"{spec_id}.md"
        if spec_file.name != expected_filename:
            result.add_error(
                ValidationError(
                    file=str(spec_file),
                    message=f"Filename '{spec_file.name}' does not match ID '{spec_id}' (expected '{expected_filename}')",
                    code="FILENAME_ID_MISMATCH",
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
    - Required fields: id, title, type, specifies
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

        if "specifies" not in frontmatter:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message="Missing required field: 'specifies'",
                    code="MISSING_REQUIRED_FIELD",
                    field="specifies",
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
        specifies = frontmatter.get("specifies", [])
        if isinstance(specifies, list):
            total_spec_references += len(specifies)

    # Set detail for display
    result.detail = f"{len(outcome_files)} files, {total_spec_references} spec references"

    return result


@jig.implements("S-042")
def validate_outcome_completeness(outcome_dir: Path) -> ValidationResult:
    """
    Validate that outcomes have non-empty specifies arrays.

    Per S-042: All outcomes SHALL specify at least one specification.
    Empty specifies arrays are incomplete and prevent O→S→TDD workflow.

    Checks:
    - Each outcome has 'specifies' field (checked by validate_outcome_files)
    - 'specifies' array is non-empty (has at least one spec ID)
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
        specifies = frontmatter.get("specifies", [])

        # Check if specifies array is empty
        if isinstance(specifies, list) and len(specifies) == 0:
            result.add_error(
                ValidationError(
                    file=str(outcome_file),
                    message=f"Outcome completeness: Outcome '{outcome_id}' has empty specifies array. Outcomes must decompose into at least one concrete specification.",
                    code="EMPTY_SPECIFIES",
                    field="specifies",
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
    - Each spec is referenced in at least one outcome's 'specifies' array
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
        specifies = frontmatter.get("specifies", [])

        if isinstance(specifies, list):
            for spec_id in specifies:
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
                    field="specifies",
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
