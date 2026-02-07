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
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
    overload,
)

from honeypy.metagraph.meta.honey_node import HoneyNode
from honeypy.metagraph.nd_file import NDHoneyFile

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

    @overload
    def pullback(
        self: "HoneyFile[P]",
        other: NDHoneyFile[Unpack[Ts]],
        map_1: Callable[[P], Any],
        map_2: Callable[[Tuple[Unpack[Ts]]], Any],
    ) -> NDHoneyFile[P, Unpack[Ts]]: ...

    @overload
    def pullback(
        self: "HoneyFile[P]",
        other: "HoneyFile[P2]",
        map_1: Callable[[P], Any],
        map_2: Callable[[P2], Any],
    ) -> NDHoneyFile[P, P2]: ...

    def pullback(
        self, other: object, map_1: Callable[..., Any], map_2: Callable[..., Any]
    ) -> Any:
        """Perform a pullback (inner join) between this file and ``other``.

        Both files are loaded when needed. ``map_1`` is applied to each
        child of this file and ``map_2`` to each child (or tuple) of ``other``;
        items whose mapped keys compare equal are paired. The joined children
        are tuples whose arity reflects the dimensionality of the operands.

        Static overloads in the package express precise ND shapes; at runtime
        a lightweight in-memory node containing the joined tuples is returned.
        """
        result = super().pullback(other, map_1, map_2)
        return result

    def __iter__(self: "HoneyFile[P]") -> Iterator[P]:
        """Call super().__iter__."""
        return super().__iter__()
