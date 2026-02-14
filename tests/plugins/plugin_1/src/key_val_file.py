from pathlib import Path
from typing import Any, Generic, Set, TypedDict, TypeVar
from uuid import UUID

from honeypy.metagraph.honey_file import HoneyFile
from tests.plugins.plugin_1.src.key_val_point import KeyValPoint

T = TypeVar("T")


class Metadata(TypedDict):
    filename: str


class KeyValFile(HoneyFile[KeyValPoint[T]], Generic[T]):
    def _unload(self) -> None:
        return

    @staticmethod
    def _parse_metadata(raw_metadata: Any) -> Metadata:
        return {"filename": str(raw_metadata["filename"])}

    @staticmethod
    def _serialise_metadata(metadata: Metadata) -> Any:
        return {k: str(v) for k, v in metadata.items()}

    @staticmethod
    def _locator(parent_location: Path, metadata: Metadata) -> Path:
        return parent_location / metadata["filename"]


class KeyIntFile(KeyValFile[int]):
    CLASS_UUID = UUID("a1c9bef2-846c-4003-a357-3639628d6d13")

    @staticmethod
    def _load_file(location: Path) -> Set[KeyValPoint[int]]:
        pts: Set[KeyValPoint[int]] = set()

        with location.open("r", encoding="utf-8") as fh:
            next(fh)

            for line in fh:
                key, val = line.split(",")
                pts.add(KeyValPoint[int]((key, int(val))))

        return pts


class KeyStrFile(KeyValFile[str]):
    CLASS_UUID = UUID("45cd53b2-8d48-4f07-b560-3d0142a8d626")

    @staticmethod
    def _load_file(location: Path) -> Set[KeyValPoint[str]]:
        pts: Set[KeyValPoint[str]] = set()

        with location.open("r", encoding="utf-8") as fh:
            next(fh)

            for line in fh:
                key, val = line.split(",")
                pts.add(KeyValPoint[str]((key, str(val))))

        return pts
