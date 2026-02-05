from datetime import datetime
from typing import Any, Dict, Generic, Iterable, Type, TypedDict, TypeVar

import yaml

from honeypy.metagraph.honey_collection import HoneyCollection
from honeypy.metagraph.honey_file import HoneyFile
from tests.projects.project_1.src.key_val_file import KeyIntFile, KeyStrFile


class MetaData(TypedDict):
    title: str
    description: str
    created_at: datetime
    created_by: str


T = TypeVar("T", bound=HoneyFile[Any])


class KeyValCollection(HoneyCollection[T], Generic[T]):
    def _load(self) -> Iterable[T]:
        return {
            self._get_class()(f, load=True, principal_parent=self)
            for f in self._location.iterdir()
            if f.is_file() and f.suffix == ".csv"
        }

    def _unload(self) -> None:
        for child in self._children:
            child.unload()

    def _load_metadata(self) -> MetaData:
        meta_file = self._location / ".metadata"

        raw: Dict[str, Any] = yaml.safe_load(meta_file.read_text(encoding="utf-8"))
        created_at = datetime.fromisoformat(str(raw.get("created_at", "")))

        return {
            "title": str(raw.get("title", "")),
            "description": str(raw.get("description", "")),
            "created_at": created_at,
            "created_by": str(raw.get("created_by", "")),
        }

    def _get_class(self) -> Any:
        raise NotImplementedError


class KeyIntCollection(KeyValCollection[KeyIntFile]):
    def _get_class(self) -> Type[KeyIntFile]:
        return KeyIntFile


class KeyStrCollection(KeyValCollection[KeyStrFile]):
    def _get_class(self) -> Type[KeyStrFile]:
        return KeyStrFile
