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
    Generic,
    Iterable,
    Iterator,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
)

from honeypy.metagraph.meta.honey_node import HoneyNode

K = TypeVar("K")
P = TypeVar("P")
Ts = TypeVarTuple("Ts")


class NDHoneyFile(HoneyNode, Generic[Unpack[Ts]]):
    """Represents a single file node containing HoneyPoint[P] items.

    Parameters
    ----------
    *args, **kwargs
        Arguments are forwarded to :class:`HoneyNode`. Concrete subclasses
        typically accept a pathlib.Path ``location`` or similar and pass
        ``load=True`` to auto-load children.

    See Also
    --------
    honeypy.metagraph.meta.honey_node.HoneyNode
        Base class that defines the load/unload/metadata contract.
    honeypy.metagraph.honey_point.HoneyPoint
        Lightweight wrapper type used for the points contained in the file.
    """

    @property
    def children(self) -> Iterable[Tuple[Unpack[Ts]]]:
        """Iterable[Tuple[Unpack[Ts]]]: Live iterable view of the node's children."""
        return super().children

    def __iter__(self: "NDHoneyFile[Unpack[Ts]]") -> Iterator[Tuple[Unpack[Ts]]]:
        """Call super().__iter__."""
        return super().__iter__()
