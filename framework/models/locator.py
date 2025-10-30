from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Union


@dataclass(frozen=True)
class Locator:
    """Strongly typed locator object shared across page objects."""

    by: str
    value: str

    def as_tuple(self) -> Tuple[str, str]:
        return self.by, self.value


LocatorTuple = Tuple[str, str]
LocatorLike = Union[Locator, LocatorTuple]


def to_locator_tuple(locator: LocatorLike) -> LocatorTuple:
    """Normalize any locator-like input to a tuple the Selenium APIs understand."""
    if isinstance(locator, Locator):
        return locator.as_tuple()
    return locator

