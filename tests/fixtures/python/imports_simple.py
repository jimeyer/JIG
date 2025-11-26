"""Module demonstrating various import styles."""
import os
import sys
from pathlib import Path
from typing import List, Optional

import json
import networkx as nx
from collections import defaultdict, Counter


def process_path(p: Path) -> str:
    """Process a path."""
    return str(p)


def load_data(filename: str) -> dict:
    """Load JSON data."""
    with open(filename) as f:
        return json.load(f)
