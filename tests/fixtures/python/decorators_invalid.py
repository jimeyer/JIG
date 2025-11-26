"""Test fixture for invalid decorator formats."""

import jig


@jig.implements("BAD-FORMAT")
def invalid_spec_id():
    """Function with invalid spec ID format."""
    pass


@jig.implements("spec-001")
def lowercase_prefix():
    """Function with lowercase prefix (invalid)."""
    pass


@jig.implements("S-ABC")
def non_numeric_id():
    """Function with non-numeric ID (invalid)."""
    pass


@jig.implements("S-001", "INVALID", "S-002")
def mixed_valid_invalid():
    """Function with mix of valid and invalid spec IDs."""
    pass


@jig.implements("S-001")
def valid_spec():
    """Function with valid spec ID."""
    pass
