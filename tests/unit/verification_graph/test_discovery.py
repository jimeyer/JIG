"""Tests for test file discovery (S-051).

Verifies the verification graph discovers all test files following pytest conventions.
"""

import tempfile
from pathlib import Path

import jig


class TestDiscoverTestFiles:
    """Tests for discover_test_files function."""

    @jig.verifies("S-051")
    def test_discovers_test_prefix_pattern(self, tmp_path: Path):
        """Discovers files matching test_*.py pattern."""
        from jig.verification_graph.discovery import discover_test_files

        # Create test directory structure
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_auth.py").write_text("def test_login(): pass")
        (test_dir / "test_utils.py").write_text("def test_helper(): pass")
        (test_dir / "conftest.py").write_text("# not a test file")

        files = discover_test_files(tmp_path, test_dir=test_dir)

        assert len(files) == 2
        filenames = {f.name for f in files}
        assert "test_auth.py" in filenames
        assert "test_utils.py" in filenames
        assert "conftest.py" not in filenames

    @jig.verifies("S-051")
    def test_discovers_test_suffix_pattern(self, tmp_path: Path):
        """Discovers files matching *_test.py pattern."""
        from jig.verification_graph.discovery import discover_test_files

        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "auth_test.py").write_text("def test_login(): pass")
        (test_dir / "utils_test.py").write_text("def test_helper(): pass")

        files = discover_test_files(tmp_path, test_dir=test_dir)

        assert len(files) == 2
        filenames = {f.name for f in files}
        assert "auth_test.py" in filenames
        assert "utils_test.py" in filenames

    @jig.verifies("S-051")
    def test_discovers_nested_test_files(self, tmp_path: Path):
        """Discovers test files in nested directories."""
        from jig.verification_graph.discovery import discover_test_files

        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "unit").mkdir()
        (test_dir / "integration").mkdir()
        (test_dir / "test_root.py").write_text("pass")
        (test_dir / "unit" / "test_auth.py").write_text("pass")
        (test_dir / "integration" / "test_api.py").write_text("pass")

        files = discover_test_files(tmp_path, test_dir=test_dir)

        assert len(files) == 3
        filenames = {f.name for f in files}
        assert "test_root.py" in filenames
        assert "test_auth.py" in filenames
        assert "test_api.py" in filenames

    @jig.verifies("S-051")
    def test_default_test_directory(self, tmp_path: Path):
        """Default test directory is tests/ relative to project root."""
        from jig.verification_graph.discovery import discover_test_files

        # Create default tests/ directory
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_default.py").write_text("pass")

        # Don't specify test_dir - should use default
        files = discover_test_files(tmp_path)

        assert len(files) == 1
        assert files[0].name == "test_default.py"

    @jig.verifies("S-051")
    def test_excludes_pycache(self, tmp_path: Path):
        """Excludes __pycache__/ directories."""
        from jig.verification_graph.discovery import discover_test_files

        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_real.py").write_text("pass")

        # Create __pycache__ with test file (should be excluded)
        pycache = test_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "test_cached.py").write_text("pass")

        files = discover_test_files(tmp_path, test_dir=test_dir)

        assert len(files) == 1
        assert files[0].name == "test_real.py"

    @jig.verifies("S-051")
    def test_excludes_venv(self, tmp_path: Path):
        """Excludes .venv/ directories."""
        from jig.verification_graph.discovery import discover_test_files

        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_real.py").write_text("pass")

        # Create .venv with test file (should be excluded)
        venv = test_dir / ".venv"
        venv.mkdir()
        (venv / "test_venv.py").write_text("pass")

        files = discover_test_files(tmp_path, test_dir=test_dir)

        assert len(files) == 1
        assert files[0].name == "test_real.py"

    @jig.verifies("S-051")
    def test_excludes_node_modules(self, tmp_path: Path):
        """Excludes node_modules/ directories."""
        from jig.verification_graph.discovery import discover_test_files

        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_real.py").write_text("pass")

        # Create node_modules with test file (should be excluded)
        node_modules = test_dir / "node_modules"
        node_modules.mkdir()
        (node_modules / "test_node.py").write_text("pass")

        files = discover_test_files(tmp_path, test_dir=test_dir)

        assert len(files) == 1
        assert files[0].name == "test_real.py"

    @jig.verifies("S-051")
    def test_deterministic_alphabetical_order(self, tmp_path: Path):
        """Returns paths in deterministic alphabetical order."""
        from jig.verification_graph.discovery import discover_test_files

        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        # Create in non-alphabetical order
        (test_dir / "test_zebra.py").write_text("pass")
        (test_dir / "test_alpha.py").write_text("pass")
        (test_dir / "test_middle.py").write_text("pass")

        files = discover_test_files(tmp_path, test_dir=test_dir)

        assert len(files) == 3
        # Should be sorted alphabetically
        assert files[0].name == "test_alpha.py"
        assert files[1].name == "test_middle.py"
        assert files[2].name == "test_zebra.py"

    @jig.verifies("S-051")
    def test_empty_directory_returns_empty_list(self, tmp_path: Path):
        """Returns empty list when no test files found."""
        from jig.verification_graph.discovery import discover_test_files

        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        # No test files, just a conftest
        (test_dir / "conftest.py").write_text("pass")

        files = discover_test_files(tmp_path, test_dir=test_dir)

        assert files == []

    @jig.verifies("S-051")
    def test_nonexistent_test_dir_returns_empty_list(self, tmp_path: Path):
        """Returns empty list when test directory doesn't exist."""
        from jig.verification_graph.discovery import discover_test_files

        # No tests/ directory created
        files = discover_test_files(tmp_path)

        assert files == []


