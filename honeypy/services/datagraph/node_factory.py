"""Node factory to create concrete nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Generator
from uuid import UUID

from honeypy.data_graph.meta.class_registry import _CLASS_REGISTRY
from honeypy.data_graph.meta.constants import ROOT_UUID
from honeypy.data_graph.meta.virtual_node import VirtualNode

if TYPE_CHECKING:
    from honeypy.data_graph.meta.honey_node import HoneyNode
    from honeypy.services.context import HoneyContext


class NodeFactory:
    """Node factory that creates concrete HoneyNodes."""

    context: HoneyContext

    def __init__(self, context: HoneyContext):
        self.context = context

    def create_node(self, uuid: UUID) -> HoneyNode:
        """
        Create a HoneyNode from a uuid.

        This function finds the associated metadata in the data graph and constructs
        the associated honey node.
        """
        node = self.context.data_graph[uuid]

        if node is None:
            raise ValueError(f"node {uuid!s} not in data graph DAG")

        raw_metadata = node.raw_metadata

        if raw_metadata["class_uuid"] == str(ROOT_UUID):
            return VirtualNode(
                location=self.context.data_graph.root_meta_folder, context=self.context
            )

        cls = _CLASS_REGISTRY[UUID(raw_metadata["class_uuid"])]

        metadata = cls._parse_metadata(raw_metadata["data"])

        return cls(context=self.context, metadata=metadata, uuid=node.uuid)

    def create_on_metadata(
        self, partial_metadata: Dict
    ) -> Generator[HoneyNode, None, None]:
        """
        Yield all HoneyNodes whose stored raw_metadata matches the given pattern.

        The match is recursive: every key path and value in ``partial_metadata`` must
        be present with the same value inside a node's ``raw_metadata`` (but the node
        may have additional keys). For each matching node UUID, this method calls
        ``create_node`` and yields the resulting HoneyNode.
        """
        return (
            self.create_node(uuid)
            for uuid in self.context.data_graph.match_on(partial_metadata)
        )
