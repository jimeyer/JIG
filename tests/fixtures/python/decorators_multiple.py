"""Test fixture for multiple @jig.implements decorators."""

import jig


@jig.implements("S-001", "S-002", "S-003")
def multi_spec_function():
    """Function implementing multiple specs."""
    pass


@jig.implements("O-001", "S-010")
class MultiSpecClass:
    """Class implementing outcome and spec."""

    @jig.implements("S-011", "S-012")
    def multi_spec_method(self):
        """Method implementing multiple specs."""
        pass
