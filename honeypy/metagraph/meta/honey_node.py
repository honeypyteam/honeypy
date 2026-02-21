"""Core metagraph node abstraction.

This module provides the base abstract node used across the metagraph model.
"""

import json
from abc import ABC, abstractmethod
from itertools import islice
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Iterator,
    LiteralString,
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

P_co = TypeVar("P_co", covariant=True)
L = TypeVar("L", bound=LiteralString | Tuple[LiteralString, ...])
M = TypeVar("M", bound=Mapping[str, Any] | Tuple[Mapping[str, Any], ...])

# registry for auto-registered node classes keyed by CLASS_UUID
_CLASS_REGISTRY: Dict[UUID, Type["HoneyNode"]] = {}


class HoneyNode(ABC, Generic[L, M, P_co]):
    """Abstract base node for the metagraph."""

    # Kept in metadata and used in parent-child dynamic construction
    CLASS_UUID: ClassVar[UUID]
    ARITY: int = 1

    _uuid: UUID

    _parents: Set["HoneyNode"]
    _principal_parent: "HoneyNode"
    _metadata: M

    def __init__(
        self,
        principal_parent: "HoneyNode",
        *,
        metadata: Optional[M] = None,
        uuid: Optional[UUID] = None,
    ) -> None:
        """Create a new HoneyNode."""
        self._uuid = uuid or uuid4()

        self._parents = set()

        self._principal_parent = principal_parent
        self._parents.add(principal_parent)
        # TODO: you want to update parent here but this cannot be done elegantly
        # yet, as it forces you to combine streams
        # it's better to create a registry for the data DAG first before we can do it
        # this also allows us to move all parent-child relationship logic from the node
        # to the registry, keeping the node class light

        if metadata is None:
            raw_metadata = HoneyNode._raw_metadata(
                self._principal_parent.location, self._uuid
            )
            if raw_metadata is not None:
                self._metadata = self._parse_metadata(raw_metadata["data"])
            else:
                self._metadata = cast(M, {})
        else:
            self._metadata = metadata

    def _save_metadata(self) -> None:
        raw_metadata: RawMetadata = {
            "class_uuid": str(self.CLASS_UUID),
            "data": self._serialise_metadata(self.metadata),
        }

        parent_loc = self._principal_parent.location
        metadata_file = HoneyNode._get_metadata_file(parent_loc, self._uuid)
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        metadata_file.write_text(json.dumps(raw_metadata), encoding="utf-8")

    @property
    def arity(self) -> int:
        """
        int: Returns the dimensionality of the data.

        Often this represents the number of modalities. The data inside the node is
        represented as a tuple of length `self.arity`
        """
        return self.ARITY

    @property
    def metadata(self) -> M:
        """Mapping[str, Any]: Read-only view of the node's metadata mapping."""
        return self._metadata

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

    def _load_children(
        self, raw_children_metadata: Optional[Dict[UUID, RawMetadata]] = None
    ) -> Iterator[P_co]:
        try:
            raw_children_metadata = raw_children_metadata or {}
            for uuid, raw_metadata in raw_children_metadata.items():
                cls = _CLASS_REGISTRY[UUID(raw_metadata["class_uuid"])]

                yield cls(  # type: ignore
                    self,
                    metadata=raw_metadata["data"],
                    uuid=uuid,
                )
        except Exception as e:
            raise Exception(f"Problem loading children metadata for {self!r}") from e

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

    def __iter__(self) -> Iterator[P_co]:
        """Iterate over the node's children.

        Yields
        ------
        T
            Child objects contained by the node.
        """
        return self._load_children(HoneyNode._get_raw_children_metadata(self.location))

    def __getitem__(self, idx):
        if idx is ...:
            return self.__getitem__(slice(None))

        if isinstance(idx, int):
            if idx < 0:
                return list(self)[idx]
            try:
                return next(islice(iter(self), idx, idx + 1))
            except StopIteration:
                raise IndexError("index out of range")

        if isinstance(idx, slice):
            start = idx.start or 0
            try:
                stop = idx.stop or len(self)  # type: ignore
            except TypeError as e:
                raise TypeError(f"Cannot slice without explicit stop if node type \
{type(self).__name__} has no len()") from e
            return islice(iter(self), start, stop, idx.step)
        if isinstance(idx, tuple):
            if len(idx) == 1:
                return self.__getitem__(idx[0])

            if len(idx) > 1 and self.arity == 1:
                raise ValueError("Cannot take multidimensional slice of a 1D object")

            if len(idx) > 2:
                # TODO: There is in fact an interpretation of such high dimensional
                # slices. It involves drilling down to the child nodes, so that e.g.,
                # col[:,:,:] for an ND collection could give an `islice`` of 1D
                # file points, and e.g., col[:,:,:] for a 1D collection could give an
                # `islice` of N-dimensional file points. Notably, project[...] would
                # give every point in the project(!!!). It's elegant, but complex
                raise NotImplementedError()

            match idx:
                case int() as x, y:
                    return self[x][y]
                case x, y:
                    return (p[y] for p in self[x])
                case _:
                    raise NotImplementedError()

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
            return  # TODO: require class UUID. Maybe add decorator for not requiring it
        if not isinstance(class_uuid, UUID):
            raise TypeError(f"{cls.__name__}.CLASS_UUID must be uuid.UUID")

        _CLASS_REGISTRY[class_uuid] = cls
