"""
Pullback transform (ND join).

Perform an inner join (pullback) between two Honey nodes. Supports both:
- key-mapper form: pullback(a, b, map_a, map_b) — efficient hash-join when keys are
  hashable.
- predicate form: pullback(a, b, predicate) — flexible pairwise predicate (may be
  O(N*M)).

This transform is N-dimensional: joining a 1-D node with an M-D node yields tuples
whose shape reflects the participant dimensionalities. The runtime returns a
lightweight in-memory HoneyNode whose children are the matched tuples.

Usage
-----
- map-based: joined = Pullback()(file_a, file_b, key_a, key_b)
- predicate:  joined = Pullback()(file_a, file_b, lambda x, y: cond(x, y))

Notes
-----
- Map-based form is preferred for large inputs; predicate form is convenient for
  nearest-time or fuzzy matches but can be expensive.
- User-provided mappers/predicates are called inside the transform; errors are
  caught and offending items skipped.
"""

from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
    overload,
)
from uuid import UUID

from honeypy.metagraph.honey_collection import HoneyCollection
from honeypy.metagraph.honey_file import HoneyFile
from honeypy.metagraph.meta.honey_node import HoneyNode
from honeypy.metagraph.nd_collection import NDHoneyCollection
from honeypy.metagraph.nd_file import NDHoneyFile
from honeypy.transform.meta.honey_transform import HoneyTransform

K = TypeVar("K")
P1 = TypeVar("P1", covariant=True)
P2 = TypeVar("P2", covariant=True)
F1 = TypeVar("F1", bound=HoneyFile, covariant=True)
F2 = TypeVar("F2", bound=HoneyFile, covariant=True)
Ts = TypeVarTuple("Ts")


M1 = TypeVar("M1", bound=Mapping[str, Any])
M2 = TypeVar("M2", bound=Mapping[str, Any])
Mt = TypeVarTuple("Mt")


