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
    Iterable,
    Iterator,
    Mapping,
    Optional,
    Set,
    TypeAlias,
)

Metadata: TypeAlias = Mapping[str, Any]


class HoneyNode(ABC):
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

    _children: Set[Any]
    _parents: Set["HoneyNode"]
    _principal_parent: Optional["HoneyNode"]
    _loaded: bool
    _metadata: Metadata
    _location: Path

    def __init__(
        self,
        location: Path,
        principal_parent: Optional["HoneyNode"] = None,
        *,
        metadata: Optional[Metadata] = None,
        load: Optional[bool] = False,
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

    def add(self, items: Iterable[Any]) -> None:
        """Add children to the node.

        Parameters
        ----------
        items : Iterable[Any]
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

    def pullback(
        self,
        other,
        map_1,
        map_2,
    ) -> Any:
        """Compute the pullback (inner join) between this node and ``other``.

        Both nodes are loaded if necessary. ``map_1`` is applied to each child of
        ``self`` and ``map_2`` is applied to each child of ``other``; any pair of
        children whose mapped keys compare equal are paired and included in the
        result.

        This method supports N-dimensional inputs. When joining an N-dimensional
        node the joined children are tuples whose arity reflects the
        dimensionality of the participants (for example joining a 1-D file with
        an M-D file yields tuples of shape ``(self_item, *other_items)``). Callers
        may express the other side with a ``TypeVarTuple`` (PEP 646) in overloads
        to preserve precise static types.

        Parameters
        ----------
        other
            Node to join with. May be any HoneyNode-like object (1-D or ND).
        map_1 : Callable
            Function applied to children of this node to compute join keys.
        map_2 : Callable
            Function applied to children of ``other`` to compute join keys.

        Returns
        -------
        HoneyNode
            A loaded in-memory node whose children are tuples representing
            matched items from the two inputs. Tuple shape depends on the
            dimensionality of the operands.

        Notes
        -----
        - Mapping errors are caught and logged; offending children are skipped.
        - This is an inner join: only matched pairs are returned.
        - Static typing is provided by overloads; the runtime result is a
          lightweight in-memory node populated with the joined tuples.
        """
        if not self._loaded:
            self.load()

        if not other._loaded:
            other.load()

        index: dict[Any, list[Any]] = {}
        for other_child in other._children:
            try:
                key = map_2(other_child)
            except Exception as e:
                print(f"Problem mapping other child {other_child!r}: {e!r}")
                continue
            index.setdefault(key, []).append(other_child)

        joined: set[tuple[Any, Any]] = set()
        for self_child in self._children:
            try:
                key = map_1(self_child)
            except Exception as e:
                print(f"Problem mapping self child {self_child!r}: {e!r}")
                continue
            for match in index.get(key, []):
                joined.add((self_child, match))

        class _JoinNode(HoneyNode):
            # TODO: refactor to not require the join node
            def __init__(self, location, children, metadata=None):
                super().__init__(location, load=False, metadata=metadata or {})
                self._children = set(children)
                self._loaded = True

            def _load(self) -> Iterable[Any]:
                return self._children

            def _unload(self) -> None:
                self._children = set()

            def _load_metadata(self) -> Metadata:
                return self._metadata

        # Instantiate and return the join node
        return _JoinNode(self._location, joined, metadata={})

    @property
    def loaded(self) -> bool:
        """bool: True if the node has been loaded (metadata and children)."""
        return self._loaded

    @property
    def metadata(self) -> Metadata:
        """Mapping[str, Any]: Read-only view of the node's metadata mapping."""
        return self._metadata

    @property
    def children(self) -> Iterable[Any]:
        """Iterable[Any]: Live iterable view of the node's children."""
        return self._children

    @property
    def location(self) -> Path:
        """Path: Representative path of this node in the file system."""
        return self._location

    @abstractmethod
    def _load(self) -> Iterable[Any]:
        """Discover or construct the node's children.

        Returns
        -------
        Iterable[Any]
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

    def __iter__(self) -> Iterator[Any]:
        """Iterate over the node's children.

        Yields
        ------
        T
            Child objects contained by the node.
        """
        return iter(self._children)
