"""Test fixture for short import form."""

from jig import implements


@implements("S-001")
def function_with_short_import():
    """Function using short import form."""
    pass


@implements("S-002")
class ClassWithShortImport:
    """Class using short import form."""

    @implements("S-003")
    def method_with_short_import(self):
        """Method using short import form."""
        pass
