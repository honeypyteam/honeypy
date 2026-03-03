from typing import Dict, NamedTuple, Type, TypeAlias
from uuid import UUID

from honeypy.data_graph.meta.honey_node import HoneyNode
from honeypy.services.context import HoneyContext
from honeypy.services.datagraph.node_factory import NodeFactory


class UUIDNode(NamedTuple):
    cls: Type[HoneyNode]
    principal_parent: UUID


UUIDNodes: TypeAlias = Dict[UUID, UUIDNode]


class MockNodeFactory(NodeFactory):
    _uuid_nodes: UUIDNodes
    context: HoneyContext

    def __init__(self, context: HoneyContext, uuid_nodes: UUIDNodes):
        self._uuid_nodes = uuid_nodes
        self.context = context

        super().__init__(context)

    def create_node(self, uuid: UUID) -> HoneyNode:
        uuid_node = self._uuid_nodes[uuid]
        return uuid_node.cls(
            uuid=uuid,
            context=self.context,
            metadata={},
            principal_parent=uuid_node.principal_parent,
        )
