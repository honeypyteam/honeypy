from typing import Generic, List, Set, TypedDict, TypeVar

from honeypy.metagraph.honey_file import HoneyFile
from tests.plugins.plugin_1.src.key_val_point import KeyValPoint

T = TypeVar("T")


class Metadata(TypedDict):
    columns: List[str]
    filename: str


class KeyValFile(HoneyFile[KeyValPoint[T]], Generic[T]):
    def _load(self) -> Set[KeyValPoint[T]]:
        pts: Set[KeyValPoint[T]] = set()

        with self._location.open("r", encoding="utf-8") as fh:
            next(fh)

            for line in fh:
                key, val = line.split(",")
                pts.add(KeyValPoint[T]((key, self._convert(val)), parents={self}))

        return pts

    def _load_metadata(self) -> Metadata:
        with self._location.open("r", encoding="utf-8") as fh:
            line = next(fh)
            cols = line.split(",")

            return {"columns": cols, "filename": self._location.name}

    def _unload(self) -> None:
        return

    def _convert(self, _: str) -> T:
        raise NotImplementedError


class KeyIntFile(KeyValFile[int]):
    def _convert(self, value: str) -> int:
        return int(value)


class KeyStrFile(KeyValFile[str]):
    def _convert(self, value: str) -> str:
        return value
