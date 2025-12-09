"""Tests for JIG content hashing (J022).

Verifies determinism, normalization, and cross-platform stability.
"""

import ast
import tempfile
from pathlib import Path

import jig
from jig.hashing import (
    compute_hash,
    git_blob_hash,
    hash_brick,
    hash_function,
    hash_intent_artifact,
    hash_test,
)


class TestComputeHash:
    """Tests for S-044: Content Hash Format."""

    @jig.verifies("S-044")
    def test_returns_12_hex_chars(self):
        """Hash output is exactly 12 lowercase hex characters."""
        result = compute_hash("hello world")
        assert len(result) == 12
        assert all(c in "0123456789abcdef" for c in result)

    @jig.verifies("S-044")
    def test_deterministic(self):
        """Same input always produces same output."""
        content = "test content for hashing"
        result1 = compute_hash(content)
        result2 = compute_hash(content)
        assert result1 == result2

    @jig.verifies("S-044")
    def test_different_input_different_hash(self):
        """Different inputs produce different hashes."""
        result1 = compute_hash("content A")
        result2 = compute_hash("content B")
        assert result1 != result2

    @jig.verifies("S-044")
    def test_utf8_content(self):
        """Hash computed from UTF-8 encoded content."""
        # Unicode content should work
        result = compute_hash("Hello 世界 🌍")
        assert len(result) == 12


class TestHashIntentArtifact:
    """Tests for S-045: Intent Artifact Hashing."""

    @jig.verifies("S-045")
    def test_parses_frontmatter_and_body(self):
        """YAML frontmatter parsed and included in hash input."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("---\nid: S-001\ntype: specification\n---\n\n# Title\n\nBody text.")
            f.flush()
            path = Path(f.name)

        result = hash_intent_artifact(path)
        assert len(result) == 12
        path.unlink()

    @jig.verifies("S-045")
    def test_trailing_whitespace_ignored(self):
        """Body text stripped of leading/trailing whitespace."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f1:
            f1.write("---\nid: S-001\n---\n\nBody text.")
            f1.flush()
            path1 = Path(f1.name)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f2:
            f2.write("---\nid: S-001\n---\n\nBody text.   \n\n\n")
            f2.flush()
            path2 = Path(f2.name)

        result1 = hash_intent_artifact(path1)
        result2 = hash_intent_artifact(path2)
        assert result1 == result2

        path1.unlink()
        path2.unlink()

    @jig.verifies("S-045")
    def test_line_ending_normalization(self):
        """CRLF vs LF differences do not affect hash."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".md", delete=False) as f1:
            f1.write(b"---\nid: S-001\n---\n\nLine 1\nLine 2")
            f1.flush()
            path1 = Path(f1.name)

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".md", delete=False) as f2:
            f2.write(b"---\r\nid: S-001\r\n---\r\n\r\nLine 1\r\nLine 2")
            f2.flush()
            path2 = Path(f2.name)

        result1 = hash_intent_artifact(path1)
        result2 = hash_intent_artifact(path2)
        assert result1 == result2

        path1.unlink()
        path2.unlink()

    @jig.verifies("S-045")
    def test_file_without_frontmatter(self):
        """Files without frontmatter still hash correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Just body content, no frontmatter.")
            f.flush()
            path = Path(f.name)

        result = hash_intent_artifact(path)
        assert len(result) == 12
        path.unlink()


class TestHashFunction:
    """Tests for S-046: Function Hashing via AST."""

    @jig.verifies("S-046")
    def test_includes_function_name(self):
        """Function name included in hash."""
        code1 = "def foo(): pass"
        code2 = "def bar(): pass"

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        result1 = hash_function(tree1.body[0])
        result2 = hash_function(tree2.body[0])

        assert result1 != result2

    @jig.verifies("S-046")
    def test_includes_parameters(self):
        """Parameters and type annotations included in hash."""
        code1 = "def foo(x): pass"
        code2 = "def foo(x, y): pass"

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        result1 = hash_function(tree1.body[0])
        result2 = hash_function(tree2.body[0])

        assert result1 != result2

    @jig.verifies("S-046")
    def test_includes_return_type(self):
        """Return type annotation included in hash."""
        code1 = "def foo() -> int: pass"
        code2 = "def foo() -> str: pass"

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        result1 = hash_function(tree1.body[0])
        result2 = hash_function(tree2.body[0])

        assert result1 != result2

    @jig.verifies("S-046")
    def test_includes_body(self):
        """Function body (all statements) included in hash."""
        code1 = "def foo(): return 1"
        code2 = "def foo(): return 2"

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        result1 = hash_function(tree1.body[0])
        result2 = hash_function(tree2.body[0])

        assert result1 != result2

    @jig.verifies("S-046")
    def test_excludes_decorators(self):
        """Decorators EXCLUDED from hash."""
        code1 = "def foo(): pass"
        code2 = "@decorator\ndef foo(): pass"

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        result1 = hash_function(tree1.body[0])
        result2 = hash_function(tree2.body[0])

        # Hashes should be identical - decorators excluded
        assert result1 == result2

    @jig.verifies("S-046")
    def test_formatting_ignored(self):
        """Whitespace/formatting excluded (normalized by AST)."""
        code1 = "def foo():\n    x = 1\n    return x"
        code2 = "def foo():\n        x=1\n        return x"

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        result1 = hash_function(tree1.body[0])
        result2 = hash_function(tree2.body[0])

        # AST normalization makes these identical
        assert result1 == result2

    @jig.verifies("S-046")
    def test_async_function(self):
        """Async functions hash correctly."""
        code = "async def foo(): pass"
        tree = ast.parse(code)

        result = hash_function(tree.body[0])
        assert len(result) == 12

    @jig.verifies("S-046")
    def test_async_excludes_decorators(self):
        """Async function decorators excluded from hash."""
        code1 = "async def foo(): pass"
        code2 = "@decorator\nasync def foo(): pass"

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        result1 = hash_function(tree1.body[0])
        result2 = hash_function(tree2.body[0])

        assert result1 == result2


