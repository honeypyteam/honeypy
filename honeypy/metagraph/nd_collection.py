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

from typing import (
    Any,
    Generic,
    Iterable,
    Iterator,
    LiteralString,
    Mapping,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
)

from honeypy.metagraph.meta.honey_node import HoneyNode

Ts = TypeVarTuple("Ts")
M = TypeVar("M", bound=Tuple[Mapping[str, Any], ...])
L = TypeVar("L", bound=Tuple[LiteralString, ...])


class NDHoneyCollection(Generic[L, M, Unpack[Ts]], HoneyNode[L, M]):
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

    def __iter__(
        self: "NDHoneyCollection[L, M, Unpack[Ts]]",
    ) -> Iterator[Tuple[Unpack[Ts]]]:
        """Call super().__iter__."""
        return super().__iter__()
