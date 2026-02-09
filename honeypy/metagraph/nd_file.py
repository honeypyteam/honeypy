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

if TYPE_CHECKING:
    from honeypy.metagraph.honey_collection import HoneyFile

K = TypeVar("K")
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

    @overload
    def pullback(
        self: "NDHoneyFile[Unpack[Ts]]",
        other: HoneyFile[P],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[P], K],
    ) -> "NDHoneyFile[Unpack[Ts], P]": ...

    @overload
    def pullback(
        self: "NDHoneyFile[Unpack[Ts]]",
        other: HoneyFile[P],
        map_1: Callable[[Tuple[Unpack[Ts]], P], bool],
    ) -> "NDHoneyFile[Unpack[Ts], P]": ...

    def pullback(
        self, other: "HoneyNode", map_1: Callable, map_2: Optional[Callable] = None
    ) -> "HoneyNode":
        """Perform a pullback (inner join) between this file and ``other``.

        Supported call forms
        --------------------
        1) Key-mapper form (recommended / efficient)
           - Signature: pullback(other, map_1, map_2)
           - map_1: Callable[[Tuple[Unpack[Ts]]], K]
           - map_2: Callable[[P], K]
           - Behaviour: computes keys for each side and performs a hash-based
             join (O(N + M) expected). Prefer this for large inputs when you
             can extract a comparable, hashable key.

            Example:
                def map_a(row_a: Tuple[RowAA, RowAB]) -> int:
                    return row_a[0].value
                def map_b(row_b: RowB) -> int:
                    return row_b.value
                joined = file_a.pullback(file_b, map_a, map_b)
                for (a_1, a_2), b in joined:
                    # `(a_1, a_2)` has type Tuple[RowAA, RowAB), `b` has type RowB
                    ...

        2) Predicate form (easy / potentially expensive)
           - Signature: pullback(other, predicate)
           - predicate: Callable[[Tuple[Unpack[Ts]], P], bool]
           - Behaviour: evaluates predicate(a, b) for candidate pairs and yields
             pairs where it returns True. This implements a general join but may
             be O(N * M) and should be used for small collections or when no
             obvious key exists.

            Example:
                from datetime import timedelta
                def near_time(a: Tuple[RowAA, RowAB], b: RowB) -> bool:
                    return abs(a[0].timestamp - b.timestamp) < timedelta(minutes=1)
                joined = file_a.pullback(file_b, near_time)
                for (a_1, a_2), b in joined:
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

    def __iter__(self: NDHoneyFile[Unpack[Ts]]) -> Iterator[Tuple[Unpack[Ts]]]:
        """Call super().__iter__."""
        return super().__iter__()
