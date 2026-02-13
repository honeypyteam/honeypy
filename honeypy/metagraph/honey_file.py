"""File node types for the metagraph.

This module defines HoneyFile, a thin node wrapper representing a filesystem-backed
file or collection of files that yields HoneyPoint[P] items when iterated.

Design & typing
--------------
- HoneyFile[P] is parameterised by the point payload type P (a HoneyPoint subtype).
- For N-ary/variadic joins we use TypeVarTuple (PEP 646) in overloads; overloads provide
  precise static shapes while the runtime implementation returns a lightweight
  in-memory node (or a concrete HoneyFile when a caller supplies a factory).

Behaviour
---------
- Loading/unloading, metadata and child management are provided by
  :class:`honeypy.metagraph.meta.honey_node.HoneyNode`.
- Use collection/file unions at call sites (Union[HoneyFile[A], HoneyFile[B]])
  when you need heterogeneous collections; prefer factory helpers to avoid casts.
"""

from typing import (
    Generic,
    Iterable,
    Iterator,
    TypeVar,
    TypeVarTuple,
)

from honeypy.metagraph.meta.honey_node import HoneyNode

K = TypeVar("K")
P = TypeVar("P", covariant=True)
P2 = TypeVar("P2", covariant=True)
Ts = TypeVarTuple("Ts")


class HoneyFile(HoneyNode, Generic[P]):
    """Represents a single file node containing HoneyPoint[P] items.

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
    honeypy.metagraph.honey_point.HoneyPoint
        Lightweight wrapper type used for the points contained in the file.
    """

    @property
    def children(self) -> Iterable[P]:
        """Iterable[P]: Live iterable view of the node's children."""
        return super().children

    def __iter__(self: "HoneyFile[P]") -> Iterator[P]:
        """Call super().__iter__."""
        return super().__iter__()
