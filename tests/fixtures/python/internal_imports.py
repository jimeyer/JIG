"""Module with internal imports (relative to project)."""
# These would be internal if analyzed from the fixtures directory
from .simple_module import hello_world, add_numbers
from .class_module import Calculator


def use_imports():
    """Use imported functions."""
    msg = hello_world()
    result = add_numbers(1, 2)
    calc = Calculator()
    return msg, result, calc
