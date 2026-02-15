"""N-dimensional project node helpers.

This module defines :class:`NDHoneyProject`, a typing-friendly abstraction for
projects whose children are tuples of heterogeneous collections (for example a project
whose children are subfolders etc.) ``TypeVarTuple`` is used to express the
variable arity of children via ``Ts = TypeVarTuple('Ts')`` and the class is
parameterized as ``NDHoneyProject[Unpack[Ts]]``.

Runtime behaviour is provided by :class:`honeypy.metagraph.meta.honey_node.HoneyNode`.
This module focuses on typing helpers and a small ND-aware convenience API.
"""

from typing import (
    Generic,
    Iterable,
    Iterator,
    Tuple,
    TypeVarTuple,
    Unpack,
)

from honeypy.metagraph.meta.honey_node import HoneyNode

Ts = TypeVarTuple("Ts")


class NDHoneyProject(HoneyNode, Generic[Unpack[Ts]]):
    """Represents a single project node containing HoneyCollection items.

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
    """

    @property
    def children(self) -> Iterable[Tuple[Unpack[Ts]]]:
        """Iterable[Tuple[Unpack[Ts]]]: Live iterable view of the node's children."""
        return super().children

    def __iter__(self: "NDHoneyProject[Unpack[Ts]]") -> Iterator[Tuple[Unpack[Ts]]]:
        """Call super().__iter__."""
        return super().__iter__()
