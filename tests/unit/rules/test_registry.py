# ABOUTME: Tests for rules registry - RULES list and lookup indexes.
# ABOUTME: Verifies S-104 (fix templates) and S-109 (rule spec traceability).
"""
Tests for rules/registry.py - RULES list and indexes.

Verifies:
- S-104: Validation Fix Template Output (rules produce fix templates)
- S-109: Rule Spec Traceability (rules reference specs)
"""

import jig
from jig.rules.base import Rule


class TestRulesRegistry:
    """Tests for RULES list."""

    @jig.verifies("S-109")
    def test_rules_list_exists_and_is_non_empty(self):
        """RULES list contains rule instances."""
        from jig.rules.registry import RULES

        assert isinstance(RULES, list)
        assert len(RULES) > 0

    @jig.verifies("S-109")
    def test_all_rules_implement_rule_protocol(self):
        """All rules in RULES implement the Rule protocol."""
        from jig.rules.registry import RULES

        for rule in RULES:
            assert isinstance(rule, Rule), f"{rule} does not implement Rule protocol"
            assert hasattr(rule, "code")
            assert hasattr(rule, "spec")
            assert hasattr(rule, "violations")
            assert hasattr(rule, "fix_for")
            assert hasattr(rule, "apply")

    @jig.verifies("S-109")
    def test_all_rules_have_code_property(self):
        """All rules have non-empty code property."""
        from jig.rules.registry import RULES

        codes = [rule.code for rule in RULES]
        assert all(code for code in codes), "All rules must have a code"

    @jig.verifies("S-109")
    def test_all_rules_have_spec_property(self):
        """All rules have spec property referencing S-### ID."""
        from jig.rules.registry import RULES

        for rule in RULES:
            spec = rule.spec
            assert spec, f"Rule {rule.code} must have a spec"
            # Spec should match S-### pattern
            assert spec.startswith("S-"), f"Rule {rule.code} spec must be S-### format, got {spec}"


class TestRulesByCodeIndex:
    """Tests for RULES_BY_CODE lookup index."""

    @jig.verifies("S-109")
    def test_rules_by_code_exists(self):
        """RULES_BY_CODE index exists and is a dict."""
        from jig.rules.registry import RULES_BY_CODE

        assert isinstance(RULES_BY_CODE, dict)

    @jig.verifies("S-109")
    def test_rules_by_code_maps_code_to_rule(self):
        """RULES_BY_CODE maps rule codes to rules."""
        from jig.rules.registry import RULES, RULES_BY_CODE

        # Should have at least one entry
        assert len(RULES_BY_CODE) > 0

        # Check some codes are in the index
        for rule in RULES[:5]:  # Check first 5
            assert rule.code in RULES_BY_CODE
            assert RULES_BY_CODE[rule.code] == rule

    @jig.verifies("S-109")
    def test_all_rules_indexed_by_code(self):
        """All rules in RULES are indexed in RULES_BY_CODE."""
        from jig.rules.registry import RULES, RULES_BY_CODE

        for rule in RULES:
            assert rule.code in RULES_BY_CODE, f"Rule {rule.code} not in RULES_BY_CODE"


class TestRulesBySpecIndex:
    """Tests for RULES_BY_SPEC lookup index."""

    @jig.verifies("S-109")
    def test_rules_by_spec_exists(self):
        """RULES_BY_SPEC index exists and is a dict."""
        from jig.rules.registry import RULES_BY_SPEC

        assert isinstance(RULES_BY_SPEC, dict)

    @jig.verifies("S-109")
    def test_rules_by_spec_maps_spec_to_rules(self):
        """RULES_BY_SPEC maps spec IDs to list of rules."""
        from jig.rules.registry import RULES_BY_SPEC

        # Should have at least one entry
        assert len(RULES_BY_SPEC) > 0

        # Each value should be a list
        for spec_id, rules in RULES_BY_SPEC.items():
            assert isinstance(rules, list), f"{spec_id} should map to list"
            assert len(rules) > 0, f"{spec_id} should have at least one rule"

    @jig.verifies("S-109")
    def test_all_rules_indexed_by_spec(self):
        """All rules in RULES are indexed in RULES_BY_SPEC."""
        from jig.rules.registry import RULES, RULES_BY_SPEC

        for rule in RULES:
            spec = rule.spec
            assert spec in RULES_BY_SPEC, f"Spec {spec} not in RULES_BY_SPEC"
            assert rule in RULES_BY_SPEC[spec], f"Rule {rule.code} not in RULES_BY_SPEC[{spec}]"


class TestRegistryRuleTypes:
    """Tests that registry contains expected rule types."""

    @jig.verifies("S-109")
    def test_has_required_field_rules(self):
        """Registry has RequiredFieldRule instances."""
        from jig.rules.registry import RULES

        codes = [r.code for r in RULES]
        assert any("REQUIRED" in code for code in codes)

    @jig.verifies("S-109")
    def test_has_id_format_rules(self):
        """Registry has IdFormatRule instances."""
        from jig.rules.registry import RULES

        codes = [r.code for r in RULES]
        assert any("ID_FORMAT" in code for code in codes)

    @jig.verifies("S-109")
    def test_has_filename_sync_rules(self):
        """Registry has FilenameSyncRule instances."""
        from jig.rules.registry import RULES

        codes = [r.code for r in RULES]
        assert any("FILENAME" in code for code in codes)

    @jig.verifies("S-109")
    def test_has_header_sync_rules(self):
        """Registry has HeaderSyncRule instances."""
        from jig.rules.registry import RULES

        codes = [r.code for r in RULES]
        assert any("HEADER" in code for code in codes)

    @jig.verifies("S-109")
    def test_has_reference_validity_rules(self):
        """Registry has ReferenceValidityRule instances."""
        from jig.rules.registry import RULES

        codes = [r.code for r in RULES]
        assert any("REFS_VALID" in code for code in codes)

    @jig.verifies("S-109")
    def test_has_bidirectional_link_rules(self):
        """Registry has BidirectionalLinkRule instances."""
        from jig.rules.registry import RULES

        codes = [r.code for r in RULES]
        assert any("BIDIRECTIONAL" in code for code in codes)

    @jig.verifies("S-109")
    def test_has_coverage_rules(self):
        """Registry has CoverageRule instances."""
        from jig.rules.registry import RULES

        codes = [r.code for r in RULES]
        assert any("COVERAGE" in code for code in codes)
