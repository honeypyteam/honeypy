"""N-dimensional collection support for the metagraph.

This module defines :class:`NDHoneyCollection`, a generalized collection type
that can represent collections whose children are tuples of heterogeneous
elements (for example a collection of pair-files or higher-arity bundles).

TypeVarTuple (PEP 646) is used to express the variable arity of child tuples
via ``Ts = TypeVarTuple('Ts')`` and the class is parameterized as
``NDHoneyCollection[Unpack[Ts]]``. The ``children`` property yields
``Iterable[Tuple[Unpack[Ts]]]``.

ND collections integrate with the node pullback APIs: joining a 1-D collection
with an M-D collection yields child tuples whose shape reflects the
participating dimensionalities (for example ``(a, *b)`` for a 1-D vs M-D join).

The runtime behaviour is intentionally lightweight: concrete collection
implementations should override the loading hooks and may provide convenient
constructors or factories for ND file types. Static typing helpers and overloads
are provided elsewhere in the package to help type-checkers reason about
ND shapes.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Iterable,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
)

from honeypy.metagraph.honey_file import HoneyFile
from honeypy.metagraph.meta.honey_node import HoneyNode

if TYPE_CHECKING:
    from honeypy.metagraph.honey_collection import HoneyCollection

F = TypeVar("F", bound=HoneyFile[Any])
Ts = TypeVarTuple("Ts")


class NDHoneyCollection(HoneyNode, Generic[Unpack[Ts]]):
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
    def children(self) -> Iterable[Tuple[Unpack[Ts]]]:
        """Iterable[Tuple[Unpack[Ts]]]: Live iterable view of the node's children."""
        return super().children

    # TODO: overload? Can't have multiple variadic types
    # but could reasonably overload, say, 2 or 3 times. Also in nd_file and co.
    # unsure if overloading will give us much, though
    def pullback(
        self: "NDHoneyCollection[Unpack[Ts]]",
        other: HoneyCollection[F],
        map_1: Callable[[Tuple[Unpack[Ts]]], Any],
        map_2: Callable[[F], Any],
    ) -> "NDHoneyCollection[Unpack[Ts], F]":
        """Perform a pullback (inner join) between this collection and ``other``.

        Both collections are loaded when needed. ``map_1`` is applied to each tuple
        child of this collection and ``map_2`` to each child (or tuple) of ``other``;
        items whose mapped keys compare equal are paired. The joined children
        are tuples whose arity reflects the dimensionality of the operands.

        Static overloads in the package express precise ND shapes; at runtime
        a lightweight in-memory node containing the joined tuples is returned.
        """
        return super().pullback(other, map_1, map_2)
