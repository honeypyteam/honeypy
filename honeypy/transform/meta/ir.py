"""Logical intermediate representation (IR) for transformations.

You could conceptualise a transformation, or query, as just a mapping. But this loses
information and makes optimisation impossible. Instead we define transformations as
IRs of mappings which can be passed into the execution engine and physical planner.

There are many useful transformations, such as reducing, grouping etc., which can be
performed on honey nodes... But it turns out to be more reasonable to define a small
group that acts as a basis. These are:
- Pullback (which generalises joins, and also is the inverse of focus)
- Focus (which generalises projections, and also is the inverse of pullback)
- Map (which is a map from a honey node to another honey node on the same level in the
data hierarchy)

In some ways this view is more sophisticated than what we see in database engines,
e.g., to handle relational algebra. Namely of these are higher order transformations;
they contain transformations as data. An example is the pullback, which requires a
mapping between the data and a latent coordinate space (such as time)--this mapping is
best handled as a transformation in its own right, i.e., they take an IR.

In fact all nodes mentioned above are higher order transformations. They "bottom out"
when plain functions are passed into them.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import product
from typing import TYPE_CHECKING, Any, Callable, ChainMap, Iterable, List, TypeVar
from uuid import UUID

from honeypy.transform.meta.utils import expand_on_arity

if TYPE_CHECKING:
    from honeypy.data_graph.meta.honey_node import HoneyNode
    from honeypy.services.datagraph.node_factory import NodeFactory

R_co = TypeVar("R_co", covariant=True)


class IRNode:
    """Base class for all query IR nodes."""

    arity: int


@dataclass
class IRPullback(IRNode):
    """Pullback of two sources along coordinate transforms (generalised join)."""

    left_source: IRNode
    right_source: IRNode
    left_transform: IRNode
    right_transform: IRNode

    def __init__(
        self,
        *,
        left_source: IRNode,
        right_source: IRNode,
        left_transform: IRNode,
        right_transform: IRNode,
    ):
        self.left_source = left_source
        self.right_source = right_source

        if isinstance(left_transform, PrimitiveFunc):
            self.left_transform = IRTransform(
                source=left_source, transform=left_transform
            )
        else:
            self.left_transform = left_transform

        if isinstance(right_transform, PrimitiveFunc):
            self.right_transform = IRTransform(
                source=left_source, transform=right_transform
            )
        else:
            self.right_transform = right_transform

        self.arity = self.left_source.arity + self.right_source.arity


@dataclass
class IRFilter(IRNode):
    """Filter a source by a boolean-valued predicate IR on its rows."""

    source: IRNode
    predicate: IRNode

    def __init__(self, *, source: IRNode, predicate: IRNode):
        self.source = source
        self.predicate = predicate
        self.arity = source.arity


@dataclass
class IRPredicatePullback(IRNode):
    """Pullback defined by a predicate over the Euclidean product of sources."""

    node: IRNode

    def __init__(self, *, left_source: IRNode, right_source: IRNode, predicate: IRNode):
        self.node = IRFilter(
            source=IREuclideanProduct(
                left_source=left_source, right_source=right_source
            ),
            predicate=predicate,
        )
        self.arity = self.node.arity


@dataclass
class IRTransform(IRNode):
    """Apply a (possibly higher-order) transform IR to each row of a source."""

    source: IRNode
    transform: IRNode

    def __init__(self, *, source: IRNode, transform: IRNode) -> None:
        self.source = source
        self.transform = transform
        self.arity = source.arity


@dataclass
class IRSelect(IRNode):
    """Leaf that selects a concrete HoneyNode by UUID as an IR source."""

    node_id: UUID
    arity: int


@dataclass
class IREuclideanProduct(IRNode):
    """Euclidean (Cartesian) product of two sources, implemented via pullback."""

    node: IRNode

    def __init__(self, left_source: IRNode, right_source: IRNode):
        POINT = object()

        self.node = IRPullback(
            left_source=left_source,
            right_source=right_source,
            left_transform=PrimitiveFunc(func=lambda *args, **kwargs: POINT),
            right_transform=PrimitiveFunc(func=lambda *args, **kwargs: POINT),
        )
        self.arity = self.node.arity


@dataclass
class PrimitiveFunc(IRNode):
    """Leaf: a plain function seen as a transformation."""

    func: Callable[..., Any]

    def __init__(self, *, func: Callable[..., Any]):
        self.func = func
        self.arity = -1


class IRVisitor:
    """Base visitor for IR."""

    def visit(self, node: IRNode):
        """Visit and process nodes in the intermediate representation tree."""
        method_name = "_visit_" + type(node).__name__
        method = getattr(self, method_name, None)
        if method is None:
            method = IRVisitor.generic_visit(node, method_name)
        return method(node)

    @staticmethod
    def generic_visit(node: IRNode, method_name: str):
        """Raise an exception."""
        raise RuntimeError(f"No {method_name!s} method found on {node!s}")


class IRExecutor(IRVisitor):
    """
    Execute IR trees against the data graph to produce result iterables.

    The executor walks an IRNode tree, resolving IRSelect leaves into concrete
    HoneyNodes via the NodeFactory and evaluating higher-order nodes (pullbacks,
    filters, transforms) to yield Python iterables of rows.
    """

    def __init__(
        self, node_factory: NodeFactory, env: dict[str, HoneyNode] | None = None
    ):
        self._node_factory = node_factory
        self._env = ChainMap(dict(env or {}))

    def run(self, ir: IRNode) -> Iterable[Any]:
        """Evaluate an IR tree and return an iterator over its results."""
        return self.visit(ir)

    def _visit_IRPullback(self, node: IRPullback) -> Iterable[Any]:
        index_left: dict[Any, List[Any]] = defaultdict(list)
        left_arity = node.left_source.arity
        right_arity = node.right_source.arity

        for coord, val in zip(
            self.visit(node.left_transform), self.visit(node.left_source)
        ):
            index_left[coord].append(val)

        index_right: dict[Any, List[Any]] = defaultdict(list)
        for coord, val in zip(
            self.visit(node.right_transform), self.visit(node.right_source)
        ):
            index_right[coord].append(val)

        def _gen():
            for coord, left_vals in index_left.items():
                right_vals = index_right.get(coord, None)
                if right_vals is None:
                    continue

                for lv, rv in product(left_vals, right_vals):
                    yield (
                        *expand_on_arity(lv, left_arity),
                        *expand_on_arity(rv, right_arity),
                    )

        return _gen()

    def _visit_IRPredicatePullback(self, node: IRPredicatePullback) -> IRNode:
        return self.visit(node.node)

    def _visit_IRFilter(self, node: IRFilter) -> IRNode:
        if isinstance(node.predicate, PrimitiveFunc):
            return (  # type: ignore
                val for val in self.visit(node.source) if node.predicate.func(val)
            )

        return (
            row
            for row, truth_value in zip(
                self.visit(node.source), self.visit(node.predicate)
            )
            if truth_value
        )  # type: ignore

    def _visit_IRTransform(self, node: IRTransform) -> Iterable[Any]:
        src_iter = self.visit(node.source)

        if isinstance(node.transform, PrimitiveFunc):
            f = node.transform.func
            return (f(x) for x in src_iter)

        def _gen():
            for x in src_iter:
                child_exec = self._with_binding("child", x)
                yield from child_exec.run(node.transform)

        return _gen()

    def _visit_IREuclideanProduct(self, node: IREuclideanProduct) -> Iterable[Any]:
        return self.visit(node.node)

    def _visit_IRSelect(self, node: IRSelect) -> Iterable[Any]:
        honey_node = self._node_factory.create_node(node.node_id)

        return iter(honey_node)

    def _with_binding(self, key: str, value: HoneyNode) -> "IRExecutor":
        child = IRExecutor(self._node_factory)
        child._env = self._env.new_child({key: value})

        return child
