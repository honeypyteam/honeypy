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
    Optional,
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

K = TypeVar("K")
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
        map_1: Callable[[C], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyProject[C, Unpack[Ts]]: ...

    @overload
    def pullback(
        self: "HoneyProject[C]",
        other: "HoneyProject[C2]",
        map_1: Callable[[C], K],
        map_2: Callable[[C2], K],
    ) -> NDHoneyProject[C, C2]: ...

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
           - map_1: Callable[[C], K]
           - map_2: Callable[[C2], K]
           - Behaviour: computes keys for each side and performs a hash-based
             join (O(N + M) expected). Prefer this for large inputs when you
             can extract a comparable, hashable key.

            Example:
                def map_a(collection_a: CollectionA) -> int:
                    return collection_a.owner
                def map_b(collection_b: CollectionB) -> int:
                    return collection_b.owner
                joined = project_a.pullback(project_b, map_a, map_b)
                for a, b in joined:
                    # `a` has type CollectionA, `b`
                    # has type CollectionB
                    ...

        2) Predicate form (easy / potentially expensive)
            - Signature: pullback(other, predicate)
            - predicate: Callable[[C, C2], bool]
            - Behaviour: evaluates predicate(a, b) for candidate pairs and yields
                pairs where it returns True. This implements a general join but may
                be O(N * M) and should be used for small collections or when no
                obvious key exists.

            Example:
                from datetime import timedelta
                def near_time(a: CollectionA, b: CollectionB) -> bool:
                    return abs(
                        a.created_time - b.created_time
                    ) < timedelta(minutes=1)
                joined = project_a.pullback(project_b, near_time)
                for a, b in joined:
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
        result = super().pullback(other, map_1, map_2)
        return result

    def __iter__(self: "HoneyProject[C]") -> Iterator[C]:
        """Call super().__iter__."""
        return super().__iter__()
