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
    Optional,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
    overload,
)

from honeypy.metagraph.honey_collection import HoneyCollection
from honeypy.metagraph.meta.honey_node import HoneyNode

if TYPE_CHECKING:
    from honeypy.metagraph.honey_project import HoneyProject

K = TypeVar("K")
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

    @overload
    def pullback(
        self: "NDHoneyProject[Unpack[Ts]]",
        other: HoneyProject[C],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[C], K],
    ) -> "NDHoneyProject[Unpack[Ts], C]": ...

    @overload
    def pullback(
        self: "NDHoneyProject[Unpack[Ts]]",
        other: HoneyProject[C],
        map_1: Callable[[Tuple[Unpack[Ts]], C], bool],
    ) -> "NDHoneyProject[Unpack[Ts], C]": ...

    def pullback(
        self,
        other: "HoneyNode",
        map_1: Callable,
        map_2: Optional[Callable] = None,
    ) -> "HoneyNode":
        """Perform a pullback (inner join) between this project and ``other``.

        Supported call forms
        --------------------
        1) Key-mapper form (recommended / efficient)
           - Signature: pullback(other, map_1, map_2)
           - map_1: Callable[[Tuple[Unpack[Ts]]], K]
           - map_2: Callable[[C], K]
           - Behaviour: computes keys for each side and performs a hash-based
             join (O(N + M) expected). Prefer this for large inputs when you
             can extract a comparable, hashable key.

            Example:
                def map_a(collection_a: Tuple[CollectionAA, CollectionAB]) -> int:
                    return collection_a.owner
                def map_b(collection_b: CollectionB) -> int:
                    return collection_b.owner
                joined = project_a.pullback(project_b, map_a, map_b)
                for (a_1, a_2), b in joined:
                    # `(a_1, a_2)` has type Tuple[CollectionAA, CollectionAB), `b`
                    # has type CollectionB
                    ...

        2) Predicate form (easy / potentially expensive)
            - Signature: pullback(other, predicate)
            - predicate: Callable[[Tuple[Unpack[Ts]], C], bool]
            - Behaviour: evaluates predicate(a, b) for candidate pairs and yields
                pairs where it returns True. This implements a general join but may
                be O(N * M) and should be used for small collections or when no
                obvious key exists.

            Example:
                from datetime import timedelta
                def near_time(a: Tuple[
                    CollectionAA,
                    CollectionAB,
                    ],
                    b: CollectionB,
                ) -> bool:
                    return abs(
                        a[0].created_time - b.created_time
                    ) < timedelta(minutes=1)
                joined = project_a.pullback(project_b, near_time)
                for (a_1, a_2), b in joined:
                    ...

        Runtime behaviour
        -----------------
        - Projects are loaded on demand if not already loaded.
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

    def __iter__(self: "NDHoneyProject[Unpack[Ts]]") -> Iterator[Tuple[Unpack[Ts]]]:
        """Call super().__iter__."""
        return super().__iter__()
