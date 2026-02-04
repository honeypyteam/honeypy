"""File node type for the metagraph.

This module defines HoneyFile, a thin node wrapper representing a filesystem
backed file or collection of files
that yields HoneyPoint[T] items when iterated. The class is kept minimal here;
concrete file types should subclass and implement the loading behaviour on the
HoneyNode contract.

Notes
-----
- A HoneyFile is parameterized by the point payload type ``T`` exposed by its
  HoneyPoint children (e.g. ``HoneyFile[tuple[str, int]]``).
- Loading/unloading, metadata and child management are provided by
  :class:`honeypy.metagraph.meta.honey_node.HoneyNode`.
"""

from typing import Generic, TypeVar

from honeypy.metagraph.honey_point import HoneyPoint
from honeypy.metagraph.meta.honey_node import HoneyNode

T = TypeVar("T")


class HoneyFile(HoneyNode[HoneyPoint[T]], Generic[T]):
    """Represents a single file node containing HoneyPoint[T] items.

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

    pass