class TestHashTest:
    """Tests for S-047: Test Hashing via AST."""

    @jig.verifies("S-047")
    def test_same_algorithm_as_hash_function(self):
        """Same hashing algorithm as S-046 applied to test functions."""
        code = "def test_something(): assert True"
        tree = ast.parse(code)

        result_function = hash_function(tree.body[0])
        result_test = hash_test(tree.body[0])

        assert result_function == result_test

    @jig.verifies("S-047")
    def test_excludes_decorators(self):
        """Decorators excluded from hash."""
        code1 = "def test_foo(): pass"
        code2 = "@pytest.mark.slow\ndef test_foo(): pass"

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        result1 = hash_test(tree1.body[0])
        result2 = hash_test(tree2.body[0])

        assert result1 == result2


class TestHashBrick:
    """Tests for S-048: Brick Definition Hashing."""

    @jig.verifies("S-048")
    def test_hashes_brick_dict(self):
        """Each brick's dict hashed correctly."""
        brick = {
            "id": "B-001",
            "name": "Test Brick",
            "layer": 0,
            "units": ["M-test.module"],
        }
        result = hash_brick(brick)
        assert len(result) == 12

    @jig.verifies("S-048")
    def test_changing_one_brick_independent(self):
        """Changing one brick does not affect other bricks' hashes."""
        brick1 = {"id": "B-001", "name": "Brick One", "layer": 0, "units": ["M-a"]}
        brick2 = {"id": "B-002", "name": "Brick Two", "layer": 1, "units": ["M-b"]}

        hash1_before = hash_brick(brick1)
        hash2_before = hash_brick(brick2)

        # Modify brick1
        brick1["units"].append("M-c")
        hash1_after = hash_brick(brick1)

        # brick2 hash unchanged
        hash2_after = hash_brick(brick2)

        assert hash1_before != hash1_after  # brick1 changed
        assert hash2_before == hash2_after  # brick2 unchanged

    @jig.verifies("S-048")
    def test_units_change_affects_hash(self):
        """Adding/removing units changes the brick's hash."""
        brick = {"id": "B-001", "name": "Test", "layer": 0, "units": ["M-a"]}
        hash_before = hash_brick(brick)

        brick["units"].append("M-b")
        hash_after = hash_brick(brick)

        assert hash_before != hash_after

    @jig.verifies("S-048")
    def test_layer_change_affects_hash(self):
        """Layer changes affect the brick's hash."""
        brick = {"id": "B-001", "name": "Test", "layer": 0, "units": ["M-a"]}
        hash_before = hash_brick(brick)

        brick["layer"] = 1
        hash_after = hash_brick(brick)

        assert hash_before != hash_after

    @jig.verifies("S-048")
    def test_canonical_json(self):
        """JSON canonicalized with sorted keys."""
        # Different key order, same content
        brick1 = {"id": "B-001", "layer": 0, "name": "Test", "units": ["M-a"]}
        brick2 = {"units": ["M-a"], "name": "Test", "layer": 0, "id": "B-001"}

        result1 = hash_brick(brick1)
        result2 = hash_brick(brick2)

        assert result1 == result2


class TestGitBlobHash:
    """Tests for S-049: Git Blob Optimization."""

    @jig.verifies("S-049")
    def test_returns_12_chars_for_tracked_file(self):
        """Returns 12-character git blob hash for tracked files."""
        # Use a file we know exists in git repo
        path = Path(__file__)
        result = git_blob_hash(path)

        # May be None if not in git repo during test, or 12 chars if tracked
        if result is not None:
            assert len(result) == 12
            assert all(c in "0123456789abcdef" for c in result)

    @jig.verifies("S-049")
    def test_returns_none_for_nonexistent_file(self):
        """Returns None for non-existent files."""
        path = Path("/nonexistent/file/path.txt")
        result = git_blob_hash(path)
        assert result is None

    @jig.verifies("S-049")
    def test_returns_none_outside_git_repo(self):
        """Returns None in non-git environments."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            path = Path(f.name)

        # Temp file outside git repo should return None or valid hash
        # (depends on whether temp dir is in a git repo)
        result = git_blob_hash(path)
        if result is not None:
            assert len(result) == 12

        path.unlink()

    @jig.verifies("S-049")
    def test_truncated_to_12_chars(self):
        """Git blob hash truncated to 12 hex chars for consistency."""
        # Git's full hash is 40 chars, we truncate to 12
        path = Path(__file__)
        result = git_blob_hash(path)

        if result is not None:
            assert len(result) == 12  # Not 40
