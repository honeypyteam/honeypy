from pathlib import Path
from typing import Any, Literal, TypedDict
from uuid import UUID

from honeypy.data_graph.honey_collection import HoneyCollection
from tests.plugins.plugin_1.src.array_file import ArrayFile


class Metadata(TypedDict):
    folder_name: str
    title: str
    description: str
    created_by: str


class ArrayFileCollection(HoneyCollection[Literal["Arrays"], Metadata, ArrayFile]):
    CLASS_UUID = UUID("f68c8749-8c91-4c8e-b07c-67f09208ff2a")

    @staticmethod
    def _parse_metadata(raw_metadata: Any) -> Metadata:
        return {
            "folder_name": raw_metadata["folder_name"],
            "title": raw_metadata["title"],
            "description": raw_metadata["description"],
            "created_by": raw_metadata["created_by"],
        }

    @staticmethod
    def _locator(
        parent_location: Path,
        metadata: Metadata,
    ) -> Path:
        return parent_location / metadata["folder_name"]

    @staticmethod
    def _serialise_metadata(metadata: Metadata) -> Any:
        return metadata
