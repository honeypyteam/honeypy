"""Node factory to create concrete nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from honeypy.data_graph.meta.class_registry import _CLASS_REGISTRY
from honeypy.data_graph.meta.virtual_node import VirtualNode

if TYPE_CHECKING:
    from honeypy.data_graph.meta.honey_node import HoneyNode

from .data_graph import DataGraph


class NodeFactory:
    """Node factory that creates concrete HoneyNodes."""

    data_graph: DataGraph

    def __init__(self, data_graph: DataGraph):
        self.data_graph = data_graph

    def create_node(self, uuid: UUID) -> HoneyNode:
        """
        Create a HoneyNode from a uuid.

        This function finds the associated metadata in the data graph and constructs
        the associated honey node.
        """
        node = self.data_graph[uuid]

        if node is None:
            raise ValueError(f"node {uuid!s} not in data graph DAG")

        raw_metadata = node.raw_metadata

        if raw_metadata["class_uuid"] == "00000000-0000-0000-0000-000000000000":
            return VirtualNode(
                location=self.data_graph.root_meta_folder, node_factory=self
            )

        cls = _CLASS_REGISTRY[UUID(raw_metadata["class_uuid"])]

        metadata = cls._parse_metadata(raw_metadata["data"])

        return cls(metadata=metadata, uuid=node.uuid, node_factory=self)
