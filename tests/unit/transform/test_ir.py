from typing import Any, Callable, List, Protocol, Tuple, Type
from uuid import UUID

import pytest

from honeypy.data_graph.honey_file import HoneyFile
from honeypy.data_graph.meta.constants import ROOT_UUID
from honeypy.data_graph.meta.node_type import NodeType
from honeypy.services.context import HoneyContext
from honeypy.services.datagraph.data_graph import DataGraphNode
from honeypy.transform.meta.ir import (
    IREuclideanProduct,
    IRFilter,
    IRPredicatePullback,
    IRPullback,
    IRSelect,
    IRTransform,
    PrimitiveFunc,
)
from tests.unit.conftest import ContextMocker, DataGraphMocker
from tests.unit.mocks.mock_files import MockIntFile, MockStrFile
from tests.unit.mocks.mock_node_factory import UUIDNode


class ContextGetter(Protocol):
    def __call__(self, nodes: List[Tuple[UUID, Type[HoneyFile]]]) -> HoneyContext: ...


def test_select(context: ContextGetter):
    node_id = UUID("be3e3036-67b3-4950-b4bf-c85abe231ee1")
    ctx = context([(node_id, MockIntFile)])
    select = IRSelect(node_id, arity=1)

    assert list(ctx.executor.run(select)) == [("a", 1), ("b", 2), ("c", 3), ("d", 4)]


def test_euclidean_product(context: ContextGetter):
    int_node_id = UUID("be3e3036-67b3-4950-b4bf-c85abe231ee1")
    str_node_id = UUID("f07935f1-e834-437a-97cb-ecc98d2cc3bf")
    ctx = context([(int_node_id, MockIntFile), (str_node_id, MockStrFile)])
    select_ints = IRSelect(int_node_id, arity=1)
    select_strs = IRSelect(str_node_id, arity=1)

    assert list(ctx.executor.run(IREuclideanProduct(select_ints, select_strs))) == [
        (key_int, key_str)
        for key_int in [("a", 1), ("b", 2), ("c", 3), ("d", 4)]
        for key_str in [("a", "one"), ("b", "two"), ("c", "three"), ("d", "four")]
    ]


def test_filter(context: ContextGetter):
    node_id = UUID("be3e3036-67b3-4950-b4bf-c85abe231ee1")
    ctx = context([(node_id, MockIntFile)])
    select = IRSelect(node_id, arity=1)
    divides_two = get_primitive_func(lambda x: x[1] % 2 == 0)
    filtered = IRFilter(source=select, predicate=divides_two)

    assert list(ctx.executor.run(filtered)) == [("b", 2), ("d", 4)]


def test_transform_primitive(context: ContextGetter):
    node_id = UUID("be3e3036-67b3-4950-b4bf-c85abe231ee1")
    ctx = context([(node_id, MockIntFile)])

    select = IRSelect(node_id, arity=1)
    func = get_primitive_func(lambda x: x[1] ** 2)

    transform = IRTransform(source=select, transform=func)

    assert list(ctx.executor.run(transform)) == [1, 4, 9, 16]


def test_transform_nested(context: ContextGetter):
    node_id = UUID("be3e3036-67b3-4950-b4bf-c85abe231ee1")
    ctx = context([(node_id, MockIntFile)])

    select = IRSelect(node_id, arity=1)
    select_int = get_primitive_func(lambda x: x[1])
    square = get_primitive_func(lambda x: x**2)

    transform = IRTransform(
        source=IRTransform(
            source=IRTransform(source=select, transform=select_int), transform=square
        ),
        transform=square,
    )

    assert list(ctx.executor.run(transform)) == [1, 16, 81, 256]


def test_pullback(context: ContextGetter):
    int_node_id = UUID("be3e3036-67b3-4950-b4bf-c85abe231ee1")
    str_node_id = UUID("f07935f1-e834-437a-97cb-ecc98d2cc3bf")
    ctx = context([(int_node_id, MockIntFile), (str_node_id, MockStrFile)])
    select_ints = IRSelect(int_node_id, arity=1)
    select_strs = IRSelect(str_node_id, arity=1)
    coords_map = get_primitive_func(lambda x: x[0])

    pullback = IRPullback(
        left_source=select_ints,
        right_source=select_strs,
        left_transform=coords_map,
        right_transform=coords_map,
    )

    assert list(ctx.executor.run(pullback)) == [
        (("a", 1), ("a", "one")),
        (("b", 2), ("b", "two")),
        (("c", 3), ("c", "three")),
        (("d", 4), ("d", "four")),
    ]


def test_predicate_pullback(context: ContextGetter):
    int_node_id = UUID("be3e3036-67b3-4950-b4bf-c85abe231ee1")

    ctx = context([(int_node_id, MockIntFile)])
    select_ints = IRSelect(int_node_id, arity=1)

    def multiplies_to_four(x: Tuple[Tuple[str, int], Tuple[str, str]]) -> bool:
        return x[0][1] * x[1][1] == 4

    primitive_multiplies_to_four = get_primitive_func(multiplies_to_four)

    pullback = IRPredicatePullback(
        left_source=select_ints,
        right_source=select_ints,
        predicate=primitive_multiplies_to_four,
    )

    assert list(ctx.executor.run(pullback)) == [
        (("a", 1), ("d", 4)),
        (("b", 2), ("b", 2)),
        (("d", 4), ("a", 1)),
    ]


def test_predicate_pullback_with_transform(context: ContextGetter):
    int_node_id = UUID("be3e3036-67b3-4950-b4bf-c85abe231ee1")

    ctx = context([(int_node_id, MockIntFile)])
    select_ints = IRSelect(int_node_id, arity=1)

    def remove_strings(x: Tuple[Tuple[str, int], Tuple[str, int]]) -> Tuple[int, int]:
        return x[0][1], x[1][1]

    def mulitplies_to_four(x: Tuple[int, int]) -> bool:
        return x[0] * x[1] == 4

    primitive_remove_strings = get_primitive_func(remove_strings)
    primitive_mulitplies_to_four = get_primitive_func(mulitplies_to_four)

    predicate = IRTransform(
        source=IRTransform(
            source=IREuclideanProduct(select_ints, select_ints),
            transform=primitive_remove_strings,
        ),
        transform=primitive_mulitplies_to_four,
    )

    pullback = IRPredicatePullback(
        left_source=select_ints, right_source=select_ints, predicate=predicate
    )

    assert list(ctx.executor.run(pullback)) == [
        (("a", 1), ("d", 4)),
        (("b", 2), ("b", 2)),
        (("d", 4), ("a", 1)),
    ]


def get_primitive_func(func: Callable[..., Any]) -> PrimitiveFunc:
    return PrimitiveFunc(func=func)


# TODO: consider moving this to conftest. Is it general enough?
@pytest.fixture
def context(
    mock_context: ContextMocker, mock_data_graph: DataGraphMocker
) -> ContextGetter:
    def _context(nodes: List[Tuple[UUID, Type[HoneyFile]]]) -> HoneyContext:
        data_graph = mock_data_graph(
            nodes={
                node_uuid: DataGraphNode(
                    uuid=node_uuid,
                    raw_metadata={
                        "node_type": NodeType.FILE,
                        "class_uuid": str(cls.CLASS_UUID),
                        "data": {},
                    },
                    principal_parent=ROOT_UUID,
                )
                for node_uuid, cls in nodes
            }
        )

        ctx = mock_context(
            data_graph=data_graph,
            uuid_nodes={
                node_uuid: UUIDNode(cls=node_cls, principal_parent=ROOT_UUID)
                for node_uuid, node_cls in nodes
            },
        )

        return ctx

    return _context
