from pathlib import Path
from typing import Any, Literal, TypeAlias, TypedDict
from uuid import UUID

from honeypy.metagraph.honey_project import HoneyProject
from honeypy.metagraph.meta.honey_node import HoneyNode
from tests.plugins.plugin_1.src.key_val_collection import (
    KeyIntCollection,
    KeyStrCollection,
)

KeyVarCollections: TypeAlias = KeyIntCollection | KeyStrCollection


class Metadata(TypedDict):
    project_name: str


class KeyValProject(
    HoneyProject[Literal["Keys and Vals"], Metadata, KeyVarCollections]
):
    CLASS_UUID = UUID("a7ef3443-6339-4a95-a0c0-73d477ead1d2")

    def __init__(self, principal_parent: HoneyNode, *, load: bool = False):
        super().__init__(principal_parent, load=load)

    def _unload(self) -> None:
        for child in self._children:
            child.unload()

    @staticmethod
    def _parse_metadata(raw_metadata: Any) -> Metadata:
        return {"project_name": raw_metadata["project name"]}

    @staticmethod
    def _serialise_metadata(metadata: Any) -> Any:
        return {k: str(v) for k, v in metadata.items()}

    @staticmethod
    def _locator(parent_location: Path, metadata: Metadata) -> Path:
        return parent_location

    def _save(self, location: Path, metadata: Metadata) -> None:
        return
