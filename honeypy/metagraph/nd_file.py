"""N-dimensional file node helpers.

This module defines :class:`NDHoneyFile`, a typing-friendly abstraction for
files whose children are tuples of heterogeneous values (for example a file
whose rows are pairs, triples, etc.). ``TypeVarTuple`` is used to express the
variable arity of children via ``Ts = TypeVarTuple('Ts')`` and the class is
parameterized as ``NDHoneyFile[Unpack[Ts]]``.

Runtime behaviour is provided by :class:`honeypy.metagraph.meta.honey_node.HoneyNode`.
This module focuses on typing helpers and a small ND-aware convenience API.
"""

from typing import (
    Any,
    Generic,
    Iterable,
    Iterator,
    LiteralString,
    Mapping,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
)

from honeypy.metagraph.meta.honey_node import HoneyNode

Ts = TypeVarTuple("Ts")
M = TypeVar("M", bound=Tuple[Mapping[str, Any], ...])
L = TypeVar("L", bound=Tuple[LiteralString, ...])
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")


class NDHoneyFile(Generic[L, M, Unpack[Ts]], HoneyNode[L, M]):
    """Represents a single file node containing point-like items."""

    @property
    def children(self) -> Iterable[Tuple[Unpack[Ts]]]:
        """Iterable[Tuple[Unpack[Ts]]]: Live iterable view of the node's children."""
        return super().children

    def __iter__(self: "NDHoneyFile[L, M, Unpack[Ts]]") -> Iterator[Tuple[Unpack[Ts]]]:
        """Call super().__iter__."""
        return super().__iter__()

    def __getitem__(self, idx):
        """Get an item. Delegates to super()."""
        return super().__getitem__(idx)
