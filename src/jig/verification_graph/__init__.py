"""Verification graph generation for JIG.

This module provides test discovery and analysis for building the
verification graph, which tracks T→S edges (tests verifying specifications).
"""

from .discovery import TestInfo, discover_test_files, discover_tests

__all__ = [
    "discover_test_files",
    "discover_tests",
    "TestInfo",
]
