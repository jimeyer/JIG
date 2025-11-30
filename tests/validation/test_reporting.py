"""
Tests for validation reporting (human and JSON formats).
"""

import json
from pathlib import Path

import jig
from jig.validation.models import ValidationError, ValidationResult
from jig.validation.reporting import format_as_json, format_validation_results


@jig.verifies("S-026")
def test_format_as_json_success():
    """JSON format for successful validation includes status and empty errors."""
    intent_result = ValidationResult(passed=True, phase_name="intent", items_checked=5)
    brick_result = ValidationResult(passed=True, phase_name="bricks", items_checked=3)

    results = {
        "intent": intent_result,
        "bricks": brick_result,
    }

    json_output = format_as_json(results)
    data = json.loads(json_output)

    assert data["status"] == "passed"
    assert data["intent"]["passed"] is True
    assert data["intent"]["errors"] == []
    assert data["bricks"]["passed"] is True
    assert data["bricks"]["errors"] == []
    assert data["summary"]["total_errors"] == 0
    assert data["summary"]["total_warnings"] == 0


@jig.verifies("S-026")
def test_format_as_json_with_errors():
    """JSON format includes structured error codes and fields."""
    result = ValidationResult(passed=False, phase_name="specifications", items_checked=2)
    result.add_error(
        ValidationError(
            file="jig/specifications/S-001.md",
            line=5,
            code="MISSING_REQUIRED_FIELD",
            message="Missing required field: 'id'",
            severity="error",
            field="id",
        )
    )
    result.add_error(
        ValidationError(
            file="jig/specifications/S-002.md",
            line=None,
            code="INVALID_ID_FORMAT",
            message="Invalid ID format: 'INVALID-001' (expected S-NNN pattern)",
            severity="error",
            field="id",
        )
    )

    results = {"intent": result}
    json_output = format_as_json(results)
    data = json.loads(json_output)

    assert data["status"] == "failed"
    assert data["intent"]["passed"] is False
    assert len(data["intent"]["errors"]) == 2

    # Check first error structure
    error1 = data["intent"]["errors"][0]
    assert error1["file"] == "jig/specifications/S-001.md"
    assert error1["line"] == 5
    assert error1["code"] == "MISSING_REQUIRED_FIELD"
    assert error1["message"] == "Missing required field: 'id'"
    assert error1["severity"] == "error"
    assert error1["field"] == "id"

    # Check second error structure
    error2 = data["intent"]["errors"][1]
    assert error2["file"] == "jig/specifications/S-002.md"
    assert error2["line"] is None
    assert error2["code"] == "INVALID_ID_FORMAT"

    # Check summary
    assert data["summary"]["total_errors"] == 2
    assert data["summary"]["total_warnings"] == 0


@jig.verifies("S-026")
def test_format_as_json_multiple_phases():
    """JSON format handles multiple validation phases."""
    intent_result = ValidationResult(passed=False, phase_name="intent", items_checked=3)
    intent_result.add_error(
        ValidationError(
            file="jig/specifications/S-001.md",
            code="MISSING_REQUIRED_FIELD",
            message="Missing required field: 'id'",
        )
    )

    brick_result = ValidationResult(passed=False, phase_name="bricks", items_checked=2)
    brick_result.add_error(
        ValidationError(
            file="jig/bricks.yaml",
            code="PARTITION_GAP",
            message="Function 'F-test.func' in 0 bricks",
        )
    )
    brick_result.add_error(
        ValidationError(
            file="jig/bricks.yaml",
            code="PARTITION_OVERLAP",
            message="Function 'F-other.func' in multiple bricks",
        )
    )

    results = {
        "intent": intent_result,
        "bricks": brick_result,
    }

    json_output = format_as_json(results)
    data = json.loads(json_output)

    assert data["status"] == "failed"
    assert data["intent"]["passed"] is False
    assert len(data["intent"]["errors"]) == 1
    assert data["bricks"]["passed"] is False
    assert len(data["bricks"]["errors"]) == 2
    assert data["summary"]["total_errors"] == 3


@jig.verifies("S-026")
def test_format_as_json_is_valid_json():
    """JSON output is valid and parseable."""
    result = ValidationResult(passed=True, phase_name="test", items_checked=1)
    results = {"test": result}

    json_output = format_as_json(results)

    # Should not raise exception
    data = json.loads(json_output)

    # Should be a dictionary
    assert isinstance(data, dict)
    assert "status" in data
    assert "summary" in data


@jig.verifies("S-026")
def test_format_human_readable():
    """Human-readable format includes check marks and error details."""
    success_result = ValidationResult(passed=True, phase_name="specifications", items_checked=5)

    output = format_validation_results([success_result])

    assert "✓" in output or "specifications" in output.lower()
    assert "5" in output


@jig.verifies("S-026")
def test_format_human_readable_with_errors():
    """Human-readable format shows errors with file paths."""
    result = ValidationResult(passed=False, phase_name="specifications", items_checked=2)
    result.add_error(
        ValidationError(
            file="jig/specifications/S-001.md",
            line=5,
            message="Missing required field: 'id'",
        )
    )

    output = format_validation_results([result])

    assert "✗" in output or "error" in output.lower()
    assert "S-001.md" in output
    assert "Missing required field" in output


@jig.verifies("S-026")
def test_json_schema_consistency():
    """JSON schema is consistent across different validation phases."""
    intent_result = ValidationResult(passed=False, phase_name="intent", items_checked=1)
    intent_result.add_error(
        ValidationError(
            file="test1.md",
            line=10,
            code="CODE1",
            message="Message 1",
            severity="error",
        )
    )

    brick_result = ValidationResult(passed=False, phase_name="bricks", items_checked=1)
    brick_result.add_error(
        ValidationError(
            file="test2.yaml",
            line=20,
            code="CODE2",
            message="Message 2",
            severity="error",
        )
    )

    results = {
        "intent": intent_result,
        "bricks": brick_result,
    }

    json_output = format_as_json(results)
    data = json.loads(json_output)

    # Both phases should have same structure
    assert "passed" in data["intent"]
    assert "errors" in data["intent"]
    assert "passed" in data["bricks"]
    assert "errors" in data["bricks"]

    # All errors should have same fields
    intent_error = data["intent"]["errors"][0]
    brick_error = data["bricks"]["errors"][0]

    assert set(intent_error.keys()) == set(brick_error.keys())
    assert "file" in intent_error
    assert "line" in intent_error
    assert "code" in intent_error
    assert "message" in intent_error
    assert "severity" in intent_error
