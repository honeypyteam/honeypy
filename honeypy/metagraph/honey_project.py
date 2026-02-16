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
    Mapping,
    TypeVar,
)

from honeypy.metagraph.honey_collection import HoneyCollection
from honeypy.metagraph.meta.honey_node import HoneyNode

C = TypeVar("C", bound=HoneyCollection, covariant=True)
M = TypeVar("M", bound=Mapping[str, Any])


class HoneyProject(Generic[M, C], HoneyNode[M]):
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

    def __iter__(self: "HoneyProject[M, C]") -> Iterator[C]:
        """Call super().__iter__."""
        return super().__iter__()
