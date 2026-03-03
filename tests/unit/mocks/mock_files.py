from pathlib import Path
from typing import Any, Generic, Iterator, Literal, LiteralString, Tuple, TypeVar
from uuid import UUID

from honeypy.data_graph.honey_file import HoneyFile

P_co = TypeVar("P_co", covariant=True)
L = TypeVar("L", bound=LiteralString)


class MockKeyValFile(HoneyFile[L, Any, P_co], Generic[L, P_co]):
    def iter_points(self) -> Iterator:
        return NotImplemented

    @staticmethod
    def _parse_metadata(raw_metadata: Any) -> Any:
        return NotImplemented

    @staticmethod
    def _serialise_metadata(metadata: Any) -> Any:
        return NotImplemented

    @staticmethod
    def _locator(parent_location: Path, metadata: Any) -> Path:
        return NotImplemented


class MockIntFile(MockKeyValFile[Literal["ints"], Tuple[str, int]]):
    CLASS_UUID = UUID("56ad455f-4bda-49c7-9c19-cf99a7c575ad")

    def iter_points(self) -> Iterator[Tuple[str, int]]:
        return (x for x in [("a", 1), ("b", 2), ("c", 3), ("d", 4)])


class MockStrFile(MockKeyValFile[Literal["strings"], Tuple[str, str]]):
    CLASS_UUID = UUID("56ad455f-4bda-49c7-9c19-cf99a7c575ad")

    def iter_points(self) -> Iterator[Tuple[str, str]]:
        return (x for x in [("a", "one"), ("b", "two"), ("c", "three"), ("d", "four")])
