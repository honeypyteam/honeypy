"""Core data graph node abstraction.

This module provides the base abstract node used across the data graph model.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import islice
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Iterator,
    LiteralString,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
)
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from honeypy.data_graph.meta.node_type import NodeType
    from honeypy.services.datagraph.data_graph import DataGraph
    from honeypy.services.datagraph.node_factory import NodeFactory

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

    _data_graph: DataGraph
    _node_factory: NodeFactory
    _principal_parent: UUID | None

    def __init__(
        self,
        uuid: Optional[UUID] = None,
        *,
        node_factory: NodeFactory,
        metadata: M,
        principal_parent: Optional[UUID] = None,
    ) -> None:
        """Create a new HoneyNode."""
        self._uuid = uuid or uuid4()
        self._metadata = metadata
        self._principal_parent = principal_parent

        self._node_factory = node_factory
        self._data_graph = node_factory.data_graph

    @property
    def arity(self) -> int:
        """
        int: Returns the dimensionality of the data.

        Often this represents the number of modalities. The data inside the node is
        represented as a tuple of length `self.arity`
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

        The location is calculated through the `self._locator` and uses the
        node's metadata and parent's location (if it exists)
        """
        return self._locator(self.principal_parent.location, self._metadata)

    @property
    def uuid(self) -> UUID:
        """Get the uuid for this node."""
        return self._uuid

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

    def __iter__(self) -> Iterator[P_co]:
        """Iterate over the node's children."""
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
                # TODO: There is in fact an interpretation of such high dimensional
                # slices. It involves drilling down to the child nodes, so that e.g.,
                # col[:,:,:] for an ND collection could give an `islice`` of 1D
                # file points, and e.g., col[:,:,:] for a 1D collection could give an
                # `islice` of N-dimensional file points. Notably, project[...] would
                # give every point in the project(!!!). It's elegant, but complex
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
