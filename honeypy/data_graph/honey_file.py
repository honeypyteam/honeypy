"""File node types for the data graph.

This module defines :class:`HoneyFile`, a thin node wrapper representing a
storage-backed file (or collection of files) that yields point-like objects when
iterated.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    LiteralString,
    Mapping,
    Optional,
    TypeVar,
)
from uuid import UUID

from honeypy.data_graph.meta.honey_node import HoneyNode
from honeypy.data_graph.meta.node_type import NodeType
from honeypy.data_graph.meta.raw_metadata import RawMetadata

P_co = TypeVar("P_co", covariant=True)
M = TypeVar("M", bound=Mapping[str, Any])
L = TypeVar("L", bound=LiteralString)


class HoneyFile(Generic[L, M, P_co], HoneyNode[L, M, P_co], ABC):
    """Represents a single file node containing point-like items."""

    NODE_TYPE = NodeType.FILE

    # Override load, since there is no children metadata
    def _load_children(  # type: ignore
        self,
        raw_children_metadata: Optional[Dict[UUID, RawMetadata]] = None,
    ) -> Iterable[P_co]:
        return []

    def __iter__(self) -> Iterator[P_co]:
        return self.iter_points()

    @abstractmethod
    def iter_points(self) -> Iterator[P_co]:
        """Iterate over the points in this file."""
        raise NotImplementedError
