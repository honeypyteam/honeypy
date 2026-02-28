from abc import abstractmethod
from pathlib import Path
from typing import (
    Any,
    Generic,
    Iterator,
    Literal,
    LiteralString,
    Mapping,
    Tuple,
    TypedDict,
    TypeVar,
)
from uuid import UUID

from honeypy.data_graph.honey_file import HoneyFile

T = TypeVar("T")
M = TypeVar("M", bound=Mapping[str, Any])
L = TypeVar("L", bound=LiteralString)


# I could TypeAlias here but type checkers aren't very explicit in the type then
class IntMetadata(TypedDict):
    filename: str


class StrMetadata(TypedDict):
    filename: str


class BoolMetadata(TypedDict):
    filename: str


class KeyValFile(HoneyFile[L, M, Tuple[str, T]], Generic[L, M, T]):
    @staticmethod
    def _parse_metadata(raw_metadata: Any) -> M:
        return {"filename": str(raw_metadata["filename"])}  # type: ignore

    @staticmethod
    def _serialise_metadata(metadata: M) -> Any:
        return {k: str(v) for k, v in metadata.items()}

    @staticmethod
    def _locator(parent_location: Path, metadata: M) -> Path:
        return parent_location / metadata["filename"]

    def iter_points(self) -> Iterator[Tuple[str, T]]:
        with self.location.open("r", encoding="utf-8") as fh:
            next(fh)

            for line in fh:
                key, val = line.rstrip("\n").split(",")
                yield (key, self._cast_val(val))

    @staticmethod
    @abstractmethod
    def _cast_val(val: str) -> T:
        raise NotImplementedError


class KeyIntFile(KeyValFile[Literal["integers"], IntMetadata, int]):
    CLASS_UUID = UUID("a1c9bef2-846c-4003-a357-3639628d6d13")

    @staticmethod
    def _cast_val(val: str) -> int:
        return int(val)


class KeyStrFile(KeyValFile[Literal["strings"], StrMetadata, str]):
    CLASS_UUID = UUID("45cd53b2-8d48-4f07-b560-3d0142a8d626")

    @staticmethod
    def _cast_val(val: str) -> str:
        return val


class KeyBoolFile(KeyValFile[Literal["bools"], BoolMetadata, bool]):
    CLASS_UUID = UUID("1d413ff9-1ce1-443a-ba5b-c5e8f878253c")

    @staticmethod
    def _cast_val(val: str) -> bool:
        return val.lower() == "true"
