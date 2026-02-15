"""Transformation primitives for the metagraph.

Defines the minimal abstract base used by concrete transform implementations.
"""

from abc import ABC, abstractmethod


class HoneyTransform(ABC):
    """Abstract callable transform.

    Subclasses implement __call__ to perform a transformation over Honey nodes.
    """

    @abstractmethod
    def __call__(self, *args, **kwds):
        """Execute the transform. Must be implemented by subclasses."""
        raise NotImplementedError
