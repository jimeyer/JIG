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
    - Required fields: id, type
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
    - Required fields: id, type
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

    return result


@jig.implements("S-020")
def validate_decorator_files(
    source_dir: Path,
    spec_dir: Path,
    outcome_dir: Optional[Path] = None,
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

    # Find all Python files
    python_files = list(source_dir.rglob("*.py"))
    result.items_checked = len(python_files)

    for py_file in python_files:
        try:
            source = py_file.read_text()
            tree = ast.parse(source, filename=str(py_file))

            # Visit all function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    _validate_function_decorators(node, py_file, valid_ids, result)

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
) -> None:
    """Validate decorators on a function definition."""
    for decorator in func_node.decorator_list:
        # Check for @jig.implements and @jig.verifies
        if isinstance(decorator, ast.Call):
            if _is_jig_decorator(decorator, "implements") or _is_jig_decorator(decorator, "verifies"):
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
