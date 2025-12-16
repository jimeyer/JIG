"""Integration tests for coverage audit pipeline.

These tests verify S-066 and S-067 end-to-end integration.
"""

import json
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import jig
from click.testing import CliRunner

from jig.cli.audit import coverage_command
from jig.cli.main import cli
from jig.config import JigConfig, PathsConfig


def _make_test_config(tmp_path: Path) -> JigConfig:
    """Create a test JigConfig pointing to a temporary directory."""
    jig_root = tmp_path / "jig"
    jig_root.mkdir(parents=True, exist_ok=True)

    generated = jig_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)

    paths = PathsConfig(
        source=tmp_path / "src",
        tests=tmp_path / "tests",
        jig_root=jig_root,
        specifications=jig_root / "specifications",
        outcomes=jig_root / "outcomes",
        bricks=jig_root / "bricks.yaml",
        generated=generated,
    )

    return JigConfig(
        paths=paths,
        project_root=tmp_path,
        config_file_path=None,
        has_config_file=False,
    )


def _create_mock_impl_graph(path: Path) -> None:
    """Create a minimal implementation graph."""
    with open(path, "w") as f:
        f.write(json.dumps({"_meta": {"version": "1.0"}}) + "\n")
        f.write(
            json.dumps(
                {
                    "type": "function",
                    "id": "F-module.func",
                    "file": "src/module.py",
                    "line": 10,
                    "jig_hash": "func_hash",
                }
            )
            + "\n"
        )


def _create_mock_verify_graph(path: Path) -> None:
    """Create a minimal verification graph."""
    with open(path, "w") as f:
        f.write(json.dumps({"_meta": {"version": "1.0"}}) + "\n")
        f.write(
            json.dumps(
                {
                    "type": "test",
                    "id": "T-test_module.test_func",
                    "file": "tests/test_module.py",
                    "jig_hash": "test_hash",
                }
            )
            + "\n"
        )


@jig.verifies("S-066", "S-067")
def test_coverage_command_missing_impl_graph(tmp_path):
    """coverage_command returns error if implementation graph missing."""
    config = _make_test_config(tmp_path)

    # Don't create impl graph
    # Create verify graph
    _create_mock_verify_graph(config.paths.generated / "verification-graph.ndjson")

    with patch("click.echo") as mock_echo:
        exit_code = coverage_command(config)

    assert exit_code == 1

    # Check error message was displayed
    error_calls = [
        call for call in mock_echo.call_args_list if "Implementation graph" in str(call)
    ]
    assert len(error_calls) > 0


@jig.verifies("S-066", "S-067")
def test_coverage_command_missing_verify_graph(tmp_path):
    """coverage_command returns error if verification graph missing."""
    config = _make_test_config(tmp_path)

    # Create impl graph but not verify graph
    _create_mock_impl_graph(config.paths.generated / "implementation-graph.ndjson")

    with patch("click.echo") as mock_echo:
        exit_code = coverage_command(config)

    assert exit_code == 1

    # Check error message was displayed
    error_calls = [
        call for call in mock_echo.call_args_list if "Verification graph" in str(call)
    ]
    assert len(error_calls) > 0


