"""N-dimensional project node helpers.

This module defines :class:`NDHoneyProject`, a typing-friendly abstraction for
projects whose children are tuples of heterogeneous collections (for example a project
whose children are subfolders etc.) ``TypeVarTuple`` is used to express the
variable arity of children via ``Ts = TypeVarTuple('Ts')`` and the class is
parameterized as ``NDHoneyProject[Unpack[Ts]]``.

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

from honeypy.metagraph.honey_collection import HoneyCollection
from honeypy.metagraph.meta.honey_node import HoneyNode

if TYPE_CHECKING:
    from honeypy.metagraph.honey_project import HoneyProject

C = TypeVar("C", bound=HoneyCollection[Any])
Ts = TypeVarTuple("Ts")


class NDHoneyProject(HoneyNode, Generic[Unpack[Ts]]):
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
    def children(self) -> Iterable[Tuple[Unpack[Ts]]]:
        """Iterable[Tuple[Unpack[Ts]]]: Live iterable view of the node's children."""
        return super().children

    def pullback(
        self: "NDHoneyProject[Unpack[Ts]]",
        other: HoneyProject[C],
        map_1: Callable[[Tuple[Unpack[Ts]]], Any],
        map_2: Callable[[C], Any],
    ) -> "NDHoneyProject[Unpack[Ts], C]":
        """Perform a pullback (inner join) between this ND project and ``other``.

        Both projects are loaded when needed. ``map_1`` is applied to each tuple
        child of this project and ``map_2`` to each child (or tuple) of ``other``;
        items whose mapped keys compare equal are paired. The joined children
        are tuples whose arity reflects the dimensionality of the operands.

        Static overloads in the package express precise ND shapes; at runtime
        a lightweight in-memory node containing the joined tuples is returned.
        """
        return super().pullback(other, map_1, map_2)

    def __iter__(self: "NDHoneyProject[Unpack[Ts]]") -> Iterator[Tuple[Unpack[Ts]]]:
        """Call super().__iter__."""
        return super().__iter__()
