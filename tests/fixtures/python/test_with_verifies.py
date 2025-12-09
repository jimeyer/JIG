"""Test fixture with @jig.verifies decorators for analyzer testing."""

import jig


@jig.verifies("S-001")
def test_simple():
    """Test with single spec."""
    assert True


@jig.verifies("S-001", "S-002")
def test_multiple_specs():
    """Test verifying multiple specs."""
    assert True


class TestWithClass:
    """Test class with decorated methods."""

    @jig.verifies("S-003")
    def test_method(self):
        """Test method with verifies decorator."""
        assert True

    @jig.verifies("S-004", "S-005")
    def test_method_multiple(self):
        """Test method verifying multiple specs."""
        assert True


def test_no_decorator():
    """Test without @jig.verifies - should have empty verifies array."""
    assert True


# Short form import test (simulated)
from jig import verifies


@verifies("S-006")
def test_short_form():
    """Test using short form @verifies decorator."""
    assert True


@jig.verifies("INVALID-001")
def test_invalid_spec_id():
    """Test with invalid spec ID format - should warn but not fail."""
    assert True


@jig.verifies("S-007")
def test_with_logic():
    """Test with actual logic for hash testing."""
    x = 1 + 2
    y = x * 3
    assert y == 9
