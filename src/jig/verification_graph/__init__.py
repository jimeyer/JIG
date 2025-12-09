"""Verification graph generation for JIG.

This module provides test discovery and analysis for building the
verification graph, which tracks T→S edges (tests verifying specifications).
"""

from .analyzer import TestAnalyzer
from .builder import build_verification_graph
from .discovery import TestInfo, discover_test_files, discover_tests

__all__ = [
    "build_verification_graph",
    "discover_test_files",
    "discover_tests",
    "TestAnalyzer",
    "TestInfo",
]
