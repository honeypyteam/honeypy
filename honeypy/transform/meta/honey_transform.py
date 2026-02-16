"""Transformation primitives for the metagraph.

Defines the minimal abstract base used by concrete transform implementations.
"""

from abc import ABC, abstractmethod
from typing import Any


class HoneyTransform(ABC):
    """Abstract callable transform.

    Subclasses implement __call__ to perform a transformation over Honey nodes.
    The method is intentionally untyped here; concrete transforms provide
    precise overloads and runtime implementations.
    """

    @abstractmethod
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Execute the transform. Must be implemented by subclasses."""
        raise NotImplementedError
