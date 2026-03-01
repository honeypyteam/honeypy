from typing import Any, Callable, Tuple
from uuid import UUID

import pytest

from honeypy.transform.meta.ir import IRExecutor, IRSelect, IRTransform, PrimitiveFunc
from tests.fixtures.get_context import ContextGetter
from tests.fixtures.get_plugin import PluginGetter


def test_ir_transforms_plugin_file(executor: IRExecutor):
    source = IRSelect(UUID("cbae2d2e-4cfb-4bbf-8df7-f9ab971640c4"), arity=1)

    def extract_int(row: Tuple[str, int]) -> int:
        return row[1]

    primitive_func = get_primitive_func(extract_int)
    square = get_primitive_func(lambda x: x**2)
    numbers = IRTransform(source=source, transform=primitive_func)
    numbers_squared = IRTransform(source=numbers, transform=square)

    assert list(executor.run(numbers)) == [1, 3, 9, 4]
    assert list(executor.run(numbers_squared)) == [1, 9, 81, 16]


def get_primitive_func(func: Callable[..., Any]) -> PrimitiveFunc:
    return PrimitiveFunc(func=func)


@pytest.fixture
def executor(
    plugin: PluginGetter,
    context: ContextGetter,
) -> IRExecutor:
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(root_meta_folder=plugin_path / ".honeypy")

    return IRExecutor(node_factory=ctx.node_factory)
