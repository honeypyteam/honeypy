from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, List, Tuple, TypeAlias, TypedDict

from honeypy.metagraph.adapters import LoadableMixin
from honeypy.metagraph.honey_file import HoneyFile

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


class ArrayFile(LoadableMixin[ExternalArray], HoneyFile[Metadata, InternalArrayRow]):
    """
    A file that works with arrays directly.

    This is a dummy example that demonstrates working with "external" libraries
    using files more like an adapter using the `LoadableMixin`
    """

    def _unload(self) -> None:
        pass

    def _save(self, location: Path, metadata: Any) -> None:
        pass

    @staticmethod
    def _load_from(data: ExternalArray) -> Iterable[InternalArrayRow]:
        return (InternalArrayRow(a, b, c) for _, (a, b, c) in data.iterrows())

    @staticmethod
    def _get_data(children: Iterable[InternalArrayRow]) -> ExternalArray:
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

    @staticmethod
    def _load_file(location: Path) -> List[InternalArrayRow]:
        rows: List[InternalArrayRow] = []
        with location.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                parts = line.split(",")

                rows.append(
                    InternalArrayRow(
                        first=int(parts[0]), second=int(parts[1]), third=int(parts[2])
                    )
                )

        return rows
