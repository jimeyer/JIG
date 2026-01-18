# ABOUTME: Tests for Rule protocol, Violation, Fix, and Artifact dataclasses.
# ABOUTME: Verifies S-108 (error ID stability) and S-109 (rule spec traceability).
"""
Tests for rules/base.py foundational types.

Verifies:
- S-108: Validation Error ID Stability
- S-109: Rule Spec Traceability
"""

import json

import jig
from jig.rules.base import (
    Artifact,
    Fix,
    Rule,
    Violation,
    compute_error_id,
)


class TestViolation:
    """Tests for Violation dataclass."""

    @jig.verifies("S-108")
    def test_violation_has_required_fields(self):
        """Violation has rule_code, artifact_id, file, line, message, context."""
        v = Violation(
            rule_code="REQUIRED_FIELD",
            artifact_id="S-001",
            file="jig/specifications/S-001.md",
            line=5,
            message="Missing required field 'outcomes'",
            context={"field": "outcomes"},
        )
        assert v.rule_code == "REQUIRED_FIELD"
        assert v.artifact_id == "S-001"
        assert v.file == "jig/specifications/S-001.md"
        assert v.line == 5
        assert v.message == "Missing required field 'outcomes'"
        assert v.context == {"field": "outcomes"}

    @jig.verifies("S-108")
    def test_violation_line_optional(self):
        """Violation line number can be None."""
        v = Violation(
            rule_code="UNIQUENESS",
            artifact_id="S-001",
            file="jig/specifications/S-001.md",
            line=None,
            message="Duplicate ID 'S-001'",
            context={},
        )
        assert v.line is None

    @jig.verifies("S-108")
    def test_violation_context_defaults_to_empty_dict(self):
        """Violation context defaults to empty dict if not provided."""
        v = Violation(
            rule_code="TEST",
            artifact_id="S-001",
            file="test.md",
            line=1,
            message="Test",
        )
        assert v.context == {}


class TestComputeErrorId:
    """Tests for error ID computation per S-108."""

    @jig.verifies("S-108")
    def test_returns_12_hex_chars(self):
        """Error ID is exactly 12 lowercase hex characters."""
        error_id = compute_error_id(
            rule_code="REQUIRED_FIELD",
            artifact_id="S-001",
            context={"field": "outcomes"},
        )
        assert len(error_id) == 12
        assert all(c in "0123456789abcdef" for c in error_id)

    @jig.verifies("S-108")
    def test_same_inputs_produce_same_id(self):
        """Same logical error produces same ID across runs."""
        id1 = compute_error_id(
            rule_code="REQUIRED_FIELD",
            artifact_id="S-001",
            context={"field": "outcomes"},
        )
        id2 = compute_error_id(
            rule_code="REQUIRED_FIELD",
            artifact_id="S-001",
            context={"field": "outcomes"},
        )
        assert id1 == id2

    @jig.verifies("S-108")
    def test_different_rule_code_produces_different_id(self):
        """Different rule codes produce different IDs."""
        id1 = compute_error_id(
            rule_code="REQUIRED_FIELD",
            artifact_id="S-001",
            context={"field": "outcomes"},
        )
        id2 = compute_error_id(
            rule_code="ID_FORMAT",
            artifact_id="S-001",
            context={"field": "outcomes"},
        )
        assert id1 != id2

    @jig.verifies("S-108")
    def test_different_artifact_produces_different_id(self):
        """Different artifact IDs produce different error IDs."""
        id1 = compute_error_id(
            rule_code="REQUIRED_FIELD",
            artifact_id="S-001",
            context={"field": "outcomes"},
        )
        id2 = compute_error_id(
            rule_code="REQUIRED_FIELD",
            artifact_id="S-002",
            context={"field": "outcomes"},
        )
        assert id1 != id2

    @jig.verifies("S-108")
    def test_different_context_produces_different_id(self):
        """Different error-specific context produces different IDs."""
        id1 = compute_error_id(
            rule_code="REQUIRED_FIELD",
            artifact_id="S-001",
            context={"field": "outcomes"},
        )
        id2 = compute_error_id(
            rule_code="REQUIRED_FIELD",
            artifact_id="S-001",
            context={"field": "architecture"},
        )
        assert id1 != id2

    @jig.verifies("S-108")
    def test_context_key_order_does_not_affect_id(self):
        """Context dict key order does not affect ID (canonical JSON)."""
        id1 = compute_error_id(
            rule_code="TEST",
            artifact_id="S-001",
            context={"a": 1, "b": 2},
        )
        id2 = compute_error_id(
            rule_code="TEST",
            artifact_id="S-001",
            context={"b": 2, "a": 1},
        )
        assert id1 == id2

    @jig.verifies("S-108")
    def test_empty_context_produces_valid_id(self):
        """Empty context produces valid 12-char ID."""
        error_id = compute_error_id(
            rule_code="UNIQUENESS",
            artifact_id="S-001",
            context={},
        )
        assert len(error_id) == 12


