"""Raw metadata shapes used for on-disk serialization.

This module defines the runtime shape used to persist child-node metadata
under a parent's metadata store. RawMetadata represents the literal JSON/YAML
structure written to disk: a stable `class_uuid` string that identifies the
concrete node class, and a `data` mapping containing the node's own metadata.
The `Metadata` alias is a recursive mapping used for the deserialized `data`
field.
"""

from typing import Dict, TypeAlias, TypedDict, Union

Metadata: TypeAlias = Dict[str, Union[str, "Metadata"]]


class RawMetadata(TypedDict):
    """TypedDict for the serialized metadata wrapper.

    Fields
    - class_uuid: UUID of the concrete child class as a string.
    - data: the child's metadata as a (possibly nested) mapping of strings.
    """

    class_uuid: str
    data: Metadata
