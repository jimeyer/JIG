"""Module with nested class definitions."""


class Outer:
    """Outer class."""

    def outer_method(self):
        """Method on outer class."""
        pass

    class Inner:
        """Inner nested class."""

        def inner_method(self):
            """Method on inner class."""
            pass

        class DeepNested:
            """Deeply nested class."""

            def deep_method(self):
                """Method on deeply nested class."""
                pass


class Container:
    """Another container class."""

    class Item:
        """Nested item class."""

        def get_value(self):
            """Get item value."""
            return 42
