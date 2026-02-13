"""Collection node for honey files.

This module provides HoneyCollection, a container node that represents a
collection of HoneyFile[T] instances stored under a filesystem location. The
collection is parameterized by the point type T exposed by its files.

The collection class is designed to be flexible, and its existence is a semantic
courtesy (it suffices, in fact, that it is a subtype of `HoneyCollection`)
Practically a collection can be represented as a single folder, or a collection of
folders with files findable by helpers in the class as well as the `location` property

The collection is responsible for locating/instantiating HoneyFile children and
can be loaded lazily (via the `load` mechanism on HoneyNode).
"""

from typing import (
    Any,
    Generic,
    Iterable,
    Iterator,
    TypeVar,
    TypeVarTuple,
)

from honeypy.metagraph.honey_file import HoneyFile
from honeypy.metagraph.meta.honey_node import HoneyNode

K = TypeVar("K")
F = TypeVar("F", bound=HoneyFile[Any], covariant=True)
F2 = TypeVar("F2", bound=HoneyFile[Any], covariant=True)
Ts = TypeVarTuple("Ts")


class HoneyCollection(HoneyNode, Generic[F]):
    """A collection of HoneyFile nodes.

    Parameters
    ----------
    location : pathlib.Path
        Filesystem path to the collection root (directory containing files).
    load : bool, optional
        If True, the collection will be loaded during initialization. Defaults
        to False.

    Attributes
    ----------
    _location : pathlib.Path
        The filesystem location backing this collection.
    """

    @property
    def children(self) -> Iterable[F]:
        """Iterable[F]: Live iterable view of the node's children."""
        return super().children

    def __iter__(self: "HoneyCollection[F]") -> Iterator[F]:
        """Call super().__iter__."""
        return super().__iter__()
