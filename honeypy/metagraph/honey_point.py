"""Honey point wrapper.

This module provides ``HoneyPoint``, a tiny wrapper around heterogeneous
payloads used in the metagraph. A point supplies a stable identity, a small
metadata mapping and backlinks to parent nodes (containers or files). Points
are intentionally lightweight: they do not implement the full node lifecycle
(loading/unloading) handled by :class:`~honeypy.metagraph.meta.honey_node.HoneyNode`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Final, Generic, Optional, Set, TypeVar
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from honeypy.metagraph.honey_file import HoneyFile

T = TypeVar("T")


class HoneyPoint(Generic[T]):
    """Lightweight wrapper around a payload with identity, metadata and links.

    A HoneyPoint encapsulates an arbitrary payload ``T`` and attaches a
    stable UUID, a small metadata dictionary and a set of parent nodes that
    reference the point. It is used to represent leaves in the metagraph
    (for example a CSV row or a small structured value).

    It could be, in a contrived but practical way, be used to wrap entire files to
    avoid the explosion associated with labeling every possible data point inside a
    a file. This is often preferred, at the expense of granularity

    It may also be reasonable, in cases of files with semantically distinct "parts",
    to divide them as `HoneyPoint` instances inside the associated `HoneyFile`

    Parameters
    ----------
    data
        The payload to wrap. May be any Python object.
    metadata : dict, optional
        Initial metadata mapping to attach to the point.
    parents : set[HoneyNode], optional
        Optional initial set of parent nodes referencing this point.
    """

    _id: Final[UUID]
    _data: T
    _metadata: Dict[str, Any]
    _parents: Set[HoneyFile["HoneyPoint[T]"]]

    def __init__(
        self,
        data: T,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        parents: Optional[Set[HoneyFile["HoneyPoint[T]"]]] = None,
    ) -> None:
        self._id: UUID = uuid4()
        self._data = data
        self._metadata = dict(metadata or {})
        self._parents = parents or set()

    @property
    def value(self) -> T:
        """Return the wrapped payload.

        Returns
        -------
        T
            The original payload object supplied to the point.
        """
        return self._data

    @property
    def id(self) -> UUID:
        """UUID: Stable identifier for the point (read-only)."""
        return self._id

    def add_parent(self, parent: HoneyFile["HoneyPoint[T]"]) -> None:
        """Register ``parent`` as a backlink to this point.

        Parameters
        ----------
        parent : HoneyNode
            The parent node to add to the point's parent set.
        """
        self._parents.add(parent)

    def remove_parent(self, parent: HoneyFile["HoneyPoint[T]"]) -> None:
        """Remove ``parent`` from the point's parent set if present."""
        self._parents.discard(parent)

    @property
    def parents(self) -> Set[HoneyFile["HoneyPoint[T]"]]:
        """Return the live set of parent nodes referencing this point.

        Note
        ----
        The returned set is the actual backing set; callers should not mutate
        it directly unless they intentionally want to modify the graph
        structure. Use ``add_parent`` / ``remove_parent`` for safe updates.
        """
        return self._parents

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata value by key, returning ``default`` if missing.

        Parameters
        ----------
        key : str
            Metadata key to look up.
        default
            Value to return when the key is not present.
        """
        return self._metadata.get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set a metadata key to ``value`` on the point."""
        self._metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the point.

        Returns a dict with the point id and a shallow copy of its metadata.
        """
        return {"id": str(self._id), "metadata": dict(self._metadata)}

    def __repr__(self) -> str:
        """Return a concise representation for debugging."""
        return f"<HoneyPoint id={self._id} data={self._data!r}>"
