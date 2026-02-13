"""Project node types for the metagraph.

This module defines HoneyProject, a thin node wrapper representing a complete research
project, for instance encompassing the folders, files and associated transformations
for a single research paper.
"""

from typing import (
    Any,
    Generic,
    Iterable,
    Iterator,
    TypeVar,
    TypeVarTuple,
)

from honeypy.metagraph.honey_collection import HoneyCollection
from honeypy.metagraph.meta.honey_node import HoneyNode

K = TypeVar("K")
C = TypeVar("C", bound=HoneyCollection["Any"], covariant=True)
C2 = TypeVar("C2", bound=HoneyCollection["Any"], covariant=True)
Ts = TypeVarTuple("Ts")


class HoneyProject(HoneyNode, Generic[C]):
    """Represents a single project node containing HoneyCollection items.

    Parameters
    ----------
    *args, **kwargs
        Arguments are forwarded to :class:`HoneyNode`. Concrete subclasses
        typically accept a pathlib.Path ``location`` or similar and pass
        ``load=True`` to auto-load children.

    See Also
    --------
    honeypy.metagraph.meta.honey_node.HoneyNode
        Base class that defines the load/unload/metadata contract.
    """

    @property
    def children(self) -> Iterable[C]:
        """Iterable[P]: Live iterable view of the node's children."""
        return super().children

    def __iter__(self: "HoneyProject[C]") -> Iterator[C]:
        """Call super().__iter__."""
        return super().__iter__()
