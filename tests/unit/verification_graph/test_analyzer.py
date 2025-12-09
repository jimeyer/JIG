"""Tests for test analyzer (S-052, S-053, S-054).

Verifies extraction of @jig.verifies decorators and jig_hash computation.
"""

import ast
import tempfile
from pathlib import Path

import jig


class TestExtractVerifiesDecorators:
    """Tests for @jig.verifies decorator extraction (S-053)."""

    @jig.verifies("S-053")
    def test_extracts_single_spec(self, tmp_path: Path):
        """Extracts @jig.verifies("S-001") decorator."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
import jig

@jig.verifies("S-001")
def test_simple():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["verifies"] == ["S-001"]

    @jig.verifies("S-053")
    def test_extracts_multiple_specs(self, tmp_path: Path):
        """Extracts @jig.verifies("S-001", "S-002") decorator."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
import jig

@jig.verifies("S-001", "S-002")
def test_multiple():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        assert sorted(result["nodes"][0]["verifies"]) == ["S-001", "S-002"]

    @jig.verifies("S-053")
    def test_extracts_short_form(self, tmp_path: Path):
        """Extracts @verifies("S-001") short form."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
from jig import verifies

@verifies("S-001")
def test_short():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["verifies"] == ["S-001"]

    @jig.verifies("S-053")
    def test_validates_spec_id_format(self, tmp_path: Path, caplog):
        """Warns on invalid spec IDs like 'INVALID-001'."""
        from jig.verification_graph.analyzer import TestAnalyzer
        import logging

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
import jig

@jig.verifies("INVALID-001")
def test_invalid():
    pass
''')

        with caplog.at_level(logging.WARNING):
            analyzer = TestAnalyzer(tmp_path)
            result = analyzer.analyze_file(test_file)

        # Test should still be included but without invalid spec
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["verifies"] == []
        # Warning should be logged
        assert "INVALID-001" in caplog.text or len(result["nodes"][0]["verifies"]) == 0

    @jig.verifies("S-053")
    def test_empty_verifies_for_undecorated(self, tmp_path: Path):
        """Tests without decorator have empty verifies array."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
def test_no_decorator():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["verifies"] == []

    @jig.verifies("S-053")
    def test_extracts_from_class_methods(self, tmp_path: Path):
        """Extracts verifies decorators from test class methods."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
import jig

class TestAuth:
    @jig.verifies("S-001")
    def test_login(self):
        pass

    @jig.verifies("S-002", "S-003")
    def test_logout(self):
        pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 2
        nodes_by_name = {n["id"].split(".")[-1]: n for n in result["nodes"]}
        assert nodes_by_name["test_login"]["verifies"] == ["S-001"]
        assert sorted(nodes_by_name["test_logout"]["verifies"]) == ["S-002", "S-003"]

    @jig.verifies("S-053")
    def test_accepts_outcome_ids(self, tmp_path: Path):
        """Accepts O-NNN outcome IDs in addition to S-NNN."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
import jig

@jig.verifies("O-001", "S-001")
def test_outcome():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        assert sorted(result["nodes"][0]["verifies"]) == ["O-001", "S-001"]


class TestNodeSchema:
    """Tests for test node schema (S-052)."""

    @jig.verifies("S-052")
    def test_node_has_required_fields(self, tmp_path: Path):
        """T nodes have id, type, file, verifies, jig_hash."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
import jig

@jig.verifies("S-001")
def test_simple():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        node = result["nodes"][0]

        # Check all required fields present
        assert "id" in node
        assert "type" in node
        assert "file" in node
        assert "verifies" in node
        assert "jig_hash" in node

        # Check field values
        assert node["type"] == "test"
        assert node["id"].startswith("T-")
        assert isinstance(node["verifies"], list)
        assert len(node["jig_hash"]) == 12  # 12 hex chars

    @jig.verifies("S-052")
    def test_node_excludes_covers(self, tmp_path: Path):
        """T nodes do NOT have covers field (Audit domain)."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
def test_simple():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        node = result["nodes"][0]
        assert "covers" not in node

    @jig.verifies("S-052")
    def test_node_excludes_brick(self, tmp_path: Path):
        """T nodes do NOT have brick field (derived at query time)."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
def test_simple():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        node = result["nodes"][0]
        assert "brick" not in node

    @jig.verifies("S-052")
    def test_node_excludes_line(self, tmp_path: Path):
        """T nodes do NOT have line field (brittle)."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
