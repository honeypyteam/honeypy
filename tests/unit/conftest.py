from typing import Dict, Protocol
from uuid import UUID

import pytest

from honeypy.services.context import HoneyContext
from honeypy.services.datagraph.data_graph import DataGraphNode
from honeypy.transform.meta.ir import IRExecutor
from tests.unit.mocks.mock_node_factory import MockNodeFactory, UUIDNodes

from .mocks import MockDataGraph


class DataGraphMocker(Protocol):
    def __call__(self, nodes: Dict[UUID, DataGraphNode]) -> MockDataGraph: ...


class NodeFactoryMocker(Protocol):
    def __call__(
        self, context: HoneyContext, uuid_nodes: UUIDNodes
    ) -> MockNodeFactory: ...


class ContextMocker(Protocol):
    def __call__(
        self, data_graph: MockDataGraph, uuid_nodes: UUIDNodes
    ) -> HoneyContext: ...


@pytest.fixture
def mock_data_graph() -> DataGraphMocker:
    def _mock_data_graph(nodes: Dict[UUID, DataGraphNode]) -> MockDataGraph:
        return MockDataGraph(nodes)

    return _mock_data_graph


@pytest.fixture
def mock_node_factory() -> NodeFactoryMocker:
    def _mock_node_factory(
        context: HoneyContext, uuid_nodes: UUIDNodes
    ) -> MockNodeFactory:
        return MockNodeFactory(context=context, uuid_nodes=uuid_nodes)

    return _mock_node_factory


@pytest.fixture
def mock_context() -> ContextMocker:
    def _mock_context(data_graph: MockDataGraph, uuid_nodes: UUIDNodes) -> HoneyContext:
        ctx = HoneyContext(data_graph)
        ctx.node_factory = MockNodeFactory(ctx, uuid_nodes)
        ctx.executor = IRExecutor(ctx.node_factory)

        return ctx

    return _mock_context
