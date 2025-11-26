"""Module with type hints and annotations."""
from typing import List, Optional, Dict


def typed_function(name: str, age: int) -> str:
    """Function with type hints."""
    return f"{name} is {age} years old"


def optional_return(value: int) -> Optional[str]:
    """Function returning optional value."""
    if value > 0:
        return str(value)
    return None


def complex_types(items: List[str], metadata: Dict[str, int]) -> bool:
    """Function with complex type hints."""
    return len(items) > 0


class TypedClass:
    """Class with typed methods."""

    def process(self, data: str) -> int:
        """Process data and return length."""
        return len(data)

    def batch_process(self, items: List[str]) -> List[int]:
        """Process multiple items."""
        return [len(item) for item in items]
