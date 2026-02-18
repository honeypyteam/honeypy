"""Core metagraph node abstraction.

This module provides the base abstract node used across the metagraph model.
Nodes implement a small lifecycle contract (load/unload) and expose a
lightweight metadata mapping. Concrete specialisations (files, collections,
projects) implement the abstract loading and unloading behaviour.
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    cast,
)
from uuid import UUID, uuid4

from honeypy.metagraph.meta.raw_metadata import RawMetadata

M = TypeVar("M", bound=Mapping[str, Any] | Tuple[Mapping[str, Any], ...])


# registry for auto-registered node classes keyed by CLASS_UUID
_CLASS_REGISTRY: Dict[UUID, Type["HoneyNode"]] = {}


class HoneyNode(ABC, Generic[M]):
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

    # Kept in metadata and used in parent-child dynamic construction
    CLASS_UUID: UUID

    _uuid: UUID

    _children: Set[Any]
    _parents: Set["HoneyNode"]
    _principal_parent: "HoneyNode"
    _loaded: bool
    _metadata: M

    def __init__(
        self,
        principal_parent: "HoneyNode",
        *,
        metadata: Optional[M] = None,
        load: Optional[bool] = False,
        load_metadata: Optional[bool] = True,
        uuid: Optional[UUID] = None,
    ) -> None:
        """Create a new HoneyNode.

        The constructor initialises internal sets and optionally triggers a
        load operation when ``load`` is True.
        """
        self._uuid = uuid or uuid4()

        self._children = set()
        self._parents = set()
        self._loaded = False

        self._principal_parent = principal_parent
        self._parents.add(principal_parent)
        self._principal_parent.update([self])

        if load_metadata and metadata is None:
            raw_metadata = HoneyNode._raw_metadata(
                self._principal_parent.location, self._uuid
            )
            if raw_metadata is not None:
                self._metadata = self._parse_metadata(raw_metadata["data"])
            else:
                self._metadata = cast(M, {})

        if metadata is not None:
            self._metadata = metadata

        if load:
            self.load()

    def update(self, items: Iterable[Any]) -> None:
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
            children = self._load(HoneyNode._get_raw_children_metadata(self.location))
            self._children.update(children)
        except Exception as e:
            print(f"Problem loading children for {self!r}: {e!r}")
        finally:
            self._loaded = True

    def save(self, recursive: Optional[bool] = True) -> None:
        """
        Save this node.

        Parameters
        ----------
        recursive: bool
            If true, save children as well

        Notes
        -----
        Because of the implicit data hierarchy, there is no need to save data related
        to the children. In fact, this is discouraged as it breaks away from the
        framework and violates loose coupling between parent and child data
        """
        if not self._loaded:
            self.load()

        self._save_metadata()
        self.location.parent.mkdir(parents=True, exist_ok=True)
        self._save(self.location, self.metadata)

        if recursive:
            for child in self.children:
                child.save(recursive=True)

        return

    def _save_metadata(self) -> None:
        raw_metadata: RawMetadata = {
            "class_uuid": str(self.CLASS_UUID),
            "data": self._serialise_metadata(self.metadata),
        }

        parent_loc = self._principal_parent.location
        metadata_file = HoneyNode._get_metadata_file(parent_loc, self._uuid)
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        metadata_file.write_text(json.dumps(raw_metadata), encoding="utf-8")

    def unload(self) -> None:
        """Unload the node and release in-memory child resources.

        This method calls the concrete ``_unload`` implementation and clears
        the node's metadata and internal child set. The node's identity and
        metadata are retained in memory only if the concrete implementation
        chooses to store them externally.
        """
        if not self._loaded:
            return

        self._metadata = cast(M, {})
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
    def metadata(self) -> M:
        """Mapping[str, Any]: Read-only view of the node's metadata mapping."""
        return self._metadata

    @property
    def children(self) -> Iterable[Any]:
        """Iterable[Any]: Live iterable view of the node's children."""
        return self._children

    @property
    def location(self) -> Path:
        """
        Path: A path chosen to represent the data's location.

        The location is calculated through the `self._locator` and uses the
        node's metadata and parent's location (if it exists)
        """
        if self._principal_parent is None:
            raise ValueError("Cannot find location without a parent node")

        return self._locator(self._principal_parent.location, self._metadata)

    def _load(
        self, raw_children_metadata: Optional[Dict[UUID, RawMetadata]] = None
    ) -> Iterable["HoneyNode"]:
        raw_children_metadata = raw_children_metadata or {}
        for uuid, raw_metadata in raw_children_metadata.items():
            cls = _CLASS_REGISTRY[UUID(raw_metadata["class_uuid"])]

            yield cls(self, metadata=raw_metadata["data"], load=True, uuid=uuid)

    @abstractmethod
    def _unload(self) -> None:
        """Free concrete resources for the node."""
        raise NotImplementedError

    @staticmethod
    def _raw_metadata(parent_location: Path, uuid: UUID) -> RawMetadata | None:
        metadata_file = HoneyNode._get_metadata_file(parent_location, uuid)

        raw_metadata: RawMetadata | None = None
        if metadata_file.exists():
            with open(metadata_file, "r") as fh:
                raw_metadata = json.load(fh)

        return raw_metadata

    @staticmethod
    def _get_metadata_file(parent_location: Path, uuid: UUID) -> Path:
        return parent_location / ".honeypy" / "children_metadata" / f"{uuid!s}.json"

    @staticmethod
    def _get_raw_children_metadata(location: Path) -> Dict[UUID, RawMetadata]:
        children_metadata_dir = location / ".honeypy" / "children_metadata"

        if not children_metadata_dir.exists():
            return {}

        result = {}
        for f in children_metadata_dir.iterdir():
            uuid = UUID(f.stem)

            with open(f, "r", encoding="utf-8") as fh:
                all_metadata: RawMetadata = json.load(fh)
                result[uuid] = all_metadata

        return result

    @staticmethod
    @abstractmethod
    def _parse_metadata(raw_metadata: Any) -> M:
        """Read raw metadata for the node.

        Returns
        -------
        Metadata
            Metadata mapping attached to the node.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _serialise_metadata(metadata: M) -> Any:
        """Serialise metadata for saving to a metadata file."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _locator(parent_location: Path, metadata: M) -> Path:
        """Return the location of this node on the filesystem."""
        raise NotImplementedError

    @abstractmethod
    def _save(self, location: Path, metadata: M) -> None:
        """
        Save data for the current node.

        Notes
        -----
        Only data related to the current node should be saved. That is, children's
        data should not be handled here but rather in the corresponding child's class.
        Recursion in the `save` method takes care of saving children's data

        For example, a `HoneyCollection` instance should not write to the filesystem
        data related to a `HoneyFile`, even if it's a child of the collection
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

    def __eq__(self, other: Any) -> bool:
        """Equality based on node id."""
        return isinstance(other, HoneyNode) and self._uuid == other._uuid

    def __hash__(self) -> int:
        """Hash based on node id."""
        return hash(self._uuid)

    def __init_subclass__(cls, **kwargs) -> None:
        """Auto-register concrete subclasses that define CLASS_UUID.

        Subclasses that set CLASS_UUID: UUID will be registered into the
        module registry at class-creation time. Abstract subclasses are
        skipped so only concrete implementations are registered.
        """
        super().__init_subclass__(**kwargs)
        class_uuid = getattr(cls, "CLASS_UUID", None)
        if getattr(cls, "__abstractmethods__", False):
            return
        if class_uuid is None:
            return
        if not isinstance(class_uuid, UUID):
            raise TypeError(f"{cls.__name__}.CLASS_UUID must be uuid.UUID")

        _CLASS_REGISTRY[class_uuid] = cls
