"""Tiny self-contained calc module — executor stress-test artifact (PLA-011)."""


def add(a: float, b: float) -> float:
    """Return the sum of a and b."""
    return a + b


def divide(a: float, b: float) -> float:
    """Return a / b; raise ValueError on division by zero."""
    if b == 0:
        raise ValueError("division by zero")
    return a / b
