from datetime import datetime
from typing import Any, Dict, Iterable, TypedDict

import yaml

from honeypy.metagraph.honey_collection import HoneyCollection
from tests.projects.project_1.src.key_val_file import KeyValFile
from tests.projects.project_1.src.str_int_point import StrIntTuple


class MetaData(TypedDict):
    title: str
    description: str
    created_at: datetime
    created_by: str


class KeyValCollection(HoneyCollection[StrIntTuple]):
    def _load(self) -> Iterable[KeyValFile]:
        return {
            KeyValFile(f, load=True, principal_parent=self)
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
