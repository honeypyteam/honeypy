"""Virtual parent node utilities.

Provides VirtualNode, a lightweight HoneyNode used as an in-memory or test
parent that supplies a canonical location and simple JSON metadata IO helpers.
Use this when you need a project/root placeholder that can resolve child
locations without touching disk layout rules of real parents.
"""

from pathlib import Path
from typing import Any, Dict, Iterable, TypedDict
from uuid import UUID

from honeypy.metagraph.meta.honey_node import HoneyNode


class Metadata(TypedDict):
    """Metadata for virtual nodes."""

    location: Path


class VirtualNode(HoneyNode):
    """A node at the top of the data hierarchy."""

    _metadata: Metadata

    def __init__(
        self,
        location: Path,
        *,
        load: bool | None = False,
    ) -> None:
        super().__init__(
            principal_parent=self, metadata={"location": location}, load=load
        )

    @property
    def location(self) -> Path:
        """
        Path: A path chosen to represent the data's location.

        This overrides the method in the superclass to avoid infinite recursion.
        """
        return self._metadata["location"]

    def _load(self, raw_children_metadata: Dict[UUID, Any] = {}) -> Iterable[Any]:
        """Return `None`."""
        return [None]

    def _unload(self) -> None:
        """Do nothing."""
        pass

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
