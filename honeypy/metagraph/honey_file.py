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

from honeypy.metagraph.meta.honey_node import HoneyNode
from honeypy.metagraph.nd_file import NDHoneyFile

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

    @overload
    def pullback(
        self: "HoneyFile[P]",
        other: NDHoneyFile[Unpack[Ts]],
        map_1: Callable[[P], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyFile[P, Unpack[Ts]]: ...

    @overload
    def pullback(
        self: "HoneyFile[P]",
        other: NDHoneyFile[Unpack[Ts]],
        map_1: Callable[[P, Tuple[Unpack[Ts]]], bool],
    ) -> NDHoneyFile[P, Unpack[Ts]]: ...

    @overload
    def pullback(
        self: "HoneyFile[P]",
        other: "HoneyFile[P2]",
        map_1: Callable[[P], K],
        map_2: Callable[[P2], K],
    ) -> NDHoneyFile[P, P2]: ...

    @overload
    def pullback(
        self: "HoneyFile[P]",
        other: "HoneyFile[P2]",
        map_1: Callable[[P, P2], bool],
    ) -> NDHoneyFile[P, P2]: ...

    def pullback(
        self, other: "HoneyNode", map_1: Callable, map_2: Optional[Callable] = None
    ) -> "HoneyNode":
        """Perform a pullback (inner join) between this file and ``other``.

        Supported call forms
        --------------------
        1) Key-mapper form (recommended / efficient)
           - Signature: pullback(other, map_1, map_2)
           - map_1: Callable[[P], K]
           - map_2: Callable[[P2], K]  (or Callable[[Tuple[Unpack[Ts]]], K] for ND)
           - Behaviour: computes keys for each side and performs a hash-based
             join (O(N + M) expected). Prefer this for large inputs when you
             can extract a comparable, hashable key.

            Example:
                def map_a(row_a: RowA) -> int:
                    return row_a.value
                def map_b(row_b: RowB) -> int:
                    return row_b.value
                joined = file_a.pullback(file_b, map_a, map_b)
                for a, b in joined:
                    # `a` has type RowA, `b` has type RowB
                    ...

        2) Predicate form (easy / potentially expensive)
           - Signature: pullback(other, predicate)
           - predicate: Callable[[P, P2], bool]  (or Callable[[P, Tuple[Unpack[Ts]]],
             bool])
           - Behaviour: evaluates predicate(a, b) for candidate pairs and yields
             pairs where it returns True. This implements a general join but may
             be O(N * M) and should be used for small collections or when no
             obvious key exists.

            Example:
                from datetime import timedelta
                def near_time(a: RowA, b: RowB) -> bool:
                    return abs(a.timestamp - b.timestamp) < timedelta(minutes=1)
                joined = file_a.pullback(file_b, near_time)
                for a, b in joined:
                    ...

        Runtime behaviour
        -----------------
        - Files are loaded on demand if not already loaded.
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

    def __iter__(self: "HoneyFile[P]") -> Iterator[P]:
        """Call super().__iter__."""
        return super().__iter__()
