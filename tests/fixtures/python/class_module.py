"""Module with classes and methods."""


class Calculator:
    """A simple calculator."""

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b

    def _internal_method(self):
        """Internal method."""
        pass


class Logger:
    """A simple logger."""

    def log(self, message):
        """Log a message."""
        print(message)

    def error(self, message):
        """Log an error."""
        print(f"ERROR: {message}")
