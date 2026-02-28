"""N-dimensional project node helpers.

This module defines :class:`NDHoneyProject`, a typing-friendly abstraction for
projects whose children are tuples of heterogeneous collections (for example a project
whose children are subfolders etc.) ``TypeVarTuple`` is used to express the
variable arity of children via ``Ts = TypeVarTuple('Ts')`` and the class is
parameterized as ``NDHoneyProject[Unpack[Ts]]``.

Runtime behaviour is provided by :class:`honeypy.datagraph.meta.honey_node.HoneyNode`.
This module focuses on typing helpers and a small ND-aware convenience API.
"""

from typing import (
    Any,
    Generic,
    LiteralString,
    Mapping,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
)

from honeypy.data_graph.meta.honey_node import HoneyNode
from honeypy.data_graph.meta.node_type import NodeType

Ts = TypeVarTuple("Ts")
M = TypeVar("M", bound=Tuple[Mapping[str, Any], ...])
L = TypeVar("L", bound=Tuple[LiteralString, ...])


class NDHoneyProject(Generic[L, M, Unpack[Ts]], HoneyNode[L, M, Tuple[Unpack[Ts]]]):
    """Represents a single project node containing HoneyCollection items."""

    NODE_TYPE = NodeType.PROJECT
