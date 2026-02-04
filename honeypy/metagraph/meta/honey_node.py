"""Core metagraph node abstraction.

This module provides the base abstract node used across the metagraph model.
Nodes implement a small lifecycle contract (load/unload) and expose a
lightweight metadata mapping. Concrete specialisations (files, collections,
projects) implement the abstract loading and unloading behaviour.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import (
    Any,
    Generic,
    Iterable,
    Iterator,
    Mapping,
    Optional,
    Set,
    TypeAlias,
    TypeVar,
)

T = TypeVar("T")


Metadata: TypeAlias = Mapping[str, Any]


class HoneyNode(ABC, Generic[T]):
    """Abstract base node for the metagraph.

    A HoneyNode manages a set of child objects (``T``) and exposes a small
    lifecycle API: loading, unloading and metadata access. The class handles
    bookkeeping (children/parents/principal parent) while delegating
    concrete I/O or discovery to the ``_load``/``_unload`` implementations.

    Parameters
    ----------
    principal_parent : Optional[HoneyNode]
        Optional canonical parent for this node. If provided the parent will
        be registered in the node's parent set.
    load : bool, optional
        If True the node will attempt to load during initialization. Defaults
        to False.
    metadata : Optional[Mapping[str, Any]]
        Optional initial metadata mapping for the node.
    """

    _children: Set[T]
    _parents: Set["HoneyNode[Any]"]
    _principal_parent: Optional["HoneyNode[Any]"]
    _loaded: bool
    _metadata: Metadata
    _location: Path

    def __init__(
        self,
        location: Path,
        principal_parent: Optional["HoneyNode"] = None,
        load: Optional[bool] = False,
        *,
        metadata: Optional[Metadata] = None,
    ) -> None:
        """Create a new HoneyNode.

        The constructor initialises internal sets and optionally triggers a
        load operation when ``load`` is True.
        """
        self._children = set()
        self._parents = set()
        self._principal_parent = None
        self._loaded = False
        self._metadata = metadata or {}
        self._location = location

        if principal_parent is not None:
            self._principal_parent = principal_parent
            self._parents.add(principal_parent)

        if load:
            self.load()

    def add(self, items: Iterable[T]) -> None:
        """Add children to the node.

        Parameters
        ----------
        items : Iterable[T]
            An iterable of child objects to insert into the node's internal
            child set. Implementations should ensure bidirectional
            consistency if they also maintain parent links on children.
        """
        self._children.update(items)

    def load(self) -> None:
        """Load metadata and children for the node.

        This method is idempotent. It first attempts to load metadata via
        ``_load_metadata`` and then calls ``_load`` to discover or create the
        concrete children. Errors during either step are caught and logged
        (printed) to avoid breaking consumers; callers may override to provide
        stricter behaviour.
        """
        if self._loaded:
            return

        try:
            self._metadata = self._load_metadata()
        except Exception as e:
            print(f"Problem loading metadata for {self!r}: {e!r}")
            return

        try:
            new_children = self._load() or set()
            self._children.update(new_children)
        except Exception as e:
            print(f"Problem loading children for {self!r}: {e!r}")
        finally:
            self._loaded = True

    def unload(self) -> None:
        """Unload the node and release in-memory child resources.

        This method calls the concrete ``_unload`` implementation and clears
        the node's metadata and internal child set. The node's identity and
        metadata are retained in memory only if the concrete implementation
        chooses to store them externally.
        """
        if not self._loaded:
            return

        self._metadata = {}
        try:
            self._unload()
        except Exception as e:
            print(f"Problem unloading {self!r}: {e!r}")
        finally:
            self._children = set()
            self._loaded = False

    @property
    def loaded(self) -> bool:
        """bool: True if the node has been loaded (metadata and children)."""
        return self._loaded

    @property
    def metadata(self) -> Metadata:
        """Mapping[str, Any]: Read-only view of the node's metadata mapping."""
        return self._metadata

    @property
    def children(self) -> Iterable[T]:
        """Iterable[T]: Live iterable view of the node's children."""
        return self._children

    @property
    def location(self) -> Path:
        """Path: Representative path of this node in the file system."""
        return self._location

    @abstractmethod
    def _load(self) -> Iterable[T]:
        """Discover or construct the node's children.

        Returns
        -------
        Iterable[T]
            Iterable of child objects. Implementations may return sets,
            lists or generators.
        """
        raise NotImplementedError

    @abstractmethod
    def _unload(self) -> None:
        """Free concrete resources for the node."""
        raise NotImplementedError

    @abstractmethod
    def _load_metadata(self) -> Metadata:
        """Load metadata for the node.

        Returns
        -------
        Mapping[str, Any]
            Metadata mapping attached to the node.
        """
        raise NotImplementedError

    def __len__(self) -> int:
        """Return the number of children currently attached to the node."""
        return len(self._children)

    def __iter__(self) -> Iterator[T]:
        """Iterate over the node's children.

        Yields
        ------
        T
            Child objects contained by the node.
        """
        return iter(self._children)
