"""Entry point for running the Python analyzer from the command line.

Usage:
    python -m jig.impl_graph.analyzers.python <file.py>
"""

from .python import main

if __name__ == "__main__":
    main()
