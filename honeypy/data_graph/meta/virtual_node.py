"""Virtual parent node utilities.

Provides VirtualNode, a lightweight HoneyNode used as an in-memory or test
parent that supplies a canonical location and simple JSON metadata IO helpers.
Use this when you need a project/root placeholder that can resolve child
locations without touching disk layout rules of real parents.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterator, Literal, Optional, TypedDict
from uuid import UUID

from honeypy.data_graph.meta.honey_node import HoneyNode
from honeypy.data_graph.meta.node_type import NodeType

if TYPE_CHECKING:
    from honeypy.services.datagraph.node_factory import NodeFactory


class Metadata(TypedDict):
    """Metadata for virtual nodes."""

    location: Path


class VirtualNode(HoneyNode[Literal[""], Metadata, None]):
    """A node at the top of the data hierarchy."""

    NODE_TYPE = NodeType.ROOT
    _metadata: Metadata

    def __init__(
        self,
        location: Path,
        node_factory: NodeFactory,
    ) -> None:
        super().__init__(
            node_factory=node_factory,
            metadata={"location": location},
            uuid=UUID("00000000-0000-0000-0000-000000000000"),
        )

    @property
    def location(self) -> Path:
        """
        Path: A path chosen to represent the data's location.

        This overrides the method in the superclass to avoid infinite recursion.
        """
        return self._metadata["location"]

    def _load_children(
        self, raw_children_metadata: Optional[Dict[UUID, Any]] = None
    ) -> Iterator[None]:
        yield None

    @staticmethod
    def _parse_metadata(raw_metadata: Any) -> Metadata:
        """Read metadata JSON."""
        return {"location": Path(raw_metadata["location"])}

    @staticmethod
    def _serialise_metadata(metadata: Metadata) -> Any:
        """Write metadata as JSON."""
        return {"location": str(metadata["location"])}

    @staticmethod
    def _locator(parent_location: Path, metadata: Metadata) -> Path:
        """Return the location of this node from the metadata directly."""
        return metadata["location"]

    def __iter__(self) -> Iterator[None]:
        yield None
