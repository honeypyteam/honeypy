from pathlib import Path
from typing import Any, Generic, List, Tuple, TypedDict, TypeVar
from uuid import UUID

from honeypy.metagraph.honey_file import HoneyFile

T = TypeVar("T")


class Metadata(TypedDict):
    filename: str


class KeyValFile(HoneyFile[Metadata, Tuple[str, T]], Generic[T]):
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

    def _save(self, location: Path, metadata: Metadata) -> None:
        with location.open("w", encoding="utf-8") as fh:
            fh.write("key,value\n")
            for key, val in self.children:  # type: ignore
                fh.write(f"{key!s},{val!s}\n")  # type: ignore


class KeyIntFile(KeyValFile[int]):
    CLASS_UUID = UUID("a1c9bef2-846c-4003-a357-3639628d6d13")

    @staticmethod
    def _load_file(location: Path) -> List[Tuple[str, int]]:
        pts: List[Tuple[str, int]] = []

        with location.open("r", encoding="utf-8") as fh:
            next(fh)

            for line in fh:
                key, val = line.split(",")
                pts.append((key, int(val)))

        return pts


class KeyStrFile(KeyValFile[str]):
    CLASS_UUID = UUID("45cd53b2-8d48-4f07-b560-3d0142a8d626")

    @staticmethod
    def _load_file(location: Path) -> List[Tuple[str, str]]:
        pts: List[Tuple[str, str]] = []

        with location.open("r", encoding="utf-8") as fh:
            next(fh)

            for line in fh:
                key, val = line.split(",")
                pts.append((key, str(val)))

        return pts
