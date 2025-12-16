"""Coverage collection for T→F edge discovery.

Runs pytest with coverage instrumentation to determine which tests
execute which functions.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

import jig
from jig.config import JigConfig


@jig.implements("S-066")
def run_coverage_collection(
    config: JigConfig,
    coverage_file: Optional[Path] = None,
) -> tuple[int, Path]:
    """Run pytest with coverage instrumentation.

    Executes the test suite with line-level coverage tracking and
    per-test context recording. Coverage data is written to a SQLite
    database that can be queried for T→F relationships.

    Args:
        config: JIG configuration with project paths.
        coverage_file: Optional path for .coverage file. Defaults to
                      project_root/.coverage.

    Returns:
        Tuple of (pytest_exit_code, coverage_file_path).
        Exit code 0 means all tests passed; non-zero means some failed
        but coverage was still collected.
    """
    project_root = config.project_root
    source_dir = config.paths.source

    # Default coverage file location
    if coverage_file is None:
        coverage_file = project_root / ".coverage"

    # Ensure audits/records directory exists
    audits_dir = config.paths.jig_root / "audits" / "records"
    audits_dir.mkdir(parents=True, exist_ok=True)

    # Build pytest command with coverage flags
    # --cov: Track coverage for source directory
    # --cov-context=test: Record which test caused each line to execute
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        f"--cov={source_dir}",
        "--cov-context=test",
        f"--cov-report=",  # Suppress report output, we just want .coverage
        str(config.paths.tests),
    ]

    # Set COVERAGE_FILE env var to control output location
    env = {"COVERAGE_FILE": str(coverage_file)}

    # Run pytest with coverage
    result = subprocess.run(
        cmd,
        cwd=project_root,
        env={**subprocess.os.environ, **env},
        capture_output=False,  # Let output go to terminal
    )

    return result.returncode, coverage_file


@jig.implements("S-066")
def ensure_audits_directory(config: JigConfig) -> Path:
    """Ensure jig/audits/records/ directory exists.

    Args:
        config: JIG configuration with project paths.

    Returns:
        Path to the audits/records directory.
    """
    audits_dir = config.paths.jig_root / "audits" / "records"
    audits_dir.mkdir(parents=True, exist_ok=True)
    return audits_dir
