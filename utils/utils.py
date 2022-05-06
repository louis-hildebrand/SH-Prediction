from collections.abc import Sequence
from typing import TypeVar


T = TypeVar("T")


def unique(x: Sequence[T]) -> T:
    if len(x) == 1:
        return x[0]
    elif len(x) == 0:
        raise ValueError("No results found.")
    else:
        raise ValueError("Multiple results found.")
