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
    Iterator,
    Optional,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
    overload,
)

from honeypy.metagraph.honey_file import HoneyFile
from honeypy.metagraph.meta.honey_node import HoneyNode

if TYPE_CHECKING:
    from honeypy.metagraph.honey_collection import HoneyCollection

K = TypeVar("K")
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
    @overload
    def pullback(
        self: "NDHoneyCollection[Unpack[Ts]]",
        other: HoneyCollection[F],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[F], K],
    ) -> "NDHoneyCollection[Unpack[Ts], F]": ...

    @overload
    def pullback(
        self: "NDHoneyCollection[Unpack[Ts]]",
        other: HoneyCollection[F],
        map_1: Callable[[Tuple[Unpack[Ts]], F], bool],
    ) -> "NDHoneyCollection[Unpack[Ts], F]": ...

    def pullback(
        self, other: "HoneyNode", map_1: Callable, map_2: Optional[Callable] = None
    ) -> "HoneyNode":
        """Perform a pullback (inner join) between this collection and ``other``.

        Supported call forms
        --------------------
        1) Key-mapper form (recommended / efficient)
           - Signature: pullback(other, map_1, map_2)
           - map_1: Callable[[Tuple[Unpack[Ts]]], K]
           - map_2: Callable[[F], K]
           - Behaviour: computes keys for each side and performs a hash-based
             join (O(N + M) expected). Prefer this for large inputs when you
             can extract a comparable, hashable key.

            Example:
                def map_a(file_a: Tuple[FileAA, FileAB]) -> str:
                    return file_a.stem
                def map_b(file_b: FileB) -> str:
                    return file_b.stem
                joined = collection_a.pullback(collection_b, map_a, map_b)
                for (a_1, a_2), b in joined:
                    # `(a_1, a_2)` has type Tuple[FileAA, FileAB), `b` has type FileB
                    ...

        2) Predicate form (easy / potentially expensive)
           - Signature: pullback(other, predicate)
           - predicate: Callable[[Tuple[Unpack[Ts]], F], bool]
           - Behaviour: evaluates predicate(a, b) for candidate pairs and yields
             pairs where it returns True. This implements a general join but may
             be O(N * M) and should be used for small collections or when no
             obvious key exists.

            Example:
                from datetime import timedelta
                def near_time(a: Tuple[FileAA, FileAB], b: FileB) -> bool:
                    return abs(
                        a[0].created_time - b.created_time
                    ) < timedelta(minutes=1)
                joined = collection_a.pullback(collection_b, near_time)
                for (a_1, a_2), b in joined:
                    ...

        Runtime behaviour
        -----------------
        - Collections are loaded on demand if not already loaded.
        - The method returns a lightweight ND node containing the joined tuples;
          static overloads in the module provide precise typing for callers.
        - If you need predicate semantics but want better performance, provide
          an auxiliary key-extractor (outside this API) to allow a hash-join.

        Notes
        -----
        - Document the expected complexity for each form; callers should prefer
          the key-mapper form for scale.
        - Implementations should catch and surface exceptions raised by user
          mappers/predicates with useful diagnostics.
        """
        return super().pullback(other, map_1, map_2)

    def __iter__(self: "NDHoneyCollection[Unpack[Ts]]") -> Iterator[Tuple[Unpack[Ts]]]:
        """Call super().__iter__."""
        return super().__iter__()
