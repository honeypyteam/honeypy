from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, List, Literal, Tuple, TypeAlias, TypedDict
from uuid import UUID

from honeypy.data_graph.adapters import LoadableMixin
from honeypy.data_graph.honey_file import HoneyFile

ExternalArrayRow: TypeAlias = Tuple[int, int, int]


@dataclass
class InternalArrayRow:
    """Internal array row"""

    first: int
    second: int
    third: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InternalArrayRow):
            return NotImplemented
        return (
            self.first == other.first
            and self.second == other.second
            and self.third == other.third
        )

    def __hash__(self) -> int:
        return hash((self.first, self.second, self.third))


class ExternalArray:
    """
    ExternalArray represents a class the plugin has not written.

    The idea of these test stubs is that this array must be adapted to via an
    implementation of the LoadableMixin interface.
    """

    contents: List[ExternalArrayRow]

    def __init__(self, contents: List[ExternalArrayRow]):
        self.contents = contents

    def iterrows(self) -> Iterator[Tuple[int, ExternalArrayRow]]:
        for idx, row in enumerate(self.contents):
            yield idx, row


class Metadata(TypedDict):
    filename: str


class ArrayFile(
    LoadableMixin[ExternalArray, InternalArrayRow],
    HoneyFile[Literal["numbers"], Metadata, InternalArrayRow],
):
    """
    A file that works with arrays directly.

    This is a dummy example that demonstrates working with "external" libraries
    using files more like an adapter using the `LoadableMixin`
    """

    CLASS_UUID = UUID("fc5cd48b-e5f9-4bdf-a956-64cec3c0d620")

    @staticmethod
    def load_from(data: ExternalArray) -> Iterator[InternalArrayRow]:
        return (InternalArrayRow(a, b, c) for _, (a, b, c) in data.iterrows())

    @staticmethod
    def _get_data(children: Iterator[InternalArrayRow]) -> ExternalArray:
        return ExternalArray(contents=[(c.first, c.second, c.third) for c in children])

    @staticmethod
    def _parse_metadata(raw_metadata: Any) -> Metadata:
        return {
            "filename": raw_metadata["filename"],
        }

    @staticmethod
    def _serialise_metadata(metadata: Metadata) -> Any:
        return {
            "filename": metadata["filename"],
        }

    @staticmethod
    def _locator(parent_location: Path, metadata: Metadata) -> Path:
        return parent_location / metadata["filename"]

    def iter_points(self) -> Iterator[InternalArrayRow]:
        with self.location.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                parts = line.split(",")

                yield InternalArrayRow(
                    first=int(parts[0]), second=int(parts[1]), third=int(parts[2])
                )
