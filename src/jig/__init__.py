"""JIG (Jig Intent Graph) - Git-native constraint-driven development tool."""

from typing import Callable, TypeVar, Union

__version__ = "0.2.0"

# Type variable for decorated functions/classes
F = TypeVar("F", bound=Callable)
C = TypeVar("C", bound=type)


def implements(*spec_ids: str) -> Callable[[Union[F, C]], Union[F, C]]:
    """Decorator to mark functions/classes as implementing specifications.

    Usage:
        @jig.implements("S-001")
        def my_function():
            pass

        @jig.implements("S-001", "S-002")
        class MyClass:
            pass

    Args:
        *spec_ids: One or more specification IDs (e.g., "S-001", "O-001")

    Returns:
        Decorator function that adds implementation metadata
    """
    def decorator(obj: Union[F, C]) -> Union[F, C]:
        # Store spec IDs as metadata on the function/class
        if not hasattr(obj, "__jig_implements__"):
            obj.__jig_implements__ = []
        obj.__jig_implements__.extend(spec_ids)
        return obj
    return decorator


def verifies(*spec_ids: str) -> Callable[[F], F]:
    """Decorator to mark test functions as verifying specifications.

    Usage:
        @jig.verifies("S-001")
        def test_my_feature():
            pass

        @jig.verifies("S-001", "S-002")
        def test_comprehensive():
            pass

    Args:
        *spec_ids: One or more specification IDs (e.g., "S-001", "O-001")

    Returns:
        Decorator function that adds verification metadata
    """
    def decorator(func: F) -> F:
        # Store spec IDs as metadata on the test function
        if not hasattr(func, "__jig_verifies__"):
            func.__jig_verifies__ = []
        func.__jig_verifies__.extend(spec_ids)
        return func
    return decorator


__all__ = ["__version__", "implements", "verifies"]
