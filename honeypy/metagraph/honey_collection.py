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
from honeypy.metagraph.nd_collection import NDHoneyCollection

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

    @overload
    def pullback(
        self: "HoneyCollection[F]",
        other: "HoneyCollection[F2]",
        map_1: Callable[[F], K],
        map_2: Callable[[F2], K],
    ) -> "NDHoneyCollection[F, F2]": ...

    @overload
    def pullback(
        self: "HoneyCollection[F]",
        other: "HoneyCollection[F2]",
        map_1: Callable[[F, F2], bool],
    ) -> "NDHoneyCollection[F, F2]": ...

    @overload
    def pullback(
        self: "HoneyCollection[F]",
        other: "NDHoneyCollection[Unpack[Ts]]",
        map_1: Callable[[F], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> "NDHoneyCollection[F, Unpack[Ts]]": ...

    @overload
    def pullback(
        self: "HoneyCollection[F]",
        other: "NDHoneyCollection[Unpack[Ts]]",
        map_1: Callable[[F, Tuple[Unpack[Ts]]], bool],
    ) -> "NDHoneyCollection[F, Unpack[Ts]]": ...

    def pullback(
        self, other: "HoneyNode", map_1: Callable, map_2: Optional[Callable] = None
    ) -> "HoneyNode":
        """Perform a pullback (inner join) between this collection and ``other``.

        Supported call forms
        --------------------
        1) Key-mapper form (recommended / efficient)
           - Signature: pullback(other, map_1, map_2)
           - map_1: Callable[[F], K]
           - map_2: Callable[[F2], K]
           - Behaviour: computes keys for each side and performs a hash-based
             join (O(N + M) expected). Prefer this for large inputs when you
             can extract a comparable, hashable key.

            Example:
                def map_a(file_a: FileA) -> str:
                    return file_a.stem
                def map_b(file_b: FileB) -> str:
                    return file_b.stem
                joined = collection_a.pullback(collection_b, map_a, map_b)
                for a, b in joined:
                    # `a` has type FileA, `b` has type FileB
                    ...

        2) Predicate form (easy / potentially expensive)
           - Signature: pullback(other, predicate)
           - predicate: Callable[[F, F2], bool]
           - Behaviour: evaluates predicate(a, b) for candidate pairs and yields
             pairs where it returns True. This implements a general join but may
             be O(N * M) and should be used for small collections or when no
             obvious key exists.

            Example:
                from datetime import timedelta
                def near_time(a: FileA, b: FileB) -> bool:
                    return abs(a.created_time - b.created_time) < timedelta(minutes=1)
                joined = collection_a.pullback(collection_b, near_time)
                for a, b in joined:
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

    def __iter__(self: "HoneyCollection[F]") -> Iterator[F]:
        """Call super().__iter__."""
        return super().__iter__()
