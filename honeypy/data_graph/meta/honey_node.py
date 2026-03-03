"""Core data graph node abstraction.

This module provides the base abstract node used across the data graph model.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from itertools import islice
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    LiteralString,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
)
from uuid import UUID, uuid4

from honeypy.transform.meta.ir import (
    IRExecutor,
    IRNode,
    IRPredicatePullback,
    IRPullback,
    IRSelect,
    IRTransform,
    PrimitiveFunc,
)
from honeypy.transform.meta.utils import (
    as_tuple,
    get_single_argument_predicate,
    is_tuple,
)

if TYPE_CHECKING:
    from honeypy.data_graph.meta.node_type import NodeType
    from honeypy.services.context import HoneyContext
    from honeypy.services.datagraph.data_graph import DataGraph
    from honeypy.services.datagraph.node_factory import NodeFactory

T_HoneyNode = TypeVar("T_HoneyNode", bound="HoneyNode[Any, Any, Any]")
P_co = TypeVar("P_co", covariant=True)
L = TypeVar("L", bound=LiteralString | Tuple[LiteralString, ...])
M = TypeVar("M", bound=Mapping[str, Any] | Tuple[Mapping[str, Any], ...])


class HoneyNode(ABC, Generic[L, M, P_co]):
    """Abstract base node for the data graph."""

    # Kept in metadata and used in parent-child dynamic construction
    CLASS_UUID: ClassVar[UUID]
    NODE_TYPE: ClassVar[NodeType]
    ARITY: int = 1
    _uuid: UUID
    _ir: IRNode
    _kind: Literal["source"] | Literal["derived"]

    _context: HoneyContext
    _principal_parent: UUID | None

    def __init__(
        self,
        uuid: Optional[UUID] = None,
        *,
        context: HoneyContext,
        metadata: M,
        principal_parent: Optional[UUID] = None,
    ) -> None:
        """Create a new HoneyNode."""
        self._uuid = uuid or uuid4()
        self._metadata = metadata
        self._principal_parent = principal_parent
        self._context = context

        self._ir = IRSelect(self._uuid, self.arity)
        self._kind = "source"

    @property
    def arity(self) -> int:
        """
        int: Returns the dimensionality of the data.

        Often this represents the number of modalities. The data inside the node is
        represented as a tuple of length ``self.arity``
        """
        return self.ARITY

    @property
    def metadata(self) -> M:
        """Mapping[str, Any]: Read-only view of the node's metadata mapping."""
        return self._metadata

    @property
    def principal_parent(self) -> "HoneyNode":
        """Get the principal parent of this node."""
        if self._uuid in self._data_graph:
            node = self._data_graph[self._uuid]
            return self._node_factory.create_node(node.principal_parent)

        if self._principal_parent is not None:
            return self._node_factory.create_node(self._principal_parent)

        raise KeyError(f"no principal parent exists for node {self.uuid!s}")

    @property
    def location(self) -> Path:
        """
        Path: A path chosen to represent the data's location.

        The location is calculated through the ``self._locator`` and uses the
        node's metadata and parent's location (if it exists)
        """
        return self._locator(self.principal_parent.location, self._metadata)

    @property
    def uuid(self) -> UUID:
        """Get the uuid for this node."""
        return self._uuid

    @property
    def _node_factory(self) -> NodeFactory:
        return self._context.node_factory

    @property
    def _data_graph(self) -> DataGraph:
        return self._context.data_graph

    @property
    def _ir_executor(self) -> IRExecutor:
        return self._context.executor

    @staticmethod
    @abstractmethod
    def _parse_metadata(raw_metadata: Any) -> M:
        """Parse raw metadata for the node."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _serialise_metadata(metadata: M) -> Any:
        """Serialise parsed metadata to raw metadata for saving."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _locator(parent_location: Path, metadata: M) -> Path:
        """Return the location reference of this node on the filesystem."""
        raise NotImplementedError

    @classmethod
    def from_uuid(
        cls: Type[T_HoneyNode], /, uuid: UUID, *, context: HoneyContext
    ) -> T_HoneyNode:
        """Construct a node of this class from a uuid."""
        return context.node_factory.create_node(uuid)  # type: ignore

    def is_source(self) -> bool:
        """Return true iff the file is explicitly stored in storage e.g., filesystem."""
        return self._kind == "source"

    def pullback(
        self,
        other: HoneyNode,
        *,
        on: Tuple[Callable | HoneyNode, Callable | HoneyNode] | Callable | HoneyNode,
    ) -> HoneyNode:
        """
        Construct a derived node given by the pullback of ``self`` and ``other``.

        - If ``on`` is a pair ``(f_self, f_other)``, build a coordinate pullback:
          rows where ``f_self(self_row) == f_other(other_row)`` are joined to form an
          ND node over the combined modalities.
        - If ``on`` is a single callable or HoneyNode IR, treat it as a predicate
          over the Euclidean product of ``self`` and ``other`` and include only pairs
          for which the predicate is true.

        The result is a new (virtual) HoneyNode whose arity is
        ``self.arity + other.arity`` and whose points are tuples of the joined rows.
        """
        ir: IRNode
        if self.NODE_TYPE != other.NODE_TYPE:
            raise ValueError("cannot perform pullback across node types")

        if is_tuple(on):
            ir = self._get_pullback_ir(other, on=on)  # type: ignore
        else:
            ir = self._get_predicate_pullback_ir(other, on=on)  # type: ignore

        return self._from_pullback(other, deepcopy(ir))

    def _get_pullback_ir(
        self, other: HoneyNode, *, on: Tuple[Callable | HoneyNode, Callable | HoneyNode]
    ) -> IRPullback:
        self_coords, other_coords = on

        self_transform: IRNode
        other_transform: IRNode

        if callable(self_coords):
            self_transform = IRTransform(
                source=self._ir, transform=PrimitiveFunc(func=self_coords)
            )
        elif isinstance(self_coords, HoneyNode):
            self_transform = IRTransform(source=self._ir, transform=self_coords._ir)
        else:
            raise ValueError(f"{self_coords} not a Callable or HoneyNode instance")

        if callable(other_coords):
            other_transform = IRTransform(
                source=other._ir, transform=PrimitiveFunc(func=other_coords)
            )
        elif isinstance(other_coords, HoneyNode):
            other_transform = IRTransform(source=other._ir, transform=other_coords._ir)
        else:
            raise ValueError(f"{other_coords} not a Callable or HoneyNode instance")

        return IRPullback(
            left_source=self._ir,
            right_source=other._ir,
            left_transform=self_transform,
            right_transform=other_transform,
        )

    def _get_predicate_pullback_ir(
        self, other: HoneyNode, *, on: Callable | HoneyNode
    ) -> IRPredicatePullback:
        predicate_transform: IRNode

        if callable(on):
            """
            the IRNode works with single argument predicate, because this is far more
            elegant from the point of view of the IR. But of course, as consumer of
            HoneyNode, you want to use multiple parameters like ``def on(x, y, ...):``
            """
            on, n_args = get_single_argument_predicate(on)
            if n_args != self.arity + other.arity:
                raise ValueError("predicate must have the same number of positional\
args as arity of resulting data node")

            predicate_transform = PrimitiveFunc(func=on)

        elif isinstance(on, HoneyNode):
            predicate_transform = on._ir
        else:
            raise ValueError(f"{on} not a Callable or HoneyNode instance")

        return IRPredicatePullback(
            left_source=self._ir,
            right_source=other._ir,
            predicate=predicate_transform,
        )

    def _from_pullback(self, other: HoneyNode, ir: IRNode) -> "HoneyNode":
        class JoinedNode(HoneyNode):
            NODE_TYPE = self.NODE_TYPE

            @staticmethod
            def _locator(parent_location: Path, metadata: Any) -> Path:
                return Path(".")  # TODO: figure this out

            @staticmethod
            def _parse_metadata(raw_metadata: Any) -> Any:
                return (
                    self._parse_metadata(raw_metadata[0]),
                    other._parse_metadata(raw_metadata[1]),
                )

            @staticmethod
            def _serialise_metadata(metadata: Any) -> Any:
                return (
                    self._serialise_metadata(metadata),
                    other._serialise_metadata(metadata),
                )

        metadata = (*as_tuple(self.metadata), *as_tuple(other.metadata))

        result = JoinedNode(
            context=self._context,
            metadata=metadata,
            principal_parent=None,
        )
        result._ir = ir
        result._kind = "derived"
        result.ARITY = self.arity + other.arity

        return result

    def __iter__(self) -> Iterator[P_co]:
        """Iterate over the node's children."""
        if self.is_source():
            yield from self._iter_physical()
        else:
            ir = self._ir
            yield from self._ir_executor.run(ir)

    def _iter_physical(self) -> Iterator[P_co]:
        node = self._data_graph[self._uuid]

        if node is None:
            raise KeyError(f"node {node!s} not in data graph")

        return (
            self._node_factory.create_node(n) for n in node.children  # type: ignore
        )

    def __getitem__(self, idx):
        if idx is ...:
            return self.__getitem__(slice(None))

        if isinstance(idx, int):
            if idx < 0:
                return list(self)[idx]
            try:
                return next(islice(iter(self), idx, idx + 1))
            except StopIteration:
                raise IndexError("index out of range")

        if isinstance(idx, slice):
            start = idx.start or 0
            try:
                stop = idx.stop or len(self)  # type: ignore
            except TypeError as e:
                raise TypeError(f"Cannot slice without explicit stop if node type \
{type(self).__name__} has no len()") from e
            return islice(iter(self), start, stop, idx.step)
        if isinstance(idx, tuple):
            if len(idx) == 1:
                return self.__getitem__(idx[0])

            if len(idx) > 1 and self.arity == 1:
                raise ValueError("Cannot take multidimensional slice of a 1D object")

            if len(idx) > 2:
                """
                TODO: There is in fact an interpretation of such high dimensional
                slices. It involves drilling down to the child nodes, so that e.g.,
                col[:,:,:] for an ND collection could give an ``islice`` of 1D
                file points, and e.g., col[:,:,:] for a 1D collection could give an
                ``islice`` of N-dimensional file points. Notably, project[...] would
                give every point in the project(!!!). It's elegant, but complex
                """
                raise NotImplementedError()

            match idx:
                case int() as x, y:
                    return self[x][y]  # type: ignore
                case x, y:
                    return (p[y] for p in self[x])
                case _:
                    raise NotImplementedError()

    def __eq__(self, other: Any) -> bool:
        """Equality based on node id."""
        return isinstance(other, HoneyNode) and self._uuid == other._uuid

    def __hash__(self) -> int:
        """Hash based on node id."""
        return hash(self._uuid)