@jig.verifies("S-066", "S-067")
def test_coverage_command_shows_progress(tmp_path):
    """coverage_command displays progress messages."""
    config = _make_test_config(tmp_path)

    # Create required graphs
    _create_mock_impl_graph(config.paths.generated / "implementation-graph.ndjson")
    _create_mock_verify_graph(config.paths.generated / "verification-graph.ndjson")

    # Create test directory
    config.paths.tests.mkdir(parents=True, exist_ok=True)

    # Mock the subprocess to avoid actually running pytest
    mock_coverage_file = tmp_path / ".coverage"

    with patch("jig.audit.coverage.subprocess.run") as mock_run, patch(
        "click.echo"
    ) as mock_echo:
        # Make subprocess succeed and create a mock .coverage file
        def create_coverage(*args, **kwargs):
            # Create a minimal .coverage SQLite database
            import sqlite3

            conn = sqlite3.connect(mock_coverage_file)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE coverage_schema (version INTEGER)")
            cursor.execute("CREATE TABLE file (id INTEGER PRIMARY KEY, path TEXT)")
            cursor.execute(
                "CREATE TABLE context (id INTEGER PRIMARY KEY, context TEXT)"
            )
            cursor.execute(
                "CREATE TABLE line_bits (file_id INTEGER, context_id INTEGER, numbits BLOB)"
            )
            conn.commit()
            conn.close()
            return MagicMock(returncode=0)

        mock_run.side_effect = create_coverage

        exit_code = coverage_command(config)

    # Check progress messages
    echo_messages = [str(call) for call in mock_echo.call_args_list]
    messages_str = " ".join(echo_messages)

    assert "Running coverage audit" in messages_str
    assert "Running tests with coverage" in messages_str
    assert "Extracting T→F edges" in messages_str
    assert "Writing record file" in messages_str


@jig.verifies("S-066", "S-067")
def test_coverage_command_writes_record_file(tmp_path):
    """coverage_command creates record file in correct location."""
    config = _make_test_config(tmp_path)

    # Create required graphs
    _create_mock_impl_graph(config.paths.generated / "implementation-graph.ndjson")
    _create_mock_verify_graph(config.paths.generated / "verification-graph.ndjson")

    # Create test directory
    config.paths.tests.mkdir(parents=True, exist_ok=True)

    mock_coverage_file = tmp_path / ".coverage"

    with patch("jig.audit.coverage.subprocess.run") as mock_run:
        # Create mock coverage database
        def create_coverage(*args, **kwargs):
            import sqlite3

            conn = sqlite3.connect(mock_coverage_file)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE coverage_schema (version INTEGER)")
            cursor.execute("CREATE TABLE file (id INTEGER PRIMARY KEY, path TEXT)")
            cursor.execute(
                "CREATE TABLE context (id INTEGER PRIMARY KEY, context TEXT)"
            )
            cursor.execute(
                "CREATE TABLE line_bits (file_id INTEGER, context_id INTEGER, numbits BLOB)"
            )
            conn.commit()
            conn.close()
            return MagicMock(returncode=0)

        mock_run.side_effect = create_coverage

        exit_code = coverage_command(config)

    assert exit_code == 0

    # Check record file was created
    records_dir = config.paths.jig_root / "audits" / "records"
    assert records_dir.exists()

    record_files = list(records_dir.glob("coverage-*.ndjson"))
    assert len(record_files) == 1

    # Verify filename format
    today = date.today()
    expected_name = f"coverage-{today.isoformat()}.ndjson"
    assert record_files[0].name == expected_name


@jig.verifies("S-066", "S-067")
def test_coverage_command_cleans_up_coverage_file(tmp_path):
    """coverage_command deletes .coverage after processing."""
    config = _make_test_config(tmp_path)

    # Create required graphs
    _create_mock_impl_graph(config.paths.generated / "implementation-graph.ndjson")
    _create_mock_verify_graph(config.paths.generated / "verification-graph.ndjson")

    # Create test directory
    config.paths.tests.mkdir(parents=True, exist_ok=True)

    mock_coverage_file = tmp_path / ".coverage"

    with patch("jig.audit.coverage.subprocess.run") as mock_run:
        def create_coverage(*args, **kwargs):
            import sqlite3

            conn = sqlite3.connect(mock_coverage_file)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE coverage_schema (version INTEGER)")
            cursor.execute("CREATE TABLE file (id INTEGER PRIMARY KEY, path TEXT)")
            cursor.execute(
                "CREATE TABLE context (id INTEGER PRIMARY KEY, context TEXT)"
            )
            cursor.execute(
                "CREATE TABLE line_bits (file_id INTEGER, context_id INTEGER, numbits BLOB)"
            )
            conn.commit()
            conn.close()
            return MagicMock(returncode=0)

        mock_run.side_effect = create_coverage

        # Verify .coverage exists before cleanup
        coverage_command(config)

    # .coverage should be deleted after processing
    assert not mock_coverage_file.exists()