class Pullback(HoneyTransform):
    """Pullback transform: compute an inner join between two Honey nodes.

    Supported call forms
    - map-based: Pullback()(a, b, map_a, map_b)
      Compute keys with map_a/map_b and perform a hash-join (preferred; O(N+M)).
    - predicate-based: Pullback()(a, b, predicate)
      Evaluate predicate(a, b) pairwise and yield matches (flexible; O(N*M)).

    N-dimensional semantics
    - Joining nodes of different arities yields tuples whose shape reflects
      the participants (e.g. joining a 1-D node with an M-D node yields
      (a_item, *other_items)). Overloads on __call__ preserve precise static
      types for common cases.

    Runtime behaviour
    - Loads inputs on demand, dispatches to projection or predicate join paths,
      and returns a lightweight in-memory HoneyNode whose children are the
      matched tuples. Mapping/predicate exceptions are caught and logged; bad
      items are skipped.

    Examples
    --------
    >>> joined = Pullback()(file_a, file_b, lambda x: x.id, lambda y: y.id)
    >>> joined = Pullback()(file_a, file_b, lambda x, y: abs(x.ts - y.ts) < delta)
    """

    # NOTE type ignores are here because bounds on TypeVarTuple are not yet in Python
    # Why did I bind the tuple-based metadata to `Mapping[str, Any]` instead of just
    # using `Tuple`? Because I noticed typecheckers don't resolve the type variable
    # for metadata otherwise, even if they reolve the correct generics on the node
    @overload
    def __call__(
        self,
        node_1: HoneyFile[M1, P1],
        node_2: HoneyFile[M2, P2],
        map_1: Callable[[P1], K],
        map_2: Callable[[P2], K],
    ) -> NDHoneyFile[Tuple[M1, M2], P1, P2]: ...

    @overload
    def __call__(
        self,
        node_1: HoneyFile[M1, P1],
        node_2: NDHoneyFile[Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[P1], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyFile[Tuple[M1, Unpack[Mt]], P1, Unpack[Ts]]: ...  # type: ignore

    @overload
    def __call__(
        self,
        node_1: NDHoneyFile[Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: HoneyFile[M2, P2],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[P2], K],
    ) -> NDHoneyFile[Tuple[Unpack[Mt], M2], Unpack[Ts], P2]: ...  # type: ignore

    # Wait for multiple variadic argument unpacking for an extra signature

    @overload
    def __call__(
        self,
        node_1: HoneyFile[M1, P1],
        node_2: HoneyFile[M2, P2],
        map_1: Callable[[P1, P2], K],
    ) -> NDHoneyFile[Tuple[M1, M2], P1, P2]: ...

    @overload
    def __call__(
        self,
        node_1: HoneyFile[M1, P1],
        node_2: NDHoneyFile[Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[P1, Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyFile[Tuple[M1, Unpack[Mt]], P1, Unpack[Ts]]: ...  # type: ignore

    @overload
    def __call__(
        self,
        node_1: NDHoneyFile[Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: HoneyFile[M2, P2],
        map_1: Callable[[Tuple[Unpack[Ts], P2]], K],
    ) -> NDHoneyFile[Tuple[Unpack[Mt], M2], Unpack[Ts], P2]: ...  # type: ignore

    # Wait for multiple variadic argument unpacking for an extra signature

    @overload
    def __call__(
        self,
        node_1: HoneyCollection[M1, F1],
        node_2: HoneyCollection[M2, F2],
        map_1: Callable[[F1], K],
        map_2: Callable[[F2], K],
    ) -> NDHoneyCollection[Tuple[M1, M2], F1, F2]: ...

    @overload
    def __call__(
        self,
        node_1: HoneyCollection[M1, F1],
        node_2: NDHoneyFile[Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[F1], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyCollection[Tuple[M1, Unpack[Mt]], F1, Unpack[Ts]]: ...  # type: ignore

    @overload
    def __call__(
        self,
        node_1: NDHoneyCollection[Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: HoneyCollection[M2, F2],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[F2], K],
    ) -> NDHoneyCollection[Tuple[Unpack[Mt], M2], Unpack[Ts], F2]: ...  # type: ignore

    # Wait for multiple variadic argument unpacking for an extra signature

    @overload
    def __call__(
        self,
        node_1: HoneyCollection[M1, F1],
        node_2: HoneyCollection[M2, F2],
        map_1: Callable[[F1, F2], K],
    ) -> NDHoneyCollection[Tuple[M1, M2], F1, F2]: ...

    @overload
    def __call__(
        self,
        node_1: HoneyCollection[M1, F1],
        node_2: NDHoneyFile[Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[F1, Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyCollection[  # type: ignore
        Tuple[M1, Tuple[Unpack[Mt]]],  # type: ignore
        F1,
        Unpack[Ts],
    ]: ...  # type: ignore

    @overload
    def __call__(
        self,
        node_1: NDHoneyCollection[Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: HoneyCollection[M2, F2],
        map_1: Callable[[Tuple[Unpack[Ts], F2]], K],
    ) -> NDHoneyCollection[  # type: ignore
        Tuple[Unpack[Mt], M2],  # type: ignore
        Unpack[Ts],
        F2,
    ]: ...

    # Wait for multiple variadic argument unpacking for an extra signature

    def __call__(
        self,
        node_1: HoneyNode,
        node_2: HoneyNode,
        map_1: Callable,
        map_2: Optional[Callable] = None,
    ) -> HoneyNode[Any]:
        """Compute the pullback (inner join) between this node and ``other``.

        Both nodes are loaded if necessary. ``map_1`` is applied to each child of
        ``self`` and ``map_2`` is applied to each child of ``other``; any pair of
        children whose mapped keys compare equal are paired and included in the
        result.

        This method supports N-dimensional inputs. When joining an N-dimensional
        node the joined children are tuples whose arity reflects the
        dimensionality of the participants (for example joining a 1-D file with
        an M-D file yields tuples of shape ``(self_item, *other_items)``). Callers
        may express the other side with a ``TypeVarTuple`` (PEP 646) in overloads
        to preserve precise static types.

        Parameters
        ----------
        other
            Node to join with. May be any HoneyNode-like object (1-D or ND).
        map_1 : Callable
            Function applied to children of this node to compute join keys.
        map_2 : Callable
            Function applied to children of ``other`` to compute join keys.

        Returns
        -------
        HoneyNode
            A loaded in-memory node whose children are tuples representing
            matched items from the two inputs. Tuple shape depends on the
            dimensionality of the operands.

        Notes
        -----
        - Mapping errors are caught and logged; offending children are skipped.
        - This is an inner join: only matched pairs are returned.
        - Static typing is provided by overloads; the runtime result is a
          lightweight in-memory node populated with the joined tuples.
        """
        if not node_1._loaded:
            node_1.load()

        if not node_2._loaded:
            node_2.load()

        if map_2 is None:
            return self._pullback_predicate(node_1, node_2, map_1)

        return self._pullback_projection(node_1, node_2, map_1, map_2)

    def _pullback_predicate(
        self,
        node_1: HoneyNode,
        node_2: HoneyNode,
        predicate: Callable[[Any, Any], bool],
    ) -> HoneyNode:
        """Perform a pullback by using a predicate over points from two domains."""
        joined: List[tuple[Any, Any]] = []

        for self_child in node_1:
            for other_child in node_2:
                if predicate(self_child, other_child):
                    if node_1.arity == 1 and node_2.arity == 1:
                        joined.append((self_child, other_child))
                    elif node_1.arity != 1 and node_2.arity == 1:
                        joined.append((*self_child, other_child))
                    elif node_2.arity == 1 and node_2.arity != 1:
                        joined.append((self_child, *other_child))
                    else:
                        joined.append((*self_child, *other_child))

        class _JoinNode(HoneyNode[Any]):
            # TODO: refactor to not require the join node. Need to do a lot of work here
            ARITY = node_2.arity + node_1.arity

            def __init__(self, children, metadata=None):
                super().__init__(
                    node_1._principal_parent, load=False, metadata=metadata or {}
                )
                self._children = children
                self._loaded = True

            def _load(
                self, raw_children_metadata: Optional[Dict[UUID, Any]] = None
            ) -> Iterable[Any]:
                return self._children

            def _unload(self) -> None:
                self._children = []

            # TODO: Think about how to combine metadata
            # Likely add as generic on HoneyNode. Makes it easier to union for instance
            @staticmethod
            def _parse_metadata(raw_metadata: Any) -> Any:
                return {}

            @staticmethod
            def _serialise_metadata(metadata: Any) -> Any:
                return {}

            @staticmethod
            def _locator(parent_location: Path, metadata: Optional[Any] = None) -> Path:
                return Path(".")

            def _save(self, location: Path, metadata: Any) -> None:
                pass

        return _JoinNode(joined, metadata=(node_1.metadata, node_2.metadata))

    def _pullback_projection(
        self, node_1: HoneyNode, node_2: HoneyNode, map_1: Callable, map_2: Callable
    ) -> "HoneyNode":
        """Perform a pullback by using two functions with a common codomain."""
        index: dict[Any, list[Any]] = {}
        for child in node_2:
            try:
                key = map_2(child)
            except Exception as e:
                print(f"Problem mapping other child {child!r}: {e!r}")
                continue
            index.setdefault(key, []).append(child)

        joined: List[tuple[Any, Any]] = []
        for child in node_1:
            try:
                key = map_1(child)
            except Exception as e:
                print(f"Problem mapping self child {child!r}: {e!r}")
                continue
            for match in index.get(key, []):
                if node_1.arity == 1 and node_2.arity == 1:
                    joined.append((child, match))
                elif node_1.arity != 1 and node_2.arity == 1:
                    joined.append((*child, match))
                elif node_2.arity == 1 and node_2.arity != 1:
                    joined.append((child, *match))
                else:
                    joined.append((*child, *match))

        class _JoinNode(HoneyNode[Any]):
            ARITY = node_2.arity + node_1.arity

            # TODO: refactor to not require the join node. Need to do a lot of work here
            def __init__(self, children, metadata=None):
                super().__init__(
                    node_1._principal_parent, load=False, metadata=metadata or {}
                )
                self._children = children
                self._loaded = True

            def _load(
                self, raw_children_metadata: Optional[Dict[UUID, Any]] = None
            ) -> Iterable[Any]:
                return self._children

            def _unload(self) -> None:
                self._children = []

            # TODO: Think about how to combine metadata
            # Likely add as generic on HoneyNode. Makes it easier to union for instance
            @staticmethod
            def _parse_metadata(raw_metadata: Any) -> Any:
                return {}

            @staticmethod
            def _serialise_metadata(metadata: Any) -> Any:
                return {}

            @staticmethod
            def _locator(parent_location: Path, metadata: Optional[Any] = None) -> Path:
                return Path(".")

            def _save(self, location: Path, metadata: Any) -> None:
                pass

        return _JoinNode(joined, metadata=(node_1.metadata, node_2.metadata))