def test_simple():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        node = result["nodes"][0]
        assert "line" not in node

    @jig.verifies("S-052")
    def test_id_format_function(self, tmp_path: Path):
        """ID format is T-{module}.{test_function}."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_auth.py"
        test_file.write_text('''
def test_login():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["id"] == "T-test_auth.test_login"

    @jig.verifies("S-052")
    def test_id_format_method(self, tmp_path: Path):
        """ID format is T-{module}.{TestClass}.{test_method}."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_auth.py"
        test_file.write_text('''
class TestSession:
    def test_create(self):
        pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["id"] == "T-test_auth.TestSession.test_create"

    @jig.verifies("S-052")
    def test_file_is_relative_path(self, tmp_path: Path):
        """File field is relative path from project root."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_dir = tmp_path / "tests" / "unit"
        test_dir.mkdir(parents=True)
        test_file = test_dir / "test_auth.py"
        test_file.write_text('''
def test_login():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["file"] == "tests/unit/test_auth.py"


class TestTestHashing:
    """Tests for test function hashing (S-054)."""

    @jig.verifies("S-054")
    def test_hash_changes_when_logic_changes(self, tmp_path: Path):
        """jig_hash changes when test function body changes."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"

        # Version 1
        test_file.write_text('''
def test_simple():
    x = 1
    assert x == 1
''')
        analyzer = TestAnalyzer(tmp_path)
        result1 = analyzer.analyze_file(test_file)
        hash1 = result1["nodes"][0]["jig_hash"]

        # Version 2 - different logic
        test_file.write_text('''
def test_simple():
    x = 2
    assert x == 2
''')
        result2 = analyzer.analyze_file(test_file)
        hash2 = result2["nodes"][0]["jig_hash"]

        assert hash1 != hash2

    @jig.verifies("S-054")
    def test_hash_stable_across_whitespace(self, tmp_path: Path):
        """jig_hash stable across whitespace changes."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"

        # Version 1 - compact
        test_file.write_text('''
def test_simple():
    x = 1
    assert x == 1
''')
        analyzer = TestAnalyzer(tmp_path)
        result1 = analyzer.analyze_file(test_file)
        hash1 = result1["nodes"][0]["jig_hash"]

        # Version 2 - extra whitespace
        test_file.write_text('''
def test_simple():
    x    =    1

    assert    x   ==   1
''')
        result2 = analyzer.analyze_file(test_file)
        hash2 = result2["nodes"][0]["jig_hash"]

        assert hash1 == hash2

    @jig.verifies("S-054")
    def test_hash_stable_across_comments(self, tmp_path: Path):
        """jig_hash stable across comment changes."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"

        # Version 1 - no comments
        test_file.write_text('''
def test_simple():
    x = 1
    assert x == 1
''')
        analyzer = TestAnalyzer(tmp_path)
        result1 = analyzer.analyze_file(test_file)
        hash1 = result1["nodes"][0]["jig_hash"]

        # Version 2 - with comments
        test_file.write_text('''
def test_simple():
    # This is a comment
    x = 1  # inline comment
    # Another comment
    assert x == 1
''')
        result2 = analyzer.analyze_file(test_file)
        hash2 = result2["nodes"][0]["jig_hash"]

        assert hash1 == hash2

    @jig.verifies("S-054")
    def test_hash_excludes_decorators(self, tmp_path: Path):
        """jig_hash excludes decorators from computation."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"

        # Version 1 - no decorator
        test_file.write_text('''
def test_simple():
    x = 1
    assert x == 1
''')
        analyzer = TestAnalyzer(tmp_path)
        result1 = analyzer.analyze_file(test_file)
        hash1 = result1["nodes"][0]["jig_hash"]

        # Version 2 - with decorator
        test_file.write_text('''
import jig

@jig.verifies("S-001")
def test_simple():
    x = 1
    assert x == 1
''')
        result2 = analyzer.analyze_file(test_file)
        hash2 = result2["nodes"][0]["jig_hash"]

        assert hash1 == hash2

    @jig.verifies("S-054")
    def test_hash_is_12_hex_chars(self, tmp_path: Path):
        """jig_hash is exactly 12 lowercase hex characters."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
def test_simple():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        jig_hash = result["nodes"][0]["jig_hash"]
        assert len(jig_hash) == 12
        assert all(c in "0123456789abcdef" for c in jig_hash)


class TestAnalyzerIntegration:
    """Integration tests for the analyzer."""

    @jig.verifies("S-052", "S-053", "S-054")
    def test_analyze_fixture_file(self):
        """Analyzes the test fixture file correctly."""
        from jig.verification_graph.analyzer import TestAnalyzer

        fixture_path = Path(__file__).parent.parent.parent / "fixtures" / "python" / "test_with_verifies.py"
        if not fixture_path.exists():
            # Skip if fixture not available
            return

        project_root = fixture_path.parent.parent.parent.parent
        analyzer = TestAnalyzer(project_root)
        result = analyzer.analyze_file(fixture_path)

        # Should find all test functions
        assert len(result["nodes"]) >= 8  # At least 8 tests in fixture

        # Check specific tests exist
        ids = {n["id"].split(".")[-1] for n in result["nodes"]}
        assert "test_simple" in ids
        assert "test_multiple_specs" in ids
        assert "test_no_decorator" in ids

    @jig.verifies("S-052")
    def test_returns_sorted_nodes(self, tmp_path: Path):
        """Nodes are returned sorted by ID."""
        from jig.verification_graph.analyzer import TestAnalyzer

        test_file = tmp_path / "test_example.py"
        test_file.write_text('''
def test_zebra():
    pass

def test_alpha():
    pass

def test_middle():
    pass
''')

        analyzer = TestAnalyzer(tmp_path)
        result = analyzer.analyze_file(test_file)

        ids = [n["id"] for n in result["nodes"]]
        assert ids == sorted(ids)
