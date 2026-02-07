"""Project node types for the metagraph.

This module defines HoneyProject, a thin node wrapper representing a complete research
project, for instance encompassing the folders, files and associated transformations
for a single research paper.
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
    overload,
)

if TYPE_CHECKING:
    from honeypy.metagraph.nd_project import NDHoneyProject

from honeypy.metagraph.honey_collection import HoneyCollection
from honeypy.metagraph.meta.honey_node import HoneyNode

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

    @overload
    def pullback(
        self: "HoneyProject[C]",
        other: NDHoneyProject[Unpack[Ts]],
        map_1: Callable[[C], Any],
        map_2: Callable[[Tuple[Unpack[Ts]]], Any],
    ) -> NDHoneyProject[C, Unpack[Ts]]: ...

    @overload
    def pullback(
        self: "HoneyProject[C]",
        other: "HoneyProject[C2]",
        map_1: Callable[[C], Any],
        map_2: Callable[[C2], Any],
    ) -> NDHoneyProject[C, C2]: ...

    def pullback(
        self, other: object, map_1: Callable[..., Any], map_2: Callable[..., Any]
    ) -> Any:
        """Perform a pullback (inner join) between this project and ``other``.

        Both projects are loaded when needed. ``map_1`` is applied to each
        child of this project and ``map_2`` to each child (or tuple) of ``other``;
        items whose mapped keys compare equal are paired. The joined children
        are tuples whose arity reflects the dimensionality of the operands.

        Static overloads in the package express precise ND shapes; at runtime
        a lightweight in-memory node containing the joined tuples is returned.
        """
        result = super().pullback(other, map_1, map_2)
        return result

    def __iter__(self: "HoneyProject[C]") -> Iterator[C]:
        """Call super().__iter__."""
        return super().__iter__()
