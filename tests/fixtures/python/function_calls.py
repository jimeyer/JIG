"""Module demonstrating function calls."""
import json
from pathlib import Path


def helper_function():
    """A helper function."""
    return "helper"


def another_helper(x):
    """Another helper."""
    return x * 2


def main_function():
    """Main function that calls others."""
    # Direct function call
    result = helper_function()

    # Function call with argument
    value = another_helper(5)

    # Module function call
    data = json.dumps({"key": "value"})

    # Chained call (should skip for V1)
    path = Path(".").resolve()

    return result


def recursive_function(n):
    """Recursive function."""
    if n <= 0:
        return 1
    return n * recursive_function(n - 1)


class Calculator:
    """Calculator class."""

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def compute(self, x, y):
        """Compute using add method."""
        # Method call - skip for V1 (requires type inference)
        result = self.add(x, y)

        # Direct function call from method
        helper = helper_function()

        return result
