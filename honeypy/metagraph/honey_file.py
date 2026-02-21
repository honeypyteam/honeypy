"""File node types for the metagraph.

This module defines `HoneyFile`, a thin node wrapper representing a filesystem-backed
file (or collection of files) that yields point-like objects when iterated.

Design & typing
--------------
- HoneyFile[P] is parameterised by the "point" payload type P
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

from honeypy.metagraph.meta.honey_node import HoneyNode
from honeypy.metagraph.meta.raw_metadata import RawMetadata

P_co = TypeVar("P_co", covariant=True)
M = TypeVar("M", bound=Mapping[str, Any])
L = TypeVar("L", bound=LiteralString)


class HoneyFile(Generic[L, M, P_co], HoneyNode[L, M, P_co], ABC):
    """Represents a single file node containing point-like items."""

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
