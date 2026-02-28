"""
A class registry which keeps track of available honey node concrete classes.

This class registry is necessary for class discovery. Since the configuration and
the metadata is parsed dynamically, we use the UUID and the below key value map
to instantiate honey nodes.
"""

# registry for auto-registered node classes keyed by CLASS_UUID
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Type
from uuid import UUID

if TYPE_CHECKING:
    from honeypy.data_graph.meta.honey_node import HoneyNode


_CLASS_REGISTRY: Dict[UUID, Type["HoneyNode"]] = {}


def register_node_class(cls: type["HoneyNode"]) -> None:
    """Register a node class on the global class registry."""
    class_uuid = getattr(cls, "CLASS_UUID", None)
    if getattr(cls, "__abstractmethods__", False):
        return
    if class_uuid is None:
        return
    if not isinstance(class_uuid, UUID):
        raise TypeError(f"{cls.__name__}.CLASS_UUID must be uuid.UUID")

    _CLASS_REGISTRY[class_uuid] = cls