class TestFix:
    """Tests for Fix dataclass."""

    @jig.verifies("S-104")
    def test_fix_has_required_fields(self):
        """Fix has action, target, params, auto, suggestions."""
        fix = Fix(
            action="set_field",
            target="jig/specifications/S-001.md",
            params={"field": "outcomes", "value": ["O-001"]},
            auto=True,
            suggestions=None,
        )
        assert fix.action == "set_field"
        assert fix.target == "jig/specifications/S-001.md"
        assert fix.params == {"field": "outcomes", "value": ["O-001"]}
        assert fix.auto is True
        assert fix.suggestions is None

    @jig.verifies("S-104")
    def test_fix_auto_defaults_false(self):
        """Fix auto flag defaults to False."""
        fix = Fix(
            action="manual_review",
            target="jig/specifications/S-001.md",
            params={},
        )
        assert fix.auto is False

    @jig.verifies("S-104")
    def test_fix_suggestions_for_manual_fixes(self):
        """Fix can have suggestions for manual intervention."""
        fix = Fix(
            action="resolve_duplicate",
            target="jig/specifications/S-001.md",
            params={},
            auto=False,
            suggestions=["Rename one of the duplicates", "Delete the duplicate"],
        )
        assert fix.suggestions == ["Rename one of the duplicates", "Delete the duplicate"]

    @jig.verifies("S-104")
    def test_fix_to_dict(self):
        """Fix can be serialized to dict for JSON output."""
        fix = Fix(
            action="set_field",
            target="test.md",
            params={"field": "id", "value": "S-001"},
            auto=True,
        )
        d = fix.to_dict()
        assert d["action"] == "set_field"
        assert d["target"] == "test.md"
        assert d["params"] == {"field": "id", "value": "S-001"}
        assert d["auto"] is True


class TestArtifact:
    """Tests for Artifact dataclass."""

    def test_artifact_has_required_fields(self):
        """Artifact has id, file, frontmatter."""
        artifact = Artifact(
            id="S-001",
            file="jig/specifications/S-001_Test.md",
            frontmatter={"id": "S-001", "title": "Test", "type": "specification"},
        )
        assert artifact.id == "S-001"
        assert artifact.file == "jig/specifications/S-001_Test.md"
        assert artifact.frontmatter["type"] == "specification"

    def test_artifact_kind_property(self):
        """Artifact kind derived from frontmatter type field."""
        spec = Artifact(
            id="S-001",
            file="spec.md",
            frontmatter={"type": "specification"},
        )
        outcome = Artifact(
            id="O-001",
            file="outcome.md",
            frontmatter={"type": "outcome"},
        )
        assert spec.kind == "specification"
        assert outcome.kind == "outcome"


class TestRuleProtocol:
    """Tests for Rule protocol compliance."""

    @jig.verifies("S-109")
    def test_rule_has_code_property(self):
        """Rule has code property returning unique identifier."""
        # Create a minimal Rule implementation for testing
        class TestRule:
            @property
            def code(self) -> str:
                return "TEST_RULE"

            @property
            def spec(self) -> str:
                return "S-999"

            def violations(self, ctx):
                return []

            def fix_for(self, violation):
                return None

            def apply(self, fix, ctx):
                pass

        rule = TestRule()
        assert rule.code == "TEST_RULE"

    @jig.verifies("S-109")
    def test_rule_has_spec_property(self):
        """Rule has spec property returning the spec ID it enforces."""
        class TestRule:
            @property
            def code(self) -> str:
                return "TEST_RULE"

            @property
            def spec(self) -> str:
                return "S-018"

            def violations(self, ctx):
                return []

            def fix_for(self, violation):
                return None

            def apply(self, fix, ctx):
                pass

        rule = TestRule()
        assert rule.spec == "S-018"

    @jig.verifies("S-109")
    def test_rule_violations_method(self):
        """Rule has violations method returning list of Violation."""
        class MockValidationContext:
            pass

        class TestRule:
            @property
            def code(self) -> str:
                return "TEST"

            @property
            def spec(self) -> str:
                return "S-018"

            def violations(self, ctx):
                return [
                    Violation(
                        rule_code=self.code,
                        artifact_id="S-001",
                        file="test.md",
                        line=1,
                        message="Test violation",
                    )
                ]

            def fix_for(self, violation):
                return None

            def apply(self, fix, ctx):
                pass

        rule = TestRule()
        ctx = MockValidationContext()
        violations = rule.violations(ctx)
        assert len(violations) == 1
        assert violations[0].rule_code == "TEST"

    @jig.verifies("S-104")
    def test_rule_fix_for_method(self):
        """Rule has fix_for method returning Fix for a violation."""
        class TestRule:
            @property
            def code(self) -> str:
                return "REQUIRED_FIELD"

            @property
            def spec(self) -> str:
                return "S-018"

            def violations(self, ctx):
                return []

            def fix_for(self, violation):
                return Fix(
                    action="set_field",
                    target=violation.file,
                    params={"field": violation.context.get("field"), "value": []},
                    auto=True,
                )

            def apply(self, fix, ctx):
                pass

        rule = TestRule()
        v = Violation(
            rule_code="REQUIRED_FIELD",
            artifact_id="S-001",
            file="test.md",
            line=1,
            message="Missing field",
            context={"field": "outcomes"},
        )
        fix = rule.fix_for(v)
        assert fix.action == "set_field"
        assert fix.params["field"] == "outcomes"

    def test_rule_apply_method(self):
        """Rule has apply method for executing a fix."""
        applied = []

        class MockMendContext:
            def set_field(self, file, field, value):
                applied.append((file, field, value))

        class TestRule:
            @property
            def code(self) -> str:
                return "TEST"

            @property
            def spec(self) -> str:
                return "S-018"

            def violations(self, ctx):
                return []

            def fix_for(self, violation):
                return None

            def apply(self, fix, ctx):
                ctx.set_field(fix.target, fix.params["field"], fix.params["value"])

        rule = TestRule()
        mend_ctx = MockMendContext()
        fix = Fix(
            action="set_field",
            target="test.md",
            params={"field": "id", "value": "S-001"},
            auto=True,
        )
        rule.apply(fix, mend_ctx)
        assert applied == [("test.md", "id", "S-001")]
