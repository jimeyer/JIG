# ABOUTME: Tests for jig.query.validate module — validation query filtering.
# ABOUTME: Verifies filter_errors_by_specs and query_validate with scope filtering.

"""Tests for query.validate module.

Tests filter_errors_by_specs() and query_validate() for filtering
validation results by intent/brick/full scope.
"""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import pytest

import jig
from jig.query.validate import (
    BRICK_SPECS,
    INTENT_SPECS,
    filter_errors_by_specs,
    query_validate,
)


@dataclass
class _FakeConfig:
    """Minimal JigConfig stand-in for tests."""

    project_root: Path
    config_file_path: Path | None = None
    has_config_file: bool = False


def _make_error(spec: str, message: str = "test error") -> dict:
    """Create a mock validation error dict."""
    return {
        "id": f"err-{spec}",
        "spec": spec,
        "message": message,
        "file": "test.md",
        "line": 1,
        "fix": {"auto": False, "suggestions": ["fix it"]},
    }


def _make_result(errors: list[dict]) -> dict:
    """Create a mock validation result with proper summary."""
    auto = sum(1 for e in errors if e.get("fix", {}).get("auto", False))
    return {
        "errors": errors,
        "summary": {
            "total": len(errors),
            "auto_fixable": auto,
            "manual": len(errors) - auto,
        },
        "counts": {"specs": 5, "outcomes": 2, "bricks": 3},
    }


@jig.verifies("S-023", "S-024", "S-025")
class TestFilterErrorsBySpecs:
    """filter_errors_by_specs keeps only errors matching given spec IDs."""

    def test_filters_to_matching_specs(self) -> None:
        errors = [_make_error("S-018"), _make_error("S-021"), _make_error("S-042")]
        result = _make_result(errors)

        filtered = filter_errors_by_specs(result, {"S-018", "S-042"})

        assert len(filtered["errors"]) == 2
        specs = {e["spec"] for e in filtered["errors"]}
        assert specs == {"S-018", "S-042"}

    def test_empty_spec_set_returns_no_errors(self) -> None:
        errors = [_make_error("S-018")]
        result = _make_result(errors)

        filtered = filter_errors_by_specs(result, set())
        assert len(filtered["errors"]) == 0

    def test_summary_recalculated(self) -> None:
        errors = [_make_error("S-018"), _make_error("S-021")]
        result = _make_result(errors)

        filtered = filter_errors_by_specs(result, {"S-018"})
        assert filtered["summary"]["total"] == 1


@jig.verifies("S-025")
class TestQueryValidateFull:
    """query_validate with scope='full' returns unfiltered results."""

    @patch("jig.query.validate.validate")
    def test_full_returns_unfiltered(self, mock_validate, tmp_path: Path) -> None:
        errors = [_make_error("S-018"), _make_error("S-021"), _make_error("S-099")]
        mock_validate.return_value = _make_result(errors)

        config = _FakeConfig(project_root=tmp_path)
        result = query_validate(config, scope="full")

        assert len(result["errors"]) == 3
        mock_validate.assert_called_once_with(tmp_path)


@jig.verifies("S-023")
class TestQueryValidateIntent:
    """query_validate with scope='intent' filters to INTENT_SPECS."""

    @patch("jig.query.validate.validate")
    def test_intent_filters_correctly(self, mock_validate, tmp_path: Path) -> None:
        # Mix of intent and non-intent errors
        errors = [_make_error("S-018"), _make_error("S-021"), _make_error("S-042")]
        mock_validate.return_value = _make_result(errors)

        config = _FakeConfig(project_root=tmp_path)
        result = query_validate(config, scope="intent")

        result_specs = {e["spec"] for e in result["errors"]}
        # S-018 and S-042 are in INTENT_SPECS, S-021 is not
        assert "S-018" in result_specs
        assert "S-042" in result_specs
        assert "S-021" not in result_specs


@jig.verifies("S-024")
class TestQueryValidateBricks:
    """query_validate with scope='bricks' filters to BRICK_SPECS."""

    @patch("jig.query.validate.validate")
    def test_bricks_filters_correctly(self, mock_validate, tmp_path: Path) -> None:
        errors = [_make_error("S-018"), _make_error("S-021"), _make_error("S-035")]
        mock_validate.return_value = _make_result(errors)

        config = _FakeConfig(project_root=tmp_path)
        result = query_validate(config, scope="bricks")

        result_specs = {e["spec"] for e in result["errors"]}
        # S-021 and S-035 are in BRICK_SPECS, S-018 is not
        assert "S-021" in result_specs
        assert "S-035" in result_specs
        assert "S-018" not in result_specs