class TestDiscoverTests:
    """Tests for discover_tests function (finds test functions in files)."""

    @jig.verifies("S-051")
    def test_finds_test_functions(self, tmp_path: Path):
        """Finds test functions (def test_*)."""
        from jig.verification_graph.discovery import discover_tests

        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_one():
    pass

def test_two():
    pass

def helper():
    pass
""")

        tests = discover_tests([test_file])

        assert len(tests) == 2
        names = {t.name for t in tests}
        assert "test_one" in names
        assert "test_two" in names
        assert "helper" not in names

    @jig.verifies("S-051")
    def test_finds_test_methods_in_classes(self, tmp_path: Path):
        """Finds test methods in TestClass."""
        from jig.verification_graph.discovery import discover_tests

        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
class TestAuth:
    def test_login(self):
        pass

    def test_logout(self):
        pass

    def helper(self):
        pass

class NotATestClass:
    def test_ignored(self):
        pass
""")

        tests = discover_tests([test_file])

        assert len(tests) == 2
        names = {t.name for t in tests}
        assert "test_login" in names
        assert "test_logout" in names
        # helper not included, and NotATestClass methods not included
        assert "helper" not in names
        assert "test_ignored" not in names

    @jig.verifies("S-051")
    def test_generates_correct_test_ids(self, tmp_path: Path):
        """Generates correct T-{module}.{function} IDs."""
        from jig.verification_graph.discovery import discover_tests

        test_file = tmp_path / "test_auth.py"
        test_file.write_text("""
def test_login():
    pass

class TestSession:
    def test_create(self):
        pass
""")

        tests = discover_tests([test_file], project_root=tmp_path)

        ids = {t.id for t in tests}
        assert "T-test_auth.test_login" in ids
        assert "T-test_auth.TestSession.test_create" in ids

    @jig.verifies("S-051")
    def test_includes_file_path(self, tmp_path: Path):
        """Test info includes file path."""
        from jig.verification_graph.discovery import discover_tests

        test_dir = tmp_path / "tests" / "unit"
        test_dir.mkdir(parents=True)
        test_file = test_dir / "test_auth.py"
        test_file.write_text("def test_one(): pass")

        tests = discover_tests([test_file], project_root=tmp_path)

        assert len(tests) == 1
        assert tests[0].file == Path("tests/unit/test_auth.py")

    @jig.verifies("S-051")
    def test_deterministic_order(self, tmp_path: Path):
        """Returns tests in deterministic order."""
        from jig.verification_graph.discovery import discover_tests

        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_zebra():
    pass

def test_alpha():
    pass
""")

        tests = discover_tests([test_file])

        # Should be sorted by ID
        assert tests[0].name == "test_alpha"
        assert tests[1].name == "test_zebra"