@jig.verifies("S-066", "S-067")
def test_coverage_command_continues_on_test_failure(tmp_path):
    """coverage_command continues processing even if tests fail."""
    config = _make_test_config(tmp_path)

    # Create required graphs
    _create_mock_impl_graph(config.paths.generated / "implementation-graph.ndjson")
    _create_mock_verify_graph(config.paths.generated / "verification-graph.ndjson")

    # Create test directory
    config.paths.tests.mkdir(parents=True, exist_ok=True)

    mock_coverage_file = tmp_path / ".coverage"

    with patch("jig.audit.coverage.subprocess.run") as mock_run, patch(
        "click.echo"
    ) as mock_echo:
        def create_coverage(*args, **kwargs):
            import sqlite3

            conn = sqlite3.connect(mock_coverage_file)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE coverage_schema (version INTEGER)")
            cursor.execute("CREATE TABLE file (id INTEGER PRIMARY KEY, path TEXT)")
            cursor.execute(
                "CREATE TABLE context (id INTEGER PRIMARY KEY, context TEXT)"
            )
            cursor.execute(
                "CREATE TABLE line_bits (file_id INTEGER, context_id INTEGER, numbits BLOB)"
            )
            conn.commit()
            conn.close()
            # Return non-zero exit code (test failure)
            return MagicMock(returncode=1)

        mock_run.side_effect = create_coverage

        exit_code = coverage_command(config)

    # Should still succeed (exit 0) even though tests failed
    assert exit_code == 0

    # Check that warning about test failures was shown
    echo_messages = [str(call) for call in mock_echo.call_args_list]
    messages_str = " ".join(echo_messages)
    assert "tests failed" in messages_str.lower()

    # Record file should still be created
    records_dir = config.paths.jig_root / "audits" / "records"
    record_files = list(records_dir.glob("coverage-*.ndjson"))
    assert len(record_files) == 1


@jig.verifies("S-066", "S-067")
def test_coverage_command_overwrites_same_day_record(tmp_path):
    """Running coverage_command twice on same day overwrites record."""
    config = _make_test_config(tmp_path)

    # Create required graphs
    _create_mock_impl_graph(config.paths.generated / "implementation-graph.ndjson")
    _create_mock_verify_graph(config.paths.generated / "verification-graph.ndjson")

    # Create test directory
    config.paths.tests.mkdir(parents=True, exist_ok=True)

    mock_coverage_file = tmp_path / ".coverage"

    def create_coverage(*args, **kwargs):
        import sqlite3

        conn = sqlite3.connect(mock_coverage_file)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE coverage_schema (version INTEGER)")
        cursor.execute("CREATE TABLE file (id INTEGER PRIMARY KEY, path TEXT)")
        cursor.execute("CREATE TABLE context (id INTEGER PRIMARY KEY, context TEXT)")
        cursor.execute(
            "CREATE TABLE line_bits (file_id INTEGER, context_id INTEGER, numbits BLOB)"
        )
        conn.commit()
        conn.close()
        return MagicMock(returncode=0)

    # Run twice
    with patch("jig.audit.coverage.subprocess.run", side_effect=create_coverage):
        coverage_command(config)

    with patch("jig.audit.coverage.subprocess.run", side_effect=create_coverage):
        coverage_command(config)

    # Should still only have one file (overwritten)
    records_dir = config.paths.jig_root / "audits" / "records"
    record_files = list(records_dir.glob("coverage-*.ndjson"))
    assert len(record_files) == 1


