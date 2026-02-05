"""N-dimensional file node helpers.

This module defines :class:`NDHoneyFile`, a typing-friendly abstraction for
files whose children are tuples of heterogeneous values (for example a file
whose rows are pairs, triples, etc.). ``TypeVarTuple`` is used to express the
variable arity of children via ``Ts = TypeVarTuple('Ts')`` and the class is
parameterized as ``NDHoneyFile[Unpack[Ts]]``.

Runtime behaviour is provided by :class:`honeypy.metagraph.meta.honey_node.HoneyNode`.
This module focuses on typing helpers and a small ND-aware convenience API.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
)

from honeypy.metagraph.meta.honey_node import HoneyNode

if TYPE_CHECKING:
    from honeypy.metagraph.honey_collection import HoneyFile

P = TypeVar("P")
Ts = TypeVarTuple("Ts")


class NDHoneyFile(HoneyNode, Generic[Unpack[Ts]]):
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
    def children(self) -> Iterable[Tuple[Unpack[Ts]]]:
        """Iterable[Tuple[Unpack[Ts]]]: Live iterable view of the node's children."""
        return super().children

    def pullback(
        self: "NDHoneyFile[Unpack[Ts]]",
        other: HoneyFile[P],
        map_1: Callable[[Tuple[Unpack[Ts]]], Any],
        map_2: Callable[[P], Any],
    ) -> "NDHoneyFile[Unpack[Ts], P]":
        """Perform a pullback (inner join) between this ND file and ``other``.

        Both files are loaded when needed. ``map_1`` is applied to each tuple
        child of this file and ``map_2`` to each child (or tuple) of ``other``;
        items whose mapped keys compare equal are paired. The joined children
        are tuples whose arity reflects the dimensionality of the operands.

        Static overloads in the package express precise ND shapes; at runtime
        a lightweight in-memory node containing the joined tuples is returned.
        """
        return super().pullback(other, map_1, map_2)

    def __iter__(self: "NDHoneyFile[Unpack[Ts]]") -> Iterator[Tuple[Unpack[Ts]]]:
        """Call super().__iter__."""
        return super().__iter__()
