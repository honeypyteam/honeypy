from datetime import datetime
from pathlib import Path
from typing import (
    Any,
    Generic,
    Literal,
    LiteralString,
    Optional,
    Type,
    TypedDict,
    TypeVar,
)
from uuid import UUID

from honeypy.metagraph.honey_collection import HoneyCollection
from honeypy.metagraph.honey_file import HoneyFile
from honeypy.metagraph.meta.honey_node import HoneyNode
from tests.plugins.plugin_1.src.key_val_file import KeyIntFile, KeyStrFile


class Metadata(TypedDict):
    folder_name: str
    title: str
    description: str
    created_at: datetime
    created_by: str
    collection_type: Literal["int collection", "str collection"]


T = TypeVar("T", bound=HoneyFile)
L = TypeVar("L", bound=LiteralString)


class KeyValCollection(HoneyCollection[L, Metadata, T], Generic[L, T]):
    def __init__(
        self,
        principal_parent: HoneyNode,
        *,
        metadata: Optional[Metadata] = None,
        load: bool = False,
        uuid: Optional[UUID] = None,
    ):
        super().__init__(principal_parent, metadata=metadata, load=load, uuid=uuid)

    def _unload(self) -> None:
        for child in self._children:
            child.unload()

    @staticmethod
    def _parse_metadata(raw_metadata: Any) -> Metadata:
        return {
            "folder_name": raw_metadata["folder_name"],
            "collection_type": raw_metadata["collection_type"],
            "title": raw_metadata["title"],
            "description": raw_metadata["description"],
            "created_at": datetime.fromisoformat(raw_metadata["created_at"]),
            "created_by": raw_metadata["created_by"],
        }

    def _get_class(self) -> Any:
        raise NotImplementedError

    def _save(self, location: Path, metadata: Metadata) -> None:
        return

    @staticmethod
    def _locator(
        parent_location: Path,
        metadata: Metadata,
    ) -> Path:
        return parent_location / metadata["folder_name"]


class KeyIntCollection(KeyValCollection[Literal["ints"], KeyIntFile]):
    CLASS_UUID = UUID("2aab4e79-abde-4cd8-9559-aa1d3dcea56e")

    def _get_class(self) -> Type[KeyIntFile]:
        return KeyIntFile

    @staticmethod
    def _serialise_metadata(metadata: Metadata) -> Any:
        return {
            "folder_name": metadata["folder_name"],
            "title": metadata["title"],
            "description": metadata["description"],
            "created_at": metadata["created_at"].isoformat(),
            "created_by": metadata["created_by"],
            "collection_type": "int collection",
        }


class KeyStrCollection(KeyValCollection[Literal["strings"], KeyStrFile]):
    CLASS_UUID = UUID("35f33923-cd77-4ba1-95b9-654611846dcf")

    def _get_class(self) -> Type[KeyStrFile]:
        return KeyStrFile

    @staticmethod
    def _serialise_metadata(metadata: Metadata) -> Any:
        return {
            "folder_name": metadata["folder_name"],
            "title": metadata["title"],
            "description": metadata["description"],
            "created_at": metadata["created_at"].isoformat(),
            "created_by": metadata["created_by"],
            "collection_type": "str collection",
        }