@jig.verifies("S-066", "S-067")
def test_cli_audit_coverage_accessible():
    """jigy audit coverage command is accessible via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ["audit", "coverage", "--help"])

    assert result.exit_code == 0
    assert "coverage" in result.output.lower()


@jig.verifies("S-067")
def test_record_file_is_grepable(tmp_path):
    """Record file output is grep-able for test and function IDs."""
    config = _make_test_config(tmp_path)

    # Create graphs with multiple entries
    impl_graph = config.paths.generated / "implementation-graph.ndjson"
    with open(impl_graph, "w") as f:
        f.write(json.dumps({"_meta": {"version": "1.0"}}) + "\n")
        f.write(
            json.dumps(
                {
                    "type": "function",
                    "id": "F-module.func_a",
                    "file": "src/module.py",
                    "line": 10,
                    "jig_hash": "hash_a",
                }
            )
            + "\n"
        )
        f.write(
            json.dumps(
                {
                    "type": "function",
                    "id": "F-module.func_b",
                    "file": "src/module.py",
                    "line": 20,
                    "jig_hash": "hash_b",
                }
            )
            + "\n"
        )

    verify_graph = config.paths.generated / "verification-graph.ndjson"
    with open(verify_graph, "w") as f:
        f.write(json.dumps({"_meta": {"version": "1.0"}}) + "\n")
        f.write(
            json.dumps(
                {
                    "type": "test",
                    "id": "T-test_module.test_a",
                    "jig_hash": "test_hash_a",
                }
            )
            + "\n"
        )
        f.write(
            json.dumps(
                {
                    "type": "test",
                    "id": "T-test_module.test_b",
                    "jig_hash": "test_hash_b",
                }
            )
            + "\n"
        )

    config.paths.tests.mkdir(parents=True, exist_ok=True)
    mock_coverage_file = tmp_path / ".coverage"
    src_file = tmp_path / "src" / "module.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text("# placeholder")
    abs_src = str(src_file.resolve())

    with patch("jig.audit.coverage.subprocess.run") as mock_run:
        def create_coverage_with_data(*args, **kwargs):
            import sqlite3

            from coverage.numbits import nums_to_numbits

            conn = sqlite3.connect(mock_coverage_file)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE coverage_schema (version INTEGER)")
            cursor.execute("CREATE TABLE file (id INTEGER PRIMARY KEY, path TEXT)")
            cursor.execute(
                "CREATE TABLE context (id INTEGER PRIMARY KEY, context TEXT)"
            )
            cursor.execute(
                "CREATE TABLE line_bits (file_id INTEGER, context_id INTEGER, numbits BLOB)"
            )

            # Add file
            cursor.execute("INSERT INTO file VALUES (1, ?)", (abs_src,))

            # Add contexts
            cursor.execute(
                "INSERT INTO context VALUES (1, 'tests/test_module.py::test_a|run')"
            )
            cursor.execute(
                "INSERT INTO context VALUES (2, 'tests/test_module.py::test_b|run')"
            )

            # Add coverage data
            # test_a covers func_a (lines 10-15)
            cursor.execute(
                "INSERT INTO line_bits VALUES (1, 1, ?)",
                (nums_to_numbits([10, 11, 12]),),
            )
            # test_b covers both functions
            cursor.execute(
                "INSERT INTO line_bits VALUES (1, 2, ?)",
                (nums_to_numbits([10, 11, 20, 21]),),
            )

            conn.commit()
            conn.close()
            return MagicMock(returncode=0)

        mock_run.side_effect = create_coverage_with_data

        coverage_command(config)

    # Read record file
    records_dir = config.paths.jig_root / "audits" / "records"
    record_files = list(records_dir.glob("coverage-*.ndjson"))
    assert len(record_files) == 1

    content = record_files[0].read_text()

    # Test grep-ability
    # Grep for specific test should find relevant lines
    test_a_lines = [line for line in content.splitlines() if "T-test_module.test_a" in line]
    assert len(test_a_lines) >= 1

    # Grep for specific function should find relevant lines
    func_b_lines = [line for line in content.splitlines() if "F-module.func_b" in line]
    assert len(func_b_lines) >= 1
