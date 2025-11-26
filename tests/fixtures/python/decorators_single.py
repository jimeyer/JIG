"""Test fixture for single @jig.implements decorator."""

import jig


@jig.implements("S-001")
def simple_function():
    """Function with single spec."""
    pass


@jig.implements("S-002")
class SimpleClass:
    """Class with single spec."""

    def method(self):
        """Method without decorator."""
        pass


class Container:
    """Class without decorator."""

    @jig.implements("S-003")
    def decorated_method(self):
        """Method with decorator."""
        pass
